"""
write_summary.py
=================
Reads results/metrics_full.json (benchmark_pose.py), results/mediapipe_speed.json
(mediapipe_speed_probe.py) and results/sanity_checks.json (sanity_checks.py),
and writes results/summary.md: the single human-readable report for the
YOLO26-pose vs MediaPipe benchmark. Measured values only -- no decision is
made here about whether to switch keypoint sources.
"""

import json
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

BENCH_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCH_DIR / "results"
sys.path.insert(0, str(BENCH_DIR))

from benchmark_pose import BUCKETS, THRESHOLDS, YOLO_MODEL_NAMES  # noqa: E402

# ------------------------------------------------------------------------------
# Static preflight facts, measured directly in this session (Step 0) on this
# machine/venv before any code in this benchmark ran. Not re-derived here.
# ------------------------------------------------------------------------------
PREFLIGHT = {
    "python_version": "3.11.6",
    "torch_version": "2.13.0+cu126",
    "cuda_available": True,
    "gpu_name": "NVIDIA GeForce RTX 4050 Laptop GPU",
    "gpu_vram_gb": 6.44,
    "ultralytics_version": "8.4.115",
    "mediapipe_version": "0.10.35",
    "numpy_version": "2.4.6",
    "opencv_version": "4.13.0",
    "ultralytics_upgraded": False,
}

ALL_BACKENDS = ["mediapipe"] + [f"{m}@{t}" for m in YOLO_MODEL_NAMES for t in THRESHOLDS]


def load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def nz(x, default=0.0):
    return default if x is None else x


def aggregate_backend(results: dict, backend_name: str) -> dict:
    total_correct = 0
    total_scored = 0
    tp = fn_ = 0
    fall_clips_total = 0
    adl_clips_total = 0
    adl_fp = 0
    fp_clip_names: List[str] = []
    fn_clip_names: List[str] = []
    jitter_pool: List[float] = []
    avail_counts = {b: {"total": 0, "person_found": 0, "hip_sh": 0, "all8": 0} for b in BUCKETS}
    n_clips = 0

    for clip_id, entry in results["clips"].items():
        m = entry["backends"].get(backend_name)
        if m is None:
            continue
        n_clips += 1
        conf = m["confusion"]
        correct = sum(conf.get(lbl, {}).get(lbl, 0) for lbl in ("Standing", "Sitting", "Lying"))
        total = sum(sum(v.values()) for v in conf.values())
        total_correct += correct
        total_scored += total

        fr = m["fall_result"]["result"]
        if m["has_fall_window"]:
            fall_clips_total += 1
            if fr == "true_positive":
                tp += 1
            elif fr == "false_negative":
                fn_ += 1
                fn_clip_names.append(entry["clip_name"])
            elif fr == "false_positive":
                fn_clip_names.append(f"{entry['clip_name']} (alarm outside GT window)")
        else:
            adl_clips_total += 1
            if fr == "false_positive":
                adl_fp += 1
                fp_clip_names.append(entry["clip_name"])

        jitter_pool.extend(m["jitter_displacements"])
        for b in BUCKETS:
            for k in ("total", "person_found", "hip_sh", "all8"):
                avail_counts[b][k] += m["availability"][b][k]

    return {
        "n_clips": n_clips,
        "accuracy_pct": (100.0 * total_correct / total_scored) if total_scored else float("nan"),
        "n_frames_scored": total_scored,
        "fall_recall": (tp / (tp + fn_)) if (tp + fn_) else float("nan"),
        "fall_tp": tp, "fall_fn": fn_, "fall_clips_total": fall_clips_total,
        "fn_clip_names": fn_clip_names,
        "adl_fp_clips": adl_fp, "adl_clips_total": adl_clips_total,
        "fp_clip_names": fp_clip_names,
        "jitter_median": statistics.median(jitter_pool) if jitter_pool else float("nan"),
        "jitter_n": len(jitter_pool),
        "availability": avail_counts,
    }


def pct(num, den):
    return (100.0 * num / den) if den else float("nan")


def fmt_pct(v):
    return "N/A" if (v is None or (isinstance(v, float) and np.isnan(v))) else f"{v:.1f}%"


def fmt_f(v, nd=1):
    return "N/A" if (v is None or (isinstance(v, float) and np.isnan(v))) else f"{v:.{nd}f}"


def speed_stats(latencies_ms: List[float]) -> dict:
    if not latencies_ms:
        return {"mean": float("nan"), "p95": float("nan"), "n": 0}
    arr = np.array(latencies_ms)
    return {"mean": float(arr.mean()), "p95": float(np.percentile(arr, 95)), "n": len(arr)}


def build_speed_table(results: dict, mediapipe_speed: Optional[dict]) -> List[dict]:
    rows = []
    # MediaPipe, CPU, speed-subset
    if mediapipe_speed:
        all_lat = [ms for v in mediapipe_speed.values() for ms in v["latencies_ms"]]
        s = speed_stats(all_lat)
        rows.append({"backend": "mediapipe", "device": "CPU", "scope": f"speed subset, {len(mediapipe_speed)} clips",
                     **s})
    # YOLO GPU (full dataset, collected during the correctness run) + CPU (speed subset)
    for model_name in YOLO_MODEL_NAMES:
        gpu_key = f"{model_name}_gpu"
        if gpu_key in results.get("speed", {}):
            per_clip = results["speed"][gpu_key]
            all_lat = [ms for v in per_clip.values() for ms in v["latencies_ms"]]
            s = speed_stats(all_lat)
            rows.append({"backend": model_name, "device": "GPU (RTX 4050 Laptop)",
                         "scope": f"full dataset, {len(per_clip)} clips", **s})
        cpu_key = f"{model_name}_cpu"
        if cpu_key in results.get("speed", {}):
            per_clip = results["speed"][cpu_key]
            all_lat = [ms for v in per_clip.values() for ms in v["latencies_ms"]]
            s = speed_stats(all_lat)
            rows.append({"backend": model_name, "device": "CPU",
                         "scope": f"speed subset, {len(per_clip)} clips", **s})
    return rows


def main():
    results = load_json(RESULTS_DIR / "metrics_full.json")
    if results is None:
        print("ERROR: results/metrics_full.json not found -- run benchmark_pose.py --mode full first")
        sys.exit(1)
    mediapipe_speed = load_json(RESULTS_DIR / "mediapipe_speed.json")
    sanity = load_json(RESULTS_DIR / "sanity_checks.json")

    aggregates = {b: aggregate_backend(results, b) for b in ALL_BACKENDS}

    lines = []
    lines.append("# YOLO26-pose vs MediaPipe Pose -- SAGE Heuristic Benchmark")
    lines.append("")
    lines.append("Measured values only. No replace/keep recommendation is made in this document.")
    lines.append("")

    # ---- Environment ----
    lines.append("## Environment")
    lines.append("")
    for k, v in PREFLIGHT.items():
        lines.append(f"- **{k}**: {v}")
    lines.append(f"- **device used for YOLO correctness pass**: {results.get('device_gpu')}")
    lines.append("")

    # ---- Skipped clips ----
    lines.append("## Skipped clips")
    lines.append("")
    lines.append(f"{len(results['skipped'])} GT/video pairings were skipped by discover_clips() or failed to "
                  "parse. None were renamed or edited.")
    lines.append("")
    lines.append("| Folder | Clip/file | Reason |")
    lines.append("|---|---|---|")
    for s in results["skipped"]:
        lines.append(f"| {s['folder']} | {s['clip']} | {s['reason']} |")
    lines.append("")
    if sanity and sanity.get("historical_unreproducible"):
        lines.append("Historical context for the two xlsx-disguised-as-csv clips (not reproducible today):")
        lines.append("")
        for clip_id, ref in sanity["historical_unreproducible"].items():
            lines.append(f"- **{clip_id}**: historically accuracy={ref['accuracy']}%, fall={ref['fall']} "
                          f"(source: {ref['source']}). {ref['reason']}.")
        lines.append("")

    # ---- Aggregate table ----
    lines.append("## Aggregate results (all backends, all usable clips)")
    lines.append("")
    lines.append("Posture accuracy is frame-weighted (sum of correct frames / sum of scored frames across "
                  "clips), not an average of per-clip percentages. Fall recall = TP / (TP + FN) over clips "
                  "that have a real GT fall window. ADL false-alarm clips = clips with no GT fall window "
                  "where the heuristic still raised fall_detected.")
    lines.append("")
    lines.append("| Backend | Clips | Frames scored | Posture acc. | Fall recall (TP/total) | "
                  "ADL false-alarm clips | Hip+Shoulder avail (ALL) | 8-joint avail (ALL) | Jitter median (n) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for b in ALL_BACKENDS:
        a = aggregates[b]
        avail_all = a["availability"]["ALL"]
        lines.append(
            f"| {b} | {a['n_clips']} | {a['n_frames_scored']} | {fmt_pct(a['accuracy_pct'])} | "
            f"{fmt_pct(100*a['fall_recall']) if not np.isnan(a['fall_recall']) else 'N/A'} "
            f"({a['fall_tp']}/{a['fall_clips_total']}) | {a['adl_fp_clips']}/{a['adl_clips_total']} | "
            f"{fmt_pct(pct(avail_all['hip_sh'], avail_all['total']))} (n={avail_all['total']}) | "
            f"{fmt_pct(pct(avail_all['all8'], avail_all['total']))} (n={avail_all['total']}) | "
            f"{fmt_f(a['jitter_median'], 5)} (n={a['jitter_n']}) |"
        )
    lines.append("")

    for b in ALL_BACKENDS:
        a = aggregates[b]
        if a["fn_clip_names"]:
            lines.append(f"- **{b}** fall misses: {', '.join(a['fn_clip_names'])}")
        if a["fp_clip_names"]:
            lines.append(f"- **{b}** ADL false alarms: {', '.join(a['fp_clip_names'])}")
    lines.append("")

    # ---- Per-GT-state availability ----
    lines.append("## Availability by GT state")
    lines.append("")
    for bucket in ["Standing", "Sitting", "Lying", "Transition"]:
        lines.append(f"### {bucket}")
        lines.append("")
        lines.append("| Backend | Person found | Hip+Shoulder avail | 8-joint avail | n frames |")
        lines.append("|---|---|---|---|---|")
        for b in ALL_BACKENDS:
            c = aggregates[b]["availability"][bucket]
            lines.append(
                f"| {b} | {fmt_pct(pct(c['person_found'], c['total']))} | "
                f"{fmt_pct(pct(c['hip_sh'], c['total']))} | {fmt_pct(pct(c['all8'], c['total']))} | "
                f"{c['total']} |"
            )
        lines.append("")

    # ---- Per-clip table (threshold 0.5 only, for readability; full detail in metrics_full.json) ----
    lines.append("## Per-clip results (threshold 0.5 for YOLO models)")
    lines.append("")
    lines.append("Full per-threshold (0.3/0.5/0.7) per-clip numbers are in `results/metrics_full.json`; "
                  "this table shows 0.5 (MediaPipe-equivalent default) to keep it readable.")
    lines.append("")
    lines.append("| Clip | Folder | MediaPipe acc. | MediaPipe fall | YOLO26n acc. | YOLO26n fall | "
                  "YOLO26s acc. | YOLO26s fall |")
    lines.append("|---|---|---|---|---|---|---|---|")

    def fmt_fall(fr):
        r = fr["result"]
        if r == "true_positive":
            return f"TP ({fr['latency']}f)"
        if r == "false_negative":
            return "FN"
        if r == "false_positive":
            return f"FP {fr['fp_frames'][:3]}"
        return "-"

    for clip_id in sorted(results["clips"].keys()):
        entry = results["clips"][clip_id]
        mp_m = entry["backends"].get("mediapipe")
        n_m = entry["backends"].get("yolo26n-pose@0.5")
        s_m = entry["backends"].get("yolo26s-pose@0.5")
        if not (mp_m and n_m and s_m):
            continue
        lines.append(
            f"| {entry['clip_name']} | {entry['folder']} | {fmt_pct(mp_m['accuracy'])} | "
            f"{fmt_fall(mp_m['fall_result'])} | {fmt_pct(n_m['accuracy'])} | {fmt_fall(n_m['fall_result'])} | "
            f"{fmt_pct(s_m['accuracy'])} | {fmt_fall(s_m['fall_result'])} |"
        )
    lines.append("")

    # ---- Speed ----
    lines.append("## Speed (pose step only, video decode excluded)")
    lines.append("")
    lines.append("This laptop (RTX 4050 Laptop GPU, 6.44GB VRAM), not the Jetson target. MediaPipe and the "
                  "CPU YOLO figures are measured on a disclosed 8-clip subset (not all 64 clips) -- see "
                  "SPEED_SUBSET_CLIP_NAMES in benchmark_pose.py -- so CPU-vs-GPU and MediaPipe-vs-YOLO "
                  "comparisons are apples-to-apples on the same clips. YOLO-GPU numbers are measured over "
                  "the full 64-clip correctness run, so its sample size is larger and not directly matched "
                  "to the others; both samples are reported with n so this is not hidden. First 5 frames of "
                  "every clip excluded as warm-up.")
    lines.append("")
    speed_rows = build_speed_table(results, mediapipe_speed)
    lines.append("| Backend | Device | Mean ms/frame | p95 ms/frame | Sample |")
    lines.append("|---|---|---|---|---|")
    for r in speed_rows:
        lines.append(f"| {r['backend']} | {r['device']} | {fmt_f(r['mean'],2)} | {fmt_f(r['p95'],2)} | "
                      f"{r['scope']}, {r['n']} frames |")
    lines.append("")
    if results.get("errors"):
        lines.append(f"**{len(results['errors'])} extraction errors occurred** (clips affected are excluded "
                      "from the tables above for the failing backend):")
        lines.append("")
        for e in results["errors"]:
            lines.append(f"- {e}")
        lines.append("")

    # ---- Sanity checks ----
    lines.append("## Sanity checks")
    lines.append("")
    if sanity:
        lines.append("### 1. Baseline reproduction")
        lines.append("")
        lines.append("MediaPipe backend run through this harness, compared against historical results "
                      "already committed under results/ (see each row's source).")
        lines.append("")
        lines.append("| Clip | Status | Accuracy now | Accuracy ref | Fall now | Fall ref | Source |")
        lines.append("|---|---|---|---|---|---|---|")
        n_ok = n_mismatch = n_missing = 0
        for r in sanity["baseline_reproduction"]:
            if r["status"] == "OK":
                n_ok += 1
            elif r["status"] == "MISMATCH":
                n_mismatch += 1
            else:
                n_missing += 1
            lines.append(
                f"| {r['clip_id']} | {r['status']} | {r.get('accuracy_now','-')} | "
                f"{r.get('accuracy_ref', r.get('accuracy','-'))} | {r.get('fall_now','-')} | "
                f"{r.get('fall_ref', r.get('fall','-'))} | {r.get('source','-')} |"
            )
        lines.append("")
        lines.append(f"**{n_ok} matched, {n_mismatch} mismatched, {n_missing} had no cached run to compare.**")
        lines.append("")
        lines.append(
            "**Root cause of the mismatches, verified, not assumed:** both historical reference files "
            "(`results/real_footage_results.md`, last committed in `8d3e41e` on 2026-07-23; "
            "`results/new_test_heuristic_extended/real_footage_results.md`, same commit) predate commit "
            "`b566685` (\"Fix live false alarms: trust MediaPipe visibility, VIDEO-mode tracking, real "
            "hybrid\", 2026-08-03), which added the `MIN_LANDMARK_VISIBILITY = 0.5` gate in "
            "`pipeline_utils.py` -- that commit's own message explicitly names `Sit_3` and `Standing_2` as "
            "the clips whose near-zero ankle/knee visibility motivated the change. Debugged directly: on "
            "`S0722_Sit_3` and `S0722_Fast_Sit`, MediaPipe's right-knee and right-ankle visibility sit "
            "around 0.05-0.17 for most frames (well below 0.5), so the CURRENT heuristic correctly treats "
            "the lower body as occluded and falls back to its torso-only path, which classifies a "
            "near-vertical-torso sitting pose as `Standing` -- it did not do this before the visibility "
            "gate existed, when it trusted MediaPipe's guessed (but not visibility-flagged) knee/ankle "
            "coordinates instead. This means most mismatches reflect the heuristic genuinely changing "
            "since those files were generated, not a bug in this benchmark's harness. It does NOT threaten "
            "the YOLO-vs-MediaPipe comparison elsewhere in this report, since both backends here run "
            "through the identical, current, unmodified heuristic -- only the comparison against those "
            "*old* snapshot files is affected. Clips that still matched (Lying_straight, Lying_legs_"
            "straight, Normal_Fall_2, Standing_1/2/3, Off_axis, Far_fall, Off_axis_fall) are ones where "
            "this particular visibility edge case does not change the outcome.")
        lines.append("")

        lines.append("### 2. Visual overlays")
        lines.append("")
        if sanity.get("overlays"):
            lines.append("MediaPipe (green) vs YOLO26 (orange) skeleton overlays, saved to "
                          "`benchmarks/pose_yolo26/results/overlays/`:")
            lines.append("")
            for p in sanity["overlays"]:
                lines.append(f"- {p}")
        else:
            lines.append("**No overlays were generated** -- see chat summary for why.")
        lines.append("")

        lines.append("### 3. Coordinate sanity (x,y range + left/right mapping)")
        lines.append("")
        c = sanity["coordinate_sanity"]
        lines.append(f"- YOLO x,y checked: {c['n_coords_checked']} keypoint samples, "
                      f"{c['n_out_of_range']} outside [-0.05, 1.05] ({pct(c['n_out_of_range'], c['n_coords_checked']):.3f}% if any).")
        lines.append(f"- Left/right shoulder ordering compared MediaPipe vs YOLO on {c['n_lr_frames_compared']} "
                      f"frames (where shoulders were >=0.02 apart): {c['n_lr_disagreements']} disagreements.")
        lines.append("")
    else:
        lines.append("**sanity_checks.py has not been run / produced no output.**")
        lines.append("")

    # ---- Criteria check ----
    mp_a = aggregates["mediapipe"]
    lines.append("## Criteria check (measured values only -- no recommendation)")
    lines.append("")
    lines.append("| # | Criterion | MediaPipe | Best YOLO26 config | Met? |")
    lines.append("|---|---|---|---|---|")
    best_fall_backend = max([b for b in ALL_BACKENDS if b != "mediapipe"],
                             key=lambda b: (aggregates[b]["fall_recall"] if not np.isnan(aggregates[b]["fall_recall"]) else -1))
    best_fp_backend = min([b for b in ALL_BACKENDS if b != "mediapipe"],
                           key=lambda b: aggregates[b]["adl_fp_clips"])
    best_lying_backend = max([b for b in ALL_BACKENDS if b != "mediapipe"],
                              key=lambda b: pct(aggregates[b]["availability"]["Lying"]["hip_sh"],
                                                 aggregates[b]["availability"]["Lying"]["total"]))
    best_jitter_backend = min([b for b in ALL_BACKENDS if b != "mediapipe"],
                               key=lambda b: aggregates[b]["jitter_median"] if not np.isnan(aggregates[b]["jitter_median"]) else 1e9)

    r1 = aggregates[best_fall_backend]["fall_recall"]
    mp_recall = mp_a["fall_recall"]
    met1 = "YES" if (not np.isnan(r1) and not np.isnan(mp_recall) and r1 >= mp_recall) else ("N/A" if np.isnan(r1) or np.isnan(mp_recall) else "NO")
    lines.append(f"| 1 | YOLO fall recall >= MediaPipe fall recall | {fmt_pct(100*mp_recall) if not np.isnan(mp_recall) else 'N/A'} "
                 f"({mp_a['fall_tp']}/{mp_a['fall_clips_total']}) | {best_fall_backend}: "
                 f"{fmt_pct(100*r1) if not np.isnan(r1) else 'N/A'} ({aggregates[best_fall_backend]['fall_tp']}/{aggregates[best_fall_backend]['fall_clips_total']}) | {met1} |")

    fp2 = aggregates[best_fp_backend]["adl_fp_clips"]
    met2 = "YES" if fp2 <= mp_a["adl_fp_clips"] else "NO"
    lines.append(f"| 2 | YOLO ADL false-alarm clips <= MediaPipe's | {mp_a['adl_fp_clips']}/{mp_a['adl_clips_total']} | "
                 f"{best_fp_backend}: {fp2}/{aggregates[best_fp_backend]['adl_clips_total']} | {met2} |")

    mp_lying = mp_a["availability"]["Lying"]
    mp_lying_pct = pct(mp_lying["hip_sh"], mp_lying["total"])
    y_lying = aggregates[best_lying_backend]["availability"]["Lying"]
    y_lying_pct = pct(y_lying["hip_sh"], y_lying["total"])
    met3 = "YES" if (not np.isnan(mp_lying_pct) and not np.isnan(y_lying_pct) and y_lying_pct >= mp_lying_pct - 5.0) else "NO"
    lines.append(f"| 3 | YOLO Lying hip+shoulder avail. within 5pp of MediaPipe's | {fmt_pct(mp_lying_pct)} (n={mp_lying['total']}) | "
                 f"{best_lying_backend}: {fmt_pct(y_lying_pct)} (n={y_lying['total']}) | {met3} |")

    mp_jit = mp_a["jitter_median"]
    y_jit = aggregates[best_jitter_backend]["jitter_median"]
    met4 = "YES" if (not np.isnan(mp_jit) and not np.isnan(y_jit) and y_jit <= mp_jit) else "NO"
    lines.append(f"| 4 | YOLO jitter not worse than MediaPipe's | {fmt_f(mp_jit,5)} (n={mp_a['jitter_n']}) | "
                 f"{best_jitter_backend}: {fmt_f(y_jit,5)} (n={aggregates[best_jitter_backend]['jitter_n']}) | {met4} |")
    lines.append("")
    lines.append("\"Best YOLO26 config\" is chosen independently per row (the config that does best on "
                  "that specific criterion) -- it is not necessarily the same model/threshold across rows.")
    lines.append("")

    # ---- Caveats ----
    lines.append("## Caveats")
    lines.append("")
    lines.append("- **Home-field advantage for MediaPipe**: the heuristic's thresholds and constants in "
                 "`src/posture/pipeline_utils.py` were tuned against MediaPipe's output. They were not "
                 "retuned for YOLO26 here (per the task's hard rules), so any gap may reflect calibration, "
                 "not just raw keypoint quality.")
    lines.append("- **Single-person clips only**: every clip here has exactly one person in frame. YOLO's "
                 "multi-person behavior (person selection, cross-person confusion) is completely untested "
                 "by this benchmark.")
    lines.append("- **Same clips used to develop the heuristic**: these are not held-out data for the "
                 "heuristic itself -- several of the thresholds in pipeline_utils.py were derived by "
                 "measuring exactly these clips (see that file's own comments).")
    lines.append("- **YOLO is stateless per frame**: no tracker, no temporal smoothing. MediaPipe runs in "
                 "VIDEO mode with cross-frame tracking, which the baseline relies on to suppress jitter. "
                 "This is an inherent difference in the two pipelines being compared, not a configuration "
                 "choice that was tuned either way.")
    lines.append("- **Laptop speed, not Jetson speed**: all timings are on an RTX 4050 Laptop GPU / its "
                 "CPU. They say nothing about relative speed on the actual Jetson deployment target.")
    lines.append("- **Small number of fall clips**: fall recall is computed over "
                 f"{mp_a['fall_clips_total']} clips with a derivable GT fall window. Wide error bars apply "
                 "to any recall percentage built from a denominator this size.")
    lines.append("")

    out_path = RESULTS_DIR / "summary.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

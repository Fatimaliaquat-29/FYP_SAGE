"""STAGE 4 -- pose benchmark v2 (corrected scoring + like-for-like speed).

Reuses, unmodified and imported by path: benchmarks/pose_yolo26/benchmark_pose.py (discovery, cache
paths, SPEED_SUBSET_CLIP_NAMES), yolo_pose_extract._apply_threshold_and_remap (the COCO->MediaPipe slot
mapping, unchanged), and evaluate_real_footage.{load_ground_truth, build_frame_gt, get_fall_window,
classify_frames, score_posture, score_fall}. Reads the existing pickle cache; writes only under OUT.

  --part score : re-score every cached clip x backend with ORIGINAL and CORRECTED fall windows
  --part speed : like-for-like latency on the disclosed 8-clip subset (run on an otherwise idle machine)
"""
import argparse
import platform
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, RAW, log, write_json, read_json, silence_pipeline_logger, import_by_path, decision

silence_pipeline_logger()          # must precede the import of pipeline_utils (via benchmark_pose)
BP = import_by_path("ov_benchmark_pose", ROOT / "benchmarks/pose_yolo26/benchmark_pose.py")
silence_pipeline_logger()
import evaluate_real_footage as ERF  # already imported by benchmark_pose; same module object
import yolo_pose_extract as YPE

import numpy as np

YOLO_MODELS = ["yolo26n-pose", "yolo26s-pose"]
THRESHOLDS = [0.3, 0.5, 0.7]


# ---------------------------------------------------------------------------------------------
# Corrected fall window (defect 1)
# ---------------------------------------------------------------------------------------------

def corrected_window(gt_df, fps):
    """Applied ONLY when get_fall_window() returns None. If the GT contains a transition (ignored)
    segment AND a lying/fall segment but NO upright (non-ignored, non-lying) segment, the expected
    window is [start of the first transition segment, end of the last fall-related (transition or
    lying) segment]. Returns (window or None, reason)."""
    o = gt_df.sort_values("start_time").reset_index(drop=True)
    lab = o["label"].astype(str).str.strip().str.lower()
    trans = o[o["ignore"].astype(bool)]
    lying = o[(~o["ignore"].astype(bool)) & (lab == "lying")]
    upright = o[(~o["ignore"].astype(bool)) & (lab != "lying")]
    if not upright.empty:
        return None, "has upright segment"
    if trans.empty or lying.empty:
        return None, "no transition+lying pair (lying-only or transition-only GT) -> no fall event"
    start = float(trans["start_time"].min())
    fall_rel = o[o["ignore"].astype(bool) | (lab == "lying")]
    end = float(fall_rel["end_time"].max())
    return (round(start * fps), round(end * fps)), "corrected: transition+lying, no upright"


def gt_rows(gt_df):
    return [[float(r.start_time), float(r.end_time), str(r.label), bool(r.ignore)] for r in gt_df.itertuples()]


# ---------------------------------------------------------------------------------------------
# Scoring part
# ---------------------------------------------------------------------------------------------

def backend_rows(clip_id):
    """Yields (backend_name, rows, fps, total, person_found_flags) from the existing cache only."""
    mp = BP._load_cache(BP._cache_path(clip_id, "mediapipe"))
    if mp is not None:
        yield "mediapipe", mp["rows"], mp["fps"], mp["total_frames"], [not np.isnan(r.get("lm_0_x", np.nan)) for r in mp["rows"]]
    else:
        yield "mediapipe", None, None, None, None
    for model in YOLO_MODELS:
        c = BP._load_cache(BP._cache_path(clip_id, f"{model}_raw_cuda0"))
        for thr in THRESHOLDS:
            if c is None:
                yield f"{model}@{thr}", None, None, None, None
                continue
            rows, counts = YPE._apply_threshold_and_remap(c["frames_raw"], thr)
            yield f"{model}@{thr}", rows, c["fps"], c["total_frames"], [n > 0 for n in counts]


def frac_in(flags, rows, lo, hi):
    sel = [f for f, r in zip(flags, rows) if lo <= int(r["frame_number"]) <= hi]
    return (sum(sel) / len(sel)) if sel else None, len(sel)


def part_score():
    clips, skipped = BP.discover_all_clips()
    old = read_json(ROOT / "benchmarks/pose_yolo26/results/metrics_full.json", {})
    out = {"n_clips": len(clips), "skipped": skipped, "clips": {}, "reproduction_mismatches": []}
    for ci, clip_id in enumerate(sorted(clips)):
        info = clips[clip_id]
        log(f"pose_v2 score [{ci + 1}/{len(clips)}] {clip_id}")
        gt_df = ERF.load_ground_truth(info["gt_path"])
        entry = {"gt_rows": gt_rows(gt_df), "backends": {}}
        for bname, rows, fps, total, flags in backend_rows(clip_id):
            if rows is None:
                entry["backends"][bname] = {"MISSING_CACHE": True}
                continue
            try:
                frame_gt = ERF.build_frame_gt(gt_df, fps, total)
                w0 = ERF.get_fall_window(gt_df, fps)
                wc, why = (w0, "original") if w0 is not None else corrected_window(gt_df, fps)
                classified = ERF.classify_frames(rows, clip_name=clip_id)
                acc, confusion, _ = ERF.score_posture(classified, frame_gt)
                f0 = ERF.score_fall(classified, w0)
                fc = ERF.score_fall(classified, wc)
                alarms = [r["frame_number"] for r in classified if r.get("fall_detected")]
                ign = {int(k): bool(v) for k, v in frame_gt["ignore"].to_dict().items()} if len(frame_gt) else {}
                preds = Counter(r.get("posture_label", "Unknown") for r in classified
                                if int(r["frame_number"]) in ign and not ign[int(r["frame_number"])])
                scored_fr = [i for i, v in ign.items() if not v]
                pf_scored = (np.mean([flags[i - 1] for i in scored_fr if 0 < i <= len(flags)]) if scored_fr else None)
                win = wc if wc is not None else None
                pf_win, n_win = frac_in(flags, rows, *win) if win else (None, 0)
                e = {"fps": fps, "total_frames": total, "n_rows": len(rows),
                     "window_original": list(w0) if w0 else None, "window_corrected": list(wc) if wc else None,
                     "window_rule": why, "accuracy": acc, "n_scored": int(sum(sum(v.values()) for v in confusion.values())),
                     "fall_original": {k: f0[k] for k in ("result", "latency")}, "fall_corrected": {k: fc[k] for k in ("result", "latency")},
                     "n_alarm_frames": len(alarms), "first_alarm": alarms[0] if alarms else None,
                     "alarms_outside_window_corrected": len(fc["fp_frames"]),
                     "pred_label_counts_scored": dict(preds), "person_found_frac_scored": pf_scored,
                     "person_found_frac_in_window": pf_win, "n_window_frames": n_win,
                     "gt_end_s": float(gt_df["end_time"].max()), "video_s": total / fps if fps else None}
                o = old.get("clips", {}).get(clip_id, {}).get("backends", {}).get(bname)
                if o is not None:
                    e["old_metrics_full_fall"] = o["fall_result"]["result"]
                    e["old_metrics_full_accuracy"] = o["accuracy"]
                    same_acc = (o["accuracy"] is None and (acc != acc)) or (o["accuracy"] is not None and abs(o["accuracy"] - acc) < 1e-6)
                    if o["fall_result"]["result"] != f0["result"] or not same_acc:
                        out["reproduction_mismatches"].append({"clip": clip_id, "backend": bname, "old": [o["fall_result"]["result"], o["accuracy"]],
                                                               "now": [f0["result"], acc]})
                entry["backends"][bname] = e
            except Exception as ex:
                entry["backends"][bname] = {"FAILED": repr(ex), "tb": traceback.format_exc()[-1500:]}
        out["clips"][clip_id] = entry
        if ci % 8 == 0:
            write_json(RAW / "pose_v2_scores.json", out)
    out["aggregates"] = aggregate(out)
    out["zero_clips"] = diagnose_zero(out)
    write_json(RAW / "pose_v2_scores.json", out)
    log(f"pose_v2 score done; reproduction mismatches vs metrics_full.json: {len(out['reproduction_mismatches'])}")


def aggregate(out):
    backends = sorted({b for c in out["clips"].values() for b in c["backends"]})
    agg = {}
    for b in backends:
        a = {}
        for mode, wkey, fkey in (("original", "window_original", "fall_original"), ("corrected", "window_corrected", "fall_corrected")):
            fall_clips = adl = tp = fn_silent = fn_alarm_outside = adl_fa = fall_extra = 0
            tp_names, miss_names, fa_names = [], [], []
            for cid, c in out["clips"].items():
                e = c["backends"].get(b)
                if not e or "FAILED" in e or "MISSING_CACHE" in e:
                    continue
                r = e[fkey]["result"]
                if e[wkey] is not None:
                    fall_clips += 1
                    if r == "true_positive":
                        tp += 1
                        tp_names.append(cid)
                    elif r == "false_positive":
                        fn_alarm_outside += 1
                        miss_names.append(cid + " (alarm outside window)")
                    else:
                        fn_silent += 1
                        miss_names.append(cid)
                else:
                    adl += 1
                    if r == "false_positive":
                        adl_fa += 1
                        fa_names.append(cid)
            a[mode] = {"fall_clips": fall_clips, "tp": tp, "fn_silent": fn_silent, "fn_alarm_outside_window": fn_alarm_outside,
                       "fall_recall": tp / fall_clips if fall_clips else None,
                       "old_style_recall_tp_over_tp_plus_silent_fn": tp / (tp + fn_silent) if (tp + fn_silent) else None,
                       "adl_clips": adl, "adl_false_alarm_clips": adl_fa,
                       "adl_false_alarm_rate": adl_fa / adl if adl else None,
                       "misses": miss_names, "adl_false_alarms": fa_names}
        tot_c = tot_s = 0
        for c in out["clips"].values():
            e = c["backends"].get(b)
            if e and "accuracy" in e and e["accuracy"] == e["accuracy"]:
                tot_c += e["accuracy"] / 100.0 * e["n_scored"]
                tot_s += e["n_scored"]
        a["posture_acc_frame_weighted"] = tot_c / tot_s if tot_s else None
        a["n_frames_scored"] = tot_s
        agg[b] = a
    changed = []
    for cid, c in out["clips"].items():
        e = c["backends"].get("mediapipe") or next(iter(c["backends"].values()))
        if e and e.get("window_rule", "").startswith("corrected"):
            changed.append({"clip": cid, "gt_rows": c["gt_rows"], "window_corrected_frames": e["window_corrected"]})
    agg["_clips_with_corrected_window"] = changed
    return agg


def diagnose_zero(out):
    """Rules (fixed before looking): a clip is listed if EVERY backend has posture accuracy 0% / no scored
    frames, or EVERY backend misses its (corrected) fall window. Cause:
      GT problem      -> no scored frames, or GT ends >1 s past the video, or GT covers <50% of the video,
                         or the corrected window lies outside the video
      no person       -> best backend's person-found fraction (scored frames for posture; window for falls) < 0.5
      heuristic miss  -> otherwise (person found, GT sane, heuristic output wrong)"""
    res = []
    for cid, c in sorted(out["clips"].items()):
        es = {b: e for b, e in c["backends"].items() if e and "accuracy" in e}
        if not es:
            continue
        any_e = next(iter(es.values()))
        posture_zero = all((e["n_scored"] == 0) or (e["accuracy"] == 0) for e in es.values())
        is_fall = any_e["window_corrected"] is not None
        fall_zero = is_fall and all(e["fall_corrected"]["result"] != "true_positive" for e in es.values())
        for kind, flag in (("posture_0pct_all_backends", posture_zero), ("fall_missed_by_all_backends", fall_zero)):
            if not flag:
                continue
            vid = any_e["video_s"] or 0
            gt_end = any_e["gt_end_s"]
            reasons = []
            if kind.startswith("posture") and all(e["n_scored"] == 0 for e in es.values()):
                reasons.append("no scored frames")
            if gt_end > vid + 1.0:
                reasons.append(f"GT ends at {gt_end:.1f}s but video is {vid:.1f}s")
            if gt_end < 0.5 * vid:
                reasons.append(f"GT covers only {gt_end:.1f}s of {vid:.1f}s")
            if kind.startswith("fall") and any_e["window_corrected"] and any_e["window_corrected"][0] > any_e["total_frames"]:
                reasons.append("fall window starts after the last frame")
            key = "person_found_frac_scored" if kind.startswith("posture") else "person_found_frac_in_window"
            pf = {b: e.get(key) for b, e in es.items()}
            best_pf = max((v for v in pf.values() if v is not None), default=None)
            if reasons:
                cause = "GT problem"
            elif best_pf is not None and best_pf < 0.5:
                cause = "no person detected"
            else:
                cause = "genuine heuristic miss"
            res.append({"clip": cid, "kind": kind, "cause": cause, "gt_reasons": reasons, "gt_rows": c["gt_rows"],
                        "person_found_frac": pf,
                        "pred_label_counts_scored": {b: e["pred_label_counts_scored"] for b, e in es.items()},
                        "fall_results": {b: e["fall_corrected"]["result"] for b, e in es.items()} if kind.startswith("fall") else None,
                        "first_alarm": {b: e["first_alarm"] for b, e in es.items()} if kind.startswith("fall") else None,
                        "window": any_e["window_corrected"]})
    return res


# ---------------------------------------------------------------------------------------------
# Speed part
# ---------------------------------------------------------------------------------------------

def part_speed(repeats=3, warm_frames=10):
    import cv2
    import torch
    import mediapipe as mp
    from ultralytics import YOLO

    clips, _ = BP.discover_all_clips()
    subset = [c for c in sorted(BP.SPEED_SUBSET_CLIP_NAMES) if c in clips]
    weights = ROOT / "benchmarks/pose_yolo26/weights"
    models = {}
    for m in YOLO_MODELS:
        models[(m, "cuda:0")] = YOLO(str(weights / f"{m}.pt"))
        models[(m, "cpu")] = YOLO(str(weights / f"{m}.pt"))
    BaseOptions = mp.tasks.BaseOptions
    _d = getattr(BaseOptions(), "delegate", None)
    delegate = "default = CPU (TFLite XNNPACK); no GPU delegate requested" if _d is None else str(_d)
    out = {"host": {"cpu": platform.processor(), "torch_threads": torch.get_num_threads(),
                    "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None},
           "mediapipe_delegate": delegate, "mediapipe_model": ERF.MODEL_PATH,
           "subset": subset, "repeats": repeats, "warmup_frames_excluded_per_clip": warm_frames,
           "input": "identical decoded full-resolution frames (cv2.VideoCapture) fed to every backend; "
                    "YOLO letterboxes internally to imgsz=640, MediaPipe resizes internally to its own input size",
           "timed_region": {"pose": "model call + result to numpy (CUDA synchronized), decode excluded",
                            "remap": "_apply_threshold_and_remap (YOLO only, thr 0.5)",
                            "heuristic": "classify_frames() total / frames (mean)"},
           "frame_sizes": {}, "runs": []}

    def frames_of(path):
        cap = cv2.VideoCapture(str(path))
        while True:
            ok, f = cap.read()
            if not ok:
                break
            yield f
        cap.release()

    def run_yolo(model, device, path, fps):
        lat, raw = [], []
        for i, fr in enumerate(frames_of(path)):
            t0 = time.perf_counter()
            r = model.predict(fr, imgsz=640, device=device, verbose=False)[0]
            persons = []
            if r.keypoints is not None and r.boxes is not None and len(r.boxes) > 0:
                xyn = r.keypoints.xyn.detach().cpu().numpy()
                kc = r.keypoints.conf.detach().cpu().numpy() if r.keypoints.conf is not None else np.zeros(xyn.shape[:2])
                bc = r.boxes.conf.detach().cpu().numpy()
                persons = [{"box_conf": float(bc[j]), "xy": xyn[j], "kconf": kc[j]} for j in range(xyn.shape[0])]
            if device != "cpu":
                torch.cuda.synchronize()
            t1 = time.perf_counter()
            lat.append((t1 - t0) * 1000)
            raw.append({"timestamp": (i + 1) / fps, "frame_number": i + 1, "n_persons": len(persons), "persons": persons})
        t0 = time.perf_counter()
        rows, _ = YPE._apply_threshold_and_remap(raw, 0.5)
        remap_ms = (time.perf_counter() - t0) * 1000 / max(1, len(raw))
        return lat, rows, remap_ms

    def run_mp(path, fps):
        opts = mp.tasks.vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=ERF.MODEL_PATH),
                                                     running_mode=mp.tasks.vision.RunningMode.VIDEO)
        det = mp.tasks.vision.PoseLandmarker.create_from_options(opts)
        lat, rows = [], []
        try:
            for i, fr in enumerate(frames_of(path)):
                ts = (i + 1) / fps
                t0 = time.perf_counter()
                rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
                res = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(ts * 1000))
                row = {"timestamp": ts, "frame_number": i + 1}
                if res.pose_landmarks:
                    for k, lm in enumerate(res.pose_landmarks[0]):
                        row.update({f"lm_{k}_x": lm.x, f"lm_{k}_y": lm.y, f"lm_{k}_z": lm.z,
                                    f"lm_{k}_visibility": lm.visibility, f"lm_{k}_presence": lm.presence})
                else:
                    for k in range(33):
                        row.update({f"lm_{k}_{s}": np.nan for s in ("x", "y", "z", "visibility", "presence")})
                t1 = time.perf_counter()
                lat.append((t1 - t0) * 1000)
                rows.append(row)
        finally:
            det.close()
        return lat, rows, None

    # global warm-up for every backend on the first clip's first 20 frames
    first = clips[subset[0]]["video_path"]
    for (m, dev), model in models.items():
        for k, fr in enumerate(frames_of(first)):
            model.predict(fr, imgsz=640, device=dev, verbose=False)
            if k >= 20:
                break
    backends = [("mediapipe", "cpu")] + [(m, d) for m in YOLO_MODELS for d in ("cuda:0", "cpu")]
    for rep in range(repeats):
        for bname, dev in backends:
            all_lat, heur, remap, nfr = [], [], [], 0
            for cid in subset:
                path = clips[cid]["video_path"]
                cap = cv2.VideoCapture(str(path))
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                out["frame_sizes"][cid] = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
                cap.release()
                if bname == "mediapipe":
                    lat, rows, rm = run_mp(path, fps)
                else:
                    lat, rows, rm = run_yolo(models[(bname, dev)], dev, path, fps)
                all_lat += lat[warm_frames:]
                nfr += len(rows)
                t0 = time.perf_counter()
                ERF.classify_frames(rows, clip_name=cid)
                heur.append(((time.perf_counter() - t0) * 1000, len(rows)))
                if rm is not None:
                    remap.append((rm, len(rows)))
            a = np.array(all_lat)
            run = {"rep": rep + 1, "backend": bname, "device": dev, "n_frames_timed": int(a.size), "n_frames_total": nfr,
                   "pose_median_ms": float(np.median(a)), "pose_p95_ms": float(np.percentile(a, 95)), "pose_mean_ms": float(a.mean()),
                   "heuristic_mean_ms_per_frame": sum(h for h, _ in heur) / max(1, sum(n for _, n in heur)),
                   "remap_mean_ms_per_frame": (sum(r * n for r, n in remap) / max(1, sum(n for _, n in remap))) if remap else None}
            out["runs"].append(run)
            log(f"speed rep{rep + 1} {bname}/{dev}: median {run['pose_median_ms']:.2f} ms, heuristic {run['heuristic_mean_ms_per_frame']:.3f} ms")
            write_json(RAW / "pose_v2_speed.json", out)
    summ = {}
    for bname, dev in backends:
        rs = [r for r in out["runs"] if r["backend"] == bname and r["device"] == dev]
        summ[f"{bname}|{dev}"] = {"pose_median_of_rep_medians_ms": float(np.median([r["pose_median_ms"] for r in rs])),
                                  "pose_p95_median_ms": float(np.median([r["pose_p95_ms"] for r in rs])),
                                  "rep_medians_ms": [r["pose_median_ms"] for r in rs],
                                  "heuristic_ms_per_frame": float(np.median([r["heuristic_mean_ms_per_frame"] for r in rs])),
                                  "remap_ms_per_frame": (float(np.median([r["remap_mean_ms_per_frame"] for r in rs]))
                                                         if rs and rs[0]["remap_mean_ms_per_frame"] is not None else None),
                                  "n_frames_timed_per_rep": rs[0]["n_frames_timed"] if rs else None}
    out["summary"] = summ
    write_json(RAW / "pose_v2_speed.json", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["score", "speed"], required=True)
    a = ap.parse_args()
    part_score() if a.part == "score" else part_speed()


if __name__ == "__main__":
    main()

"""
benchmarks/gait_calibration_harness.py
=======================================
Reusable, re-runnable calibration-EVIDENCE harness for src/gait/gait_risk.py's
sigmoid thresholds (walking_speed, stride_regularity, postural_sway,
sit_to_stand).

WHY this exists: docs/GAIT_CALIBRATION_DATASET_PLAN.md and
docs/GAIT_DATA_ASSESSMENT.md identify quiet_stand/slow_walk/fast_walk/
sway_wobble/sts_fast as scenarios with zero or near-zero real-footage
grounding for their sigmoid centers today. This script does NOT calibrate
or adjust anything itself -- it only reports what real footage, once
recorded and dropped into the folder layout below, actually produces
through the SAME production code path (build_pose_row ->
classify_posture_and_fall -> TorsoBaselineCalibrator ->
StreamingGaitRiskAssessor) that realtime_fall_detection.py uses, so a
human can decide whether/how to move a center. Running this script never
edits src/gait/gait_risk.py.

Expected input layout -- a folder of subfolders, one per calibration
PURPOSE TAG (matching docs/GAIT_CALIBRATION_DATASET_PLAN.md Table 2's own
scenario names):

    <intake_root>/
        quiet_stand/*.mp4 (or .mov)      [+ optional per-clip *_GT.csv]
        sway_wobble/*.mp4
        slow_walk/*.mp4
        fast_walk/*.mp4
        normal_walk/*.mp4
        sts_normal/*.mp4
        sts_fast/*.mp4
        <any other tag>/*.mp4             -- reported generically, no
                                              directional verdict since
                                              this script doesn't know
                                              what to expect from it

Only the subfolder NAME is meaningful; clip filenames inside are
free-form. GT CSVs are optional (same fuzzy-matched *_GT.csv / *_gt.csv
convention as gait_risk_distribution_analysis.py) and only feed the
gt_overlap field in the underlying per-window log -- the agree/disagree
verdicts below are always against gait_risk.py's live signal computation,
never against a GT label (these signals have no ground truth of their
own to compare against).

Usage:
    python benchmarks/gait_calibration_harness.py --intake <folder> [--out report.md] [--limit-per-tag N]

Idempotent / incremental: per-clip extraction is cached (see
gait_risk_distribution_analysis.extract_and_cache's CACHE_DIR), so
dropping one new clip into an existing tag folder and re-running only
re-extracts that one clip -- safe to re-run every time new footage
arrives without re-deriving anything.
"""
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BENCH_DIR = Path(__file__).resolve().parent
if str(BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(BENCH_DIR))

import gait_risk_distribution_analysis as gda  # noqa: E402

VIDEO_EXTS = (".mov", ".mp4", ".MOV", ".MP4")

# Mirrors the literal sigmoid center/slope values hardcoded in
# src/gait/gait_risk.py's _speed_risk / _stride_cv_risk / _sway_risk /
# _sit_to_stand_risk as of writing. These are inline literals there, not
# named module constants, so this table is a manually-maintained mirror --
# it must be updated by hand if those functions' literals change.
CURRENT_CALIBRATION = {
    "walking_speed": {"center": 1.0, "slope": 3.0, "direction": "lower value -> higher risk"},
    "stride_regularity": {"center": 0.30, "slope": 12.0, "direction": "higher value (CV) -> higher risk"},
    "postural_sway": {"center": 0.05, "slope": 15.0, "direction": "higher value -> higher risk"},
    "sit_to_stand": {
        "duration_center": 2.0, "duration_slope": 1.5,
        "reversal_center": 2.0, "reversal_slope": 0.8,
        "blend": "0.6 * duration_risk + 0.4 * reversal_risk",
        "direction": "longer duration / more reversals -> higher risk",
    },
}

# purpose tag -> [(signal_name, expected_risk_direction), ...]
# expected_risk_direction is "low" (risk_contribution should sit below
# 0.5), "high" (should sit above 0.5), or "mid" (no pass/fail verdict --
# this tag is a baseline/reference sample, not a tail sample).
# Not exhaustive: any subfolder name absent from this table still gets
# full distribution reporting below, just without a verdict line.
TAG_EXPECTATIONS = {
    "quiet_stand": [("postural_sway", "low")],
    "sway_wobble": [("postural_sway", "high")],
    "slow_walk": [("walking_speed", "high")],
    "fast_walk": [("walking_speed", "low")],
    "normal_walk": [("walking_speed", "mid"), ("stride_regularity", "mid")],
    "sts_normal": [("sit_to_stand", "mid")],
    "sts_fast": [("sit_to_stand", "low")],
}


def discover_intake(intake_root: Path) -> Dict[str, List[Path]]:
    tags: Dict[str, List[Path]] = {}
    for sub in sorted(p for p in intake_root.iterdir() if p.is_dir()):
        videos = sorted(p for p in sub.iterdir() if p.suffix in VIDEO_EXTS)
        if videos:
            tags[sub.name] = videos
    return tags


def _stats(values: List[float]) -> Optional[Dict[str, Any]]:
    if not values:
        return None
    a = np.asarray(values, dtype=float)
    return {
        "n": len(a), "min": float(a.min()), "p25": float(np.percentile(a, 25)),
        "median": float(np.median(a)), "p75": float(np.percentile(a, 75)),
        "max": float(a.max()), "mean": float(a.mean()),
    }


def run_tag(tag: str, videos: List[Path], limit: Optional[int] = None) -> Dict[str, Any]:
    if limit:
        videos = videos[:limit]
    per_signal_values: Dict[str, List[float]] = {}
    per_signal_risk: Dict[str, List[float]] = {}
    clip_summaries = []
    for video in videos:
        gt_path = gda._find_gt(video)
        gt_rows = gda._load_gt(gt_path)
        try:
            cached = gda.extract_and_cache(video)
            result = gda.run_gait_pipeline(video, cached, gt_rows)
        except Exception as exc:
            clip_summaries.append({"clip": video.name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        for w in result["windows"]:
            for name, sig in w["signals"].items():
                if not sig.get("available"):
                    continue
                val, rc = sig.get("value"), sig.get("risk_contribution")
                if isinstance(val, (int, float)):
                    per_signal_values.setdefault(name, []).append(float(val))
                if isinstance(rc, (int, float)):
                    per_signal_risk.setdefault(name, []).append(float(rc))
        clip_summaries.append({
            "clip": video.name, "n_frames": result["n_frames"], "n_windows": result["n_windows"],
            "calibrated_at_frame": result["calibrated_at_frame"], "torso_baseline": result["torso_baseline"],
        })
    return {
        "tag": tag, "n_clips": len(videos), "clips": clip_summaries,
        "signal_values": {k: _stats(v) for k, v in per_signal_values.items()},
        "signal_risk_contribution": {k: _stats(v) for k, v in per_signal_risk.items()},
    }


def _verdict(direction: str, rc_stats: Optional[Dict[str, Any]]) -> str:
    if rc_stats is None:
        return "no windows produced this signal -- no evidence"
    med = rc_stats["median"]
    if direction == "low":
        ok = med < 0.5
        return f"median risk_contribution={med:.3f} -- {'AGREES' if ok else 'DISAGREES'} with current threshold (expected < 0.5 for this scenario)"
    if direction == "high":
        ok = med >= 0.5
        return f"median risk_contribution={med:.3f} -- {'AGREES' if ok else 'DISAGREES'} with current threshold (expected >= 0.5 for this scenario)"
    return f"median risk_contribution={med:.3f} -- baseline/reference sample, no pass/fail verdict"


def render_report(tag_results: Dict[str, Dict[str, Any]]) -> str:
    lines = ["# GAIT Calibration Harness Report", ""]
    lines.append("Current sigmoid calibration (mirrored from `src/gait/gait_risk.py`, not derived automatically):")
    lines.append("")
    for name, cal in CURRENT_CALIBRATION.items():
        lines.append(f"- `{name}`: {cal}")
    lines.append("")

    if not tag_results:
        lines.append("No purpose-tag subfolders with video clips found under the intake root.")
        return "\n".join(lines)

    for tag, res in tag_results.items():
        lines.append(f"## `{tag}/` ({res['n_clips']} clip(s))")
        lines.append("")
        for c in res["clips"]:
            if "error" in c:
                lines.append(f"- **{c['clip']}**: ERROR -- {c['error']}")
            else:
                lines.append(
                    f"- {c['clip']}: {c['n_frames']} frames, {c['n_windows']} gait window(s), "
                    f"calibrated_at_frame={c['calibrated_at_frame']}, torso_baseline={c['torso_baseline']}"
                )
        lines.append("")

        expectations = dict(TAG_EXPECTATIONS.get(tag, []))
        signals_seen = set(res["signal_values"]) | set(res["signal_risk_contribution"])
        if not signals_seen:
            lines.append("No gait windows were produced for this tag (clips too short, or no valid calibration) -- no signal evidence.")
            lines.append("")
            continue

        for signal in sorted(signals_seen):
            v_stats = res["signal_values"].get(signal)
            rc_stats = res["signal_risk_contribution"].get(signal)
            lines.append(f"**{signal}**")
            if v_stats:
                lines.append(
                    f"- raw value distribution (n={v_stats['n']}): "
                    f"min={v_stats['min']:.4f} p25={v_stats['p25']:.4f} median={v_stats['median']:.4f} "
                    f"p75={v_stats['p75']:.4f} max={v_stats['max']:.4f} mean={v_stats['mean']:.4f}"
                )
            if rc_stats:
                lines.append(
                    f"- risk_contribution distribution (n={rc_stats['n']}): "
                    f"min={rc_stats['min']:.3f} p25={rc_stats['p25']:.3f} median={rc_stats['median']:.3f} "
                    f"p75={rc_stats['p75']:.3f} max={rc_stats['max']:.3f} mean={rc_stats['mean']:.3f}"
                )
            if signal in expectations:
                lines.append(f"- verdict vs. current threshold: {_verdict(expectations[signal], rc_stats)}")
            lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--intake", required=True, help="Folder containing one subfolder per calibration purpose tag")
    ap.add_argument("--out", default=str(REPO_ROOT / "benchmarks" / "gait_calibration_harness_report.md"))
    ap.add_argument("--limit-per-tag", type=int, default=None)
    args = ap.parse_args()

    intake_root = Path(args.intake)
    if not intake_root.is_dir():
        print(f"Intake root not found or not a directory: {intake_root}")
        sys.exit(1)

    tags = discover_intake(intake_root)
    print(f"Found {len(tags)} purpose-tag folder(s) under {intake_root}: {list(tags)}\n")

    tag_results = {}
    for tag, videos in tags.items():
        print(f"[{tag}] {len(videos)} clip(s)")
        tag_results[tag] = run_tag(tag, videos, limit=args.limit_per_tag)

    report = render_report(tag_results)
    print("\n" + report)

    out_path = Path(args.out)
    out_path.write_text(report, encoding="utf-8")
    print(f"\nWrote report -> {out_path}")


if __name__ == "__main__":
    main()

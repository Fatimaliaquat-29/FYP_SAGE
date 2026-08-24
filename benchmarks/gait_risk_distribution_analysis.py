"""
benchmarks/gait_risk_distribution_analysis.py
==============================================
Empirical evidence-gathering for a GAIT risk-mapping audit: runs the SAME
production code path realtime_fall_detection.py uses (build_pose_row with
world_landmarks -> classify_posture_and_fall -> TorsoBaselineCalibrator ->
StreamingGaitRiskAssessor), decoupled from cv2 display/camera reading, over
every real clip in this repo's two corpora (test_footage/Hussain Testing
7-30-26/, test_footage/Sanawar Testing 7-22-26/) plus
test_footage/GAIT_Analysis_Test_Footages/ -- the same ~44-clip corpus prior
GAIT audit sessions call "the full real-footage corpus."

Two-phase design so repeated analysis passes don't re-pay MediaPipe's
extraction cost:
  1. extract_and_cache(video) -- raw MediaPipe landmarks (2D + world),
     cached to disk (pickle) per clip.
  2. run_gait_pipeline(...) -- classification + calibration + GAIT streaming
     over the CACHED rows -- fast, pure Python/numpy, safe to re-run many
     times while iterating on gait_risk.py's risk-mapping functions.

Read-only reuse of evaluate_real_footage.py's extraction and
pipeline_utils.py's build_pose_row/classify_posture_and_fall/
reset_session_state (same convention as the existing validate_*.py
scripts in this directory) -- RF/LSTM/TCN model files are never loaded.

Usage:
    python benchmarks/gait_risk_distribution_analysis.py [--limit N] [--clip NAME]

Writes benchmarks/gait_risk_distribution_results.json (per-window results
for every clip) and prints a summary table to stdout.
"""
import argparse
import csv
import json
import pickle
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluate_real_footage import extract_keypoints, _keypoints_from_row, _visibility_from_row, _world_keypoints_from_row
from src.posture.pipeline_utils import build_pose_row, classify_posture_and_fall, reset_session_state
from src.gait import gait_features as gf
from src.gait.gait_stream import StreamingGaitRiskAssessor, TorsoBaselineCalibrator

# Repo-relative (not a session-specific scratchpad path) so the cache is
# portable across machines/sessions and reruns of this script -- or of
# anything importing extract_and_cache -- keep paying MediaPipe extraction
# cost only once per clip, not once per Claude session.
CACHE_DIR = REPO_ROOT / "benchmarks" / "_gait_risk_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = REPO_ROOT / "benchmarks" / "gait_risk_distribution_results.json"

CORPUS_DIRS = [
    REPO_ROOT / "test_footage" / "Hussain Testing 7-30-26",
    REPO_ROOT / "test_footage" / "Sanawar Testing 7-22-26",
    REPO_ROOT / "test_footage" / "GAIT_Analysis_Test_Footages",
]

WINDOW_FRAMES = gf.MIN_WINDOW_FRAMES  # 90 -- deliberately the floor, not the
# production default (150), so short real clips (many bend/fall clips are
# well under 5s) still produce at least some windows -- see this script's
# own module docstring for the rationale.
REASSESS_EVERY_N = 10
MIN_CALIBRATION_FRAMES = 45


def _find_video_files() -> List[Path]:
    exts = (".mov", ".mp4", ".MOV", ".MP4")
    out = []
    for d in CORPUS_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.suffix in exts:
                out.append(p)
    return out


def _find_gt(video_path: Path) -> Optional[Path]:
    """Fuzzy match: GT filenames across this project's two older corpora are
    NOT perfectly consistent (`_GT.csv`, `_GT .csv` with a stray space,
    `_gt.csv` lowercase) -- normalize by stripping spaces/case before
    comparing, rather than assuming one exact convention."""
    stem = video_path.stem
    candidates = [
        video_path.with_name(stem + "_GT.csv"),
        video_path.with_name(stem + "_gt.csv"),
    ]
    for c in candidates:
        if c.exists():
            return c
    # Fuzzy fallback: normalize (lowercase, strip spaces) and compare against
    # every csv in the same directory.
    norm_target = re.sub(r"\s+", "", stem.lower()) + "gt"
    for p in video_path.parent.iterdir():
        if p.suffix.lower() != ".csv":
            continue
        norm = re.sub(r"\s+", "", p.stem.lower())
        if norm == norm_target:
            return p
    return None


def _load_gt(path: Optional[Path]) -> List[Dict[str, Any]]:
    if path is None:
        return []
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                rows.append({
                    "start": float(row["start_time"]), "end": float(row["end_time"]),
                    "state": row["state"].strip(), "label": row["label"].strip(),
                })
            except (KeyError, ValueError):
                continue
    return rows


def _gt_overlap(gt_rows, ws: float, we: float) -> List[str]:
    return [f"{r['state']}:{r['label']}" for r in gt_rows if r["start"] < we and r["end"] > ws]


def extract_and_cache(video_path: Path) -> Dict[str, Any]:
    cache_path = CACHE_DIR / (video_path.stem + ".pkl")
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    kp_rows, fps, total = extract_keypoints(str(video_path))
    data = {"kp_rows": kp_rows, "fps": fps, "total": total}
    with open(cache_path, "wb") as f:
        pickle.dump(data, f)
    return data


def run_gait_pipeline(video_path: Path, cached: Dict[str, Any], gt_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mirrors realtime_fall_detection.py's run()'s own per-frame block
    (build_pose_row -> classify_posture_and_fall -> TorsoBaselineCalibrator
    -> StreamingGaitRiskAssessor), decoupled from cv2/camera/display, over
    already-extracted rows -- see this module's own docstring for why."""
    kp_rows = cached["kp_rows"]
    fps = cached["fps"] or 30.0

    reset_session_state()
    assessor = StreamingGaitRiskAssessor(window_frames=WINDOW_FRAMES, reassess_every_n_frames=REASSESS_EVERY_N)
    calibrator = TorsoBaselineCalibrator(min_run_frames=MIN_CALIBRATION_FRAMES)

    previous_rows: List[dict] = []
    windows: List[Dict[str, Any]] = []
    calibrated_at_frame = None

    for i, kp_row in enumerate(kp_rows):
        keypoints = _keypoints_from_row(kp_row)
        visibility = _visibility_from_row(kp_row)
        world_kps = _world_keypoints_from_row(kp_row)
        has_world = any(np.isfinite(v) for v in world_kps)
        row = build_pose_row(
            timestamp=kp_row.get("timestamp"), frame=i + 1,
            keypoints=keypoints, visibility=visibility,
            world_landmarks=[tuple(world_kps[j:j + 3]) for j in range(0, len(world_kps), 3)] if has_world else None,
        )
        result_dict = classify_posture_and_fall(row, previous_rows=previous_rows, lstm_classifier=None)
        row.update(result_dict)
        previous_rows.append(row)
        if len(previous_rows) > 320:
            previous_rows = previous_rows[-320:]

        posture = result_dict.get("posture_label", "Unknown")
        fall_now = bool(result_dict.get("fall_detected", False))

        if calibrator is not None and not calibrator.is_calibrated:
            if calibrator.observe(row, posture, fall_now):
                assessor.set_torso_baseline(calibrator.baseline)
                calibrated_at_frame = i + 1

        gait_result = assessor.push_frame(row)
        if gait_result is not None:
            t = row.get("timestamp", i / fps)
            t = float(t) if not isinstance(t, str) else float(t)
            win_start = max(0.0, t - WINDOW_FRAMES / fps)
            # Standalone diagnostic (see gait_features.py's own "TORSO
            # ANGULAR VELOCITY" section docstring) -- NOT part of
            # gait_result/risk_score, computed on the EXACT SAME window
            # StreamingGaitRiskAssessor just assessed (its RingFrameBuffer
            # still holds that snapshot at this point, before the next
            # push_frame() evicts the oldest frame), purely for offline
            # comparison against walking_speed on real footage.
            _diag_window = assessor._buffer.snapshot()
            torso_angvel = gf.compute_torso_angular_velocity_diagnostic(
                _diag_window, _world_raw=gf._raw_world_keypoint_array(_diag_window))
            windows.append({
                "frame": i + 1,
                "t": t,
                "gt_overlap": _gt_overlap(gt_rows, win_start, t),
                "risk_score": gait_result["risk_score"],
                "signals": {
                    s["name"]: {
                        "available": s["available"], "value": s["value"],
                        "risk_contribution": s["risk_contribution"],
                        "reliability": s.get("reliability"),
                        "n_events": s.get("n_events"),
                        "cadence_steps_per_min": s.get("cadence_steps_per_min"),
                    } for s in gait_result["signals"]
                },
                "torso_angular_velocity_diagnostic": torso_angvel,
                "posture_label": posture,
                "fall_detected": fall_now,
            })

    return {
        "n_frames": len(kp_rows),
        "fps": fps,
        "calibrated_at_frame": calibrated_at_frame,
        "torso_baseline": calibrator.baseline,
        "torso_baseline_mode": calibrator.baseline_mode,
        "n_windows": len(windows),
        "windows": windows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--clip", type=str, default=None, help="Only process clips whose filename contains this substring")
    args = ap.parse_args()

    videos = _find_video_files()
    if args.clip:
        videos = [v for v in videos if args.clip.lower() in v.name.lower()]
    if args.limit:
        videos = videos[:args.limit]

    print(f"Found {len(videos)} clips to process.\n")
    results = {}
    for i, video in enumerate(videos):
        name = video.stem
        print(f"[{i + 1}/{len(videos)}] {video.relative_to(REPO_ROOT)}", flush=True)
        t0 = time.perf_counter()
        try:
            gt_path = _find_gt(video)
            gt_rows = _load_gt(gt_path)
            cached = extract_and_cache(video)
            result = run_gait_pipeline(video, cached, gt_rows)
            result["gt_found"] = gt_path is not None
            result["corpus"] = video.parent.name
            results[name] = result
            print(f"    {result['n_frames']} frames, {result['n_windows']} gait windows, "
                  f"baseline={result['torso_baseline']}, {time.perf_counter() - t0:.1f}s", flush=True)
        except Exception as exc:
            results[name] = {"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}
            print(f"    ERROR: {exc}", flush=True)
        # Write incrementally so a long run's partial progress is never lost.
        with open(OUT_PATH, "w") as f:
            json.dump(results, f, indent=2, default=str)

    print(f"\nWrote {len(results)} clip results -> {OUT_PATH}")


if __name__ == "__main__":
    main()

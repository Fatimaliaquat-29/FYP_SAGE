"""
benchmarks/validate_new_gait_footage.py
========================================
Runs GaitRiskAssessor (via StreamingGaitRiskAssessor, same windowing
convention as validate_gait_on_footage.py: WINDOW_FRAMES=MIN_WINDOW_FRAMES,
REASSESS_EVERY_N=15) against the new
test_footage/GAIT_Analysis_Test_Footages/*.mov clips, cross-referencing
each assessment's window against that clip's *_GT.csv (start_time,end_time,
state,label) to report which ground-truth state each assessment window
overlaps.

Read-only reuse of evaluate_real_footage.py's MediaPipe extraction and
pipeline_utils.build_pose_row (same as validate_gait_on_footage.py) --
RF/LSTM/TCN are never imported. Writes a JSON results file.
"""
import csv
import glob
import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluate_real_footage import extract_keypoints, _keypoints_from_row, _visibility_from_row
from src.posture.pipeline_utils import build_pose_row, reset_session_state
from src.gait import gait_features as gf
from src.gait.gait_stream import StreamingGaitRiskAssessor

WINDOW_FRAMES = gf.MIN_WINDOW_FRAMES
REASSESS_EVERY_N = 15
FOOTAGE_DIR = REPO_ROOT / "test_footage" / "GAIT_Analysis_Test_Footages"


def _num_or_none(x):
    if x is None:
        return None
    if isinstance(x, dict):
        return {k: _num_or_none(v) for k, v in x.items()}
    if isinstance(x, (np.floating, np.integer)):
        x = x.item()
    if isinstance(x, float) and not np.isfinite(x):
        return None
    return x


def load_gt(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append({
                "start": float(row["start_time"]),
                "end": float(row["end_time"]),
                "state": row["state"],
                "label": row["label"],
            })
    return rows


def gt_states_overlapping(gt_rows, win_start: float, win_end: float) -> List[str]:
    out = []
    for r in gt_rows:
        if r["start"] < win_end and r["end"] > win_start:
            out.append(f"{r['state']}: {r['label']}")
    return out


def extract_pose_rows(video_path: str):
    reset_session_state()
    kp_rows, fps, total = extract_keypoints(video_path)
    rows = []
    for kp_row in kp_rows:
        keypoints = _keypoints_from_row(kp_row)
        pose_row = build_pose_row(
            timestamp=kp_row.get("timestamp"),
            frame=int(kp_row.get("frame_number", 0)),
            keypoints=keypoints,
            visibility=_visibility_from_row(kp_row),
        )
        rows.append(pose_row)
    return rows, fps


def validate_clip(video_path: Path) -> Dict[str, Any]:
    name = video_path.stem
    gt_path = video_path.with_name(name + "_GT.csv")
    entry: Dict[str, Any] = {"file": str(video_path), "name": name}
    try:
        gt_rows = load_gt(gt_path) if gt_path.exists() else None
        entry["gt"] = gt_rows

        t0 = time.perf_counter()
        rows, fps = extract_pose_rows(str(video_path))
        entry["extract_sec"] = time.perf_counter() - t0
        entry["fps"] = fps
        entry["n_frames"] = len(rows)

        if len(rows) < WINDOW_FRAMES:
            entry["skipped_reason"] = f"only {len(rows)} frames, need >= {WINDOW_FRAMES}"
            return entry

        raw = gf._raw_keypoint_array(rows)
        pts = raw.reshape(-1, 33, 2)
        ankle_valid = ~(np.isnan(pts[:, gf.LEFT_ANKLE, 1]) | np.isnan(pts[:, gf.RIGHT_ANKLE, 1]))
        hip_valid = ~(np.isnan(pts[:, gf.LEFT_HIP, :]).any(axis=1) | np.isnan(pts[:, gf.RIGHT_HIP, :]).any(axis=1))
        entry["raw_visibility"] = {
            "ankle_valid_ratio": float(ankle_valid.mean()),
            "hip_valid_ratio": float(hip_valid.mean()),
        }

        sa = StreamingGaitRiskAssessor(window_frames=WINDOW_FRAMES, reassess_every_n_frames=REASSESS_EVERY_N)
        assessments = []
        for i, row in enumerate(rows):
            result = sa.push_frame(row)
            if result is None:
                continue
            win_end_t = row.get("timestamp", i / fps)
            win_start_t = max(0.0, win_end_t - WINDOW_FRAMES / fps)
            overlap = gt_states_overlapping(gt_rows, win_start_t, win_end_t) if gt_rows else None
            assessments.append({
                "frame_idx": i,
                "window_start_sec": win_start_t,
                "window_end_sec": win_end_t,
                "risk_score": _num_or_none(result["risk_score"]),
                "signals": {s["name"]: {
                    "available": s["available"],
                    "value": _num_or_none(s["value"]),
                    "risk_contribution": _num_or_none(s["risk_contribution"]),
                    "reliability": _num_or_none(s.get("reliability")),
                    **({"cadence_steps_per_min": _num_or_none(s["cadence_steps_per_min"]),
                        "n_events": s.get("n_events")} if "cadence_steps_per_min" in s else {}),
                } for s in result["signals"]},
                "gt_overlap": overlap,
            })
        entry["n_assessments"] = len(assessments)
        entry["assessments"] = assessments

    except Exception as exc:
        entry["error"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"

    return entry


def main():
    print("CAVEAT: all GAIT_Analysis_Test_Footages/ clips are self-recorded from a "
          "single (N=1) subject -- nothing below generalizes to a population. See the "
          "standing caveat at the top of docs/GAIT_DATA_ASSESSMENT.md.\n")
    video_paths = sorted(glob.glob(str(FOOTAGE_DIR / "*.mov")))
    results = []
    out_path = REPO_ROOT / "benchmarks" / "gait_new_footage_validation_results.json"
    for i, vp in enumerate(video_paths):
        print(f"[{i + 1}/{len(video_paths)}] {vp}", flush=True)
        t0 = time.perf_counter()
        entry = validate_clip(Path(vp))
        print(f"    done in {time.perf_counter() - t0:.1f}s "
              f"({entry.get('n_assessments', 'ERR')} assessments)", flush=True)
        results.append(entry)
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)
    print(f"\nWrote {len(results)} clip results -> {out_path}")


if __name__ == "__main__":
    main()

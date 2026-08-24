"""
benchmarks/validate_gait_on_footage.py
========================================
Validates src/gait/ (gait_features.py, gait_risk.py, gait_stream.py)
against REAL test_footage/ clips, not synthetic windows. Read-only reuse
of evaluate_real_footage.py's MediaPipe extraction and
pipeline_utils.build_pose_row -- neither is edited, and the RF/LSTM/TCN
posture classifiers are never touched or imported for scoring here.

NOTE on ground truth: the *_gt.csv / *_GT.csv files alongside each clip
are posture labels (Standing/Sitting/Lying/Fall) for the existing
Fall/Lying/Sitting/Standing/Unknown classifier -- NOT gait fall-risk
ground truth. No gait-risk-labeled dataset exists in this repo (see
docs/GAIT_DATA_ASSESSMENT.md), so this script validates STRUCTURALLY
(crash-free, signal availability makes sense, old-vs-new parity, timing)
rather than against a risk-level ground truth that doesn't exist.

What this does, per clip:
  1. Extracts real MediaPipe keypoints -> pose rows (same extraction path
     evaluate_real_footage.py uses for the posture pipeline).
  2. Streams those rows through StreamingGaitRiskAssessor directly
     (single-threaded, for precise per-call latency) AND through the full
     GaitPipeline (threaded producer-consumer, to exercise the real
     threading path) -- records every non-None assessment over time.
  3. At every streaming reassessment point, runs BOTH the current
     (post-vectorization) feature functions and the independently
     reimplemented pre-vectorization ones (benchmarks/gait_old_impl.py)
     on the identical window and diffs the result.
  4. Replays a subset of clips through GaitPipeline with randomized
     inter-frame delays/drops to simulate camera jitter.
  5. Records per-frame push latency (no-op appends) and per-assessment
     latency (actual feature computation) separately, from real footage,
     not synthetic benchmark windows.

Writes a JSON results file; benchmarks/summarize_gait_validation.py turns
it into the markdown report/table.
"""
import argparse
import glob
import json
import random
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluate_real_footage import extract_keypoints, _keypoints_from_row, _visibility_from_row
from src.posture.pipeline_utils import build_pose_row, reset_session_state
from src.gait import gait_features as gf
from src.gait.gait_risk import GaitRiskAssessor
from src.gait.gait_stream import GaitPipeline, StreamingGaitRiskAssessor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gait_old_impl as old

WINDOW_FRAMES = gf.MIN_WINDOW_FRAMES  # 90 -- short clips (5-15s) need the floor, not 150
REASSESS_EVERY_N = 15
JITTER_CLIP_COUNT = 3  # how many clips get the frame-drop/delay simulation (keeps total runtime sane)


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


def _signals_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    return {s["name"]: {"available": s["available"], "value": _num_or_none(s["value"]),
                         "risk_contribution": _num_or_none(s["risk_contribution"])}
            for s in result["signals"]}


def compare_old_vs_new(window: List[dict]) -> Dict[str, Any]:
    new_result = GaitRiskAssessor().assess_risk(window)
    old_result = old.old_assess_risk(window)

    new_score = new_result["risk_score"]
    old_score = old_result["risk_score"]
    if new_score is None and old_score is None:
        score_match = True
        score_diff = 0.0
    elif new_score is None or old_score is None:
        score_match = False
        score_diff = None
    else:
        score_diff = abs(new_score - old_score)
        score_match = score_diff < 1e-9

    value_mismatches = []
    new_by_name = {s["name"]: s["value"] for s in new_result["signals"]}
    for name, old_value in old_result["values"].items():
        new_value = new_by_name.get(name)
        if old_value is None and new_value is None:
            continue
        if old_value is None or new_value is None:
            value_mismatches.append(name)
            continue
        if isinstance(old_value, dict):
            for k in old_value:
                if abs(float(old_value[k]) - float(new_value[k])) > 1e-6:
                    value_mismatches.append(f"{name}.{k}")
        else:
            if abs(float(old_value) - float(new_value)) > 1e-9:
                value_mismatches.append(name)

    return {
        "score_match": score_match,
        "score_diff": score_diff,
        "new_score": _num_or_none(new_score),
        "old_score": _num_or_none(old_score),
        "value_mismatches": value_mismatches,
    }


def run_streaming(window_rows: List[dict], fps: float) -> Dict[str, Any]:
    """Single-threaded streaming pass (precise per-call timing) that ALSO
    performs the old-vs-new parity check at every reassessment point."""
    sa = StreamingGaitRiskAssessor(window_frames=WINDOW_FRAMES, reassess_every_n_frames=REASSESS_EVERY_N)
    buffer_snapshot_ref = sa._buffer  # internal, read-only, for grabbing the exact window compared below

    push_latencies_ms = []
    assessment_latencies_ms = []
    assessments = []  # (frame_idx, time_sec, result)
    parity_checks = []
    first_assessment_frame = None

    for i, row in enumerate(window_rows):
        t0 = time.perf_counter()
        result = sa.push_frame(row)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        if result is not None:
            assessment_latencies_ms.append(dt_ms)
            if first_assessment_frame is None:
                first_assessment_frame = i
            assessments.append({
                "frame_idx": i,
                "time_sec": row.get("timestamp", i / fps),
                "risk_score": _num_or_none(result["risk_score"]),
                "signals": _signals_summary(result),
            })
            window_now = buffer_snapshot_ref.snapshot()
            try:
                parity_checks.append(compare_old_vs_new(window_now))
            except Exception as exc:
                parity_checks.append({"error": f"{type(exc).__name__}: {exc}"})
        else:
            push_latencies_ms.append(dt_ms)

    return {
        "n_frames": len(window_rows),
        "first_assessment_frame": first_assessment_frame,
        "time_to_first_assessment_sec": (first_assessment_frame / fps) if first_assessment_frame is not None else None,
        "n_assessments": len(assessments),
        "assessments": assessments,
        "push_latency_ms_mean": float(np.mean(push_latencies_ms)) if push_latencies_ms else None,
        "push_latency_ms_p95": float(np.percentile(push_latencies_ms, 95)) if push_latencies_ms else None,
        # First assessment's latency reported SEPARATELY from the rest: real
        # camera clips (unlike the synthetic profiling benchmark, which does
        # one warm-up call before timing) hit this process's actual FIRST
        # call to compute_stride_regularity/_torso_scaled_hip_track, which
        # lazily `import scipy.signal` / `import pandas` on first use --
        # burying that one-time cost inside a "mean" would hide a real
        # cold-start latency spike a live deployment would see on its very
        # first assessment after startup.
        "first_assessment_latency_ms": assessment_latencies_ms[0] if assessment_latencies_ms else None,
        "assessment_latency_ms_mean_excl_first": (
            float(np.mean(assessment_latencies_ms[1:])) if len(assessment_latencies_ms) > 1 else None
        ),
        "assessment_latency_ms_max_excl_first": (
            float(np.max(assessment_latencies_ms[1:])) if len(assessment_latencies_ms) > 1 else None
        ),
        "parity_checks": parity_checks,
    }


def run_threaded_pipeline(window_rows: List[dict], fps: float, jitter: bool, seed: int = 0) -> Dict[str, Any]:
    """Replays rows through the real threaded GaitPipeline, PACED at the
    clip's actual fps -- a live camera delivers frames at a roughly steady
    real-time rate, not as fast as Python can loop, so pacing here is what
    makes this a meaningful test of the threaded path rather than an
    artificial producer/consumer race. If `jitter`, per-frame timing is
    perturbed and ~10% of frames are dropped on top of that pacing, to
    simulate real camera jitter/dropped frames (see item 3's ask)."""
    rng = random.Random(seed)
    base_interval = 1.0 / fps
    results = []
    errors = []

    def on_result(r):
        results.append(_num_or_none(r["risk_score"]))

    pipeline = GaitPipeline(window_frames=WINDOW_FRAMES, reassess_every_n_frames=REASSESS_EVERY_N,
                             queue_maxsize=64, on_result=on_result)
    t_start = time.perf_counter()
    pipeline.start()
    try:
        for row in window_rows:
            if jitter and rng.random() < 0.1:
                continue  # simulate a dropped camera frame
            pipeline.submit_frame(row)
            sleep_for = base_interval
            if jitter:
                sleep_for = max(0.0, base_interval + rng.uniform(-base_interval * 0.7, base_interval * 4.0))
            time.sleep(sleep_for)

        # Give the consumer a short grace period to finish draining the
        # queue after the last frame was submitted.
        deadline = time.perf_counter() + 3.0
        while time.perf_counter() < deadline:
            time.sleep(0.05)
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
    finally:
        stop_ok = True
        try:
            pipeline.stop(timeout=5.0)
        except Exception as exc:
            stop_ok = False
            errors.append(f"stop() failed: {exc}")

    return {
        "jitter": jitter,
        "n_results": len(results),
        "results": results,
        "clean_stop": stop_ok,
        "errors": errors,
        "wall_time_sec": time.perf_counter() - t_start,
    }


def validate_clip(video_path: str, do_jitter: bool) -> Dict[str, Any]:
    name = Path(video_path).stem
    entry: Dict[str, Any] = {"file": video_path, "name": name}
    try:
        t0 = time.perf_counter()
        rows, fps = extract_pose_rows(video_path)
        extract_sec = time.perf_counter() - t0
        entry["fps"] = fps
        entry["n_frames"] = len(rows)
        entry["extract_sec"] = extract_sec

        if len(rows) < WINDOW_FRAMES:
            entry["skipped_reason"] = f"only {len(rows)} frames, need >= {WINDOW_FRAMES} (MIN_WINDOW_FRAMES)"
            return entry

        entry["streaming"] = run_streaming(rows, fps)
        entry["threaded_pipeline"] = run_threaded_pipeline(rows, fps, jitter=False)
        if do_jitter:
            entry["threaded_pipeline_jitter"] = run_threaded_pipeline(rows, fps, jitter=True, seed=42)

        # Under realistic (paced, no-drop) timing, the threaded pipeline
        # should reach the SAME number of assessments as the direct
        # single-threaded streaming pass on the identical frames -- a
        # mismatch here would mean the threading/queueing layer itself is
        # losing or duplicating work, not just an artifact of unrealistic
        # test pacing.
        entry["threaded_matches_streaming_count"] = (
            entry["threaded_pipeline"]["n_results"] == entry["streaming"]["n_assessments"]
        )

        # Raw-visibility summary for edge-case flagging (ankle/hip NaN ratio).
        raw = gf._raw_keypoint_array(rows)
        pts = raw.reshape(-1, 33, 2)
        ankle_valid = ~(np.isnan(pts[:, gf.LEFT_ANKLE, 1]) | np.isnan(pts[:, gf.RIGHT_ANKLE, 1]))
        hip_valid = ~(np.isnan(pts[:, gf.LEFT_HIP, :]).any(axis=1) | np.isnan(pts[:, gf.RIGHT_HIP, :]).any(axis=1))
        entry["raw_visibility"] = {
            "ankle_valid_ratio": float(ankle_valid.mean()),
            "hip_valid_ratio": float(hip_valid.mean()),
        }

    except Exception as exc:
        entry["error"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"

    return entry


def main():
    print("CAVEAT: all test_footage/ clips are self-recorded from a single (N=1) "
          "subject -- nothing below generalizes to a population. See the standing "
          "caveat at the top of docs/GAIT_DATA_ASSESSMENT.md.\n")
    ap = argparse.ArgumentParser()
    ap.add_argument("--footage_dir", default="test_footage")
    ap.add_argument("--output", default="benchmarks/gait_footage_validation_results.json")
    ap.add_argument("--limit", type=int, default=None, help="only process the first N clips (debug)")
    args = ap.parse_args()

    video_paths = sorted(glob.glob(str(Path(args.footage_dir) / "**" / "*.MOV"), recursive=True)) + \
                  sorted(glob.glob(str(Path(args.footage_dir) / "**" / "*.mp4"), recursive=True))
    if args.limit:
        video_paths = video_paths[:args.limit]

    jitter_set = set(video_paths[:JITTER_CLIP_COUNT]) | {
        p for p in video_paths if "Moving_in_out_frame" in p
    }

    results = []
    for i, vp in enumerate(video_paths):
        print(f"[{i + 1}/{len(video_paths)}] {vp}", flush=True)
        t0 = time.perf_counter()
        entry = validate_clip(vp, do_jitter=(vp in jitter_set))
        print(f"    done in {time.perf_counter() - t0:.1f}s", flush=True)
        results.append(entry)
        # Write incrementally so a crash partway through doesn't lose everything.
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

    print(f"\nWrote {len(results)} clip results -> {args.output}")


if __name__ == "__main__":
    main()

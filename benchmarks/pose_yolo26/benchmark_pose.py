"""
benchmark_pose.py
==================
Benchmarks YOLO26-pose (nano + small, 3 keypoint-confidence thresholds each)
against the existing MediaPipe-Pose baseline as the keypoint source feeding
the UNMODIFIED SAGE posture/fall heuristic, over every clip discoverable
under Testing/.

Reuses, unmodified, from evaluate_real_footage.py: discover_clips,
load_ground_truth, build_frame_gt, get_fall_window, classify_frames,
score_posture, score_fall, per_class_accuracy, extract_keypoints (the
MediaPipe baseline), and the private row-building helpers
_keypoints_from_row / _visibility_from_row (so the availability/jitter
metrics below mask landmarks exactly the way classify_frames does).

Results are cached per clip+backend under cache/ and written as a single
JSON blob to results/metrics.json for write_summary.py to render.

Usage:
  .venv2\\Scripts\\python.exe benchmark_pose.py --mode smoke
  .venv2\\Scripts\\python.exe benchmark_pose.py --mode full
"""

import argparse
import json
import logging
import pickle
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BENCH_DIR = Path(__file__).resolve().parent
CACHE_DIR = BENCH_DIR / "cache"
WEIGHTS_DIR = BENCH_DIR / "weights"
RESULTS_DIR = BENCH_DIR / "results"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
if str(BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(BENCH_DIR))

from evaluate_real_footage import (  # noqa: E402
    discover_clips,
    load_ground_truth,
    build_frame_gt,
    get_fall_window,
    classify_frames,
    score_posture,
    score_fall,
    per_class_accuracy,
    extract_keypoints as mediapipe_extract_keypoints,
    _keypoints_from_row,
    _visibility_from_row,
)
from src.posture.pipeline_utils import build_pose_row, is_landmark_valid  # noqa: E402

from yolo_pose_extract import extract_keypoints_yolo_raw, _apply_threshold_and_remap  # noqa: E402

# pipeline_utils.py's module-level logger (set to INFO at IMPORT time, inside
# that file) writes one INFO/WARNING line per posture transition / fall
# trigger -- at 64 clips x 7 backend configs that is hundreds of thousands of
# lines, and it also appends every one of them to data/detections.log (a
# gitignored but still never-touch-directory file pipeline_utils opens at
# import time). Must run AFTER the imports above, since pipeline_utils' own
# `logger.setLevel(logging.INFO)` runs during that import and would otherwise
# undo a suppression set beforehand. This is a runtime logging-config change
# in OUR process, not an edit to pipeline_utils.py's file.
logging.getLogger("posture_pipeline").setLevel(logging.CRITICAL + 1)

TESTING_ROOT = REPO_ROOT / "Testing"
FOLDER_TAGS = {
    "Hussain Testing 7-23-26": "H0723",
    "Hussain Testing 7-30-26": "H0730",
    "Hussain Testing 8-2-26": "H0802",
    "Sanawar Testing 7-22-26": "S0722",
    "Sanawar Testing 7-25-26": "S0725",
    "Sanawar Testing 8-7-26": "S0807",
}

THRESHOLDS = [0.3, 0.5, 0.7]
YOLO_MODEL_NAMES = ["yolo26n-pose", "yolo26s-pose"]
DEVICE_GPU = "cuda:0" if torch.cuda.is_available() else None
DEVICE_CPU = "cpu"

# Clips used for the CPU-vs-GPU speed comparison (a deliberately small,
# disclosed subset -- see summary.md "Speed" section for why: timing every
# clip on CPU for both models would multiply total runtime for no extra
# statistical value beyond what a representative subset already gives).
SPEED_SUBSET_CLIP_NAMES = {
    "S0722_Standing_1",            # short ADL, upright
    "S0722_Sit_3",                 # short ADL, seated
    "S0807_Floor_long_lie",        # long lying clip
    "H0730_LyingdownSlowly",       # slow transition into lying
    "H0802_Fall_backward_2",       # real fall
    "S0725_Occluded_fall",         # occluded fall
    "H0730_Bend_pickup_lowLight",  # low light
    "S0722_Off_axis",              # off-axis framing
}


# ------------------------------------------------------------------------------
# Discovery
# ------------------------------------------------------------------------------

def discover_all_clips() -> Tuple[Dict[str, dict], List[dict]]:
    clips: Dict[str, dict] = {}
    skipped: List[dict] = []
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

    for folder_name, tag in FOLDER_TAGS.items():
        batch_dir = TESTING_ROOT / folder_name
        if not batch_dir.exists():
            skipped.append({"folder": folder_name, "clip": None,
                             "reason": "folder does not exist"})
            continue

        pairs = discover_clips(str(batch_dir))
        matched_gt_paths = set()

        for video_path, gt_path, clip_name in pairs:
            matched_gt_paths.add(Path(gt_path).resolve())
            clip_id = f"{tag}_{clip_name}"
            try:
                load_ground_truth(gt_path)
            except Exception as e:
                head = b""
                try:
                    with open(gt_path, "rb") as fh:
                        head = fh.read(4)
                except OSError:
                    pass
                extra = (" (file begins with 'PK' -- it is actually a zip/xlsx "
                          "file saved with a .csv extension)" if head[:2] == b"PK" else "")
                skipped.append({"folder": folder_name, "clip": clip_name,
                                 "reason": f"GT unparseable: {e}{extra}"})
                continue

            clips[clip_id] = {
                "video_path": video_path,
                "gt_path": gt_path,
                "folder": folder_name,
                "clip_name": clip_name,
                "tag": tag,
            }

        all_csvs = sorted(batch_dir.rglob("*.csv"))
        for f in all_csvs:
            if f.resolve() in matched_gt_paths:
                continue
            if f.name.lower().endswith("_gt.csv"):
                stem = f.stem[:-3]
                candidates = [c for c in batch_dir.iterdir()
                              if c.suffix.lower() in video_exts and c.stem.lower() == stem.lower()]
                if not candidates:
                    reason = (f"GT file matches '_gt.csv' pattern (stem '{stem}') but no video "
                               f"with that stem exists (name mismatch / typo / wrong extension)")
                else:
                    reason = "matched pattern and a video exists but discover_clips did not pair them (unexpected)"
            else:
                reason = ("filename does not end in '_gt.csv' -- likely a stray space before "
                           "the extension, wrong case, or an alternate-dialect file (e.g. "
                           "'_GT_converted.csv') that discover_clips does not select")
            skipped.append({"folder": folder_name, "clip": f.stem, "reason": f"{reason} [{f.name}]"})

    return clips, skipped


# ------------------------------------------------------------------------------
# Caching
# ------------------------------------------------------------------------------

def _cache_path(clip_id: str, tag: str) -> Path:
    safe = clip_id.replace("/", "_").replace(" ", "_")
    return CACHE_DIR / f"{safe}__{tag}.pkl"


def _load_cache(path: Path):
    if path.exists():
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


def _save_cache(path: Path, obj) -> None:
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def get_mediapipe_rows(clip_id: str, video_path: str):
    path = _cache_path(clip_id, "mediapipe")
    cached = _load_cache(path)
    if cached is not None:
        return cached["rows"], cached["fps"], cached["total_frames"]
    rows, fps, total_frames = mediapipe_extract_keypoints(video_path)
    _save_cache(path, {"rows": rows, "fps": fps, "total_frames": total_frames})
    return rows, fps, total_frames


def get_yolo_raw(clip_id: str, video_path: str, model_name: str, weights_path: Path, device: str):
    dev_tag = device.replace(":", "")
    path = _cache_path(clip_id, f"{model_name}_raw_{dev_tag}")
    cached = _load_cache(path)
    if cached is not None:
        return cached["frames_raw"], cached["fps"], cached["total_frames"], cached["latencies_ms"]
    frames_raw, fps, total_frames, latencies_ms = extract_keypoints_yolo_raw(
        video_path, str(weights_path), imgsz=640, device=device)
    _save_cache(path, {"frames_raw": frames_raw, "fps": fps, "total_frames": total_frames,
                        "latencies_ms": latencies_ms})
    return frames_raw, fps, total_frames, latencies_ms


# ------------------------------------------------------------------------------
# GT-state bucketing (Standing / Sitting / Lying / Transition / Other)
# ------------------------------------------------------------------------------

def _gt_bucket(frame_gt: pd.DataFrame, fn: int) -> Optional[str]:
    if fn not in frame_gt.index:
        return None
    entry = frame_gt.loc[fn]
    if bool(entry["ignore"]):
        return "Transition"
    lbl = str(entry["gt_label"]).strip().capitalize()
    if lbl in ("Standing", "Sitting", "Lying"):
        return lbl
    return "Other"


BUCKETS = ["Standing", "Sitting", "Lying", "Transition", "Other", "ALL"]


# ------------------------------------------------------------------------------
# Availability + jitter (computed on the SAME masked keypoints the heuristic sees)
# ------------------------------------------------------------------------------

def compute_availability(rows: List[dict], frame_gt: pd.DataFrame,
                          person_found_flags: List[bool]) -> dict:
    counts = {b: {"total": 0, "person_found": 0, "hip_sh": 0, "all8": 0} for b in BUCKETS}

    for row, pf in zip(rows, person_found_flags):
        fn = int(row.get("frame_number", 0))
        bucket = _gt_bucket(frame_gt, fn)
        if bucket is None:
            continue

        keypoints = _keypoints_from_row(row)
        visibility = _visibility_from_row(row)
        pose_row = build_pose_row(timestamp=row.get("timestamp"), frame=fn,
                                   keypoints=keypoints, visibility=visibility)
        kp = pose_row["keypoints"]
        pairs = [(kp[2 * i], kp[2 * i + 1]) for i in range(33)]

        hip_sh_ok = (is_landmark_valid(pairs[11]) and is_landmark_valid(pairs[12])
                     and is_landmark_valid(pairs[23]) and is_landmark_valid(pairs[24]))
        all8_ok = hip_sh_ok and all(is_landmark_valid(pairs[i]) for i in (25, 26, 27, 28))

        for b in (bucket, "ALL"):
            counts[b]["total"] += 1
            if pf:
                counts[b]["person_found"] += 1
            if hip_sh_ok:
                counts[b]["hip_sh"] += 1
            if all8_ok:
                counts[b]["all8"] += 1

    return counts


def compute_jitter(rows: List[dict], frame_gt: pd.DataFrame) -> List[float]:
    hip_mid: Dict[int, Tuple[float, float]] = {}
    for row in rows:
        fn = int(row.get("frame_number", 0))
        if _gt_bucket(frame_gt, fn) != "Standing":
            continue
        keypoints = _keypoints_from_row(row)
        visibility = _visibility_from_row(row)
        pose_row = build_pose_row(timestamp=row.get("timestamp"), frame=fn,
                                   keypoints=keypoints, visibility=visibility)
        kp = pose_row["keypoints"]
        hp_l = (kp[46], kp[47])
        hp_r = (kp[48], kp[49])
        if is_landmark_valid(hp_l) and is_landmark_valid(hp_r):
            hip_mid[fn] = ((hp_l[0] + hp_r[0]) / 2.0, (hp_l[1] + hp_r[1]) / 2.0)

    frame_numbers = sorted(hip_mid.keys())
    displacements = []
    for a, b in zip(frame_numbers, frame_numbers[1:]):
        if b == a + 1:
            dx = hip_mid[b][0] - hip_mid[a][0]
            dy = hip_mid[b][1] - hip_mid[a][1]
            displacements.append(float(np.hypot(dx, dy)))
    return displacements


# ------------------------------------------------------------------------------
# Per-clip, per-backend evaluation
# ------------------------------------------------------------------------------

def evaluate_backend_on_clip(clip_id: str, clip_info: dict, rows: List[dict],
                              fps: float, total_frames: int,
                              person_found_flags: List[bool]) -> dict:
    gt_df = load_ground_truth(clip_info["gt_path"])
    frame_gt = build_frame_gt(gt_df, fps, total_frames)
    fall_window = get_fall_window(gt_df, fps)
    has_fall_window = fall_window is not None

    classified = classify_frames(rows, clip_name=clip_id)
    accuracy, confusion, mismatches = score_posture(classified, frame_gt)
    fall_result = score_fall(classified, fall_window)
    per_class = per_class_accuracy(confusion)
    n_scored = int(sum(sum(v.values()) for v in confusion.values()))

    availability = compute_availability(rows, frame_gt, person_found_flags)
    jitter = compute_jitter(rows, frame_gt)

    return {
        "accuracy": accuracy,
        "confusion": confusion,
        "per_class": per_class,
        "fall_result": fall_result,
        "has_fall_window": has_fall_window,
        "n_frames_scored": n_scored,
        "n_mismatches": len(mismatches),
        "availability": availability,
        "jitter_displacements": jitter,
        "total_frames": total_frames,
    }


# ------------------------------------------------------------------------------
# Main run
# ------------------------------------------------------------------------------

def run(mode: str) -> dict:
    print(f"[benchmark_pose] mode={mode}  device_gpu={DEVICE_GPU}  device_cpu={DEVICE_CPU}")

    clips, skipped = discover_all_clips()
    print(f"[benchmark_pose] discovered {len(clips)} usable clips, {len(skipped)} skipped")
    for s in skipped:
        print(f"  SKIPPED [{s['folder']}] {s['clip']}: {s['reason']}")

    clip_ids = sorted(clips.keys())
    if mode == "smoke":
        preferred = ["H0802_Fall_backward_2", "S0722_Standing_1"]
        clip_ids = [c for c in preferred if c in clips] or clip_ids[:2]
        print(f"[benchmark_pose] SMOKE TEST on clips: {clip_ids}")

    results = {
        "device_gpu": DEVICE_GPU,
        "device_cpu": DEVICE_CPU,
        "skipped": skipped,
        "clips": {},          # clip_id -> {folder, clip_name, backends: {backend_name: metrics}}
        "speed": {},          # backend_name -> {clip_id: latency stats}
        "errors": [],
    }

    t_start = time.time()
    for ci, clip_id in enumerate(clip_ids, start=1):
        info = clips[clip_id]
        print(f"[{ci}/{len(clip_ids)}] {clip_id}  ({info['video_path']})")
        clip_entry = {"folder": info["folder"], "clip_name": info["clip_name"], "backends": {}}

        try:
            # ---- MediaPipe baseline ----
            t0 = time.time()
            mp_rows, mp_fps, mp_total = get_mediapipe_rows(clip_id, info["video_path"])
            print(f"    mediapipe extracted: {mp_total} frames @ {mp_fps:.2f}fps "
                  f"({time.time()-t0:.1f}s)")
            mp_person_found = [not np.isnan(r.get("lm_0_x", np.nan)) for r in mp_rows]
            clip_entry["backends"]["mediapipe"] = evaluate_backend_on_clip(
                clip_id, info, mp_rows, mp_fps, mp_total, mp_person_found)

            # ---- YOLO26 models, raw once, thresholds applied cheaply ----
            if DEVICE_GPU is None:
                raise RuntimeError("CUDA not available -- GPU is required for the YOLO correctness pass")

            for model_name in YOLO_MODEL_NAMES:
                weights_path = WEIGHTS_DIR / f"{model_name}.pt"
                t0 = time.time()
                frames_raw, y_fps, y_total, latencies_ms = get_yolo_raw(
                    clip_id, info["video_path"], model_name, weights_path, DEVICE_GPU)
                print(f"    {model_name} (GPU) extracted: {y_total} frames "
                      f"({time.time()-t0:.1f}s, mean {np.mean(latencies_ms):.1f}ms/frame)")

                if abs(y_fps - mp_fps) > 0.5 or y_total != mp_total:
                    results["errors"].append(
                        f"{clip_id}: fps/total_frames mismatch between mediapipe "
                        f"({mp_fps:.2f},{mp_total}) and {model_name} ({y_fps:.2f},{y_total})")

                results["speed"].setdefault(f"{model_name}_gpu", {})[clip_id] = {
                    "latencies_ms": latencies_ms, "n_frames": len(latencies_ms),
                }

                for thr in THRESHOLDS:
                    rows, person_counts = _apply_threshold_and_remap(frames_raw, thr)
                    person_found = [c > 0 for c in person_counts]
                    backend_name = f"{model_name}@{thr}"
                    clip_entry["backends"][backend_name] = evaluate_backend_on_clip(
                        clip_id, info, rows, y_fps, y_total, person_found)

            results["clips"][clip_id] = clip_entry

        except Exception as e:
            tb = traceback.format_exc()
            print(f"    ERROR on {clip_id}: {e}\n{tb}")
            results["errors"].append(f"{clip_id}: {e}")

    print(f"[benchmark_pose] done in {time.time()-t_start:.1f}s")
    return results


def run_cpu_speed_subset() -> dict:
    """Separate, disclosed-subset speed measurement: YOLO on CPU (both
    models) for the small SPEED_SUBSET_CLIP_NAMES set, matching the GPU
    latencies already collected for those same clips during the full run.
    This is additive instrumentation only -- it does not touch any
    correctness metric.
    """
    print("[benchmark_pose] CPU speed subset run")
    clips, _ = discover_all_clips()
    speed = {}
    for clip_id in sorted(SPEED_SUBSET_CLIP_NAMES):
        if clip_id not in clips:
            print(f"    WARNING: speed-subset clip {clip_id} not found among discovered clips, skipping")
            continue
        info = clips[clip_id]
        for model_name in YOLO_MODEL_NAMES:
            weights_path = WEIGHTS_DIR / f"{model_name}.pt"
            t0 = time.time()
            _frames_raw, _fps, _total, latencies_ms = get_yolo_raw(
                clip_id, info["video_path"], model_name, weights_path, DEVICE_CPU)
            print(f"    {clip_id} {model_name} (CPU): {len(latencies_ms)} frames, "
                  f"{time.time()-t0:.1f}s, mean {np.mean(latencies_ms):.1f}ms/frame")
            speed.setdefault(f"{model_name}_cpu", {})[clip_id] = {
                "latencies_ms": latencies_ms, "n_frames": len(latencies_ms),
            }
    return speed


# ------------------------------------------------------------------------------
# JSON-safe serialization (NaN -> None)
# ------------------------------------------------------------------------------

def _json_default(obj):
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if np.isnan(v) else v
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, float) and np.isnan(obj):
        return None
    raise TypeError(f"Cannot serialize {type(obj)}")


def save_results(results: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=_json_default)
    print(f"[benchmark_pose] wrote {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--with_cpu_speed", action="store_true",
                         help="also run the CPU speed-subset pass")
    args = parser.parse_args()

    results = run(args.mode)
    out_path = RESULTS_DIR / f"metrics_{args.mode}.json"
    save_results(results, out_path)

    if args.with_cpu_speed:
        cpu_speed = run_cpu_speed_subset()
        results["speed"].update(cpu_speed)
        save_results(results, out_path)

    print("\n[benchmark_pose] SUMMARY")
    print(f"  clips evaluated: {len(results['clips'])}")
    print(f"  clips skipped:   {len(results['skipped'])}")
    print(f"  errors:          {len(results['errors'])}")
    for e in results["errors"]:
        print(f"    - {e}")


if __name__ == "__main__":
    main()

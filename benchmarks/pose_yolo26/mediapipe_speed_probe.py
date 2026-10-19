"""
mediapipe_speed_probe.py
=========================
evaluate_real_footage.extract_keypoints() does not expose per-frame timing,
and we are not allowed to edit that file to add it. This script duplicates
ONLY the minimal MediaPipe call sequence (same model file, same VIDEO
running mode, same cv2 read loop) so we can time the pose-inference step in
isolation (decode via cap.read() excluded), on the same CPU-only setup the
real pipeline uses. It is NOT used for any correctness metric -- the
accuracy/fall numbers always come from the real, unmodified
evaluate_real_footage.extract_keypoints() + classify_frames(). This file
exists purely to answer the "ms/frame, pose step only" speed question for
MediaPipe, matching how yolo_pose_extract.py times YOLO's model.predict().

Run on the same SPEED_SUBSET_CLIP_NAMES subset used for the YOLO CPU speed
pass, for an apples-to-apples comparison (see benchmark_pose.py).
"""

import json
import sys
import time
from pathlib import Path
from typing import List

import cv2
import mediapipe as mp
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BENCH_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCH_DIR / "results"

MODEL_PATH = str(REPO_ROOT / "models" / "pose_landmarker_full.task")

N_WARMUP_FRAMES = 5  # excluded from latency stats, matches the YOLO warm-up treatment


def measure_mediapipe_speed(video_path: str) -> List[float]:
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
    )
    detector = PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        detector.close()
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    latencies_ms = []
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            ts = frame_count / fps

            t0 = time.perf_counter()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            _result = detector.detect_for_video(mp_image, int(ts * 1000))
            t1 = time.perf_counter()

            if frame_count > N_WARMUP_FRAMES:
                latencies_ms.append((t1 - t0) * 1000.0)
    finally:
        cap.release()
        detector.close()

    return latencies_ms


def main():
    sys.path.insert(0, str(BENCH_DIR))
    from benchmark_pose import discover_all_clips, SPEED_SUBSET_CLIP_NAMES  # noqa: E402

    clips, _skipped = discover_all_clips()
    speed = {}
    for clip_id in sorted(SPEED_SUBSET_CLIP_NAMES):
        if clip_id not in clips:
            print(f"  WARNING: speed-subset clip {clip_id} not found, skipping")
            continue
        video_path = clips[clip_id]["video_path"]
        t0 = time.time()
        latencies_ms = measure_mediapipe_speed(video_path)
        print(f"  {clip_id}: {len(latencies_ms)} frames, {time.time()-t0:.1f}s, "
              f"mean {np.mean(latencies_ms):.1f}ms/frame")
        speed[clip_id] = {"latencies_ms": latencies_ms, "n_frames": len(latencies_ms)}

    out_path = RESULTS_DIR / "mediapipe_speed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(speed, f, indent=2)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

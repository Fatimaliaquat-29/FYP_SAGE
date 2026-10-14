"""
yolo_pose_extract.py
=====================
YOLO26-pose adapter for the SAGE heuristic benchmark. Produces keypoint rows
in the same MediaPipe-33-landmark schema that
evaluate_real_footage.extract_keypoints() produces, so classify_frames() (and
therefore the existing posture/fall heuristic) can consume either source
unmodified.

Two-stage design so a threshold sweep (0.3 / 0.5 / 0.7) never re-runs
inference:
  1. extract_keypoints_yolo_raw() runs the model once per video and returns
     RAW per-frame detections (every person, COCO-17 xy + per-keypoint
     confidence + box confidence) plus per-frame pose-inference latency.
  2. extract_keypoints_yolo() takes that raw result (or computes it if not
     given), picks the highest-box-confidence person per frame, remaps
     COCO-17 -> MediaPipe-33 slots, and applies the confidence threshold.

Frames are read with cv2.VideoCapture the same way
evaluate_real_footage.extract_keypoints() does, so both backends see
identical decoded frames. YOLO is run statelessly per frame: no tracker, no
temporal smoothing (unlike the MediaPipe baseline, which runs in VIDEO mode
with cross-frame tracking).
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

# COCO-17 keypoint index -> MediaPipe-33 landmark index. Everything else
# (face detail, fingers) has no COCO equivalent and stays NaN.
COCO_TO_MP33: Dict[int, int] = {
    0: 0,    # nose
    1: 2,    # left eye
    2: 5,    # right eye
    3: 7,    # left ear
    4: 8,    # right ear
    5: 11,   # left shoulder
    6: 12,   # right shoulder
    7: 13,   # left elbow
    8: 14,   # right elbow
    9: 15,   # left wrist
    10: 16,  # right wrist
    11: 23,  # left hip
    12: 24,  # right hip
    13: 25,  # left knee
    14: 26,  # right knee
    15: 27,  # left ankle
    16: 28,  # right ankle
}

LANDMARK_COUNT = 33

_MODEL_CACHE: Dict[str, object] = {}


def _get_model(weights_path: str):
    from ultralytics import YOLO
    key = str(weights_path)
    if key not in _MODEL_CACHE:
        _MODEL_CACHE[key] = YOLO(key)
    return _MODEL_CACHE[key]


def extract_keypoints_yolo_raw(
    video_path: str,
    weights: str,
    imgsz: int = 640,
    device: str = "cpu",
) -> Tuple[List[dict], float, int, List[float]]:
    """Run YOLO pose once over the whole video.

    Returns (frames_raw, fps, total_frames, latencies_ms).
    frames_raw[i] = {"timestamp", "frame_number", "n_persons", "persons": [...]}
    persons[j] = {"box_conf": float, "xy": (17,2) ndarray normalized [0,1],
                  "kconf": (17,) ndarray}
    latencies_ms is the wall-clock time of the model.predict() call only
    (video decode, i.e. cap.read(), is excluded).
    """
    model = _get_model(weights)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_raw: List[dict] = []
    latencies_ms: List[float] = []
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            ts = frame_count / fps

            t0 = time.perf_counter()
            results = model.predict(frame, imgsz=imgsz, device=device, verbose=False)
            t1 = time.perf_counter()
            latencies_ms.append((t1 - t0) * 1000.0)

            r = results[0]
            persons = []
            if r.keypoints is not None and r.boxes is not None and len(r.boxes) > 0:
                xyn = r.keypoints.xyn.detach().cpu().numpy()          # (N,17,2)
                kconf_t = r.keypoints.conf
                if kconf_t is not None:
                    kconf = kconf_t.detach().cpu().numpy()            # (N,17)
                else:
                    kconf = np.zeros(xyn.shape[:2], dtype=np.float32)
                bconf = r.boxes.conf.detach().cpu().numpy()            # (N,)
                for i in range(xyn.shape[0]):
                    persons.append({
                        "box_conf": float(bconf[i]),
                        "xy": xyn[i],
                        "kconf": kconf[i],
                    })

            frames_raw.append({
                "timestamp": ts,
                "frame_number": frame_count,
                "n_persons": len(persons),
                "persons": persons,
            })
    finally:
        cap.release()

    return frames_raw, fps, (total_frames or frame_count), latencies_ms


def _apply_threshold_and_remap(
    frames_raw: List[dict], kp_conf_threshold: float
) -> Tuple[List[dict], List[int]]:
    """Pick the best-box-confidence person per frame, remap COCO-17 ->
    MediaPipe-33, and drop keypoints below kp_conf_threshold.

    Per the benchmark spec: build_pose_row's own 0.5 visibility gate is tuned
    for MediaPipe's differently-calibrated confidence, so the YOLO threshold
    is applied HERE instead -- sub-threshold points become NaN, and surviving
    points get visibility/presence hard-set to 1.0 so they always pass that
    downstream 0.5 gate regardless of their original YOLO confidence value.
    """
    rows: List[dict] = []
    person_counts: List[int] = []

    for fr in frames_raw:
        row = {"timestamp": fr["timestamp"], "frame_number": fr["frame_number"]}
        for i in range(LANDMARK_COUNT):
            row[f"lm_{i}_x"] = np.nan
            row[f"lm_{i}_y"] = np.nan
            row[f"lm_{i}_z"] = np.nan
            row[f"lm_{i}_visibility"] = np.nan
            row[f"lm_{i}_presence"] = np.nan

        person_counts.append(fr["n_persons"])

        if fr["persons"]:
            best = max(fr["persons"], key=lambda p: p["box_conf"])
            for coco_i, mp_i in COCO_TO_MP33.items():
                x, y = best["xy"][coco_i]
                conf = float(best["kconf"][coco_i])
                if conf < kp_conf_threshold:
                    continue
                row[f"lm_{mp_i}_x"] = float(x)
                row[f"lm_{mp_i}_y"] = float(y)
                row[f"lm_{mp_i}_z"] = np.nan
                row[f"lm_{mp_i}_visibility"] = 1.0
                row[f"lm_{mp_i}_presence"] = 1.0

        rows.append(row)

    return rows, person_counts


def extract_keypoints_yolo(
    video_path: str,
    weights: str,
    imgsz: int = 640,
    device: str = "cpu",
    kp_conf_threshold: float = 0.5,
    raw_cache: Optional[Tuple[List[dict], float, int, List[float]]] = None,
) -> Tuple[List[dict], float, int, List[int]]:
    """YOLO26-pose counterpart of evaluate_real_footage.extract_keypoints().

    Returns (rows, fps, total_frames, person_counts) -- rows has the same
    schema (timestamp, frame_number, lm_{i}_x/_y/_z/_visibility/_presence for
    i in 0..32) the MediaPipe baseline produces, plus person_counts (one int
    per frame: how many people YOLO detected) which the baseline has no
    equivalent of.

    Pass `raw_cache` (the tuple returned by extract_keypoints_yolo_raw) to
    apply a different kp_conf_threshold without re-running inference.
    """
    if raw_cache is None:
        frames_raw, fps, total_frames, _latencies = extract_keypoints_yolo_raw(
            video_path, weights, imgsz=imgsz, device=device
        )
    else:
        frames_raw, fps, total_frames, _latencies = raw_cache

    rows, person_counts = _apply_threshold_and_remap(frames_raw, kp_conf_threshold)
    return rows, fps, total_frames, person_counts

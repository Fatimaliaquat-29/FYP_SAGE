"""
hybrid_evaluate.py
==================
Hybrid (Heuristic OR LSTM) evaluation against the same ground-truth clips
used by evaluate_real_footage.py.

For every clip in test_footage/ it runs THREE parallel fall-detection signals:
  - Heuristic only     (existing pipeline_utils logic)
  - LSTM only          (30-frame rolling window on lstm_posture.keras)
  - Hybrid (OR gate)   (fall_detected if EITHER heuristic OR LSTM fires)

Outputs a side-by-side summary table and per-clip CSV files.

Usage
-----
  python hybrid_evaluate.py --batch_dir test_footage --output_dir results/hybrid
  python hybrid_evaluate.py --video test_footage/normal.mov --ground_truth test_footage/normal_gt.csv
"""

import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import (
    LANDMARK_COUNT,
    build_pose_row,
    classify_posture_and_fall,
    reset_session_state,
)

# Re-use all GT helpers from the existing evaluator
from evaluate_real_footage import (
    load_ground_truth,
    build_frame_gt,
    get_fall_window,
    extract_keypoints,
    score_fall,
    _fmt_fall,
    _needs_flag,
)

MODEL_PATH         = str(REPO_ROOT / "models" / "pose_landmarker_full.task")
LSTM_MODEL_PATH    = REPO_ROOT / "models" / "lstm_posture.keras"
LSTM_ENCODER_PATH  = REPO_ROOT / "models" / "lstm_label_encoder.json"
WINDOW_SIZE        = 30   # must match what the model was trained on
FEATURE_DIM        = 66   # 33 landmarks x (x, y)
FALL_CLASS_NAME    = "Fall"

FLAG_ACCURACY_THRESHOLD = 90.0


# ---------------------------------------------------------------------------
# LSTM loader
# ---------------------------------------------------------------------------

def load_lstm_model():
    """Load the trained LSTM model and its label encoder. Returns (model, fall_idx)."""
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(str(LSTM_MODEL_PATH))
    except Exception as e:
        print(f"  [LSTM] Could not load model: {e}")
        return None, None

    if not LSTM_ENCODER_PATH.exists():
        print(f"  [LSTM] Encoder not found at {LSTM_ENCODER_PATH}")
        return None, None

    with open(LSTM_ENCODER_PATH, "r", encoding="utf-8") as fh:
        encoder = json.load(fh)

    classes  = encoder.get("classes", [])
    fall_idx = classes.index(FALL_CLASS_NAME) if FALL_CLASS_NAME in classes else None
    if fall_idx is None:
        print(f"  [LSTM] '{FALL_CLASS_NAME}' class not found in encoder: {classes}")
        return None, None

    print(f"  [LSTM] Loaded model — classes: {classes}  fall_idx={fall_idx}")
    return model, fall_idx


# ---------------------------------------------------------------------------
# Keypoint → feature vector
# ---------------------------------------------------------------------------

def _row_to_feature(kp_row: dict) -> np.ndarray:
    """Extract the 66-element (x, y) feature vector from a landmark row."""
    feat = np.full(FEATURE_DIM, np.nan, dtype=np.float32)
    for i in range(LANDMARK_COUNT):
        feat[i * 2]     = kp_row.get(f"lm_{i}_x", np.nan)
        feat[i * 2 + 1] = kp_row.get(f"lm_{i}_y", np.nan)
    # Impute NaN with 0 (same strategy as training)
    feat = np.where(np.isnan(feat), 0.0, feat)
    return feat


# ---------------------------------------------------------------------------
# Core hybrid classification
# ---------------------------------------------------------------------------

def classify_frames_hybrid(
    kp_rows: List[dict],
    lstm_model,
    fall_idx: Optional[int],
    clip_name: Optional[str] = None,
    lstm_threshold: float = 0.50,
    lstm_warmup_frames: int = 45,
    lstm_consecutive_frames: int = 6,
) -> List[dict]:
    """
    Run heuristic AND LSTM in lock-step over every frame.

    Parameters
    ----------
    lstm_warmup_frames : int
        Number of frames at the start of a clip during which LSTM predictions
        are suppressed. This prevents the model from firing false positives on
        the very first complete window (frame 30) when a clip opens with the
        subject already in a non-standing posture. Default: 45 (~1.5s @ 30fps).
    lstm_consecutive_frames : int
        Number of consecutive frames the LSTM must predict 'Fall' before the
        signal is actually accepted. Helps filter out short 3-5 frame FP bursts.

    Returns a list of dicts — one per frame — containing:
      fall_heuristic   bool  heuristic-only fall signal
      fall_lstm        bool  LSTM-only fall signal (False if model unavailable)
      fall_hybrid      bool  OR gate of the two signals
      lstm_fall_prob   float probability assigned to 'Fall' class by LSTM
      posture_label    str   heuristic posture label
    """
    reset_session_state()
    previous_rows: List[dict] = []
    # Rolling buffer of feature vectors for the LSTM window
    window_buffer: deque = deque(maxlen=WINDOW_SIZE)
    results = []
    lstm_available = lstm_model is not None and fall_idx is not None
    lstm_consecutive_count = 0

    for kp_row in kp_rows:
        # ── Build heuristic keypoint row ─────────────────────────────────────
        flat_kps = []
        for i in range(LANDMARK_COUNT):
            flat_kps.append(kp_row.get(f"lm_{i}_x", np.nan))
            flat_kps.append(kp_row.get(f"lm_{i}_y", np.nan))

        pose_row = build_pose_row(
            timestamp=kp_row.get("timestamp"),
            frame=int(kp_row.get("frame_number", 0)),
            keypoints=flat_kps,
        )
        classification = classify_posture_and_fall(pose_row, previous_rows=previous_rows)
        pose_row.update(classification)
        previous_rows.append(pose_row)

        fall_heuristic = bool(pose_row.get("fall_detected", False))

        # ── Feed LSTM window buffer ───────────────────────────────────────────
        feat = _row_to_feature(kp_row)
        window_buffer.append(feat)

        lstm_fall_prob = 0.0
        fall_lstm      = False

        frame_number = int(kp_row.get("frame_number", 0))
        in_warmup    = frame_number <= lstm_warmup_frames

        if lstm_available and len(window_buffer) == WINDOW_SIZE and not in_warmup:
            window_arr = np.array(window_buffer, dtype=np.float32)[np.newaxis]  # (1, 30, 66)
            probs      = lstm_model.predict(window_arr, verbose=0)[0]           # (n_classes,)
            lstm_fall_prob = float(probs[fall_idx])
            
            if lstm_fall_prob >= lstm_threshold:
                lstm_consecutive_count += 1
            else:
                lstm_consecutive_count = 0
                
            fall_lstm = lstm_consecutive_count >= lstm_consecutive_frames

        # ── OR gate ──────────────────────────────────────────────────────────
        fall_hybrid = fall_heuristic or fall_lstm

        results.append({
            "frame_number":    kp_row.get("frame_number", 0),
            "timestamp":       kp_row.get("timestamp", 0.0),
            "posture_label":   pose_row.get("posture_label", "Unknown"),
            "fall_heuristic":  fall_heuristic,
            "fall_lstm":       fall_lstm,
            "fall_hybrid":     fall_hybrid,
            "lstm_fall_prob":  round(lstm_fall_prob, 4),
            "confidence":      pose_row.get("confidence", 0.0),
        })

    return results


# ---------------------------------------------------------------------------
# Scoring helpers (work on a custom fall_detected column)
# ---------------------------------------------------------------------------

def _score_fall_from_results(
    results: List[dict],
    fall_key: str,
    fall_window: Optional[Tuple[int, int]],
) -> dict:
    """Same logic as evaluate_real_footage.score_fall but reads an arbitrary key."""
    fall_frames = [r["frame_number"] for r in results if r.get(fall_key)]

    if fall_window is None:
        if fall_frames:
            return {"result": "false_positive", "latency": None, "fp_frames": fall_frames}
        return {"result": "no_fall", "latency": None, "fp_frames": []}

    window_start, window_end = fall_window
    inside  = [f for f in fall_frames if window_start <= f <= window_end]
    outside = [f for f in fall_frames if f < window_start or f > window_end]

    if inside:
        return {"result": "true_positive", "latency": inside[0] - window_start, "fp_frames": outside}
    if outside:
        return {"result": "false_positive", "latency": None, "fp_frames": outside}
    return {"result": "false_negative", "latency": None, "fp_frames": []}


# ---------------------------------------------------------------------------
# Per-clip evaluation
# ---------------------------------------------------------------------------

def evaluate_clip_hybrid(
    video_path: str,
    gt_path: str,
    clip_name: str,
    output_dir: Path,
    lstm_model,
    fall_idx: Optional[int],
    lstm_threshold: float = 0.50,
    lstm_warmup_frames: int = 45,
    lstm_consecutive_frames: int = 6,
) -> dict:
    print(f"\n[{clip_name}] Extracting keypoints from: {video_path}")
    kp_rows, fps, total_frames = extract_keypoints(video_path)
    print(f"  {total_frames} frames @ {fps:.2f} fps")

    print(f"[{clip_name}] Running hybrid classification...")
    results = classify_frames_hybrid(
        kp_rows, lstm_model, fall_idx, clip_name=clip_name,
        lstm_threshold=lstm_threshold,
        lstm_warmup_frames=lstm_warmup_frames,
        lstm_consecutive_frames=lstm_consecutive_frames,
    )

    gt_df       = load_ground_truth(gt_path)
    fall_window = get_fall_window(gt_df, fps)

    fall_h = _score_fall_from_results(results, "fall_heuristic", fall_window)
    fall_l = _score_fall_from_results(results, "fall_lstm",      fall_window)
    fall_y = _score_fall_from_results(results, "fall_hybrid",    fall_window)

    print(f"  Heuristic : {_fmt_fall(fall_h)}")
    print(f"  LSTM      : {_fmt_fall(fall_l)}")
    print(f"  Hybrid    : {_fmt_fall(fall_y)}")

    # Save per-frame CSV
    csv_path = output_dir / f"{clip_name}_hybrid.csv"
    pd.DataFrame(results).to_csv(csv_path, index=False)
    print(f"  Per-frame CSV: {csv_path}")

    return {
        "clip_name":   clip_name,
        "fall_h":      fall_h,
        "fall_l":      fall_l,
        "fall_hybrid": fall_y,
    }


# ---------------------------------------------------------------------------
# Summary reporting
# ---------------------------------------------------------------------------

def _result_symbol(r: dict) -> str:
    res = r["result"]
    if res == "true_positive":
        return f"TP +{r['latency']}f"
    if res == "false_negative":
        return "FN"
    if res == "false_positive":
        fps_str = ",".join(str(f) for f in r["fp_frames"][:3])
        return f"FP [{fps_str}]"
    return "-"


def print_summary(summary_rows: List[dict]):
    w = 30
    print(f"\n{'='*85}")
    print(f"  HYBRID EVALUATION SUMMARY")
    print(f"{'='*85}")
    print(f"  {'Clip':<{w}} {'Heuristic':<18} {'LSTM':<18} {'Hybrid (OR)':<18}")
    print(f"  {'-'*w} {'-'*18} {'-'*18} {'-'*18}")
    for r in summary_rows:
        print(
            f"  {r['clip_name']:<{w}} "
            f"{_result_symbol(r['fall_h']):<18} "
            f"{_result_symbol(r['fall_l']):<18} "
            f"{_result_symbol(r['fall_hybrid']):<18}"
        )
    print(f"{'='*85}")

    # Count TP / FN / FP per mode
    for mode_key, label in [("fall_h", "Heuristic"), ("fall_l", "LSTM"), ("fall_hybrid", "Hybrid")]:
        tp = sum(1 for r in summary_rows if r[mode_key]["result"] == "true_positive")
        fn = sum(1 for r in summary_rows if r[mode_key]["result"] == "false_negative")
        fp = sum(1 for r in summary_rows if r[mode_key]["result"] == "false_positive")
        nd = sum(1 for r in summary_rows if r[mode_key]["result"] == "no_fall")
        print(f"  {label:<12}: TP={tp}  FN={fn}  FP={fp}  no_fall={nd}")
    print(f"{'='*85}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SAGE Hybrid (Heuristic + LSTM) Evaluation")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--batch_dir", type=str, default=None)
    mode.add_argument("--video",     type=str, default=None)
    parser.add_argument("--ground_truth",   type=str, default=None)
    parser.add_argument("--output_dir",     type=str, default="results/hybrid")
    parser.add_argument("--lstm_threshold", type=float, default=0.50,
                        help="LSTM fall-probability threshold (default 0.50)")
    parser.add_argument("--lstm_warmup", type=int, default=45,
                        help="Frames to suppress LSTM at start of clip (default 45, ~1.5s @ 30fps)")
    parser.add_argument("--lstm_consecutive", type=int, default=6,
                        help="Consecutive Fall predictions required (default 6)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading LSTM model...")
    lstm_model, fall_idx = load_lstm_model()
    if lstm_model is None:
        print("WARNING: LSTM model unavailable — LSTM column will be all False.")

    if args.batch_dir:
        from evaluate_real_footage import discover_clips
        clips = discover_clips(args.batch_dir)
        if not clips:
            print(f"No clips found in {args.batch_dir}")
            sys.exit(1)
        print(f"Found {len(clips)} clip(s) in {args.batch_dir}")
        summary_rows = []
        for video_path, gt_path, clip_name in clips:
            row = evaluate_clip_hybrid(
                video_path, gt_path, clip_name, output_dir,
                lstm_model, fall_idx, args.lstm_threshold,
                lstm_warmup_frames=args.lstm_warmup,
                lstm_consecutive_frames=args.lstm_consecutive,
            )
            summary_rows.append(row)
        print_summary(summary_rows)

    elif args.video:
        if not args.ground_truth:
            parser.error("--ground_truth required in single-clip mode")
        clip_name = Path(args.video).stem
        row = evaluate_clip_hybrid(
            args.video, args.ground_truth, clip_name, output_dir,
            lstm_model, fall_idx, args.lstm_threshold,
            lstm_warmup_frames=args.lstm_warmup,
            lstm_consecutive_frames=args.lstm_consecutive,
        )
        print_summary([row])

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

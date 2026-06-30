"""
lstm_dataset.py
===============
Builds a sliding-window dataset from raw pose keypoints for LSTM training.

Input:
    data/pose_keypoints.csv   – 33 landmark (x, y) pairs per frame (66 features)
    data/posture_output.csv   – rule-based labels (posture_label, fall_detected)
                                used as weak supervision

Output:
    data/lstm_dataset.npz
        X      – shape (N_windows, window_size, 66)
        y      – shape (N_windows,)  integer class index
        classes – array of label strings, index matches y

Usage:
    python src/posture/lstm/lstm_dataset.py [--window-size 30] [--step 1]
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = REPO_ROOT / "data"
POSE_KEYPOINTS_CSV = DATA_DIR / "processed_keypoints" / "pose_keypoints.csv"
POSTURE_OUTPUT_CSV = DATA_DIR / "processed_keypoints" / "posture_output.csv"
LSTM_DATASET_NPZ = DATA_DIR / "datasets" / "lstm_dataset.npz"

LANDMARK_COUNT = 33
FEATURE_DIM = LANDMARK_COUNT * 2  # 66: x1,y1 ... x33,y33

# Class labels (alphabetically sorted for reproducibility)
CLASSES = np.array(["Fall", "Lying", "Sitting", "Standing"])
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

def _make_standing_kps(noise: float = 0.01) -> np.ndarray:
    """33-landmark keypoints for an upright standing pose."""
    kps = np.full(FEATURE_DIM, np.nan)
    # shoulders (idx 11/12 → cols 22-25)
    kps[22], kps[23] = 0.48, 0.22
    kps[24], kps[25] = 0.52, 0.22
    # hips (idx 23/24 → cols 46-49)
    kps[46], kps[47] = 0.49, 0.52
    kps[48], kps[49] = 0.51, 0.52
    # knees (idx 25/26 → cols 50-53)
    kps[50], kps[51] = 0.49, 0.66
    kps[52], kps[53] = 0.51, 0.66
    # ankles (idx 27/28 → cols 54-57)
    kps[54], kps[55] = 0.49, 0.80
    kps[56], kps[57] = 0.51, 0.80
    kps += np.random.randn(FEATURE_DIM) * noise
    return kps


def _make_sitting_kps(noise: float = 0.01) -> np.ndarray:
    """33-landmark keypoints for a seated pose (compressed body height)."""
    kps = np.full(FEATURE_DIM, np.nan)
    kps[22], kps[23] = 0.48, 0.32
    kps[24], kps[25] = 0.52, 0.32
    kps[46], kps[47] = 0.49, 0.50
    kps[48], kps[49] = 0.51, 0.50
    kps[50], kps[51] = 0.49, 0.60
    kps[52], kps[53] = 0.51, 0.60
    kps[54], kps[55] = 0.49, 0.70
    kps[56], kps[57] = 0.51, 0.70
    kps += np.random.randn(FEATURE_DIM) * noise
    return kps


def _make_lying_kps(noise: float = 0.01) -> np.ndarray:
    """33-landmark keypoints for a lying (horizontal) pose."""
    kps = np.full(FEATURE_DIM, np.nan)
    kps[22], kps[23] = 0.20, 0.75
    kps[24], kps[25] = 0.22, 0.75
    kps[46], kps[47] = 0.50, 0.75
    kps[48], kps[49] = 0.52, 0.75
    kps[50], kps[51] = 0.65, 0.75
    kps[52], kps[53] = 0.67, 0.75
    kps[54], kps[55] = 0.79, 0.75
    kps[56], kps[57] = 0.81, 0.75
    kps += np.random.randn(FEATURE_DIM) * noise
    return kps


def _make_fall_sequence(window_size: int) -> np.ndarray:
    """
    A window where the person rapidly transitions from standing to lying.
    The transition happens in the middle of the window.
    """
    frames = []
    transition_start = window_size // 3
    transition_end = window_size * 2 // 3

    for i in range(window_size):
        if i < transition_start:
            # Standing
            kps = _make_standing_kps(noise=0.005)
        elif i < transition_end:
            # Rapid mid-fall: interpolate between standing and lying keypoints
            t = (i - transition_start) / max(transition_end - transition_start, 1)
            stand = _make_standing_kps(noise=0.005)
            lie = _make_lying_kps(noise=0.005)
            # Replace NaNs with 0 for interpolation
            stand_clean = np.where(np.isnan(stand), 0.0, stand)
            lie_clean = np.where(np.isnan(lie), 0.0, lie)
            kps = (1.0 - t) * stand_clean + t * lie_clean
            kps += np.random.randn(FEATURE_DIM) * 0.02  # more noise during fall
        else:
            # Lying
            kps = _make_lying_kps(noise=0.005)
        frames.append(kps)
    return np.array(frames)  # (window_size, 66)


def generate_synthetic_windows(
    window_size: int,
    n_per_class: int = 800,
    rng_seed: int = 42,
) -> tuple:
    """
    Generate n_per_class synthetic sliding-window samples per class.

    Returns
    -------
    X : np.ndarray of shape (n_per_class * 4, window_size, 66)
    y : np.ndarray of shape (n_per_class * 4,)  integer labels
    """
    np.random.seed(rng_seed)
    X_parts, y_parts = [], []

    # ── Standing ──────────────────────────────────────────────────────────────
    windows = np.array(
        [np.stack([_make_standing_kps() for _ in range(window_size)]) for _ in range(n_per_class)]
    )
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Standing"]))

    # ── Sitting ───────────────────────────────────────────────────────────────
    windows = np.array(
        [np.stack([_make_sitting_kps() for _ in range(window_size)]) for _ in range(n_per_class)]
    )
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Sitting"]))

    # ── Lying ─────────────────────────────────────────────────────────────────
    windows = np.array(
        [np.stack([_make_lying_kps() for _ in range(window_size)]) for _ in range(n_per_class)]
    )
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Lying"]))

    # ── Fall ──────────────────────────────────────────────────────────────────
    windows = np.array([_make_fall_sequence(window_size) for _ in range(n_per_class)])
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Fall"]))

    X = np.concatenate(X_parts, axis=0)
    y = np.concatenate(y_parts, axis=0)
    return X, y


# ---------------------------------------------------------------------------
# Real-data processing
# ---------------------------------------------------------------------------

def _extract_keypoint_array(df: pd.DataFrame) -> np.ndarray:
    """
    Extract the 66-column keypoint matrix (x1..x33, y1..y33) from the
    pose_keypoints DataFrame as a (N_frames, 66) float array.
    NaN values are preserved; the trainer will impute them.
    """
    cols = []
    for i in range(1, LANDMARK_COUNT + 1):
        cols.extend([f"x{i}", f"y{i}"])
    available = [c for c in cols if c in df.columns]
    if not available:
        return np.empty((len(df), FEATURE_DIM), dtype=np.float32)
    arr = df[available].values.astype(np.float32)
    # Pad to FEATURE_DIM if some landmark columns are missing
    if arr.shape[1] < FEATURE_DIM:
        pad = np.full((len(df), FEATURE_DIM - arr.shape[1]), np.nan, dtype=np.float32)
        arr = np.concatenate([arr, pad], axis=1)
    return arr


def _derive_label(posture_label: str, fall_detected) -> int:
    """Map a row's posture + fall flag to a class index."""
    if str(fall_detected).lower() in ("true", "1", "yes"):
        return CLASS_TO_IDX["Fall"]
    label = str(posture_label).strip().capitalize()
    return CLASS_TO_IDX.get(label, CLASS_TO_IDX["Standing"])


def build_windows_from_real_data(
    kp_csv: Path,
    out_csv: Path,
    window_size: int = 30,
    step: int = 1,
) -> tuple:
    """
    Load real keypoints CSV and posture output CSV, join on 'frame',
    and produce sliding-window samples per sequence_id.

    Returns
    -------
    X : np.ndarray of shape (N_windows, window_size, 66)  or empty
    y : np.ndarray of shape (N_windows,)
    """
    if not kp_csv.exists():
        print(f"  [dataset] {kp_csv} not found – skipping this real data source.")
        return np.empty((0, window_size, FEATURE_DIM), dtype=np.float32), np.empty(0, dtype=np.int32)

    try:
        kp_df = pd.read_csv(kp_csv)
    except Exception as e:
        print(f"  [dataset] Could not read {kp_csv}: {e}")
        return np.empty((0, window_size, FEATURE_DIM), dtype=np.float32), np.empty(0, dtype=np.int32)

    frame_col = "frame" if "frame" in kp_df.columns else ("frame_number" if "frame_number" in kp_df.columns else None)
    if frame_col is None:
        print("  [dataset] No frame column found in CSV – skipping.")
        return np.empty((0, window_size, FEATURE_DIM), dtype=np.float32), np.empty(0, dtype=np.int32)
    kp_df = kp_df.rename(columns={frame_col: "frame"})

    # Check for sequence_id, default to 'single_sequence' if not present
    if "sequence_id" not in kp_df.columns:
        kp_df["sequence_id"] = "single_sequence"

    # Merge labels if available
    if out_csv.exists():
        try:
            out_df = pd.read_csv(out_csv)
            out_frame_col = "frame" if "frame" in out_df.columns else ("frame_number" if "frame_number" in out_df.columns else None)
            if out_frame_col:
                out_df = out_df.rename(columns={out_frame_col: "frame"})
                label_cols = ["frame"]
                if "sequence_id" in out_df.columns:
                    label_cols.append("sequence_id")
                if "posture_label" in out_df.columns:
                    label_cols.append("posture_label")
                if "posture" in out_df.columns and "posture_label" not in label_cols:
                    label_cols.append("posture")
                    out_df = out_df.rename(columns={"posture": "posture_label"})
                if "fall_detected" in out_df.columns:
                    label_cols.append("fall_detected")
                
                merge_on = ["sequence_id", "frame"] if "sequence_id" in label_cols else ["frame"]
                out_df = out_df[label_cols].drop_duplicates(merge_on)
                kp_df = kp_df.merge(out_df, on=merge_on, how="left", suffixes=("", "_out"))
        except Exception as e:
            print(f"  [dataset] Could not merge posture labels: {e}")

    if "posture_label" not in kp_df.columns:
        kp_df["posture_label"] = "Standing"
    if "fall_detected" not in kp_df.columns:
        kp_df["fall_detected"] = False

    X_list, y_list = [], []
    
    # Process sliding windows per sequence to prevent cross-sequence bleeding
    for seq_id, seq_df in kp_df.groupby("sequence_id"):
        seq_df = seq_df.sort_values("frame").reset_index(drop=True)
        kp_arr = _extract_keypoint_array(seq_df)
        labels = seq_df.apply(
            lambda r: _derive_label(r["posture_label"], r.get("fall_detected", False)), axis=1
        ).values.astype(np.int32)

        n_frames = len(kp_arr)
        if n_frames < window_size:
            continue

        for start in range(0, n_frames - window_size + 1, step):
            window = kp_arr[start: start + window_size]
            label = labels[start + window_size - 1]
            X_list.append(window)
            y_list.append(label)

    X = np.array(X_list, dtype=np.float32) if X_list else np.empty((0, window_size, FEATURE_DIM), dtype=np.float32)
    y = np.array(y_list, dtype=np.int32) if y_list else np.empty(0, dtype=np.int32)
    
    print(f"  [dataset] Source ({kp_csv.name}): {len(X)} windows from {len(kp_df)} frames across {kp_df['sequence_id'].nunique()} sequences.")
    return X, y


# ---------------------------------------------------------------------------
# NaN imputation
# ---------------------------------------------------------------------------

def impute_nan(X: np.ndarray) -> np.ndarray:
    """
    Replace NaN values in X (N, window_size, 66) with per-feature column median.
    Columns that are entirely NaN are set to 0.
    """
    flat = X.reshape(-1, X.shape[-1])  # (N * window_size, 66)
    for col_idx in range(flat.shape[1]):
        col = flat[:, col_idx]
        nan_mask = np.isnan(col)
        if nan_mask.all():
            flat[:, col_idx] = 0.0
        elif nan_mask.any():
            flat[:, col_idx] = np.where(nan_mask, np.nanmedian(col), col)
    return flat.reshape(X.shape)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_dataset(
    window_size: int = 30,
    step: int = 1,
    n_synthetic: int = 800,
    output_path: Path = LSTM_DATASET_NPZ,
) -> tuple:
    """
    Full dataset build:
      1. Load real keypoint data (if available)
      2. Append synthetic windows
      3. Impute NaNs
      4. Shuffle and save

    Returns X, y, CLASSES
    """
    print("=" * 55)
    print("  LSTM Dataset Builder")
    print("=" * 55)
    print(f"  Window size  : {window_size} frames")
    print(f"  Step size    : {step}")
    print(f"  Synthetic/cls: {n_synthetic}")

    # Real data
    X_real_list, y_real_list = [], []
    real_sources = [
        (DATA_DIR / "processed_keypoints" / "real_pose_keypoints.csv", DATA_DIR / "processed_keypoints" / "real_posture_output.csv"),
        (DATA_DIR / "processed_keypoints" / "pose_keypoints.csv", DATA_DIR / "processed_keypoints" / "posture_output.csv")
    ]
    
    for kp_csv, out_csv in real_sources:
        X_r, y_r = build_windows_from_real_data(
            kp_csv=kp_csv, 
            out_csv=out_csv, 
            window_size=window_size, 
            step=step
        )
        if len(X_r) > 0:
            X_real_list.append(X_r)
            y_real_list.append(y_r)
            
    if X_real_list:
        X_real = np.concatenate(X_real_list, axis=0)
        y_real = np.concatenate(y_real_list, axis=0)
    else:
        X_real = np.empty((0, window_size, FEATURE_DIM), dtype=np.float32)
        y_real = np.empty(0, dtype=np.int32)

    # Synthetic data
    print("  Generating synthetic windows…")
    X_syn, y_syn = generate_synthetic_windows(window_size=window_size, n_per_class=n_synthetic)

    # Combine
    if len(X_real) > 0:
        X = np.concatenate([X_real, X_syn], axis=0).astype(np.float32)
        y = np.concatenate([y_real, y_syn], axis=0).astype(np.int32)
        print(f"  Combined     : {len(X_real)} real + {len(X_syn)} synthetic = {len(X)} total windows")
    else:
        X = X_syn.astype(np.float32)
        y = y_syn.astype(np.int32)
        print(f"  Synthetic only: {len(X)} total windows")

    # Impute NaNs
    print("  Imputing NaN values…")
    X = impute_nan(X)

    # Shuffle
    rng = np.random.default_rng(seed=0)
    idx = rng.permutation(len(X))
    X, y = X[idx], y[idx]

    # Class distribution
    print("\n  Class distribution:")
    for i, cls in enumerate(CLASSES):
        count = int((y == i).sum())
        print(f"    {cls:<10}: {count:>6} windows ({100*count/len(y):.1f}%)")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(output_path), X=X, y=y, classes=CLASSES)
    print(f"\n  Saved -> {output_path}")
    print("=" * 55)

    return X, y, CLASSES


def main():
    parser = argparse.ArgumentParser(description="LSTM Posture Dataset Builder")
    parser.add_argument("--window-size", type=int, default=30, help="Sliding window length in frames (default: 30)")
    parser.add_argument("--step", type=int, default=1, help="Sliding window step (default: 1)")
    parser.add_argument("--synthetic", type=int, default=800, help="Synthetic samples per class (default: 800)")
    parser.add_argument("--output", type=str, default=str(LSTM_DATASET_NPZ), help="Output .npz path")
    args = parser.parse_args()

    build_dataset(
        window_size=args.window_size,
        step=args.step,
        n_synthetic=args.synthetic,
        output_path=Path(args.output),
    )


if __name__ == "__main__":
    main()

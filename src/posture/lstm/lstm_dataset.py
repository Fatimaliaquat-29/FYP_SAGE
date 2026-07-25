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

from src.posture.lstm import lstm_features as lf

DATA_DIR = REPO_ROOT / "data"
POSE_KEYPOINTS_CSV = DATA_DIR / "processed_keypoints" / "pose_keypoints.csv"
POSTURE_OUTPUT_CSV = DATA_DIR / "processed_keypoints" / "posture_output.csv"
LSTM_DATASET_NPZ = DATA_DIR / "lstm_dataset.npz"

LANDMARK_COUNT = 33
RAW_FEATURE_DIM = LANDMARK_COUNT * 2  # 66: x1,y1 ... x33,y33 (raw screen-space)
FEATURE_DIM = lf.FEATURE_DIM          # 132: normalized position + velocity (model input)

# Class labels (alphabetically sorted for reproducibility)
CLASSES = np.array(["Fall", "Lying", "Sitting", "Standing", "Unknown"])
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}


# ---------------------------------------------------------------------------
# Synthetic data generation
#
# Templates are expressed directly in NORMALIZED space (hip-mid at the
# origin, torso length == 1 unit, matching lstm_features.normalize_frame)
# rather than raw screen coordinates. This makes them automatically valid
# regardless of camera distance/framing -- the exact generalization gap
# that let the raw-coordinate model confuse "far from camera" with "lying
# down" (see lstm_features.py docstring). Only shoulders/hips/knees/ankles
# are populated; all other landmarks stay NaN, same as before.
# ---------------------------------------------------------------------------

def _make_standing_kps(noise: float = 0.03) -> np.ndarray:
    """Normalized-space keypoints for an upright standing pose: legs straight,
    torso vertical (shoulder-mid directly above hip-mid)."""
    kps = np.full(RAW_FEATURE_DIM, np.nan)
    kps[22], kps[23] = -0.15, -1.0   # left shoulder
    kps[24], kps[25] = 0.15, -1.0    # right shoulder
    kps[46], kps[47] = -0.10, 0.0    # left hip
    kps[48], kps[49] = 0.10, 0.0     # right hip
    kps[50], kps[51] = -0.10, 1.3    # left knee
    kps[52], kps[53] = 0.10, 1.3     # right knee
    kps[54], kps[55] = -0.10, 2.6    # left ankle
    kps[56], kps[57] = 0.10, 2.6     # right ankle
    kps += np.random.randn(RAW_FEATURE_DIM) * noise
    return kps


def _make_sitting_kps(noise: float = 0.03) -> np.ndarray:
    """Normalized-space keypoints for a seated pose: torso still roughly
    vertical, but thighs folded forward so knees sit near hip height with a
    large horizontal offset instead of straight below."""
    kps = np.full(RAW_FEATURE_DIM, np.nan)
    kps[22], kps[23] = -0.15, -1.0   # left shoulder
    kps[24], kps[25] = 0.15, -1.0    # right shoulder
    kps[46], kps[47] = -0.10, 0.0    # left hip
    kps[48], kps[49] = 0.10, 0.0     # right hip
    kps[50], kps[51] = 0.85, 0.15    # left knee (forward, folded)
    kps[52], kps[53] = 1.05, 0.15    # right knee
    kps[54], kps[55] = 0.85, 1.45    # left ankle (down from knee)
    kps[56], kps[57] = 1.05, 1.45    # right ankle
    kps += np.random.randn(RAW_FEATURE_DIM) * noise
    return kps


def _make_lying_kps(noise: float = 0.03) -> np.ndarray:
    """Normalized-space keypoints for a lying (horizontal) pose: torso and
    legs extend sideways (large x offset) instead of vertically."""
    kps = np.full(RAW_FEATURE_DIM, np.nan)
    kps[22], kps[23] = -1.0, -0.05   # left shoulder
    kps[24], kps[25] = -1.0, 0.05    # right shoulder
    kps[46], kps[47] = -0.10, -0.05  # left hip
    kps[48], kps[49] = 0.10, 0.05    # right hip
    kps[50], kps[51] = 1.0, -0.05    # left knee
    kps[52], kps[53] = 1.0, 0.05     # right knee
    kps[54], kps[55] = 2.0, -0.05    # left ankle
    kps[56], kps[57] = 2.0, 0.05     # right ankle
    kps += np.random.randn(RAW_FEATURE_DIM) * noise
    return kps


def _make_fall_sequence(window_size: int) -> np.ndarray:
    """
    A window (in normalized space) where the person rapidly transitions
    from standing to lying. The transition happens in the middle of the
    window, giving the Fall class an explicit, learnable motion signature
    once lf.add_velocity() is applied on top.
    """
    frames = []
    transition_start = window_size // 3
    transition_end = window_size * 2 // 3

    for i in range(window_size):
        if i < transition_start:
            kps = _make_standing_kps(noise=0.015)
        elif i < transition_end:
            t = (i - transition_start) / max(transition_end - transition_start, 1)
            stand = _make_standing_kps(noise=0.015)
            lie = _make_lying_kps(noise=0.015)
            stand_clean = np.where(np.isnan(stand), 0.0, stand)
            lie_clean = np.where(np.isnan(lie), 0.0, lie)
            kps = (1.0 - t) * stand_clean + t * lie_clean
            kps += np.random.randn(RAW_FEATURE_DIM) * 0.04  # more noise during fall
        else:
            kps = _make_lying_kps(noise=0.015)
        frames.append(kps)
    return np.array(frames)  # (window_size, 66) normalized-space


def generate_synthetic_windows(
    window_size: int,
    n_per_class: int = 800,
    rng_seed: int = 42,
) -> tuple:
    """
    Generate n_per_class synthetic sliding-window samples per class.

    Returns
    -------
    X : np.ndarray of shape (n_per_class * 4, window_size, 132)
    y : np.ndarray of shape (n_per_class * 4,)  integer labels
    g : np.ndarray of shape (n_per_class * 4,)  string sequence ids
    """
    np.random.seed(rng_seed)
    X_parts, y_parts, g_parts = [], [], []

    # ── Standing ──────────────────────────────────────────────────────────────
    windows = np.array(
        [np.stack([_make_standing_kps() for _ in range(window_size)]) for _ in range(n_per_class)]
    )
    windows = np.stack([lf.add_velocity(w) for w in windows], axis=0)
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Standing"]))
    g_parts.append(np.array([f"syn_stand_{i}" for i in range(n_per_class)]))

    # ── Sitting ───────────────────────────────────────────────────────────────
    windows = np.array(
        [np.stack([_make_sitting_kps() for _ in range(window_size)]) for _ in range(n_per_class)]
    )
    windows = np.stack([lf.add_velocity(w) for w in windows], axis=0)
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Sitting"]))
    g_parts.append(np.array([f"syn_sit_{i}" for i in range(n_per_class)]))

    # ── Lying ─────────────────────────────────────────────────────────────────
    windows = np.array(
        [np.stack([_make_lying_kps() for _ in range(window_size)]) for _ in range(n_per_class)]
    )
    windows = np.stack([lf.add_velocity(w) for w in windows], axis=0)
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Lying"]))
    g_parts.append(np.array([f"syn_lie_{i}" for i in range(n_per_class)]))

    # ── Fall ──────────────────────────────────────────────────────────────────
    windows = np.array([_make_fall_sequence(window_size) for _ in range(n_per_class)])
    windows = np.stack([lf.add_velocity(w) for w in windows], axis=0)
    X_parts.append(windows)
    y_parts.append(np.full(n_per_class, CLASS_TO_IDX["Fall"]))
    g_parts.append(np.array([f"syn_fall_{i}" for i in range(n_per_class)]))

    X = np.concatenate(X_parts, axis=0)
    y = np.concatenate(y_parts, axis=0)
    g = np.concatenate(g_parts, axis=0)
    return X, y, g


# ---------------------------------------------------------------------------
# Real-data processing
# ---------------------------------------------------------------------------

def _extract_keypoint_array(df: pd.DataFrame) -> np.ndarray:
    """
    Extract the 66-column RAW keypoint matrix (x1..x33, y1..y33) from the
    pose_keypoints DataFrame as a (N_frames, 66) float array.
    NaN values are preserved; lstm_features.build_features_from_raw_sequence
    normalizes and imputes them downstream.
    """
    cols = []
    for i in range(1, LANDMARK_COUNT + 1):
        cols.extend([f"x{i}", f"y{i}"])
    available = [c for c in cols if c in df.columns]
    if not available:
        return np.empty((len(df), RAW_FEATURE_DIM), dtype=np.float32)
    arr = df[available].values.astype(np.float32)
    # Pad to RAW_FEATURE_DIM if some landmark columns are missing
    if arr.shape[1] < RAW_FEATURE_DIM:
        pad = np.full((len(df), RAW_FEATURE_DIM - arr.shape[1]), np.nan, dtype=np.float32)
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
    g : np.ndarray of shape (N_windows,) string sequence ids
    """
    if not kp_csv.exists():
        print(f"  [dataset] {kp_csv} not found – skipping this real data source.")
        return np.empty((0, window_size, FEATURE_DIM), dtype=np.float32), np.empty(0, dtype=np.int32), np.empty(0, dtype=object)

    try:
        kp_df = pd.read_csv(kp_csv, low_memory=False)
    except Exception as e:
        print(f"  [dataset] Could not read {kp_csv}: {e}")
        return np.empty((0, window_size, FEATURE_DIM), dtype=np.float32), np.empty(0, dtype=np.int32), np.empty(0, dtype=object)

    frame_col = "frame" if "frame" in kp_df.columns else ("frame_number" if "frame_number" in kp_df.columns else None)
    if frame_col is None:
        print("  [dataset] No frame column found in CSV – skipping.")
        return np.empty((0, window_size, FEATURE_DIM), dtype=np.float32), np.empty(0, dtype=np.int32), np.empty(0, dtype=object)
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

    X_list, y_list, g_list = [], [], []

    # Process sliding windows per sequence to prevent cross-sequence bleeding
    for seq_id, seq_df in kp_df.groupby("sequence_id"):
        seq_df = seq_df.sort_values("frame").reset_index(drop=True)
        kp_arr = _extract_keypoint_array(seq_df)
        # Normalize (hip-centered, torso-scaled) + attach velocity BEFORE
        # windowing, across the full sequence, so every window position
        # (including the first row of a window) gets a real velocity value
        # computed from genuine adjacent frames rather than a zero-padded
        # window boundary.
        feat_arr = lf.build_features_from_raw_sequence(kp_arr)
        labels = seq_df.apply(
            lambda r: _derive_label(r["posture_label"], r.get("fall_detected", False)), axis=1
        ).values.astype(np.int32)

        n_frames = len(feat_arr)
        if n_frames < window_size:
            continue

        for start in range(0, n_frames - window_size + 1, step):
            window = feat_arr[start: start + window_size]
            window_labels = labels[start: start + window_size]

            if CLASS_TO_IDX["Fall"] in window_labels:
                label = CLASS_TO_IDX["Fall"]
            else:
                label = window_labels[-1]

            X_list.append(window)
            y_list.append(label)
            g_list.append(str(seq_id))

    X = np.array(X_list, dtype=np.float32) if X_list else np.empty((0, window_size, FEATURE_DIM), dtype=np.float32)
    y = np.array(y_list, dtype=np.int32) if y_list else np.empty(0, dtype=np.int32)
    g = np.array(g_list, dtype=object) if g_list else np.empty(0, dtype=object)
    
    print(f"  [dataset] Source ({kp_csv.name}): {len(X)} windows from {len(kp_df)} frames across {kp_df['sequence_id'].nunique()} sequences.")
    return X, y, g


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
    output_path: Path = LSTM_DATASET_NPZ,
) -> tuple:
    """
    Build the REAL-ONLY sliding-window dataset from all available keypoint CSVs.

    Synthetic augmentation is intentionally excluded here so that the
    train/val split in lstm_trainer.py operates on a 100% real-world proxy
    before any synthetic windows are injected into the training fold.

    Outputs
    -------
    X_real  : (N, window_size, 66)  float32
    y_real  : (N,)                  int32
    groups  : (N,)                  object  (sequence_id strings)
    """
    print("=" * 55)
    print("  LSTM Dataset Builder  [real data only]")
    print("=" * 55)
    print(f"  Window size  : {window_size} frames")
    print(f"  Step size    : {step}")
    print(f"  Synthetic    : injected post-split in trainer (not here)")

    # Real data
    X_real_list, y_real_list, g_real_list = [], [], []
    real_sources = [
        (DATA_DIR / "processed_keypoints" / "real_pose_keypoints.csv",  DATA_DIR / "processed_keypoints" / "real_posture_output.csv"),
        (DATA_DIR / "processed_keypoints" / "pose_keypoints.csv",       DATA_DIR / "processed_keypoints" / "posture_output.csv")
    ]

    for kp_csv, out_csv in real_sources:
        X_r, y_r, g_r = build_windows_from_real_data(
            kp_csv=kp_csv,
            out_csv=out_csv,
            window_size=window_size,
            step=step
        )
        if len(X_r) > 0:
            X_real_list.append(X_r)
            y_real_list.append(y_r)
            g_real_list.append(g_r)

    if X_real_list:
        X_real = np.concatenate(X_real_list, axis=0)
        y_real = np.concatenate(y_real_list, axis=0)
        g_real = np.concatenate(g_real_list, axis=0)
    else:
        X_real = np.empty((0, window_size, FEATURE_DIM), dtype=np.float32)
        y_real = np.empty(0, dtype=np.int32)
        g_real = np.empty(0, dtype=object)

    # Compute per-feature column medians from the real (pre-imputation) data
    # so lstm_classifier.py can use the SAME imputation statistics at live
    # inference time instead of an arbitrary constant fill value (previously
    # this was never computed/persisted at all -- inference silently filled
    # NaNs with a flat 0.5 while training used per-column medians, a real
    # train/inference skew bug).
    col_medians = lf.compute_col_medians(X_real)

    # Impute NaNs on real data only
    print("  Imputing NaN values...")
    X_real = impute_nan(X_real)

    # Shuffle (preserves group integrity; trainer re-shuffles within train fold)
    rng = np.random.default_rng(seed=0)
    idx = rng.permutation(len(X_real))
    X_real, y_real, g_real = X_real[idx], y_real[idx], g_real[idx]

    # Class distribution
    n = len(y_real)
    print(f"\n  Real-data windows : {n}")
    print("  Class distribution (real only):")
    for i, cls in enumerate(CLASSES):
        count = int((y_real == i).sum())
        n_seqs = int(np.unique(g_real[y_real == i]).shape[0]) if count > 0 else 0
        pct = 100 * count / n if n > 0 else 0.0
        print(f"    {cls:<10}: {count:>6} windows  {n_seqs:>4} seqs  ({pct:.1f}%)")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(output_path),
        X=X_real, y=y_real, groups=g_real, classes=CLASSES,
        col_medians=col_medians,
    )
    print(f"\n  Saved -> {output_path}")
    print("=" * 55)

    return X_real, y_real, CLASSES


def main():
    parser = argparse.ArgumentParser(description="LSTM Posture Dataset Builder")
    parser.add_argument("--window-size", type=int, default=30, help="Sliding window length in frames (default: 30)")
    parser.add_argument("--step", type=int, default=1, help="Sliding window step (default: 1)")
    parser.add_argument("--output", type=str, default=str(LSTM_DATASET_NPZ), help="Output .npz path")
    args = parser.parse_args()

    build_dataset(
        window_size=args.window_size,
        step=args.step,
        output_path=Path(args.output),
    )


if __name__ == "__main__":
    main()

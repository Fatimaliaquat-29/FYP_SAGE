"""
lstm_features.py
=================
Single source of truth for the LSTM's input feature representation.

Root cause this module fixes
-----------------------------
The LSTM was trained directly on raw MediaPipe (x, y) landmark coordinates,
normalized only to the [0, 1] image frame. Those coordinates are NOT
invariant to camera distance, framing, or position in shot: a person
standing far from the camera occupies a small vertical extent in the same
way a person lying down does, and the model has no structural way to tell
those apart from absolute position alone. Diagnostic evidence: a clean,
motionless Standing clip (torso_angle ~2 deg, knee/hip angle ~170 deg,
velocity ~0.2 body-heights/sec -- textbook upright and static by every
scale-invariant measure the heuristic computes) still gets ~66% "Fall"
probability from the raw-coordinate model. The features below make the
LSTM's input scale- and translation-invariant (like the heuristic's joint
angles already are) while keeping full body-shape information, and add an
explicit motion signal so static-but-oddly-framed poses can't be confused
with a real collapse.

Every consumer (training in lstm_dataset.py, production inference in
lstm_classifier.py, and batch evaluation in hybrid_evaluate.py) must import
and use this module rather than reimplementing the transform -- three
independent reimplementations already existed before this file was added
(fixed 0.5 fill vs 0.0 fill vs an unused median-imputation code path that
was never actually wired up), which is exactly the kind of silent drift
that makes train/inference behavior diverge without anyone noticing.

Feature layout
--------------
Per frame: 132 floats = 66 (normalized position) + 66 (frame-to-frame
velocity of that normalized position). Both blocks are ordered
x1, y1, x2, y2, ..., x33, y33 to match the raw landmark ordering.
"""

import numpy as np

LANDMARK_COUNT = 33
RAW_FEATURE_DIM = LANDMARK_COUNT * 2   # 66
FEATURE_DIM = RAW_FEATURE_DIM * 2      # 132: normalized position + velocity

LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_HIP, RIGHT_HIP = 23, 24


def normalize_frame(raw: np.ndarray) -> np.ndarray:
    """
    Center a raw (66,) landmark vector on the hip midpoint and scale by
    torso length (shoulder-mid to hip-mid distance).

    Using torso length (not full body height) as the scale reference keeps
    this well-defined even when legs are occluded or out of frame, since a
    trackable person's shoulders and hips are visible far more often than
    their ankles.

    Returns a (66,) array. If either hip or shoulder landmark is missing
    (NaN) or degenerate (zero torso length), the whole frame is returned as
    NaN -- callers should run their normal NaN-imputation on top of this,
    rather than silently normalizing around a phantom origin.
    """
    raw = np.asarray(raw, dtype=np.float32).reshape(LANDMARK_COUNT, 2)
    hip_l, hip_r = raw[LEFT_HIP], raw[RIGHT_HIP]
    sh_l, sh_r = raw[LEFT_SHOULDER], raw[RIGHT_SHOULDER]

    if np.any(np.isnan(hip_l)) or np.any(np.isnan(hip_r)) or np.any(np.isnan(sh_l)) or np.any(np.isnan(sh_r)):
        return np.full(RAW_FEATURE_DIM, np.nan, dtype=np.float32)

    hip_center = (hip_l + hip_r) / 2.0
    sh_center = (sh_l + sh_r) / 2.0
    scale = float(np.linalg.norm(sh_center - hip_center))
    if scale < 1e-3:
        return np.full(RAW_FEATURE_DIM, np.nan, dtype=np.float32)

    normalized = (raw - hip_center) / scale
    return normalized.reshape(-1).astype(np.float32)


def normalize_sequence(raw_seq: np.ndarray) -> np.ndarray:
    """Apply normalize_frame independently to every row of a (T, 66) array."""
    return np.stack([normalize_frame(raw_seq[t]) for t in range(raw_seq.shape[0])], axis=0)


def add_velocity(normalized_seq: np.ndarray) -> np.ndarray:
    """
    Build the (T, 132) feature sequence: [normalized position | velocity].

    velocity[t] = normalized[t] - normalized[t-1]; velocity[0] = 0 (no prior
    frame exists). NaN propagates naturally through the subtraction when
    either frame failed to normalize, so downstream NaN-imputation handles
    it the same way as missing position data.
    """
    T = normalized_seq.shape[0]
    velocity = np.zeros_like(normalized_seq)
    if T > 1:
        velocity[1:] = normalized_seq[1:] - normalized_seq[:-1]
    return np.concatenate([normalized_seq, velocity], axis=1).astype(np.float32)


def build_features_from_raw_sequence(raw_seq: np.ndarray) -> np.ndarray:
    """
    Full pipeline: (T, 66) raw landmark coordinates -> (T, 132) feature
    sequence ready for the LSTM (before NaN-imputation).
    """
    normalized = normalize_sequence(raw_seq)
    return add_velocity(normalized)


def build_features_from_raw_window(raw_window: np.ndarray) -> np.ndarray:
    """
    Inference-time convenience wrapper for a window of RAW keypoints with one
    extra leading frame of history, i.e. shape (window_size + 1, 66).

    The extra leading frame supplies the reference point for the first
    output row's velocity, so every one of the `window_size` output rows
    gets a real (not zero-padded) velocity -- matching how training computes
    velocity across the full sequence before slicing into windows, instead
    of artificially zeroing the oldest frame of every single inference call.

    Returns (window_size, 132).
    """
    normalized = normalize_sequence(raw_window)  # (window_size+1, 66)
    velocity = normalized[1:] - normalized[:-1]   # (window_size, 66)
    return np.concatenate([normalized[1:], velocity], axis=1).astype(np.float32)


def impute_nan(X: np.ndarray, col_medians: np.ndarray = None) -> np.ndarray:
    """
    Replace NaNs in a (..., FEATURE_DIM) array using per-feature column
    medians. Columns that are entirely NaN (or when col_medians is None)
    fall back to 0.0, which is the natural "centered, no motion" origin in
    this normalized feature space (unlike raw screen coordinates, where 0.0
    is an arbitrary corner of the frame).
    """
    flat = X.reshape(-1, X.shape[-1]).copy()
    for col_idx in range(flat.shape[1]):
        col = flat[:, col_idx]
        nan_mask = np.isnan(col)
        if not nan_mask.any():
            continue
        if col_medians is not None and not np.isnan(col_medians[col_idx]):
            flat[nan_mask, col_idx] = col_medians[col_idx]
        else:
            flat[nan_mask, col_idx] = 0.0
    return flat.reshape(X.shape)


def compute_col_medians(X: np.ndarray) -> np.ndarray:
    """Per-feature column median over a (..., FEATURE_DIM) array, ignoring NaNs."""
    flat = X.reshape(-1, X.shape[-1])
    with np.errstate(all="ignore"):
        medians = np.nanmedian(flat, axis=0)
    return np.where(np.isnan(medians), 0.0, medians).astype(np.float32)

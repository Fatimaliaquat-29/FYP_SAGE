"""
benchmarks/gait_old_impl.py
============================
Standalone, independent reimplementation of the PRE-vectorization
src/gait/gait_features.py functions -- copied verbatim from that file's
state before this session's vectorization work (per-frame Python loops,
no `_ts`/`_raw` sharing). Used ONLY by benchmarks/validate_gait_on_footage.py
to diff old-vs-new output on real footage; not imported by any production
code, and does not modify src/gait/ in any way.

Where the original function's own downstream logic (past the loop that got
vectorized) was untouched by the vectorization work, that logic is copied
here verbatim too, so this file is a fully independent parallel
implementation -- not a thin wrapper that calls back into the new module
for the parts that didn't change (which could silently hide a regression
in exactly those unchanged parts).
"""
from typing import Dict, List, Optional

import numpy as np

from src.posture.pipeline_utils import _extract_keypoint_pairs, is_landmark_valid, _compute_hip_angle
from src.posture.lstm import lstm_features as lf
from src.gait import gait_features as gf  # only for shared constants (indices, thresholds), not logic

LEFT_SHOULDER, RIGHT_SHOULDER = gf.LEFT_SHOULDER, gf.RIGHT_SHOULDER
LEFT_HIP, RIGHT_HIP = gf.LEFT_HIP, gf.RIGHT_HIP
LEFT_KNEE, RIGHT_KNEE = gf.LEFT_KNEE, gf.RIGHT_KNEE
LEFT_ANKLE, RIGHT_ANKLE = gf.LEFT_ANKLE, gf.RIGHT_ANKLE
MIN_AMBULATION_PATH = gf.MIN_AMBULATION_PATH
_HIP_ANGLE_SITTING_MAX = gf._HIP_ANGLE_SITTING_MAX
_HIP_ANGLE_STANDING_MIN = gf._HIP_ANGLE_STANDING_MIN


def old_timestamps(window: List[dict]) -> np.ndarray:
    ts = []
    for i, row in enumerate(window):
        try:
            ts.append(float(row.get("timestamp")))
        except (TypeError, ValueError):
            ts.append(i / 30.0)
    return np.array(ts, dtype=np.float64)


def old_raw_keypoint_array(window: List[dict]) -> np.ndarray:
    out = np.full((len(window), 66), np.nan, dtype=np.float32)
    for i, row in enumerate(window):
        pairs = _extract_keypoint_pairs(row)
        flat = [c for pair in pairs for c in pair]
        n = min(len(flat), 66)
        out[i, :n] = flat[:n]
    out[~np.isfinite(out)] = np.nan
    return out


def old_normalized_positions(window: List[dict], _raw: Optional[np.ndarray] = None) -> np.ndarray:
    raw = _raw if _raw is not None else old_raw_keypoint_array(window)
    normalized = np.stack([lf.normalize_frame(raw[t]) for t in range(raw.shape[0])], axis=0)
    return normalized.reshape(-1, 33, 2)


def old_torso_scaled_hip_track(window: List[dict], smooth_window: int = 5,
                                _raw: Optional[np.ndarray] = None) -> np.ndarray:
    # Unchanged by the vectorization work -- copied verbatim anyway to keep
    # this module fully independent of gait_features.py's own code.
    raw = _raw if _raw is not None else old_raw_keypoint_array(window)
    pairs_per_frame = raw.reshape(-1, 33, 2)
    sh_mid = (pairs_per_frame[:, LEFT_SHOULDER, :] + pairs_per_frame[:, RIGHT_SHOULDER, :]) / 2.0
    hip_mid = (pairs_per_frame[:, LEFT_HIP, :] + pairs_per_frame[:, RIGHT_HIP, :]) / 2.0
    torso_len = np.linalg.norm(sh_mid - hip_mid, axis=1)
    torso_len = np.where(torso_len < 1e-3, np.nan, torso_len)
    track = hip_mid / torso_len[:, None]

    if smooth_window > 1 and len(track) > 1:
        import pandas as pd
        smoothed = pd.DataFrame(track).rolling(
            window=smooth_window, center=True, min_periods=1
        ).mean().to_numpy()
        return smoothed
    return track


def old_compute_walking_speed(window: List[dict], _hip_track: Optional[np.ndarray] = None) -> Optional[float]:
    hip_center = _hip_track if _hip_track is not None else old_torso_scaled_hip_track(window)
    ts = old_timestamps(window)

    valid = ~np.isnan(hip_center).any(axis=1)
    if valid.sum() < 2:
        return None

    speeds = []
    total_path = 0.0
    for i in range(1, len(window)):
        if not (valid[i] and valid[i - 1]):
            continue
        dt = ts[i] - ts[i - 1]
        if dt <= 0:
            continue
        disp = float(np.linalg.norm(hip_center[i] - hip_center[i - 1]))
        total_path += disp
        speeds.append(disp / dt)

    if not speeds or total_path < MIN_AMBULATION_PATH:
        return None

    return float(np.mean(speeds))


def old_compute_stride_regularity(window: List[dict], _raw: Optional[np.ndarray] = None) -> Optional[float]:
    try:
        from scipy.signal import find_peaks
    except ImportError:
        return None

    pos = old_normalized_positions(window, _raw=_raw)
    ts = old_timestamps(window)
    ankle_y = (pos[:, LEFT_ANKLE, 1] + pos[:, RIGHT_ANKLE, 1]) / 2.0

    valid = ~np.isnan(ankle_y)
    if valid.sum() < len(window) * 0.5:
        return None

    idx = np.arange(len(ankle_y))
    if valid.sum() >= 2:
        ankle_y_filled = np.interp(idx, idx[valid], ankle_y[valid])
    else:
        return None

    peaks, _ = find_peaks(ankle_y_filled, distance=5)
    if len(peaks) < 3:
        return None

    peak_times = ts[peaks]
    intervals = np.diff(peak_times)
    intervals = intervals[intervals > 0]
    if len(intervals) < 2:
        return None

    mean_interval = float(np.mean(intervals))
    if mean_interval < 1e-6:
        return None
    return float(np.std(intervals) / mean_interval)


def old_compute_postural_sway(window: List[dict], stable_subwindow: int = 15, displacement_thresh: float = 0.15,
                               _hip_track: Optional[np.ndarray] = None) -> Optional[float]:
    # Untouched by the vectorization work -- copied verbatim.
    hip_center = _hip_track if _hip_track is not None else old_torso_scaled_hip_track(window)
    valid = ~np.isnan(hip_center).any(axis=1)

    sways = []
    n = len(window)
    for start in range(0, n - stable_subwindow + 1, stable_subwindow):
        seg = hip_center[start:start + stable_subwindow]
        seg_valid = valid[start:start + stable_subwindow]
        if seg_valid.sum() < stable_subwindow * 0.7:
            continue
        seg = seg[seg_valid]
        net_disp = float(np.linalg.norm(seg[-1] - seg[0]))
        if net_disp > displacement_thresh:
            continue
        sways.append(float(np.std(np.linalg.norm(seg - seg.mean(axis=0), axis=1))))

    return float(np.mean(sways)) if sways else None


def old_compute_sit_to_stand(window: List[dict], _raw: Optional[np.ndarray] = None) -> Optional[Dict[str, float]]:
    raw = _raw if _raw is not None else old_raw_keypoint_array(window)
    pairs_per_frame = raw.reshape(-1, 33, 2)

    def _pt(idx):
        return pairs_per_frame[:, idx, :]

    l_sh, r_sh = _pt(LEFT_SHOULDER), _pt(RIGHT_SHOULDER)
    l_hp, r_hp = _pt(LEFT_HIP), _pt(RIGHT_HIP)
    l_kn, r_kn = _pt(LEFT_KNEE), _pt(RIGHT_KNEE)

    T = raw.shape[0]
    hip_angles = np.full(T, np.nan, dtype=np.float64)
    for t in range(T):
        left_pts = (l_sh[t], l_hp[t], l_kn[t])
        right_pts = (r_sh[t], r_hp[t], r_kn[t])
        left_angle = _compute_hip_angle(*left_pts) if all(is_landmark_valid(p) for p in left_pts) else np.nan
        right_angle = _compute_hip_angle(*right_pts) if all(is_landmark_valid(p) for p in right_pts) else np.nan
        valid_angles = [a for a in (left_angle, right_angle) if not np.isnan(a)]
        if valid_angles:
            hip_angles[t] = float(np.mean(valid_angles))
    ts = old_timestamps(window)

    sitting_mask = hip_angles <= _HIP_ANGLE_SITTING_MAX
    standing_mask = hip_angles >= _HIP_ANGLE_STANDING_MIN

    sit_idx = np.where(sitting_mask)[0]
    stand_idx = np.where(standing_mask)[0]
    if len(sit_idx) == 0 or len(stand_idx) == 0:
        return None

    last_sit = None
    first_stand_after = None
    for s in sit_idx:
        later_stands = stand_idx[stand_idx > s]
        if len(later_stands) > 0:
            last_sit = s
            first_stand_after = int(later_stands[0])
            break
    if last_sit is None:
        return None

    duration_sec = float(ts[first_stand_after] - ts[last_sit])
    if duration_sec <= 0:
        return None

    segment = hip_angles[last_sit:first_stand_after + 1]
    deltas = np.diff(segment)
    deltas = deltas[~np.isnan(deltas)]
    reversal_count = 0
    for i in range(1, len(deltas)):
        if deltas[i] == 0 or deltas[i - 1] == 0:
            continue
        if np.sign(deltas[i]) != np.sign(deltas[i - 1]):
            reversal_count += 1

    return {"duration_sec": duration_sec, "reversal_count": float(reversal_count)}


def old_assess_risk(window: List[dict]) -> dict:
    """Full old-style assess_risk(), built from the OLD feature functions
    above but reusing gait_risk.py's risk-mapping functions and weights
    UNCHANGED (that blending/weighting logic was never touched by the
    vectorization work -- only the feature extraction underneath it was),
    so this isolates exactly what the vectorization could have affected."""
    from src.gait.gait_risk import _SIGNAL_WEIGHTS, _speed_risk, _stride_cv_risk, _sway_risk, _sit_to_stand_risk

    raw = old_raw_keypoint_array(window)
    hip_track = old_torso_scaled_hip_track(window, _raw=raw)

    values = {
        "walking_speed": old_compute_walking_speed(window, _hip_track=hip_track),
        "stride_regularity": old_compute_stride_regularity(window, _raw=raw),
        "postural_sway": old_compute_postural_sway(window, _hip_track=hip_track),
        "sit_to_stand": old_compute_sit_to_stand(window, _raw=raw),
    }
    risk_fns = {
        "walking_speed": _speed_risk,
        "stride_regularity": _stride_cv_risk,
        "postural_sway": _sway_risk,
        "sit_to_stand": _sit_to_stand_risk,
    }

    weighted_sum = 0.0
    weight_total = 0.0
    contributions = {}
    for name, value in values.items():
        if value is None:
            contributions[name] = None
            continue
        contribution = risk_fns[name](value)
        contributions[name] = contribution
        weighted_sum += _SIGNAL_WEIGHTS[name] * contribution
        weight_total += _SIGNAL_WEIGHTS[name]

    risk_score = (weighted_sum / weight_total) if weight_total > 0 else None
    return {"risk_score": risk_score, "values": values, "contributions": contributions}

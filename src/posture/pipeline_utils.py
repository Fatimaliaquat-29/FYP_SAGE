import os
import sys
import csv
import logging
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
POSE_KEYPOINTS_CSV = DATA_DIR / "processed_keypoints" / "pose_keypoints.csv"
POSTURE_OUTPUT_CSV = DATA_DIR / "processed_keypoints" / "posture_output.csv"
DETECTIONS_LOG = DATA_DIR / "detections.log"
LANDMARK_COUNT = 33

# Configure logger
logger = logging.getLogger("posture_pipeline")
logger.setLevel(logging.INFO)

# Avoid adding multiple handlers if the module is re-imported
if not logger.handlers:
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # File handler
    fh = logging.FileHandler(DETECTIONS_LOG, encoding="utf-8")
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)


def ensure_data_dir(path: Optional[Path] = None) -> Path:
    target = path or DATA_DIR
    target.mkdir(parents=True, exist_ok=True)
    return target


def build_pose_row(timestamp: Optional[str] = None, frame: Optional[int] = None, landmarks: Optional[Sequence[Tuple[float, float]]] = None, keypoints: Optional[Sequence[float]] = None):
    timestamp_value = timestamp or datetime.utcnow().isoformat()
    frame_value = frame if frame is not None else 0

    row = {
        "timestamp": timestamp_value,
        "frame": frame_value,
        "posture_label": "Unknown",
        "fall_detected": False,
        "confidence": 0.0,
        "other_labels": "",
        "keypoints": [],
    }

    if keypoints is not None:
        row["keypoints"] = [float(x) if x is not None else np.nan for x in keypoints]
    elif landmarks:
        row["keypoints"] = [float(coord) if coord is not None else np.nan for pair in landmarks for coord in pair]

    # Fill default NaNs if keypoints is empty or insufficient
    if len(row["keypoints"]) < LANDMARK_COUNT * 2:
        row["keypoints"] = row["keypoints"] + [np.nan] * (LANDMARK_COUNT * 2 - len(row["keypoints"]))

    return row


def _normalize_keypoints(value) -> List[Tuple[float, float]]:
    if isinstance(value, str):
        # Handle string serialization e.g. "x1,y1,x2,y2,..." or "[x1, y1, ...]"
        clean_str = value.replace("[", "").replace("]", "").replace(" ", "")
        tokens = [token for token in clean_str.split(",") if token != ""]
        try:
            flat = [float(token) for token in tokens]
        except ValueError:
            return []
    elif isinstance(value, (list, tuple, np.ndarray)):
        flat = []
        for item in value:
            try:
                flat.append(float(item))
            except (TypeError, ValueError):
                flat.append(np.nan)
    else:
        return []

    if len(flat) % 2 != 0:
        flat = flat[:-1]

    return [(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]


def _extract_keypoint_pairs(row: dict) -> List[Tuple[float, float]]:
    keypoints = row.get("keypoints") or []
    if isinstance(keypoints, str):
        return _normalize_keypoints(keypoints)
    return _normalize_keypoints(keypoints)


def _joint_point(pairs, index):
    if pairs and 0 <= index < len(pairs):
        return pairs[index]
    return None


def is_landmark_valid(pt, margin: float = 0.1) -> bool:
    if pt is None:
        return False
    if any(np.isnan(value) for value in pt):
        return False
    # Allow a small margin beyond [0, 1] because MediaPipe can extrapolate
    # slightly outside the frame for partially-occluded landmarks (e.g. ankles
    # near the bottom edge when sitting on a bed).
    if pt[0] < -margin or pt[0] > 1.0 + margin or pt[1] < -margin or pt[1] > 1.0 + margin:
        return False
    return True


def _compute_torso_angle(shoulder, hip):
    if shoulder is None or hip is None:
        return np.nan
    if any(np.isnan(value) for value in shoulder) or any(np.isnan(value) for value in hip):
        return np.nan
    dx = shoulder[0] - hip[0]
    dy = shoulder[1] - hip[1]
    dist = np.sqrt(dx**2 + dy**2)
    if dist < 1e-6:
        return np.nan
    cosine = -dy / dist
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def _compute_knee_angle(hip, knee, ankle):
    if hip is None or knee is None or ankle is None:
        return np.nan
    if any(np.isnan(value) for value in hip) or any(np.isnan(value) for value in knee) or any(np.isnan(value) for value in ankle):
        return np.nan
    v1 = np.array(hip, dtype=float) - np.array(knee, dtype=float)
    v2 = np.array(ankle, dtype=float) - np.array(knee, dtype=float)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 < 1e-6 or norm2 < 1e-6:
        return np.nan
    cos_theta = np.dot(v1, v2) / (norm1 * norm2)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_theta)))


def _compute_hip_angle(shoulder, hip, knee):
    """Angle at the hip joint: shoulder -> hip -> knee.
    ~170-180 deg when standing upright (torso in line with legs).
    ~70-110 deg when sitting (torso folded over thighs)."""
    if shoulder is None or hip is None or knee is None:
        return np.nan
    if any(np.isnan(v) for v in shoulder) or any(np.isnan(v) for v in hip) or any(np.isnan(v) for v in knee):
        return np.nan
    v1 = np.array(shoulder, dtype=float) - np.array(hip, dtype=float)
    v2 = np.array(knee, dtype=float) - np.array(hip, dtype=float)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < 1e-6 or n2 < 1e-6:
        return np.nan
    cos_theta = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_theta)))


def _compute_velocity(previous_row: dict, current_row: dict) -> float:
    """Hip-center speed, normalized by elapsed time and by body scale.

    Returns speed in units of (body_height fractions) per second, so the
    same real-world fall speed reads the same regardless of camera distance
    or frame rate."""
    prev_pairs = _extract_keypoint_pairs(previous_row)
    curr_pairs = _extract_keypoint_pairs(current_row)
    if not prev_pairs or not curr_pairs:
        return 0.0

    if len(prev_pairs) <= 24 or len(curr_pairs) <= 24:
        return 0.0

    prev_hip = ((prev_pairs[23][0] + prev_pairs[24][0]) / 2.0,
                (prev_pairs[23][1] + prev_pairs[24][1]) / 2.0)
    curr_hip = ((curr_pairs[23][0] + curr_pairs[24][0]) / 2.0,
                (curr_pairs[23][1] + curr_pairs[24][1]) / 2.0)
    if any(np.isnan(v) for v in prev_hip) or any(np.isnan(v) for v in curr_hip):
        return 0.0

    raw_disp = float(np.linalg.norm(np.array(curr_hip) - np.array(prev_hip)))

    try:
        dt = float(current_row.get("timestamp", 0)) - float(previous_row.get("timestamp", 0))
    except (TypeError, ValueError):
        dt = 0.0
    if dt <= 0:
        dt = 1.0 / 30.0  # fallback: assume ~30 FPS

    speed_per_sec = raw_disp / dt

    body_scale = current_row.get("body_height", np.nan)
    if body_scale is None or np.isnan(body_scale) or body_scale < 1e-3:
        body_scale = 1.0

    return speed_per_sec / body_scale


# Module-level state for post-fall tracking (shared across calls within a session)
_frames_since_fall: int = 10**6      # frames elapsed since last fall trigger
_consecutive_nan_frames: int = 0     # frames of total landmark loss
_recent_angular_velocities: deque = deque(maxlen=3)   # rolling window for angular velocity smoothing
_frames_angvel_above_floor: int = 0  # Fix D: consecutive frames with smoothed angvel > floor
_last_confirmed_label: str = "Unknown"   # Fix B: last non-Unknown posture label
_frames_since_confirmed: int = 0         # Fix B: frames since that label was set
_last_valid_velocity: float = 0.0        # Fix C: velocity of last frame with landmarks
_lying_run_length: int = 0               # Sustained Lying: frames continuously labeled as Lying
_has_been_upright_this_session: bool = False # Sustained Lying: whether the clip has seen non-Lying posture

POST_FALL_WINDOW = 10          # frames after a fall trigger to loosen Lying detection
NAN_AFTER_FALL_THRESHOLD = 10  # consecutive all-NaN frames that infer Lying (after confirmed fall)
LYING_PERSIST_WINDOW = 20      # Fix B: frames over which a prior Lying label persists through NaN
VELOCITY_UPTICK_FACTOR = 0.5  # Fix C: fraction of FALL_AVG_VELOCITY_FLOOR to arm NaN inference
ANGULAR_VELOCITY_CAP = 720.0  # deg/sec hard implausibility cap
ANGVEL_SUSTAIN_FRAMES = 3     # consecutive frames above the (150 deg/sec) angular-velocity floor to confirm rotation (was 5); lower = less detection latency, still filters single-frame landmark jitter
LYING_PERSISTENCE_FRAMES = 40 # Sustained Lying: frames of Lying needed to infer a fall without velocity triggers


def reset_session_state() -> None:
    """Reset all inter-frame module-level state.

    Must be called at the start of each new clip/session so that state from one
    clip does not bleed into the next (particularly important in batch evaluation).
    """
    global _frames_since_fall, _consecutive_nan_frames, _recent_angular_velocities
    global _frames_angvel_above_floor
    global _last_confirmed_label, _frames_since_confirmed
    global _last_valid_velocity, _lying_run_length, _has_been_upright_this_session
    _frames_since_fall = 10**6
    _consecutive_nan_frames = 0
    _recent_angular_velocities = deque(maxlen=3)
    _frames_angvel_above_floor = 0
    _last_confirmed_label = "Unknown"
    _frames_since_confirmed = 0
    _last_valid_velocity = 0.0
    _lying_run_length = 0
    _has_been_upright_this_session = False


def classify_posture_and_fall(
    row: dict,
    previous_rows: Optional[Sequence[dict]] = None,
    lstm_classifier=None,
) -> dict:
    """
    Classify posture and detect falls for a single pose frame.

    Parameters
    ----------
    row : dict
        Current pose row (must contain 'keypoints' key).
    previous_rows : list of dict, optional
        Ordered history of previous processed rows.
    lstm_classifier : LSTMPostureClassifier, optional
        When provided and the rolling buffer is large enough, the LSTM
        pipeline is used instead of the rule-based heuristic.  Pass None
        (the default) to always use the heuristic.
    """
    # Declared here (rather than only in the heuristic section below) because
    # the LSTM branch also reads/writes it, and a name can only be declared
    # global once an assignment to it hasn't already occurred earlier in the
    # function body.
    global _has_been_upright_this_session

    # ── LSTM path ──────────────────────────────────────────────────────────────
    # When a pre-loaded LSTMPostureClassifier is supplied and the rolling
    # history contains enough frames to fill one window, defer to the LSTM.
    # The heuristic path (below) remains the default when lstm_classifier=None.
    if lstm_classifier is not None and lstm_classifier.is_available:
        # raw_history_needed = window_size + 1: one extra leading raw frame so
        # the LSTM can compute a genuine (not zero-padded) velocity for every
        # frame in its window, including the oldest one. See lstm_features.py.
        required = lstm_classifier.raw_history_needed - 1
        if previous_rows is not None and len(previous_rows) >= required:
            window = list(previous_rows[-required:]) + [row]
            try:
                lstm_result = lstm_classifier.predict(window)
                # Propagate computed metrics so downstream logging still works
                row.setdefault("body_height", np.nan)
                row.setdefault("torso_angle", np.nan)
                row.setdefault("hip_height", np.nan)
                row.setdefault("velocity", 0.0)
                row["posture_label"] = lstm_result["posture_label"]

                fall_detected = lstm_result["fall_detected"]
                if lstm_result["posture_label"] in ("Standing", "Sitting"):
                    _has_been_upright_this_session = True
                elif not _has_been_upright_this_session:
                    # No genuine upright -> lying transition has been
                    # observed yet this session, so a "Fall" claim is
                    # indistinguishable from "already lying when tracking
                    # started" -- a single window has no way to tell those
                    # apart. Suppress it, mirroring the heuristic's own
                    # _has_been_upright_this_session guard on sustained-lying
                    # detection. Diagnostic evidence: Lying_straight.mov and
                    # Lying_legs_straight.mov (subject lying for the entire
                    # clip, posture_label=="Lying" throughout) went from 0
                    # false Fall frames to ~57% of frames flagged once the
                    # LSTM's raw-coordinate shortcut was removed -- this gate
                    # closes that gap without needing the shortcut back.
                    fall_detected = False

                row["fall_detected"] = fall_detected
                lstm_result = dict(lstm_result, fall_detected=fall_detected)
                return lstm_result
            except Exception as exc:
                logger.warning(f"LSTM prediction failed (frame {row.get('frame', '?')}): {exc}. "
                               "Falling back to heuristic.")
    # ── Heuristic path ─────────────────────────────────────────────────────────
    global _frames_since_fall, _consecutive_nan_frames, _recent_angular_velocities
    global _frames_angvel_above_floor, _last_confirmed_label, _frames_since_confirmed
    global _last_valid_velocity, _lying_run_length

    pairs = _extract_keypoint_pairs(row)

    # 1. Handle missing critical landmarks for upper body / torso
    has_critical_landmarks = False
    if pairs and len(pairs) >= 29:
        sh_l = pairs[11]
        sh_r = pairs[12]
        hp_l = pairs[23]
        hp_r = pairs[24]
        sh_ok = is_landmark_valid(sh_l) and is_landmark_valid(sh_r)
        hp_ok = is_landmark_valid(hp_l) and is_landmark_valid(hp_r)
        if sh_ok and hp_ok:
            has_critical_landmarks = True

    if not has_critical_landmarks:
        row["body_height"] = np.nan
        row["vertical_span"] = np.nan
        row["torso_angle"] = np.nan
        row["hip_height"] = np.nan
        row["knee_angle"] = np.nan
        row["velocity"] = 0.0
        row["raw_posture_label"] = "Unknown"
        row["tracking_lost_after_fall"] = False

        _consecutive_nan_frames += 1
        _frames_since_fall += 1
        _frames_since_confirmed += 1

        # Fix B: persist a recent confirmed Lying label over sparse NaN frames
        if (_last_confirmed_label == "Lying"
                and _frames_since_confirmed <= LYING_PERSIST_WINDOW):
            return {
                "posture_label": "Lying",
                "fall_detected": False,
                "confidence": 0.0,
                "other_labels": "lying_persistence",
            }

        # Fix C / Issue 4 Alternative: sustained NaN after confirmed fall OR if upright recently
        # Resolves tracking loss prior to velocity spikes
        velocity_uptick_armed = (
            _last_valid_velocity > VELOCITY_UPTICK_FACTOR * 1.5  # 1.5 = FALL_AVG_VELOCITY_FLOOR
        )
        nan_inference_armed = (
            _frames_since_fall <= POST_FALL_WINDOW + NAN_AFTER_FALL_THRESHOLD
            or velocity_uptick_armed
        )
        if _consecutive_nan_frames >= NAN_AFTER_FALL_THRESHOLD and nan_inference_armed:
            row["tracking_lost_after_fall"] = True
            return {
                "posture_label": "Lying",
                "fall_detected": True,
                "confidence": 0.0,
                "other_labels": "tracking_lost_after_fall",
            }
        return {
            "posture_label": "Unknown",
            "fall_detected": False,
            "confidence": 0.0,
            "other_labels": "missing_keypoints",
        }

    sh_l = pairs[11]
    sh_r = pairs[12]
    hp_l = pairs[23]
    hp_r = pairs[24]
    kn_l = pairs[25]
    kn_r = pairs[26]
    ak_l = pairs[27]
    ak_r = pairs[28]

    kn_ok = is_landmark_valid(kn_l) and is_landmark_valid(kn_r)
    ak_ok = is_landmark_valid(ak_l) and is_landmark_valid(ak_r)

    shoulder = ((sh_l[0] + sh_r[0]) / 2.0, (sh_l[1] + sh_r[1]) / 2.0)
    hip = ((hp_l[0] + hp_r[0]) / 2.0, (hp_l[1] + hp_r[1]) / 2.0)

    # Flag whether we are operating in lower-body-occluded (e.g. sitting on bed) mode
    lower_body_occluded = not ak_ok and not kn_ok

    # Calculate height and span proxies depending on lower-body visibility
    if ak_ok:
        ankle = ((ak_l[0] + ak_r[0]) / 2.0, (ak_l[1] + ak_r[1]) / 2.0)
        body_height = float(np.linalg.norm(np.array(shoulder, dtype=float) - np.array(ankle, dtype=float)))
        vertical_span = float(abs(shoulder[1] - ankle[1]))
    elif kn_ok:
        # Ankles are occluded but knees are present. Scale knee coordinates as proxy.
        knee = ((kn_l[0] + kn_r[0]) / 2.0, (kn_l[1] + kn_r[1]) / 2.0)
        body_height = float(np.linalg.norm(np.array(shoulder, dtype=float) - np.array(knee, dtype=float))) * 1.5
        vertical_span = float(abs(shoulder[1] - knee[1])) * 1.5
    else:
        # Lower body is fully occluded (e.g. sitting on a bed with legs hidden).
        # Use the torso segment (shoulder → hip) as a proxy; scale up by 2.0 to
        # approximate full-body height so that the relative thresholds still work.
        torso_len = float(np.linalg.norm(np.array(shoulder, dtype=float) - np.array(hip, dtype=float)))
        body_height = torso_len * 2.0
        vertical_span = float(abs(shoulder[1] - hip[1])) * 2.0

    torso_angle = _compute_torso_angle(shoulder, hip)
    hip_height = float(1.0 - hip[1])
    
    # Calculate knee angle if hips, knees, and ankles are all visible
    if hp_ok and kn_ok and ak_ok:
        kl_angle = _compute_knee_angle(hp_l, kn_l, ak_l)
        kr_angle = _compute_knee_angle(hp_r, kn_r, ak_r)
        valid_angles = [a for a in [kl_angle, kr_angle] if not np.isnan(a)]
        knee_angle = float(np.mean(valid_angles)) if valid_angles else np.nan
    else:
        knee_angle = np.nan

    # Calculate hip angle if hips and knees are visible (does not need ankles)
    if hp_ok and kn_ok:
        hl_angle = _compute_hip_angle(sh_l, hp_l, kn_l)
        hr_angle = _compute_hip_angle(sh_r, hp_r, kn_r)
        valid_hip_angles = [a for a in [hl_angle, hr_angle] if not np.isnan(a)]
        hip_angle = float(np.mean(valid_hip_angles)) if valid_hip_angles else np.nan
    else:
        hip_angle = np.nan

    row["body_height"] = body_height
    row["vertical_span"] = vertical_span
    row["torso_angle"] = torso_angle
    row["hip_height"] = hip_height
    row["knee_angle"] = knee_angle
    row["hip_angle"] = hip_angle
    row["lower_body_occluded"] = lower_body_occluded
    row["tracking_lost_after_fall"] = False
    # Landmarks are present; reset the consecutive-NaN counter
    _consecutive_nan_frames = 0
    _last_valid_velocity = row.get("velocity", 0.0)  # updated below; placeholder resets on landmark loss

    # 2. Dynamic calibration from rolling history
    # Only calibrate using frames where the person was Standing, to prevent the calibration
    # from adapting downwards to Sitting or Lying postures over time.
    # Keep the last 300 standing frames to adapt to camera distance changes.
    recent_standing_history = [
        r for r in (previous_rows or [])
        if r.get("posture_label") == "Standing"
    ][-300:]

    history_body_heights = [r.get("body_height") for r in recent_standing_history if r.get("body_height") is not None and not np.isnan(r.get("body_height"))]
    all_body_heights = history_body_heights + [body_height]
    max_body_height = max(all_body_heights) if all_body_heights else 1.0

    history_spans = [r.get("vertical_span") for r in recent_standing_history if r.get("vertical_span") is not None and not np.isnan(r.get("vertical_span"))]
    all_spans = history_spans + [vertical_span]
    max_span = max(all_spans) if all_spans else 1.0

    effective_max_bh = max(max_body_height, 0.15)
    effective_max_span = max(max_span, 0.15)
    row["effective_max_bh"] = effective_max_bh

    # 3. Classify raw posture label using scale-invariant angles as primary signal
    ANGLE_STANDING_MIN = 143.0  # TODO-tune-further-if-needed
    ANGLE_SITTING_MAX = 125.0   # TODO-tune-further-if-needed

    raw_posture_label = "Unknown"
    other_labels = []
    angles_available = not np.isnan(knee_angle) and not np.isnan(hip_angle)
    angle_says_standing = (angles_available
                           and knee_angle >= ANGLE_STANDING_MIN
                           and hip_angle >= ANGLE_STANDING_MIN)

    # Issue 3: loosen vertical_span Lying threshold for frames shortly after a fall trigger
    post_fall_active = _frames_since_fall <= POST_FALL_WINDOW
    lying_span_threshold = 0.55 if post_fall_active else 0.40

    if np.isnan(torso_angle):
        raw_posture_label = "Unknown"
        other_labels.append("invalid_angle")
    # Rule 1: Lying – large torso inclination (applies even without lower-body visibility)
    # Guard: if joint angles clearly say Standing, skip the vertical_span Lying heuristic
    #        (prevents false Lying when camera distance changes mid-session).
    # Guard 2: a vertical torso (torso_angle < 30.0) cannot be lying, even with a small vertical span.
    elif torso_angle >= 45.0 or (not lower_body_occluded
                                  and not angle_says_standing
                                  and vertical_span < lying_span_threshold * effective_max_span
                                  and torso_angle >= 30.0):
        raw_posture_label = "Lying"
        other_labels.append("horizontal_torso" if torso_angle >= 45.0 else "horizontal_span")
    elif lower_body_occluded:
        # ── Torso-only path (e.g. sitting on a bed with legs not visible) ──
        # Fix A: use torso_angle as the primary standing signal (hip_height is unreliable
        # when the camera is mounted high and hips appear near the bottom of frame).
        if not np.isnan(torso_angle) and torso_angle < 30.0:
            raw_posture_label = "Standing"
            other_labels.append("torso_only_standing")
        elif np.isnan(torso_angle) and hip_height > 0.55:
            # torso_angle unavailable: fall back to the old hip_height heuristic
            raw_posture_label = "Standing"
            other_labels.append("torso_only_standing_hh")
        else:
            raw_posture_label = "Sitting"
            other_labels.append("torso_only_sitting")
    # Rule 2 (PRIMARY): Joint-angle classification — scale-invariant
    elif angles_available and knee_angle >= ANGLE_STANDING_MIN and hip_angle >= ANGLE_STANDING_MIN:
        raw_posture_label = "Standing"
        other_labels.append("angle_standing")
    elif angles_available and (knee_angle <= ANGLE_SITTING_MAX or hip_angle <= ANGLE_SITTING_MAX):
        raw_posture_label = "Sitting"
        other_labels.append("angle_sitting")
    # Rule 3 (FALLBACK): Ambiguous angles or angles unavailable — body_height ratio heuristic
    elif body_height >= 0.92 * effective_max_bh:
        raw_posture_label = "Standing"
        other_labels.append("fallback_height_standing")
    elif body_height < 0.88 * effective_max_bh:
        raw_posture_label = "Sitting"
        other_labels.append("fallback_height_sitting")
    else:
        raw_posture_label = "Standing"
        other_labels.append("fallback_default")

    row["raw_posture_label"] = raw_posture_label

    # 4. Temporal Smoothing (5-Frame Persistence Filter)
    #
    # Transitioning INTO "Lying" is allowed to bypass the full 5-frame majority
    # vote so a genuine fall isn't flagged several frames late. But a SINGLE
    # isolated raw-Lying frame must NOT latch: during a fast sit-down the
    # projected torso_angle can spike past the horizontal threshold for one
    # frame, and the "keep previous label" rule below would otherwise stick that
    # transient at Lying for several frames -- long enough for the (now
    # recall-biased) fall-motion gate to fire a false positive. Requiring TWO
    # consecutive raw-Lying frames to enter Lying rejects those 1-frame spikes
    # while costing a genuine fall only a single extra frame of latency (a real
    # collapse produces many consecutive horizontal frames).
    SMOOTHING_WINDOW = 5
    prev_raw = previous_rows[-1].get("raw_posture_label", "Unknown") if previous_rows else "Unknown"
    lying_confirmed = raw_posture_label == "Lying" and prev_raw == "Lying"
    if previous_rows and len(previous_rows) >= (SMOOTHING_WINDOW - 1):
        recent_raw = [r.get("raw_posture_label", "Unknown") for r in previous_rows[-(SMOOTHING_WINDOW - 1):]] + [raw_posture_label]
        if len(set(recent_raw)) == 1:
            posture_label = raw_posture_label
        elif lying_confirmed:
            # Two consecutive raw-Lying frames -> fast-track into Lying.
            posture_label = "Lying"
        else:
            posture_label = previous_rows[-1].get("posture_label", "Unknown")
    elif previous_rows:
        if lying_confirmed:
            posture_label = "Lying"
        else:
            posture_label = previous_rows[-1].get("posture_label", "Unknown")
    else:
        posture_label = raw_posture_label

    if posture_label in ("Standing", "Sitting"):
        _has_been_upright_this_session = True
        _lying_run_length = 0
    elif posture_label == "Lying":
        _lying_run_length += 1
    else:
        _lying_run_length = 0

    # 5. Fall detection logic
    # ── Constants (units: body-heights/sec and deg/sec) ────────────────────────
    # Re-derived July 2026 from the peak-motion distribution of 96 real
    # annotated LeFD falls vs 34 pure-ADL clips, cross-checked against the
    # fall-detection literature: a real fall's trunk angular velocity peaks
    # ~178 deg/sec (== 3.1 rad/sec, the classic wearable-gyro fall threshold),
    # and our data's 5th-percentile of real-fall peak angular velocity was
    # 177 deg/sec -- near-identical convergence.
    #
    # Design rationale (this is what broke the month-long tuning loop):
    #  - Hip velocity is a WEAK discriminator. Real-fall peak velocity has a
    #    MEDIAN of 5.1 body-heights/sec (25th pct 3.1) and pure-ADL peak has a
    #    median of 4.1 -- they overlap heavily. The old FALL_PEAK_VELOCITY_FLOOR
    #    of 15.0 (hand-fit to 2 clips) caught only ~17% of real falls, forcing
    #    the other 83% to wait for the slow sustained-lying fallback (the source
    #    of the 76-/81-/114-frame detection latencies). Velocity is now only a
    #    mild "real motion happened" floor, not a hard gate.
    #  - The STRONG discriminator is "did the rapid motion END IN LYING." Fast
    #    sit-downs and bends also spike velocity/angular-velocity but leave the
    #    person seated/upright, not lying on the floor. So the recall-biased
    #    thresholds below are safe because the rapid_fall trigger additionally
    #    requires posture_label == "Lying".
    #  - Biased toward RECALL: this is an elderly-safety system, where a missed
    #    fall (person left injured on the floor) is far worse than a false alarm.
    FALL_VELOCITY_THRESHOLD      = 1.5    # was 2.0  — "fast frame" counter floor
    FALL_SUSTAINED_COUNT         = 2      # minimum fast frames in the window
    FALL_AVG_VELOCITY_FLOOR      = 1.0    # was 1.5
    FALL_PEAK_VELOCITY_FLOOR     = 3.0    # was 15.0 (caught only ~17% of real falls!)
    FALL_ANGULAR_VELOCITY_FLOOR  = 150.0  # was 200.0 — catches ~97% of real falls (lit. ~178)
    FALL_LOOK_BACK_FRAMES        = 10     # how many recent frames to scan
    FALL_NON_LYING_WINDOW        = 15     # how far back to look for a non-Lying posture
    # A genuine fall drops the hips toward the floor. A person who merely
    # reclines (e.g. leans back in a chair/recliner) has their trunk pitch past
    # horizontal -- reading as "Lying" -- while their HIPS stay at roughly
    # constant seat height. Requiring a real downward hip displacement over the
    # fall window separates "collapsed to the floor" from "reclined in a seat".
    # Units: fraction of frame height (normalized image y).
    FALL_HIP_DESCENT_MIN         = 0.06
    # Pre-Lying trigger fires BEFORE a Lying posture is confirmed, so it has no
    # posture gate to suppress fast-ADL false positives -> it keeps a
    # deliberately HIGHER, unambiguous-fast-fall bar than the lying-confirmed
    # path above.
    FALL_PRELYING_ANGVEL_FLOOR   = 250.0  # deg/sec peak — well above typical fast sit/bend
    FALL_PRELYING_SUSTAIN        = 4      # consecutive frames of angular velocity > floor
    # ──────────────────────────────────────────────────────────────────────────────

    fall_detected = False
    confidence = 0.55
    velocity = 0.0

    # Compute torso angle delta and time-normalize to deg/sec by looking back to the last valid torso angle
    prev_torso_angle = np.nan
    dt_for_angle = 1.0 / 30.0
    if previous_rows:
        for r in reversed(previous_rows):
            if "torso_angle" in r and not np.isnan(r["torso_angle"]):
                prev_torso_angle = r["torso_angle"]
                try:
                    dt_for_angle = float(row.get("timestamp", 0)) - float(r.get("timestamp", 0))
                except (TypeError, ValueError):
                    pass
                break

    torso_angle_delta = 0.0
    if not np.isnan(torso_angle) and not np.isnan(prev_torso_angle):
        torso_angle_delta = abs(torso_angle - prev_torso_angle)
        if dt_for_angle <= 0:
            dt_for_angle = 1.0 / 30.0
    # Cap at ANGULAR_VELOCITY_CAP before storing or comparing
    torso_angular_velocity = min(torso_angle_delta / dt_for_angle, ANGULAR_VELOCITY_CAP)
    row["torso_angular_velocity"] = torso_angular_velocity

    # Maintain a short rolling window; use the median for fall threshold comparisons
    _recent_angular_velocities.append(torso_angular_velocity)
    smoothed_angular_velocity = float(np.median(list(_recent_angular_velocities)))

    if previous_rows:
        # Find the last row with valid hip landmarks to compute velocity
        prev_valid_row = None
        for r in reversed(previous_rows):
            p = _extract_keypoint_pairs(r)
            if p and len(p) > 24 and not np.isnan(p[23][0]) and not np.isnan(p[24][0]):
                prev_valid_row = r
                break

        if prev_valid_row:
            velocity = _compute_velocity(prev_valid_row, row)
        else:
            velocity = 0.0

        row["velocity"] = velocity
        _last_valid_velocity = velocity  # Fix C: track velocity of last frame with landmarks

        # Collect metrics over the recent look-back window.
        # Frames that hit the missing-landmark branch never had "velocity" set
        # at all (rather than being genuinely 0.0) -- treating a tracking-loss
        # frame as 0.0 velocity would dilute the average/peak/fast-frame-count
        # exactly during the motion blur a fast real fall tends to cause,
        # making genuine falls look slower than they were. Exclude them
        # instead of silently zero-filling.
        look_back = previous_rows[-FALL_LOOK_BACK_FRAMES:]
        recent_velocities = [r["velocity"] for r in look_back if "velocity" in r] + [velocity]
        max_recent_velocity = max(recent_velocities) if recent_velocities else 0.0

        fast_frame_count = sum(1 for v in recent_velocities if v > FALL_VELOCITY_THRESHOLD)

        avg_recent_velocity = (
            sum(recent_velocities) / len(recent_velocities)
        ) if recent_velocities else 0.0

        # Determine whether there was a non-Lying state recently.
        recent_non_lying = [
            r for r in previous_rows[-FALL_NON_LYING_WINDOW:]
            if r.get("posture_label") in ("Standing", "Sitting")
        ]
        had_upright_recently = len(recent_non_lying) > 0

        # Net downward hip displacement over the fall window: current hip_y minus
        # the HIGHEST hip position (smallest y) seen recently. Large positive =>
        # the hips dropped toward the floor, the signature of a real collapse.
        # (Reclining keeps the hips at a near-constant height -> ~0 descent.)
        hip_descended = False
        if not np.isnan(hip[1]):
            recent_hip_ys = []
            for r in look_back:
                p = _extract_keypoint_pairs(r)
                if p and len(p) > 24 and not np.isnan(p[23][1]) and not np.isnan(p[24][1]):
                    recent_hip_ys.append((p[23][1] + p[24][1]) / 2.0)
            if recent_hip_ys:
                hip_descent = hip[1] - min(recent_hip_ys)  # y grows downward
                hip_descended = hip_descent >= FALL_HIP_DESCENT_MIN
        row["hip_descent_ok"] = hip_descended

        # Fix D: track how many consecutive frames smoothed or raw angular velocity exceeds the floor
        if max(smoothed_angular_velocity, torso_angular_velocity) > FALL_ANGULAR_VELOCITY_FLOOR:
            _frames_angvel_above_floor += 1
        else:
            _frames_angvel_above_floor = 0
        angvel_sustained = _frames_angvel_above_floor >= ANGVEL_SUSTAIN_FRAMES

        # Max angular velocity in the lookback window (the torso rotation happens
        # during the fall but is zero once the person is on the ground).
        # Use the stored (already-capped) values from history; compare against the
        # smoothed reading for the current frame to suppress single-frame jitter.
        recent_angular_velocities = (
            [r["torso_angular_velocity"] for r in look_back if "torso_angular_velocity" in r]
            + [smoothed_angular_velocity]
        )
        max_recent_angular_velocity = max(recent_angular_velocities) if recent_angular_velocities else 0.0

        # Fall signal: rapid torso rotation (the strong signal) sustained over
        # a few frames, accompanied by real (but not necessarily large) hip
        # motion. This is only ever consumed inside the posture_label=="Lying"
        # branch below, so the "ends in Lying" gate -- not the motion magnitude
        # -- is what separates a real fall from a fast-but-benign ADL motion.
        # That is why these floors are recall-biased (see the constant block).
        is_fall_motion = (
            fast_frame_count >= FALL_SUSTAINED_COUNT
            and avg_recent_velocity > FALL_AVG_VELOCITY_FLOOR
            and max_recent_angular_velocity > FALL_ANGULAR_VELOCITY_FLOOR
            and angvel_sustained
            and max_recent_velocity > FALL_PEAK_VELOCITY_FLOOR
        )

        if posture_label == "Lying":
            if had_upright_recently and is_fall_motion and hip_descended:
                fall_detected = True
                confidence = 0.95
                other_labels.append("rapid_fall")
                _frames_since_fall = 0
            elif _has_been_upright_this_session and _lying_run_length >= LYING_PERSISTENCE_FRAMES:
                fall_detected = True
                confidence = 0.90
                other_labels.append("sustained_lying")
                _frames_since_fall = 0
                logger.warning(f"Frame {row.get('frame', 0)}: Sustained Lying FALL DETECTED!")
            else:
                confidence = 0.65
                other_labels.append("slow_lie")

        else:
            # ── Pre-Lying fall trigger ─────────────────────────────────────────
            # Fires while the person is still mid-fall (not yet classified
            # Lying), buying a few frames of earlier warning. Because there is
            # no Lying posture to confirm a genuine fall here, it uses a
            # HIGHER, unambiguous-fast-fall bar (peak angular velocity above
            # FALL_PRELYING_ANGVEL_FLOOR sustained for FALL_PRELYING_SUSTAIN
            # frames, plus real translational drop) so ordinary fast sit-downs
            # and bends -- which spike angular velocity briefly but don't have
            # a sustained high-speed body drop -- do not trip it.
            prelying_angvel = (
                max_recent_angular_velocity > FALL_PRELYING_ANGVEL_FLOOR
                and _frames_angvel_above_floor >= FALL_PRELYING_SUSTAIN
            )
            # The torso must actually be pitching toward horizontal right now.
            # A real fall in progress passes through a large trunk inclination;
            # a fast sit-down spikes angular velocity while the trunk stays
            # upright in the seat (torso_angle stays small). This single gate is
            # what separates the two without a Lying posture to lean on.
            torso_going_horizontal = (not np.isnan(torso_angle)) and torso_angle >= 45.0
            if (had_upright_recently
                    and torso_going_horizontal
                    and fast_frame_count >= (FALL_SUSTAINED_COUNT + 1)
                    and avg_recent_velocity > FALL_AVG_VELOCITY_FLOOR
                    and max_recent_velocity > FALL_PEAK_VELOCITY_FLOOR
                    and prelying_angvel):
                fall_detected = True
                confidence = 0.85
                other_labels.append("pre_lying_fall")
                _frames_since_fall = 0
                logger.warning(
                    f"Frame {row.get('frame', 0)}: Pre-Lying FALL DETECTED! "
                    f"avg_v={avg_recent_velocity:.3f} fast_frames={fast_frame_count}"
                )
            else:
                confidence = 0.62

        _frames_since_fall += 1

    else:
        row["velocity"] = 0.0
        row["torso_angle_delta"] = 0.0
        row["torso_angular_velocity"] = 0.0
        _frames_since_fall += 1
        _frames_angvel_above_floor = 0
        if posture_label == "Lying":
            confidence = 0.60
            other_labels.append("lying_static")

    # Log posture transition or fall detection
    prev_label = previous_rows[-1].get("posture_label", "Unknown") if previous_rows else None
    if prev_label and prev_label != posture_label:
        logger.info(f"Frame {row.get('frame', 0)}: Posture transition {prev_label} -> {posture_label}")

    if fall_detected:
        logger.warning(f"Frame {row.get('frame', 0)}: FALL DETECTED! Confidence: {confidence:.2f}")

    # Fix B: update last-confirmed-label tracker
    if posture_label != "Unknown":
        _last_confirmed_label = posture_label
        _frames_since_confirmed = 0

    return {
        "posture_label": posture_label,
        "fall_detected": fall_detected,
        "confidence": round(confidence, 2),
        "other_labels": ",".join(other_labels) if other_labels else "",
    }


def _flatten_pose_row(row: dict, landmark_count: int = LANDMARK_COUNT) -> List[float]:
    pairs = _extract_keypoint_pairs(row)
    flattened = []
    for index in range(landmark_count):
        if index < len(pairs):
            flattened.extend([pairs[index][0], pairs[index][1]])
        else:
            flattened.extend([np.nan, np.nan])
    return flattened


def write_pose_outputs(rows: Sequence[dict], pose_path: Optional[Path] = None, posture_path: Optional[Path] = None):
    pose_path = Path(pose_path or POSE_KEYPOINTS_CSV)
    posture_path = Path(posture_path or POSTURE_OUTPUT_CSV)
    ensure_data_dir(pose_path.parent)
    ensure_data_dir(posture_path.parent)

    keypoint_cols = []
    for i in range(1, LANDMARK_COUNT + 1):
        keypoint_cols.extend([f"x{i}", f"y{i}"])
    pose_columns = ["timestamp", "frame"] + keypoint_cols + ["posture_label", "other_labels"]

    posture_columns = [
        "timestamp", 
        "frame", 
        "posture_label", 
        "fall_detected", 
        "confidence", 
        "other_labels",
        "body_height",
        "torso_angle",
        "hip_height"
    ]

    try:
        pose_file_exists = pose_path.exists()
        with pose_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=pose_columns)
            if not pose_file_exists:
                writer.writeheader()
            for row in rows:
                pose_row = {
                    "timestamp": row.get("timestamp", ""),
                    "frame": row.get("frame", 0),
                    "posture_label": row.get("posture_label", "Unknown"),
                    "other_labels": row.get("other_labels", "")
                }
                keypoints = row.get("keypoints", [])
                for i in range(1, LANDMARK_COUNT + 1):
                    idx_x = (i - 1) * 2
                    idx_y = idx_x + 1
                    pose_row[f"x{i}"] = keypoints[idx_x] if idx_x < len(keypoints) else np.nan
                    pose_row[f"y{i}"] = keypoints[idx_y] if idx_y < len(keypoints) else np.nan
                writer.writerow(pose_row)

        posture_file_exists = posture_path.exists()
        with posture_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=posture_columns)
            if not posture_file_exists:
                writer.writeheader()
            for row in rows:
                posture_row = {
                    "timestamp": row.get("timestamp", ""),
                    "frame": row.get("frame", 0),
                    "posture_label": row.get("posture_label", "Unknown"),
                    "fall_detected": row.get("fall_detected", False),
                    "confidence": row.get("confidence", 0.0),
                    "other_labels": row.get("other_labels", ""),
                    "body_height": row.get("body_height", np.nan),
                    "torso_angle": row.get("torso_angle", np.nan),
                    "hip_height": row.get("hip_height", np.nan)
                }
                writer.writerow(posture_row)
    except (PermissionError, OSError) as e:
        logger.error(f"Permission denied or I/O error writing outputs to CSV: {e}. Please ensure the CSV files are not open in another application.")


def load_existing_rows(path: Optional[Path] = None) -> List[dict]:
    path = Path(path or POSE_KEYPOINTS_CSV)
    if not path.exists():
        return []
    try:
        df = pd.read_csv(path)
    except Exception:
        return []
    rows = []
    for _, row in df.iterrows():
        keypoints = []
        for i in range(1, LANDMARK_COUNT + 1):
            x_val = row.get(f"x{i}")
            y_val = row.get(f"y{i}")
            keypoints.append(float(x_val) if pd.notna(x_val) else np.nan)
            keypoints.append(float(y_val) if pd.notna(y_val) else np.nan)
        
        rows.append({
            "timestamp": row.get("timestamp", ""),
            "frame": int(row.get("frame", 0)) if pd.notna(row.get("frame")) else 0,
            "keypoints": keypoints,
            "posture_label": row.get("posture_label", "Unknown"),
            "other_labels": row.get("other_labels", ""),
        })
    return rows


def append_detection_log(row: dict, result: dict):
    ensure_data_dir(DETECTIONS_LOG.parent)
    try:
        with DETECTIONS_LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"{row.get('timestamp', '')} frame={row.get('frame', '')} posture={result.get('posture_label', 'Unknown')} fall={result.get('fall_detected', False)} confidence={result.get('confidence', 0.0)} labels={result.get('other_labels', '')}\n")
    except (PermissionError, OSError) as e:
        logger.error(f"Permission denied or I/O error writing to detections.log: {e}")

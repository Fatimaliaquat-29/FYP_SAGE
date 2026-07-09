import os
import sys
import csv
import logging
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
    # ── LSTM path ──────────────────────────────────────────────────────────────
    # When a pre-loaded LSTMPostureClassifier is supplied and the rolling
    # history contains enough frames to fill one window, defer to the LSTM.
    # The heuristic path (below) remains the default when lstm_classifier=None.
    if lstm_classifier is not None and lstm_classifier.is_available:
        required = lstm_classifier.window_size - 1
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
                row["fall_detected"] = lstm_result["fall_detected"]
                return lstm_result
            except Exception as exc:
                logger.warning(f"LSTM prediction failed (frame {row.get('frame', '?')}): {exc}. "
                               "Falling back to heuristic.")
    # ── Heuristic path ─────────────────────────────────────────────────────────
    pairs = _extract_keypoint_pairs(row)
    
    # 1. Handle missing critical landmarks for upper body / torso
    if not pairs or len(pairs) < 29:
        row["body_height"] = np.nan
        row["vertical_span"] = np.nan
        row["torso_angle"] = np.nan
        row["hip_height"] = np.nan
        row["knee_angle"] = np.nan
        row["velocity"] = 0.0
        row["raw_posture_label"] = "Unknown"
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

    sh_ok = is_landmark_valid(sh_l) and is_landmark_valid(sh_r)
    hp_ok = is_landmark_valid(hp_l) and is_landmark_valid(hp_r)
    kn_ok = is_landmark_valid(kn_l) and is_landmark_valid(kn_r)
    ak_ok = is_landmark_valid(ak_l) and is_landmark_valid(ak_r)

    # If shoulders OR hips are missing we genuinely cannot classify – return Unknown.
    # However, if ONLY the lower body (ankles + knees) is occluded (very common when
    # sitting on a bed where legs are hidden by the mattress/frame), we fall back to a
    # torso-only classification instead of blindly returning Unknown.
    if not sh_ok or not hp_ok:
        row["body_height"] = np.nan
        row["vertical_span"] = np.nan
        row["torso_angle"] = np.nan
        row["hip_height"] = np.nan
        row["knee_angle"] = np.nan
        row["velocity"] = 0.0
        row["raw_posture_label"] = "Unknown"
        return {
            "posture_label": "Unknown",
            "fall_detected": False,
            "confidence": 0.0,
            "other_labels": "missing_upper_body_keypoints",
        }

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

    # 2. Dynamic calibration from rolling history
    history_body_heights = [r.get("body_height") for r in (previous_rows or []) if r.get("body_height") is not None and not np.isnan(r.get("body_height"))]
    all_body_heights = history_body_heights + [body_height]
    max_body_height = max(all_body_heights) if all_body_heights else 1.0

    history_spans = [r.get("vertical_span") for r in (previous_rows or []) if r.get("vertical_span") is not None and not np.isnan(r.get("vertical_span"))]
    all_spans = history_spans + [vertical_span]
    max_span = max(all_spans) if all_spans else 1.0

    effective_max_bh = max(max_body_height, 0.50)
    effective_max_span = max(max_span, 0.50)

    # 3. Classify raw posture label using scale-invariant angles as primary signal
    ANGLE_STANDING_MIN = 155.0  # TODO-tune-with-real-footage
    ANGLE_SITTING_MAX = 125.0   # TODO-tune-with-real-footage

    raw_posture_label = "Unknown"
    other_labels = []
    angles_available = not np.isnan(knee_angle) and not np.isnan(hip_angle)
    angle_says_standing = (angles_available
                           and knee_angle >= ANGLE_STANDING_MIN
                           and hip_angle >= ANGLE_STANDING_MIN)

    if np.isnan(torso_angle):
        raw_posture_label = "Unknown"
        other_labels.append("invalid_angle")
    # Rule 1: Lying – large torso inclination (applies even without lower-body visibility)
    # Guard: if joint angles clearly say Standing, skip the vertical_span Lying heuristic
    #        (prevents false Lying when camera distance changes mid-session).
    elif torso_angle >= 45.0 or (not lower_body_occluded
                                  and not angle_says_standing
                                  and vertical_span < 0.40 * effective_max_span):
        raw_posture_label = "Lying"
        other_labels.append("horizontal_torso" if torso_angle >= 45.0 else "horizontal_span")
    elif lower_body_occluded:
        # ── Torso-only path (e.g. sitting on a bed with legs not visible) ──
        if hip_height > 0.55:
            raw_posture_label = "Standing"
            other_labels.append("torso_only_standing")
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

    # 4. Temporal Smoothing (2-Frame Persistence Filter)
    if previous_rows:
        prev_smoothed = previous_rows[-1].get("posture_label", "Unknown")
        if raw_posture_label == prev_smoothed:
            posture_label = raw_posture_label
        elif raw_posture_label == "Lying":
            # Direct transition to Lying to prevent fall detection delay
            posture_label = "Lying"
        elif previous_rows[-1].get("raw_posture_label") == raw_posture_label:
            # Transition to a new state only if sustained for 2 consecutive frames
            posture_label = raw_posture_label
        else:
            # Retain the previous state to filter out single-frame noise
            posture_label = prev_smoothed
    else:
        posture_label = raw_posture_label

    # 5. Fall detection logic
    # ── Constants (units: body-heights/sec and deg/sec) ────────────────────────
    FALL_VELOCITY_THRESHOLD      = 2.0    # body-heights/sec per frame to count as "fast"  # TODO-tune
    FALL_SUSTAINED_COUNT         = 2      # minimum fast frames in the window                # TODO-tune
    FALL_AVG_VELOCITY_FLOOR      = 1.5    # avg velocity over window (body-heights/sec)    # TODO-tune
    FALL_ANGULAR_VELOCITY_FLOOR  = 200.0  # torso angular velocity floor (deg/sec)         # TODO-tune
    FALL_LOOK_BACK_FRAMES        = 10     # how many recent frames to scan
    FALL_NON_LYING_WINDOW        = 15     # how far back to look for a non-Lying posture
    # ──────────────────────────────────────────────────────────────────────────────

    fall_detected = False
    confidence = 0.55
    velocity = 0.0

    # Compute torso angle delta and time-normalize to deg/sec
    prev_torso_angle = previous_rows[-1].get("torso_angle", np.nan) if previous_rows else np.nan
    torso_angle_delta = 0.0
    if not np.isnan(torso_angle) and not np.isnan(prev_torso_angle):
        torso_angle_delta = abs(torso_angle - prev_torso_angle)
    row["torso_angle_delta"] = torso_angle_delta

    dt_for_angle = 1.0 / 30.0
    if previous_rows:
        try:
            dt_for_angle = float(row.get("timestamp", 0)) - float(previous_rows[-1].get("timestamp", 0))
        except (TypeError, ValueError):
            pass
        if dt_for_angle <= 0:
            dt_for_angle = 1.0 / 30.0
    torso_angular_velocity = torso_angle_delta / dt_for_angle
    row["torso_angular_velocity"] = torso_angular_velocity

    if previous_rows:
        previous_row = previous_rows[-1]
        velocity = _compute_velocity(previous_row, row)
        row["velocity"] = velocity

        # Collect metrics over the recent look-back window
        look_back = previous_rows[-FALL_LOOK_BACK_FRAMES:]
        recent_velocities = [r.get("velocity", 0.0) for r in look_back] + [velocity]

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

        # Max angular velocity in the lookback window (the torso rotation happens
        # during the fall but is zero once the person is on the ground).
        recent_angular_velocities = (
            [r.get("torso_angular_velocity", 0.0) for r in look_back]
            + [torso_angular_velocity]
        )
        max_recent_angular_velocity = max(recent_angular_velocities) if recent_angular_velocities else 0.0

        # Fall signal: sustained rapid hip movement AND rapid torso rotation
        is_fall_motion = (
            fast_frame_count >= FALL_SUSTAINED_COUNT
            and avg_recent_velocity > FALL_AVG_VELOCITY_FLOOR
            and max_recent_angular_velocity > FALL_ANGULAR_VELOCITY_FLOOR
        )

        if posture_label == "Lying":
            if had_upright_recently and is_fall_motion:
                fall_detected = True
                confidence = 0.95
                other_labels.append("rapid_fall")
            else:
                confidence = 0.65
                other_labels.append("slow_lie")

        else:
            # ── Pre-Lying fall trigger ─────────────────────────────────────────
            if (had_upright_recently
                    and fast_frame_count >= (FALL_SUSTAINED_COUNT + 1)
                    and avg_recent_velocity > FALL_AVG_VELOCITY_FLOOR
                    and max_recent_angular_velocity > FALL_ANGULAR_VELOCITY_FLOOR):
                fall_detected = True
                confidence = 0.85
                other_labels.append("pre_lying_fall")
                logger.warning(
                    f"Frame {row.get('frame', 0)}: Pre-Lying FALL DETECTED! "
                    f"avg_v={avg_recent_velocity:.3f} fast_frames={fast_frame_count}"
                )
            else:
                confidence = 0.62

    else:
        row["velocity"] = 0.0
        row["torso_angle_delta"] = 0.0
        row["torso_angular_velocity"] = 0.0
        if posture_label == "Lying":
            confidence = 0.60
            other_labels.append("lying_static")

    # Log posture transition or fall detection
    prev_label = previous_rows[-1].get("posture_label", "Unknown") if previous_rows else None
    if prev_label and prev_label != posture_label:
        logger.info(f"Frame {row.get('frame', 0)}: Posture transition {prev_label} -> {posture_label}")

    if fall_detected:
        logger.warning(f"Frame {row.get('frame', 0)}: FALL DETECTED! Confidence: {confidence:.2f}")

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

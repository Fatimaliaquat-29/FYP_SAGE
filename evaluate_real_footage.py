"""
evaluate_real_footage.py
========================
Batch validation of the heuristic posture + fall pipeline against ground-truth-
labelled real video clips stored in test_footage/.

Usage
-----
  # Batch mode (auto-discovers all *_gt.csv in --batch_dir)
  python evaluate_real_footage.py --batch_dir test_footage --output_dir results

  # Single-clip mode
  python evaluate_real_footage.py ``
      --video test_footage/Fall_Curled.mov ``
      --ground_truth test_footage/Fall_Curled_gt.csv ``
      --test_case_name Fall_Curled ``
      --output_dir results
"""

import argparse
import os
import sys
import time
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

MODEL_PATH = str(REPO_ROOT / "models" / "pose_landmarker_full.task")
POSTURE_CLASSES = ["Standing", "Sitting", "Lying"]
FLAG_ACCURACY_THRESHOLD = 90.0
DEBUG_NORMAL_FALL_1 = False
DEBUG_SIT_3 = False


# ------------------------------------------------------------------------------
# Ground-truth helpers
# ------------------------------------------------------------------------------

def _parse_mmss(time_str: str) -> float:
    time_str = time_str.strip()
    parts = time_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    raise ValueError(f"Unexpected time format: {time_str!r}")


def _parse_time_any(time_str: str) -> float:
    """M:SS (legacy dialects) or plain decimal seconds (state/label dialect)."""
    time_str = time_str.strip()
    if ":" in time_str:
        return _parse_mmss(time_str)
    return float(time_str)


def _parse_bool(val: str) -> bool:
    return val.strip().upper() in ("TRUE", "1", "YES")


# Maps the third-dialect "state" column to the Standing/Sitting/Lying/Unknown
# vocabulary the scorer compares predictions against. "Fall" -> "Lying" because
# by the time the state settles into "Fall" the person IS lying on the floor;
# the actual falling motion lives in the "Transition State" segment, which is
# excluded from posture-accuracy scoring the same way the other dialects
# exclude their transition rows.
_STATE_TO_LABEL = {
    "standing": "Standing",
    "sitting": "Sitting",
    "lying": "Lying",
    "fall": "Lying",
}


def load_ground_truth(gt_path: str) -> pd.DataFrame:
    """
    Parse GT CSVs that appear in three dialects:
      (a) Each row is a single quoted string: "0:00, 0:05, Standing, FALSE"
      (b) Proper multi-column CSV with per-field quoting:
          "00:00,","00:06,","Standing,",FALSE
      (c) Header + decimal-seconds + state/label columns:
          start_time,end_time,state,label
          0.00,1.20,Standing,Standing
          1.20,2.30,Transition State,Falling (Backward)
          2.30,3.71,Fall,Fallen / Lying
    (a) and (b) use "M:SS" timestamps with an explicit ignore boolean in the
    4th column; (c) uses decimal-second timestamps with a "state" (mapped via
    _STATE_TO_LABEL) and a free-text descriptive "label" in the 4th column
    instead of a boolean -- the dialect is told apart by whether the raw time
    string contains ":".
    Uses csv.reader, then falls back to splitting on commas when the whole
    row was treated as one quoted string.
    """
    import csv as _csv

    rows = []
    try:
        with open(gt_path, "rb") as f:
            content = f.read()
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("windows-1252")
    import io
    with io.StringIO(text) as fh:
        for csv_fields in _csv.reader(fh):
            # Format (a): csv.reader wraps the entire row in one token
            if len(csv_fields) == 1:
                csv_fields = csv_fields[0].split(",")
            # Normalise: strip whitespace and trailing commas from every token
            parts = [f.strip().rstrip(",").strip() for f in csv_fields]
            parts = [p for p in parts if p]
            if len(parts) < 4:
                continue
            try:
                start = _parse_time_any(parts[0])
                end   = _parse_time_any(parts[1])
                if ":" in parts[0] or ":" in parts[1]:
                    # Dialect (a)/(b): explicit posture label + ignore boolean.
                    label  = parts[2]
                    ignore = _parse_bool(parts[3])
                else:
                    # Dialect (c): state/label schema, decimal seconds.
                    state_key = parts[2].strip().lower()
                    if "transition" in state_key:
                        label  = "Transition"
                        ignore = True
                    else:
                        label  = _STATE_TO_LABEL.get(state_key, parts[2])
                        ignore = False
            except (ValueError, IndexError):
                continue

            fall_start = np.nan
            fall_end   = np.nan
            if len(parts) >= 6:
                try:
                    fall_start = _parse_time_any(parts[4])
                    fall_end   = _parse_time_any(parts[5])
                except ValueError:
                    pass

            rows.append({
                "start_time":          start,
                "end_time":            end,
                "label":               label,
                "ignore":              ignore,
                "expected_fall_start": fall_start,
                "expected_fall_end":   fall_end,
            })

    if not rows:
        raise ValueError(f"No valid rows parsed from ground truth: {gt_path}")

    return pd.DataFrame(rows)



def build_frame_gt(gt_df: pd.DataFrame, fps: float, total_frames: int) -> pd.DataFrame:
    records = []
    for _, seg in gt_df.iterrows():
        start_frame = max(1, round(seg["start_time"] * fps))
        end_frame   = min(total_frames, round(seg["end_time"] * fps))
        for f in range(start_frame, end_frame + 1):
            records.append({
                "frame_number": f,
                "gt_label":     seg["label"],
                "ignore":       seg["ignore"],
            })

    if not records:
        return pd.DataFrame(columns=["frame_number", "gt_label", "ignore"])

    frame_gt = pd.DataFrame(records)
    frame_gt = frame_gt.drop_duplicates(subset=["frame_number"], keep="last")
    return frame_gt.set_index("frame_number")


def get_fall_window(gt_df: pd.DataFrame, fps: float) -> Optional[Tuple[int, int]]:
    explicit = gt_df.dropna(subset=["expected_fall_start", "expected_fall_end"])
    if not explicit.empty:
        row = explicit.iloc[0]
        return (round(row["expected_fall_start"] * fps),
                round(row["expected_fall_end"]   * fps))

    ordered = gt_df.sort_values("start_time").reset_index(drop=True)
    non_ignore = ordered[~ordered["ignore"]]
    lying_segs = non_ignore[non_ignore["label"].str.strip().str.lower() == "lying"]
    upright_segs = non_ignore[~non_ignore["label"].str.strip().str.lower().isin(["lying"])]
    # Only derive a fall window from the Lying segment when there is also an upright
    # segment in the GT — a clip that is Lying-only from the start has no fall event.
    if not lying_segs.empty and not upright_segs.empty:
        lying_pos = lying_segs.index[0]
        window_start_time = ordered.loc[lying_pos, "start_time"]
        window_end_time   = ordered.loc[lying_pos, "end_time"]

        # Extend the window backward through any immediately preceding
        # "ignored" segment(s) (a "Transition"/"Transition State" row marking
        # the actual falling motion). Without this, a detector that correctly
        # fires WHILE the person is falling -- the ideal early-warning
        # behavior, especially for a slow crumple -- gets scored as a false
        # positive purely because it landed before the person had finished
        # settling onto the floor. See docs/sanity_check_clips.md and the
        # Slow_fall.mp4 case this was found from.
        i = lying_pos - 1
        while i >= 0 and bool(ordered.loc[i, "ignore"]):
            window_start_time = ordered.loc[i, "start_time"]
            i -= 1

        return (round(window_start_time * fps), round(window_end_time * fps))

    return None


# ------------------------------------------------------------------------------
# Keypoint extraction
# ------------------------------------------------------------------------------

def extract_keypoints(video_path: str) -> Tuple[List[dict], float, int]:
    BaseOptions           = mp.tasks.BaseOptions
    PoseLandmarker        = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        # VIDEO mode (matches realtime_fall_detection.py): landmarks are tracked
        # across frames rather than re-detected independently, which removes the
        # frame-to-frame jitter that the fall logic would otherwise read as
        # genuine hip velocity / torso rotation.
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
    )
    detector = PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        detector.close()
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    rows       = []
    frame_count = 0
    start_wall  = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            # Use video-time (not wall-clock) so dt in _compute_velocity is the
            # true inter-frame interval regardless of CPU processing speed.
            ts = frame_count / fps

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            result    = detector.detect_for_video(mp_image, int(ts * 1000))

            row: dict = {"timestamp": ts, "frame_number": frame_count}
            if result.pose_landmarks:
                landmarks = result.pose_landmarks[0]
                for i, lm in enumerate(landmarks):
                    row[f"lm_{i}_x"]          = lm.x
                    row[f"lm_{i}_y"]          = lm.y
                    row[f"lm_{i}_z"]          = lm.z
                    row[f"lm_{i}_visibility"] = lm.visibility
                    row[f"lm_{i}_presence"]   = lm.presence
            else:
                for i in range(33):
                    row[f"lm_{i}_x"]          = np.nan
                    row[f"lm_{i}_y"]          = np.nan
                    row[f"lm_{i}_z"]          = np.nan
                    row[f"lm_{i}_visibility"] = np.nan
                    row[f"lm_{i}_presence"]   = np.nan

            rows.append(row)

            if frame_count % 60 == 0:
                elapsed = time.time() - start_wall
                print(f"  Extracted {frame_count}/{total_frames} frames "
                      f"({frame_count / elapsed:.1f} fps)")
    finally:
        cap.release()
        detector.close()

    return rows, fps, total_frames or frame_count


# ------------------------------------------------------------------------------
# Classification
# ------------------------------------------------------------------------------

def _keypoints_from_row(kp_row: dict) -> List[float]:
    flat = []
    for i in range(LANDMARK_COUNT):
        flat.append(kp_row.get(f"lm_{i}_x", np.nan))
        flat.append(kp_row.get(f"lm_{i}_y", np.nan))
    return flat


def _visibility_from_row(kp_row: dict) -> List[float]:
    """MediaPipe's per-joint confidence, already captured by extract_keypoints().
    Previously extracted and then discarded -- feeding it to build_pose_row is
    what stops occluded (guessed) joints being treated as observed ones."""
    return [kp_row.get(f"lm_{i}_visibility", np.nan) for i in range(LANDMARK_COUNT)]


def classify_frames(kp_rows: List[dict], clip_name: Optional[str] = None) -> List[dict]:
    # Reset all inter-frame pipeline state so clips don't bleed into each other
    reset_session_state()
    previous_rows: List[dict] = []
    results = []
    import src.posture.pipeline_utils as pu

    for kp_row in kp_rows:
        keypoints = _keypoints_from_row(kp_row)
        pose_row  = build_pose_row(
            timestamp=kp_row.get("timestamp"),
            frame=int(kp_row.get("frame_number", 0)),
            keypoints=keypoints,
            visibility=_visibility_from_row(kp_row),
        )

        classification = classify_posture_and_fall(pose_row, previous_rows=previous_rows)
        pose_row.update(classification)
        previous_rows.append(pose_row)

        # Build recent raw-label history string for Sit_2 diagnostics
        recent_raw = [
            r.get("raw_posture_label", "?") for r in previous_rows[-5:]
        ]
        recent_label_history = "|".join(recent_raw)

        if (DEBUG_NORMAL_FALL_1 and clip_name == "Normal_Fall_1" and 100 <= pose_row['frame'] <= 112) or \
           (DEBUG_SIT_3 and clip_name == "Sit_3" and 60 <= pose_row['frame'] <= 66):
            smoothed_ang_vel = float(np.median(list(pu._recent_angular_velocities))) if pu._recent_angular_velocities else 0.0
            print(
                f"[DEBUG {clip_name}] Frame {pose_row['frame']:3d} | "
                f"RawAngVel: {pose_row.get('torso_angular_velocity', 0.0):7.2f} | "
                f"SmoothedAngVel: {smoothed_ang_vel:7.2f} | "
                f"FramesAboveFloor: {pu._frames_angvel_above_floor:2d} | "
                f"PeakInWindow: {pu._peak_angvel_in_window:7.2f} | "
                f"Posture: {pose_row.get('posture_label', 'Unknown'):8s} | "
                f"RawPosture: {pose_row.get('raw_posture_label', 'Unknown'):8s}"
            )

        out = dict(kp_row)
        out["posture_label"]             = pose_row.get("posture_label", "Unknown")
        out["fall_detected"]             = pose_row.get("fall_detected", False)
        out["confidence"]                = pose_row.get("confidence", 0.0)
        out["other_labels"]              = pose_row.get("other_labels", "")
        out["knee_angle"]                = pose_row.get("knee_angle", np.nan)
        out["hip_angle"]                 = pose_row.get("hip_angle", np.nan)
        out["torso_angle"]               = pose_row.get("torso_angle", np.nan)
        out["velocity"]                  = pose_row.get("velocity", 0.0)
        out["torso_angular_velocity"]    = pose_row.get("torso_angular_velocity", 0.0)
        out["body_height"]               = pose_row.get("body_height", np.nan)
        out["hip_height"]                = pose_row.get("hip_height", np.nan)
        out["effective_max_bh"]          = pose_row.get("effective_max_bh", np.nan)
        out["lower_body_occluded"]       = pose_row.get("lower_body_occluded", np.nan)
        out["tracking_lost_after_fall"]  = pose_row.get("tracking_lost_after_fall", False)
        out["recent_label_history"]      = recent_label_history
        results.append(out)

    return results


# ------------------------------------------------------------------------------
# Scoring
# ------------------------------------------------------------------------------

def score_posture(
    classified: List[dict],
    frame_gt: pd.DataFrame,
) -> Tuple[float, Dict[str, Dict[str, int]], List[dict]]:
    all_labels = POSTURE_CLASSES + ["Unknown"]
    confusion: Dict[str, Dict[str, int]] = {
        c: {p: 0 for p in all_labels} for c in all_labels
    }
    correct    = 0
    total      = 0
    mismatches = []

    for row in classified:
        fn = int(row.get("frame_number", 0))
        if fn not in frame_gt.index:
            continue
        gt_entry = frame_gt.loc[fn]
        if gt_entry["ignore"]:
            continue

        gt_norm   = gt_entry["gt_label"].strip().capitalize()
        pred_norm = (row.get("posture_label", "Unknown") or "Unknown").capitalize()

        if gt_norm not in confusion:
            confusion[gt_norm] = {p: 0 for p in all_labels}
        confusion[gt_norm][pred_norm] = confusion[gt_norm].get(pred_norm, 0) + 1

        total += 1
        if gt_norm == pred_norm:
            correct += 1
        else:
            mismatches.append({
                "frame_number":             fn,
                "gt_label":                 gt_norm,
                "pred_label":               pred_norm,
                "knee_angle":               row.get("knee_angle", np.nan),
                "hip_angle":                row.get("hip_angle", np.nan),
                "torso_angle":              row.get("torso_angle", np.nan),
                "velocity":                 row.get("velocity", 0.0),
                "torso_angular_velocity":   row.get("torso_angular_velocity", 0.0),
                "body_height":              row.get("body_height", np.nan),
                "effective_max_bh":         row.get("effective_max_bh", np.nan),
                "hip_height":               row.get("hip_height", np.nan),
                "lower_body_occluded":      row.get("lower_body_occluded", np.nan),
                "tracking_lost_after_fall": row.get("tracking_lost_after_fall", False),
                "recent_label_history":     row.get("recent_label_history", ""),
            })

    accuracy = (correct / total * 100.0) if total > 0 else float("nan")
    return accuracy, confusion, mismatches


def score_fall(
    classified: List[dict],
    fall_window: Optional[Tuple[int, int]],
) -> dict:
    fall_frames = [row["frame_number"] for row in classified if row.get("fall_detected")]

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


def per_class_accuracy(confusion: Dict) -> Dict[str, float]:
    acc = {}
    for label in POSTURE_CLASSES:
        row_vals = confusion.get(label, {})
        tp    = row_vals.get(label, 0)
        total = sum(row_vals.values())
        acc[label] = (tp / total * 100.0) if total > 0 else float("nan")
    return acc


# ------------------------------------------------------------------------------
# Reporting helpers
# ------------------------------------------------------------------------------

def _fmt_fall(fall_result: dict) -> str:
    r = fall_result["result"]
    if r == "true_positive":
        return f"TP (latency {fall_result['latency']} frames)"
    if r == "false_negative":
        return "FN"
    if r == "false_positive":
        fps_str = ", ".join(str(f) for f in fall_result["fp_frames"][:5])
        return f"FP frames [{fps_str}]"
    return "-"


def _needs_flag(accuracy: float, fall_result: dict) -> str:
    issues = []
    if not (isinstance(accuracy, float) and np.isnan(accuracy)):
        if accuracy < FLAG_ACCURACY_THRESHOLD:
            issues.append(f"posture<{FLAG_ACCURACY_THRESHOLD:.0f}%")
    if fall_result["result"] in ("false_negative", "false_positive"):
        issues.append(fall_result["result"].replace("_", " "))
    return ", ".join(issues) if issues else ""


def print_clip_report(clip_name: str, accuracy: float, confusion: dict,
                      per_class: dict, fall_result: dict, mismatches: List[dict]):
    print(f"\n{'='*60}")
    print(f"  CLIP: {clip_name}")
    print(f"{'='*60}")
    print(f"  Posture accuracy (non-ignored frames): {accuracy:.1f}%")
    print()
    print("  Per-class accuracy:")
    for c in POSTURE_CLASSES:
        v = per_class.get(c, float("nan"))
        print(f"    {c:<10}: {v:.1f}%")
    print()
    all_labels = POSTURE_CLASSES + ["Unknown"]
    print("  Confusion matrix (rows=GT, cols=Pred):")
    col_header = "GT\\Pred"
    header = f"  {col_header:<12}" + "".join(f"{p[:7]:>9}" for p in all_labels)
    print(header)
    for gt_lbl in POSTURE_CLASSES:
        row_vals = confusion.get(gt_lbl, {})
        row_str = f"  {gt_lbl:<12}" + "".join(f"{row_vals.get(p, 0):>9}" for p in all_labels)
        print(row_str)
    print()
    print(f"  Fall detection: {_fmt_fall(fall_result)}")
    print()
    if mismatches:
        print(f"  Mismatched frames ({len(mismatches)} total):")
        print(f"  {'Frame':>6} {'GT':<12} {'Pred':<12} {'knee':>7} "
              f"{'hip':>7} {'torso':>7} {'vel':>8} {'angvel':>9} "
              f"{'bh':>7} {'emb':>7} {'hip_h':>7} {'lbo':>5} {'tlaf':>5} recent_labels")
        for m in mismatches[:50]:
            def _f(v):
                return f"{v:7.1f}" if not (isinstance(v, float) and np.isnan(v)) else "    nan"
            def _b(v):
                return "T" if v else "F"
            print(f"  {int(m['frame_number']):>6} {m['gt_label']:<12} {m['pred_label']:<12} "
                  f"{_f(m['knee_angle'])} {_f(m['hip_angle'])} {_f(m['torso_angle'])} "
                  f"{_f(m['velocity'])} {_f(m['torso_angular_velocity'])} "
                  f"{_f(m['body_height'])} {_f(m['effective_max_bh'])} {_f(m['hip_height'])} "
                  f"  {_b(m['lower_body_occluded'])}   {_b(m['tracking_lost_after_fall'])} "
                  f"{m.get('recent_label_history', '')}")
        if len(mismatches) > 50:
            print(f"  ... and {len(mismatches) - 50} more (see per-frame CSV)")
    else:
        print("  No mismatched frames")


# ------------------------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------------------------

def _confusion_md(confusion: dict) -> str:
    all_labels = POSTURE_CLASSES + ["Unknown"]
    header = "| GT \\ Pred |" + "|".join(f" {p} " for p in all_labels) + "|"
    sep    = "|" + "|".join("---" for _ in range(len(all_labels) + 1)) + "|"
    lines  = [header, sep]
    for gt_lbl in POSTURE_CLASSES:
        row_vals = confusion.get(gt_lbl, {})
        row = f"| **{gt_lbl}** |" + "|".join(
            f" {row_vals.get(p, 0)} " for p in all_labels
        ) + "|"
        lines.append(row)
    return "\n".join(lines)


def _mismatches_md(mismatches: List[dict]) -> str:
    if not mismatches:
        return "_None_"
    lines = ["| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in mismatches:
        def _f(v):
            return f"{v:.1f}" if not (isinstance(v, float) and np.isnan(v)) else "nan"
        def _b(v):
            return "T" if v else "F"
        lines.append(
            f"| {int(m['frame_number'])} | {m['gt_label']} | {m['pred_label']} "
            f"| {_f(m['knee_angle'])} | {_f(m['hip_angle'])} | {_f(m['torso_angle'])} "
            f"| {_f(m['velocity'])} | {_f(m['torso_angular_velocity'])} "
            f"| {_f(m['body_height'])} | {_f(m['effective_max_bh'])} | {_f(m['hip_height'])} "
            f"| {_b(m['lower_body_occluded'])} | {_b(m['tracking_lost_after_fall'])} "
            f"| {m.get('recent_label_history', '')} |"
        )
    return "\n".join(lines)


def append_clip_section(md_path: Path, clip_name: str, accuracy: float,
                        confusion: dict, per_class: dict, fall_result: dict,
                        mismatches: List[dict]):
    flag    = _needs_flag(accuracy, fall_result)
    flag_md = f" (**{flag}**)" if flag else ""

    with open(md_path, "a", encoding="utf-8") as fh:
        fh.write(f"\n---\n\n## {clip_name}{flag_md}\n\n")
        fh.write(f"**Posture accuracy:** {accuracy:.1f}%\n\n")
        fh.write("**Per-class accuracy:**\n\n")
        for c in POSTURE_CLASSES:
            fh.write(f"- {c}: {per_class.get(c, float('nan')):.1f}%\n")
        fh.write("\n**Confusion matrix:**\n\n")
        fh.write(_confusion_md(confusion))
        fh.write("\n\n**Fall detection:** " + _fmt_fall(fall_result) + "\n\n")
        fh.write("**Mismatched frames:**\n\n")
        fh.write(_mismatches_md(mismatches))
        fh.write("\n")


def write_summary_table(md_path: Path, summary_rows: List[dict]):
    existing = ""
    if md_path.exists():
        with open(md_path, "r", encoding="utf-8") as fh:
            existing = fh.read()
        sep_idx = existing.find("\n---\n")
        if sep_idx != -1:
            existing = existing[sep_idx:]

    header = (
        "# Real Footage Evaluation - Summary\n\n"
        "| Clip | Accuracy % | Fall Result | Flag |\n"
        "|---|---|---|---|\n"
    )
    table_rows = []
    for r in summary_rows:
        flag      = _needs_flag(r["accuracy"], r["fall_result"])
        flag_cell = f"**{flag}**" if flag else ""
        acc_str   = f"{r['accuracy']:.1f}%" if not (isinstance(r["accuracy"], float) and np.isnan(r["accuracy"])) else "N/A"
        table_rows.append(
            f"| {r['clip_name']} | {acc_str} | {_fmt_fall(r['fall_result'])} | {flag_cell} |"
        )

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(header + "\n".join(table_rows) + "\n")
        fh.write(existing)


# ------------------------------------------------------------------------------
# Per-frame CSV
# ------------------------------------------------------------------------------

EXPORT_COLUMNS = [
    "frame_number", "timestamp",
    "gt_label", "ignore",
    "posture_label", "fall_detected", "confidence", "other_labels",
    "knee_angle", "hip_angle", "torso_angle", "velocity", "torso_angular_velocity",
    "body_height", "effective_max_bh", "hip_height", "lower_body_occluded",
    "tracking_lost_after_fall", "recent_label_history",
]


def save_per_frame_csv(classified: List[dict], frame_gt: pd.DataFrame, out_path: Path):
    rows = []
    for row in classified:
        fn = int(row.get("frame_number", 0))
        if fn in frame_gt.index:
            gt_label = frame_gt.loc[fn, "gt_label"]
            ignore   = frame_gt.loc[fn, "ignore"]
        else:
            gt_label = ""
            ignore   = False

        rows.append({
            "frame_number":             fn,
            "timestamp":                row.get("timestamp", ""),
            "gt_label":                 gt_label,
            "ignore":                   ignore,
            "posture_label":            row.get("posture_label", "Unknown"),
            "fall_detected":            row.get("fall_detected", False),
            "confidence":               row.get("confidence", 0.0),
            "other_labels":             row.get("other_labels", ""),
            "knee_angle":               row.get("knee_angle", np.nan),
            "hip_angle":                row.get("hip_angle", np.nan),
            "torso_angle":              row.get("torso_angle", np.nan),
            "velocity":                 row.get("velocity", 0.0),
            "torso_angular_velocity":   row.get("torso_angular_velocity", 0.0),
            "body_height":              row.get("body_height", np.nan),
            "effective_max_bh":         row.get("effective_max_bh", np.nan),
            "hip_height":               row.get("hip_height", np.nan),
            "lower_body_occluded":      row.get("lower_body_occluded", np.nan),
            "tracking_lost_after_fall": row.get("tracking_lost_after_fall", False),
            "recent_label_history":     row.get("recent_label_history", ""),
        })

    pd.DataFrame(rows, columns=EXPORT_COLUMNS).to_csv(out_path, index=False)
    print(f"  Per-frame CSV saved: {out_path}")


# ------------------------------------------------------------------------------
# Single-clip evaluation
# ------------------------------------------------------------------------------

def evaluate_clip(
    video_path: str,
    gt_path: str,
    clip_name: str,
    output_dir: Path,
    md_path: Path,
) -> dict:
    print(f"\n[{clip_name}] Extracting keypoints from: {video_path}")
    kp_rows, fps, total_frames = extract_keypoints(video_path)
    print(f"  {total_frames} frames at {fps:.2f} fps")

    print(f"[{clip_name}] Classifying frames...")
    classified = classify_frames(kp_rows, clip_name=clip_name)

    gt_df       = load_ground_truth(gt_path)
    frame_gt    = build_frame_gt(gt_df, fps, total_frames)
    fall_window = get_fall_window(gt_df, fps)

    accuracy, confusion, mismatches = score_posture(classified, frame_gt)
    fall_result = score_fall(classified, fall_window)
    per_class   = per_class_accuracy(confusion)

    print_clip_report(clip_name, accuracy, confusion, per_class, fall_result, mismatches)

    csv_out = output_dir / f"{clip_name}_predictions.csv"
    save_per_frame_csv(classified, frame_gt, csv_out)

    append_clip_section(md_path, clip_name, accuracy, confusion, per_class,
                        fall_result, mismatches)

    return {"clip_name": clip_name, "accuracy": accuracy, "fall_result": fall_result}


# ------------------------------------------------------------------------------
# Batch discovery
# ------------------------------------------------------------------------------

def discover_clips(batch_dir: str) -> List[Tuple[str, str, str]]:
    batch      = Path(batch_dir)
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    pairs      = []

    for gt_file in sorted(batch.glob("*_gt.csv")):
        stem       = gt_file.stem[:-3]   # strip "_gt"
        video_file = None
        for ext in video_exts:
            candidate = batch / (stem + ext)
            if candidate.exists():
                video_file = candidate
                break
        if video_file is None:
            for f in batch.iterdir():
                if f.suffix.lower() in video_exts and f.stem.lower() == stem.lower():
                    video_file = f
                    break

        if video_file is None:
            print(f"  Warning: no video found for GT {gt_file.name}, skipping.")
            continue

        pairs.append((str(video_file), str(gt_file), stem))

    return pairs


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SAGE real-footage evaluation")
    mode   = parser.add_mutually_exclusive_group()
    mode.add_argument("--batch_dir",      type=str, default=None)
    mode.add_argument("--video",          type=str, default=None)
    parser.add_argument("--ground_truth",    type=str, default=None)
    parser.add_argument("--test_case_name",  type=str, default=None)
    parser.add_argument("--output_dir",      type=str, default="results")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "real_footage_results.md"

    if args.batch_dir:
        md_path.write_text("", encoding="utf-8")
        clips = discover_clips(args.batch_dir)
        if not clips:
            print(f"No paired clips found in {args.batch_dir}")
            sys.exit(1)
        print(f"Found {len(clips)} clip(s) in {args.batch_dir}")
        summary_rows = []
        for video_path, gt_path, clip_name in clips:
            summary = evaluate_clip(video_path, gt_path, clip_name, output_dir, md_path)
            summary_rows.append(summary)
        write_summary_table(md_path, summary_rows)

        print(f"\nSummary written to: {md_path}")
        print("\n" + "="*66)
        print("  TOP-LEVEL SUMMARY")
        print("="*66)
        print(f"  {'Clip':<30} {'Accuracy':>10}  {'Fall':<28}  Flag")
        print(f"  {'-'*30} {'-'*10}  {'-'*28}  {'-'*20}")
        for r in summary_rows:
            acc_str  = f"{r['accuracy']:.1f}%" if not (isinstance(r["accuracy"], float) and np.isnan(r["accuracy"])) else "N/A"
            fall_str = _fmt_fall(r["fall_result"])
            flag     = _needs_flag(r["accuracy"], r["fall_result"])
            print(f"  {r['clip_name']:<30} {acc_str:>10}  {fall_str:<28}  {flag}")
        print("="*66)

    elif args.video:
        if not args.ground_truth:
            parser.error("--ground_truth is required in single-clip mode")
        clip_name = args.test_case_name or Path(args.video).stem
        summary   = evaluate_clip(args.video, args.ground_truth, clip_name, output_dir, md_path)
        write_summary_table(md_path, [summary])
        print(f"\nReport written to: {md_path}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

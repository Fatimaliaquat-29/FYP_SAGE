import os
import sys
import csv
import glob
from pathlib import Path
import cv2
import mediapipe as mp

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import (
    build_pose_row,
    classify_posture_and_fall,
    LANDMARK_COUNT
)
from src.data_processing.build_lstm_datasets import make_video_detector

DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MODELS_DIR = REPO_ROOT / "models"
MODEL_PATH = MODELS_DIR / "pose_landmarker_full.task"

OUT_POSE_CSV = DATA_DIR / "processed_keypoints" / "real_pose_keypoints.csv"
OUT_POSTURE_CSV = DATA_DIR / "processed_keypoints" / "real_posture_output.csv"

# Frame rate this project's own recording/extraction pipeline assumes
# whenever a video's own real FPS isn't otherwise available (same fallback
# used by evaluate_real_footage.py and src/detection/generate_bbox_dataset.py:
# `cap.get(cv2.CAP_PROP_FPS) or 30.0`). If your recorded clips were captured
# at a materially different frame rate, pass `fps=` through to
# process_sequence() explicitly rather than relying on this default -- an
# incorrect FPS here still corrupts the velocity features, just less
# severely than the wall-clock bug this constant replaces.
RAW_FPS = 30.0


def get_image_files(directory):
    """Get sorted list of image files in a directory."""
    files = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        files.extend(glob.glob(os.path.join(directory, ext)))
    # Sort files to maintain chronological order
    files.sort()
    return files


def process_sequence(detector, sequence_dir, sequence_id, expected_fall=False, fps=RAW_FPS):
    """Extract keypoints and labels for a single image sequence.

    `detector` must be a fresh, VIDEO-mode PoseLandmarker for THIS sequence
    only (see make_video_detector() in build_lstm_datasets.py) -- VIDEO mode
    both carries tracking state and requires monotonically increasing
    timestamps across every call on one instance, so a detector shared
    across sequences either leaks tracking state or crashes outright the
    moment a second sequence's own clock restarts at 0.
    """
    image_files = get_image_files(sequence_dir)
    if not image_files:
        return [], []

    print(f"Processing sequence '{sequence_id}' ({len(image_files)} frames)...")

    pose_rows = []
    posture_rows = []
    previous_rows = []

    # To enforce 'Fall' label on the transition, we find when the person ends up lying
    # or if the heuristic detects a fall.
    # Simple approach: If expected_fall is True, any 'Lying' frame towards the end is a 'Fall',
    # or any frame where heuristic says fall_detected=True.

    for frame_idx, img_path in enumerate(image_files):
        frame_number = frame_idx + 1
        # Video time, NOT wall-clock -- see build_lstm_datasets.py's own
        # UR_FPS comment for the bug this fixes: using time.time() here
        # made the inter-frame dt depend on how fast THIS MACHINE could
        # read+process each image, not on the real motion recorded, which
        # scaled every velocity feature by processing speed rather than
        # real motion.
        current_time = frame_idx / fps

        frame = cv2.imread(img_path)
        if frame is None:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect_for_video(mp_image, int(current_time * 1000))

        landmark_pairs = []
        landmark_vis = []
        if detection_result.pose_landmarks:
            landmarks = detection_result.pose_landmarks[0]
            landmark_pairs = [(lm.x, lm.y) for lm in landmarks]
            # Visibility is carried through so occluded (guessed) joints are
            # dropped here exactly as they are at inference time -- otherwise the
            # LSTM trains on confident coordinates it will never see in practice.
            landmark_vis = [lm.visibility for lm in landmarks]

        row = build_pose_row(
            timestamp=str(current_time),
            frame=frame_number,
            landmarks=landmark_pairs,
            visibility=landmark_vis or None,
        )
        
        # Use heuristic to get baseline labels
        result = classify_posture_and_fall(row, previous_rows=previous_rows)
        row.update(result)
        
        # Override fall label if this is a fall event and heuristic missed it,
        # or just trust the heuristic for now and ensure "Fall" if expected_fall and lying.
        if expected_fall:
            if result["fall_detected"]:
                row["fall_detected"] = True
                row["posture_label"] = "Fall"
            elif result["posture_label"] == "Lying" and frame_number > len(image_files) * 0.3:
                # If they are lying down in the latter part of a fall sequence, label it Fall
                # so the LSTM learns the transition sequence resulting in a fall.
                row["fall_detected"] = True
                row["posture_label"] = "Fall"
                
        previous_rows.append(row)
        
        # Prepare for saving
        # Pose CSV needs: sequence_id, timestamp, frame, x1, y1, ..., x33, y33, posture_label, other_labels
        pose_row = {
            "sequence_id": sequence_id,
            "timestamp": row.get("timestamp", ""),
            "frame": row.get("frame", 0),
            "posture_label": row.get("posture_label", "Unknown"),
            "other_labels": row.get("other_labels", "")
        }
        keypoints = row.get("keypoints", [])
        for i in range(1, LANDMARK_COUNT + 1):
            idx_x = (i - 1) * 2
            idx_y = idx_x + 1
            pose_row[f"x{i}"] = keypoints[idx_x] if idx_x < len(keypoints) else ""
            pose_row[f"y{i}"] = keypoints[idx_y] if idx_y < len(keypoints) else ""
            
        pose_rows.append(pose_row)
        
        # Posture CSV needs: sequence_id, timestamp, frame, posture_label, fall_detected, confidence, etc.
        posture_row = {
            "sequence_id": sequence_id,
            "timestamp": row.get("timestamp", ""),
            "frame": row.get("frame", 0),
            "posture_label": row.get("posture_label", "Unknown"),
            "fall_detected": row.get("fall_detected", False),
            "confidence": row.get("confidence", 0.0),
            "other_labels": row.get("other_labels", ""),
            "body_height": row.get("body_height", ""),
            "torso_angle": row.get("torso_angle", ""),
            "hip_height": row.get("hip_height", "")
        }
        posture_rows.append(posture_row)

    return pose_rows, posture_rows


def main():
    print(f"Loading MediaPipe Pose Landmarker from: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        sys.exit(1)

    all_pose_rows = []
    all_posture_rows = []

    # A FRESH VIDEO-mode detector per sequence (see process_sequence()'s own
    # docstring for why a shared detector is unsafe) -- exactly the pattern
    # build_lstm_datasets.py::main() and build_ur_dataset_from_data_root.py
    # already use for the UR dataset.
    # Process ADL activities
    adl_dir = RAW_DIR / "adl_activities"
    if adl_dir.exists():
        # We only process -rgb directories as MediaPipe uses RGB
        for seq_path in sorted(adl_dir.iterdir()):
            if seq_path.is_dir() and seq_path.name.endswith("-rgb"):
                # Sometimes the images are inside another subfolder with the same name
                img_dir = seq_path / seq_path.name
                if not img_dir.exists():
                    img_dir = seq_path
                detector = make_video_detector()
                try:
                    p_rows, post_rows = process_sequence(detector, str(img_dir), seq_path.name, expected_fall=False)
                finally:
                    detector.close()
                all_pose_rows.extend(p_rows)
                all_posture_rows.extend(post_rows)

    # Process Fall events
    fall_dir = RAW_DIR / "fall_events"
    if fall_dir.exists():
        for seq_path in sorted(fall_dir.iterdir()):
            if seq_path.is_dir() and seq_path.name.endswith("-rgb"):
                img_dir = seq_path / seq_path.name
                if not img_dir.exists():
                    img_dir = seq_path
                detector = make_video_detector()
                try:
                    p_rows, post_rows = process_sequence(detector, str(img_dir), seq_path.name, expected_fall=True)
                finally:
                    detector.close()
                all_pose_rows.extend(p_rows)
                all_posture_rows.extend(post_rows)

    if not all_pose_rows:
        print("No image sequences found to process.")
        sys.exit(0)

    # Write to CSV
    print(f"Writing extracted keypoints to {OUT_POSE_CSV}")
    pose_headers = ["sequence_id", "timestamp", "frame"]
    for i in range(1, LANDMARK_COUNT + 1):
        pose_headers.extend([f"x{i}", f"y{i}"])
    pose_headers.extend(["posture_label", "other_labels"])
    
    with open(OUT_POSE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=pose_headers)
        writer.writeheader()
        writer.writerows(all_pose_rows)

    print(f"Writing extracted posture labels to {OUT_POSTURE_CSV}")
    posture_headers = [
        "sequence_id", "timestamp", "frame", "posture_label", "fall_detected", 
        "confidence", "other_labels", "body_height", "torso_angle", "hip_height"
    ]
    with open(OUT_POSTURE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=posture_headers)
        writer.writeheader()
        writer.writerows(all_posture_rows)

    print(f"Done! Processed {len(all_pose_rows)} frames in total.")

if __name__ == "__main__":
    main()

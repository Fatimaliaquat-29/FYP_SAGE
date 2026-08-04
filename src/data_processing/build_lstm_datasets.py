import os
import re
import sys
import csv
import glob
import time
import zipfile
import pandas as pd
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

DATA_DIR = REPO_ROOT / "data"
DATASETS_DIR = REPO_ROOT / "datasets"
MODELS_DIR = REPO_ROOT / "models"
MODEL_PATH = MODELS_DIR / "pose_landmarker_full.task"

OUT_DIR = DATA_DIR / "processed_keypoints"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_POSE_CSV = OUT_DIR / "pose_keypoints.csv"
OUT_POSTURE_CSV = OUT_DIR / "posture_output.csv"

# LeFD (Le2i Fall Detection) scenes.
# Only scenes with an Annotation(s)_files directory carry frame-accurate fall
# ground truth; Office/ and Lecture_room/ ship videos only (no annotations in
# this download) so they are skipped rather than guessed at.
LEFD_SCENES = [
    ("Coffee_room_01", "Coffee_room_01/Coffee_room_01"),
    ("Coffee_room_02", "Coffee_room_02/Coffee_room_02"),
    ("Home_01", "Home_01/Home_01"),
    ("Home_02", "Home_02/Home_02"),
]

# UP-Fall Activity Mapping
UPFALL_ACTIVITY_MAP = {
    1: "Fall",
    2: "Fall",
    3: "Fall",
    4: "Fall",
    5: "Fall",
    6: "Walking",
    7: "Standing",
    8: "Sitting",
    9: "Picking_Object",
    10: "Jumping",
    11: "Lying"
}


UR_FPS = 30.0   # UR Fall Detection image sequences are 30 FPS recordings


def make_video_detector():
    """A FRESH PoseLandmarker in VIDEO mode, for exactly one sequence.

    VIDEO mode is what realtime_fall_detection.py and evaluate_real_footage.py
    now use, and the training data has to be produced the same way: in IMAGE
    mode the landmarks jitter, which inflates the velocity half of the LSTM's
    input features (measured ~6x larger on still activities). A model trained
    on IMAGE-mode features and run on VIDEO-mode features is being asked to
    generalise across a distribution shift it never saw -- that is what made
    the previous model fire on ordinary sitting.

    One detector PER SEQUENCE: VIDEO mode carries tracking state between calls,
    so reusing a detector across clips would let one clip's pose leak into the
    first frames of the next.
    """
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
    )
    return mp.tasks.vision.PoseLandmarker.create_from_options(options)


def get_image_files(directory):
    files = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        files.extend(glob.glob(os.path.join(directory, ext)))
    files.sort()
    return files


def process_ur_sequence(detector, sequence_dir, sequence_id, expected_fall=False):
    image_files = get_image_files(sequence_dir)
    if not image_files:
        return [], []

    print(f"  [UR] Processing sequence '{sequence_id}' ({len(image_files)} frames)...")

    pose_rows = []
    posture_rows = []
    previous_rows = []
    
    for frame_idx, img_path in enumerate(image_files):
        frame_number = frame_idx + 1
        # Video time, NOT wall-clock. These images are consecutive frames of a
        # 30 FPS recording, so the inter-frame dt that _compute_velocity divides
        # by must be 1/30 s. Using time.time() here made dt the CPU's processing
        # time per frame, so every velocity feature in the UR half of the
        # training set was scaled by machine speed rather than real motion.
        current_time = frame_idx / UR_FPS

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
            landmark_vis = [lm.visibility for lm in landmarks]

        row = build_pose_row(
            timestamp=str(current_time),
            frame=frame_number,
            landmarks=landmark_pairs,
            visibility=landmark_vis or None,
        )

        result = classify_posture_and_fall(row, previous_rows=previous_rows)
        row.update(result)

        if expected_fall:
            if result["fall_detected"]:
                row["fall_detected"] = True
                row["posture_label"] = "Fall"
                
        previous_rows.append(row)
        
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


def parse_lefd_annotation(ann_path):
    """
    Parse a LeFD (Le2i) annotation .txt file.

    Format: line 1 = frame number where the fall begins, line 2 = frame
    number where the fall ends, followed by per-frame bounding boxes (unused
    here). Both 0 means the clip is a pure ADL/no-fall recording.

    Returns (fall_start, fall_end) as ints; (0, 0) if unparsable/no fall.
    """
    try:
        with open(ann_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
        fall_start = int(lines[0])
        fall_end = int(lines[1])
        return fall_start, fall_end
    except (IndexError, ValueError, OSError):
        return 0, 0


def process_lefd_video(detector, video_path, ann_path, sequence_id):
    """
    Process one LeFD video through MediaPipe and label frames.

    Ground truth (when an annotation file exists) drives a state machine
    identical in spirit to the UP-Fall fix: frames before the annotated fall
    are left to the heuristic's own Standing/Sitting/Lying/Unknown call,
    frames inside [fall_start, fall_end] are forced to "Fall", and frames
    after fall_end are forced to "Lying" (person down after impact). Pure
    ADL clips (fall_start == 0) are trusted entirely to the heuristic.
    """
    fall_start, fall_end = parse_lefd_annotation(ann_path) if ann_path and os.path.exists(ann_path) else (0, 0)
    has_fall = fall_start > 0 and fall_end >= fall_start

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return [], []

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    label = "FALL" if has_fall else "ADL"
    print(f"  [LeFD] Processing '{sequence_id}' ({total_frames} frames, {label})...")

    pose_rows = []
    posture_rows = []
    previous_rows = []
    frame_number = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_number += 1

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect_for_video(mp_image, int((frame_number / fps) * 1000))

        landmark_pairs = []
        landmark_vis = []
        if detection_result.pose_landmarks:
            landmarks = detection_result.pose_landmarks[0]
            landmark_pairs = [(lm.x, lm.y) for lm in landmarks]
            landmark_vis = [lm.visibility for lm in landmarks]

        row = build_pose_row(
            timestamp=str(frame_number / fps),
            frame=frame_number,
            landmarks=landmark_pairs,
            visibility=landmark_vis or None,
        )

        result = classify_posture_and_fall(row, previous_rows=previous_rows)
        row.update(result)

        if has_fall:
            if frame_number < fall_start:
                row["fall_detected"] = False  # pre-fall: trust heuristic's posture, but no fall yet
            elif frame_number <= fall_end:
                row["posture_label"] = "Fall"
                row["fall_detected"] = True
            else:
                row["posture_label"] = "Lying"
                row["fall_detected"] = False
        else:
            # Ground truth says this clip has no fall at all: never let the
            # heuristic's own fall_detected flag leak a "Fall" label onto
            # genuine ADL frames (e.g. lying on a couch) via _derive_label().
            row["fall_detected"] = False

        previous_rows.append(row)

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

    cap.release()
    return pose_rows, posture_rows


def process_lefd_dataset(detector):
    print("\nProcessing LeFD Dataset (Le2i, annotated scenes only)...")
    lefd_root = DATASETS_DIR / "LeFD"
    if not lefd_root.exists():
        print("LeFD dataset directory not found - skipping.")
        return [], []

    all_pose_rows = []
    all_posture_rows = []
    video_re = re.compile(r"\((\d+)\)")

    for scene_name, scene_rel in LEFD_SCENES:
        scene_dir = lefd_root / scene_rel
        if not scene_dir.exists():
            print(f"  [LeFD] Scene folder not found, skipping: {scene_dir}")
            continue

        videos_dir = scene_dir / "Videos"
        if not videos_dir.exists():
            print(f"  [LeFD] No Videos/ folder for scene {scene_name}, skipping.")
            continue

        # Annotation folder name is inconsistent across scenes
        # ("Annotation_files" vs "Annotations_files").
        ann_dir = None
        for cand in ("Annotation_files", "Annotations_files"):
            if (scene_dir / cand).exists():
                ann_dir = scene_dir / cand
                break

        video_files = sorted(videos_dir.glob("*.avi"))
        for video_path in video_files:
            m = video_re.search(video_path.stem)
            vid_num = m.group(1) if m else video_path.stem
            ann_path = (ann_dir / f"video ({vid_num}).txt") if ann_dir else None
            sequence_id = f"lefd_{scene_name.lower()}_v{vid_num}"

            # Fresh VIDEO-mode detector per video so tracking state cannot leak
            # from one clip into the opening frames of the next.
            detector = make_video_detector()
            try:
                p_rows, post_rows = process_lefd_video(detector, video_path, ann_path, sequence_id)
            finally:
                detector.close()
            all_pose_rows.extend(p_rows)
            all_posture_rows.extend(post_rows)

    print(f"  -> Extracted {len(all_pose_rows)} frames from LeFD dataset.")
    return all_pose_rows, all_posture_rows


def process_upfall_dataset():
    print("\nProcessing UP-Fall Dataset (3D Skeletons)...")
    upfall_dir = DATASETS_DIR / "3D_skeletons-UP-Fall-Dataset-main"
    if not upfall_dir.exists():
        print("UP-Fall dataset directory not found!")
        return [], []

    all_pose_rows = []
    
    zip_files = sorted(upfall_dir.glob("SUBJECT*.zip"))
    if not zip_files:
        print("No SUBJECT*.zip files found in UP-Fall dataset.")
        return [], []

    for zip_path in zip_files:
        print(f"  [UP-Fall] Reading {zip_path.name}...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX')]
            for csv_file in csv_files:
                try:
                    # Parse Activity ID from filename C1S1A1T1.csv
                    # Sometimes format is C2S1_A1_T2.csv
                    name_clean = csv_file.replace('_', '')
                    a_idx = name_clean.find('A')
                    t_idx = name_clean.find('T')
                    
                    if a_idx == -1 or t_idx == -1:
                        continue
                        
                    activity_id = int(name_clean[a_idx+1:t_idx])
                    target_label = UPFALL_ACTIVITY_MAP.get(activity_id, "Unknown")
                    
                    with z.open(csv_file) as f:
                        df = pd.read_csv(f)
                        
                        has_impact_occurred = False
                        for frame_idx, (_, row) in enumerate(df.iterrows()):
                            # Overwrite label if impact is explicitly tagged in the dataset
                            # LABEL == 1 means impact detected.
                            is_impact = False
                            if 'LABEL' in row and row['LABEL'] == 1:
                                is_impact = True
                                has_impact_occurred = True
                            
                            if activity_id in [1, 2, 3, 4, 5]: # Fall activities
                                if is_impact:
                                    final_label = "Fall"
                                elif has_impact_occurred:
                                    final_label = "Lying"
                                else:
                                    final_label = "Standing"
                            else:
                                final_label = target_label
                            
                            pose_row = {
                                "sequence_id": csv_file.replace('.csv', ''),
                                "timestamp": "",
                                "frame": frame_idx + 1,
                                "posture_label": final_label,
                                "other_labels": ""
                            }
                            
                            for i in range(1, LANDMARK_COUNT + 1):
                                x_col = f"Joint{i}_X"
                                y_col = f"Joint{i}_Y"
                                if x_col in row and y_col in row:
                                    pose_row[f"x{i}"] = row[x_col]
                                    pose_row[f"y{i}"] = row[y_col]
                                else:
                                    pose_row[f"x{i}"] = ""
                                    pose_row[f"y{i}"] = ""
                                    
                            all_pose_rows.append(pose_row)
                except Exception as e:
                    print(f"Error reading {csv_file} in {zip_path.name}: {e}")
                    
    print(f"  -> Extracted {len(all_pose_rows)} frames from UP-Fall dataset.")
    return all_pose_rows, []


def main():
    print(f"Loading MediaPipe Pose Landmarker from: {MODEL_PATH}")
    if not MODEL_PATH.exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        sys.exit(1)

    all_pose_rows = []
    all_posture_rows = []

    # 1. Process UR Dataset. A FRESH VIDEO-mode detector per sequence -- see
    #    make_video_detector() for why VIDEO mode, and why it must not be shared.
    print("\nProcessing UR Dataset (Raw Images)...")
    ur_dir = DATASETS_DIR / "UR_data"

    for sub, expected_fall in (("ADL", False), ("Fall", True)):
        sub_dir = ur_dir / sub
        if not sub_dir.exists():
            continue
        for seq_path in sorted(sub_dir.iterdir()):
            if not seq_path.is_dir():
                continue
            img_dir = seq_path / seq_path.name if (seq_path / seq_path.name).exists() else seq_path
            detector = make_video_detector()
            try:
                p_rows, post_rows = process_ur_sequence(
                    detector, str(img_dir), seq_path.name, expected_fall=expected_fall)
            finally:
                detector.close()
            all_pose_rows.extend(p_rows)
            all_posture_rows.extend(post_rows)

    # 2. Process LeFD Dataset (creates its own per-video detectors)
    lefd_pose_rows, lefd_posture_rows = process_lefd_dataset(None)
    all_pose_rows.extend(lefd_pose_rows)
    all_posture_rows.extend(lefd_posture_rows)

    # 3. UP-Fall is DELIBERATELY EXCLUDED.
    #    Those 5 SUBJECT*.zip files hold pre-computed 3D skeleton coordinates
    #    with no source frames, so they can never be re-extracted through
    #    MediaPipe: no visibility scores to gate on, no VIDEO-mode tracking, and
    #    a different coordinate convention entirely. Mixing them in would leave
    #    part of the training set permanently misaligned with what the camera
    #    actually produces at inference -- the exact mismatch this rebuild
    #    exists to remove. (Decision made with the team, July 2026.)

    if not all_pose_rows:
        print("No data found to process.")
        sys.exit(0)

    # 3. Write Output
    print(f"\nWriting extracted keypoints to {OUT_POSE_CSV}")
    pose_headers = ["sequence_id", "timestamp", "frame"]
    for i in range(1, LANDMARK_COUNT + 1):
        pose_headers.extend([f"x{i}", f"y{i}"])
    pose_headers.extend(["posture_label", "other_labels"])
    
    with open(OUT_POSE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=pose_headers)
        writer.writeheader()
        writer.writerows(all_pose_rows)

    if all_posture_rows:
        print(f"Writing extracted posture labels to {OUT_POSTURE_CSV}")
        posture_headers = [
            "sequence_id", "timestamp", "frame", "posture_label", "fall_detected", 
            "confidence", "other_labels", "body_height", "torso_angle", "hip_height"
        ]
        with open(OUT_POSTURE_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=posture_headers)
            writer.writeheader()
            writer.writerows(all_posture_rows)

    print(f"\nDone! Processed {len(all_pose_rows)} frames in total across all datasets.")

if __name__ == "__main__":
    main()

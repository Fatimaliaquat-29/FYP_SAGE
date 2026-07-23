import os
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
        current_time = time.time()
        
        frame = cv2.imread(img_path)
        if frame is None:
            continue
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        landmark_pairs = []
        if detection_result.pose_landmarks:
            landmarks = detection_result.pose_landmarks[0]
            landmark_pairs = [(lm.x, lm.y) for lm in landmarks]
            
        row = build_pose_row(
            timestamp=str(current_time),
            frame=frame_number,
            landmarks=landmark_pairs,
        )
        
        result = classify_posture_and_fall(row, previous_rows=previous_rows)
        row.update(result)
        
        if expected_fall:
            if result["fall_detected"]:
                row["fall_detected"] = True
                row["posture_label"] = "Fall"
            elif result["posture_label"] == "Lying" and frame_number > len(image_files) * 0.3:
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
                        
                        for frame_idx, (_, row) in enumerate(df.iterrows()):
                            # Overwrite label if impact is explicitly tagged in the dataset
                            # LABEL == 1 means impact detected.
                            is_impact = False
                            if 'LABEL' in row and row['LABEL'] == 1:
                                is_impact = True
                            
                            final_label = "Fall" if is_impact else target_label
                            
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

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE
    )
    detector = PoseLandmarker.create_from_options(options)

    all_pose_rows = []
    all_posture_rows = []

    # 1. Process UR Dataset
    print("\nProcessing UR Dataset (Raw Images)...")
    ur_dir = DATASETS_DIR / "UR_data"
    
    adl_dir = ur_dir / "ADL"
    if adl_dir.exists():
        for seq_path in sorted(adl_dir.iterdir()):
            if seq_path.is_dir():
                img_dir = seq_path / seq_path.name if (seq_path / seq_path.name).exists() else seq_path
                p_rows, post_rows = process_ur_sequence(detector, str(img_dir), seq_path.name, expected_fall=False)
                all_pose_rows.extend(p_rows)
                all_posture_rows.extend(post_rows)

    fall_dir = ur_dir / "Fall"
    if fall_dir.exists():
        for seq_path in sorted(fall_dir.iterdir()):
            if seq_path.is_dir():
                img_dir = seq_path / seq_path.name if (seq_path / seq_path.name).exists() else seq_path
                p_rows, post_rows = process_ur_sequence(detector, str(img_dir), seq_path.name, expected_fall=True)
                all_pose_rows.extend(p_rows)
                all_posture_rows.extend(post_rows)

    detector.close()

    # 2. Process UP-Fall Dataset
    upfall_pose_rows, _ = process_upfall_dataset()
    all_pose_rows.extend(upfall_pose_rows)
    
    # We do not strictly need posture_rows for UP-Fall since the LSTM trains mostly on pose_keypoints
    # But the heuristic script expects both if used later. The heuristic doesn't process UP-Fall directly here.

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

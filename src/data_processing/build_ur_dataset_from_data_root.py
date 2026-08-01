"""
build_ur_dataset_from_data_root.py
===================================
One-off adapter for the UR Fall Detection Dataset when it's dropped directly
under `data/ADL/` and `data/Fall/` (the layout used for this project's new
training-data drop) instead of `datasets/UR_data/ADL` and `datasets/UR_data/Fall`
(the layout `build_lstm_datasets.py::main()` expects).

Rather than duplicating the MediaPipe extraction logic or modifying
build_lstm_datasets.py's hardcoded DATASETS_DIR-based paths, this script
imports and reuses `process_ur_sequence` from that module unchanged and
points it at `data/ADL` / `data/Fall` directly. Output is written to the
exact same `data/processed_keypoints/pose_keypoints.csv` /
`posture_output.csv` paths `src/posture/lstm/lstm_dataset.py` already reads,
so no downstream file needs to change either.

Usage:
    python src/data_processing/build_ur_dataset_from_data_root.py
"""

import csv
import sys
from pathlib import Path

import mediapipe as mp

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import LANDMARK_COUNT
from src.data_processing.build_lstm_datasets import process_ur_sequence

DATA_DIR = REPO_ROOT / "data"
MODELS_DIR = REPO_ROOT / "models"
MODEL_PATH = MODELS_DIR / "pose_landmarker_full.task"

OUT_DIR = DATA_DIR / "processed_keypoints"
OUT_POSE_CSV = OUT_DIR / "pose_keypoints.csv"
OUT_POSTURE_CSV = OUT_DIR / "posture_output.csv"


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
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
    )
    detector = PoseLandmarker.create_from_options(options)

    all_pose_rows = []
    all_posture_rows = []

    adl_dir = DATA_DIR / "ADL"
    if adl_dir.exists():
        for seq_path in sorted(adl_dir.iterdir()):
            if seq_path.is_dir():
                img_dir = seq_path / seq_path.name if (seq_path / seq_path.name).exists() else seq_path
                p_rows, post_rows = process_ur_sequence(detector, str(img_dir), seq_path.name, expected_fall=False)
                all_pose_rows.extend(p_rows)
                all_posture_rows.extend(post_rows)
    else:
        print(f"  {adl_dir} not found - skipping.")

    fall_dir = DATA_DIR / "Fall"
    if fall_dir.exists():
        for seq_path in sorted(fall_dir.iterdir()):
            if seq_path.is_dir():
                img_dir = seq_path / seq_path.name if (seq_path / seq_path.name).exists() else seq_path
                p_rows, post_rows = process_ur_sequence(detector, str(img_dir), seq_path.name, expected_fall=True)
                all_pose_rows.extend(p_rows)
                all_posture_rows.extend(post_rows)
    else:
        print(f"  {fall_dir} not found - skipping.")

    detector.close()

    if not all_pose_rows:
        print("No sequences found under data/ADL or data/Fall.")
        sys.exit(0)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nWriting extracted keypoints to {OUT_POSE_CSV}")
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
        "confidence", "other_labels", "body_height", "torso_angle", "hip_height",
    ]
    with open(OUT_POSTURE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=posture_headers)
        writer.writeheader()
        writer.writerows(all_posture_rows)

    print(f"\nDone! Processed {len(all_pose_rows)} frames across "
          f"{len(set(r['sequence_id'] for r in all_pose_rows))} sequences.")


if __name__ == "__main__":
    main()

import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import (
    DATA_DIR,
    LANDMARK_COUNT,
    POSTURE_OUTPUT_CSV,
    build_pose_row,
    classify_posture_and_fall,
)


def main():
    input_csv = os.path.join(str(DATA_DIR), 'posture_features.csv')
    output_csv = str(POSTURE_OUTPUT_CSV)

    print(f"Reading posture features from: {input_csv}")
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} does not exist. Please run posture_features.py first.")
        sys.exit(1)

    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error: Could not read {input_csv}: {e}")
        sys.exit(1)

    if len(df) == 0:
        print("Error: Input features file is empty.")
        sys.exit(1)

    print("Classifying postures frame-by-frame...")

    postures = []
    fall_detected_list = []
    confidences = []
    other_labels_list = []
    previous_rows = []

    for idx, df_row in df.iterrows():
        keypoints = []
        for j in range(1, LANDMARK_COUNT + 1):
            x_val = df_row.get(f"x{j}", np.nan)
            y_val = df_row.get(f"y{j}", np.nan)
            keypoints.append(float(x_val) if pd.notna(x_val) else np.nan)
            keypoints.append(float(y_val) if pd.notna(y_val) else np.nan)

        row = build_pose_row(
            timestamp=df_row.get("timestamp"),
            frame=int(df_row.get("frame_number", 0)) if pd.notna(df_row.get("frame_number")) else 0,
            keypoints=keypoints,
        )

        result = classify_posture_and_fall(row, previous_rows=previous_rows)
        row.update(result)
        previous_rows.append(row)

        postures.append(result.get("posture_label", "Unknown"))
        fall_detected_list.append(result.get("fall_detected", False))
        confidences.append(result.get("confidence", 0.0))
        other_labels_list.append(result.get("other_labels", ""))

    df['posture_label'] = postures
    df['posture'] = postures  # backward compatibility
    df['fall_detected'] = fall_detected_list
    df['confidence'] = confidences
    df['other_labels'] = other_labels_list
    df['frame'] = df['frame_number']  # align column name

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_output = df[['timestamp', 'frame', 'frame_number', 'body_height', 'torso_angle', 'hip_height', 'posture_label', 'posture', 'fall_detected', 'confidence', 'other_labels']]
    df_output.to_csv(output_csv, index=False)
    print(f"Postures saved to: {output_csv}")

    # Calculate summary statistics
    counts = df_output['posture'].value_counts()
    total_frames = len(df_output)

    print("\n" + "="*50)
    print("          POSTURE CLASSIFICATION SUMMARY")
    print("="*50)
    for state in ['Standing', 'Sitting', 'Lying', 'Unknown']:
        count = counts.get(state, 0)
        percentage = (count / total_frames) * 100
        print(f"  {state:<10} : {count:>5} frames ({percentage:>6.1f}%)")
    print("="*50)

    # Print chronological state transitions and frame ranges
    print("\nState Timeline:")
    current_state = None
    start_frame = None

    timeline_blocks = []
    for idx, row in df_output.iterrows():
        f_num = int(row['frame_number'])
        posture = row['posture']

        if current_state is None:
            current_state = posture
            start_frame = f_num
        elif posture != current_state:
            timeline_blocks.append((current_state, start_frame, f_num - 1))
            current_state = posture
            start_frame = f_num

    # Add the last block
    if current_state is not None:
        timeline_blocks.append((current_state, start_frame, int(df_output.iloc[-1]['frame_number'])))

    for state, start, end in timeline_blocks:
        duration = end - start + 1
        print(f"  Frames {start:>4} - {end:>4} [{duration:>4} frames] : {state}")
    print("="*50 + "\n")


if __name__ == '__main__':
    main()


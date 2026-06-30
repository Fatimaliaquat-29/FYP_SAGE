import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import DATA_DIR, POSTURE_OUTPUT_CSV


def main():
    input_csv = os.path.join(str(DATA_DIR), 'posture_features.csv')
    output_csv = str(POSTURE_OUTPUT_CSV)

    print(f"Reading posture features from: {input_csv}")
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} does not exist. Please run posture_features.py first.")
        sys.exit(1)

    try:
        # Load and compute vertical span helper
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error: Could not read {input_csv}: {e}")
        sys.exit(1)

    if len(df) == 0:
        print("Error: Input features file is empty.")
        sys.exit(1)

    print("Classifying postures frame-by-frame...")

    # Calculate calibration metrics from data
    max_body_height = df['body_height'].dropna().max() if not df['body_height'].dropna().empty else 1.0
    
    # We estimate vertical span from average shoulder and ankle Y coordinates:
    # vertical_span = abs(avg_shoulder_y - avg_ankle_y)
    df['vertical_span'] = np.abs(df['avg_shoulder_y'] - df['avg_ankle_y'])
    max_span = df['vertical_span'].dropna().max() if not df['vertical_span'].dropna().empty else 1.0

    print(f"Calibration - Max Body Height: {max_body_height:.3f}, Max Vertical Span: {max_span:.3f}")

    postures = []
    fall_detected_list = []
    confidences = []
    other_labels_list = []

    previous_rows = []

    # Fallbacks
    effective_max_bh = max(max_body_height, 0.50)
    effective_max_span = max(max_span, 0.50)

    for idx, row in df.iterrows():
        body_height = row['body_height']
        vertical_span = row['vertical_span']
        torso_angle = row['torso_angle']
        hip_height = row['hip_height']

        # 1. Unknown classification: core values are missing or NaN
        if pd.isna(body_height) or pd.isna(torso_angle) or pd.isna(hip_height):
            posture_label = 'Unknown'
            fall_detected = False
            confidence = 0.0
            other_labels = 'missing_keypoints'
        else:
            # 2. Lying classification: large torso inclination OR extremely compressed vertical span
            if torso_angle >= 45.0 or vertical_span < 0.40 * effective_max_span:
                posture_label = 'Lying'
                other_labels = 'horizontal_torso' if torso_angle >= 45.0 else 'horizontal_span'
            # 3. Standing classification: close to max height
            elif body_height >= 0.92 * effective_max_bh:
                posture_label = 'Standing'
                other_labels = 'upright_max_height'
            # 4. Sitting classification: compressed body height
            elif body_height < 0.88 * effective_max_bh:
                posture_label = 'Sitting'
                other_labels = 'compressed_sitting'
            # 5. Default standing fallback
            else:
                posture_label = 'Standing'
                other_labels = 'upright'

            # Fall detection logic based on velocity (change of hip height)
            fall_detected = False
            confidence = 0.55
            velocity = 0.0

            if previous_rows:
                prev_row = previous_rows[-1]
                velocity = abs(hip_height - prev_row['hip_height'])

                if posture_label == 'Lying':
                    recent_non_lying = [r for r in previous_rows[-10:] if r['posture_label'] not in ['Lying', 'Unknown']]
                    if recent_non_lying:
                        recent_velocities = [r.get('velocity', 0.0) for r in previous_rows[-5:]] + [velocity]
                        max_recent_velocity = max(recent_velocities) if recent_velocities else 0.0

                        if max_recent_velocity > 0.07:
                            fall_detected = True
                            confidence = 0.95
                            other_labels += ',rapid_fall'
                        else:
                            confidence = 0.70
                            other_labels += ',slow_lie'
                    else:
                        confidence = 0.60
                        other_labels += ',lying_static'
                else:
                    confidence = 0.62
            else:
                if posture_label == 'Lying':
                    confidence = 0.60
                    other_labels += ',lying_static'

        curr_dict = {
            'body_height': body_height,
            'torso_angle': torso_angle,
            'hip_height': hip_height,
            'posture_label': posture_label,
            'velocity': velocity
        }
        previous_rows.append(curr_dict)

        postures.append(posture_label)
        fall_detected_list.append(fall_detected)
        confidences.append(confidence)
        other_labels_list.append(other_labels)

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

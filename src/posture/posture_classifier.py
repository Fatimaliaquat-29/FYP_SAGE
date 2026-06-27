import pandas as pd
import numpy as np
import os
import sys

def main():
    input_csv = 'data/processed_keypoints/posture_features.csv'
    output_csv = 'data/processed_keypoints/posture_output.csv'
    root_output_csv = 'posture_output.csv'

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

    # Calculate calibration metrics from data to adapt to different camera setups
    # If the user only performs one posture, we handle small variations gracefully
    max_body_height = df['body_height'].dropna().max() if not df['body_height'].dropna().empty else 1.0
    min_body_height = df['body_height'].dropna().min() if not df['body_height'].dropna().empty else 0.0
    
    max_hip_height = df['hip_height'].dropna().max() if not df['hip_height'].dropna().empty else 1.0
    min_hip_height = df['hip_height'].dropna().min() if not df['hip_height'].dropna().empty else 0.0

    print(f"Calibration - Max Body Height: {max_body_height:.3f}, Max Hip Height: {max_hip_height:.3f}")

    postures = []

    for idx, row in df.iterrows():
        body_height = row['body_height']
        torso_angle = row['torso_angle']
        hip_height = row['hip_height']

        # 1. Unknown classification: core values are missing or NaN
        if pd.isna(body_height) or pd.isna(torso_angle) or pd.isna(hip_height):
            postures.append('Unknown')
            continue

        # 2. Lying classification: large torso inclination (near horizontal)
        # Typically when laying down, torso angle is extreme (e.g. > 50 degrees)
        if abs(torso_angle) > 50.0:
            postures.append('Lying')
            
        # 3. Sitting classification:
        # Body height is compressed (knees bent, distance shoulder-to-ankle drops below 82% of max height)
        # AND hips are low (below 65% mark of the hip height range)
        elif body_height < 0.82 * max_body_height and hip_height < (min_hip_height + 0.65 * (max_hip_height - min_hip_height)):
            postures.append('Sitting')
            
        # 4. Standing classification:
        # Upright torso, high body height and high hip position (includes walking)
        else:
            postures.append('Standing')

    df['posture'] = postures

    # Save output to data/processed_keypoints/posture_output.csv
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_output = df[['timestamp', 'frame_number', 'body_height', 'torso_angle', 'hip_height', 'posture']]
    df_output.to_csv(output_csv, index=False)
    print(f"Postures saved to processed folder: {output_csv}")

    # Save copy to root posture_output.csv
    df_output.to_csv(root_output_csv, index=False)
    print(f"Postures saved to workspace root: {root_output_csv}")

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

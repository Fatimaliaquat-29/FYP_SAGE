import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

def main():
    input_csv = 'pose_keypoints.csv'
    output_dir = 'data/processed_keypoints'
    output_csv = os.path.join(output_dir, 'posture_features.csv')
    graphs_dir = 'docs'

    print(f"Reading raw pose keypoints from: {input_csv}")
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} does not exist. Please run the keypoint exporter first.")
        sys.exit(1)

    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error: Could not read {input_csv}: {e}")
        sys.exit(1)

    if len(df) == 0:
        print(f"Error: {input_csv} contains no rows.")
        sys.exit(1)

    print("Computing features...")

    # Calculate average coordinates for shoulders (landmarks 11 and 12)
    df['avg_shoulder_x'] = (df['lm_11_x'] + df['lm_12_x']) / 2
    df['avg_shoulder_y'] = (df['lm_11_y'] + df['lm_12_y']) / 2
    df['avg_shoulder_z'] = (df['lm_11_z'] + df['lm_12_z']) / 2

    # Calculate average coordinates for hips (landmarks 23 and 24)
    df['avg_hip_x'] = (df['lm_23_x'] + df['lm_24_x']) / 2
    df['avg_hip_y'] = (df['lm_23_y'] + df['lm_24_y']) / 2
    df['avg_hip_z'] = (df['lm_23_z'] + df['lm_24_z']) / 2

    # Calculate average coordinates for ankles (landmarks 27 and 28)
    df['avg_ankle_x'] = (df['lm_27_x'] + df['lm_28_x']) / 2
    df['avg_ankle_y'] = (df['lm_27_y'] + df['lm_28_y']) / 2
    df['avg_ankle_z'] = (df['lm_27_z'] + df['lm_28_z']) / 2

    # 1. Body height: 3D Euclidean distance between average shoulder and average ankle
    df['body_height'] = np.sqrt(
        (df['avg_shoulder_x'] - df['avg_ankle_x'])**2 +
        (df['avg_shoulder_y'] - df['avg_ankle_y'])**2 +
        (df['avg_shoulder_z'] - df['avg_ankle_z'])**2
    )

    # 2. Torso angle: inclination relative to vertical axis (upward is -dy since Y-axis is downward)
    dy = df['avg_shoulder_y'] - df['avg_hip_y']
    dx = df['avg_shoulder_x'] - df['avg_hip_x']
    # np.arctan2(dx, -dy) gives angle in radians where 0 is vertical upright, positive is leaning right, negative is leaning left
    df['torso_angle'] = np.degrees(np.arctan2(dx, -dy))

    # 3. Hip height: height above frame bottom (Y = 1.0)
    df['hip_height'] = 1.0 - df['avg_hip_y']

    # 4. Hip drop: height difference from previous frame (positive value indicates a downward drop)
    df['hip_drop'] = df['hip_height'].shift(1) - df['hip_height']

    # 5. Hip movement: 2D Euclidean distance of average hip positions between consecutive frames
    df['hip_movement'] = np.sqrt(
        (df['avg_hip_x'] - df['avg_hip_x'].shift(1))**2 +
        (df['avg_hip_y'] - df['avg_hip_y'].shift(1))**2
    )

    # Clean CSV Columns
    output_columns = [
        'timestamp', 'frame_number', 'body_height', 'torso_angle', 
        'hip_height', 'hip_drop', 'hip_movement',
        'avg_shoulder_x', 'avg_shoulder_y', 'avg_shoulder_z',
        'avg_hip_x', 'avg_hip_y', 'avg_hip_z',
        'avg_ankle_x', 'avg_ankle_y', 'avg_ankle_z'
    ]

    # Save to data/processed_keypoints/posture_features.csv
    os.makedirs(output_dir, exist_ok=True)
    df_output = df[output_columns]
    df_output.to_csv(output_csv, index=False)
    print(f"Features saved to: {output_csv}")

    # Print Summary Statistics (ignoring NaN)
    print("\n" + "="*50)
    print("           POSTURE FEATURES SUMMARY STATISTICS")
    print("="*50)
    stats_cols = ['body_height', 'torso_angle', 'hip_height', 'hip_drop', 'hip_movement']
    summary = df_output[stats_cols].describe().T[['mean', 'std', 'min', 'max']]
    print(summary.to_string())
    print("="*50 + "\n")

    # Generate and save premium visualization graphs
    os.makedirs(graphs_dir, exist_ok=True)
    print("Generating verification graphs...")

    # Plot settings for clean, premium appearance
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['grid.color'] = '#cccccc'
    plt.rcParams['axes.edgecolor'] = '#888888'
    plt.rcParams['axes.linewidth'] = 0.8

    # Filter rows with valid coordinates to prevent plotting gaps/errors
    df_valid = df_output.dropna(subset=['body_height', 'torso_angle', 'hip_height'])
    frames = df_valid['frame_number']

    # 1. Torso Angle Plot
    plt.figure(figsize=(10, 4))
    plt.plot(frames, df_valid['torso_angle'], color='#4361ee', linewidth=2, label='Torso Angle')
    plt.title('Torso Inclination Angle over Time', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Frame Number', fontsize=10)
    plt.ylabel('Angle (Degrees)', fontsize=10)
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.grid(True)
    plt.tight_layout()
    torso_plot_path = os.path.join(graphs_dir, 'torso_angle.png')
    plt.savefig(torso_plot_path, dpi=150)
    plt.close()
    print(f"Graph saved: {torso_plot_path}")

    # 2. Hip Height Plot
    plt.figure(figsize=(10, 4))
    plt.plot(frames, df_valid['hip_height'], color='#f72585', linewidth=2, label='Hip Height')
    plt.title('Hip Height over Time (Frame bottom = 0)', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Frame Number', fontsize=10)
    plt.ylabel('Normalized Height [0-1]', fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    hip_plot_path = os.path.join(graphs_dir, 'hip_height.png')
    plt.savefig(hip_plot_path, dpi=150)
    plt.close()
    print(f"Graph saved: {hip_plot_path}")

    # 3. Body Height Plot
    plt.figure(figsize=(10, 4))
    plt.plot(frames, df_valid['body_height'], color='#4cc9f0', linewidth=2, label='Body Height')
    plt.title('Skeletal Body Height over Time', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Frame Number', fontsize=10)
    plt.ylabel('Normalized Distance [0-1]', fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    height_plot_path = os.path.join(graphs_dir, 'body_height.png')
    plt.savefig(height_plot_path, dpi=150)
    plt.close()
    print(f"Graph saved: {height_plot_path}")

    print("\nFeature extraction and visualization completed successfully.")

if __name__ == '__main__':
    main()

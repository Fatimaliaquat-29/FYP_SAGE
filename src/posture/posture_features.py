import os
import sys
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import DATA_DIR, POSE_KEYPOINTS_CSV


def main():
    parser = argparse.ArgumentParser(description="SAGE Posture Features Extractor")
    parser.add_argument('--input', type=str, default=str(POSE_KEYPOINTS_CSV), help="Path to input pose keypoints CSV")
    parser.add_argument('--output', type=str, default=os.path.join(str(DATA_DIR), 'posture_features.csv'), help="Path to output features CSV")
    args = parser.parse_args()

    input_csv = args.input
    output_csv = args.output
    output_dir = os.path.dirname(output_csv)
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

    # Calculate average coordinates for shoulders (landmarks 11 and 12, mapping to columns x12, y12 and x13, y13)
    df['avg_shoulder_x'] = (df['x12'] + df['x13']) / 2
    df['avg_shoulder_y'] = (df['y12'] + df['y13']) / 2

    # Calculate average coordinates for hips (landmarks 23 and 24, mapping to columns x24, y24 and x25, y25)
    df['avg_hip_x'] = (df['x24'] + df['x25']) / 2
    df['avg_hip_y'] = (df['y24'] + df['y25']) / 2

    # Calculate average coordinates for ankles (landmarks 27 and 28, mapping to columns x28, y28 and x29, y29)
    df['avg_ankle_x'] = (df['x28'] + df['x29']) / 2
    df['avg_ankle_y'] = (df['y28'] + df['y29']) / 2

    # 1. Body height: 2D Euclidean distance between average shoulder and average ankle
    df['body_height'] = np.sqrt(
        (df['avg_shoulder_x'] - df['avg_ankle_x'])**2 +
        (df['avg_shoulder_y'] - df['avg_ankle_y'])**2
    )

    # 2. Torso angle: inclination relative to upward vertical axis (0, -1) in screen-space
    dy = df['avg_shoulder_y'] - df['avg_hip_y']
    dx = df['avg_shoulder_x'] - df['avg_hip_x']
    dist = np.sqrt(dx**2 + dy**2)
    # Avoid division by zero
    safe_dist = np.where(dist < 1e-6, np.nan, dist)
    cosine = -dy / safe_dist
    cosine = np.clip(cosine, -1.0, 1.0)
    df['torso_angle'] = np.degrees(np.arccos(cosine))

    # 3. Hip height: height above frame bottom (Y = 1.0)
    df['hip_height'] = 1.0 - df['avg_hip_y']

    # 4. Hip drop: height difference from previous frame (positive value indicates a downward drop)
    frame_col = 'frame' if 'frame' in df.columns else 'frame_number'
    df['frame_number'] = df[frame_col]
    
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
        'avg_shoulder_x', 'avg_shoulder_y',
        'avg_hip_x', 'avg_hip_y',
        'avg_ankle_x', 'avg_ankle_y'
    ]

    if output_dir:
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

    if len(frames) > 0:
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

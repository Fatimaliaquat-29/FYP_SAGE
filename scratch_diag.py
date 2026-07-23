import os
import pandas as pd
import numpy as np

results_dir = r"c:\University\FYP\fatima\fatima\results"
clips = [f.replace("_predictions.csv", "") for f in os.listdir(results_dir) if f.endswith("_predictions.csv")]

print("=== Diagnostic 1: Sit_3 Raw AngVel ===")
sit3_df = pd.read_csv(os.path.join(results_dir, "Sit_3_predictions.csv"))
consec = 0
max_consec = 0
for val in sit3_df["torso_angular_velocity"]:
    if not np.isnan(val) and val > 200.0:
        consec += 1
        max_consec = max(max_consec, consec)
    else:
        consec = 0
print(f"Max consecutive raw torso_angular_velocity > 200.0 in Sit_3: {max_consec} (Floor requires 5)")

print("\n=== Diagnostic 2: Normal_Fall_1 Determinism ===")
nf1_df = pd.read_csv(os.path.join(results_dir, "Normal_Fall_1_predictions.csv"))
n_missing = nf1_df["body_height"].isna().sum()
n_dupes = nf1_df["timestamp"].duplicated().sum()
print(f"Normal_Fall_1: {len(nf1_df)} frames, {n_missing} missing bh, {n_dupes} duplicate timestamps")
# also check dt variation
nf1_df["dt"] = nf1_df["timestamp"].diff()
print(f"Normal_Fall_1 dt stats: min={nf1_df['dt'].min():.4f}, max={nf1_df['dt'].max():.4f}, std={nf1_df['dt'].std():.4f}")


print("\n=== Diagnostic 3: 13-Clip Velocity Sweep ===")
for clip in clips:
    df = pd.read_csv(os.path.join(results_dir, f"{clip}_predictions.csv"))
    max_v = df["velocity"].max()
    max_av = df["torso_angular_velocity"].max()
    print(f"{clip:25s}: Max Vel = {max_v:.2f}, Max AngVel = {max_av:.2f}")


print("\n=== Task 1: Lying-Persistence cutoffs ===")
def get_lying_runs(df):
    runs = []
    current_run = 0
    start_idx = None
    for i, row in df.iterrows():
        if row["posture_label"] == "Lying":
            if current_run == 0:
                start_idx = row["frame_number"]
            current_run += 1
        else:
            if current_run > 0:
                runs.append((start_idx, current_run))
                current_run = 0
    if current_run > 0:
        runs.append((start_idx, current_run))
    return runs

for clip in clips:
    df = pd.read_csv(os.path.join(results_dir, f"{clip}_predictions.csv"))
    runs = get_lying_runs(df)
    
    print(f"[{clip}] Lying runs:")
    for start, length in runs:
        # Determine if this run is inside the expected fall window.
        # Fall window logic: in our prediction CSV, 'gt_label' might be 'Fall' or we just check if it overlaps with Lying in GT.
        # But wait, gt_label is 'Lying' after the fall. 
        # A simpler way: just report the lengths of all Lying runs. We can visually inspect which ones correspond to the real fall.
        print(f"  Start: {start}, Length: {length} frames")

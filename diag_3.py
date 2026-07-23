import pandas as pd
import numpy as np
import subprocess
import threading
import time

def cpu_spinner():
    while True:
        _ = [x**2 for x in range(1000)]

print("=== Diagnostic 1: Raw-only AngVel Counter ===")
sit3 = pd.read_csv("results/Sit_3_predictions.csv")
nf1 = pd.read_csv("results/Normal_Fall_1_predictions.csv")

def print_raw_counter(df, name, start, end):
    counter = 0
    print(f"\n{name} Frames {start}-{end}:")
    for idx, row in df.iterrows():
        frame = row['frame_number']
        angvel = row['torso_angular_velocity']
        if pd.notna(angvel) and angvel > 200.0:
            counter += 1
        else:
            counter = 0
            
        if start <= frame <= end:
            print(f"Frame {int(frame)}: angvel = {angvel:.1f}, counter = {counter}")

print_raw_counter(sit3, "Sit_3", 61, 66)
print_raw_counter(nf1, "Normal_Fall_1", 104, 108)


print("\n=== Diagnostic 2: Normal_Fall_1 Determinism ===")
# Start CPU spinner
t = threading.Thread(target=cpu_spinner, daemon=True)
t.start()

import evaluate_real_footage as erf
from pathlib import Path
import json

for run in range(1, 4):
    print(f"Run {run} starting...")
    # Clean previous output if needed
    erf.reset_session_state()
    # Run single clip evaluate_clip
    # To capture exact trigger path, we need to inspect the CSV or the logger.
    # evaluate_clip saves to results/Normal_Fall_1_predictions.csv
    # We can just call evaluate_clip manually.
    erf.evaluate_clip(
        video_path="test_footage/Normal_Fall_1.mov",
        gt_path="test_footage/Normal_Fall_1_gt.csv",
        clip_name="Normal_Fall_1",
        output_dir=Path("results"),
        md_path=Path("results/temp_md.md")
    )
    df = pd.read_csv("results/Normal_Fall_1_predictions.csv")
    falls = df[df["fall_detected"] == True]
    if not falls.empty:
        first_fall = falls.iloc[0]
        frame = first_fall["frame_number"]
        labels = first_fall["other_labels"]
        print(f"  Run {run}: Fall at frame {int(frame)}, tags: {labels}")
    else:
        print(f"  Run {run}: No fall detected.")

print("\n=== Diagnostic 3: Fall_Curled Trigger Investigation ===")
fc = pd.read_csv("results/Fall_Curled_predictions.csv")
print("Frame | AngVel | Fall Detected | Other Labels")
for idx, row in fc.iterrows():
    frame = int(row['frame_number'])
    if 1 <= frame <= 115:
        angvel = row['torso_angular_velocity']
        fd = row['fall_detected']
        ol = row['other_labels']
        if fd or (pd.notna(angvel) and angvel > 150):
            print(f"{frame:5d} | {angvel:6.1f} | {fd} | {ol}")
        # Only print the one that triggers the fall, and the few frames before it
        elif frame > 30 and frame < 45:
             print(f"{frame:5d} | {angvel:6.1f} | {fd} | {ol}")


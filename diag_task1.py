import os
import pandas as pd

results_dir = r"c:\University\FYP\fatima\fatima\results"
clips = [f.replace("_predictions.csv", "") for f in os.listdir(results_dir) if f.endswith("_predictions.csv")]

def get_lying_runs(df):
    runs = []
    current_run = 0
    for i, row in df.iterrows():
        if row["posture_label"] == "Lying":
            current_run += 1
        else:
            if current_run > 0:
                runs.append(current_run)
                current_run = 0
    if current_run > 0:
        runs.append(current_run)
    return runs

for clip in clips:
    path = os.path.join(results_dir, f"{clip}_predictions.csv")
    if not os.path.exists(path):
        continue
    df = pd.read_csv(path)
    runs = get_lying_runs(df)
    if runs:
        print(f"[{clip}] Max Lying Run: {max(runs)} frames")
    else:
        print(f"[{clip}] No Lying Runs")

import numpy as np
import pandas as pd
import json

def main():
    print("Loading lstm_dataset.npz...")
    data = np.load('data/lstm_dataset.npz', allow_pickle=True)
    X = data['X']
    y = data['y']
    
    with open('models/lstm_label_encoder.json', 'r') as f:
        encoder = json.load(f)
    
    # Actually, CLASS_TO_IDX is Fall=0, Lying=1, Sitting=2, Standing=3, Unknown=4 in lstm_dataset.py
    # But let's verify what index Fall is by looking at y counts.
    unique, counts = np.unique(y, return_counts=True)
    fall_idx = 0  # Assuming 0 is Fall from lstm_dataset output
    
    print(f"Total windows: {len(y)}")
    
    # We want to know: What percentage of "Fall" windows contain a transition?
    # And are there pure static Lying frames left in the "Fall" class?
    
    # Wait, X doesn't contain labels, it contains keypoints!
    # To check if a window contains a transition, we need the labels inside the window.
    # The simplest way is to run a check on the pose_keypoints.csv with the same sliding window logic.
    
    df = pd.read_csv('data/processed_keypoints/pose_keypoints.csv', low_memory=False)
    
    if 'label' not in df.columns:
        df['label'] = df['posture_label']
        
    df = df.dropna(subset=['posture_label'])
    
    window_size = 30
    step = 1
    
    fall_windows_total = 0
    fall_windows_with_transition = 0
    fall_windows_pure_lying = 0
    
    for seq_id, seq_df in df.groupby("sequence_id"):
        seq_df = seq_df.sort_values("frame").reset_index(drop=True)
        postures = seq_df['posture_label'].values
        
        n_frames = len(postures)
        if n_frames < window_size:
            continue
            
        for start in range(0, n_frames - window_size + 1, step):
            window_labels = postures[start: start + window_size]
            
            # Replicate lstm_dataset.py logic
            if "Fall" in window_labels:
                label = "Fall"
            else:
                label = window_labels[-1]
                
            if label == "Fall":
                fall_windows_total += 1
                
                # A transition means there is a non-Fall/non-Lying frame AND a Fall/Lying frame, 
                # OR it explicitly contains Fall (which IS the transition frame now!)
                # Since we only label it Fall if "Fall" is in the window, 
                # and "Fall" is only assigned during impact/detection.
                has_fall_frame = "Fall" in window_labels
                has_pre_fall = any(p in ["Standing", "Unknown"] for p in window_labels)
                has_post_fall = "Lying" in window_labels
                
                if has_fall_frame:
                    fall_windows_with_transition += 1
                
                # Check for pure static Lying (this should be impossible now since we require "Fall" to be in the window to label it Fall)
                is_pure_lying = all(p == "Lying" for p in window_labels)
                if is_pure_lying:
                    fall_windows_pure_lying += 1
                    
    print(f"\nVerification Results:")
    print(f"Total 'Fall' windows generated: {fall_windows_total}")
    if fall_windows_total > 0:
        print(f"Percentage of Fall windows containing the transition (a 'Fall' frame): {fall_windows_with_transition / fall_windows_total * 100:.1f}%")
        print(f"Number of Fall windows that are PURE static Lying frames: {fall_windows_pure_lying} ({fall_windows_pure_lying / fall_windows_total * 100:.1f}%)")
    else:
        print("No Fall windows found!")

if __name__ == '__main__':
    main()

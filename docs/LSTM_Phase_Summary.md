# S.A.G.E. LSTM Phase — Status, Discoveries, and Challenges
**Date:** July 2026

## 1. The Goal
Following the S.A.G.E. FYP Continuation Plan, we transitioned from single-frame pose heuristics to building a temporal model (LSTM). The primary goal of the LSTM was to capture the *temporal dynamics* of movement across a rolling 30-frame window. Specifically, we wanted the LSTM to detect "slow crumple" falls that do not generate enough sudden angular velocity to trigger the heuristic rules.

## 2. What We Accomplished
Over the course of the LSTM phase, we successfully built an end-to-end training and evaluation pipeline:
- **Temporal Dataset Construction:** Processed 33-landmark MediaPipe keypoints into a sliding-window dataset.
- **Synthetic Augmentation:** Implemented runtime data augmentation (synthetic rotations and noise) to artificially expand the dataset and improve model robustness.
- **Resolved Severe Data Leakage:** Discovered that the initial random train/validation split allowed frames from the exact same fall recording to exist in both sets, artificially inflating accuracy to 93%.
- **Strict Real-World Validation:** Refactored the data pipeline (`lstm_dataset.py` and `lstm_trainer.py`) to enforce a pristine, 100% real-data validation set using `StratifiedGroupKFold`. 
- **Hybrid Evaluation Harness:** Created `hybrid_evaluate.py` to run the Heuristic layer and the LSTM layer in parallel on real-world video clips, combining them with an OR-gate logic (`fall = Heuristic OR LSTM`).

## 3. Key Discoveries (The Wins)
After enforcing strict dataset separation and retraining the model on the clean split, the LSTM achieved an honest **83.12% accuracy** on entirely unseen real sequences.
- **True Learning:** The LSTM genuinely learned the physical dynamics of falling. It achieved a 98% recall rate on unseen fall recordings.
- **Latency Reduction:** During the Hybrid Evaluation, we discovered the LSTM excels at early detection. On `newTest.mov` (a slow fall), the LSTM triggered the fall alarm **41 frames earlier** than the heuristic. On `normal.mov`, it triggered 30 frames earlier.

## 4. The Core Problem (The FP Crisis)
Despite the successes on actual falls, the Hybrid Evaluation revealed a critical flaw: **The LSTM generates permanent, high-confidence False Positives on normal activities like sitting down.**

### The "First-Window Glitch" vs The Reality
Initially, it appeared the LSTM was just glitching when a clip started. We attempted two fixes:
1. **45-Frame Warm-up:** Suppressed the LSTM for the first 1.5 seconds.
2. **Consecutive-Frame Gate:** Required the LSTM to predict "Fall" for 6 frames in a row.

Neither fix worked. A deep dive into the raw probability data for `Sit_1.mov` (a person sitting on a couch) revealed that the LSTM reaches a **97% confidence that sitting is falling**, and maintains that >50% probability for the entire remainder of the clip.

### The Root Cause: Severe Dataset Imbalance
The LSTM fundamentally cannot distinguish between an uncontrolled fall and a controlled descent (sitting/lying down). 
- In a 30-frame window, both actions involve a downward trajectory.
- Our training dataset has **111 real fall sequences**, but only **~7 sitting sequences** and **~6 lying sequences**.
- The model simply never had enough negative examples to learn the subtle geometrical differences between falling and sitting. It essentially learned a shortcut: `"Person going down = Fall"`.

Because the Hybrid pipeline uses an **OR Gate**, the perfect zero-FP record of the Heuristic system is currently being ruined by the high-FP rate of the LSTM.

## 5. Next Steps and Options
We have reached the absolute limit of what this specific LSTM model can do with the current, imbalanced dataset. To progress the S.A.G.E. project, we must choose one of the following paths:

1. **Massive Dataset Expansion (Data-Centric Fix):** Go back to the data gathering phase and record/label vastly more ADL (Activities of Daily Living) clips—specifically Sitting, Bending, and Lying down—so the model can learn negative examples.
2. **Move to TCN Phase (Model-Centric Fix):** The Continuation Plan outlines evaluating a **Temporal Convolutional Network (TCN)**. TCNs process time-series data differently than LSTMs and may capture the nuance of "controlled" vs "uncontrolled" descent better.
3. **Change the Hybrid Architecture:** Stop using an OR-gate. Rely *only* on the Heuristic for the final, hard alarm, and use the LSTM purely as a "low-latency early warning" UI indicator.

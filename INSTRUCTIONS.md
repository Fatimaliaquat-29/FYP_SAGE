# S.A.G.E. — Setup & Run Instructions

Fall detection pipeline: a rule-based heuristic and an LSTM, combined in an OR-gate hybrid, with a real-time camera entry point. See `context.txt` for the full technical history if you need to understand *why* something works the way it does — this file is just "how do I run it."

---

## 1. One-time setup

### 1.1 Python environment
Requires Python 3.11.

```bash
python -m venv .venv2
# Windows (PowerShell):
.venv2\Scripts\Activate.ps1
# Windows (Git Bash) / macOS / Linux:
source .venv2/Scripts/activate   # or .venv2/bin/activate on macOS/Linux

pip install -r requirements.txt
```

### 1.2 Pose model
`models/pose_landmarker_full.task` must exist (it's committed to the repo — if it's missing, download MediaPipe's `pose_landmarker_full.task` and place it there).

### 1.3 Trained LSTM model
`models/lstm_posture.keras` and `models/lstm_label_encoder.json` are committed to the repo — you do **not** need to retrain anything to run the system. Retraining is only needed if you change the dataset or the feature pipeline (see Section 5).

### 1.4 Data folders NOT in git
`data/`, `datasets/`, and `Testing/` are excluded from version control (large/regenerable). If you need them:
- `data/` — regenerate via Section 5 below, or copy it from a teammate.
- `datasets/` — the raw training sources (UR Fall, UP-Fall, LeFD). Only needed if retraining from scratch. Get this from a teammate/shared drive.
- `Testing/` — recorded validation footage. Get this from a teammate/shared drive, or record your own following `docs/sanity_check_clips.md`.

---

## 2. Run it live, through a camera

This is the actual deployable entry point: `realtime_fall_detection.py`.

```bash
# Default webcam (device 0), hybrid mode (heuristic OR LSTM), with a preview window:
python realtime_fall_detection.py

# A different camera (e.g. an external/USB webcam is often device 1):
python realtime_fall_detection.py --input 1

# Replay a video file as if it were a live feed (useful for testing without a camera):
python realtime_fall_detection.py --input "Testing/Sanawar Testing 7-22-26/Normal_Fall_1.mov"

# Heuristic only, no LSTM:
python realtime_fall_detection.py --no-lstm

# Headless (no preview window — for a server/Pi with no display):
python realtime_fall_detection.py --no-display
```

**While running:** a green/amber/red posture label and FPS counter are overlaid on the video. When a fall is confirmed, a red border and "FALL DETECTED" banner appear, and `*** FALL ALERT ***` is printed to the console. Press `q` in the preview window (or Ctrl+C in the terminal) to quit.

**Tuning the alert sensitivity**, if it's too jumpy or too slow to confirm:
```bash
python realtime_fall_detection.py --alert-window 12 --alert-min-hits 4 --alert-hold 5.0
```
- `--alert-window` / `--alert-min-hits`: an alert fires once the fall signal has been present in at least `min-hits` of the last `window` frames. Lower `min-hits` (relative to `window`) = more sensitive, more prone to false alarms.
- `--alert-hold`: once alarmed, how many seconds it stays latched before it can re-arm.

**Wiring up a real notification** (SMS/email/dashboard): `realtime_fall_detection.run()` takes an `on_alert(event: dict)` callback (`event` has `frame`, `timestamp`, `posture`, `labels`). If you're calling it from your own script rather than the CLI:
```python
from realtime_fall_detection import run

def notify(event):
    print(f"Send an alert! {event}")
    # e.g. requests.post(your_webhook_url, json=event)

run(input_source=0, on_alert=notify)
```

---

## 3. Run it against a recorded video, with scoring against ground truth

Use this to check accuracy on a specific clip, not just watch it live. Needs a paired ground-truth CSV (see `docs/sanity_check_clips.md` Section 4 for the format).

**Heuristic only:**
```bash
# One clip:
python evaluate_real_footage.py --video path/to/clip.mp4 --ground_truth path/to/clip_gt.csv --test_case_name clip_name --output_dir results/my_run

# A whole folder (auto-pairs every *_gt.csv with its same-named video):
python evaluate_real_footage.py --batch_dir "Testing/Sanawar Testing 7-22-26" --output_dir results/my_run
```

**Heuristic + LSTM (hybrid), with a side-by-side comparison table:**
```bash
python hybrid_evaluate.py --video path/to/clip.mp4 --ground_truth path/to/clip_gt.csv --output_dir results/my_run
python hybrid_evaluate.py --batch_dir "Testing/Sanawar Testing 7-22-26" --output_dir results/my_run
```

Both print a summary table (accuracy / TP-FP-FN / latency) and write a per-frame CSV + markdown report to `--output_dir`.

**No ground truth for your clip?** You can still see what the pipeline detects — there just won't be a scored accuracy table. Ask whoever is running the session to run the clip through `hybrid_evaluate.py`'s underlying functions directly (`extract_keypoints` + `classify_frames_hybrid`) and inspect the per-frame CSV, or just use Section 2's live-replay mode and watch the console output.

---

## 4. Recording new validation footage

Follow `docs/sanity_check_clips.md` — it covers camera setup, the exact list of fall/no-fall scenarios worth recording, and the ground-truth CSV format. Put new recordings in `Testing/<YourName> Testing <date>/` to match the existing convention.

---

## 5. Rebuilding the training data / retraining the LSTM

Only needed if you're adding new training footage or changing the feature pipeline — not needed to just run the system.

```bash
# 1. Process raw videos/datasets (datasets/) into frame-level keypoint CSVs (data/processed_keypoints/):
python src/data_processing/build_lstm_datasets.py

# 2. Build the sliding-window training set (data/lstm_dataset.npz):
python src/posture/lstm/lstm_dataset.py

# 3. Sanity-check the labels (should report 100% of Fall windows contain a real transition frame):
python verify_labels.py

# 4. Train (saves models/lstm_posture.keras + models/lstm_label_encoder.json):
python src/posture/lstm/lstm_trainer.py
```

Step 1 requires `datasets/` (not in git — see Section 1.4). Steps 2-4 only need `data/processed_keypoints/` from step 1.

---

## 6. Running the tests

```bash
python -m unittest tests.test_lstm_pipeline -v
```
21 tests covering dataset building, NaN imputation, the LSTM classifier's fallback behavior, and integration with the heuristic. Some tests are skipped if `models/lstm_posture.keras` is missing.

---

## 7. Quick reference — what to run for what

| I want to... | Run this |
|---|---|
| See it work live on a webcam | `python realtime_fall_detection.py` |
| Try it on a video file like a live feed | `python realtime_fall_detection.py --input <path>` |
| Get an accuracy score on a labeled clip | `python hybrid_evaluate.py --video <path> --ground_truth <path>` |
| Score a whole folder of labeled clips | `python hybrid_evaluate.py --batch_dir <folder>` |
| Check the heuristic alone (no LSTM) | `python evaluate_real_footage.py --batch_dir <folder>` or `realtime_fall_detection.py --no-lstm` |
| Record new test clips | Read `docs/sanity_check_clips.md` |
| Retrain after adding data | Section 5 above |
| Understand *why* a threshold/design choice is what it is | `context.txt` |

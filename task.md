# SAGE Development Task Tracker

This file tracks the project lifecycle milestones and phases.

## Phase 1: Environment & Camera Integration (Current)
- [x] Create project workspace folder tree structure
- [x] Configure Python 3.11 virtual environment (`.venv`)
- [x] Install core packages (`opencv-python`, `mediapipe`, `numpy`, `pandas`, `matplotlib`)
- [x] Save active dependencies to `requirements.txt`
- [x] Verify webcam ingestion loop with real-time FPS overlay (`src/camera/camera_test.py`)
- [x] Document environment configuration (`docs/setup.md`)

## Phase 2: MediaPipe Pose Estimation Integration (Current)
- [x] Download official `pose_landmarker_full.task` to `models/`
- [x] Implement joint landmark extraction and connect skeletal bone lines overlays (`src/pose/pose_test.py`)
- [x] Export X, Y, Z, visibility, and presence coordinates for 33 joints to CSV format (`src/pose/save_keypoints.py`)
- [x] Document MediaPipe coordination logic and index topology (`docs/mediapipe_pose_reference.md`)

## Phase 3: Posture Feature Extraction (Completed)
- [x] Create feature extractor module (`src/posture/posture_features.py`)
- [x] Read pose keypoints and compute average shoulder, hip, and ankle positions
- [x] Compute body height (3D Euclidean distance), torso inclination angle, and hip height
- [x] Compute hip drop and hip movement metrics between consecutive frames
- [x] Export postural features to CSV (`data/processed_keypoints/posture_features.csv`)
- [x] Graph torso angle, hip height, and body height over time

## Phase 4: Posture Classification (Current)
- [x] Create posture classifier script (`src/posture/posture_classifier.py`)
- [x] Classify each frame into Standing, Sitting, Lying, or Unknown based on dynamic calibration
- [x] Log posture classification outputs to CSV (`posture_output.csv` in root)
- [x] Output chronological state timeline segments and statistics summary
- [ ] Record test videos for walking, sitting, standing, turning, and falling down
- [ ] Process raw videos to export keypoint CSV dataset sequences
- [ ] Train/calibrate ML classifiers on extracted feature sets
- [ ] Implement fall detection heuristics/temporal thresholds (e.g., rapid vertical height change followed by continuous lying down)

## Phase 5: Caregiver Dashboard & Integration (Upcoming)
- [ ] Implement web dashboard UI using modern premium styling
- [ ] Integrate local real-time feed with state classifications overlays
- [ ] Configure threshold triggers for text/email notifications upon fall detection

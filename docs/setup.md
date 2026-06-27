# SAGE Development Environment Setup

This document describes how to set up the development environment for SAGE (Smart AI Guardian for Elderly).

## Environment Requirements
- **Python Version**: 3.11.x (Python 3.11.9 is used for testing)
- **Operating System**: Windows

## Folder Structure
```
SAGE/ (Workspace Root)
│
├── .venv/                      # Python 3.11 Virtual Environment
├── data/
│   ├── raw_videos/            # Raw video feeds for testing
│   ├── processed_keypoints/   # Keypoint features generated from videos
│   └── datasets/              # Training/validation datasets
│
├── docs/
│   ├── setup.md               # This setup guide
│   └── mediapipe_pose_reference.md # MediaPipe API coordinates & mapping guide
├── logs/                      # Application diagnostics & execution logs
├── models/
│   └── pose_landmarker_full.task # Downloaded MediaPipe Pose Landmarker model
├── notebooks/                 # Jupyter notebooks for analytical modeling
├── src/
│   ├── camera/
│   │   └── camera_test.py     # Webcam capture and FPS verification script
│   ├── pose/
│   │   ├── pose_test.py       # Live skeleton landmark overlay rendering script
│   │   └── save_keypoints.py  # Coordinates exporter to pose_keypoints.csv
│   ├── posture/               # Future posture classification module
│   ├── fall_detection/        # Future fall detection classifier
│   ├── dashboard/             # Future web interface dashboard
│   ├── logging/               # Logger handlers
│   └── utils/                 # Utility files
├── tests/                     # Test suite
├── README.md                  # Project overview
├── requirements.txt           # Python frozen requirements list
└── task.md                    # Project checklist file
```

## Setup Instructions

1. **Verify Python 3.11 Availability**:
   Verify Python 3.11 exists on your system.
   ```powershell
   py -3.11 --version
   ```

2. **Create the Virtual Environment**:
   Initialize `.venv` with Python 3.11.
   ```powershell
   py -3.11 -m venv .venv
   ```

3. **Activate the Virtual Environment**:
   - **PowerShell**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Command Prompt (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```

4. **Install Dependencies**:
   Upgrade `pip` and install frozen requirements.
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. **Download Model File**:
   If `models/pose_landmarker_full.task` is missing, you can download it via python command:
   ```powershell
   python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task', 'models/pose_landmarker_full.task')"
   ```

6. **Running Verification Scripts**:
   - **Basic Camera Verification**:
     Checks camera input capture, frame loop, and FPS overlay. Press `Q` to quit.
     ```powershell
     python src/camera/camera_test.py
     ```
   - **Pose Skeleton Overlay Verification**:
     Checks MediaPipe initialization, tracking, and joint connection lines overlays. Press `Q` to quit.
     ```powershell
     python src/pose/pose_test.py
     ```
   - **Keypoint Exporter CSV Logging**:
     Outputs coordinates (X, Y, Z, Visibility, Presence) for all 33 joints to a CSV. Press `Q` to quit.
     ```powershell
     python src/pose/save_keypoints.py
     ```

## Core Dependencies Installed

Here are the primary libraries installed in our environment:
* **`mediapipe` (0.10.35)**: Used for high-fidelity hand, face, and body pose estimation.
* **`opencv-python` (4.13.0.92)**: Used for capture, scaling, image manipulation, frame rendering, and drawing overlays.
* **`numpy` (2.4.6)**: Provides multi-dimensional array support for frame buffers and matrix analysis.
* **`pandas` (3.0.3)**: Provides dataframes for exporting coordinates efficiently to CSV.
* **`matplotlib` (3.11.0)**: Used for plotting joints, trajectories, and debugging.

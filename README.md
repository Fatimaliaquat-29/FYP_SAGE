# SAGE: Smart AI Guardian for Elderly

SAGE is a real-time computer vision and pose analysis application designed to monitor, assist, and safeguard elderly individuals. SAGE utilizes non-invasive optical cameras, deep learning-based pose estimation, and activity analysis to detect falls, classify postures, and alert caregivers of potential hazards.

## Project Vision
To provide a secure, low-latency, and privacy-focused guardian solution that runs on local hardware or edge systems, ensuring continuous safety without relying on invasive wearables.

## Directory Structure
Refer to [setup.md](file:///c:/Sage/docs/setup.md) for a detailed description of the project layout.

## Getting Started

1. **Prerequisites**: Python 3.11.x installed.
2. **Setup virtual environment**:
   ```powershell
   py -3.11 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
4. **Download the model**:
   Ensure `pose_landmarker_full.task` is placed in `models/`.
5. **Run test scripts**:
   - Camera test: `python src/camera/camera_test.py`
   - Pose estimation visual overlay: `python src/pose/pose_test.py`
   - Exporter CSV: `python src/pose/save_keypoints.py`
   - Postural feature extraction: `python src/posture/posture_features.py`
   - Posture classification: `python src/posture/posture_classifier.py`

## Reference Docs
- [SAGE Environment Setup Instructions](file:///c:/Sage/docs/setup.md)
- [MediaPipe Pose Landmarker Reference](file:///c:/Sage/docs/mediapipe_pose_reference.md)

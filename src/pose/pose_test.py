import argparse
import sys
import time
from pathlib import Path

import cv2
import mediapipe as mp

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import (
    POSE_KEYPOINTS_CSV,
    POSTURE_OUTPUT_CSV,
    append_detection_log,
    build_pose_row,
    classify_posture_and_fall,
    write_pose_outputs,
)

# Define standard MediaPipe Pose Connections (33 landmarks)
POSE_CONNECTIONS = [
    # Face (nose, eyes, ears, mouth corners)
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    # Shoulders and Torso
    (11, 12), (11, 23), (12, 24), (23, 24),
    # Left Arm
    (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    # Right Arm
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    # Left Leg
    (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
    # Right Leg
    (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
]

def draw_skeleton(image, landmarks, connections, min_visibility=0.5):
    h, w, _ = image.shape
    
    # 1. Draw connections (bones)
    for connection in connections:
        start_idx, end_idx = connection
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start_lm = landmarks[start_idx]
            end_lm = landmarks[end_idx]
            
            # Draw line if both landmarks are visible enough
            if start_lm.visibility >= min_visibility and end_lm.visibility >= min_visibility:
                start_pt = (int(start_lm.x * w), int(start_lm.y * h))
                end_pt = (int(end_lm.x * w), int(end_lm.y * h))
                # Use a pleasant light green for bones
                cv2.line(image, start_pt, end_pt, (100, 240, 100), 2, cv2.LINE_AA)
                
    # 2. Draw landmarks (joints)
    for idx, lm in enumerate(landmarks):
        if lm.visibility >= min_visibility:
            pt = (int(lm.x * w), int(lm.y * h))
            
            # Sleek color coding for joints:
            if idx < 11:
                color = (0, 120, 255) # Orange/red-ish for face points
            elif idx in [11, 12, 23, 24]:
                color = (255, 50, 50) # Blue for torso joints (shoulders/hips)
            else:
                color = (0, 255, 255) # Yellow/Cyan for limb joints
                
            cv2.circle(image, pt, 4, color, -1, cv2.LINE_AA)
            cv2.circle(image, pt, 6, (255, 255, 255), 1, cv2.LINE_AA) # outer ring

def main():
    parser = argparse.ArgumentParser(description="SAGE MediaPipe Pose Estimation Test")
    parser.add_argument(
        '--input', 
        type=str, 
        default='0', 
        help="Path to video file or camera index (default: '0' for webcam)"
    )
    parser.add_argument(
        '--model', 
        type=str, 
        default='models/pose_landmarker_full.task', 
        help="Path to pose landmarker task file"
    )
    args = parser.parse_args()

    # Determine input source
    if args.input.isdigit():
        source = int(args.input)
        is_webcam = True
    else:
        source = args.input
        is_webcam = False

    print(f"Loading MediaPipe Pose Landmarker from: {args.model}")
    try:
        # Initialize Tasks API Landmarker
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        
        # Configure model options
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=args.model),
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        detector = PoseLandmarker.create_from_options(options)
    except Exception as e:
        print(f"Error: Failed to initialize MediaPipe Pose Landmarker: {e}")
        sys.exit(1)

    print("Opening video source...")
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Could not open input source: {source}")
        sys.exit(1)

    print("Successfully connected. Press 'q' or 'Q' to exit.")
    
    prev_time = time.time()
    frame_count = 0
    previous_rows = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if is_webcam:
                    print("Error: Could not read frame from webcam.")
                else:
                    print("Reached end of video file.")
                break

            frame_count += 1
            current_time = time.time()
            elapsed = current_time - prev_time
            fps = 1.0 / elapsed if elapsed > 0 else 0
            prev_time = current_time

            # Convert BGR (OpenCV default) to RGB (MediaPipe requirement)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # Perform detection
            detection_result = detector.detect(mp_image)
            landmark_pairs = []
            if detection_result.pose_landmarks:
                for landmarks in detection_result.pose_landmarks:
                    draw_skeleton(frame, landmarks, POSE_CONNECTIONS)
                    landmark_pairs = [(lm.x, lm.y) for lm in landmarks]

            row = build_pose_row(
                timestamp=str(current_time),
                frame=frame_count,
                landmarks=landmark_pairs,
            )
            result = classify_posture_and_fall(row, previous_rows=previous_rows)
            row.update(result)
            previous_rows.append(row)
            append_detection_log(row, result)
            write_pose_outputs([row], pose_path=POSE_KEYPOINTS_CSV, posture_path=POSTURE_OUTPUT_CSV)

            # Overlays for FPS and landmarks count
            fps_text = f"FPS: {fps:.1f}"
            detected_text = "Pose Detected" if detection_result.pose_landmarks else "No Pose"
            
            # Print to stdout periodically
            if frame_count % 30 == 0:
                print(f"Frame {frame_count} | {fps_text} | Status: {detected_text}")

            # Draw overlays
            label_text = f"Posture: {row.get('posture_label', 'Unknown')}"
            fall_text = "FALL" if row.get('fall_detected') else ""
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, label_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, fall_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

            try:
                cv2.imshow("SAGE Pose Estimation Test", frame)
            except cv2.error as e:
                if frame_count == 1:
                    print(f"Warning: GUI display not available ({e}). Running in headless console logging mode.")

            # Quit handler
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("Quit requested by user.")
                break
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()
        print(f"Results written to {POSE_KEYPOINTS_CSV} and {POSTURE_OUTPUT_CSV}")
        print("Resources clean-up finished.")

if __name__ == '__main__':
    main()

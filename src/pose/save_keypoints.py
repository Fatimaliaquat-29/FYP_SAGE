import cv2
import csv
import time
import sys
import argparse
import os
import mediapipe as mp

def main():
    parser = argparse.ArgumentParser(description="SAGE Keypoints Logger")
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
    parser.add_argument(
        '--output', 
        type=str, 
        default='pose_keypoints.csv', 
        help="Path to output CSV file (default: 'pose_keypoints.csv')"
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
        detector.close()
        sys.exit(1)

    # Prepare CSV header
    headers = ['timestamp', 'frame_number']
    for i in range(33):
        headers.extend([
            f'lm_{i}_x',
            f'lm_{i}_y',
            f'lm_{i}_z',
            f'lm_{i}_visibility',
            f'lm_{i}_presence'
        ])

    print(f"Writing keypoints to: {args.output}")
    try:
        csv_file = open(args.output, mode='w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
    except Exception as e:
        print(f"Error: Could not open output file {args.output} for writing: {e}")
        cap.release()
        detector.close()
        sys.exit(1)

    print("Starting keypoint recording. Press 'q' or 'Q' to quit.")
    
    frame_count = 0
    start_time = time.time()

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
            current_timestamp = time.time()

            # Convert BGR (OpenCV default) to RGB (MediaPipe requirement)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # Perform detection
            detection_result = detector.detect(mp_image)

            # Construct CSV row
            row = [current_timestamp, frame_count]
            
            if detection_result.pose_landmarks:
                # MediaPipe Pose Landmarker usually returns landmarks for the primary detected person (index 0)
                landmarks = detection_result.pose_landmarks[0]
                for lm in landmarks:
                    row.extend([lm.x, lm.y, lm.z, lm.visibility, lm.presence])
                
                status_text = "Pose Logged"
            else:
                # If no pose is detected, fill the landmark columns with empty values
                row.extend([""] * (33 * 5))
                status_text = "No Pose Detected"

            csv_writer.writerow(row)

            # Print updates to console periodically
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"Frame {frame_count} | FPS: {fps:.1f} | Status: {status_text}")

            # Draw visual feedback
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, status_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if detection_result.pose_landmarks else (0, 0, 255), 2, cv2.LINE_AA)
            
            try:
                cv2.imshow("SAGE Keypoint Logger", frame)
            except cv2.error:
                pass # Headless mode fallback

            # Quit handler
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("Quit requested by user.")
                break
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    finally:
        csv_file.close()
        detector.close()
        cap.release()
        cv2.destroyAllWindows()
        print(f"Keypoint recording finished. Total frames: {frame_count}. Output saved to {args.output}")

if __name__ == '__main__':
    main()

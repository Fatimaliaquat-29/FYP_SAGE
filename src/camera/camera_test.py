import cv2
import time
import sys

def main():
    print("Initializing camera feed (index 0)...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam at index 0. If you do not have a webcam, please verify connection.")
        sys.exit(1)
        
    print("Webcam successfully opened.")
    print("Press 'q' or 'Q' to quit.")
    
    prev_time = time.time()
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break
                
            frame_count += 1
            current_time = time.time()
            elapsed = current_time - prev_time
            fps = 1.0 / elapsed if elapsed > 0 else 0
            prev_time = current_time
            
            # Print periodically to console so that even headless run shows progress
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames. Current FPS: {fps:.2f}")
                
            # Draw FPS overlay
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(
                frame, 
                fps_text, 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1.0, 
                (0, 255, 0), 
                2, 
                cv2.LINE_AA
            )
            
            try:
                cv2.imshow("SAGE Camera Test", frame)
            except cv2.error as e:
                # If we encounter a GUI error (e.g. running headless), print warning and continue logging to console
                if frame_count == 1:
                    print(f"Warning: GUI display not available ({e}). Running in console logging mode.")
                
            # Read keypress
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("Quit requested by user.")
                break
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    finally:
        # Crucial clean-up
        cap.release()
        cv2.destroyAllWindows()
        print("Camera resource released. All windows destroyed.")

if __name__ == '__main__':
    main()

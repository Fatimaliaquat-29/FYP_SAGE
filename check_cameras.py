"""Quick camera-index finder. Run before a live demo to confirm which device
index is the real camera you want (laptops with a virtual/Zoom camera often
have more than one index registered, and 0 isn't always the physical webcam).

Usage: python check_cameras.py
Shows a preview window per detected camera; press any key to move to the next.
"""
import cv2

for idx in range(5):
    cap = cv2.VideoCapture(idx)
    if not cap.isOpened():
        cap.release()
        continue
    ok, frame = cap.read()
    if not ok:
        cap.release()
        continue
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera index {idx}: opened OK, frame size {w}x{h}. Showing preview -- press any key for next index, 'q' to stop.")
    cv2.putText(frame, f"Camera index {idx}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Camera check", frame)
    key = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()
    cap.release()
    if key == ord('q'):
        break

print("Done. Use --input <the index that showed your real camera> with realtime_fall_detection.py")

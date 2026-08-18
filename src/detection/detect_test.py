import argparse
import statistics
import sys
import time
from pathlib import Path

import cv2

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.yolo_objects import YOLOObjectDetector

PERSON_COLOR = (0, 120, 255)
OTHER_COLOR = (60, 220, 60)


def draw_detections(frame, detections):
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
        color = PERSON_COLOR if det["class"] == "person" else OTHER_COLOR
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
        label = f'{det["class"]} {det["confidence"]:.2f}'
        cv2.putText(frame, label, (x1, max(y1 - 8, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)


def main():
    parser = argparse.ArgumentParser(description="SAGE YOLOv8 object detection sanity check")
    parser.add_argument("--input", type=str, default="0", help="Path to video file or camera index (default: '0' for webcam)")
    parser.add_argument("--model", type=str, default=None, help="Path to YOLO weights (default: models/yolov8n.pt)")
    parser.add_argument("--conf", type=float, default=0.4, help="Confidence threshold")
    parser.add_argument("--headless", action="store_true", help="Skip cv2.imshow, just print the summary (for batch runs over saved clips)")
    args = parser.parse_args()

    source = int(args.input) if args.input.isdigit() else args.input

    detector_kwargs = {"confidence_threshold": args.conf}
    if args.model:
        detector_kwargs["model_path"] = Path(args.model)
    detector = YOLOObjectDetector(**detector_kwargs)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Could not open input source: {source}")
        sys.exit(1)

    frame_count = 0
    person_frames = 0
    latencies_ms = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            t0 = time.perf_counter()
            detections = detector.detect(frame)
            latencies_ms.append((time.perf_counter() - t0) * 1000)

            if any(d["class"] == "person" for d in detections):
                person_frames += 1

            if not args.headless:
                draw_detections(frame, detections)
                recent_avg = statistics.mean(latencies_ms[-30:])
                overlay = f"{recent_avg:.1f} ms/frame ({1000 / recent_avg:.1f} FPS)"
                cv2.putText(frame, overlay, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                try:
                    cv2.imshow("SAGE YOLO Object Detection", frame)
                except cv2.error:
                    pass
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), ord("Q")):
                    print("Quit requested by user.")
                    break

            if frame_count % 60 == 0:
                print(f"Frame {frame_count} | last 60-frame avg: {statistics.mean(latencies_ms[-60:]):.1f} ms/frame")
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if frame_count == 0:
        print("No frames were read from the input source.")
        return

    sorted_latencies = sorted(latencies_ms)
    p95 = sorted_latencies[int(0.95 * len(sorted_latencies))]

    print("\n--- Summary ---")
    print(f"Source: {args.input}")
    print(f"Frames processed: {frame_count}")
    print(f"Person detected in {person_frames}/{frame_count} frames ({100 * person_frames / frame_count:.1f}%)")
    print(
        f"Latency: mean={statistics.mean(latencies_ms):.1f} ms, "
        f"median={statistics.median(latencies_ms):.1f} ms, p95={p95:.1f} ms"
    )
    print(f"Effective FPS (mean): {1000 / statistics.mean(latencies_ms):.1f}")


if __name__ == "__main__":
    main()

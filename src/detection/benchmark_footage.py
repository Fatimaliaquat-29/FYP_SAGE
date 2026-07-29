import argparse
import statistics
import sys
import time
from pathlib import Path

import cv2

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.generate_bbox_dataset import is_fall_lying_clip, split_clips
from src.detection.yolo_objects import YOLOObjectDetector

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def find_clips(testing_dir: Path):
    return sorted(p for p in testing_dir.rglob("*") if p.suffix.lower() in VIDEO_EXTENSIONS)


def benchmark_clip(detector, clip_path: Path):
    cap = cv2.VideoCapture(str(clip_path))
    if not cap.isOpened():
        return None

    frame_count = 0
    person_frames = 0
    latencies_ms = []

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

    cap.release()
    if frame_count == 0:
        return None

    return {
        "clip": clip_path,
        "frames": frame_count,
        "person_frames": person_frames,
        "person_rate": person_frames / frame_count,
        "mean_ms": statistics.mean(latencies_ms),
        "median_ms": statistics.median(latencies_ms),
        "p95_ms": sorted(latencies_ms)[int(0.95 * len(latencies_ms))],
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark YOLO person detection over Testing/ footage")
    parser.add_argument("--testing_dir", type=str, default=str(REPO_ROOT / "Testing"))
    parser.add_argument("--conf", type=float, default=0.4)
    parser.add_argument("--model", type=str, default=None, help="Path to YOLO weights (default: models/yolov8n.pt)")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size; match what a fine-tuned model was trained at")
    parser.add_argument(
        "--out",
        type=str,
        default=str(REPO_ROOT / "results" / "yolo_person_detection" / "real_footage_results.md"),
    )
    args = parser.parse_args()

    testing_dir = Path(args.testing_dir)
    clips = find_clips(testing_dir)
    if not clips:
        print(f"No video clips found under {testing_dir}")
        sys.exit(1)

    print(f"Found {len(clips)} clips under {testing_dir}")
    detector_kwargs = {"confidence_threshold": args.conf, "imgsz": args.imgsz}
    if args.model:
        detector_kwargs["model_path"] = Path(args.model)
    detector = YOLOObjectDetector(**detector_kwargs)

    rows = []
    for clip in clips:
        print(f"Processing {clip.relative_to(testing_dir)} ...")
        result = benchmark_clip(detector, clip)
        if result is None:
            print(f"  Warning: could not read {clip}, skipping.")
            continue
        rows.append(result)
        print(
            f"  frames={result['frames']} person_rate={100 * result['person_rate']:.1f}% "
            f"mean={result['mean_ms']:.1f}ms p95={result['p95_ms']:.1f}ms"
        )

    if not rows:
        print("No clips could be processed.")
        sys.exit(1)

    total_frames = sum(r["frames"] for r in rows)
    total_person_frames = sum(r["person_frames"] for r in rows)
    overall_person_rate = 100 * total_person_frames / total_frames
    overall_mean_ms = statistics.mean(r["mean_ms"] for r in rows)

    # Held-out clips never contributed frames to fine-tuning, so they are the
    # only honest generalization test when benchmarking a fine-tuned model.
    _, val_clips = split_clips(clips)
    held_out = {c.resolve() for c in val_clips}

    def subset_rate(predicate):
        subset = [r for r in rows if predicate(r)]
        if not subset:
            return None
        frames = sum(r["frames"] for r in subset)
        person = sum(r["person_frames"] for r in subset)
        return frames, 100 * person / frames

    groups = {
        "Upright (standing/sitting clips)": subset_rate(lambda r: not is_fall_lying_clip(r["clip"])),
        "Falling / lying clips": subset_rate(lambda r: is_fall_lying_clip(r["clip"])),
        "Held-out clips only (never trained on)": subset_rate(lambda r: r["clip"].resolve() in held_out),
        "Held-out falling / lying clips only": subset_rate(
            lambda r: r["clip"].resolve() in held_out and is_fall_lying_clip(r["clip"])
        ),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    model_label = Path(args.model).name if args.model else "yolov8n.pt (COCO pretrained)"
    lines = [
        "# YOLO Person Detection - Real Footage Benchmark",
        "",
        f"Model: {model_label}, confidence threshold {args.conf}, imgsz {args.imgsz}",
        f"Clips: {len(rows)}, total frames: {total_frames}",
        f"Overall person-detection rate: {overall_person_rate:.1f}%",
        f"Overall mean latency: {overall_mean_ms:.1f} ms/frame ({1000 / overall_mean_ms:.1f} FPS)",
        "",
        "## Breakdown",
        "",
        "| Subset | Frames | Person detected % |",
        "|---|---|---|",
    ]
    for label, stats in groups.items():
        if stats is None:
            continue
        frames, rate = stats
        lines.append(f"| {label} | {frames} | {rate:.1f}% |")

    lines += [
        "",
        "## Per-clip",
        "",
        "| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        held = "yes" if r["clip"].resolve() in held_out else "no"
        lines.append(
            f"| {r['clip'].relative_to(testing_dir)} | {held} | {r['frames']} | {100 * r['person_rate']:.1f}% | "
            f"{r['mean_ms']:.1f} | {r['median_ms']:.1f} | {r['p95_ms']:.1f} |"
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote report to {out_path}")
    for label, stats in groups.items():
        if stats is not None:
            print(f"  {label}: {stats[1]:.1f}% over {stats[0]} frames")


if __name__ == "__main__":
    main()

"""Scores an object detector against HAND-DRAWN labels on held-out footage.

Why this exists
---------------
Every furniture number this project has quoted so far was computed against
pseudo-labels -- boxes a stock COCO YOLOv8n guessed on our own rooms (see
report_label_sources.py: 73.9% of `chair` and 81.1% of `bed` boxes in the
merged val split). Scoring a model trained on those, against those, measures
agreement with the teacher rather than accuracy.

This script scores against labels a human drew, on a room that appears in no
training run. That makes it the only furniture measurement here that is
evidence.

Deliberately NOT reusing the merged val split, and deliberately requiring an
--eval_dir whose labels came from a person.

Usage
-----
    python src/detection/sample_heldout_frames.py          # extract frames
    ...draw boxes by hand...
    python src/detection/score_heldout_objects.py \
        --eval_dir eval/heldout_objects \
        --model models/yolov8n_sage_merged_v3.pt

Pass --model twice to compare two checkpoints on identical frames.
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.sage_classes import SAGE_CLASSES

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def load_ground_truth(labels_dir: Path, image_paths):
    """Read hand-drawn YOLO labels. Returns (per_image_boxes, n_unlabelled).

    A MISSING .txt is treated as "not yet labelled" and the image is excluded,
    NOT as "no objects present". Those two are opposite claims, and silently
    conflating them would inflate the false-positive count with detections on
    frames nobody has looked at yet. An intentionally object-free frame must be
    an EMPTY file.
    """
    ground_truth = {}
    unlabelled = []
    for image_path in image_paths:
        label_path = labels_dir / f"{image_path.stem}.txt"
        if not label_path.exists():
            unlabelled.append(image_path.name)
            continue
        boxes = []
        for line in label_path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            cls = int(float(parts[0]))
            cx, cy, w, h = (float(v) for v in parts[1:5])
            boxes.append((cls, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
        ground_truth[image_path] = boxes
    return ground_truth, unlabelled


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    intersection = iw * ih
    if intersection <= 0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


def score_model(model_path: Path, ground_truth, conf: float, iou_threshold: float):
    """Greedy IoU matching per class. Returns per-class {tp, fp, fn}."""
    from ultralytics import YOLO

    model = YOLO(str(model_path))
    stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for image_path, gt_boxes in ground_truth.items():
        results = model.predict(str(image_path), conf=conf, verbose=False)
        predictions = []
        for result in results:
            for box in result.boxes:
                cls = int(box.cls.item())
                confidence = float(box.conf.item())
                x1, y1, x2, y2 = (float(v) for v in box.xyxyn[0])
                predictions.append((confidence, cls, (x1, y1, x2, y2)))
        # Highest-confidence predictions claim their match first, so a weak
        # duplicate cannot steal the box from the detection we would ship.
        predictions.sort(key=lambda p: -p[0])

        unmatched = list(range(len(gt_boxes)))
        for _, cls, box in predictions:
            best_iou, best_idx = 0.0, None
            for gi in unmatched:
                gt_cls, *gt_box = gt_boxes[gi]
                if gt_cls != cls:
                    continue
                overlap = iou(box, tuple(gt_box))
                if overlap > best_iou:
                    best_iou, best_idx = overlap, gi
            if best_idx is not None and best_iou >= iou_threshold:
                stats[cls]["tp"] += 1
                unmatched.remove(best_idx)
            else:
                stats[cls]["fp"] += 1
        for gi in unmatched:
            stats[gt_boxes[gi][0]]["fn"] += 1
    return stats


def print_report(model_path: Path, stats, n_images):
    print(f"\n=== {model_path.name} on {n_images} hand-labelled frames ===")
    header = (f"{'idx':>3}  {'class':<14} {'TP':>6} {'FP':>6} {'FN':>6} "
              f"{'precision':>10} {'recall':>8} {'F1':>7}")
    print(header)
    print("-" * len(header))

    totals = {"tp": 0, "fp": 0, "fn": 0}
    for idx, name in enumerate(SAGE_CLASSES):
        s = stats.get(idx)
        if not s or (s["tp"] + s["fp"] + s["fn"]) == 0:
            continue
        tp, fp, fn = s["tp"], s["fp"], s["fn"]
        for key, value in (("tp", tp), ("fp", fp), ("fn", fn)):
            totals[key] += value
        precision = tp / (tp + fp) if tp + fp else float("nan")
        recall = tp / (tp + fn) if tp + fn else float("nan")
        f1 = (2 * precision * recall / (precision + recall)
              if precision == precision and recall == recall and (precision + recall) > 0
              else float("nan"))
        print(f"{idx:>3}  {name:<14} {tp:>6} {fp:>6} {fn:>6} "
              f"{precision:>10.3f} {recall:>8.3f} {f1:>7.3f}")

    tp, fp, fn = totals["tp"], totals["fp"], totals["fn"]
    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")
    print("-" * len(header))
    print(f"{'':>3}  {'ALL':<14} {tp:>6} {fp:>6} {fn:>6} {precision:>10.3f} {recall:>8.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Score a detector against hand-drawn labels on held-out footage")
    parser.add_argument("--eval_dir", type=str,
                        default=str(REPO_ROOT / "eval" / "heldout_objects"),
                        help="Directory with images/ and hand-drawn labels/")
    parser.add_argument("--model", type=str, action="append", required=True,
                        help="Weights to score. Repeat to compare checkpoints on identical frames.")
    parser.add_argument("--conf", type=float, default=0.25,
                        help="Detection confidence threshold (default 0.25)")
    parser.add_argument("--iou", type=float, default=0.5,
                        help="IoU required to count a detection as a match (default 0.5)")
    args = parser.parse_args()

    eval_dir = Path(args.eval_dir)
    images_dir, labels_dir = eval_dir / "images", eval_dir / "labels"
    if not images_dir.is_dir():
        raise SystemExit(f"{images_dir} not found -- run sample_heldout_frames.py first.")
    if not labels_dir.is_dir():
        raise SystemExit(f"{labels_dir} not found -- the hand-labelling step has not been done.")

    image_paths = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)
    if not image_paths:
        raise SystemExit(f"No images in {images_dir}.")

    ground_truth, unlabelled = load_ground_truth(labels_dir, image_paths)
    if unlabelled:
        print(f"WARNING: {len(unlabelled)} of {len(image_paths)} images have no .txt and were "
              "EXCLUDED.\n"
              "  A missing file means 'not yet labelled', which is not the same claim as 'no\n"
              "  objects here' -- an intentionally object-free frame needs an EMPTY .txt.")
        print(f"  e.g. {', '.join(unlabelled[:5])}"
              + (" ..." if len(unlabelled) > 5 else ""))
        print()
    if not ground_truth:
        raise SystemExit("No labelled images to score against.")

    n_boxes = sum(len(v) for v in ground_truth.values())
    print(f"eval set: {len(ground_truth)} labelled frames, {n_boxes} hand-drawn boxes")
    print(f"conf={args.conf}  iou={args.iou}")

    for model_arg in args.model:
        model_path = Path(model_arg)
        if not model_path.exists():
            print(f"\nSKIP {model_path} -- not found")
            continue
        stats = score_model(model_path, ground_truth, args.conf, args.iou)
        print_report(model_path, stats, len(ground_truth))

    print("\nThese numbers are scored against human-drawn boxes on footage held out of training.")
    print("Unlike the merged val split, they are not circular -- see report_label_sources.py")
    print("--target merged-val for why that split cannot answer this question.")


if __name__ == "__main__":
    main()

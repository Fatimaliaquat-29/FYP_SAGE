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

from src.detection.sage_classes import CLASS_TO_INDEX, SAGE_CLASSES

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


def score_model(model_path: Path, ground_truth, conf: float, iou_threshold: float,
                only_classes=None, imgsz: int = 320):
    """Greedy IoU matching per class. Returns per-class {tp, fp, fn}.

    only_classes: optional set of SAGE class indices to score. Both predictions
        AND ground truth are filtered to it, which is what makes a PARTIAL
        labelling pass valid. If you hand-label only `person` and score every
        class, each furniture detection becomes an unmatched prediction and is
        counted as a false positive -- reporting terrible precision for classes
        you simply had not labelled yet. Restricting both sides keeps the
        measurement honest about what was actually annotated.
    """
    from ultralytics import YOLO

    return score_loaded_model(YOLO(str(model_path)), ground_truth, conf,
                              iou_threshold, only_classes, imgsz)


def score_loaded_model(model, ground_truth, conf: float, iou_threshold: float,
                       only_classes=None, imgsz: int = 320):
    """As score_model, but takes an already-loaded YOLO.

    --per_clip scores the same weights once per clip. Reloading them each time
    would dominate the runtime and change nothing about the numbers.
    """
    stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for image_path, all_gt in ground_truth.items():
        gt_boxes = [g for g in all_gt if only_classes is None or g[0] in only_classes]
        # imgsz matters: the merged series (including v3) was trained and gated
        # at 320, while Ultralytics silently defaults predict() to 640 -- the
        # resolution the 640px experiment already measured as failing v3's
        # recall gate. Not passing this unfairly deflates any model tuned for a
        # non-default size.
        results = model.predict(str(image_path), conf=conf, imgsz=imgsz, verbose=False)
        predictions = []
        for result in results:
            for box in result.boxes:
                cls = int(box.cls.item())
                if only_classes is not None and cls not in only_classes:
                    continue
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


def group_by_clip(ground_truth):
    """Split the eval set into clips using the frame-number filename suffix.

    sample_heldout_frames.py writes `<clip>_<6-digit frame>.jpg`, so dropping
    the last underscore-separated field recovers the clip. Returns an ordered
    {clip: {image_path: boxes}}.
    """
    clips = defaultdict(dict)
    for image_path, boxes in ground_truth.items():
        clip, _, frame = image_path.stem.rpartition("_")
        if not clip or not frame.isdigit():
            clip = image_path.stem
        clips[clip][image_path] = boxes
    return dict(sorted(clips.items()))


def print_per_clip_report(model_path: Path, model, ground_truth, conf,
                          iou_threshold, only_classes, imgsz):
    """Detection rate per clip -- the view that separates activity from model.

    An aggregate recall hides the thing that matters most in this project: fall
    clips and walk/sit clips behave completely differently, and a single number
    averages the two into something that describes neither. See
    results/yolo_person_detection/reserved_heldout_posture.md.

    The denominator is tp + fn -- boxes of the scored classes only. Counting
    every line in the label file instead would include furniture and silently
    understate every rate.
    """
    print(f"\n=== {model_path.name} per clip ===")
    header = (f"{'clip':<34} {'boxes':>6} {'detected':>10} {'rate':>7} {'FP':>5}")
    print(header)
    print("-" * len(header))

    rows = []
    for clip, clip_gt in group_by_clip(ground_truth).items():
        stats = score_loaded_model(model, clip_gt, conf, iou_threshold,
                                   only_classes, imgsz)
        tp = sum(s["tp"] for s in stats.values())
        fp = sum(s["fp"] for s in stats.values())
        fn = sum(s["fn"] for s in stats.values())
        if tp + fn == 0:
            # No labelled boxes of the scored classes. Reporting a rate here
            # would be a division by zero dressed up as 0%; the clip simply
            # does not participate in recall. Its FPs still count.
            rows.append((clip, 0, tp, None, fp))
            continue
        rows.append((clip, tp + fn, tp, tp / (tp + fn), fp))

    rows.sort(key=lambda r: (r[3] is None, -(r[3] or 0)))
    for clip, n, tp, rate, fp in rows:
        rate_text = "     --" if rate is None else f"{rate:>7.2f}"
        detected = "--" if rate is None else f"{tp}/{n}"
        print(f"{clip[:33]:<34} {n:>6} {detected:>10} {rate_text} {fp:>5}")

    print("-" * len(header))
    total_n = sum(r[1] for r in rows)
    total_tp = sum(r[2] for r in rows if r[3] is not None)
    total_fp = sum(r[4] for r in rows)
    overall = f"{total_tp / total_n:>7.2f}" if total_n else "     --"
    print(f"{'ALL':<34} {total_n:>6} {str(total_tp) + '/' + str(total_n):>10} "
          f"{overall} {total_fp:>5}")


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
    parser.add_argument("--imgsz", type=int, default=320,
                        help="Inference resolution (default 320, matching what the merged "
                             "series was trained and gated at -- NOT Ultralytics' own 640 "
                             "default, which the 640px experiment already found fails v3's "
                             "recall gate). Stock yolov8n.pt is a 640 model, so pass 640 "
                             "explicitly when scoring it or the comparison is rigged.")
    parser.add_argument("--classes", type=str, default=None,
                        help="Comma-separated SAGE class names to score, e.g. 'person'. Filters "
                             "BOTH predictions and ground truth, so a partial labelling pass "
                             "(person only) does not report unlabelled furniture as false "
                             "positives. Omit to score every class.")
    parser.add_argument("--per_clip", action="store_true",
                        help="Also break the result down by clip. Fall clips and walk/sit "
                             "clips have very different detection rates, so the aggregate "
                             "describes neither -- see reserved_heldout_posture.md.")
    args = parser.parse_args()

    only_classes = None
    if args.classes:
        only_classes = set()
        for raw in args.classes.split(","):
            name = raw.strip().lower()
            if name not in CLASS_TO_INDEX:
                raise SystemExit(f"Unknown class {name!r}. Valid: {', '.join(SAGE_CLASSES)}")
            only_classes.add(CLASS_TO_INDEX[name])
        print(f"Scoring ONLY: {args.classes} (both predictions and ground truth filtered)")

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
    print(f"conf={args.conf}  iou={args.iou}  imgsz={args.imgsz}")

    for model_arg in args.model:
        model_path = Path(model_arg)
        if not model_path.exists():
            print(f"\nSKIP {model_path} -- not found")
            continue
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        stats = score_loaded_model(model, ground_truth, args.conf, args.iou,
                                   only_classes, args.imgsz)
        print_report(model_path, stats, len(ground_truth))
        if args.per_clip:
            print_per_clip_report(model_path, model, ground_truth, args.conf,
                                  args.iou, only_classes, args.imgsz)

    print("\nThese numbers are scored against human-drawn boxes on footage held out of training.")
    print("Unlike the merged val split, they are not circular -- see report_label_sources.py")
    print("--target merged-val for why that split cannot answer this question.")


if __name__ == "__main__":
    main()

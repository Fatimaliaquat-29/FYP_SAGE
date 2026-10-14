"""v5 vs v6 vs v7, person + all 12 object classes, one combined pass, over
TWO eval sets. Generalizes score_heldout_combined.py (which was hardcoded to
exactly 2 models) to N models.

Eval sets:
  1. eval/heldout_objects/       -- the general held-out set used every round.
  2. handlabels/round6_heldout/  -- Laying_Dim_HM + Behind_Bed_HM, deliberately
     held back from the v7 training merge. This is the actual test of whether
     v7 got better at the hard case (dark/occluded lying person) or just fit
     the new labels -- see docs/HAMMAD_CLIPS_ROUND6.md.

Read-only. Does not touch yolo_testing/held_out/ or retrain anything.
"""

import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ultralytics import YOLO

from src.detection.sage_classes import SAGE_CLASSES
from src.detection.score_heldout_objects import iou, load_ground_truth

MODELS = {
    "v5": REPO_ROOT / "models" / "yolov8n_sage_merged_v5.pt",
    "v6": REPO_ROOT / "models" / "yolov8n_sage_merged_v6.pt",
    "v7": REPO_ROOT / "models" / "yolov8n_sage_merged_v7.pt",
}
EVAL_SETS = {
    "eval/heldout_objects (general)": REPO_ROOT / "eval" / "heldout_objects",
    "round6_heldout (Laying_Dim_HM + Behind_Bed_HM, held back)": REPO_ROOT / "handlabels" / "round6_heldout",
}
CONF = 0.4
IMGSZ = 640
N_VALID_CLASSES = len(SAGE_CLASSES)


def score_model(model, ground_truth, iou_match):
    stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    n_out_of_schema = 0
    for image_path, all_gt in ground_truth.items():
        gt_boxes = []
        for cls, *box in all_gt:
            if cls >= N_VALID_CLASSES:
                n_out_of_schema += 1
                continue
            gt_boxes.append((cls, tuple(box)))

        results = model.predict(str(image_path), conf=CONF, imgsz=IMGSZ, verbose=False)
        predictions = []
        for result in results:
            for box in result.boxes:
                cls = int(box.cls.item())
                confidence = float(box.conf.item())
                x1, y1, x2, y2 = (float(v) for v in box.xyxyn[0])
                predictions.append((confidence, cls, (x1, y1, x2, y2)))
        predictions.sort(key=lambda p: -p[0])

        unmatched = list(range(len(gt_boxes)))
        for _, cls, box in predictions:
            best_iou, best_idx = 0.0, None
            for gi in unmatched:
                gt_cls, gt_box = gt_boxes[gi]
                if gt_cls != cls:
                    continue
                overlap = iou(box, gt_box)
                if overlap > best_iou:
                    best_iou, best_idx = overlap, gi
            if best_idx is not None and best_iou >= iou_match:
                stats[cls]["tp"] += 1
                unmatched.remove(best_idx)
            else:
                stats[cls]["fp"] += 1
        for gi in unmatched:
            stats[gt_boxes[gi][0]]["fn"] += 1
    return stats, n_out_of_schema


def main():
    iou_match = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5

    models = {}
    for name, path in MODELS.items():
        if not path.exists():
            print(f"SKIP {name}: {path} not found")
            continue
        models[name] = YOLO(str(path))

    lines = [f"# v5 / v6 / v7 suite -- combined person+object, IoU {iou_match}", ""]
    print(f"Models loaded: {list(models.keys())}  conf={CONF} imgsz={IMGSZ} iou_match={iou_match}\n")

    for eval_label, eval_dir in EVAL_SETS.items():
        images_dir, labels_dir = eval_dir / "images", eval_dir / "labels"
        if not images_dir.is_dir():
            print(f"SKIP {eval_label}: {images_dir} not found")
            continue
        image_paths = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
        ground_truth, unlabelled = load_ground_truth(labels_dir, image_paths)
        n_boxes = sum(len(v) for v in ground_truth.values())
        print(f"=== {eval_label} ===")
        print(f"{len(ground_truth)} frames, {n_boxes} hand-drawn boxes ({len(unlabelled)} unlabelled, excluded)\n")

        lines += [f"## {eval_label}", "", f"{len(ground_truth)} frames, {n_boxes} hand-drawn boxes", ""]

        all_stats = {}
        for name, model in models.items():
            stats, n_oos = score_model(model, ground_truth, iou_match)
            all_stats[name] = stats
            if n_oos:
                print(f"  [{name}] {n_oos} boxes outside the 13-class schema excluded")

        header = "| class | n |" + "".join(f" {n} P | {n} R |" for n in models) + "\n|---|---|" + "---|---" * len(models) + "|"
        print(header.replace("|", " | "))
        lines.append(header)

        for idx, cls_name in enumerate(SAGE_CLASSES):
            n = sum(1 for boxes in ground_truth.values() for b in boxes if b[0] == idx)
            if n == 0:
                continue
            row = f"| {cls_name} | {n} |"
            console_row = f"{cls_name:<14} {n:>4} |"
            for name in models:
                s = all_stats[name].get(idx, {"tp": 0, "fp": 0, "fn": 0})
                tp, fp, fn = s["tp"], s["fp"], s["fn"]
                p = tp / (tp + fp) if tp + fp else float("nan")
                r = tp / (tp + fn) if tp + fn else float("nan")
                row += f" {p:.2f} | {r:.2f} |"
                console_row += f" {name} P={p:.2f} R={r:.2f} (tp={tp} fp={fp} fn={fn}) |"
            print(console_row)
            lines.append(row)
        lines.append("")
        print()

    out_path = REPO_ROOT / "results" / "yolo_person_detection" / f"v7_suite_iou{iou_match}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

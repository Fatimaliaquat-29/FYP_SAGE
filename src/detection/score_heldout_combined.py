"""v5 vs v6, person + all 12 object classes, in ONE pass over eval/heldout_objects/.

Every previous v5/v6 comparison scored person alone (--classes person) or
furniture alone (against pseudo-labels, not hand-drawn ones). This scores
both from the same model.predict() call per frame, at the settings used
throughout this project (conf 0.4, imgsz 640, IoU-0.5 match), so a class
trade-off within one pass would actually show up here.

Also answers the open question in the v6 results doc: it reported fewer
couches (4,123 vs 5,804) and zero refrigerators for v6 vs v5 on the EMPTY-ROOM
test, but that was never checked against hand-drawn labels -- a room with less
furniture in frame would produce the same numbers without any regression.
This scores couch/refrigerator/etc against the hand-drawn boxes already in
eval/heldout_objects/labels/ to tell real regression from frame composition.

Read-only. Does not touch yolo_testing/held_out/.
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

EVAL_DIR = REPO_ROOT / "eval" / "heldout_objects"
MODELS = {
    "v5": REPO_ROOT / "models" / "yolov8n_sage_merged_v5.pt",
    "v6": REPO_ROOT / "models" / "yolov8n_sage_merged_v6.pt",
}
CONF = 0.4
IMGSZ = 640
IOU_MATCH = 0.5
MIN_MEANINGFUL_N = 10  # below this, flag the row rather than let a rate stand alone
N_VALID_CLASSES = len(SAGE_CLASSES)


def score_model(model, ground_truth):
    """One predict() per image, all classes at once. Returns per-class
    {tp, fp, fn, iou_sum} plus counts of ground-truth boxes this run couldn't
    use (class index outside the 13-class schema)."""
    stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "iou_sum": 0.0})
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
            if best_idx is not None and best_iou >= IOU_MATCH:
                stats[cls]["tp"] += 1
                stats[cls]["iou_sum"] += best_iou
                unmatched.remove(best_idx)
            else:
                stats[cls]["fp"] += 1
        for gi in unmatched:
            stats[gt_boxes[gi][0]]["fn"] += 1

    return stats, n_out_of_schema


def main():
    images_dir, labels_dir = EVAL_DIR / "images", EVAL_DIR / "labels"
    image_paths = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    ground_truth, unlabelled = load_ground_truth(labels_dir, image_paths)
    n_boxes = sum(len(v) for v in ground_truth.values())
    print(f"eval set: {len(ground_truth)} labelled frames, {n_boxes} hand-drawn boxes "
          f"({len(unlabelled)} frames unlabelled, excluded)")
    print(f"conf={CONF}  imgsz={IMGSZ}  iou_match={IOU_MATCH}  -- ALL 13 classes scored in one pass\n")

    all_stats = {}
    for name, path in MODELS.items():
        model = YOLO(str(path))
        stats, n_oos = score_model(model, ground_truth)
        all_stats[name] = stats
        if n_oos:
            print(f"[{name}] {n_oos} hand-drawn boxes use a class index outside the 13-class "
                  f"schema (index >= {N_VALID_CLASSES}) and were excluded from scoring -- a "
                  f"labeling-tool artifact, not a model error. See TV_Lounge_1_Fall/Fall2, "
                  f"TV_Lounge_2_Fall2.")

    # Per-class table, side by side.
    header = (f"{'class':<14} {'n':>4} | {'v5 P':>6} {'v5 R':>6} {'v5 IoU':>7} {'v5 TP/FP/FN':>12} | "
              f"{'v6 P':>6} {'v6 R':>6} {'v6 IoU':>7} {'v6 TP/FP/FN':>12}")
    print(header)
    print("-" * len(header))

    person_row, object_rows = None, []
    for idx, cls_name in enumerate(SAGE_CLASSES):
        n = sum(1 for boxes in ground_truth.values() for b in boxes if b[0] == idx)
        if n == 0:
            continue
        row_cells = [cls_name, n]
        row_data = {"class": cls_name, "n": n}
        for name in ("v5", "v6"):
            s = all_stats[name].get(idx, {"tp": 0, "fp": 0, "fn": 0, "iou_sum": 0.0})
            tp, fp, fn = s["tp"], s["fp"], s["fn"]
            precision = tp / (tp + fp) if tp + fp else float("nan")
            recall = tp / (tp + fn) if tp + fn else float("nan")
            mean_iou = s["iou_sum"] / tp if tp else float("nan")
            row_cells += [precision, recall, mean_iou, f"{tp}/{fp}/{fn}"]
            row_data[name] = {"precision": precision, "recall": recall, "mean_iou": mean_iou,
                              "tp": tp, "fp": fp, "fn": fn}
        flag = " *" if n < MIN_MEANINGFUL_N else "  "
        print(f"{cls_name:<14} {n:>4}{flag}| "
              f"{row_data['v5']['precision']:>6.2f} {row_data['v5']['recall']:>6.2f} "
              f"{row_data['v5']['mean_iou']:>7.2f} {row_data['v5']['tp']}/{row_data['v5']['fp']}/{row_data['v5']['fn']:<7} | "
              f"{row_data['v6']['precision']:>6.2f} {row_data['v6']['recall']:>6.2f} "
              f"{row_data['v6']['mean_iou']:>7.2f} {row_data['v6']['tp']}/{row_data['v6']['fp']}/{row_data['v6']['fn']}")
        if idx == 0:
            person_row = row_data
        else:
            object_rows.append(row_data)

    print("-" * len(header))
    print(f"* n < {MIN_MEANINGFUL_N} hand-drawn boxes -- too few to say anything meaningful about this class alone.\n")

    print("=== couch / refrigerator: real regression, or frame composition? ===")
    for target in ("couch", "refrigerator"):
        row = next((r for r in object_rows if r["class"] == target), None)
        if row is None:
            print(f"{target}: 0 hand-drawn boxes in this eval set -- the empty-room gap "
                  f"CANNOT be checked against ground truth here at all.")
            continue
        note = " (too few to draw a conclusion)" if row["n"] < MIN_MEANINGFUL_N else ""
        print(f"{target}: {row['n']} hand-drawn boxes{note}")
        print(f"  v5: recall {row['v5']['recall']:.2f}  precision {row['v5']['precision']:.2f}  "
              f"({row['v5']['tp']}/{row['v5']['fp']}/{row['v5']['fn']} tp/fp/fn)")
        print(f"  v6: recall {row['v6']['recall']:.2f}  precision {row['v6']['precision']:.2f}  "
              f"({row['v6']['tp']}/{row['v6']['fp']}/{row['v6']['fn']} tp/fp/fn)")


if __name__ == "__main__":
    main()

"""Is v6's low confidence on correctly-located persons a calibration shift, or
genuine uncertainty? Read-only, scored against eval/heldout_objects/ (the
hand-drawn held-out set, not laying_dim.MOV -- that clip stays untouched).

For every hand-drawn person box, run v5 and v6 at conf=0.001 (no floor) and
match predictions to it by IoU>=0.5. Three outcomes per box:
  both_hit   -- both models found it: compare their paired confidences
  v5_only    -- v5 found it, v6's best candidate in that region did not reach
                IoU 0.5 (or scored ~0): a localization miss, not a confidence one
  neither    -- both missed

If both_hit's v6/v5 confidence ratio is roughly constant across the difficulty
range (bucketed by v5's own confidence, the closest thing to a difficulty
proxy available here), that is consistent with a monotonic recalibration
(temperature scaling / threshold shift) closing the gap safely. If the ratio
collapses specifically on v5's own hard cases, low confidence there is v6
being less certain about genuinely hard frames -- recalibration cannot fix
that without also promoting false positives.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ultralytics import YOLO

from src.detection.sage_classes import CLASS_TO_INDEX
from src.detection.score_heldout_objects import iou, load_ground_truth

EVAL_DIR = REPO_ROOT / "eval" / "heldout_objects"
V5_PATH = REPO_ROOT / "models" / "yolov8n_sage_merged_v5.pt"
V6_PATH = REPO_ROOT / "models" / "yolov8n_sage_merged_v6.pt"
OUT_PATH = REPO_ROOT / "results" / "yolo_person_detection" / "v6_calibration_diagnostic.md"
IMGSZ = 640
RAW_CONF = 0.001
IOU_MATCH = 0.5
PERSON_CLS = CLASS_TO_INDEX["person"]


def predict_person_boxes(model, image_path):
    results = model.predict(str(image_path), conf=RAW_CONF, imgsz=IMGSZ, verbose=False)
    boxes = []
    for result in results:
        for box in result.boxes:
            if int(box.cls.item()) != PERSON_CLS:
                continue
            conf = float(box.conf.item())
            x1, y1, x2, y2 = (float(v) for v in box.xyxyn[0])
            boxes.append((conf, (x1, y1, x2, y2)))
    boxes.sort(key=lambda b: -b[0])
    return boxes


def best_match(gt_box, predictions):
    """Highest-confidence prediction reaching IOU_MATCH; else the single
    highest-IoU candidate regardless of confidence, so a genuine near-miss
    can still be reported (conf, iou) instead of silently reading 'nothing'."""
    hit = None
    closest = (0.0, None)  # (iou, conf) of the best-overlapping candidate, any confidence
    for conf, box in predictions:
        ov = iou(gt_box, box)
        if ov > closest[0]:
            closest = (ov, conf)
        if ov >= IOU_MATCH and (hit is None or conf > hit[0]):
            hit = (conf, ov)
    return hit, closest


def main():
    images_dir, labels_dir = EVAL_DIR / "images", EVAL_DIR / "labels"
    image_paths = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    ground_truth, unlabelled = load_ground_truth(labels_dir, image_paths)
    print(f"eval set: {len(ground_truth)} labelled frames ({len(unlabelled)} unlabelled, excluded)")

    v5 = YOLO(str(V5_PATH))
    v6 = YOLO(str(V6_PATH))

    both_hit = []      # (v5_conf, v6_conf, v6_iou)
    v5_only = []        # (v5_conf, v6_best_conf_if_any, v6_best_iou_if_any)
    neither = 0
    n_gt = 0

    for i, (image_path, all_gt) in enumerate(ground_truth.items()):
        gt_boxes = [g[1:] for g in all_gt if g[0] == PERSON_CLS]
        if not gt_boxes:
            continue
        p5 = predict_person_boxes(v5, image_path)
        p6 = predict_person_boxes(v6, image_path)
        for gt_box in gt_boxes:
            n_gt += 1
            hit5, _ = best_match(gt_box, p5)
            hit6, closest6 = best_match(gt_box, p6)
            if hit5 is None:
                # v5 itself misses this box -- outside this question's scope
                # (this diagnostic is about v6 relative to v5's successes).
                continue
            v5_conf = hit5[0]
            if hit6 is not None:
                both_hit.append((v5_conf, hit6[0], hit6[1]))
            else:
                v5_only.append((v5_conf, closest6[1], closest6[0]))
        if (i + 1) % 100 == 0:
            print(f"  ... {i + 1}/{len(ground_truth)} frames")

    print(f"v5-detected person boxes: {len(both_hit) + len(v5_only)} of {n_gt} hand-drawn")
    print(f"  both_hit (v6 also >= IoU {IOU_MATCH}): {len(both_hit)}")
    print(f"  v5_only  (v6 localisation miss):        {len(v5_only)}")

    # Bucket both_hit by v5's own confidence -- the difficulty proxy.
    buckets = [(0.0, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)]
    lines = [
        "# v6 calibration diagnostic — vs v5 on eval/heldout_objects",
        "",
        f"{n_gt} hand-drawn person boxes; v5 detects {len(both_hit) + len(v5_only)} of them "
        f"(conf>={RAW_CONF}, imgsz={IMGSZ}). Restricted to boxes v5 finds, since the question is "
        "what v6 does differently on cases v5 already solves.",
        "",
        f"- **both_hit** ({len(both_hit)}): v6 also matches at IoU>={IOU_MATCH} -- confidence-only comparison.",
        f"- **v5_only** ({len(v5_only)}): v6's best candidate in that region never reaches IoU {IOU_MATCH} "
        "-- a localisation miss, not just a low score.",
        "",
        "## both_hit: is the confidence gap constant across difficulty?",
        "",
        "Bucketed by v5's own confidence (proxy for how easy the frame is). A roughly constant "
        "v6/v5 ratio across buckets is consistent with a monotonic recalibration. A ratio that "
        "collapses in the low-v5-confidence bucket means v6 is genuinely less sure specifically "
        "on hard cases, which recalibration cannot safely fix.",
        "",
        "| v5 conf range | n | mean v5 conf | mean v6 conf | mean v6/v5 ratio | mean v6 IoU |",
        "|---|---|---|---|---|---|",
    ]
    for lo, hi in buckets:
        sub = [b for b in both_hit if lo <= b[0] < hi]
        if not sub:
            lines.append(f"| {lo:.1f}-{hi:.1f} | 0 | - | - | - | - |")
            continue
        mv5 = sum(b[0] for b in sub) / len(sub)
        mv6 = sum(b[1] for b in sub) / len(sub)
        mratio = sum(b[1] / b[0] for b in sub) / len(sub)
        miou = sum(b[2] for b in sub) / len(sub)
        lines.append(f"| {lo:.1f}-{hi:.1f} | {len(sub)} | {mv5:.3f} | {mv6:.3f} | {mratio:.3f} | {miou:.3f} |")

    if v5_only:
        mv5o = sum(b[0] for b in v5_only) / len(v5_only)
        mclosest_iou = sum(b[2] for b in v5_only) / len(v5_only)
        n_v6_saw_nothing = sum(1 for b in v5_only if b[1] is None)
        lines += [
            "",
            "## v5_only: localisation misses",
            "",
            f"{len(v5_only)} boxes where v5 is correct and v6's best candidate never overlaps enough "
            f"to count as the same detection (mean best-candidate IoU {mclosest_iou:.2f}, threshold "
            f"{IOU_MATCH}). Mean v5 confidence on these: {mv5o:.3f}. "
            f"v6 produced literally no candidate anywhere near {n_v6_saw_nothing}/{len(v5_only)} of these boxes "
            "(vs. a wrong-shaped/mislocated one for the rest).",
            "Not a threshold problem -- no confidence cutoff recovers a box that isn't there.",
        ]

    # Recalibration simulation: sweep v6 conf thresholds and report how much
    # of the recall gap a lower operating threshold could close, purely on
    # the both_hit population (recalibration cannot touch v5_only at all).
    lines += [
        "",
        "## Recalibration sweep (both_hit population only)",
        "",
        "What fraction of the both_hit boxes would clear a given v6 confidence threshold -- "
        "i.e. how much of THIS gap (not the v5_only localisation gap) a lower operating point "
        "could recover, with no model change.",
        "",
        "| v6 threshold | both_hit boxes recovered |",
        "|---|---|",
    ]
    for thresh in (0.4, 0.25, 0.10, 0.05, 0.02, 0.01):
        n = sum(1 for b in both_hit if b[1] >= thresh)
        pct = 100 * n / len(both_hit) if both_hit else 0
        lines.append(f"| {thresh} | {n}/{len(both_hit)} ({pct:.0f}%) |")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

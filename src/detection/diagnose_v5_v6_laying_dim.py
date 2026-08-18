"""v5-vs-v6 diagnostic on yolo_testing/held_out/laying_dim.MOV.

reserved_heldout_posture_v6.md step 2: v6 detects the person in 0/620 frames
(even at conf 0.10) where v5 hits 69.5%. This compares both models frame by
frame at very low confidence to see whether v6 sees something faint in the
region v5 finds, or truly nothing, and whether that tracks darkness/occlusion.

Read-only: opens the clip and both checkpoints, writes a report and annotated
frames. Does not touch handlabels/, does not retrain, does not write anything
back into laying_dim.MOV or any dataset -- this clip's value as a control
depends on staying unseen by training.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ultralytics import YOLO

from src.detection.footage_paths import HELD_OUT_ROOT
from src.detection.footage_rotation import get_rotation, needs_verification

CLIP_PATH = HELD_OUT_ROOT / "laying_dim.MOV"
V5_PATH = REPO_ROOT / "models" / "yolov8n_sage_merged_v5.pt"
V6_PATH = REPO_ROOT / "models" / "yolov8n_sage_merged_v6.pt"
OUT_DIR = REPO_ROOT / "results" / "yolo_person_detection" / "laying_dim_diagnostic"
IMGSZ = 640
RAW_CONF = 0.001  # floor -- Ultralytics NMS still applies, but nothing above this is hidden
STRIDE = 10
SNAPSHOT_COUNT = 8  # frames to render as annotated jpgs, spread across the clip


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter == 0:
        return 0.0
    a_area = (ax2 - ax1) * (ay2 - ay1)
    b_area = (bx2 - bx1) * (by2 - by1)
    return inter / (a_area + b_area - inter)


def best_person_box(result):
    """Highest-confidence person box in an Ultralytics result, or None."""
    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        return None
    best = None
    for box in boxes:
        if int(box.cls[0]) != 0:
            continue
        conf = float(box.conf[0])
        if best is None or conf > best[0]:
            best = (conf, [float(v) for v in box.xyxy[0]])
    return best


def region_brightness(frame, bbox):
    x1, y1, x2, y2 = [int(round(v)) for v in bbox]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
    if x2 <= x1 or y2 <= y1:
        return float("nan")
    crop = frame[y1:y2, x1:x2]
    return float(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).mean())


def draw_box(frame, bbox, color, label):
    x1, y1, x2, y2 = [int(round(v)) for v in bbox]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, label, (x1, max(0, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def main():
    if not CLIP_PATH.exists():
        print(f"Missing clip: {CLIP_PATH}")
        sys.exit(1)

    rotation = get_rotation(CLIP_PATH)
    if needs_verification(CLIP_PATH):
        print(f"WARNING: {CLIP_PATH.name} has no verified rotation entry -- aborting rather than guessing.")
        sys.exit(1)
    print(f"[setup] {CLIP_PATH.name}: registered rotation = {rotation!r} (None = confirmed upright)")

    cap = cv2.VideoCapture(str(CLIP_PATH))
    if not cap.isOpened():
        print(f"Could not open {CLIP_PATH}")
        sys.exit(1)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[setup] {total_frames} frames, sampling every {STRIDE}th")

    v5 = YOLO(str(V5_PATH))
    v6 = YOLO(str(V6_PATH))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sampled_candidates = list(range(0, total_frames, STRIDE))
    snapshot_indices = {
        sampled_candidates[int(round(i))]
        for i in np.linspace(0, len(sampled_candidates) - 1, SNAPSHOT_COUNT)
    }

    rows = []
    frame_idx = -1
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if frame_idx % STRIDE != 0:
            continue
        if rotation is not None:
            frame = cv2.rotate(frame, rotation)

        r5 = v5.predict(frame, conf=RAW_CONF, imgsz=IMGSZ, device=None, verbose=False)[0]
        r6 = v6.predict(frame, conf=RAW_CONF, imgsz=IMGSZ, device=None, verbose=False)[0]

        b5 = best_person_box(r5)
        b6 = best_person_box(r6)

        row = {"frame": frame_idx, "v5": b5, "v6_at_v5_region": None, "v6_max_anywhere": b6}

        if b5 is not None:
            v5_conf, v5_bbox = b5
            brightness = region_brightness(frame, v5_bbox)
            # v6's confidence specifically in the region v5 found, not just its
            # global max -- if v6's max box is a false positive elsewhere, that
            # would otherwise hide "v6 assigns near-zero here" behind an
            # unrelated number.
            best_overlap = None
            if r6.boxes is not None:
                for box in r6.boxes:
                    if int(box.cls[0]) != 0:
                        continue
                    cand_bbox = [float(v) for v in box.xyxy[0]]
                    ov = iou(v5_bbox, cand_bbox)
                    if ov > 0.1 and (best_overlap is None or float(box.conf[0]) > best_overlap[0]):
                        best_overlap = (float(box.conf[0]), cand_bbox, ov)
            row["v5"] = (v5_conf, v5_bbox, brightness)
            row["v6_at_v5_region"] = best_overlap

        rows.append(row)

        if frame_idx in snapshot_indices:
            v5_img = frame.copy()
            v6_img = frame.copy()
            if b5 is not None:
                draw_box(v5_img, b5[1], (0, 200, 0), f"v5 {b5[0]:.2f}")
            if b6 is not None:
                draw_box(v6_img, b6[1], (0, 0, 220), f"v6 {b6[0]:.2f}")
            else:
                cv2.putText(v6_img, "v6: NO BOX (any class, conf>=0.001)", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 220), 2)
            side_by_side = np.hstack([v5_img, v6_img])
            cv2.imwrite(str(OUT_DIR / f"frame_{frame_idx:05d}_v5_vs_v6.jpg"), side_by_side)

    cap.release()

    # Report
    lines = [
        "# v5 vs v6 diagnostic — laying_dim.MOV",
        "",
        f"Clip: `{CLIP_PATH}` ({total_frames} frames, rotation={rotation!r}).",
        f"Sampled every {STRIDE}th frame, both models at conf>={RAW_CONF} (effectively unthresholded), imgsz={IMGSZ}.",
        "Purely diagnostic -- this clip is not touched for training.",
        "",
        "| frame | v5 conf | v5 brightness (region) | v6 conf in v5's region (IoU) | v6 max conf anywhere |",
        "|---|---|---|---|---|",
    ]
    n_v5_hit = 0
    n_v6_in_region = 0
    for row in rows:
        f = row["frame"]
        if row["v5"] is None:
            v6max = row["v6_max_anywhere"]
            v6max_cell = f"{v6max[0]:.3f}" if v6max is not None else "none"
            lines.append(f"| {f} | - (v5 no box) | - | - | {v6max_cell} |")
            continue
        n_v5_hit += 1
        v5_conf, v5_bbox, brightness = row["v5"]
        v6r = row["v6_at_v5_region"]
        v6max = row["v6_max_anywhere"]
        if v6r is not None:
            n_v6_in_region += 1
            v6_cell = f"{v6r[0]:.3f} (IoU {v6r[2]:.2f})"
        else:
            v6_cell = "none (<0.001)"
        v6max_cell = f"{v6max[0]:.3f}" if v6max is not None else "none"
        lines.append(f"| {f} | {v5_conf:.3f} | {brightness:.1f} | {v6_cell} | {v6max_cell} |")

    lines += [
        "",
        f"v5 found a person in {n_v5_hit}/{len(rows)} sampled frames.",
        f"Of those, v6 assigned ANY confidence (down to 0.001) inside v5's box in {n_v6_in_region}/{n_v5_hit}.",
        "",
        f"Annotated side-by-side frames written to `{OUT_DIR.relative_to(REPO_ROOT)}/`.",
    ]
    report_path = OUT_DIR / "report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[done] {n_v5_hit}/{len(rows)} sampled frames have a v5 person box.")
    print(f"[done] v6 assigns non-zero confidence in that region on {n_v6_in_region}/{n_v5_hit} of those.")
    print(f"[done] Report: {report_path}")
    print(f"[done] Snapshots: {OUT_DIR}")


if __name__ == "__main__":
    main()

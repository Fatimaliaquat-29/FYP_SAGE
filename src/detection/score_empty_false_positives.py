"""Person false-positive rate on held-out EMPTY rooms, over every frame. Read-only.

Why this is a separate script from score_heldout_objects.py
-----------------------------------------------------------
Those two answer different questions and need different data:

  furniture accuracy  -> needs hand-drawn boxes, so it can only ever be
                         measured on the sparse subset somebody labelled
  person FALSE POSITIVES on an empty room
                      -> needs NO labels at all. The room is empty; that IS
                         the ground truth. Every person detection is wrong by
                         definition.

So this runs over EVERY frame, not the labelled subset. That matters: the
labelling stride is chosen for human effort (one frame per viewpoint), and a
handheld clip pans across angles between sampled frames. If the model fires on
a chair at an angle that fell between two labelled frames, a sparse evaluation
never sees it. Sampling is a labelling compromise; it must not become a
measurement compromise.

What counts as a false positive
-------------------------------
ONLY `person`. Furniture detections in an empty room are CORRECT -- the
furniture is really there -- so they are reported separately as context, never
as errors. Confusing the two would make a well-performing model look broken.

Usage
-----
    python src/detection/score_empty_false_positives.py \
        --model models/yolov8n_sage_merged_v3.pt

    # compare two checkpoints over identical frames
    python src/detection/score_empty_false_positives.py \
        --model models/yolov8n_sage_merged_v3.pt --model models/yolov8n.pt
"""

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cv2

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.footage_paths import RESERVED_EMPTY, is_reserved

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def iter_frames(path: Path, stride: int):
    """Yield (frame_index, image) for a video or a still image."""
    if path.suffix.lower() in IMAGE_EXTENSIONS:
        image = cv2.imread(str(path))
        if image is not None:
            yield 0, image
        return

    capture = cv2.VideoCapture(str(path))
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        index += 1
        if stride <= 1 or index % stride == 0:
            yield index, frame
    capture.release()


def score_clip(model, path: Path, stride: int, conf: float, imgsz: int):
    """Returns (n_frames, n_frames_with_person, person_boxes, other_classes, worst)."""
    n_frames = 0
    frames_with_person = 0
    person_boxes = 0
    other = Counter()
    worst = []  # (confidence, frame_index) of the most confident false positives

    for index, frame in iter_frames(path, stride):
        n_frames += 1
        found_person = False
        for result in model.predict(frame, conf=conf, imgsz=imgsz, verbose=False):
            for box in result.boxes or []:
                name = result.names[int(box.cls[0])].strip().lower()
                if name == "person":
                    found_person = True
                    person_boxes += 1
                    worst.append((float(box.conf[0]), index))
                else:
                    other[name] += 1
        if found_person:
            frames_with_person += 1

    worst.sort(reverse=True)
    return n_frames, frames_with_person, person_boxes, other, worst[:5]


def main():
    parser = argparse.ArgumentParser(
        description="Person false-positive rate over EVERY frame of held-out empty rooms")
    parser.add_argument("--empty_dir", type=str, default=str(RESERVED_EMPTY),
                        help="Held-out empty-room footage. Default: yolo_testing/Reserved/Empty")
    parser.add_argument("--model", type=str, action="append", required=True,
                        help="Weights to score. Repeat to compare checkpoints on identical frames.")
    parser.add_argument("--conf", type=float, default=0.25,
                        help="Detection confidence threshold (default 0.25)")
    parser.add_argument("--imgsz", type=int, default=320,
                        help="Inference resolution (default 320, what the merged series was "
                             "trained and gated at). Stock yolov8n.pt is a 640 model -- pass "
                             "640 for it. Comparing two models at different imgsz or different "
                             "--conf makes the numbers non-comparable.")
    parser.add_argument("--stride", type=int, default=1,
                        help="Frame stride. DEFAULT 1 = every frame, which is the point of this "
                             "script -- raise it only for a quick smoke test, and say so when "
                             "reporting the number.")
    args = parser.parse_args()

    empty_dir = Path(args.empty_dir)
    if not empty_dir.is_dir():
        raise SystemExit(f"{empty_dir} not found.")

    clips = sorted(p for p in empty_dir.rglob("*")
                   if p.suffix.lower() in VIDEO_EXTENSIONS | IMAGE_EXTENSIONS)
    if not clips:
        raise SystemExit(f"No footage under {empty_dir}.")

    if not is_reserved(empty_dir):
        print(f"WARNING: {empty_dir} is not under Reserved/. If the model trained on this")
        print("         footage, the false-positive rate below measures fit, not generalisation.\n")

    if args.stride > 1:
        print(f"WARNING: --stride {args.stride} skips frames. A pan angle between sampled frames")
        print("         can hide a real false positive. Use stride 1 for the reported number.\n")

    print(f"empty-room footage: {len(clips)} clip(s) under {empty_dir}")
    print(f"conf={args.conf}  stride={args.stride}  imgsz={args.imgsz}")
    print("Ground truth: these rooms contain NO people, so every `person` detection is an error.\n")

    from ultralytics import YOLO

    for model_arg in args.model:
        model_path = Path(model_arg)
        if not model_path.exists():
            print(f"SKIP {model_path} -- not found")
            continue
        model = YOLO(str(model_path))

        print(f"=== {model_path.name} ===")
        header = f"{'clip':<34} {'frames':>7} {'FP frames':>10} {'FP rate':>8} {'boxes':>6}"
        print(header)
        print("-" * len(header))

        totals = defaultdict(int)
        all_other = Counter()
        flagged = []
        for clip in clips:
            n, fp_frames, boxes, other, worst = score_clip(model, clip, args.stride, args.conf, args.imgsz)
            if n == 0:
                print(f"{clip.name[:33]:<34} unreadable")
                continue
            totals["frames"] += n
            totals["fp_frames"] += fp_frames
            totals["boxes"] += boxes
            all_other.update(other)
            rate = 100 * fp_frames / n
            print(f"{clip.name[:33]:<34} {n:>7} {fp_frames:>10} {rate:>7.2f}% {boxes:>6}")
            if worst:
                flagged.append((clip.name, worst))

        print("-" * len(header))
        n, fp = totals["frames"], totals["fp_frames"]
        rate = 100 * fp / n if n else 0.0
        print(f"{'ALL':<34} {n:>7} {fp:>10} {rate:>7.2f}% {totals['boxes']:>6}")

        if flagged:
            print("\n  Most confident false positives (inspect these frames first):")
            for name, worst in flagged:
                shown = ", ".join(f"frame {i} @ {c:.2f}" for c, i in worst)
                print(f"    {name}: {shown}")

        if all_other:
            print("\n  Furniture detected in these rooms (NOT errors -- the furniture is real):")
            print("   ", dict(all_other.most_common()))
        print()


if __name__ == "__main__":
    main()

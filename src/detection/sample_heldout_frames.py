"""Samples frames from the held-out evaluation footage, ready for HAND labelling.

Why this exists
---------------
The furniture labels in our training and validation data were guessed by a
stock COCO YOLOv8n (see report_label_sources.py). Scoring the model against
those is circular. The only cure is a set of boxes a human drew, on a room the
model never trained on.

`yolo_testing/Reserved/` is that room. It is protected by assert_not_reserved() in
the training-data producers (see footage_paths.py), but it contains no labels
at all. This script does the mechanical half -- pulling frames out -- so the
only manual work left is drawing boxes.

Labelling shortcut -- ONLY when the camera is genuinely static
--------------------------------------------------------------
If the camera does not move, furniture does not move either, so you can label
ONE frame and copy that .txt to every other frame from the same position.

That shortcut is unsafe on handheld footage, and applying it there silently
offsets every box -- poisoning the one measurement this eval exists to make
honest. So this script MEASURES camera drift (phase correlation between kept
frames) and tells you per clip whether copying is safe. Do not assume it is.

Measured on the first held-out clip: a handheld phone video drifting up to
14 px, where copying would have corrupted the whole eval set.

The empty/ clips are the best ones to start with: with nobody in frame the
score is pure furniture precision/recall, with no person confound.

Safety
------
Writes ONLY into --out_dir, and refuses to place output inside datasets/,
yolo_testing/ or Testing/ -- those trees are walked by the training scripts, and dropping
frames into them is exactly the silent contamination footage_paths.py's
assert_not_reserved() exists to prevent.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.footage_paths import RESERVED_ROOT

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

# Directory names that training/eval scripts rglob. Output must never land in
# one: extracted frames written back under yolo_testing/ would be discovered as if
# they were source footage, and could be swept into a training set.
FORBIDDEN_PARENTS = ("datasets", "yolo_testing", "Testing")


def assert_safe_output(out_dir: Path):
    """Refuse to write into any tree a training script walks."""
    resolved = out_dir.resolve()
    for part in resolved.parts:
        if part in FORBIDDEN_PARENTS:
            raise SystemExit(
                f"Refusing to write to {resolved}.\n"
                f"  '{part}/' is walked by the dataset builders, so frames placed there can be\n"
                "  swept into training -- which permanently destroys the held-out set's value.\n"
                "  Pick an --out_dir outside those trees (default: eval/heldout_objects/)."
            )


def iter_source_clips(source_dir: Path):
    """Yield (relative_key, path) for every image/video under source_dir.

    Keys are built from the path RELATIVE to source_dir, not the bare stem:
    empty/room.mp4 and falls/room.mp4 would otherwise collide and silently
    overwrite each other's frames -- a failure this project has already hit.
    """
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in IMAGE_EXTENSIONS and suffix not in VIDEO_EXTENSIONS:
            continue
        try:
            relative = path.relative_to(source_dir)
        except ValueError:
            relative = Path(path.name)
        key = "_".join(list(relative.parts[:-1]) + [relative.stem])
        key = key.replace(" ", "_").replace("-", "_")
        yield key, path


# Translation (pixels) between kept frames above which the copy-one-label
# shortcut stops being safe. Deliberately strict: a few pixels of offset on
# every box is a systematic bias in the ONE eval set that is supposed to be
# trustworthy, and the shortcut only ever saves minutes.
DRIFT_TOLERANCE_PX = 2.0


def measure_drift(frames):
    """Peak translation of each frame from the first, via phase correlation.

    frames: list of grayscale float32 arrays, in capture order.
    Returns (max_shift_px, per_frame_shifts). Empty/1-frame input -> (0.0, []).
    """
    if len(frames) < 2:
        return 0.0, []

    import cv2

    reference = frames[0]
    shifts = []
    for frame in frames[1:]:
        (dx, dy), _ = cv2.phaseCorrelate(reference, frame)
        shifts.append((dx ** 2 + dy ** 2) ** 0.5)
    return (max(shifts) if shifts else 0.0), shifts


def report_drift(max_shift: float):
    """Tell the labeller whether one .txt can be reused across this clip."""
    if max_shift <= DRIFT_TOLERANCE_PX:
        print(f"    camera STATIC (max drift {max_shift:.1f}px) -- "
              "label one frame, copy the .txt to the rest")
        return True
    print(f"    camera MOVES (max drift {max_shift:.1f}px) -- "
          "LABEL EACH FRAME SEPARATELY.")
    print("      Copying one .txt across these frames would offset every box by up to")
    print(f"      {max_shift:.0f}px, biasing the eval set this script exists to keep honest.")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Extract frames from held-out footage for hand labelling")
    parser.add_argument("--source_dir", type=str, default=str(RESERVED_ROOT),
                        help="Held-out footage to sample (read-only). Defaults to yolo_testing/Reserved.")
    parser.add_argument("--out_dir", type=str,
                        default=str(REPO_ROOT / "eval" / "heldout_objects"),
                        help="Where sampled frames are written. Must be outside datasets/, yolo_testing/ and Testing/")
    parser.add_argument("--stride", type=int, default=30,
                        help="Keep every Nth video frame (default 30, ~1/sec at 30fps). "
                             "Raise it if the camera never moves -- fewer frames means fewer "
                             "camera positions to hand-label.")
    parser.add_argument("--max_frames", type=int, default=200,
                        help="Stop after this many frames total (default 200). Hand labelling is "
                             "the bottleneck, not extraction.")
    parser.add_argument("--dry_run", action="store_true",
                        help="Report what would be extracted without writing anything")
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    out_dir = Path(args.out_dir)
    if not source_dir.is_dir():
        raise SystemExit(f"{source_dir} not found.")
    assert_safe_output(out_dir)

    import cv2

    clips = list(iter_source_clips(source_dir))
    if not clips:
        raise SystemExit(f"No images or videos found under {source_dir}.")

    print(f"source:  {source_dir}")
    print(f"out:     {out_dir}")
    print(f"clips:   {len(clips)}")
    print(f"stride:  every {args.stride} frames, cap {args.max_frames}")
    print()

    images_out = out_dir / "images"
    labels_out = out_dir / "labels"
    if not args.dry_run:
        images_out.mkdir(parents=True, exist_ok=True)
        labels_out.mkdir(parents=True, exist_ok=True)

    written = 0
    any_clip_moves = False
    for key, path in clips:
        if written >= args.max_frames:
            print(f"  (frame cap {args.max_frames} reached; remaining clips skipped)")
            break

        if path.suffix.lower() in IMAGE_EXTENSIONS:
            image = cv2.imread(str(path))
            if image is None:
                print(f"  SKIP unreadable {path.name}")
                continue
            if not args.dry_run:
                cv2.imwrite(str(images_out / f"{key}.jpg"), image)
            written += 1
            print(f"  {key}.jpg  (still image)")
            continue

        capture = cv2.VideoCapture(str(path))
        total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        kept = 0
        index = 0
        grayscales = []
        while written < args.max_frames:
            ok, frame = capture.read()
            if not ok:
                break
            index += 1
            if index % args.stride:
                continue
            if not args.dry_run:
                cv2.imwrite(str(images_out / f"{key}_{index:06d}.jpg"), frame)
            grayscales.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype("float32"))
            kept += 1
            written += 1
        capture.release()
        print(f"  {key}: {kept} frames kept of {total or 'unknown'}")

        max_shift, _ = measure_drift(grayscales)
        if not report_drift(max_shift):
            any_clip_moves = True

    print()
    print(f"{'would extract' if args.dry_run else 'extracted'} {written} frames")
    if args.dry_run:
        return

    print()
    print("NEXT -- draw the boxes:")
    print(f"  1. Label furniture in {images_out}")
    print("     Use the SAGE class indices (src/detection/sage_classes.py), YOLO txt format:")
    print("       <class_idx> <x_center> <y_center> <width> <height>   (all normalised 0-1)")
    print(f"  2. Save each .txt beside its image in {labels_out}")
    if any_clip_moves:
        print("     DO NOT reuse one .txt across frames of a clip flagged 'camera MOVES' above.")
        print("     Label those frames individually -- copying would offset every box.")
    else:
        print("     Every clip above measured STATIC, so you may label one frame per clip and")
        print("     copy that .txt to its other frames.")
    print("  3. An image with NO furniture still needs an EMPTY .txt file, not a missing one.")
    print("     A missing file is indistinguishable from 'not yet labelled', and scoring")
    print("     would silently skip it.")
    print("  4. Then score:")
    print(f"     python src/detection/score_heldout_objects.py --eval_dir {out_dir} \\")
    print("            --model models/yolov8n_sage_merged_v3.pt")


if __name__ == "__main__":
    main()

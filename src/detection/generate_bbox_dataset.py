"""Builds a YOLO fine-tuning dataset (single 'person' class) from Testing/ footage.

No manual bounding-box labeling needed: MediaPipe already extracts 33 body
keypoints per frame for the existing posture pipeline, so a padded box drawn
around those keypoints becomes a free bounding-box label. This targets YOLO's
main real-footage weakness found during benchmarking -- it frequently fails to
detect a person once they are lying/fallen, because COCO's training photos are
almost all upright people.

Whole clips (not individual frames) are assigned to train or val, to avoid
near-duplicate frames from the same clip leaking across the split.
"""

import argparse
import sys
from pathlib import Path

import cv2
import mediapipe as mp

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
POSE_MODEL_PATH = REPO_ROOT / "models" / "pose_landmarker_full.task"
DEFAULT_OUT_DIR = REPO_ROOT / "datasets" / "sage_person_finetune"

# Clips whose ground truth is dominated by a fallen/lying person -- exactly the
# case the baseline benchmark showed YOLO struggling with. Keeping this list
# explicit (rather than data-driven) mirrors how the real-footage benchmark
# report categorized clips, so before/after comparisons stay apples-to-apples.
FALL_LYING_KEYWORDS = ("fall", "lying")


def find_clips(testing_dir: Path):
    return sorted(p for p in testing_dir.rglob("*") if p.suffix.lower() in VIDEO_EXTENSIONS)


def is_fall_lying_clip(clip_path: Path) -> bool:
    name = clip_path.stem.lower()
    return any(kw in name for kw in FALL_LYING_KEYWORDS)


def split_clips(clips, val_every=5):
    """Assign whole clips to train/val, stratified by upright vs fall/lying,
    so val isn't accidentally all-upright or all-fall/lying."""
    upright = [c for c in clips if not is_fall_lying_clip(c)]
    fall_lying = [c for c in clips if is_fall_lying_clip(c)]

    train, val = [], []
    for group in (upright, fall_lying):
        for i, clip in enumerate(group):
            (val if (i % val_every == val_every - 1) else train).append(clip)
    return train, val


def landmarks_to_bbox(landmarks, min_visibility, pad_fraction):
    xs = [lm.x for lm in landmarks if lm.visibility >= min_visibility]
    ys = [lm.y for lm in landmarks if lm.visibility >= min_visibility]
    if len(xs) < 4:
        return None

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    pad_x = (x_max - x_min) * pad_fraction
    pad_y = (y_max - y_min) * pad_fraction
    x_min = max(0.0, x_min - pad_x)
    x_max = min(1.0, x_max + pad_x)
    y_min = max(0.0, y_min - pad_y)
    y_max = min(1.0, y_max + pad_y)

    width = x_max - x_min
    height = y_max - y_min
    if width <= 0 or height <= 0:
        return None

    x_center = x_min + width / 2
    y_center = y_min + height / 2
    return x_center, y_center, width, height


def clip_key(clip_path: Path, testing_dir: Path) -> str:
    """Filename-safe key that is unique across the whole Testing/ tree.

    The clip's own stem is NOT enough: several folders reuse names like
    `normal` and `old`, so keying on the stem alone made later clips silently
    overwrite earlier ones' frames. Including the parent folders keeps
    same-named clips from different sessions distinct.
    """
    try:
        relative = clip_path.resolve().relative_to(testing_dir.resolve())
    except ValueError:
        relative = Path(clip_path.name)
    parts = list(relative.parts[:-1]) + [relative.stem]
    return "_".join(parts).replace(" ", "_").replace("-", "_")


def process_clip(detector, clip_path, images_dir, labels_dir, stride, min_visibility, pad_fraction, clip_stem):
    cap = cv2.VideoCapture(str(clip_path))
    if not cap.isOpened():
        print(f"  Warning: could not open {clip_path}")
        return 0

    frame_idx = 0
    written = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if frame_idx % stride != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = detector.detect(mp_image)
        if not result.pose_landmarks:
            continue

        bbox = landmarks_to_bbox(result.pose_landmarks[0], min_visibility, pad_fraction)
        if bbox is None:
            continue

        stem = f"{clip_stem}_{frame_idx:06d}"
        image_path = images_dir / f"{stem}.jpg"
        label_path = labels_dir / f"{stem}.txt"

        cv2.imwrite(str(image_path), frame)
        x_center, y_center, width, height = bbox
        label_path.write_text(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n", encoding="utf-8")
        written += 1

    cap.release()
    return written


def main():
    parser = argparse.ArgumentParser(description="Generate a YOLO person-detection fine-tuning dataset from Testing/ footage")
    parser.add_argument("--testing_dir", type=str, default=str(REPO_ROOT / "Testing"))
    parser.add_argument("--out_dir", type=str, default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--stride", type=int, default=2, help="Keep every Nth frame (reduces near-duplicate frames)")
    parser.add_argument("--min_visibility", type=float, default=0.3)
    parser.add_argument("--pad_fraction", type=float, default=0.12, help="Padding added around the keypoint-derived box")
    parser.add_argument("--val_every", type=int, default=5, help="Every Nth clip (per category) goes to val")
    args = parser.parse_args()

    testing_dir = Path(args.testing_dir)
    out_dir = Path(args.out_dir)
    clips = find_clips(testing_dir)
    if not clips:
        print(f"No clips found under {testing_dir}")
        sys.exit(1)

    train_clips, val_clips = split_clips(clips, val_every=args.val_every)
    print(f"Clips: {len(clips)} total -> {len(train_clips)} train, {len(val_clips)} val")

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(POSE_MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
    )
    detector = PoseLandmarker.create_from_options(options)

    totals = {}
    for split_name, split_clips_list in (("train", train_clips), ("val", val_clips)):
        images_dir = out_dir / "images" / split_name
        labels_dir = out_dir / "labels" / split_name
        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)

        split_total = 0
        for clip in split_clips_list:
            print(f"[{split_name}] {clip.relative_to(testing_dir)} ...")
            written = process_clip(
                detector, clip, images_dir, labels_dir,
                args.stride, args.min_visibility, args.pad_fraction,
                clip_key(clip, testing_dir),
            )
            print(f"  wrote {written} labeled frames")
            split_total += written
        totals[split_name] = split_total

    detector.close()

    data_yaml = out_dir / "data.yaml"
    data_yaml.write_text(
        "path: {}\n"
        "train: images/train\n"
        "val: images/val\n"
        "names:\n"
        "  0: person\n".format(out_dir.resolve().as_posix()),
        encoding="utf-8",
    )

    print(f"\nTotal labeled frames: train={totals['train']}, val={totals['val']}")
    print(f"Dataset written to {out_dir}")
    print(f"data.yaml: {data_yaml}")


if __name__ == "__main__":
    main()

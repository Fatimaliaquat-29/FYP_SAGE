"""Auto-labels the four high-coverage Hammad clips through the SAME path
generate_bbox_dataset.py uses for real training data (make_pose_detector,
process_clip, build_object_labeler) -- but into a STAGING directory, not any
merged dataset. Nothing here touches training; this exists so the auto-labels
can be spot-checked before anyone decides to promote them.

Clips (95-100% MediaPipe coverage per coverage_hammad_clips.py):
    LyingDown_HM, Sitting_Chair_HM, Standing_Walking_HM, PartiallyCovered_HM

After labeling, renders a random sample of frames per clip with boxes drawn,
for visual spot-check.
"""

import random
import sys
from pathlib import Path

import cv2

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.footage_paths import HELD_OUT_ROOT, assert_not_protected
from src.detection.footage_rotation import get_rotation, needs_verification
from src.detection.generate_bbox_dataset import build_object_labeler, make_pose_detector, process_clip
from src.detection.sage_classes import SAGE_CLASSES

CLIPS_DIR = HELD_OUT_ROOT / "Hammad Clips"
TARGET_CLIPS = ["LyingDown_HM.mp4", "Sitting_Chair_HM.mp4", "Standing_Walking_HM.mp4", "PartiallyCovered_HM.mp4"]

STOCK_YOLO_PATH = REPO_ROOT / "models" / "yolov8n.pt"
OUT_DIR = REPO_ROOT / "datasets" / "hammad_autolabel_staging"
SPOTCHECK_DIR = REPO_ROOT / "results" / "yolo_person_detection" / "hammad_autolabel_spotcheck"
STRIDE = 2          # matches this project's default training-data stride
MIN_VISIBILITY = 0.3
PAD_FRACTION = 0.12
OBJECT_CONF = 0.5
SAMPLES_PER_CLIP = 18
SEED = 0


def draw_labels(image_path: Path, label_path: Path, out_path: Path):
    frame = cv2.imread(str(image_path))
    h, w = frame.shape[:2]
    if label_path.exists():
        for line in label_path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            cls = int(float(parts[0]))
            cx, cy, bw, bh = (float(v) for v in parts[1:5])
            x1, y1 = int((cx - bw / 2) * w), int((cy - bh / 2) * h)
            x2, y2 = int((cx + bw / 2) * w), int((cy + bh / 2) * h)
            color = (0, 200, 0) if cls == 0 else (0, 160, 255)
            name = SAGE_CLASSES[cls] if cls < len(SAGE_CLASSES) else str(cls)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, name, (x1, max(0, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    cv2.imwrite(str(out_path), frame)


def main():
    images_dir, labels_dir = OUT_DIR / "images", OUT_DIR / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    object_labeler = build_object_labeler(STOCK_YOLO_PATH, OBJECT_CONF)

    written_by_clip = {}
    for name in TARGET_CLIPS:
        clip_path = CLIPS_DIR / name
        if not clip_path.exists():
            print(f"SKIP {name}: not found under {CLIPS_DIR}")
            continue
        assert_not_protected(clip_path, "Hammad staging auto-label (spot-check only, not merged into training)",
                             allow_protected=True)
        if needs_verification(clip_path):
            print(f"SKIP {name}: rotation not verified.")
            continue
        rotation = get_rotation(clip_path)

        clip_stem = clip_path.stem
        before = set(images_dir.glob(f"{clip_stem}_*.jpg"))
        detector = make_pose_detector()
        n_written = process_clip(
            detector, clip_path, images_dir, labels_dir,
            stride=STRIDE, min_visibility=MIN_VISIBILITY, pad_fraction=PAD_FRACTION,
            clip_stem=clip_stem, object_labeler=object_labeler, stats=None, rotation=rotation,
        )
        after = set(images_dir.glob(f"{clip_stem}_*.jpg")) - before
        written_by_clip[name] = sorted(after)
        print(f"{name}: {n_written} frames written")

    print(f"\nStaging set: {OUT_DIR} (NOT merged into any training dataset)")

    # Spot-check sample, per clip.
    SPOTCHECK_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    for name, images in written_by_clip.items():
        clip_out = SPOTCHECK_DIR / Path(name).stem
        clip_out.mkdir(parents=True, exist_ok=True)
        sample = images if len(images) <= SAMPLES_PER_CLIP else rng.sample(images, SAMPLES_PER_CLIP)
        sample.sort()
        for image_path in sample:
            label_path = labels_dir / f"{image_path.stem}.txt"
            draw_labels(image_path, label_path, clip_out / image_path.name)
        print(f"  {name}: {len(sample)} spot-check frames -> {clip_out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

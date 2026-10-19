"""Extracts ONLY the frames MediaPipe misses on Standing_Walking_Dim_HM and
Sitting_Dim_HM -- the two Hammad clips investigate_hammad_misses.py found to
be short scattered flicker (mean miss-run 3.8-5.2 frames), not real dropouts,
so the decision was to patch the gaps with hand-drawn boxes rather than
relabel the whole clip. Behind_Chair_HM (mean run 13.3 frames, up to 136) was
NOT patchable by this logic and moved to full hand-labeling instead -- see
handlabels/round6/ and docs/HAMMAD_CLIPS_ROUND6.md.

Writes into handlabels/round6_patch/images/ (every missed frame, ALL of them,
not a sample -- a patch needs to cover every gap or the auto-label/hand-label
mix would silently have holes) with labels/ empty and ready, matching the
handlabels.py workflow: these get passed as --handlabels_dir alongside the
clip's normal MediaPipe run WITHOUT --handlabels_only, so hand-drawn boxes
override exactly the frames MediaPipe missed and MediaPipe's own frames are
kept everywhere else.
"""

import sys
from pathlib import Path

import cv2
import mediapipe as mp

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.footage_paths import HELD_OUT_ROOT
from src.detection.footage_rotation import apply as apply_rotation
from src.detection.footage_rotation import get_rotation, needs_verification
from src.detection.generate_bbox_dataset import landmarks_to_bbox

CLIPS_DIR = HELD_OUT_ROOT / "Hammad Clips"
TARGET_CLIPS = ["Standing_Walking_Dim_HM.mp4", "Sitting_Dim_HM.mp4"]
POSE_MODEL_PATH = REPO_ROOT / "models" / "pose_landmarker_full.task"
MIN_VISIBILITY = 0.3
OUT_DIR = REPO_ROOT / "handlabels" / "round6_patch"


def make_pose_detector():
    return mp.tasks.vision.PoseLandmarker.create_from_options(
        mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(POSE_MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
        )
    )


def find_missed_frames(clip_path: Path, rotation):
    """First pass: VIDEO-mode tracking, no frames written -- just which indices miss."""
    cap = cv2.VideoCapture(str(clip_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    detector = make_pose_detector()
    missed = []
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        frame = apply_rotation(frame, rotation)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = detector.detect_for_video(mp_image, int(frame_idx / fps * 1000))
        ok = bool(result.pose_landmarks) and landmarks_to_bbox(result.pose_landmarks[0], MIN_VISIBILITY, 0.0) is not None
        if not ok:
            missed.append(frame_idx)
    cap.release()
    detector.close()
    return missed


def save_frames(clip_path: Path, frame_indices, rotation, images_dir: Path):
    """Second pass: re-read the clip and save exactly the requested frames."""
    cap = cv2.VideoCapture(str(clip_path))
    remaining = set(frame_indices)
    idx = 0
    saved = 0
    while remaining:
        ret, frame = cap.read()
        if not ret:
            break
        idx += 1
        if idx in remaining:
            frame = apply_rotation(frame, rotation)
            cv2.imwrite(str(images_dir / f"{clip_path.stem}_{idx:06d}.jpg"), frame)
            remaining.discard(idx)
            saved += 1
    cap.release()
    return saved


def main():
    images_dir, labels_dir = OUT_DIR / "images", OUT_DIR / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for name in TARGET_CLIPS:
        clip_path = CLIPS_DIR / name
        if not clip_path.exists():
            print(f"SKIP {name}: not found")
            continue
        if needs_verification(clip_path):
            print(f"SKIP {name}: rotation not verified")
            continue
        rotation = get_rotation(clip_path)

        print(f"Processing {name} ...")
        missed = find_missed_frames(clip_path, rotation)
        saved = save_frames(clip_path, missed, rotation, images_dir)
        print(f"  {len(missed)} missed frames found, {saved} saved to {images_dir.relative_to(REPO_ROOT)}")
        total += saved

    print(f"\n{total} patch frames extracted -> {OUT_DIR}")
    print("Draw boxes for these same as any hand-label round (SAGE class indices, YOLO txt format).")
    print(f"An image with genuinely nothing labelled still needs an EMPTY .txt in {labels_dir.relative_to(REPO_ROOT)},")
    print("not a missing file -- a missing file reads as 'not yet labelled', not 'nothing here'.")
    print("These are a PATCH, not a full relabel: pass --handlabels_dir handlabels/round6_patch to")
    print("generate_bbox_dataset.py WITHOUT --handlabels_only, so MediaPipe's own frames for these")
    print("two clips are kept everywhere else and only these exact gaps get overridden.")


if __name__ == "__main__":
    main()

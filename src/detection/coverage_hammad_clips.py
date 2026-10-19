"""MediaPipe pose coverage for yolo_testing/held_out/Hammad Clips/. Read-only:
runs the VIDEO-mode PoseLandmarker (see generate_bbox_dataset.make_pose_detector
for why VIDEO mode, not IMAGE) over every frame of each clip and reports what
fraction get a pose, so it's clear which clips can lean on auto-labeling with a
spot-check versus which need full hand-labeling. Writes no dataset, no labels --
just a report. Does not touch training data or call assert_not_protected: this
is evaluation, not a training-data producer, and reading held_out/ is exactly
what evaluation scripts are for.
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
from src.detection.footage_rotation import describe as describe_rotation
from src.detection.footage_rotation import get_rotation, needs_verification
from src.detection.generate_bbox_dataset import landmarks_to_bbox

CLIPS_DIR = HELD_OUT_ROOT / "Hammad Clips"
POSE_MODEL_PATH = REPO_ROOT / "models" / "pose_landmarker_full.task"
MIN_VISIBILITY = 0.3
OUT_PATH = REPO_ROOT / "results" / "yolo_person_detection" / "hammad_clips_coverage.md"


def make_pose_detector():
    return mp.tasks.vision.PoseLandmarker.create_from_options(
        mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(POSE_MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
        )
    )


def score_clip(clip_path: Path):
    rotation = get_rotation(clip_path)
    if needs_verification(clip_path):
        print(f"  WARNING: {clip_path.name} has no verified rotation -- skipping rather than guessing.")
        return None

    cap = cv2.VideoCapture(str(clip_path))
    if not cap.isOpened():
        print(f"  WARNING: could not open {clip_path.name}")
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    detector = make_pose_detector()  # fresh per clip -- tracking state must not bleed across clips
    n_frames = 0
    n_with_pose = 0
    n_bbox_ok = 0  # has landmarks AND enough of them pass min_visibility to form a box

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        frame = apply_rotation(frame, rotation)
        n_frames += 1

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = detector.detect_for_video(mp_image, int(frame_idx / fps * 1000))

        if result.pose_landmarks:
            n_with_pose += 1
            if landmarks_to_bbox(result.pose_landmarks[0], MIN_VISIBILITY, 0.0) is not None:
                n_bbox_ok += 1

    cap.release()
    detector.close()
    return {
        "clip": clip_path.name,
        "rotation": describe_rotation(rotation),
        "frames": n_frames,
        "with_pose": n_with_pose,
        "pose_coverage": n_with_pose / n_frames if n_frames else 0.0,
        "bbox_ok": n_bbox_ok,
        "bbox_coverage": n_bbox_ok / n_frames if n_frames else 0.0,
    }


def main():
    clips = sorted(CLIPS_DIR.glob("*.mp4"))
    if not clips:
        print(f"No clips found under {CLIPS_DIR}")
        sys.exit(1)

    print(f"{len(clips)} clip(s) under {CLIPS_DIR}\n")
    rows = []
    for clip in clips:
        print(f"Processing {clip.name} ...")
        row = score_clip(clip)
        if row is None:
            continue
        rows.append(row)
        print(f"  frames={row['frames']}  pose_coverage={100*row['pose_coverage']:.1f}%  "
              f"usable_bbox_coverage={100*row['bbox_coverage']:.1f}%")

    rows.sort(key=lambda r: r["bbox_coverage"])

    lines = [
        "# MediaPipe VIDEO-mode coverage — Hammad Clips (held_out/, untriaged)",
        "",
        f"{len(rows)} clips, every frame (no stride), min_visibility={MIN_VISIBILITY}.",
        "`pose_coverage` = frames where MediaPipe found a person at all.",
        "`bbox_coverage` = frames where enough of those landmarks clear min_visibility "
        "to form a usable auto-label box (what generate_bbox_dataset.py would actually write).",
        "",
        "| clip | rotation | frames | pose coverage | usable bbox coverage |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['clip']} | {r['rotation']} | {r['frames']} | "
                      f"{100*r['pose_coverage']:.1f}% | {100*r['bbox_coverage']:.1f}% |")

    lines += [
        "",
        "## Reading this",
        "",
        "High bbox coverage (roughly 80%+, in line with this project's easier clips) -- "
        "auto-labeling + spot-check is plausible.",
        "Low coverage (well under that, in line with dim/occluded clips elsewhere in this "
        "project) -- MediaPipe's own detector is failing on these frames, which is exactly "
        "the condition full hand-labeling exists for; auto-labeling would silently "
        "under-represent them, same failure mode documented for TV_Lounge_1_Fall and "
        "laying_dim.MOV.",
    ]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

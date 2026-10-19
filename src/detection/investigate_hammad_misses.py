"""What is MediaPipe actually missing on the three medium-coverage Hammad clips
(Standing_Walking_Dim_HM 87%, Sitting_Dim_HM 86%, Behind_Furniture_HM 67%)?

Read-only. Runs the same VIDEO-mode tracker as coverage_hammad_clips.py but
records a per-frame hit/miss sequence, then reports whether misses are a few
long dropouts (losing the person entirely for a stretch) or scattered
single-frame flickers (occasional failures within an otherwise-tracked clip)
-- the distinction the labeling decision (hand-label the whole clip vs. patch
the gaps) turns on. Saves a sample of MISSED frames, spread across distinct
runs rather than clustered in one, for visual review.
"""

import random
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
TARGET_CLIPS = ["Standing_Walking_Dim_HM.mp4", "Sitting_Dim_HM.mp4", "Behind_Chair_HM.mp4"]
POSE_MODEL_PATH = REPO_ROOT / "models" / "pose_landmarker_full.task"
MIN_VISIBILITY = 0.3
OUT_DIR = REPO_ROOT / "results" / "yolo_person_detection" / "hammad_miss_investigation"
SAMPLES_PER_CLIP = 18
SEED = 0


def make_pose_detector():
    return mp.tasks.vision.PoseLandmarker.create_from_options(
        mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(POSE_MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
        )
    )


def find_runs(hits):
    """Contiguous runs of False (misses) in a bool list. Returns list of (start, end) 1-based frame indices, inclusive."""
    runs = []
    start = None
    for i, ok in enumerate(hits, start=1):
        if not ok and start is None:
            start = i
        elif ok and start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(hits)))
    return runs


def process(clip_path: Path, out_dir: Path):
    rotation = get_rotation(clip_path)
    if needs_verification(clip_path):
        print(f"  WARNING: {clip_path.name} rotation unverified -- skipping.")
        return None

    cap = cv2.VideoCapture(str(clip_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    detector = make_pose_detector()

    hits = []
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
        hits.append(ok)
    cap.release()
    detector.close()

    total = len(hits)
    n_miss = sum(1 for h in hits if not h)
    runs = find_runs(hits)
    run_lengths = [end - start + 1 for start, end in runs]

    print(f"  {clip_path.name}: {total} frames, {n_miss} missed ({100*n_miss/total:.1f}%), "
          f"{len(runs)} distinct miss run(s)")
    if run_lengths:
        print(f"    run lengths: min={min(run_lengths)} max={max(run_lengths)} "
              f"mean={sum(run_lengths)/len(run_lengths):.1f} frames "
              f"(~{max(run_lengths)/fps:.1f}s longest)")

    # Sample missed frames spread across distinct runs: round-robin one frame
    # per run until we have enough, rather than randomly (which would
    # over-represent one long dropout and under-represent short scattered ones).
    rng = random.Random(SEED)
    picks = []
    run_pool = [list(range(s, e + 1)) for s, e in runs]
    for r in run_pool:
        rng.shuffle(r)
    i = 0
    while len(picks) < SAMPLES_PER_CLIP and any(run_pool):
        for r in run_pool:
            if r and len(picks) < SAMPLES_PER_CLIP:
                picks.append(r.pop())
        if not any(run_pool):
            break
    picks = sorted(set(picks))

    # Re-read the clip to grab just the picked frames (cheaper than holding 1500 frames in RAM).
    clip_out = out_dir / clip_path.stem
    clip_out.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(clip_path))
    idx = 0
    picks_set = set(picks)
    saved = 0
    while picks_set:
        ret, frame = cap.read()
        if not ret:
            break
        idx += 1
        if idx in picks_set:
            frame = apply_rotation(frame, rotation)
            run_no = next(i for i, (s, e) in enumerate(runs, start=1) if s <= idx <= e)
            cv2.imwrite(str(clip_out / f"{clip_path.stem}_{idx:06d}_run{run_no}.jpg"), frame)
            picks_set.discard(idx)
            saved += 1
    cap.release()
    print(f"    saved {saved} missed-frame samples -> {clip_out.relative_to(REPO_ROOT)}")

    return {
        "clip": clip_path.name, "total": total, "n_miss": n_miss,
        "n_runs": len(runs), "run_lengths": run_lengths, "fps": fps,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = []
    for name in TARGET_CLIPS:
        clip_path = CLIPS_DIR / name
        if not clip_path.exists():
            print(f"SKIP {name}: not found")
            continue
        print(f"Processing {name} ...")
        row = process(clip_path, OUT_DIR)
        if row:
            summary.append(row)

    lines = [
        "# What MediaPipe misses — medium-coverage Hammad clips",
        "",
        "Read-only investigation, no labels written. Per-frame VIDEO-mode tracking; a "
        "miss run is a maximal contiguous stretch of frames with no usable pose box.",
        "",
        "| clip | frames | missed | miss runs | shortest run | longest run | mean run |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in summary:
        rl = r["run_lengths"]
        lines.append(
            f"| {r['clip']} | {r['total']} | {r['n_miss']} ({100*r['n_miss']/r['total']:.1f}%) | "
            f"{r['n_runs']} | {min(rl) if rl else '-'} | {max(rl) if rl else '-'} "
            f"({max(rl)/r['fps']:.1f}s)| {sum(rl)/len(rl):.1f} |" if rl else
            f"| {r['clip']} | {r['total']} | 0 | 0 | - | - | - |"
        )
    lines += [
        "",
        "Many short runs (mean close to 1-2 frames) = scattered flicker, isolated failures "
        "within an otherwise-tracked clip -- patchable with a handful of hand-drawn boxes.",
        "Few long runs = the person is being lost entirely for a stretch (occlusion, tracker "
        "losing the ROI) -- that stretch needs full hand-labeling, not a patch.",
        "",
        "Sampled missed frames (raw, no boxes -- there is nothing to draw) are saved per clip, "
        "named `<clip>_<frame>_run<N>.jpg` so frames from the same dropout are identifiable "
        "as a group rather than looking like independent failures.",
    ]
    (OUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT_DIR / 'report.md'}")


if __name__ == "__main__":
    main()

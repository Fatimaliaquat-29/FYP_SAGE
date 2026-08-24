"""
benchmarks/regression_check_old_corpus_sts.py
================================================
Fast regression check (streaming only, no threaded/jitter passes) of
sit_to_stand detections across the existing 28-clip test_footage/ corpus,
to confirm the fallback-path hip-rise guard added this session (see
gait_features._detect_fast_shallow_transition's guard #5) does not
suppress any previously-working detection on the corpus it wasn't derived
from. Read-only reuse of the same extraction path as
validate_gait_on_footage.py.
"""
import glob
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluate_real_footage import extract_keypoints, _keypoints_from_row, _visibility_from_row
from src.posture.pipeline_utils import build_pose_row, reset_session_state
from src.gait import gait_features as gf
from src.gait.gait_stream import StreamingGaitRiskAssessor

WINDOW_FRAMES = gf.MIN_WINDOW_FRAMES
REASSESS_EVERY_N = 15


def extract_pose_rows(video_path: str):
    reset_session_state()
    kp_rows, fps, total = extract_keypoints(video_path)
    rows = []
    for kp_row in kp_rows:
        keypoints = _keypoints_from_row(kp_row)
        pose_row = build_pose_row(
            timestamp=kp_row.get("timestamp"), frame=int(kp_row.get("frame_number", 0)),
            keypoints=keypoints, visibility=_visibility_from_row(kp_row),
        )
        rows.append(pose_row)
    return rows, fps


def main():
    print("CAVEAT: all test_footage/ clips are self-recorded from a single (N=1) "
          "subject -- nothing below generalizes to a population. See the standing "
          "caveat at the top of docs/GAIT_DATA_ASSESSMENT.md.\n")
    video_paths = sorted(glob.glob(str(Path("test_footage") / "**" / "*.MOV"), recursive=True)) + \
                  sorted(glob.glob(str(Path("test_footage") / "**" / "*.mp4"), recursive=True))
    for vp in video_paths:
        name = Path(vp).stem
        try:
            rows, fps = extract_pose_rows(vp)
        except Exception as exc:
            print(f"{name}: EXTRACT ERROR {exc}")
            continue
        if len(rows) < WINDOW_FRAMES:
            continue
        sa = StreamingGaitRiskAssessor(window_frames=WINDOW_FRAMES, reassess_every_n_frames=REASSESS_EVERY_N)
        detections = []
        n_assess = 0
        for i, row in enumerate(rows):
            result = sa.push_frame(row)
            if result is None:
                continue
            n_assess += 1
            sts = next(s for s in result["signals"] if s["name"] == "sit_to_stand")
            if sts["available"]:
                detections.append((row.get("timestamp", i / fps), sts["value"]["duration_sec"], sts["value"]["reversal_count"]))
        durs = ",".join(f"{d[1]:.2f}/{d[2]:.0f}" for d in detections)
        print(f"{name}: n_assess={n_assess} n_sts_detections={len(detections)} [dur/rev]={durs}")


if __name__ == "__main__":
    main()

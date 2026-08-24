"""
benchmarks/profile_gait_pipeline.py
====================================
Standalone timing/profiling harness for src/gait/ (GaitRiskAssessor +
gait_features.py) ONLY -- does not touch the RF/LSTM/TCN posture
classifiers. Not a unit test: prints a timing breakdown to stdout so the
actual bottleneck can be identified before any optimization work, and can
be re-run after each change (or later on real Jetson hardware) to confirm
the change actually moved the numbers.

Usage:
    python benchmarks/profile_gait_pipeline.py
    python benchmarks/profile_gait_pipeline.py --frames 150 --repeats 200
"""
import argparse
import cProfile
import pstats
import sys
import time
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_gait_risk import _walking_window, _sit_to_stand_window
from src.gait import gait_features as gf
from src.gait.gait_risk import GaitRiskAssessor


def _time_it(label, fn, repeats):
    # Warm-up (import caches, numpy dispatch, etc.) so the timed loop
    # measures steady-state cost, not one-time setup.
    fn()
    t0 = time.perf_counter()
    for _ in range(repeats):
        fn()
    elapsed = time.perf_counter() - t0
    per_call_ms = (elapsed / repeats) * 1000.0
    print(f"  {label:<32s} {per_call_ms:8.3f} ms/call   ({repeats} calls, {elapsed:.3f}s total)")
    return per_call_ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=150, help="window length in frames")
    ap.add_argument("--repeats", type=int, default=200, help="timing repeats per stage")
    ap.add_argument("--profile", action="store_true", help="also run cProfile over assess_risk()")
    args = ap.parse_args()

    window = _walking_window(args.frames, speed=0.12, stride_jitter=0.08, speed_jitter=0.05, sway_amp=0.02)
    sts_window = _sit_to_stand_window(shaky=True, n_frames=max(args.frames, 90))
    assessor = GaitRiskAssessor()

    print(f"\n=== Stage-by-stage timing (window = {args.frames} frames, {args.repeats} repeats each) ===")
    _time_it("_raw_keypoint_array", lambda: gf._raw_keypoint_array(window), args.repeats)
    raw = gf._raw_keypoint_array(window)
    _time_it("_normalized_positions", lambda: gf._normalized_positions(window, _raw=raw), args.repeats)
    _time_it("_torso_scaled_hip_track", lambda: gf._torso_scaled_hip_track(window, _raw=raw), args.repeats)
    hip_track = gf._torso_scaled_hip_track(window, _raw=raw)
    _time_it("compute_walking_speed", lambda: gf.compute_walking_speed(window, _hip_track=hip_track), args.repeats)
    _time_it("compute_stride_regularity", lambda: gf.compute_stride_regularity(window, _raw=raw), args.repeats)
    _time_it("compute_postural_sway", lambda: gf.compute_postural_sway(window, _hip_track=hip_track), args.repeats)
    _time_it("compute_sit_to_stand (walking win)", lambda: gf.compute_sit_to_stand(window, _raw=raw), args.repeats)
    sts_raw = gf._raw_keypoint_array(sts_window)
    _time_it("compute_sit_to_stand (sts win)", lambda: gf.compute_sit_to_stand(sts_window, _raw=sts_raw), args.repeats)

    print(f"\n=== Full assess_risk() end-to-end ===")
    per_call_ms = _time_it("assess_risk (walking window)", lambda: assessor.assess_risk(window), args.repeats)
    _time_it("assess_risk (sit-to-stand window)", lambda: assessor.assess_risk(sts_window), args.repeats)
    print(f"\n  -> implied max throughput: {1000.0 / per_call_ms:.1f} assess_risk() calls/sec (single-threaded, walking window)")

    if args.profile:
        print(f"\n=== cProfile breakdown (assess_risk x {args.repeats}, walking window, cumulative time) ===")
        profiler = cProfile.Profile()
        profiler.enable()
        for _ in range(args.repeats):
            assessor.assess_risk(window)
        profiler.disable()
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
        stats.print_stats(25)
        print(stream.getvalue())


if __name__ == "__main__":
    main()

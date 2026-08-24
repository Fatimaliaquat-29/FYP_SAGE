"""
tests/test_gait_stream.py
==========================
Tests for src/gait/gait_stream.py (RingFrameBuffer, StreamingGaitRiskAssessor,
GaitPipeline) -- the streaming/windowed + producer-consumer wrapper around
GaitRiskAssessor. Does not re-test GaitRiskAssessor's own scoring (see
test_gait_risk.py for that); this file only covers the buffering/cadence/
threading glue this module adds on top of it.
"""

import sys
import time
import unittest
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.gait import gait_features as gf
from src.gait.gait_stream import RingFrameBuffer, StreamingGaitRiskAssessor, GaitPipeline, TorsoBaselineCalibrator
from tests.test_gait_risk import _walking_window, _standing_kps, _sustained_bend_window

RNG = np.random.default_rng(99)


class RingFrameBufferTests(unittest.TestCase):
    def test_rejects_maxlen_below_min_window_frames(self):
        with self.assertRaises(ValueError):
            RingFrameBuffer(maxlen=gf.MIN_WINDOW_FRAMES - 1)

    def test_bounded_size_evicts_oldest(self):
        buf = RingFrameBuffer(maxlen=gf.MIN_WINDOW_FRAMES)
        rows = _walking_window(gf.MIN_WINDOW_FRAMES + 50, speed=0.1)
        for row in rows:
            buf.append(row)
        self.assertEqual(len(buf), gf.MIN_WINDOW_FRAMES)
        self.assertTrue(buf.is_full())
        # The buffer should hold the LAST MIN_WINDOW_FRAMES frames, not the first.
        snap = buf.snapshot()
        self.assertEqual(snap[-1]["frame"], rows[-1]["frame"])
        self.assertEqual(snap[0]["frame"], rows[-gf.MIN_WINDOW_FRAMES]["frame"])

    def test_snapshot_is_a_stable_copy(self):
        buf = RingFrameBuffer(maxlen=gf.MIN_WINDOW_FRAMES)
        for row in _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.1):
            buf.append(row)
        snap = buf.snapshot()
        buf.append({"timestamp": 999.0, "frame": 999, "keypoints": [np.nan] * 66})
        self.assertNotEqual(snap[-1]["frame"], 999)

    def test_snapshot_shares_row_objects_with_the_live_buffer(self):
        """Regression test documenting snapshot()'s SHALLOW-copy aliasing
        contract (see docs/GAIT_CODE_REVIEW.md finding #13 and
        RingFrameBuffer.snapshot's own docstring): the returned list is new,
        but its elements are the SAME row-dict objects the live buffer still
        holds (not a deep copy) -- a caller must not mutate a returned row
        in place. `maxlen` == number of rows appended here, so nothing has
        been evicted yet and every row must still be present by identity."""
        buf = RingFrameBuffer(maxlen=gf.MIN_WINDOW_FRAMES)
        rows = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.1)
        for row in rows:
            buf.append(row)
        snap = buf.snapshot()
        self.assertIs(snap[0], rows[0])
        self.assertIs(snap[-1], rows[-1])


class StreamingGaitRiskAssessorTests(unittest.TestCase):
    def test_returns_none_until_buffer_full(self):
        sa = StreamingGaitRiskAssessor(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=5)
        rows = _walking_window(gf.MIN_WINDOW_FRAMES - 1, speed=0.1)
        for row in rows:
            result = sa.push_frame(row)
            self.assertIsNone(result)

    def test_reassesses_on_cadence_once_full(self):
        sa = StreamingGaitRiskAssessor(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=5)
        rows = _walking_window(gf.MIN_WINDOW_FRAMES + 20, speed=0.1)
        results = [sa.push_frame(row) for row in rows]

        # Nothing before the buffer is full.
        for r in results[:gf.MIN_WINDOW_FRAMES - 1]:
            self.assertIsNone(r)
        # The very first frame that fills the buffer triggers an assessment
        # (frames_since_last_assessment reaches the buffer-fill point, which
        # is >= reassess_every_n_frames=5 for a MIN_WINDOW_FRAMES-sized buffer).
        self.assertIsNotNone(results[gf.MIN_WINDOW_FRAMES - 1])
        # Subsequent assessments should land roughly every 5 frames, not every frame.
        non_none = [i for i, r in enumerate(results) if r is not None]
        gaps = np.diff(non_none)
        self.assertTrue(np.all(gaps == 5), f"expected every-5-frame cadence, got gaps={gaps}")

    def test_result_matches_direct_assess_risk_call(self):
        """The streamed result for a full window must be identical to
        calling GaitRiskAssessor.assess_risk() directly on the same window
        -- this module must not change scoring, only when it's computed."""
        from src.gait.gait_risk import GaitRiskAssessor
        rows = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.12, stride_jitter=0.05)

        sa = StreamingGaitRiskAssessor(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=1)
        streamed = None
        for row in rows:
            streamed = sa.push_frame(row)

        direct = GaitRiskAssessor().assess_risk(rows)
        self.assertEqual(streamed["risk_score"], direct["risk_score"])
        for s1, s2 in zip(streamed["signals"], direct["signals"]):
            self.assertEqual(s1["value"], s2["value"])


class TorsoBaselineCalibratorTests(unittest.TestCase):
    """Tests for TorsoBaselineCalibrator -- the real-time-session torso-
    baseline safety gate (see realtime_fall_detection.py's own "GAIT
    integration" docstring for how this is actually wired into the live
    pipeline; this file covers the calibrator's own logic in isolation,
    with no camera/MediaPipe dependency)."""

    def _standing_row(self, i):
        return {"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()}

    def test_calibrates_from_a_confirmed_standing_run(self):
        calib = TorsoBaselineCalibrator(min_run_frames=30)
        completed_at = None
        for i in range(45):
            if calib.observe(self._standing_row(i), "Standing", False):
                completed_at = i
        self.assertIsNotNone(completed_at, "must calibrate once 30 confirmed-Standing frames accumulate")
        self.assertEqual(completed_at, 29, "must complete on the exact frame the run reaches min_run_frames")
        self.assertTrue(calib.is_calibrated)
        self.assertIsNotNone(calib.baseline)
        self.assertEqual(calib.baseline_mode, "2d", "no world_keypoints on this fixture -- must fall back to 2D")
        expected = gf._raw_torso_len([self._standing_row(0)])[0]
        self.assertAlmostEqual(calib.baseline, float(expected), places=4)

    def test_non_standing_frames_never_calibrate(self):
        calib = TorsoBaselineCalibrator(min_run_frames=30)
        for i in range(60):
            fired = calib.observe(self._standing_row(i), "Sitting", False)
            self.assertFalse(fired)
        self.assertFalse(calib.is_calibrated)

    def test_fall_detected_frames_never_calibrate_even_if_labeled_standing(self):
        """The audit's explicit safety requirement: never calibrate during
        a fall, even if the posture label itself still reads 'Standing'
        (e.g. a brief pre-collapse frame)."""
        calib = TorsoBaselineCalibrator(min_run_frames=30)
        for i in range(60):
            fired = calib.observe(self._standing_row(i), "Standing", True)
            self.assertFalse(fired)
        self.assertFalse(calib.is_calibrated)

    def test_an_interruption_resets_the_contiguous_run(self):
        """29 Standing frames (one short of the 30-frame requirement), then
        a single non-Standing frame, then Standing again -- must NOT
        calibrate at frame 30 of the ORIGINAL run; the interruption forces
        a fresh count."""
        calib = TorsoBaselineCalibrator(min_run_frames=30)
        for i in range(29):
            self.assertFalse(calib.observe(self._standing_row(i), "Standing", False))
        self.assertFalse(calib.observe(self._standing_row(29), "Unknown", False))
        # Only 1 more Standing frame so far post-interruption -- must not
        # have silently kept the old count.
        self.assertFalse(calib.observe(self._standing_row(30), "Standing", False))
        self.assertFalse(calib.is_calibrated)

    def test_calibrates_exactly_once(self):
        calib = TorsoBaselineCalibrator(min_run_frames=30)
        for i in range(30):
            calib.observe(self._standing_row(i), "Standing", False)
        self.assertTrue(calib.is_calibrated)
        first_baseline = calib.baseline

        # Feeding more (even different-looking) frames after calibration
        # must be a pure no-op.
        for i in range(30, 60):
            fired = calib.observe({"timestamp": i / 30.0, "keypoints": _standing_kps(noise=0.05)},
                                   "Standing", False)
            self.assertFalse(fired)
        self.assertEqual(calib.baseline, first_baseline)

    def test_reset_allows_recalibration(self):
        calib = TorsoBaselineCalibrator(min_run_frames=30)
        for i in range(30):
            calib.observe(self._standing_row(i), "Standing", False)
        self.assertTrue(calib.is_calibrated)
        calib.reset()
        self.assertFalse(calib.is_calibrated)
        self.assertIsNone(calib.baseline)
        fired = False
        for i in range(30):
            fired = calib.observe(self._standing_row(i), "Standing", False) or fired
        self.assertTrue(fired)
        self.assertTrue(calib.is_calibrated)

    def test_min_run_frames_floored_at_calibration_segment_frames(self):
        """A caller passing an unreasonably small min_run_frames must not
        be able to undercut compute_torso_baseline()'s own internal
        20-frame segment requirement."""
        calib = TorsoBaselineCalibrator(min_run_frames=1)
        self.assertGreaterEqual(calib._min_run_frames, gf.CALIBRATION_SEGMENT_FRAMES)


class StreamingGaitRiskAssessorTorsoBaselineTests(unittest.TestCase):
    """Proves set_torso_baseline() actually reaches assess_risk() through
    the streaming path -- the concrete mechanism that makes the torso-
    collapse protections (gait_features.MIN_TORSO_BASELINE_RATIO) reachable
    from a live session rather than only from a direct assess_risk() unit
    test."""

    def test_default_behavior_unchanged_when_baseline_never_set(self):
        sa = StreamingGaitRiskAssessor(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=1)
        window = _sustained_bend_window(n_frames=gf.MIN_WINDOW_FRAMES)
        result = None
        for row in window:
            result = sa.push_frame(row)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertTrue(speed_signal["available"], "without a baseline, the spurious sustained-bend "
                                                     "reading must still be reported exactly as before "
                                                     "this class ever had set_torso_baseline()")

    def test_set_torso_baseline_gates_the_next_assessment(self):
        sa = StreamingGaitRiskAssessor(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=1)
        standing_prefix = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(30)]
        baseline = gf.compute_torso_baseline(standing_prefix)
        self.assertIsNotNone(baseline)

        sa.set_torso_baseline(baseline)
        window = _sustained_bend_window(n_frames=gf.MIN_WINDOW_FRAMES)
        result = None
        for row in window:
            result = sa.push_frame(row)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertFalse(speed_signal["available"], "set_torso_baseline() must actually reach "
                                                      "assess_risk() -- the sustained-bend artifact "
                                                      "must now be suppressed")

    def test_set_torso_baseline_none_reverts_to_ungated(self):
        sa = StreamingGaitRiskAssessor(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=1)
        standing_prefix = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(30)]
        baseline = gf.compute_torso_baseline(standing_prefix)
        sa.set_torso_baseline(baseline)
        sa.set_torso_baseline(None)
        window = _sustained_bend_window(n_frames=gf.MIN_WINDOW_FRAMES)
        result = None
        for row in window:
            result = sa.push_frame(row)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertTrue(speed_signal["available"])


class GaitPipelineTests(unittest.TestCase):
    def test_produces_a_result_without_blocking_the_producer(self):
        # queue_maxsize is generously large here on purpose: this test is
        # about correctness of the produce -> consume -> assess flow, not
        # about drop-under-overload behavior (a real camera paces frames at
        # ~30fps with plenty of headroom for the ~2ms consumer cost; a tight
        # unpaced test loop submitting frames back-to-back is a much higher
        # rate than that, so a small queue would legitimately drop most of
        # them before the buffer ever filled -- that's correct, intentional
        # behavior, just not what this test is checking).
        results = []
        pipeline = GaitPipeline(
            window_frames=gf.MIN_WINDOW_FRAMES,
            reassess_every_n_frames=5,
            queue_maxsize=500,
            on_result=lambda r: results.append(r),
        )
        pipeline.start()
        try:
            rows = _walking_window(gf.MIN_WINDOW_FRAMES + 10, speed=0.1)
            t0 = time.perf_counter()
            for row in rows:
                pipeline.submit_frame(row)
            producer_elapsed = time.perf_counter() - t0

            deadline = time.perf_counter() + 5.0
            while not results and time.perf_counter() < deadline:
                time.sleep(0.02)
        finally:
            pipeline.stop()

        self.assertGreater(len(results), 0, "GaitPipeline never produced a result within the timeout")
        self.assertIn("risk_score", results[0])
        self.assertIn("signals", results[0])
        # Submitting ~160 frames through a non-blocking queue should be fast
        # (well under real camera frame-interval budgets) -- this is a loose
        # sanity bound, not a strict perf assertion.
        self.assertLess(producer_elapsed, 2.0)

    def test_get_latest_result_reflects_last_assessment(self):
        pipeline = GaitPipeline(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=5, queue_maxsize=500)
        pipeline.start()
        try:
            self.assertIsNone(pipeline.get_latest_result())
            rows = _walking_window(gf.MIN_WINDOW_FRAMES + 10, speed=0.1)
            for row in rows:
                pipeline.submit_frame(row)

            deadline = time.perf_counter() + 5.0
            while pipeline.get_latest_result() is None and time.perf_counter() < deadline:
                time.sleep(0.02)
        finally:
            pipeline.stop()

        self.assertIsNotNone(pipeline.get_latest_result())

    def test_stop_joins_cleanly_and_is_idempotent(self):
        pipeline = GaitPipeline(window_frames=gf.MIN_WINDOW_FRAMES)
        pipeline.start()
        pipeline.stop()
        pipeline.stop()  # must not raise on a second stop()

    def test_small_queue_drops_under_overload_without_crashing(self):
        """A deliberately tiny queue, fed a burst of frames far faster than
        a real 30fps camera would -- the producer must never block (this is
        the entire point of submit_frame), some submissions should report a
        drop, and stop() must still join cleanly afterward."""
        pipeline = GaitPipeline(window_frames=gf.MIN_WINDOW_FRAMES, reassess_every_n_frames=5, queue_maxsize=2)
        pipeline.start()
        try:
            rows = _walking_window(300, speed=0.1)
            accepted = [pipeline.submit_frame(row) for row in rows]
            self.assertIn(False, accepted, "expected at least one drop under this overload burst")
        finally:
            pipeline.stop()


if __name__ == "__main__":
    unittest.main()

"""
tests/test_realtime_error_resilience.py
========================================
Regression tests for the Phase-1 audit's crash-isolation findings in
realtime_fall_detection.py's run() loop:

  - the MediaPipe VIDEO-mode timestamp now comes from time.monotonic(), not
    wall-clock time.time() -- a backward clock step (e.g. an NTP sync) must
    not raise `ValueError: Input timestamp must be monotonically increasing.`
    (confirmed this is what MediaPipe actually raises, against this
    project's own installed mediapipe build, before writing this test)
  - a single-frame exception from MediaPipe detection, posture/fall
    classification, or object detection must not end the whole run() loop
  - a live (camera-index) input source retries a transient read failure
    instead of stopping immediately; a video-file input source still stops
    immediately at end-of-file (this must NOT regress -- it's the correct,
    pre-existing behavior for every other test in this suite that replays a
    file through run()/pose_test.py)

These are wiring/resilience tests, not signal-correctness tests, so they
deliberately use small synthetic (blank) frames through a fake VideoCapture
rather than real footage -- MediaPipe, the heuristic classifier, and (where
relevant) YOLO still run for real, unmocked, on those frames; only the frame
SOURCE and (for the exception-injection tests) one specific call are faked.
This keeps the suite fast and independent of which real clips happen to be
present on disk, appropriate for wiring tests per this project's own
test_realtime_gait_integration.py precedent (which reserves real footage for
signal-correctness proofs, not wiring proofs).
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

POSE_MODEL_PATH = REPO_ROOT / "models" / "pose_landmarker_full.task"
DEFAULT_OBJECT_MODEL = REPO_ROOT / "models" / "yolov8n_sage_merged_v5.pt"  # matches realtime_fall_detection.DEFAULT_OBJECT_MODEL_PATH

_SKIP_REASON = None
if not POSE_MODEL_PATH.exists():
    _SKIP_REASON = f"MediaPipe pose model not found at {POSE_MODEL_PATH}"
else:
    try:
        import realtime_fall_detection as rfd
        import mediapipe as mp
        from src.posture.pipeline_utils import classify_posture_and_fall as _real_classify
        from src.detection.yolo_objects import YOLOObjectDetector
    except Exception as exc:  # pragma: no cover -- environment-dependent
        _SKIP_REASON = f"realtime_fall_detection could not be imported: {exc}"


class _FakeCapture:
    """Stands in for cv2.VideoCapture: yields a fixed, scripted sequence of
    (ok, frame) reads, then False forever. Lets these tests drive run()'s
    loop deterministically without a real camera or video file."""

    def __init__(self, frames):
        self.frames = list(frames)
        self.read_calls = 0

    def isOpened(self):
        return True

    def read(self):
        self.read_calls += 1
        if self.frames:
            return self.frames.pop(0)
        return False, None

    def release(self):
        pass


def _blank_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


@unittest.skipIf(_SKIP_REASON is not None, _SKIP_REASON or "")
class MonotonicClockTests(unittest.TestCase):
    """§3.1: MediaPipe's VIDEO-mode timestamp must survive a backward
    wall-clock step. Empirically confirmed (see this file's module
    docstring) that MediaPipe raises ValueError for a non-increasing
    timestamp -- before the fix, this loop fed it directly from
    time.time(), so a backward step would have propagated that ValueError
    all the way out of run() (pre-existing crash risk this test locks in
    as fixed)."""

    def test_backward_wall_clock_step_does_not_crash_the_loop(self):
        frames = [(True, _blank_frame()) for _ in range(8)]
        fake_cap = _FakeCapture(frames)

        real_time = __import__("time").time
        # Wall clock jumps backward by an hour partway through the run --
        # simulates an NTP correction. time.monotonic() is untouched (it's a
        # separate mock target), matching what a real clock step does.
        call_count = {"n": 0}

        def flaky_wall_clock():
            call_count["n"] += 1
            base = real_time()
            if call_count["n"] > 4:
                return base - 3600
            return base

        with mock.patch("cv2.VideoCapture", return_value=fake_cap), \
             mock.patch("time.time", side_effect=flaky_wall_clock):
            try:
                rfd.run(
                    "fake_source", use_lstm=False, show_display=False,
                    use_objects=False, use_gait=False,
                )
            except ValueError as e:
                self.fail(f"run() raised {e!r} on a backward wall-clock step -- "
                          "the MediaPipe timestamp is not actually monotonic-clock-based")

        self.assertEqual(fake_cap.read_calls, 9,
                          "expected all 8 scripted frames to be consumed plus the "
                          "final end-of-stream read")


@unittest.skipIf(_SKIP_REASON is not None, _SKIP_REASON or "")
class CrashIsolationTests(unittest.TestCase):
    """§3.2: a single-frame exception from each of the three previously-
    unguarded call sites must not end the whole run() loop. Each test
    injects a real exception on one specific frame via the real (unmocked)
    function/method, then confirms run() still consumes every scripted
    frame afterward."""

    def _run_and_count_frames(self, n_frames, **run_kwargs):
        frames = [(True, _blank_frame()) for _ in range(n_frames)]
        fake_cap = _FakeCapture(frames)
        seen_frames = []
        with mock.patch("cv2.VideoCapture", return_value=fake_cap):
            rfd.run(
                "fake_source", show_display=False,
                on_gait_update=lambda d: seen_frames.append(d["frame"]),
                **run_kwargs,
            )
        return fake_cap

    def test_mediapipe_exception_does_not_crash_the_loop(self):
        original = mp.tasks.vision.PoseLandmarker.detect_for_video
        state = {"n": 0}

        def flaky(self_, *args, **kwargs):
            state["n"] += 1
            if state["n"] == 3:
                raise RuntimeError("injected MediaPipe failure for testing")
            return original(self_, *args, **kwargs)

        with mock.patch.object(mp.tasks.vision.PoseLandmarker, "detect_for_video", flaky):
            fake_cap = self._run_and_count_frames(
                6, use_lstm=False, use_objects=False, use_gait=True)

        self.assertEqual(fake_cap.read_calls, 7,
                          "run() stopped early after the injected MediaPipe exception -- "
                          "it is not actually isolated per-frame")

    def test_classification_exception_does_not_crash_the_loop(self):
        state = {"n": 0}

        def flaky(row, previous_rows=None, lstm_classifier=None):
            state["n"] += 1
            if state["n"] == 3:
                raise RuntimeError("injected classification failure for testing")
            return _real_classify(row, previous_rows=previous_rows, lstm_classifier=lstm_classifier)

        with mock.patch("realtime_fall_detection.classify_posture_and_fall", flaky):
            fake_cap = self._run_and_count_frames(
                6, use_lstm=False, use_objects=False, use_gait=False)

        self.assertEqual(fake_cap.read_calls, 7,
                          "run() stopped early after the injected classification exception")

    def test_object_detection_exception_does_not_crash_the_loop(self):
        if not DEFAULT_OBJECT_MODEL.exists():
            self.skipTest(f"YOLO weights not found at {DEFAULT_OBJECT_MODEL}")
        original = YOLOObjectDetector.detect
        state = {"n": 0}

        def flaky(self_, frame):
            state["n"] += 1
            if state["n"] == 3:
                raise RuntimeError("injected YOLO failure for testing")
            return original(self_, frame)

        with mock.patch.object(YOLOObjectDetector, "detect", flaky):
            fake_cap = self._run_and_count_frames(
                6, use_lstm=False, use_objects=True, use_gait=False)

        self.assertEqual(fake_cap.read_calls, 7,
                          "run() stopped early after the injected YOLO exception")


@unittest.skipIf(_SKIP_REASON is not None, _SKIP_REASON or "")
class CameraRetryTests(unittest.TestCase):
    """§3.3: a live (camera-index) source retries a transient read failure
    instead of stopping; a file-path source must NOT retry (regression
    guard -- every other test/tool in this repo that replays a video file
    through run() relies on immediate stop at end-of-file)."""

    def test_live_source_retries_transient_read_failures(self):
        frames = ([(False, None)] * 3 + [(True, _blank_frame())] * 2)
        fake_cap = _FakeCapture(frames)
        with mock.patch("cv2.VideoCapture", return_value=fake_cap), \
             mock.patch("time.sleep") as mock_sleep:
            rfd.run(0, use_lstm=False, show_display=False, use_objects=False, use_gait=False)

        # 3 initial failures (retried) + 2 real frames + retries again on the
        # trailing False reads: CAMERA_RETRY_MAX_ATTEMPTS reads that each
        # retry, plus one more that finds consecutive_read_failures already
        # at the cap and gives up (that read() call itself still happens
        # before the give-up check).
        expected_calls = 3 + 2 + (rfd.CAMERA_RETRY_MAX_ATTEMPTS + 1)
        self.assertEqual(fake_cap.read_calls, expected_calls,
                          "live-source retry count doesn't match CAMERA_RETRY_MAX_ATTEMPTS")
        self.assertGreaterEqual(mock_sleep.call_count, 3,
                                 "expected a backoff sleep on each retried read")

    def test_file_source_does_not_retry_on_end_of_stream(self):
        frames = [(True, _blank_frame())] * 3 + [(False, None)]
        fake_cap = _FakeCapture(frames)
        with mock.patch("cv2.VideoCapture", return_value=fake_cap), \
             mock.patch("time.sleep") as mock_sleep:
            rfd.run("some_clip.mov", use_lstm=False, show_display=False,
                    use_objects=False, use_gait=False)

        self.assertEqual(fake_cap.read_calls, 4,
                          "a file source retried past end-of-stream -- this is a "
                          "regression, file inputs must stop immediately")
        mock_sleep.assert_not_called()


@unittest.skipIf(_SKIP_REASON is not None, _SKIP_REASON or "")
class ObjectDetectorWarmUpTests(unittest.TestCase):
    """§3.9: the object detector is warmed up once before the main loop, so
    its one-time lazy-init cost doesn't land on the first real frame."""

    def test_warm_up_runs_detect_once_before_the_loop_and_never_raises(self):
        calls = []
        fake_detector = mock.Mock()
        fake_detector.detect = mock.Mock(side_effect=lambda frame: calls.append(frame) or [])
        rfd._warm_up_object_detector(fake_detector)
        self.assertEqual(fake_detector.detect.call_count, 1)

    def test_warm_up_swallows_a_failing_detector_without_raising(self):
        fake_detector = mock.Mock()
        fake_detector.detect = mock.Mock(side_effect=RuntimeError("boom"))
        try:
            rfd._warm_up_object_detector(fake_detector)
        except Exception as e:
            self.fail(f"_warm_up_object_detector raised {e!r} -- it must never raise")

    def test_warm_up_is_a_no_op_for_none(self):
        try:
            rfd._warm_up_object_detector(None)
        except Exception as e:
            self.fail(f"_warm_up_object_detector(None) raised {e!r}")


@unittest.skipIf(_SKIP_REASON is not None, _SKIP_REASON or "")
class YOLODefaultsTests(unittest.TestCase):
    """§3.6: the real-time CLI's default inference resolution and default
    object-detection checkpoint must not silently regress back to the
    values the project's own evaluation showed are unsafe -- imgsz=320
    ("every model in this project detects zero fallen people at 320",
    docs/TRAINING_v6_CONTEXT.md:192-193) or the stale v3 checkpoint
    (superseded by v5; v6 has a documented dim-light regression, commit
    334aa4c)."""

    def test_run_default_object_imgsz_is_640_not_320(self):
        import inspect
        default = inspect.signature(rfd.run).parameters["object_imgsz"].default
        self.assertEqual(default, 640)

    def test_default_object_model_is_v5_and_exists_on_disk(self):
        self.assertEqual(rfd.DEFAULT_OBJECT_MODEL_PATH.name, "yolov8n_sage_merged_v5.pt")
        self.assertTrue(rfd.DEFAULT_OBJECT_MODEL_PATH.exists(),
                         f"{rfd.DEFAULT_OBJECT_MODEL_PATH} does not exist on disk")

    def test_cli_argparse_default_for_imgsz_matches_runs_own_default(self):
        # The CLI default (in main()'s argparse setup) and run()'s own kwarg
        # default are two separate places this value is written -- lock them
        # together so they can't silently drift apart again.
        import inspect
        import re
        source = inspect.getsource(rfd.main)
        match = re.search(r'"--object-imgsz".*?default=(\d+)', source, re.DOTALL)
        self.assertIsNotNone(match, "--object-imgsz argparse default not found in main()")
        cli_default = int(match.group(1))
        run_default = inspect.signature(rfd.run).parameters["object_imgsz"].default
        self.assertEqual(cli_default, run_default)
        self.assertEqual(cli_default, 640)


if __name__ == "__main__":
    unittest.main()

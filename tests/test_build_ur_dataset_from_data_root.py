"""
tests/test_build_ur_dataset_from_data_root.py
===============================================
Regression tests for src/data_processing/build_ur_dataset_from_data_root.py,
which had never actually been exercised end-to-end before the cam1-ingestion
round of the GAIT audit first ran it (see that script's own module
docstring). Two real bugs surfaced on the very first real run:

1. Its PoseLandmarker was built in `RunningMode.IMAGE`, but
   `process_ur_sequence` (imported unchanged from build_lstm_datasets.py)
   always calls `detector.detect_for_video()`, which raises immediately
   against an IMAGE-mode detector. Fixed by delegating detector
   construction to build_lstm_datasets.py's own `make_video_detector()`
   (already correctly VIDEO-mode).

2. It then shared ONE detector across every sequence in the whole run.
   VIDEO-mode detectors require monotonically increasing timestamps across
   all calls on one instance, and every sequence's own clock restarts at
   0 -- so a shared detector crashed with "Input timestamp must be
   monotonically increasing" on the second sequence's first frame (and,
   per make_video_detector's own docstring, would have silently leaked
   tracking state across sequence boundaries even where it didn't crash).
   Fixed by creating and closing a fresh detector per sequence, exactly as
   build_lstm_datasets.py::main() already does for the same dataset.
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import mediapipe as mp

import src.data_processing.build_ur_dataset_from_data_root as mod
from src.data_processing import build_lstm_datasets


class MakeVideoDetectorRunningModeTest(unittest.TestCase):
    def test_make_video_detector_uses_video_mode_not_image_mode(self):
        captured = {}

        def fake_create_from_options(options):
            captured["running_mode"] = options.running_mode

            class _FakeDetector:
                def close(self):
                    pass
            return _FakeDetector()

        with mock.patch.object(mp.tasks.vision.PoseLandmarker, "create_from_options",
                                side_effect=fake_create_from_options):
            build_lstm_datasets.make_video_detector().close()

        self.assertEqual(captured.get("running_mode"), mp.tasks.vision.RunningMode.VIDEO)


class FreshDetectorPerSequenceTests(unittest.TestCase):
    def test_creates_and_closes_a_new_detector_for_every_sequence(self):
        created = []

        class FakeDetector:
            def __init__(self):
                self.closed = False

            def close(self):
                self.closed = True

        def fake_make_video_detector():
            d = FakeDetector()
            created.append(d)
            return d

        def fake_process_ur_sequence(detector, img_dir, seq_id, expected_fall=False):
            self.assertFalse(detector.closed, "detector must still be open while its own sequence is being processed")
            return [], []

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            data_dir = tmp_path / "data"
            for i in range(2):
                (data_dir / "ADL" / f"adl-{i}").mkdir(parents=True)
            for i in range(3):
                (data_dir / "Fall" / f"fall-{i}").mkdir(parents=True)
            model_path = tmp_path / "fake.task"
            model_path.write_bytes(b"x")

            with mock.patch.object(mod, "MODEL_PATH", model_path), \
                 mock.patch.object(mod, "DATA_DIR", data_dir), \
                 mock.patch.object(mod, "make_video_detector", side_effect=fake_make_video_detector), \
                 mock.patch.object(mod, "process_ur_sequence", side_effect=fake_process_ur_sequence):
                with self.assertRaises(SystemExit):
                    mod.main()  # exits(0): fake_process_ur_sequence returns no rows

        self.assertEqual(len(created), 5, "expected one fresh detector per sequence (2 ADL + 3 Fall)")
        self.assertTrue(all(d.closed for d in created), "every per-sequence detector must be closed before the next is created")


if __name__ == "__main__":
    unittest.main()

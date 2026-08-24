"""
tests/test_extract_raw_dataset.py
==================================
Regression tests for src/data_processing/extract_raw_dataset.py, the
adapter for self-recorded training footage under data/raw/. This pipeline
had never actually been run end-to-end: `data/raw/` doesn't exist and
`data/processed_keypoints/real_pose_keypoints.csv` doesn't exist anywhere
on disk. Two real bugs, found by inspection (following the same class of
bug already caught in the sibling UR-dataset adapter):

1. Per-frame timestamps were computed with `time.time()` (wall-clock)
   instead of a fixed video clock (`frame_idx / fps`). `build_lstm_datasets.py`
   already documents exactly this bug for the UR dataset: wall-clock dt
   depends on how fast the CPU processes each image, not on the real
   motion recorded, which silently scales every velocity feature by
   processing speed. Fixed by deriving `current_time` from `frame_idx / fps`
   (RAW_FPS=30.0 default, overridable per call) and switching the detector
   to VIDEO mode (`detect_for_video`), matching `build_lstm_datasets.py`'s
   own UR-sequence handling.
2. That VIDEO-mode switch reintroduces the exact shared-detector bug fixed
   last round in `build_ur_dataset_from_data_root.py`: VIDEO-mode detectors
   require monotonically increasing timestamps across every call on ONE
   instance, and this script's `main()` built one detector and reused it
   across every sequence. Fixed by delegating to `build_lstm_datasets.py`'s
   own `make_video_detector()` (fresh detector per sequence, closed after).
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import cv2

import src.data_processing.extract_raw_dataset as mod


class TimestampIsFixedClockNotWallClockTest(unittest.TestCase):
    def test_process_sequence_uses_frame_index_over_fps_not_time_time(self):
        """The exact bug class this fix targets: two frames processed with
        an artificial wall-clock delay between them must still produce
        timestamps that differ by exactly 1/fps, not by the delay."""
        received_timestamps_ms = []

        class FakeDetector:
            def detect_for_video(self, mp_image, timestamp_ms):
                received_timestamps_ms.append(timestamp_ms)

                class _Result:
                    pose_landmarks = []
                return _Result()

            def close(self):
                pass

        with tempfile.TemporaryDirectory() as tmp:
            seq_dir = Path(tmp)
            img = np.zeros((10, 10, 3), dtype=np.uint8)
            for i in range(3):
                cv2.imwrite(str(seq_dir / f"frame_{i:03d}.png"), img)

            # Simulate a slow machine: a real wall-clock read between frames
            # (mocked here rather than truly sleeping) must NOT affect the
            # timestamps passed to the detector once the fix is in place.
            real_imread = cv2.imread
            call_count = {"n": 0}

            def slow_imread(path):
                call_count["n"] += 1
                return real_imread(path)

            with mock.patch.object(cv2, "imread", side_effect=slow_imread):
                mod.process_sequence(FakeDetector(), str(seq_dir), "test_seq", expected_fall=False, fps=30.0)

        self.assertEqual(len(received_timestamps_ms), 3)
        # frame_idx / 30.0 * 1000 = 0, 33, 66 (int-truncated)
        self.assertEqual(received_timestamps_ms, [0, 33, 66])


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

        def fake_process_sequence(detector, img_dir, seq_id, expected_fall=False):
            self.assertFalse(detector.closed, "detector must still be open while its own sequence is being processed")
            return [], []

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw_dir = tmp_path / "raw"
            for i in range(2):
                (raw_dir / "adl_activities" / f"seq-{i}-rgb").mkdir(parents=True)
            for i in range(3):
                (raw_dir / "fall_events" / f"seq-{i}-rgb").mkdir(parents=True)
            model_path = tmp_path / "fake.task"
            model_path.write_bytes(b"x")

            with mock.patch.object(mod, "MODEL_PATH", model_path), \
                 mock.patch.object(mod, "RAW_DIR", raw_dir), \
                 mock.patch.object(mod, "make_video_detector", side_effect=fake_make_video_detector), \
                 mock.patch.object(mod, "process_sequence", side_effect=fake_process_sequence):
                with self.assertRaises(SystemExit):
                    mod.main()  # exits(0): fake_process_sequence returns no rows

        self.assertEqual(len(created), 5, "expected one fresh detector per sequence (2 ADL + 3 Fall)")
        self.assertTrue(all(d.closed for d in created), "every per-sequence detector must be closed before the next is created")


if __name__ == "__main__":
    unittest.main()

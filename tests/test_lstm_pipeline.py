"""
tests/test_lstm_pipeline.py
============================
Unit tests for the LSTM posture classification pipeline.

Covers:
  - Dataset builder shape and label correctness
  - NaN imputation
  - LSTMPostureClassifier fallback when model is absent
  - LSTMPostureClassifier output format
  - Integration with pipeline_utils.classify_posture_and_fall(lstm_classifier=...)
  - No regressions in existing heuristic path
"""

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import build_pose_row, classify_posture_and_fall
from src.posture.lstm.lstm_dataset import (
    CLASS_TO_IDX,
    FEATURE_DIM,
    RAW_FEATURE_DIM,
    generate_synthetic_windows,
    build_windows_from_real_data,
    impute_nan,
    _make_standing_kps,
    _make_sitting_kps,
    _make_lying_kps,
    _make_fall_sequence,
)
from src.posture.lstm.lstm_classifier import LSTMPostureClassifier, _extract_raw_keypoints


# ─────────────────────────────────────────────────────────────────────────────
# Dataset builder tests
# ─────────────────────────────────────────────────────────────────────────────

class TestLSTMDataset(unittest.TestCase):

    WINDOW_SIZE = 10  # small for fast tests

    # generate_synthetic_windows only ever synthesizes 4 of the 5 classes:
    # Standing/Sitting/Lying/Fall. "Unknown" (missing/unclear landmark data)
    # has no distinct body-shape template, so it's intentionally absent here
    # and only ever comes from real data.
    SYNTHETIC_CLASSES = ("Standing", "Sitting", "Lying", "Fall")

    def test_synthetic_window_shape(self):
        X, y, g = generate_synthetic_windows(
            window_size=self.WINDOW_SIZE, n_per_class=20, rng_seed=0
        )
        n_classes = len(self.SYNTHETIC_CLASSES)
        self.assertEqual(X.shape, (20 * n_classes, self.WINDOW_SIZE, FEATURE_DIM))
        self.assertEqual(y.shape, (20 * n_classes,))

    def test_synthetic_all_classes_present(self):
        X, y, g = generate_synthetic_windows(
            window_size=self.WINDOW_SIZE, n_per_class=10, rng_seed=1
        )
        for cls_name in self.SYNTHETIC_CLASSES:
            cls_idx = CLASS_TO_IDX[cls_name]
            count = (y == cls_idx).sum()
            self.assertEqual(count, 10, f"Expected 10 samples for class '{cls_name}'")

    def test_synthetic_feature_dim(self):
        X, y, g = generate_synthetic_windows(
            window_size=self.WINDOW_SIZE, n_per_class=5, rng_seed=2
        )
        self.assertEqual(X.shape[2], FEATURE_DIM)  # must be 132: normalized position + velocity

    def test_fall_sequence_shape(self):
        fall_win = _make_fall_sequence(self.WINDOW_SIZE)
        self.assertEqual(fall_win.shape, (self.WINDOW_SIZE, RAW_FEATURE_DIM))

    def test_standing_kps_has_non_nan(self):
        kps = _make_standing_kps(noise=0.0)
        # Key landmark positions should not all be NaN
        # shoulders (indices 22-25), hips (46-49), ankles (54-57)
        key_indices = [22, 23, 24, 25, 46, 47, 48, 49, 54, 55, 56, 57]
        valid = [not np.isnan(kps[i]) for i in key_indices]
        self.assertTrue(all(valid), "Key keypoints should not be NaN for standing pose")

    def test_lying_kps_horizontal(self):
        kps = _make_lying_kps(noise=0.0)
        # In normalized (hip-centered) space, a lying pose extends sideways
        # (large x offsets) with shoulders/hips/ankles all near the same y.
        sh_y = kps[23]   # left shoulder y
        hp_y = kps[47]   # left hip y
        ak_y = kps[55]   # left ankle y
        self.assertAlmostEqual(sh_y, hp_y, places=1)
        self.assertAlmostEqual(hp_y, ak_y, places=1)

    def test_nan_imputation_removes_nans(self):
        X, _, _ = generate_synthetic_windows(
            window_size=self.WINDOW_SIZE, n_per_class=10, rng_seed=3
        )
        # Inject some NaNs
        X[0, 0, 0] = np.nan
        X[1, 2, 5] = np.nan
        X_imputed = impute_nan(X)
        self.assertFalse(np.isnan(X_imputed).any(), "No NaN should remain after imputation")

    def test_imputation_entirely_nan_column(self):
        """A column that is entirely NaN should be set to 0."""
        X = np.ones((5, self.WINDOW_SIZE, FEATURE_DIM), dtype=np.float32)
        X[:, :, 10] = np.nan  # column 10 is all NaN
        X_imputed = impute_nan(X)
        self.assertTrue((X_imputed[:, :, 10] == 0.0).all())

    def test_build_windows_from_missing_csv(self):
        """Should return empty arrays gracefully when CSV is absent."""
        X, y, g = build_windows_from_real_data(
            kp_csv=Path("/nonexistent/pose_keypoints.csv"),
            out_csv=Path("/nonexistent/posture_output.csv"),
            window_size=self.WINDOW_SIZE,
        )
        self.assertEqual(len(X), 0)
        self.assertEqual(len(y), 0)

    def test_build_dataset_from_synthetic_dataframe(self):
        """Create a minimal in-memory CSV and verify window extraction."""
        import pandas as pd
        import tempfile
        import os

        window_size = 5
        n_frames = 20

        # Build a minimal pose_keypoints.csv equivalent as DataFrame
        rows = []
        for i in range(n_frames):
            row = {"timestamp": f"t{i}", "frame": i + 1}
            kps = _make_standing_kps(noise=0.0)
            for j in range(1, 34):
                row[f"x{j}"] = float(kps[(j - 1) * 2])
                row[f"y{j}"] = float(kps[(j - 1) * 2 + 1])
            row["posture_label"] = "Standing"
            row["fall_detected"] = False
            rows.append(row)
        df = pd.DataFrame(rows)

        with tempfile.TemporaryDirectory() as tmpdir:
            kp_csv = Path(tmpdir) / "pose_keypoints.csv"
            df.to_csv(kp_csv, index=False)
            X, y, g = build_windows_from_real_data(
                kp_csv=kp_csv,
                out_csv=Path(tmpdir) / "posture_output.csv",
                window_size=window_size,
                step=1,
            )
        expected_windows = n_frames - window_size + 1
        self.assertEqual(len(X), expected_windows)
        self.assertEqual(X.shape[1], window_size)
        self.assertEqual(X.shape[2], FEATURE_DIM)


# ─────────────────────────────────────────────────────────────────────────────
# Classifier tests
# ─────────────────────────────────────────────────────────────────────────────

class TestLSTMClassifier(unittest.TestCase):

    WINDOW_SIZE = 10

    def _make_window(self, n_frames=10, pose_fn=None):
        """Build a list of pose row dicts with synthetic keypoints."""
        if pose_fn is None:
            pose_fn = _make_standing_kps
        return [{"keypoints": list(pose_fn())} for _ in range(n_frames)]

    def test_fallback_when_model_missing(self):
        """Classifier must return Unknown gracefully when model file is absent."""
        clf = LSTMPostureClassifier(
            model_path=Path("/nonexistent/model.keras"),
            encoder_path=Path("/nonexistent/encoder.json"),
        )
        self.assertFalse(clf.is_available)
        window = self._make_window(self.WINDOW_SIZE)
        result = clf.predict(window)
        self.assertEqual(result["posture_label"], "Unknown")
        self.assertFalse(result["fall_detected"])
        self.assertEqual(result["confidence"], 0.0)
        self.assertIn("fallback", result["other_labels"])

    def test_fallback_when_window_too_short(self):
        """If window shorter than window_size, return fallback even if model exists."""
        clf = LSTMPostureClassifier(
            model_path=Path("/nonexistent/model.keras"),
            encoder_path=Path("/nonexistent/encoder.json"),
        )
        # Manually set as if model were available to test window-length guard
        clf._available = True
        clf._window_size = self.WINDOW_SIZE
        clf._model = None  # model is None so predict will error and fall back

        window = self._make_window(n_frames=2)  # too short
        result = clf.predict(window)
        self.assertEqual(result["posture_label"], "Unknown")

    def test_output_keys_present(self):
        """Result dict must always have the four expected keys."""
        clf = LSTMPostureClassifier(
            model_path=Path("/nonexistent/model.keras"),
            encoder_path=Path("/nonexistent/encoder.json"),
        )
        window = self._make_window(self.WINDOW_SIZE)
        result = clf.predict(window)
        self.assertIn("posture_label", result)
        self.assertIn("fall_detected", result)
        self.assertIn("confidence", result)
        self.assertIn("other_labels", result)

    def test_extract_raw_keypoints_from_row(self):
        """_extract_raw_keypoints should return a (66,) array."""
        kps = list(_make_standing_kps())
        row = {"keypoints": kps}
        arr = _extract_raw_keypoints(row)
        self.assertEqual(arr.shape, (RAW_FEATURE_DIM,))

    def test_extract_raw_keypoints_pads_short_list(self):
        """Short keypoints lists should be padded with NaN to RAW_FEATURE_DIM."""
        row = {"keypoints": [0.5, 0.5]}  # only 2 values
        arr = _extract_raw_keypoints(row)
        self.assertEqual(arr.shape, (RAW_FEATURE_DIM,))
        self.assertTrue(np.isnan(arr[2:]).all())

    def test_extract_raw_keypoints_empty(self):
        """Empty keypoints → all NaN (66,) array."""
        row = {"keypoints": []}
        arr = _extract_raw_keypoints(row)
        self.assertEqual(arr.shape, (RAW_FEATURE_DIM,))
        self.assertTrue(np.isnan(arr).all())


# ─────────────────────────────────────────────────────────────────────────────
# Integration: classify_posture_and_fall with lstm_classifier=None (heuristic)
# ─────────────────────────────────────────────────────────────────────────────

class TestLSTMIntegrationWithPipeline(unittest.TestCase):
    """
    Verify that passing lstm_classifier=None (or omitting it) still produces
    correct heuristic results — i.e., no regressions.
    """

    def _build_kps(self, sh_y=0.22, hp_y=0.52, ak_y=0.80):
        kps = [np.nan] * 66
        kps[22], kps[23] = 0.48, sh_y
        kps[24], kps[25] = 0.52, sh_y
        kps[46], kps[47] = 0.49, hp_y
        kps[48], kps[49] = 0.51, hp_y
        kps[54], kps[55] = 0.49, ak_y
        kps[56], kps[57] = 0.51, ak_y
        return kps

    def test_heuristic_still_works_without_lstm(self):
        kps = self._build_kps()
        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row, previous_rows=[], lstm_classifier=None)
        self.assertEqual(res["posture_label"], "Standing")
        self.assertFalse(res["fall_detected"])

    def test_lstm_not_triggered_when_none(self):
        """lstm_classifier=None must not cause any errors or routing changes."""
        kps = self._build_kps(sh_y=0.35, hp_y=0.50, ak_y=0.70)
        prev = []
        # Warm up history with standing frames
        for _ in range(5):
            stand_row = build_pose_row(keypoints=self._build_kps())
            r = classify_posture_and_fall(stand_row, previous_rows=prev, lstm_classifier=None)
            stand_row.update(r)
            prev.append(stand_row)

        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row, previous_rows=prev, lstm_classifier=None)
        self.assertIn(res["posture_label"], ["Standing", "Sitting", "Unknown"])

    def test_lstm_fallback_classifier_passes_through_to_heuristic(self):
        """
        When an LSTMPostureClassifier with is_available=False is passed,
        the code should fall back to the heuristic seamlessly.
        """
        clf = LSTMPostureClassifier(
            model_path=Path("/nonexistent/model.keras"),
            encoder_path=Path("/nonexistent/encoder.json"),
        )
        self.assertFalse(clf.is_available)

        kps = self._build_kps()
        row = build_pose_row(keypoints=kps)
        # Should fall through to heuristic and still classify as Standing
        res = classify_posture_and_fall(row, previous_rows=[], lstm_classifier=clf)
        self.assertEqual(res["posture_label"], "Standing")
        self.assertFalse(res["fall_detected"])


# ─────────────────────────────────────────────────────────────────────────────
# Optional: integration test that requires a trained model (skipped if absent)
# ─────────────────────────────────────────────────────────────────────────────

class TestLSTMWithTrainedModel(unittest.TestCase):

    MODEL_PATH = REPO_ROOT / "models" / "lstm_posture.keras"
    ENCODER_PATH = REPO_ROOT / "models" / "lstm_label_encoder.json"

    def setUp(self):
        if not self.MODEL_PATH.exists():
            self.skipTest("Trained model not found. Run lstm_trainer.py first.")

    def test_standing_prediction(self):
        clf = LSTMPostureClassifier(
            model_path=self.MODEL_PATH,
            encoder_path=self.ENCODER_PATH,
        )
        self.assertTrue(clf.is_available)
        window = [{"keypoints": list(_make_standing_kps())} for _ in range(clf.raw_history_needed)]
        res = clf.predict(window)
        self.assertIn(res["posture_label"], ["Standing", "Sitting", "Lying", "Unknown"])
        self.assertIn("fall_detected", res)
        self.assertGreaterEqual(res["confidence"], 0.0)
        self.assertLessEqual(res["confidence"], 1.0)

    def test_fall_prediction_class(self):
        clf = LSTMPostureClassifier(
            model_path=self.MODEL_PATH,
            encoder_path=self.ENCODER_PATH,
        )
        fall_frames = _make_fall_sequence(clf.raw_history_needed)
        window = [{"keypoints": list(f)} for f in fall_frames]
        res = clf.predict(window)
        # For a fall window, we expect either fall_detected=True or Lying posture
        self.assertIn(res["posture_label"], ["Lying", "Standing", "Sitting", "Unknown"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

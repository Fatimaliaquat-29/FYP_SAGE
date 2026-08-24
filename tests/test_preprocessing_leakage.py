"""
tests/test_preprocessing_leakage.py
====================================
Regression tests for the NaN-imputation preprocessing-leakage fix (this
audit session — see docs/RF_GENERALIZATION_INVESTIGATION.md's
"Preprocessing leakage" section for the full history).

Previously, `lstm_dataset.py::build_dataset()` imputed NaNs using
`col_medians` computed over the FULL real dataset (train + validation
combined) *before* any trainer's train/val split existed, so
validation-fold statistics leaked into how training-fold NaNs were
filled. The fix: `build_dataset()` now saves `X` raw (NaNs preserved),
and each trainer (lstm_trainer.py/tcn_trainer.py/rf_trainer.py) computes
`col_medians` from its OWN training fold only, after its own
StratifiedGroupKFold split, and imputes both folds with those
train-only statistics -- which are also what gets saved into the
model's encoder for inference.

No test anywhere previously verified that validation-fold data is
actually excluded from the imputation statistics used at training time
-- this file closes that gap.
"""

import sys
import unittest
import tempfile
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.lstm import lstm_features as lf


class ColMedianFoldIsolationTests(unittest.TestCase):
    """Deterministic, synthetic-data proof that compute_col_medians()/
    impute_nan() only ever see the fold they're given -- no dependence on
    values that exist solely in a different (e.g. validation) fold."""

    def test_train_only_median_ignores_validation_fold_values(self):
        # One feature column: every TRAIN row is NaN except a handful with
        # a known median of 1.0. Every VALIDATION row holds a wildly
        # different value (1000.0) that must NEVER influence the train-fold
        # median -- if it did, the leakage this fix closed would still be
        # present.
        col = 5
        X_train = np.zeros((20, 3, lf.FEATURE_DIM), dtype=np.float32)
        X_train[:, :, col] = np.nan
        X_train[0:6, 0, col] = 1.0  # real train-fold values, median 1.0

        X_val = np.zeros((10, 3, lf.FEATURE_DIM), dtype=np.float32)
        X_val[:, :, col] = 1000.0  # must not leak into the train median

        train_medians = lf.compute_col_medians(X_train)
        self.assertAlmostEqual(float(train_medians[col]), 1.0, places=5)

        # Sanity check the leak WOULD have shown up if computed the old
        # (pre-fix) way, over train+val combined -- proves this is a real,
        # sensitive test rather than one that would pass either way.
        combined_medians = lf.compute_col_medians(
            np.concatenate([X_train, X_val], axis=0))
        self.assertNotAlmostEqual(
            float(combined_medians[col]), 1.0, places=2,
            msg="Test is not sensitive: combined median should differ from "
                "the train-only median for this fixture, or this test can't "
                "actually detect a regression.")

    def test_impute_nan_with_train_medians_never_introduces_val_values(self):
        col = 7
        train_col_medians = np.zeros(lf.FEATURE_DIM, dtype=np.float32)
        train_col_medians[col] = -3.0  # a value that could only come from train

        X_val = np.full((4, 3, lf.FEATURE_DIM), np.nan, dtype=np.float32)
        imputed = lf.impute_nan(X_val, train_col_medians)
        self.assertTrue(np.all(imputed[:, :, col] == -3.0))


class TrainerLeakageIntegrationTests(unittest.TestCase):
    """Integration-level check against the real dataset and the real
    rf_trainer.train() entry point: confirms the checkpoint's saved
    col_medians actually equal medians computed from the training fold
    alone (reproduced independently here), and DIFFER from the
    whole-dataset diagnostic col_medians build_dataset() also saves --
    proving production training is not silently using the leaky
    whole-dataset statistic."""

    @classmethod
    def setUpClass(cls):
        cls.dataset_path = REPO_ROOT / "data" / "lstm_dataset.npz"
        if not cls.dataset_path.exists():
            raise unittest.SkipTest("data/lstm_dataset.npz not present in this checkout")

        data = np.load(str(cls.dataset_path), allow_pickle=True)
        if not np.isnan(data["X"]).any():
            raise unittest.SkipTest(
                "data/lstm_dataset.npz has no NaNs -- this checkout's dataset "
                "predates the raw-X leakage fix, so fold isolation can't be "
                "meaningfully exercised here.")

        from src.posture.rf.rf_trainer import train
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.model_path = Path(cls.tmpdir.name) / "rf_leakage_test.joblib"
        cls.encoder_path = Path(cls.tmpdir.name) / "rf_leakage_test_encoder.json"
        # n_estimators=5 -- this test only needs train() to run its data
        # loading/split/imputation path, not a well-trained model.
        train(model_out=cls.model_path, encoder_out=cls.encoder_path, n_estimators=5)

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def test_encoder_col_medians_match_independently_reproduced_train_fold_only(self):
        import json
        from sklearn.model_selection import StratifiedGroupKFold

        data = np.load(str(self.dataset_path), allow_pickle=True)
        X, y, groups = data["X"].astype(np.float32), data["y"].astype(np.int32), data["groups"]

        # Reproduce rf_trainer.train()'s exact split (same seed/scheme).
        n_splits = max(2, round(1.0 / 0.20))
        sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42)
        train_idx, _ = next(sgkf.split(X, y, groups))
        X_train = X[train_idx]

        expected_train_only_medians = lf.compute_col_medians(X_train)
        whole_dataset_medians = data["col_medians"].astype(np.float32)

        enc = json.loads(self.encoder_path.read_text(encoding="utf-8"))
        saved_medians = np.array(enc["col_medians"], dtype=np.float32)

        np.testing.assert_allclose(saved_medians, expected_train_only_medians, atol=1e-4)

        # The whole-dataset diagnostic value (saved by build_dataset(), see
        # its own docstring) must NOT be what got shipped in the encoder --
        # if it were, the fold-scoped fix would not actually be wired up in
        # rf_trainer.py despite the code claiming it is.
        self.assertFalse(
            np.allclose(saved_medians, whole_dataset_medians, atol=1e-4),
            msg="Encoder's col_medians match the whole-DATASET diagnostic "
                "value, not the train-fold-only value -- the leakage fix is "
                "not actually wired into rf_trainer.py.")


if __name__ == "__main__":
    unittest.main()

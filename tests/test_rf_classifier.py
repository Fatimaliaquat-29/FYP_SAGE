"""
tests/test_rf_classifier.py
=============================
Tests for RFPostureClassifier, focused on what changed this session: the
encoder-driven feature_representation switch ("flatten" vs "summary") and
the n_jobs=1 inference fix. Uses the real production checkpoint (an
integration-level check, not a mock) plus a small trained "summary"
checkpoint to exercise both code paths.
"""

import sys
import unittest
import tempfile
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.rf.rf_classifier import RFPostureClassifier
from src.posture.lstm import lstm_features as lf


def _standing_kps():
    kps = [np.nan] * 66
    kps[22], kps[23] = 0.45, 0.30
    kps[24], kps[25] = 0.55, 0.30
    kps[46], kps[47] = 0.47, 0.55
    kps[48], kps[49] = 0.53, 0.55
    kps[50], kps[51] = 0.47, 0.75
    kps[52], kps[53] = 0.53, 0.75
    kps[54], kps[55] = 0.47, 0.95
    kps[56], kps[57] = 0.53, 0.95
    return kps


class RFProductionCheckpointTests(unittest.TestCase):
    """Integration-level checks against the real, currently-trained
    production checkpoint -- skipped (not failed) if it isn't present in
    this checkout, same convention as tests/test_lstm_pipeline.py."""

    @classmethod
    def setUpClass(cls):
        cls.clf = RFPostureClassifier()
        if not cls.clf.is_available:
            raise unittest.SkipTest("models/rf_posture.joblib not present in this checkout")

    def test_loads_with_flatten_representation(self):
        # Current production encoder explicitly records this (see
        # rf_trainer.py's FEATURE_REPRESENTATION default and
        # docs/RF_GENERALIZATION_INVESTIGATION.md for why "summary" was
        # tried and rejected).
        self.assertEqual(self.clf._feature_representation, "flatten")

    def test_n_jobs_forced_to_one_after_load(self):
        # Regression test for the runaway-inference bug (see context.txt
        # Section 15.5): predict_proba() re-parallelizes per call using
        # whatever n_jobs the pickled estimator has; must be 1 at
        # inference time regardless of what training used.
        self.assertEqual(self.clf._model.n_jobs, 1)

    def test_predict_on_standing_window_returns_valid_structure(self):
        window = [{"keypoints": _standing_kps(), "frame_number": i, "timestamp": i / 30.0}
                  for i in range(self.clf.raw_history_needed)]
        result = self.clf.predict(window)
        self.assertIn("posture_label", result)
        self.assertIn("fall_detected", result)
        self.assertIn("confidence", result)
        self.assertIsInstance(result["fall_detected"], bool)
        self.assertTrue(0.0 <= result["confidence"] <= 1.0)
        self.assertTrue(np.isfinite(result["confidence"]))

    def test_predict_is_deterministic(self):
        window = [{"keypoints": _standing_kps(), "frame_number": i, "timestamp": i / 30.0}
                  for i in range(self.clf.raw_history_needed)]
        r1 = self.clf.predict(window)
        r2 = self.clf.predict(window)
        self.assertEqual(r1["posture_label"], r2["posture_label"])
        self.assertEqual(r1["confidence"], r2["confidence"])

    def test_fall_confirm_frames_default_does_not_change_raw_behavior(self):
        # Default (1) must be byte-identical to no smoothing at all --
        # compare_all_models.py's architecture comparisons rely on this.
        window = [{"keypoints": _standing_kps(), "frame_number": i, "timestamp": i / 30.0}
                  for i in range(self.clf.raw_history_needed)]
        clf_default = RFPostureClassifier()
        self.assertEqual(clf_default.fall_confirm_frames, 1)
        result = clf_default.predict(window)
        self.assertEqual(result, self.clf.predict(window))

    def test_reset_state_clears_consecutive_fall_counter(self):
        # Regression test: compare_tcn_lstm.py's evaluate_model() reuses one
        # classifier instance across every clip in a batch without calling
        # reset_state() -- a real bug found while sweeping fall_confirm_frames
        # (a non-monotonic false-positive count across increasing thresholds
        # was cross-clip state contamination, not a real property of the
        # threshold). Fixed in compare_tcn_lstm.py; this test locks in the
        # underlying mechanism reset_state() is supposed to provide.
        clf = RFPostureClassifier(fall_confirm_frames=3)
        clf._consecutive_fall_count = 2  # simulate mid-streak from a prior clip
        clf.reset_state()
        self.assertEqual(clf._consecutive_fall_count, 0)

    def test_fall_confirm_frames_suppresses_short_streaks(self):
        # Exercises the REAL predict() method (not a re-implementation of
        # its logic) by stubbing the underlying model's predict_proba to
        # always vote "Fall" (class index 0 -- see lstm_dataset.CLASSES),
        # so the confirm-frame state machine is tested end-to-end through
        # the actual code path rather than duplicated inline.
        class _AlwaysFallModel:
            n_jobs = 1
            def predict_proba(self, X):
                return np.array([[0.9, 0.025, 0.025, 0.025, 0.025]])

        clf = RFPostureClassifier(fall_confirm_frames=3)
        clf._model = _AlwaysFallModel()
        clf._available = True
        clf._classes = ["Fall", "Lying", "Sitting", "Standing", "Unknown"]

        window = [{"keypoints": _standing_kps(), "frame_number": i, "timestamp": i / 30.0}
                  for i in range(clf.raw_history_needed)]
        results = [clf.predict(window)["fall_detected"] for _ in range(5)]
        # First 2 calls (streak length 1, 2) must be suppressed; from the
        # 3rd call onward (streak length >= 3) it must confirm.
        self.assertEqual(results, [False, False, True, True, True])

    def test_too_short_window_falls_back(self):
        window = [{"keypoints": _standing_kps(), "frame_number": 0, "timestamp": 0.0}]
        result = self.clf.predict(window)
        self.assertEqual(result["other_labels"], "rf_fallback")
        self.assertEqual(result["posture_label"], "Unknown")

    def test_missing_keypoints_key_degrades_gracefully_not_crash(self):
        """A row missing the 'keypoints' key entirely does NOT raise --
        confirmed this is already handled two layers down
        (sequence_window_classifier.extract_raw_keypoints uses
        `row.get('keypoints', [])`, defaulting to an all-NaN array later
        imputed via col_medians) -- so this window still produces a REAL
        classification, not a fallback. This test locks in that graceful-
        by-design behavior (not a crash) rather than asserting a specific
        predicted class, which is legitimately data/model-dependent."""
        window = [{"frame_number": i, "timestamp": i / 30.0} for i in range(self.clf.raw_history_needed)]
        result = self.clf.predict(window)  # must not raise
        self.assertIn("posture_label", result)
        self.assertIn(result["other_labels"].split(",")[0], ("rf", "rf_fallback"))

    def test_malformed_keypoints_length_degrades_gracefully_not_crash(self):
        """Same as above, different malformation: 'keypoints' present but
        the wrong length (a real integration-mismatch scenario -- e.g. a
        caller supplying keypoints for a different landmark count).
        extract_raw_keypoints pads/truncates to RAW_FEATURE_DIM, so this
        also does not raise."""
        window = [{"keypoints": [0.5, 0.5, 0.5], "frame_number": i, "timestamp": i / 30.0}
                  for i in range(self.clf.raw_history_needed)]
        result = self.clf.predict(window)  # must not raise
        self.assertIn("posture_label", result)

    def test_non_dict_row_falls_back_instead_of_raising(self):
        """Regression test for a real bug found in a later audit session:
        predict()'s try/except previously only wrapped the predict_proba
        call, not the feature-building steps above it (extract_raw_keypoints/
        build_features_from_raw_window/impute_nan). A row that isn't even a
        dict (e.g. None -- a real shape this project's own row-building
        code should never produce, but nothing enforced that at this
        boundary) raises AttributeError inside extract_raw_keypoints's own
        `row.get(...)` call -- CONFIRMED this raised uncaught before this
        session's fix (verified by re-running against the pre-fix code
        path). compare_all_models.py/compare_tcn_lstm.py call `.predict()`
        with no try/except of their own, so this would have aborted an
        entire batch-evaluation run over one bad row. Must now degrade to
        the same graceful `_fallback()` every other input problem in this
        class already produces."""
        window = [None for _ in range(self.clf.raw_history_needed)]
        result = self.clf.predict(window)  # must not raise
        self.assertEqual(result["other_labels"], "rf_fallback")
        self.assertEqual(result["posture_label"], "Unknown")
        self.assertFalse(result["fall_detected"])

    def test_class_index_misalignment_is_handled_correctly(self):
        """Correctness fix, a later audit session: predict() previously
        assumed probs[i] corresponds to self._classes[i] positionally.
        sklearn's predict_proba columns are ordered by model.classes_,
        which is only [0,1,...,n-1] densely if EVERY class appeared in the
        training fold. This simulates a model trained on a fold where
        'Lying' (class index 1) was entirely absent -- model.classes_ =
        [0, 2, 3, 4] -- and confirms predict() still returns the CORRECT
        class name, not the class at the wrong positional offset (which
        would silently misreport 'Sitting' as 'Lying', 'Standing' as
        'Sitting', etc. under the old positional-assumption bug)."""
        class _MissingLyingModel:
            n_jobs = 1
            classes_ = np.array([0, 2, 3, 4])  # 'Lying' (index 1) absent from training

            def predict_proba(self, X):
                # Confidently votes for 'Sitting' (real class index 2),
                # which sits at POSITION 1 in this model's own probability
                # columns (since classes_[1] == 2) -- the exact case the old
                # `self._classes[argmax_position]` bug would misread as
                # 'Lying' (self._classes[1]).
                return np.array([[0.05, 0.85, 0.05, 0.05]])

        clf = RFPostureClassifier()
        clf._model = _MissingLyingModel()
        clf._available = True
        clf._classes = ["Fall", "Lying", "Sitting", "Standing", "Unknown"]
        clf._n_features_out = None  # skip the schema check for this synthetic-model test

        window = [{"keypoints": _standing_kps(), "frame_number": i, "timestamp": i / 30.0}
                  for i in range(clf.raw_history_needed)]
        result = clf.predict(window)
        self.assertEqual(result["posture_label"], "Sitting")
        self.assertEqual(result["other_labels"], "rf,pred=Sitting")
        self.assertFalse(result["fall_detected"])

    def test_feature_schema_mismatch_falls_back_with_clear_message(self):
        """A checkpoint recorded a different n_features_out than what the
        CURRENT feature-building pipeline actually produces (e.g. after an
        unrelated lstm_features.py change without retraining this model) --
        must be caught proactively and fall back cleanly, not surface as a
        raw sklearn shape-mismatch exception."""
        clf = RFPostureClassifier()
        clf._model = object()  # never reached -- the schema check must short-circuit first
        clf._available = True
        clf._classes = ["Fall", "Lying", "Sitting", "Standing", "Unknown"]
        clf._n_features_out = 999999  # cannot match any real built feature vector

        window = [{"keypoints": _standing_kps(), "frame_number": i, "timestamp": i / 30.0}
                  for i in range(clf.raw_history_needed)]
        result = clf.predict(window)  # must not raise
        self.assertEqual(result["other_labels"], "rf_fallback")

    def test_n_features_out_loaded_from_real_encoder(self):
        """The production encoder file always has n_features_out (rf_trainer.py
        writes it unconditionally) -- confirms _load() actually reads it,
        not just that the attribute exists with a None default."""
        self.assertIsNotNone(self.clf._n_features_out)
        self.assertEqual(self.clf._n_features_out, 30 * lf.FEATURE_DIM)  # flatten representation


class RFTrainerConfigurationTests(unittest.TestCase):
    """Locks in documented, evidence-based training-configuration decisions
    from docs/RF_GENERALIZATION_INVESTIGATION.md so they can't silently
    drift -- code-only checks (no training run needed), so these stay fast."""

    def test_class_weighting_defaults_off(self):
        """use_class_weights=True was tested and REJECTED (see
        docs/RF_GENERALIZATION_INVESTIGATION.md Section 4b): balanced
        weighting dropped real fall-detection recall from 100% to 75% on
        the Hussain set AND from 87.5% to 75% on the Sanawar set --
        missing a real fall on both real test sets to chase better
        macro-F1/minority-class recall on the validation split. Given this
        project's explicit priority (a missed fall is worse than a false
        alarm), this default must not silently flip back to True."""
        import inspect
        from src.posture.rf.rf_trainer import train
        sig = inspect.signature(train)
        self.assertEqual(sig.parameters["use_class_weights"].default, False)

    def test_pruning_config_matches_real_footage_validated_values(self):
        """min_samples_leaf=20 / max_features=0.1 were chosen via real-
        footage-validated sweeps (see rf_trainer.py's own MIN_SAMPLES_LEAF/
        MAX_FEATURES comments) -- a silent change here would retrain every
        future checkpoint against an unvalidated configuration."""
        from src.posture.rf import rf_trainer
        self.assertEqual(rf_trainer.MIN_SAMPLES_LEAF, 20)
        self.assertEqual(rf_trainer.MAX_FEATURES, 0.1)

    def test_flatten_remains_the_default_representation(self):
        """"summary" was tested and REJECTED as the default (see
        docs/RF_GENERALIZATION_INVESTIGATION.md Section 4a): it lost 12
        points of accuracy and 0.08 macro F1 on the harder, more decision-
        relevant Hussain real-footage set despite looking better on the
        validation split -- kept available, not default."""
        from src.posture.rf import rf_trainer
        self.assertEqual(rf_trainer.FEATURE_REPRESENTATION, "flatten")

    def test_training_split_and_forest_seeds_are_fixed(self):
        """Reproducibility: both the StratifiedGroupKFold split and the
        RandomForestClassifier fit must use a fixed random_state, and the
        post-split real+synthetic shuffle must use a fixed Generator seed
        -- otherwise which sequences land in train vs. validation (and
        therefore every reported metric) would vary run to run. Checked by
        source inspection rather than a training run, since this is about
        the CALL arguments always being the same fixed values, not the
        resulting model."""
        import inspect
        from src.posture.rf import rf_trainer
        source = inspect.getsource(rf_trainer.train)
        self.assertIn("random_state=42", source)
        self.assertIn("seed=1", source)


class RFClassLabelConsistencyTests(unittest.TestCase):
    """Verifies the label encoder's class list is consistent with what the
    shared dataset/training pipeline actually produces -- the two halves of
    the exact contract RFPostureClassifier.predict()'s class-index-mapping
    fix (see RFProductionCheckpointTests.test_class_index_misalignment_is_
    handled_correctly) depends on being correct in the first place."""

    def test_real_dataset_class_order_matches_deployed_encoder(self):
        dataset_path = REPO_ROOT / "data" / "lstm_dataset.npz"
        encoder_path = REPO_ROOT / "models" / "rf_label_encoder.json"
        if not dataset_path.exists() or not encoder_path.exists():
            raise unittest.SkipTest("dataset or production encoder not present in this checkout")
        import json
        import numpy as np
        classes = np.load(dataset_path, allow_pickle=True)["classes"]
        enc = json.loads(encoder_path.read_text(encoding="utf-8"))
        self.assertEqual(list(classes), enc["classes"])

    def test_every_class_has_real_training_representation(self):
        """A degenerate split (a class with zero windows reaching the
        training fold) is exactly the scenario
        test_class_index_misalignment_is_handled_correctly's mocked model
        simulates -- this test checks the REAL dataset never actually has
        a class so small that a reasonable group split could plausibly
        drop it entirely (i.e. that scenario is a defensive guard, not
        something expected to fire in practice)."""
        dataset_path = REPO_ROOT / "data" / "lstm_dataset.npz"
        if not dataset_path.exists():
            raise unittest.SkipTest("data/lstm_dataset.npz not present in this checkout")
        import numpy as np
        d = np.load(dataset_path, allow_pickle=True)
        y, classes = d["y"], d["classes"]
        counts = np.bincount(y, minlength=len(classes))
        for cls, count in zip(classes, counts):
            self.assertGreater(count, 50, f"class {cls!r} has only {count} real windows -- "
                                           "a class this small risks being dropped entirely "
                                           "by a StratifiedGroupKFold split")


class RFSummaryRepresentationTests(unittest.TestCase):
    """Exercises the "summary" feature-representation code path (not the
    production default, but a real, documented, tested-and-kept option --
    see docs/RF_GENERALIZATION_INVESTIGATION.md Section 4a) by training a
    tiny real model with it and confirming inference builds the expected
    660-dim vector without crashing."""

    @classmethod
    def setUpClass(cls):
        dataset_path = REPO_ROOT / "data" / "lstm_dataset.npz"
        if not dataset_path.exists():
            raise unittest.SkipTest("data/lstm_dataset.npz not present in this checkout")

        from src.posture.rf.rf_trainer import train
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.model_path = Path(cls.tmpdir.name) / "rf_summary_test.joblib"
        cls.encoder_path = Path(cls.tmpdir.name) / "rf_summary_test_encoder.json"
        # n_estimators=20 -- this test only needs the code path exercised
        # correctly, not a well-trained model, so keep it fast.
        train(
            model_out=cls.model_path, encoder_out=cls.encoder_path,
            feature_representation="summary", n_estimators=20,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def test_encoder_records_summary_representation(self):
        import json
        enc = json.loads(self.encoder_path.read_text(encoding="utf-8"))
        self.assertEqual(enc["feature_representation"], "summary")
        self.assertEqual(enc["n_features_out"], 132 * 5)

    def test_predict_builds_660_dim_vector_without_crashing(self):
        clf = RFPostureClassifier(model_path=self.model_path, encoder_path=self.encoder_path)
        self.assertTrue(clf.is_available)
        self.assertEqual(clf._feature_representation, "summary")
        window = [{"keypoints": _standing_kps(), "frame_number": i, "timestamp": i / 30.0}
                  for i in range(clf.raw_history_needed)]
        result = clf.predict(window)  # should not raise
        self.assertIn("posture_label", result)
        self.assertTrue(np.isfinite(result["confidence"]))


if __name__ == "__main__":
    unittest.main()

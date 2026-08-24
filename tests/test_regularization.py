"""
tests/test_regularization.py
=============================
Experimental verification that L1/L2 weight regularization (TCN's default
L2=1e-5, LSTM's opt-in l1/l2 params) is actually wired into the real model
graph and actually contributes to the compiled loss Keras optimizes --
not just present as configuration variables in source code.

Background (a later audit session): the user asked this be verified
experimentally rather than assumed from reading source. This file locks
those experiments in as permanent regression tests, covering: regularizer
objects are attached to the intended layers only, zero coefficients
produce zero regularizer objects (not zero-valued ones -- byte-identical
graphs for existing callers), the regularization loss value scales
linearly with the coefficient, and it is genuinely included in
model.evaluate()'s reported loss (the same code path model.fit() trains
against), not merely present as inert metadata.
"""

import sys
import unittest
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TCNRegularizationTests(unittest.TestCase):
    """TCN's default L2=1e-5 (see tcn_model.py's own docstring for the
    sweep that chose it) is production-active -- these tests verify it on
    the real default, not just a synthetic on/off toggle."""

    @classmethod
    def setUpClass(cls):
        import tensorflow as tf
        cls.tf = tf

    def test_default_l2_attaches_regularizer_to_every_conv_and_dense_layer(self):
        from src.posture.tcn.tcn_model import build_tcn_model, L2_REG, L1_REG
        self.assertGreater(L2_REG, 0.0, "TCN's production default must be non-zero for this test to be meaningful")
        m = build_tcn_model(30, 132, 5)  # uses module defaults
        regularized_layers = [l.name for l in m.layers if getattr(l, "kernel_regularizer", None) is not None]
        # 4 residual blocks x 2 convs + 1 projection (channel count changes on block 0) + 1 output dense.
        expected_min = 4 * 2 + 1  # at least the 8 block convs + output dense
        self.assertGreaterEqual(len(regularized_layers), expected_min)
        for name in regularized_layers:
            layer = m.get_layer(name)
            cfg = layer.kernel_regularizer.get_config()
            self.assertAlmostEqual(cfg["l2"], L2_REG)
            self.assertAlmostEqual(cfg["l1"], L1_REG)

    def test_zero_coefficients_produce_no_regularizer_object_at_all(self):
        from src.posture.tcn.tcn_model import build_tcn_model
        m = build_tcn_model(30, 132, 5, l1=0.0, l2=0.0)
        self.assertEqual(len(m.losses), 0)
        for layer in m.layers:
            self.assertIsNone(getattr(layer, "kernel_regularizer", None))

    def test_regularization_loss_scales_linearly_with_coefficient(self):
        from src.posture.tcn.tcn_model import build_tcn_model
        X = np.random.RandomState(0).randn(4, 30, 132).astype("float32")

        vals = {}
        for l2 in (1e-5, 1e-3):
            self.tf.keras.utils.set_random_seed(42)
            m = build_tcn_model(30, 132, 5, l2=l2)
            _ = m(X, training=True)  # populate m.losses with real scalar values at current weights
            vals[l2] = float(sum(float(l) for l in m.losses))

        self.assertGreater(vals[1e-5], 0.0)
        self.assertGreater(vals[1e-3], 0.0)
        # 100x the coefficient (same weights, fixed seed) -> ~100x the loss.
        ratio = vals[1e-3] / vals[1e-5]
        self.assertAlmostEqual(ratio, 100.0, delta=1.0)

    def test_regularization_penalty_is_included_in_the_actual_optimized_loss(self):
        """Not just model.losses metadata -- model.evaluate() (same compiled
        loss computation model.fit() optimizes) must report a higher total
        loss when regularization is on, for identical weights/data/labels."""
        from src.posture.tcn.tcn_model import build_tcn_model
        X = np.random.RandomState(0).randn(8, 30, 132).astype("float32")
        y = np.random.RandomState(1).randint(0, 5, size=8).astype("int32")

        losses = {}
        for l2 in (0.0, 1e-2):
            self.tf.keras.utils.set_random_seed(42)  # identical initial weights each time
            m = build_tcn_model(30, 132, 5, l2=l2)
            losses[l2] = m.evaluate(X, y, verbose=0)[0]

        self.assertGreater(losses[1e-2], losses[0.0],
                            "L2 regularization is not contributing to the compiled loss")


class LSTMRegularizationTests(unittest.TestCase):
    """LSTM's l1/l2 defaulted to 0.0 in BOTH build_model() and train() until
    a later audit session: the production LSTM originally shipped with NO
    weight regularization (unlike the TCN), a real, documented, but never
    separately validated difference. A 4-config sweep on the validation
    split, independently confirmed (not re-tuned) on both real-footage test
    sets, found l2=1e-5 -- the same value already used by the TCN -- a
    clean improvement with no trade-off (see lstm_trainer.py's own L2_REG
    comment for the full evidence). The production default is now
    genuinely L2_REG=1e-5, not zero; these tests confirm that IS what's
    active by default, and that the mechanism still works correctly when a
    caller opts for a different value."""

    def test_production_default_is_l2_reg_not_zero(self):
        from src.posture.lstm.lstm_trainer import build_model, L1_REG, L2_REG
        self.assertGreater(L2_REG, 0.0, "Production default must be non-zero for this test to be meaningful")
        m = build_model(30, 132, 5)  # no l1/l2 passed -> module defaults (L1_REG, L2_REG)
        lstm_layers = [l for l in m.layers if l.__class__.__name__ == "LSTM"]
        self.assertEqual(len(lstm_layers), 2)
        for layer in lstm_layers:
            self.assertIsNotNone(layer.kernel_regularizer)
            self.assertIsNotNone(layer.recurrent_regularizer)
            self.assertAlmostEqual(layer.kernel_regularizer.get_config()["l2"], L2_REG)
            self.assertAlmostEqual(layer.kernel_regularizer.get_config()["l1"], L1_REG)

    def test_zero_coefficients_produce_no_regularizer_object_at_all(self):
        from src.posture.lstm.lstm_trainer import build_model
        m = build_model(30, 132, 5, l1=0.0, l2=0.0)
        self.assertEqual(len(m.losses), 0)
        for layer in m.layers:
            self.assertIsNone(getattr(layer, "kernel_regularizer", None))
            self.assertIsNone(getattr(layer, "recurrent_regularizer", None))

    def test_opting_in_attaches_kernel_and_recurrent_regularizers_to_both_lstm_layers(self):
        from src.posture.lstm.lstm_trainer import build_model
        m = build_model(30, 132, 5, l1=1e-4, l2=1e-3)
        lstm_layers = [l for l in m.layers if l.__class__.__name__ == "LSTM"]
        self.assertEqual(len(lstm_layers), 2)
        for layer in lstm_layers:
            self.assertIsNotNone(layer.kernel_regularizer)
            self.assertIsNotNone(layer.recurrent_regularizer)
            self.assertAlmostEqual(layer.kernel_regularizer.get_config()["l1"], 1e-4)
            self.assertAlmostEqual(layer.kernel_regularizer.get_config()["l2"], 1e-3)
        dense = m.get_layer("dense" if "dense" in [l.name for l in m.layers] else m.layers[-1].name)
        self.assertIsNotNone(dense.kernel_regularizer)


if __name__ == "__main__":
    unittest.main()

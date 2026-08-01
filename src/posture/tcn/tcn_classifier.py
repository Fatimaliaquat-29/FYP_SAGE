"""
tcn_classifier.py
==================
Inference module for the trained TCN posture classifier.

Provides:
    TCNPostureClassifier – class with a rolling window buffer and predict()
    classify_with_tcn()  – convenience function matching the existing
                           classify_posture_and_fall() return signature

Its public interface (.predict(), .window_size, .raw_history_needed,
.is_available) is intentionally identical to LSTMPostureClassifier
(src/posture/lstm/lstm_classifier.py) so it can act as a drop-in replacement
anywhere the LSTM classifier is used.

Usage (demo):
    python src/posture/tcn/tcn_classifier.py --demo
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.lstm import lstm_features as lf

MODELS_DIR = REPO_ROOT / "models"
TCN_MODEL_PATH = MODELS_DIR / "tcn_posture.keras"
TCN_ENCODER_PATH = MODELS_DIR / "tcn_label_encoder.json"

LANDMARK_COUNT = 33
RAW_FEATURE_DIM = LANDMARK_COUNT * 2  # 66: raw x/y landmark coordinates
FEATURE_DIM = lf.FEATURE_DIM           # 132: normalized position + velocity (model input)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_raw_keypoints(row: dict) -> np.ndarray:
    """
    Extract a (66,) float array of x/y landmark coordinates from a pose row dict.

    The row must contain a 'keypoints' key whose value is a flat list of
    [x1, y1, x2, y2, ..., x33, y33] floats (as produced by build_pose_row).
    Missing / NaN values are preserved and later imputed by the classifier.
    """
    kps = row.get("keypoints", [])
    arr = np.array(kps, dtype=np.float32)
    if len(arr) < RAW_FEATURE_DIM:
        arr = np.concatenate([arr, np.full(RAW_FEATURE_DIM - len(arr), np.nan, dtype=np.float32)])
    return arr[:RAW_FEATURE_DIM]


# ---------------------------------------------------------------------------
# Main classifier class
# ---------------------------------------------------------------------------

class TCNPostureClassifier:
    """
    Real-time posture classifier backed by a trained Keras TCN model.

    Parameters
    ----------
    model_path : Path, optional
        Path to the saved .keras model file. Defaults to
        models/tcn_posture.keras in the repository root.
    encoder_path : Path, optional
        Path to the label encoder JSON. Defaults to
        models/tcn_label_encoder.json.

    Usage
    -----
    clf = TCNPostureClassifier()
    result = clf.predict(window_rows)
    # result → {"posture_label": "Standing", "fall_detected": False,
    #            "confidence": 0.94, "other_labels": "tcn"}
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None,
    ):
        self.model_path = Path(model_path or TCN_MODEL_PATH)
        self.encoder_path = Path(encoder_path or TCN_ENCODER_PATH)

        self._model = None
        self._classes: List[str] = ["Fall", "Lying", "Sitting", "Standing", "Unknown"]
        self._window_size: int = 30
        self._n_features: int = FEATURE_DIM
        self._col_medians: Optional[np.ndarray] = None
        self._available: bool = False

        self._load()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load(self):
        """Attempt to load model and encoder. Sets self._available = True on success."""
        # Load label encoder
        if self.encoder_path.exists():
            try:
                enc = json.loads(self.encoder_path.read_text(encoding="utf-8"))
                self._classes = enc.get("classes", self._classes)
                self._window_size = int(enc.get("window_size", self._window_size))
                self._n_features = int(enc.get("n_features", self._n_features))
                col_medians = enc.get("col_medians")
                if col_medians is not None:
                    self._col_medians = np.array(col_medians, dtype=np.float32)
            except Exception as e:
                print(f"[TCNClassifier] Warning: could not load encoder: {e}")

        # Load Keras model
        if not self.model_path.exists():
            print(
                f"[TCNClassifier] Model not found at {self.model_path}. "
                "Run tcn_trainer.py first. Falling back to Unknown."
            )
            return

        try:
            import tensorflow as tf
            self._model = tf.keras.models.load_model(str(self.model_path))
            self._available = True
            print(f"[TCNClassifier] Loaded model from {self.model_path}")
        except ImportError:
            print(
                "[TCNClassifier] TensorFlow not installed. "
                "Install with: pip install tensorflow-cpu"
            )
        except Exception as e:
            print(f"[TCNClassifier] Failed to load model: {e}")

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def window_size(self) -> int:
        return self._window_size

    @property
    def raw_history_needed(self) -> int:
        """
        Number of raw pose rows the caller must supply to predict(): one more
        than window_size, because computing a real (not zero-padded) velocity
        for the oldest row in the model's window requires the frame just
        before it. Identical requirement to LSTMPostureClassifier since both
        consume the same lstm_features windowing.
        """
        return self._window_size + 1

    @property
    def is_available(self) -> bool:
        """True when the model loaded successfully and inference is possible."""
        return self._available

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict(self, window: List[dict]) -> dict:
        """
        Classify posture from a sliding window of pose row dicts.

        Parameters
        ----------
        window : list of dict
            Each dict must have a 'keypoints' key (flat list of 66 floats)
            as produced by pipeline_utils.build_pose_row().
            Length must be >= self.raw_history_needed (window_size + 1);
            only the last raw_history_needed rows are used. The extra
            leading row is consumed to compute a genuine velocity for the
            first frame of the model's window (see lstm_features.py).

        Returns
        -------
        dict with keys:
            posture_label  str   – "Standing" | "Sitting" | "Lying" | "Unknown"
            fall_detected  bool  – True when TCN predicts "Fall" class
            confidence     float – max softmax probability
            other_labels   str   – "tcn" or "tcn_fallback"
        """
        if not self._available or self._model is None:
            return self._fallback()

        if len(window) < self.raw_history_needed:
            return self._fallback()

        # Use the last raw_history_needed raw frames (window_size + 1)
        recent = window[-self.raw_history_needed:]

        # Raw (window_size+1, 66) -> normalized position + velocity (window_size, 132)
        raw = np.stack([_extract_raw_keypoints(r) for r in recent], axis=0)
        frames = lf.build_features_from_raw_window(raw)
        frames = lf.impute_nan(frames, self._col_medians)

        # Model expects (batch, window_size, n_features)
        X = frames[np.newaxis, ...].astype(np.float32)  # (1, window_size, 132)

        try:
            probs = self._model.predict(X, verbose=0)[0]  # (n_classes,)
        except Exception as e:
            print(f"[TCNClassifier] Prediction error: {e}")
            return self._fallback()

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        pred_class = self._classes[pred_idx] if pred_idx < len(self._classes) else "Unknown"

        fall_detected = pred_class == "Fall"
        # Map "Fall" → "Lying" for posture_label (fall is a sub-event of lying)
        posture_label = "Lying" if fall_detected else pred_class

        return {
            "posture_label": posture_label,
            "fall_detected": fall_detected,
            "confidence": round(confidence, 3),
            "other_labels": f"tcn,pred={pred_class}",
        }

    @staticmethod
    def _fallback() -> dict:
        return {
            "posture_label": "Unknown",
            "fall_detected": False,
            "confidence": 0.0,
            "other_labels": "tcn_fallback",
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def classify_with_tcn(
    window: List[dict],
    classifier: Optional[TCNPostureClassifier] = None,
    model_path: Optional[Path] = None,
) -> dict:
    """
    Convenience wrapper that classifies a window of pose rows using the TCN.

    Parameters
    ----------
    window : list of pose row dicts (each with 'keypoints')
    classifier : TCNPostureClassifier, optional
        Pass a pre-loaded classifier to avoid reloading the model every call.
    model_path : Path, optional
        Override model path (used if classifier is None).

    Returns
    -------
    Same dict format as pipeline_utils.classify_posture_and_fall().
    """
    if classifier is None:
        classifier = TCNPostureClassifier(model_path=model_path)
    return classifier.predict(window)


# ---------------------------------------------------------------------------
# Demo / CLI
# ---------------------------------------------------------------------------

def _run_demo():
    """Quick smoke test using synthetic standing and fall windows."""
    from src.posture.lstm.lstm_dataset import (
        _make_standing_kps,
        _make_fall_sequence,
    )

    clf = TCNPostureClassifier()
    n = clf.raw_history_needed  # window_size + 1 raw frames

    if not clf.is_available:
        print("\n[demo] Model not available. Run tcn_trainer.py first.")
        print("[demo] Showing fallback output:")
        window = [{"keypoints": list(_make_standing_kps())} for _ in range(n)]
        print(" ", clf.predict(window))
        return

    print(f"\n[demo] window_size={clf.window_size}, n_features={clf._n_features}")

    # Standing window
    window_stand = [{"keypoints": list(_make_standing_kps())} for _ in range(n)]
    res = clf.predict(window_stand)
    print(f"  Standing window → {res}")

    # Fall window (transition from standing to lying)
    fall_frames = _make_fall_sequence(n)
    window_fall = [{"keypoints": list(f)} for f in fall_frames]
    res = clf.predict(window_fall)
    print(f"  Fall    window → {res}")


def main():
    parser = argparse.ArgumentParser(description="TCN Posture Classifier")
    parser.add_argument("--demo", action="store_true", help="Run demo inference on synthetic windows")
    parser.add_argument("--model", type=str, default=None, help="Path to .keras model file")
    args = parser.parse_args()

    if args.demo:
        _run_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

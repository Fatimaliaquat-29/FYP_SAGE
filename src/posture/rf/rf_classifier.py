"""
rf_classifier.py
=================
Inference module for the trained Random Forest posture classifier.

Provides:
    RFPostureClassifier – class with a rolling window buffer and predict(),
                          with the same public interface as
                          LSTMPostureClassifier/TCNPostureClassifier
                          (.predict(), .window_size, .raw_history_needed,
                          .is_available), so it is a drop-in replacement
                          anywhere either of those is used (see
                          compare_tcn_lstm.py's use of that shared shape).

Unlike LSTMPostureClassifier/TCNPostureClassifier, this does NOT subclass
SequenceWindowClassifier -- that base class assumes a Keras model loaded via
tf.keras.models.load_model(); a Random Forest is loaded via joblib and takes
a single flattened feature vector rather than a (window_size, n_features)
tensor. The windowing/feature-extraction logic (extract_raw_keypoints,
lstm_features normalization + velocity + imputation) is reused as-is from
sequence_window_classifier.py rather than reimplemented.

Usage (demo):
    python src/posture/rf/rf_classifier.py --demo
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
from src.posture.sequence_window_classifier import extract_raw_keypoints, run_classifier_demo

MODELS_DIR = REPO_ROOT / "models"
RF_MODEL_PATH = MODELS_DIR / "rf_posture.joblib"
RF_ENCODER_PATH = MODELS_DIR / "rf_label_encoder.json"


class RFPostureClassifier:
    """
    Real-time posture classifier backed by a trained scikit-learn
    RandomForestClassifier. Consumes the same rolling window of
    normalized-position-plus-velocity features as the LSTM/TCN (see
    lstm_features.py) but flattens the window into a single feature vector
    before calling predict_proba, since a Random Forest has no notion of a
    time axis.

    Usage
    -----
    clf = RFPostureClassifier()
    result = clf.predict(window_rows)
    # result -> {"posture_label": "Standing", "fall_detected": False,
    #            "confidence": 0.94, "other_labels": "rf,pred=Standing"}
    """

    DEFAULT_MODEL_PATH = RF_MODEL_PATH
    DEFAULT_ENCODER_PATH = RF_ENCODER_PATH
    LABEL_TAG = "rf"

    def __init__(self, model_path: Optional[Path] = None, encoder_path: Optional[Path] = None):
        self.model_path = Path(model_path or self.DEFAULT_MODEL_PATH)
        self.encoder_path = Path(encoder_path or self.DEFAULT_ENCODER_PATH)

        self._model = None
        self._classes: List[str] = ["Fall", "Lying", "Sitting", "Standing", "Unknown"]
        self._window_size: int = 30
        self._n_features: int = lf.FEATURE_DIM
        self._col_medians: Optional[np.ndarray] = None
        self._available: bool = False

        self._load()

    def _load(self) -> None:
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
                print(f"[RFClassifier] Warning: could not load encoder: {e}")

        if not self.model_path.exists():
            print(
                f"[RFClassifier] Model not found at {self.model_path}. "
                "Run rf_trainer.py first. Falling back to Unknown."
            )
            return

        try:
            import joblib
            self._model = joblib.load(str(self.model_path))
            self._available = True
            print(f"[RFClassifier] Loaded model from {self.model_path}")
        except ImportError:
            print("[RFClassifier] joblib not installed. Install with: pip install joblib")
        except Exception as e:
            print(f"[RFClassifier] Failed to load model: {e}")

    @property
    def window_size(self) -> int:
        return self._window_size

    @property
    def raw_history_needed(self) -> int:
        """One more than window_size -- same rationale as
        SequenceWindowClassifier.raw_history_needed: computing a real
        velocity for the oldest row of the window needs the frame before it."""
        return self._window_size + 1

    @property
    def is_available(self) -> bool:
        return self._available

    def predict(self, window: List[dict]) -> dict:
        """
        Classify posture from a sliding window of pose row dicts. Same
        contract as SequenceWindowClassifier.predict() (see that module for
        the full docstring) -- the only difference is the (window_size,
        n_features) feature tensor gets flattened to a single
        (window_size * n_features,) vector before calling predict_proba.
        """
        if not self._available or self._model is None:
            return self._fallback()

        if len(window) < self.raw_history_needed:
            return self._fallback()

        recent = window[-self.raw_history_needed:]
        raw = np.stack([extract_raw_keypoints(r) for r in recent], axis=0)
        frames = lf.build_features_from_raw_window(raw)
        frames = lf.impute_nan(frames, self._col_medians)

        X = frames.reshape(1, -1).astype(np.float32)  # (1, window_size * n_features)

        try:
            probs = self._model.predict_proba(X)[0]  # (n_classes,)
        except Exception as e:
            print(f"[RFClassifier] Prediction error: {e}")
            return self._fallback()

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        pred_class = self._classes[pred_idx] if pred_idx < len(self._classes) else "Unknown"

        fall_detected = pred_class == "Fall"
        posture_label = "Lying" if fall_detected else pred_class

        return {
            "posture_label": posture_label,
            "fall_detected": fall_detected,
            "confidence": round(confidence, 3),
            "other_labels": f"rf,pred={pred_class}",
        }

    def _fallback(self) -> dict:
        return {
            "posture_label": "Unknown",
            "fall_detected": False,
            "confidence": 0.0,
            "other_labels": "rf_fallback",
        }


def classify_with_rf(window: List[dict], classifier: Optional[RFPostureClassifier] = None) -> dict:
    """Convenience function matching classify_posture_and_fall()'s return signature."""
    if classifier is None:
        classifier = RFPostureClassifier()
    return classifier.predict(window)


def main() -> None:
    parser = argparse.ArgumentParser(description="Random Forest Posture Classifier")
    parser.add_argument("--demo", action="store_true", help="Run demo inference on synthetic windows")
    parser.add_argument("--model", type=str, default=None, help="Path to .joblib model file")
    args = parser.parse_args()

    if args.demo:
        run_classifier_demo(RFPostureClassifier)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

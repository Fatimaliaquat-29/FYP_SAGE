"""
lstm_classifier.py
==================
Inference module for the trained LSTM posture classifier.

Provides:
    LSTMPostureClassifier  – class with a rolling window buffer and predict()
    classify_with_lstm()   – convenience function matching the existing
                             classify_posture_and_fall() return signature

Usage (demo):
    python src/posture/lstm/lstm_classifier.py --demo
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

MODELS_DIR = REPO_ROOT / "models"
LSTM_MODEL_PATH = MODELS_DIR / "lstm_posture.keras"
LSTM_ENCODER_PATH = MODELS_DIR / "lstm_label_encoder.json"

LANDMARK_COUNT = 33
FEATURE_DIM = LANDMARK_COUNT * 2  # 66


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
    if len(arr) < FEATURE_DIM:
        arr = np.concatenate([arr, np.full(FEATURE_DIM - len(arr), np.nan, dtype=np.float32)])
    return arr[:FEATURE_DIM]


def _impute_row(arr: np.ndarray, col_medians: Optional[np.ndarray] = None) -> np.ndarray:
    """Replace NaNs in a (66,) array using provided medians or 0.5 fallback."""
    out = arr.copy()
    nan_mask = np.isnan(out)
    if nan_mask.any():
        if col_medians is not None:
            out[nan_mask] = col_medians[nan_mask]
        else:
            out[nan_mask] = 0.5  # neutral screen-space position
    return out


# ---------------------------------------------------------------------------
# Main classifier class
# ---------------------------------------------------------------------------

class LSTMPostureClassifier:
    """
    Real-time posture classifier backed by a trained Keras LSTM model.

    Parameters
    ----------
    model_path : Path, optional
        Path to the saved .keras model file. Defaults to
        models/lstm_posture.keras in the repository root.
    encoder_path : Path, optional
        Path to the label encoder JSON. Defaults to
        models/lstm_label_encoder.json.

    Usage
    -----
    clf = LSTMPostureClassifier()
    result = clf.predict(window_rows)
    # result → {"posture_label": "Standing", "fall_detected": False,
    #            "confidence": 0.94, "other_labels": "lstm"}
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None,
    ):
        self.model_path = Path(model_path or LSTM_MODEL_PATH)
        self.encoder_path = Path(encoder_path or LSTM_ENCODER_PATH)

        self._model = None
        self._classes: List[str] = ["Fall", "Lying", "Sitting", "Standing"]
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
            except Exception as e:
                print(f"[LSTMClassifier] Warning: could not load encoder: {e}")

        # Load Keras model
        if not self.model_path.exists():
            print(
                f"[LSTMClassifier] Model not found at {self.model_path}. "
                "Run lstm_trainer.py first. Falling back to Unknown."
            )
            return

        try:
            import tensorflow as tf
            self._model = tf.keras.models.load_model(str(self.model_path))
            self._available = True
            print(f"[LSTMClassifier] Loaded model from {self.model_path}")
        except ImportError:
            print(
                "[LSTMClassifier] TensorFlow not installed. "
                "Install with: pip install tensorflow-cpu"
            )
        except Exception as e:
            print(f"[LSTMClassifier] Failed to load model: {e}")

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def window_size(self) -> int:
        return self._window_size

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
            Length must be >= self.window_size; only the last window_size
            rows are used.

        Returns
        -------
        dict with keys:
            posture_label  str   – "Standing" | "Sitting" | "Lying" | "Unknown"
            fall_detected  bool  – True when LSTM predicts "Fall" class
            confidence     float – max softmax probability
            other_labels   str   – "lstm" or "lstm_fallback"
        """
        if not self._available or self._model is None:
            return self._fallback()

        if len(window) < self._window_size:
            return self._fallback()

        # Use the last window_size frames
        recent = window[-self._window_size:]

        # Build (window_size, 66) array
        frames = np.stack(
            [_impute_row(_extract_raw_keypoints(r), self._col_medians) for r in recent],
            axis=0,
        ).astype(np.float32)

        # Model expects (batch, window_size, n_features)
        X = frames[np.newaxis, ...]  # (1, window_size, 66)

        try:
            probs = self._model.predict(X, verbose=0)[0]  # (n_classes,)
        except Exception as e:
            print(f"[LSTMClassifier] Prediction error: {e}")
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
            "other_labels": f"lstm,pred={pred_class}",
        }

    @staticmethod
    def _fallback() -> dict:
        return {
            "posture_label": "Unknown",
            "fall_detected": False,
            "confidence": 0.0,
            "other_labels": "lstm_fallback",
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def classify_with_lstm(
    window: List[dict],
    classifier: Optional[LSTMPostureClassifier] = None,
    model_path: Optional[Path] = None,
) -> dict:
    """
    Convenience wrapper that classifies a window of pose rows using the LSTM.

    Parameters
    ----------
    window : list of pose row dicts (each with 'keypoints')
    classifier : LSTMPostureClassifier, optional
        Pass a pre-loaded classifier to avoid reloading the model every call.
    model_path : Path, optional
        Override model path (used if classifier is None).

    Returns
    -------
    Same dict format as pipeline_utils.classify_posture_and_fall().
    """
    if classifier is None:
        classifier = LSTMPostureClassifier(model_path=model_path)
    return classifier.predict(window)


# ---------------------------------------------------------------------------
# Demo / CLI
# ---------------------------------------------------------------------------

def _run_demo():
    """Quick smoke test using synthetic standing and fall windows."""
    from src.posture.lstm.lstm_dataset import (
        _make_standing_kps,
        _make_fall_sequence,
        FEATURE_DIM,
    )

    clf = LSTMPostureClassifier()

    if not clf.is_available:
        print("\n[demo] Model not available. Run lstm_trainer.py first.")
        print("[demo] Showing fallback output:")
        window = [{"keypoints": list(_make_standing_kps())} for _ in range(clf.window_size)]
        print(" ", clf.predict(window))
        return

    print(f"\n[demo] window_size={clf.window_size}, n_features={clf._n_features}")

    # Standing window
    stand_kps = _make_standing_kps()
    window_stand = [{"keypoints": list(stand_kps)} for _ in range(clf.window_size)]
    res = clf.predict(window_stand)
    print(f"  Standing window → {res}")

    # Fall window (transition from standing to lying)
    fall_frames = _make_fall_sequence(clf.window_size)
    window_fall = [{"keypoints": list(f)} for f in fall_frames]
    res = clf.predict(window_fall)
    print(f"  Fall    window → {res}")


def main():
    parser = argparse.ArgumentParser(description="LSTM Posture Classifier")
    parser.add_argument("--demo", action="store_true", help="Run demo inference on synthetic windows")
    parser.add_argument("--model", type=str, default=None, help="Path to .keras model file")
    args = parser.parse_args()

    if args.demo:
        _run_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

"""
sequence_window_classifier.py
==============================
Shared base for the LSTM and TCN posture classifiers
(`LSTMPostureClassifier`, `TCNPostureClassifier`). Both models consume an
identical (window_size, 132) normalized-position-plus-velocity input (see
`lstm_features.py`) through an identical rolling-window buffer contract, and
differ only in which trained Keras model backs them -- so every bit of
loading, windowing, inference, and fallback logic lives here exactly once.
A subclass only needs to declare three class attributes
(`DEFAULT_MODEL_PATH`, `DEFAULT_ENCODER_PATH`, `LABEL_TAG`) to get a fully
working, drop-in-compatible classifier with the same public interface:
`.predict()`, `.window_size`, `.raw_history_needed`, `.is_available`.
"""

import argparse
from pathlib import Path
from typing import List, Optional

import numpy as np

from src.posture.lstm import lstm_features as lf

LANDMARK_COUNT = 33
RAW_FEATURE_DIM = LANDMARK_COUNT * 2  # 66: raw x/y landmark coordinates
FEATURE_DIM = lf.FEATURE_DIM           # 132: normalized position + velocity (model input)


def extract_raw_keypoints(row: dict) -> np.ndarray:
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


class SequenceWindowClassifier:
    """
    Real-time posture classifier backed by a trained Keras model that
    consumes a rolling window of normalized-position-plus-velocity features
    (see `lstm_features.py`).

    Subclasses must declare:
        DEFAULT_MODEL_PATH   : Path to the .keras file loaded when
                                `model_path` isn't given to `__init__`.
        DEFAULT_ENCODER_PATH : Path to the label-encoder JSON loaded when
                                `encoder_path` isn't given to `__init__`.
        LABEL_TAG             : short lowercase string identifying the model
                                in `other_labels` and log messages, e.g.
                                "lstm" or "tcn".

    Parameters
    ----------
    model_path : Path, optional
        Path to the saved .keras model file. Defaults to DEFAULT_MODEL_PATH.
    encoder_path : Path, optional
        Path to the label encoder JSON. Defaults to DEFAULT_ENCODER_PATH.

    Usage
    -----
    clf = LSTMPostureClassifier()  # or TCNPostureClassifier()
    result = clf.predict(window_rows)
    # result -> {"posture_label": "Standing", "fall_detected": False,
    #            "confidence": 0.94, "other_labels": "lstm,pred=Standing"}
    """

    DEFAULT_MODEL_PATH: Path
    DEFAULT_ENCODER_PATH: Path
    LABEL_TAG: str

    def __init__(
        self,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None,
    ) -> None:
        self.model_path = Path(model_path or self.DEFAULT_MODEL_PATH)
        self.encoder_path = Path(encoder_path or self.DEFAULT_ENCODER_PATH)

        self._model = None
        self._classes: List[str] = ["Fall", "Lying", "Sitting", "Standing", "Unknown"]
        self._window_size: int = 30
        self._n_features: int = FEATURE_DIM
        self._col_medians: Optional[np.ndarray] = None
        self._available: bool = False

        self._load()

    # ── Loading ───────────────────────────────────────────────────────────────

    @property
    def _log_tag(self) -> str:
        return f"{self.LABEL_TAG.upper()}Classifier"

    def _load(self) -> None:
        """Attempt to load model and encoder. Sets self._available = True on success."""
        if self.encoder_path.exists():
            try:
                import json
                enc = json.loads(self.encoder_path.read_text(encoding="utf-8"))
                self._classes = enc.get("classes", self._classes)
                self._window_size = int(enc.get("window_size", self._window_size))
                self._n_features = int(enc.get("n_features", self._n_features))
                col_medians = enc.get("col_medians")
                if col_medians is not None:
                    self._col_medians = np.array(col_medians, dtype=np.float32)
            except Exception as e:
                print(f"[{self._log_tag}] Warning: could not load encoder: {e}")

        if not self.model_path.exists():
            print(
                f"[{self._log_tag}] Model not found at {self.model_path}. "
                f"Run {self.LABEL_TAG}_trainer.py first. Falling back to Unknown."
            )
            return

        try:
            import tensorflow as tf
            self._model = tf.keras.models.load_model(str(self.model_path))
            self._available = True
            print(f"[{self._log_tag}] Loaded model from {self.model_path}")
        except ImportError:
            print(
                f"[{self._log_tag}] TensorFlow not installed. "
                "Install with: pip install tensorflow-cpu"
            )
        except Exception as e:
            print(f"[{self._log_tag}] Failed to load model: {e}")

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
        before it.
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
            fall_detected  bool  – True when the model predicts "Fall" class
            confidence     float – max softmax probability
            other_labels   str   – "{LABEL_TAG},pred=..." or "{LABEL_TAG}_fallback"
        """
        if not self._available or self._model is None:
            return self._fallback()

        if len(window) < self.raw_history_needed:
            return self._fallback()

        # Use the last raw_history_needed raw frames (window_size + 1)
        recent = window[-self.raw_history_needed:]

        # Raw (window_size+1, 66) -> normalized position + velocity (window_size, 132)
        raw = np.stack([extract_raw_keypoints(r) for r in recent], axis=0)
        frames = lf.build_features_from_raw_window(raw)
        frames = lf.impute_nan(frames, self._col_medians)

        # Model expects (batch, window_size, n_features)
        X = frames[np.newaxis, ...].astype(np.float32)  # (1, window_size, 132)

        try:
            probs = self._model.predict(X, verbose=0)[0]  # (n_classes,)
        except Exception as e:
            print(f"[{self._log_tag}] Prediction error: {e}")
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
            "other_labels": f"{self.LABEL_TAG},pred={pred_class}",
        }

    def _fallback(self) -> dict:
        return {
            "posture_label": "Unknown",
            "fall_detected": False,
            "confidence": 0.0,
            "other_labels": f"{self.LABEL_TAG}_fallback",
        }


# ---------------------------------------------------------------------------
# Shared demo / CLI entry point
# ---------------------------------------------------------------------------

def run_classifier_demo(classifier_cls: type) -> None:
    """Quick smoke test using synthetic standing and fall windows, shared by
    lstm_classifier.py's and tcn_classifier.py's `--demo` CLI flag."""
    from src.posture.lstm.lstm_dataset import _make_standing_kps, _make_fall_sequence

    clf = classifier_cls()
    n = clf.raw_history_needed  # window_size + 1 raw frames

    if not clf.is_available:
        print(f"\n[demo] Model not available. Run {clf.LABEL_TAG}_trainer.py first.")
        print("[demo] Showing fallback output:")
        window = [{"keypoints": list(_make_standing_kps())} for _ in range(n)]
        print(" ", clf.predict(window))
        return

    print(f"\n[demo] window_size={clf.window_size}, n_features={clf._n_features}")

    # Standing window
    window_stand = [{"keypoints": list(_make_standing_kps())} for _ in range(n)]
    res = clf.predict(window_stand)
    print(f"  Standing window -> {res}")

    # Fall window (transition from standing to lying)
    fall_frames = _make_fall_sequence(n)
    window_fall = [{"keypoints": list(f)} for f in fall_frames]
    res = clf.predict(window_fall)
    print(f"  Fall    window -> {res}")


def run_classifier_cli(classifier_cls: type, description: str) -> None:
    """Shared `if __name__ == "__main__"` entry point for both classifier modules."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--demo", action="store_true", help="Run demo inference on synthetic windows")
    parser.add_argument("--model", type=str, default=None, help="Path to .keras model file")
    args = parser.parse_args()

    if args.demo:
        run_classifier_demo(classifier_cls)
    else:
        parser.print_help()

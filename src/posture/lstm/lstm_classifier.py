"""
lstm_classifier.py
==================
Inference module for the trained LSTM posture classifier.

Provides:
    LSTMPostureClassifier – LSTM-backed SequenceWindowClassifier (see
                            src/posture/sequence_window_classifier.py for
                            the shared loading/windowing/inference logic)
    classify_with_lstm()  – convenience function matching the existing
                            classify_posture_and_fall() return signature

Usage (demo):
    python src/posture/lstm/lstm_classifier.py --demo
"""

import sys
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.sequence_window_classifier import (
    SequenceWindowClassifier,
    extract_raw_keypoints as _extract_raw_keypoints,  # re-exported: tests/test_lstm_pipeline.py imports this name
    run_classifier_cli,
)

MODELS_DIR = REPO_ROOT / "models"
LSTM_MODEL_PATH = MODELS_DIR / "lstm_posture.keras"
LSTM_ENCODER_PATH = MODELS_DIR / "lstm_label_encoder.json"


class LSTMPostureClassifier(SequenceWindowClassifier):
    """
    Real-time posture classifier backed by a trained Keras LSTM model.

    See `SequenceWindowClassifier` for the full interface contract
    (`.predict()`, `.window_size`, `.raw_history_needed`, `.is_available`) --
    this class only supplies the LSTM-specific default paths and label tag.

    Usage
    -----
    clf = LSTMPostureClassifier()
    result = clf.predict(window_rows)
    # result → {"posture_label": "Standing", "fall_detected": False,
    #            "confidence": 0.94, "other_labels": "lstm,pred=Standing"}
    """
    DEFAULT_MODEL_PATH = LSTM_MODEL_PATH
    DEFAULT_ENCODER_PATH = LSTM_ENCODER_PATH
    LABEL_TAG = "lstm"


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


def main() -> None:
    run_classifier_cli(LSTMPostureClassifier, description="LSTM Posture Classifier")


if __name__ == "__main__":
    main()

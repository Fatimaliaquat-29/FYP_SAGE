"""
tcn_classifier.py
==================
Inference module for the trained TCN posture classifier.

Provides:
    TCNPostureClassifier – TCN-backed SequenceWindowClassifier (see
                           src/posture/sequence_window_classifier.py for
                           the shared loading/windowing/inference logic).
                           Its public interface (.predict(), .window_size,
                           .raw_history_needed, .is_available) is identical
                           to LSTMPostureClassifier so it can act as a
                           drop-in replacement anywhere the LSTM classifier
                           is used.
    classify_with_tcn()  – convenience function matching the existing
                           classify_posture_and_fall() return signature

Usage (demo):
    python src/posture/tcn/tcn_classifier.py --demo
"""

import sys
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.sequence_window_classifier import SequenceWindowClassifier, run_classifier_cli

MODELS_DIR = REPO_ROOT / "models"
TCN_MODEL_PATH = MODELS_DIR / "tcn_posture.keras"
TCN_ENCODER_PATH = MODELS_DIR / "tcn_label_encoder.json"


class TCNPostureClassifier(SequenceWindowClassifier):
    """
    Real-time posture classifier backed by a trained Keras TCN model.

    See `SequenceWindowClassifier` for the full interface contract
    (`.predict()`, `.window_size`, `.raw_history_needed`, `.is_available`) --
    this class only supplies the TCN-specific default paths and label tag,
    plus one optional addition: `fall_confirm_frames`.

    Usage
    -----
    clf = TCNPostureClassifier()
    result = clf.predict(window_rows)
    # result → {"posture_label": "Standing", "fall_detected": False,
    #            "confidence": 0.94, "other_labels": "tcn,pred=Standing"}

    fall_confirm_frames (default 1 -- no change from raw behavior)
    ------------------------------------------------------------
    Phase 2.5's edge-case analysis (see TCN_IMPLEMENTATION_NOTES.md) found
    that a fast bend-to-pick-up-an-object motion gets classified as
    "Fall" with moderately high confidence (mean 0.77) for brief stretches
    -- confidence thresholding alone doesn't separate these from genuine
    falls, because the model isn't uncertain, it's confidently wrong for a
    short time. What does separate them is duration: a real fall's Lying
    phase lasts seconds, a bend's misclassified stretch lasts a couple of
    dozen frames. Setting fall_confirm_frames > 1 requires that many
    *consecutive* raw "Fall" predictions before `fall_detected` is actually
    reported True (same idea `hybrid_evaluate.py` already applies to the
    LSTM, and the rule-based heuristic already applies internally).

    Default is 1 (report on the very first "Fall" prediction, identical to
    the original behavior) so nothing about the public interface or
    existing callers changes unless this is explicitly opted into --
    `compare_tcn_lstm.py`'s architecture comparison deliberately leaves it
    at the default to keep comparing LSTM vs. TCN raw decisions, not tuned
    ones.
    """
    DEFAULT_MODEL_PATH = TCN_MODEL_PATH
    DEFAULT_ENCODER_PATH = TCN_ENCODER_PATH
    LABEL_TAG = "tcn"

    def __init__(self, model_path=None, encoder_path=None, fall_confirm_frames: int = 1):
        self.fall_confirm_frames = max(1, int(fall_confirm_frames))
        self._consecutive_fall_count = 0
        super().__init__(model_path=model_path, encoder_path=encoder_path)

    def reset_state(self) -> None:
        """Clear the consecutive-fall counter -- call this between clips/
        sessions when reusing one classifier instance, so a streak from the
        end of one clip can't bleed into the start of the next."""
        self._consecutive_fall_count = 0

    def predict(self, window):
        result = super().predict(window)
        if self.fall_confirm_frames <= 1:
            return result  # default: identical to SequenceWindowClassifier's raw behavior

        if result["fall_detected"]:
            self._consecutive_fall_count += 1
        else:
            self._consecutive_fall_count = 0

        if result["fall_detected"] and self._consecutive_fall_count < self.fall_confirm_frames:
            # Momentary "Fall" prediction, not yet sustained long enough to
            # confirm -- still report the posture_label (e.g. "Lying") since
            # that classification itself may be perfectly reasonable, just
            # don't raise the fall_detected flag on a single/few-frame blip.
            result = dict(result)
            result["fall_detected"] = False

        return result


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


def main() -> None:
    run_classifier_cli(TCNPostureClassifier, description="TCN Posture Classifier")


if __name__ == "__main__":
    main()

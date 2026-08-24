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
from collections import Counter
from pathlib import Path
from typing import List, Optional, Tuple

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

    def __init__(self, model_path: Optional[Path] = None, encoder_path: Optional[Path] = None,
                 fall_confirm_frames: int = 1, smoothing_window: int = 1):
        """
        fall_confirm_frames (default 1 -- no change from raw per-window
        behavior): requires this many *consecutive* raw "Fall" predictions
        before fall_detected is actually reported True, same mechanism and
        rationale as TCNPostureClassifier's own fall_confirm_frames (see
        src/posture/tcn/tcn_classifier.py). Investigated for this model
        specifically after a false-positive diagnosis on the Hussain set
        (see docs/RF_GENERALIZATION_INVESTIGATION.md "False-alarm
        diagnosis"): most of the observed false alarms are sustained
        misclassifications lasting well over a second (up to ~3.5s for
        "person exiting frame"), not brief blips, so this knob has limited
        -- not zero -- effect; it is NOT a substitute for improving the
        underlying decision boundary. Left at the default (disabled) for
        `compare_all_models.py`'s architecture comparisons, same reasoning
        as the TCN's default.

        smoothing_window (default 1 -- no change from raw per-window
        behavior; a later audit session, RF-vs-HGB real-footage
        confirmation round 2): rolling MAJORITY-VOTE smoothing over the
        last N raw per-frame predicted classes, applied BEFORE the
        fall_detected/posture_label derivation in predict() below, so both
        are smoothed consistently from one source instead of risking them
        disagreeing. This is deliberately separate from fall_confirm_frames
        above, not a reuse of it: fall_confirm_frames only gates the
        fall_detected BOOLEAN via a consecutive-Fall counter and never
        touches posture_label at all, so it does not generalize to
        smoothing the Standing/Sitting/Lying/Unknown decision -- checked
        before writing this, see _smooth()'s docstring for the tie-break
        rule and current evaluation results for whether this actually
        helps (majority-vote smoothing suppresses brief flicker; it is NOT
        expected to fix a sustained, high-confidence misclassification
        spanning most of a window).
        """
        self.model_path = Path(model_path or self.DEFAULT_MODEL_PATH)
        self.encoder_path = Path(encoder_path or self.DEFAULT_ENCODER_PATH)
        self.fall_confirm_frames = max(1, int(fall_confirm_frames))
        self._consecutive_fall_count = 0
        self.smoothing_window = max(1, int(smoothing_window))
        self._raw_class_history: List[Tuple[str, float]] = []

        self._model = None
        self._classes: List[str] = ["Fall", "Lying", "Sitting", "Standing", "Unknown"]
        self._window_size: int = 30
        self._n_features: int = lf.FEATURE_DIM
        self._col_medians: Optional[np.ndarray] = None
        self._n_features_out: Optional[int] = None
        self._available: bool = False
        # "flatten" (every frame value) or "summary" (mean/std/min/max/last
        # per feature across the window) -- read from the encoder so a
        # checkpoint always dictates its own inference-time transform
        # rather than this class assuming one. Defaults to "flatten" for
        # older checkpoints saved before this field existed.
        self._feature_representation: str = "flatten"

        self._load()

    def reset_state(self) -> None:
        """Clear the consecutive-fall counter AND the posture-smoothing
        history -- call this between clips/sessions when reusing one
        classifier instance, so neither a fall streak nor stale smoothing
        history from the end of one clip can bleed into the start of the
        next."""
        self._consecutive_fall_count = 0
        self._raw_class_history = []

    def _load(self) -> None:
        if self.encoder_path.exists():
            try:
                enc = json.loads(self.encoder_path.read_text(encoding="utf-8"))
                self._classes = enc.get("classes", self._classes)
                self._window_size = int(enc.get("window_size", self._window_size))
                self._n_features = int(enc.get("n_features", self._n_features))
                self._feature_representation = enc.get("feature_representation", "flatten")
                # n_features_out: the flattened/summarized vector width this
                # checkpoint was trained on (rf_trainer.py always writes it --
                # see that module's own `encoder` dict). Absent only for a
                # checkpoint saved before this field existed; None is a valid
                # "unknown, don't check" sentinel, not an error, in that case.
                n_features_out = enc.get("n_features_out")
                self._n_features_out = int(n_features_out) if n_features_out is not None else None
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
            # Training uses n_jobs=-1 to parallelize tree-building across the
            # whole dataset, which is the right call there -- but predict()
            # here is called once per video frame on a single-row batch, and
            # RandomForestClassifier.predict_proba re-parallelizes across
            # trees on every call using the n_jobs baked into the pickled
            # estimator. Spinning up a joblib worker pool per single-sample
            # call is pure overhead (no work to parallelize) and was
            # observed to make frame-by-frame inference catastrophically
            # slow. Force single-threaded prediction; training scripts set
            # their own n_jobs independently and are unaffected.
            self._model.n_jobs = 1
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

    def _smooth(self, pred_class: str, confidence: float) -> Tuple[str, float]:
        """Rolling majority-vote smoothing over the last `smoothing_window`
        raw per-frame predicted classes (the model's own 5-class output --
        Fall/Lying/Sitting/Standing/Unknown -- BEFORE the fall_detected/
        posture_label collapse in predict()). At smoothing_window<=1 (the
        default) this always returns (pred_class, confidence) unchanged --
        existing callers see byte-for-byte identical behavior.

        Ties (classes equally common within the window) are broken toward
        the MOST RECENT tied class, not insertion order, so once a genuine
        new state is at least as common as anything else in the window it
        wins immediately rather than waiting for stale votes to age out.

        Smoothed confidence is the mean of only the votes that agree with
        the smoothed class (not the whole window), so it reflects
        confidence in the winning decision, not diluted by disagreeing
        frames.
        """
        self._raw_class_history.append((pred_class, confidence))
        if len(self._raw_class_history) > self.smoothing_window:
            self._raw_class_history.pop(0)
        if self.smoothing_window <= 1:
            return pred_class, confidence

        counts = Counter(c for c, _ in self._raw_class_history)
        max_count = max(counts.values())
        tied = {c for c, n in counts.items() if n == max_count}
        smoothed_class = next(c for c, _ in reversed(self._raw_class_history) if c in tied)
        matching_conf = [conf for c, conf in self._raw_class_history if c == smoothed_class]
        return smoothed_class, float(np.mean(matching_conf))

    @property
    def is_available(self) -> bool:
        return self._available

    def predict(self, window: List[dict]) -> dict:
        """
        Classify posture from a sliding window of pose row dicts. Same
        contract as SequenceWindowClassifier.predict() (see that module for
        the full docstring) -- the only difference is the (window_size,
        n_features) feature tensor gets reduced to a single feature vector
        (per self._feature_representation -- "flatten" or "summary", see
        _load()) before calling predict_proba, since a Random Forest has no
        notion of a time axis.

        ROBUSTNESS (a later audit session -- see docs/RF_GENERALIZATION_INVESTIGATION.md's
        own follow-up section for the evidence): the ENTIRE feature-building
        + prediction path is now inside one try/except, not just the
        `predict_proba` call. Previously, an exception raised while building
        `X` (a malformed row missing "keypoints", an unexpected keypoint
        count, or any other feature-extraction failure) was NOT caught --
        every OTHER failure mode in this class (missing model, missing
        encoder, a predict_proba error) already falls back gracefully, but
        this one path did not, so a single malformed frame could crash an
        entire batch-evaluation run (compare_all_models.py/
        compare_tcn_lstm.py call `.predict()` with no try/except of their
        own) instead of degrading to one `_fallback()` result the way every
        other input problem already does.
        """
        if not self._available or self._model is None:
            return self._fallback()

        if len(window) < self.raw_history_needed:
            return self._fallback()

        try:
            recent = window[-self.raw_history_needed:]
            raw = np.stack([extract_raw_keypoints(r) for r in recent], axis=0)
            frames = lf.build_features_from_raw_window(raw)
            frames = lf.impute_nan(frames, self._col_medians)

            if self._feature_representation == "summary":
                # Must exactly mirror rf_trainer.summarize_windows()'s
                # mean/std/min/max/last order -- a mismatch here would silently
                # feed the model nonsense features rather than erroring.
                mean = frames.mean(axis=0)
                std = frames.std(axis=0)
                mn = frames.min(axis=0)
                mx = frames.max(axis=0)
                last = frames[-1, :]
                X = np.concatenate([mean, std, mn, mx, last])[np.newaxis, :].astype(np.float32)
            else:
                X = frames.reshape(1, -1).astype(np.float32)  # (1, window_size * n_features)

            # Proactive, LOUD schema check (a later audit session) -- without
            # this, a checkpoint/feature-pipeline mismatch (e.g.
            # lstm_features.py's own feature set changing without retraining
            # this model) would only surface as sklearn's own internal
            # "X has N features, but RandomForestClassifier is expecting M"
            # ValueError, caught by the broad except below and silently
            # degraded to a generic "Unknown" fallback -- indistinguishable
            # from ordinary low-confidence uncertainty. Checking (and naming
            # the mismatch explicitly) before calling predict_proba turns a
            # silent integration bug into a clear, diagnosable log line.
            if self._n_features_out is not None and X.shape[1] != self._n_features_out:
                print(f"[RFClassifier] Feature schema mismatch: built {X.shape[1]}-dim input, "
                      f"checkpoint expects {self._n_features_out} (feature_representation="
                      f"{self._feature_representation!r}). Falling back to Unknown.")
                return self._fallback()

            probs = self._model.predict_proba(X)[0]  # (n_classes,), columns ordered per self._model.classes_

            # Correctness fix (a later audit session): DO NOT assume probs[i]
            # corresponds to self._classes[i] positionally. sklearn's
            # predict_proba columns are ordered by `model.classes_`, which is
            # only [0, 1, ..., n_classes-1] densely if EVERY class appeared in
            # the training fold -- if a class were entirely absent from
            # training (e.g. an unlucky StratifiedGroupKFold split), model.
            # classes_ would be a SUBSET/non-contiguous, and the old
            # `self._classes[pred_idx]` lookup would silently return the WRONG
            # class name for every prediction. Confirmed currently latent
            # (the production checkpoint's model.classes_ == [0,1,2,3,4],
            # dense) but unguarded -- this makes the mapping explicit and
            # correct regardless of whether every class was present in
            # training, rather than relying on that always being true.
            model_classes = getattr(self._model, "classes_", np.arange(len(self._classes)))
            pred_pos = int(np.argmax(probs))
            confidence = float(probs[pred_pos])
            class_idx = int(model_classes[pred_pos])
            pred_class = self._classes[class_idx] if 0 <= class_idx < len(self._classes) else "Unknown"
        except Exception as e:
            print(f"[RFClassifier] Prediction error: {e}")
            return self._fallback()

        smoothed_class, smoothed_confidence = self._smooth(pred_class, confidence)

        fall_detected = smoothed_class == "Fall"
        posture_label = "Lying" if fall_detected else smoothed_class

        result = {
            "posture_label": posture_label,
            "fall_detected": fall_detected,
            "confidence": round(smoothed_confidence, 3),
            "other_labels": (f"rf,pred={pred_class}" if self.smoothing_window <= 1
                              else f"rf,pred={pred_class},smoothed={smoothed_class}"),
        }

        if self.fall_confirm_frames <= 1:
            return result  # default: raw per-window decision, unchanged

        if fall_detected:
            self._consecutive_fall_count += 1
        else:
            self._consecutive_fall_count = 0

        if fall_detected and self._consecutive_fall_count < self.fall_confirm_frames:
            # Momentary "Fall" prediction, not yet sustained long enough to
            # confirm -- keep the posture_label (still a reasonable read of
            # this one frame) but don't raise fall_detected on a blip.
            result = dict(result)
            result["fall_detected"] = False

        return result

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
        # Bug fixed (a later audit session): --model was parsed but never
        # actually used -- run_classifier_demo(RFPostureClassifier) always
        # constructs its classifier as `classifier_cls()` internally (see
        # sequence_window_classifier.run_classifier_demo, shared with the
        # LSTM/TCN demo CLIs), with no way to pass constructor arguments
        # through, so a caller passing --model expecting it to load a
        # specific checkpoint got no error and no warning, just the wrong
        # (default) model. Fixed here, locally, without touching that
        # shared helper: a zero-arg lambda satisfies the same
        # `classifier_cls()` call it already makes, while closing over the
        # requested path.
        classifier_cls = (lambda: RFPostureClassifier(model_path=args.model)) if args.model else RFPostureClassifier
        run_classifier_demo(classifier_cls)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

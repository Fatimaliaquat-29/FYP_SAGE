# S.A.G.E. — Smart Automated Guardian & Evaluator

A fall-detection and fall-risk pipeline built on MediaPipe pose landmarks.
It detects falls as/after they happen (a rule-based heuristic plus a choice
of LSTM/TCN/Random Forest temporal models, combined in an OR-gate hybrid),
and separately, experimentally, assesses longer-term fall *risk* from gait
quality signals. A real-time camera entry point ties the fall-detection
side together for live/recorded-video use.

This file is the practical "how do I use this" entry point. For *why*
specific thresholds/designs are what they are, see `context.txt` (full
technical/narrative history) and the topic-specific docs under `docs/`.

---

## 1. Purpose

Detect falls in elderly/at-risk individuals from ordinary camera footage,
and flag elevated fall risk before a fall happens, without wearables. The
project targets eventual deployment on edge hardware (Jetson Nano/Orin),
so model size/latency/memory are tracked deliberately alongside accuracy
throughout.

## 2. What's actually implemented (current state)

| Component | Status | Where |
|---|---|---|
| MediaPipe pose extraction | Done | `src/posture/pipeline_utils.py`, `evaluate_real_footage.py` |
| Rule-based heuristic fall detector | Done, tuned on real data | `src/posture/pipeline_utils.py` |
| LSTM temporal classifier | Done, trained | `src/posture/lstm/` |
| TCN temporal classifier | Done, trained, regression fixed (see `docs/TCN_REGRESSION_REPORT.md`) | `src/posture/tcn/` |
| Random Forest classifier | Done, trained, pruned | `src/posture/rf/` |
| Heuristic+LSTM hybrid (OR-gate) | Done, production path | `src/posture/pipeline_utils.py`, `hybrid_evaluate.py` |
| Real-time camera entry point | Done | `realtime_fall_detection.py` |
| 3-way model comparison (LSTM/TCN/RF) | Done | `compare_all_models.py`, `results/all_models_*/` |
| Gait/fall-risk assessment (`assess_risk`) | First-pass rule-based implementation, **not clinically validated** — see limitations | `src/gait/` |
| YOLO object detection layer | Not started (separate branch, `YOLO_fatima`) | — |
| Structured event schema / LLM reasoning layer | Not started (planned integration phase, see `docs/IMPLEMENTATION_PLAN.md` Section 5) | — |

## 3. Model architectures

**Heuristic** (`pipeline_utils.py`): scale-invariant joint angles (torso,
knee, hip) as the primary posture signal; hip velocity and torso angular
velocity (both time- and body-scale-normalized) drive three fall triggers
(`rapid_fall`, `pre_lying_fall`, `sustained_lying`). See `context.txt`
Section 2 for the full derivation and current constants.

**LSTM** (`src/posture/lstm/`):
```
Input (30 frames x 132 features)
  -> LSTM(64) -> Dropout(0.3)
  -> LSTM(32) -> Dropout(0.3)
  -> Dense(5, softmax)
```
63,013 parameters. Output classes: Fall, Lying, Sitting, Standing, Unknown.

**TCN** (`src/posture/tcn/`): 4 residual blocks (causal, dilated Conv1D,
dilations 1/2/4/8) -> `GlobalAveragePooling1D` -> `Dense(5, softmax)`.
39,365 parameters — same input/output contract as the LSTM, drop-in
compatible (`TCNPostureClassifier` mirrors `LSTMPostureClassifier`'s
interface exactly). L2=1e-5 weight regularization; see
`docs/TCN_IMPLEMENTATION_NOTES.md` for the full architecture rationale and
`docs/TCN_REGRESSION_REPORT.md` for a regression that was found and fixed
in this component (balanced class-weighting hurt real-footage accuracy;
reverted, L2 kept).

**Random Forest** (`src/posture/rf/`): `RandomForestClassifier` on the
*same* 30x132 windows, flattened to a single 3,960-dim vector (a tree
ensemble has no notion of a time axis). `n_estimators=300`,
`min_samples_leaf=20` (pruned — see Section 10). Same public interface as
the other two classifiers.

All three temporal models consume the *identical* input representation
(see Section 5) and share the *identical* train/val split methodology (see
Section 7), making them directly comparable — see
`results/all_models_sanawar/all_models_comparison.md` and
`results/all_models_hussain/all_models_comparison.md` for head-to-head
numbers on two real-footage test sets (Section 8/9).

**Gait risk assessor** (`src/gait/`): a conceptually separate,
rule-based, first-pass module — see Section 15.

## 4. Dataset / data pipeline

Training data combines three sources into `data/lstm_dataset.npz`:
UR Fall Dataset (~30 real fall+ADL sequences), UP-Fall Dataset (5 subjects,
3D skeleton), and LeFD/Le2i (130 annotated videos, 96 falls + 34 ADL).
Total: 62,202 real frames across 282 sequences. `data/`, `datasets/`, and
`Testing/` are gitignored (large/regenerable) — see Section 20 for how to
get or rebuild them.

Raw video -> per-frame MediaPipe keypoint CSVs:
`src/data_processing/build_lstm_datasets.py` /
`src/data_processing/extract_raw_dataset.py`. Per-frame CSVs ->
sliding-window `.npz`: `src/posture/lstm/lstm_dataset.py`.

## 5. Feature pipeline

Single source of truth: `src/posture/lstm/lstm_features.py`. Every frame's
33 raw MediaPipe (x, y) landmarks (66 values) are re-expressed as
**hip-centered, torso-length-scaled position** (66 dims, camera-distance
and translation invariant) plus **frame-to-frame velocity of that
normalized position** (66 dims) — 132 features per frame total. This fixed
a real bug: the original raw-coordinate model couldn't distinguish "far
from camera" from "lying down" (see `context.txt` Section 3). NaN landmarks
(MediaPipe visibility < 0.5, masked centrally in `pipeline_utils.build_pose_row`)
are imputed with per-feature training-set medians (`col_medians`, saved
alongside every model's label encoder so inference uses the same
statistics as training).

All three temporal-model trainers (`lstm_dataset.py`, `tcn_trainer.py`,
`rf_trainer.py`) load this exact same `data/lstm_dataset.npz` — nobody
re-derives features independently.

## 6. Windowing

30-frame sliding windows, computed per `sequence_id` (never crossing
sequence boundaries). A window is labeled `"Fall"` if any frame inside it
is labeled Fall; otherwise it takes its last frame's label
(`lstm_dataset.py::build_windows_from_real_data`). `verify_labels.py`
checks this invariant holds. Inference needs `window_size + 1` raw frames
(`.raw_history_needed`) since the oldest window frame needs a real (not
zero-padded) velocity, computed from the frame before it.

## 7. Training process

All three trainers (`lstm_trainer.py`, `tcn_trainer.py`, `rf_trainer.py`)
share the same methodology: `StratifiedGroupKFold` split by `sequence_id`
(so no sequence's frames appear in both train and validation — see
Section 12 on leakage), post-split synthetic-window augmentation (800
windows/class, train fold only, real validation data only), and a fixed
seed (42) so repeated runs are comparable. The two neural trainers add
`EarlyStopping`(patience 10, on `val_accuracy`) and `ReduceLROnPlateau`.

## 8. Validation process

Held out via the `StratifiedGroupKFold` split above — 100% real data (no
synthetic windows), disjoint sequences from training. Reported per-trainer:
accuracy, loss, and a full per-class precision/recall/F1 report
(`sklearn.classification_report`).

## 9. Test process

Real, labelled, held-out video clips (never used in training) —
`test_footage/Sanawar Testing 7-22-26/` (8 clips, ~90% Lying frames — the
"clean" scenario) and `test_footage/Hussain Testing 7-30-26/` (17 clips —
low light, occlusion, off-axis, floor-sitting, bending — the harder,
edge-case scenario). `compare_all_models.py` runs all three temporal
models over identical extracted keypoints and reports accuracy, macro
precision/recall/F1, confusion matrices, fall-detection recall, latency,
parameter/node counts, model size, and peak RAM. See Section 22.

## 10. Pruning

Applied to the Random Forest only (the two neural models use
Dropout+L2/L1 instead — Section 11). Two rounds, both confirmed on real
footage, not just the validation split (this project has been burned by
validation-split-only tuning before — see `docs/TCN_REGRESSION_REPORT.md`):

1. A 10-config sweep over `max_depth`, `min_samples_leaf`, `n_estimators`,
   and cost-complexity (`ccp_alpha`) found `min_samples_leaf=20` closes
   the train/val accuracy gap (0.289 -> 0.250), improves macro F1 on both
   the validation split (0.550 -> 0.592) and real footage (0.498 -> 0.511
   on the harder Hussain set), and cuts the serialized model from 27.7MB
   to 7.8MB (72% smaller).
2. A follow-up 11-config sweep specifically targeting the *remaining* gap
   found `max_features=0.1` (each split considers ~396 of the 3,960
   flattened features, vs. `RandomForestClassifier`'s own default of
   `sqrt(3960)` ~= 63) narrows the validation gap further (0.250 -> 0.238)
   and, confirmed on real footage: costs ~1 point of accuracy on the
   easier Sanawar set (56.2% -> 55.2%) but gains ~8.7 points on the harder
   Hussain edge-case set (60.5% -> 69.2%) with better macro F1 there too
   (0.511 -> 0.565) — fall-detection recall unchanged (100%/87.5%) on
   both sets. A genuine trade-off, not a free win, but consistent with
   this project's own conclusion that the harder, more realistic Hussain
   set is the more decision-relevant one (Section 13), so it's kept as
   the default. **Final production model**: 92.74% train / 68.92% val
   accuracy (gap 23.8%, down from the unpruned 28.9%).

Set in `rf_trainer.py::MIN_SAMPLES_LEAF` / `MAX_FEATURES`.

A follow-up deeper investigation (leakage audit, OOB-score trustworthiness,
an alternative summary-statistic feature representation, and class
weighting) confirmed this two-round config remains the best real-footage-
validated one — see `docs/RF_GENERALIZATION_INVESTIGATION.md` for the full
root-cause analysis and why two more well-motivated techniques were tried
and correctly rejected.

## 11. Fine-tuning / overfitting mitigation

- **LSTM/TCN**: Dropout (0.3 / 0.2) plus optional L1/L2 weight
  regularization (`l1`/`l2` params on both trainers; TCN uses `l2=1e-5` by
  default, evidence-supported — see `docs/TCN_IMPLEMENTATION_NOTES.md`
  Section 6). `use_class_weights` exists on all three trainers
  (LSTM/TCN/RF) for class-imbalance handling but **defaults to `False`
  everywhere** — balanced class weighting was tried on the TCN, measured,
  and reverted after it collapsed real-footage accuracy from 76.0% to
  47.8% by over-predicting the rare "Unknown" class (full ablation:
  `docs/TCN_IMPLEMENTATION_NOTES.md` Section 6.5). This is the project's
  clearest example of why every tuning decision here is confirmed against
  real footage, not just the validation split.
- **Random Forest**: pruning (Section 10) is the overfitting lever, since
  there's no dropout/regularization equivalent for a tree ensemble.

## 12. Data leakage safeguards

- `StratifiedGroupKFold` split is by `sequence_id`, not by window — a
  person's frames never appear in both train and validation.
- Synthetic augmentation is injected *after* the split, into the train
  fold only — the validation fold is 100% real data.
- `col_medians` (NaN-imputation statistics) are computed from training
  data and saved into each model's label encoder, reused verbatim at
  inference — training and inference never use different imputation
  statistics.
- The real-footage test sets (`test_footage/`) are entirely separate
  clips from the training data sources (UR Fall/UP-Fall/LeFD) — genuinely
  held out, not a split of the same pool.

## 13. Model evaluation

See `docs/TCN_REGRESSION_REPORT.md` for the full final comparison
(classification metrics, efficiency metrics, deployment analysis for
Jetson Nano/Orin). Headline: no single model wins outright — TCN is best
on the easier Sanawar set, Random Forest is best on the harder Hussain
edge-case set (best accuracy, best macro F1, and the only model that
caught every labelled fall in that set). Full per-class metrics and
confusion matrices: `results/all_models_sanawar/all_models_comparison.md`,
`results/all_models_hussain/all_models_comparison.md`.

## 14. Inference

`LSTMPostureClassifier` / `TCNPostureClassifier` / `RFPostureClassifier`
(`src/posture/{lstm,tcn,rf}/*_classifier.py`) share one public interface
(the first two share a literal base class,
`src/posture/sequence_window_classifier.py`; the RF reimplements the same
interface since it needs a flattened, not windowed, input):

```python
clf = TCNPostureClassifier()          # or LSTMPostureClassifier() / RFPostureClassifier()
result = clf.predict(window)          # window: list of pose row dicts, len >= clf.raw_history_needed
# result -> {"posture_label": "Standing", "fall_detected": False,
#            "confidence": 0.94, "other_labels": "tcn,pred=Standing"}
```

Production/live usage goes through `pipeline_utils.classify_posture_and_fall(lstm_classifier=...)`
(heuristic OR chosen temporal model) via `realtime_fall_detection.py`.

## 15. `assess_risk(window)` — gait/fall-risk interface

**Conceptually separate from everything above.** Sections 2-14 detect a
fall as/after it happens; this assesses longer-term fall *risk* from gait
quality *before* any fall occurs — a slower, trend-based signal over
multiple seconds, not a per-frame event. Per
`docs/IMPLEMENTATION_PLAN.md` Section 3, this is deliberately its own
module (`src/gait/`), not an extension of the Fall/Lying/Sitting/Standing/
Unknown classifier — forcing it into that framework would be a conceptual
mismatch, not just a code-organization one.

```python
from src.gait.gait_risk import GaitRiskAssessor

assessor = GaitRiskAssessor()
result = assessor.assess_risk(window)   # window: >= 90 pose-row dicts (~3s+ at 30fps)
result["risk_score"]   # float in [0, 1], or None if nothing was measurable
result["signals"]      # list of 4 signal dicts (see below)
```

**This is a risk SCORE, not a fall/no-fall classifier.** There is no
`fall_detected` field anywhere in its output, and no external API of any
kind (no REST/Flask/FastAPI/cloud service) — it's a plain local class.

### Risk-score contract
- `0.0` = lower assessed risk, `1.0` = higher assessed risk, on this
  module's own **internal, uncalibrated** scale — not a fall probability,
  not a clinically validated cut-off (see Limitations).
- `None` when *none* of the four signals could be computed from the given
  window (e.g. no walking bout, no sit-to-stand event, no valid tracking)
  — returning a fabricated middle value in that case would be silently
  wrong, so this contract returns `None` and explains why via `signals`
  instead.
- A weighted average of whichever signals *are* available for this
  specific window (see `src/gait/gait_risk.py::_SIGNAL_WEIGHTS`).

### Signals contract
Always 4 entries (one per candidate signal), each:
```python
{
    "name": "walking_speed" | "stride_regularity" | "postural_sway" | "sit_to_stand",
    "available": bool,             # could this window support this signal at all?
    "value": float | dict | None,  # the raw measured value; None if unavailable
    "risk_contribution": float | None,  # this signal's [0,1] sub-score
    "calibrated": False,           # always False currently -- see Limitations
    "description": str,
}
```
Signals are genuinely computed by `src/gait/gait_features.py`, never
fabricated to fill a gap — literature basis for each:
`docs/GAIT_LITERATURE_REVIEW.md`.

### Input contract
`window`: `List[dict]`, one per video frame, same row schema
`pipeline_utils.build_pose_row()` produces (`timestamp`, `keypoints`).
Single window per call (no batch dimension — see
`src/gait/gait_risk.py`'s module docstring for why). Minimum 90 frames
(`gait_features.MIN_WINDOW_FRAMES`); shorter raises `ValueError`. No
external preprocessing needed — normalization and NaN/Inf handling happen
internally.

## 16. Example usage

```python
# Fall detection (production path)
from src.posture.pipeline_utils import classify_posture_and_fall, build_pose_row
from src.posture.tcn.tcn_classifier import TCNPostureClassifier

tcn = TCNPostureClassifier()
row = build_pose_row(timestamp=..., frame=0, keypoints=flat_66_xy, visibility=vis_33)
result = classify_posture_and_fall(row, previous_rows=history, lstm_classifier=tcn)

# Gait/fall-risk assessment (separate, experimental)
from src.gait.gait_risk import GaitRiskAssessor
risk = GaitRiskAssessor().assess_risk(window_of_90plus_rows)
```

## 17. Project structure

```
src/
  posture/
    pipeline_utils.py        # heuristic fall detector, shared row schema (DO NOT edit lightly -- see docs/IMPLEMENTATION_PLAN.md Sec 0)
    sequence_window_classifier.py  # shared LSTM/TCN inference base class
    lstm/                     # LSTM: features, dataset, trainer, classifier
    tcn/                      # TCN: model, trainer, classifier
    rf/                       # Random Forest: trainer, classifier
  gait/                       # gait/fall-risk assessment (separate module)
  data_processing/            # raw video/dataset -> keypoint CSVs
  camera/, pose/               # standalone dev utilities (webcam smoke test,
                               # live pose-keypoint logging) -- not part of the
                               # main train/evaluate/infer pipeline, useful for
                               # ad-hoc camera/MediaPipe setup checks
compare_tcn_lstm.py           # 2-way LSTM/TCN evaluation harness
compare_all_models.py         # 3-way LSTM/TCN/RF evaluation harness
evaluate_real_footage.py      # heuristic-only batch evaluation + keypoint extraction
hybrid_evaluate.py            # heuristic+LSTM hybrid batch evaluation
realtime_fall_detection.py    # live/recorded-video entry point
verify_labels.py              # sanity-checks the Fall-window labeling invariant
tests/                        # unittest suite
docs/                         # architecture/protocol/literature reference docs
models/                       # trained checkpoints -- flat, one file per model (see note below)
context.txt                   # full technical/narrative project history
```

**`models/` is intentionally flat** (11 files: `pose_landmarker_full.task`
+ each of LSTM/TCN/RF's production `.keras`/`.joblib` checkpoint + label
encoder, plus `lstm_posture_before_lefd.keras`/`lstm_posture_retrained.keras`
and their encoders, kept specifically for the before/after and
same-data-fair comparisons in `context.txt` Sections 3 and 13). Every
trainer/classifier resolves its checkpoint via a hardcoded path constant
(e.g. `rf_trainer.RF_MODEL_PATH`), so splitting into per-architecture
subfolders was considered and rejected during the August 2026 cleanup
(`context.txt` Section 16) — it would mean updating those constants across
six files for no real discoverability gain at only 11 files, all already
namespaced by filename prefix (`lstm_*`/`tcn_*`/`rf_*`). Two stale
duplicate/superseded checkpoint directories (`models/experiments/`,
`models/lstm_checkpoint/`) were removed in that same cleanup — see
`context.txt` Section 16.1.

## 18. Installation

Requires Python 3.11+ (this checkout's own `.venv` is 3.13.14 — confirmed
working with the exact pinned versions in `requirements.txt`).
```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (Git Bash) / macOS / Linux:
source .venv/Scripts/activate   # or .venv/bin/activate

pip install -r requirements.txt
```
`models/pose_landmarker_full.task` must exist (committed to the repo — if
missing, download MediaPipe's `pose_landmarker_full.task` and place it
there). Trained model checkpoints (`models/lstm_posture.keras`,
`models/tcn_posture.keras`, `models/rf_posture.joblib` + their label
encoders) are committed — no retraining needed to run the system.

## 19. Requirements

See `requirements.txt`. Notable groups: `tensorflow-cpu` + `scikit-learn`
(LSTM/TCN training and Random Forest), `psutil` (peak-RAM measurement in
the comparison scripts), `joblib` (RF serialization), `scipy` (stride-peak
detection in `src/gait/gait_features.py`). Everything else
(`mediapipe`, `opencv-python`, `numpy`, `pandas`, `matplotlib`, etc.) is
core pose-extraction/data-handling infrastructure.

## 20. How to train

```bash
# 1. (Only if rebuilding from raw video -- datasets/ not in git) process raw
#    videos/datasets into frame-level keypoint CSVs:
python src/data_processing/build_lstm_datasets.py

# 2. Build the sliding-window training set (data/lstm_dataset.npz):
python src/posture/lstm/lstm_dataset.py

# 3. Sanity-check labels (should report 100% of Fall windows contain a real transition frame):
python verify_labels.py

# 4. Train whichever model(s) you need:
python src/posture/lstm/lstm_trainer.py     # -> models/lstm_posture.keras
python src/posture/tcn/tcn_trainer.py       # -> models/tcn_posture.keras
python src/posture/rf/rf_trainer.py         # -> models/rf_posture.joblib
```
`data/`, `datasets/`, and `Testing/` are gitignored — get them from a
teammate/shared drive, or `Testing/`-equivalent footage by following
`docs/sanity_check_clips.md`.

## 21. How to evaluate

```bash
# Heuristic only:
python evaluate_real_footage.py --batch_dir "test_footage/Sanawar Testing 7-22-26" --output_dir results/my_run

# Heuristic + LSTM hybrid:
python hybrid_evaluate.py --batch_dir "test_footage/Sanawar Testing 7-22-26" --output_dir results/my_run

# LSTM vs TCN:
python compare_tcn_lstm.py --batch_dir "test_footage/Sanawar Testing 7-22-26" --output_dir results/my_run

# LSTM vs TCN vs Random Forest (the full picture):
python compare_all_models.py --batch_dir "test_footage/Sanawar Testing 7-22-26" --output_dir results/my_run
```
Each writes a markdown report + per-window CSV(s) to `--output_dir`.

## 22. How to run inference

```bash
# Live webcam, hybrid mode (heuristic OR LSTM):
python realtime_fall_detection.py

# A specific camera / replay a video file as if live:
python realtime_fall_detection.py --input 1
python realtime_fall_detection.py --input "test_footage/Sanawar Testing 7-22-26/Chair_fall.mp4"

# Heuristic only / headless:
python realtime_fall_detection.py --no-lstm
python realtime_fall_detection.py --no-display
```
Tune alert sensitivity with `--alert-window`/`--alert-min-hits`/`--alert-hold`.
Wire a real notification via the `on_alert(event: dict)` callback to
`realtime_fall_detection.run()`. See `docs/TCN_IMPLEMENTATION_NOTES.md`/
`context.txt` Section 6 for details.

## 23. How to test

```bash
python -m unittest tests.test_lstm_pipeline tests.test_posture_pipeline tests.test_gait_risk tests.test_rf_classifier -v
```
66 tests total (21 LSTM pipeline + 16 posture pipeline + 19 gait-risk + 10
Random Forest, per `grep -c "    def test_" tests/*.py`): LSTM/posture
pipeline tests, gait-risk tests (contract, signal-direction regression
checks, input validation, NaN/Inf/occlusion robustness, and an integration
check against real extracted keypoints), and Random Forest tests
(checkpoint loading, the `n_jobs=1` inference fix, prediction determinism,
`fall_confirm_frames`, and the summary feature-representation path). Some
tests are skipped if a given model checkpoint is missing. Verified passing
(66/66) as of the August 2026 cleanup audit (`context.txt` Section 16).

## 24. Known limitations

- **`assess_risk()`'s gait signals are not clinically validated.** No
  dataset with real fall-risk outcomes exists for this project (see
  `docs/GAIT_DATA_ASSESSMENT.md`) — validation is limited to synthetic
  steady-vs-unsteady walking (confirms signals move in the expected
  *direction*) and a crash/plausibility smoke test on real but unlabeled
  footage. Every risk-mapping threshold is heuristic and marked
  `"calibrated": False`.
- **TCN fall-recall regression on the Sanawar set after a MediaPipi
  extraction-pipeline change** (VIDEO-mode tracking, merged from `main`):
  87.5% -> 75.0% fall recall, isolated as unrelated to the class-weighting
  fix and currently unexplained — see `docs/TCN_REGRESSION_REPORT.md`
  Limitations.
- **8 and 17 labelled real clips are a small evaluation set** for either
  test set individually — one flipped clip meaningfully swings any
  per-clip recall metric.
- **Random Forest has no temporal inductive bias** (the window is
  flattened, discarding explicit sequence structure) and still shows a
  visible train/val gap (92%/67%) even after pruning — it may be relying
  more on memorized spatial poses than genuine motion understanding.
- **No YOLO/object-detection layer or structured multi-signal event
  schema exists yet** — planned, not started (see
  `docs/IMPLEMENTATION_PLAN.md` Section 5).

## 25. Current status

TCN/LSTM/RF fall-detection pipeline: complete, cross-validated, and
compared on two real-footage test sets. Gait/fall-risk module: first-pass
rule-based implementation complete and unit-tested, explicitly not
clinically validated. Real-time hybrid detection: production-usable.
Integration of gait risk + a future object-detection layer into one
structured event schema: not started (deliberately sequenced after the
per-branch work lands — see `docs/IMPLEMENTATION_PLAN.md` Section 5).

## 26. Future work

- Real gait-risk validation data (public dataset or new self-recorded
  footage) to actually calibrate `src/gait/`'s thresholds — see
  `docs/GAIT_DATA_ASSESSMENT.md` "Next steps."
- Investigate the post-merge TCN fall-recall regression (Section 24).
- A 3-way ensemble/voting gate (heuristic + best neural model + RF), since
  TCN and RF each win on a different real-footage test set.
- YOLO object-detection layer (`YOLO_fatima` branch) and the structured
  event schema that eventually combines heuristic/temporal-model/YOLO/gait
  output for an LLM reasoning layer (`docs/IMPLEMENTATION_PLAN.md` Section 5).
- TFLite/TensorRT export for a genuine on-device Jetson latency/RAM
  comparison, rather than the development-machine numbers in
  `docs/TCN_REGRESSION_REPORT.md`.

## 27. Where to look for more detail

- `context.txt` — full technical/narrative history (why every threshold
  and design choice is what it is).
- `docs/IMPLEMENTATION_PLAN.md` — the multi-branch (TCN/YOLO/GAIT) project
  plan and integration sequencing.
- `docs/TCN_IMPLEMENTATION_NOTES.md` / `docs/TCN_REGRESSION_REPORT.md` —
  TCN architecture, hyperparameter sweeps, and the class-weighting
  regression writeup.
- `docs/GAIT_LITERATURE_REVIEW.md` / `docs/GAIT_DATA_ASSESSMENT.md` — the
  gait/fall-risk module's clinical grounding and honest data limitations.
- `docs/sanity_check_clips.md` / `docs/recording_round2.md` — how to
  record new validation footage.
- `docs/mediapipe_pose_reference.md` — MediaPipe landmark index reference.

# LSTM vs TCN Posture Classifier Comparison

## 1. Overview

This report compares the existing LSTM posture classifier (`src/posture/lstm/`) against a Temporal Convolutional Network (TCN) alternative (`src/posture/tcn/`) trained and evaluated on identical inputs, generated automatically by `compare_tcn_lstm.py`.

## 2. Experimental Setup

- Test clips: 8 labelled clip(s) — Backward_fall, Chair_fall, Fall_and_lie, Far_fall, Occluded_fall, Off_axis_fall, Side_fall, Slow_fall
- Both models consume the identical extracted keypoints per clip (single `extract_keypoints()` pass, shared between both models).
- Both models use their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect the raw per-window architecture decision for each model.

## 3. Dataset Used

- **Checkpoints evaluated this run**: LSTM = `models\lstm_posture_retrained.keras`, TCN = `models\tcn_posture.keras` (pass `--lstm-model`/`--tcn-model` to point this script at a different checkpoint; whichever paths are printed here are the actual files this report's numbers came from).
- **TCN training data**: `data/lstm_dataset.npz` (sliding windows of `lstm_features`-normalized pose keypoints; see `src/posture/lstm/lstm_dataset.py`), built from the raw footage under `data/ADL`/`data/Fall` via `src/data_processing/build_ur_dataset_from_data_root.py`, then trained with `src/posture/tcn/tcn_trainer.py`.
- **LSTM training data**: if the LSTM checkpoint above is `models/lstm_posture.keras` (the default, pre-existing, already-committed file), it was NOT retrained for this comparison and its original training data predates this session -- read this as "pre-existing LSTM vs. freshly trained TCN," not a controlled same-data ablation. Any other path (e.g. `lstm_posture_retrained.keras`) was trained on the exact same `data/lstm_dataset.npz` as the TCN via the unmodified `lstm_trainer.py`, making this a fair, same-data architecture comparison.
- **Evaluation footage**: labelled clips discovered under the `--batch_dir`/`--video` arguments to this script (same ground-truth format as `evaluate_real_footage.py`).

## 4. Model Architectures

- **LSTM**: `Input -> LSTM(64, return_sequences=True) -> Dropout(0.3) -> LSTM(32) -> Dropout(0.3) -> Dense(5, softmax)` (see `src/posture/lstm/lstm_trainer.py::build_model`).
- **TCN**: 4 residual blocks (dilations 1, 2, 4, 8), each with two causal `Conv1D` layers + `LayerNormalization` + ReLU + Dropout, followed by `GlobalAveragePooling1D -> Dense(5, softmax)` (see `src/posture/tcn/tcn_model.py::build_model`).

## 5. Evaluation Methodology

- **Posture accuracy/precision/recall/F1**: computed over every non-ignored ground-truth frame, pooled across all clips, using `sklearn.metrics.classification_report` on the Standing/Sitting/Lying/Unknown vocabulary (same as `evaluate_real_footage.py`'s `POSTURE_CLASSES`).
- **Fall-detection recall**: per-clip TP/FN/FP against the labelled fall window (`get_fall_window`), identical scoring logic to `evaluate_real_footage.score_fall`.
- **Latency**: wall-clock time around each `.predict()` call, mean/median/min/max/p95 across every window in every clip.
- **Parameter count**: `model.count_params()` on the loaded Keras model.
- **Peak RAM**: peak resident-set size (RSS) of this process, sampled every 50ms while each model's full evaluation pass runs (models evaluated sequentially, one at a time, so the two measurements don't share concurrent memory pressure).
- **Per-window detail**: every window's predicted class, ground truth, correctness, and latency is saved to `lstm_per_window.csv` / `tcn_per_window.csv` in the output directory (one row per inference call, per clip).

## 6. Full Comparison Table

| Metric | LSTM | TCN |
|---|---|---|
| Accuracy | 74.1% | 76.9% |
| Macro Precision | 0.354 | 0.232 |
| Macro Recall | 0.283 | 0.215 |
| Macro F1 | 0.314 | 0.223 |
| Fall-detection recall | 75.0% (6/8) | 87.5% (7/8) |
| Fall false positives (clips) | 0 | 0 |
| Latency mean (ms/window) | 216.453 | 106.636 |
| Latency median (ms/window) | 166.515 | 90.979 |
| Latency min (ms/window) | 64.756 | 56.262 |
| Latency max (ms/window) | 1485.422 | 1229.630 |
| Latency p95 (ms/window) | 565.076 | 175.959 |
| Parameter count | 63,013 | 39,365 |
| Peak RAM (MB) | 445.2 | 470.3 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.477 | 0.341 | 0.397 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.938 | 0.793 | 0.860 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.354 | 0.283 | 0.314 | 967 |
| *Weighted avg* | 0.884 | 0.741 | 0.806 | 967 |


### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.000 | 0.000 | 0.000 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.929 | 0.860 | 0.893 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.232 | 0.215 | 0.223 | 967 |
| *Weighted avg* | 0.831 | 0.769 | 0.799 | 967 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 31 | 0 | 34 | 26 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 34 | 42 | 686 | 103 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 46 | 45 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 0 | 23 | 744 | 98 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Per-clip results

| Clip | LSTM acc | LSTM avg latency (ms) | LSTM fall result | TCN acc | TCN avg latency (ms) | TCN fall result |
|---|---|---|---|---|---|---|
| Backward_fall | 25.0 (12/48) | 202.032 | true_positive | 10.4 (5/48) | 100.800 | true_positive |
| Chair_fall | 44.6 (82/184) | 175.870 | true_positive | 56.0 (103/184) | 93.526 | true_positive |
| Fall_and_lie | 82.6 (238/288) | 408.011 | true_positive | 94.8 (273/288) | 94.568 | true_positive |
| Far_fall | 100.0 (66/66) | 173.335 | false_negative | 74.2 (49/66) | 103.835 | false_negative |
| Occluded_fall | 94.4 (102/108) | 163.081 | false_negative | 81.5 (88/108) | 99.713 | true_positive |
| Off_axis_fall | 91.8 (56/61) | 161.523 | true_positive | 98.4 (60/61) | 227.588 | true_positive |
| Side_fall | 97.9 (95/97) | 104.082 | true_positive | 97.9 (95/97) | 130.385 | true_positive |
| Slow_fall | 57.4 (66/115) | 101.790 | true_positive | 61.7 (71/115) | 72.304 | true_positive |



## 7. Discussion

**Recall.** Fall-detection recall was 75.0% for the LSTM (6/8 labelled fall clips detected) versus 87.5% for the TCN (7/8). Recall matters more than precision for fall detection specifically because a missed fall (false negative) can mean a real injury goes unnoticed until someone happens to check on the person, while a false alarm (false positive) only costs a caregiver a few seconds of checking a monitor -- the two error types are not symmetric in consequence, so the model with higher recall is preferable even if it comes with a lower precision, up to the point where false alarms become frequent enough to cause alert fatigue.

**Latency.** Mean per-window inference time was 216.45 ms for the LSTM and 106.64 ms for the TCN (measured identically: wall-clock time around a single `.predict()` call, same machine, same warm model, same window buffer construction).

**Model size.** The LSTM has 63,013 trainable parameters versus 39,365 for the TCN (TCN is smaller).

**Advantages of the LSTM.** Recurrent state gives it an unbounded (in principle) memory of everything seen since the window started, and it is the architecture already tuned into the rest of this pipeline (warmup frames, consecutive-frame gating in `hybrid_evaluate.py`) -- adopting a different architecture means re-tuning those knobs.

**Advantages of the TCN.** Convolutions over a fixed window are naturally parallelizable across time steps (no sequential recurrence to unroll), which tends to make inference latency more predictable, and the receptive field is explicit and finite (set by the dilation schedule) rather than an emergent property of trained gate weights.

**Trade-offs.** The LSTM's recurrence can capture dependencies longer than the fixed window if state were carried across windows (not currently done here -- both models are evaluated strictly per-window); the TCN's fixed receptive field is a hard ceiling. Conversely, the TCN's residual/dilated-conv structure trains more predictably (no vanishing/exploding gradients through many recurrent steps) and is simpler to reason about layer-by-layer.

**Recommendation for future Hybrid AI work.** Given the existing heuristic-OR-LSTM hybrid in `hybrid_evaluate.py`, and that the TCN showed higher fall-detection recall in the run above, a natural next step is a three-way OR/voting gate (heuristic, LSTM, TCN) or an ensemble that averages the two models' softmax outputs before the argmax, so a fall gets flagged if either sequence model agrees with the heuristic. This is worth re-checking on a larger/more varied evaluation set before committing to it, since the run above is 8 clips from one recording session.

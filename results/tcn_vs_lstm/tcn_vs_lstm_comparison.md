# LSTM vs TCN Posture Classifier Comparison

## 1. Overview

This report compares the existing LSTM posture classifier (`src/posture/lstm/`) against a Temporal Convolutional Network (TCN) alternative (`src/posture/tcn/`) trained and evaluated on identical inputs, generated automatically by `compare_tcn_lstm.py`.

## 2. Experimental Setup

- Test clips: 8 labelled clip(s) — Backward_fall, Chair_fall, Fall_and_lie, Far_fall, Occluded_fall, Off_axis_fall, Side_fall, Slow_fall
- Both models consume the identical extracted keypoints per clip (single `extract_keypoints()` pass, shared between both models).
- Both models use their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect the raw per-window architecture decision for each model.

## 3. Dataset Used

- **TCN training data**: `data/lstm_dataset.npz` (sliding windows of `lstm_features`-normalized pose keypoints; see `src/posture/lstm/lstm_dataset.py`), built from the raw footage under `data/ADL`/`data/Fall` via `src/data_processing/build_ur_dataset_from_data_root.py`, then trained with `src/posture/tcn/tcn_trainer.py`.
- **LSTM being evaluated**: the pre-existing, already-committed `models/lstm_posture.keras` -- it was NOT retrained for this comparison (this script evaluates the existing model as-is, per the task's own instruction to use "the existing LSTM model"). Its original training data predates this session and isn't necessarily identical to `data/lstm_dataset.npz` above, so this comparison should be read as "pre-existing LSTM vs. freshly trained TCN on this new data" rather than a fully controlled same-training-data ablation. Retraining the LSTM on the exact same `data/lstm_dataset.npz` (via the existing, unmodified `lstm_trainer.py`) would remove this caveat if a stricter architecture-only comparison is needed later.
- **Evaluation footage**: labelled clips discovered under the `--batch_dir`/`--video` arguments to this script (same ground-truth format as `evaluate_real_footage.py`).

## 4. Model Architectures

- **LSTM**: `Input -> LSTM(64, return_sequences=True) -> Dropout(0.3) -> LSTM(32) -> Dropout(0.3) -> Dense(5, softmax)` (see `src/posture/lstm/lstm_trainer.py::build_model`).
- **TCN**: 4 residual blocks (dilations 1, 2, 4, 8), each with two causal `Conv1D` layers + `LayerNormalization` + ReLU + Dropout, followed by `GlobalAveragePooling1D -> Dense(5, softmax)` (see `src/posture/tcn/tcn_model.py::build_model`).

## 5. Evaluation Methodology

- **Posture accuracy/precision/recall/F1**: computed over every non-ignored ground-truth frame, pooled across all clips, using `sklearn.metrics.classification_report` on the Standing/Sitting/Lying/Unknown vocabulary (same as `evaluate_real_footage.py`'s `POSTURE_CLASSES`).
- **Fall-detection recall**: per-clip TP/FN/FP against the labelled fall window (`get_fall_window`), identical scoring logic to `evaluate_real_footage.score_fall`.
- **Latency**: wall-clock time around each `.predict()` call, mean/median/p95 across every window in every clip.
- **Parameter count**: `model.count_params()` on the loaded Keras model.
- **Peak RAM**: peak resident-set size (RSS) of this process, sampled every 50ms while each model's full evaluation pass runs (models evaluated sequentially, one at a time, so the two measurements don't share concurrent memory pressure).
- **Per-window detail**: every window's predicted class, ground truth, correctness, and latency is saved to `lstm_per_window.csv` / `tcn_per_window.csv` in the output directory (one row per inference call, per clip).

## 6. Full Comparison Table

| Metric | LSTM | TCN |
|---|---|---|
| Accuracy | 49.6% | 72.6% |
| Macro Precision | 0.339 | 0.390 |
| Macro Recall | 0.252 | 0.296 |
| Macro F1 | 0.277 | 0.336 |
| Fall-detection recall | 75.0% (6/8) | 87.5% (7/8) |
| Fall false positives (clips) | 0 | 0 |
| Latency mean (ms/window) | 56.342 | 55.437 |
| Latency median (ms/window) | 55.609 | 54.331 |
| Latency p95 (ms/window) | 60.027 | 58.770 |
| Parameter count | 63,013 | 39,365 |
| Peak RAM (MB) | 443.6 | 469.1 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.407 | 0.505 | 0.451 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.950 | 0.502 | 0.657 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.339 | 0.252 | 0.277 | 967 |
| *Weighted avg* | 0.888 | 0.496 | 0.630 | 967 |


### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.623 | 0.418 | 0.500 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.938 | 0.768 | 0.844 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.390 | 0.296 | 0.336 | 967 |
| *Weighted avg* | 0.898 | 0.726 | 0.802 | 967 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 46 | 22 | 23 | 0 |
| **Sitting** | 0 | 0 | 0 | 11 |
| **Lying** | 67 | 102 | 434 | 262 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 38 | 10 | 33 | 10 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 23 | 49 | 664 | 129 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Per-clip results

| Clip | LSTM acc | LSTM avg latency (ms) | LSTM fall result | TCN acc | TCN avg latency (ms) | TCN fall result |
|---|---|---|---|---|---|---|
| Backward_fall | 31.2 (15/48) | 61.232 | false_negative | 8.3 (4/48) | 58.648 | true_positive |
| Chair_fall | 19.6 (36/184) | 58.243 | false_negative | 51.6 (95/184) | 54.662 | true_positive |
| Fall_and_lie | 15.3 (44/288) | 55.536 | true_positive | 73.3 (211/288) | 54.166 | true_positive |
| Far_fall | 100.0 (66/66) | 55.299 | true_positive | 100.0 (66/66) | 54.217 | false_negative |
| Occluded_fall | 81.5 (88/108) | 55.544 | true_positive | 93.5 (101/108) | 54.083 | true_positive |
| Off_axis_fall | 70.5 (43/61) | 55.924 | true_positive | 96.7 (59/61) | 54.048 | true_positive |
| Side_fall | 100.0 (97/97) | 55.439 | true_positive | 100.0 (97/97) | 60.995 | true_positive |
| Slow_fall | 79.1 (91/115) | 55.324 | true_positive | 60.0 (69/115) | 55.585 | true_positive |



## 7. Discussion

**Recall.** Fall-detection recall was 75.0% for the LSTM (6/8 labelled fall clips detected) versus 87.5% for the TCN (7/8). Recall matters more than precision for fall detection specifically because a missed fall (false negative) can mean a real injury goes unnoticed until someone happens to check on the person, while a false alarm (false positive) only costs a caregiver a few seconds of checking a monitor -- the two error types are not symmetric in consequence, so the model with higher recall is preferable even if it comes with a lower precision, up to the point where false alarms become frequent enough to cause alert fatigue.

**Latency.** Mean per-window inference time was 56.34 ms for the LSTM and 55.44 ms for the TCN (measured identically: wall-clock time around a single `.predict()` call, same machine, same warm model, same window buffer construction).

**Model size.** The LSTM has 63,013 trainable parameters versus 39,365 for the TCN (TCN is smaller).

**Advantages of the LSTM.** Recurrent state gives it an unbounded (in principle) memory of everything seen since the window started, and it is the architecture already tuned into the rest of this pipeline (warmup frames, consecutive-frame gating in `hybrid_evaluate.py`) -- adopting a different architecture means re-tuning those knobs.

**Advantages of the TCN.** Convolutions over a fixed window are naturally parallelizable across time steps (no sequential recurrence to unroll), which tends to make inference latency more predictable, and the receptive field is explicit and finite (set by the dilation schedule) rather than an emergent property of trained gate weights.

**Trade-offs.** The LSTM's recurrence can capture dependencies longer than the fixed window if state were carried across windows (not currently done here -- both models are evaluated strictly per-window); the TCN's fixed receptive field is a hard ceiling. Conversely, the TCN's residual/dilated-conv structure trains more predictably (no vanishing/exploding gradients through many recurrent steps) and is simpler to reason about layer-by-layer.

**Recommendation for future Hybrid AI work.** Given the existing heuristic-OR-LSTM hybrid in `hybrid_evaluate.py`, and that the TCN showed higher fall-detection recall in the run above, a natural next step is a three-way OR/voting gate (heuristic, LSTM, TCN) or an ensemble that averages the two models' softmax outputs before the argmax, so a fall gets flagged if either sequence model agrees with the heuristic. This is worth re-checking on a larger/more varied evaluation set before committing to it, since the run above is 8 clips from one recording session.

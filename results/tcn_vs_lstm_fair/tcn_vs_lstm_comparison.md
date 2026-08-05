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
| Accuracy | 72.8% | 79.1% |
| Macro Precision | 0.343 | 0.489 |
| Macro Recall | 0.294 | 0.312 |
| Macro F1 | 0.315 | 0.368 |
| Fall-detection recall | 87.5% (7/8) | 75.0% (6/8) |
| Fall false positives (clips) | 0 | 0 |
| Latency mean (ms/window) | 87.578 | 85.198 |
| Latency median (ms/window) | 83.822 | 82.719 |
| Latency min (ms/window) | 54.543 | 55.322 |
| Latency max (ms/window) | 335.175 | 816.708 |
| Latency p95 (ms/window) | 127.483 | 119.427 |
| Parameter count | 63,013 | 39,365 |
| Peak RAM (MB) | 440.5 | 464.1 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.394 | 0.407 | 0.400 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.977 | 0.771 | 0.862 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.343 | 0.294 | 0.315 | 967 |
| *Weighted avg* | 0.911 | 0.728 | 0.809 | 967 |


### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 1.000 | 0.407 | 0.578 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.955 | 0.842 | 0.895 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.489 | 0.312 | 0.368 | 967 |
| *Weighted avg* | 0.949 | 0.791 | 0.855 | 967 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 37 | 0 | 5 | 49 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 57 | 60 | 667 | 81 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 37 | 0 | 23 | 31 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 0 | 17 | 728 | 120 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Per-clip results

| Clip | LSTM acc | LSTM avg latency (ms) | LSTM fall result | TCN acc | TCN avg latency (ms) | TCN fall result |
|---|---|---|---|---|---|---|
| Backward_fall | 8.3 (4/48) | 75.421 | true_positive | 12.5 (6/48) | 110.099 | false_negative |
| Chair_fall | 23.4 (43/184) | 91.224 | true_positive | 47.8 (88/184) | 74.680 | true_positive |
| Fall_and_lie | 89.2 (257/288) | 85.064 | true_positive | 92.0 (265/288) | 85.291 | true_positive |
| Far_fall | 100.0 (66/66) | 110.866 | false_negative | 100.0 (66/66) | 66.791 | false_negative |
| Occluded_fall | 100.0 (108/108) | 77.193 | true_positive | 100.0 (108/108) | 104.074 | true_positive |
| Off_axis_fall | 98.4 (60/61) | 102.211 | true_positive | 98.4 (60/61) | 78.298 | true_positive |
| Side_fall | 97.9 (95/97) | 91.924 | true_positive | 97.9 (95/97) | 71.449 | true_positive |
| Slow_fall | 61.7 (71/115) | 77.306 | true_positive | 67.0 (77/115) | 96.081 | true_positive |



## 7. Discussion

**Recall.** Fall-detection recall was 87.5% for the LSTM (7/8 labelled fall clips detected) versus 75.0% for the TCN (6/8). Recall matters more than precision for fall detection specifically because a missed fall (false negative) can mean a real injury goes unnoticed until someone happens to check on the person, while a false alarm (false positive) only costs a caregiver a few seconds of checking a monitor -- the two error types are not symmetric in consequence, so the model with higher recall is preferable even if it comes with a lower precision, up to the point where false alarms become frequent enough to cause alert fatigue.

**Latency.** Mean per-window inference time was 87.58 ms for the LSTM and 85.20 ms for the TCN (measured identically: wall-clock time around a single `.predict()` call, same machine, same warm model, same window buffer construction).

**Model size.** The LSTM has 63,013 trainable parameters versus 39,365 for the TCN (TCN is smaller).

**Advantages of the LSTM.** Recurrent state gives it an unbounded (in principle) memory of everything seen since the window started, and it is the architecture already tuned into the rest of this pipeline (warmup frames, consecutive-frame gating in `hybrid_evaluate.py`) -- adopting a different architecture means re-tuning those knobs.

**Advantages of the TCN.** Convolutions over a fixed window are naturally parallelizable across time steps (no sequential recurrence to unroll), which tends to make inference latency more predictable, and the receptive field is explicit and finite (set by the dilation schedule) rather than an emergent property of trained gate weights.

**Trade-offs.** The LSTM's recurrence can capture dependencies longer than the fixed window if state were carried across windows (not currently done here -- both models are evaluated strictly per-window); the TCN's fixed receptive field is a hard ceiling. Conversely, the TCN's residual/dilated-conv structure trains more predictably (no vanishing/exploding gradients through many recurrent steps) and is simpler to reason about layer-by-layer.

**Recommendation for future Hybrid AI work.** Given the existing heuristic-OR-LSTM hybrid in `hybrid_evaluate.py`, and that the LSTM showed higher fall-detection recall in the run above, a natural next step is a three-way OR/voting gate (heuristic, LSTM, TCN) or an ensemble that averages the two models' softmax outputs before the argmax, so a fall gets flagged if either sequence model agrees with the heuristic. This is worth re-checking on a larger/more varied evaluation set before committing to it, since the run above is 8 clips from one recording session.

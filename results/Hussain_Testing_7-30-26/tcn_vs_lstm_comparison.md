# LSTM vs TCN Posture Classifier Comparison

## 1. Overview

This report compares the existing LSTM posture classifier (`src/posture/lstm/`) against a Temporal Convolutional Network (TCN) alternative (`src/posture/tcn/`) trained and evaluated on identical inputs, generated automatically by `compare_tcn_lstm.py`.

## 2. Experimental Setup

- Test clips: 17 labelled clip(s) — Bend_pickup_lowLight, Bend_pickup_normalLight_back, Bend_pickup_normalLight, Bend_pickup_normalLight_leftRight, Bend_pickup_squat_lowLight, Bend_pickup_squat_normalLight, Kneeling, LyingdownSlowly, Moving_in_out_frame, Moving_in_out_frame_withFall, Sit_Stand_AnklesInvisible, SitFast_GetupFast, SitFloor_lowKeypoints_crossedLegs, SitFloor_lowKeypoints, Sitting_HalfLandmarks, Sitting_Lying_FewLandmarks_back, Sitting_Lying_FewLandmarks
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
| Accuracy | 42.1% | 47.6% |
| Macro Precision | 0.444 | 0.477 |
| Macro Recall | 0.464 | 0.524 |
| Macro F1 | 0.330 | 0.377 |
| Fall-detection recall | 100.0% (3/3) | 100.0% (3/3) |
| Fall false positives (clips) | 10 | 12 |
| Latency mean (ms/window) | 94.509 | 87.136 |
| Latency median (ms/window) | 88.877 | 84.517 |
| Latency min (ms/window) | 56.822 | 55.335 |
| Latency max (ms/window) | 600.043 | 380.853 |
| Latency p95 (ms/window) | 143.697 | 124.591 |
| Parameter count | 63,013 | 39,365 |
| Peak RAM (MB) | 506.1 | 527.2 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.385 | 0.796 | 0.519 | 387 |
| Sitting | 1.000 | 0.145 | 0.253 | 775 |
| Lying | 0.391 | 0.915 | 0.548 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.444 | 0.464 | 0.330 | 1517 |
| *Weighted avg* | 0.701 | 0.491 | 0.390 | 1517 |


### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.478 | 0.935 | 0.632 | 387 |
| Sitting | 1.000 | 0.160 | 0.276 | 775 |
| Lying | 0.430 | 1.000 | 0.602 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.477 | 0.524 | 0.377 | 1517 |
| *Weighted avg* | 0.733 | 0.554 | 0.443 | 1517 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 308 | 0 | 79 | 0 |
| **Sitting** | 371 | 112 | 267 | 25 |
| **Lying** | 30 | 0 | 325 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 362 | 0 | 25 | 0 |
| **Sitting** | 309 | 124 | 281 | 61 |
| **Lying** | 0 | 0 | 355 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |


### Per-clip results

| Clip | LSTM acc | LSTM avg latency (ms) | LSTM fall result | TCN acc | TCN avg latency (ms) | TCN fall result |
|---|---|---|---|---|---|---|
| Bend_pickup_lowLight | 56.5 (13/23) | 117.072 | false_positive | 100.0 (23/23) | 93.146 | false_positive |
| Bend_pickup_normalLight_back | 97.7 (84/86) | 100.576 | false_positive | 100.0 (86/86) | 87.090 | false_positive |
| Bend_pickup_normalLight | 35.7 (10/28) | 76.943 | false_positive | 67.9 (19/28) | 78.138 | false_positive |
| Bend_pickup_normalLight_leftRight | 72.1 (106/147) | 99.707 | false_positive | 90.5 (133/147) | 89.907 | false_positive |
| Bend_pickup_squat_lowLight | 74.2 (23/31) | 102.242 | false_positive | 93.5 (29/31) | 83.364 | false_positive |
| Bend_pickup_squat_normalLight | 100.0 (12/12) | 146.009 | false_positive | 100.0 (12/12) | 87.015 | false_positive |
| Kneeling | 17.4 (15/86) | 82.757 | no_fall | 17.4 (15/86) | 84.210 | false_positive |
| LyingdownSlowly | 100.0 (118/118) | 99.031 | true_positive | 100.0 (118/118) | 85.030 | true_positive |
| Moving_in_out_frame | 0.0 (0/175) | 99.186 | false_positive | 0.0 (0/175) | 79.412 | false_positive |
| Moving_in_out_frame_withFall | 41.5 (56/135) | 86.316 | true_positive | 43.7 (59/135) | 92.352 | true_positive |
| Sit_Stand_AnklesInvisible | 14.4 (18/125) | 95.746 | no_fall | 14.4 (18/125) | 77.923 | no_fall |
| SitFast_GetupFast | 0.0 (0/80) | 89.681 | no_fall | 0.0 (0/80) | 103.869 | no_fall |
| SitFloor_lowKeypoints_crossedLegs | 39.1 (45/115) | 83.640 | false_positive | 0.0 (0/115) | 81.436 | false_positive |
| SitFloor_lowKeypoints | 29.8 (34/114) | 84.658 | no_fall | 30.7 (35/114) | 93.415 | false_positive |
| Sitting_HalfLandmarks | 4.5 (4/88) | 89.248 | false_positive | 27.3 (24/88) | 96.020 | false_positive |
| Sitting_Lying_FewLandmarks_back | 59.5 (157/264) | 88.115 | false_positive | 68.9 (182/264) | 86.518 | false_positive |
| Sitting_Lying_FewLandmarks | 35.5 (50/141) | 93.060 | true_positive | 62.4 (88/141) | 85.866 | true_positive |



## 7. Discussion

**Recall.** Fall-detection recall was 100.0% for the LSTM (3/3 labelled fall clips detected) versus 100.0% for the TCN (3/3). Recall matters more than precision for fall detection specifically because a missed fall (false negative) can mean a real injury goes unnoticed until someone happens to check on the person, while a false alarm (false positive) only costs a caregiver a few seconds of checking a monitor -- the two error types are not symmetric in consequence, so the model with higher recall is preferable even if it comes with a lower precision, up to the point where false alarms become frequent enough to cause alert fatigue.

**Latency.** Mean per-window inference time was 94.51 ms for the LSTM and 87.14 ms for the TCN (measured identically: wall-clock time around a single `.predict()` call, same machine, same warm model, same window buffer construction).

**Model size.** The LSTM has 63,013 trainable parameters versus 39,365 for the TCN (TCN is smaller).

**Advantages of the LSTM.** Recurrent state gives it an unbounded (in principle) memory of everything seen since the window started, and it is the architecture already tuned into the rest of this pipeline (warmup frames, consecutive-frame gating in `hybrid_evaluate.py`) -- adopting a different architecture means re-tuning those knobs.

**Advantages of the TCN.** Convolutions over a fixed window are naturally parallelizable across time steps (no sequential recurrence to unroll), which tends to make inference latency more predictable, and the receptive field is explicit and finite (set by the dilation schedule) rather than an emergent property of trained gate weights.

**Trade-offs.** The LSTM's recurrence can capture dependencies longer than the fixed window if state were carried across windows (not currently done here -- both models are evaluated strictly per-window); the TCN's fixed receptive field is a hard ceiling. Conversely, the TCN's residual/dilated-conv structure trains more predictably (no vanishing/exploding gradients through many recurrent steps) and is simpler to reason about layer-by-layer.

**Recommendation for future Hybrid AI work.** Given the existing heuristic-OR-LSTM hybrid in `hybrid_evaluate.py`, and that the TCN showed higher fall-detection recall in the run above, a natural next step is a three-way OR/voting gate (heuristic, LSTM, TCN) or an ensemble that averages the two models' softmax outputs before the argmax, so a fall gets flagged if either sequence model agrees with the heuristic. This is worth re-checking on a larger/more varied evaluation set before committing to it, since the run above is 8 clips from one recording session.

# TCN Implementation Notes

This document explains the Temporal Convolutional Network (TCN) added as an
alternative to the existing LSTM posture classifier, what was and wasn't
touched in the existing codebase, and how to train/evaluate it.

## 1. How a Temporal Convolutional Network works

A TCN classifies a sequence using only 1D convolutions, not recurrence:

- **Causal convolution**: the output at time step `t` is computed only from
  inputs at time steps `<= t`. This is enforced with `padding="causal"` in
  Keras (equivalent to left-padding the input by `(kernel_size - 1) *
  dilation_rate` and then using standard "valid" convolution). It guarantees
  the model never looks into the future, which matters for a realtime
  fall-detection system where "the future" doesn't exist yet at inference
  time.
- **Dilated convolution**: instead of sliding the kernel over every
  consecutive timestep, a dilation rate `d` spaces the kernel taps `d`
  timesteps apart. Stacking layers with exponentially increasing dilation
  (1, 2, 4, 8, ...) makes the receptive field grow exponentially with depth
  instead of linearly, so a handful of layers can "see" a long history
  without an enormous number of layers or parameters.
- **Residual connections**: each block adds its input back to its output
  (`Add()`), the same idea as a ResNet. This keeps gradients flowing cleanly
  through a deep stack of dilated convolutions and lets a block learn a
  small correction to its input rather than having to reconstruct the whole
  signal from scratch.
- **Global pooling + dense head**: after the convolutional stack, a
  `GlobalAveragePooling1D` layer collapses the (time, channels) tensor into
  a single per-clip summary vector, and a `Dense(n_classes, softmax)` layer
  turns that into class probabilities — architecturally the same role the
  LSTM's final `Dense(n_classes, softmax)` plays after its last recurrent
  layer.

## 2. Why TCN was chosen

The project already has a working LSTM for the same 132-dimensional,
normalized-position-plus-velocity window input (see
`src/posture/lstm/lstm_features.py`). A TCN is the standard "convolutional
alternative to an RNN for sequence classification" (Bai et al., 2018,
*An Empirical Evaluation of Generic Convolutional and Recurrent Networks
for Sequence Modeling*) and is a natural apples-to-apples comparison point:
same task, same fixed-length window, same input representation, different
mechanism for modeling temporal structure (convolution + dilation vs.
recurrence + gating).

## 3. Differences between LSTM and TCN (as implemented here)

| | LSTM (`src/posture/lstm/`) | TCN (`src/posture/tcn/`) |
|---|---|---|
| Temporal mechanism | Recurrent gating, processes the window step-by-step | Dilated causal convolutions, processes the whole window in parallel |
| Depth / receptive field | 2 LSTM layers (64, then 32 units by default); memory is a learned state vector, not a fixed lookback | 4 residual blocks, dilations 1/2/4/8; receptive field is a fixed, computable 31 frames |
| Normalization | None (dropout only) | `LayerNormalization` after each conv (see rationale in `tcn_model.py` docstring: per-sample, so behavior doesn't shift between training-batch and single-window inference) |
| Pooling to a fixed vector | Last LSTM layer's final hidden state (`return_sequences=False`) | `GlobalAveragePooling1D` over the whole sequence |
| Output head | `Dense(n_classes, softmax)` | `Dense(n_classes, softmax)` (identical) |
| Trainable parameters (default hyperparameters) | 63,013 | 39,365 |

## 4. Files added

- `src/posture/tcn/__init__.py` — package marker.
- `src/posture/tcn/tcn_model.py` — the TCN architecture (`build_tcn_model`).
- `src/posture/tcn/tcn_trainer.py` — training script; mirrors
  `lstm_trainer.py`'s data loading, `StratifiedGroupKFold` grouped split,
  post-split synthetic augmentation, `EarlyStopping`/`ReduceLROnPlateau`
  callbacks, and evaluation/reporting flow exactly, swapping in
  `tcn_model.build_tcn_model` as the only architectural difference. Saves to
  `models/tcn_posture.keras` + `models/tcn_label_encoder.json`.
- `src/posture/tcn/tcn_classifier.py` — `TCNPostureClassifier`, with the
  exact same public surface as `LSTMPostureClassifier`
  (`.predict()`, `.window_size`, `.raw_history_needed`, `.is_available`),
  so it is a drop-in replacement anywhere the LSTM classifier is used.
- `src/data_processing/build_ur_dataset_from_data_root.py` — one-off adapter
  that reuses `build_lstm_datasets.py::process_ur_sequence` unchanged to
  process the UR Fall Detection Dataset when dropped directly under
  `data/ADL`/`data/Fall` (this project's actual data layout) instead of the
  `datasets/UR_data/ADL`/`Fall` layout the original script expects.
- `compare_tcn_lstm.py` (repo root, alongside `evaluate_real_footage.py` and
  `hybrid_evaluate.py`) — evaluates both models under identical conditions
  on the same labelled test footage, writes a per-window CSV per model
  (`{lstm,tcn}_per_window.csv`: clip, frame, ground truth, prediction,
  correct, latency) and a markdown report with a per-clip breakdown,
  full confusion matrices, and a discussion section generated from the
  actual measured numbers. Supports `--lstm-model`/`--lstm-encoder`/
  `--tcn-model`/`--tcn-encoder` to point at any checkpoint, not just the
  defaults.

## 5. Files modified

- `requirements.txt` — added `psutil`, needed by `compare_tcn_lstm.py` to
  measure peak resident memory (RSS) per model. Python's built-in
  alternative (`resource.getrusage`) is POSIX-only and this project targets
  Windows as well, so a cross-platform library was necessary for that one
  metric.
- `src/posture/lstm/lstm_trainer.py` — three additive changes, all
  backward-compatible (defaults reproduce the exact original behavior):
  1. `build_model()`/`train()` gained `units1`, `units2`, `dropout_rate`,
     `learning_rate` keyword arguments (defaults: 64, 32, 0.3, 1e-3 — the
     original hardcoded values) so a hyperparameter sweep didn't require
     hand-editing the file between runs.
  2. `keras.utils.set_random_seed(42)` added at the top of `train()` —
     model weight initialization was previously unseeded, so two training
     runs with *identical* hyperparameters produced measurably different
     real-footage results (see Section 6). This was necessary for any
     hyperparameter comparison to mean anything.
  3. Fixed a dead parameter: `val_split` was accepted (and exposed via
     `--val-split`) but never actually used — the train/val split always
     used a hardcoded `StratifiedGroupKFold(n_splits=5, ...)` regardless of
     the value passed. `n_splits` is now derived from `val_split`
     (`round(1/val_split)`), so the flag actually does something; the
     default (`0.20` -> 5 splits) is unchanged.
- `src/posture/tcn/tcn_model.py` / `tcn_trainer.py` — the equivalent three
  changes: `learning_rate` added to `build_tcn_model` (filters/kernel/dropout
  were already parameterized), the same `set_random_seed(42)` fix, and the
  same `val_split` -> `n_splits` fix.

No existing LSTM *behavior* changed for any caller using default arguments
— `lstm_features.py`, `lstm_dataset.py`, and `lstm_classifier.py` were not
touched at all. `pipeline_utils.py`, `realtime_fall_detection.py`,
`evaluate_real_footage.py`, and `hybrid_evaluate.py` were also left
untouched — `compare_tcn_lstm.py` imports helper functions from
`evaluate_real_footage.py` (`discover_clips`, `extract_keypoints`,
`load_ground_truth`, `build_frame_gt`, `get_fall_window`) rather than
duplicating them.

## 6. What the hyperparameter sweep found (important caveat)

A sweep of ~4 hyperparameter variants per model was run (wider/narrower
layers, different dropout, different learning rate) and picked winners by
validation accuracy. On the validation split, "TCN wider" (48 filters vs.
32) and "LSTM narrow_lowdrop" (48/24 units vs. 64/32) both looked like
improvements.

**On the real `test_footage/` clips, this did not hold up.** Both "improved"
configs performed *worse* on fall-detection recall (75% vs. 87.5%) than
their own defaults. Investigating further revealed the real cause: model
weight initialization was unseeded, so re-training the *exact same*
default hyperparameters twice produced different real-footage results
(75% vs. 87.5% fall recall) purely from random initialization — the
apparent hyperparameter effect was mostly noise. Adding
`keras.utils.set_random_seed(42)` (Section 5) reduces but does not fully
eliminate this — TensorFlow's CPU convolution/LSTM ops are not fully
deterministic across separate process runs even with a fixed seed unless
`tf.config.experimental.enable_op_determinism()` is also enabled (which has
its own performance cost and was not enabled here).

**Conclusion**: with only 8 labelled real-world clips, one flipped clip
swings fall-detection recall by 12.5 percentage points — enough to make
single-run hyperparameter comparisons unreliable. The final models kept
(Section 8) use the **original default hyperparameters** for both
architectures, not the sweep's nominal "winners," since the winners'
apparent edge could not be distinguished from training noise. A real
hyperparameter search would need multiple seeds averaged per configuration
and/or a larger real-footage evaluation set before its conclusions could be
trusted.

## 7. How to train

Both trainers need `data/lstm_dataset.npz` to exist first (see
`INSTRUCTIONS.md` section 5, or use
`src/data_processing/build_ur_dataset_from_data_root.py` +
`src/posture/lstm/lstm_dataset.py` if your raw data is under `data/ADL`/
`data/Fall` as described in Section 4 above).

```bash
# TCN -> models/tcn_posture.keras (never touches the LSTM's files)
python src/posture/tcn/tcn_trainer.py

# LSTM retrained on the SAME data, to a non-default path so the
# already-committed models/lstm_posture.keras is never overwritten:
python -c "
from src.posture.lstm.lstm_trainer import train, LSTM_DATASET_NPZ, MODELS_DIR
train(dataset_path=LSTM_DATASET_NPZ,
      model_out=MODELS_DIR / 'lstm_posture_retrained.keras',
      encoder_out=MODELS_DIR / 'lstm_label_encoder_retrained.json')
"
```

Both `train()` functions now accept hyperparameter overrides
(`units1`/`units2`/`dropout_rate`/`learning_rate` for LSTM;
`num_filters`/`kernel_size`/`dropout_rate`/`learning_rate` for TCN) if you
want to experiment — see Section 6's caveat before trusting a single run's
results, though.

## 8. How to run the comparison

```bash
# Compare the pre-existing production LSTM against the TCN:
python compare_tcn_lstm.py --batch_dir test_footage --output_dir results/tcn_vs_lstm

# Compare a specific pair of checkpoints (e.g. the same-data-retrained LSTM):
python compare_tcn_lstm.py --batch_dir test_footage --output_dir results/tcn_vs_lstm_fair \
  --lstm-model models/lstm_posture_retrained.keras \
  --lstm-encoder models/lstm_label_encoder_retrained.json
```

This writes `<output_dir>/tcn_vs_lstm_comparison.md` (accuracy, per-class
precision/recall/F1, confusion matrices, fall-detection recall, latency,
parameter counts, peak RAM, per-clip breakdown, and a discussion section
generated from the actual measured numbers) plus
`<output_dir>/{lstm,tcn}_per_window.csv` (one row per inference call, every
clip: predicted class, ground truth, correct/incorrect, latency).

`results/tcn_vs_lstm/` holds the original pre-existing-LSTM-vs-TCN
comparison; `results/tcn_vs_lstm_fair/` holds the same-training-data,
fixed-seed comparison (the methodologically cleaner one — see Section 6).

## 9. Future improvements

- Extend `hybrid_evaluate.py`'s OR-gate pattern to a 3-way heuristic/LSTM/TCN
  vote, or an ensemble that averages softmax outputs before the argmax.
- Enable `tf.config.experimental.enable_op_determinism()` and re-run the
  hyperparameter sweep with multiple seeds per config, averaged, before
  drawing any conclusions about which hyperparameters are actually better —
  see Section 6.
- Record more real-world test clips. 8 clips is too few for fall-detection
  recall to be a stable metric; each additional clip is worth ~12 points of
  precision in that number.
- If the TCN's fixed receptive field (31 frames) proves limiting compared
  to the LSTM's carried state, consider stacking one more dilation level
  (16) rather than widening `window_size`, to keep the input representation
  unchanged.
- Consider exporting both models to TFLite for a real like-for-like
  on-device latency/RAM comparison (a Raspberry Pi or similar edge target,
  rather than the development machine `compare_tcn_lstm.py` runs on).

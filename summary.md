# Summary — 2026-08-01

## What today's session was about
Implementing a Temporal Convolutional Network (TCN) as an alternative to the
existing LSTM posture classifier, training it, retraining the LSTM on the
same data for a fair comparison, running a hyperparameter optimization pass,
and cleaning up the resulting code. Full narrative history is in
`context.txt` Section 13; full architecture/usage docs are in
`TCN_IMPLEMENTATION_NOTES.md`. This file is just today's recap.

## What got built
- **`src/posture/tcn/`** — a complete TCN implementation
  (`tcn_model.py`/`tcn_trainer.py`/`tcn_classifier.py`) mirroring the LSTM
  pipeline's structure: same input (30×132 normalized-position-plus-velocity
  windows), same `StratifiedGroupKFold` split, same synthetic augmentation,
  same callbacks, same public classifier interface
  (`.predict()`/`.window_size`/`.raw_history_needed`/`.is_available`) so it's
  a drop-in replacement anywhere the LSTM classifier is used.
- **`src/data_processing/build_ur_dataset_from_data_root.py`** — a small
  adapter so the raw UR Fall Detection Dataset frames you dropped under
  `data/ADL`/`data/Fall` could be processed into the keypoint CSVs the
  existing dataset builder expects, without modifying that existing script.
- **`compare_tcn_lstm.py`** — evaluates both models under identical
  conditions on `test_footage/`, writes a per-window CSV per model (frame,
  ground truth, prediction, correct, latency) and an auto-generated markdown
  report (accuracy/precision/recall/F1, confusion matrices, fall-detection
  recall, latency, parameter counts, peak RAM, per-clip breakdown, and a
  discussion section written from the actual numbers).

## What got run
1. Extracted MediaPipe keypoints from all 70 raw sequences (11,936 frames)
   under `data/ADL`/`data/Fall`.
2. Built `data/lstm_dataset.npz` — 9,906 windows, 5 classes.
3. Trained the TCN (39,365 params).
4. Retrained the LSTM on the *same* `data/lstm_dataset.npz`
   (`models/lstm_posture_retrained.keras` — a separate file; the production
   `models/lstm_posture.keras` was never touched or overwritten).
5. Ran the comparison on all 8 valid clips in `test_footage/` (a 9th clip,
   `Forward_fall_gt.csv`, has no matching video — `Foward_fall.mp4` is
   missing an "r" — flagged, not renamed).
6. Ran an 8-config hyperparameter sweep (4 LSTM variants, 4 TCN variants).
7. Found the sweep's apparent winners didn't hold up on real footage, traced
   it to unseeded model training, fixed that, and settled on the original
   default hyperparameters as final for both models (see below).
8. Did a code-quality cleanup pass: fixed a dead `val_split` parameter that
   was silently ignored in both trainers, fixed a report section that had
   gone factually stale, removed a duplicated constant and an in-function
   import.

## Final result (`results/tcn_vs_lstm_fair/tcn_vs_lstm_comparison.md`)

| Metric | LSTM (retrained, same data) | TCN |
|---|---|---|
| Accuracy | 74.1% | 76.0% |
| Fall-detection recall | 75.0% (6/8) | **87.5% (7/8)** |
| Parameters | 63,013 | 39,365 |
| Latency mean | 57.9 ms/window | 55.1 ms/window |
| Peak RAM | 442.4 MB | 468.7 MB |

TCN comes out ahead on every measured axis in this run.

## The most important finding wasn't a number — it was a methodology gap
The hyperparameter sweep initially seemed to find real improvements (a wider
TCN, a narrower LSTM) by validation accuracy. Testing those "winners" on
real footage showed the opposite — both **regressed** (fall recall dropped
from 87.5% to 75%). Digging in: neither trainer seeded model weight
initialization, so training the *exact same* default hyperparameters twice
produced different real-footage outcomes purely from random initialization.
Fixed by adding `keras.utils.set_random_seed(42)` to both trainers — this
helps but doesn't fully guarantee bit-exact reproducibility (TensorFlow's
CPU ops have their own non-determinism; full determinism needs
`tf.config.experimental.enable_op_determinism()`, not enabled here).
**Conclusion: the hyperparameter sweep's results are not reliable evidence
of a real improvement** — with only 8 real test clips, one flipped clip is
worth 12.5 points of "recall," which is bigger than the effects being
measured. The final models use the original default hyperparameters for
both architectures, not the sweep's nominal winners.

## Files changed today
**Added:** `src/posture/tcn/` (4 files), `src/data_processing/build_ur_dataset_from_data_root.py`,
`compare_tcn_lstm.py`, `TCN_IMPLEMENTATION_NOTES.md`, `models/tcn_posture.keras`
+ `tcn_label_encoder.json`, `models/lstm_posture_retrained.keras` +
`lstm_label_encoder_retrained.json`, `results/tcn_vs_lstm/`,
`results/tcn_vs_lstm_fair/`, this file, and the `context.txt` Section 13/14
update.

**Modified:** `requirements.txt` (+`psutil`), `src/posture/lstm/lstm_trainer.py`
(hyperparameter knobs, seed fix, `val_split` fix — all additive/backward
compatible), `src/posture/tcn/tcn_model.py` + `tcn_trainer.py` (same three
fixes), `context.txt` (Section 13/14 added).

**Never touched:** `models/lstm_posture.keras`, `models/lstm_label_encoder.json`
(the production LSTM), `lstm_features.py`, `lstm_dataset.py`,
`lstm_classifier.py`, `pipeline_utils.py`, `realtime_fall_detection.py`,
`evaluate_real_footage.py`, `hybrid_evaluate.py`.

## Open items for next time
- `test_footage/Foward_fall.mp4` / `Forward_fall_gt.csv` filename mismatch —
  needs the user to rename one of them.
- Reproducibility gap not fully closed — see "most important finding"
  above. A real hyperparameter conclusion needs multiple seeds averaged per
  config, ideally with `tf.config.experimental.enable_op_determinism()`
  enabled.
- Only 8 labelled real clips exist for evaluation — more clips would matter
  more than more tuning right now.
- Nothing from today has been committed or pushed — all changes are sitting
  in the working tree for review.

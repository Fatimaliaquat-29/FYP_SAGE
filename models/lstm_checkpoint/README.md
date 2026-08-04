# LSTM CHECKPOINT  (reference point, 30 July 2026)

`lstm_posture.keras` + `lstm_label_encoder.json` here are the **known-good
fallback**. If an experiment ends up worse than this, restore from here:

    cp models/lstm_checkpoint/lstm_posture.keras       models/lstm_posture.keras
    cp models/lstm_checkpoint/lstm_label_encoder.json  models/lstm_label_encoder.json

## Measured performance (full hybrid, realtime debounce 4-of-12, vetoes OFF)

| set                                   | result           |
|---------------------------------------|------------------|
| Round-2 held-out (Hussain 7-30-26)    | 9/18 ADL clean, fall detected |
| Round-1 (Sanawar 7-22 + 7-25)         | 9/9 ADL clean, 11/12 falls    |
| Only round-1 fall missed              | Backward_fall    |

Trained on the OLD extraction (RunningMode.IMAGE, no visibility gating, UR
frames timestamped with wall-clock). It is NOT aligned with the current
inference pipeline -- it simply happens to score better than the v2 retrain.

## The v2 retrain (30 July) is NOT kept here

Retraining on the CORRECTED extraction (VIDEO mode, visibility gating, real
timestamps, UP-Fall dropped) scored **6/18** on round-2 -- worse than this
checkpoint's 9/18 -- so it was rolled back. Its weights were lost to a bad
command ordering during that rollback; it is reproducible in ~25 min from
`data/lstm_dataset.npz`, which is the rebuilt (corrected) dataset.

Why it got worse: `build_lstm_datasets.py` generates its posture labels by
calling `classify_posture_and_fall()`, i.e. the LSTM trains on the HEURISTIC's
own output outside the annotated fall windows. It is a distillation of the
rulebook and inherits the rulebook's bend-reads-as-Lying error. Cleaning up the
input features simply let it learn that wrong mapping more faithfully.

Consequence worth remembering: heuristic and LSTM are NOT independent detectors,
so "heuristic OR LSTM" mostly amplifies shared errors rather than covering for
each other.


---

## SUPERSEDED 2 Aug 2026 — v4 is now the active model

Round-3 (`Testing/Hussain Testing 8-2-26`, 6 falls from the deployment camera
setup) settled the choice this checkpoint could not:

| model | vetoes | R2 negatives | R3 falls |
|---|---|---|---|
| this checkpoint | either | 9/18 | 6/6 |
| **v4** (`models/experiments/lstm_v4_round2_gt.keras`) | **ON** | **17/18** | **6/6** |

v4 + `ENABLE_UPRIGHT_VETOES = True` is shipped. This checkpoint remains the
rollback target; restore with the two commands at the top of this file (and set
`ENABLE_UPRIGHT_VETOES = False`, which is the config these numbers were measured under).

Caveat on the 17/18: 13 of those 18 negatives were in v4's training data. On the
5 strictly held-out ones v4 scores 4/5 vs this checkpoint's 2/5. Round-3 is
fully held out, so its 6/6 is clean.

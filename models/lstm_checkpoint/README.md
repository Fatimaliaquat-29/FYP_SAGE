# LSTM CHECKPOINT — currently v5 (round-2 2x oversample), 7 August 2026

`lstm_posture.keras` + `lstm_label_encoder.json` here are the **known-good
fallback**, kept in sync with whatever is the current best-validated model.
If a future experiment ends up worse, restore from here:

    cp models/lstm_checkpoint/lstm_posture.keras       models/lstm_posture.keras
    cp models/lstm_checkpoint/lstm_label_encoder.json  models/lstm_label_encoder.json
    # and set ENABLE_UPRIGHT_VETOES = True in pipeline_utils.py (current config)

## Measured performance (full hybrid, realtime debounce 4-of-12, vetoes ON)

| set | result |
|---|---|
| Round-1 (Sanawar 7-22 + 7-25) | **9/9** ADL clean, **10/12** falls |
| Round-2 held-out (5 clips never in training) | **4/5** clean — only `LyingdownSlowly` still fires |
| Round-2 in-training fall clip | detected |
| Round-3 (6 falls, deployment camera, fully held out) | **6/6**, all caught during the fall transition |

Beats the previous checkpoint (v4) on round-1 (was 8/9, 9/12) and matches it
everywhere else — no metric got worse. Comparison that produced this pick:

| model | R1 ADL | R1 falls | R2-held ADL | R3 falls |
|---|---|---|---|---|
| v4 (previous checkpoint) | 8/9 | 9/12 | 4/5 | 6/6 |
| **v5, round-2 oversampled 2x** | **9/9** | **10/12** | 4/5 | 6/6 |
| v5, round-2 oversampled 3x | 8/9 | 9/12 | **1/5** ⚠️ | 6/6 |

3x was also tried and rejected — validation accuracy dropped (76.9% vs 2x's
81.1%), Sitting recall crashed to 0.38, and it scored *worse than doing
nothing* on the round-2 held-out set. Repeating the same real clips three
times pushed the model into memorizing that specific footage rather than
learning from it. Kept in `models/experiments/` for reference, not shipped.

## How v5 differs from v4

Two changes, both upstream of training, in `src/posture/pipeline_utils.py`
and `src/posture/lstm/lstm_dataset.py`:

1. **Low-confidence frames dropped from LeFD/UR labeling.** The heuristic
   tags every posture decision with which rule fired; four of those tags
   (`fallback_default`, `fallback_height_standing/sitting`,
   `torso_only_standing_hh`) are the rulebook's own explicit last-resort
   guesses. Frames carrying those tags are now excluded from training instead
   of teaching the model a guess — 10.6% of LeFD/UR (5,714/54,002), with
   frames inside an annotated fall window always protected regardless of tag
   (they're anchored to real timing, not the heuristic's opinion). Full
   before/after class-balance table: `docs/data_quality_improvement_plan.md`.
2. **Your own real, human-labeled clips (round-2) are repeated 2x** in the
   training set via `build_dataset(oversample_prefix="r2_",
   oversample_factor=2)`. They're the only frames in the whole dataset with
   genuinely correct labels rather than the heuristic's guess, but at their
   natural ~6% share they were easily drowned out by the much larger public
   dataset. Repeating makes the model actually pay attention to them. Applied
   after the imputation-median computation (so that isn't skewed) and before
   the shuffle.

Net effect: `LyingdownSlowly` (a deliberate lie-down) is still a false
positive — same known issue as before, driven by the LSTM directly rather
than the sustained-lying counter, needs targeted lie-down training examples
or a descent-dynamics gate to fix. Every *bending*-related held-out clip
(the thing this round of work actually targeted) is now clean.

## Full history

- **Original checkpoint (30 Jul 2026):** trained on the old extraction
  (IMAGE mode, no visibility gating, wall-clock UR timestamps). Archived at
  `models/checkpoint_history/lstm_posture_original_30jul.keras` — kept for
  the record, not a live rollback target for anything current.
- **v2 (30 Jul):** retrain on corrected features alone. Scored *worse*
  (6/18 vs the original's 9/18) — the heuristic's own bend-reads-as-Lying
  error got learned more faithfully once the input noise was cleaned up.
  Rolled back; weights lost to a bad command-ordering mistake during that
  rollback (a lesson, see the process note below).
- **v3 (30 Jul):** retrain with the upright-vetoes on for labeling too.
  Still a net loss overall (traded one held-out clip for a lost round-1 ADL
  clip and a lost fall). Preserved: `models/experiments/lstm_v3_vetoes_on.keras`.
- **v4 (2 Aug):** round-2 clips folded into training with real GT labels
  (not heuristic-derived). Round-3 (6 fresh fall clips from the deployment
  camera) settled the comparison: 17/18 vs the original checkpoint's 9/18 on
  round-2 (caveat: 13 of those 18 were in v4's training data; on the 5
  strictly held-out ones, 4/5 vs 2/5). Shipped, but **the physical checkpoint
  files here were never actually updated to v4** — only this README's text
  claimed it. That inconsistency has now been fixed as part of this v5 update;
  worth remembering that "the README says X" and "the files are X" can drift
  apart if only one gets updated. Preserved:
  `models/experiments/lstm_v4_round2_gt.keras`.
- **v5 (7 Aug) — current:** this checkpoint. Low-confidence-frame dropping
  (Phase 1) + round-2 oversampling (Phase 2) of the joint data-quality plan,
  see `docs/data_quality_improvement_plan.md`. 3x tried, rejected, kept in
  `models/experiments/`.

## Structural note, still true as of v5

`build_lstm_datasets.py` still generates LeFD/UR labels by calling
`classify_posture_and_fall()` for anything outside an annotated fall window,
so the LSTM is still fundamentally a distillation of the heuristic there —
v5 makes that distillation less noisy (fewer bad guesses, more real examples
mixed in) but does not remove the ceiling. "Heuristic OR LSTM" is still not
two independent detectors. Full writeup:
`docs/data_quality_improvement_plan.md` and the `lstm-is-distilled-from-heuristic`
project memory note.

## Process note (unchanged from before)

A sweep script that swapped `models/lstm_posture.keras` in place was once
interrupted and left the wrong model live. Measurement scripts must load
models via `LSTMPostureClassifier(model_path=..., encoder_path=...)` and
never mutate the active model mid-comparison.

# Random Forest Generalization Investigation

A deeper investigation into the RF's train/validation gap, done after two
prior pruning rounds (`min_samples_leaf=20`, then `max_features=0.1` —
see `rf_trainer.py`'s own comments and `docs/TCN_REGRESSION_REPORT.md`)
had already reduced it from 28.9% to 23.8%. This document asks the
question those rounds didn't: *is the remaining gap actually leakage, or
a fixable representation problem, rather than just "needs more
pruning"?* Two additional techniques were designed from that diagnosis,
tested, and honestly rejected after real-footage confirmation contradicted
what the validation split suggested — a third time this project has hit
that exact trap.

## 1. Data leakage audit — clean

- **Group/subject leakage**: `StratifiedGroupKFold` split by `sequence_id`
  confirmed zero sequence overlap between train (56 sequences) and
  validation (14 sequences) folds. No window from a training sequence ever
  appears in validation.
- **Window-overlap leakage**: sliding windows (step=1) within a sequence
  overlap heavily, but since whole sequences go to one side of the split,
  this never crosses the train/val boundary. Not leakage, though it does
  mean the *effective* number of independent training examples is much
  smaller than the raw window count (see Section 3).
- **Preprocessing leakage — RESOLVED (a later audit session)**: this
  section originally reported that `col_medians` were computed in
  `lstm_dataset.py::build_dataset()` over the FULL real dataset (train +
  validation combined) *before* any trainer's train/val split happened,
  and left unfixed because `lstm_dataset.py` was on the project's
  do-not-edit list. That diagnosis was correct, and the fix has since
  landed: `build_dataset()` no longer imputes real data at all — it saves
  `X` raw, with NaNs preserved (confirmed: ~25.5% of feature values in the
  rebuilt `data/lstm_dataset.npz` are NaN, 49% of windows have at least
  one). Each trainer (`lstm_trainer.py`/`tcn_trainer.py`/`rf_trainer.py`)
  now computes `col_medians` from its own training fold ONLY, after its
  own `StratifiedGroupKFold` split, and imputes both its train and
  validation folds with those train-only statistics — the same
  train-fold medians are also what gets saved into the model's encoder,
  so live inference imputation matches what the model actually trained
  against. All three models were retrained on the fixed pipeline;
  validation-split numbers moved by less than a point in either direction
  (RF: 92.74%/68.92% -> 92.71%/69.31% train/val), consistent with this
  section's original judgment that the leakage's effect was real but
  small in magnitude — it was a genuine correctness bug worth fixing, not
  the dominant driver of the train/val gap discussed in Section 3 below.

## 2. Full metrics (see also the Final Report table for the consolidated version)

Measured on the production split (fold 0), current config
(`min_samples_leaf=20`, `max_features=0.1`, flatten representation):

| | Train (real-only) | Train (real+synthetic, as usually reported) | Validation |
|---|---|---|---|
| Accuracy | 89.78% | 92.74% | 68.92% |
| Balanced accuracy | 84.49% | — | 55.79% |
| Macro F1 | 0.86 | — | 0.57 |

**Synthetic augmentation partially inflates the commonly-reported "92.74%
train accuracy"**: synthetic-only accuracy is 100.00% (trivial — the
templates are clean, noise-free). The fairer real-to-real comparison is
89.78% (real train) vs. 68.92% (validation) = a 20.9-point gap, not 23.8.
Still substantial, but ~3 points of the "official" gap is a real+synthetic
mixing artifact, not overfitting to real patterns.

**OOB score is NOT a trustworthy estimate here**: `oob_score_=0.8889`,
far above the actual validation accuracy (0.6892). `RandomForestClassifier`'s
out-of-bag estimate bootstraps individual *windows*, not *sequences* — a
window's "held-out" trees are still very likely to have seen a
near-identical adjacent window from the same sequence, so OOB silently
overstates generalization on this kind of grouped, temporally-correlated
data. Do not use OOB score as a stopping criterion for this dataset without
this caveat.

**Confusion matrix (validation)** shows the generalization problem is
concentrated in specific classes, especially `Unknown` (recall 0.10, and
64% of true-Unknown windows are misclassified as `Fall`) — an inherently
ambiguous catch-all class with the least crisp, most subject-specific
decision boundary. Note (Section 5): this specific weakness turns out not
to matter much for real-footage deployment, since none of the ground-truth
labels in either real test set are ever "Unknown."

## 3. Root cause

**Not leakage. Dimensionality vs. independent sample count.** Feature
importance is diffuse — the top-10 (of 3,960) features carry only 16.2%
of total importance, and 3,790/3,960 features have some nonzero
importance — ruling out a single leaky/suspicious feature driving
overfitting. The more consistent explanation: 3,960 flattened features
built from only **56 independent real training sequences** (each
contributing dozens of heavily autocorrelated sliding windows the model
still treats as i.i.d. samples) is a classic high-dimension/low-
independent-sample setup for a tree ensemble with no inherent smoothness
prior across time, unlike the LSTM/TCN.

## 4. Techniques tried in response to that diagnosis

### 4a. Summary-statistic feature representation — tested, REJECTED

`rf_trainer.py::summarize_windows()`: reduces each window from 3,960
flattened values to 660 (mean/std/min/max/last-frame-value per feature
across the window) — directly targets the diagnosed dimensionality
problem.

A 5-fold **group-aware** CV (all 5 `StratifiedGroupKFold` folds, not just
fold 0, to avoid tuning the representation choice itself to one split)
showed summary-stat features beating the flattened representation on
*every* validation metric:

| Representation | Avg val accuracy | Avg macro F1 | Avg balanced accuracy | Avg gap |
|---|---|---|---|---|
| flatten (current) | 0.7085 | 0.6143 | 0.6050 | 0.2101 |
| summary (best variant) | 0.7197 | 0.6328 | 0.6245 | 0.2204 |

This looked like a genuine win. **Confirmed on real footage — it lost
decisively on the Hussain edge-case set** (the more decision-relevant test
set per this project's own prior conclusion):

| | Sanawar | Hussain |
|---|---|---|
| flatten (current production) | 55.2% acc / 0.276 F1 | **69.2%** acc / **0.565** F1 |
| summary (best variant) | 54.1% acc / 0.304 F1 | 57.1% acc / 0.484 F1 |

Roughly a wash on Sanawar, but a clear loss on Hussain (12 points of
accuracy, 0.08 of macro F1, plus 2 more false alarms). **Rejected as the
default** — kept in the codebase as a documented, available-but-not-
recommended option (`feature_representation="summary"`), since the
underlying dimensionality diagnosis is still believed correct; this
particular remedy just didn't survive contact with real footage. This is
the third time in this project's history that a validation-split
conclusion didn't hold up on real footage (after the TCN class-weighting
regression and the earlier RF `max_samples` pruning variant) — a pattern,
not a fluke.

### 4b. Class weighting (`use_class_weights=True`) — tested, REJECTED

Motivated by `Unknown`'s poor validation recall (0.10). Balanced weighting
raised it to 0.76 on the validation split, and even nudged macro F1
slightly (0.566 -> 0.577 on real Hussain footage) — but **fall-detection
recall dropped from 100% to 75% on the Hussain set AND from 87.5% to 75%
on the Sanawar set**, missing a real fall on *both* test sets. This is the
exact same failure signature already found and reverted for the TCN
(`docs/TCN_IMPLEMENTATION_NOTES.md` Section 6.5): balanced weighting makes
the model over-predict the rare class at the expense of majority-class
(here: `Fall`) recall. Given this project's explicit priority (a missed
fall is worse than a false alarm), this is a disqualifying regression
regardless of the minor accuracy/F1 gains elsewhere. `use_class_weights`
stays `False` by default.

### 4c. `max_leaf_nodes` — tested, negligible, not adopted

Capping at 200/500/1000 changed validation accuracy by less than 0.2
points (0.6911 vs. 0.6892 baseline) — redundant with the regularization
`min_samples_leaf=20` + `max_features=0.1` already provide; trees aren't
reaching anywhere near these leaf counts in practice. Not worth the added
configuration surface for no measurable benefit.

### 4d. Feature selection / removal — investigated, no action taken

Feature importance is diffuse (Section 3), not concentrated in a small
suspicious subset — there is no specific feature to point to and remove.
Aggressively pruning to only the top-K important features was not
separately tested given this: the diffuseness itself is evidence that a
hard feature cut would discard broadly-useful signal rather than target a
leak, which is a materially different situation from "one feature is
doing something suspicious."

### 4e. Consecutive-frame confirmation (`fall_confirm_frames`) — tested, REJECTED as a default

Motivated by a follow-up question: can the RF's 5 fall false alarms on the
Hussain set be reduced? Diagnosed the actual `fall_detected=True` run
lengths on each false-positive clip before assuming a smoothing gate would
help:

| Clip | Longest sustained "Fall" run |
|---|---|
| Bend_pickup_lowLight | 28 frames (~1.2s) |
| Bend_pickup_normalLight_back | 4 and 10 frames |
| Bend_pickup_normalLight_leftRight | 40 frames (~1.4s) |
| Moving_in_out_frame | 101 frames (~3.5s) |
| SitFloor_lowKeypoints_crossedLegs | 9 frames (~0.3s) |

**Most of these are sustained misclassifications (over a second, one over
3.5s), not brief noise blips** — bending forward geometrically resembles
falling, and a person exiting the frame edge produces a shrinking/
truncated body pattern that reads as collapsing, for as long as they
remain partially out of frame. Only the two short runs (9 and 10 frames)
are in a range a consecutive-frame gate could plausibly suppress.

Added `fall_confirm_frames` to `RFPostureClassifier` (same mechanism as
`TCNPostureClassifier`'s existing parameter) and swept thresholds
1/5/8/10/15/20 against both real test sets:

| confirm_frames | Sanawar fall recall | Hussain fall recall | Hussain false alarms |
|---|---|---|---|
| 1 (default) | 87.5% | 100.0% | 5 |
| 5 | 87.5% | 100.0% | 5 |
| 8 | **75.0%** | 100.0% | 5 |
| 10 | 75.0% | 100.0% | 4 |
| 15 | 75.0% | 100.0% | **3** |
| 20 | 75.0% | 100.0% | 4 |

**Rejected.** The threshold needed to suppress the short false-positive
runs (8+) is exactly the threshold that costs a real, genuine fall on the
Sanawar set — recall drops from 87.5% to 75.0% starting at
`fall_confirm_frames=8`, with no further recovery at higher thresholds.
There is no value in this range that reduces false alarms without also
risking a missed fall elsewhere. Given this project's stated priority (a
missed fall is worse than a false alarm), `fall_confirm_frames` stays at
its default of `1` (disabled) — same conclusion, same reasoning, as the
TCN's own default.

The non-monotonic false-alarm count at high thresholds (5→4→3→4 from
confirm_frames 8→10→15→20) is likely an artifact of a *different*,
genuinely fixed bug found during this sweep: delaying confirmation also
delays *true* detections, and a delayed-but-correct detection can land
outside the labelled fall window's scoring boundary, which
`evaluate_real_footage.score_fall`-style scoring then counts as a new
false positive rather than a (late) true positive — a real, separate
finding about the interaction between confirmation delay and fixed
scoring windows, not a smoothing win.

**A real bug was found and fixed while running this sweep**, independent
of the confirm-frames conclusion above: `compare_tcn_lstm.py`'s
`evaluate_model()` reuses one classifier instance across every clip in a
batch but never called `reset_state()` between clips, so a stateful
classifier's consecutive-fall counter could leak from the end of one clip
into the start of the next. Fixed (guarded with `hasattr` since
`LSTMPostureClassifier` has no such state); this affects any future use
of `fall_confirm_frames > 1` in this harness, for either the TCN or the
RF, not just this specific sweep.

**Recommended real fix (not implemented here, future work)**: the
existing heuristic (`pipeline_utils.py`) already solves exactly this
"bending vs. falling" ambiguity for its own fall trigger via
`FALL_HIP_DESCENT_MIN` — requiring genuine downward hip displacement, not
just torso rotation, before confirming a fall (see `context.txt` Section
2). Gating the RF's `fall_detected` on the same real-hip-descent check
(rather than time alone) would directly target the actual failure
mechanism (bending doesn't drop the hips to the floor; falling does)
instead of trading detection latency for false-alarm suppression. This is
a cross-model integration change, not a Random-Forest-internal one, and
was judged out of scope for this investigation.

## 5. An important scoping note: `Unknown`-class performance vs. real deployment

The validation split's worst-generalizing class (`Unknown`, recall 0.10)
is a real training class (derived from ambiguous heuristic-labeled
frames), but **neither real test set's ground truth ever labels a frame
"Unknown"** — `evaluate_real_footage.py`'s ground-truth vocabulary for
real footage is Standing/Sitting/Lying/Fall only. This means the
`Unknown`-class weakness identified on the validation split is real but
**does not directly cost anything on real-footage evaluation** — and
partially explains why techniques that specifically targeted it (summary
features, class weighting) both looked better on the validation split but
did not translate into a real-footage win: they were solving a problem
that matters less for the actual deployment target than the validation
split's own class distribution suggests.

## 6. Conclusion

The two-round pruning already done (`min_samples_leaf=20` +
`max_features=0.1`) remains the best real-footage-validated configuration.
Two further, well-motivated techniques (summary-stat features, class
weighting) were designed from a genuine root-cause diagnosis, properly
tested with group-aware validation, and correctly rejected after real-
footage confirmation contradicted the validation-split signal — this is
what "evidence-based" is supposed to look like, including when the
evidence says "don't ship this." The remaining ~21-24 point gap is judged
an acceptable cost of a 3,960-feature, 56-independent-sequence training
regime for a non-temporal model, not a symptom of leakage or a fixable
implementation bug.

## 7. Round 2 addendum (2026-08-24): HistGradientBoosting, dimensionality reduction, temporal smoothing — none close the gap

A separate investigation, triggered by re-examining a prior rejection of
`GradientBoostingClassifier` that turned out to be on flawed grounds (fit
time alone — ~94min for one fit — rejected before latency or model size
were ever measured; see `benchmarks/rf_alternatives_full_sweep.py`'s own
docstring for the full audit trail). Re-run properly this time with full
instrumentation and real-footage confirmation, same evidentiary standard
as Sections 1-6 above.

### 7a. HistGradientBoostingClassifier — real latency win, not a validated replacement

- Round 1's implementation choice was itself the problem: sequential,
  single-threaded `GradientBoostingClassifier`. Round 2 used
  `HistGradientBoostingClassifier` (histogram-based, natively
  multithreaded, no new dependency — already in the installed sklearn).
- **5-fold CV** (`benchmarks/dimensionality_reduction_sweep.json`'s
  no-reduction baselines): accuracy 77.39% vs. RF's 77.61% and macro F1
  0.6929 vs. 0.6858 — both differences are within a single fold's own
  noise (std dev 3.8-5.2 points across folds), i.e. not a real signal
  either way. p95 classify latency 21.09ms vs. 70.24ms (**-70%**, held
  robustly across all 5 folds) and model size 5928KB vs. 6272KB (-5.5%)
  are real, but latency is the only one that clearly matters at this
  scale.
- **Real-footage confirmation** (`results/rf_vs_hgb_realfootage/summary.json`,
  same 28-clip corpora and protocol this document's own rule requires):
  fall recall **ties** at 92.3% (same single missed clip, `Backward_fall`,
  for both models); RF wins overall accuracy/macro/balanced/weighted F1
  by a modest, consistent margin; HGB has a lower aggregate fall
  false-positive rate (40.0% vs. 46.7%) — but introduces a new,
  **sustained, high-confidence** failure RF does not have:
  `SitFloor_crossedLegs` (floor-sitting, crossed legs) misread as Lying in
  165/259 windows at 0.85-0.96 confidence, 0% accuracy on that clip,
  triggering a false fall alarm.
- **Temporal smoothing does not fix this.** A new rolling majority-vote
  mechanism (`smoothing_window` param, `RFPostureClassifier._smooth()` in
  `src/posture/rf/rf_classifier.py` — deliberately separate from
  `fall_confirm_frames` in Section 4e above, which only gates the
  `fall_detected` boolean and never touches posture classification) was
  swept at N=1/3/5/7/10
  (`results/rf_vs_hgb_smoothing_sweep/summary.json`). `SitFloor_crossedLegs`
  stays a 0%-accuracy false positive at every single window size — a
  sustained majority-class error has no minority of flicker frames for a
  majority vote to overrule. Fall recall stays exactly 92.3% at every N,
  for both models. HGB's aggregate FP rate does improve with larger N
  (40.0% -> 26.7%), but only by suppressing *other*, blip-type false
  positives, never this one — at a real cost of up to ~311ms of added
  decision delay at N=10.
- **Feature-level diagnostic (2026-08-24, no retraining)**: RF's already-
  shipped `models/rf_posture.joblib` was inspected directly
  (`feature_importances_`); `HistGradientBoostingClassifier` has no such
  attribute in the installed sklearn, and no HGB model was ever persisted
  to disk, so an HGB-specific importance ranking was not obtainable
  without retraining — explicitly out of scope for this check, not
  fabricated. RF's importance is concentrated in static landmark
  *position* (98.7% of total; velocity ~1.3%), dominated by shoulder/knee/
  ankle (`right_shoulder` alone carries 31% of position importance). The
  actual misclassified frame's feature values, compared against the
  training distribution, did not point to one specific broken feature —
  the signal was mixed across the top landmarks, and the training data's
  own `Sitting` class already has very large intra-class variance for
  knee/ankle position (std 2.9-4.9 normalized units, vs. Standing's
  0.7-1.3), consistent with `Sitting` being an internally heterogeneous
  class that was never given a tight, well-covered example of this
  specific floor-level/crossed-legs configuration. **No actionable
  single-feature fix identified — this is a general decision-boundary /
  data-coverage gap, not a fixable feature-engineering bug.** For
  comparison, RF's own analogous clip
  (`SitFloor_lowKeypoints_crossedLegs`) fails much more mildly: a ~20-frame
  (~0.65s), low-confidence (0.34-0.41) blip during what is almost
  certainly the sit-down transition, not a sustained confident misread —
  consistent with, and corroborated by, Section 4e's earlier
  `fall_confirm_frames` sweep on this exact clip (a 9-frame "Fall" run,
  ~0.3s).

### 7b. Dimensionality reduction (PCA / FeatureAgglomeration / GaussianRandomProjection) — rejected, no deployment benefit

Full results: `benchmarks/dimensionality_reduction_sweep.json` / `.md`
(5-fold CV, both RF and HGB, n=50/100/200, with a Jetson-oriented
latency/size breakdown separating transform-only from classify-only cost).
No configuration matched the no-reduction baseline on both accuracy and
macro F1, for either classifier. Counter to the intuitive "fewer features
-> faster/smaller" assumption: PCA *increases* serialized size for RF
(9.6-11.5MB vs. 6.27MB — the reducer's own component matrix costs more
than the smaller trees save) and *worsens* classify latency for HGB at
every tested n. The one place reduction genuinely helped (RF's
classify-only latency, ~15-30% faster) never approached plain HGB's
latency anyway, at a larger accuracy cost than that latency gain
justified. t-SNE and Kernel PCA were ruled out architecturally without
spending CV compute on either: neither supports a compatible real-time
out-of-sample transform for a single new window.

### 7c. Decision (2026-08-24): keep Random Forest as the production model

`models/rf_posture.joblib` / `models/rf_label_encoder.json` are
unchanged. Neither HistGradientBoosting, dimensionality reduction, nor
temporal smoothing produced a real-footage-confirmed improvement over the
existing configuration. HGB's one genuine, robust advantage (latency,
~70% lower) does not offset a real, structural, smoothing-resistant
floor-sitting failure mode that RF does not share in the same form. **This
is a recorded decision, not an open question — a future session should
not re-litigate it without new evidence.**

**What would actually change this decision**: genuinely diverse new
Sitting/Lying training sequences specifically covering floor-level and
crossed-legs postures — the same data-collection priority Section 3
already identified (few independent real sequences relative to feature
dimensionality), now with two concrete real-footage reference clips to
design new recordings against:
`test_footage/Hussain Testing 7-30-26/SitFloor_crossedLegs.MOV` (HGB's
total failure) and
`test_footage/Hussain Testing 7-30-26/SitFloor_lowKeypoints_crossedLegs.MOV`
(RF's milder, transition-only version of the same weak spot). If that
data is collected and either model is retrained on it, this decision
should be revisited against fresh real-footage evidence, not assumed to
still hold.

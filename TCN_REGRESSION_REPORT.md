# TCN Regression: Root-Cause Analysis, Fix, and Final Model Comparison

This report covers three things, in order: (1) why the TCN's accuracy dropped
after the "edge-case improvements and regularization" changes, (2) the fix
and its validation, and (3) the completed Random Forest implementation and
final LSTM vs. TCN vs. Random Forest comparison. All numbers below are
measured, not estimated — the scripts used to produce them are named
throughout so every claim can be re-run.

---

## Phase 1–2: Regression Analysis & Root Cause

### What actually changed

Comparing the working tree against the last commit (`a4a5870`) isolated
exactly two behavior-affecting changes to `src/posture/tcn/`:

| Change | File | Default | Intended purpose |
|---|---|---|---|
| L2 weight regularization (`l2=1e-5`) | `tcn_model.py` | On (non-zero) | Reduce train/val overfitting gap |
| Balanced class weighting (`use_class_weights=True`) | `tcn_trainer.py` | On | Fix near-zero recall on the minority `Sitting`/`Unknown` classes |

Everything else touched in the same diff (`SequenceWindowClassifier` /
`fall_confirm_frames` refactor in `tcn_classifier.py`, the identical L1/L2
plumbing added to `lstm_trainer.py`) is inference-side or defaults to
exactly the pre-existing behavior — confirmed by re-reading the diffs
line-by-line, not just the docstrings. Those were ruled out as candidates
immediately; the investigation focused on the two changes above.

### Isolating which one caused the regression

A 4-config ablation retrained the TCN from scratch — same seed (42), same
`StratifiedGroupKFold` split, same synthetic augmentation — for every
combination of the two changes, then evaluated each checkpoint two ways:
on the in-distribution validation split, and on the same real 8-clip test
set (`test_footage/Sanawar Testing 7-22-26`) used for the project's
previous "best TCN" numbers.

**Validation split** (in-distribution, 2056 windows):

| Config | Val accuracy | Val macro F1 | Unknown recall |
|---|---|---|---|
| baseline (l2=0, no class weights) | 69.3% | 0.517 | 0.0% |
| l2=1e-5 only | 69.8% | 0.537 | 0.4% |
| class weights only | 67.0% | 0.586 | 66.8% |
| l2 + class weights (as shipped) | 67.0% | 0.595 | 68.8% |

**Real footage** (8 labelled clips, 967 scored frames, ~90% Lying):

| Config | Accuracy | Fall recall | "Unknown" predictions |
|---|---|---|---|
| baseline (l2=0, no class weights) | 76.0% | 87.5% (7/8) | 134 |
| l2=1e-5 only | **76.9%** | 87.5% (7/8) | 143 |
| class weights only | 51.5% | 75.0% (6/8) | 413 |
| l2 + class weights (as shipped) | 47.8% | 75.0% (6/8) | 464 |

### Root cause

**`use_class_weights=True` is the entire regression. L2 regularization is
not implicated** — alone, it's harmless and even mildly *better* than the
original baseline on real footage (76.0% → 76.9%).

Balanced class weighting reweights the training loss so misclassifying a
rare class (`Sitting`, `Unknown`) costs ~1.4–1.8× more than misclassifying
`Lying`. This does fix `Unknown`-class recall on the validation split (0.0%
→ ~68%) — but it does so by making the model predict "Unknown" far more
liberally overall, not just on genuinely ambiguous frames. Real footage is
~90% `Lying` frames, so a broad shift toward "Unknown" shows up there as
across-the-board accuracy collapse: predicted "Unknown" frames roughly
tripled (134 → 464) at the direct expense of correct `Lying`/`Standing`
calls, and one real fall clip (`Backward_fall`) flips from a detected fall
to a missed one because its Lying-phase frames get relabeled Unknown.

**Process gap identified along the way**: the `use_class_weights` docstring
referenced a "Phase 2.5" edge-case write-up that was never actually
committed anywhere retrievable in the repo. The change was motivated by a
real, evidenced problem (Sitting confusions dominating misclassifications;
Sitting is 9.2% of training windows vs. Standing's 39.8%) but shipped as
the new default without re-running the project's own standing regression
check (`compare_tcn_lstm.py` against the same real footage) before being
made default. That's the proximate cause of a 28-point accuracy regression
shipping as an "improvement."

Full ablation methodology, tables, and mechanism explanation are now
committed to `TCN_IMPLEMENTATION_NOTES.md` §6.5 so this isn't lost again.

---

## Phase 3–4: Fix and Validation

### Fix applied

- `src/posture/tcn/tcn_trainer.py`: `use_class_weights` default changed
  `True` → `False`. Parameter kept (not removed) so a softer scheme (e.g.
  capped weights, or weighting only `Sitting`) can be tried later with a
  proper before/after check — seeing this shipped without one is exactly
  what caused the regression.
- `src/posture/tcn/tcn_model.py`: **no change.** `l2=1e-5` stays the
  default — it's evidence-supported (Section 6 of the implementation notes,
  reconfirmed by the ablation above).
- `models/tcn_posture.keras` / `models/tcn_label_encoder.json`: retrained
  with the corrected default and promoted to production.
- `src/posture/lstm/lstm_trainer.py`: gained the same `use_class_weights`
  parameter (default `False`) purely for **parity** across all three
  trainers (LSTM/TCN/RF now expose the identical `l1`/`l2`/
  `use_class_weights` knob set) — not turned on, since it hasn't been
  separately validated for the LSTM either.

### Validation: corrected TCN vs. previous best

**Validation split** (`models/tcn_posture.keras`, restored best epoch = 3):

| | Train | Validation |
|---|---|---|
| Accuracy | 85.14% | 69.84% |
| Loss | 0.3687 | 0.9645 |

Per-class (validation, 2056 windows):

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Fall | 0.55 | 0.86 | 0.67 | 476 |
| Lying | 0.64 | 0.66 | 0.65 | 295 |
| Sitting | 0.88 | 0.33 | 0.48 | 191 |
| Standing | 0.85 | 0.91 | 0.88 | 844 |
| Unknown | 0.03 | 0.00 | 0.01 | 250 |
| **Accuracy** | | | **0.70** | 2056 |
| Macro avg | 0.59 | 0.55 | 0.54 | |

**Real footage**, apples-to-apples with the historical baseline
(`test_footage/Sanawar Testing 7-22-26`, same extraction pipeline the
76.0%/87.5% baseline was measured under):

| | Previous best (committed) | Corrected (this fix) |
|---|---|---|
| Accuracy | 76.0% | **76.9%** |
| Fall-detection recall | 87.5% (7/8) | 87.5% (7/8) |

**The fix meets the primary objective: it matches or exceeds the previous
best TCN performance**, using only the evidence-supported change (revert
class weighting; keep L2).

### An important caveat: what changed underneath, unrelated to this fix

Per your instruction, `origin/main` was merged into `TCN_sanawar` before
finalizing. That merge is clean with respect to everything above — it
touches zero files under `src/posture/tcn/`, `src/posture/lstm/`, the new
`src/posture/rf/`, or `compare_tcn_lstm.py`, and all 37 existing unit tests
still pass post-merge. **However**, it changes `extract_keypoints()` in
`evaluate_real_footage.py` (MediaPipe `IMAGE` mode → `VIDEO`-mode tracking,
plus landmark-visibility masking in `pipeline_utils.py`). That's a real,
independent improvement to the extraction pipeline itself — but it means
real-footage numbers computed *after* the merge are not directly comparable
to the historical 76.0%/87.5% baseline, which was measured under the old
extraction code. Re-running the full comparison after the merge
(`results/all_models_sanawar/`) gives:

| | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 72.8% | 79.1% | 57.3% |
| Fall recall | 87.5% (7/8) | 75.0% (6/8) | 87.5% (7/8) |

TCN's accuracy is higher under the new extraction pipeline (79.1%), but its
fall recall under this specific measurement drops to 75% (now misses
`Backward_fall` in addition to `Far_fall`) — LSTM and RF both hold at
87.5%. **This is not caused by the class-weighting fix** — it's confirmed
separately from it, since the apples-to-apples pre-merge check above (same
extraction code as the historical baseline) shows the fix alone preserves
87.5%. It's an incidental interaction between the TCN specifically and
`main`'s extraction-pipeline change, and it's flagged here as a known
limitation for follow-up (see "Limitations" below) rather than something
this task's scope covers fixing.

---

## Phase 5: Random Forest

`src/posture/rf/rf_trainer.py` + `src/posture/rf/rf_classifier.py`, added:

- **Reuses the exact existing feature vectors**: same `data/lstm_dataset.npz`,
  same `StratifiedGroupKFold` split (seed 42), same post-split synthetic
  augmentation as the LSTM/TCN trainers. The only RF-specific step is
  flattening each `(30, 132)` window into a single `3960`-dim vector, since
  a tree ensemble has no notion of a time axis.
- **Training**: `RandomForestClassifier(n_estimators=300, ...)`, `class_weight`
  off by default for the same evidence-based reason as the TCN fix above
  (not blindly applying balanced weighting without a validated before/after).
- **Serialization**: `models/rf_posture.joblib` + `models/rf_label_encoder.json`
  (identical encoder schema to LSTM/TCN, for pipeline consistency).
- **Inference**: `RFPostureClassifier` — same public interface
  (`.predict()`, `.window_size`, `.raw_history_needed`, `.is_available`) as
  `LSTMPostureClassifier`/`TCNPostureClassifier`, so it drops into
  `compare_tcn_lstm.py`'s (now `compare_all_models.py`'s) evaluation loop
  unchanged.

Validation split: 96.60% train accuracy vs. 67.70% validation accuracy —
a visible overfitting gap (unsurprising for 300 trees over a 3960-dim
flattened, un-regularized feature space with a few thousand real training
sequences), but usable, and — as the real-footage numbers below show —
not necessarily worse where it matters.

---

## Final Comparison: LSTM vs. TCN vs. Random Forest

All numbers below are from `compare_all_models.py` (extends
`compare_tcn_lstm.py`'s evaluation code — identical extracted keypoints,
identical windowing, no smoothing layered on any model), run post-merge on
both real test sets.

### Classification metrics

**Sanawar set** (8 clips, ~90% Lying — the "clean" scenario):

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 72.8% | **79.1%** | 57.3% |
| Macro F1 | 0.315 | **0.368** | 0.301 |
| Fall recall | **87.5% (7/8)** | 75.0% (6/8) | **87.5% (7/8)** |

**Hussain edge-case set** (17 clips — low light, occlusion, off-axis,
bending/kneeling/sit-on-floor, the scenarios the class-weighting change was
originally trying to fix):

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 46.0% | 49.7% | **60.3%** |
| Macro F1 | 0.372 | 0.402 | **0.498** |
| Fall recall | 75.0% (3/4) | 75.0% (3/4) | **100.0% (4/4)** |
| Fall false positives | 11 | 7 | **6** |

Full per-class precision/recall/F1 and confusion matrices for both sets:
`results/all_models_sanawar/all_models_comparison.md`,
`results/all_models_hussain/all_models_comparison.md`.

**This is a genuine trade-off, not a clean win for one model.** TCN is
best on the easier, Lying-dominated set. RF is clearly best on the harder,
more realistic edge-case set — both on accuracy *and* on the
safety-critical fall-recall metric (catches every labelled fall, with
fewer false alarms than either neural model).

### Efficiency metrics

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Training time (same machine, same data, back-to-back) | 85.0s | 86.5s | **57.9s** |
| Parameters / tree nodes | 63,013 | **39,365** | 271,508 |
| Model file size | 774.4 KB | **628.5 KB** | 27,700.7 KB (~27 MB) |
| Inference latency, mean (Sanawar set) | 92.5 ms | 89.8 ms | **76.1 ms** |
| Inference latency, p95 | 129.7 ms | 121.4 ms | **109.4 ms** |
| Peak RAM (measurement caveat below) | 494.7 MB | 508.9 MB | 509.2 MB |

Peak-RAM caveat: all three models were measured within one long-running
Python process that already has TensorFlow loaded for the LSTM/TCN passes
before RF's turn runs, so RF's isolated (standalone-process) RAM footprint
is likely lower than shown — this measurement understates RF's actual
deployment-time RAM advantage rather than overstating it.

### Deployment analysis (Jetson Nano / Orin)

- **Model size**: TCN is smallest and RF is by far the largest (~44× TCN's
  file size), but 27 MB is trivial in absolute terms even for Jetson Nano's
  storage; this is not a real deployment blocker.
- **Dependencies**: RF needs only `scikit-learn` + `joblib` — no
  TensorFlow. On Jetson's constrained storage/setup, avoiding a
  multi-hundred-MB TensorFlow(-cpu) install is a real, practical advantage
  for ease of deployment, even though the LSTM/TCN checkpoints themselves
  are smaller.
- **Acceleration path**: TCN's causal-conv structure is the best fit for
  TensorRT/cuDNN acceleration on Jetson Orin's GPU (parallel across the
  time axis, standard fusable ops). LSTM's recurrence is inherently
  sequential and historically harder to accelerate the same way. RF has no
  meaningful GPU acceleration path — it runs CPU-only regardless of target
  — but its measured latency here is already the *fastest* of the three
  even on CPU, so this is a smaller liability than it sounds.
- **Robustness**: on the edge-case set — the one that actually resembles
  uncontrolled deployment conditions — RF is the most robust of the three
  by a clear margin, and the only one that caught every labelled fall.
- **Capacity/generalization risk**: RF's 96.6% train vs. 67.7% validation
  accuracy is a real overfitting signal, and flattening the window discards
  the explicit temporal/motion prior that both neural models encode
  structurally. With only 70 raw training sequences, RF may be leaning on
  memorized spatial poses more than genuine motion understanding — its
  edge-case win should be re-checked as more real footage is collected, not
  treated as a permanently settled result.

### Recommendation

**No single architecture wins outright, and the honest recommendation
depends on which failure mode matters more:**

- If the deployment target is closer to the *Sanawar-style* clean,
  mostly-lying-down monitoring scenario and minimizing footprint / using
  Jetson Orin's GPU is the priority: **TCN** — best accuracy on that set,
  smallest model, and the architecture most compatible with TensorRT
  acceleration.
- If the deployment target needs to be robust to the *harder, more varied*
  conditions in the Hussain set (occlusion, low light, off-axis, floor
  sitting) — which is arguably the more realistic bar for an unattended
  real-world fall-detection system — **Random Forest** is the
  evidence-backed choice: best accuracy, best macro F1, and catches every
  fall with fewer false alarms, while also being the fastest and simplest
  to deploy dependency-wise.
- **LSTM** is not the top performer on either axis here and its main
  remaining advantage is that it's the architecture the rest of the
  pipeline's tuned knobs (`hybrid_evaluate.py`'s warmup/consecutive-frame
  gating) were built around — a real switching cost, not a modeling one.

Given this project's explicitly stated priority (a missed fall is worse
than a false alarm) and that the edge-case set is the more realistic
stand-in for real deployment variability, **Random Forest is the
recommended default**, with TCN kept as the fallback/companion model for
the cleaner scenario and for any future work targeting Jetson Orin's GPU
specifically — an ensemble/voting combination of the two (already flagged
as future work below) would very plausibly beat either alone.

---

## Summary of code changes

| File | Change |
|---|---|
| `src/posture/tcn/tcn_trainer.py` | `use_class_weights` default `True` → `False`; docstring rewritten with the ablation evidence |
| `src/posture/tcn/tcn_model.py` | No change (L2=1e-5 default confirmed correct, kept) |
| `src/posture/lstm/lstm_trainer.py` | Added `use_class_weights` param (default `False`) for parity with TCN/RF trainers |
| `models/tcn_posture.keras`, `models/tcn_label_encoder.json` | Retrained with corrected defaults, promoted to production |
| `TCN_IMPLEMENTATION_NOTES.md` | New §6.5: full regression ablation, root cause, fix |
| `src/posture/rf/__init__.py`, `rf_trainer.py`, `rf_classifier.py` | New: Random Forest training + inference, same public interface as LSTM/TCN |
| `models/rf_posture.joblib`, `models/rf_label_encoder.json` | New: trained RF checkpoint |
| `compare_tcn_lstm.py` | Added `_model_param_count()` generic helper (Keras `count_params()` or sklearn tree-node-count) so the same evaluation code works for all three model types |
| `compare_all_models.py` | New: 3-way LSTM/TCN/RF comparison script, reuses `compare_tcn_lstm.py`'s evaluation primitives |
| `results/all_models_sanawar/`, `results/all_models_hussain/` | New: full 3-way comparison reports + per-window CSVs |
| `results/Sanawar_Testing_7-22-26/`, `results/Hussain_Testing_7-30-26/` | Regenerated with corrected TCN |

Merged from `origin/main` (per request, before finalizing): landmark-
visibility masking and MediaPipe VIDEO-mode tracking (`pipeline_utils.py`,
`evaluate_real_footage.py`, `realtime_fall_detection.py`, `hybrid_evaluate.py`),
plus LSTM production-checkpoint retraining artifacts from that branch's own
work. No conflicts with anything above; all 37 pre-existing unit tests pass
after the merge.

## Limitations and suggested future work

1. **TCN fall-recall regression after the `main` merge** (87.5% → 75.0% on
   the Sanawar set, under the new VIDEO-mode extraction) is real and
   currently unexplained — flagged above, not fixed, since it's outside
   this task's scope (the class-weighting regression) and needs its own
   isolated investigation (does VIDEO-mode tracking change the *specific*
   frames the TCN's fixed 31-frame receptive field sees at clip boundaries
   differently than the LSTM's carried state?).
2. **8 and 17 labelled real clips are still a small evaluation set** for
   either test set individually — one flipped clip is worth ~12-25 points
   of any per-clip recall metric. This was already flagged in
   `TCN_IMPLEMENTATION_NOTES.md` before this session and remains true.
3. **RF's overfitting gap** (96.6% train / 67.7% val) suggests either more
   training sequences or an explicit regularization pass (max depth,
   min-samples-leaf sweep, or trying summary-statistic features instead of
   the full flattened window) would likely improve it further — not
   attempted here to avoid adding untested complexity beyond what the task
   required.
4. **A 3-way ensemble/voting gate** (heuristic + best-of neural model + RF)
   is the natural next step given RF and TCN each win on a different axis
   here — flagged in `TCN_IMPLEMENTATION_NOTES.md` §9 as future work
   already, now with a second, independent motivation.
5. **The Peak-RAM measurement methodology** (shared long-running process
   across all three models) understates RF's real standalone-deployment RAM
   advantage — a clean per-process measurement would give a fairer number
   for the deployment writeup.

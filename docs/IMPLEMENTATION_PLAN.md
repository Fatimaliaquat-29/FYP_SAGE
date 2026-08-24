# SAGE — Parallel Implementation Plan (TCN / YOLO / GAIT)

**Branches:** `TCN_sanawar`, `YOLO_fatima`, `GAIT_hussain`, all forked from `main` at commit `bf1e0b1`.
**Why these three, together:** they map onto Phase 4 (Temporal Model Comparison) and Phase 5 (Hybrid AI Exploration) of `SAGE_FYP_Continuation_Plan.xlsx`, plus one "Advanced Feature Later" (gait/fall-risk) pulled forward. All three are genuinely independent of each other and of the existing fall-detection pipeline *if built the way this plan describes* — new modules, not edits to shared files. See Section 5 for why that matters and what happens when it's time to merge.

---

## 0. Read this first — the one rule that keeps this mergeable

**During this phase, nobody edits these files:** `src/posture/pipeline_utils.py`, `src/posture/lstm/*`, `hybrid_evaluate.py`, `evaluate_real_footage.py`, `realtime_fall_detection.py`. These are the files where nearly every hard-won bug fix in this project's history lived, and they're also the files all three branches would otherwise collide on. Every branch below is scoped to add **new files in new folders** instead. Wiring everything together into the live pipeline is a deliberate, later, one-person-at-a-time step (Section 5) — not something that happens inside these three branches.

If a branch genuinely needs something changed in those files, that's a flag to raise with the whole team first, not a solo edit.

**Update (a later, full-project audit session)**: this rule was invoked, not bypassed. `src/posture/lstm/lstm_dataset.py`, `lstm_trainer.py`, `tcn_trainer.py`, `rf_trainer.py`, `rf_classifier.py`, and `sequence_window_classifier.py` were edited during a full-project audit to close a real, confirmed preprocessing-leakage bug (see Section 6 below for the full account) — exactly the kind of shared-infrastructure change this section says needs a team flag rather than a silent solo edit. Flagging it here explicitly: these files changed, all three models were retrained and re-validated on real footage as a result, and the team should review Section 6 before continuing separate work on branches that touch this shared code.

---

## 1. TCN_sanawar — Temporal Model Comparison (Continuation Plan Phase 4 / Week 7)

### Objective
Build a Temporal Convolutional Network as an alternative to the LSTM, and produce the rigorous head-to-head comparison the Continuation Plan's "Week 7 Deep Dive" tab specifies: accuracy, recall, precision, F1, latency, parameter count, memory. This is a genuine thesis research contribution, not just an engineering exercise — treat the write-up as seriously as the code.

### The good news: almost no new data work
The LSTM's input problem (no scale/distance invariance) has already been fixed — every training window is now (30 frames × 132 features: hip-centered/torso-scaled position + velocity). That fix lives in `data/lstm_dataset.npz` and `src/posture/lstm/lstm_features.py`. **The TCN should consume the exact same `.npz` file — don't rebuild the dataset, don't re-derive features.** This alone removes what would otherwise be the biggest chunk of work.

### Technical approach
- Framework: Keras (already a project dependency via `tensorflow-cpu`), so `tcn_trainer.py` can closely mirror `lstm_trainer.py`'s existing structure (same `StratifiedGroupKFold` split by `sequence_id`, same post-split synthetic augmentation, same `EarlyStopping`/`ReduceLROnPlateau` callbacks) — only the model architecture function changes.
- Architecture: a standard TCN — a stack of dilated causal 1D convolutions (`keras.layers.Conv1D` with increasing `dilation_rate`, e.g. 1→2→4→8, `padding='causal'`), residual connections between blocks, `GlobalAveragePooling1D`, then `Dense(5, softmax)` to match the LSTM's 5-class output.
- Keep parameter count in the same ballpark as the LSTM (~46K) for a fair comparison where possible, but don't force it — report the actual difference honestly; the Continuation Plan explicitly wants parameter count reported *because* it's expected to differ.

### File plan (new folder, zero edits to existing files)
```
src/posture/tcn/
  __init__.py
  tcn_model.py        # build_tcn_model(window_size, n_features, n_classes) -> keras.Model
  tcn_trainer.py       # near-copy of lstm_trainer.py, imports build_tcn_model instead
  tcn_classifier.py    # mirrors LSTMPostureClassifier's public interface EXACTLY:
                       #   .predict(window) -> dict, .window_size, .raw_history_needed, .is_available
                       # so it's a drop-in alternative wherever LSTMPostureClassifier is used later
```
Models save to `models/tcn_posture.keras` / `models/tcn_label_encoder.json` — parallel names, never overwrites the LSTM's files.

### Task breakdown
1. Read `src/posture/lstm/lstm_features.py` and `lstm_dataset.py` end to end first — understand the feature/window pipeline before writing anything (no code changes needed here, just comprehension).
2. Implement `tcn_model.py`.
3. Implement `tcn_trainer.py`, train on `data/lstm_dataset.npz`, confirm it produces a per-class precision/recall/F1 report like `lstm_trainer.py` already does.
4. Implement `tcn_classifier.py` with the matching interface.
5. Build a comparison script (new file, e.g. `compare_tcn_lstm.py` at repo root, or a new `results/tcn_vs_lstm/` output) that runs **both** classifiers over `Testing/Sanawar Testing 7-22-26/` and reports the full metrics table from the Continuation Plan: accuracy, recall, precision, F1, latency (ms/window), parameter count, peak RAM.
6. Write up the comparison. **Foreground recall specifically** — the Continuation Plan's own notes say a missed fall is the costliest error for this application, so don't let a headline accuracy number bury a recall regression.

### Deliverables
- `models/tcn_posture.keras` + label encoder
- A comparison report (markdown, in the style of `results/*/real_footage_results.md`)
- A recommendation on which model (LSTM or TCN) the Hybrid AI phase should build on

### Dependencies / sequencing
None — can start immediately.

---

## 2. YOLO_fatima — Object Detection Layer (prerequisite for Phase 5, and for Medication Adherence per the Scope Document)

### Objective
Add a person/object detection layer using YOLOv8 (the Scope Document's explicit tech choice), producing the object-level detections the Hybrid Approach report's "Structured Event Schema" needs: person confidence, and eventually medicine containers/furniture for the medication-adherence feature.

### Scope for this phase — be realistic about what's achievable now
Don't try to build medication-adherence detection end-to-end in this branch. Focus on:
1. Getting YOLOv8 running per-frame, alongside (not replacing) MediaPipe.
2. Producing reliable person-detection confidence — genuinely useful immediately, since the Hybrid Approach report specifically recommends cross-checking it against MediaPipe's own tracking confidence ("high-confidence pose + low-confidence bottle = skeptical").
3. A first-pass bounding box for COCO-adjacent classes like "bottle" / furniture, clearly flagged in your write-up as a placeholder — genuine medicine-container detection needs a custom-labeled dataset, which is realistically its own follow-up effort (comparable to how the LeFD dataset had to be added for fall detection).

### Technical approach
- Use `ultralytics` (YOLOv8n or YOLOv8s — start with the nano model for speed) with pretrained COCO weights. COCO already includes "person," so basic person detection works with zero custom training.
- New top-level module, fully independent of `src/posture/`:
```
src/detection/
  __init__.py
  yolo_objects.py   # class YOLOObjectDetector:
                    #   __init__(model_path=...)
                    #   detect(frame: np.ndarray) -> list[dict]
                    #   each dict: {"class": str, "confidence": float, "bbox": [x1,y1,x2,y2]}
```
Keep the interface as simple as that — one method, one clear return type. That's what makes it a mechanical, low-risk integration later.

### Task breakdown
1. Install `ultralytics`, download YOLOv8n pretrained weights.
2. Implement `YOLOObjectDetector` with the interface above.
3. Write a small standalone script that runs it over a few `Testing/` clips and manually sanity-checks person-detection reliability (should be close to 100% given COCO pretraining — if it isn't, something's wrong with the setup, not the model).
4. **Measure per-frame latency honestly, on the actual dev machine.** This matters: running MediaPipe + YOLO both, per frame, roughly doubles today's compute cost, and the Scope Document's target is 15+ FPS on a Jetson — know the real number before anyone assumes it's fine.
5. Do **not** wire this into `realtime_fall_detection.py` in this branch — that's Section 5's job, after the whole team has agreed on the structured event schema and after Phase 4 (TCN decision) has landed, per the Continuation Plan's own sequencing.
6. Stretch goal if time allows: scope out what a custom medicine-container dataset would take to collect/label (even a small one) — this is genuinely a data problem, not a modeling problem, and worth sizing up early rather than discovering it late.

### Deliverables
- A working, benchmarked, standalone `YOLOObjectDetector`
- A short report: person-detection reliability, measured latency, and an honest assessment of what's needed for real medicine-container detection

### Dependencies / sequencing
Person detection: none, start immediately. Medicine-container detection: blocked on new labeled data — don't let this block the rest of the branch.

---

## 3. GAIT_hussain — Gait Analysis / Fall-Risk Prediction (Advanced Feature, pulled forward)

### Objective, and why this is conceptually different from everything else built so far
Everything in this codebase so far **detects a fall as or after it happens.** Gait analysis is about predicting elevated fall *risk* from how someone walks *before* any fall occurs — a slower, trend-based signal (built up over many seconds or repeated observations), not a single frame-level event. Treat this as its own module with its own output type (a risk score), not an extension of the existing Fall/Lying/Sitting/Standing/Unknown classifier. Forcing it into that framework would be a conceptual mismatch, not just a code-organization one.

### Do the literature/data check before writing much code
This is the least-explored of the three branches for this team. Two things should happen early, in this order:
1. **A literature check** on elderly gait analysis / fall-risk prediction — this doubles as progress on the still-outstanding Phase 1 literature matrix, so it's not wasted effort even outside this branch.
2. **An honest data-availability assessment.** None of the existing datasets (UR Fall, UP-Fall, LeFD) are built for this — they're short clips centered on a single fall event, not extended walking sequences. Figure out early whether there's a usable public gait dataset (e.g. from Parkinson's/elderly-gait research) or whether this needs new self-recorded walking footage (normal walking vs. a deliberately unsteady/shuffling walk as a rough proxy). This determines how ambitious the modeling step can realistically be — decide this before investing in a modeling approach that assumes data you don't have.

### Technical approach — candidate signals
Start from established clinical fall-risk indicators, since they're the ones with an actual literature base behind them:
- **Walking speed** — average hip displacement per second while in a walking/"Standing" state. `pipeline_utils.py` already computes hip velocity; reuse that as a building block rather than recomputing it.
- **Stride regularity** — step-to-step variability in the periodic ankle/knee swing pattern during a walking bout.
- **Postural sway** — small oscillations in shoulder/hip position while someone is supposedly standing still (a known clinical indicator, related to Timed-Up-and-Go / Berg Balance style assessments).
- **Sit-to-stand time and smoothness** — how long, and how shakily, someone gets up from a chair.

### Modeling approach recommendation
Given data is likely to be scarce initially, **start simple and interpretable** — a threshold/rule-based first pass on the signals above, the same way the fall-detection heuristic itself started, rather than reaching for a data-hungry deep model before there's enough gait-specific data to train one meaningfully. This isn't a lesser approach — it mirrors exactly how the more mature parts of this project got their start.

### File plan
```
src/gait/
  __init__.py
  gait_features.py   # walking speed, stride regularity, sway, sit-to-stand — reusing pipeline_utils.py's
                      # existing angle/velocity computations where possible
  gait_risk.py        # class GaitRiskAssessor:
                       #   assess_risk(window) -> {"risk_score": float, "signals": {...}}
                       # NOTE: a risk score, not a fall/no-fall flag — keep this distinction explicit
```

### Task breakdown
1. Literature check + data-availability assessment (above) — do this first.
2. Define the exact output contract (`assess_risk()` signature above) before writing feature code.
3. Implement feature extraction for the candidate signals, reusing `pipeline_utils.py` computations wherever possible (read-only imports, not edits).
4. Implement a first-pass rule-based risk model.
5. Validate against whatever data turns out to be realistically available, and **be explicit in the write-up about how limited that validation is** if the data is thin — that honesty is exactly what's made the rest of this project's reporting credible, and it should carry over here too.

### Deliverables
- A working `src/gait/` module with a defined risk-score interface
- A short literature summary
- An honest data-availability assessment and whatever validation the available data supports

### Dependencies / sequencing
The literature check and data assessment should come before the modeling work — they determine its scope.

---

## 4. Shared "definition of done" before any of these three merges into `main`

- [ ] All new code lives in a new module/folder — no edits to `pipeline_utils.py`, `src/posture/lstm/*`, `hybrid_evaluate.py`, `evaluate_real_footage.py`, or `realtime_fall_detection.py`.
- [ ] `python -m unittest tests.test_lstm_pipeline -v` still passes (confirms nothing was accidentally broken).
- [ ] No regression on `python hybrid_evaluate.py --batch_dir "Testing/Sanawar Testing 7-22-26"` vs. the existing numbers in `results/hybrid_extended_window/` — if your branch doesn't touch the detection pipeline at all, this should be a formality, but check anyway.
- [ ] A short markdown write-up of what was built and what was found, in the style of `docs/LSTM_Phase_Summary.md` or `context.txt` — this is what turns into thesis material later, so write it as you go, not retroactively.
- [ ] Branch has been kept in sync with `main` periodically (`git merge main` while on your branch) rather than left to diverge for weeks — see the earlier discussion on why long-lived branches get painful to merge.

## 5. What happens after all three are individually done — the integration phase

This is deliberately **not** part of any of the three branches above, and shouldn't be attempted by three people simultaneously:

1. **TCN decision first.** Once `TCN_sanawar`'s comparison report is in, the team picks LSTM or TCN as the model going forward. This decides what the Hybrid AI schema (next step) actually reasons over.
2. **Wire YOLO's detections and the chosen temporal model's output into a single structured event schema** — this is genuinely new integration code (touching `realtime_fall_detection.py`/`hybrid_evaluate.py` for the first time in this phase), and should be done by one person at a time, reviewed, and validated against the full `Testing/` suite before the next piece lands.
3. **Gait's risk score is a separate, parallel output** — it doesn't need to block or be blocked by the YOLO/temporal-model integration, since it's not part of the same fall-detection decision path. It can be wired into a dashboard/alert system as its own independent signal whenever it's ready.

   **Done (a later session)**: `realtime_fall_detection.py` now runs a `StreamingGaitRiskAssessor` alongside the existing posture/LSTM pipeline, fed the same per-frame pose rows, exactly in the "separate, parallel, non-gating" shape described above — see that module's own "GAIT integration" docstring (in `run()`) for the data flow, and `docs/GAIT_DATA_ASSESSMENT.md`'s own later section for the full account (including two real bugs found and fixed only once this integration made the relevant code paths actually reachable). The YOLO/temporal-model event-schema integration (points 1-2 above) was NOT attempted as part of this — still open, still a separate, later, one-person-at-a-time step.
4. Only after that integration is stable does an LLM reasoning layer (Continuation Plan Phase 5's other half) make sense to attempt — it's meant to reason over the *combined* structured output of steps 1-3, so building it before they exist would mean building it against a schema that's still guessed at, not real.

---

## 6. Full-project audit (a later session) — preprocessing leakage fix, retrain, and re-validation

Scope: independent verification of the entire pipeline (data, LSTM/TCN/RF, GAIT, tests, docs), prompted specifically by a suspected NaN-imputation leakage bug a prior RF investigation had flagged but not fixed. Full findings below; this section is the authoritative current status — anything in earlier sections of this document or in `docs/RF_GENERALIZATION_INVESTIGATION.md`/`docs/TCN_REGRESSION_REPORT.md` that conflicts with this section is superseded by it.

### 6.1 The bug, and why it was more than a documentation gap

`docs/RF_GENERALIZATION_INVESTIGATION.md` had already diagnosed that `col_medians` (the NaN-imputation statistic baked into every model's encoder) were computed over the FULL real dataset (train + validation combined) before any split — real preprocessing leakage — but left it unfixed as a flagged, do-not-touch issue. On inspection, a prior uncommitted session had *started* fixing it: `lstm_dataset.py::build_dataset()` had been changed to stop imputing `X` at all and save it raw (NaNs preserved), with comments saying each trainer would now compute its own train-fold-only medians. **But none of the three trainers had actually been updated** — `lstm_trainer.py`/`tcn_trainer.py`/`rf_trainer.py` all still loaded `X` from the npz and used it directly, with zero imputation step of their own. This was silently masked only because the on-disk `data/lstm_dataset.npz` was stale (built before the raw-X change, so it still had zero NaNs). The moment that dataset was rebuilt with the new code — confirmed by actually doing it — **25.5% of feature values came back NaN** (49% of windows affected). Had this been rebuilt and trainers run as they stood, LSTM/TCN training would have produced NaN losses and RF training would have hard-crashed (sklearn rejects NaN input). This was a live, unfinished, silently-broken change sitting in the working tree, not a documented-and-deferred one.

### 6.2 The fix

All three trainers now compute `col_medians` from their own training fold only, immediately after their `StratifiedGroupKFold` split and before synthetic-data injection, and impute both their train and validation folds with those train-fold statistics. The same train-fold medians (not the whole-dataset value `build_dataset()` still saves for diagnostic reference only) are what gets written into each model's encoder JSON, so live inference imputation matches what the model actually trained against — using a different statistic at inference than at training would reintroduce the exact train/inference skew bug this project had already fixed once before. `src/posture/rf/rf_classifier.py` also picked up a related, independently-found fix: the previously dead `--model` CLI argument (parsed but never used) is now wired through for the LSTM/TCN demo CLIs too (`sequence_window_classifier.py::run_classifier_cli`), same bug class, same fix pattern.

A new regression test, `tests/test_preprocessing_leakage.py`, locks this in: it reproduces `rf_trainer.py`'s exact split independently and asserts the encoder's saved `col_medians` match a train-fold-only computation and explicitly do NOT match the whole-dataset diagnostic value — so a future regression back to whole-dataset statistics would fail loudly, not silently.

### 6.3 Dataset rebuild and retrain

`data/lstm_dataset.npz` was rebuilt (9,906 real windows, 70 sequences — same counts as before, now with real NaNs preserved instead of pre-imputed). All three models were retrained on the corrected pipeline with no other hyperparameter changes. Pre-fix checkpoints and the pre-fix dataset were backed up (`models/pre_leakage_fix_backup/`, `data/lstm_dataset.npz.bak_preleak`) before overwriting, so a revert is possible if ever needed.

Validation-split accuracy barely moved (RF: 92.74%/68.92% train/val -> 92.71%/69.31%; TCN: 69.84% val -> 70.28%; LSTM: ~65-70% val -> 65.76%), consistent with the original investigation's judgment that the leakage's effect was real but small in magnitude on this metric — it was a genuine correctness bug worth fixing regardless, not the dominant driver of the RF train/val gap discussed elsewhere.

### 6.4 Two more real bugs found while re-validating on real footage: silently-excluded clips

Re-running the real-footage comparison surfaced two independent, previously-invisible bugs in `evaluate_real_footage.py::discover_clips()`'s filename-matching logic — both meant a labelled real clip had **never once been included in any real-footage evaluation this project has run**, for any model, ever:

- `test_footage/Sanawar Testing 7-22-26/Foward_fall.mp4` was misspelled (missing the 'r'); its ground truth (`Forward_fall_gt.csv`, correctly spelled) could never match it. The project's own docs cite "8 clips" for this set when 9 video files exist — this is why. **Fixed**: video renamed to `Forward_fall.mp4`.
- `test_footage/Hussain Testing 7-30-26/Bend_pickup_lowLight_leftRight_GT .csv` and `SitFloor_crossedLegs_GT .csv` both had a stray trailing space before `.csv`, which fails the discovery glob's `*_gt.csv` suffix match. Docs cite "17 clips" for this set when 19 video files exist — same root cause. **Fixed**: both GT files renamed to drop the trailing space.

With all three previously-hidden clips now included, all three models were re-evaluated on the corrected, complete 9-clip Sanawar and 19-clip Hussain sets (`results/all_models_sanawar_postleakfix_full9/`, `results/all_models_hussain_postleakfix_full19/`). The two newly-recovered Hussain clips are both bend/floor-sit scenarios — the already-documented "bending reads as falling" false-positive class — so the modest false-positive increase they bring (LSTM 6->8, TCN 8->9, RF 5->7 on Hussain) is an expected consequence of previously-incomplete test coverage, not a new failure mode.

### 6.5 Real-footage results after the fix (apples-to-apples, corrected clip sets)

| Metric | LSTM (was) | LSTM (now) | TCN (was) | TCN (now) | RF (was) | RF (now) |
|---|---|---|---|---|---|---|
| Sanawar accuracy | 72.8% (8 clips) | 50.8% (9 clips) | 79.1% | 74.4% | 55.2% | 58.8% |
| Sanawar fall recall | 87.5% (7/8) | 77.8% (7/9) | 75.0% (6/8) | 77.8% (7/9) | 87.5% (7/8) | 88.9% (8/9) |
| Hussain accuracy | 46.0% (17 clips) | 56.5% (19 clips) | 49.7% | 50.9% | 69.2% | 74.3% |
| Hussain fall recall | 75.0% (3/4) | 75.0% (3/4) | 75.0% (3/4) | 66.7% (2/3) | 100.0% (4/4) | 100.0% (4/4) |

RF and TCN are stable-to-improved on both sets. **LSTM shows a real, measured accuracy/recall dip specifically on the Sanawar set** (one clip, `Backward_fall`, flips from a true to a false-negative fall detection). This was isolated directly: re-evaluating the OLD (pre-fix) LSTM checkpoint against the identical corrected 9-clip set and extraction code gives 56.2% accuracy / 88.9% (8/9) fall recall — confirming the drop tracks the retrained checkpoint specifically, not an extraction-pipeline or clip-set difference. The most likely explanation is NOT the leakage fix itself but ordinary LSTM training non-determinism (TensorFlow's oneDNN backend on this machine explicitly warns results vary run-to-run from floating-point reduction-order differences, even with a fixed seed) combined with this project's own repeatedly-documented caveat that one flipped clip swings any per-clip metric by ~11-25 points on a set this small. This is reported honestly rather than hidden: the current recommendation (RF as the primary, real-footage-robust choice; TCN as the companion for the cleaner-scenario/GPU-acceleration case) is unaffected, since it was never LSTM-favoring to begin with, but LSTM's real-footage numbers should not be treated as more precise than a 9-clip test set actually supports.

### 6.6 Other audit findings (this session)

- **NaN/Inf numerical-stability sweep** (pipeline_utils.py, lstm_features.py, gait_features.py, gait_risk.py, all three classifiers): no unguarded division/sqrt/arccos/log/empty-reduction bugs found. Every risky operation traced to a real, effective guard. This codebase has clearly already been through prior hardening passes.
- **GAIT module**: independently re-verified against `docs/GAIT_CODE_REVIEW.md`'s 17 findings — the large majority are confirmed genuinely fixed (not just claimed fixed); a few remain honestly open and documented as such (the bend/sit geometric-degeneracy ambiguity, Finding #3, and the single-transition-per-window contract, Finding #7). `TorsoBaselineCalibrator`/`StreamingGaitRiskAssessor`'s live wiring into `realtime_fall_detection.py` is real, tested, and defensively wrapped (a GAIT failure can never stall or crash fall detection). No new numerical issues found. 197/197 GAIT-specific tests pass.
- **Group/subject leakage**: sequence-level split integrity is confirmed sound (70 distinct sequence IDs, zero cross-fold overlap by construction). **However, no subject-identity metadata exists anywhere in this pipeline.** The real training data is drawn from the public UR Fall Detection Dataset, recorded by a small number of repeat volunteers across its sequences — the same physical person plausibly appears in both the train and validation folds even though no single *video* does. This cannot be fixed without new subject-labeled data; it is a genuine, disclosed limitation, not a coding bug, and is why validation-split numbers are treated as directional rather than a precise generalization estimate throughout this project's own documentation.
- **Documentation drift found and fixed**: `README.md`'s status table and two prose sections claimed "No YOLO/object-detection layer... not started" — false; `src/detection/` is real, committed, and already integrated as an additive signal in `realtime_fall_detection.py`. Fixed. `docs/RF_GENERALIZATION_INVESTIGATION.md`'s "found, not fixed" leakage section is now marked resolved with the fix description and before/after numbers (Section 6.3 above).
- **Dead-code candidates identified in this session, confirmed and removed in a later session**: `src/detection/diagnose_v5_v6_laying_dim.py` and `diagnose_v6_calibration.py` (one-off investigation scripts from a single commit, `fb09a56`, zero references anywhere else in the repo) and `src/posture/posture_classifier.py` (legacy pre-LSTM CLI, superseded by `pipeline_utils.classify_posture_and_fall`, zero imports/test references) were all exhaustively re-checked for imports, CLI usage, test references, and doc mentions before removal. `src/posture/posture_features.py` was investigated the same way and found genuinely NOT dead -- `tests/test_posture_pipeline.py::test_posture_feature_script_runs_from_repo_root` actually subprocess-invokes it and asserts on its output, so it was kept.
- **Minor, accepted-as-is**: `hybrid_evaluate.py` hardcodes `WINDOW_SIZE = 30` rather than reading it from the encoder JSON the way `SequenceWindowClassifier` does — currently consistent with every trained model, but would silently drift if a future retrain ever changed the default window size. Not fixed this session (no current bug, just a latent risk); worth a follow-up if window size ever becomes a tuning knob.

### 6.7 Test suite status

Full suite (`python -m unittest discover -s tests -v`): **264/264 pass** (261 pre-existing + 3 new in `tests/test_preprocessing_leakage.py`), 0 failures, 0 errors — run after the retrain, against the NaN-preserving dataset, not before it.

### 6.8 Footage still needed (GAIT calibration — unchanged conclusion from `docs/GAIT_CALIBRATION_DATASET_PLAN.md`/`GAIT_DATA_ASSESSMENT.md`, reconfirmed this session)

The GAIT module's real-footage corpus (`test_footage/GAIT_Analysis_Test_Footages/`, 16 clips) remains narrowly purpose-built to close specific already-identified findings, not a general calibration set. Still needed, highest-leverage first:
1. **`quiet_stand`** — ≥10 clips, 8-10s, front-on, stationary. `postural_sway`'s risk-mapping sigmoid center has zero real reference point; this is the single highest-leverage gap per the assessment doc.
2. **`slow_walk` / `fast_walk`** — ~10 + ~8 clips. Only one mid-pace walking clip exists; both tails of the walking-speed sigmoid are uncalibrated.
3. **`sway_wobble`** — ≥10 clips, 10-15s. Needed to validate postural_sway's elevated-risk tail; explicitly left open pending a genuinely-sitting-vs-bending discriminator.
4. **`sts_fast`** — ~10 clips. The fast-descent guard rests on one legacy reference clip.
5. **An isolated, unoccluded, front-on, well-lit deep bend (≥2-2.5m distance)** — to separate the still-open geometric bend/sit degeneracy from the already-fixed occlusion-driven false positive, which the one existing deep-bend clip conflates.
6. **2-3 additional subjects** performing sit-to-stand and standing-bend, varying body proportions/camera distance — needed to move from a per-window-relative torso-length plausibility check to an absolute one.

All GAIT thresholds remain explicitly N=1-subject, self-recorded, behavioral-label (not clinical) calibration — no sensitivity/specificity numbers exist and none should be implied from this corpus.

For LSTM/TCN/RF (not GAIT): the Sanawar (now 9) and Hussain (now 19) real clips remain, in this project's own words, "still a small evaluation set... one flipped clip is worth ~12-25 points of any per-clip recall metric" (directly demonstrated again this session by the LSTM Sanawar result, Section 6.5). More real fall/ADL footage, ideally from more distinct subjects, would meaningfully tighten these numbers; this is a data problem, not a modeling one.

---

## 7. Second full-project audit (a later session) — pruning/L1L2 verification, LSTM Sanawar root cause, dead-code removal

A follow-up, deliberately skeptical full-project audit, explicitly asked not to stop at Section 6's conclusions. One premise from the request was corrected up front rather than assumed: **there is no neural-network weight/sparsity pruning (TFMOT-style) anywhere in this codebase for LSTM or TCN** -- no library import, no schedule, no wrapper, confirmed by an exhaustive repo-wide search. The only thing resembling "pruning" is `rf_trainer.py`'s decision-tree complexity controls (`min_samples_leaf=20`, `max_features=0.1`), a different technique for a different model type, already rigorously ablated (10+11-config sweeps, both real-footage-confirmed) in `docs/RF_GENERALIZATION_INVESTIGATION.md`. Re-verified this session against the CURRENT retrained checkpoint directly (not just the historical claim): `models/rf_posture.joblib` has `min_samples_leaf=20`, `max_features=0.1`, mean tree depth 15.75, total node count 69,222 -- matching the documented configuration exactly.

### 7.1 L1/L2 regularization -- verified experimentally, not just read from source

Built the real Keras model objects both ways and inspected them directly (not just the config code): TCN's default `L2_REG=1e-5` attaches a real `kernel_regularizer` to all 10 Conv1D/Dense layers (`model.losses` has 10 nonzero terms); `l1=0, l2=0` attaches none at all (0 terms, not zero-valued ones -- byte-identical graph for existing callers, as the docstring claims). Regularization-loss magnitude scales linearly with the coefficient (100x coefficient -> ~100x loss, measured: 0.003337 -> 0.333735). Confirmed the penalty is actually included in the compiled loss `model.fit()` optimizes, not just present as inert metadata (`model.evaluate()` on identical weights/data: loss 3.232 at l2=0 vs. 6.570 at l2=0.01, difference matching the expected regularization contribution almost exactly). Locked in as `tests/test_regularization.py` (6 tests).

### 7.2 LSTM's Sanawar weakness -- root cause found, not just described

The LSTM's Sanawar accuracy drop reported in Section 6.5 was investigated to a concrete mechanism, not left at "training non-determinism" (that earlier explanation is retracted -- it was a reasonable hypothesis but wrong, found by actually tracing the divergence rather than continuing to guess). Direct comparison confirmed the flipped clip was `Far_fall`, not `Backward_fall` as first assumed (`Backward_fall` was a false negative for LSTM both before AND after retraining -- a separate, pre-existing, unrelated weakness). Frame-by-frame raw-class inspection on `Far_fall` showed the old and new checkpoints agree almost exactly on WHEN the fall happens (frame 60 of 129, both checkpoints), and disagree only on WHICH of two adjacent classes to assign the sustained aftermath: old calls frames 60-129 `"Fall"` (confidence climbing to ~0.99), new calls the identical frames `"Lying"` (confidence ~0.68-0.97) -- both physically correct, differing only on the transient-vs-settled label boundary that the training-label-derivation rule (`"Fall"` only if a window contains a heuristic-flagged frame, else last-frame's label) makes inherently fuzzy for this region. The 32-of-132 feature columns whose imputation medians measurably shifted under the leakage fix are a plausible, mechanistically-grounded driver of exactly this kind of boundary shift. Critically, **this narrow-signal weakness does not reach the deployed system**: `hybrid_evaluate.py`'s heuristic+LSTM OR-gate still scores `Far_fall` a true positive via the heuristic path alone, confirmed by directly running it end to end (`Heuristic: TP +53f`, `Hybrid: TP +53f`) -- the raw-LSTM-only scoring `compare_all_models.py` uses is stricter than what the actual production pipeline does.

### 7.3 LSTM L1/L2 -- never separately validated until now, tested properly, adopted

The LSTM previously shipped with `l1=0, l2=0` (no regularization at all), unlike the TCN -- explicitly flagged in this file's own prior text as "not turned on... hasn't been separately validated for the LSTM." A 4-config sweep (baseline, l2=1e-5, l2=1e-4, l1=1e-5) was run using ONLY the group-aware validation split for selection (no footage from Sanawar/Hussain used in choosing among candidates, per this project's own explicit anti-pattern about not tuning against the real test sets). `l2=1e-5` -- the identical value already independently chosen for the TCN -- won on validation accuracy (65.76% -> 69.02%). Selection was then, and only then, confirmed (not re-tuned) against both independent real-footage sets: Sanawar accuracy 50.8% -> 70.3% (fall recall 7/9 -> 8/9), Hussain accuracy 56.5% -> 58.5% (fall recall unchanged 3/4, false positives 8 -> 6) -- a clean win with no trade-off on either set. Adopted as the new production default (`lstm_trainer.py`'s `L1_REG`/`L2_REG` module constants, mirroring `tcn_model.py`'s existing pattern); production `models/lstm_posture.keras` retrained accordingly. `tests/test_regularization.py` updated to assert the new production default is genuinely non-zero.

### 7.4 Dead code -- exhaustively re-verified, then actually removed

Each of the four files flagged (not removed) in Section 6.6 was re-checked for imports, CLI usage, test references, doc mentions, and git history before any deletion:
- `src/detection/diagnose_v5_v6_laying_dim.py`, `diagnose_v6_calibration.py` -- CONFIRMED DEAD (single commit each, `fb09a56`, zero references anywhere else). Removed.
- `src/posture/posture_classifier.py` -- CONFIRMED DEAD (legacy pre-LSTM CLI, superseded by `pipeline_utils.classify_posture_and_fall`, zero imports/test references). Removed.
- `src/posture/posture_features.py` -- **NOT dead, kept**: `tests/test_posture_pipeline.py::test_posture_feature_script_runs_from_repo_root` genuinely subprocess-invokes it and asserts on its output. This is exactly the "verify before deleting" case the audit was designed to catch -- it looked like the same kind of legacy file as `posture_classifier.py` but has a real, currently-passing test dependency.

### 7.5 Configuration drift -- fixed the real one, left the deliberate one alone

`hybrid_evaluate.py` hardcoded `WINDOW_SIZE=30`/`RAW_HISTORY_NEEDED=31` as module constants instead of reading them from the LSTM encoder it already loads -- a genuine latent drift risk (a future retrain with a different `--window-size` would silently desync this script). Fixed: `load_lstm_model()` now reads `window_size` from the encoder and returns it; threaded through `classify_frames_hybrid()`/`evaluate_clip_hybrid()`/`main()` as a real parameter, with the module constants kept only as an unreachable-in-practice fallback for the encoder-missing case. `RAW_FEATURE_DIM=66` also de-hardcoded to `LANDMARK_COUNT * 2`. Verified with a live smoke run (`window_size=30` correctly read and logged).

Investigated but NOT changed: `evaluate_real_footage.py`'s `POSTURE_CLASSES = ["Standing","Sitting","Lying"]` vs. `compare_tcn_lstm.py`'s `POSTURE_CLASSES = [...,"Unknown"]` -- two separately-defined lists, but `compare_tcn_lstm.py`'s own comment already cross-references `evaluate_real_footage.py`'s version, indicating this is a known, deliberate parallel structure (heuristic-only vocabulary vs. ML vocabulary), not silent drift -- and unifying them risks changing what scored accuracy numbers mean, which was judged not worth the risk for a cosmetic fix. Left as-is, documented here as a reviewed, accepted finding rather than an unexamined one.

### 7.6 Full real-footage matrix -- all 28 available clips, zero crashes

Every clip in both real-footage sets (9 Sanawar + 19 Hussain = 28) was evaluated against all three models with the final, fully-updated pipeline. Zero NaN/Inf propagated to any of the 17,451 total per-window predictions (5,817 windows x 3 models) across either set -- confirmed directly by scanning every model's confidence column, not inferred. Full per-clip tables: `results/all_models_sanawar_final/`, `results/all_models_hussain_final/`. One clip, `SitFast_GetupFast`, scores 0% for all three models simultaneously (GT="Sitting" throughout, all three confidently but wrongly predict "Standing"/other) -- traced to zero NaN/missing-landmark issues (perfect extraction, mean confidence 0.80), so this is not a software or numerical bug. It matches this project's own already-documented, already-investigated "Sitting" class weakness (9.2% of real training windows vs. Standing's 39.8%; TCN's own notes found Sitting confusions dominate ~74% of real-footage misclassifications) -- classified as insufficient training diversity for this specific fast-sit posture, not something a code fix can address, and NOT re-attempted via class-weighting given that exact remedy is already documented as tested and rejected (TCN_IMPLEMENTATION_NOTES.md Sec 6.5) for trading away fall-detection recall.

### 7.7 Test suite status (this round)

271/271 pass (270 + 1 new test from the LSTM regularization-default update), including a fresh full GAIT recheck (202/202) confirming this round's changes (hybrid_evaluate.py, dead-code removal) didn't touch shared GAIT-adjacent infrastructure.

---

## 8. Third full-project audit (a later session) -- cleanup, remaining config drift, Sitting-class data root cause

Explicitly scoped to fixes that need NO new footage (new diverse video is being collected separately). A parallel fresh re-audit (independent of Sections 6-7's own conclusions) found:

- **Fixed**: `realtime_fall_detection.py`'s `GAIT_WINDOW_FRAMES = 150` was itself a hardcoded duplicate of `StreamingGaitRiskAssessor.__init__`'s own default -- now derived via `inspect.signature(...).parameters["window_frames"].default` instead of a second literal `150`, closing the exact "documented but not structurally prevented" drift the original comment already worried about.
- **Fixed (stale docs)**: `README.md` credited only the TCN with `l2=1e-5`, still listed "66 tests total" (now 271 across 8 files, one file's own list was 4 files short), and the project-structure tree omitted `src/detection/` (a real, wired-in module) and `benchmarks/`. All corrected.
- **Investigated, kept**: `check_cameras.py` -- initially looked like a dead-code candidate (zero repo references), but on inspection it's a small, self-documented, genuinely distinct dev utility (scans multiple camera indices to find the real physical webcam) from `src/camera/camera_test.py` (tests one fixed camera) -- not a duplicate, not the "one-off investigation script" pattern that justified removing the 3 files in Section 7.4. Added to README's structure tree instead of removing it.
- **Reviewed, not changed**: `GaitPipeline.__init__`'s own separate `window_frames: int = 150` default (a different class, not currently used by `realtime_fall_detection.py`, which calls `StreamingGaitRiskAssessor` directly) -- a milder, currently-inert instance of the same pattern; not fixed since it isn't live/reachable from any current caller and touching `gait_stream.py` for a cosmetic parity fix wasn't judged worth the risk to shared, heavily-tested infrastructure.

### 8.1 Repository cleanup

Four untracked `results/` directories from this session's own earlier diagnostic work were confirmed as pure, uncited duplicates (identical numbers to a directory that IS cited by `docs/IMPLEMENTATION_PLAN.md`/`docs/TCN_REGRESSION_REPORT.md`) and removed: `results/all_models_hussain_postleakfix/`, `results/all_models_sanawar_postleakfix/` (both an 8/17-clip run superseded by the corrected 9/19-clip `_full9`/`_full19` versions, which ARE cited), `results/lstm_l2_candidate_hussain/`, `results/lstm_l2_candidate_sanawar/` (scratch candidate-evaluation runs, numbers identical to the production `_final` runs once the candidate was promoted). Kept: `results/lstm_old_checkpoint_isolation_check/` (uncited by exact path but the unique, small, directly-relevant evidence artifact behind the Far_fall root-cause finding in Section 7.2 -- reproducible from `models/pre_leakage_fix_backup/` if ever needed again, but cheap enough to keep as-is). Pre-existing, git-tracked `results/` directories (`baseline_regress/`, `round4_8-7-26/`, `tcn_vs_lstm/`, `tcn_vs_lstm_fair/`, `yolo_person_detection/`, `all_models_sanawar/`, `all_models_hussain/`) predate this session, are deliberately committed by the team, and were left untouched -- reviewed, not blindly assumed safe. `benchmarks/gait_old_impl.py` and `benchmarks/regression_check_old_corpus_sts.py` were checked despite "old"/"backup"-sounding names and confirmed to be legitimate, actively-used regression-testing infrastructure (an intentional frozen pre-vectorization GAIT implementation for diffing behavior against, not dead code) -- not removed.

### 8.2 Hybrid system: investigated a general fix for the weak-LSTM-confidence pattern, did not implement it

Section 7.2 found the LSTM's raw "Fall" confidence is sometimes weak/absent on `Far_fall`/`Backward_fall` because the model correctly prefers "Lying" for the settled aftermath. A generalizable (not clip-specific) idea was considered: have the hybrid decision logic treat the LSTM's OWN predicted Standing/Sitting -> Lying transition as corroborating evidence, mirroring how the heuristic already reasons about transitions -- not just requiring a literal "Fall"-class hit. Investigated whether this is safely gradable right now: checked `LyingdownSlowly` (a deliberate, slow, non-fall lying-down clip) and found this project's OWN ground-truth/scoring convention already treats ANY Standing-to-Lying transition as the positive "fall" target for scoring purposes (get_fall_window() builds its window from any Transition-then-Lying/Fall state sequence, regardless of manner) -- meaning the current 28-clip corpus contains no genuine "person deliberately lies down for an innocuous reason and this should NOT alarm" case to validate a false-positive risk against. Implementing this now would mean iterating only against the same 28 clips already used for every other LSTM/TCN/RF measurement -- exactly the "tune against the test set" anti-pattern this audit is required to avoid. **Not implemented.** Documented as a well-reasoned, scoped recommendation for later, contingent on new footage that includes genuine benign non-fall Standing-to-Sitting/Lying transitions (see Section 8.4's data plan) to validate against before this could be safely built.

### 8.3 Sitting-class weakness -- root cause traced to training-data provenance, not a code problem

`SitFast_GetupFast` (Section 7.6) was traced further this round. **Every one of the 38 sequences containing real "Sitting"-class training windows comes from the public UR Fall Detection Dataset's `cam0` recordings only** (26 `adl-*` activities-of-daily-living sequences + 12 `fall-*` sequences where sitting appears as a brief pre/post-fall phase) -- confirmed directly from `data/lstm_dataset.npz`'s `groups` array and `data/processed_keypoints/pose_keypoints.csv`'s `sequence_id` column. Sitting has the fewest real sequences of any non-catch-all class (38, vs. Standing's 55, Lying's 52, Fall's 42). This means **zero** of this team's own self-recorded footage (any camera angle, room, subject, or sitting style/speed different from UR Fall's fixed lab setup) currently contributes anything to the Sitting class -- every real "Sitting" example the model has ever trained on is one fixed camera position, one fixed room, UR Fall's own volunteer pool, and (for the `adl-*` sequences) unhurried, deliberate sitting. `SitFast_GetupFast`'s fast, self-recorded, different-room, different-camera sitting motion is maximally far from all of that -- a genuine, data-explained generalization gap, not a bug. One concrete, low-cost (no new recording needed) mitigation is identified in Section 8.4: UR Fall Dataset also publishes a second camera angle (`cam1`, ceiling-mounted) for the same sequences, which was never downloaded/ingested (`data/ADL/`, `data/Fall/` on disk contain `cam0` folders only) -- free camera-angle diversity for every class, not just Sitting, at zero recording cost, using the existing `src/data_processing/build_ur_dataset_from_data_root.py` pipeline unmodified once the raw files are present.

### 8.4 Evaluation-protocol protection -- verified, not just assumed

Confirmed structurally (not just by convention) that `test_footage/` can never leak into training: grepped every dataset-building/training file (`src/data_processing/*.py`, `lstm_dataset.py`, `lstm_trainer.py`, `tcn_trainer.py`, `rf_trainer.py`) for any reference to `test_footage` and found none -- the training pipeline only ever reads from `data/processed_keypoints/*.csv`, which is built exclusively from `data/ADL/`/`data/Fall/`/`data/processed_keypoints/real_*.csv`, entirely separate directories from `test_footage/`. This is an inherent, already-existing protection, not something this session added.

### 8.5 Test suite status (this round)

271/271 pass (unchanged count -- this round's fixes were config/doc changes, not new testable behavior). Re-ran after every change.

## 9. Fourth full-project audit (a later session) -- UR Fall cam1 ingestion, and a reusable calibration harness for GAIT

Two independent workstreams, run to convergence: (1) an analyze-fix-validate loop closing everything actionable without new footage, following up on Section 8.3's cam1 recommendation; (2) a reusable, re-runnable harness so GAIT calibration evidence (Section 8.3's still-open `quiet_stand`/`slow_walk`/`fast_walk`/`sway_wobble`/`sts_fast` gaps -- unchanged this round, still genuinely footage-gated) can be gathered the moment new footage exists, without re-deriving the approach each time.

### 9.1 cam1 is real for Fall sequences only -- Section 8.3's "every class" claim corrected

Section 8.3 assumed cam1 gives "free camera-angle diversity for every class, not just Sitting." Verified directly against the dataset's current host (`fenix.ur.edu.pl`, migrated from the dead `fenix.univ.rzeszow.pl`): `HEAD` on all 30 `fall-NN-cam1-rgb.zip` URLs returns 200; all 40 `adl-NN-cam1-rgb.zip` URLs return 404. **cam1 does not exist for any ADL sequence.** Since Section 8.3 itself traced Sitting's weakness to 26 of its 38 real sequences coming from `adl-*` (cam0 only, unreachable by cam1) and only 12 from `fall-*` (reachable), cam1 could only ever help a minority of the Sitting gap, not "every class" uniformly. Downloaded and integrity-checked (`unzip -t`) all 30 available `fall-*-cam1-rgb.zip` archives (~1.1 GB) and extracted them into `data/Fall/fall-NN-cam1-rgb/`, matching the existing `cam0` nested-folder convention exactly.

### 9.2 Two real bugs found: the cam1 pipeline had never actually been run before

`src/data_processing/build_ur_dataset_from_data_root.py` (Section 8.3's cited "unmodified" pipeline) crashed immediately on its first real run:

- **Bug 1**: its `PoseLandmarker` was built with `RunningMode.IMAGE`, but `process_ur_sequence()` (imported unchanged from `build_lstm_datasets.py`) always calls `detector.detect_for_video()`, which raises `ValueError` against an IMAGE-mode detector on the very first frame.
- **Bug 2** (surfaced only after fixing Bug 1): the script built ONE detector and shared it across all 100 sequences. VIDEO-mode detectors require monotonically increasing timestamps across every call on one instance, and each sequence's own clock restarts at 0 -- the shared detector crashed with "Input timestamp must be monotonically increasing" on the second sequence's first frame, and (per `make_video_detector()`'s own docstring in `build_lstm_datasets.py`) would have silently leaked pose-tracking state across sequence boundaries even where it didn't outright crash.

Both fixed by delegating detector construction to `build_lstm_datasets.py`'s own already-correct `make_video_detector()` (one fresh detector per sequence, closed after use) -- exactly the pattern `build_lstm_datasets.py::main()` already uses for the same dataset via its own `datasets/UR_data` path. Two regression tests added (`tests/test_build_ur_dataset_from_data_root.py`) so neither bug can silently reappear. This means the 70-`cam0`-sequence dataset this project has trained on up to now was never actually produced by this adapter script -- it must predate it (produced via `build_lstm_datasets.py` directly against a `datasets/UR_data`-style layout before the data was reorganized under `data/ADL`/`data/Fall`).

### 9.3 Ingestion result and retrain -- mixed, honestly reported, nothing tuned in response

After both fixes, ingestion succeeded cleanly: 13,531 frames across 100 sequences (70 cam0 + 30 cam1), 0 errors. cam1 added 7 new Sitting-containing sequences (all `fall-*`-sourced, as predicted by 9.1) -- Sitting rows went from 1,298 to 1,315; the rebuilt `lstm_dataset.npz` shows Sitting's sequence count rising from 38 to 52. Backed up pre-ingestion `data/processed_keypoints/*.csv`, `data/lstm_dataset.npz`, and all model files to `data/pre_cam1_ingestion_backup/` / `models/pre_cam1_ingestion_backup/` before rebuilding (same convention as `models/pre_leakage_fix_backup/`).

All three models retrained on the cam1-augmented dataset and re-validated on the full real-footage corpus (`compare_all_models.py`, both `Sanawar Testing 7-22-26` and `Hussain Testing 7-30-26`). Results are genuinely mixed -- reported as-is, per this project's own rule against tuning based on ambiguous evidence:

| Metric (Hussain, 19 clips, 893 Sitting-window support) | Before | After cam1 | Change |
|---|---|---|---|
| LSTM Sitting recall | 0.389 | 0.411 | +0.022 |
| TCN Sitting recall | 0.237 | 0.499 | **+0.262** |
| RF Sitting recall | 0.674 | 0.534 | **-0.140** |
| LSTM overall accuracy | 56.5% | 52.5% | -4.0pp |
| TCN overall accuracy | 50.9% | 62.9% | **+12.0pp** |
| RF overall accuracy | 74.3% | 67.0% | **-7.3pp** |
| LSTM fall false positives (clips) | 8 | 12 | worse |
| TCN fall false positives (clips) | 9 | 6 | better |
| RF fall false positives (clips) | 7 | 7 | unchanged |
| Fall-detection recall, all 3 models | 66.7-100% | 100% | improved/unchanged |

TCN improved broadly; RF regressed on accuracy and Sitting recall (fall recall held at 100%); LSTM's overall accuracy dropped modestly while its fall-detection recall improved. **Section 8.2's LSTM Far_fall/Backward_fall weak-confidence pattern is completely unchanged**: still 0/99 and 0/81 windows predicted "Fall" on those exact clips (avg confidence 0.874/0.683, both up slightly from baseline but never crossing into a "Fall" prediction) -- confirming Section 8.2's own conclusion that this pattern is about the ground-truth Standing-to-Lying convention, not camera-angle diversity. No new crashes, schema mismatches, or camera-angle-specific errors surfaced in either corpus's evaluation output. **Nothing was tuned in response to these numbers** -- per this audit's standing rule, a training-data-composition change with a mixed, not-unambiguous effect is not the kind of "clear as the leakage fix" evidence that justifies touching a threshold, weight, or hyperparameter; RF's regression and LSTM's false-positive increase are documented as open items for human judgement (Section 9.5), not fixed.

### 9.4 Reusable GAIT calibration harness -- built and verified, not run for conclusions

`benchmarks/gait_calibration_harness.py` added: given a folder of subfolders named after a calibration purpose tag (`quiet_stand/`, `sway_wobble/`, `slow_walk/`, `fast_walk/`, `normal_walk/`, `sts_normal/`, `sts_fast/`, or any other tag reported generically), it runs every clip through the exact production code path (`build_pose_row` -> `classify_posture_and_fall` -> `TorsoBaselineCalibrator` -> `StreamingGaitRiskAssessor`), reusing `benchmarks/gait_risk_distribution_analysis.py`'s extraction/caching rather than duplicating it, and reports per-signal raw-value and `risk_contribution` distributions against `src/gait/gait_risk.py`'s current sigmoid centers/slopes, with an AGREES/DISAGREES verdict for tags with a known directional expectation. It never edits `gait_risk.py`. Idempotent and incremental: per-clip extraction is cached, so dropping one new clip into an existing tag folder and re-running only re-extracts that clip. Verified end-to-end (not just unit-tested) by pointing it at a temporary folder built from real, already-existing clips in this repo's corpus (`Sit_Stand_1.mov` under a `sts_normal/` tag, `Stride.mov` under `normal_walk/` and, to exercise the AGREES/DISAGREES branch specifically, `fast_walk/`) -- confirmed correct discovery, aggregation, and verdict rendering. This was a plumbing smoke-test only; per this audit's standing rule, **no calibration conclusion was drawn from it**, since none of those clips are the deliberate calibration recordings Section 8.4/`GAIT_CALIBRATION_DATASET_PLAN.md` describes. Also fixed, while wiring the harness up: `gait_risk_distribution_analysis.py`'s `CACHE_DIR` was hardcoded to a now-nonexistent path from a prior session's own scratchpad -- moved to a repo-relative, gitignored `benchmarks/_gait_risk_cache/` so the cache (and this harness, which reuses the same extraction function) is portable across machines and sessions.

### 9.5 Test suite status (this round) and remaining problems

Full suite: 287/287 pass (271 pre-existing + 16 new: 2 in `tests/test_build_ur_dataset_from_data_root.py`, 14 in `tests/test_gait_calibration_harness.py`). Re-ran after every change, both before and after retraining.

Remaining open items after this round:
- **RF's Sitting-recall/accuracy regression and LSTM's fall-false-positive increase (9.3)** -- data-gated in the sense that more real cam1-reachable diversity (or the still-missing ADL angle diversity) might resolve it, but also plausibly ordinary retraining variance on a small dataset; needs either repeated retrains to check variance or a human call on whether the TCN-favoring tradeoff is acceptable. Not fixed this round -- correctly a human judgement call, not a code bug.
- **GAIT calibration gaps (`quiet_stand`, `slow_walk`/`fast_walk`, `sway_wobble`, `sts_fast`)** -- unchanged from Section 8.3, still blocked purely on new self-recorded footage; the Section 9.4 harness is ready to consume it the moment it exists.
- **ADL-side camera-angle diversity** -- still zero (9.1): cam1 cannot close this gap since UR Fall Dataset never published it. The remaining path to more ADL-side Sitting diversity is new self-recorded footage, not further public-dataset ingestion.

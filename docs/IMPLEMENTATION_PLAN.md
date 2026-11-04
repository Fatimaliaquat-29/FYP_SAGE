# SAGE — Parallel Implementation Plan (TCN / YOLO / GAIT)

**Branches:** `TCN_sanawar`, `YOLO_fatima`, `GAIT_hussain`, all forked from `main` at commit `bf1e0b1`.
**Why these three, together:** they map onto Phase 4 (Temporal Model Comparison) and Phase 5 (Hybrid AI Exploration) of `SAGE_FYP_Continuation_Plan.xlsx`, plus one "Advanced Feature Later" (gait/fall-risk) pulled forward. All three are genuinely independent of each other and of the existing fall-detection pipeline *if built the way this plan describes* — new modules, not edits to shared files. See Section 5 for why that matters and what happens when it's time to merge.

---

## 0. Read this first — the one rule that keeps this mergeable

**During this phase, nobody edits these files:** `src/posture/pipeline_utils.py`, `src/posture/lstm/*`, `hybrid_evaluate.py`, `evaluate_real_footage.py`, `realtime_fall_detection.py`. These are the files where nearly every hard-won bug fix in this project's history lived, and they're also the files all three branches would otherwise collide on. Every branch below is scoped to add **new files in new folders** instead. Wiring everything together into the live pipeline is a deliberate, later, one-person-at-a-time step (Section 5) — not something that happens inside these three branches.

If a branch genuinely needs something changed in those files, that's a flag to raise with the whole team first, not a solo edit.

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
4. Only after that integration is stable does an LLM reasoning layer (Continuation Plan Phase 5's other half) make sense to attempt — it's meant to reason over the *combined* structured output of steps 1-3, so building it before they exist would mean building it against a schema that's still guessed at, not real.

# Data Quality Improvement Plan — Fall Detection & Object Detection

Written August 2026. Covers two independent tracks that don't block each
other: Hussain's fall-detection models (LSTM/TCN/RF), and Fatima's
object-detection model (YOLO). Both hit the **same underlying bug** for
different reasons — read the "The shared problem" section first even if you
only own one track, because it explains why both fixes look similar.

---

## The shared problem, in one paragraph

Neither model was trained on labels a human checked. The fall-detection
labels come from our own rule-based heuristic's guesses; the furniture labels
come from a rough off-the-shelf detector's guesses on our own rooms. Both
"student" models learned to imitate an imperfect "teacher" instead of learning
the real thing — so both look good on data that resembles what the teacher
already got right, and struggle the moment they see something new. The fix in
both cases is the same shape: stop trusting the guesses, lean on the labels
that are actually real, and don't throw away information we'll need later
(fall detection still needs full Standing/Sitting/Lying output for future
activity monitoring — we are NOT simplifying to a Fall/Not-Fall-only model).

---

## Track 1 — Hussain: Fall detection (LSTM / TCN / RF)

### Phase 1 — Relabel the public data with the improved rulebook

**What & why:** The public datasets (LeFD, UR) are currently labeled by
calling our OLD heuristic on every frame outside the annotated fall window.
We've since improved that heuristic (the "upright vetoes" in
`pipeline_utils.py`, gated by `ENABLE_UPRIGHT_VETOES`).
Re-labeling with the improved version fixes most of the bad guesses for free,
with zero information lost — we keep full Standing/Sitting/Lying/Fall labels
the whole way through.

> **Correction (Aug 2026):** an earlier draft of this plan said the vetoes were
> "currently switched off" and made turning them on step 1. They were already
> `True` — set in `b566685`, which this plan's own commit descends from. The
> draft was written from a stale `DISABLED BY DEFAULT` comment header that sat
> above the flag; that header has since been corrected. **No flag needs
> flipping.** The rebuild in step 1 is still required, because switching the
> flag on does not retroactively relabel CSVs that were generated before it.

**Steps:**
1. Rebuild the LeFD/UR label CSVs so they pick up the (already-enabled) vetoes.
2. For any frame where even the improved heuristic is still unsure (e.g. mid
   bend, ambiguous torso angle) — don't force a label in. Drop that frame from
   training rather than teach the model a guess.

**Ask AI for help with:** *"In `src/data_processing/build_lstm_datasets.py`,
add a confidence check when labeling frames outside the annotated fall window:
if the heuristic's classification is ambiguous (e.g. torso_angle is in a
borderline range, or legs aren't visible so the upright veto can't apply),
skip the frame instead of assigning a label. Show me how many frames get
dropped before committing to it."*

### Phase 2 — Make the real human-labeled clips count for more

**What & why:** Your own recorded clips (round-2/round-3, and future ones)
have labels YOU checked — these are the only fully-trustworthy fine-grained
posture labels in the whole dataset. Right now they're a tiny fraction of the
training set (~6%), so the model barely notices them next to the much larger
pile of public data. Repeating/oversampling them makes the model pay real
attention to exactly the situations (bending, kneeling, deliberate lying)
where the public data can't teach it anything.

**Steps:**
1. When building the training set, repeat the round-2/round-3 GT-labeled
   frames 2–3x (same trick Fatima's YOLO branch used for the person class —
   `--own_repeat 2` in `src/detection/build_merged_dataset.py`, added in
   `2b33933` — proven to work, low risk).
2. Retrain, check whether it holds or improves fall recall on your existing
   held-out clips before deciding the repeat factor.

**Ask AI for help with:** *"In the dataset-building step, oversample the
frames whose sequence_id starts with `r2_` (or the round-3 equivalent) by
2x when constructing the training windows, without touching the
LeFD/UR-derived portion. Show me the before/after class balance."*

### Phase 3 (optional, later) — Add UP-Fall's real fall clips as a small bonus

**What & why:** `datasets/3D_skeletons-UP-Fall-Dataset-main/` has 82 short,
real, human-checked fall clips in a compatible coordinate format (confirmed —
same 0–1 scale, same 33-point MediaPipe skeleton). It has no ADL/posture
data, so it can't help Phase 1's problem — it's purely a small top-up to the
Fall class, similar in spirit to your round-3 recordings. Low priority, easy
to add later once Phases 1–2 are validated.

### Phase 4 — Retrain and validate honestly

**What & why:** Every previous retrain (v2, v3, v4) was measured against the
same held-out clips so we could tell real improvement from wishful thinking.
Keep doing that — this is the step that decides whether Phases 1–2 actually
worked, not just whether they sound reasonable.

**Steps:**
1. Rebuild `data/lstm_dataset.npz` from the relabeled data.
2. Retrain.
3. Score against the round-2 held-out clips and round-3 falls (same method
   as before — see `models/lstm_checkpoint/README.md` for the comparison
   format).
4. Only replace the shipped model if it beats the checkpoint on BOTH held-out
   negatives and fall recall. If it's mixed, say so honestly rather than
   picking whichever number looks better.

**Ask AI for help with:** *"Retrain the LSTM on the rebuilt dataset, then
score it against the same held-out clips and thresholds used for the v4
model (see the checkpoint README). Report the comparison table before
replacing anything, and back up the current model first."*

---

## Track 2 — Fatima: Object detection (YOLO furniture/objects)

### Phase 1 — ~~Rebalance away from the self-guessed labels~~ SUPERSEDED

> **Measured Aug 2026 (`src/detection/report_label_sources.py`) — this phase
> as written should NOT be done.** Three findings, each independently fatal to
> it:
>
> 1. **The premise is backwards in aggregate.** COCO already dominates: own
>    footage is only **15.2%** of all object boxes (4,599 vs 25,725), or 26.3%
>    at the `--own_repeat 2` v3 actually used. It is *not* "currently
>    outweighed by the pseudo-labeled data."
> 2. **It only ever concerned two classes.** Pseudo-labels exist for just 5 of
>    13 classes, and own footage leads in only `bed` (59.9%) and, at repeat 2,
>    `chair` (48.9%). The other 8 classes are 100% COCO — reweighting does
>    literally nothing for them.
> 3. **The requested mechanism cannot exist.** `--own_repeat` applies to the
>    whole `own` source, person and furniture together, so diluting pseudo-
>    furniture also dilutes the reliably-labeled person boxes. And deleting the
>    furniture boxes instead is *actively harmful* for exactly the reason
>    `copy_split()` already documents about COCO's person boxes: unlabeled
>    objects that are visibly present train as **background**. All 4,168 own
>    images contain furniture.
>
> **Replaced by Phase 1b (better teacher) and a reordering: do Phase 3 first.**

### Phase 1b — Improve the teacher instead of down-weighting it

**What & why:** The pseudo-labels come from **YOLOv8-nano**, the weakest model
in the family (`generate_bbox_dataset.py`, `STOCK_YOLO_PATH`), at
`--object_conf 0.5`. Better labels beat reweighted bad labels, and this
sidesteps the `--own_repeat` problem entirely.

**Steps:**
1. Re-run pseudo-labeling with `--object_model models/yolov8x.pt`. One offline
   pass over 4,168 frames, no training involved — `--object_model` is already a
   parameter, so this is a flag change.
2. Hand-correct the result. This is far cheaper than it sounds: the 4,168
   frames come from only **28 clips across 3 recording sessions**, and
   furniture is static under a fixed camera — so you correct roughly one frame
   per camera setup and propagate, not 4,168 frames.
3. Re-check `datasets/coco_subset/` per-class counts (already measured — see
   the balance table; `couch` 943, `toilet` 726, `refrigerator` 402 are the
   thin ones).

*(The original "Ask AI" prompt for the superseded Phase 1 asked for the
per-class ratio and then a rebalance. The ratio is now a committed script —
`python src/detection/report_label_sources.py --target sources` — and the rebalance half is
the part finding 3 above shows cannot be built.)*

### Phase 2 — Prioritize new rooms over new clips

**What & why:** More footage of the same 2–3 rooms doesn't teach "chair" —
it just gives the model more chances to memorize those specific chairs.
Genuinely different rooms teach generalization; repeat footage doesn't.

**Steps:** When there's time to record, record in rooms the model has never
seen (different house, different furniture style), even briefly — a few
minutes in 3 new rooms is worth more than another hour in a familiar one.

### Phase 3 — Validate honestly — **DO THIS FIRST**

**What & why:** This phase understated the problem, and fixing that moves it to
the front of the queue. It says the current numbers are "partly measuring did
it memorize this room." Measured, it is worse than that: **the validation
labels for furniture are themselves the rough detector's guesses.**

| class | val boxes from own footage (pseudo) | from COCO (human) | pseudo share |
|---|---|---|---|
| chair | 1835 | 648 | **73.9%** |
| bed | 334 | 78 | **81.1%** |
| dining table | 179 | 245 | 42.2% |
| tv | 34 | 90 | 27.4% |

So "chair/bed strong" is scoring the student against the teacher it was trained
to imitate, on the same rooms. That is circular, and **a held-out room does not
fix it by itself** — if that room's furniture is also pseudo-labeled, the
circularity is reproduced intact. The held-out room's labels must be drawn by
hand.

Nothing else in Track 2 can be evaluated until this is done, which is why it
now precedes Phase 1b rather than following it.

**Steps:**
1. Use `Testing_HeldOutEval/` — it already exists, with structural protection
   and a README. Note it currently contains only `empty/`, and **no furniture
   labels at all**.
2. Sample frames (`src/detection/sample_heldout_frames.py`). The `empty/` clip
   is ideal: with no person in frame, the score is pure furniture
   precision/recall and no person confound.
3. **Hand-label the furniture.** The "label one frame, copy the .txt to the
   rest" shortcut only holds if the camera is genuinely static — and the first
   held-out clip is handheld, drifting up to **14px**. Copying there would
   offset every box and bias the one eval set that exists to be trustworthy.
   `sample_heldout_frames.py` now measures drift per clip (phase correlation)
   and reports `camera STATIC` or `camera MOVES`; label individually whenever
   it says MOVES. *(Caught by Hussain in review — an earlier draft of this plan
   recommended the shortcut unqualified.)*
4. Score `yolov8n_sage_merged_v3.pt` against those labels
   (`src/detection/score_heldout_objects.py`). This is the first furniture
   number on this project not scored against pseudo-labels.
5. Keep reporting split by label source from now on
   (`src/detection/report_label_sources.py --target merged-val`) so a contaminated furniture number
   can never be quoted again by accident.

### Phase 4 (parallel, independent) — Medicine-container detection

**What & why:** This isn't a generalization bug — it's a task that hasn't
started yet. Zero training examples exist for pill bottles / blister packs.
Doesn't depend on Phases 1–3 and can happen on its own schedule.

**Steps:** See `docs/MEDICATION_DETECTION_SCOPE.md` (already written) —
roughly 600 labeled images, 2–5 hours with the tracking-assisted labeling
tool, one Colab training run.

**Ask AI for help with:** *"Walk me through using [the labeling tool] to
label ~600 images of medicine containers, following the class list and
format in `docs/MEDICATION_DETECTION_SCOPE.md`, so the output is directly
usable by `build_merged_dataset.py`."*

---

## How the two tracks fit together

- **Fully independent.** Different models, different data, different people
  — nothing here blocks the other track. Work in parallel.
- **Same principle, applied twice.** If one of you gets stuck, the other
  track's phase 1–2 is a good template for what "fixing it" looks like.
- **Both end the same way:** retrain, then measure against footage the model
  has never seen, and only keep the new version if it's honestly better —
  not just different.

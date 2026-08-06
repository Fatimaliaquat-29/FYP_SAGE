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
We've since improved that heuristic (the "upright vetoes" — already written,
currently switched off in `pipeline_utils.py` via `ENABLE_UPRIGHT_VETOES`).
Re-labeling with the improved version fixes most of the bad guesses for free,
with zero information lost — we keep full Standing/Sitting/Lying/Fall labels
the whole way through.

**Steps:**
1. Turn `ENABLE_UPRIGHT_VETOES = True` on, rebuild the LeFD/UR label CSVs.
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
   frames 2–3x (same trick Sanawar's YOLO branch used for the person class —
   `--own_repeat 2` — proven to work, low risk).
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

### Phase 1 — Rebalance away from the self-guessed labels

**What & why:** Right now, furniture boxes (chair/bed/couch/etc.) in your own
room footage were drawn by a rough, un-fine-tuned YOLO model, not a person —
those are "pseudo-labels." A real, human-labeled furniture dataset (COCO) is
already part of the training mix, but it's currently outweighed by the
pseudo-labeled room-specific data. Turning that balance around is the fix.

**Steps:**
1. In `build_merged_dataset.py`, reduce the repeat/weight given to the
   pseudo-labeled "own footage" object boxes relative to the COCO subset.
2. Re-check `datasets/coco_subset/` actually has enough examples per class
   (chair, bed, couch, etc.) — if any class is thin, that's worth knowing
   before retraining, not after.

**Ask AI for help with:** *"In `src/detection/build_merged_dataset.py`,
show me the current ratio of pseudo-labeled own-footage object boxes to
COCO object boxes per class. Then help me rebalance so COCO dominates the
furniture classes while our own footage still dominates the `person`
class (which IS reliably labeled, via MediaPipe)."*

### Phase 2 — Prioritize new rooms over new clips

**What & why:** More footage of the same 2–3 rooms doesn't teach "chair" —
it just gives the model more chances to memorize those specific chairs.
Genuinely different rooms teach generalization; repeat footage doesn't.

**Steps:** When there's time to record, record in rooms the model has never
seen (different house, different furniture style), even briefly — a few
minutes in 3 new rooms is worth more than another hour in a familiar one.

### Phase 3 — Validate on a room held out from training, honestly

**What & why:** The "5.4% false-positive" and "chair/bed strong" numbers we
have now are partly measuring "did it memorize this room," not real
generalization. A clean test needs a room that never appeared in training at
all — same principle as Hussain's held-out clips.

**Steps:**
1. Pick (or record) one room that goes into ZERO training runs, ever.
2. After retraining with the Phase 1 rebalance, measure furniture detection
   and false-positive rate on that room specifically.
3. Compare against the old numbers honestly — if it's still bad, that tells
   us the rebalance wasn't enough, which is useful to know.

**Ask AI for help with:** *"Score `yolov8n_sage_merged_v3.pt` and the
retrained model on [held-out room], reporting per-class precision/recall
and false-positive rate, the same way `benchmark_footage.py` already does
for person detection. Don't include this room in any training or
validation split."*

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

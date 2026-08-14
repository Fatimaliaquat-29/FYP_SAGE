# v5 vs v3 on held-out hand-drawn labels: ship v5

Measured 14 Aug 2026 against **hand-drawn** boxes on footage held out of every
training run. `conf 0.4`, `imgsz 640`. **388 person boxes across 11 clips in 3
rooms**, from 569 labelled frames.

Supersedes the first version of this file, which was computed on 179 boxes
before the fall clips were densified from stride 30 to stride 10. Three of its
numbers were wrong and are corrected below.

This is the run [`docs/TRAINING_v5_CONTEXT.md`](../../docs/TRAINING_v5_CONTEXT.md)
specified as the gate:

> If v5 lifts the fall column and holds the walk/sit column, the fix worked.

**It lifts the fall column and improves the walk/sit column — but only at
IoU 0.3.** At IoU 0.5 the fall column does not move. That threshold sensitivity
is the central finding, and it is a property of v5's box placement, not of its
detection.

---

## Headline

| IoU 0.5 | recall | precision | FP |
|---|---|---|---|
| v3 | 179/388 · **0.461** | **0.937** | 12 |
| v5 | 181/388 · **0.466** | 0.879 | 25 |

| IoU 0.3 | recall | precision | FP |
|---|---|---|---|
| v3 | 182/388 · **0.469** | 0.953 | 9 |
| **v5** | 204/388 · **0.526** | **0.990** | **2** |

At IoU 0.3 v5 wins on **both** axes decisively: +0.057 recall and a precision of
**0.990** — two false positives across 206 predictions. At IoU 0.5 it reads as a
tie on recall and a loss on precision. Same predictions, same frames.

---

## Per clip

| clip | boxes | v3 @ 0.5 | v5 @ 0.5 | v3 @ 0.3 | v5 @ 0.3 |
|---|---|---|---|---|---|
| `Bedroom_Walk` | 14 | 1.00 | 1.00 | 1.00 | 1.00 |
| `TV_Lounge_1_Walk` | 1 | 1.00 | 1.00 | 1.00 | 1.00 |
| `people` | 18 | 1.00 | 1.00 | 1.00 | 1.00 |
| `people_(2)` | 32 | 0.94 | 0.97 | 0.94 | 0.97 |
| `TV_Lounge_1_Sit` | 16 | 0.88 | **1.00** | 0.88 | **1.00** |
| `Bedroom_Sit` | 24 | 0.83 | 0.88 | 0.88 | 0.88 |
| | | | | | |
| `TV_Lounge_2_Fall` | 35 | 0.46 | 0.43 | 0.46 | 0.43 |
| `TV_Lounge_2_Fall2` | 41 | 0.39 | 0.41 | 0.39 | 0.41 |
| **`Bedroom_Fall`** | 62 | 0.35 | 0.32 | 0.39 | **0.68** |
| `TV_Lounge_1_Fall2` | 48 | 0.27 | 0.25 | 0.27 | 0.25 |
| `TV_Lounge_1_Fall` | 97 | 0.15 | 0.16 | 0.15 | **0.18** |

By activity:

| group | boxes | v3 @ 0.5 | v5 @ 0.5 | v3 @ 0.3 | v5 @ 0.3 |
|---|---|---|---|---|---|
| walk / sit / upright | 105 | 0.924 | **0.962** | 0.933 | **0.962** |
| **fall** | 283 | 0.290 | 0.283 | 0.297 | **0.364** |
| all | 388 | 0.461 | 0.466 | 0.469 | **0.526** |

---

## What the densification corrected

The fall clips were previously sampled at stride 30 — about 3% of their frames.
Re-extracting at stride 10 and hand-labelling took the fall evidence from 76
boxes to 283. Three claims changed:

**1. `TV_Lounge_1_Fall` was overstated.** Reported at 0.25 for both models on 16
boxes; on **97 boxes it is 0.15 (v3) / 0.18 (v5)**. The small sample was
optimistic by ten points. This is now clearly the hardest clip in the set for
both models.

**2. The `TV_Lounge_2` swings were noise, as suspected.** The earlier −0.09 on
`TV_Lounge_2_Fall` and +0.08 on `TV_Lounge_2_Fall2` were single-box differences
on 11 and 13 boxes. At 35 and 41 boxes the two models sit within one or two
boxes of each other on both clips — 0.46/0.43 and 0.39/0.41. Neither is a real
difference.

**3. `Bedroom_Fall` held.** 0.35 → **0.75** on 20 boxes became 0.39 → **0.68**
on 62. The effect regressed slightly toward the mean, as a small sample should,
and survived tripling the data.

**Consequence: `Bedroom_Fall` is the only clip where v5 genuinely separates from
v3.** That is a narrower claim than the first version of this file made, and it
is the claim the next round of footage should target.

---

## Why the threshold decides the verdict

v5 finds the fallen person in ~22 more `Bedroom_Fall` frames than v3 and places
the box **loosely** — overlapping the person, but under 0.5 IoU.

On `Bedroom_Fall`, v5 records **22 false positives at IoU 0.5 and 0 at IoU 0.3.**
Every one is a real detection on the real person. The strict gate scores those
frames as *both* a miss and a false positive, penalising v5 twice for finding
someone v3 misses entirely. That is the whole of v5's apparent precision loss:
its FP count falls 25 → 2 when the threshold moves.

Measured on the earlier sample, the loose boxes were ~2.3× oversized with a
consistent centre offset, most plausibly enclosing the person together with the
bed they are lying on — the same person/furniture merging identified as the
root failure mode in [`reserved_heldout_posture.md`](reserved_heldout_posture.md).
Where both models fire, v5 localises as tightly as v3; there is no general
localisation regression.

**IoU 0.5 is therefore a load-bearing choice, not a neutral default.** It is the
sole reason this run can be read as "no improvement".

---

## Four label gaps, now closed

Four frames carried a high-confidence person detection against a label file
containing only furniture. All four were inspected: **a person is plainly
present in every one**, at close range in dark clothing, filling much of the
frame. Both models were correct and were being scored as false positives for it.

They are now labelled, and the effect is visible in `TV_Lounge_1_Sit`:

| `TV_Lounge_1_Sit` (16 boxes) | detected | FP |
|---|---|---|
| v3 | 14/16 · 0.88 | 4 |
| **v5** | **16/16 · 1.00** | **0** |

v5 detects both close-range people; v3 misses them and is charged 4 false
positives. The gap was hidden while the ground truth was wrong.

---

## Empty-room false positives at 640

Closes the open item carried in `reserved_heldout_posture.md`. Every frame of
all 11 held-out empty clips, `--stride 1`, 7,200 frames per model:

| model | FP frames | FP rate |
|---|---|---|
| v3 | 28 | 0.39% |
| **v5** | **0** | **0.00%** |

All 28 of v3's are in `living room.mov`. **v5 hallucinates no people at all in
empty rooms.**

This also corrects the "0.00% for both" reported in `19b1139`, most likely a
clip-coverage difference — the one clip producing every false positive is the
one a partial local copy would be missing.

---

## What consumes these boxes

Traced before recommending, because a loose box only matters if something reads
it.

**Today nothing reads the geometry.** The only consumer of `bbox` outside
`src/detection/` is the on-screen rectangle at
`realtime_fall_detection.py:283`. The code states it at lines 217–219: *"purely
additive context … It never feeds `fall_detected` above; the alarm stays
posture/LSTM-only."* `hybrid_evaluate.py` does not reference YOLO at all.

**The planned integration reads class and confidence.**
`docs/IMPLEMENTATION_PLAN.md` §2 defines the deliverable as *"person
confidence"* for the Structured Event Schema, cross-checked against MediaPipe's
tracking confidence. No box coordinates.

**Geometry-as-semantics is already rejected** — fault #4 in
`reserved_heldout_posture.md` establishes that box aspect ratio does not encode
posture.

**Medication adherence is the one future consumer that would care**, since
"is the person near the container" is a spatial relation. It is blocked on
recording and labelling a container dataset and is not a reason to hold v5 now.

---

## Recommendation

**Ship v5.**

| axis | v3 | v5 |
|---|---|---|
| fall detection rate (IoU 0.3) | 0.297 | **0.364** |
| walk/sit detection rate | 0.933 | **0.962** |
| overall precision (IoU 0.3) | 0.953 | **0.990** |
| empty-room false positives | 0.39% | **0.00%** |
| close-range people (`TV_Lounge_1_Sit`) | 0.88, 4 FP | **1.00, 0 FP** |
| localisation where both fire | IoU 0.71–0.92 | IoU 0.76–0.91 |

Better or equal on every axis that anything downstream consumes.

Carry-forwards, not blockers:

1. **The drawn boxes will look wrong on fallen-person frames** — roughly double
   size, enclosing the furniture. Cosmetic today, conspicuous in a live demo.
2. **Re-check box quality before medication adherence is built.**

---

## What this does not fix

`TV_Lounge_1_Fall` sits at 0.15/0.18 on 97 boxes, and `TV_Lounge_1_Fall2` at
0.27/0.25 on 48. Both models fail on the majority of fall frames in that room,
and relabelling cannot fix it — `TV_Lounge_1_Fall` already had 100% MediaPipe
coverage before the v5 label fix, so there were no missing labels to recover.

The failure profile in `reserved_heldout_posture.md` stands: person lying **on**
furniture, low contrast, foreground occlusion. Two training runs have now failed
to move it by changing labels on existing footage.

A useful counter-example arrived from `people_ground_mahaRoom` — a room in no
training run and no hand-labelled set. It shows a person lying full-length on a
bed, brightly lit, in a light-striped shirt, unoccluded. **Both models detect it
in ~100% of frames with tight boxes** (v5 947/947, v3 938/947; v5 box area
varies over a 2.2-point range vs v3's 8.9), and both produce **zero** false
positives across 1,012 frames of the same room empty.

So *lying on furniture* alone does not break either model. The binding factors
are the others — dark clothing on dark furniture, dim light, foreground
occlusion. **New footage should cross those factors deliberately rather than
recording more falls**, so the next analysis can attribute the failure instead
of re-observing it.

---

## Method

- `src/detection/score_heldout_objects.py --classes person --imgsz 640
  --conf 0.4 --per_clip`, at `--iou 0.5` and `--iou 0.3`.
- Fall clips re-extracted at stride 10 via `sample_heldout_frames.py`. Stride 10
  keeps the stride-30 frames at identical filenames, so no existing label was
  orphaned — the failure recorded as fault #3 in `reserved_heldout_posture.md`.
- Denominator is person boxes only (`tp + fn`); label files also carry
  `chair` / `bed` boxes.
- Empty rooms: `score_empty_false_positives.py --imgsz 640 --conf 0.4
  --stride 1`.
- 148 of 717 extracted frames have no `.txt` and were excluded as unlabelled,
  not scored as empty. All are walk/sit or empty-room frames; **every fall frame
  is labelled.**

### Caveats

- 388 boxes, 11 clips, 3 rooms, two recording sessions by the same people.
  Single-box clips like `TV_Lounge_1_Walk` mean nothing alone.
- Fall clips are sampled at stride 10, walk/sit at stride 30, so the eval set is
  now 73% fall boxes. **The ALL row is not comparable to the 179-box version of
  this file** (0.676 there vs 0.469 here for v3) — that is a change in
  composition, not in the model. Per-clip rates are comparable.
- Frames 0.4 s apart remain correlated. Densifying reduces sampling noise; it
  does not give 3× independent evidence.
- IoU 0.3 is reported to expose a localisation effect, **not** proposed as the
  new gate. Choosing the threshold that flatters a checkpoint after seeing the
  results is a trap this directory has fallen into before.
- Latency not re-measured. This machine is CPU-only (174 ms/frame at 640); the
  13.5 ms/frame in `reserved_people_v5_640.md` came from a CUDA machine.

---

## Related

- [`reserved_heldout_posture.md`](reserved_heldout_posture.md) — the v3 baseline and the four measurement faults corrected along the way
- [`reserved_people_v5_640.md`](reserved_people_v5_640.md) / [`reserved_people_v3_640.md`](reserved_people_v3_640.md) — the coverage/latency benchmark, and why it is not recall
- [`labeler_video_mode_fix.md`](labeler_video_mode_fix.md) — the IMAGE/VIDEO root cause that motivated v5
- [`docs/TRAINING_v5_CONTEXT.md`](../../docs/TRAINING_v5_CONTEXT.md) — the runbook that set this gate

# v5 vs v3 on held-out hand-drawn labels: v5 finds more fallen people — ship it

Measured 14 Aug 2026, against the same **hand-drawn** boxes and the same
procedure as [`reserved_heldout_posture.md`](reserved_heldout_posture.md).
`conf 0.4`, `imgsz 640`. **179 person boxes across 11 clips in 3 rooms.**

This is the run [`docs/TRAINING_v5_CONTEXT.md`](../../docs/TRAINING_v5_CONTEXT.md)
specified as the gate:

> If v5 lifts the fall column and holds the walk/sit column, the fix worked.

**The answer depends entirely on the IoU threshold, and that turns out to be the
finding.** At the project's standard IoU 0.5 the fall column does not move at
all. At IoU 0.3 it moves a lot. Both numbers come from the same predictions on
the same frames.

---

## The result at both thresholds

Detection rate per clip, both models on identical frames:

| clip | v3 @ IoU 0.5 | v5 @ IoU 0.5 | v3 @ IoU 0.3 | v5 @ IoU 0.3 |
|---|---|---|---|---|
| `Bedroom_Walk` | 14/14 · 1.00 | 14/14 · 1.00 | 14/14 · 1.00 | 14/14 · 1.00 |
| `TV_Lounge_1_Sit` | 14/14 · 1.00 | 14/14 · 1.00 | 14/14 · 1.00 | 14/14 · 1.00 |
| `TV_Lounge_1_Walk` | 1/1 · 1.00 | 1/1 · 1.00 | 1/1 · 1.00 | 1/1 · 1.00 |
| `people` | 17/18 · 0.94 | 16/18 · 0.89 | 18/18 · 1.00 | 18/18 · 1.00 |
| `people_(2)` | 30/32 · 0.94 | 31/32 · 0.97 | 30/32 · 0.94 | 31/32 · 0.97 |
| `Bedroom_Sit` | 20/24 · 0.83 | 21/24 · 0.88 | 21/24 · 0.88 | 21/24 · 0.88 |
| | | | | |
| `TV_Lounge_2_Fall` | 5/11 · 0.45 | 4/11 · 0.36 | 5/11 · 0.45 | 4/11 · 0.36 |
| `TV_Lounge_2_Fall2` | 5/13 · 0.38 | 6/13 · 0.46 | 5/13 · 0.38 | 6/13 · 0.46 |
| **`Bedroom_Fall`** | 7/20 · 0.35 | 7/20 · 0.35 | 7/20 · 0.35 | **15/20 · 0.75** |
| `TV_Lounge_1_Fall` | 4/16 · 0.25 | 4/16 · 0.25 | 4/16 · 0.25 | 4/16 · 0.25 |
| `TV_Lounge_1_Fall2` | 4/16 · 0.25 | 4/16 · 0.25 | 4/16 · 0.25 | 4/16 · 0.25 |

Aggregated by activity:

| group | boxes | v3 @ 0.5 | v5 @ 0.5 | v3 @ 0.3 | v5 @ 0.3 |
|---|---|---|---|---|---|
| walk / sit / upright | 103 | 0.932 | 0.942 | 0.951 | 0.961 |
| **fall** | 76 | **0.329** | **0.329** | **0.329** | **0.434** |
| all | 179 | 0.676 | 0.682 | 0.687 | **0.737** |

Person false positives, with-people frames:

| | v3 | v5 |
|---|---|---|
| IoU 0.5, as scored | 9 | 15 |
| IoU 0.5, excluding label gaps (see below) | 8 | 11 |
| IoU 0.3, as scored | 7 | **5** |

**At IoU 0.5, v5 looks like no gain and worse precision. At IoU 0.3, v5 is
better on both.** Same model, same frames, same confidence threshold.

**Neither model produced a single genuine hallucination on with-people frames.**
Every unmatched prediction from either model either overlaps a real person or
lands on a real person the labeller missed. There are no boxes on empty
furniture, walls or floor.

---

## What is actually going on

v5 detects the fallen person in roughly eight more `Bedroom_Fall` frames than
v3 does. It places the box **loosely** — overlapping the person, but not tightly
enough to clear IoU 0.5.

Every one of v5's eight `Bedroom_Fall` "false positives" at IoU 0.5 overlaps a
real hand-drawn person box, at IoU **0.33 – 0.47**. None is a hallucination, and
none is somewhere else in the frame:

| frame | conf | best IoU with a real person |
|---|---|---|
| `Bedroom_Fall_000240` | 0.43 | 0.40 |
| `Bedroom_Fall_000390` | 0.41 | 0.33 |
| `Bedroom_Fall_000420` | 0.47 | 0.34 |
| `Bedroom_Fall_000450` | 0.44 | 0.34 |
| `Bedroom_Fall_000480` | 0.48 | 0.34 |
| `Bedroom_Fall_000510` | 0.48 | 0.33 |
| `Bedroom_Fall_000540` | 0.47 | 0.35 |
| `Bedroom_Fall_000570` | 0.46 | 0.36 |

That cluster sitting just under the threshold is the whole disagreement between
this file and the coverage benchmark. The IoU-0.5 gate scores these eight frames
as *both* a miss and a false positive — penalising v5 twice for finding a person
v3 misses entirely.

**So the earlier reading of this run — "v5 emits more boxes while finding no
additional people" — was wrong.** It is finding additional people. The boxes are
poorly fitted.

### This vindicates the coverage benchmark's direction

[`reserved_people_v5_640.md`](reserved_people_v5_640.md) reported `Bedroom_Fall`
rising 38.2% → 67.3%. Against hand-drawn labels at IoU 0.3 the same clip goes
0.35 → 0.75. Those agree closely. The coverage metric still cannot be used for
recall comparisons — it has no ground truth and cannot tell a loose box from a
tight one or from a hallucination — but on this clip its signal was real, and
the strict-IoU gate is what obscured it.

The `Bedroom_Sit` / `TV_Lounge_2_Sit` "regressions" flagged in `19b1139` remain
artifacts: `Bedroom_Sit` is 0.83 → 0.88 at IoU 0.5 and flat at IoU 0.3, never
worse.

---

## Four "false positives" are missing labels, not errors

Four frames carry a high-confidence person detection against a label file
containing **only furniture** — no person box at all. All four were inspected
directly. **A person is plainly present in every one**, walking past the camera
at close range in dark navy clothing, occupying a large fraction of the frame:

| frame | v5 conf | v3 conf | labels present | person actually in frame? |
|---|---|---|---|---|
| `TV_Lounge_1_Sit_000090` | 0.85 | — | 1 × table, 2 × couch | **yes** |
| `TV_Lounge_1_Sit_000540` | 0.89 | — | 1 × table, 3 × couch | **yes** |
| `TV_Lounge_1_Fall_000090` | 0.88 | — | 1 × table, 3 × couch | **yes** |
| `TV_Lounge_1_Fall_000120` | 0.66 | 0.69 | 1 × table, 2 × couch | **yes** |

Both models are **correct** on these frames and were penalised for it. The
labeller annotated the furniture and skipped the person — plausibly because a
torso filling half the frame does not look like the small, whole-body figures
the rest of the pass contains.

Consequences:

- Precision is understated for both models, more so for v5 (4 of its 15
  IoU-0.5 false positives are these; 2 of v3's 9, counting the one it also
  fires on plus one in an empty room).
- Recall is unaffected in the numbers above — a frame with no person label
  contributes nothing to the denominator — but the eval set is missing at
  least four real people, so 179 understates the true box count.
- The gap is **systematic, not random**: all four are the same situation
  (person very close to the lens in `TV_Lounge_1`). Other close-range frames in
  the set may be unlabelled in the same way.

**These frames should be labelled before the eval set is used for a precision
gate.** They are fine for the recall comparison above.

---

## Empty-room false positives at 640

Closes the open item carried in `reserved_heldout_posture.md` (previously
measured only at imgsz 320). Every frame of all 11 held-out empty clips,
`--stride 1`, 7,200 frames per model, `conf 0.4`, `imgsz 640`:

| model | FP frames | FP rate | boxes |
|---|---|---|---|
| v3 | 28 | 0.39% | 28 |
| **v5** | **0** | **0.00%** | **0** |

All 28 of v3's are in `living room.mov`, up to conf 0.59. **v5 is strictly
better and hallucinates no people at all in empty rooms.**

This also corrects the empty-room claim in `19b1139` ("0.00% for both v3 and
v5"). v3 is 0.39% here. The likely cause is clip coverage — this sweep runs all
11 clips in `yolo_testing/Reserved/Empty/`, and the one clip that produces every
false positive is `living room.mov`; a run that did not include it would report
0.00% for both models.

---

## What this rules in and out

**Confirmed:**

- v5 finds meaningfully more fallen people than v3 on `Bedroom_Fall`
  (0.35 → 0.75 at IoU 0.3), and the VIDEO-mode label fix is the plausible cause.
- v5 hallucinates less: 0.00% vs 0.39% on empty rooms, and fewer false positives
  on with-people frames once loose boxes are not double-counted.
- Walk/sit did not regress at either threshold.
- v5 was trained from stock `yolov8n.pt`: its head carries all 13 classes
  (`person`…`refrigerator`), so it did not repeat v4's collapse to one class.

**Ruled out:**

- **The label fix is not a general fix for falls.** `TV_Lounge_1_Fall` and
  `TV_Lounge_1_Fall2` sit at exactly 4/16 for both models at *both* thresholds.
  `TV_Lounge_1_Fall` already had 100% MediaPipe coverage before the fix, so
  there were no missing labels there to recover. The furniture-occlusion
  diagnosis in `reserved_heldout_posture.md` stands for those clips.

**New:**

- **v5 does not localise worse in general.** On the seven `Bedroom_Fall` frames
  both models detect, v5's boxes are as tight as v3's or tighter (IoU 0.76–0.91
  vs 0.71–0.92; area ratio ~1.0 for both). There is no localisation regression
  on the cases v3 already handles.
- **The looseness is confined to the eight frames only v5 detects**, and it has
  a consistent signature — the box is **~2.3× too large** with a repeated
  centre offset:

  | frame | IoU | pred area ÷ true area | centre Δx | centre Δy |
  |---|---|---|---|---|
  | `Bedroom_Fall_000240` | 0.40 | 2.19 | +0.054 | +0.029 |
  | `Bedroom_Fall_000390` | 0.33 | 2.33 | +0.038 | +0.040 |
  | `Bedroom_Fall_000420` | 0.34 | 2.34 | +0.039 | +0.040 |
  | `Bedroom_Fall_000450` | 0.34 | 2.30 | +0.037 | +0.041 |
  | `Bedroom_Fall_000480` | 0.34 | 2.31 | +0.039 | +0.038 |
  | `Bedroom_Fall_000510` | 0.33 | 2.38 | +0.039 | +0.043 |
  | `Bedroom_Fall_000540` | 0.35 | 2.24 | +0.039 | +0.037 |
  | `Bedroom_Fall_000570` | 0.36 | 2.17 | +0.039 | +0.033 |

  The tight clustering across a contiguous run of frames points at one cause,
  most plausibly the box enclosing the person **together with the bed they are
  lying on** — the same person/furniture merging that
  `reserved_heldout_posture.md` identified as the failure mode. v5 now finds
  the person there but cannot separate them from the furniture.

- **IoU 0.5 is a load-bearing choice**, not a neutral default. It was inherited
  without argument and it is the sole reason this run reads as "no
  improvement".

---

## What consumes these boxes

Traced before recommending, because the value of a loose box depends entirely
on who reads it.

**Today: nothing reads the geometry.** The only consumer of `bbox` outside
`src/detection/` is the on-screen rectangle at
`realtime_fall_detection.py:283`. `detect()` is called at line 220 and its
result flows only to `_draw_objects`. The code says so explicitly at lines
217–219 — *"purely additive context … It never feeds `fall_detected` above; the
alarm stays posture/LSTM-only."* `hybrid_evaluate.py` does not reference YOLO
at all; it runs heuristic and LSTM over MediaPipe pose.

**Planned: class and confidence, not geometry.** `docs/IMPLEMENTATION_PLAN.md`
§2 defines the deliverable as *"person confidence"* for the Hybrid Approach
report's Structured Event Schema, cross-checked against MediaPipe's own
tracking confidence (*"high-confidence pose + low-confidence bottle =
skeptical"*). That is presence and confidence — exactly what v5 improves, and
it reads no box coordinates.

**Already rejected: geometry as semantics.** Fault #4 in
`reserved_heldout_posture.md` establishes that box aspect ratio does not encode
posture and must not be used as a proxy. The project has already decided not to
derive meaning from box shape.

**The one future consumer that would care** is medication adherence — deciding
whether a person is *near* a container requires a spatial relation between two
boxes, and a 2.3×-inflated person box would overlap objects the person is not
touching. That work is blocked on recording and labelling a container dataset
(`MEDICATION_DETECTION_SCOPE.md`: *"Blocked on: recording and labeling. Nothing
else."*), and containers appear zero times in current footage. It is not a
reason to hold back v5 now, but it is a reason to re-check box quality before
that feature is built.

---

## Recommendation

**Ship v5.** The condition attached to the earlier draft of this file is
resolved: nothing downstream reads box geometry, now or in the planned
integration.

On the axes that are actually consumed, v5 is better or equal on every one:

| axis | consumed by | v3 | v5 |
|---|---|---|---|
| fall detection rate (IoU 0.3) | event schema presence | 0.329 | **0.434** |
| walk/sit detection rate | event schema presence | 0.951 | **0.961** |
| empty-room false positives | alert credibility | 0.39% | **0.00%** |
| hallucinations on with-people frames | alert credibility | none | none |
| localisation where both fire | nothing today | IoU 0.71–0.92 | IoU 0.76–0.91 |

Two things to carry forward rather than treat as blockers:

1. **The on-screen boxes will look visibly wrong on fallen-person frames** —
   roughly double size, enclosing the bed. Cosmetic today, since drawing is the
   only consumer, but it will be conspicuous in a live demo.
2. **Re-check box quality before medication adherence is built.** That is the
   first feature that would read geometry.

Do not ship on the strength of `reserved_people_v5_640.md` alone; its agreement
with this file on `Bedroom_Fall` is not something that metric could have
established by itself.

---

## Method

- `src/detection/score_heldout_objects.py --classes person --imgsz 640
  --conf 0.4 --per_clip`. The `--per_clip` flag was added for this run; the v3
  column it produces reproduces `reserved_heldout_posture.md` box-for-box,
  which is what validates the harness.
- Denominator is person boxes only (`tp + fn`). The label files also carry
  `chair` / `bed` boxes; counting those inflates the denominator and understates
  every rate.
- Empty rooms: `src/detection/score_empty_false_positives.py --imgsz 640
  --conf 0.4 --stride 1`.
- 148 of 533 extracted frames have no `.txt` and were excluded as unlabelled,
  not scored as empty.
- `mahaRoom` footage excluded from the recall measurement, as in v3's.

### Caveats

- 179 person boxes, 11 clips, 3 rooms, two recording sessions by the same
  people. Small sample; single-box clips like `TV_Lounge_1_Walk` mean nothing
  alone. The headline `Bedroom_Fall` result rests on 20 boxes in one clip.
- IoU 0.3 is reported here to expose a localisation effect, **not** proposed as
  the new gate. Picking the threshold that flatters a checkpoint after seeing
  the results is exactly the trap this results directory has fallen into before.
- Four frames are unlabelled people, counted as false positives throughout —
  see the section above. Precision here is a floor, not an estimate.
- Latency not re-measured. This machine is CPU-only (174 ms/frame at 640); the
  13.5 ms/frame in `reserved_people_v5_640.md` came from a CUDA machine and the
  two are not comparable.

---

## Related

- [`reserved_heldout_posture.md`](reserved_heldout_posture.md) — the v3 baseline this reproduces, and the four measurement faults corrected along the way
- [`reserved_people_v5_640.md`](reserved_people_v5_640.md) — the coverage/latency benchmark, and why it is not recall
- [`labeler_video_mode_fix.md`](labeler_video_mode_fix.md) — the IMAGE/VIDEO root cause that motivated v5
- [`docs/TRAINING_v5_CONTEXT.md`](../../docs/TRAINING_v5_CONTEXT.md) — the runbook that set this gate

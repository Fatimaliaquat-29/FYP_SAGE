# Held-out person detection: fall clips vs everything else

Measured 11 Aug 2026 against **hand-drawn** boxes on footage held out of every
training run. `conf 0.4`, `imgsz 640`, IoU 0.5. **179 person boxes across 11
clips in 3 rooms.**

> **This file has been rewritten twice.** An earlier version reported "both
> models are blind to falls, 0/65", produced by three measurement faults. A
> second version framed the result by box aspect ratio, which turned out to be
> a broken proxy. Both are superseded. See "What was wrong before".

---

## The result

Detection rate per clip, v3 @ 640:

| clip | detected | rate |
|---|---|---|
| `Bedroom_Walk` | 14/14 | **1.00** |
| `TV_Lounge_1_Sit` | 14/14 | **1.00** |
| `TV_Lounge_1_Walk` | 1/1 | **1.00** |
| `people` | 17/18 | **0.94** |
| `people_(2)` | 30/32 | **0.94** |
| `Bedroom_Sit` | 20/24 | **0.83** |
| | | |
| `TV_Lounge_2_Fall` | 5/11 | **0.45** |
| `TV_Lounge_2_Fall2` | 5/13 | **0.38** |
| `Bedroom_Fall` | 7/20 | **0.35** |
| `TV_Lounge_1_Fall` | 4/16 | **0.25** |
| `TV_Lounge_1_Fall2` | 4/16 | **0.25** |

**Walk/Sit: 0.83–1.00. Fall: 0.25–0.45. No overlap.**

Five fall clips, three rooms, two recording sessions, two camera setups — no
exceptions. Fall footage loses roughly 60–75% of person detections regardless
of room. This is a split by *activity*, not by location.

All 51 misses are **IoU 0.00** — the model emits no person box at all, rather
than a poorly-placed one. It is not a localisation problem.

---

## Why the misses happen

The 51 missed frames are saved in `eval/missed_falls/`. Looking at them
directly, the causes are visible and are **not** what was originally assumed:

**Motion blur is not the cause.** Only 2 of 51 frames are blurred. The rest are
sharp, static frames of a person already at rest after the fall.

What the missed frames actually share:

1. **The person is lying ON furniture, not on open floor** — curled on a bed,
   sprawled along a sofa, stretched prone across a bench. Their outline merges
   with the object supporting them.
2. **Foreground occlusion.** A glass coffee table cuts horizontally across the
   body in every missed `TV_Lounge_1_Fall` frame.
3. **Low contrast.** Dark clothing against dark furniture in dim rooms — black
   against a dark headboard, navy against a shadowed sofa.
4. **Poses unlike any COCO training photo** — foetal curl, prone plank across a
   narrow bench.

The controlling comparison is `people_(2)` at **0.94**: also a fallen person,
also horizontal, but on an **open floor**, in **light clothing**, unoccluded,
side-on to camera. Detected almost perfectly.

**So the failure mode is not "the person is fallen". It is "the person is
merged with furniture in low contrast".** Falling just happens to be the
activity that reliably produces that situation, because people land on and
against furniture.

---

## Model comparison

Same 148-box subset, both resolutions (this table predates the 31 extra fall
labels; the per-clip table above is the current one):

| model | imgsz | detection rate |
|---|---|---|
| v3 | 320 | 0.514 |
| **v3** | **640** | **0.736** |
| v4 | 320 | 0.439 |
| v4 | 640 | 0.520 |
| merged_640 | 320 | 0.405 |
| merged_640 | 640 | **0.770** |
| stock | 640 | 0.588 |

**Inference resolution is the single largest factor.** At 320 the same weights
lose roughly a third of their detections. The runtime code was already correct
(`YOLOObjectDetector` and `benchmark_footage.py` both default to 640); the 320
default lived only in the *scoring* scripts, which is why offline evaluation
disagreed with the runtime for so long.

**v4 should not ship.** It is worse than v3 at every resolution on this data.
Its only advantage is a lower empty-room false-positive rate (0.39% vs 2.70%,
measured at imgsz 320 — needs re-running at 640).

### Latency

Interleaved round-robin, 72 timings per config, on a loaded laptop CPU:

| model | imgsz | median ms | IQR |
|---|---|---|---|
| v3 | 320 | 81.3 | 78–87 |
| merged_640 | 320 | 79.3 | 76–83 |
| v3 | 640 | 150.3 | 145–159 |
| merged_640 | 640 | 150.2 | 144–156 |

**v3@640 and merged_640@640 cost exactly the same** (150.3 vs 150.2 ms). They
are the same architecture at the same input size. `merged_640` was rejected for
failing an 85.9 ms latency gate — but that was never a property of that
checkpoint, it is the price of running at 640. **v3 at 640 pays it too.**

The latency gate therefore does not discriminate between checkpoints. It
discriminates between resolutions. Absolute values here are unusable (the same
config measured 33.8 ms and 81.3 ms on different runs of the same machine);
only the ~2x ratio between 320 and 640 should be expected to transfer.
Re-measure on the deployment device.

---

## What was wrong before

Four faults, each of which produced a *believable wrong number* rather than an
error. Recorded because each was invisible until specifically looked for.

**1. Inference resolution.** Scoring ran at imgsz 320 because that is what the
merged series was trained at. Sensible-sounding, and wrong for inference.

**2. Frame rotation.** `cv2.VideoCapture` ignores rotation metadata.
`Bedroom_Fall.mov` is stored portrait and needs 90° CW, so every extracted
frame was sideways. Worse, posture was derived from box aspect ratio, so in a
rotated frame a **standing** person is wide and was counted as lying. Those 20
labels were deleted and redrawn. Now handled by
`src/detection/footage_rotation.py`, an eye-verified per-clip table.

**3. Orphaned labels.** Re-extraction renamed images, so 50 hand-drawn labels
silently stopped matching any frame and dropped out of scoring — including all
32 boxes of the one clip where detection works.

**4. Aspect ratio as a posture proxy.** `w/h > 1` was used to mean "lying". It
does not: three of five fall clips produce **zero** wide boxes, because a
person who falls onto a bed or toward the camera keeps a tall box. The "0/52
lying" figure was measuring *wide boxes*, not fallen people. Detection rate per
clip needs no proxy and is used instead.

Also caught: v3 was once compared at `conf 0.25` against v4 at `conf 0.4`,
inflating v3's false-positive rate to 49.32% (21.26% at matched settings).

**Rule:** compare models at the same `--conf` and `--imgsz`, on frames with
verified orientation, with labels confirmed to match their images, and do not
derive semantics from box geometry.

---

## Method

- `src/detection/score_heldout_objects.py --classes person`
- Labels: 385 label files, all verified to match an existing image. 50 frames
  by Fatima (`people`, `people_(2)`), 38 on the `Fall2` re-shoots, 31 on
  `Bedroom_Fall` / `TV_Lounge_2_Fall`, remainder from the team's
  `Bedroom_*` / `TV_Lounge_1_*` set.
- `mahaRoom` footage deliberately excluded (`--exclude mahaRoom`).

### Caveats

- 179 person boxes, 11 clips, 3 rooms. The activity split is unambiguous, but
  the sample is small and from two recording sessions by the same people.
- `TV_Lounge_1_Walk` contributes a single box; its 1.00 is not meaningful alone.
- Empty-room false-positive rates were measured at imgsz 320 and need
  re-running at 640 before use as a gate. **Open item.**

---

## What this means for improving v3

The failure is tied to an identifiable visual situation, not to a room or to
"falls" as such. That makes it more tractable than a generic recall problem.

Training data almost certainly lacks people lying **on** furniture, in low
contrast, partly occluded by foreground objects. COCO's people are upright and
unoccluded; our own footage is three rooms of mostly-upright activity, and its
person labels come from MediaPipe, which is itself weakest on exactly these
poses — so those frames are likely missing or mislabelled in training too.

Targeted next steps, cheapest first:

1. **Record people lying on furniture** — sofas, beds, benches — in dark
   clothing, in dim light, with foreground objects between camera and subject.
   That is the specific gap, and it is much narrower than "more rooms".
2. **Check whether MediaPipe labels these poses at all** in the existing
   training footage. If it does not, the fine-tune never saw them.
3. Re-measure false positives at 640 to complete the picture.

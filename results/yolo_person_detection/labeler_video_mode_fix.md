# Root cause: the label generator was still in IMAGE mode

`generate_bbox_dataset.py` — which produces every person label in the training
set — used `RunningMode.IMAGE`. `realtime_fall_detection.py` and
`evaluate_real_footage.py` were switched to `VIDEO` in `b566685`; the label
generator was missed, so all training data has been built by the unfixed path.

---

## Why it matters

MediaPipe Pose is two-stage: a **person detector** finds an ROI, then landmarks
are regressed inside it.

- **IMAGE mode** re-runs the detector from scratch on every frame, no memory.
- **VIDEO mode** seeds the ROI from the previous frame's pose, falling back to
  full detection only when tracking is lost.

In a fall clip the subject is upright and easy to detect for the first second
or two. VIDEO mode carries that tracking *through* the fall. IMAGE mode discards
it and re-detects independently — so the moment the person becomes hard to spot
(dark, on furniture, occluded, in a pose unlike any training photo) it emits
nothing at all.

The result is a self-reinforcing loop: the labeler drops fallen-person frames →
the training set under-represents them → the fine-tuned model cannot detect
fallen people.

---

## How it was found

Diagnosed by elimination on 76 hand-labelled held-out fall frames, where
MediaPipe returned no pose at all on 41 of them:

| hypothesis | test | result |
|---|---|---|
| visibility threshold filtering a weak pose | count poses found but rejected by `min_visibility` | **0 of 76** — nothing to recover |
| a stronger model variant would help | `heavy` vs `full`, grid over `min_vis` | **worse** — more boxes (46 vs 35) but precision 0.39 vs 0.71, fewer usable |
| person is horizontal, detector expects upright | re-run rotated 90cw / 90ccw / 180 | **3–5 of 41** — not the cause |
| detector cannot locate the person in a wide cluttered frame | crop tightly to the labelled person, re-run | **16 of 41 recovered** |

The crop result pointed at stage-one detection failing to *locate* the person
rather than failing to interpret the pose — which is exactly what VIDEO mode
fixes automatically, by supplying the ROI from the previous frame.

Also checked: no `lite`/`heavy` variant is better here, and `full @ min_vis 0.3`
— what the pipeline already used — is the optimal setting of every combination
tried. The threshold and the model variant are both dead ends.

---

## Measured effect

Coverage over the 14 fall/lying training clips, stride 5:

| clip | IMAGE | VIDEO | gain |
|---|---|---|---|
| `Fall_and_lie` | 0.23 | **0.61** | **+0.39** |
| `Side_fall` | 0.50 | **0.88** | **+0.38** |
| `Foward_fall` | 0.57 | **0.93** | **+0.37** |
| `Normal_Fall_1` | 0.84 | 0.97 | +0.12 |
| `Fall_Curled` | 0.71 | 0.81 | +0.10 |
| `Off_axis_fall` | 0.50 | 0.58 | +0.08 |
| `Chair_fall` | 0.78 | 0.84 | +0.06 |
| `Slow_fall` | 0.73 | 0.78 | +0.05 |
| `Normal_Fall_2` | 0.58 | 0.62 | +0.04 |
| `Far_fall`, `Lying_straight`, `Lying_legs_straight` | 0.96–1.00 | unchanged | 0.00 |
| `Backward_fall` | 1.00 | 0.95 | −0.05 |
| `Occluded_fall` | 1.00 | 0.91 | −0.09 |
| **TOTAL** | **0.70** | **0.83** | **+0.13** |

The clips that were worst improve the most. Two regress slightly where tracking
holds a stale ROI; far outweighed.

### Rebuilt dataset

`--stride 2 --pseudo_objects --object_conf 0.35`, same clips and split as v3:

| | IMAGE (old) | VIDEO (new) | change |
|---|---|---|---|
| labelled frames | 4,168 | 4,380 | +212 (+5.1%) |
| object boxes | 4,599 | 4,675 | +76 (+1.7%) |
| **frames from fall/lying clips** | **806** | **1,015** | **+209 (+25.9%)** |
| fall/lying share of person boxes | 19.3% | **23.2%** | +3.9pp |

**209 of the 212 new frames come from fall/lying clips.** Upright clips were
already at 0.99 coverage, so there was nothing to recover there.

### Box quality

Recovered boxes were checked by eye on the three biggest gainers
(`eval/video_mode_check/`). All sit correctly on the subject through the
crouch, the fall and the landing, tightening as the body compacts. No drift onto
furniture, no stale positions. `Side_fall`'s recovered frames are wide boxes of
a person flat on the floor — precisely the examples the training set lacked.

On `TV_Lounge_1_Fall`, where both modes already reach 100% coverage, VIDEO is
marginally worse (median IoU 0.70 vs 0.73, 14 vs 16 usable of 16). VIDEO mode
helps where detection is hard and costs a little where it is not.

---

## Implementation notes

Two things beyond changing the enum, either of which would have silently broken it:

1. **Detection now runs on every frame.** The old loop skipped frames with
   `frame_idx % stride` *before* detection. In VIDEO mode that severs the
   tracking chain, which is the entire point. `stride` now controls only which
   frames are *written*. Cost: pose inference on every frame, roughly doubling
   build time.
2. **A fresh detector per clip** (`make_pose_detector()`), or tracking state
   bleeds one room's ROI into the next.

---

## Limits — what this does NOT fix

**It fixes the labeler, not the detector.** `TV_Lounge_1_Fall` already had 100%
MediaPipe coverage, yet v3 detects only 4 of 16 person boxes there. That failure
is not caused by missing labels.

**+5% data overall.** A 26% increase in fall frames may or may not move
detection measurably. Worth measuring, not worth predicting.

**Conditions absent from the training rooms remain absent.** The held-out
analysis showed the misses share a profile — person lying *on* furniture, dark
clothing against dark furniture, foreground occlusion. No amount of relabeling
creates footage that was never shot.

**Any new fall footage hits the same ceiling.** MediaPipe covers ~46% of the
hardest fall frames even in VIDEO mode, biased toward the easier ones. Plan
recording sessions and labelling sessions together.

---

## Suggested check elsewhere

`src/data_processing/build_lstm_datasets.py` may have the same gap. The
`b566685` fix covered the runtime and evaluation paths; if the LSTM's training
data is also generated by an IMAGE-mode path, the same under-representation of
fallen poses would apply there.

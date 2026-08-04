# S.A.G.E. — Recording Round 2 (targeted gaps)

Companion to [`sanity_check_clips.md`](sanity_check_clips.md), which still holds for
safety and general setup — **read its safety note first, every simulated fall goes onto
a crash mat / mattress.** This document only covers the gaps that the July 2026
diagnostic work actually measured, so the recording effort goes where the evidence says
it is needed.

---

## 0. Fix the framing first — this is worth more than any new clip

Measured across the existing test clips: the camera **crops the subject at the waist**.
MediaPipe reports the ankles at a median visibility of **0.04** (`Standing_2`, `Sit_3`)
and the knees at 0.13–0.22 — i.e. it is openly saying *"I cannot see these joints"* and
inventing coordinates for them.

> Across **all nine** indoor ADL clips there is **not one single frame** where both
> knees and both ankles reach 0.5 visibility.

That is why a standing person was being read as "Lying": `body_height` and
`vertical_span` were computed from guessed ankle positions. The pipeline now ignores
untrusted joints, but ignoring them means falling back to torso-only reasoning, which is
strictly weaker. `sanity_check_clips.md` already specifies *"whole body (head to feet)
visible"* — the existing clips simply do not meet it.

**Before recording anything:** move the camera back / raise it / angle it down until you
can see **head to feet** with the person standing at 2–4 m, and confirm it. Run:

```
python realtime_fall_detection.py --input 1
```

and look at the skeleton overlay — **yellow joints are trusted, dim-red are guesses.**
Adjust until the knees and ankles render yellow while you stand normally. Only then
start recording.

Record **both** framings for the priority-A clips if you can spare the time: the good
framing shows what the system can do, the waist-crop framing documents the degraded
case you may still face in a real room. Suffix them `_full` and `_crop`.

---

## Priority A — negatives (highest value by far)

The current set has **12 fall clips but only 9 ADL clips**, while false alarms are the
actual pain point. Worse, the two motions reported as misfiring live have **zero
representation anywhere** — not in the test set, not in training. These clips are the
most valuable thing you can record.

| # | Clip name | What to do | Why it matters |
|---|---|---|---|
| 1 | `Bend_pickup_1` | Stand, bend at the waist, pick something off the floor, stand back up | **Reported misfiring live.** Trunk pitches past 45° while the legs stay vertical — the classic bend-vs-fall confusion in the literature |
| 2 | `Bend_pickup_2` | Same, but squat down with a straight back instead of hinging | Different trunk/leg geometry for the same intent |
| 3 | `Bend_sideways` | Bend sideways to pick something up beside you | Off-axis trunk rotation |
| 4 | `Bend_tie_shoe` | Crouch down, stay ~5 s (tying a shoe), stand up | Sustained low posture — probes the sustained-lying counter |
| 5 | `Lie_down_bed_slow` | Sit on the bed, then lie down deliberately | **Reported misfiring live** |
| 6 | `Lie_down_bed_fast` | Flop onto the bed quickly | The hard case — fast *and* ends horizontal |
| 7 | `Lie_down_sofa` | Lie down along a sofa | Horizontal but at seat height, not floor height |
| 8 | `Lie_down_floor_deliberate` | Lower yourself to the floor **slowly and in control**, rest, get up | **The hardest negative we have.** Geometrically near-identical to a fall; the only difference is speed and control. Tells us exactly where the boundary sits |
| 9 | `Sit_sofa_fast` | Drop quickly onto a sofa | Only one fast-sit clip exists today |
| 10 | `Sit_floor_crosslegged` | Sit down on the floor cross-legged, stay, get up | Ends low but is not a fall |
| 11 | `Walk_out_and_back` | Walk out of frame, pause, walk back in | Tracking loss and re-acquisition — the "Unknown" flapping path |
| 12 | `Kneel_and_stand` | Kneel on both knees, pause, stand | Low posture, legs folded |

## Priority B — the one real detection gap

`Backward_fall` is the **only** fall the system misses, and the reason is measurable:
it produces zero Lying frames, and its peak velocity (1.68) and angular velocity (146)
both sit *below* the ADL maxima. One example is not enough to tell whether that is a
property of backward falls generally or just that clip.

| # | Clip name | What to do |
|---|---|---|
| 13 | `Backward_fall_2` | Fall straight backwards onto the mat |
| 14 | `Backward_fall_3` | Fall backwards, ending with legs bent/tucked |
| 15 | `Backward_fall_sideways` | Fall backwards and slightly to one side |
| 16 | `Fall_from_chair_2` | Slump sideways off a chair (only one chair-fall exists, and it is the weakest detection at 38 Lying frames vs the 32 threshold) |

## Priority C — elderly realism and robustness

The Scope Document targets elderly users, but every clip so far is a fit adult. Do these
by **slowing the movement down**, never by having an older person actually fall.

| # | Clip name | What to do |
|---|---|---|
| 17 | `Slow_crumple_1` | Sink to the floor slowly, knees first, as a faint would look |
| 18 | `Slow_crumple_2` | Same, but catching yourself on furniture on the way down |
| 19 | `Fall_partial_occlusion` | Fall so you end up partly behind a bed/sofa (the "foot behind the bed" case) |
| 20 | `Fall_then_recover` | Fall, lie ~5 s, then get yourself back up |
| 21 | `Fall_low_light` | A normal fall with the room lights dimmed |
| 22 | `Two_people_one_falls` | Two people in frame, one falls — the pipeline currently only ever reads `pose_landmarks[0]` |

Clip 22 is worth doing even though we will not fix multi-person now; it documents a
known limitation for the thesis.

---

## Ground-truth files (please do this — clips are unusable to me without them)

One CSV per clip, named `<clip_name>_gt.csv`, in the same folder. Use this exact format
(it matches `Testing/Sanawar Testing 7-25-26/`, which parses cleanly):

**A clip containing a fall:**
```
start_time,end_time,state,label
0.00,1.40,Standing,Standing
1.40,2.60,Transition State,Falling (Backward)
2.60,6.20,Fall,Fallen / Lying
```

**A clip with no fall (all Priority-A clips):**
```
start_time,end_time,state,label
0.00,3.10,Standing,Standing
3.10,5.40,Sitting,Lying down on bed
5.40,9.00,Sitting,Lying on bed
```

Rules that make the timings usable:
- Times are **seconds with decimals**, measured from the start of that clip.
- `state` must be one of `Standing`, `Sitting`, `Transition State`, `Fall`. Only `Fall`
  counts as ground-truth "on the floor"; scoring credit also extends back through the
  preceding `Transition State`, so mark the transition where the fall *begins*.
- For an ADL clip **never use the `Fall` state**, even if the person ends up horizontal
  — that is the whole point of those clips.
- Rough timings (±0.2 s) are fine. Don't agonise; consistency matters more than precision.

---

## Practical notes

- **10–15 s per clip**, person already in frame at the start, one action per clip.
- Keep resolution/FPS **identical across every clip** (720p @ 30 FPS is fine).
- Same room and camera position as your demo, since that is the deployment condition.
- **Priority A alone (~12 clips, ~20 minutes) is the single highest-value thing** — it
  roughly doubles the negative set and covers both live failures. Do that first even if
  B and C have to wait.
- Drop everything into a new folder, e.g. `Testing/<Name> Testing <date>/`, clips and
  `_gt.csv` files side by side. That is where the evaluation harness looks.

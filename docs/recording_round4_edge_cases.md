# S.A.G.E. — Recording Round 4: Lie-Down & Occlusion Edge Cases

15 clips to stress-test the shipped 2x model on two specific things:

1. **Deliberate lying down** — `LyingdownSlowly` is the one round-2 clip that
   still false-alarms on the current model. One clip isn't enough to know if
   that's a systematic weakness or just that one recording (the same lesson
   round-3 taught us about `Backward_fall`, which turned out to be a single
   bad clip, not a blind spot). These 7 clips test the boundary properly.
2. **Occlusion / disappearing** — the "foot behind the bed" and "walked out
   of frame" failure modes that were flagged as risks early on but never
   directly tested with dedicated clips.

**None of these are falls.** Every clip here is a normal activity that should
never trigger an alarm — that's the whole point. Ground truth must never use
the word "fall" in any label (see the format section — the scorer keys off
that word to decide what's a fall clip).

**This set stays held out.** Same rule as round-2/round-3: once you send
these, they become the measurement, not training data. Don't reuse this
footage later without deciding that trade-off deliberately.

---

## Setup — identical to round-2/round-3, don't vary this

- Same room, same camera position/height as your last two batches (the one
  where the skeleton overlay showed full head-to-feet, joints reading
  yellow/trusted). Changing the camera here would confound the comparison —
  we want to isolate "does the new model handle this behavior," not "does a
  new room break it."
- 10–15 s per clip, 720p+ @ ~25–30 fps preferred (round-3's 56 fps worked
  fine, but matching your usual rate keeps this simple).
- One behavior per clip.

---

## Part A — Deliberate lying down (7 clips)

The point of this group is to vary *how* and *where* the lie-down happens,
so we find out whether the false alarm follows the motion or the specific
clip.

| # | Clip name | What to do |
|---|---|---|
| 1 | `LieDown_floor_slow_v2` | Stand, lower yourself to the floor slowly and deliberately, rest, get up. A repeat of the original failing clip — same behavior, new take. |
| 2 | `LieDown_bed_slow` | Sit on the edge of the bed, then lie back slowly until flat. |
| 3 | `LieDown_sofa_slow` | Lie down along a sofa, slowly, feet up. |
| 4 | `LieDown_via_sitting` | Stand → sit on the floor → recline backwards slowly until lying flat. Three stages in one clip. |
| 5 | `LieDown_medium_pace` | Same as #1 but at a normal, unhurried pace — not slow-motion slow, not a flop. Tests whether the false alarm is specific to *very* slow descent or holds at ordinary speed too. |
| 6 | `LieDown_long_hold` | Lie down slowly, then stay completely still for the full remaining clip length (hold as long as you comfortably can, 10s+ after lying down). Tests whether duration on the ground matters. |
| 7 | `LieDown_then_up_quickly` | Lie down slowly, pause 3–5 s, then get back up at normal speed. Tests the recovery half, not just the descent. |

---

## Part B — Occlusion & disappearing (8 clips)

| # | Clip name | What to do |
|---|---|---|
| 8 | `Occlude_walk_out_pause_in` | Walk fully out of frame, pause 2–3 s out of frame, walk back in. (Same idea as your earlier `Moving_in_out_frame` clip — a repeat, different take, since this is a group worth having more than one example of too.) |
| 9 | `Occlude_behind_furniture` | Walk behind something tall enough to fully hide your body for a couple of seconds (wardrobe, door, pillar), then re-emerge. |
| 10 | `Occlude_seated_behind_desk` | Sit down behind a desk/table so your lower body is hidden but torso/head stay visible. |
| 11 | `Occlude_lying_behind_bed` | Lie down so you end up **partly** behind a bed/sofa — only the upper half of your body stays visible. The specific "foot behind the bed" scenario. |
| 12 | `Occlude_frame_edge` | Move to the very edge of the frame so you're half in, half out, and hold there a few seconds before stepping back in. |
| 13 | `Occlude_in_out_repeated` | Walk in and out of frame 3–4 times in one clip, varying pace each time. |
| 14 | `Occlude_low_light` | A normal walk + sit + stand sequence with the room lights dimmed, so MediaPipe's keypoint confidence genuinely drops. |
| 15 | `Occlude_crouch_behind_furniture` | Crouch down behind a low piece of furniture (coffee table, low shelf) so you disappear while transitioning, then stand back up. Tests occlusion *during* a posture change, not just while static. |

---

## Ground truth — same format as before, one `_GT.csv` per clip

```
start_time,end_time,state,label
0.00,1.20,Standing,Standing
1.20,4.00,Transition State,Lying down slowly
4.00,9.00,Lying,Lying down on floor
9.00,10.50,Transition State,Getting up
```

For the occlusion clips, use the `Not in frame` state for any stretch where
you're fully out of the picture (matches the format already used for
`Moving_in_out_frame`):

```
start_time,end_time,state,label
0.00,2.00,Standing,Standing
2.00,3.50,Walking,Moving out of frame
3.50,5.80,Not in frame,Not in frame
5.80,7.00,Walking,Moving back into frame
7.00,8.50,Standing,Standing
```

Rules, same as every prior round:
- Never use the word "fall" anywhere in a `label` for these clips.
- Times are seconds with decimals, from the start of that clip. Rough
  timing (±0.2s) is fine.
- `state` must be one of: `Standing`, `Sitting`, `Lying`, `Transition State`,
  `Walking`, `Not in frame`.
- One action/behavior per clip — don't chain a lie-down and an occlusion in
  the same clip, so a failure is easy to attribute to one specific thing.

---

## Where this goes

New folder: `Testing/<Your Name> Testing <date>/`, clips and `_GT.csv` files
side by side — same convention as every previous round. Once it's there,
send the word and I'll extract, score the 2x model against all 15 cold, and
report per-clip results the same way we did for round-2 and round-3.

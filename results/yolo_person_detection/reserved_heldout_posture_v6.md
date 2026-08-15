# v6 vs v5 vs v3 on held-out hand-drawn labels: ship v6 — SEE CAVEAT

> ## ⚠ DO NOT DEPLOY v6 OVER v5 ON THE STRENGTH OF THIS FILE ALONE
>
> **Added 16 Aug 2026, after four new dim-lighting clips were benchmarked.**
> Everything measured below still holds. The *conclusion* drawn from it was too
> broad.
>
> On new footage in `yolo_testing/held_out/`, **v6 detects nobody at all in
> `laying_dim.MOV` — 0 of 620 frames — where v5 detects the person in 69.5%.**
> Not a threshold effect: v6 finds no person there even at `conf 0.10`. v6 also
> trails v5 on the other lying clip, 80.8% vs 90.7%.
>
> Both clips are the same failure signature this file says v6 improved on:
> a person lying on furniture, dark clothing, dim room, foreground occlusion.
>
> See [Superseding evidence](#superseding-evidence-v6-regresses-on-new-dim-footage)
> below before acting on the recommendation.

Measured 16 Aug 2026 against **hand-drawn** boxes on footage held out of every
training run. `conf 0.4`, `imgsz 640`. **388 person boxes across 11 clips in 3
rooms**, from 569 labelled frames — the same eval set as
[`reserved_heldout_posture_v5.md`](reserved_heldout_posture_v5.md), so every
number here is directly comparable to that file.

This is the run [`docs/TRAINING_v6_CONTEXT.md`](../../docs/TRAINING_v6_CONTEXT.md)
specified as the gate, and it is the first run to add **new footage of the
missing conditions** rather than new labels on old footage.

**Ship v6.** It is better than v5 on recall, on localisation and on
false positives, and it regresses nothing. But the headline fall number is
**one clip**, and the clip round 5 was recorded for did not move.

---

## Headline

| IoU 0.5 | recall | precision | FP |
|---|---|---|---|
| v3 | 179/388 · 0.461 | 0.937 | 12 |
| v5 | 181/388 · 0.466 | 0.879 | 25 |
| **v6** | **224/388 · 0.577** | **0.966** | **8** |

| IoU 0.3 | recall | precision | FP |
|---|---|---|---|
| v3 | 182/388 · 0.469 | 0.953 | 9 |
| v5 | 204/388 · 0.526 | **0.990** | **2** |
| **v6** | **227/388 · 0.585** | 0.978 | 5 |

**v6 at the strict threshold beats v5 at the lenient one.**

---

## The most robust finding: v5's loose boxes are gone

This is the part that does **not** rest on a single clip.

| model | IoU 0.5 | IoU 0.3 | boxes gained by relaxing |
|---|---|---|---|
| v3 | 0.461 | 0.469 | +3 |
| v5 | 0.466 | 0.526 | **+23** |
| **v6** | **0.577** | **0.585** | **+3** |

`reserved_heldout_posture_v5.md` established that v5's apparent gain existed
only at IoU 0.3, because it placed boxes **loosely** — overlapping the person
but under 0.5 IoU, most plausibly enclosing the person together with the
furniture they were lying on. Its false-positive count fell 25 → 2 when the
threshold moved, and every one of those 22 `Bedroom_Fall` "false positives" was
a real detection scored as both a miss and an error.

v6 does not have that property. It scores the same at either threshold, exactly
like v3 — but with 45 more boxes than v3 and 23 more than v5.

**So v6 is v3's localisation with better recall than v5.** That threshold
sensitivity was the central caveat of the v5 result, and it is resolved.

It also removes the carry-forward v5 shipped with: *"the drawn boxes will look
wrong on fallen-person frames — roughly double size, enclosing the furniture.
Cosmetic today, conspicuous in a live demo."* That is fixed.

---

## Per clip

Rate | false positives, IoU 0.3:

| clip | boxes | v3 | v5 | v6 |
|---|---|---|---|---|
| `Bedroom_Walk` | 14 | 1.00 \| 1 | 1.00 \| 0 | 1.00 \| 0 |
| `TV_Lounge_1_Walk` | 1 | 1.00 \| 0 | 1.00 \| 0 | 1.00 \| 0 |
| `TV_Lounge_1_Sit` | 16 | 0.88 \| 4 | 1.00 \| 0 | 1.00 \| 0 |
| `people` | 18 | 1.00 \| 0 | 1.00 \| 1 | 1.00 \| 1 |
| `Bedroom_Sit` | 24 | 0.88 \| 0 | 0.88 \| 0 | **1.00 \| 0** |
| `people_(2)` | 32 | 0.94 \| 0 | **0.97 \| 0** | 0.94 \| 0 |
| | | | | |
| **`Bedroom_Fall`** | 62 | 0.39 \| 1 | 0.68 \| 0 | **0.95 \| 0** |
| `TV_Lounge_2_Fall` | 35 | 0.46 \| 0 | 0.43 \| 0 | 0.46 \| 0 |
| `TV_Lounge_2_Fall2` | 41 | 0.39 \| 0 | 0.41 \| 0 | 0.41 \| 0 |
| `TV_Lounge_1_Fall2` | 48 | 0.27 \| 1 | 0.25 \| 1 | **0.31 \| 1** |
| **`TV_Lounge_1_Fall`** | 97 | 0.15 \| 1 | 0.18 \| 0 | **0.18 \| 3** |

By activity, IoU 0.3:

| group | boxes | v3 | v5 | v6 |
|---|---|---|---|---|
| walk / sit / upright | 105 | 0.933 | 0.962 | **0.981** |
| **fall** | 283 | 0.297 | 0.364 | **0.438** |
| all | 388 | 0.469 | 0.526 | **0.585** |

Nothing regressed. The only per-clip loss anywhere is `people_(2)`, 0.97 → 0.94
— one box.

---

## The fall gain is one clip

**Remove `Bedroom_Fall` and the fall column is flat.**

| fall clips excluding `Bedroom_Fall` | boxes | v3 | v5 | v6 |
|---|---|---|---|---|
| IoU 0.3 | 221 | 0.271 | 0.276 | **0.294** |
| IoU 0.5 | 221 | 0.271 | 0.271 | **0.290** |

Five boxes out of 221. `Bedroom_Fall` alone accounts for 35 of v6's 45-box gain
over v3.

**`TV_Lounge_1_Fall` — the clip named in advance as the number to watch — went
0.18 → 0.18 at IoU 0.3.** Identical to v5, on 97 boxes. It is still the hardest
clip in the set, and it is still unsolved.

---

## What round 5 actually ruled out

The obvious reading of `Bedroom_Fall` 0.39 → 0.95 is that the model learned that
specific bedroom, because round-5's `Bedroom_Falll.mov` was shot there. **The
frames confirm it is the same room** — same AC unit, curtains, wallpaper,
headboard, ceiling fan and wardrobe, at a different angle in dimmer light.

But that explanation fails its own control. **Round 5 filmed the TV lounge too,
and `TV_Lounge_Fallll.mov` is the same room as `TV_Lounge_1_Fall`** — same sofa
set, same V-pedestal coffee table, same plant, shot dark and through a doorway.

| room | round-5 training footage | eval clip | v3 → v6 @ IoU 0.3 |
|---|---|---|---|
| Bedroom | same room | `Bedroom_Fall` | 0.39 → **0.95** |
| TV Lounge 1 | same room | `TV_Lounge_1_Fall` | 0.15 → **0.18** |

Same intervention, same-room in both cases, opposite outcomes. If proximity to
the training room were what produced the bedroom gain, the lounge would have
gained too.

**So round 5 rules out the most obvious remaining hypothesis: that
`TV_Lounge_1_Fall` fails for want of training examples from that room under
those conditions.** It now has them, hand-labelled, and it did not move.

This compounds what v5 established — that clip already had 100% MediaPipe
coverage, so it was never short of labels either. Two independent explanations
are now eliminated:

1. **Missing labels** (v5 — ruled out: coverage was already complete)
2. **Missing footage of the conditions** (v6 — ruled out: it now has 56
   hand-labelled frames of that room, dark and occluded)

That is a real result from round 5, and it is not the one the round was
expecting. **Whatever defeats `TV_Lounge_1_Fall` is a property of the clip
itself, not of the training set.** The next investigation should be diagnostic —
look at what the model does on those 80 missed frames — rather than another
recording round. Recording round 6 against the same hypothesis would be the
third run to test an explanation the evidence has already closed off.

---

## Empty-room false positives

Every frame of all 11 held-out empty clips, `--stride 1`, 7,200 frames per
model:

| model | FP frames | FP rate |
|---|---|---|
| v3 | 28 | 0.39% |
| v5 | **0** | **0.00%** |
| **v6** | **0** | **0.00%** |

v6 holds v5's perfect record. It hallucinates no people in empty rooms, across
seven thousand frames of five rooms.

Furniture detection in those same rooms is unchanged in character (couch 4,123,
chair 2,331, bed 1,275, tv 829, dining table 570). These are not errors — the
furniture is real — but note v6 reports **fewer** couches than v5 (4,123 vs
5,804) and no refrigerators. Not scored here; flagged only because the object
classes have never been measured against hand-drawn furniture labels in these
rooms.

---

## Superseding evidence: v6 regresses on new dim footage

Four clips recorded after this evaluation, benchmarked 16 Aug 2026 at
`conf 0.4`, `imgsz 640`, in `yolo_testing/held_out/`. **Coverage — the fraction
of frames the model fires at all. There are no labels yet, so this is not
recall**, and a confident detection on the wrong thing counts the same as a
correct one.

| clip | frames | v6 | v5 | stock |
|---|---|---|---|---|
| `IMG_9435` — lying, floor mattress | 1,208 | 80.8% | **90.7%** | 26.8% |
| `IMG_9439` — sitting, sofa | 565 | 100% | 100% | 100% |
| `laying_dim` — lying, sofa, occluded | 620 | **0.0%** | **69.5%** | 83.9% |
| `sitting_dim` — sitting, chair | 923 | 100% | 100% | 100% |

The two sitting clips saturate at 100% for all three models and discriminate
nothing. **The two lying clips are the informative ones, and v5 beats v6 on
both.**

`laying_dim` was inspected frame by frame rather than taken on trust:

- v6 returns **no person box at any confidence down to 0.10**. This is not a
  borderline miss.
- v5 returns a correct, tight box on the subject at ~0.45.
- Stock's 83.9% is **inflated**: a large share of it is a near-full-frame box on
  the blurred foreground object, not the person. Its true rate on the subject is
  much lower. Ranking on this clip is v5 correct, stock partly spurious, v6
  blind.

### The likely mechanism, and why this file missed it

v6 bought its precision gain (0.879 → 0.966 at IoU 0.5) by becoming **more
conservative**, and on genuinely low-contrast lying people that conservatism
turns into total misses rather than loose boxes.

The held-out set could not expose this. There, v5's extra firings were *loose*
boxes, penalised as false positives at IoU 0.5 — so v6's unwillingness to fire
scored as a pure win. Coverage on unlabelled footage asks a different question,
"does it fire at all", and v6 answers worse.

**Both measurements are correct. They are measuring different things**, and
shipping decisions need the second one too.

---

## Next steps

In order. Nothing here should be skipped on the basis of the tables above.

1. **Hand-label `laying_dim` and `IMG_9435`** — the two discriminating clips.
   Skip `IMG_9439` and `sitting_dim`: saturated at 100% for every model, so
   labels there buy nothing. Use `sample_heldout_frames.py`; the rotations are
   registered and eye-verified (all four upright).

2. **Run a v5-vs-v6 diagnostic on the same frames, BEFORE any retraining.**
   `laying_dim` is a better handle on this failure than anything previously
   available: it is the exact signature that has defeated three model versions
   on `TV_Lounge_1_Fall`, but with a model that *succeeds* on it. Comparing what
   v5 fires on against what v6 does not can identify what v6 lost. No amount of
   new footage answers that.

3. **Only then decide on a round 7.** Note the ordering constraint: **training
   on `laying_dim` destroys its value as the control.** Once v6 has seen it, it
   can no longer answer "what does v6 lack that v5 has". Spend it as evidence
   first.

4. **Re-run this gate plus a coverage benchmark for any future checkpoint.**
   The lesson is not "v6 is bad" — it is that IoU-scored recall on hand-drawn
   boxes and coverage on unlabelled hard footage disagree, and a checkpoint can
   win the first while losing the second.

---

## Recommendation

**Ship v6 — but not over v5 for deployment, pending step 2 above.**

The tables in this file are unchanged and still support everything they claim
about the held-out set. What changed is scope: they were read as "v6 is better
at detecting fallen people", and the new clips show that does not generalise to
the hardest low-contrast cases, where v6 is materially worse than v5.

If a single checkpoint must be chosen for a live demo today, **choose v5**: an
over-large box on a detected person degrades gracefully, whereas v6's failure
mode on `laying_dim` is silence, and this is a fall-detection system.

The original recommendation, for the record:

| axis | v3 | v5 | v6 |
|---|---|---|---|
| fall detection rate (IoU 0.3) | 0.297 | 0.364 | **0.438** |
| fall detection rate (IoU 0.5) | 0.290 | 0.283 | **0.431** |
| walk/sit detection rate | 0.933 | 0.962 | **0.981** |
| overall recall (IoU 0.5) | 0.461 | 0.466 | **0.577** |
| overall precision (IoU 0.5) | 0.937 | 0.879 | **0.966** |
| threshold sensitivity | +3 boxes | +23 boxes | **+3 boxes** |
| empty-room false positives | 0.39% | 0.00% | **0.00%** |

Better than v5 on every axis except IoU-0.3 precision (0.978 vs 0.990, three
boxes), and better than both on the axis v5 was weakest: box placement.

Honest framing for anyone quoting this:

- **"v6 lifts overall recall 0.526 → 0.585 and fixes v5's loose boxes"** is
  supported by all 388 boxes.
- **"v6 improves fall detection 0.364 → 0.438"** is true but is carried by one
  clip; outside `Bedroom_Fall` the fall column moved 0.276 → 0.294.
- **"Round 5 solved the dark/occluded fall case"** is not supported. The clip it
  was recorded for did not move.
- **"v6 is the better detector of fallen people"** is **contradicted** by the
  new dim clips above. It is the better detector *as scored by IoU against
  hand-drawn boxes on this eval set*. On the hardest unlabelled footage it
  misses people v5 finds.

---

## Method

- `src/detection/score_heldout_objects.py --classes person --imgsz 640
  --conf 0.4 --per_clip`, at `--iou 0.5` and `--iou 0.3`, all three models
  scored in one invocation on identical frames.
- Empty rooms: `score_empty_false_positives.py --imgsz 640 --conf 0.4
  --stride 1`.
- Denominator is person boxes only (`tp + fn`); label files also carry furniture
  boxes.
- Room identity checked by extracting frame 30 from each clip with the verified
  rotation applied and comparing by eye.

### Caveats

- **388 boxes, 11 clips, 3 rooms, two recording sessions by the same people.**
  Single-box clips like `TV_Lounge_1_Walk` mean nothing alone.
- The eval set is 73% fall boxes by composition (fall clips sampled at stride
  10, walk/sit at stride 30). The ALL row is not comparable to the 179-box
  version of the v5 file.
- Frames 0.4 s apart remain correlated.
- **`Bedroom_Fall` and `TV_Lounge_1_Fall` are the same rooms as round-5 training
  footage.** Still non-circular — different clips, never trained on — but this
  is "same room, different take", which is a weaker generalisation claim than
  "unseen room". `empty_ground_mahaRoom` remains the only genuinely unseen room.
- IoU 0.3 is reported alongside 0.5, not instead of it. Both were specified
  before the run. v6 happens to be insensitive to the choice, which is itself
  the finding.
- Latency not re-measured. CPU-only machine.
- **The dim-clip figures are coverage, not recall**, on four clips with no
  ground truth, two of which discriminate nothing. They are enough to block a
  deployment decision and not enough to rank the models. That is what step 1 of
  Next Steps is for.

---

## Related

- [`reserved_heldout_posture_v5.md`](reserved_heldout_posture_v5.md) — v5 vs v3, the loose-box diagnosis, and the failure profile that motivated round 5
- [`reserved_heldout_posture.md`](reserved_heldout_posture.md) — the v3 baseline and the four measurement faults corrected along the way
- [`docs/TRAINING_v6_CONTEXT.md`](../../docs/TRAINING_v6_CONTEXT.md) — the runbook that set this gate
- [`docs/NEXT_round5_to_v6.md`](../../docs/NEXT_round5_to_v6.md) — the handoff round 5 came from

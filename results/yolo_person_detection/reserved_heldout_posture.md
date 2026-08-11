# Held-out person detection by POSTURE — v3 vs v4

Measured 11 Aug 2026 against **hand-drawn** boxes on footage held out of every
training run. Settings identical for both models: `conf 0.4`, `imgsz 320`,
IoU 0.5 for a match.

> **Read this before citing the 56.1% figure in
> [`reserved_people_v3.md`](reserved_people_v3.md).** See "Reconciling with
> 56.1%" below. Short version: that number is measured over whole clips that
> *contain* a fall, most of which is the person still upright. Scored on the
> frames where the person is actually horizontal, detection is **0%**.

---

## Headline

| | v3 | v4 |
|---|---|---|
| Upright recall (standing / sitting) | **0.905** (67/74) | 0.757 (56/74) |
| **Lying recall (horizontal)** | **0.000** (0/65) | **0.000** (0/65) |
| Empty-room false-positive rate | 2.70% (172/6366) | **0.39%** (25/6366) |

**Neither model detects a fallen person. 0 out of 65, across three rooms.**

This is not degradation, it is absence: the misses are total non-detections,
not localisation errors. Scored per box, the best-IoU distribution is perfectly
bimodal — the model either finds the person and localises them well (IoU ≥ 0.75)
or emits no person box at all. Zero boxes landed in the 0.30–0.49 near-miss
band, so this is not an artefact of the IoU threshold or of box tightness.

For a fall-detection product this is the defining failure mode: the system
tracks a person reliably right up to the moment they fall, then loses them
completely.

---

## v3 per clip

| clip | room | upright | lying |
|---|---|---|---|
| Bedroom_Walk | Bedroom | 14/14 | — |
| TV_Lounge_1_Sit | TV Lounge 1 | 14/14 | — |
| people | Fatima's room | 18/18 | — |
| TV_Lounge_1_Walk | TV Lounge 1 | 1/1 | — |
| Bedroom_Sit | Bedroom | 17/23 | 0/1 |
| TV_Lounge_1_Fall | TV Lounge 1 | 3/4 | **0/12** |
| Bedroom_Fall | Bedroom | — | **0/20** |
| people_(2) | Fatima's room | — | **0/32** |
| **TOTAL** | 3 rooms | **67/74** | **0/65** |

v3 is genuinely good at what it was trained for — 0.905 upright recall on rooms
it has never seen, with three clips perfect. The failure is specific, not general.

## v4 per clip

Identical frames, identical settings.

| clip | upright | lying |
|---|---|---|
| Bedroom_Walk | 14/14 | — |
| TV_Lounge_1_Sit | 14/14 | — |
| TV_Lounge_1_Fall | 4/4 | 0/12 |
| people | 17/18 | — |
| TV_Lounge_1_Walk | 1/1 | — |
| **Bedroom_Sit** | **6/23** | 0/1 |
| Bedroom_Fall | — | 0/20 |
| people_(2) | — | 0/32 |
| **TOTAL** | **56/74** | **0/65** |

v4's upright loss is concentrated almost entirely in `Bedroom_Sit`
(17/23 → 6/23). Lying is unchanged at zero.

---

## False positives — every frame of 9 held-out empty rooms

Empty rooms need no labels: the room is empty, so that IS the ground truth and
every `person` detection is an error by definition. Run over **every** frame
(`--stride 1`), not a sampled subset — see the note on sampling below.

| clip | frames | v3 | v4 |
|---|---|---|---|
| **living room.mov** | 809 | **172 (21.26%)** | **25 (3.09%)** |
| Bedroom_Empty | 854 | 0 | 0 |
| TV_Lounge_1_Empty | 826 | 0 | 0 |
| TV_Lounge_2_Empty | 497 | 0 | 0 |
| beds | 861 | 0 | 0 |
| lonuge | 595 | 0 | 0 |
| empty_ground_mahaRoom | 1012 | 0 | 0 |
| WhatsApp 5.49 / 7.44 | 912 | 0 | 0 |
| **ALL** | **6366** | **172 (2.70%)** | **25 (0.39%)** |

Both models fail on **exactly one room**. `living room.mov` contains an armchair
with a cream cushion which v3 boxes as a person at up to 0.78 confidence. Eight
other held-out rooms, including all three new 4K ones, are clean at 0.00%.

A narrow, reproducible confusion is good news — it is fixable with targeted
data, unlike general trigger-happiness.

---

## Reconciling with 56.1%

[`reserved_people_v3.md`](reserved_people_v3.md) reports **56.1% on "falling /
lying clips"**. That appears to contradict the 0/65 above. It does not — the two
measure different things.

| | that report | this report |
|---|---|---|
| unit | one frame | one hand-drawn box |
| population | every frame of a clip that *contains* a fall | only frames where the person is actually horizontal |
| ground truth | none — "did the model emit any person box?" | hand-drawn boxes |

A fall clip is mostly **not** a fall. The subject walks in, stands, sits, and is
upright for the majority of the runtime; the horizontal portion is a minority of
frames at the end. v3 detects the upright majority almost perfectly, and that is
what carries the 56.1%.

**So 56.1% is largely a measurement of the upright footage inside fall clips.
On the fall itself, detection is 0%.**

> **Do not cite 56.1% as evidence that fall detection works.** It is a valid
> number for what it measures — overall person-detection rate across
> fall-containing clips — but it says nothing about whether a fallen person is
> detected. Measured directly, that is 0 of 65 across three rooms and both models.

The same caution applies to the "Held-out clips only" rows in
`reserved_people_v3.md` (20.1%) and `reserved_people_v4.md` (68.5%): those two
runs held out **different clips** (`TV_Lounge_2_Sit` vs `TV_Lounge_1_Walk`), so
20.1% → 68.5% is a change of test set, not an improvement.

---

## Which model should ship

**v3.** v4 buys a 7× false-alarm reduction (2.70% → 0.39%) by giving up 15% of
real upright detections (0.905 → 0.757), and fixes nothing on lying. For a fall
detector a missed person costs more than a false alarm, so v4's headline gain is
on the metric that matters less.

Neither model addresses the fallen-person case.

---

## Why this is a data problem, not a modelling one

1. **Three training rooms.** All own-footage training data comes from 3
   recording sessions. Furniture and viewpoint diversity are close to nil.
2. **The person labels come from MediaPipe**, which is itself weakest on fallen
   and occluded poses — so the training set barely contains correctly-labelled
   fallen people. The model cannot learn what it was never shown.
3. `generate_bbox_dataset.py` exists specifically to fix fallen-person
   detection — its docstring names that as the weakness it targets. It works on
   the training rooms and does not transfer.

The fix is footage of fallen people in rooms the model has not seen, with boxes
a human drew.

---

## Method

- **Recall**: `src/detection/score_heldout_objects.py --classes person`.
  `--classes` filters predictions *and* ground truth, so a person-only labelling
  pass does not report unlabelled furniture as false positives.
- **False positives**: `src/detection/score_empty_false_positives.py`, `--stride 1`.
- Posture is classified from the hand-drawn box aspect ratio: `w/h > 1`
  (wide) = horizontal. Confounded with size — lying boxes average 4.2% of frame
  area versus 12.6% upright — so some of the miss rate is small-object detection
  rather than posture as such. The two cannot be fully separated with this
  footage. What survives the caveat: whatever the mechanism, detection of fallen
  people in an unseen room is zero.
- Labels: 50 frames drawn by Fatima (`people`, `people_(2)`), the remainder from
  the team's `Bedroom_*` / `TV_Lounge_1_*` set already in the repo.

### Two settings mistakes worth not repeating

Both were made and corrected while producing this report:

- **imgsz.** Ultralytics' `predict()` defaults to 640; the merged series is
  trained and gated at **320**. Scoring v3 at 640 reported its precision as
  0.391 when the correct figure is 0.581. `--imgsz` is now a required
  consideration in both scripts.
- **conf.** v3 was first scanned at `conf 0.25` and v4 at `conf 0.4`, which made
  v4 look like it had almost eliminated the armchair false positive. At matched
  settings the real comparison is 21.26% → 3.09%. The earlier **49.32%** figure
  for v3 came from that mismatched run and should not be quoted.

Any two models must be compared at the same `--conf` **and** `--imgsz`, each at
the resolution it was trained for.

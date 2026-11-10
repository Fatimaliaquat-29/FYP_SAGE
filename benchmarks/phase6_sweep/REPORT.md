# Phase 6 report: learning rate, schedule, batch size, and re-adding the 4 clips

**Date:** 2026-11-08 (overnight, started 03:12). **All held-out scores are PROVISIONAL**: the held-out labels follow
no consistent written convention yet (docs/LABELLING_SPEC.md is still a v0.1 draft).

**Status (final, 15:30):** all runs are done and scored: the four planned runs (LR2, D, COS, B8) plus **DCOS**
(D's data + cosine schedule, added this morning after seeing results; section 6). Pipeline ended 15:24. The supervisor scores each run and redraws every image automatically; `RESULTS.md` always
has the latest numbers.

Every run changes **one thing** compared with C (the phase-5 model; not retrained). Same recipe, seed, val set and
scoring harness as phase 5. The A control reproduced its recorded numbers exactly (58/93, 107/249, 50/226), and C's
numbers are identical to phase 5, so all runs are compared on equal terms.

| run | change vs C | status |
|---|---|---|
| **LR2** | learning rate x2 (0.000588 -> 0.001176) | done, 224 min |
| **D** | C's data + the 4 problem clips re-added after filtering | done, 259 min |
| **COS** | linear -> cosine learning-rate schedule | done, 233 min |
| **B8** | batch 16 -> 8 | done, 245 min |
| **DCOS** | D's data + cosine schedule (two changes; added after seeing results) | done, 207 min |

The rule (`DECISION_RULE.md`, written before any result): a run is "clearly better than C" only if it is ahead with
McNemar p < 0.05 on **both** round6_heldout and reserved388_partial (people, IoU 0.5). The bed question for D was
pre-registered the same way: "fixed" only if D is ahead of C on per-box bed hits with p < 0.05.

---

## 1. Short answer

- **Best model of the phase: DCOS** (the 4 clips re-added + cosine schedule). By our pre-agreed rule it is still
  not "clearly better" than C, because round6_heldout is close (53 vs 51, p = 0.63). But:
  - **People:** 148/249 on reserved388_partial vs C's 104 (45 vs 1 boxes, p = 1e-12), and the most people of any
    model on heldout_objects (60/93, 6 vs 0, p = 0.03) and round6_heldout (53/226, tied with D).
  - **Person lying on the bed:** 59/62 on With_people_Bedroom_Fall (C 21). It draws **one tight box** per person
    with **no pillow boxes** (`lying_on_bed_sheet.jpg`). That fixes COS's false positives: 4 false person boxes on
    reserved388_partial, vs 24 for COS and 12 for C.
  - **0 false alarms** on 4,101 empty-room frames (D had 2).
  - **Box fit:** 0 very loose boxes and the most people matched (201), though many boxes are slightly tight.
  - **Beds:** 44/128 on reserved388_partial (C 1/128). But most of that is one clip (Bedroom_Fall), and on
    Bedroom_Sit / heldout_objects it is worse than D (3/86 vs 16/86, p = 0.001). So beds are only partly fixed.
- **The single settings, each against C:**
  - **Cosine schedule (COS):** found the lying person (54/62) but added pillow boxes.
  - **Re-adding the 4 clips (D):** fixed beds (pre-registered test passed, 26/128 vs 1/128) and box fit.
  - **Learning rate x2 (LR2):** no gain and looser boxes. Keep the current rate.
  - **Batch 8 (B8):** no change, as expected (effective batch is always 64). Keep batch 16 (faster).
- **Recommendation: adopt DCOS as the 7-class candidate.** Recipe: C's settings + `cos_lr=True`, trained on
  `sage_v8_fixclips`. Keep lr0 0.000588 and batch 16.
- **Warnings:**
  1. DCOS was chosen **after** seeing the other results, so treat it as exploratory until it is confirmed on new footage
     or with another seed.
  2. round6_heldout's Laying_Dim_HM is **filmed in the same room** as two of the re-added clips (section 4), so bed
     and chair scores there (D, DCOS) are not evidence for new rooms.
  3. One seed per setting: LR2 jumped to 39/128 beds without new data, so part of any single gain can be luck.
- **Still unsolved:** a person lying in a **dim** room. Laying_Dim_HM: 2–5 of 153 for every model (DCOS 4).
  The TV-lounge falls are also unchanged (~17/97).

---

## 2. What each run tests

- **Learning rate (LR2).** C's learning rate (0.000588) was chosen for the old 13-class data and never re-tuned for
  the 7 classes. LR2 doubles it. (A half-rate run, LRH, was planned only if time allowed; it did not.)
- **Schedule (COS).** C lowers the learning rate in a straight line; COS uses a cosine curve, which stays high
  longer and falls faster at the end. See the top-left panel of `training_curves.png`.
- **Batch size (B8).** Important detail: Ultralytics adds up gradients until it reaches 64 images before each
  update (nbs=64). So with batch 8, 16 or 32 the model is updated with the same 64-image average, and batch size
  mostly changes the BatchNorm statistics and speed, not the learning dynamics. B32 needs ~3.8 GB of GPU memory and
  could not share the 6 GB GPU with a second run, so B8 was run instead (recorded in DECISION_RULE.md before any
  result). B32 can run on its own later if wanted.
- **Re-adding the 4 clips (D).** Phase 5 dropped the 4 problem clips whole, which also threw away 1,260 good bed
  boxes. D puts them back with only the bad frames removed (`build_D.py`):

  | decision | frames (before repeat copies) |
  |---|---|
  | keep: hand-labelled (Dim clips, Blanket outside the bad span) | 464 |
  | keep: model C (never trained on these clips) confirms every person box (IoU >= 0.5) and sees no extra person | 541 |
  | drop: a labelled person box C could not confirm | 735 |
  | drop: C sees a person who is not labelled | 11 |
  | drop: Blanket_Cover_HM frames 710–1420 (the box is on a blanket, teammate report) | 72 |

  Result: 2,010 training images added (with repeat copies): 2,006 person, 1,066 bed, 1,446 chair, 52 cup boxes.
  `spotcheck_D.jpg` shows kept and dropped frames; the dropped ones include the MediaPipe boxes on bedding.
  **Bias:** the filter also drops correct frames that C simply cannot see (very dim scenes), which are exactly the
  hard frames we most want. That may be why D still struggles with the dim lying clip.

---

## 3. Results (people, IoU 0.5 = decision threshold)

| set | N | A (v7) | C | D | LR2 | COS | B8 | DCOS |
|---|---|---|---|---|---|---|---|---|
| heldout_objects | 93 | 58 | 54 | 57 | 58 | 57 | 59 | **60** |
| reserved388_partial | 249 | 107 | 104 | 110 | 107 | 139 | 106 | **148** |
| round6_heldout | 226 | 50 | 51 | **53** | 49 | 50 | 50 | **53** |
| CAUCAFall subject 10* | 419 | 202 | 419 | 419 | 419 | 419 | 419 | 419 |
| ExDark test half* | 346 | 198 | 204 | **220** | 206 | 218 | 208 | 217 |
| false person boxes, reserved388_partial | | 3 | 12 | **1** | 22 | 24 | 6 | 4 |
| empty room (frames with a false person, of 4,101) | | 0 | 0 | 2 | 0 | 0 | 0 | 0 |

\* C and every phase-6 run trained on other images of these datasets; A did not.

Paired against C (boxes only the run finds / boxes only C finds, exact McNemar p):

| set | D | LR2 | COS | B8 | DCOS |
|---|---|---|---|---|---|
| round6_heldout | 4 / 2, p 0.69 | 1 / 3, p 0.63 | 0 / 1, p 1 | 0 / 1, p 1 | 3 / 1, p 0.63 |
| reserved388_partial | 7 / 1, p 0.07 | 6 / 3, p 0.51 | **39 / 4, p 3e-8** | 5 / 3, p 0.73 | **45 / 1, p 1e-12** |
| heldout_objects | 3 / 0, p 0.25 | 5 / 1, p 0.22 | 5 / 2, p 0.45 | 5 / 0, p 0.06 | 6 / 0, p 0.03 |
| ExDark | 32 / 16, p 0.03 | 22 / 20, p 0.88 | 26 / 12, p 0.03 | 20 / 16, p 0.62 | 33 / 20, p 0.10 |

**Verdicts by the rule:** D, LR2, COS, B8 and DCOS are each "no clear difference" vs C (and vs A). COS and DCOS fail only on
the round6_heldout half of the rule (round6_heldout is mostly the dim lying clip, which no model can do yet).

DCOS vs its two parents (people, secondary, pre-registered in amendment 2): vs D, reserved388_partial 39 / 1
(p 7e-11), other sets within 3 boxes; vs COS, reserved388_partial 10 / 1 (p 0.01), other sets within 4 boxes.
So for people DCOS is at least as good as both parents everywhere.

**Where COS's gain comes from** (reserved388_partial, people found per clip):

| clip | N | A | C | D | LR2 | COS | B8 | DCOS |
|---|---|---|---|---|---|---|---|---|
| With_people_Bedroom_Fall | 62 | 21 | 21 | 25 | 21 | 54 | 20 | **59** |
| With_people_Bedroom_Sit | 24 | 21 | 18 | 21 | 22 | 22 | 22 | 23 |
| With_people_Bedroom_Walk | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 |
| With_people_TV_Lounge_1_Fall | 97 | 18 | 18 | 18 | 18 | 17 | 18 | 18 |
| With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 15 | 15 | 15 | 16 | 16 |
| With_people_TV_Lounge_2_Fall | 35 | 16 | 17 | 16 | 16 | 16 | 15 | 17 |

34 of COS's 39 extra people are in Bedroom_Fall: the person falls onto the bed and lies there. `lying_on_bed_sheet.jpg`
shows it: COS boxes the lying person tightly in all four frames (C draws a bed-sized box, D and A find nothing), but
it also puts a second "person" box (confidence ~0.4–0.5) on the pillow beside them. DCOS draws one tight box per
frame and no pillow box. The other fall clips
(TV_Lounge falls, ~17/97 and 16/35) are not helped by any run.

### Box fit (own footage, 475 labelled people, phase-5 method)

| model | matched | good | tight (<90% of the person covered) | loose (>25% extra area) | very loose (>2x) |
|---|---|---|---|---|---|
| A | 159 | 80 | 65 | 14 | 2 |
| C | 165 | 92 | 59 | 24 | 10 |
| **D** | 165 | **102** | 53 | **11** | 1 |
| LR2 | 176 | 83 | 78 | 37 | 1 |
| COS | **191** | 85 | 95 | 16 | **0** |
| B8 | 158 | 90 | 53 | 15 | 1 |
| DCOS | **201** | 96 | 92 | 14 | **0** |

COS and DCOS match the most people, with no very loose boxes, but many of their boxes cut off part of the person
("tight").

### Val set (same val images for C and every phase-6 run, best epoch)

| model | mAP50 | mAP50-95 |
|---|---|---|
| C | 0.586 | 0.424 |
| D | 0.574 | 0.414 |
| LR2 | 0.572 | 0.415 |
| COS | 0.575 | 0.416 |
| B8 | 0.586 | 0.421 |
| DCOS | 0.573 | 0.415 |

All within 0.012 of each other. Val mAP covers all 7 classes and is mostly CAUCAFall/ExDark/v7 images, so it does
not see the bedroom problems this phase targets: the big differences above are invisible in it.

---

## 4. Beds (the phase-5 regression)

| set / clip | A | C | D | LR2 | COS | B8 | DCOS |
|---|---|---|---|---|---|---|---|
| reserved388_partial, all | 19/128 | 1/128 | 26/128 | 39/128 | 1/128 | 3/128 | **44/128** |
| Bedroom_Fall | 12/62 | 1/62 | 10/62 | 37/62 | 1/62 | 1/62 | 41/62 |
| Bedroom_Sit | 3/24 | 0/24 | **15/24** | 2/24 | 0/24 | 2/24 | 2/24 |
| Bedroom_Walk | 4/14 | 0/14 | 1/14 | 0/14 | 0/14 | 0/14 | 1/14 |
| heldout_objects, all | 7/86 | 0/86 | **16/86** | 2/86 | 0/86 | 2/86 | 3/86 |
| round6_heldout Laying_Dim_HM (**same room as re-added clips**) | 1/153 | 0/153 | 152/153 | 0/153 | 0/153 | 0/153 | 151/153 |
| round6_heldout Behind_Bed_HM | 145/145 | 145/145 | 145/145 | 145/145 | 145/145 | 145/145 | 145/145 |

Bed hits on Bedroom_Fall swing a lot between runs (LR2 37, DCOS 41, D 10, others 1), while Bedroom_Sit is only
reliably found by D. Beds in rooms the models never saw are therefore only partly fixed; D is the most consistent.

(Empty_Bedroom_Empty's 28 bed labels are missed by every model, even at IoU 0.3; worth a label check.)

What the pictures show (`bed_sheet.jpg`): in With_people_Bedroom the label marks only the **far** bed. C, LR2 and COS
usually draw **one** box over both the far bed and the bed nearest the camera, which fails IoU 0.5. D more often
draws a separate box on the far bed, which is why D scores well on Bedroom_Sit.

Same-room check: Laying_Dim_HM (held out) and Sitting_Dim_HM / Standing_Walking_Dim_HM (re-added to training)
show the same room from the same camera position: same clock, curtain, door, desk, green chair and floor bed.
D's near-perfect beds and chairs there are therefore not evidence for new rooms. (A also trained on those clips and
still finds 1/153 beds there, so it is not pure memorising either, but this set cannot settle that.)

Other classes, briefly (full table in `RESULTS.md`): COS finds more tables (13/94 vs C 4/94) and chairs, but with
many more false chair/table boxes; D finds 0/94 tables.

---

## 5. Images

| file | what it shows |
|---|---|
| `training_curves.png` | learning rate, train box loss, val mAP and losses per epoch for C and every phase-6 run (running runs appear as partial curves) |
| `person_recall_by_set.png` | person recall per held-out set with 95% intervals, all scored models |
| `examples_sheet.jpg`, `examples/` | frames where a run and C disagree on a person (white = label) |
| `lying_on_bed_sheet.jpg` | **the key COS picture**: four "person lying on the bed" frames, A / C / D / LR2 / COS |
| `bed_sheet.jpg` | beds on rooms D never saw, plus one same-room frame (marked) |
| `spotcheck_D.jpg` | what D's filter kept and dropped from the 4 clips |

---

## 6. DCOS (added this morning)

D and COS each fixed a different problem, so DCOS (D's data + cosine schedule) tested whether the two gains add up.
It changes two things and was chosen after seeing results, so it is **exploratory**: written into `DECISION_RULE.md`
(amendment 2) before it started, judged by the same rule vs C, and compared with D and COS as secondary.
Result: the people gains add up and COS's pillow boxes disappear (sections 1 and 3); D's bed gain on Bedroom_Sit does
not carry over (section 4).

---

## 7. Caveats

- **One run per setting (seed 0).** Changing anything also changes the random path of training. LR2's bed jump
  without any new data shows how big that effect can be, and COS's gain sits in one 62-box clip. McNemar treats each
  trained model as fixed and does not cover run-to-run luck. 2 more seeds of the final candidate and of C would settle it.
- **PROVISIONAL labels**, as in every phase.
- **D's filter is biased** towards frames C can already see (section 2).
- **Same-room leakage** on round6_heldout's Laying_Dim_HM for D (section 4). Re-adding the 4 clips makes that clip a
  weaker test for every future model trained on them.

## 8. Suggested next steps

1. Adopt DCOS as the candidate (`runs/DCOS/weights/best.pt`); keep lr0 0.000588 and batch 16.
2. Confirm it: one more seed of DCOS (and of C), and a test on footage from a room not in training.
3. Hand-check the 735 frames D dropped as "person box not confirmed": many are probably correct dim frames that
   could be added back by hand. Those are the frames that teach "person in the dark".
4. Collect a lying-in-the-dark clip in a **new** room as a clean test, since Laying_Dim_HM now shares a room with
   training data.
5. Then 2 more seeds of the candidate and of C.

## 9. Message for the supervisor

> Sir, as you suggested we tested learning rate, scheduling and batch size, one change at a time against our current
> 7-class model, with the same data, seed and test procedure (the old model reproduced its recorded scores exactly).
> Doubling the learning rate gave no gain and looser boxes, and batch size 8 made no difference. That was expected,
> because the framework accumulates gradients to an effective batch of 64, so batch size mainly affects normalisation
> statistics. A cosine learning-rate schedule made the biggest single difference: in our bedroom fall clip, where the
> person ends up lying on the bed, it found 54 of 62 people versus 21. Separately, we re-added the four problem clips
> with only the faulty frames removed, which brought back bed detection and made person boxes fit better. Combining
> the two (re-added clips + cosine schedule) gave our best model so far: 148 of 249 people on our main held-out set
> versus 104, 59 of 62 on the lying-on-bed clip, fewer false boxes, and still zero false alarms on 4,101 empty-room
> frames. It is not yet a statistically clear win on our second test set, which is dominated by a person lying in a
> dim room; no model handles that yet, and it is our main remaining weakness. We chose the combination after seeing
> the single results, so we will confirm it with another training seed and new footage. All scores are provisional
> until our labelling spec is final.

---

## Files (all in `benchmarks/phase6_sweep/`)

| purpose | files |
|---|---|
| decisions | `PLAN.md`, `DECISION_RULE.md` (written before training; amendments dated), `STATUS.md`, `events.log` |
| D's data | `build_D.py`, `build_D_report.json`, `build_D_decisions.csv`, `spotcheck_D.jpg` (data: `datasets/sage_v8_fixclips`, hardlinks) |
| training | `train_p6.py`, `supervise_p6.py`, `queue.json`, `runs/<RUN>/`, `train_<RUN>.log`, `train_<RUN>_effective_args.json` |
| scoring | `score_p6.py`, `RESULTS.md`, `p6_scores.json`, `hits_*.csv`, `preds_*.json`, `cache/` |
| images | `plot_p6.py`, see section 5 |

Note: `yolo26n.pt` in this folder was downloaded by Ultralytics' automatic AMP check at the start of training; it is
not used by any run and can be deleted.

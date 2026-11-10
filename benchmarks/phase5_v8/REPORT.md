# Phase 5 report: class cleanup, problem clips, retrain with new data

**Date:** 2026-11-07 (overnight run, 03:47 to 09:16). **All held-out scores are PROVISIONAL**: the held-out labels follow no consistent written convention yet (docs/LABELLING_SPEC.md is still a v0.1 draft).

Models compared (same recipe, seed, optimizer and scoring harness as every earlier phase):

| | Model | Training data | Classes |
|---|---|---|---|
| **A** | v7 (current, `models/yolov8n_sage_merged_v7.pt`) | v7 merged set | 13 |
| **B** | `runs/B/weights/best.pt` | v7 minus the 4 problem clips, relabelled to the new classes | 7 |
| **C** | `runs/C/weights/best.pt` | B + CAUCAFall + ExDark (indoor) | 7 |

B was added on purpose: it is the same as C without the new datasets, so comparing B with C shows what the new data did, and A with B shows what the cleanup did.

---

## 1. Short answer

- **All three tasks are done.**
  - The class list now follows the teammates' plan: 0 person, 1 bed, 2 chair, 3 sofa, 4 table, 5 bottle, 6 cup.
  - All 4 problem clips are out of training.
  - C was retrained with CAUCAFall and ExDark added.
- **On our own footage, neither new model is clearly better or worse than v7.** This applies the rule we wrote before training. Person hits differ by at most 4 boxes per set, and every p-value is 0.125 or higher.
- **No new false alarms:** 0 person boxes on 4,101 empty-room frames for every model.
- **On the new kinds of footage, C is much better.**
  - CAUCAFall subject 10 (a person C never saw): C found 419/419 people, v7 202/419.
  - ExDark dark indoor photos: 204/346 vs 198/346 people, with fewer false person boxes (44 vs 66).
  - Caveat: C trained on other images of these same datasets and A did not, so this shows C learned those settings. It does not prove C generalises better.
- **One regression to fix: beds (and tables) in the "With_people_Bedroom" held-out clips.** v7 found 19/128 beds on reserved388_partial; B and C found 1/128. The likely cause is that the removed clips carried 1,260 bed boxes, which B and C lost (section 5).
- **The biggest weakness is unchanged:** a person lying in a dim room (Laying_Dim_HM). All three models find 1–4 of 153 people.
- **Recommendation:** use **C** as the 7-class candidate. It is never worse than A by our rule and is clearly ahead on the new domains. Before we call it final, re-add the 4 clips with only their bad person boxes removed, which should bring the bed labels back (section 7).

---

## 2. Task 1: class cleanup (SAGE_Class_Cleanup_Plan.pdf)

Done exactly as the plan's fixed ID order says. The IDs are rewritten inside the label files of the training copies; the original datasets are untouched.

| New ID | Class | From (v7 / COCO name) |
|---|---|---|
| 0 | person | person |
| 1 | bed | bed |
| 2 | chair | chair |
| 3 | sofa | couch (renamed) |
| 4 | table | dining table (renamed) |
| 5 | bottle | bottle (conditional, kept for now) |
| 6 | cup | cup (conditional, kept for now) |
| dropped | wine glass, bowl, tv, sink, toilet, refrigerator | boxes removed |

- **Bottle and cup are kept.** The plan marks them conditional and the open questions aren't answered yet. They are last in the order, so dropping them later won't change any other ID.
- **Dropped classes:** removing them deleted 6,816 COCO boxes and 111 boxes from our own footage. 707 training and 81 validation COCO images now have no labels left. They stay in as background images, which is normal for YOLO.
- **Section 7 risk (labels missing after the merge)** was handled as the plan suggests:
  - Objects the new datasets don't label were pseudo-labelled with the stock YOLOv8n at conf 0.35, the same convention v7's footage used. Its person boxes were thrown away.
  - I then spot-checked the result visually (`spotcheck_caucafall.jpg`, `spotcheck_exdark.jpg`).
- **Problem found by the spot check:** ExDark labels sofas as "Chair". In the first build the stock model then added a second "sofa" box on top of the same object (`spotcheck_exdark_first_build.jpg`).
  - Fix: when a pseudo sofa box overlaps an ExDark "Chair" box (IoU ≥ 0.5), that box becomes **sofa** (71 boxes). Any other overlapping pseudo box is dropped (76 sofa, 7 bed).
  - The data was rebuilt and checked again.

## 3. Task 2: problem clips (problematic_clips.pdf)

All four clips are removed from training completely, including their `_r1` repeat copies. None of them were in validation or any held-out set.

| Clip | Teammates' finding | Images removed |
|---|---|---|
| Bedroom_Falll | pillow covers the person | 124 |
| Blanket_Cover_HM | frames 710–1420 are a blanket, not a person | 304 |
| Sitting_Dim_HM | ~40% MediaPipe boxes on bedding | 1,722 |
| Standing_Walking_Dim_HM | ~15% bad boxes | 1,496 |
| **Total** | | **3,646** (all train) |

These images held 3,642 person, 1,938 chair, 1,260 bed and 78 cup boxes (v7 names). The full list is in `dropped_problem_clips.csv`.

- **Why whole clips:** your instruction was to filter the clips out, and the bad boxes are spread through the clips, not confined to known frames (except Blanket_Cover). Removing whole clips was the cleanest test.
- **Side effect:** this also removed the hand-drawn frames we had added for clips 2 and 3, and the good bed and chair boxes in those clips. Section 5 shows that this cost us.

## 4. Task 3: new datasets

| Dataset | What was used | Train | Val | Held-out test |
|---|---|---|---|---|
| CAUCAFall | every 6th labelled frame; split by person: subjects 1–8 train, 9 val, **10 test** | 2,599 | 361 | 419 images / 419 people |
| ExDark | **indoor images only** with at least one kept class; official split 1+3 → train, split 2 → half val / half test | 1,556 | 297 | 293 images / 346 people (+ chair 225, table 183, bottle 211, cup 199) |
| OmniFall | **not used for the detector** (no boxes); it fits the posture/LSTM side | – | – | – |

- **ExDark details:**
  - I downloaded its official box annotations, which we didn't have yet (`new datasets/ExDark/annotations_download/`).
  - Skipped: 4,541 outdoor images and 676 indoor images with none of our classes.
- **Leakage check:** no subject-10 frames are in C's train or val data, and no ExDark test image is in train or val.

**Final training sets** (0 corrupt images in the Ultralytics scan):

| Set | Train images | Val images |
|---|---|---|
| B (`datasets/sage_v8_clean`) | 11,397 | 2,610 |
| C (`datasets/sage_v8_full`) | 15,552 | 3,268 |

**Training:**
- Recipe: v7's recipe (YOLOv8n, 30 epochs, imgsz 640, batch 16, patience 10, seed 0, AdamW lr 0.000588 pinned).
- C ran all 30 epochs (192 min).
- B early-stopped after epoch 29, its best epoch being 19 (130 min). Early stopping is part of the same recipe A was trained with.

![Training curves](A_B_C_training_curves.png)

The validation curves can't be compared across models: A is validated on 13 classes, B on 7, and C on 7 plus extra CAUCAFall and ExDark images. **We don't decide on validation mAP**; the decision uses held-out recall, below.

---

## 5. Results

Scoring setup:
- Same harness as every phase: conf 0.4, imgsz 640, same-class greedy matching, exact McNemar test on per-box person hits.
- A's 13-class predictions are mapped into the 7-class space. Person is ID 0 in both, so A's person numbers are unaffected.

### 5.1 Control

A reproduces its recorded numbers exactly, so the harness is unchanged.

| Set | Recorded | Measured |
|---|---|---|
| heldout_objects | 58/93 | 58/93 ✓ |
| reserved388_partial | 107/249 | 107/249 ✓ |
| round6_heldout | 50/226 | 50/226 ✓ |

### 5.2 Verdict (DECISION_RULE.md, written before training)

| Model | round6_heldout (new-only / A-only, p) | reserved388_partial (new-only / A-only, p) | Verdict |
|---|---|---|---|
| B vs A | 2 / 2, p = 1 | 2 / 6, p = 0.29 | **no clear difference** |
| C vs A | 3 / 2, p = 1 | 2 / 5, p = 0.45 | **no clear difference** |

Empty-room false alarms: A 0/4101, B 0/4101, C 0/4101.

### 5.3 Person recall per held-out set (IoU 0.5)

![Person recall per set](person_recall_by_set.png)

| Set | N | A | B | C | False person boxes (A / B / C) |
|---|---|---|---|---|---|
| heldout_objects | 93 | 58 (0.62) | 55 (0.59) | 54 (0.58) | 1 / 4 / 1 |
| reserved388_partial | 249 | 107 (0.43) | 103 (0.41) | 104 (0.42) | 3 / 4 / 12 |
| round6_heldout | 226 | 50 (0.22) | 50 (0.22) | 51 (0.23) | 0 / 2 / 1 |
| CAUCAFall subject 10* | 419 | 202 (0.48) | 163 (0.39) | **419 (1.00)** | 1 / 3 / 0 |
| ExDark test half* | 346 | 198 (0.57) | 180 (0.52) | 204 (0.59) | 66 / 36 / 44 |

\* C trained on other images from these datasets; A and B did not.

How to read the paired tests (full tables, with 95% CIs and per-clip rows, in `RESULTS.md`):

- **C vs B (what the new data did):**
  - CAUCAFall: C better, 256 vs 0 boxes only one model found.
  - ExDark: C better, 41 vs 17, p = 0.002.
  - Our own three sets: no difference.
  - Supplementary (IoU 0.3): C also beats B on reserved388_partial, 14 vs 3, p = 0.013. Almost all of that is in With_people_Bedroom_Fall (11 vs 0): C puts looser but usable boxes on fallen people that B misses entirely.
- **B vs A (what the cleanup alone did):**
  - CAUCAFall: B worse, p = 2.6e-6.
  - ExDark: B worse, p = 0.013.
  - Our sets: no difference.
  - So cleaning alone did not help on unfamiliar footage. The new data is what moved C ahead. This run can't separate whether B lost ground because of the removed clips or because of the class change.
- **Weak spot, all models:** Laying_Dim_HM. A 2/153, B 1/153, C 4/153 people found.

### 5.4 Example frames (same frames for all three models)

Frames where A and C disagree, picked automatically from the held-out sets, plus one dim-room frame. White = ground-truth person; coloured = that model's person boxes (A blue, B orange, C green). Single frames are in `examples/`.

![A | B | C example frames](examples_sheet.jpg)

### 5.4b Box fit: are the person boxes too tight? (`box_fit.py`, added after the run)

Each hand-labelled person in our own test footage (reserved388_partial + round6_heldout, 475 people) is paired with the model's best-overlapping person box. Coverage is the share of the labelled box the model's box covers.

| Model | Matched | Median IoU | Median coverage | Boxes covering ≥ 90% | Median size vs label | 10th–90th pct |
|---|---|---|---|---|---|---|
| A | 159 | 0.86 | 93% | 94/159 | 0.99× | 0.80–1.17× |
| B | 154 | 0.85 | 95% | 103/154 | 1.00× | 0.82–1.20× |
| C | 165 | 0.85 | 95% | 106/165 | 1.02× | 0.85–1.34× |

When a model finds a person, the box is typically the same size as the hand label and covers about 95% of it. Boxes are not systematically too tight; C's are slightly looser than A's.

![Box fit, model C](box_fit/box_fit_sheet_C.jpg)

### 5.5 Other classes (IoU 0.5, recall and false positives)

| Set | Class | A | B | C |
|---|---|---|---|---|
| heldout_objects | bed | 7/86 (fp 35) | 0/86 (fp 47) | 0/86 (fp 39) |
| heldout_objects | chair | 18/90 (fp 14) | 18/90 (fp 1) | 19/90 (fp 8) |
| heldout_objects | sofa | 168/276 (fp 36) | 111/276 (fp 14) | 155/276 (fp 18) |
| heldout_objects | table | 8/94 (fp 1) | 0/94 (fp 13) | 4/94 (fp 27) |
| reserved388_partial | bed | 19/128 (fp 62) | 1/128 (fp 82) | 1/128 (fp 54) |
| reserved388_partial | sofa | 231/450 (fp 98) | 201/450 (fp 20) | 228/450 (fp 57) |
| reserved388_partial | table | 8/94 (fp 7) | 0/94 (fp 13) | 4/94 (fp 28) |
| round6_heldout | bed | 146/298 (fp 0) | 159/298 (fp 0) | 145/298 (fp 0) |
| round6_heldout | chair | 326/443 (fp 2) | 298/443 (fp 10) | 374/443 (fp 25) |
| exdark_test* | chair | 99/225 | 94/225 | 117/225 |
| exdark_test* | table | 29/183 | 23/183 | 65/183 |
| exdark_test* | bottle | 73/211 | 79/211 | 92/211 |
| exdark_test* | cup | 55/199 | 49/199 | 99/199 |

- **Bed and table regression on the With_people_Bedroom clips.**
  - All the bed boxes left in our own training footage come from the Sanawar/Hussain testing clips and Behind_Chair_HM.
  - The 1,260 bed boxes in the removed clips were most likely the main examples of the bedroom these held-out clips were filmed in.
  - This is the likely explanation, not a proven one.
- **On round6_heldout, beds are unaffected** (159 and 145 vs 146).
- **Chairs:** C finds more on round6_heldout (374 vs 326) but makes more false chair boxes (25 vs 2).

---

## 6. Caveats

1. **Held-out labels are provisional.** There is no written labelling convention yet, so small differences (a few boxes) are within label noise.
2. **The new test sets favour C.** C trained on the same settings (same CAUCAFall rooms and cameras, same ExDark photo style). CAUCAFall's 419/419 says C has learned that setting; it does not say C will be perfect on our home.
3. **Whole clips were removed**, including their good bed and chair boxes and the hand-drawn frames for clips 2 and 3. This is the likely cause of the bed regression.
4. **Bottle and cup** are kept until the team answers the plan's open questions.
5. **OmniFall** was not used, because it has no boxes.
6. **ExDark is licensed for research use only.** Fine for the FYP; check before any product use.
7. **Single run per model** (seed 0); there was no time for repeat seeds overnight.

## 7. Suggested next steps

1. **Re-add the 4 clips, keeping their bed and chair boxes but removing only the bad person boxes.**
   - Blanket_Cover_HM: drop the person box on frames 710–1420 only.
   - Sitting_Dim_HM and Standing_Walking_Dim_HM: drop the MediaPipe person boxes that sit on bedding, or hand-fix them.
   - Bedroom_Falll: drop the person box where the pillow covers the person.

   Then retrain C the same way. This should recover beds without bringing back the bad person labels. Build and score scripts are ready to reuse.
2. **Target the dim lying case.** Hand-label more lying-in-dim-room frames; no model gets more than 4/153 of these.
3. **Finish the labelling spec** so held-out scores stop being provisional.
4. **Decide bottle and cup.** If dropped, IDs 0–4 stay the same.

---

## 8. Message for the supervisor

> Sir, overnight we applied the team's class cleanup (7 classes: person, bed, chair, sofa, table, bottle, cup), removed the four problem clips (3,646 training images), and retrained YOLOv8n with two new datasets added (CAUCAFall, and the indoor part of ExDark). We used the same recipe and test procedure as before, and the old model reproduced its recorded scores exactly, so the comparison is fair. On our own held-out footage the new model is statistically the same as v7 for detecting people, with zero false alarms on 4,101 empty-room frames. On new kinds of footage it is clearly better: 419/419 people on an unseen CAUCAFall subject vs 202 for v7, and slightly better on dark indoor photos with fewer false alarms. One regression: bed detection in our bedroom test clips dropped, most likely because removing whole clips also removed their good bed labels. Next we will re-add those clips with only the bad person boxes removed. Detecting a person lying in a dim room is still the main weakness for every model. All scores are provisional until our labelling spec is final.

---

## Files (all in `benchmarks/phase5_v8/`)

| Purpose | Files |
|---|---|
| Decisions | `PLAN.md`, `DECISION_RULE.md` (both written before training), `STATUS.md` (log) |
| Data build | `build_v8.py`, `build_report.json`, `dropped_problem_clips.csv`, `pseudo_labels_new_sources.csv`, `spotcheck*.jpg` |
| Training | `train_v8.py`, `run_overnight.py`, `runs/B`, `runs/C`, `train_*_effective_args.json`, `pipeline_events.log` |
| Scoring | `score_v8.py`, `RESULTS.md`, `v8_scores.json`, `hits_{A,B,C}.csv`, `preds_{A,B,C}.json` |
| Figures | `plot_v8.py`, `A_B_C_training_curves.png`, `person_recall_by_set.png`, `examples_sheet.jpg`, `examples/` |

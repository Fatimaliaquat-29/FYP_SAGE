# Phase 5 plan: class cleanup, problem-clip removal, retrain with new datasets

Written 2026-11-07 ~03:15, before any dataset was built or model trained. Hussain asked for three things overnight
(class redefinition per `SAGE_Class_Cleanup_Plan.pdf`, removal of the clips in `problematic_clips.pdf`, retrain
including the new datasets) and left the decisions to Claude. Every decision below is recorded so it can be undone.

## 1. Classes (from the cleanup plan, sections 3, 4 and 6)

New fixed ID order, applied by rewriting the IDs inside every label file:

| id | class | from v7 (13-class) | from ExDark | from CAUCAFall |
|---|---|---|---|---|
| 0 | person | person (0) | People | fall, nofall |
| 1 | bed | bed (7) | (pseudo-label) | (pseudo-label) |
| 2 | chair | chair (5) | Chair | (pseudo-label) |
| 3 | sofa | couch (6) | (pseudo-label) | (pseudo-label) |
| 4 | table | dining table (8) | Table | (pseudo-label) |
| 5 | bottle | bottle (1) | Bottle | (pseudo-label) |
| 6 | cup | cup (2) | Cup | (pseudo-label) |

Dropped: wine glass, bowl, toilet, tv, sink, refrigerator (their boxes are deleted; the images stay).

**Decision: bottle and cup are kept.** The plan marks them conditional on open questions 1 and 3, which are not
answered yet. They are last in the ID order, so dropping them later does not change the core IDs.

## 2. Problem clips (from problematic_clips.pdf)

**Decision: every training frame of the 4 clips is removed, including the `_r1` repeat copies** ("filter out
those clips"). In v7 train that is 3,646 images: Sitting_Dim_HM 1,722, Standing_Walking_Dim_HM 1,496,
Blanket_Cover_HM 304, Bedroom_Falll 124. None of the 4 clips is in v7 val or in any held-out evaluation set.
Note this also removes the hand-drawn frames of clips 2 and 3 (211 and 173 frames), not only their MediaPipe frames.

## 3. New datasets

- **CAUCAFall**: every 6th labelled frame per (subject, activity) folder. Subjects 1-8 train, subject 9 val,
  subject 10 held-out test. Person boxes from CAUCAFall's own labels; 6 frames without labels skipped.
- **ExDark**: only **indoor** images (ExDark's own indoor/outdoor flag) with at least one box of a kept class.
  ExDark split 1 (train) + 3 (test) -> our train; split 2 (val) -> half val, half held-out test (by name parity).
  JPEGs with an EXIF rotation tag are skipped (their pixel boxes would not line up after decoding).
  Boxes of Bicycle, Boat, Bus, Car, Cat, Dog, Motorbike are dropped.
- **OmniFall: not used for the detector.** It has activity labels but no boxes. It belongs to the
  posture/activity side (cleanup plan, Group 2).

**Missing labels (cleanup plan, section 7)**: classes a source does not annotate are pseudo-labelled the way
v7's own footage was (`src/detection/generate_bbox_dataset.py --pseudo_objects --object_conf 0.35`): stock
`models/yolov8n.pt`, conf 0.35, its person boxes discarded. CAUCAFall gets bed/chair/sofa/table/bottle/cup;
ExDark gets bed and sofa only. A sample is drawn and checked by eye before training.

## 4. Models

| model | data | notes |
|---|---|---|
| A | v7 (existing `models/yolov8n_sage_merged_v7.pt`) | 13 classes, baseline |
| B | `datasets/sage_v8_clean`: v7 minus the 4 clips, 7 classes | isolates the effect of cleanup |
| C | `datasets/sage_v8_full`: B + CAUCAFall + ExDark | the requested model |

Recipe for B and C: A's recorded `train_args` (30 epochs, imgsz 640, batch 16, patience 10, close_mosaic 10,
seed 0, starting from `models/yolov8n.pt`) with optimizer pinned to what A actually used (AdamW, lr0 0.000588,
momentum 0.9). Without pinning, `optimizer=auto` would pick a different learning rate for 7 classes
(0.002*5/(4+nc)). Training order: C first (the deliverable), then B.

## 5. Evaluation

Same harness as phases 3-4 (`score_v7_suite` matching, conf 0.4, imgsz 640), on the same three held-out sets
plus the empty-room clips, with ground truth and model-A predictions mapped into the 7-class space. Person is ID 0
in both, so A's control numbers must still reproduce (58/93, 107/249, 50/226). Supplementary: person (and
ExDark's human-labelled chair/table/bottle/cup) on the new held-out tests (CAUCAFall subject 10, ExDark test half);
C has seen those domains in training, A and B have not.

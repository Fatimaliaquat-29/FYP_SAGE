# Training-label audit -- datasets/sage_merged_v7 (train split)

Generated from files in benchmarks/label_audit/ (stats run 2026-10-10T14:58:46). Read-only on the dataset: images and label files were read directly; no ultralytics train/val, no data.yaml loading by ultralytics. Dataset label caches unchanged (raw/raw_cache_before.txt vs the post-run listing in DECISIONS.md).

**Two kinds of evidence, never mixed:** (1) automatic flags from a stock detector -- leads, not verdicts; (2) a provisional reading of 120 sampled images by an AI (Claude) -- **UNVERIFIED, not ground truth**; the human columns in audit_sheet.csv are empty.

Class order: src/detection/sage_classes.py vs datasets/sage_merged_v7/data.yaml names -> **identical** (13 classes, person = index 0).

## (a) Inventory

- images 15043, label files 15043, images without a label file 0, images with an empty label file 539, label files without an image 0, boxes with out-of-schema class ids 0.
- `_rN` repeat copies (build_merged_dataset --own_repeat): 4552, of which md5-identical to their original: 4552. Other md5 duplicates (not explained by `_rN`): 499 files.
  Non-repeat duplicate groups by clip (identical frames under different names): `Hussain_Testing_7_23_26_old == Sanawar_Testing_7_22_26_old` x307; `Hussain_Testing_7_23_26_normal == Sanawar_Testing_7_22_26_normal` x192.

| source (filename prefix) | images | of which `_rN` copies | person boxes | mean person boxes / image | images with 0 person boxes |
|---|---|---|---|---|---|
| `coco_` -- COCO (external dataset; name is explicit) | 5400 | 0 | 11371 | 2.11 | 2870/5400 (53.1%) |
| `empty_` -- own empty-room footage | 539 | 0 | 0 | 0.00 | 539/539 (100.0%) |
| `own_` -- own footage | 9104 | 4552 | 9076 | 1.00 | 28/9104 (0.3%) |

Person-label provenance (from handlabels/ cross-check; see DECISIONS.md):

| provenance | images | person boxes | mean / image | 0-person images |
|---|---|---|---|---|
| MediaPipe-derived | 7458 | 7458 | 1.00 | 0/7458 (0.0%) |
| coco (external, human-drawn) | 5400 | 11371 | 2.11 | 2870/5400 (53.1%) |
| empty-room (no person by construction) | 539 | 0 | 0.00 | 539/539 (100.0%) |
| hand-drawn (round5) | 236 | 208 | 0.88 | 28/236 (11.9%) |
| hand-drawn (round6) | 642 | 642 | 1.00 | 0/642 (0.0%) |
| hand-drawn (round6_patch) | 768 | 768 | 1.00 | 0/768 (0.0%) |

<details><summary>Per clip</summary>

| clip | images | person boxes | mean / image | 0-person images |
|---|---|---|---|---|
| Bedroom_Emptyy | 18 | 0 | 0.00 | 18/18 (100.0%) |
| Bedroom_Falll | 124 | 120 | 0.97 | 4/124 (3.2%) |
| Behind_Chair_HM | 338 | 338 | 1.00 | 0/338 (0.0%) |
| Blanket_Cover_HM | 304 | 304 | 1.00 | 0/304 (0.0%) |
| Hussain_Testing_7_23_26_normal | 384 | 384 | 1.00 | 0/384 (0.0%) |
| Hussain_Testing_7_23_26_old | 614 | 614 | 1.00 | 0/614 (0.0%) |
| Sanawar_Testing_7_22_26_Fall_Curled | 82 | 82 | 1.00 | 0/82 (0.0%) |
| Sanawar_Testing_7_22_26_Fast_Sit | 62 | 62 | 1.00 | 0/62 (0.0%) |
| Sanawar_Testing_7_22_26_Legs_occluded | 154 | 154 | 1.00 | 0/154 (0.0%) |
| Sanawar_Testing_7_22_26_Lying_legs_straight | 146 | 146 | 1.00 | 0/146 (0.0%) |
| Sanawar_Testing_7_22_26_Lying_straight | 146 | 146 | 1.00 | 0/146 (0.0%) |
| Sanawar_Testing_7_22_26_Normal_Fall_1 | 154 | 154 | 1.00 | 0/154 (0.0%) |
| Sanawar_Testing_7_22_26_Off_axis | 190 | 190 | 1.00 | 0/190 (0.0%) |
| Sanawar_Testing_7_22_26_Sit_1 | 156 | 156 | 1.00 | 0/156 (0.0%) |
| Sanawar_Testing_7_22_26_Sit_3 | 176 | 176 | 1.00 | 0/176 (0.0%) |
| Sanawar_Testing_7_22_26_Standing_1 | 168 | 168 | 1.00 | 0/168 (0.0%) |
| Sanawar_Testing_7_22_26_Standing_2 | 180 | 180 | 1.00 | 0/180 (0.0%) |
| Sanawar_Testing_7_22_26_Standing_3 | 126 | 126 | 1.00 | 0/126 (0.0%) |
| Sanawar_Testing_7_22_26_normal | 384 | 384 | 1.00 | 0/384 (0.0%) |
| Sanawar_Testing_7_22_26_old | 614 | 614 | 1.00 | 0/614 (0.0%) |
| Sanawar_Testing_7_25_26_Backward_fall | 106 | 106 | 1.00 | 0/106 (0.0%) |
| Sanawar_Testing_7_25_26_Chair_fall | 210 | 210 | 1.00 | 0/210 (0.0%) |
| Sanawar_Testing_7_25_26_Fall_and_lie | 274 | 274 | 1.00 | 0/274 (0.0%) |
| Sanawar_Testing_7_25_26_Far_fall | 124 | 124 | 1.00 | 0/124 (0.0%) |
| Sanawar_Testing_7_25_26_Occluded_fall | 166 | 166 | 1.00 | 0/166 (0.0%) |
| Sanawar_Testing_7_25_26_Off_axis_fall | 78 | 78 | 1.00 | 0/78 (0.0%) |
| Sanawar_Testing_7_25_26_Side_fall | 154 | 154 | 1.00 | 0/154 (0.0%) |
| Sanawar_Testing_7_25_26_Slow_fall | 160 | 160 | 1.00 | 0/160 (0.0%) |
| Sitting_Dim_HM | 1722 | 1722 | 1.00 | 0/1722 (0.0%) |
| Standing_Walking_Dim_HM | 1496 | 1496 | 1.00 | 0/1496 (0.0%) |
| TV_Lounge_Emptyy | 30 | 0 | 0.00 | 30/30 (100.0%) |
| TV_Lounge_Fallll | 112 | 88 | 0.79 | 24/112 (21.4%) |
| WhatsApp_Video_2026_07_29_at_7.31.43_PM | 26 | 0 | 0.00 | 26/26 (100.0%) |
| WhatsApp_Video_2026_07_29_at_7.42.21_PM | 33 | 0 | 0.00 | 33/33 (100.0%) |
| WhatsApp_Video_2026_07_29_at_7.42.52_PM | 27 | 0 | 0.00 | 27/27 (100.0%) |
| WhatsApp_Video_2026_07_29_at_7.43.14_PM | 17 | 0 | 0.00 | 17/17 (100.0%) |
| coco | 5400 | 11371 | 2.11 | 2870/5400 (53.1%) |
| empty_Top_drawing | 50 | 0 | 0.00 | 50/50 (100.0%) |
| empty_Top_lounge | 53 | 0 | 0.00 | 53/53 (100.0%) |
| empty_ground_myRoom1 | 33 | 0 | 0.00 | 33/33 (100.0%) |
| empty_mid_bedroom | 49 | 0 | 0.00 | 49/49 (100.0%) |
| empty_mid_bedroom1 | 59 | 0 | 0.00 | 59/59 (100.0%) |
| empty_mid_bedroom_1 | 45 | 0 | 0.00 | 45/45 (100.0%) |
| empty_top_bedroom | 49 | 0 | 0.00 | 49/49 (100.0%) |
| empty_top_room | 50 | 0 | 0.00 | 50/50 (100.0%) |

</details>

Darkness: mean luma per image in train_images.csv; dark = luma <= 93.3 (bottom third of ALL train images), bright = luma >= 121.0. Distribution by source: coco: bright 1597, dark 1549, mid 2254; empty: bright 253, dark 30, mid 256; own: bright 3164, dark 3436, mid 2504.

## (b) Leakage check

| eval set | eval images | filename overlap | overlap after stripping `own_`/`coco_`/`empty_` and `_rN` | md5 overlap |
|---|---|---|---|---|
| eval/heldout_objects | 200 | 0 | 0 | 0 |
| handlabels/round6_heldout | 298 | 0 | 0 | 0 |

Train vs val split of the same dataset: 0 of 2610 val images are md5-identical to a train image.

md5 catches byte-identical copies only; a re-encoded or re-extracted frame of the same video moment would not match.

## (c) Automatic flags (detector proxy -- leads, NOT verdicts)

Detector `yolo26s.pt` (stock COCO, person class only), imgsz 640, run on 5091 images (stride 1): own_ + empty_ images (own footage; empty_ names match yolo_testing/Training/Empty clips), excluding _rN repeat copies (md5-identical duplicates). **SUSPECTED_MISSING** = a detection with conf >= 0.5 whose best IoU with every GT person box is < 0.3. **SUSPECTED_PHANTOM** = a GT person box with no detection (conf >= 0.25) at IoU >= 0.3. The detector itself fails on dark, occluded and lying people and fires on reflections/posters, so a flag says 'detector and label disagree', not which one is wrong. Calibration point: on frames whose person boxes were HAND-drawn, the detector disagrees with the label (PHANTOM) at the rates shown below; that is mostly the detector's own miss rate on hard footage.

**by provenance**

| group | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM | phantom GT boxes / GT person boxes |
|---|---|---|---|---|
| ALL | 5091 | 271/5091 (5.3%) | 1012/5091 (19.9%) | 1012/4538 |
| MediaPipe-derived | 3729 | 264/3729 (7.1%) | 649/3729 (17.4%) | 649/3729 |
| empty-room (no person by construction) | 539 | 0/539 (0.0%) | 0/539 (0.0%) | 0/0 |
| hand-drawn (round5) | 118 | 0/118 (0.0%) | 69/118 (58.5%) | 69/104 |
| hand-drawn (round6) | 321 | 5/321 (1.6%) | 204/321 (63.6%) | 204/321 |
| hand-drawn (round6_patch) | 384 | 2/384 (0.5%) | 90/384 (23.4%) | 90/384 |

**by darkness bucket**

| group | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM | phantom GT boxes / GT person boxes |
|---|---|---|---|---|
| ALL | 5091 | 271/5091 (5.3%) | 1012/5091 (19.9%) | 1012/4538 |
| bright | 1835 | 7/1835 (0.4%) | 231/1835 (12.6%) | 231/1582 |
| dark | 1748 | 236/1748 (13.5%) | 641/1748 (36.7%) | 641/1706 |
| mid | 1508 | 28/1508 (1.9%) | 140/1508 (9.3%) | 140/1250 |

**by provenance x darkness**

| group | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM | phantom GT boxes / GT person boxes |
|---|---|---|---|---|
| ALL | 5091 | 271/5091 (5.3%) | 1012/5091 (19.9%) | 1012/4538 |
| MediaPipe-derived | bright | 1261 | 2/1261 (0.2%) | 27/1261 (2.1%) | 27/1261 |
| MediaPipe-derived | dark | 1227 | 234/1227 (19.1%) | 485/1227 (39.5%) | 485/1227 |
| MediaPipe-derived | mid | 1241 | 28/1241 (2.3%) | 137/1241 (11.0%) | 137/1241 |
| empty-room (no person by construction) | bright | 253 | 0/253 (0.0%) | 0/253 (0.0%) | 0/0 |
| empty-room (no person by construction) | dark | 30 | 0/30 (0.0%) | 0/30 (0.0%) | 0/0 |
| empty-room (no person by construction) | mid | 256 | 0/256 (0.0%) | 0/256 (0.0%) | 0/0 |
| hand-drawn (round5) | dark | 107 | 0/107 (0.0%) | 66/107 (61.7%) | 66/95 |
| hand-drawn (round5) | mid | 11 | 0/11 (0.0%) | 3/11 (27.3%) | 3/9 |
| hand-drawn (round6) | bright | 321 | 5/321 (1.6%) | 204/321 (63.6%) | 204/321 |
| hand-drawn (round6_patch) | dark | 384 | 2/384 (0.5%) | 90/384 (23.4%) | 90/384 |

**by lying proxy (GT person box wider than tall in pixels -- crude)**

| group | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM | phantom GT boxes / GT person boxes |
|---|---|---|---|---|
| ALL | 5091 | 271/5091 (5.3%) | 1012/5091 (19.9%) | 1012/4538 |
| GT person box taller than wide | 3061 | 49/3061 (1.6%) | 356/3061 (11.6%) | 356/3061 |
| GT person box wider than tall | 1477 | 222/1477 (15.0%) | 656/1477 (44.4%) | 656/1477 |
| no GT person | 553 | 0/553 (0.0%) | 0/553 (0.0%) | 0/0 |

**by source prefix**

| group | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM | phantom GT boxes / GT person boxes |
|---|---|---|---|---|
| ALL | 5091 | 271/5091 (5.3%) | 1012/5091 (19.9%) | 1012/4538 |
| empty | 539 | 0/539 (0.0%) | 0/539 (0.0%) | 0/0 |
| own | 4552 | 271/4552 (6.0%) | 1012/4552 (22.2%) | 1012/4538 |

<details><summary>by clip</summary>

| clip | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM |
|---|---|---|---|
| ALL | 5091 | 271/5091 (5.3%) | 1012/5091 (19.9%) |
| Bedroom_Emptyy | 18 | 0/18 (0.0%) | 0/18 (0.0%) |
| Bedroom_Falll | 62 | 0/62 (0.0%) | 39/62 (62.9%) |
| Behind_Chair_HM | 169 | 0/169 (0.0%) | 98/169 (58.0%) |
| Blanket_Cover_HM | 152 | 5/152 (3.3%) | 106/152 (69.7%) |
| Hussain_Testing_7_23_26_normal | 192 | 0/192 (0.0%) | 0/192 (0.0%) |
| Hussain_Testing_7_23_26_old | 307 | 0/307 (0.0%) | 0/307 (0.0%) |
| Sanawar_Testing_7_22_26_Fall_Curled | 41 | 0/41 (0.0%) | 0/41 (0.0%) |
| Sanawar_Testing_7_22_26_Fast_Sit | 31 | 0/31 (0.0%) | 0/31 (0.0%) |
| Sanawar_Testing_7_22_26_Legs_occluded | 77 | 0/77 (0.0%) | 0/77 (0.0%) |
| Sanawar_Testing_7_22_26_Lying_legs_straight | 73 | 1/73 (1.4%) | 5/73 (6.8%) |
| Sanawar_Testing_7_22_26_Lying_straight | 73 | 1/73 (1.4%) | 0/73 (0.0%) |
| Sanawar_Testing_7_22_26_Normal_Fall_1 | 77 | 2/77 (2.6%) | 2/77 (2.6%) |
| Sanawar_Testing_7_22_26_Off_axis | 95 | 0/95 (0.0%) | 0/95 (0.0%) |
| Sanawar_Testing_7_22_26_Sit_1 | 78 | 0/78 (0.0%) | 0/78 (0.0%) |
| Sanawar_Testing_7_22_26_Sit_3 | 88 | 0/88 (0.0%) | 0/88 (0.0%) |
| Sanawar_Testing_7_22_26_Standing_1 | 84 | 0/84 (0.0%) | 0/84 (0.0%) |
| Sanawar_Testing_7_22_26_Standing_2 | 90 | 0/90 (0.0%) | 0/90 (0.0%) |
| Sanawar_Testing_7_22_26_Standing_3 | 63 | 0/63 (0.0%) | 0/63 (0.0%) |
| Sanawar_Testing_7_22_26_normal | 192 | 0/192 (0.0%) | 0/192 (0.0%) |
| Sanawar_Testing_7_22_26_old | 307 | 0/307 (0.0%) | 0/307 (0.0%) |
| Sanawar_Testing_7_25_26_Backward_fall | 53 | 1/53 (1.9%) | 1/53 (1.9%) |
| Sanawar_Testing_7_25_26_Chair_fall | 105 | 1/105 (1.0%) | 2/105 (1.9%) |
| Sanawar_Testing_7_25_26_Fall_and_lie | 137 | 2/137 (1.5%) | 78/137 (56.9%) |
| Sanawar_Testing_7_25_26_Far_fall | 62 | 0/62 (0.0%) | 12/62 (19.4%) |
| Sanawar_Testing_7_25_26_Occluded_fall | 83 | 2/83 (2.4%) | 31/83 (37.3%) |
| Sanawar_Testing_7_25_26_Off_axis_fall | 39 | 0/39 (0.0%) | 9/39 (23.1%) |
| Sanawar_Testing_7_25_26_Side_fall | 77 | 0/77 (0.0%) | 6/77 (7.8%) |
| Sanawar_Testing_7_25_26_Slow_fall | 80 | 20/80 (25.0%) | 18/80 (22.5%) |
| Sitting_Dim_HM | 861 | 166/861 (19.3%) | 420/861 (48.8%) |
| Standing_Walking_Dim_HM | 748 | 70/748 (9.4%) | 155/748 (20.7%) |
| TV_Lounge_Emptyy | 30 | 0/30 (0.0%) | 0/30 (0.0%) |
| TV_Lounge_Fallll | 56 | 0/56 (0.0%) | 30/56 (53.6%) |
| WhatsApp_Video_2026_07_29_at_7.31.43_PM | 26 | 0/26 (0.0%) | 0/26 (0.0%) |
| WhatsApp_Video_2026_07_29_at_7.42.21_PM | 33 | 0/33 (0.0%) | 0/33 (0.0%) |
| WhatsApp_Video_2026_07_29_at_7.42.52_PM | 27 | 0/27 (0.0%) | 0/27 (0.0%) |
| WhatsApp_Video_2026_07_29_at_7.43.14_PM | 17 | 0/17 (0.0%) | 0/17 (0.0%) |
| empty_Top_drawing | 50 | 0/50 (0.0%) | 0/50 (0.0%) |
| empty_Top_lounge | 53 | 0/53 (0.0%) | 0/53 (0.0%) |
| empty_ground_myRoom1 | 33 | 0/33 (0.0%) | 0/33 (0.0%) |
| empty_mid_bedroom | 49 | 0/49 (0.0%) | 0/49 (0.0%) |
| empty_mid_bedroom1 | 59 | 0/59 (0.0%) | 0/59 (0.0%) |
| empty_mid_bedroom_1 | 45 | 0/45 (0.0%) | 0/45 (0.0%) |
| empty_top_bedroom | 49 | 0/49 (0.0%) | 0/49 (0.0%) |
| empty_top_room | 50 | 0/50 (0.0%) | 0/50 (0.0%) |

</details>

## (d) Provisional AI review of 120 sampled images -- UNVERIFIED

Sample (seed 0): 40 uniform random + 40 SUSPECTED_MISSING + 20 SUSPECTED_PHANTOM + 20 from the darkest 10% of own footage (luma <= 66.8), deduplicated, shortfalls {'random': 0, 'suspected_missing': 0, 'suspected_phantom': 0, 'darkest_10pct_own': 0}. Contact sheets: sheets/sheet_NN.jpg, sheet n = idx 9(n-1)+1..9n row-major; GREEN = GT person box, RED = detector box (conf>=0.5) matching no GT person, thin GREY = other GT classes; darkest tiles are display-brightened (labelled on the tile). Verdicts are Claude's reading of those sheets at contact-sheet resolution; **a human has not checked them.**

**AI verdicts by sampling_reason**

| group | n | OK | BAD_BOX | MISSING_PERSON_BOX | UNCLEAR |
|---|---|---|---|---|---|
| darkest_10pct_own | 20 | 14/20 (70.0%) | 5/20 (25.0%) | 0/20 (0.0%) | 1/20 (5.0%) |
| random | 40 | 32/40 (80.0%) | 6/40 (15.0%) | 0/40 (0.0%) | 2/40 (5.0%) |
| suspected_missing | 40 | 4/40 (10.0%) | 36/40 (90.0%) | 0/40 (0.0%) | 0/40 (0.0%) |
| suspected_phantom | 20 | 5/20 (25.0%) | 11/20 (55.0%) | 0/20 (0.0%) | 4/20 (20.0%) |
| ALL | 120 | 55/120 (45.8%) | 58/120 (48.3%) | 0/120 (0.0%) | 7/120 (5.8%) |

**AI verdicts by source (clip)**

| group | n | OK | BAD_BOX | MISSING_PERSON_BOX | UNCLEAR |
|---|---|---|---|---|---|
| Behind_Chair_HM | 5 | 2/5 (40.0%) | 0/5 (0.0%) | 0/5 (0.0%) | 3/5 (60.0%) |
| Blanket_Cover_HM | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Hussain_Testing_7_23_26_normal | 2 | 2/2 (100.0%) | 0/2 (0.0%) | 0/2 (0.0%) | 0/2 (0.0%) |
| Hussain_Testing_7_23_26_old | 2 | 2/2 (100.0%) | 0/2 (0.0%) | 0/2 (0.0%) | 0/2 (0.0%) |
| Sanawar_Testing_7_22_26_Fall_Curled | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Sanawar_Testing_7_22_26_Fast_Sit | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Sanawar_Testing_7_22_26_Lying_legs_straight | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Sanawar_Testing_7_22_26_Normal_Fall_1 | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Sanawar_Testing_7_22_26_Off_axis | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Sanawar_Testing_7_22_26_Standing_3 | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Sanawar_Testing_7_22_26_normal | 2 | 2/2 (100.0%) | 0/2 (0.0%) | 0/2 (0.0%) | 0/2 (0.0%) |
| Sanawar_Testing_7_22_26_old | 3 | 3/3 (100.0%) | 0/3 (0.0%) | 0/3 (0.0%) | 0/3 (0.0%) |
| Sanawar_Testing_7_25_26_Fall_and_lie | 5 | 5/5 (100.0%) | 0/5 (0.0%) | 0/5 (0.0%) | 0/5 (0.0%) |
| Sanawar_Testing_7_25_26_Far_fall | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| Sanawar_Testing_7_25_26_Slow_fall | 4 | 4/4 (100.0%) | 0/4 (0.0%) | 0/4 (0.0%) | 0/4 (0.0%) |
| Sitting_Dim_HM | 51 | 7/51 (13.7%) | 44/51 (86.3%) | 0/51 (0.0%) | 0/51 (0.0%) |
| Standing_Walking_Dim_HM | 34 | 19/34 (55.9%) | 14/34 (41.2%) | 0/34 (0.0%) | 1/34 (2.9%) |
| TV_Lounge_Fallll | 3 | 0/3 (0.0%) | 0/3 (0.0%) | 0/3 (0.0%) | 3/3 (100.0%) |
| empty_top_bedroom | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| ALL | 120 | 55/120 (45.8%) | 58/120 (48.3%) | 0/120 (0.0%) | 7/120 (5.8%) |

**AI verdicts by provenance**

| group | n | OK | BAD_BOX | MISSING_PERSON_BOX | UNCLEAR |
|---|---|---|---|---|---|
| MediaPipe-derived | 104 | 45/104 (43.3%) | 58/104 (55.8%) | 0/104 (0.0%) | 1/104 (1.0%) |
| empty-room (no person by construction) | 1 | 1/1 (100.0%) | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| hand-drawn (round5) | 3 | 0/3 (0.0%) | 0/3 (0.0%) | 0/3 (0.0%) | 3/3 (100.0%) |
| hand-drawn (round6) | 6 | 3/6 (50.0%) | 0/6 (0.0%) | 0/6 (0.0%) | 3/6 (50.0%) |
| hand-drawn (round6_patch) | 6 | 6/6 (100.0%) | 0/6 (0.0%) | 0/6 (0.0%) | 0/6 (0.0%) |
| ALL | 120 | 55/120 (45.8%) | 58/120 (48.3%) | 0/120 (0.0%) | 7/120 (5.8%) |

**AI verdicts by darkness bucket**

| group | n | OK | BAD_BOX | MISSING_PERSON_BOX | UNCLEAR |
|---|---|---|---|---|---|
| bright | 18 | 15/18 (83.3%) | 0/18 (0.0%) | 0/18 (0.0%) | 3/18 (16.7%) |
| dark | 88 | 26/88 (29.5%) | 58/88 (65.9%) | 0/88 (0.0%) | 4/88 (4.5%) |
| mid | 14 | 14/14 (100.0%) | 0/14 (0.0%) | 0/14 (0.0%) | 0/14 (0.0%) |
| ALL | 120 | 55/120 (45.8%) | 58/120 (48.3%) | 0/120 (0.0%) | 7/120 (5.8%) |

Only the 40 'random' rows estimate a rate for the whole checked population: AI BAD_BOX 6/40 (15.0%), UNCLEAR 2/40 (5.0%). The other rows were chosen because something looked off and say nothing about overall rates.

**Exploratory (defined after looking, so not a test):** the AI-flagged 'box on the bedding' boxes in the two fixed-camera Dim_HM clips occupy one small image region. Counting own frames whose person box falls inside that region (envelope cx/cy/w/h = [[0.429, 0.575], [0.687, 0.811], [0.067, 0.426], [0.115, 0.323]]):

| clip | provenance | frames | frames with a person box in the region |
|---|---|---|---|
| Sitting_Dim_HM | MediaPipe-derived | 650 | 258/650 (39.7%) |
| Standing_Walking_Dim_HM | MediaPipe-derived | 575 | 85/575 (14.8%) |
| Sitting_Dim_HM / Standing_Walking_Dim_HM | hand-drawn (round6_patch) | 384 | 0 (no row in raw/bedding_signature.json) |

The region test is only meaningful inside those two clips (same fixed camera). Hits in other clips are a different room and camera and are listed in raw/bedding_signature.json only for completeness. The region is a box envelope, so it can also contain a correct box of a person who really is lying there; it is a pointer, not a count of errors.

## (e) Reading

Plain-language reading (written by Claude after the run; numbers quoted from the tables above; the AI verdicts are unverified).

**Where the problems are.** Almost all the evidence points at one place: the **MediaPipe-derived person boxes in the two dim,
fixed-camera clips `Sitting_Dim_HM` and `Standing_Walking_Dim_HM`**.
- Detector flags: Sitting_Dim_HM 19.3% SUSPECTED_MISSING / 48.8% SUSPECTED_PHANTOM (n=861); Standing_Walking_Dim_HM 9.4% / 20.7% (n=748).
  Most bright own-footage clips show 0 flags of either kind.
- AI review: 44/51 sampled Sitting_Dim_HM frames and 14/34 Standing_Walking_Dim_HM frames read as BAD_BOX. **All 58 BAD_BOX
  readings are on MediaPipe-derived labels; none of the 15 sampled hand-drawn frames got one.**
- What it looks like: the person box is not missing, it is **in the wrong place**. It is a low, wide box on the bedding/pillow
  (or a box 2–3× too wide around the desk), while the person stands or sits above it, unboxed. So in those frames the real
  person is effectively unlabelled, and a patch of bedding is labelled "person".
- Exploratory count (region defined after looking, so it is a pointer, not a test): 258/650 MediaPipe-labelled Sitting_Dim_HM
  frames and 85/575 MediaPipe-labelled Standing_Walking_Dim_HM frames have a person box in that bedding region. **0 of the 384
  hand-drawn round6_patch frames from the same two clips do.** Note that the `_r1` copies double these frames in training.

**Dark vs lying vs everywhere.** The flags are concentrated, not spread evenly:
- MediaPipe-derived × dark: 19.1% SUSPECTED_MISSING (n=1,227) vs 0.2% for MediaPipe-derived × bright (n=1,261).
- In the 40 uniformly random sampled frames, the AI marked 6/40 BAD_BOX, all from the two Dim_HM clips.

Whether *lying* is a separate problem cannot be told from this data. The "wider than tall" lying proxy is flagged far more
often (15.0% vs 1.6% SUSPECTED_MISSING), but the misplaced bedding boxes are themselves wide, so the proxy is contaminated by
the same defect.

The lying/fall clips with hand-drawn labels (Bedroom_Falll, TV_Lounge_Fallll, Behind_Chair_HM, Blanket_Cover_HM) have high
PHANTOM rates (54–70% per clip). Those boxes were drawn by a person, so this mostly measures the detector failing on hard
footage, not label errors. They do raise two convention questions for a human:
- 3/3 sampled TV_Lounge_Fallll frames: the AI could not see a person inside the box even with brightening.
- 3/5 sampled Behind_Chair_HM frames: the box sits on a green chair with no visible person (fully occluded person, or mislabel?).

The Slow_fall SUSPECTED_MISSING flags that were sampled (4) are the detector firing on the person's reflection in a glass
panel; the labels looked fine. COCO was not checked (external, human-drawn). Empty-room frames: 0 detector flags in 539.

**Other findings.**
- No leakage: 0 filename or md5 overlap with eval/heldout_objects or handlabels/round6_heldout, and 0 val images md5-identical
  to a train image.
- Class order is identical in sage_classes.py and data.yaml.
- The `old` and `normal` clips appear in train twice under different session names (Hussain_Testing_7_23_26_* and
  Sanawar_Testing_7_22_26_*: 307 + 192 byte-identical frames). With the `_r1` copies, each of those frames is in train 4 times.

**How confident.**
- Fairly confident: the Dim_HM misplaced-box pattern is real. Three independent signals agree: detector disagreement, the AI's
  visual reading, and the position count. They separate cleanly by provenance (MediaPipe vs hand-drawn, same clips).
- Not established: how many frames are affected exactly. The 258 / 85 counts are a post-hoc region envelope, and the AI
  reading is at contact-sheet resolution on 120 of 5,091 checked images and is unverified.
- Weak: anything about lying-specific errors, or about the hand-drawn fall clips. The detector is unreliable exactly there.

**A connection to check, not a conclusion.** The overnight run found B (YOLO26n trained on this data) placing person boxes on
the pillow/bedding on Laying_Dim_HM. A training set that labels bedding as "person" in a dim bedroom is one plausible
cause. This audit does not test that.

### Look at these first (also in look_first.csv)

1. `own_TV_Lounge_Fallll_000360.jpg` -- TV_Lounge_Fallll (sheet idx 8): AI UNCLEAR (unverified): hand-drawn box on the sofa; person not discernible even with display brightening
2. `own_Behind_Chair_HM_001370.jpg` -- Behind_Chair_HM (sheet idx 17): AI UNCLEAR (unverified): hand-drawn person box on the green chair; no person visible (possibly a fully occluded person behind the chair, possibly a mislabel)
3. `own_Behind_Chair_HM_001300.jpg` -- Behind_Chair_HM (sheet idx 83): AI UNCLEAR (unverified): hand-drawn person box on the green chair; no person visible (possibly a fully occluded person behind the chair, possibly a mislabel)
4. `own_Standing_Walking_Dim_HM_000492.jpg` -- Standing_Walking_Dim_HM (sheet idx 86): AI UNCLEAR (unverified): dark low shape near the red box may be a crouched person; GT box beside it; cannot judge
5. `own_TV_Lounge_Fallll_000350.jpg` -- TV_Lounge_Fallll (sheet idx 97): AI UNCLEAR (unverified): hand-drawn box on the sofa; person not discernible even with display brightening
6. `own_Behind_Chair_HM_000810.jpg` -- Behind_Chair_HM (sheet idx 100): AI UNCLEAR (unverified): hand-drawn person box on the green chair; no person visible (possibly a fully occluded person behind the chair, possibly a mislabel)
7. `own_TV_Lounge_Fallll_000340.jpg` -- TV_Lounge_Fallll (sheet idx 117): AI UNCLEAR (unverified): hand-drawn box on the sofa; person not discernible even with display brightening
8. `own_Sitting_Dim_HM_001464.jpg` -- Sitting_Dim_HM (sheet idx 9): AI BAD_BOX (unverified): GT box starts below the head/upper torso of the seated person
9. `own_Standing_Walking_Dim_HM_000330.jpg` -- Standing_Walking_Dim_HM (sheet idx 25): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
10. `own_Sitting_Dim_HM_001340.jpg` -- Sitting_Dim_HM (sheet idx 19): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
11. `own_Standing_Walking_Dim_HM_001238.jpg` -- Standing_Walking_Dim_HM (sheet idx 45): AI BAD_BOX (unverified): GT box much larger than / offset from the person (includes desk/chair); IoU with the person likely < 0.5
12. `own_Sitting_Dim_HM_001438.jpg` -- Sitting_Dim_HM (sheet idx 32): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
13. `own_Standing_Walking_Dim_HM_001260.jpg` -- Standing_Walking_Dim_HM (sheet idx 47): AI BAD_BOX (unverified): GT box much larger than / offset from the person (includes desk/chair); IoU with the person likely < 0.5
14. `own_Sitting_Dim_HM_001194.jpg` -- Sitting_Dim_HM (sheet idx 35): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
15. `own_Standing_Walking_Dim_HM_000428.jpg` -- Standing_Walking_Dim_HM (sheet idx 48): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
16. `own_Sitting_Dim_HM_001480.jpg` -- Sitting_Dim_HM (sheet idx 37): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
17. `own_Standing_Walking_Dim_HM_000124.jpg` -- Standing_Walking_Dim_HM (sheet idx 49): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
18. `own_Sitting_Dim_HM_001402.jpg` -- Sitting_Dim_HM (sheet idx 41): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
19. `own_Standing_Walking_Dim_HM_000362.jpg` -- Standing_Walking_Dim_HM (sheet idx 50): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
20. `own_Sitting_Dim_HM_001366.jpg` -- Sitting_Dim_HM (sheet idx 42): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
21. `own_Standing_Walking_Dim_HM_000324.jpg` -- Standing_Walking_Dim_HM (sheet idx 57): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
22. `own_Sitting_Dim_HM_001390.jpg` -- Sitting_Dim_HM (sheet idx 43): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
23. `own_Standing_Walking_Dim_HM_001236.jpg` -- Standing_Walking_Dim_HM (sheet idx 61): AI BAD_BOX (unverified): GT box much larger than / offset from the person (includes desk/chair); IoU with the person likely < 0.5
24. `own_Sitting_Dim_HM_001404.jpg` -- Sitting_Dim_HM (sheet idx 44): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
25. `own_Standing_Walking_Dim_HM_000440.jpg` -- Standing_Walking_Dim_HM (sheet idx 63): AI BAD_BOX (unverified): GT box much larger than / offset from the person (includes desk/chair); IoU with the person likely < 0.5
26. `own_Sitting_Dim_HM_000962.jpg` -- Sitting_Dim_HM (sheet idx 46): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
27. `own_Standing_Walking_Dim_HM_000410.jpg` -- Standing_Walking_Dim_HM (sheet idx 67): AI BAD_BOX (unverified): GT box much larger than / offset from the person (includes desk/chair); IoU with the person likely < 0.5
28. `own_Sitting_Dim_HM_001360.jpg` -- Sitting_Dim_HM (sheet idx 51): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
29. `own_Standing_Walking_Dim_HM_000446.jpg` -- Standing_Walking_Dim_HM (sheet idx 70): AI BAD_BOX (unverified): GT box much larger than / offset from the person (includes desk/chair); IoU with the person likely < 0.5
30. `own_Sitting_Dim_HM_000966.jpg` -- Sitting_Dim_HM (sheet idx 54): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
31. `own_Standing_Walking_Dim_HM_000438.jpg` -- Standing_Walking_Dim_HM (sheet idx 73): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
32. `own_Sitting_Dim_HM_001446.jpg` -- Sitting_Dim_HM (sheet idx 55): AI BAD_BOX (unverified): GT person box sits low on the bedding/pillow/desk area while the visible person is elsewhere (standing/sitting above it); person itself not boxed
33. `own_Sanawar_Testing_7_25_26_Backward_fall_000092.jpg` -- Sanawar_Testing_7_25_26_Backward_fall: not in the sample; SUSPECTED_MISSING at conf 0.93 outside the Dim_HM clips
34. `own_Sanawar_Testing_7_22_26_Normal_Fall_1_000124.jpg` -- Sanawar_Testing_7_22_26_Normal_Fall_1: not in the sample; SUSPECTED_MISSING at conf 0.90 outside the Dim_HM clips
35. `own_Sanawar_Testing_7_25_26_Slow_fall_000094.jpg` -- Sanawar_Testing_7_25_26_Slow_fall: not in the sample; SUSPECTED_MISSING at conf 0.87 outside the Dim_HM clips
36. `own_Sanawar_Testing_7_22_26_Normal_Fall_1_000126.jpg` -- Sanawar_Testing_7_22_26_Normal_Fall_1: not in the sample; SUSPECTED_MISSING at conf 0.87 outside the Dim_HM clips
37. `own_Sanawar_Testing_7_25_26_Slow_fall_000006.jpg` -- Sanawar_Testing_7_25_26_Slow_fall: not in the sample; SUSPECTED_MISSING at conf 0.85 outside the Dim_HM clips
38. `own_Sanawar_Testing_7_25_26_Slow_fall_000010.jpg` -- Sanawar_Testing_7_25_26_Slow_fall: not in the sample; SUSPECTED_MISSING at conf 0.85 outside the Dim_HM clips
39. `own_Sanawar_Testing_7_25_26_Slow_fall_000038.jpg` -- Sanawar_Testing_7_25_26_Slow_fall: not in the sample; SUSPECTED_MISSING at conf 0.84 outside the Dim_HM clips
40. `own_Sanawar_Testing_7_25_26_Slow_fall_000014.jpg` -- Sanawar_Testing_7_25_26_Slow_fall: not in the sample; SUSPECTED_MISSING at conf 0.84 outside the Dim_HM clips

Decisions: DECISIONS.md. Per-image data: train_images.csv. Raw: raw/.

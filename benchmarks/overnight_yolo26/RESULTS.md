# Overnight YOLO26 experiments -- RESULTS

Generated 2026-10-10 06:46 from files in benchmarks/overnight_yolo26/ only. Eval set named on every number.

## Summary

- Stages done: 11; not done: S6_train_C (skipped).
- **READ-ONLY RULE BROKEN (my error):** Ultralytics overwrote datasets/sage_merged_v7/labels/train.cache and val.cache (derived label-scan caches, not labels/images); the junction workaround did not prevent it. Now: train.cache 4064610 B, mtime 2026-10-10 02:57; val.cache 690807 B, mtime 2026-10-10 02:14. See DECISIONS.md.
- Control A reproduced on every reference value (eval/heldout_objects 58/93 1 FP; round6_heldout chair/bed/person; empty-room 0/4101).
- Person @IoU0.5, reserved388_partial: A 107/249 (0.430) vs B 109/249 (0.438).
- Person @IoU0.5, round6_heldout: A 50/226 (0.221) vs B 50/226 (0.221).
- **Non-overlapping 95% CIs vs A (person @IoU0.5, conf 0.4):** reserved388_partial: v6 145/249 vs A 107/249; reserved388_partial: stock_yolo26s 153/249 vs A 107/249. Where v6 beats A this CONTRADICTS v7_results.md ('v7 detects exactly the same fall frames v5 and v6 did'), which was measured on the as-stored set with sideways Bedroom_Fall frames.
- C: C SKIPPED: recall_within_0.02_on_each_set (raw/gate.json).
- VERDICT: enhancement is NOT worthwhile -- no single variant helps >= 2 of ['A_v7', 'B_yolo26n_30ep', 'stock_yolo26n'] under the pre-registered rule.
- Pose v2 (corrected): MediaPipe falls 23/37, ADL false alarms 2/27; most fall TPs: yolo26s-pose@0.3 30/37, ADL FA 4/27. With ~37 fall clips, a few clips' difference is noise.

Full detail follows; raw JSON/CSV in raw/.

## 1. What finished / failed / skipped

| stage | status | start | end | wall min | note |
|---|---|---|---|---|---|
| S0_preflight | done | 02:09:43 | 02:10:58 | 1.2 |  |
| S1_control | done | 02:10:58 | 02:14:58 | 4.0 |  |
| S2_stock | done | 02:14:58 | 02:25:28 | 10.5 |  |
| S3_enhance_A_stock | done | 02:25:28 | 02:31:28 | 6.0 |  |
| S4a_pose_score | done | 02:31:28 | 02:33:13 | 1.8 |  |
| S4b_pose_speed | done | 02:33:13 | 02:56:58 | 23.8 |  |
| S5_train_B | done | 02:56:58 | 06:28:59 | 212.0 | succeeded on attempt fresh |
| S5_train_B__attempt1_fresh | done | 02:56:58 | 06:28:59 | 212.0 |  |
| S5_score_B | done | 06:28:59 | 06:31:59 | 3.0 |  |
| S6_gate | done | 06:31:59 | 06:32:14 | 0.2 |  |
| S6_train_C | skipped |  |  |  | C SKIPPED: recall_within_0.02_on_each_set |
| S6_enhance_BC | done | 06:32:14 | 06:35:14 | 3.0 |  |
| S7_report | done | 06:35:14 | 06:35:29 | 0.2 |  |

Driver launches: 2026-10-10T02:09:43. Run start 2026-10-10 01:47; report generated 2026-10-10 06:46 (5.00 h after start).

## 2. Control reproduction (A = models/yolov8n_sage_merged_v7.pt, conf 0.4, imgsz 640)

**Control reproduced**: every reference value for A matched within 1 person box and 0.02 recall.

| check | measured | reference | ok |
|---|---|---|---|
| A heldout_objects person @IoU0.5 | 58/93 | 58/93 | yes |
| A heldout_objects person FP @IoU0.5 | 1 | 1 | yes |
| A heldout_objects With_people_TV_Lounge_1_Fall @IoU0.5 | 6/18 | 6/18 | yes |
| A heldout_objects With_people_Bedroom_Fall @IoU0.5 | 0/20 | 0/20 | yes |
| A round6_heldout person @IoU0.5 | 50/226 | 50/226 | yes |
| A round6_heldout person FP @IoU0.5 | 0 | 0 | yes |
| A round6_heldout chair recall @IoU0.5 | 0.7358916478555305 (326/443) | 0.74 | yes |
| A round6_heldout bed recall @IoU0.5 | 0.4899328859060403 (146/298) | 0.49 | yes |
| A empty-room FP rate (Reserved/Empty, every frame) | 0.00% of 4101 frames | 0.00% of 4101 frames | yes |
| v6 reserved388 With_people_Bedroom_Walk @IoU0.3 | 14/14 FP 0 | 1.00 of 14 (~14 boxes; FP 0) | yes |
| v6 reserved388 With_people_TV_Lounge_1_Walk @IoU0.3 | 1/1 FP 0 | 1.00 of 1 (~1 boxes; FP 0) | yes |
| v6 reserved388 With_people_TV_Lounge_1_Sit @IoU0.3 | 16/16 FP 0 | 1.00 of 16 (~16 boxes; FP 0) | yes |
| v6 reserved388 With_people_people @IoU0.3 | NOT AVAILABLE (source clip missing) | 1.00 of 18 | n/a |
| v6 reserved388 With_people_Bedroom_Sit @IoU0.3 | 24/24 FP 0 | 1.00 of 24 (~24 boxes; FP 0) | yes |
| v6 reserved388 With_people_people_(2) @IoU0.3 | NOT AVAILABLE (source clip missing) | 0.94 of 32 | n/a |
| v6 reserved388 With_people_Bedroom_Fall @IoU0.3 | 59/62 FP 0 | 0.95 of 62 (~59 boxes; FP 0) | yes |
| v6 reserved388 With_people_TV_Lounge_2_Fall @IoU0.3 | 16/35 FP 0 | 0.46 of 35 (~16 boxes; FP 0) | yes |
| v6 reserved388 With_people_TV_Lounge_2_Fall2 @IoU0.3 | NOT AVAILABLE (source clip missing) | 0.41 of 41 | n/a |
| v6 reserved388 With_people_TV_Lounge_1_Fall2 @IoU0.3 | NOT AVAILABLE (source clip missing) | 0.31 of 48 | n/a |
| v6 reserved388 With_people_TV_Lounge_1_Fall @IoU0.3 | 17/97 FP 3 | 0.18 of 97 (~17 boxes; FP 3) | yes |

Harness equality check (A, eval/heldout_objects, person, IoU 0.5): original `score_loaded_model` {'tp': 58, 'fp': 1, 'fn': 35} vs this harness {'tp': 58, 'fp': 1, 'fn': 35} -> IDENTICAL.

**Measurement artifact found in eval/heldout_objects:** clip(s) ['With_people_Bedroom_Fall'] are stored as the raw, unrotated (sideways) frame while their hand-drawn labels fit the upright frame (registered rotation in src/detection/footage_rotation.py). The long-standing reference 'Bedroom_Fall 0/20 for v5, v6, v7' therefore measures a sideways image against upright boxes, not the model. The `heldout_objects_rotfix` set below is the same 200 frames with only those images rotated; the as-stored set is kept so the reference can be reproduced.

**388-box reserved set**: labels found (eval/heldout_objects/labels, 569 files, 388 person boxes), images for only 319 frames / 249 person boxes obtainable. Missing source clips: With_people_TV_Lounge_1_Fall2, With_people_TV_Lounge_2_Fall2, With_people_people, With_people_people_(2). Re-extraction check vs the existing images: n=100, max mean |diff| = 0.48 grey levels. v6 per-clip reproduction on the partial set: OK (rows 'v6 reserved388 ...' above). The full-set reference (v6 0.577 @0.5 / 0.585 @0.3 on 388 boxes) cannot be checked.

A re-validated now on OUT/data_v7_fixed.yaml (2,610 val images): mAP50 0.5212, mAP50-95 0.3850.
- v6 388-set reference overall (0.577 @0.5 = 224/388, 0.585 @0.3 = 227/388) cannot be checked directly: 4 of 11 source clips are not on disk. Only the per-clip rows above are checkable.

## 3. Person detection (conf 0.4 unless stated, imgsz 640; TP/FP/FN, recall with 95% Wilson CI)

Every number below is tied to its eval set; do not compare across sets. Frames within a clip are correlated, so the Wilson intervals (which assume independent boxes) are if anything too narrow. With 93-249 boxes per set, recall differences under roughly 0.08-0.10 are not distinguishable from noise.

### heldout_objects -- eval/heldout_objects as stored (Bedroom_Fall frames sideways)

| model | conf | IoU | TP | FP | FN | recall | 95% CI | precision | Δrecall vs A |
|---|---|---|---|---|---|---|---|---|---|
| A_v7 | 0.4 | 0.5 | 58 | 1 | 35 | 0.624 | [0.52, 0.72] | 0.983 |  |
| v6 | 0.4 | 0.5 | 60 | 4 | 33 | 0.645 | [0.54, 0.73] | 0.938 | +0.022 |
| B_yolo26n_30ep | 0.4 | 0.5 | 52 | 1 | 41 | 0.559 | [0.46, 0.66] | 0.981 | -0.065 |
| stock_yolo26n | 0.4 | 0.5 | 59 | 5 | 34 | 0.634 | [0.53, 0.73] | 0.922 | +0.011 |
| stock_yolo26s | 0.4 | 0.5 | 71 | 3 | 22 | 0.763 | [0.67, 0.84] | 0.959 | +0.140 |
| stock_yolov8n | 0.4 | 0.5 | 63 | 5 | 30 | 0.677 | [0.58, 0.76] | 0.926 | +0.054 |
| stock_yolo26n | 0.25 | 0.5 | 65 | 18 | 28 | 0.699 | [0.60, 0.78] | 0.783 | +0.075 |
| stock_yolo26s | 0.25 | 0.5 | 71 | 8 | 22 | 0.763 | [0.67, 0.84] | 0.899 | +0.140 |
| stock_yolov8n | 0.25 | 0.5 | 68 | 19 | 25 | 0.731 | [0.63, 0.81] | 0.782 | +0.108 |
| A_v7 | 0.4 | 0.3 | 58 | 1 | 35 | 0.624 | [0.52, 0.72] | 0.983 |  |
| v6 | 0.4 | 0.3 | 61 | 3 | 32 | 0.656 | [0.55, 0.74] | 0.953 | +0.032 |
| B_yolo26n_30ep | 0.4 | 0.3 | 52 | 1 | 41 | 0.559 | [0.46, 0.66] | 0.981 | -0.065 |
| stock_yolo26n | 0.4 | 0.3 | 59 | 5 | 34 | 0.634 | [0.53, 0.73] | 0.922 | +0.011 |
| stock_yolo26s | 0.4 | 0.3 | 71 | 3 | 22 | 0.763 | [0.67, 0.84] | 0.959 | +0.140 |
| stock_yolov8n | 0.4 | 0.3 | 63 | 5 | 30 | 0.677 | [0.58, 0.76] | 0.926 | +0.054 |
| stock_yolo26n | 0.25 | 0.3 | 65 | 18 | 28 | 0.699 | [0.60, 0.78] | 0.783 | +0.075 |
| stock_yolo26s | 0.25 | 0.3 | 71 | 8 | 22 | 0.763 | [0.67, 0.84] | 0.899 | +0.140 |
| stock_yolov8n | 0.25 | 0.3 | 68 | 19 | 25 | 0.731 | [0.63, 0.81] | 0.782 | +0.108 |

### heldout_objects_rotfix -- same frames, Bedroom_Fall rotated upright (OUT copy)

| model | conf | IoU | TP | FP | FN | recall | 95% CI | precision | Δrecall vs A |
|---|---|---|---|---|---|---|---|---|---|
| A_v7 | 0.4 | 0.5 | 66 | 1 | 27 | 0.710 | [0.61, 0.79] | 0.985 |  |
| v6 | 0.4 | 0.5 | 79 | 3 | 14 | 0.849 | [0.76, 0.91] | 0.963 | +0.140 |
| B_yolo26n_30ep | 0.4 | 0.5 | 63 | 1 | 30 | 0.677 | [0.58, 0.76] | 0.984 | -0.032 |
| stock_yolo26n | 0.4 | 0.5 | 66 | 2 | 27 | 0.710 | [0.61, 0.79] | 0.971 | +0.000 |
| stock_yolo26s | 0.4 | 0.5 | 81 | 2 | 12 | 0.871 | [0.79, 0.92] | 0.976 | +0.161 |
| stock_yolov8n | 0.4 | 0.5 | 70 | 4 | 23 | 0.753 | [0.66, 0.83] | 0.946 | +0.043 |
| stock_yolo26n | 0.25 | 0.5 | 72 | 6 | 21 | 0.774 | [0.68, 0.85] | 0.923 | +0.065 |
| stock_yolo26s | 0.25 | 0.5 | 88 | 3 | 5 | 0.946 | [0.88, 0.98] | 0.967 | +0.237 |
| stock_yolov8n | 0.25 | 0.5 | 75 | 8 | 18 | 0.806 | [0.71, 0.87] | 0.904 | +0.097 |
| A_v7 | 0.4 | 0.3 | 66 | 1 | 27 | 0.710 | [0.61, 0.79] | 0.985 |  |
| v6 | 0.4 | 0.3 | 80 | 2 | 13 | 0.860 | [0.78, 0.92] | 0.976 | +0.151 |
| B_yolo26n_30ep | 0.4 | 0.3 | 63 | 1 | 30 | 0.677 | [0.58, 0.76] | 0.984 | -0.032 |
| stock_yolo26n | 0.4 | 0.3 | 66 | 2 | 27 | 0.710 | [0.61, 0.79] | 0.971 | +0.000 |
| stock_yolo26s | 0.4 | 0.3 | 81 | 2 | 12 | 0.871 | [0.79, 0.92] | 0.976 | +0.161 |
| stock_yolov8n | 0.4 | 0.3 | 70 | 4 | 23 | 0.753 | [0.66, 0.83] | 0.946 | +0.043 |
| stock_yolo26n | 0.25 | 0.3 | 72 | 6 | 21 | 0.774 | [0.68, 0.85] | 0.923 | +0.065 |
| stock_yolo26s | 0.25 | 0.3 | 88 | 3 | 5 | 0.946 | [0.88, 0.98] | 0.967 | +0.237 |
| stock_yolov8n | 0.25 | 0.3 | 75 | 8 | 18 | 0.806 | [0.71, 0.87] | 0.904 | +0.097 |

### reserved388_partial -- 388-box labels, 7/11 clips with obtainable images

| model | conf | IoU | TP | FP | FN | recall | 95% CI | precision | Δrecall vs A |
|---|---|---|---|---|---|---|---|---|---|
| A_v7 | 0.4 | 0.5 | 107 | 3 | 142 | 0.430 | [0.37, 0.49] | 0.973 |  |
| v6 | 0.4 | 0.5 | 145 | 5 | 104 | 0.582 | [0.52, 0.64] | 0.967 | +0.153 |
| B_yolo26n_30ep | 0.4 | 0.5 | 109 | 2 | 140 | 0.438 | [0.38, 0.50] | 0.982 | +0.008 |
| stock_yolo26n | 0.4 | 0.5 | 128 | 3 | 121 | 0.514 | [0.45, 0.58] | 0.977 | +0.084 |
| stock_yolo26s | 0.4 | 0.5 | 153 | 3 | 96 | 0.614 | [0.55, 0.67] | 0.981 | +0.185 |
| stock_yolov8n | 0.4 | 0.5 | 118 | 7 | 131 | 0.474 | [0.41, 0.54] | 0.944 | +0.044 |
| stock_yolo26n | 0.25 | 0.5 | 135 | 9 | 114 | 0.542 | [0.48, 0.60] | 0.938 | +0.112 |
| stock_yolo26s | 0.25 | 0.5 | 180 | 4 | 69 | 0.723 | [0.66, 0.77] | 0.978 | +0.293 |
| stock_yolov8n | 0.25 | 0.5 | 137 | 11 | 112 | 0.550 | [0.49, 0.61] | 0.926 | +0.120 |
| A_v7 | 0.4 | 0.3 | 109 | 1 | 140 | 0.438 | [0.38, 0.50] | 0.991 |  |
| v6 | 0.4 | 0.3 | 147 | 3 | 102 | 0.590 | [0.53, 0.65] | 0.980 | +0.153 |
| B_yolo26n_30ep | 0.4 | 0.3 | 109 | 2 | 140 | 0.438 | [0.38, 0.50] | 0.982 | +0.000 |
| stock_yolo26n | 0.4 | 0.3 | 128 | 3 | 121 | 0.514 | [0.45, 0.58] | 0.977 | +0.076 |
| stock_yolo26s | 0.4 | 0.3 | 153 | 3 | 96 | 0.614 | [0.55, 0.67] | 0.981 | +0.177 |
| stock_yolov8n | 0.4 | 0.3 | 118 | 7 | 131 | 0.474 | [0.41, 0.54] | 0.944 | +0.036 |
| stock_yolo26n | 0.25 | 0.3 | 135 | 9 | 114 | 0.542 | [0.48, 0.60] | 0.938 | +0.104 |
| stock_yolo26s | 0.25 | 0.3 | 180 | 4 | 69 | 0.723 | [0.66, 0.77] | 0.978 | +0.285 |
| stock_yolov8n | 0.25 | 0.3 | 137 | 11 | 112 | 0.550 | [0.49, 0.61] | 0.926 | +0.112 |

### round6_heldout -- handlabels/round6_heldout (Laying_Dim_HM + Behind_Bed_HM)

| model | conf | IoU | TP | FP | FN | recall | 95% CI | precision | Δrecall vs A |
|---|---|---|---|---|---|---|---|---|---|
| A_v7 | 0.4 | 0.5 | 50 | 0 | 176 | 0.221 | [0.17, 0.28] | 1.000 |  |
| v6 | 0.4 | 0.5 | 49 | 2 | 177 | 0.217 | [0.17, 0.28] | 0.961 | -0.004 |
| B_yolo26n_30ep | 0.4 | 0.5 | 50 | 22 | 176 | 0.221 | [0.17, 0.28] | 0.694 | +0.000 |
| stock_yolo26n | 0.4 | 0.5 | 44 | 6 | 182 | 0.195 | [0.15, 0.25] | 0.880 | -0.027 |
| stock_yolo26s | 0.4 | 0.5 | 50 | 0 | 176 | 0.221 | [0.17, 0.28] | 1.000 | +0.000 |
| stock_yolov8n | 0.4 | 0.5 | 47 | 2 | 179 | 0.208 | [0.16, 0.27] | 0.959 | -0.013 |
| stock_yolo26n | 0.25 | 0.5 | 45 | 15 | 181 | 0.199 | [0.15, 0.26] | 0.750 | -0.022 |
| stock_yolo26s | 0.25 | 0.5 | 53 | 1 | 173 | 0.235 | [0.18, 0.29] | 0.981 | +0.013 |
| stock_yolov8n | 0.25 | 0.5 | 50 | 4 | 176 | 0.221 | [0.17, 0.28] | 0.926 | +0.000 |
| A_v7 | 0.4 | 0.3 | 50 | 0 | 176 | 0.221 | [0.17, 0.28] | 1.000 |  |
| v6 | 0.4 | 0.3 | 49 | 2 | 177 | 0.217 | [0.17, 0.28] | 0.961 | -0.004 |
| B_yolo26n_30ep | 0.4 | 0.3 | 50 | 22 | 176 | 0.221 | [0.17, 0.28] | 0.694 | +0.000 |
| stock_yolo26n | 0.4 | 0.3 | 46 | 4 | 180 | 0.204 | [0.16, 0.26] | 0.920 | -0.018 |
| stock_yolo26s | 0.4 | 0.3 | 50 | 0 | 176 | 0.221 | [0.17, 0.28] | 1.000 | +0.000 |
| stock_yolov8n | 0.4 | 0.3 | 48 | 1 | 178 | 0.212 | [0.16, 0.27] | 0.980 | -0.009 |
| stock_yolo26n | 0.25 | 0.3 | 47 | 13 | 179 | 0.208 | [0.16, 0.27] | 0.783 | -0.013 |
| stock_yolo26s | 0.25 | 0.3 | 53 | 1 | 173 | 0.235 | [0.18, 0.29] | 0.981 | +0.013 |
| stock_yolov8n | 0.25 | 0.3 | 50 | 4 | 176 | 0.221 | [0.17, 0.28] | 0.926 | +0.000 |

### Empty-room person false positives (yolo_testing/Reserved/Empty, every frame, stride 1)

| model | conf | frames | FP frames | FP rate | person boxes |
|---|---|---|---|---|---|
| A_v7 | 0.4 | 4101 | 0 | 0.00% | 0 |
| v6 | 0.4 | 4101 | 0 | 0.00% | 0 |
| B_yolo26n_30ep | 0.4 | 4101 | 0 | 0.00% | 0 |
| stock_yolo26n | 0.4 | 4101 | 0 | 0.00% | 0 |
| stock_yolo26s | 0.4 | 4101 | 1 | 0.02% | 1 |
| stock_yolov8n | 0.4 | 4101 | 0 | 0.00% | 0 |
| stock_yolo26n | 0.25 | 4101 | 0 | 0.00% | 0 |
| stock_yolo26s | 0.25 | 4101 | 19 | 0.46% | 19 |
| stock_yolov8n | 0.25 | 4101 | 0 | 0.00% | 0 |

### Per-clip person recall, IoU 0.5, conf 0.4 (TP/boxes, FP)

**heldout_objects_rotfix**

| clip | A_v7 | v6 | B_yolo26n_30ep | stock_yolo26n |
|---|---|---|---|---|
| With_people_Bedroom_Fall | 8/20, 0FP | 19/20, 0FP | 11/20, 0FP | 7/20, 0FP |
| With_people_Bedroom_Sit | 21/24, 0FP | 23/24, 1FP | 20/24, 0FP | 15/24, 0FP |
| With_people_Bedroom_Walk | 14/14, 0FP | 14/14, 0FP | 14/14, 0FP | 14/14, 0FP |
| With_people_TV_Lounge_1_Fall | 6/18, 0FP | 6/18, 2FP | 4/18, 0FP | 16/18, 1FP |
| With_people_TV_Lounge_1_Sit | 16/16, 1FP | 16/16, 0FP | 13/16, 1FP | 13/16, 1FP |
| With_people_TV_Lounge_1_Walk | 1/1, 0FP | 1/1, 0FP | 1/1, 0FP | 1/1, 0FP |

**reserved388_partial**

| clip | A_v7 | v6 | B_yolo26n_30ep | stock_yolo26n |
|---|---|---|---|---|
| With_people_Bedroom_Fall | 21/62, 2FP | 58/62, 1FP | 28/62, 1FP | 21/62, 0FP |
| With_people_Bedroom_Sit | 21/24, 0FP | 23/24, 1FP | 20/24, 0FP | 15/24, 0FP |
| With_people_Bedroom_Walk | 14/14, 0FP | 14/14, 0FP | 14/14, 0FP | 14/14, 0FP |
| With_people_TV_Lounge_1_Fall | 18/97, 0FP | 17/97, 3FP | 15/97, 0FP | 50/97, 2FP |
| With_people_TV_Lounge_1_Sit | 16/16, 1FP | 16/16, 0FP | 13/16, 1FP | 13/16, 1FP |
| With_people_TV_Lounge_1_Walk | 1/1, 0FP | 1/1, 0FP | 1/1, 0FP | 1/1, 0FP |
| With_people_TV_Lounge_2_Fall | 16/35, 0FP | 16/35, 0FP | 18/35, 0FP | 14/35, 0FP |

**round6_heldout**

| clip | A_v7 | v6 | B_yolo26n_30ep | stock_yolo26n |
|---|---|---|---|---|
| Behind_Bed_HM | 48/73, 0FP | 46/73, 2FP | 50/73, 0FP | 42/73, 6FP |
| Laying_Dim_HM | 2/153, 0FP | 3/153, 0FP | 0/153, 22FP | 2/153, 0FP |

**heldout_objects**

| clip | A_v7 | v6 | B_yolo26n_30ep | stock_yolo26n |
|---|---|---|---|---|
| With_people_Bedroom_Fall | 0/20, 0FP | 0/20, 1FP | 0/20, 0FP | 0/20, 3FP |
| With_people_Bedroom_Sit | 21/24, 0FP | 23/24, 1FP | 20/24, 0FP | 15/24, 0FP |
| With_people_Bedroom_Walk | 14/14, 0FP | 14/14, 0FP | 14/14, 0FP | 14/14, 0FP |
| With_people_TV_Lounge_1_Fall | 6/18, 0FP | 6/18, 2FP | 4/18, 0FP | 16/18, 1FP |
| With_people_TV_Lounge_1_Sit | 16/16, 1FP | 16/16, 0FP | 13/16, 1FP | 13/16, 1FP |
| With_people_TV_Lounge_1_Walk | 1/1, 0FP | 1/1, 0FP | 1/1, 0FP | 1/1, 0FP |

### Other classes on round6_heldout (SAGE models only; stock COCO models are scored on person only)

| model | IoU | class | TP | FP | FN | recall | precision |
|---|---|---|---|---|---|---|---|
| A_v7 | 0.5 | chair | 326 | 2 | 117 | 0.736 | 0.994 |
| A_v7 | 0.5 | bed | 146 | 0 | 152 | 0.490 | 1.000 |
| A_v7 | 0.3 | chair | 327 | 1 | 116 | 0.738 | 0.997 |
| A_v7 | 0.3 | bed | 146 | 0 | 152 | 0.490 | 1.000 |
| v6 | 0.5 | chair | 49 | 5 | 394 | 0.111 | 0.907 |
| v6 | 0.5 | bed | 2 | 0 | 296 | 0.007 | 1.000 |
| v6 | 0.5 | refrigerator | 0 | 76 | 0 | -- | 0.000 |
| v6 | 0.3 | chair | 50 | 4 | 393 | 0.113 | 0.926 |
| v6 | 0.3 | bed | 2 | 0 | 296 | 0.007 | 1.000 |
| v6 | 0.3 | refrigerator | 0 | 76 | 0 | -- | 0.000 |
| B_yolo26n_30ep | 0.5 | chair | 346 | 2 | 97 | 0.781 | 0.994 |
| B_yolo26n_30ep | 0.5 | bed | 146 | 0 | 152 | 0.490 | 1.000 |
| B_yolo26n_30ep | 0.3 | chair | 347 | 1 | 96 | 0.783 | 0.997 |
| B_yolo26n_30ep | 0.3 | bed | 146 | 0 | 152 | 0.490 | 1.000 |

## 4. Training comparison (13-class val split of sage_merged_v7, 2,610 images)

| model | base | epochs run / set | patience | early-stopped | best epoch (mAP50-95) | best mAP50-95 (training log) | mAP50 at best | mean s/epoch | median s/epoch | re-val mAP50 | re-val mAP50-95 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A (v7) | yolov8n.pt | 30/30 | 10 | False | 29 | 0.3854 | 0.5233 | 400 | 413 | 0.5212 | 0.3850 |
| B_yolo26n_30ep | yolo26n.pt | 30/30 | 10 | False | 29 | 0.3918 | 0.5257 | 421 | 417 | 0.5258 | 0.3920 |
| C_yolo26n_50ep | yolo26n.pt | not run | | | | | | | | | |

s/epoch for A comes from its results.csv (cumulative `time` column, includes validation); for B/C from epoch-start -> fit-epoch-end callbacks (also includes validation). Same machine, same dataset, workers 0, batch 16 unless an attempt below says otherwise.

- B_yolo26n_30ep attempts: `[{"name": "B_yolo26n_30ep", "status": "done", "resume": null, "batch_override": null, "optimizer_used": "AdamW", "lr0_used": 0.000588, "dropped_keys_not_accepted": [], "changed_vs_control": {"model": ["models/yolov8n.pt", null], "data": ["datasets/sage_merged_v7/data.yaml", "D:\\FYP\\PROJECT FILES\\fatima\\benchmarks\\overnight_yolo26\\data_v7_fixed.yaml"], "epochs": [1, 30], "project": ["C:\\University\\FYP\\fatima\\fatima\\runs\\detect", "D:\\FYP\\PROJECT FILES\\fatima\\benchmarks\\overnight_yolo26\\runs"], "name": ["v7_1epoch_benchmark2", "B_yolo26n_30ep"]}, "error": null}]`

## 5. Dark-frame enhancement (pre-registered rule)

Dark = bottom third of mean-luma (Y of YCrCb) per eval set, bright = top third, fixed in preflight before any enhancement result. Rule: a variant *helps* a model iff pooled dark-subset person recall @IoU0.5 rises >= 0.05 absolute vs no enhancement, while pooled bright-subset recall drops <= 0.02 and overall precision drops <= 0.03. 'Enhancement is worthwhile' iff one variant helps >= 2 of the 3 models (A, B, and C -- or stock yolo26n if C does not exist). Pooled = reserved388_partial + round6_heldout (disjoint, correctly oriented).

| set | dark luma <= | bright luma >= | frames | dark frames | bright frames |
|---|---|---|---|---|---|
| heldout_objects | 133.7 | 144.0 | 200 | 67 | 67 |
| heldout_objects_rotfix | 133.7 | 144.0 | 200 | 67 | 67 |
| reserved388_partial | 133.7 | 141.0 | 319 | 107 | 107 |
| round6_heldout | 65.3 | 143.0 | 298 | 100 | 100 |

| model | variant | dark recall (TP/n) | Δdark | bright recall (TP/n) | Δbright | precision (all) | Δprec | helps? | dark underpowered (<30 boxes)? |
|---|---|---|---|---|---|---|---|---|---|
| A_v7 | none | 0.245 (40/163) | +0.000 | 0.302 (39/129) | +0.000 | 0.981 | +0.000 | no | no |
| A_v7 | gamma0.6 | 0.239 (39/163) | -0.006 | 0.302 (39/129) | +0.000 | 0.951 | -0.031 | no | no |
| A_v7 | gamma0.5 | 0.239 (39/163) | -0.006 | 0.302 (39/129) | +0.000 | 0.932 | -0.049 | no | no |
| A_v7 | clahe | 0.227 (37/163) | -0.018 | 0.302 (39/129) | +0.000 | 0.945 | -0.036 | no | no |
| A_v7 | gamma0.6+clahe | 0.227 (37/163) | -0.018 | 0.302 (39/129) | +0.000 | 0.927 | -0.054 | no | no |
| B_yolo26n_30ep | none | 0.239 (39/163) | +0.000 | 0.271 (35/129) | +0.000 | 0.869 | +0.000 | no | no |
| B_yolo26n_30ep | gamma0.6 | 0.190 (31/163) | -0.049 | 0.287 (37/129) | +0.016 | 0.870 | +0.001 | no | no |
| B_yolo26n_30ep | gamma0.5 | 0.166 (27/163) | -0.074 | 0.295 (38/129) | +0.023 | 0.960 | +0.091 | no | no |
| B_yolo26n_30ep | clahe | 0.227 (37/163) | -0.012 | 0.279 (36/129) | +0.008 | 0.869 | +0.000 | no | no |
| B_yolo26n_30ep | gamma0.6+clahe | 0.178 (29/163) | -0.061 | 0.271 (35/129) | +0.000 | 0.816 | -0.053 | no | no |
| stock_yolo26n | none | 0.227 (37/163) | +0.000 | 0.527 (68/129) | +0.000 | 0.950 | +0.000 | no | no |
| stock_yolo26n | gamma0.6 | 0.190 (31/163) | -0.037 | 0.318 (41/129) | -0.209 | 0.971 | +0.021 | no | no |
| stock_yolo26n | gamma0.5 | 0.172 (28/163) | -0.055 | 0.295 (38/129) | -0.233 | 0.955 | +0.004 | no | no |
| stock_yolo26n | clahe | 0.227 (37/163) | +0.000 | 0.488 (63/129) | -0.039 | 0.938 | -0.013 | no | no |
| stock_yolo26n | gamma0.6+clahe | 0.202 (33/163) | -0.025 | 0.302 (39/129) | -0.225 | 0.944 | -0.007 | no | no |

**VERDICT: enhancement is NOT worthwhile -- no single variant helps >= 2 of ['A_v7', 'B_yolo26n_30ep', 'stock_yolo26n'] under the pre-registered rule.**

Per-set (not pooled) dark-subset recall @IoU0.5, for transparency:

| model | set | variant | dark TP/n | bright TP/n |
|---|---|---|---|---|
| A_v7 | heldout_objects | none | 18/20 | 23/35 |
| A_v7 | heldout_objects | gamma0.6 | 17/20 | 23/35 |
| A_v7 | heldout_objects | gamma0.5 | 17/20 | 23/35 |
| A_v7 | heldout_objects | clahe | 17/20 | 23/35 |
| A_v7 | heldout_objects | gamma0.6+clahe | 17/20 | 23/35 |
| A_v7 | heldout_objects_rotfix | none | 18/20 | 23/35 |
| A_v7 | heldout_objects_rotfix | gamma0.6 | 17/20 | 23/35 |
| A_v7 | heldout_objects_rotfix | gamma0.5 | 17/20 | 23/35 |
| A_v7 | heldout_objects_rotfix | clahe | 17/20 | 23/35 |
| A_v7 | heldout_objects_rotfix | gamma0.6+clahe | 17/20 | 23/35 |
| A_v7 | reserved388_partial | none | 38/63 | 30/101 |
| A_v7 | reserved388_partial | gamma0.6 | 36/63 | 30/101 |
| A_v7 | reserved388_partial | gamma0.5 | 36/63 | 30/101 |
| A_v7 | reserved388_partial | clahe | 37/63 | 30/101 |
| A_v7 | reserved388_partial | gamma0.6+clahe | 36/63 | 30/101 |
| A_v7 | round6_heldout | none | 2/100 | 9/28 |
| A_v7 | round6_heldout | gamma0.6 | 3/100 | 9/28 |
| A_v7 | round6_heldout | gamma0.5 | 3/100 | 9/28 |
| A_v7 | round6_heldout | clahe | 0/100 | 9/28 |
| A_v7 | round6_heldout | gamma0.6+clahe | 1/100 | 9/28 |
| B_yolo26n_30ep | heldout_objects | none | 17/20 | 19/35 |
| B_yolo26n_30ep | heldout_objects | gamma0.6 | 11/20 | 21/35 |
| B_yolo26n_30ep | heldout_objects | gamma0.5 | 8/20 | 22/35 |
| B_yolo26n_30ep | heldout_objects | clahe | 15/20 | 20/35 |
| B_yolo26n_30ep | heldout_objects | gamma0.6+clahe | 10/20 | 19/35 |
| B_yolo26n_30ep | heldout_objects_rotfix | none | 17/20 | 19/35 |
| B_yolo26n_30ep | heldout_objects_rotfix | gamma0.6 | 11/20 | 21/35 |
| B_yolo26n_30ep | heldout_objects_rotfix | gamma0.5 | 8/20 | 22/35 |
| B_yolo26n_30ep | heldout_objects_rotfix | clahe | 15/20 | 20/35 |
| B_yolo26n_30ep | heldout_objects_rotfix | gamma0.6+clahe | 10/20 | 19/35 |
| B_yolo26n_30ep | reserved388_partial | none | 39/63 | 25/101 |
| B_yolo26n_30ep | reserved388_partial | gamma0.6 | 31/63 | 27/101 |
| B_yolo26n_30ep | reserved388_partial | gamma0.5 | 27/63 | 28/101 |
| B_yolo26n_30ep | reserved388_partial | clahe | 37/63 | 26/101 |
| B_yolo26n_30ep | reserved388_partial | gamma0.6+clahe | 28/63 | 25/101 |
| B_yolo26n_30ep | round6_heldout | none | 0/100 | 10/28 |
| B_yolo26n_30ep | round6_heldout | gamma0.6 | 0/100 | 10/28 |
| B_yolo26n_30ep | round6_heldout | gamma0.5 | 0/100 | 10/28 |
| B_yolo26n_30ep | round6_heldout | clahe | 0/100 | 10/28 |
| B_yolo26n_30ep | round6_heldout | gamma0.6+clahe | 1/100 | 10/28 |
| stock_yolo26n | heldout_objects | none | 17/20 | 30/35 |
| stock_yolo26n | heldout_objects | gamma0.6 | 13/20 | 24/35 |
| stock_yolo26n | heldout_objects | gamma0.5 | 10/20 | 22/35 |
| stock_yolo26n | heldout_objects | clahe | 17/20 | 28/35 |
| stock_yolo26n | heldout_objects | gamma0.6+clahe | 14/20 | 23/35 |
| stock_yolo26n | heldout_objects_rotfix | none | 17/20 | 30/35 |
| stock_yolo26n | heldout_objects_rotfix | gamma0.6 | 13/20 | 24/35 |
| stock_yolo26n | heldout_objects_rotfix | gamma0.5 | 10/20 | 22/35 |
| stock_yolo26n | heldout_objects_rotfix | clahe | 17/20 | 28/35 |
| stock_yolo26n | heldout_objects_rotfix | gamma0.6+clahe | 14/20 | 23/35 |
| stock_yolo26n | reserved388_partial | none | 35/63 | 59/101 |
| stock_yolo26n | reserved388_partial | gamma0.6 | 29/63 | 33/101 |
| stock_yolo26n | reserved388_partial | gamma0.5 | 26/63 | 30/101 |
| stock_yolo26n | reserved388_partial | clahe | 35/63 | 54/101 |
| stock_yolo26n | reserved388_partial | gamma0.6+clahe | 30/63 | 31/101 |
| stock_yolo26n | round6_heldout | none | 2/100 | 9/28 |
| stock_yolo26n | round6_heldout | gamma0.6 | 2/100 | 8/28 |
| stock_yolo26n | round6_heldout | gamma0.5 | 2/100 | 8/28 |
| stock_yolo26n | round6_heldout | clahe | 2/100 | 9/28 |
| stock_yolo26n | round6_heldout | gamma0.6+clahe | 3/100 | 8/28 |

Example grids (original | gamma0.6, model A; green = hand-drawn person GT, red = model person detections (conf>=0.4)): grid_1_reserved388_partial_With_people_TV_Lounge_1_Fall_000070.jpg, grid_2_reserved388_partial_With_people_TV_Lounge_1_Fall_000080.jpg, grid_3_reserved388_partial_With_people_TV_Lounge_1_Sit_000090.jpg, grid_4_round6_heldout_Laying_Dim_HM_000010.jpg, grid_5_round6_heldout_Laying_Dim_HM_000020.jpg, grid_6_round6_heldout_Laying_Dim_HM_000030.jpg in OUT/enhance_grids/.

## 6. Pose benchmark v2 (benchmarks/pose_yolo26 cache, corrected scoring)

Re-scoring the cached keypoints with the ORIGINAL rule reproduces metrics_full.json on every clip x backend.

**Defect 1 (get_fall_window -> None when the GT has no upright segment): CONFIRMED in code** (evaluate_real_footage.get_fall_window requires a non-ignored, non-lying segment) and in data. Corrected rule, applied only when the original returns None: if the GT has a transition (ignored) segment and a lying/fall segment but no upright segment, the expected window is [start of first transition segment, end of last transition/lying segment]. Clips whose window this creates:

| clip | GT rows (start, end, label, ignore) | corrected window (frames) |
|---|---|---|
| H0802_Fall_backward_2 | 0-2s Transition (ign); 2-4s Lying | [0, 222] |
| H0802_Fall_backward_3 | 0-2s Transition (ign); 2-4s Lying | [0, 221] |
| H0802_Fall_backward_4 | 0-1.5s Transition (ign); 1.5-5s Lying | [0, 292] |
| H0802_Fall_from_chair_2 | 0-3s Transition (ign); 3-3.8s Lying | [0, 213] |
| H0802_Fall_slow_collapse | 0-4s Transition (ign); 4-7s Lying | [0, 414] |

**ORIGINAL vs CORRECTED** (fall recall = TP / fall clips; a fall clip whose only alarms are outside the window is a miss; ADL false-alarm rate = ADL clips with any alarm / ADL clips):

| backend | ORIG fall TP/clips | ORIG old-style % (TP/(TP+silent FN)) | ORIG ADL FA/clips | CORR fall TP/clips | CORR misses (silent / alarm outside) | CORR ADL FA/clips | posture acc (frame-weighted, n) |
|---|---|---|---|---|---|---|---|
| mediapipe | 18/32 = 0.562 | 0.600 | 7/32 | 23/37 = 0.622 | 12 / 2 | 2/27 = 0.074 | 0.719 (n=13796) |
| yolo26n-pose@0.3 | 19/32 = 0.594 | 0.633 | 11/32 | 24/37 = 0.649 | 11 / 2 | 6/27 = 0.222 | 0.725 (n=13796) |
| yolo26n-pose@0.5 | 19/32 = 0.594 | 0.633 | 11/32 | 24/37 = 0.649 | 11 / 2 | 6/27 = 0.222 | 0.732 (n=13796) |
| yolo26n-pose@0.7 | 22/32 = 0.688 | 0.759 | 10/32 | 27/37 = 0.730 | 7 / 3 | 5/27 = 0.185 | 0.722 (n=13796) |
| yolo26s-pose@0.3 | 25/32 = 0.781 | 0.833 | 9/32 | 30/37 = 0.811 | 5 / 2 | 4/27 = 0.148 | 0.696 (n=13796) |
| yolo26s-pose@0.5 | 23/32 = 0.719 | 0.719 | 9/32 | 28/37 = 0.757 | 9 / 0 | 4/27 = 0.148 | 0.690 (n=13796) |
| yolo26s-pose@0.7 | 22/32 = 0.688 | 0.710 | 9/32 | 27/37 = 0.730 | 9 / 1 | 4/27 = 0.148 | 0.662 (n=13796) |

**Defect 2 (inconsistent denominators): CONFIRMED.** The old summary printed e.g. MediaPipe '60.0% (18/32)': the percentage was TP/(TP+silent FN) = 0.600, while the parenthesis used all 32 fall clips (18/32 = 0.562). Fall clips whose alarm landed outside the window were dropped from the percentage's denominator but kept in the printed one. v2 uses one definition everywhere and prints the denominator with every rate.

**Defect 3 (clips at 0% for every backend):** rules fixed before looking -- GT problem (no scored frames / GT longer than video by >1 s / GT covers <50% of video / window past the end), no person detected (best backend finds a person in <50% of the relevant frames), else genuine heuristic miss.

| clip | kind | cause | evidence |
|---|---|---|---|
| H0730_Sitting_Lying_FewLandmarks | fall_missed_by_all_backends | genuine heuristic miss | best person-found 1.00 / window [112, 236]; results ['false_negative']; first alarms {'mediapipe': None, 'yolo26n-pose@0.3': None, 'yolo26n-pose@0.5': None, 'yolo26n-pose@0.7': None, 'yolo26s-pose@0.3': None, 'yolo26s-pose@0.5': None, 'yolo26s-pose@0.7': None} |
| S0722_Fast_Sit | posture_0pct_all_backends | genuine heuristic miss | best person-found 1.00 / GT Sitting; MediaPipe predicted {'Standing': 31} |
| S0722_Normal_Fall_1 | fall_missed_by_all_backends | genuine heuristic miss | best person-found 1.00 / window [30, 150]; results ['false_negative', 'false_positive']; first alarms {'mediapipe': 151, 'yolo26n-pose@0.3': None, 'yolo26n-pose@0.5': None, 'yolo26n-pose@0.7': None, 'yolo26s-pose@0.3': None, 'yolo26s-pose@0.5': None, 'yolo26s-pose@0.7': None} |
| S0725_Backward_fall | fall_missed_by_all_backends | genuine heuristic miss | best person-found 1.00 / window [36, 111]; results ['false_negative']; first alarms {'mediapipe': None, 'yolo26n-pose@0.3': None, 'yolo26n-pose@0.5': None, 'yolo26n-pose@0.7': None, 'yolo26s-pose@0.3': None, 'yolo26s-pose@0.5': None, 'yolo26s-pose@0.7': None} |
| S0807_Floor_lie | fall_missed_by_all_backends | genuine heuristic miss | best person-found 0.97 / window [225, 298]; results ['false_negative', 'false_positive']; first alarms {'mediapipe': 77, 'yolo26n-pose@0.3': None, 'yolo26n-pose@0.5': None, 'yolo26n-pose@0.7': 132, 'yolo26s-pose@0.3': 120, 'yolo26s-pose@0.5': None, 'yolo26s-pose@0.7': 124} |
| S0807_Sofa_lie | fall_missed_by_all_backends | genuine heuristic miss | best person-found 1.00 / window [255, 414]; results ['false_negative', 'false_positive']; first alarms {'mediapipe': None, 'yolo26n-pose@0.3': 196, 'yolo26n-pose@0.5': 196, 'yolo26n-pose@0.7': 196, 'yolo26s-pose@0.3': None, 'yolo26s-pose@0.5': None, 'yolo26s-pose@0.7': None} |

**Defect 4 (speed not like-for-like): CONFIRMED** -- the old table compared YOLO-GPU over all 64 clips with MediaPipe-CPU over an 8-clip subset, single run. v2: same 8 clips, same decoded frames, same machine with no other job running, warm-up (10 frames/clip excluded + 20-frame global warm-up), median of 3 repeated runs. MediaPipe ran with delegate `default = CPU (TFLite XNNPACK); no GPU delegate requested` (CPU; the Python Tasks API on Windows has no GPU delegate here). Input: identical decoded full-resolution frames (cv2.VideoCapture) fed to every backend; YOLO letterboxes internally to imgsz=640, MediaPipe resizes internally to its own input size.

| backend | device | pose ms/frame (median of rep medians) | rep medians | p95 | remap ms | heuristic ms/frame | frames/rep |
|---|---|---|---|---|---|---|---|
| mediapipe | cpu | 17.16 | 17.16, 18.19, 17.16 | 19.26 | -- | 0.399 | 2022 |
| yolo26n-pose | cuda:0 | 14.94 | 15.08, 14.85, 14.94 | 19.86 | 0.037 | 0.383 | 2022 |
| yolo26n-pose | cpu | 44.39 | 44.39, 44.32, 44.46 | 50.37 | 0.053 | 0.470 | 2022 |
| yolo26s-pose | cuda:0 | 13.99 | 14.05, 13.99, 13.97 | 18.88 | 0.038 | 0.377 | 2022 |
| yolo26s-pose | cpu | 87.88 | 87.88, 87.75, 88.07 | 96.88 | 0.055 | 0.469 | 2022 |


### Bottom line (corrected scoring)

| backend | fall TP / fall clips | fall recall 95% CI | ADL false alarms / ADL clips | ADL FA 95% CI | pose median ms (GPU) | pose median ms (CPU) |
|---|---|---|---|---|---|---|
| mediapipe | 23/37 | [0.46, 0.76] | 2/27 | [0.02, 0.23] | n/a | 17.16 |
| yolo26n-pose@0.3 | 24/37 | [0.49, 0.78] | 6/27 | [0.11, 0.41] | 14.94 | 44.39 |
| yolo26n-pose@0.5 | 24/37 | [0.49, 0.78] | 6/27 | [0.11, 0.41] | 14.94 | 44.39 |
| yolo26n-pose@0.7 | 27/37 | [0.57, 0.85] | 5/27 | [0.08, 0.37] | 14.94 | 44.39 |
| yolo26s-pose@0.3 | 30/37 | [0.66, 0.91] | 4/27 | [0.06, 0.32] | 13.99 | 87.88 |
| yolo26s-pose@0.5 | 28/37 | [0.60, 0.87] | 4/27 | [0.06, 0.32] | 13.99 | 87.88 |
| yolo26s-pose@0.7 | 27/37 | [0.57, 0.85] | 4/27 | [0.06, 0.32] | 13.99 | 87.88 |

## 7. Recommendations (derived from the tables above)

Detector, B (YOLO26n, A's recipe) vs A, person @IoU0.5 conf 0.4:

- heldout_objects: B 52/93 vs A 58/93 (Δ -0.065; FP B 1 vs A 1); 95% CIs overlap -> not distinguishable.
- heldout_objects_rotfix: B 63/93 vs A 66/93 (Δ -0.032; FP B 1 vs A 1); 95% CIs overlap -> not distinguishable.
- reserved388_partial: B 109/249 vs A 107/249 (Δ +0.008; FP B 2 vs A 3); 95% CIs overlap -> not distinguishable.
- round6_heldout: B 50/226 vs A 50/226 (Δ +0.000; FP B 22 vs A 0); 95% CIs overlap -> not distinguishable.

- Empty-room FP: A 0.00% vs B 0.00% of 4101 frames.

Model vs labels -- do B's misses fall on the same boxes as A's? (person, IoU 0.5, conf 0.4)

| set | person boxes | A misses | other model | its misses | both miss | share of A's misses also missed |
|---|---|---|---|---|---|---|
| reserved388_partial | 249 | 142 | B_yolo26n_30ep | 140 | 132 | 0.93 |
| reserved388_partial | 249 | 142 | stock_yolo26n | 121 | 108 | 0.76 |
| round6_heldout | 226 | 176 | B_yolo26n_30ep | 176 | 174 | 0.99 |
| round6_heldout | 226 | 176 | stock_yolo26n | 182 | 173 | 0.98 |
| heldout_objects_rotfix | 93 | 27 | B_yolo26n_30ep | 30 | 23 | 0.85 |
| heldout_objects_rotfix | 93 | 27 | stock_yolo26n | 27 | 16 | 0.59 |

Reading rule: if B (a different architecture trained on the same labels) misses mostly the same boxes A misses, the ceiling is more likely in the data/labels (or the frames themselves) than in the architecture. A high share is evidence for that only together with the per-clip table in section 3 showing the misses concentrate in the same clips.

### 7b. Plain-language reading (written after the run; every figure is quoted from the tables above)

**Which detector to carry forward.** B (YOLO26n, A's exact recipe) is not distinguishable from A on any person set:
Δrecall −0.065 (heldout_objects, 52 vs 58 of 93), −0.032 (rotfix, 63 vs 66 of 93), +0.008 (reserved388_partial, 109 vs 107
of 249), 0.000 (round6_heldout, 50 vs 50 of 226), with overlapping 95% CIs everywhere. B's gains are on the 13-class val
split (re-val mAP50-95 0.3920 vs 0.3850) and on chair in round6_heldout (346 vs 326 of 443). B has one concrete
regression: **22 person false positives on Laying_Dim_HM, where A has 0**. One rendered frame (Laying_Dim_HM_000430) shows the
box on the pillow/bedding beside the person, not a loose box on the person (0 TP even at IoU 0.3). That is the
dark-bedroom condition this project cares most about, so **do not switch the deployed detector from A to B on this evidence.**
C was not trained (gate failed on recall vs A on eval/heldout_objects; see raw/gate.json).

**The bigger finding is not B; it is that A (v7) is not the best person detector this run measured.** On reserved388_partial,
v6 finds 145/249 vs A's 107/249 (non-overlapping CIs). Almost all of that is Bedroom_Fall (58/62 vs 21/62). Stock
yolo26s at conf 0.4 finds 153/249 with 0.02% empty-room FP (1/4101 frames). Stock yolo26n finds 50/97 on TV_Lounge_1_Fall,
the clip earlier rounds called unsolved, where A finds 18/97 and v6 17/97. Two caveats:
(1) the v6 file records v6 going blind on the unlabelled `laying_dim.MOV`, and round6_heldout Laying_Dim_HM is ≤3/153 for each of A, v6, B and stock yolo26n
so no checkpoint wins everywhere; (2) these are 7 of 11 clips of the 388-box set, with frames correlated within clips.
The earlier claim that v7 "detects exactly the same fall frames v5 and v6 did" (v7_results.md) rested on the as-stored
heldout_objects set, whose 20 Bedroom_Fall frames are sideways. With them upright, A is 8/20 and v6 19/20.

**Model or labels?** B misses 93% of the same person boxes A misses on reserved388_partial, 99% on round6_heldout and 85% on the
rotfix set. In the per-clip table the misses sit in the same clips (Bedroom_Fall, TV_Lounge_1_Fall, Laying_Dim_HM). A second
architecture trained on the same labels reproduces the same blind spots, which points to the training data, not the
architecture. The stock models support this: stock yolo26n (not trained on SAGE data) shares only 76% of A's misses on
reserved388_partial and recovers TV_Lounge_1_Fall. So on TV_Lounge_1_Fall the frames are evidently detectable, and the
fine-tuned series loses something the COCO prior had. On Laying_Dim_HM all four per-clip-scored models (A, v6, B, stock yolo26n; stock shares 98% of A's round6 misses)
fails. That looks like a property of those frames (the darkest set: round6 dark-tercile luma ≤ 65.3) or of how they were
labelled. Look at those labels before recording more footage.

**Enhancement:** not worthwhile under the pre-registered rule. Gamma brightening lowers stock yolo26n's bright-frame recall by
0.21–0.23 and does not raise dark-frame recall for any model.

**Pose:** after fixing the fall-window and denominator defects, yolo26s-pose@0.3 has the most fall TPs (30/37, CI [0.66, 0.91])
vs MediaPipe 23/37 ([0.46, 0.76]), with 4/27 vs 2/27 ADL false alarms. The intervals overlap, so this is suggestive, not
conclusive. YOLO26-pose needs a GPU to match MediaPipe's latency (on this laptop's CPU: 87.88 ms yolo26s / 44.39 ms
yolo26n vs MediaPipe 17.16 ms; on GPU 13.99 / 14.94 ms). Every clip missed by all backends was classified a heuristic miss with a person found in
≥97% of the window, so for those clips the fall heuristic, not the keypoint source, is the limit.

**Extra hand checks from this reading:** (a) open a few Laying_Dim_HM frames with their labels; no model gets above 3/153 there,
so the labels themselves are worth a look; (b) look at B's 22 Laying_Dim_HM person boxes (raw/preds/B_yolo26n_30ep__round6_heldout__c0.4__none.json);
(c) look at stock yolo26n's TV_Lounge_1_Fall detections (50/97) and check that they are on the person.

## 8. Decisions log and things to double-check by hand

Full log: DECISIONS.md. Entries:

- [2026-10-10 02:03] Training/val use OUT/data_v7_fixed.yaml whose `path:` is OUT/dataset_view (NTFS junctions to datasets/sage_merged_v7/{images,labels}/{train,val}), not the dataset dir itself. Reason: Ultralytics would otherwise rewrite the existing labels/train.cache and val.cache (hash includes the pre-move paths), violating the read-only rule. Same files, same train/val split.
- [2026-10-10 01:50] Interpreter: .venv is broken (pyvenv.cfg points at C:\Users\DELL\...\python.exe, "No Python at ..."). Using .venv2 (Python 3.11.6, torch 2.13.0+cu126, CUDA True, RTX 4050 Laptop 6.4 GB, ultralytics 8.4.115).
- [2026-10-10 01:47] Git: created branch bench/overnight-yolo26 (from bench/yolo26-pose, working tree carried over untouched). No commits.
- [2026-10-10 01:55] eval/heldout_objects: the 20 With_people_Bedroom_Fall images are stored UNROTATED (portrait 1920x1080 HxW) while their hand-drawn labels match the upright frame (verified by drawing a label on both). The reference "Bedroom_Fall 0/20" is therefore a measurement artifact. Decision: score the set exactly as stored (to reproduce the reference) AND a copy in OUT/evalsets/held_out/heldout_objects_rotfix with only those 20 frames rotated by the registered rotation (ROTATE_90_CLOCKWISE). Both are reported as separate, named eval sets.
- [2026-10-10 02:00] 388-box reserved posture set: its 569 label files are in eval/heldout_objects/labels (per-clip person-box counts match reserved_heldout_posture_v6.md exactly: 62,24,14,97,48,16,1,35,41,18,32 = 388), but only 200 images exist. Source videos for TV_Lounge_1_Fall2, TV_Lounge_2_Fall2, people, people_(2) (139 boxes) and 4 empty clips are not on disk (searched D:\ and C:\University). Decision: build reserved388_partial = every labelled frame whose image exists or can be re-extracted from yolo_testing/Reserved with the registered rotation (319 frames, 249 person boxes, 7 of 11 clips). Re-extraction verified against the 100 overlapping existing images (max mean abs pixel diff 0.48). The full-388 v6 reference (0.577/0.585) cannot be checked; v6 per-clip IoU-0.3 rates are checked instead.
- [2026-10-10 02:05] Dark/bright definition fixed in preflight from pixels only (raw/luma_thresholds.json), before any enhancement scoring. Note that terciles are relative per set: the dark cut-off is luma <=133.7 on heldout_objects but <=65.3 on round6_heldout, so "dark" on heldout_objects is not dark in absolute terms.
- [2026-10-10 02:10] Enhancement verdict pooling: the rule is evaluated on the pooled dark/bright subsets of the two disjoint, correctly-oriented sets (reserved388_partial + round6_heldout). Per-set numbers are reported alongside. heldout_objects/_rotfix are subsets of reserved388_partial and are not pooled to avoid double counting.
- [2026-10-10 02:10] C gate "each located person set" = all four scored sets (heldout_objects, heldout_objects_rotfix, reserved388_partial, round6_heldout) -- the stricter reading.
- [2026-10-10 02:12] Execution order is strictly sequential in stage-number order (S0,S1,S2,S3,S4,S5,S6), with no concurrent GPU work during training. Reason: system commit headroom is only ~4.3 GB of 25.6 GB before training starts; a second CUDA-torch process beside the trainer risks WinError 1455 / OOM in B (the same failure mode documented in v7_results.md). Consequence accepted: C's time gate is evaluated late and may fail.
- [2026-10-10 02:12] Bytecode: all processes run with -B / PYTHONDONTWRITEBYTECODE=1 so importing project modules writes no __pycache__ into ROOT. pipeline_utils' import-time FileHandler on data/detections.log is pre-empted with a NullHandler (file verified unchanged: 17692125 bytes, mtime Oct 6 14:15). YOLO_AUTOINSTALL=False so ultralytics cannot pip-install anything.
- [2026-10-10 02:12] Stock yolov8n = models/yolov8n.pt (sha256 f59b3d83..., 80 classes; the base A was trained from). Not re-downloaded.
- [2026-10-10 02:09] Training/val use OUT/data_v7_fixed.yaml whose `path:` is OUT/dataset_view (NTFS junctions to datasets/sage_merged_v7/{images,labels}/{train,val}), not the dataset dir itself. Reason: Ultralytics would otherwise rewrite the existing labels/train.cache and val.cache (hash includes the pre-move paths), violating the read-only rule. Same files, same train/val split.
- [2026-10-10 03:12] **RULE-1 VIOLATION (my error, discovered at 03:12):** the junction view did NOT protect the dataset caches. Ultralytics' check_det_dataset resolves the split paths (Path.resolve follows NTFS junctions), so it wrote its label caches back into the ORIGINAL dataset dir: datasets/sage_merged_v7/labels/val.cache was overwritten at 02:14 (S1, `val` of A; Aug-22 version was 701,431 bytes, now 690,807) and labels/train.cache at 02:57 (start of B training; was 4,126,607 bytes, now 4,064,610). No label/image file was touched. The previous cache contents are not recoverable. Impact: these are derived scan caches (keyed by a hash of file paths); the Aug-22 ones were already stale after the project move and would have been regenerated by any training run. Their hashes now match, so no further rewrites are expected. Decision: do NOT stop B (stopping would not undo the write); disclose prominently in RESULTS.md. I should have tested the cache location before launching.
- [2026-10-10 03:20] Audit: `find ROOT -newermt '2026-10-10 01:47'` (excluding OUT, .git, venvs) lists only datasets/sage_merged_v7/labels/{train,val}.cache (+ their parent dir mtime, and benchmarks/ for creating OUT). No other file in ROOT was modified. .git changed only through the allowed branch creation.
- [2026-10-10 04:10] B recipe check: optimizer=auto resolved to AdamW (lr0 0.000588); B's lr/pg0 column in results.csv is identical to A's v7_full_train for epochs 1-5, i.e. same optimizer/LR schedule as the control. No args keys were dropped as unsupported. B epochs 2-6 (~470 s) were slowed by my own filesystem audit (find over the dataset tree, ~03:12-03:20); steady-state epochs ~418 s.
- [2026-10-10 06:33] Ultralytics' final validation re-fires on_fit_epoch_end, producing a 31st epoch record that duplicates epoch 30's start time (duration = epoch 30 + final val). Gate and report de-duplicate by epoch start time; the raw file is left as written.
- [2026-10-10 06:31] C gate: run_C=False; failed conditions: ['recall_within_0.02_on_each_set'] (details raw/gate.json)
- [2026-10-10 06:50] Driver finished all stages at 06:35 (4.8 h); C skipped by its gate (recall condition). Per the task, the run stops here rather than using the remaining budget. ANALYST_NOTES.md (plain-language reading, numbers quoted from the generated tables) was written by hand after the run and is embedded in RESULTS.md section 7b; RESULTS.md was regenerated afterwards.

**Double-check by hand:**

- Eyeball OUT/evalsets/held_out/heldout_objects_rotfix/images/With_people_Bedroom_Fall_*.jpg against their labels (the rotation fix rests on one rendered frame + the registered rotation).
- Look at OUT/enhance_grids/*.jpg -- the 6 darkest labelled person frames, original vs best variant.
- The 4 missing source clips (TV_Lounge_1_Fall2, TV_Lounge_2_Fall2, people, people_(2)): if they exist elsewhere, the full 388-box set can be rebuilt with stage0_preflight.build_eval_sets().
- The corrected fall-window rule (section 6) for each clip it changed -- confirm against the videos that the alarm frames really are during the fall.
- Any 'CONTROL NOT REPRODUCED' / 'NOT REPRODUCED' row in section 2.


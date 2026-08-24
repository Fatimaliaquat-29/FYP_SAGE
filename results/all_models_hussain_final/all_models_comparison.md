# LSTM vs TCN vs Random Forest Posture Classifier Comparison

Generated automatically by `compare_all_models.py`. All three models consume the identical extracted keypoints per clip and their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect each architecture's raw per-window decision.

Test clips: 19 — Bend_pickup_lowLight, Bend_pickup_lowLight_leftRight, Bend_pickup_normalLight_back, Bend_pickup_normalLight, Bend_pickup_normalLight_leftRight, Bend_pickup_squat_lowLight, Bend_pickup_squat_normalLight, Kneeling, LyingdownSlowly, Moving_in_out_frame, Moving_in_out_frame_withFall, Sit_Stand_AnklesInvisible, SitFast_GetupFast, SitFloor_crossedLegs, SitFloor_lowKeypoints_crossedLegs, SitFloor_lowKeypoints, Sitting_HalfLandmarks, Sitting_Lying_FewLandmarks_back, Sitting_Lying_FewLandmarks


## Full Comparison Table

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 58.5% | 50.9% | 74.3% |
| Macro Precision | 0.497 | 0.480 | 0.574 |
| Macro Recall | 0.515 | 0.478 | 0.619 |
| Macro F1 | 0.458 | 0.388 | 0.578 |
| Fall-detection recall | 75.0% (3/4) | 66.7% (2/3) | 100.0% (4/4) |
| Fall false positives (clips) | 6 | 9 | 7 |
| Latency mean (ms/window) | 130.510 | 103.948 | 40.333 |
| Latency p95 (ms/window) | 191.598 | 159.266 | 78.345 |
| Parameter/node count | 63,013 | 39,365 | 69,222 |
| Model file size (KB) | 775.1 | 628.5 | 7156.0 |
| Peak RAM (MB) | 616.2 | 633.0 | 632.8 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.506 | 0.679 | 0.580 | 610 |
| Sitting | 1.000 | 0.442 | 0.613 | 893 |
| Lying | 0.483 | 0.938 | 0.637 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.497 | 0.515 | 0.458 | 1858 |
| *Weighted avg* | 0.739 | 0.615 | 0.607 | 1858 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 414 | 0 | 186 | 10 |
| **Sitting** | 360 | 395 | 108 | 30 |
| **Lying** | 22 | 0 | 333 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.528 | 0.730 | 0.613 | 610 |
| Sitting | 1.000 | 0.237 | 0.384 | 893 |
| Lying | 0.392 | 0.946 | 0.554 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.480 | 0.478 | 0.388 | 1858 |
| *Weighted avg* | 0.729 | 0.534 | 0.491 | 1858 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 445 | 0 | 160 | 5 |
| **Sitting** | 352 | 212 | 295 | 34 |
| **Lying** | 19 | 0 | 336 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — RF

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.616 | 0.823 | 0.705 | 610 |
| Sitting | 0.993 | 0.674 | 0.803 | 893 |
| Lying | 0.686 | 0.977 | 0.806 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.574 | 0.619 | 0.578 | 1858 |
| *Weighted avg* | 0.811 | 0.781 | 0.771 | 1858 |


### Confusion matrix — RF

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 502 | 0 | 94 | 14 |
| **Sitting** | 291 | 602 | 0 | 0 |
| **Lying** | 3 | 4 | 347 | 1 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-clip accuracy

| Clip | LSTM acc | TCN acc | RF acc | LSTM fall result | TCN fall result | RF fall result |
|---|---|---|---|---|---|---|
| Bend_pickup_lowLight | 65.2 (15/23) | 69.6 (16/23) | 100.0 (23/23) | false_positive | false_positive | false_positive |
| Bend_pickup_lowLight_leftRight | 43.9 (29/66) | 68.2 (45/66) | 89.4 (59/66) | false_positive | false_positive | false_positive |
| Bend_pickup_normalLight_back | 100.0 (86/86) | 100.0 (86/86) | 100.0 (86/86) | no_fall | no_fall | false_positive |
| Bend_pickup_normalLight | 75.0 (21/28) | 60.7 (17/28) | 100.0 (28/28) | no_fall | false_positive | no_fall |
| Bend_pickup_normalLight_leftRight | 71.4 (105/147) | 83.0 (122/147) | 94.6 (139/147) | false_positive | false_positive | false_positive |
| Bend_pickup_squat_lowLight | 100.0 (31/31) | 100.0 (31/31) | 100.0 (31/31) | no_fall | no_fall | no_fall |
| Bend_pickup_squat_normalLight | 100.0 (12/12) | 100.0 (12/12) | 100.0 (12/12) | no_fall | no_fall | no_fall |
| Kneeling | 17.4 (15/86) | 10.5 (9/86) | 98.8 (85/86) | no_fall | false_positive | no_fall |
| LyingdownSlowly | 100.0 (118/118) | 100.0 (118/118) | 100.0 (118/118) | true_positive | false_positive | true_positive |
| Moving_in_out_frame | 21.7 (38/175) | 24.6 (43/175) | 32.0 (56/175) | false_positive | false_positive | false_positive |
| Moving_in_out_frame_withFall | 57.8 (78/135) | 57.8 (78/135) | 43.7 (59/135) | true_positive | true_positive | true_positive |
| Sit_Stand_AnklesInvisible | 12.8 (16/125) | 14.4 (18/125) | 14.4 (18/125) | false_positive | no_fall | no_fall |
| SitFast_GetupFast | 0.0 (0/80) | 0.0 (0/80) | 0.0 (0/80) | no_fall | no_fall | no_fall |
| SitFloor_crossedLegs | 100.0 (118/118) | 100.0 (118/118) | 100.0 (118/118) | no_fall | no_fall | false_positive |
| SitFloor_lowKeypoints_crossedLegs | 71.3 (82/115) | 0.0 (0/115) | 88.7 (102/115) | false_positive | false_positive | false_positive |
| SitFloor_lowKeypoints | 43.0 (49/114) | 23.7 (27/114) | 36.8 (42/114) | no_fall | false_positive | no_fall |
| Sitting_HalfLandmarks | 25.0 (22/88) | 31.8 (28/88) | 100.0 (88/88) | no_fall | no_fall | no_fall |
| Sitting_Lying_FewLandmarks_back | 97.0 (256/264) | 70.1 (185/264) | 100.0 (264/264) | false_negative | false_negative | true_positive |
| Sitting_Lying_FewLandmarks | 36.2 (51/141) | 28.4 (40/141) | 87.2 (123/141) | true_positive | true_positive | true_positive |

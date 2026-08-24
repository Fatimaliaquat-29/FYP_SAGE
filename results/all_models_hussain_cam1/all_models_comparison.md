# LSTM vs TCN vs Random Forest Posture Classifier Comparison

Generated automatically by `compare_all_models.py`. All three models consume the identical extracted keypoints per clip and their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect each architecture's raw per-window decision.

Test clips: 19 — Bend_pickup_lowLight, Bend_pickup_lowLight_leftRight, Bend_pickup_normalLight_back, Bend_pickup_normalLight, Bend_pickup_normalLight_leftRight, Bend_pickup_squat_lowLight, Bend_pickup_squat_normalLight, Kneeling, LyingdownSlowly, Moving_in_out_frame, Moving_in_out_frame_withFall, Sit_Stand_AnklesInvisible, SitFast_GetupFast, SitFloor_crossedLegs, SitFloor_lowKeypoints_crossedLegs, SitFloor_lowKeypoints, Sitting_HalfLandmarks, Sitting_Lying_FewLandmarks_back, Sitting_Lying_FewLandmarks


## Full Comparison Table

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 52.5% | 62.9% | 67.0% |
| Macro Precision | 0.421 | 0.522 | 0.542 |
| Macro Recall | 0.437 | 0.535 | 0.565 |
| Macro F1 | 0.410 | 0.504 | 0.531 |
| Fall-detection recall | 100.0% (4/4) | 100.0% (4/4) | 100.0% (4/4) |
| Fall false positives (clips) | 12 | 6 | 7 |
| Latency mean (ms/window) | 138.045 | 108.615 | 35.901 |
| Latency p95 (ms/window) | 211.950 | 164.006 | 55.689 |
| Parameter/node count | 63,013 | 39,365 | 61,532 |
| Model file size (KB) | 775.1 | 628.5 | 6375.0 |
| Peak RAM (MB) | 615.6 | 633.3 | 602.3 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.460 | 0.716 | 0.560 | 610 |
| Sitting | 0.717 | 0.411 | 0.522 | 893 |
| Lying | 0.508 | 0.620 | 0.558 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.421 | 0.437 | 0.410 | 1858 |
| *Weighted avg* | 0.592 | 0.551 | 0.542 | 1858 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 437 | 25 | 129 | 19 |
| **Sitting** | 480 | 367 | 46 | 0 |
| **Lying** | 14 | 120 | 220 | 1 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.503 | 0.782 | 0.612 | 610 |
| Sitting | 0.897 | 0.499 | 0.642 | 893 |
| Lying | 0.687 | 0.859 | 0.763 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.522 | 0.535 | 0.504 | 1858 |
| *Weighted avg* | 0.728 | 0.661 | 0.655 | 1858 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 477 | 11 | 101 | 21 |
| **Sitting** | 438 | 446 | 0 | 9 |
| **Lying** | 10 | 40 | 305 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — RF

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.553 | 0.857 | 0.673 | 610 |
| Sitting | 0.914 | 0.534 | 0.674 | 893 |
| Lying | 0.702 | 0.868 | 0.776 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.542 | 0.565 | 0.531 | 1858 |
| *Weighted avg* | 0.755 | 0.704 | 0.693 | 1858 |


### Confusion matrix — RF

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 523 | 0 | 67 | 20 |
| **Sitting** | 401 | 477 | 15 | 0 |
| **Lying** | 2 | 45 | 308 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-clip accuracy

| Clip | LSTM acc | TCN acc | RF acc | LSTM fall result | TCN fall result | RF fall result |
|---|---|---|---|---|---|---|
| Bend_pickup_lowLight | 95.7 (22/23) | 100.0 (23/23) | 100.0 (23/23) | false_positive | false_positive | false_positive |
| Bend_pickup_lowLight_leftRight | 65.2 (43/66) | 75.8 (50/66) | 100.0 (66/66) | false_positive | false_positive | false_positive |
| Bend_pickup_normalLight_back | 100.0 (86/86) | 100.0 (86/86) | 100.0 (86/86) | no_fall | no_fall | false_positive |
| Bend_pickup_normalLight | 39.3 (11/28) | 100.0 (28/28) | 100.0 (28/28) | false_positive | false_positive | no_fall |
| Bend_pickup_normalLight_leftRight | 76.9 (113/147) | 81.6 (120/147) | 100.0 (147/147) | false_positive | false_positive | no_fall |
| Bend_pickup_squat_lowLight | 100.0 (31/31) | 100.0 (31/31) | 100.0 (31/31) | false_positive | no_fall | no_fall |
| Bend_pickup_squat_normalLight | 100.0 (12/12) | 100.0 (12/12) | 100.0 (12/12) | false_positive | false_positive | no_fall |
| Kneeling | 17.4 (15/86) | 17.4 (15/86) | 31.4 (27/86) | no_fall | no_fall | no_fall |
| LyingdownSlowly | 100.0 (118/118) | 100.0 (118/118) | 100.0 (118/118) | true_positive | true_positive | true_positive |
| Moving_in_out_frame | 28.0 (49/175) | 27.4 (48/175) | 33.7 (59/175) | false_positive | false_positive | false_positive |
| Moving_in_out_frame_withFall | 32.6 (44/135) | 34.8 (47/135) | 36.3 (49/135) | true_positive | true_positive | true_positive |
| Sit_Stand_AnklesInvisible | 8.8 (11/125) | 14.4 (18/125) | 14.4 (18/125) | false_positive | no_fall | no_fall |
| SitFast_GetupFast | 0.0 (0/80) | 0.0 (0/80) | 0.0 (0/80) | false_positive | no_fall | no_fall |
| SitFloor_crossedLegs | 14.4 (17/118) | 100.0 (118/118) | 100.0 (118/118) | false_positive | no_fall | no_fall |
| SitFloor_lowKeypoints_crossedLegs | 100.0 (115/115) | 92.2 (106/115) | 100.0 (115/115) | false_positive | no_fall | false_positive |
| SitFloor_lowKeypoints | 93.9 (107/114) | 92.1 (105/114) | 100.0 (114/114) | no_fall | no_fall | false_positive |
| Sitting_HalfLandmarks | 11.4 (10/88) | 0.0 (0/88) | 0.0 (0/88) | false_positive | no_fall | false_positive |
| Sitting_Lying_FewLandmarks_back | 61.0 (161/264) | 92.4 (244/264) | 90.2 (238/264) | true_positive | true_positive | true_positive |
| Sitting_Lying_FewLandmarks | 41.8 (59/141) | 41.8 (59/141) | 41.8 (59/141) | true_positive | true_positive | true_positive |

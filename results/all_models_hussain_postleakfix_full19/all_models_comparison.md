# LSTM vs TCN vs Random Forest Posture Classifier Comparison

Generated automatically by `compare_all_models.py`. All three models consume the identical extracted keypoints per clip and their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect each architecture's raw per-window decision.

Test clips: 19 — Bend_pickup_lowLight, Bend_pickup_lowLight_leftRight, Bend_pickup_normalLight_back, Bend_pickup_normalLight, Bend_pickup_normalLight_leftRight, Bend_pickup_squat_lowLight, Bend_pickup_squat_normalLight, Kneeling, LyingdownSlowly, Moving_in_out_frame, Moving_in_out_frame_withFall, Sit_Stand_AnklesInvisible, SitFast_GetupFast, SitFloor_crossedLegs, SitFloor_lowKeypoints_crossedLegs, SitFloor_lowKeypoints, Sitting_HalfLandmarks, Sitting_Lying_FewLandmarks_back, Sitting_Lying_FewLandmarks


## Full Comparison Table

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 56.5% | 50.9% | 74.3% |
| Macro Precision | 0.518 | 0.480 | 0.574 |
| Macro Recall | 0.509 | 0.478 | 0.619 |
| Macro F1 | 0.465 | 0.388 | 0.578 |
| Fall-detection recall | 75.0% (3/4) | 66.7% (2/3) | 100.0% (4/4) |
| Fall false positives (clips) | 8 | 9 | 7 |
| Latency mean (ms/window) | 115.719 | 105.843 | 34.084 |
| Latency p95 (ms/window) | 175.587 | 159.963 | 54.585 |
| Parameter/node count | 63,013 | 39,365 | 69,222 |
| Model file size (KB) | 774.4 | 628.5 | 7156.0 |
| Peak RAM (MB) | 616.7 | 634.8 | 634.5 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.522 | 0.666 | 0.585 | 610 |
| Sitting | 0.986 | 0.389 | 0.557 | 893 |
| Lying | 0.563 | 0.983 | 0.716 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.518 | 0.509 | 0.465 | 1858 |
| *Weighted avg* | 0.753 | 0.593 | 0.597 | 1858 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 406 | 0 | 170 | 34 |
| **Sitting** | 347 | 347 | 64 | 135 |
| **Lying** | 1 | 5 | 349 | 0 |
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
| Bend_pickup_lowLight | 73.9 (17/23) | 69.6 (16/23) | 100.0 (23/23) | false_positive | false_positive | false_positive |
| Bend_pickup_lowLight_leftRight | 37.9 (25/66) | 68.2 (45/66) | 89.4 (59/66) | false_positive | false_positive | false_positive |
| Bend_pickup_normalLight_back | 100.0 (86/86) | 100.0 (86/86) | 100.0 (86/86) | false_positive | no_fall | false_positive |
| Bend_pickup_normalLight | 100.0 (28/28) | 60.7 (17/28) | 100.0 (28/28) | no_fall | false_positive | no_fall |
| Bend_pickup_normalLight_leftRight | 69.4 (102/147) | 83.0 (122/147) | 94.6 (139/147) | false_positive | false_positive | false_positive |
| Bend_pickup_squat_lowLight | 77.4 (24/31) | 100.0 (31/31) | 100.0 (31/31) | no_fall | no_fall | no_fall |
| Bend_pickup_squat_normalLight | 100.0 (12/12) | 100.0 (12/12) | 100.0 (12/12) | no_fall | no_fall | no_fall |
| Kneeling | 17.4 (15/86) | 10.5 (9/86) | 98.8 (85/86) | no_fall | false_positive | no_fall |
| LyingdownSlowly | 100.0 (118/118) | 100.0 (118/118) | 100.0 (118/118) | true_positive | false_positive | true_positive |
| Moving_in_out_frame | 22.3 (39/175) | 24.6 (43/175) | 32.0 (56/175) | false_positive | false_positive | false_positive |
| Moving_in_out_frame_withFall | 57.8 (78/135) | 57.8 (78/135) | 43.7 (59/135) | true_positive | true_positive | true_positive |
| Sit_Stand_AnklesInvisible | 9.6 (12/125) | 14.4 (18/125) | 14.4 (18/125) | no_fall | no_fall | no_fall |
| SitFast_GetupFast | 0.0 (0/80) | 0.0 (0/80) | 0.0 (0/80) | no_fall | no_fall | no_fall |
| SitFloor_crossedLegs | 100.0 (118/118) | 100.0 (118/118) | 100.0 (118/118) | false_positive | no_fall | false_positive |
| SitFloor_lowKeypoints_crossedLegs | 17.4 (20/115) | 0.0 (0/115) | 88.7 (102/115) | false_positive | false_positive | false_positive |
| SitFloor_lowKeypoints | 57.0 (65/114) | 23.7 (27/114) | 36.8 (42/114) | no_fall | false_positive | no_fall |
| Sitting_HalfLandmarks | 29.5 (26/88) | 31.8 (28/88) | 100.0 (88/88) | false_positive | no_fall | no_fall |
| Sitting_Lying_FewLandmarks_back | 98.1 (259/264) | 70.1 (185/264) | 100.0 (264/264) | false_negative | false_negative | true_positive |
| Sitting_Lying_FewLandmarks | 41.1 (58/141) | 28.4 (40/141) | 87.2 (123/141) | true_positive | true_positive | true_positive |

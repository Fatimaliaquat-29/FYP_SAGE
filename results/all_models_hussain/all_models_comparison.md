# LSTM vs TCN vs Random Forest Posture Classifier Comparison

Generated automatically by `compare_all_models.py`. All three models consume the identical extracted keypoints per clip and their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect each architecture's raw per-window decision.

Test clips: 17 — Bend_pickup_lowLight, Bend_pickup_normalLight_back, Bend_pickup_normalLight, Bend_pickup_normalLight_leftRight, Bend_pickup_squat_lowLight, Bend_pickup_squat_normalLight, Kneeling, LyingdownSlowly, Moving_in_out_frame, Moving_in_out_frame_withFall, Sit_Stand_AnklesInvisible, SitFast_GetupFast, SitFloor_lowKeypoints_crossedLegs, SitFloor_lowKeypoints, Sitting_HalfLandmarks, Sitting_Lying_FewLandmarks_back, Sitting_Lying_FewLandmarks


## Full Comparison Table

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 46.0% | 49.7% | 60.3% |
| Macro Precision | 0.456 | 0.479 | 0.511 |
| Macro Recall | 0.488 | 0.530 | 0.589 |
| Macro F1 | 0.372 | 0.402 | 0.498 |
| Fall-detection recall | 75.0% (3/4) | 75.0% (3/4) | 100.0% (4/4) |
| Fall false positives (clips) | 11 | 7 | 6 |
| Latency mean (ms/window) | 88.990 | 90.023 | 81.198 |
| Latency p95 (ms/window) | 122.979 | 128.700 | 119.988 |
| Parameter/node count | 63,013 | 39,365 | 271,508 |
| Model file size (KB) | 774.4 | 628.5 | 27700.7 |
| Peak RAM (MB) | 554.8 | 572.8 | 571.5 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.381 | 0.778 | 0.511 | 387 |
| Sitting | 1.000 | 0.228 | 0.372 | 775 |
| Lying | 0.444 | 0.946 | 0.604 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.456 | 0.488 | 0.372 | 1517 |
| *Weighted avg* | 0.712 | 0.537 | 0.462 | 1517 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 301 | 0 | 82 | 4 |
| **Sitting** | 391 | 177 | 167 | 40 |
| **Lying** | 19 | 0 | 336 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.422 | 0.891 | 0.573 | 387 |
| Sitting | 1.000 | 0.230 | 0.374 | 775 |
| Lying | 0.492 | 1.000 | 0.660 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.479 | 0.530 | 0.402 | 1517 |
| *Weighted avg* | 0.734 | 0.579 | 0.491 | 1517 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 345 | 0 | 41 | 1 |
| **Sitting** | 383 | 178 | 163 | 51 |
| **Lying** | 0 | 0 | 355 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — RF

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.419 | 0.907 | 0.573 | 387 |
| Sitting | 0.976 | 0.476 | 0.640 | 775 |
| Lying | 0.650 | 0.975 | 0.780 | 355 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.511 | 0.589 | 0.498 | 1517 |
| *Weighted avg* | 0.758 | 0.703 | 0.656 | 1517 |


### Confusion matrix — RF

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 351 | 0 | 36 | 0 |
| **Sitting** | 404 | 369 | 0 | 2 |
| **Lying** | 0 | 9 | 346 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-clip accuracy

| Clip | LSTM acc | TCN acc | RF acc | LSTM fall result | TCN fall result | RF fall result |
|---|---|---|---|---|---|---|
| Bend_pickup_lowLight | 43.5 (10/23) | 69.6 (16/23) | 100.0 (23/23) | false_positive | false_positive | false_positive |
| Bend_pickup_normalLight_back | 100.0 (86/86) | 100.0 (86/86) | 100.0 (86/86) | false_positive | no_fall | false_positive |
| Bend_pickup_normalLight | 57.1 (16/28) | 60.7 (17/28) | 96.4 (27/28) | false_positive | false_positive | false_positive |
| Bend_pickup_normalLight_leftRight | 71.4 (105/147) | 84.4 (124/147) | 76.2 (112/147) | false_positive | false_positive | false_positive |
| Bend_pickup_squat_lowLight | 71.0 (22/31) | 100.0 (31/31) | 100.0 (31/31) | false_positive | no_fall | no_fall |
| Bend_pickup_squat_normalLight | 100.0 (12/12) | 100.0 (12/12) | 100.0 (12/12) | false_positive | no_fall | no_fall |
| Kneeling | 17.4 (15/86) | 16.3 (14/86) | 17.4 (15/86) | no_fall | no_fall | no_fall |
| LyingdownSlowly | 100.0 (118/118) | 100.0 (118/118) | 100.0 (118/118) | true_positive | true_positive | true_positive |
| Moving_in_out_frame | 0.0 (0/175) | 0.0 (0/175) | 0.0 (0/175) | false_positive | false_positive | false_positive |
| Moving_in_out_frame_withFall | 40.7 (55/135) | 43.7 (59/135) | 40.7 (55/135) | true_positive | true_positive | true_positive |
| Sit_Stand_AnklesInvisible | 11.2 (14/125) | 14.4 (18/125) | 14.4 (18/125) | false_positive | no_fall | no_fall |
| SitFast_GetupFast | 0.0 (0/80) | 0.0 (0/80) | 0.0 (0/80) | no_fall | no_fall | no_fall |
| SitFloor_lowKeypoints_crossedLegs | 51.3 (59/115) | 0.0 (0/115) | 98.3 (113/115) | false_positive | false_positive | false_positive |
| SitFloor_lowKeypoints | 18.4 (21/114) | 38.6 (44/114) | 100.0 (114/114) | false_positive | false_positive | no_fall |
| Sitting_HalfLandmarks | 15.9 (14/88) | 36.4 (32/88) | 27.3 (24/88) | false_positive | false_positive | no_fall |
| Sitting_Lying_FewLandmarks_back | 84.5 (223/264) | 93.9 (248/264) | 98.1 (259/264) | false_negative | false_negative | true_positive |
| Sitting_Lying_FewLandmarks | 31.2 (44/141) | 41.8 (59/141) | 41.8 (59/141) | true_positive | true_positive | true_positive |

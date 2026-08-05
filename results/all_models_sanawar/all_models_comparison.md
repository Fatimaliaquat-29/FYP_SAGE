# LSTM vs TCN vs Random Forest Posture Classifier Comparison

Generated automatically by `compare_all_models.py`. All three models consume the identical extracted keypoints per clip and their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect each architecture's raw per-window decision.

Test clips: 8 — Backward_fall, Chair_fall, Fall_and_lie, Far_fall, Occluded_fall, Off_axis_fall, Side_fall, Slow_fall


## Full Comparison Table

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 72.8% | 79.1% | 57.3% |
| Macro Precision | 0.343 | 0.489 | 0.334 |
| Macro Recall | 0.294 | 0.312 | 0.337 |
| Macro F1 | 0.315 | 0.368 | 0.301 |
| Fall-detection recall | 87.5% (7/8) | 75.0% (6/8) | 87.5% (7/8) |
| Fall false positives (clips) | 0 | 0 | 0 |
| Latency mean (ms/window) | 92.452 | 89.842 | 76.054 |
| Latency p95 (ms/window) | 129.714 | 121.436 | 109.384 |
| Parameter/node count | 63,013 | 39,365 | 271,508 |
| Model file size (KB) | 774.4 | 628.5 | 27700.7 |
| Peak RAM (MB) | 494.7 | 508.9 | 509.2 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.394 | 0.407 | 0.400 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.977 | 0.771 | 0.862 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.343 | 0.294 | 0.315 | 967 |
| *Weighted avg* | 0.911 | 0.728 | 0.809 | 967 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 37 | 0 | 5 | 49 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 57 | 60 | 667 | 81 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 1.000 | 0.407 | 0.578 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.955 | 0.842 | 0.895 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.489 | 0.312 | 0.368 | 967 |
| *Weighted avg* | 0.949 | 0.791 | 0.855 | 967 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 37 | 0 | 23 | 31 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 0 | 17 | 728 | 120 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — RF

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.358 | 0.791 | 0.493 | 91 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.978 | 0.557 | 0.710 | 865 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.334 | 0.337 | 0.301 | 967 |
| *Weighted avg* | 0.908 | 0.573 | 0.681 | 967 |


### Confusion matrix — RF

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 72 | 0 | 0 | 19 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 129 | 198 | 482 | 56 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-clip accuracy

| Clip | LSTM acc | TCN acc | RF acc | LSTM fall result | TCN fall result | RF fall result |
|---|---|---|---|---|---|---|
| Backward_fall | 8.3 (4/48) | 12.5 (6/48) | 10.4 (5/48) | true_positive | false_negative | false_negative |
| Chair_fall | 23.4 (43/184) | 47.8 (88/184) | 31.5 (58/184) | true_positive | true_positive | true_positive |
| Fall_and_lie | 89.2 (257/288) | 92.0 (265/288) | 30.2 (87/288) | true_positive | true_positive | true_positive |
| Far_fall | 100.0 (66/66) | 100.0 (66/66) | 100.0 (66/66) | false_negative | false_negative | true_positive |
| Occluded_fall | 100.0 (108/108) | 100.0 (108/108) | 100.0 (108/108) | true_positive | true_positive | true_positive |
| Off_axis_fall | 98.4 (60/61) | 98.4 (60/61) | 100.0 (61/61) | true_positive | true_positive | true_positive |
| Side_fall | 97.9 (95/97) | 97.9 (95/97) | 100.0 (97/97) | true_positive | true_positive | true_positive |
| Slow_fall | 61.7 (71/115) | 67.0 (77/115) | 62.6 (72/115) | true_positive | true_positive | true_positive |

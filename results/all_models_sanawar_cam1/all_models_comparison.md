# LSTM vs TCN vs Random Forest Posture Classifier Comparison

Generated automatically by `compare_all_models.py`. All three models consume the identical extracted keypoints per clip and their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect each architecture's raw per-window decision.

Test clips: 9 — Backward_fall, Chair_fall, Fall_and_lie, Far_fall, Forward_fall, Occluded_fall, Off_axis_fall, Side_fall, Slow_fall


## Full Comparison Table

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 45.2% | 68.8% | 56.2% |
| Macro Precision | 0.353 | 0.326 | 0.347 |
| Macro Recall | 0.275 | 0.356 | 0.380 |
| Macro F1 | 0.284 | 0.312 | 0.311 |
| Fall-detection recall | 100.0% (9/9) | 88.9% (8/9) | 88.9% (8/9) |
| Fall false positives (clips) | 0 | 0 | 0 |
| Latency mean (ms/window) | 169.974 | 139.233 | 60.514 |
| Latency p95 (ms/window) | 235.759 | 180.322 | 96.351 |
| Parameter/node count | 63,013 | 39,365 | 61,532 |
| Model file size (KB) | 775.1 | 628.5 | 6375.0 |
| Peak RAM (MB) | 499.9 | 515.0 | 515.0 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.452 | 0.667 | 0.538 | 105 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.962 | 0.434 | 0.598 | 943 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.353 | 0.275 | 0.284 | 1059 |
| *Weighted avg* | 0.902 | 0.452 | 0.586 | 1059 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 70 | 9 | 14 | 12 |
| **Sitting** | 0 | 0 | 2 | 9 |
| **Lying** | 85 | 391 | 409 | 58 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.304 | 0.733 | 0.430 | 105 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 1.000 | 0.691 | 0.818 | 943 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.326 | 0.356 | 0.312 | 1059 |
| *Weighted avg* | 0.921 | 0.688 | 0.771 | 1059 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 77 | 10 | 0 | 18 |
| **Sitting** | 0 | 0 | 0 | 11 |
| **Lying** | 176 | 32 | 652 | 83 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — RF

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.389 | 1.000 | 0.560 | 105 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 1.000 | 0.520 | 0.684 | 943 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.347 | 0.380 | 0.311 | 1059 |
| *Weighted avg* | 0.929 | 0.562 | 0.664 | 1059 |


### Confusion matrix — RF

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 105 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 11 |
| **Lying** | 165 | 244 | 490 | 44 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-clip accuracy

| Clip | LSTM acc | TCN acc | RF acc | LSTM fall result | TCN fall result | RF fall result |
|---|---|---|---|---|---|---|
| Backward_fall | 50.0 (24/48) | 2.1 (1/48) | 10.4 (5/48) | true_positive | false_negative | false_negative |
| Chair_fall | 3.3 (6/184) | 20.1 (37/184) | 9.8 (18/184) | true_positive | true_positive | true_positive |
| Fall_and_lie | 20.5 (59/288) | 74.7 (215/288) | 27.4 (79/288) | true_positive | true_positive | true_positive |
| Far_fall | 53.0 (35/66) | 90.9 (60/66) | 100.0 (66/66) | true_positive | true_positive | true_positive |
| Forward_fall | 85.9 (79/92) | 78.3 (72/92) | 91.3 (84/92) | true_positive | true_positive | true_positive |
| Occluded_fall | 70.4 (76/108) | 100.0 (108/108) | 100.0 (108/108) | true_positive | true_positive | true_positive |
| Off_axis_fall | 59.0 (36/61) | 75.4 (46/61) | 78.7 (48/61) | true_positive | true_positive | true_positive |
| Side_fall | 100.0 (97/97) | 100.0 (97/97) | 100.0 (97/97) | true_positive | true_positive | true_positive |
| Slow_fall | 58.3 (67/115) | 80.9 (93/115) | 78.3 (90/115) | true_positive | true_positive | true_positive |

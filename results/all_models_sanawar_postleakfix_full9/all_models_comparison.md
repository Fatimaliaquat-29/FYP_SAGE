# LSTM vs TCN vs Random Forest Posture Classifier Comparison

Generated automatically by `compare_all_models.py`. All three models consume the identical extracted keypoints per clip and their own `.predict()` public interface with no additional threshold/warmup/smoothing layered on top, so results reflect each architecture's raw per-window decision.

Test clips: 9 — Backward_fall, Chair_fall, Fall_and_lie, Far_fall, Forward_fall, Occluded_fall, Off_axis_fall, Side_fall, Slow_fall


## Full Comparison Table

| Metric | LSTM | TCN | RF |
|---|---|---|---|
| Accuracy | 50.8% | 74.4% | 58.8% |
| Macro Precision | 0.350 | 0.491 | 0.329 |
| Macro Recall | 0.221 | 0.247 | 0.328 |
| Macro F1 | 0.267 | 0.294 | 0.296 |
| Fall-detection recall | 77.8% (7/9) | 77.8% (7/9) | 88.9% (8/9) |
| Fall false positives (clips) | 0 | 0 | 0 |
| Latency mean (ms/window) | 215.894 | 200.632 | 65.533 |
| Latency p95 (ms/window) | 368.041 | 303.807 | 96.640 |
| Parameter/node count | 63,013 | 39,365 | 69,222 |
| Model file size (KB) | 774.4 | 628.5 | 7156.0 |
| Peak RAM (MB) | 494.5 | 472.3 | 472.3 |


### Per-class metrics — LSTM

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.407 | 0.352 | 0.378 | 105 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.992 | 0.531 | 0.692 | 943 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.350 | 0.221 | 0.267 | 1059 |
| *Weighted avg* | 0.924 | 0.508 | 0.654 | 1059 |


### Confusion matrix — LSTM

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 37 | 0 | 4 | 64 |
| **Sitting** | 0 | 0 | 0 | 11 |
| **Lying** | 54 | 204 | 501 | 184 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — TCN

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 1.000 | 0.171 | 0.293 | 105 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.963 | 0.817 | 0.884 | 943 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.491 | 0.247 | 0.294 | 1059 |
| *Weighted avg* | 0.956 | 0.744 | 0.816 | 1059 |


### Confusion matrix — TCN

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 18 | 12 | 19 | 56 |
| **Sitting** | 0 | 0 | 11 | 0 |
| **Lying** | 0 | 61 | 770 | 112 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-class metrics — RF

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Standing | 0.332 | 0.733 | 0.457 | 105 |
| Sitting | 0.000 | 0.000 | 0.000 | 11 |
| Lying | 0.984 | 0.579 | 0.729 | 943 |
| Unknown | 0.000 | 0.000 | 0.000 | 0 |
| *Macro avg* | 0.329 | 0.328 | 0.296 | 1059 |
| *Weighted avg* | 0.909 | 0.588 | 0.694 | 1059 |


### Confusion matrix — RF

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 77 | 0 | 0 | 28 |
| **Sitting** | 0 | 0 | 9 | 2 |
| **Lying** | 155 | 181 | 546 | 61 |
| **Unknown** | 0 | 0 | 0 | 0 |



### Per-clip accuracy

| Clip | LSTM acc | TCN acc | RF acc | LSTM fall result | TCN fall result | RF fall result |
|---|---|---|---|---|---|---|
| Backward_fall | 0.0 (0/48) | 6.2 (3/48) | 10.4 (5/48) | false_negative | false_negative | false_negative |
| Chair_fall | 20.1 (37/184) | 47.3 (87/184) | 25.0 (46/184) | true_positive | true_positive | true_positive |
| Fall_and_lie | 18.8 (54/288) | 81.9 (236/288) | 28.8 (83/288) | true_positive | true_positive | true_positive |
| Far_fall | 100.0 (66/66) | 74.2 (49/66) | 100.0 (66/66) | false_negative | false_negative | true_positive |
| Forward_fall | 84.8 (78/92) | 84.8 (78/92) | 100.0 (92/92) | true_positive | true_positive | true_positive |
| Occluded_fall | 100.0 (108/108) | 98.1 (106/108) | 100.0 (108/108) | true_positive | true_positive | true_positive |
| Off_axis_fall | 75.4 (46/61) | 98.4 (60/61) | 100.0 (61/61) | true_positive | true_positive | true_positive |
| Side_fall | 97.9 (95/97) | 97.9 (95/97) | 100.0 (97/97) | true_positive | true_positive | true_positive |
| Slow_fall | 47.0 (54/115) | 64.3 (74/115) | 56.5 (65/115) | true_positive | true_positive | true_positive |

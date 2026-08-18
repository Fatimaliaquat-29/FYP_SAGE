# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| Backward_fall | 38.5% | FN | **posture<90%, false negative** |
| Chair_fall | 0.0% | FN | **posture<90%, false negative** |
| Fall_and_lie | 29.6% | TP (latency 16 frames) | **posture<90%** |
| Far_fall | 100.0% | TP (latency 53 frames) |  |
| Occluded_fall | 100.0% | TP (latency 52 frames) |  |
| Off_axis_fall | 100.0% | TP (latency 16 frames) |  |
| Side_fall | 95.3% | TP (latency 67 frames) |  |
| Slow_fall | 100.0% | TP (latency 27 frames) |  |

---

## Backward_fall (**posture<90%, false negative**)

**Posture accuracy:** 38.5%

**Per-class accuracy:**

- Standing: 85.7%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 30 | 0 | 0 | 5 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 6 | 37 | 0 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | 170.9 | 171.8 | 2.7 | 0.0 | 0.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing |
| 3 | Standing | Unknown | 172.0 | 171.8 | 2.7 | 0.0 | 1.6 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing |
| 4 | Standing | Unknown | 172.8 | 171.5 | 2.6 | 0.1 | 3.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing |
| 5 | Standing | Unknown | 171.7 | 171.8 | 2.9 | 0.0 | 9.8 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 69 | Lying | Sitting | nan | 152.6 | 5.0 | 1.1 | 41.5 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 70 | Lying | Sitting | nan | 148.4 | 3.1 | 0.8 | 56.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 71 | Lying | Sitting | nan | 143.6 | 1.6 | 0.6 | 47.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 72 | Lying | Sitting | nan | 154.3 | 0.3 | 0.5 | 37.4 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 73 | Lying | Sitting | nan | 154.3 | 1.4 | 0.2 | 31.4 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 74 | Lying | Sitting | nan | 154.4 | 2.3 | 0.4 | 27.0 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 75 | Lying | Sitting | nan | 154.3 | 2.2 | 0.2 | 2.7 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 76 | Lying | Sitting | nan | 153.2 | 2.7 | 0.3 | 14.8 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 77 | Lying | Standing | nan | 164.2 | 3.3 | 0.4 | 19.0 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 78 | Lying | Standing | nan | 161.9 | 4.6 | 0.2 | 38.2 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 79 | Lying | Standing | nan | 162.5 | 6.0 | 0.2 | 43.0 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 80 | Lying | Standing | nan | 166.8 | 5.5 | 0.4 | 16.0 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 81 | Lying | Standing | nan | 166.7 | 5.8 | 0.1 | 8.7 | 0.3 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 82 | Lying | Sitting | nan | 166.7 | 5.7 | 0.2 | 1.4 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 83 | Lying | Sitting | nan | 168.4 | 5.7 | 0.6 | 1.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 84 | Lying | Sitting | nan | 165.1 | 3.8 | 0.8 | 56.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 85 | Lying | Sitting | nan | 164.1 | 2.5 | 0.5 | 38.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 86 | Lying | Sitting | nan | 162.4 | 3.3 | 0.1 | 22.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 87 | Lying | Sitting | nan | 159.3 | 3.2 | 0.1 | 2.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 88 | Lying | Sitting | nan | 157.7 | 4.3 | 0.1 | 32.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 89 | Lying | Sitting | nan | 162.2 | 4.4 | 0.1 | 2.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 90 | Lying | Sitting | nan | 160.8 | 4.1 | 0.1 | 7.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 91 | Lying | Sitting | nan | 163.4 | 3.6 | 0.3 | 15.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 92 | Lying | Sitting | nan | 167.5 | 2.4 | 0.4 | 34.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 93 | Lying | Sitting | nan | 175.7 | 7.3 | 0.1 | 145.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 94 | Lying | Sitting | nan | 158.0 | 9.3 | 0.8 | 60.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 95 | Lying | Sitting | nan | 158.2 | 6.0 | 0.7 | 98.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 96 | Lying | Sitting | nan | 152.8 | 5.3 | 0.3 | 22.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 97 | Lying | Sitting | nan | 161.8 | 5.0 | 0.1 | 9.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 98 | Lying | Sitting | nan | 155.8 | 8.2 | 0.1 | 97.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Lying | Sitting | nan | 167.9 | 6.8 | 0.4 | 42.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 101 | Lying | Sitting | nan | 169.9 | 2.1 | 0.3 | 70.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 102 | Lying | Sitting | nan | nan | 6.7 | 1.7 | 137.7 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Unknown|Sitting|Standing |
| 103 | Lying | Sitting | nan | nan | 5.9 | 1.4 | 22.6 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Unknown|Sitting|Standing|Standing |
| 104 | Lying | Sitting | nan | nan | 5.6 | 0.4 | 9.5 | 0.2 | 0.3 | 0.1 | T | F | Unknown|Sitting|Standing|Standing|Standing |
| 105 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Standing|Standing|Standing|Unknown |
| 106 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 107 | Lying | Sitting | nan | nan | 6.3 | 0.5 | 6.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Unknown|Unknown|Standing |
| 108 | Lying | Sitting | nan | nan | 4.8 | 0.7 | 44.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Unknown|Unknown|Standing|Standing |
| 109 | Lying | Sitting | nan | nan | 3.4 | 0.4 | 41.4 | 0.2 | 0.3 | 0.1 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 110 | Lying | Sitting | nan | nan | 2.9 | 0.0 | 15.7 | 0.2 | 0.3 | 0.1 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 111 | Lying | Standing | nan | nan | 2.4 | 0.1 | 12.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Chair_fall (**posture<90%, false negative**)

**Posture accuracy:** 0.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: 0.0%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 41 |
| **Lying** | 91 | 82 | 0 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown |
| 4 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown |
| 5 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 6 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 7 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 8 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 9 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 10 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 11 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 12 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 13 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 14 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 15 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 16 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 17 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 18 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 19 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 20 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 21 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 22 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 23 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 24 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 25 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 26 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 27 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 28 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 29 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 30 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 31 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 32 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 33 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 34 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 35 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 36 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 37 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 38 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 39 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 40 | Sitting | Unknown | nan | nan | 15.2 | 0.0 | 0.0 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 41 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 78 | Lying | Standing | nan | nan | 11.7 | 0.5 | 18.9 | 0.3 | 0.6 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 79 | Lying | Standing | nan | nan | 13.0 | 0.6 | 40.4 | 0.3 | 0.6 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 80 | Lying | Standing | nan | nan | 12.2 | 0.5 | 26.1 | 0.3 | 0.6 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 81 | Lying | Standing | nan | nan | 11.1 | 0.8 | 30.6 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 82 | Lying | Standing | nan | nan | 10.2 | 0.9 | 27.1 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 83 | Lying | Standing | nan | nan | 8.8 | 0.9 | 43.2 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Lying | Standing | nan | nan | 7.0 | 0.3 | 53.4 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Lying | Standing | nan | nan | 6.3 | 1.0 | 20.9 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Lying | Standing | nan | nan | 6.5 | 0.8 | 5.5 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Lying | Standing | nan | nan | 6.5 | 0.3 | 2.1 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Lying | Standing | nan | nan | 6.6 | 0.2 | 2.2 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Lying | Standing | nan | nan | 7.1 | 0.4 | 13.5 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Lying | Standing | nan | nan | 7.0 | 0.4 | 2.2 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Lying | Standing | nan | nan | 8.4 | 0.5 | 43.2 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Lying | Standing | nan | nan | 10.2 | 0.2 | 52.3 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Lying | Standing | nan | nan | 9.9 | 0.3 | 9.9 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Lying | Standing | nan | nan | 10.3 | 0.0 | 13.0 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Lying | Standing | nan | nan | 9.6 | 0.1 | 21.2 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Lying | Standing | nan | nan | 7.6 | 0.7 | 60.3 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Lying | Standing | nan | nan | 4.9 | 0.5 | 80.9 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Lying | Standing | nan | nan | 5.8 | 0.4 | 28.1 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Lying | Standing | nan | nan | 4.2 | 0.5 | 49.0 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Lying | Standing | nan | nan | 2.4 | 0.5 | 51.5 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 101 | Lying | Standing | nan | nan | 2.7 | 0.5 | 9.0 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 102 | Lying | Standing | nan | nan | 0.9 | 0.2 | 55.6 | 0.3 | 0.6 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 103 | Lying | Standing | 153.2 | 171.0 | 0.5 | 0.3 | 12.7 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 104 | Lying | Standing | 160.6 | 167.1 | 2.2 | 0.4 | 52.6 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 105 | Lying | Standing | 165.0 | 166.6 | 4.7 | 0.7 | 73.5 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 106 | Lying | Standing | 163.3 | 166.8 | 6.7 | 0.4 | 61.6 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 107 | Lying | Standing | 167.7 | 165.3 | 7.4 | 0.2 | 19.5 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 108 | Lying | Standing | 168.8 | 165.4 | 7.6 | 0.1 | 6.6 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 109 | Lying | Standing | 167.6 | 165.5 | 8.5 | 0.1 | 27.8 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 110 | Lying | Standing | 167.8 | 165.0 | 9.6 | 0.1 | 32.4 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 111 | Lying | Standing | 168.1 | 163.9 | 10.8 | 0.1 | 35.1 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 112 | Lying | Standing | 170.2 | 163.5 | 10.7 | 0.2 | 2.4 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 113 | Lying | Standing | 168.6 | 163.9 | 11.5 | 0.1 | 23.2 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 114 | Lying | Standing | 167.0 | 163.4 | 13.1 | 0.2 | 49.0 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 115 | Lying | Standing | 166.8 | 163.8 | 14.3 | 0.3 | 34.5 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 116 | Lying | Standing | 165.8 | 163.8 | 15.2 | 0.2 | 26.2 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 117 | Lying | Standing | 164.0 | 163.8 | 15.7 | 0.4 | 16.3 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 118 | Lying | Standing | 164.1 | 164.2 | 15.7 | 0.4 | 0.3 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 119 | Lying | Standing | 164.4 | 164.6 | 16.6 | 0.3 | 27.9 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 120 | Lying | Standing | 165.6 | 164.5 | 18.0 | 0.2 | 40.0 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Lying | Standing | 167.2 | 164.0 | 18.7 | 0.2 | 21.7 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Lying | Standing | 171.3 | 163.2 | 18.8 | 0.2 | 4.4 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Lying | Standing | 178.2 | 163.0 | 18.2 | 0.3 | 18.8 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Lying | Standing | 174.2 | 163.2 | 17.8 | 0.1 | 10.9 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Lying | Standing | 174.8 | 164.6 | 17.6 | 0.1 | 7.3 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Lying | Standing | 178.3 | 162.3 | 17.9 | 0.0 | 9.9 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Lying | Standing | 177.9 | 161.4 | 17.9 | 0.0 | 2.0 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Lying | Standing | 177.1 | 160.6 | 17.9 | 0.1 | 0.4 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Lying | Standing | 175.8 | 160.0 | 17.8 | 0.0 | 2.8 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Lying | Standing | 175.5 | 160.6 | 17.5 | 0.0 | 7.6 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Lying | Standing | 175.6 | 160.7 | 16.8 | 0.1 | 20.7 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Lying | Standing | 176.4 | 160.7 | 16.0 | 0.1 | 26.3 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Lying | Standing | 177.4 | 160.2 | 14.7 | 0.2 | 38.6 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Lying | Standing | 179.0 | 159.8 | 14.2 | 0.3 | 14.8 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Lying | Standing | 178.7 | 160.3 | 13.2 | 0.2 | 27.8 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Lying | Standing | 178.3 | 160.0 | 12.5 | 0.2 | 23.6 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Lying | Standing | 177.7 | 160.2 | 10.6 | 0.4 | 54.7 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Lying | Standing | 177.3 | 160.5 | 9.2 | 0.6 | 43.2 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Lying | Standing | 176.7 | 159.5 | 8.8 | 0.2 | 10.4 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Lying | Standing | 176.1 | 158.8 | 8.9 | 0.2 | 2.6 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Lying | Standing | 174.9 | 158.8 | 9.1 | 0.2 | 3.9 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Lying | Standing | 175.9 | 157.0 | 9.0 | 0.1 | 0.9 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Lying | Standing | 175.8 | 155.6 | 9.0 | 0.2 | 2.1 | 0.3 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Lying | Standing | 175.4 | 154.2 | 8.9 | 0.3 | 0.3 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Lying | Standing | 177.3 | 152.0 | 9.3 | 0.1 | 10.7 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Lying | Standing | 177.1 | 151.9 | 9.4 | 0.3 | 3.2 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Lying | Standing | 177.1 | 148.4 | 9.9 | 0.0 | 13.7 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 148 | Lying | Standing | 176.6 | 147.7 | 9.9 | 0.0 | 1.0 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 149 | Lying | Standing | 176.0 | 146.4 | 10.5 | 0.0 | 17.4 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 150 | Lying | Standing | 175.7 | 145.7 | 11.0 | 0.0 | 15.2 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 151 | Lying | Standing | 175.2 | 144.7 | 14.3 | 1.1 | 98.6 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 152 | Lying | Standing | 176.1 | 144.9 | 14.7 | 0.3 | 13.4 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 153 | Lying | Standing | 175.9 | 145.1 | 16.4 | 0.2 | 48.4 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 154 | Lying | Standing | 176.8 | 144.6 | 16.8 | 0.1 | 14.1 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 155 | Lying | Standing | 177.0 | 141.7 | 18.8 | 0.6 | 58.8 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 156 | Lying | Standing | 177.0 | 143.3 | 19.3 | 0.4 | 15.2 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Sitting|Standing |
| 157 | Lying | Standing | 175.6 | 136.0 | 29.1 | 2.8 | 293.2 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Sitting|Standing|Sitting |
| 158 | Lying | Standing | 171.2 | 124.4 | 49.4 | 1.9 | 606.8 | 0.2 | 0.6 | 0.3 | F | F | Standing|Sitting|Standing|Sitting|Sitting |
| 159 | Lying | Standing | 168.8 | 96.7 | 74.5 | 0.7 | 720.0 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 160 | Lying | Standing | 166.2 | 67.1 | 104.2 | 1.6 | 720.0 | 0.2 | 0.6 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 161 | Lying | Sitting | 165.6 | 66.3 | 98.9 | 0.7 | 157.3 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 162 | Lying | Sitting | 165.6 | 58.9 | 107.0 | 0.4 | 242.2 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 163 | Lying | Sitting | 167.5 | 51.0 | 120.5 | 0.7 | 404.1 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 164 | Lying | Sitting | 168.9 | 47.7 | 122.5 | 0.2 | 59.9 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 165 | Lying | Sitting | 168.3 | 44.1 | 124.9 | 0.4 | 70.7 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 166 | Lying | Sitting | 167.2 | 42.0 | 123.0 | 0.3 | 55.5 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 167 | Lying | Sitting | 167.7 | 35.1 | 120.0 | 0.6 | 89.3 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 168 | Lying | Sitting | 168.2 | 37.6 | 115.7 | 0.1 | 129.6 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 169 | Lying | Sitting | 169.9 | 40.4 | 120.0 | 0.9 | 130.0 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 170 | Lying | Sitting | 166.1 | 45.9 | 112.4 | 1.5 | 228.9 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 171 | Lying | Sitting | 164.7 | 44.9 | 114.0 | 0.2 | 49.2 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 172 | Lying | Sitting | 169.5 | 43.0 | 113.1 | 0.8 | 27.5 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 173 | Lying | Sitting | 166.9 | 41.5 | 114.0 | 0.1 | 26.4 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 174 | Lying | Sitting | 162.5 | 36.4 | 118.1 | 0.0 | 121.0 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 175 | Lying | Sitting | 165.8 | 35.1 | 116.6 | 0.4 | 42.9 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 176 | Lying | Sitting | 165.5 | 38.6 | 113.9 | 1.1 | 82.6 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 177 | Lying | Sitting | 168.4 | 43.0 | 105.9 | 1.1 | 236.7 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 178 | Lying | Sitting | 171.7 | 34.4 | 110.8 | 1.0 | 145.3 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 179 | Lying | Sitting | 174.0 | 35.4 | 107.9 | 0.2 | 86.4 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 180 | Lying | Sitting | 174.6 | 36.4 | 108.1 | 0.2 | 5.3 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 181 | Lying | Sitting | 174.9 | 36.6 | 107.8 | 0.2 | 9.9 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 182 | Lying | Sitting | 175.9 | 36.7 | 107.3 | 0.2 | 14.3 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 183 | Lying | Sitting | 169.4 | 36.9 | 97.1 | 1.5 | 303.3 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 184 | Lying | Sitting | 163.4 | 47.9 | 93.5 | 1.5 | 109.9 | 0.2 | 0.6 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 185 | Lying | Sitting | 162.8 | 54.0 | 87.9 | 1.1 | 166.4 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 186 | Lying | Sitting | 162.8 | 59.8 | 92.6 | 1.2 | 141.3 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 187 | Lying | Sitting | 157.2 | 67.3 | 88.2 | 1.8 | 131.8 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 188 | Lying | Sitting | 160.4 | 117.3 | 64.6 | 2.6 | 707.6 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 189 | Lying | Sitting | 158.6 | 134.5 | 63.9 | 0.5 | 20.0 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 190 | Lying | Sitting | 164.5 | 107.2 | 57.0 | 0.6 | 207.1 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 191 | Lying | Sitting | 161.6 | 142.8 | 4.9 | 5.7 | 720.0 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 192 | Lying | Sitting | 167.6 | 135.7 | 6.6 | 2.3 | 50.4 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 193 | Lying | Sitting | 173.4 | 147.1 | 12.0 | 6.6 | 159.8 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 194 | Lying | Sitting | 171.7 | 149.2 | 15.0 | 2.6 | 91.3 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 195 | Lying | Sitting | 169.5 | 149.8 | 13.8 | 2.1 | 35.7 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 196 | Lying | Sitting | 170.0 | 148.1 | 8.2 | 1.2 | 167.5 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 197 | Lying | Standing | 170.0 | 150.8 | 3.4 | 0.9 | 145.2 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 198 | Lying | Standing | 168.4 | 149.5 | 1.3 | 0.5 | 63.4 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 199 | Lying | Standing | 167.5 | 146.5 | 0.0 | 0.1 | 36.5 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 200 | Lying | Standing | 164.2 | 146.1 | 1.4 | 0.2 | 40.2 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 201 | Lying | Standing | 148.2 | 139.7 | 2.4 | 0.1 | 29.1 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 202 | Lying | Standing | 140.3 | 137.3 | 2.7 | 0.2 | 9.7 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 203 | Lying | Standing | 132.9 | 135.9 | 3.0 | 0.2 | 8.8 | 0.2 | 0.6 | 0.2 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 204 | Lying | Standing | 125.0 | 133.2 | 2.5 | 0.6 | 15.4 | 0.2 | 0.6 | 0.2 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 205 | Lying | Sitting | 122.4 | 133.3 | 2.4 | 0.7 | 2.4 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 206 | Lying | Sitting | 115.4 | 131.4 | 2.3 | 1.3 | 2.5 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 207 | Lying | Sitting | 132.0 | 137.4 | 1.5 | 0.9 | 23.6 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 208 | Lying | Sitting | 128.0 | 134.3 | 0.3 | 0.7 | 35.9 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 209 | Lying | Sitting | 119.9 | 127.2 | 0.2 | 0.4 | 1.7 | 0.2 | 0.6 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 210 | Lying | Sitting | 115.7 | 124.5 | 0.5 | 1.2 | 7.6 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 211 | Lying | Sitting | 102.8 | 114.7 | 0.6 | 1.4 | 2.6 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 212 | Lying | Sitting | 93.4 | 103.3 | 1.2 | 1.5 | 19.0 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 213 | Lying | Sitting | 96.8 | 105.7 | 2.6 | 0.8 | 42.5 | 0.1 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 214 | Lying | Sitting | 86.7 | 92.9 | 4.4 | 1.4 | 54.0 | 0.1 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 215 | Lying | Sitting | 64.0 | 74.0 | 4.1 | 2.0 | 9.6 | 0.1 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 216 | Lying | Sitting | 47.9 | 62.1 | 1.5 | 0.6 | 77.1 | 0.1 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 217 | Lying | Sitting | 40.0 | 58.0 | 1.5 | 0.2 | 0.1 | 0.1 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 218 | Lying | Sitting | 38.8 | 55.9 | 3.6 | 0.7 | 60.6 | 0.1 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 219 | Lying | Sitting | 39.8 | 56.3 | 0.1 | 1.6 | 104.7 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 220 | Lying | Sitting | 43.5 | 59.1 | 0.2 | 0.6 | 2.9 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 221 | Lying | Sitting | 49.1 | 64.6 | 1.8 | 0.7 | 49.1 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 222 | Lying | Sitting | 60.6 | 72.0 | 0.9 | 0.4 | 27.7 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 223 | Lying | Sitting | 79.1 | 83.5 | 0.9 | 0.2 | 1.2 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 224 | Lying | Sitting | 87.1 | 87.9 | 2.0 | 0.2 | 33.3 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 225 | Lying | Sitting | 94.3 | 91.5 | 3.0 | 0.2 | 27.4 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 226 | Lying | Sitting | 98.9 | 98.3 | 3.1 | 0.5 | 3.1 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 227 | Lying | Sitting | 100.1 | 98.9 | 2.6 | 0.2 | 14.3 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 228 | Lying | Sitting | 99.5 | 97.0 | 2.2 | 0.7 | 11.2 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 229 | Lying | Sitting | 102.5 | 99.6 | 2.7 | 0.4 | 13.4 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 230 | Lying | Sitting | 104.8 | 101.0 | 2.7 | 0.5 | 0.6 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 231 | Lying | Sitting | 110.0 | 102.8 | 2.6 | 0.4 | 3.2 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 232 | Lying | Sitting | 110.8 | 103.2 | 2.5 | 0.5 | 1.7 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 233 | Lying | Sitting | 110.4 | 105.5 | 2.1 | 0.3 | 11.2 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 234 | Lying | Sitting | 107.5 | 107.2 | 1.1 | 0.3 | 30.7 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 235 | Lying | Sitting | 111.4 | 110.1 | 0.9 | 0.3 | 7.6 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 236 | Lying | Sitting | 110.5 | 103.9 | 2.3 | 0.7 | 43.9 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 237 | Lying | Sitting | 102.0 | 99.8 | 2.6 | 0.3 | 7.7 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 238 | Lying | Sitting | 103.8 | 99.5 | 3.3 | 0.4 | 22.5 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 239 | Lying | Sitting | 102.0 | 96.7 | 2.0 | 0.4 | 40.1 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 240 | Lying | Sitting | 100.4 | 90.5 | 1.5 | 0.2 | 14.8 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 241 | Lying | Sitting | 103.1 | 91.6 | 0.6 | 0.1 | 25.6 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 242 | Lying | Sitting | 109.6 | 98.8 | 0.9 | 0.1 | 8.5 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 243 | Lying | Sitting | 110.2 | 100.1 | 1.0 | 0.1 | 2.6 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 244 | Lying | Sitting | 110.1 | 100.1 | 1.0 | 0.0 | 1.0 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 245 | Lying | Sitting | 114.6 | 105.2 | 1.0 | 0.0 | 0.9 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 246 | Lying | Sitting | 115.1 | 105.5 | 1.2 | 0.0 | 5.4 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 247 | Lying | Sitting | 127.0 | 115.1 | 1.5 | 0.0 | 8.2 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 248 | Lying | Sitting | 130.4 | 119.0 | 2.0 | 0.1 | 15.3 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 249 | Lying | Sitting | 126.4 | 115.2 | 2.3 | 0.1 | 10.9 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 250 | Lying | Sitting | 127.4 | 116.0 | 2.5 | 0.0 | 5.9 | 0.2 | 0.6 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Fall_and_lie (**posture<90%**)

**Posture accuracy:** 29.6%

**Per-class accuracy:**

- Standing: 70.7%
- Sitting: nan%
- Lying: 23.5%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 29 | 0 | 6 | 6 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 112 | 0 | 65 | 100 |

**Fall detection:** TP (latency 16 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Standing | Unknown | nan | nan | 167.6 | 0.0 | 0.0 | 0.1 | 0.1 | 0.4 | T | F | Unknown|Unknown|Lying |
| 4 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Lying|Unknown |
| 5 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Lying|Unknown|Unknown |
| 6 | Standing | Unknown | nan | nan | 179.2 | 0.3 | 116.1 | 0.1 | 0.1 | 0.4 | T | F | Unknown|Lying|Unknown|Unknown|Lying |
| 7 | Standing | Lying | nan | nan | 177.9 | 1.6 | 40.5 | 0.1 | 0.1 | 0.4 | T | F | Lying|Unknown|Unknown|Lying|Lying |
| 8 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Lying|Lying|Unknown |
| 9 | Standing | Lying | nan | nan | 0.5 | 7.6 | 720.0 | 0.2 | 0.2 | 0.3 | T | F | Unknown|Lying|Lying|Unknown|Standing |
| 10 | Standing | Lying | nan | nan | 0.2 | 0.2 | 10.1 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Unknown|Standing|Standing |
| 11 | Standing | Lying | nan | nan | 0.1 | 0.3 | 1.1 | 0.2 | 0.2 | 0.3 | T | F | Lying|Unknown|Standing|Standing|Standing |
| 12 | Standing | Lying | nan | nan | 0.2 | 0.3 | 1.5 | 0.2 | 0.2 | 0.3 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 143 | Lying | Standing | nan | nan | 11.0 | 0.2 | 45.1 | 0.3 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Lying | Standing | nan | nan | 9.7 | 0.5 | 39.5 | 0.3 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Lying | Standing | nan | nan | 8.5 | 0.3 | 36.6 | 0.3 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Lying | Standing | nan | nan | 7.3 | 0.1 | 35.7 | 0.3 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Lying | Standing | nan | nan | 8.0 | 0.1 | 20.9 | 0.3 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 148 | Lying | Standing | nan | nan | 8.1 | 0.6 | 1.9 | 0.3 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 149 | Lying | Standing | nan | nan | 8.2 | 0.3 | 4.8 | 0.2 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 150 | Lying | Standing | nan | nan | 6.3 | 0.7 | 58.2 | 0.3 | 0.3 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 151 | Lying | Standing | nan | nan | 4.9 | 0.5 | 40.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 152 | Lying | Standing | nan | nan | 5.8 | 0.7 | 24.9 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 153 | Lying | Standing | nan | nan | 4.9 | 0.6 | 26.5 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 154 | Lying | Standing | nan | nan | 7.6 | 2.2 | 81.5 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 155 | Lying | Standing | nan | nan | 8.8 | 0.2 | 35.0 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 156 | Lying | Standing | nan | nan | 10.8 | 0.7 | 61.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 157 | Lying | Standing | nan | nan | 8.3 | 0.6 | 75.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 158 | Lying | Standing | nan | nan | 7.8 | 0.7 | 16.6 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 159 | Lying | Standing | nan | nan | 8.7 | 0.1 | 28.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 160 | Lying | Standing | nan | nan | 10.2 | 0.3 | 45.5 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 161 | Lying | Standing | nan | nan | 10.7 | 0.4 | 14.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 162 | Lying | Standing | nan | nan | 12.0 | 0.2 | 39.6 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 163 | Lying | Standing | nan | nan | 14.2 | 0.2 | 65.9 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 164 | Lying | Standing | nan | nan | 13.8 | 0.7 | 14.2 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 165 | Lying | Standing | nan | nan | 13.8 | 1.1 | 2.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 166 | Lying | Standing | nan | nan | 13.8 | 0.7 | 2.0 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 167 | Lying | Standing | nan | nan | 13.8 | 1.5 | 1.0 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 168 | Lying | Standing | nan | nan | 15.0 | 1.3 | 36.2 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 169 | Lying | Standing | nan | nan | 15.2 | 0.3 | 6.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 170 | Lying | Standing | nan | nan | 14.4 | 0.6 | 24.0 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 171 | Lying | Standing | nan | nan | 14.0 | 0.4 | 13.9 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 172 | Lying | Standing | nan | nan | 12.1 | 0.6 | 56.3 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 173 | Lying | Standing | nan | nan | 11.3 | 1.3 | 25.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 174 | Lying | Standing | nan | nan | 9.7 | 0.0 | 45.9 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 175 | Lying | Standing | nan | nan | 10.2 | 0.7 | 14.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 176 | Lying | Standing | nan | nan | 10.0 | 0.6 | 5.6 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 177 | Lying | Standing | nan | nan | 9.4 | 0.3 | 16.6 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 178 | Lying | Standing | nan | nan | 8.2 | 0.4 | 37.6 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 179 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 180 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 181 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 182 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 183 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 184 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 185 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 186 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 187 | Lying | Standing | nan | nan | 9.0 | 0.0 | 2.6 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 188 | Lying | Standing | nan | nan | 9.3 | 0.4 | 9.6 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 189 | Lying | Standing | nan | nan | 8.8 | 0.1 | 14.5 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 190 | Lying | Standing | nan | nan | 8.3 | 0.5 | 13.7 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 191 | Lying | Standing | nan | nan | 7.6 | 0.3 | 23.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 192 | Lying | Standing | nan | nan | 6.8 | 0.4 | 23.7 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 193 | Lying | Standing | nan | nan | 6.3 | 0.1 | 13.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 194 | Lying | Standing | nan | nan | 6.8 | 0.2 | 13.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 195 | Lying | Standing | nan | nan | 7.9 | 0.6 | 33.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 196 | Lying | Standing | nan | nan | 8.3 | 0.5 | 13.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 197 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 198 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 199 | Lying | Standing | nan | nan | 9.9 | 0.3 | 15.3 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Unknown|Unknown|Standing |
| 200 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Standing|Unknown |
| 201 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 202 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 203 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 204 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 205 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 206 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 207 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 208 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 209 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 210 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 211 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 212 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 213 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 214 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 215 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 216 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 217 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 218 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 219 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 220 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 221 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 222 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 223 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 224 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 225 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 226 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 227 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 228 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 229 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 230 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 231 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 232 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 233 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 234 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 235 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 236 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 237 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 238 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 239 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 240 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 241 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 242 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 243 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 244 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 245 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 246 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 247 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 248 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 249 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 250 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 251 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 252 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 253 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 254 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 255 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 256 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 257 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 258 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 259 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 260 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 261 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 262 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 263 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 264 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 265 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 266 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 267 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 268 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 269 | Lying | Unknown | nan | nan | 14.1 | 0.0 | 1.8 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 270 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 271 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 272 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 273 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 274 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 275 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 276 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 277 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 278 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 279 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 280 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 281 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 282 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 283 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 284 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 285 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 286 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 287 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 288 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 289 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 290 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 291 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 292 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 293 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 294 | Lying | Unknown | nan | nan | 12.6 | 0.1 | 1.8 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 295 | Lying | Unknown | nan | nan | 12.6 | 0.0 | 1.8 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 296 | Lying | Unknown | nan | nan | 11.8 | 0.3 | 23.5 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 297 | Lying | Unknown | nan | nan | 12.0 | 0.1 | 6.1 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 298 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 299 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 300 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 301 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 302 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 303 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 304 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 305 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 306 | Lying | Unknown | nan | nan | 10.4 | 0.1 | 5.4 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 307 | Lying | Unknown | nan | nan | 11.1 | 0.6 | 18.7 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 308 | Lying | Unknown | nan | nan | 10.5 | 0.4 | 18.0 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 309 | Lying | Unknown | nan | nan | 10.5 | 0.2 | 1.1 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 310 | Lying | Standing | nan | nan | 9.6 | 0.7 | 25.5 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 311 | Lying | Standing | nan | nan | 9.8 | 1.0 | 4.9 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 312 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 313 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 314 | Lying | Standing | nan | nan | 12.0 | 0.3 | 21.8 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Unknown|Unknown|Standing |
| 315 | Lying | Standing | nan | nan | 13.0 | 1.9 | 29.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Unknown|Unknown|Standing|Standing |
| 316 | Lying | Standing | nan | nan | 12.2 | 0.3 | 22.1 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 317 | Lying | Standing | nan | nan | 12.2 | 0.1 | 0.3 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 318 | Lying | Standing | nan | nan | 12.1 | 1.1 | 3.3 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 319 | Lying | Standing | nan | nan | 12.7 | 0.3 | 16.5 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 320 | Lying | Standing | nan | nan | 12.7 | 0.2 | 1.3 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 321 | Lying | Standing | nan | nan | 13.4 | 0.1 | 20.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 322 | Lying | Standing | nan | nan | 14.0 | 0.3 | 17.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 323 | Lying | Standing | nan | nan | 13.6 | 0.6 | 12.2 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 324 | Lying | Standing | nan | nan | 12.7 | 0.7 | 26.5 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 325 | Lying | Standing | nan | nan | 11.7 | 1.0 | 30.7 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 326 | Lying | Standing | nan | nan | 10.5 | 0.5 | 34.0 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 327 | Lying | Standing | nan | nan | 10.4 | 0.1 | 4.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 328 | Lying | Standing | nan | nan | 9.9 | 0.3 | 13.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 329 | Lying | Standing | nan | nan | 10.8 | 0.2 | 26.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 330 | Lying | Standing | nan | nan | 10.7 | 0.1 | 2.9 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 331 | Lying | Standing | nan | nan | 10.0 | 0.9 | 22.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 332 | Lying | Standing | nan | nan | 10.2 | 0.3 | 5.2 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 333 | Lying | Standing | nan | nan | 10.2 | 0.2 | 1.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 334 | Lying | Standing | nan | nan | 10.3 | 0.5 | 1.5 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 335 | Lying | Standing | nan | nan | 10.5 | 1.1 | 7.5 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 336 | Lying | Standing | nan | nan | 11.4 | 0.2 | 26.0 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 337 | Lying | Standing | nan | nan | 11.9 | 0.3 | 16.1 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 338 | Lying | Standing | nan | nan | 12.4 | 0.5 | 14.6 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 339 | Lying | Standing | nan | nan | 12.2 | 0.4 | 7.3 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 340 | Lying | Standing | nan | nan | 12.8 | 0.3 | 17.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 341 | Lying | Standing | nan | nan | 13.3 | 0.6 | 17.4 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 342 | Lying | Standing | nan | nan | 13.1 | 0.3 | 7.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 343 | Lying | Standing | nan | nan | 13.6 | 0.2 | 16.7 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 344 | Lying | Standing | nan | nan | 15.2 | 1.1 | 48.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 345 | Lying | Standing | nan | nan | 14.5 | 0.5 | 22.5 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 346 | Lying | Standing | nan | nan | 15.3 | 0.6 | 25.6 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 347 | Lying | Standing | nan | nan | 15.6 | 0.3 | 6.6 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 348 | Lying | Standing | nan | nan | 14.4 | 0.8 | 33.5 | 0.3 | 0.3 | -0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 349 | Lying | Standing | nan | nan | 15.7 | 1.7 | 36.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 350 | Lying | Standing | nan | nan | 15.6 | 1.6 | 2.2 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 351 | Lying | Standing | nan | nan | 16.3 | 0.5 | 20.5 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 352 | Lying | Standing | nan | nan | 16.3 | 0.6 | 0.0 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 353 | Lying | Standing | nan | nan | 16.2 | 0.1 | 0.8 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 354 | Lying | Standing | nan | nan | 14.9 | 0.4 | 40.1 | 0.3 | 0.3 | -0.0 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Far_fall

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 47 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 49 | 0 |

**Fall detection:** TP (latency 53 frames)

**Mismatched frames:**

_None_

---

## Occluded_fall

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 50 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 88 | 0 |

**Fall detection:** TP (latency 52 frames)

**Mismatched frames:**

_None_

---

## Off_axis_fall

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 31 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 60 | 0 |

**Fall detection:** TP (latency 16 frames)

**Mismatched frames:**

_None_

---

## Side_fall

**Posture accuracy:** 95.3%

**Per-class accuracy:**

- Standing: 81.2%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 26 | 0 | 0 | 6 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 95 | 0 |

**Fall detection:** TP (latency 67 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Standing | Unknown | 178.7 | 164.4 | 7.9 | 0.0 | 0.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing |
| 4 | Standing | Unknown | 178.6 | 164.6 | 8.3 | 0.1 | 12.4 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing |
| 5 | Standing | Unknown | 178.5 | 165.2 | 8.7 | 0.1 | 13.7 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 6 | Standing | Unknown | 178.3 | 165.1 | 8.9 | 0.0 | 4.2 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |

---

## Slow_fall

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 65 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 80 | 0 |

**Fall detection:** TP (latency 27 frames)

**Mismatched frames:**

_None_

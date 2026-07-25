# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| normal | 89.4% | TP (latency 43 frames) | **posture<90%** |

---

## normal (**posture<90%**)

**Posture accuracy:** 89.4%

**Per-class accuracy:**

- Standing: 73.3%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 88 | 14 | 18 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 181 | 0 |

**Fall detection:** TP (latency 43 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 89 | Standing | Sitting | 128.8 | 129.2 | 4.0 | 3.4 | 163.6 | 0.4 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 90 | Standing | Sitting | 119.0 | 122.1 | 5.2 | 3.1 | 73.5 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 91 | Standing | Sitting | 109.0 | 116.8 | 7.0 | 2.5 | 110.3 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 92 | Standing | Sitting | 108.0 | 113.8 | 10.1 | 3.6 | 183.8 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 93 | Standing | Sitting | 95.2 | 103.1 | 10.4 | 3.8 | 16.1 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 94 | Standing | Sitting | 69.5 | 83.1 | 12.7 | 4.4 | 140.2 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 95 | Standing | Sitting | 61.1 | 70.1 | 12.5 | 4.6 | 15.2 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 96 | Standing | Sitting | 73.7 | 81.2 | 14.6 | 0.4 | 130.3 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 97 | Standing | Sitting | 60.7 | 66.1 | 15.6 | 3.4 | 60.1 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 98 | Standing | Sitting | 51.4 | 53.7 | 17.2 | 3.8 | 93.6 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Standing | Sitting | 48.4 | 48.1 | 18.4 | 2.2 | 69.8 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Standing | Sitting | 51.4 | 53.1 | 21.1 | 0.7 | 164.7 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Standing | Sitting | 44.9 | 51.7 | 27.7 | 0.6 | 394.5 | 0.2 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 102 | Standing | Sitting | 45.6 | 55.9 | 32.6 | 0.5 | 295.3 | 0.2 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Lying |
| 103 | Standing | Lying | 44.1 | 55.9 | 35.6 | 1.2 | 180.0 | 0.2 | 0.7 | 0.1 | F | F | Sitting|Sitting|Sitting|Lying|Lying |
| 104 | Standing | Lying | 65.1 | 72.6 | 38.3 | 1.7 | 165.0 | 0.2 | 0.7 | 0.1 | F | F | Sitting|Sitting|Lying|Lying|Lying |
| 105 | Standing | Lying | 54.4 | 60.5 | 39.2 | 1.6 | 49.2 | 0.2 | 0.7 | 0.1 | F | F | Sitting|Lying|Lying|Lying|Lying |
| 106 | Standing | Lying | 92.7 | 115.7 | 44.1 | 4.9 | 295.1 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 107 | Standing | Lying | 64.0 | 72.5 | 48.2 | 0.6 | 249.4 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 108 | Standing | Lying | 80.3 | 85.2 | 50.6 | 2.4 | 139.4 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 109 | Standing | Lying | 69.5 | 77.4 | 53.6 | 1.1 | 181.3 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 110 | Standing | Lying | 59.1 | 92.8 | 56.6 | 0.9 | 180.6 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 111 | Standing | Lying | 61.6 | 91.7 | 57.8 | 0.8 | 72.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 112 | Standing | Lying | 61.0 | 92.1 | 60.0 | 0.4 | 131.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 113 | Standing | Lying | 63.6 | 90.4 | 59.2 | 0.6 | 49.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 114 | Standing | Lying | 67.1 | 96.8 | 58.9 | 1.2 | 14.4 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 115 | Standing | Lying | 63.1 | 97.8 | 63.7 | 0.5 | 289.4 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 116 | Standing | Lying | 70.7 | 101.0 | 64.2 | 1.0 | 27.8 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 117 | Standing | Lying | 69.7 | 96.4 | 66.3 | 0.6 | 123.7 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 118 | Standing | Lying | 62.4 | 91.8 | 67.9 | 0.4 | 96.5 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 119 | Standing | Lying | 66.3 | 98.8 | 70.1 | 2.7 | 132.3 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 120 | Standing | Lying | 67.3 | 98.4 | 70.4 | 0.3 | 17.9 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |

---

## old (**false positive**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 420 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 121 | 0 |

**Fall detection:** FP frames [475, 476, 477, 478, 479]

**Mismatched frames:**

_None_

---

## normal (**posture<90%**)

**Posture accuracy:** 89.4%

**Per-class accuracy:**

- Standing: 73.3%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 88 | 14 | 18 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 181 | 0 |

**Fall detection:** TP (latency 43 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 89 | Standing | Sitting | 128.8 | 129.2 | 4.0 | 3.4 | 163.6 | 0.4 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 90 | Standing | Sitting | 119.0 | 122.1 | 5.2 | 3.1 | 73.5 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 91 | Standing | Sitting | 109.0 | 116.8 | 7.0 | 2.5 | 110.3 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 92 | Standing | Sitting | 108.0 | 113.8 | 10.1 | 3.6 | 183.8 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 93 | Standing | Sitting | 95.2 | 103.1 | 10.4 | 3.8 | 16.1 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 94 | Standing | Sitting | 69.5 | 83.1 | 12.7 | 4.4 | 140.2 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 95 | Standing | Sitting | 61.1 | 70.1 | 12.5 | 4.6 | 15.2 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 96 | Standing | Sitting | 73.7 | 81.2 | 14.6 | 0.4 | 130.3 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 97 | Standing | Sitting | 60.7 | 66.1 | 15.6 | 3.4 | 60.1 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 98 | Standing | Sitting | 51.4 | 53.7 | 17.2 | 3.8 | 93.6 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Standing | Sitting | 48.4 | 48.1 | 18.4 | 2.2 | 69.8 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Standing | Sitting | 51.4 | 53.1 | 21.1 | 0.7 | 164.7 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Standing | Sitting | 44.9 | 51.7 | 27.7 | 0.6 | 394.5 | 0.2 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 102 | Standing | Sitting | 45.6 | 55.9 | 32.6 | 0.5 | 295.3 | 0.2 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Lying |
| 103 | Standing | Lying | 44.1 | 55.9 | 35.6 | 1.2 | 180.0 | 0.2 | 0.7 | 0.1 | F | F | Sitting|Sitting|Sitting|Lying|Lying |
| 104 | Standing | Lying | 65.1 | 72.6 | 38.3 | 1.7 | 165.0 | 0.2 | 0.7 | 0.1 | F | F | Sitting|Sitting|Lying|Lying|Lying |
| 105 | Standing | Lying | 54.4 | 60.5 | 39.2 | 1.6 | 49.2 | 0.2 | 0.7 | 0.1 | F | F | Sitting|Lying|Lying|Lying|Lying |
| 106 | Standing | Lying | 92.7 | 115.7 | 44.1 | 4.9 | 295.1 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 107 | Standing | Lying | 64.0 | 72.5 | 48.2 | 0.6 | 249.4 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 108 | Standing | Lying | 80.3 | 85.2 | 50.6 | 2.4 | 139.4 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 109 | Standing | Lying | 69.5 | 77.4 | 53.6 | 1.1 | 181.3 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 110 | Standing | Lying | 59.1 | 92.8 | 56.6 | 0.9 | 180.6 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 111 | Standing | Lying | 61.6 | 91.7 | 57.8 | 0.8 | 72.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 112 | Standing | Lying | 61.0 | 92.1 | 60.0 | 0.4 | 131.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 113 | Standing | Lying | 63.6 | 90.4 | 59.2 | 0.6 | 49.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 114 | Standing | Lying | 67.1 | 96.8 | 58.9 | 1.2 | 14.4 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 115 | Standing | Lying | 63.1 | 97.8 | 63.7 | 0.5 | 289.4 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 116 | Standing | Lying | 70.7 | 101.0 | 64.2 | 1.0 | 27.8 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 117 | Standing | Lying | 69.7 | 96.4 | 66.3 | 0.6 | 123.7 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 118 | Standing | Lying | 62.4 | 91.8 | 67.9 | 0.4 | 96.5 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 119 | Standing | Lying | 66.3 | 98.8 | 70.1 | 2.7 | 132.3 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 120 | Standing | Lying | 67.3 | 98.4 | 70.4 | 0.3 | 17.9 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |

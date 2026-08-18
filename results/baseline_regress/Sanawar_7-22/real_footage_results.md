# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| Fall_Curled | 100.0% | FN | **false negative** |
| Fast_Sit | 0.0% | - | **posture<90%** |
| Lying_legs_straight | 100.0% | - |  |
| Lying_straight | 100.0% | - |  |
| newTest | 79.2% | TP (latency 71 frames) | **posture<90%** |
| Normal_Fall_1 | 77.8% | FP frames [151] | **posture<90%, false positive** |
| Normal_Fall_2 | 100.0% | TP (latency 71 frames) |  |
| normal | 88.0% | TP (latency 75 frames) | **posture<90%** |
| Off_axis | 100.0% | - |  |
| old | 97.0% | TP (latency 106 frames) |  |
| Sit_1 | 65.6% | - | **posture<90%** |
| Sit_2 | 65.6% | - | **posture<90%** |
| Sit_3 | 0.0% | - | **posture<90%** |
| Standing_1 | 100.0% | - |  |
| Standing_2 | 100.0% | - |  |
| Standing_3 | 100.0% | - |  |

---

## Fall_Curled (**false negative**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 29 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 16 | 0 |

**Fall detection:** FN

**Mismatched frames:**

_None_

---

## Fast_Sit (**posture<90%**)

**Posture accuracy:** 0.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: 0.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 31 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 30 | Sitting | Standing | nan | nan | 8.6 | 0.6 | 5.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 31 | Sitting | Standing | nan | nan | 4.9 | 1.2 | 109.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 32 | Sitting | Standing | nan | nan | 0.4 | 1.5 | 136.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 33 | Sitting | Standing | nan | nan | 2.5 | 0.9 | 64.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 34 | Sitting | Standing | nan | nan | 4.2 | 1.1 | 50.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 35 | Sitting | Standing | nan | nan | 6.9 | 1.0 | 82.4 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 36 | Sitting | Standing | nan | nan | 5.5 | 0.7 | 42.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 37 | Sitting | Standing | nan | nan | 8.9 | 1.8 | 99.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 38 | Sitting | Standing | nan | nan | 10.4 | 1.5 | 46.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 39 | Sitting | Standing | nan | nan | 15.0 | 1.5 | 137.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 40 | Sitting | Standing | nan | nan | 13.1 | 1.2 | 57.4 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 41 | Sitting | Standing | nan | nan | 11.9 | 0.9 | 33.4 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 42 | Sitting | Standing | nan | nan | 12.5 | 2.5 | 17.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 43 | Sitting | Standing | nan | nan | 7.0 | 1.0 | 166.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 44 | Sitting | Standing | nan | nan | 7.5 | 1.7 | 14.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 45 | Sitting | Standing | nan | nan | 5.9 | 1.1 | 46.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 46 | Sitting | Standing | nan | nan | 1.9 | 1.4 | 122.0 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 47 | Sitting | Standing | nan | nan | 1.7 | 1.4 | 3.4 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 48 | Sitting | Standing | nan | nan | 5.9 | 0.3 | 124.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 49 | Sitting | Standing | nan | nan | 11.0 | 0.3 | 151.8 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 50 | Sitting | Standing | nan | nan | 15.6 | 0.5 | 137.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 51 | Sitting | Standing | nan | nan | 16.0 | 1.0 | 14.6 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 52 | Sitting | Standing | nan | nan | 19.2 | 0.5 | 95.8 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 53 | Sitting | Standing | nan | nan | 21.4 | 0.4 | 65.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 54 | Sitting | Standing | nan | nan | 21.4 | 0.2 | 0.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 55 | Sitting | Standing | nan | nan | 22.8 | 0.2 | 40.9 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 56 | Sitting | Standing | nan | nan | 24.1 | 0.2 | 37.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 57 | Sitting | Standing | nan | nan | 24.3 | 0.3 | 6.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 58 | Sitting | Standing | nan | nan | 26.6 | 0.7 | 69.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 59 | Sitting | Standing | nan | nan | 29.3 | 0.5 | 81.8 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 60 | Sitting | Standing | nan | nan | 28.7 | 0.1 | 20.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Lying_legs_straight

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 120 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Lying_straight

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 147 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## newTest (**posture<90%**)

**Posture accuracy:** 79.2%

**Per-class accuracy:**

- Standing: 76.7%
- Sitting: nan%
- Lying: 91.7%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 1841 | 416 | 48 | 95 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 17 | 23 | 440 | 0 |

**Fall detection:** TP (latency 71 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown |
| 4 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown |
| 5 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 6 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 7 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 8 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 9 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 10 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 11 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 12 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 13 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 14 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 15 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 16 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 17 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 18 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 19 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 20 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 21 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 22 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 23 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 24 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 25 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 26 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 27 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 28 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 29 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 30 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 31 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 32 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 33 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 34 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 35 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 36 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 37 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 38 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 39 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 40 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 41 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 42 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 43 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 44 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 45 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 46 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 47 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 48 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 49 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 50 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 51 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 52 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 53 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 54 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 55 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 56 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 57 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 58 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 59 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 60 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 61 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 62 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 63 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 64 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 65 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 66 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 67 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 68 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 69 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 70 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 71 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 72 | Standing | Unknown | nan | nan | 7.6 | 0.0 | 0.0 | 0.7 | 0.7 | 0.2 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 73 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 74 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 75 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 76 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 77 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 78 | Standing | Unknown | nan | nan | 9.4 | 1.2 | 18.2 | 0.6 | 0.6 | 0.3 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 79 | Standing | Unknown | nan | nan | 9.4 | 0.2 | 3.1 | 0.6 | 0.6 | 0.3 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 80 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Standing|Unknown |
| 81 | Standing | Unknown | nan | nan | 14.2 | 1.4 | 144.0 | 0.5 | 0.5 | 0.3 | T | F | Unknown|Standing|Standing|Unknown|Standing |
| 82 | Standing | Unknown | nan | nan | 12.4 | 2.2 | 104.3 | 0.5 | 0.5 | 0.3 | T | F | Standing|Standing|Unknown|Standing|Standing |
| 83 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Standing|Standing|Unknown |
| 84 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Standing|Unknown|Unknown |
| 85 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 86 | Standing | Unknown | nan | nan | 18.0 | 1.1 | 82.7 | 0.6 | 0.6 | 0.3 | T | F | Standing|Unknown|Unknown|Unknown|Standing |
| 87 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 88 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 89 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 90 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 91 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 92 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 93 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 94 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 95 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 96 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 97 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 98 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 99 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 100 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 101 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 102 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 103 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 104 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 105 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 106 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 107 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 108 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 109 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 110 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 111 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 112 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 113 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 114 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 115 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 116 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 117 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 118 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 119 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 120 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 121 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 122 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 123 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 124 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 125 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 126 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 127 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 128 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 129 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 130 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 131 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 132 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 133 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 134 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 135 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 136 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 137 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 138 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 139 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 140 | Standing | Lying | nan | nan | 2.6 | 1.1 | 17.1 | 1.2 | 1.2 | -0.1 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 141 | Standing | Lying | nan | nan | 2.7 | 0.7 | 6.2 | 1.2 | 1.2 | -0.1 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 142 | Standing | Lying | nan | nan | 2.7 | 0.3 | 1.9 | 1.2 | 1.2 | -0.1 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 143 | Standing | Lying | nan | nan | 2.8 | 0.3 | 5.2 | 1.2 | 1.2 | -0.1 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 198 | Standing | Sitting | nan | 174.9 | 0.2 | 0.1 | 4.8 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 199 | Standing | Sitting | nan | 175.3 | 0.2 | 0.1 | 3.4 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 200 | Standing | Sitting | nan | 175.7 | 0.1 | 0.3 | 8.3 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 201 | Standing | Sitting | nan | 176.1 | 0.1 | 0.3 | 0.3 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 202 | Standing | Sitting | nan | 176.5 | 0.1 | 0.1 | 4.0 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 203 | Standing | Sitting | nan | 176.9 | 0.0 | 0.2 | 6.2 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 204 | Standing | Sitting | nan | 176.8 | 0.0 | 0.1 | 0.8 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 205 | Standing | Sitting | nan | 177.0 | 0.0 | 0.1 | 0.4 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 206 | Standing | Sitting | nan | 177.1 | 0.1 | 0.1 | 6.7 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 207 | Standing | Sitting | nan | 177.4 | 0.2 | 0.1 | 3.9 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 208 | Standing | Sitting | nan | 177.5 | 0.4 | 0.1 | 8.7 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 209 | Standing | Sitting | nan | 177.7 | 0.5 | 0.2 | 7.6 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 210 | Standing | Sitting | nan | 178.1 | 0.7 | 0.6 | 11.8 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 211 | Standing | Sitting | nan | 178.1 | 0.8 | 0.6 | 4.6 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 212 | Standing | Sitting | nan | 178.0 | 0.8 | 0.4 | 0.7 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 213 | Standing | Sitting | nan | 178.2 | 0.8 | 0.2 | 2.8 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 214 | Standing | Sitting | nan | 178.4 | 0.8 | 0.3 | 0.4 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 215 | Standing | Sitting | nan | 178.4 | 0.7 | 0.2 | 6.6 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 216 | Standing | Sitting | nan | 178.4 | 0.5 | 0.3 | 13.1 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 217 | Standing | Sitting | nan | 178.6 | 0.3 | 0.2 | 11.5 | 0.9 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 218 | Standing | Sitting | 175.8 | 179.5 | 0.2 | 0.4 | 7.3 | 0.8 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 219 | Standing | Sitting | 175.3 | 179.4 | 0.2 | 0.3 | 3.2 | 0.8 | 1.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 220 | Standing | Sitting | 174.2 | 179.6 | 0.3 | 0.1 | 5.2 | 0.8 | 1.2 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 221 | Standing | Sitting | 173.3 | 179.1 | 0.3 | 0.3 | 3.8 | 0.8 | 1.2 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 229 | Standing | Sitting | nan | 179.2 | 2.1 | 0.2 | 2.7 | 0.8 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 230 | Standing | Sitting | nan | 179.6 | 2.4 | 0.2 | 15.0 | 0.8 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 231 | Standing | Sitting | nan | 179.2 | 2.4 | 0.1 | 1.6 | 0.8 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 232 | Standing | Sitting | nan | 179.4 | 2.4 | 0.1 | 1.3 | 0.9 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 233 | Standing | Sitting | nan | 179.5 | 2.6 | 0.2 | 11.5 | 0.9 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 234 | Standing | Sitting | nan | nan | 2.9 | 0.4 | 22.0 | 0.7 | 1.2 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 235 | Standing | Sitting | nan | nan | 2.8 | 0.1 | 7.6 | 0.7 | 1.2 | 0.4 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 236 | Standing | Sitting | nan | nan | 2.5 | 0.1 | 18.3 | 0.7 | 1.2 | 0.4 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 237 | Standing | Sitting | nan | nan | 2.4 | 0.3 | 3.0 | 0.7 | 1.2 | 0.4 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 244 | Standing | Sitting | nan | 176.7 | 1.0 | 0.3 | 43.0 | 0.9 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 245 | Standing | Sitting | nan | 176.6 | 0.5 | 0.3 | 33.7 | 0.9 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 246 | Standing | Sitting | nan | 176.7 | 0.3 | 0.0 | 8.9 | 0.9 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 247 | Standing | Sitting | nan | 176.9 | 0.2 | 0.1 | 9.6 | 0.9 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 248 | Standing | Sitting | nan | 177.0 | 0.0 | 0.1 | 9.6 | 0.9 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 249 | Standing | Sitting | 170.7 | 177.0 | 0.1 | 0.1 | 4.0 | 0.7 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 250 | Standing | Sitting | 171.9 | 177.2 | 0.1 | 0.2 | 4.0 | 0.7 | 1.2 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 251 | Standing | Sitting | 172.3 | 177.8 | 0.1 | 0.1 | 0.5 | 0.7 | 1.2 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 252 | Standing | Sitting | 173.0 | 178.7 | 0.0 | 0.1 | 7.4 | 0.7 | 1.2 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 796 | Standing | Sitting | nan | nan | 2.4 | 0.2 | 4.4 | 0.6 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 797 | Standing | Sitting | nan | nan | 2.4 | 0.2 | 4.5 | 0.6 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 798 | Standing | Sitting | nan | nan | 2.1 | 0.1 | 16.7 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 799 | Standing | Sitting | nan | nan | 1.9 | 0.2 | 12.8 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 800 | Standing | Sitting | nan | nan | 1.8 | 0.3 | 4.3 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 801 | Standing | Sitting | nan | nan | 1.6 | 0.2 | 14.2 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 802 | Standing | Sitting | 175.0 | 172.4 | 1.2 | 0.2 | 21.4 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 803 | Standing | Sitting | 174.9 | 171.6 | 0.7 | 0.1 | 27.7 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 804 | Standing | Sitting | 162.3 | 171.7 | 0.6 | 0.4 | 8.3 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 805 | Standing | Sitting | 166.8 | 174.1 | 0.2 | 0.2 | 25.7 | 0.7 | 1.0 | 0.5 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 1086 | Standing | Sitting | 138.6 | 142.6 | 4.4 | 0.2 | 1.1 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1087 | Standing | Sitting | 137.3 | 141.2 | 4.4 | 0.4 | 1.0 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1088 | Standing | Sitting | 137.8 | 141.6 | 4.4 | 0.4 | 0.9 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1089 | Standing | Sitting | 135.6 | 139.2 | 4.3 | 0.2 | 1.8 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1090 | Standing | Sitting | 136.2 | 139.9 | 4.4 | 0.3 | 4.8 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1091 | Standing | Sitting | 135.5 | 139.6 | 4.4 | 0.1 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1092 | Standing | Sitting | 135.8 | 139.9 | 4.5 | 0.1 | 7.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1093 | Standing | Sitting | 135.8 | 140.0 | 4.7 | 0.2 | 10.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1094 | Standing | Sitting | 136.0 | 140.7 | 4.8 | 0.2 | 3.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1095 | Standing | Sitting | 135.7 | 140.6 | 4.9 | 0.0 | 9.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1096 | Standing | Sitting | 135.4 | 140.6 | 5.0 | 0.2 | 2.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1097 | Standing | Sitting | 135.3 | 140.6 | 5.0 | 0.1 | 5.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1098 | Standing | Sitting | 135.5 | 140.8 | 5.1 | 0.1 | 5.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1099 | Standing | Sitting | 136.0 | 141.5 | 5.3 | 0.1 | 11.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1100 | Standing | Sitting | 135.2 | 141.1 | 5.5 | 0.1 | 12.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1101 | Standing | Sitting | 135.1 | 141.3 | 5.7 | 0.1 | 13.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1102 | Standing | Sitting | 135.1 | 141.7 | 5.9 | 0.0 | 7.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1103 | Standing | Sitting | 135.3 | 142.1 | 6.0 | 0.0 | 9.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1104 | Standing | Sitting | 135.3 | 142.2 | 6.2 | 0.0 | 9.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1105 | Standing | Sitting | 134.6 | 141.9 | 6.3 | 0.0 | 10.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1106 | Standing | Sitting | 134.6 | 142.0 | 6.4 | 0.0 | 4.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1107 | Standing | Sitting | 135.6 | 143.0 | 6.5 | 0.0 | 7.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1108 | Standing | Sitting | 136.7 | 144.2 | 6.6 | 0.0 | 3.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1109 | Standing | Sitting | 138.9 | 145.8 | 6.7 | 0.0 | 4.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1110 | Standing | Sitting | 139.6 | 146.4 | 6.7 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1111 | Standing | Sitting | 140.6 | 147.0 | 6.7 | 0.0 | 2.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1112 | Standing | Sitting | 140.8 | 147.2 | 6.8 | 0.0 | 2.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1113 | Standing | Sitting | 141.0 | 147.3 | 6.8 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1114 | Standing | Sitting | 141.1 | 147.3 | 6.9 | 0.0 | 4.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1115 | Standing | Sitting | 141.0 | 147.2 | 7.0 | 0.0 | 5.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1116 | Standing | Sitting | 140.9 | 147.1 | 7.0 | 0.0 | 2.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1117 | Standing | Sitting | 140.9 | 147.0 | 7.0 | 0.0 | 2.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1118 | Standing | Sitting | 141.0 | 147.0 | 7.1 | 0.1 | 3.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1119 | Standing | Sitting | 141.2 | 147.2 | 7.1 | 0.0 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1120 | Standing | Sitting | 141.4 | 147.3 | 7.1 | 0.0 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1121 | Standing | Sitting | 141.6 | 147.4 | 7.1 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1122 | Standing | Sitting | 142.0 | 147.8 | 7.1 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1123 | Standing | Sitting | 142.0 | 147.8 | 7.1 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1124 | Standing | Sitting | 142.2 | 148.1 | 7.2 | 0.0 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1125 | Standing | Sitting | 142.0 | 148.0 | 7.2 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1126 | Standing | Sitting | 142.0 | 148.2 | 7.2 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1127 | Standing | Sitting | 141.9 | 148.1 | 7.2 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1128 | Standing | Sitting | 141.9 | 148.2 | 7.2 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1129 | Standing | Sitting | 142.0 | 148.3 | 7.2 | 0.0 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1130 | Standing | Sitting | 142.0 | 148.3 | 7.2 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1131 | Standing | Sitting | 141.7 | 148.3 | 7.2 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1132 | Standing | Sitting | 141.2 | 148.0 | 7.2 | 0.1 | 1.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1133 | Standing | Sitting | 140.9 | 147.9 | 7.3 | 0.0 | 2.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1134 | Standing | Sitting | 139.6 | 147.0 | 7.3 | 0.0 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1135 | Standing | Sitting | 136.6 | 145.0 | 7.4 | 0.1 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1136 | Standing | Sitting | 135.3 | 144.2 | 7.4 | 0.0 | 4.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1137 | Standing | Sitting | 135.1 | 144.0 | 7.5 | 0.0 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1138 | Standing | Sitting | 135.0 | 144.0 | 7.5 | 0.1 | 1.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1139 | Standing | Sitting | 134.9 | 144.1 | 7.6 | 0.1 | 4.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1140 | Standing | Sitting | 133.8 | 143.5 | 7.6 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1141 | Standing | Sitting | 133.7 | 143.4 | 7.7 | 0.0 | 4.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1142 | Standing | Sitting | 132.8 | 142.9 | 7.7 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1143 | Standing | Sitting | 132.5 | 142.5 | 7.7 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1144 | Standing | Sitting | 132.2 | 142.2 | 7.7 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1145 | Standing | Sitting | 132.3 | 142.3 | 7.7 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1146 | Standing | Sitting | 132.3 | 142.4 | 7.7 | 0.0 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1147 | Standing | Sitting | 132.1 | 142.4 | 7.7 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1148 | Standing | Sitting | 131.8 | 142.1 | 7.8 | 0.0 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1149 | Standing | Sitting | 131.9 | 142.3 | 7.8 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1150 | Standing | Sitting | 132.0 | 142.4 | 7.8 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1151 | Standing | Sitting | 132.1 | 142.5 | 7.8 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1152 | Standing | Sitting | 132.6 | 143.0 | 7.8 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1153 | Standing | Sitting | 132.7 | 143.1 | 7.8 | 0.0 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1154 | Standing | Sitting | 132.8 | 143.2 | 7.8 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1155 | Standing | Sitting | 132.5 | 142.7 | 7.9 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1156 | Standing | Sitting | 132.5 | 142.7 | 7.8 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1157 | Standing | Sitting | 132.2 | 142.4 | 7.9 | 0.0 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1158 | Standing | Sitting | 132.3 | 142.6 | 7.9 | 0.1 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1159 | Standing | Sitting | 131.9 | 142.1 | 7.9 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1160 | Standing | Sitting | 131.6 | 141.7 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1161 | Standing | Sitting | 131.1 | 141.2 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1162 | Standing | Sitting | 131.1 | 141.1 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1163 | Standing | Sitting | 130.8 | 140.8 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1164 | Standing | Sitting | 130.9 | 141.0 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1165 | Standing | Sitting | 130.9 | 140.9 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1166 | Standing | Sitting | 131.0 | 141.1 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1167 | Standing | Sitting | 131.2 | 141.4 | 7.9 | 0.1 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1168 | Standing | Sitting | 131.6 | 141.8 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1169 | Standing | Sitting | 131.7 | 141.8 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1170 | Standing | Sitting | 131.5 | 141.6 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1171 | Standing | Sitting | 131.5 | 141.6 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1172 | Standing | Sitting | 131.5 | 141.6 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1173 | Standing | Sitting | 131.5 | 141.6 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1174 | Standing | Sitting | 131.5 | 141.6 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1175 | Standing | Sitting | 131.5 | 141.6 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1176 | Standing | Sitting | 131.6 | 141.8 | 7.9 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1177 | Standing | Sitting | 131.5 | 141.7 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1178 | Standing | Sitting | 131.5 | 141.8 | 7.8 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1179 | Standing | Sitting | 131.8 | 142.1 | 7.8 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1180 | Standing | Sitting | 132.0 | 142.4 | 7.9 | 0.1 | 2.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1181 | Standing | Sitting | 132.0 | 142.5 | 7.9 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1182 | Standing | Sitting | 131.7 | 142.4 | 7.9 | 0.0 | 1.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1183 | Standing | Sitting | 132.0 | 142.6 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1184 | Standing | Sitting | 131.9 | 142.6 | 7.9 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1185 | Standing | Sitting | 132.1 | 142.7 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1186 | Standing | Sitting | 132.2 | 142.9 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1187 | Standing | Sitting | 132.2 | 142.8 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1188 | Standing | Sitting | 132.2 | 142.8 | 7.9 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1189 | Standing | Sitting | 132.4 | 142.9 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1190 | Standing | Sitting | 132.4 | 143.0 | 7.9 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1191 | Standing | Sitting | 132.5 | 143.1 | 7.9 | 0.1 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1192 | Standing | Sitting | 132.8 | 143.6 | 7.9 | 0.0 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1193 | Standing | Sitting | 132.0 | 142.4 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1194 | Standing | Sitting | 131.2 | 141.4 | 7.9 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1195 | Standing | Sitting | 131.5 | 141.6 | 7.9 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1196 | Standing | Sitting | 131.4 | 141.3 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1197 | Standing | Sitting | 131.1 | 141.0 | 7.9 | 0.1 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1198 | Standing | Sitting | 131.0 | 140.9 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1199 | Standing | Sitting | 130.8 | 140.6 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1200 | Standing | Sitting | 130.8 | 140.5 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1201 | Standing | Sitting | 130.9 | 140.5 | 7.9 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1202 | Standing | Sitting | 130.9 | 140.5 | 7.8 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1203 | Standing | Sitting | 132.3 | 141.5 | 7.9 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1204 | Standing | Sitting | 132.3 | 141.5 | 7.8 | 0.1 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1205 | Standing | Sitting | 133.0 | 142.0 | 7.8 | 0.1 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1206 | Standing | Sitting | 133.1 | 142.1 | 7.8 | 0.1 | 2.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1207 | Standing | Sitting | 132.8 | 141.8 | 7.8 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1208 | Standing | Sitting | 132.3 | 141.4 | 7.8 | 0.0 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1209 | Standing | Sitting | 132.5 | 141.5 | 7.8 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1210 | Standing | Sitting | 132.1 | 141.1 | 7.7 | 0.2 | 2.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1211 | Standing | Sitting | 132.0 | 141.0 | 7.7 | 0.0 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1212 | Standing | Sitting | 131.5 | 140.5 | 7.7 | 0.1 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1213 | Standing | Sitting | 131.6 | 140.7 | 7.7 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1214 | Standing | Sitting | 131.2 | 140.4 | 7.7 | 0.1 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1215 | Standing | Sitting | 131.3 | 140.5 | 7.7 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1216 | Standing | Sitting | 131.0 | 140.2 | 7.7 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1217 | Standing | Sitting | 131.0 | 140.2 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1218 | Standing | Sitting | 130.9 | 140.2 | 7.7 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1219 | Standing | Sitting | 130.9 | 140.3 | 7.7 | 0.0 | 1.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1220 | Standing | Sitting | 131.2 | 140.6 | 7.7 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1221 | Standing | Sitting | 131.3 | 140.8 | 7.7 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1222 | Standing | Sitting | 131.6 | 141.1 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1223 | Standing | Sitting | 131.7 | 141.2 | 7.7 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1224 | Standing | Sitting | 131.5 | 141.1 | 7.7 | 0.0 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1225 | Standing | Sitting | 131.3 | 140.9 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1226 | Standing | Sitting | 131.2 | 141.0 | 7.7 | 0.1 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1227 | Standing | Sitting | 131.1 | 140.9 | 7.7 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1228 | Standing | Sitting | 131.6 | 141.3 | 7.7 | 0.1 | 2.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1229 | Standing | Sitting | 132.2 | 141.8 | 7.7 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1230 | Standing | Sitting | 132.2 | 142.0 | 7.7 | 0.0 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1231 | Standing | Sitting | 132.2 | 141.9 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1232 | Standing | Sitting | 132.1 | 141.9 | 7.7 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1233 | Standing | Sitting | 132.0 | 141.8 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1234 | Standing | Sitting | 132.1 | 141.9 | 7.7 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1235 | Standing | Sitting | 132.0 | 141.7 | 7.7 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1236 | Standing | Sitting | 132.1 | 141.8 | 7.7 | 0.1 | 2.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1237 | Standing | Sitting | 132.0 | 142.0 | 7.7 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1238 | Standing | Sitting | 132.0 | 141.9 | 7.7 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1239 | Standing | Sitting | 131.7 | 141.7 | 7.7 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1240 | Standing | Sitting | 131.6 | 141.5 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1241 | Standing | Sitting | 131.6 | 141.5 | 7.7 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1242 | Standing | Sitting | 131.7 | 141.7 | 7.7 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1243 | Standing | Sitting | 131.8 | 141.7 | 7.7 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1244 | Standing | Sitting | 131.8 | 141.7 | 7.7 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1245 | Standing | Sitting | 131.7 | 141.5 | 7.7 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1246 | Standing | Sitting | 131.7 | 141.5 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1247 | Standing | Sitting | 131.9 | 141.7 | 7.7 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1248 | Standing | Sitting | 132.1 | 141.9 | 7.7 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1249 | Standing | Sitting | 132.2 | 142.0 | 7.7 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1250 | Standing | Sitting | 133.8 | 143.2 | 7.7 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1251 | Standing | Sitting | 133.5 | 143.0 | 7.7 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1252 | Standing | Sitting | 133.5 | 143.1 | 7.6 | 0.0 | 2.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1253 | Standing | Sitting | 133.7 | 143.7 | 7.6 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1254 | Standing | Sitting | 133.6 | 143.6 | 7.6 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1255 | Standing | Sitting | 133.5 | 143.5 | 7.6 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1256 | Standing | Sitting | 133.4 | 143.4 | 7.6 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1257 | Standing | Sitting | 133.2 | 143.3 | 7.6 | 0.1 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1258 | Standing | Sitting | 132.8 | 142.9 | 7.6 | 0.1 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1259 | Standing | Sitting | 132.9 | 143.0 | 7.7 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1260 | Standing | Sitting | 132.6 | 142.7 | 7.7 | 0.0 | 2.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1261 | Standing | Sitting | 132.3 | 142.5 | 7.7 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1262 | Standing | Sitting | 132.0 | 142.1 | 7.7 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1263 | Standing | Sitting | 131.9 | 142.0 | 7.8 | 0.0 | 2.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1264 | Standing | Sitting | 131.6 | 141.7 | 7.8 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1265 | Standing | Sitting | 131.7 | 141.8 | 7.8 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1266 | Standing | Sitting | 131.7 | 141.8 | 7.8 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1267 | Standing | Sitting | 131.7 | 141.8 | 7.8 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1268 | Standing | Sitting | 131.6 | 141.8 | 7.8 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1269 | Standing | Sitting | 131.6 | 141.7 | 7.8 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1270 | Standing | Sitting | 131.5 | 141.7 | 7.8 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1271 | Standing | Sitting | 132.7 | 142.4 | 7.8 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1272 | Standing | Sitting | 132.6 | 142.3 | 7.8 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1273 | Standing | Sitting | 132.6 | 142.3 | 7.8 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1274 | Standing | Sitting | 132.4 | 142.2 | 7.8 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1275 | Standing | Sitting | 132.5 | 142.3 | 7.8 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1276 | Standing | Sitting | 132.4 | 142.2 | 7.8 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1277 | Standing | Sitting | 132.2 | 142.1 | 7.8 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1278 | Standing | Sitting | 131.9 | 141.7 | 7.8 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1279 | Standing | Sitting | 131.8 | 141.7 | 7.8 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1280 | Standing | Sitting | 131.6 | 141.5 | 7.8 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1281 | Standing | Sitting | 131.6 | 141.6 | 7.8 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1282 | Standing | Sitting | 131.4 | 141.2 | 7.8 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1283 | Standing | Sitting | 131.4 | 141.3 | 7.8 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1284 | Standing | Sitting | 131.3 | 141.2 | 7.8 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1285 | Standing | Sitting | 131.4 | 141.4 | 7.8 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1286 | Standing | Sitting | 131.5 | 141.5 | 7.8 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1287 | Standing | Sitting | 131.6 | 141.7 | 7.8 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1288 | Standing | Sitting | 131.9 | 142.0 | 7.8 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1289 | Standing | Sitting | 132.5 | 142.6 | 7.8 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1290 | Standing | Sitting | 132.8 | 143.0 | 7.8 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1291 | Standing | Sitting | 132.9 | 143.1 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1292 | Standing | Sitting | 132.9 | 143.1 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1293 | Standing | Sitting | 133.1 | 143.0 | 7.9 | 0.0 | 2.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1294 | Standing | Sitting | 132.8 | 142.7 | 7.9 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1295 | Standing | Sitting | 133.6 | 143.1 | 7.9 | 0.0 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1296 | Standing | Sitting | 133.6 | 143.0 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1297 | Standing | Sitting | 133.8 | 143.0 | 7.9 | 0.1 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1298 | Standing | Sitting | 133.8 | 142.9 | 7.9 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1299 | Standing | Sitting | 133.8 | 142.9 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1300 | Standing | Sitting | 133.6 | 142.7 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1301 | Standing | Sitting | 134.2 | 143.2 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1302 | Standing | Sitting | 134.1 | 143.2 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1303 | Standing | Sitting | 133.8 | 143.0 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1304 | Standing | Sitting | 134.0 | 143.1 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1305 | Standing | Sitting | 133.7 | 142.8 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1306 | Standing | Sitting | 132.8 | 141.7 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1307 | Standing | Sitting | 132.5 | 141.2 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1308 | Standing | Sitting | 132.7 | 141.3 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1309 | Standing | Sitting | 132.5 | 141.0 | 7.9 | 0.1 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1310 | Standing | Sitting | 132.4 | 140.7 | 7.9 | 0.0 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1311 | Standing | Sitting | 131.9 | 140.4 | 8.0 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1312 | Standing | Sitting | 131.8 | 140.5 | 8.0 | 0.1 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1313 | Standing | Sitting | 132.2 | 142.5 | 7.9 | 0.1 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1314 | Standing | Sitting | 132.6 | 143.1 | 7.9 | 0.1 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1315 | Standing | Sitting | 132.6 | 143.6 | 7.9 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1316 | Standing | Sitting | 132.9 | 143.7 | 7.9 | 0.1 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1317 | Standing | Sitting | 131.9 | 143.7 | 7.9 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1318 | Standing | Sitting | 131.9 | 143.6 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1319 | Standing | Sitting | 131.1 | 143.1 | 7.9 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1320 | Standing | Sitting | 130.9 | 143.0 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1321 | Standing | Sitting | 131.4 | 143.3 | 7.9 | 0.1 | 1.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1322 | Standing | Sitting | 130.9 | 142.8 | 7.9 | 0.1 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1323 | Standing | Sitting | 131.3 | 142.7 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1324 | Standing | Sitting | 131.4 | 142.8 | 7.9 | 0.0 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1325 | Standing | Sitting | 132.2 | 143.3 | 7.9 | 0.0 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1326 | Standing | Sitting | 132.0 | 143.4 | 7.9 | 0.1 | 2.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1327 | Standing | Sitting | 132.5 | 143.5 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1328 | Standing | Sitting | 132.6 | 143.4 | 7.9 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1329 | Standing | Sitting | 132.6 | 143.3 | 7.9 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1330 | Standing | Sitting | 132.7 | 143.2 | 7.9 | 0.0 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1331 | Standing | Sitting | 132.9 | 143.2 | 7.9 | 0.0 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1332 | Standing | Sitting | 133.4 | 143.4 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1333 | Standing | Sitting | 133.4 | 143.3 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1334 | Standing | Sitting | 133.6 | 143.5 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1335 | Standing | Sitting | 133.5 | 143.4 | 7.9 | 0.1 | 2.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1336 | Standing | Sitting | 133.9 | 143.3 | 7.9 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1337 | Standing | Sitting | 133.1 | 142.7 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1338 | Standing | Sitting | 133.3 | 142.8 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1339 | Standing | Sitting | 133.6 | 143.1 | 7.9 | 0.1 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1340 | Standing | Sitting | 133.6 | 143.1 | 7.9 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1341 | Standing | Sitting | 133.7 | 143.2 | 7.9 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1342 | Standing | Sitting | 133.6 | 143.0 | 7.9 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1343 | Standing | Sitting | 133.7 | 143.3 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1344 | Standing | Sitting | 133.5 | 143.3 | 7.9 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1345 | Standing | Sitting | 133.6 | 143.5 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1346 | Standing | Sitting | 133.6 | 143.5 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1347 | Standing | Sitting | 133.5 | 143.1 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1348 | Standing | Sitting | 133.2 | 142.6 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1349 | Standing | Sitting | 132.9 | 142.2 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1350 | Standing | Sitting | 133.2 | 142.6 | 7.9 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1351 | Standing | Sitting | 132.4 | 142.0 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1352 | Standing | Sitting | 132.2 | 141.9 | 7.9 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1353 | Standing | Sitting | 132.3 | 142.0 | 7.9 | 0.1 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1354 | Standing | Sitting | 132.3 | 142.2 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1355 | Standing | Sitting | 132.4 | 142.2 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1356 | Standing | Sitting | 132.6 | 142.5 | 7.9 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1357 | Standing | Sitting | 132.8 | 142.8 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1358 | Standing | Sitting | 133.1 | 143.3 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1359 | Standing | Sitting | 133.2 | 143.4 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1360 | Standing | Sitting | 133.1 | 143.2 | 7.8 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1361 | Standing | Sitting | 133.0 | 143.1 | 7.8 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1362 | Standing | Sitting | 133.1 | 143.1 | 7.9 | 0.1 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1363 | Standing | Sitting | 133.1 | 143.1 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1364 | Standing | Sitting | 133.3 | 143.3 | 7.9 | 0.1 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1365 | Standing | Sitting | 133.4 | 143.5 | 7.9 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1366 | Standing | Sitting | 133.4 | 143.5 | 7.9 | 0.1 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1367 | Standing | Sitting | 133.4 | 143.5 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1368 | Standing | Sitting | 133.4 | 143.5 | 7.9 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1369 | Standing | Sitting | 132.6 | 142.9 | 7.9 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1370 | Standing | Sitting | 132.6 | 142.9 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1371 | Standing | Sitting | 132.7 | 143.4 | 7.9 | 0.0 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1372 | Standing | Sitting | 133.5 | 144.3 | 7.9 | 0.0 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1373 | Standing | Sitting | 134.1 | 144.5 | 7.9 | 0.0 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1374 | Standing | Sitting | 134.0 | 144.8 | 7.8 | 0.0 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1375 | Standing | Sitting | 134.3 | 144.8 | 7.8 | 0.0 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1376 | Standing | Sitting | 134.4 | 144.8 | 7.8 | 0.0 | 2.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1377 | Standing | Sitting | 134.7 | 145.0 | 7.7 | 0.0 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1378 | Standing | Sitting | 134.8 | 145.0 | 7.7 | 0.1 | 2.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1379 | Standing | Sitting | 135.5 | 145.3 | 7.7 | 0.0 | 2.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1380 | Standing | Sitting | 135.4 | 144.9 | 7.6 | 0.1 | 1.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1381 | Standing | Sitting | 134.7 | 144.2 | 7.6 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1382 | Standing | Sitting | 135.2 | 144.4 | 7.6 | 0.0 | 1.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1383 | Standing | Sitting | 135.0 | 144.2 | 7.6 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1384 | Standing | Sitting | 135.0 | 144.0 | 7.6 | 0.0 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1385 | Standing | Sitting | 135.3 | 144.1 | 7.5 | 0.0 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1386 | Standing | Sitting | 135.5 | 144.1 | 7.5 | 0.0 | 2.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1387 | Standing | Sitting | 135.5 | 144.1 | 7.5 | 0.0 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1388 | Standing | Sitting | 135.7 | 144.1 | 7.4 | 0.0 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1389 | Standing | Sitting | 135.8 | 144.1 | 7.4 | 0.0 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1390 | Standing | Sitting | 136.1 | 144.2 | 7.3 | 0.0 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1391 | Standing | Sitting | 136.1 | 144.1 | 7.3 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1392 | Standing | Sitting | 134.9 | 143.1 | 7.3 | 0.1 | 3.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1393 | Standing | Sitting | 134.7 | 142.6 | 7.3 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1394 | Standing | Sitting | 134.8 | 142.3 | 7.2 | 0.1 | 5.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1395 | Standing | Sitting | 137.0 | 143.5 | 7.2 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1396 | Standing | Sitting | 136.9 | 143.3 | 7.1 | 0.0 | 2.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1397 | Standing | Sitting | 136.8 | 143.2 | 7.1 | 0.0 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1398 | Standing | Sitting | 136.6 | 142.9 | 7.1 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1399 | Standing | Sitting | 136.7 | 143.0 | 7.1 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1400 | Standing | Sitting | 136.5 | 142.6 | 7.1 | 0.0 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1401 | Standing | Sitting | 136.5 | 142.6 | 7.1 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1402 | Standing | Sitting | 136.5 | 142.5 | 7.1 | 0.0 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1403 | Standing | Sitting | 136.6 | 142.3 | 7.0 | 0.0 | 5.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1404 | Standing | Sitting | 136.4 | 141.8 | 7.0 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1405 | Standing | Sitting | 136.6 | 142.1 | 7.0 | 0.0 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1406 | Standing | Sitting | 136.7 | 142.1 | 7.0 | 0.0 | 4.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1407 | Standing | Sitting | 136.3 | 141.9 | 6.9 | 0.0 | 2.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1408 | Standing | Sitting | 136.0 | 141.8 | 6.8 | 0.0 | 8.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1409 | Standing | Sitting | 135.8 | 141.5 | 6.7 | 0.0 | 6.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1410 | Standing | Sitting | 136.5 | 142.2 | 6.5 | 0.1 | 13.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1411 | Standing | Sitting | 137.7 | 143.1 | 6.4 | 0.0 | 2.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1412 | Standing | Sitting | 137.8 | 143.1 | 6.3 | 0.2 | 5.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1413 | Standing | Sitting | 138.5 | 143.5 | 6.2 | 0.1 | 4.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1414 | Standing | Sitting | 139.4 | 144.3 | 6.1 | 0.2 | 8.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1415 | Standing | Sitting | 139.5 | 144.4 | 5.9 | 0.1 | 10.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1416 | Standing | Sitting | 140.3 | 145.0 | 5.7 | 0.1 | 12.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1417 | Standing | Sitting | 142.2 | 146.3 | 5.5 | 0.1 | 11.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1418 | Standing | Sitting | 141.9 | 146.2 | 5.4 | 0.1 | 6.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1419 | Standing | Sitting | 141.5 | 146.0 | 5.3 | 0.0 | 6.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1420 | Standing | Sitting | 141.7 | 145.7 | 5.2 | 0.0 | 7.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1421 | Standing | Sitting | 142.9 | 146.4 | 5.1 | 0.0 | 2.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1422 | Standing | Sitting | 142.2 | 145.7 | 5.0 | 0.0 | 8.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1423 | Standing | Sitting | 142.3 | 145.6 | 4.7 | 0.0 | 14.9 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1424 | Standing | Sitting | 142.5 | 145.6 | 4.5 | 0.0 | 14.2 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1425 | Standing | Sitting | 142.7 | 145.6 | 4.3 | 0.0 | 12.5 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1426 | Standing | Sitting | 142.2 | 145.2 | 4.0 | 0.1 | 13.9 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1427 | Standing | Sitting | 141.3 | 144.2 | 3.8 | 0.1 | 14.8 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1428 | Standing | Sitting | 141.0 | 143.7 | 3.6 | 0.1 | 14.6 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1429 | Standing | Sitting | 138.9 | 141.8 | 3.4 | 0.2 | 11.0 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1430 | Standing | Sitting | 138.8 | 141.8 | 3.2 | 0.1 | 7.6 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1431 | Standing | Sitting | 137.4 | 140.6 | 3.1 | 0.1 | 8.6 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1432 | Standing | Sitting | 140.0 | 142.6 | 2.9 | 0.3 | 14.1 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1433 | Standing | Sitting | 142.6 | 144.4 | 2.6 | 0.2 | 14.0 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1434 | Standing | Sitting | 143.7 | 145.3 | 2.4 | 0.1 | 15.4 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1435 | Standing | Sitting | 143.9 | 145.5 | 2.2 | 0.1 | 9.1 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 1436 | Standing | Sitting | 145.8 | 147.1 | 2.1 | 0.3 | 9.8 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 1437 | Standing | Sitting | 145.9 | 147.1 | 2.0 | 0.1 | 4.3 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 1739 | Lying | Sitting | nan | nan | 2.5 | 0.5 | 47.2 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1740 | Lying | Sitting | nan | nan | 3.2 | 0.9 | 39.9 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1741 | Lying | Sitting | nan | nan | 4.0 | 1.0 | 45.0 | 0.7 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1742 | Lying | Sitting | nan | 173.4 | 4.4 | 0.7 | 26.0 | 0.9 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1743 | Lying | Sitting | nan | 173.6 | 5.2 | 0.5 | 48.4 | 0.9 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 1744 | Lying | Sitting | nan | 173.2 | 5.6 | 0.4 | 26.8 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 1745 | Lying | Sitting | nan | 170.2 | 5.8 | 0.1 | 8.0 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 1746 | Lying | Sitting | nan | 168.7 | 6.0 | 0.2 | 14.3 | 0.8 | 1.0 | 0.4 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 1747 | Lying | Sitting | nan | 166.7 | 5.9 | 0.4 | 6.9 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1748 | Lying | Sitting | 156.8 | 165.3 | 5.9 | 0.9 | 3.1 | 0.6 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1749 | Lying | Sitting | 159.4 | 164.1 | 6.0 | 0.9 | 6.3 | 0.6 | 1.0 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 1750 | Lying | Sitting | 157.2 | 162.1 | 5.8 | 1.0 | 8.7 | 0.6 | 1.0 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 1751 | Lying | Sitting | 162.5 | 162.4 | 5.8 | 1.3 | 0.9 | 0.6 | 1.0 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 1752 | Lying | Standing | 167.8 | 163.5 | 6.1 | 1.4 | 16.2 | 0.6 | 1.0 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1753 | Lying | Standing | 168.7 | 164.9 | 6.8 | 1.8 | 42.0 | 0.6 | 1.0 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1754 | Lying | Standing | 169.0 | 165.8 | 6.9 | 1.7 | 9.0 | 0.6 | 1.0 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1755 | Lying | Standing | nan | 166.4 | 7.2 | 1.2 | 12.8 | 0.8 | 1.0 | 0.3 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 1756 | Lying | Standing | nan | 167.6 | 7.4 | 1.4 | 14.7 | 0.8 | 1.0 | 0.2 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 1757 | Lying | Standing | nan | 168.4 | 7.9 | 1.2 | 30.5 | 0.8 | 1.0 | 0.2 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 1758 | Lying | Standing | nan | 168.9 | 8.7 | 1.1 | 47.1 | 0.8 | 1.0 | 0.2 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 1759 | Lying | Sitting | nan | 169.9 | 10.0 | 0.7 | 76.2 | 0.8 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1760 | Lying | Sitting | nan | 172.0 | 11.2 | 1.2 | 75.6 | 0.8 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1761 | Lying | Sitting | nan | 170.0 | 12.8 | 1.5 | 92.4 | 0.8 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1762 | Lying | Sitting | nan | nan | 14.3 | 1.8 | 93.1 | 0.6 | 1.0 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1763 | Lying | Sitting | nan | nan | 16.1 | 0.8 | 107.3 | 0.6 | 1.0 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 1764 | Lying | Sitting | nan | nan | 17.5 | 1.6 | 81.3 | 0.6 | 1.0 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 1765 | Lying | Sitting | nan | nan | 19.2 | 1.6 | 102.3 | 0.6 | 1.0 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 1766 | Lying | Standing | nan | nan | 21.0 | 1.2 | 112.2 | 0.6 | 1.0 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1767 | Lying | Standing | nan | nan | 23.4 | 0.7 | 138.9 | 0.6 | 1.0 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1768 | Lying | Standing | nan | nan | 26.3 | 0.4 | 174.0 | 0.5 | 1.0 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1769 | Lying | Standing | nan | nan | 27.7 | 1.4 | 85.7 | 0.5 | 1.0 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1770 | Lying | Standing | nan | nan | 28.5 | 2.7 | 49.9 | 0.5 | 1.0 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1771 | Lying | Standing | nan | nan | 29.4 | 1.9 | 50.7 | 0.5 | 1.0 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1772 | Lying | Standing | nan | nan | 30.6 | 1.6 | 75.6 | 0.5 | 1.0 | 0.0 | T | F | Standing|Standing|Standing|Standing|Sitting |
| 1773 | Lying | Standing | nan | nan | 32.3 | 1.2 | 101.5 | 0.5 | 1.0 | 0.0 | T | F | Standing|Standing|Standing|Sitting|Sitting |
| 1774 | Lying | Standing | nan | nan | 33.8 | 1.0 | 90.8 | 0.4 | 1.0 | 0.0 | T | F | Standing|Standing|Sitting|Sitting|Sitting |
| 1775 | Lying | Standing | nan | nan | 36.9 | 1.6 | 181.2 | 0.4 | 1.0 | 0.0 | T | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 1776 | Lying | Sitting | nan | nan | 38.9 | 2.1 | 119.4 | 0.4 | 1.0 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1777 | Lying | Sitting | nan | nan | 39.7 | 1.1 | 50.5 | 0.4 | 1.0 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1778 | Lying | Sitting | nan | 119.1 | 41.4 | 0.9 | 102.4 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Lying |
| 2398 | Standing | Sitting | nan | 165.5 | 7.0 | 0.6 | 7.5 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2399 | Standing | Sitting | nan | 165.5 | 6.6 | 0.3 | 21.7 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2400 | Standing | Sitting | nan | 164.9 | 6.3 | 0.3 | 15.8 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2401 | Standing | Sitting | nan | 165.2 | 5.8 | 0.3 | 31.9 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2402 | Standing | Sitting | nan | 166.2 | 5.3 | 0.4 | 27.4 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2403 | Standing | Sitting | nan | 167.1 | 4.8 | 0.2 | 33.5 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2404 | Standing | Sitting | nan | 168.1 | 4.4 | 0.3 | 22.6 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2405 | Standing | Sitting | nan | 168.4 | 3.9 | 0.2 | 30.3 | 0.8 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2406 | Standing | Sitting | 158.5 | 168.1 | 3.3 | 0.4 | 37.6 | 0.7 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 2407 | Standing | Sitting | 162.1 | 168.5 | 3.0 | 0.5 | 16.7 | 0.7 | 1.0 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 2408 | Standing | Sitting | 165.7 | 168.4 | 2.6 | 0.5 | 25.2 | 0.7 | 1.0 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 2409 | Standing | Sitting | 169.5 | 168.3 | 2.1 | 0.4 | 31.7 | 0.7 | 1.0 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |

---

## Normal_Fall_1 (**posture<90%, false positive**)

**Posture accuracy:** 77.8%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 67.2%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 29 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 9 | 11 | 41 | 0 |

**Fall detection:** FP frames [151]

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 90 | Lying | Standing | 159.3 | 156.8 | 5.9 | 0.9 | 21.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Lying | Standing | 157.9 | 155.0 | 4.7 | 0.9 | 35.8 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Lying | Standing | 155.4 | 151.2 | 3.9 | 1.0 | 24.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Lying | Standing | 151.2 | 148.1 | 2.8 | 1.2 | 33.2 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Lying | Standing | 149.3 | 144.4 | 2.0 | 0.7 | 21.8 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Lying | Standing | 147.0 | 139.1 | 1.1 | 1.2 | 27.9 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 96 | Lying | Standing | 140.3 | 130.4 | 0.2 | 1.6 | 26.0 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 97 | Lying | Standing | 62.1 | 47.8 | 0.4 | 3.1 | 5.3 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 98 | Lying | Standing | 32.3 | 32.3 | 1.3 | 3.1 | 27.3 | 0.2 | 0.3 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 99 | Lying | Sitting | 33.9 | 24.0 | 2.0 | 0.9 | 21.3 | 0.2 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Lying | Sitting | 36.3 | 26.2 | 1.1 | 1.5 | 26.9 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Lying | Sitting | 32.2 | 22.3 | 0.7 | 3.1 | 12.9 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 102 | Lying | Sitting | 45.2 | 25.9 | 2.5 | 2.1 | 53.5 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 103 | Lying | Sitting | 45.6 | 35.3 | 6.7 | 0.5 | 126.2 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 104 | Lying | Sitting | 41.2 | 33.6 | 9.8 | 0.5 | 94.6 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 105 | Lying | Sitting | 35.3 | 38.9 | 13.4 | 0.8 | 106.7 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 106 | Lying | Sitting | 44.7 | 41.7 | 19.8 | 2.0 | 192.4 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 107 | Lying | Sitting | 48.2 | 38.5 | 22.4 | 0.9 | 77.0 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 108 | Lying | Sitting | 76.8 | 50.3 | 28.0 | 1.1 | 167.5 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 109 | Lying | Sitting | 73.0 | 41.8 | 34.0 | 2.6 | 180.9 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Lying |

---

## Normal_Fall_2

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 29 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 31 | 0 |

**Fall detection:** TP (latency 71 frames)

**Mismatched frames:**

_None_

---

## normal (**posture<90%**)

**Posture accuracy:** 88.0%

**Per-class accuracy:**

- Standing: 70.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 84 | 19 | 17 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 181 | 0 |

**Fall detection:** TP (latency 75 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 85 | Standing | Sitting | 139.9 | 140.3 | 2.8 | 2.8 | 19.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 86 | Standing | Sitting | 134.1 | 135.7 | 2.7 | 2.3 | 1.3 | 0.4 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 87 | Standing | Sitting | 131.5 | 134.2 | 3.1 | 2.5 | 19.0 | 0.4 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 88 | Standing | Sitting | 126.6 | 129.4 | 3.6 | 2.7 | 35.0 | 0.4 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 89 | Standing | Sitting | 119.2 | 123.4 | 4.6 | 2.6 | 58.5 | 0.4 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 90 | Standing | Sitting | 110.8 | 118.2 | 5.9 | 2.2 | 74.9 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 91 | Standing | Sitting | 100.8 | 110.3 | 7.3 | 2.5 | 87.7 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 92 | Standing | Sitting | 89.2 | 99.2 | 8.9 | 3.4 | 96.1 | 0.3 | 0.7 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 93 | Standing | Sitting | 90.2 | 99.3 | 10.9 | 2.5 | 116.7 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 94 | Standing | Sitting | 87.8 | 96.3 | 12.6 | 3.5 | 101.8 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 95 | Standing | Sitting | 74.8 | 82.7 | 14.2 | 3.6 | 96.0 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 96 | Standing | Sitting | 62.8 | 70.3 | 15.7 | 3.0 | 89.3 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 97 | Standing | Sitting | 54.2 | 63.5 | 17.8 | 3.3 | 130.0 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 98 | Standing | Sitting | 53.3 | 57.4 | 20.2 | 2.6 | 142.4 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Standing | Sitting | 52.4 | 57.3 | 22.2 | 1.0 | 121.6 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Standing | Sitting | 50.8 | 56.0 | 23.8 | 1.3 | 97.3 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Standing | Sitting | 57.6 | 62.4 | 27.1 | 1.4 | 196.6 | 0.3 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 102 | Standing | Sitting | 62.0 | 63.4 | 29.6 | 1.3 | 148.5 | 0.3 | 0.7 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 103 | Standing | Sitting | 60.4 | 52.8 | 32.1 | 1.1 | 150.6 | 0.3 | 0.7 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Lying |
| 104 | Standing | Lying | 60.4 | 62.4 | 35.0 | 0.5 | 171.7 | 0.3 | 0.7 | 0.1 | F | F | Sitting|Sitting|Sitting|Lying|Lying |
| 105 | Standing | Lying | 61.2 | 65.8 | 38.7 | 0.7 | 223.0 | 0.2 | 0.7 | 0.1 | F | F | Sitting|Sitting|Lying|Lying|Lying |
| 106 | Standing | Lying | 60.8 | 66.7 | 42.9 | 1.1 | 252.9 | 0.2 | 0.7 | 0.2 | F | F | Sitting|Lying|Lying|Lying|Lying |
| 107 | Standing | Lying | 71.9 | 74.0 | 46.7 | 1.2 | 227.9 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 108 | Standing | Lying | 69.0 | 94.1 | 49.5 | 1.9 | 170.7 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 109 | Standing | Lying | 71.6 | 97.7 | 53.0 | 0.9 | 204.6 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 110 | Standing | Lying | 66.8 | 96.0 | 55.9 | 0.6 | 177.4 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 111 | Standing | Lying | 66.9 | 94.7 | 58.0 | 1.0 | 124.9 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 112 | Standing | Lying | 74.6 | 102.2 | 59.2 | 0.6 | 72.7 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 113 | Standing | Lying | 71.6 | 98.8 | 59.8 | 0.6 | 36.5 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 114 | Standing | Lying | 72.9 | 99.2 | 60.6 | 0.7 | 46.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 115 | Standing | Lying | 80.2 | 103.0 | 62.4 | 0.4 | 111.3 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 116 | Standing | Lying | 73.5 | 98.1 | 64.4 | 0.7 | 116.0 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 117 | Standing | Lying | 69.7 | 96.3 | 65.9 | 0.2 | 89.7 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 118 | Standing | Lying | 66.8 | 94.3 | 67.1 | 0.1 | 76.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 119 | Standing | Lying | 66.5 | 94.6 | 67.3 | 0.3 | 9.2 | 0.2 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |
| 120 | Standing | Lying | 67.7 | 95.6 | 67.3 | 0.2 | 0.1 | 0.3 | 0.7 | 0.2 | F | F | Lying|Lying|Lying|Lying|Lying |

---

## Off_axis

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 180 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## old

**Posture accuracy:** 97.0%

**Per-class accuracy:**

- Standing: 96.2%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 404 | 16 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 121 | 0 |

**Fall detection:** TP (latency 106 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 184 | Standing | Sitting | nan | 168.8 | 10.4 | 0.3 | 4.4 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 185 | Standing | Sitting | nan | 169.1 | 10.4 | 0.2 | 1.9 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 186 | Standing | Sitting | nan | 169.0 | 10.6 | 0.2 | 9.6 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 187 | Standing | Sitting | nan | 168.7 | 10.8 | 0.1 | 12.2 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 188 | Standing | Sitting | nan | 168.5 | 10.7 | 0.1 | 3.0 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 189 | Standing | Sitting | nan | 168.3 | 10.7 | 0.2 | 2.0 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 190 | Standing | Sitting | nan | 168.4 | 10.6 | 0.2 | 3.1 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 191 | Standing | Sitting | nan | 168.2 | 10.7 | 0.3 | 3.6 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 192 | Standing | Sitting | nan | 168.2 | 10.7 | 0.2 | 0.1 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 193 | Standing | Sitting | nan | 167.8 | 10.8 | 0.3 | 3.6 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 194 | Standing | Sitting | nan | 167.6 | 11.1 | 0.5 | 22.2 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 195 | Standing | Sitting | 174.7 | 167.6 | 11.2 | 0.3 | 4.0 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 196 | Standing | Sitting | 175.1 | 168.2 | 10.9 | 0.1 | 16.7 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 197 | Standing | Sitting | 175.9 | 168.9 | 10.6 | 0.2 | 19.7 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 198 | Standing | Sitting | 176.0 | 169.3 | 10.3 | 0.1 | 16.3 | 0.6 | 0.8 | 0.5 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 420 | Standing | Sitting | 137.3 | 156.7 | 18.2 | 1.0 | 30.1 | 0.5 | 0.8 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Sit_1 (**posture<90%**)

**Posture accuracy:** 65.6%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 0.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 59 | 0 | 0 | 0 |
| **Sitting** | 31 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 120 | Sitting | Standing | nan | nan | 17.2 | 0.1 | 1.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Sitting | Standing | nan | nan | 18.1 | 0.3 | 26.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Sitting | Standing | nan | nan | 17.5 | 0.1 | 18.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Sitting | Standing | nan | nan | 17.0 | 0.2 | 13.8 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Sitting | Standing | nan | nan | 16.3 | 0.0 | 20.4 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Sitting | Standing | nan | nan | 16.5 | 0.3 | 5.9 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Sitting | Standing | nan | nan | 16.1 | 0.1 | 12.9 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Sitting | Standing | nan | nan | 15.9 | 0.0 | 6.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Sitting | Standing | nan | nan | 14.6 | 0.3 | 38.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Sitting | Standing | nan | nan | 14.3 | 0.0 | 10.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Sitting | Standing | nan | nan | 13.9 | 0.1 | 12.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Sitting | Standing | nan | nan | 13.3 | 0.1 | 16.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Sitting | Standing | nan | nan | 12.6 | 0.2 | 22.9 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Sitting | Standing | nan | nan | 12.4 | 0.0 | 3.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Sitting | Standing | nan | nan | 11.9 | 0.2 | 15.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Sitting | Standing | nan | nan | 12.4 | 0.1 | 15.4 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Sitting | Standing | nan | nan | 13.3 | 0.2 | 25.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Sitting | Standing | nan | nan | 13.2 | 0.1 | 4.4 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Sitting | Standing | nan | nan | 12.9 | 0.1 | 7.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Sitting | Standing | nan | nan | 12.9 | 0.1 | 0.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Sitting | Standing | nan | nan | 12.4 | 0.1 | 14.8 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Sitting | Standing | nan | nan | 12.4 | 0.0 | 0.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Sitting | Standing | nan | nan | 12.4 | 0.0 | 0.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Sitting | Standing | nan | nan | 12.8 | 0.1 | 14.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Sitting | Standing | nan | nan | 12.3 | 0.2 | 16.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Sitting | Standing | nan | nan | 11.6 | 0.2 | 20.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Sitting | Standing | nan | nan | 10.7 | 0.2 | 26.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Sitting | Standing | nan | nan | 10.4 | 0.1 | 11.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 148 | Sitting | Standing | nan | nan | 10.3 | 0.1 | 1.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 149 | Sitting | Standing | nan | nan | 11.3 | 0.3 | 30.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 150 | Sitting | Standing | nan | nan | 11.3 | 0.0 | 1.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Sit_2 (**posture<90%**)

**Posture accuracy:** 65.6%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 0.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 59 | 0 | 0 | 0 |
| **Sitting** | 31 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 120 | Sitting | Standing | nan | nan | 16.5 | 0.1 | 2.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Sitting | Standing | nan | nan | 16.9 | 0.0 | 11.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Sitting | Standing | nan | nan | 17.1 | 0.2 | 5.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Sitting | Standing | nan | nan | 17.5 | 0.2 | 11.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Sitting | Standing | nan | nan | 17.9 | 0.2 | 13.4 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Sitting | Standing | nan | nan | 18.4 | 0.3 | 14.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Sitting | Standing | nan | nan | 17.8 | 0.1 | 17.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Sitting | Standing | nan | nan | 18.0 | 0.1 | 5.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Sitting | Standing | nan | nan | 17.4 | 0.3 | 16.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Sitting | Standing | nan | nan | 15.6 | 0.5 | 56.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Sitting | Standing | nan | nan | 15.9 | 0.2 | 10.9 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Sitting | Standing | nan | nan | 16.8 | 0.3 | 24.8 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Sitting | Standing | nan | nan | 16.7 | 0.2 | 1.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Sitting | Standing | nan | nan | 16.7 | 0.0 | 1.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Sitting | Standing | nan | nan | 16.5 | 0.0 | 4.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Sitting | Standing | nan | nan | 16.7 | 0.0 | 6.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Sitting | Standing | nan | nan | 16.9 | 0.1 | 6.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Sitting | Standing | nan | nan | 16.9 | 0.1 | 0.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Sitting | Standing | nan | nan | 17.0 | 0.1 | 1.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Sitting | Standing | nan | nan | 17.0 | 0.0 | 0.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Sitting | Standing | nan | nan | 17.3 | 0.2 | 9.9 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Sitting | Standing | nan | nan | 17.3 | 0.0 | 1.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Sitting | Standing | nan | nan | 17.8 | 0.1 | 13.8 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Sitting | Standing | nan | nan | 17.8 | 0.0 | 0.2 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Sitting | Standing | nan | nan | 18.1 | 0.0 | 8.3 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Sitting | Standing | nan | nan | 18.2 | 0.0 | 3.5 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Sitting | Standing | nan | nan | 18.2 | 0.0 | 0.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Sitting | Standing | nan | nan | 18.4 | 0.1 | 5.6 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 148 | Sitting | Standing | nan | nan | 18.4 | 0.1 | 0.1 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 149 | Sitting | Standing | nan | nan | 18.2 | 0.0 | 4.7 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 150 | Sitting | Standing | nan | nan | 18.7 | 0.2 | 14.0 | 0.2 | 0.2 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Sit_3 (**posture<90%**)

**Posture accuracy:** 0.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: 0.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 91 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | Sitting | Standing | nan | nan | 24.9 | 1.3 | 3.7 | 0.3 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 61 | Sitting | Standing | nan | nan | 22.8 | 0.8 | 62.6 | 0.3 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 62 | Sitting | Standing | nan | nan | 19.2 | 0.8 | 108.8 | 0.3 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 63 | Sitting | Standing | nan | nan | 15.1 | 0.7 | 123.9 | 0.3 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 64 | Sitting | Standing | nan | nan | 11.2 | 0.9 | 115.0 | 0.3 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 65 | Sitting | Standing | nan | nan | 9.5 | 0.2 | 51.8 | 0.3 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 66 | Sitting | Standing | nan | nan | 7.0 | 0.3 | 75.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 67 | Sitting | Standing | nan | nan | 6.0 | 0.3 | 31.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 68 | Sitting | Standing | nan | nan | 4.0 | 0.3 | 59.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 69 | Sitting | Standing | nan | nan | 1.5 | 0.2 | 75.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 70 | Sitting | Standing | nan | nan | 0.7 | 0.2 | 24.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 71 | Sitting | Standing | nan | nan | 0.4 | 0.1 | 7.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 72 | Sitting | Standing | nan | nan | 4.3 | 0.3 | 114.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 73 | Sitting | Standing | nan | nan | 5.9 | 0.3 | 48.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 74 | Sitting | Standing | nan | nan | 7.9 | 0.5 | 60.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 75 | Sitting | Standing | nan | nan | 7.1 | 0.2 | 23.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 76 | Sitting | Standing | nan | nan | 10.0 | 0.4 | 87.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 77 | Sitting | Standing | nan | nan | 9.6 | 0.2 | 13.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 78 | Sitting | Standing | nan | nan | 8.8 | 0.2 | 21.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 79 | Sitting | Standing | nan | nan | 7.4 | 0.5 | 41.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 80 | Sitting | Standing | nan | nan | 9.7 | 0.0 | 67.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 81 | Sitting | Standing | nan | nan | 8.1 | 0.2 | 47.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 82 | Sitting | Standing | nan | nan | 7.4 | 0.0 | 19.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 83 | Sitting | Standing | nan | nan | 7.1 | 0.3 | 9.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Sitting | Standing | nan | nan | 6.0 | 0.1 | 33.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Sitting | Standing | nan | nan | 6.1 | 0.3 | 1.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Sitting | Standing | nan | nan | 7.2 | 0.3 | 33.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Sitting | Standing | nan | nan | 9.1 | 0.3 | 57.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Sitting | Standing | nan | nan | 8.5 | 0.1 | 18.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Sitting | Standing | nan | nan | 8.0 | 0.2 | 14.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Sitting | Standing | nan | nan | 6.5 | 0.1 | 44.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Sitting | Standing | nan | nan | 5.7 | 0.1 | 24.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Sitting | Standing | nan | nan | 6.8 | 0.3 | 34.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Sitting | Standing | nan | nan | 6.6 | 0.1 | 7.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Sitting | Standing | nan | nan | 5.0 | 0.0 | 47.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Sitting | Standing | nan | nan | 4.3 | 0.1 | 19.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Sitting | Standing | nan | nan | 3.6 | 0.3 | 23.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Sitting | Standing | nan | nan | 2.8 | 0.2 | 24.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Sitting | Standing | nan | nan | 2.5 | 0.0 | 6.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Sitting | Standing | nan | nan | 2.3 | 0.1 | 6.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Sitting | Standing | nan | nan | 0.4 | 0.2 | 57.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 101 | Sitting | Standing | nan | nan | 1.2 | 0.3 | 23.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 102 | Sitting | Standing | nan | nan | 1.3 | 0.1 | 3.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 103 | Sitting | Standing | nan | nan | 0.4 | 0.5 | 25.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 104 | Sitting | Standing | nan | nan | 0.0 | 0.0 | 13.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 105 | Sitting | Standing | nan | nan | 0.1 | 0.3 | 2.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 106 | Sitting | Standing | nan | nan | 0.0 | 0.0 | 1.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 107 | Sitting | Standing | nan | nan | 0.7 | 0.1 | 20.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 108 | Sitting | Standing | nan | nan | 1.1 | 0.2 | 12.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 109 | Sitting | Standing | nan | nan | 2.9 | 0.4 | 54.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 110 | Sitting | Standing | nan | nan | 2.9 | 0.0 | 1.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 111 | Sitting | Standing | nan | nan | 2.4 | 0.1 | 14.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 112 | Sitting | Standing | nan | nan | 2.6 | 0.1 | 5.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 113 | Sitting | Standing | nan | nan | 2.7 | 0.1 | 3.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 114 | Sitting | Standing | nan | nan | 2.9 | 0.0 | 5.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 115 | Sitting | Standing | nan | nan | 3.3 | 0.2 | 11.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 116 | Sitting | Standing | nan | nan | 2.8 | 0.2 | 15.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 117 | Sitting | Standing | nan | nan | 3.1 | 0.2 | 11.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 118 | Sitting | Standing | nan | nan | 2.3 | 0.2 | 25.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 119 | Sitting | Standing | nan | nan | 1.7 | 0.2 | 17.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 120 | Sitting | Standing | nan | nan | 1.6 | 0.2 | 4.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Sitting | Standing | nan | nan | 2.5 | 0.5 | 27.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Sitting | Standing | nan | nan | 2.6 | 0.0 | 2.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Sitting | Standing | nan | nan | 0.8 | 0.1 | 52.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Sitting | Standing | nan | nan | 1.8 | 0.2 | 30.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Sitting | Standing | nan | nan | 1.2 | 0.1 | 19.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Sitting | Standing | nan | nan | 2.2 | 0.2 | 30.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Sitting | Standing | nan | nan | 1.7 | 0.3 | 16.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Sitting | Standing | nan | nan | 1.5 | 0.1 | 6.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Sitting | Standing | nan | nan | 1.2 | 0.2 | 8.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Sitting | Standing | nan | nan | 0.2 | 0.2 | 28.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Sitting | Standing | nan | nan | 1.2 | 0.1 | 29.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Sitting | Standing | nan | nan | 1.2 | 0.1 | 0.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Sitting | Standing | nan | nan | 1.2 | 0.0 | 0.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Sitting | Standing | nan | nan | 2.5 | 0.4 | 37.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Sitting | Standing | nan | nan | 2.3 | 0.1 | 3.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Sitting | Standing | nan | nan | 1.9 | 0.1 | 13.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Sitting | Standing | nan | nan | 1.5 | 0.0 | 11.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Sitting | Standing | nan | nan | 0.8 | 0.5 | 23.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Sitting | Standing | nan | nan | 0.7 | 0.1 | 1.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Sitting | Standing | nan | nan | 0.9 | 0.4 | 4.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Sitting | Standing | nan | nan | 0.3 | 0.1 | 16.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Sitting | Standing | nan | nan | 0.1 | 0.1 | 6.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Sitting | Standing | nan | nan | 0.4 | 0.1 | 10.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Sitting | Standing | nan | nan | 0.2 | 0.0 | 7.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Sitting | Standing | nan | nan | 0.1 | 0.1 | 2.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Sitting | Standing | nan | nan | 1.1 | 0.3 | 29.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Sitting | Standing | nan | nan | 0.7 | 0.4 | 10.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 148 | Sitting | Standing | nan | nan | 0.5 | 0.2 | 7.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 149 | Sitting | Standing | nan | nan | 0.8 | 0.1 | 8.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 150 | Sitting | Standing | nan | nan | 0.8 | 0.2 | 0.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Standing_1

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 150 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Standing_2

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 166 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Standing_3

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 120 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

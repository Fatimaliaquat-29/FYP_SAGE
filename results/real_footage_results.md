# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| Fall_Curled | 100.0% | TP (latency 9 frames) |  |
| Fast_Sit | 100.0% | - |  |
| Lying_legs_straight | 100.0% | - |  |
| Lying_straight | 100.0% | - |  |
| newTest | 74.0% | TP (latency 76 frames) | **posture<90%** |
| Normal_Fall_1 | 83.3% | TP (latency 18 frames) | **posture<90%** |
| Normal_Fall_2 | 100.0% | TP (latency 8 frames) |  |
| normal | 89.4% | TP (latency 81 frames) | **posture<90%** |
| Off_axis | 100.0% | - |  |
| old | 100.0% | TP (latency 114 frames) |  |
| Sit_1 | 100.0% | - |  |
| Sit_2 | 54.4% | - | **posture<90%** |
| Sit_3 | 94.5% | - |  |
| Standing_1 | 100.0% | - |  |
| Standing_2 | 100.0% | - |  |
| Standing_3 | 100.0% | - |  |

---

## Fall_Curled

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

**Fall detection:** TP (latency 9 frames)

**Mismatched frames:**

_None_

---

## Fast_Sit

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: 100.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 31 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

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

**Posture accuracy:** 74.0%

**Per-class accuracy:**

- Standing: 70.4%
- Sitting: nan%
- Lying: 92.3%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 1689 | 574 | 0 | 137 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 37 | 0 | 443 | 0 |

**Fall detection:** TP (latency 76 frames)

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
| 72 | Standing | Unknown | 143.7 | 148.7 | 7.6 | 0.0 | 0.0 | 0.6 | 0.6 | 0.2 | F | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 73 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 74 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 75 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 76 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 77 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 78 | Standing | Unknown | 167.2 | 157.5 | 9.4 | 1.2 | 18.2 | 0.6 | 0.6 | 0.3 | F | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 79 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 80 | Standing | Unknown | 173.9 | 146.8 | 11.3 | 0.7 | 56.4 | 0.6 | 0.6 | 0.3 | F | F | Unknown|Unknown|Standing|Unknown|Standing |
| 81 | Standing | Unknown | 175.2 | 155.4 | 14.2 | 3.0 | 171.9 | 0.5 | 0.5 | 0.3 | F | F | Unknown|Standing|Unknown|Standing|Standing |
| 82 | Standing | Unknown | 167.7 | 167.9 | 12.3 | 3.2 | 112.2 | 0.5 | 0.5 | 0.3 | F | F | Standing|Unknown|Standing|Standing|Standing |
| 83 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Standing|Standing|Unknown |
| 84 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 85 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 86 | Standing | Unknown | 110.5 | 136.0 | 18.0 | 0.8 | 84.7 | 0.5 | 0.5 | 0.3 | F | F | Standing|Unknown|Unknown|Unknown|Sitting |
| 87 | Standing | Unknown | 72.6 | 128.6 | 20.0 | 0.3 | 119.9 | 0.5 | 0.5 | 0.3 | F | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 88 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Sitting|Unknown |
| 89 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Sitting|Unknown|Unknown |
| 90 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Unknown|Unknown |
| 91 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 92 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 93 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 94 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 95 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 96 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 97 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 98 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 99 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 100 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 101 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 102 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 103 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 104 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 105 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 106 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 107 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 108 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 109 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 110 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 111 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 112 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 113 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 114 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 115 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 116 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 117 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 118 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 119 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 120 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 121 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 122 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 123 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 124 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 125 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 126 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 127 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 128 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 129 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 130 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 131 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 132 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 133 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 134 | Standing | Unknown | nan | nan | 0.6 | 2.7 | 24.7 | 1.0 | 1.0 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 135 | Standing | Unknown | nan | nan | 0.1 | 1.3 | 31.5 | 1.1 | 1.1 | -0.1 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 136 | Standing | Unknown | nan | nan | 0.2 | 2.0 | 4.9 | 1.1 | 1.1 | -0.0 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 137 | Standing | Unknown | nan | nan | 1.0 | 1.4 | 47.9 | 1.1 | 1.1 | -0.1 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 195 | Standing | Sitting | nan | 175.4 | 0.0 | 0.2 | 3.4 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 196 | Standing | Sitting | nan | 175.4 | 0.4 | 0.3 | 22.5 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 197 | Standing | Sitting | nan | 175.3 | 0.4 | 0.1 | 0.6 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 198 | Standing | Sitting | nan | 175.6 | 0.2 | 1.1 | 10.6 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 199 | Standing | Sitting | nan | 175.3 | 0.3 | 0.6 | 4.9 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 200 | Standing | Sitting | nan | 176.7 | 0.3 | 0.2 | 0.7 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 201 | Standing | Sitting | nan | 176.0 | 0.1 | 0.2 | 12.6 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 202 | Standing | Sitting | nan | 175.6 | 0.3 | 0.2 | 11.2 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 203 | Standing | Sitting | nan | 175.5 | 0.4 | 0.5 | 6.0 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 204 | Standing | Sitting | nan | 176.5 | 0.2 | 0.0 | 10.6 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 205 | Standing | Sitting | nan | 176.5 | 0.1 | 0.5 | 7.6 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 206 | Standing | Sitting | nan | 176.8 | 0.2 | 0.3 | 5.2 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 207 | Standing | Sitting | nan | 176.9 | 0.2 | 0.5 | 4.7 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 208 | Standing | Sitting | nan | 177.6 | 0.6 | 0.0 | 19.3 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 209 | Standing | Sitting | nan | 177.0 | 0.8 | 0.3 | 13.5 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 210 | Standing | Sitting | nan | 177.4 | 0.8 | 0.2 | 0.9 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 211 | Standing | Sitting | nan | 177.4 | 0.7 | 0.4 | 3.6 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 212 | Standing | Sitting | nan | 177.1 | 0.5 | 0.2 | 13.6 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 213 | Standing | Sitting | nan | 177.5 | 0.4 | 0.2 | 6.9 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 214 | Standing | Sitting | nan | 178.2 | 0.5 | 0.5 | 4.7 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 215 | Standing | Sitting | nan | 178.5 | 0.3 | 0.4 | 13.3 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 216 | Standing | Sitting | nan | 178.4 | 0.0 | 0.2 | 13.7 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 217 | Standing | Sitting | nan | 178.5 | 0.7 | 0.2 | 41.6 | 1.0 | 1.1 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 218 | Standing | Sitting | nan | 178.9 | 0.1 | 0.7 | 37.4 | 0.9 | 1.1 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Sitting |
| 219 | Standing | Sitting | 172.4 | 179.2 | 0.5 | 0.9 | 23.6 | 0.8 | 1.1 | 0.4 | F | F | Standing|Standing|Standing|Sitting|Standing |
| 220 | Standing | Sitting | 169.6 | 179.5 | 0.4 | 0.5 | 4.3 | 0.7 | 1.1 | 0.4 | F | F | Standing|Standing|Sitting|Standing|Standing |
| 221 | Standing | Sitting | 168.5 | 179.1 | 0.4 | 1.4 | 1.8 | 0.7 | 1.1 | 0.4 | F | F | Standing|Sitting|Standing|Standing|Standing |
| 222 | Standing | Sitting | 165.3 | 179.2 | 0.6 | 0.5 | 10.8 | 0.7 | 1.1 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 928 | Standing | Sitting | 142.4 | 165.9 | 2.3 | 1.0 | 39.5 | 0.5 | 0.8 | 0.6 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 929 | Standing | Sitting | 155.3 | 172.6 | 2.4 | 0.3 | 6.8 | 0.5 | 0.8 | 0.6 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 930 | Standing | Sitting | 158.8 | 173.4 | 2.9 | 0.2 | 30.8 | 0.6 | 0.8 | 0.6 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 931 | Standing | Sitting | 160.3 | 174.3 | 1.9 | 0.7 | 60.2 | 0.5 | 0.8 | 0.6 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 932 | Standing | Sitting | 153.1 | 169.5 | 2.7 | 0.5 | 48.3 | 0.5 | 0.8 | 0.6 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 1085 | Standing | Sitting | 139.8 | 143.5 | 4.1 | 0.3 | 33.2 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1086 | Standing | Sitting | 140.1 | 144.6 | 3.4 | 0.3 | 39.4 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1087 | Standing | Sitting | 139.6 | 143.9 | 3.8 | 0.2 | 21.1 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1088 | Standing | Sitting | 136.8 | 140.8 | 4.4 | 0.7 | 39.3 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1089 | Standing | Sitting | 132.1 | 135.9 | 4.0 | 0.2 | 27.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1090 | Standing | Sitting | 138.6 | 142.8 | 3.9 | 0.7 | 6.2 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1091 | Standing | Sitting | 139.0 | 143.9 | 3.7 | 0.1 | 7.1 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1092 | Standing | Sitting | 143.4 | 147.4 | 4.0 | 0.6 | 15.4 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1093 | Standing | Sitting | 138.9 | 144.4 | 4.2 | 0.2 | 11.1 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 1094 | Standing | Sitting | 137.5 | 142.3 | 4.4 | 0.5 | 12.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 1095 | Standing | Sitting | 135.6 | 140.9 | 4.7 | 0.2 | 18.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 1096 | Standing | Sitting | 135.0 | 140.6 | 5.0 | 0.4 | 16.4 | 0.4 | 0.7 | 0.4 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 1097 | Standing | Sitting | 137.7 | 143.1 | 5.3 | 0.3 | 20.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1098 | Standing | Sitting | 136.2 | 141.8 | 5.4 | 0.1 | 4.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1099 | Standing | Sitting | 134.4 | 140.5 | 5.7 | 0.1 | 17.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1100 | Standing | Sitting | 133.2 | 139.3 | 5.9 | 0.1 | 15.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1101 | Standing | Sitting | 136.9 | 142.7 | 6.2 | 0.2 | 15.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1102 | Standing | Sitting | 134.8 | 140.9 | 6.2 | 0.2 | 2.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1103 | Standing | Sitting | 132.3 | 138.8 | 6.6 | 0.2 | 27.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1104 | Standing | Sitting | 135.5 | 141.8 | 6.6 | 0.2 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1105 | Standing | Sitting | 136.0 | 142.1 | 6.7 | 0.1 | 5.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1106 | Standing | Sitting | 139.8 | 145.6 | 6.6 | 0.3 | 7.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1107 | Standing | Sitting | 143.8 | 148.5 | 6.9 | 0.2 | 19.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1108 | Standing | Sitting | 144.0 | 148.5 | 7.0 | 0.1 | 6.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 1109 | Standing | Sitting | 141.8 | 146.4 | 6.8 | 0.2 | 12.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Sitting |
| 1110 | Standing | Sitting | 143.8 | 147.5 | 6.8 | 0.3 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Standing|Standing|Sitting|Standing |
| 1111 | Standing | Sitting | 144.0 | 147.6 | 6.7 | 0.1 | 5.3 | 0.4 | 0.7 | 0.4 | F | F | Standing|Standing|Sitting|Standing|Standing |
| 1112 | Standing | Sitting | 144.8 | 148.8 | 7.1 | 0.4 | 20.4 | 0.4 | 0.7 | 0.4 | F | F | Standing|Sitting|Standing|Standing|Standing |
| 1113 | Standing | Sitting | 141.9 | 146.3 | 7.3 | 0.3 | 15.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Sitting |
| 1114 | Standing | Sitting | 144.8 | 149.2 | 7.4 | 0.0 | 5.9 | 0.4 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Sitting|Standing |
| 1115 | Standing | Sitting | 141.4 | 145.8 | 7.6 | 0.3 | 8.4 | 0.4 | 0.7 | 0.4 | F | F | Standing|Standing|Sitting|Standing|Sitting |
| 1116 | Standing | Sitting | 143.5 | 147.0 | 7.6 | 0.1 | 1.4 | 0.4 | 0.7 | 0.4 | F | F | Standing|Sitting|Standing|Sitting|Standing |
| 1117 | Standing | Sitting | 141.7 | 145.9 | 7.5 | 0.3 | 8.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Standing|Sitting|Standing|Sitting |
| 1118 | Standing | Sitting | 143.3 | 146.9 | 7.4 | 0.1 | 4.2 | 0.4 | 0.7 | 0.4 | F | F | Standing|Sitting|Standing|Sitting|Standing |
| 1119 | Standing | Sitting | 140.0 | 143.9 | 7.5 | 0.1 | 7.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Standing|Sitting|Standing|Sitting |
| 1120 | Standing | Sitting | 142.3 | 146.3 | 7.5 | 0.1 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Standing|Sitting|Standing|Sitting|Sitting |
| 1121 | Standing | Sitting | 142.6 | 146.7 | 7.7 | 0.3 | 12.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 1122 | Standing | Sitting | 141.1 | 145.8 | 7.5 | 0.7 | 11.7 | 0.4 | 0.7 | 0.4 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 1123 | Standing | Sitting | 140.7 | 144.8 | 7.7 | 0.5 | 8.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1124 | Standing | Sitting | 141.5 | 145.7 | 7.8 | 0.1 | 6.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1125 | Standing | Sitting | 141.6 | 145.9 | 7.7 | 0.2 | 6.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1126 | Standing | Sitting | 142.0 | 146.1 | 7.6 | 0.2 | 1.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1127 | Standing | Sitting | 141.4 | 146.0 | 7.5 | 0.1 | 8.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1128 | Standing | Sitting | 141.9 | 147.0 | 7.1 | 0.2 | 23.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1129 | Standing | Sitting | 142.0 | 146.4 | 7.5 | 0.4 | 24.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1130 | Standing | Sitting | 141.2 | 146.7 | 7.7 | 0.1 | 9.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1131 | Standing | Sitting | 140.7 | 146.4 | 7.4 | 0.6 | 15.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1132 | Standing | Sitting | 139.9 | 145.7 | 7.6 | 0.5 | 11.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1133 | Standing | Sitting | 138.5 | 144.7 | 7.5 | 0.1 | 6.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1134 | Standing | Sitting | 137.4 | 143.7 | 7.3 | 0.3 | 12.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1135 | Standing | Sitting | 138.6 | 144.7 | 7.4 | 0.2 | 7.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1136 | Standing | Sitting | 137.8 | 143.8 | 7.5 | 0.1 | 7.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1137 | Standing | Sitting | 136.8 | 143.0 | 7.5 | 0.2 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1138 | Standing | Sitting | 139.1 | 144.9 | 7.6 | 0.6 | 4.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1139 | Standing | Sitting | 139.4 | 145.8 | 7.6 | 0.2 | 2.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1140 | Standing | Sitting | 135.9 | 142.6 | 7.4 | 0.2 | 8.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1141 | Standing | Sitting | 138.2 | 144.4 | 7.5 | 0.3 | 7.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1142 | Standing | Sitting | 136.9 | 143.9 | 7.5 | 0.1 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1143 | Standing | Sitting | 137.4 | 144.5 | 7.6 | 0.6 | 4.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1144 | Standing | Sitting | 137.8 | 144.7 | 7.6 | 0.1 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1145 | Standing | Sitting | 137.8 | 144.3 | 7.5 | 0.4 | 9.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1146 | Standing | Sitting | 138.1 | 145.0 | 7.6 | 0.3 | 6.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1147 | Standing | Sitting | 137.6 | 144.6 | 7.6 | 0.1 | 3.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1148 | Standing | Sitting | 137.6 | 144.3 | 7.5 | 0.1 | 6.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1149 | Standing | Sitting | 136.7 | 143.9 | 7.5 | 0.2 | 1.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1150 | Standing | Sitting | 138.7 | 146.2 | 7.4 | 0.4 | 7.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1151 | Standing | Sitting | 139.4 | 146.6 | 7.5 | 0.3 | 4.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1152 | Standing | Sitting | 139.8 | 147.0 | 7.4 | 0.1 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1153 | Standing | Sitting | 138.3 | 145.6 | 7.4 | 0.4 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1154 | Standing | Sitting | 138.4 | 145.6 | 7.6 | 0.5 | 13.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1155 | Standing | Sitting | 137.0 | 144.3 | 7.6 | 0.1 | 2.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1156 | Standing | Sitting | 136.2 | 143.2 | 7.6 | 0.1 | 2.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1157 | Standing | Sitting | 137.6 | 144.7 | 7.7 | 0.0 | 2.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1158 | Standing | Sitting | 135.2 | 142.3 | 7.4 | 0.1 | 14.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1159 | Standing | Sitting | 135.1 | 142.1 | 7.5 | 0.2 | 4.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1160 | Standing | Sitting | 133.4 | 140.7 | 7.5 | 0.0 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1161 | Standing | Sitting | 135.4 | 142.6 | 7.4 | 0.2 | 8.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1162 | Standing | Sitting | 134.5 | 141.8 | 7.6 | 0.3 | 12.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1163 | Standing | Sitting | 135.0 | 142.0 | 7.3 | 0.1 | 13.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1164 | Standing | Sitting | 137.2 | 144.0 | 7.4 | 0.1 | 3.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1165 | Standing | Sitting | 136.7 | 143.8 | 7.5 | 0.1 | 6.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1166 | Standing | Sitting | 137.1 | 144.0 | 7.4 | 0.1 | 4.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1167 | Standing | Sitting | 138.0 | 144.8 | 7.1 | 0.2 | 17.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1168 | Standing | Sitting | 137.8 | 144.8 | 7.2 | 0.1 | 3.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1169 | Standing | Sitting | 137.7 | 144.7 | 7.3 | 0.1 | 5.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1170 | Standing | Sitting | 138.3 | 145.1 | 7.2 | 0.1 | 5.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1171 | Standing | Sitting | 134.6 | 142.3 | 7.2 | 0.3 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1172 | Standing | Sitting | 135.6 | 142.6 | 7.3 | 0.1 | 3.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1173 | Standing | Sitting | 134.6 | 141.9 | 7.2 | 0.1 | 5.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1174 | Standing | Sitting | 135.1 | 142.3 | 7.2 | 0.2 | 2.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1175 | Standing | Sitting | 136.8 | 144.3 | 7.2 | 0.0 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1176 | Standing | Sitting | 137.8 | 145.5 | 7.2 | 0.2 | 1.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1177 | Standing | Sitting | 135.9 | 143.8 | 7.2 | 0.2 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1178 | Standing | Sitting | 135.6 | 144.0 | 7.3 | 0.4 | 5.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1179 | Standing | Sitting | 136.0 | 143.3 | 7.2 | 0.1 | 5.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1180 | Standing | Sitting | 135.4 | 142.4 | 7.2 | 0.1 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1181 | Standing | Sitting | 134.2 | 141.7 | 7.5 | 0.2 | 15.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1182 | Standing | Sitting | 134.4 | 141.9 | 7.4 | 0.4 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1183 | Standing | Sitting | 135.2 | 142.9 | 7.6 | 0.4 | 7.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1184 | Standing | Sitting | 134.6 | 142.8 | 7.3 | 0.3 | 14.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1185 | Standing | Sitting | 135.0 | 143.0 | 7.3 | 0.2 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1186 | Standing | Sitting | 137.0 | 145.0 | 7.4 | 0.2 | 3.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1187 | Standing | Sitting | 136.8 | 144.0 | 7.4 | 0.1 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1188 | Standing | Sitting | 133.5 | 141.5 | 7.4 | 0.3 | 2.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1189 | Standing | Sitting | 134.1 | 142.1 | 7.7 | 0.1 | 16.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1190 | Standing | Sitting | 134.8 | 141.7 | 7.6 | 0.3 | 1.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1191 | Standing | Sitting | 135.1 | 142.3 | 7.4 | 0.3 | 13.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1192 | Standing | Sitting | 134.5 | 141.9 | 7.4 | 0.1 | 3.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1193 | Standing | Sitting | 135.4 | 142.3 | 7.7 | 0.1 | 17.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1194 | Standing | Sitting | 133.3 | 140.8 | 7.7 | 0.3 | 2.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1195 | Standing | Sitting | 132.5 | 140.1 | 7.6 | 0.3 | 7.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1196 | Standing | Sitting | 135.0 | 141.8 | 7.6 | 0.2 | 2.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1197 | Standing | Sitting | 132.6 | 140.0 | 7.5 | 0.1 | 9.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1198 | Standing | Sitting | 133.1 | 141.0 | 7.7 | 0.2 | 11.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1199 | Standing | Sitting | 133.9 | 141.0 | 7.7 | 0.3 | 3.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1200 | Standing | Sitting | 133.9 | 141.1 | 7.8 | 0.3 | 5.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1201 | Standing | Sitting | 133.7 | 140.7 | 7.7 | 0.1 | 8.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1202 | Standing | Sitting | 133.8 | 141.5 | 7.6 | 0.2 | 5.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1203 | Standing | Sitting | 134.2 | 141.3 | 7.7 | 0.2 | 6.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1204 | Standing | Sitting | 135.0 | 140.9 | 7.7 | 0.2 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1205 | Standing | Sitting | 135.7 | 141.8 | 7.6 | 0.0 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1206 | Standing | Sitting | 134.8 | 141.0 | 7.8 | 0.1 | 7.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1207 | Standing | Sitting | 135.9 | 143.1 | 7.7 | 0.2 | 5.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1208 | Standing | Sitting | 133.8 | 140.5 | 7.7 | 0.1 | 2.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1209 | Standing | Sitting | 134.3 | 141.1 | 7.5 | 0.3 | 12.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1210 | Standing | Sitting | 136.2 | 143.4 | 7.7 | 0.2 | 12.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1211 | Standing | Sitting | 129.5 | 138.1 | 7.5 | 0.1 | 12.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1212 | Standing | Sitting | 130.4 | 138.5 | 7.6 | 0.1 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1213 | Standing | Sitting | 130.9 | 138.8 | 7.6 | 0.1 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1214 | Standing | Sitting | 130.0 | 138.5 | 7.6 | 0.2 | 0.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1215 | Standing | Sitting | 132.2 | 140.5 | 7.5 | 0.2 | 7.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1216 | Standing | Sitting | 132.6 | 140.6 | 7.6 | 0.1 | 8.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1217 | Standing | Sitting | 132.7 | 140.7 | 7.5 | 0.2 | 7.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1218 | Standing | Sitting | 134.0 | 141.6 | 7.5 | 0.0 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1219 | Standing | Sitting | 134.7 | 142.2 | 7.6 | 0.2 | 8.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1220 | Standing | Sitting | 134.7 | 142.2 | 7.5 | 0.0 | 8.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1221 | Standing | Sitting | 134.5 | 142.2 | 7.5 | 0.1 | 3.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1222 | Standing | Sitting | 132.7 | 141.5 | 7.5 | 0.3 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1223 | Standing | Sitting | 132.6 | 141.1 | 7.6 | 0.3 | 3.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1224 | Standing | Sitting | 133.2 | 141.0 | 7.6 | 0.1 | 0.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1225 | Standing | Sitting | 133.2 | 141.3 | 7.6 | 0.1 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1226 | Standing | Sitting | 133.5 | 141.8 | 7.7 | 0.2 | 6.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1227 | Standing | Sitting | 133.0 | 141.6 | 7.8 | 0.1 | 5.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1228 | Standing | Sitting | 134.2 | 142.0 | 7.7 | 0.4 | 6.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1229 | Standing | Sitting | 133.5 | 141.6 | 7.7 | 0.1 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1230 | Standing | Sitting | 137.0 | 144.9 | 7.5 | 0.3 | 10.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1231 | Standing | Sitting | 136.0 | 143.9 | 7.5 | 0.0 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1232 | Standing | Sitting | 135.9 | 143.7 | 7.4 | 0.1 | 3.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1233 | Standing | Sitting | 134.9 | 142.7 | 7.4 | 0.0 | 0.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1234 | Standing | Sitting | 135.5 | 143.2 | 7.5 | 0.2 | 5.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1235 | Standing | Sitting | 134.5 | 142.5 | 7.6 | 0.3 | 5.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1236 | Standing | Sitting | 133.1 | 141.4 | 7.7 | 0.2 | 3.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1237 | Standing | Sitting | 131.6 | 140.3 | 7.6 | 0.1 | 5.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1238 | Standing | Sitting | 134.9 | 143.3 | 7.6 | 0.4 | 1.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1239 | Standing | Sitting | 131.3 | 140.1 | 7.6 | 0.4 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1240 | Standing | Sitting | 131.0 | 139.7 | 7.6 | 0.0 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1241 | Standing | Sitting | 131.4 | 139.9 | 7.7 | 0.1 | 6.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1242 | Standing | Sitting | 131.0 | 139.6 | 7.8 | 0.1 | 2.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1243 | Standing | Sitting | 130.8 | 139.5 | 7.9 | 0.1 | 7.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1244 | Standing | Sitting | 133.1 | 141.0 | 7.9 | 0.2 | 0.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1245 | Standing | Sitting | 131.8 | 140.1 | 7.8 | 0.0 | 3.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1246 | Standing | Sitting | 131.7 | 140.6 | 7.6 | 0.5 | 11.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1247 | Standing | Sitting | 133.0 | 141.8 | 7.5 | 0.1 | 8.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1248 | Standing | Sitting | 132.5 | 141.3 | 7.6 | 0.1 | 6.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1249 | Standing | Sitting | 132.3 | 141.0 | 7.4 | 0.2 | 10.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1250 | Standing | Sitting | 131.8 | 140.9 | 7.4 | 0.1 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1251 | Standing | Sitting | 132.5 | 141.3 | 7.5 | 0.1 | 4.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1252 | Standing | Sitting | 132.3 | 141.2 | 7.6 | 0.0 | 3.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1253 | Standing | Sitting | 133.8 | 142.8 | 7.6 | 0.5 | 3.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1254 | Standing | Sitting | 134.3 | 143.1 | 7.6 | 0.0 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1255 | Standing | Sitting | 132.4 | 141.0 | 7.6 | 0.2 | 1.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1256 | Standing | Sitting | 133.3 | 141.5 | 7.5 | 0.1 | 8.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1257 | Standing | Sitting | 131.4 | 140.4 | 7.5 | 0.4 | 0.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1258 | Standing | Sitting | 131.8 | 140.2 | 7.5 | 0.1 | 5.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1259 | Standing | Sitting | 133.2 | 141.2 | 7.6 | 0.1 | 2.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1260 | Standing | Sitting | 132.9 | 141.1 | 7.7 | 0.0 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1261 | Standing | Sitting | 133.2 | 141.1 | 7.5 | 0.1 | 9.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1262 | Standing | Sitting | 133.4 | 141.2 | 7.6 | 0.1 | 6.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1263 | Standing | Sitting | 134.1 | 142.6 | 7.6 | 0.1 | 1.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1264 | Standing | Sitting | 135.1 | 142.8 | 7.7 | 0.1 | 5.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1265 | Standing | Sitting | 134.6 | 142.4 | 7.9 | 0.1 | 9.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1266 | Standing | Sitting | 132.9 | 141.6 | 7.7 | 0.4 | 11.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1267 | Standing | Sitting | 133.6 | 142.1 | 7.6 | 0.1 | 1.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1268 | Standing | Sitting | 131.7 | 140.1 | 7.6 | 0.3 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1269 | Standing | Sitting | 130.4 | 139.1 | 7.5 | 0.1 | 8.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1270 | Standing | Sitting | 132.4 | 140.8 | 7.5 | 0.1 | 5.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1271 | Standing | Sitting | 132.4 | 140.2 | 7.3 | 0.4 | 12.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1272 | Standing | Sitting | 131.1 | 139.3 | 7.2 | 0.0 | 6.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1273 | Standing | Sitting | 132.0 | 140.0 | 7.3 | 0.1 | 3.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1274 | Standing | Sitting | 130.9 | 139.2 | 7.3 | 0.0 | 1.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1275 | Standing | Sitting | 128.6 | 137.9 | 7.5 | 0.6 | 14.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1276 | Standing | Sitting | 132.6 | 141.1 | 7.5 | 0.1 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1277 | Standing | Sitting | 132.8 | 141.2 | 7.4 | 0.1 | 2.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1278 | Standing | Sitting | 135.9 | 144.3 | 7.4 | 0.1 | 2.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1279 | Standing | Sitting | 134.2 | 142.5 | 7.3 | 0.1 | 5.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1280 | Standing | Sitting | 134.0 | 142.4 | 7.2 | 0.0 | 5.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1281 | Standing | Sitting | 133.2 | 141.2 | 7.0 | 0.2 | 10.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1282 | Standing | Sitting | 133.5 | 141.6 | 7.3 | 0.3 | 15.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1283 | Standing | Sitting | 133.1 | 140.8 | 7.4 | 0.2 | 4.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1284 | Standing | Sitting | 135.1 | 142.1 | 7.3 | 0.0 | 7.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1285 | Standing | Sitting | 136.3 | 144.5 | 7.4 | 0.2 | 9.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1286 | Standing | Sitting | 136.2 | 143.1 | 7.4 | 0.2 | 3.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1287 | Standing | Sitting | 140.9 | 148.0 | 7.1 | 0.3 | 17.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1288 | Standing | Sitting | 139.3 | 146.3 | 7.4 | 0.5 | 18.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1289 | Standing | Sitting | 138.1 | 145.7 | 7.3 | 0.2 | 1.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1290 | Standing | Sitting | 138.0 | 145.7 | 7.3 | 0.1 | 3.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1291 | Standing | Sitting | 138.1 | 145.6 | 7.2 | 0.1 | 4.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1292 | Standing | Sitting | 138.3 | 145.7 | 7.2 | 0.0 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1293 | Standing | Sitting | 137.8 | 145.0 | 7.2 | 0.0 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1294 | Standing | Sitting | 134.4 | 142.5 | 7.3 | 0.1 | 7.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1295 | Standing | Sitting | 136.4 | 143.6 | 7.2 | 0.1 | 3.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1296 | Standing | Sitting | 135.2 | 142.0 | 7.4 | 0.1 | 10.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1297 | Standing | Sitting | 133.7 | 140.7 | 7.5 | 0.1 | 7.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1298 | Standing | Sitting | 135.2 | 142.4 | 7.5 | 0.1 | 2.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1299 | Standing | Sitting | 133.1 | 140.1 | 7.4 | 0.1 | 8.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1300 | Standing | Sitting | 132.2 | 139.6 | 7.4 | 0.0 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1301 | Standing | Sitting | 134.1 | 141.6 | 7.5 | 0.3 | 6.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1302 | Standing | Sitting | 132.4 | 140.7 | 7.9 | 0.2 | 23.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1303 | Standing | Sitting | 131.2 | 139.7 | 7.6 | 0.3 | 18.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1304 | Standing | Sitting | 130.4 | 138.7 | 7.7 | 0.1 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1305 | Standing | Sitting | 131.0 | 139.3 | 7.7 | 0.2 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1306 | Standing | Sitting | 126.1 | 135.5 | 7.4 | 0.5 | 13.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1307 | Standing | Sitting | 130.5 | 139.2 | 7.7 | 0.2 | 13.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1308 | Standing | Sitting | 134.4 | 142.2 | 7.6 | 0.3 | 6.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1309 | Standing | Sitting | 131.4 | 140.1 | 7.6 | 0.1 | 4.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1310 | Standing | Sitting | 134.4 | 141.8 | 7.8 | 0.1 | 11.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1311 | Standing | Sitting | 132.0 | 139.8 | 7.5 | 0.4 | 19.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1312 | Standing | Sitting | 133.6 | 141.4 | 7.4 | 0.2 | 4.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1313 | Standing | Sitting | 125.4 | 139.6 | 7.1 | 0.2 | 19.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1314 | Standing | Sitting | 136.0 | 144.6 | 7.3 | 0.3 | 12.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1315 | Standing | Sitting | 134.4 | 143.3 | 7.6 | 0.2 | 18.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1316 | Standing | Sitting | 138.4 | 145.8 | 7.4 | 0.2 | 13.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1317 | Standing | Sitting | 131.4 | 140.3 | 7.5 | 0.3 | 6.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1318 | Standing | Sitting | 132.7 | 140.9 | 7.7 | 0.4 | 8.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1319 | Standing | Sitting | 133.3 | 141.7 | 7.6 | 0.1 | 2.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1320 | Standing | Sitting | 137.7 | 145.7 | 7.7 | 0.2 | 7.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1321 | Standing | Sitting | 134.7 | 142.5 | 7.6 | 0.2 | 8.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1322 | Standing | Sitting | 132.3 | 141.4 | 7.4 | 0.1 | 8.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1323 | Standing | Sitting | 132.5 | 140.7 | 7.4 | 0.2 | 0.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1324 | Standing | Sitting | 134.2 | 142.4 | 7.5 | 0.3 | 2.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1325 | Standing | Sitting | 134.0 | 142.4 | 7.5 | 0.1 | 2.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1326 | Standing | Sitting | 134.6 | 142.2 | 7.6 | 0.1 | 4.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1327 | Standing | Sitting | 134.9 | 143.0 | 7.2 | 0.1 | 21.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1328 | Standing | Sitting | 135.9 | 143.4 | 7.4 | 0.2 | 7.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1329 | Standing | Sitting | 136.2 | 143.2 | 7.4 | 0.1 | 2.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1330 | Standing | Sitting | 134.5 | 142.2 | 7.4 | 0.1 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1331 | Standing | Sitting | 135.1 | 142.6 | 7.5 | 0.4 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1332 | Standing | Sitting | 134.9 | 142.1 | 7.5 | 0.0 | 2.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1333 | Standing | Sitting | 134.9 | 142.1 | 7.8 | 0.1 | 14.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1334 | Standing | Sitting | 138.8 | 145.5 | 7.5 | 0.2 | 12.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1335 | Standing | Sitting | 135.3 | 142.5 | 7.8 | 0.4 | 17.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1336 | Standing | Sitting | 136.2 | 144.1 | 7.5 | 0.2 | 17.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1337 | Standing | Sitting | 131.8 | 140.9 | 7.6 | 0.4 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1338 | Standing | Sitting | 133.1 | 141.8 | 7.5 | 0.2 | 1.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1339 | Standing | Sitting | 135.3 | 144.3 | 7.4 | 0.2 | 8.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1340 | Standing | Sitting | 134.6 | 143.1 | 7.2 | 0.1 | 9.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1341 | Standing | Sitting | 133.5 | 142.6 | 7.3 | 0.1 | 3.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1342 | Standing | Sitting | 136.0 | 143.1 | 7.7 | 0.2 | 24.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1343 | Standing | Sitting | 130.5 | 139.9 | 7.5 | 0.8 | 9.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1344 | Standing | Sitting | 133.2 | 142.0 | 7.5 | 0.4 | 4.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1345 | Standing | Sitting | 138.8 | 145.7 | 7.6 | 0.5 | 7.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1346 | Standing | Sitting | 135.8 | 144.3 | 7.7 | 0.2 | 5.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1347 | Standing | Sitting | 132.8 | 141.4 | 7.5 | 0.1 | 9.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1348 | Standing | Sitting | 132.2 | 140.9 | 7.6 | 0.1 | 5.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1349 | Standing | Sitting | 133.2 | 142.0 | 7.5 | 0.1 | 6.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1350 | Standing | Sitting | 133.5 | 142.8 | 7.5 | 0.3 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1351 | Standing | Sitting | 131.6 | 140.8 | 7.7 | 0.1 | 11.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1352 | Standing | Sitting | 132.7 | 141.6 | 7.5 | 0.1 | 13.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1353 | Standing | Sitting | 130.9 | 140.8 | 7.7 | 0.1 | 9.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1354 | Standing | Sitting | 132.4 | 141.2 | 7.7 | 0.1 | 0.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1355 | Standing | Sitting | 132.9 | 141.1 | 7.9 | 0.2 | 15.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1356 | Standing | Sitting | 132.4 | 140.8 | 7.7 | 0.1 | 12.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1357 | Standing | Sitting | 135.4 | 142.5 | 7.9 | 0.3 | 12.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1358 | Standing | Sitting | 135.5 | 143.1 | 8.0 | 0.1 | 2.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1359 | Standing | Sitting | 135.5 | 143.1 | 8.1 | 0.2 | 8.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1360 | Standing | Sitting | 132.1 | 140.0 | 7.8 | 0.6 | 20.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1361 | Standing | Sitting | 129.9 | 138.7 | 7.6 | 0.2 | 12.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1362 | Standing | Sitting | 131.0 | 139.2 | 8.0 | 0.3 | 26.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1363 | Standing | Sitting | 131.2 | 139.8 | 7.9 | 0.3 | 5.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1364 | Standing | Sitting | 128.7 | 136.9 | 7.7 | 0.2 | 12.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1365 | Standing | Sitting | 129.2 | 138.0 | 8.1 | 0.4 | 22.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1366 | Standing | Sitting | 130.7 | 139.0 | 7.9 | 0.4 | 13.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1367 | Standing | Sitting | 125.7 | 134.8 | 7.9 | 0.2 | 1.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1368 | Standing | Sitting | 126.1 | 134.9 | 8.1 | 0.1 | 10.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1369 | Standing | Sitting | 130.7 | 138.6 | 8.1 | 0.1 | 0.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1370 | Standing | Sitting | 133.0 | 140.3 | 8.0 | 0.0 | 4.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1371 | Standing | Sitting | 134.0 | 142.5 | 7.9 | 0.3 | 4.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1372 | Standing | Sitting | 137.7 | 144.8 | 7.4 | 0.4 | 33.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1373 | Standing | Sitting | 135.6 | 143.9 | 7.5 | 0.1 | 5.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1374 | Standing | Sitting | 136.6 | 144.8 | 7.7 | 0.3 | 13.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1375 | Standing | Sitting | 134.9 | 142.7 | 7.2 | 0.4 | 32.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1376 | Standing | Sitting | 138.3 | 145.2 | 7.4 | 0.1 | 13.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1377 | Standing | Sitting | 136.3 | 143.7 | 7.4 | 0.4 | 0.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1378 | Standing | Sitting | 135.1 | 143.4 | 7.5 | 0.1 | 6.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1379 | Standing | Sitting | 134.0 | 141.5 | 7.2 | 0.2 | 18.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1380 | Standing | Sitting | 134.5 | 142.0 | 7.4 | 0.3 | 13.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1381 | Standing | Sitting | 133.8 | 141.1 | 7.2 | 0.1 | 11.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1382 | Standing | Sitting | 134.8 | 142.4 | 7.3 | 0.3 | 3.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1383 | Standing | Sitting | 132.4 | 140.0 | 7.0 | 0.1 | 16.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1384 | Standing | Sitting | 134.4 | 141.9 | 7.1 | 0.3 | 6.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1385 | Standing | Sitting | 133.5 | 141.1 | 7.0 | 0.3 | 7.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1386 | Standing | Sitting | 134.0 | 141.7 | 6.9 | 0.2 | 3.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1387 | Standing | Sitting | 134.6 | 142.3 | 7.0 | 0.3 | 6.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1388 | Standing | Sitting | 136.5 | 142.9 | 6.7 | 0.2 | 17.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1389 | Standing | Sitting | 136.3 | 142.8 | 6.9 | 0.2 | 6.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1390 | Standing | Sitting | 137.5 | 143.7 | 6.9 | 0.1 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1391 | Standing | Sitting | 129.9 | 137.1 | 6.7 | 0.7 | 6.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1392 | Standing | Sitting | 132.8 | 138.5 | 6.6 | 0.3 | 11.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1393 | Standing | Sitting | 134.7 | 141.7 | 6.4 | 0.4 | 10.4 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1394 | Standing | Sitting | 136.3 | 142.1 | 6.5 | 0.3 | 5.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1395 | Standing | Sitting | 135.4 | 141.6 | 6.5 | 0.1 | 1.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1396 | Standing | Sitting | 135.8 | 140.2 | 6.6 | 0.3 | 7.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1397 | Standing | Sitting | 135.3 | 139.9 | 6.1 | 0.5 | 33.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1398 | Standing | Sitting | 135.5 | 140.3 | 6.5 | 0.3 | 23.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1399 | Standing | Sitting | 133.9 | 139.9 | 6.3 | 0.3 | 7.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1400 | Standing | Sitting | 138.2 | 142.1 | 6.4 | 0.3 | 5.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1401 | Standing | Sitting | 135.7 | 139.7 | 6.6 | 0.5 | 9.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1402 | Standing | Sitting | 138.2 | 141.1 | 6.5 | 0.1 | 7.3 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1403 | Standing | Sitting | 138.4 | 142.4 | 6.2 | 0.3 | 13.5 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1404 | Standing | Sitting | 138.8 | 142.6 | 5.8 | 0.3 | 28.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1405 | Standing | Sitting | 139.9 | 143.0 | 5.9 | 0.1 | 5.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1406 | Standing | Sitting | 140.7 | 144.1 | 5.8 | 0.1 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1407 | Standing | Sitting | 140.2 | 144.3 | 5.7 | 0.1 | 6.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1408 | Standing | Sitting | 137.5 | 141.5 | 5.4 | 0.1 | 21.6 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1409 | Standing | Sitting | 139.1 | 143.0 | 5.4 | 0.3 | 1.9 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1410 | Standing | Sitting | 140.5 | 144.4 | 5.2 | 0.3 | 10.7 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1411 | Standing | Sitting | 141.4 | 145.7 | 5.3 | 0.5 | 4.1 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1412 | Standing | Sitting | 140.7 | 144.7 | 5.1 | 0.1 | 11.3 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1413 | Standing | Sitting | 137.6 | 141.6 | 5.4 | 0.3 | 19.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1414 | Standing | Sitting | 133.8 | 138.8 | 5.0 | 0.4 | 27.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1415 | Standing | Sitting | 135.2 | 140.6 | 5.0 | 0.4 | 0.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1416 | Standing | Sitting | 137.7 | 142.9 | 4.9 | 0.3 | 1.2 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1417 | Standing | Sitting | 140.2 | 144.6 | 4.9 | 0.1 | 2.8 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1418 | Standing | Sitting | 140.8 | 144.7 | 4.3 | 0.1 | 33.0 | 0.4 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1419 | Standing | Sitting | 137.6 | 142.4 | 4.4 | 0.3 | 5.1 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1420 | Standing | Sitting | 133.1 | 140.1 | 4.4 | 0.3 | 3.3 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1421 | Standing | Sitting | 134.5 | 140.4 | 4.5 | 0.3 | 5.9 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1422 | Standing | Sitting | 135.1 | 140.9 | 4.9 | 0.4 | 23.4 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1423 | Standing | Sitting | 130.6 | 137.3 | 4.0 | 0.7 | 49.7 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1424 | Standing | Sitting | 139.1 | 143.0 | 4.5 | 0.2 | 26.4 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1425 | Standing | Sitting | 137.6 | 141.6 | 4.7 | 0.3 | 15.0 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1426 | Standing | Sitting | 132.9 | 138.8 | 4.4 | 0.6 | 18.3 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1427 | Standing | Sitting | 138.3 | 142.4 | 3.8 | 0.1 | 39.0 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1428 | Standing | Sitting | 137.0 | 141.6 | 3.1 | 0.3 | 43.2 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1429 | Standing | Sitting | 137.2 | 141.7 | 2.6 | 0.2 | 24.9 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1430 | Standing | Sitting | 138.0 | 142.2 | 2.0 | 0.6 | 40.2 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1431 | Standing | Sitting | 142.5 | 146.5 | 2.2 | 1.2 | 15.0 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1432 | Standing | Sitting | 140.6 | 143.1 | 1.9 | 0.1 | 22.0 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 1433 | Standing | Sitting | 145.8 | 146.7 | 2.1 | 0.7 | 17.6 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1434 | Standing | Sitting | 144.0 | 145.8 | 1.7 | 0.6 | 23.7 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 1435 | Standing | Sitting | 145.1 | 147.1 | 2.0 | 0.3 | 15.4 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 1436 | Standing | Sitting | 143.1 | 147.0 | 1.1 | 0.5 | 54.3 | 0.3 | 0.7 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 1739 | Lying | Standing | 173.9 | 178.2 | 3.3 | 1.5 | 72.7 | 0.8 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1740 | Lying | Standing | 169.3 | 178.6 | 4.0 | 0.3 | 41.9 | 0.7 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1741 | Lying | Standing | 161.2 | 175.4 | 4.6 | 0.8 | 33.9 | 0.7 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1742 | Lying | Standing | 151.7 | 172.7 | 4.8 | 1.1 | 9.4 | 0.7 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1743 | Lying | Standing | 154.3 | 172.6 | 5.5 | 0.3 | 45.6 | 0.7 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1744 | Lying | Standing | 155.4 | 171.4 | 5.9 | 0.4 | 24.6 | 0.7 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1745 | Lying | Standing | 149.8 | 168.2 | 5.7 | 0.2 | 14.6 | 0.6 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1746 | Lying | Standing | 148.1 | 164.8 | 5.7 | 0.7 | 1.6 | 0.6 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1747 | Lying | Standing | 149.0 | 163.4 | 5.7 | 1.1 | 0.8 | 0.6 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1748 | Lying | Standing | 155.1 | 163.5 | 5.5 | 0.5 | 14.7 | 0.6 | 0.9 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1749 | Lying | Standing | 158.1 | 161.7 | 5.3 | 1.1 | 10.7 | 0.6 | 0.9 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1750 | Lying | Standing | 160.6 | 161.2 | 5.0 | 0.3 | 15.6 | 0.6 | 0.9 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1751 | Lying | Standing | 163.9 | 164.8 | 6.2 | 2.3 | 73.0 | 0.6 | 0.9 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1752 | Lying | Standing | 171.0 | 165.0 | 7.1 | 1.9 | 51.7 | 0.6 | 0.9 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1753 | Lying | Standing | 169.0 | 167.5 | 7.8 | 1.4 | 41.4 | 0.7 | 0.9 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1754 | Lying | Standing | nan | 165.4 | 7.6 | 1.4 | 12.9 | 0.8 | 0.9 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1755 | Lying | Standing | nan | 167.4 | 8.3 | 1.6 | 43.8 | 0.8 | 0.9 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1756 | Lying | Standing | nan | 169.1 | 9.5 | 1.3 | 68.9 | 0.8 | 0.9 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1757 | Lying | Standing | nan | 168.7 | 9.1 | 0.7 | 18.3 | 0.8 | 0.9 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 1758 | Lying | Standing | nan | 171.8 | 10.8 | 0.8 | 100.9 | 0.8 | 0.9 | 0.2 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 1759 | Lying | Standing | nan | 171.7 | 11.5 | 1.3 | 42.9 | 0.7 | 0.9 | 0.2 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 1760 | Lying | Standing | nan | 169.9 | 12.7 | 0.9 | 67.0 | 0.7 | 0.9 | 0.2 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 1761 | Lying | Standing | nan | 167.5 | 14.3 | 0.6 | 97.8 | 0.8 | 0.9 | 0.2 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 1762 | Lying | Standing | nan | nan | 15.5 | 2.7 | 72.8 | 0.6 | 0.9 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 1763 | Lying | Standing | nan | nan | 17.8 | 0.3 | 139.5 | 0.6 | 0.9 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 1764 | Lying | Standing | nan | nan | 18.8 | 2.3 | 56.9 | 0.6 | 0.9 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 1765 | Lying | Standing | nan | nan | 21.5 | 0.6 | 162.7 | 0.5 | 0.9 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 1766 | Lying | Standing | nan | nan | 21.7 | 2.6 | 13.0 | 0.6 | 0.9 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1767 | Lying | Standing | nan | nan | 23.6 | 0.8 | 111.3 | 0.5 | 0.9 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1768 | Lying | Standing | nan | nan | 25.9 | 0.9 | 139.3 | 0.5 | 0.9 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1769 | Lying | Standing | nan | nan | 26.9 | 2.4 | 57.6 | 0.5 | 0.9 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1770 | Lying | Standing | nan | nan | 27.7 | 1.8 | 51.9 | 0.5 | 0.9 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1771 | Lying | Standing | nan | nan | 29.0 | 1.2 | 74.4 | 0.5 | 0.9 | 0.0 | T | F | Standing|Standing|Standing|Standing|Standing |
| 1772 | Lying | Standing | nan | nan | 30.3 | 1.5 | 80.9 | 0.5 | 0.9 | 0.0 | T | F | Standing|Standing|Standing|Standing|Sitting |
| 1773 | Lying | Standing | nan | nan | 32.6 | 1.0 | 137.7 | 0.5 | 0.9 | 0.0 | T | F | Standing|Standing|Standing|Sitting|Sitting |
| 1774 | Lying | Standing | nan | nan | 34.6 | 1.1 | 117.6 | 0.4 | 0.9 | 0.0 | T | F | Standing|Standing|Sitting|Sitting|Sitting |
| 1775 | Lying | Standing | nan | nan | 38.8 | 1.5 | 253.3 | 0.4 | 0.9 | 0.0 | T | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 2398 | Standing | Sitting | 130.7 | 163.9 | 7.5 | 0.5 | 1.3 | 0.6 | 0.9 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2399 | Standing | Sitting | 134.1 | 164.9 | 6.8 | 0.8 | 40.7 | 0.6 | 0.9 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2400 | Standing | Sitting | 144.7 | 165.2 | 6.7 | 0.8 | 6.8 | 0.6 | 0.9 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 2401 | Standing | Sitting | 145.2 | 166.0 | 6.2 | 0.7 | 29.1 | 0.6 | 0.9 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 2402 | Standing | Sitting | 148.7 | 166.5 | 5.7 | 0.4 | 31.5 | 0.6 | 0.9 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 2403 | Standing | Sitting | 150.3 | 167.2 | 5.3 | 0.3 | 25.8 | 0.6 | 0.9 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 2904 | Standing | Sitting | 79.0 | 99.2 | 13.0 | 2.6 | 0.6 | 0.5 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2905 | Standing | Sitting | 96.8 | 93.6 | 13.7 | 0.6 | 39.9 | 0.5 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2906 | Standing | Sitting | 85.4 | 77.8 | 14.0 | 1.6 | 20.9 | 0.5 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2907 | Standing | Sitting | 76.4 | 76.4 | 14.4 | 0.1 | 19.8 | 0.5 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2908 | Standing | Sitting | 77.6 | 72.9 | 14.2 | 2.1 | 8.5 | 0.5 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2909 | Standing | Sitting | 54.0 | 58.0 | 13.7 | 2.0 | 33.4 | 0.4 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2910 | Standing | Sitting | 56.9 | 58.8 | 13.2 | 2.0 | 27.9 | 0.4 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2911 | Standing | Sitting | 50.7 | 51.0 | 13.9 | 1.2 | 42.3 | 0.4 | 1.0 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2912 | Standing | Sitting | 47.4 | 48.6 | 13.4 | 2.0 | 32.5 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2913 | Standing | Sitting | 45.6 | 47.7 | 13.1 | 1.8 | 14.5 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2914 | Standing | Sitting | 45.7 | 50.3 | 12.5 | 1.1 | 35.1 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2915 | Standing | Sitting | 46.5 | 50.1 | 12.5 | 0.8 | 4.2 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2916 | Standing | Sitting | 48.6 | 54.8 | 11.7 | 1.6 | 47.9 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2917 | Standing | Sitting | 44.3 | 54.8 | 11.3 | 1.5 | 22.1 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2918 | Standing | Sitting | 47.6 | 53.6 | 10.0 | 1.3 | 77.1 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2919 | Standing | Sitting | 38.6 | 50.8 | 9.4 | 1.0 | 35.8 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2920 | Standing | Sitting | 39.0 | 47.1 | 9.6 | 1.8 | 10.0 | 0.4 | 1.0 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2921 | Standing | Sitting | 43.1 | 47.9 | 8.3 | 4.5 | 77.0 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2922 | Standing | Sitting | 47.9 | 53.7 | 7.7 | 0.6 | 36.0 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2923 | Standing | Sitting | nan | 56.6 | 7.3 | 0.5 | 24.6 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2924 | Standing | Sitting | 51.2 | 55.0 | 6.9 | 0.7 | 25.0 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2925 | Standing | Sitting | nan | 53.3 | 6.0 | 2.1 | 49.8 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2926 | Standing | Sitting | nan | 52.7 | 5.1 | 0.5 | 58.5 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2927 | Standing | Sitting | 37.4 | 48.2 | 5.1 | 1.4 | 2.5 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2928 | Standing | Sitting | nan | 73.9 | 4.2 | 1.2 | 54.5 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2929 | Standing | Sitting | nan | 76.5 | 4.4 | 0.3 | 9.8 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2930 | Standing | Sitting | nan | 56.8 | 3.6 | 1.1 | 46.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2931 | Standing | Sitting | nan | 67.8 | 3.4 | 0.5 | 14.3 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2932 | Standing | Sitting | nan | 60.9 | 2.6 | 0.7 | 43.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2933 | Standing | Sitting | nan | 50.9 | 2.0 | 0.2 | 38.6 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2934 | Standing | Sitting | nan | 52.5 | 1.8 | 1.1 | 10.8 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2935 | Standing | Sitting | nan | 51.7 | 2.2 | 0.8 | 19.9 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2936 | Standing | Sitting | nan | 58.8 | 1.5 | 1.1 | 38.3 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2937 | Standing | Sitting | nan | 56.9 | 1.5 | 1.1 | 0.8 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2938 | Standing | Sitting | nan | 45.0 | 0.7 | 3.3 | 49.5 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2939 | Standing | Sitting | nan | 52.1 | 0.2 | 1.7 | 28.6 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2940 | Standing | Sitting | nan | 42.0 | 0.1 | 3.6 | 7.8 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2941 | Standing | Sitting | 39.0 | 44.1 | 0.4 | 0.7 | 16.2 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2942 | Standing | Sitting | 29.4 | 37.1 | 1.0 | 2.1 | 39.4 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2943 | Standing | Sitting | 41.1 | 44.1 | 0.6 | 1.2 | 24.8 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2944 | Standing | Sitting | 27.2 | 34.7 | 1.3 | 0.9 | 44.0 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2945 | Standing | Sitting | nan | 43.4 | 2.2 | 1.3 | 53.6 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2946 | Standing | Sitting | nan | 96.0 | 2.1 | 2.1 | 10.7 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2947 | Standing | Sitting | 39.9 | 48.3 | 1.7 | 1.0 | 22.0 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2948 | Standing | Sitting | 53.9 | 56.5 | 1.6 | 0.3 | 8.3 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2949 | Standing | Sitting | 66.5 | 75.8 | 0.9 | 4.4 | 36.7 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2950 | Standing | Sitting | nan | 94.0 | 0.9 | 0.7 | 3.6 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2951 | Standing | Sitting | 75.5 | 81.6 | 2.5 | 1.0 | 94.3 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2952 | Standing | Sitting | 79.1 | 78.5 | 1.1 | 1.7 | 83.6 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2953 | Standing | Sitting | nan | 128.9 | 0.2 | 0.3 | 50.3 | 0.6 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2954 | Standing | Sitting | nan | 87.6 | 2.4 | 2.5 | 133.2 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2955 | Standing | Sitting | nan | nan | 2.4 | 1.2 | 1.4 | 0.6 | 1.0 | 0.0 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 2956 | Standing | Sitting | nan | nan | 2.2 | 1.1 | 10.2 | 0.6 | 1.0 | 0.0 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 2957 | Standing | Sitting | nan | nan | 3.3 | 0.1 | 65.1 | 0.6 | 1.0 | 0.0 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 2958 | Standing | Sitting | nan | 139.8 | 2.9 | 1.5 | 28.2 | 0.6 | 1.0 | 0.0 | F | F | Sitting|Standing|Standing|Standing|Sitting |
| 2959 | Standing | Sitting | nan | 128.4 | 3.3 | 0.9 | 25.9 | 0.6 | 1.0 | 0.0 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 2960 | Standing | Sitting | nan | nan | 3.6 | 1.2 | 21.0 | 0.6 | 1.0 | 0.0 | T | F | Standing|Standing|Sitting|Sitting|Standing |
| 2961 | Standing | Sitting | nan | 93.2 | 5.7 | 3.8 | 126.2 | 0.5 | 1.0 | -0.0 | F | F | Standing|Sitting|Sitting|Standing|Sitting |
| 2962 | Standing | Sitting | nan | 121.5 | 3.9 | 1.7 | 110.9 | 0.6 | 1.0 | 0.0 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 2963 | Standing | Sitting | nan | nan | 5.3 | 1.2 | 81.3 | 0.7 | 1.0 | -0.0 | T | F | Sitting|Standing|Sitting|Sitting|Standing |
| 2964 | Standing | Sitting | nan | 87.4 | 3.3 | 1.3 | 119.9 | 0.5 | 1.0 | 0.0 | F | F | Standing|Sitting|Sitting|Standing|Sitting |
| 2965 | Standing | Sitting | nan | 65.2 | 3.5 | 2.6 | 11.6 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 2966 | Standing | Sitting | nan | 63.7 | 4.1 | 0.7 | 36.3 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 2967 | Standing | Sitting | nan | 53.4 | 4.8 | 1.7 | 43.0 | 0.4 | 1.0 | 0.0 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 2968 | Standing | Sitting | nan | 57.1 | 5.4 | 1.6 | 39.4 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2969 | Standing | Sitting | nan | 63.2 | 3.8 | 0.9 | 99.3 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2970 | Standing | Sitting | nan | 67.6 | 6.5 | 1.3 | 162.9 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2971 | Standing | Sitting | nan | 64.1 | 5.6 | 0.3 | 50.6 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2972 | Standing | Sitting | nan | 64.8 | 4.8 | 1.2 | 52.7 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2973 | Standing | Sitting | nan | 67.1 | 5.8 | 3.7 | 64.3 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2974 | Standing | Sitting | nan | 57.7 | 6.5 | 3.4 | 37.6 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2975 | Standing | Sitting | nan | 59.4 | 7.4 | 0.8 | 56.5 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2976 | Standing | Sitting | nan | 64.5 | 5.8 | 1.0 | 94.1 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2977 | Standing | Sitting | nan | 57.6 | 6.6 | 3.3 | 45.3 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2978 | Standing | Sitting | nan | 79.4 | 6.1 | 1.1 | 32.3 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2979 | Standing | Sitting | nan | 91.7 | 4.8 | 2.5 | 76.9 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2980 | Standing | Sitting | nan | 79.8 | 6.3 | 2.7 | 89.5 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2981 | Standing | Sitting | nan | 91.9 | 5.2 | 0.5 | 64.4 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2982 | Standing | Sitting | nan | 96.6 | 5.0 | 0.9 | 8.7 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 2983 | Standing | Sitting | nan | nan | 5.4 | 1.5 | 18.9 | 0.7 | 1.0 | -0.0 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 2984 | Standing | Sitting | nan | nan | 3.6 | 3.7 | 107.7 | 0.7 | 1.0 | 0.0 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 2985 | Standing | Sitting | nan | nan | 4.3 | 0.4 | 44.1 | 0.7 | 1.0 | 0.0 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 2986 | Standing | Sitting | nan | 134.4 | 5.1 | 1.8 | 49.9 | 0.7 | 1.0 | -0.0 | F | F | Sitting|Standing|Standing|Standing|Sitting |
| 2987 | Standing | Sitting | nan | 117.5 | 3.1 | 3.1 | 123.6 | 0.6 | 1.0 | 0.0 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 2988 | Standing | Sitting | nan | 109.6 | 3.8 | 1.4 | 45.7 | 0.6 | 1.0 | 0.0 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 2989 | Standing | Sitting | nan | nan | 4.0 | 0.3 | 8.9 | 0.7 | 1.0 | 0.0 | T | F | Standing|Sitting|Sitting|Sitting|Standing |
| 2990 | Standing | Sitting | nan | nan | 3.2 | 0.4 | 43.9 | 0.7 | 1.0 | 0.0 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 2991 | Standing | Sitting | nan | nan | 4.5 | 3.1 | 77.1 | 0.7 | 1.0 | -0.0 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 2992 | Standing | Sitting | nan | nan | 4.6 | 0.5 | 1.7 | 0.7 | 1.0 | -0.0 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 3025 | Standing | Sitting | nan | 103.6 | 4.4 | 0.3 | 6.6 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3026 | Standing | Sitting | nan | 102.0 | 4.6 | 0.3 | 11.4 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3027 | Standing | Sitting | nan | nan | 4.1 | 0.3 | 30.3 | 0.7 | 1.0 | -0.0 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 3028 | Standing | Sitting | nan | 93.9 | 4.4 | 0.7 | 19.9 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 3029 | Standing | Sitting | nan | 91.6 | 4.5 | 0.2 | 3.1 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 3030 | Standing | Sitting | nan | 89.1 | 4.4 | 0.3 | 6.4 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 3031 | Standing | Sitting | nan | 105.8 | 4.4 | 2.3 | 2.2 | 0.5 | 1.0 | 0.0 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 3032 | Standing | Sitting | nan | 84.7 | 4.0 | 1.1 | 23.9 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3033 | Standing | Sitting | nan | 93.5 | 2.4 | 1.9 | 94.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3034 | Standing | Sitting | nan | 105.5 | 4.7 | 4.5 | 136.0 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3035 | Standing | Sitting | nan | 101.8 | 4.6 | 0.4 | 4.1 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3036 | Standing | Sitting | nan | 93.7 | 4.8 | 0.2 | 12.6 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3037 | Standing | Sitting | nan | 100.6 | 4.5 | 2.2 | 19.9 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3038 | Standing | Sitting | nan | 111.6 | 4.2 | 0.3 | 21.5 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3039 | Standing | Sitting | nan | 102.3 | 3.9 | 0.6 | 13.4 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3040 | Standing | Sitting | nan | 105.6 | 4.5 | 0.8 | 33.9 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3041 | Standing | Sitting | nan | 101.5 | 3.4 | 1.7 | 63.0 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3042 | Standing | Sitting | nan | 78.9 | 4.0 | 4.0 | 34.4 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3043 | Standing | Sitting | nan | 75.7 | 3.8 | 0.4 | 11.4 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3044 | Standing | Sitting | nan | 74.6 | 4.0 | 0.9 | 11.1 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3045 | Standing | Sitting | nan | 70.6 | 4.0 | 0.5 | 1.4 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3046 | Standing | Sitting | nan | 85.9 | 3.8 | 2.4 | 13.3 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3047 | Standing | Sitting | nan | 70.2 | 4.2 | 2.0 | 22.8 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3048 | Standing | Sitting | nan | 84.0 | 4.5 | 1.8 | 18.3 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3049 | Standing | Sitting | nan | 81.3 | 3.8 | 1.5 | 38.9 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3050 | Standing | Sitting | nan | 79.4 | 3.7 | 2.0 | 6.0 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3051 | Standing | Sitting | nan | 100.5 | 3.4 | 0.3 | 15.6 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3052 | Standing | Sitting | nan | 102.8 | 3.1 | 0.2 | 19.7 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3053 | Standing | Sitting | nan | 91.7 | 3.2 | 0.1 | 4.3 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3054 | Standing | Sitting | nan | 85.1 | 3.7 | 0.4 | 32.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3055 | Standing | Sitting | nan | 100.8 | 3.1 | 0.4 | 39.9 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3056 | Standing | Sitting | nan | 94.4 | 3.0 | 0.1 | 3.0 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3057 | Standing | Sitting | nan | 101.1 | 2.8 | 0.6 | 12.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3058 | Standing | Sitting | nan | 79.4 | 3.3 | 0.3 | 28.9 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3059 | Standing | Sitting | nan | 104.5 | 3.2 | 0.8 | 6.2 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3060 | Standing | Sitting | nan | 106.7 | 2.8 | 0.8 | 23.0 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3061 | Standing | Sitting | nan | 99.2 | 2.8 | 0.6 | 2.8 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3062 | Standing | Sitting | nan | 110.9 | 2.8 | 0.0 | 0.3 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3063 | Standing | Sitting | nan | 75.9 | 2.8 | 0.7 | 0.5 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3064 | Standing | Sitting | nan | 96.4 | 2.9 | 0.9 | 2.7 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3065 | Standing | Sitting | nan | 88.1 | 2.5 | 0.1 | 20.5 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3066 | Standing | Sitting | nan | 90.7 | 2.5 | 0.2 | 0.5 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3067 | Standing | Sitting | nan | 84.3 | 3.4 | 1.5 | 51.6 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3068 | Standing | Sitting | nan | 81.9 | 3.4 | 0.4 | 1.8 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3069 | Standing | Sitting | nan | 79.0 | 3.3 | 1.8 | 6.9 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3070 | Standing | Sitting | nan | 74.9 | 2.4 | 0.5 | 56.3 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3071 | Standing | Sitting | nan | 92.4 | 4.2 | 3.0 | 106.2 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3072 | Standing | Sitting | nan | 100.3 | 3.7 | 1.5 | 26.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3073 | Standing | Sitting | nan | 88.5 | 3.8 | 0.4 | 7.7 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3074 | Standing | Sitting | nan | 95.7 | 4.6 | 1.2 | 43.6 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3075 | Standing | Sitting | nan | 91.6 | 4.3 | 1.7 | 17.8 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3076 | Standing | Sitting | nan | 97.4 | 4.5 | 0.3 | 11.4 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3077 | Standing | Sitting | nan | 96.8 | 4.0 | 0.6 | 31.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3078 | Standing | Sitting | nan | 89.1 | 3.8 | 0.5 | 10.4 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3079 | Standing | Sitting | nan | 95.6 | 3.5 | 0.2 | 16.7 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3080 | Standing | Sitting | nan | 75.0 | 4.6 | 2.1 | 68.6 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3081 | Standing | Sitting | nan | 97.6 | 3.3 | 2.3 | 80.4 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3082 | Standing | Sitting | nan | 75.3 | 3.0 | 0.2 | 18.5 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3083 | Standing | Sitting | nan | 84.4 | 2.7 | 0.3 | 14.8 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3084 | Standing | Sitting | nan | 73.9 | 2.6 | 0.8 | 6.3 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3085 | Standing | Sitting | nan | 70.5 | 2.8 | 1.1 | 10.7 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3086 | Standing | Sitting | nan | 90.5 | 2.5 | 0.7 | 17.8 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3087 | Standing | Sitting | nan | 84.4 | 2.8 | 0.5 | 14.9 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3088 | Standing | Sitting | nan | 78.0 | 2.6 | 0.2 | 10.1 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3089 | Standing | Sitting | nan | 66.8 | 3.5 | 2.4 | 55.6 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3090 | Standing | Sitting | nan | 71.7 | 3.5 | 0.2 | 4.5 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3091 | Standing | Sitting | nan | 65.3 | 3.6 | 0.2 | 11.6 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3092 | Standing | Sitting | nan | 62.8 | 3.2 | 2.2 | 29.3 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3093 | Standing | Sitting | nan | 70.3 | 3.0 | 0.4 | 10.4 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3094 | Standing | Sitting | nan | 76.8 | 3.0 | 0.4 | 2.2 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3095 | Standing | Sitting | nan | 59.8 | 3.4 | 0.6 | 20.0 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3096 | Standing | Sitting | nan | 72.5 | 3.8 | 0.7 | 28.9 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3097 | Standing | Sitting | nan | 70.5 | 4.5 | 0.9 | 38.8 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3098 | Standing | Sitting | nan | 71.6 | 4.1 | 0.3 | 22.4 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3099 | Standing | Sitting | nan | 68.7 | 4.6 | 1.7 | 27.8 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3100 | Standing | Sitting | nan | 74.9 | 4.0 | 1.2 | 33.9 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3101 | Standing | Sitting | nan | 71.7 | 4.5 | 2.3 | 29.8 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3102 | Standing | Sitting | nan | 86.9 | 4.9 | 0.5 | 23.1 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3103 | Standing | Sitting | nan | 97.9 | 3.3 | 3.5 | 93.3 | 0.5 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3104 | Standing | Sitting | nan | 87.2 | 5.0 | 2.7 | 97.2 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3105 | Standing | Sitting | nan | 67.8 | 3.5 | 0.2 | 89.2 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3106 | Standing | Sitting | nan | 57.1 | 4.2 | 0.6 | 43.9 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3107 | Standing | Sitting | nan | 65.0 | 4.0 | 0.1 | 12.7 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3108 | Standing | Sitting | nan | 52.4 | 4.0 | 0.6 | 1.4 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3109 | Standing | Sitting | nan | 55.3 | 2.5 | 2.8 | 90.2 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3110 | Standing | Sitting | nan | 55.6 | 2.2 | 1.0 | 15.5 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3111 | Standing | Sitting | 46.1 | 60.6 | 1.7 | 0.8 | 32.3 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3112 | Standing | Sitting | 40.5 | 56.9 | 1.2 | 2.0 | 28.9 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3113 | Standing | Sitting | 40.4 | 56.3 | 1.8 | 0.9 | 33.7 | 0.4 | 1.0 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3114 | Standing | Sitting | nan | 58.9 | 1.1 | 0.9 | 42.8 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3115 | Standing | Sitting | nan | 53.8 | 1.0 | 2.4 | 7.2 | 0.4 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3116 | Standing | Sitting | nan | 60.5 | 1.0 | 2.2 | 1.8 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3117 | Standing | Sitting | nan | 57.0 | 0.1 | 4.5 | 52.9 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 3118 | Standing | Sitting | nan | 64.9 | 0.4 | 0.2 | 20.7 | 0.5 | 1.0 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Normal_Fall_1 (**posture<90%**)

**Posture accuracy:** 83.3%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 75.4%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 29 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 8 | 3 | 46 | 4 |

**Fall detection:** TP (latency 18 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 90 | Lying | Standing | 159.2 | 154.6 | 3.1 | 0.9 | 47.8 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Lying | Standing | 157.0 | 150.9 | 2.2 | 0.8 | 24.6 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Lying | Standing | 158.9 | 150.5 | 2.2 | 0.9 | 0.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Lying | Standing | 151.2 | 144.1 | 1.2 | 1.1 | 30.7 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Lying | Standing | 148.7 | 140.7 | 1.4 | 1.1 | 4.7 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 95 | Lying | Standing | 141.7 | 130.0 | 1.0 | 1.4 | 9.6 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 96 | Lying | Standing | 137.0 | 125.0 | 2.9 | 1.8 | 54.1 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 97 | Lying | Standing | 58.9 | 49.3 | 1.9 | 2.7 | 27.6 | 0.2 | 0.3 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 98 | Lying | Sitting | 39.2 | 29.6 | 3.7 | 2.7 | 52.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Lying | Sitting | 28.1 | 19.5 | 5.9 | 3.5 | 65.6 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Lying | Sitting | 24.9 | 23.1 | 0.9 | 1.8 | 147.5 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 102 | Lying | Unknown | 28.0 | 26.0 | 0.6 | 1.8 | 5.1 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 103 | Lying | Unknown | 32.2 | 29.3 | 1.0 | 2.7 | 12.5 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 104 | Lying | Unknown | 36.6 | 34.1 | 21.3 | 8.7 | 607.7 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Unknown|Sitting|Sitting|Sitting |

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

**Fall detection:** TP (latency 8 frames)

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
| **Standing** | 88 | 13 | 19 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 181 | 0 |

**Fall detection:** TP (latency 81 frames)

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
| 102 | Standing | Lying | 45.6 | 55.9 | 32.6 | 0.5 | 295.3 | 0.2 | 0.7 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Lying |
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

**Fall detection:** TP (latency 114 frames)

**Mismatched frames:**

_None_

---

## Sit_1

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 100.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 59 | 0 | 0 | 0 |
| **Sitting** | 0 | 31 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Sit_2 (**posture<90%**)

**Posture accuracy:** 54.4%

**Per-class accuracy:**

- Standing: 30.5%
- Sitting: 100.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 18 | 16 | 0 | 25 |
| **Sitting** | 0 | 31 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 19 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Sitting|Standing|Standing|Unknown |
| 20 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Standing|Standing|Unknown|Unknown |
| 21 | Standing | Unknown | 160.6 | 168.5 | 9.4 | 0.2 | 19.2 | 0.2 | 0.2 | 0.2 | F | F | Standing|Standing|Unknown|Unknown|Standing |
| 22 | Standing | Unknown | 159.1 | 165.7 | 4.1 | 1.2 | 159.8 | 0.2 | 0.2 | 0.2 | F | F | Standing|Unknown|Unknown|Standing|Standing |
| 23 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Standing|Unknown |
| 24 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Standing|Unknown|Unknown |
| 25 | Standing | Unknown | 169.1 | 172.0 | 6.8 | 0.2 | 26.4 | 0.2 | 0.2 | 0.2 | F | F | Standing|Standing|Unknown|Unknown|Standing |
| 26 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Standing|Unknown |
| 27 | Standing | Unknown | 163.1 | 164.4 | 6.6 | 0.1 | 3.0 | 0.2 | 0.2 | 0.2 | F | F | Unknown|Unknown|Standing|Unknown|Standing |
| 28 | Standing | Unknown | 167.7 | 170.1 | 6.6 | 0.3 | 1.9 | 0.2 | 0.2 | 0.2 | F | F | Unknown|Standing|Unknown|Standing|Standing |
| 29 | Standing | Unknown | 145.0 | 150.0 | 1.2 | 1.7 | 161.3 | 0.2 | 0.2 | 0.2 | F | F | Standing|Unknown|Standing|Standing|Standing |
| 30 | Standing | Unknown | 175.5 | 175.9 | 2.1 | 0.7 | 24.4 | 0.2 | 0.2 | 0.2 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 31 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 32 | Standing | Unknown | 141.9 | 124.7 | 12.9 | 1.3 | 163.5 | 0.2 | 0.2 | 0.2 | F | F | Standing|Standing|Standing|Unknown|Sitting |
| 33 | Standing | Unknown | 167.3 | 160.3 | 1.6 | 2.5 | 340.6 | 0.2 | 0.2 | 0.2 | F | F | Standing|Standing|Unknown|Sitting|Standing |
| 34 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Sitting|Standing|Unknown |
| 35 | Standing | Unknown | 155.4 | 157.1 | 0.8 | 0.1 | 11.9 | 0.2 | 0.2 | 0.2 | F | F | Unknown|Sitting|Standing|Unknown|Standing |
| 36 | Standing | Unknown | 143.9 | 154.7 | 2.1 | 0.3 | 39.0 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Standing|Unknown|Standing|Standing |
| 37 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Standing|Standing|Unknown |
| 38 | Standing | Unknown | 100.1 | 126.2 | 5.2 | 0.3 | 46.9 | 0.2 | 0.2 | 0.2 | F | F | Unknown|Standing|Standing|Unknown|Sitting |
| 39 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Sitting|Unknown |
| 40 | Standing | Unknown | 112.6 | 134.5 | 9.9 | 0.2 | 70.3 | 0.2 | 0.2 | 0.2 | F | F | Standing|Unknown|Sitting|Unknown|Sitting |
| 41 | Standing | Unknown | 87.7 | 115.5 | 11.8 | 1.1 | 58.0 | 0.2 | 0.2 | 0.2 | F | F | Unknown|Sitting|Unknown|Sitting|Sitting |
| 42 | Standing | Unknown | 114.4 | 119.3 | 11.5 | 1.3 | 11.6 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 43 | Standing | Unknown | 122.0 | 124.9 | 13.2 | 1.0 | 51.5 | 0.2 | 0.2 | 0.2 | F | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 44 | Standing | Sitting | 104.3 | 108.1 | 15.6 | 1.0 | 72.0 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 45 | Standing | Sitting | 98.7 | 101.8 | 17.6 | 0.8 | 59.3 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 46 | Standing | Sitting | 98.9 | 120.3 | 17.6 | 0.6 | 2.4 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 47 | Standing | Sitting | 145.5 | 133.7 | 17.3 | 0.2 | 10.6 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 48 | Standing | Sitting | 131.7 | 135.9 | 20.8 | 0.7 | 105.8 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 49 | Standing | Sitting | 122.1 | 136.2 | 21.6 | 0.4 | 24.0 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Standing|Standing|Sitting |
| 50 | Standing | Sitting | 120.5 | 126.8 | 20.9 | 0.6 | 20.1 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Standing|Standing|Sitting|Sitting |
| 51 | Standing | Sitting | 118.3 | 110.2 | 22.3 | 0.7 | 40.4 | 0.2 | 0.2 | 0.2 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 52 | Standing | Sitting | 119.7 | 71.7 | 27.3 | 1.9 | 150.4 | 0.2 | 0.2 | 0.2 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 53 | Standing | Sitting | 73.1 | 82.2 | 22.8 | 1.8 | 135.9 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 54 | Standing | Sitting | 78.6 | 71.2 | 25.4 | 0.7 | 77.9 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 55 | Standing | Sitting | 90.7 | 72.6 | 27.2 | 0.4 | 54.9 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 56 | Standing | Sitting | 106.8 | 76.1 | 29.3 | 0.8 | 64.6 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 57 | Standing | Sitting | 136.6 | 78.8 | 31.7 | 0.6 | 70.7 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 58 | Standing | Sitting | 90.7 | 65.5 | 30.9 | 0.7 | 24.6 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 59 | Standing | Sitting | 115.0 | 74.4 | 32.8 | 0.5 | 56.7 | 0.2 | 0.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Sit_3

**Posture accuracy:** 94.5%

**Per-class accuracy:**

- Standing: nan%
- Sitting: 94.5%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 86 | 5 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 63 | Sitting | Lying | 152.7 | 55.9 | 50.6 | 7.3 | 573.3 | 0.2 | 0.2 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Lying |
| 64 | Sitting | Lying | 27.1 | 84.1 | 13.1 | 11.1 | 720.0 | 0.2 | 0.2 | 0.1 | F | F | Sitting|Sitting|Sitting|Lying|Sitting |
| 65 | Sitting | Lying | 33.1 | 85.0 | 12.3 | 0.4 | 23.6 | 0.2 | 0.2 | 0.1 | F | F | Sitting|Sitting|Lying|Sitting|Sitting |
| 66 | Sitting | Lying | 22.2 | 85.4 | 9.3 | 1.4 | 89.4 | 0.2 | 0.2 | 0.1 | F | F | Sitting|Lying|Sitting|Sitting|Sitting |
| 67 | Sitting | Lying | 27.6 | 99.2 | 1.9 | 1.8 | 222.8 | 0.2 | 0.2 | 0.1 | F | F | Lying|Sitting|Sitting|Sitting|Sitting |

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

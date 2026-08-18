# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| Bend_pickup_lowLight | 100.0% | - |  |
| Bend_pickup_normalLight_back | 100.0% | - |  |
| Bend_pickup_normalLight | 100.0% | FP frames [59, 60, 63] | **false positive** |
| Bend_pickup_normalLight_leftRight | 92.0% | - |  |
| Bend_pickup_squat_lowLight | 100.0% | - |  |
| Bend_pickup_squat_normalLight | 100.0% | - |  |
| Kneeling | 98.2% | - |  |
| LyingdownSlowly | 100.0% | TP (latency 95 frames) |  |
| Moving_in_out_frame | 44.9% | - | **posture<90%** |
| Moving_in_out_frame_withFall | 49.7% | FN | **posture<90%, false negative** |
| Sit_Stand_AnklesInvisible | 41.1% | - | **posture<90%** |
| SitFast_GetupFast | 34.3% | - | **posture<90%** |
| SitFloor_lowKeypoints_crossedLegs | 100.0% | - |  |
| SitFloor_lowKeypoints | 95.1% | - |  |
| Sitting_HalfLandmarks | 86.2% | - | **posture<90%** |
| Sitting_Lying_FewLandmarks_back | 13.7% | FN | **posture<90%, false negative** |
| Sitting_Lying_FewLandmarks | 29.7% | FN | **posture<90%, false negative** |

---

## Bend_pickup_lowLight

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 41 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Bend_pickup_normalLight_back

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 116 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Bend_pickup_normalLight (**false positive**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 50 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** FP frames [59, 60, 63]

**Mismatched frames:**

_None_

---

## Bend_pickup_normalLight_leftRight

**Posture accuracy:** 92.0%

**Per-class accuracy:**

- Standing: 92.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 149 | 13 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 87 | Standing | Sitting | nan | nan | 20.3 | 0.2 | 16.5 | 0.5 | 0.6 | 0.4 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 88 | Standing | Sitting | nan | nan | 18.9 | 0.2 | 40.5 | 0.5 | 0.6 | 0.4 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 89 | Standing | Sitting | nan | nan | 17.4 | 0.6 | 42.3 | 0.5 | 0.6 | 0.5 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 90 | Standing | Sitting | nan | nan | 16.9 | 0.1 | 15.5 | 0.5 | 0.6 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 91 | Standing | Sitting | 175.6 | 159.9 | 15.2 | 0.0 | 49.3 | 0.5 | 0.6 | 0.5 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 92 | Standing | Sitting | 175.2 | 161.8 | 13.9 | 0.1 | 37.6 | 0.5 | 0.6 | 0.5 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 93 | Standing | Sitting | 174.7 | 163.6 | 12.5 | 0.1 | 40.2 | 0.5 | 0.6 | 0.5 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 94 | Standing | Sitting | 174.9 | 165.3 | 11.3 | 0.1 | 34.3 | 0.5 | 0.6 | 0.5 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 261 | Standing | Sitting | 158.6 | 141.5 | 31.1 | 0.4 | 19.3 | 0.4 | 0.6 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 262 | Standing | Sitting | 152.2 | 145.4 | 29.6 | 0.3 | 45.2 | 0.4 | 0.6 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 263 | Standing | Sitting | 155.8 | 149.9 | 26.5 | 0.1 | 88.9 | 0.4 | 0.6 | 0.4 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 264 | Standing | Sitting | 161.7 | 152.1 | 23.8 | 0.2 | 79.1 | 0.5 | 0.6 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 265 | Standing | Sitting | nan | 153.8 | 23.0 | 0.4 | 22.7 | 0.6 | 0.6 | 0.4 | F | F | Sitting|Standing|Standing|Standing|Standing |

---

## Bend_pickup_squat_lowLight

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 59 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Bend_pickup_squat_normalLight

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 40 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Kneeling

**Posture accuracy:** 98.2%

**Per-class accuracy:**

- Standing: 95.1%
- Sitting: 100.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 39 | 2 | 0 | 0 |
| **Sitting** | 0 | 71 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 156 | Standing | Sitting | 151.8 | 169.5 | 4.1 | 0.6 | 5.1 | 0.6 | 0.6 | 0.5 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 157 | Standing | Sitting | 154.6 | 170.9 | 3.6 | 0.4 | 14.3 | 0.6 | 0.6 | 0.5 | F | F | Sitting|Standing|Standing|Standing|Standing |

---

## LyingdownSlowly

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 24 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 118 | 0 |

**Fall detection:** TP (latency 95 frames)

**Mismatched frames:**

_None_

---

## Moving_in_out_frame (**posture<90%**)

**Posture accuracy:** 44.9%

**Per-class accuracy:**

- Standing: 62.6%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 92 | 55 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 59 | Not in frame | Standing | 178.0 | 175.5 | 0.2 | 0.0 | 0.9 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 60 | Not in frame | Standing | 176.5 | 174.3 | 0.3 | 0.2 | 0.7 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 61 | Not in frame | Standing | 172.8 | 174.0 | 0.4 | 0.1 | 4.1 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 62 | Not in frame | Standing | 170.7 | 173.3 | 1.1 | 0.1 | 20.3 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 63 | Not in frame | Standing | 170.5 | 172.6 | 1.1 | 0.1 | 1.1 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 64 | Not in frame | Standing | 172.7 | 173.6 | 1.1 | 0.5 | 0.8 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 65 | Not in frame | Standing | 172.2 | 173.0 | 2.0 | 0.2 | 26.1 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 66 | Not in frame | Standing | 172.8 | 174.8 | 2.5 | 0.1 | 13.6 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 67 | Not in frame | Standing | 177.6 | 173.2 | 1.0 | 0.4 | 43.2 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 68 | Not in frame | Standing | 176.9 | 174.2 | 0.4 | 0.1 | 16.4 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 69 | Not in frame | Standing | 174.8 | 173.5 | 1.2 | 0.7 | 22.9 | 0.7 | 0.7 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 70 | Not in frame | Standing | nan | 174.7 | 1.1 | 0.6 | 4.4 | 0.8 | 0.8 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 71 | Not in frame | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 72 | Not in frame | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 73 | Not in frame | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 74 | Not in frame | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 75 | Not in frame | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 76 | Not in frame | Standing | nan | 12.1 | 160.2 | 15.0 | 720.0 | 0.1 | 0.8 | 0.5 | F | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 77 | Not in frame | Standing | nan | 12.4 | 160.0 | 1.4 | 5.7 | 0.1 | 0.8 | 0.5 | F | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 78 | Not in frame | Standing | nan | nan | 159.2 | 0.4 | 25.0 | 0.3 | 0.8 | 0.5 | T | F | Unknown|Unknown|Sitting|Sitting|Sitting |
| 79 | Not in frame | Standing | nan | nan | 158.6 | 0.2 | 18.5 | 0.3 | 0.8 | 0.5 | T | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 80 | Not in frame | Sitting | nan | nan | 158.4 | 0.2 | 4.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 81 | Not in frame | Sitting | nan | nan | 160.5 | 0.2 | 61.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 82 | Not in frame | Sitting | nan | nan | 161.5 | 0.2 | 28.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 83 | Not in frame | Sitting | nan | nan | 162.5 | 0.4 | 31.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 84 | Not in frame | Sitting | nan | nan | 162.1 | 0.3 | 13.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 85 | Not in frame | Sitting | nan | nan | 163.2 | 0.4 | 32.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 86 | Not in frame | Sitting | nan | nan | 163.3 | 0.1 | 2.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 87 | Not in frame | Sitting | nan | nan | 164.2 | 0.2 | 26.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 88 | Not in frame | Sitting | nan | nan | 164.0 | 0.4 | 5.4 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 89 | Not in frame | Sitting | nan | nan | 163.8 | 0.1 | 7.5 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 90 | Not in frame | Sitting | nan | nan | 163.5 | 0.1 | 6.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 91 | Not in frame | Sitting | nan | nan | 163.7 | 0.2 | 5.5 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 92 | Not in frame | Sitting | nan | nan | 165.4 | 0.1 | 48.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 93 | Not in frame | Sitting | nan | nan | 165.3 | 0.5 | 3.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 94 | Not in frame | Sitting | nan | nan | 163.8 | 0.4 | 45.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 95 | Not in frame | Sitting | nan | nan | 161.5 | 0.1 | 66.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 96 | Not in frame | Sitting | nan | nan | 161.2 | 0.1 | 10.4 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 97 | Not in frame | Sitting | nan | nan | 160.6 | 0.5 | 16.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 98 | Not in frame | Sitting | nan | nan | 160.4 | 0.1 | 6.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Not in frame | Sitting | nan | nan | 159.9 | 0.7 | 13.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Not in frame | Sitting | nan | nan | 160.0 | 0.2 | 2.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Not in frame | Sitting | nan | nan | 160.3 | 0.2 | 9.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 102 | Not in frame | Sitting | nan | nan | 160.3 | 0.2 | 0.5 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 103 | Not in frame | Sitting | nan | nan | 159.9 | 0.0 | 10.9 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 104 | Not in frame | Sitting | nan | nan | 159.5 | 0.2 | 13.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 105 | Not in frame | Sitting | nan | nan | 160.2 | 0.4 | 21.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 106 | Not in frame | Sitting | nan | nan | 160.7 | 0.4 | 14.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 107 | Not in frame | Sitting | nan | nan | 160.9 | 0.1 | 4.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 108 | Not in frame | Sitting | nan | nan | 161.2 | 0.1 | 8.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 109 | Not in frame | Sitting | nan | nan | 161.5 | 0.2 | 10.6 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 110 | Not in frame | Sitting | nan | nan | 162.6 | 0.1 | 32.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 111 | Not in frame | Sitting | nan | nan | 163.6 | 0.5 | 28.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 112 | Not in frame | Sitting | nan | nan | 164.1 | 0.2 | 14.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 113 | Not in frame | Sitting | nan | nan | 164.0 | 0.3 | 1.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 114 | Not in frame | Sitting | nan | nan | 163.8 | 0.4 | 5.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 115 | Not in frame | Sitting | nan | nan | 162.7 | 0.3 | 33.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 116 | Not in frame | Sitting | nan | nan | 161.8 | 0.5 | 24.6 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 117 | Standing | Sitting | nan | nan | 161.4 | 0.0 | 14.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 118 | Standing | Sitting | nan | nan | 161.2 | 0.2 | 5.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 119 | Standing | Sitting | nan | nan | 161.7 | 0.8 | 16.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 120 | Standing | Sitting | nan | nan | 161.8 | 1.3 | 2.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 121 | Standing | Sitting | nan | nan | 162.0 | 0.2 | 5.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 122 | Standing | Sitting | nan | nan | 163.0 | 0.9 | 30.6 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 123 | Standing | Sitting | nan | nan | 163.5 | 0.3 | 11.9 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 124 | Standing | Sitting | nan | nan | 162.6 | 0.4 | 24.6 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 125 | Standing | Sitting | nan | nan | 163.6 | 0.2 | 27.5 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 126 | Standing | Sitting | nan | nan | 164.2 | 0.8 | 18.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 127 | Standing | Sitting | nan | nan | 164.9 | 0.4 | 21.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 128 | Standing | Sitting | nan | nan | 163.5 | 0.1 | 41.4 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 129 | Standing | Sitting | nan | nan | 163.8 | 0.1 | 8.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 130 | Standing | Sitting | nan | nan | 164.0 | 0.1 | 6.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 131 | Standing | Sitting | nan | nan | 163.7 | 0.1 | 10.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 132 | Standing | Sitting | nan | nan | 164.7 | 0.6 | 29.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 133 | Standing | Sitting | nan | nan | 166.3 | 0.0 | 48.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 134 | Standing | Sitting | nan | nan | 167.1 | 0.3 | 23.5 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 135 | Standing | Sitting | nan | nan | 168.8 | 0.3 | 48.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 136 | Standing | Sitting | nan | nan | 167.0 | 0.5 | 51.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 137 | Standing | Sitting | nan | nan | 167.0 | 0.0 | 1.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 138 | Standing | Sitting | nan | nan | 167.9 | 0.0 | 27.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 139 | Standing | Sitting | nan | nan | 167.8 | 0.2 | 4.6 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 140 | Standing | Sitting | nan | nan | 167.7 | 0.1 | 2.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 141 | Standing | Sitting | nan | nan | 167.2 | 0.1 | 14.9 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 142 | Standing | Sitting | nan | nan | 166.8 | 0.4 | 10.9 | 0.4 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 143 | Standing | Sitting | nan | nan | 166.3 | 0.2 | 15.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 144 | Standing | Sitting | nan | nan | 165.8 | 0.2 | 12.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 145 | Standing | Sitting | nan | nan | 165.8 | 0.1 | 1.9 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 146 | Standing | Sitting | nan | nan | 167.0 | 0.4 | 36.6 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 147 | Standing | Sitting | nan | nan | 166.7 | 0.3 | 8.1 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 148 | Standing | Sitting | nan | nan | 166.6 | 0.2 | 3.9 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 149 | Standing | Sitting | nan | nan | 167.5 | 0.1 | 25.2 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 150 | Standing | Sitting | nan | nan | 167.9 | 0.1 | 11.4 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 151 | Standing | Sitting | nan | nan | 167.9 | 0.1 | 0.9 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 152 | Standing | Sitting | nan | nan | 168.8 | 0.1 | 26.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 153 | Standing | Sitting | nan | nan | 168.4 | 0.1 | 11.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 154 | Standing | Sitting | nan | nan | 167.7 | 0.1 | 22.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 155 | Standing | Sitting | nan | nan | 168.0 | 0.1 | 10.3 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 156 | Standing | Sitting | nan | nan | 165.9 | 0.2 | 61.7 | 0.4 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 157 | Standing | Sitting | nan | nan | 166.2 | 0.1 | 9.7 | 0.4 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 158 | Standing | Sitting | nan | nan | 165.4 | 0.0 | 25.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 159 | Standing | Sitting | nan | nan | 167.3 | 0.3 | 56.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 160 | Standing | Sitting | nan | nan | 166.9 | 0.0 | 13.0 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 161 | Standing | Sitting | nan | nan | 166.6 | 0.0 | 7.5 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 162 | Standing | Sitting | nan | nan | 167.0 | 0.1 | 10.7 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 163 | Standing | Sitting | nan | nan | 167.6 | 0.1 | 18.5 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 164 | Standing | Sitting | nan | nan | 167.9 | 0.1 | 8.6 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 165 | Standing | Sitting | nan | nan | 167.9 | 0.3 | 1.4 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 166 | Standing | Sitting | nan | nan | 167.7 | 0.7 | 3.8 | 0.3 | 0.8 | 0.5 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 167 | Standing | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 168 | Standing | Sitting | nan | nan | 3.3 | 5.0 | 720.0 | 0.7 | 0.8 | 0.4 | T | F | Sitting|Sitting|Sitting|Unknown|Standing |
| 169 | Standing | Sitting | nan | nan | 3.6 | 0.5 | 7.2 | 0.7 | 0.8 | 0.4 | T | F | Sitting|Sitting|Unknown|Standing|Standing |
| 170 | Standing | Sitting | nan | nan | 3.8 | 0.4 | 6.1 | 0.7 | 0.8 | 0.4 | T | F | Sitting|Unknown|Standing|Standing|Standing |
| 171 | Standing | Sitting | nan | nan | 3.3 | 0.2 | 13.1 | 0.7 | 0.8 | 0.4 | T | F | Unknown|Standing|Standing|Standing|Standing |

---

## Moving_in_out_frame_withFall (**posture<90%, false negative**)

**Posture accuracy:** 49.7%

**Per-class accuracy:**

- Standing: 58.6%
- Sitting: nan%
- Lying: 69.5%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 41 | 0 | 0 | 29 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 10 | 8 | 41 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 42 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 43 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 44 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 45 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 46 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 47 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 48 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 49 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 50 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 51 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 52 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 53 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 54 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 55 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 56 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 57 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 58 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 59 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 60 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 61 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 62 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 63 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 64 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 65 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 66 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 67 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 68 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 69 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 70 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 71 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 72 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 73 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 74 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 75 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 76 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 77 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 78 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 79 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 80 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 81 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 82 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 83 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 84 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 85 | Not in frame | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 88 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 89 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 90 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 91 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
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
| 104 | Standing | Unknown | nan | nan | 0.5 | 0.0 | 2.2 | 0.6 | 0.7 | 0.4 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 105 | Standing | Unknown | nan | 161.0 | 2.2 | 0.9 | 47.5 | 0.7 | 0.7 | 0.4 | F | F | Unknown|Unknown|Unknown|Standing|Standing |
| 106 | Standing | Unknown | nan | 168.3 | 3.3 | 0.7 | 33.1 | 0.7 | 0.7 | 0.3 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 107 | Standing | Unknown | nan | 172.9 | 3.7 | 0.6 | 12.0 | 0.7 | 0.7 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 146 | Lying | Standing | nan | nan | 31.7 | 0.8 | 136.4 | 0.4 | 0.8 | 0.2 | T | F | Standing|Standing|Standing|Standing|Sitting |
| 147 | Lying | Standing | nan | nan | 37.5 | 1.0 | 167.1 | 0.4 | 0.8 | 0.2 | T | F | Standing|Standing|Standing|Sitting|Sitting |
| 148 | Lying | Standing | nan | nan | 39.8 | 0.9 | 68.7 | 0.4 | 0.8 | 0.2 | T | F | Standing|Standing|Sitting|Sitting|Sitting |
| 149 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Sitting|Sitting|Sitting|Unknown |
| 150 | Lying | Standing | nan | nan | 51.4 | 1.3 | 169.2 | 0.3 | 0.8 | 0.2 | T | F | Sitting|Sitting|Sitting|Unknown|Lying |
| 192 | Lying | Sitting | 15.5 | 156.9 | 169.5 | 0.7 | 9.2 | 0.2 | 0.8 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 193 | Lying | Sitting | nan | 119.8 | 169.8 | 0.4 | 7.0 | 0.3 | 0.8 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 194 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 195 | Lying | Sitting | nan | nan | 30.0 | 3.1 | 720.0 | 0.3 | 0.8 | 0.3 | T | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 196 | Lying | Sitting | nan | nan | 29.8 | 0.4 | 6.1 | 0.3 | 0.8 | 0.3 | T | F | Sitting|Sitting|Unknown|Sitting|Standing |
| 197 | Lying | Sitting | nan | nan | 28.1 | 1.4 | 49.2 | 0.3 | 0.8 | 0.3 | T | F | Sitting|Unknown|Sitting|Standing|Standing |
| 198 | Lying | Sitting | nan | nan | 28.4 | 1.1 | 9.0 | 0.3 | 0.8 | 0.3 | T | F | Unknown|Sitting|Standing|Standing|Standing |
| 199 | Lying | Sitting | nan | nan | 27.7 | 0.4 | 22.1 | 0.3 | 0.8 | 0.3 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 200 | Lying | Standing | nan | nan | 24.5 | 3.5 | 93.4 | 0.3 | 0.8 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 201 | Lying | Standing | nan | nan | 24.4 | 1.9 | 2.4 | 0.3 | 0.8 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 202 | Lying | Standing | nan | nan | 23.2 | 0.1 | 34.3 | 0.3 | 0.8 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 203 | Lying | Standing | nan | nan | 22.7 | 4.6 | 14.9 | 0.3 | 0.8 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 204 | Lying | Standing | nan | nan | 21.0 | 3.2 | 48.2 | 0.3 | 0.8 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Sit_Stand_AnklesInvisible (**posture<90%**)

**Posture accuracy:** 41.1%

**Per-class accuracy:**

- Standing: 93.5%
- Sitting: 26.4%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 29 | 2 | 0 | 0 |
| **Sitting** | 81 | 29 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 28 | Sitting | Standing | nan | nan | 1.3 | 0.1 | 2.3 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 29 | Sitting | Standing | nan | nan | 1.5 | 0.2 | 4.9 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 30 | Sitting | Standing | nan | nan | 1.6 | 0.1 | 5.0 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 31 | Sitting | Standing | nan | nan | 1.2 | 0.4 | 13.3 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 32 | Sitting | Standing | nan | nan | 0.5 | 0.6 | 17.8 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 33 | Sitting | Standing | nan | nan | 0.7 | 0.3 | 3.7 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 34 | Sitting | Standing | nan | nan | 1.1 | 1.2 | 11.9 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 35 | Sitting | Standing | nan | nan | 0.5 | 0.7 | 16.8 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 36 | Sitting | Standing | nan | nan | 0.1 | 0.2 | 11.6 | 0.3 | 0.5 | 0.5 | T | F | Standing|Standing|Standing|Standing|Standing |
| 37 | Sitting | Standing | nan | nan | 0.4 | 0.6 | 9.7 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 38 | Sitting | Standing | nan | 168.5 | 0.2 | 0.2 | 7.2 | 0.4 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 39 | Sitting | Standing | nan | 166.6 | 0.0 | 0.3 | 3.7 | 0.4 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 40 | Sitting | Standing | nan | 165.9 | 0.4 | 0.3 | 10.7 | 0.4 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 41 | Sitting | Standing | nan | 164.2 | 0.3 | 0.1 | 2.6 | 0.4 | 0.5 | 0.4 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 42 | Sitting | Standing | nan | 163.6 | 0.2 | 0.3 | 3.8 | 0.4 | 0.5 | 0.4 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 72 | Sitting | Standing | nan | nan | 4.8 | 0.1 | 0.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 73 | Sitting | Standing | nan | nan | 4.6 | 0.0 | 5.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 74 | Sitting | Standing | nan | nan | 4.6 | 0.0 | 0.3 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 75 | Sitting | Standing | nan | nan | 4.8 | 0.1 | 5.1 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 76 | Sitting | Standing | nan | nan | 5.1 | 0.1 | 8.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 77 | Sitting | Standing | nan | nan | 5.3 | 0.1 | 5.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 78 | Sitting | Standing | nan | nan | 5.3 | 0.3 | 0.4 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 79 | Sitting | Standing | nan | nan | 5.2 | 0.1 | 1.9 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 80 | Sitting | Standing | nan | nan | 5.0 | 0.2 | 5.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 81 | Sitting | Standing | nan | nan | 5.0 | 0.1 | 0.1 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 82 | Sitting | Standing | nan | nan | 5.1 | 0.0 | 1.4 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 83 | Sitting | Standing | nan | nan | 5.0 | 0.2 | 1.7 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Sitting | Standing | nan | nan | 5.0 | 0.1 | 1.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Sitting | Standing | nan | nan | 5.1 | 0.0 | 0.8 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Sitting | Standing | nan | nan | 5.0 | 0.1 | 0.9 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Sitting | Standing | nan | nan | 5.1 | 0.2 | 1.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Sitting | Standing | nan | nan | 5.1 | 0.0 | 0.7 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Sitting | Standing | nan | nan | 5.1 | 0.1 | 0.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Sitting | Standing | nan | nan | 5.3 | 0.1 | 5.1 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Sitting | Standing | nan | nan | 5.2 | 0.0 | 1.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Sitting | Standing | nan | nan | 5.2 | 0.0 | 0.4 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Sitting | Standing | nan | nan | 5.2 | 0.1 | 0.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Sitting | Standing | nan | nan | 5.2 | 0.0 | 0.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Sitting | Standing | nan | nan | 5.2 | 0.2 | 1.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Sitting | Standing | nan | nan | 5.1 | 0.1 | 0.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Sitting | Standing | nan | nan | 5.1 | 0.1 | 0.7 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Sitting | Standing | nan | nan | 5.1 | 0.0 | 0.4 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Sitting | Standing | nan | nan | 5.1 | 0.1 | 0.1 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Sitting | Standing | nan | nan | 5.1 | 0.0 | 0.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 101 | Sitting | Standing | nan | nan | 5.2 | 0.1 | 2.9 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 102 | Sitting | Standing | nan | nan | 5.2 | 0.0 | 0.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 103 | Sitting | Standing | nan | nan | 5.4 | 0.2 | 4.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 104 | Sitting | Standing | nan | nan | 5.4 | 0.0 | 0.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 105 | Sitting | Standing | nan | nan | 5.4 | 0.0 | 0.4 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 106 | Sitting | Standing | nan | nan | 5.4 | 0.0 | 1.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 107 | Sitting | Standing | nan | nan | 5.4 | 0.0 | 0.9 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 108 | Sitting | Standing | nan | nan | 5.5 | 0.0 | 1.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 109 | Sitting | Standing | nan | nan | 5.5 | 0.0 | 1.3 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 110 | Sitting | Standing | nan | nan | 5.5 | 0.1 | 0.1 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 111 | Sitting | Standing | nan | nan | 5.4 | 0.1 | 2.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 112 | Sitting | Standing | nan | nan | 5.5 | 0.0 | 0.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 113 | Sitting | Standing | nan | nan | 5.6 | 0.1 | 2.7 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 114 | Sitting | Standing | nan | nan | 5.6 | 0.0 | 0.8 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 115 | Sitting | Standing | nan | nan | 5.7 | 0.1 | 1.8 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 116 | Sitting | Standing | nan | nan | 5.7 | 0.2 | 0.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 117 | Sitting | Standing | nan | nan | 5.5 | 0.0 | 4.9 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 118 | Sitting | Standing | nan | nan | 5.5 | 0.1 | 0.8 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 119 | Sitting | Standing | nan | nan | 5.5 | 0.1 | 1.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 120 | Sitting | Standing | nan | nan | 5.6 | 0.0 | 1.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Sitting | Standing | nan | nan | 5.6 | 0.0 | 1.7 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Sitting | Standing | nan | nan | 5.7 | 0.0 | 0.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Sitting | Standing | nan | nan | 5.7 | 0.0 | 0.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Sitting | Standing | nan | nan | 5.8 | 0.1 | 2.2 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Sitting | Standing | nan | nan | 5.8 | 0.0 | 1.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Sitting | Standing | nan | nan | 5.8 | 0.0 | 1.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Sitting | Standing | nan | nan | 5.7 | 0.1 | 2.7 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Sitting | Standing | nan | nan | 5.6 | 0.2 | 3.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Sitting | Standing | nan | nan | 5.5 | 0.1 | 2.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Sitting | Standing | nan | nan | 5.5 | 0.2 | 1.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Sitting | Standing | nan | nan | 5.4 | 0.2 | 2.5 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Sitting | Standing | nan | nan | 5.4 | 0.1 | 0.3 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Sitting | Standing | nan | nan | 5.2 | 0.4 | 4.9 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Sitting | Standing | nan | nan | 5.1 | 0.0 | 3.1 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Sitting | Standing | nan | nan | 5.0 | 0.5 | 1.6 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Sitting | Standing | nan | nan | 5.0 | 0.0 | 0.9 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Sitting | Standing | nan | nan | 5.0 | 0.1 | 1.0 | 0.3 | 0.5 | 0.4 | T | F | Standing|Standing|Standing|Standing|Standing |
| 168 | Standing | Sitting | nan | 171.4 | 1.3 | 0.4 | 3.8 | 0.4 | 0.5 | 0.4 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 169 | Standing | Sitting | nan | 172.0 | 1.8 | 0.7 | 14.8 | 0.4 | 0.5 | 0.5 | F | F | Sitting|Standing|Standing|Standing|Standing |

---

## SitFast_GetupFast (**posture<90%**)

**Posture accuracy:** 34.3%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 16.9%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 22 | 0 | 0 | 0 |
| **Sitting** | 69 | 14 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 28 | Sitting | Standing | 162.8 | 161.0 | 4.1 | 0.4 | 3.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 29 | Sitting | Standing | 159.2 | 158.9 | 4.0 | 0.3 | 3.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 30 | Sitting | Standing | 157.3 | 157.9 | 3.2 | 0.5 | 20.4 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 31 | Sitting | Standing | 155.6 | 156.8 | 2.6 | 0.3 | 17.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 32 | Sitting | Standing | 154.9 | 156.3 | 0.8 | 0.1 | 48.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 33 | Sitting | Standing | 154.6 | 156.6 | 0.5 | 0.0 | 8.7 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 34 | Sitting | Standing | 153.8 | 156.3 | 0.2 | 0.1 | 9.6 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 35 | Sitting | Standing | 153.0 | 156.2 | 1.0 | 0.0 | 22.3 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 36 | Sitting | Standing | 152.8 | 156.7 | 1.3 | 0.1 | 9.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 37 | Sitting | Standing | 152.3 | 156.4 | 2.2 | 0.0 | 24.3 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 38 | Sitting | Standing | 152.3 | 156.6 | 2.8 | 0.0 | 16.3 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 39 | Sitting | Standing | 151.9 | 155.7 | 3.1 | 0.1 | 9.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 40 | Sitting | Standing | 150.0 | 154.1 | 3.3 | 0.1 | 6.7 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 41 | Sitting | Standing | 147.9 | 152.8 | 3.8 | 0.1 | 11.5 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 42 | Sitting | Standing | 145.5 | 150.9 | 4.1 | 0.1 | 8.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 43 | Sitting | Standing | 144.2 | 149.9 | 4.4 | 0.2 | 10.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 44 | Sitting | Standing | 143.6 | 149.4 | 4.8 | 0.1 | 9.4 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 45 | Sitting | Standing | 141.6 | 147.9 | 5.0 | 0.0 | 6.8 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 46 | Sitting | Standing | 141.9 | 148.1 | 5.3 | 0.0 | 7.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 47 | Sitting | Standing | 141.5 | 147.7 | 5.3 | 0.0 | 1.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 48 | Sitting | Standing | 142.2 | 148.3 | 5.3 | 0.0 | 0.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 56 | Sitting | Standing | 144.2 | 149.2 | 5.3 | 0.0 | 0.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 57 | Sitting | Standing | 144.6 | 149.4 | 5.3 | 0.0 | 0.5 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 58 | Sitting | Standing | 145.1 | 149.6 | 5.4 | 0.0 | 1.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 59 | Sitting | Standing | 144.6 | 149.2 | 5.3 | 0.0 | 1.6 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 60 | Sitting | Standing | 145.2 | 149.4 | 5.3 | 0.0 | 0.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 61 | Sitting | Standing | 144.5 | 148.9 | 5.3 | 0.1 | 0.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 62 | Sitting | Standing | 144.6 | 149.0 | 5.4 | 0.0 | 1.8 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 63 | Sitting | Standing | 144.1 | 148.6 | 5.3 | 0.0 | 1.7 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 64 | Sitting | Standing | 145.2 | 149.4 | 5.4 | 0.1 | 3.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 65 | Sitting | Standing | 144.8 | 149.1 | 5.4 | 0.0 | 0.4 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 66 | Sitting | Standing | 144.8 | 149.2 | 5.4 | 0.0 | 0.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 67 | Sitting | Standing | 145.2 | 149.7 | 5.4 | 0.0 | 1.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 68 | Sitting | Standing | 144.6 | 149.0 | 5.4 | 0.0 | 0.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 69 | Sitting | Standing | 144.7 | 149.3 | 5.3 | 0.0 | 0.3 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 70 | Sitting | Standing | 144.8 | 149.3 | 5.4 | 0.0 | 0.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 71 | Sitting | Standing | 144.5 | 149.0 | 5.4 | 0.0 | 0.4 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 72 | Sitting | Standing | 145.0 | 149.4 | 5.4 | 0.0 | 0.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 73 | Sitting | Standing | 144.5 | 149.1 | 5.3 | 0.0 | 1.5 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 74 | Sitting | Standing | 144.3 | 148.8 | 5.3 | 0.1 | 0.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 75 | Sitting | Standing | 144.9 | 149.5 | 5.4 | 0.1 | 2.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 76 | Sitting | Standing | 144.4 | 149.2 | 5.4 | 0.0 | 1.6 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 77 | Sitting | Standing | 144.2 | 149.0 | 5.4 | 0.0 | 0.3 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 78 | Sitting | Standing | 144.0 | 148.6 | 5.4 | 0.0 | 0.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 79 | Sitting | Standing | 144.2 | 149.0 | 5.4 | 0.0 | 0.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 80 | Sitting | Standing | 144.2 | 149.1 | 5.4 | 0.0 | 0.6 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 81 | Sitting | Standing | 144.4 | 149.2 | 5.3 | 0.0 | 0.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 82 | Sitting | Standing | 144.5 | 149.3 | 5.3 | 0.0 | 0.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 83 | Sitting | Standing | 144.3 | 149.2 | 5.4 | 0.1 | 1.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Sitting | Standing | 144.3 | 149.2 | 5.5 | 0.0 | 2.4 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Sitting | Standing | 144.0 | 149.1 | 5.4 | 0.0 | 2.7 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Sitting | Standing | 144.4 | 149.3 | 5.4 | 0.0 | 0.7 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Sitting | Standing | 144.2 | 149.0 | 5.4 | 0.0 | 0.7 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Sitting | Standing | 144.2 | 149.0 | 5.4 | 0.0 | 0.3 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Sitting | Standing | 144.6 | 149.5 | 5.4 | 0.0 | 0.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Sitting | Standing | 144.3 | 149.4 | 5.4 | 0.1 | 0.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Sitting | Standing | 144.6 | 149.9 | 5.5 | 0.2 | 3.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Sitting | Standing | 144.4 | 149.5 | 5.5 | 0.0 | 0.6 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Sitting | Standing | 144.6 | 149.7 | 5.5 | 0.0 | 0.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Sitting | Standing | 144.4 | 149.6 | 5.5 | 0.0 | 0.4 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Sitting | Standing | 144.4 | 149.6 | 5.5 | 0.0 | 0.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Sitting | Standing | 144.5 | 149.8 | 5.4 | 0.0 | 1.8 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Sitting | Standing | 144.5 | 149.7 | 5.3 | 0.1 | 3.8 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Sitting | Standing | 144.2 | 149.5 | 5.3 | 0.0 | 0.0 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Sitting | Standing | 143.9 | 149.1 | 5.3 | 0.0 | 1.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Sitting | Standing | 141.9 | 147.1 | 5.3 | 0.0 | 0.9 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 101 | Sitting | Standing | 141.5 | 146.7 | 5.3 | 0.2 | 1.1 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 102 | Sitting | Standing | 138.4 | 143.6 | 5.3 | 0.0 | 0.2 | 0.3 | 0.5 | 0.4 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 103 | Sitting | Standing | 137.7 | 143.0 | 5.3 | 0.1 | 0.4 | 0.3 | 0.5 | 0.4 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |

---

## SitFloor_lowKeypoints_crossedLegs

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: 100.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 115 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## SitFloor_lowKeypoints

**Posture accuracy:** 95.1%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 92.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 57 | 0 | 0 | 0 |
| **Sitting** | 7 | 80 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 117 | Sitting | Standing | nan | nan | 7.8 | 0.4 | 57.2 | 0.3 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 118 | Sitting | Standing | nan | nan | 5.3 | 0.5 | 71.7 | 0.3 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 119 | Sitting | Standing | nan | nan | 3.2 | 0.3 | 61.9 | 0.4 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 120 | Sitting | Standing | nan | 49.1 | 1.6 | 0.3 | 46.9 | 0.2 | 0.7 | 0.2 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 121 | Sitting | Standing | 71.4 | 50.6 | 0.3 | 0.2 | 38.7 | 0.3 | 0.7 | 0.2 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 122 | Sitting | Standing | 74.6 | 53.5 | 1.0 | 0.4 | 21.1 | 0.3 | 0.7 | 0.2 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 123 | Sitting | Standing | 75.1 | 55.0 | 3.3 | 0.5 | 67.2 | 0.3 | 0.7 | 0.2 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |

---

## Sitting_HalfLandmarks (**posture<90%**)

**Posture accuracy:** 86.2%

**Per-class accuracy:**

- Standing: 64.3%
- Sitting: 93.2%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 18 | 0 | 0 | 10 |
| **Sitting** | 6 | 82 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown |
| 4 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown |
| 5 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 6 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 7 | Standing | Unknown | 175.5 | 176.0 | 3.3 | 0.0 | 0.0 | 0.6 | 0.6 | 0.4 | F | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 8 | Standing | Unknown | 178.5 | 175.1 | 3.7 | 0.5 | 14.1 | 0.6 | 0.6 | 0.4 | F | F | Unknown|Unknown|Unknown|Standing|Standing |
| 9 | Standing | Unknown | 177.8 | 174.5 | 4.6 | 0.5 | 24.4 | 0.7 | 0.7 | 0.4 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 10 | Standing | Unknown | 177.7 | 174.7 | 4.9 | 0.1 | 8.6 | 0.7 | 0.7 | 0.4 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 130 | Sitting | Standing | 144.0 | 149.2 | 6.9 | 0.1 | 0.5 | 0.5 | 0.7 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Sitting | Standing | 145.2 | 149.6 | 7.2 | 0.0 | 7.9 | 0.5 | 0.7 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Sitting | Standing | 140.8 | 147.1 | 7.4 | 0.0 | 5.6 | 0.5 | 0.7 | 0.2 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 133 | Sitting | Standing | 141.6 | 148.2 | 7.4 | 0.2 | 1.7 | 0.5 | 0.7 | 0.2 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 134 | Sitting | Standing | 142.0 | 148.5 | 7.6 | 0.1 | 4.3 | 0.5 | 0.7 | 0.2 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 135 | Sitting | Standing | 140.1 | 147.9 | 7.7 | 0.1 | 4.3 | 0.5 | 0.7 | 0.2 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |

---

## Sitting_Lying_FewLandmarks_back (**posture<90%, false negative**)

**Posture accuracy:** 13.7%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 0.0%
- Lying: 20.2%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 14 | 0 | 0 | 0 |
| **Sitting** | 145 | 0 | 0 | 0 |
| **Lying** | 0 | 95 | 24 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 47 | Sitting | Standing | nan | nan | 1.4 | 0.1 | 27.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 48 | Sitting | Standing | nan | nan | 1.9 | 0.1 | 15.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 49 | Sitting | Standing | nan | nan | 2.6 | 0.2 | 19.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 50 | Sitting | Standing | nan | nan | 2.6 | 0.1 | 0.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 51 | Sitting | Standing | nan | nan | 2.5 | 0.0 | 0.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 52 | Sitting | Standing | nan | nan | 3.0 | 0.3 | 14.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 53 | Sitting | Standing | nan | nan | 3.9 | 0.1 | 25.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 54 | Sitting | Standing | nan | nan | 4.0 | 0.3 | 3.8 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 55 | Sitting | Standing | nan | nan | 3.9 | 0.1 | 3.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 56 | Sitting | Standing | nan | nan | 3.6 | 0.3 | 7.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 57 | Sitting | Standing | nan | nan | 4.0 | 0.2 | 12.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 58 | Sitting | Standing | nan | nan | 3.1 | 0.2 | 27.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 59 | Sitting | Standing | nan | nan | 3.0 | 0.3 | 3.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 60 | Sitting | Standing | nan | nan | 3.7 | 0.1 | 21.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 61 | Sitting | Standing | nan | nan | 3.8 | 0.1 | 2.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 62 | Sitting | Standing | nan | nan | 3.5 | 0.2 | 6.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 63 | Sitting | Standing | nan | nan | 2.7 | 0.2 | 25.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 64 | Sitting | Standing | nan | nan | 1.9 | 0.3 | 24.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 65 | Sitting | Standing | nan | nan | 2.1 | 0.3 | 5.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 66 | Sitting | Standing | nan | nan | 2.0 | 0.6 | 2.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 67 | Sitting | Standing | nan | nan | 1.0 | 0.6 | 29.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 68 | Sitting | Standing | nan | nan | 1.4 | 0.2 | 11.4 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 69 | Sitting | Standing | nan | nan | 1.7 | 0.0 | 10.4 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 70 | Sitting | Standing | nan | nan | 2.2 | 0.2 | 12.8 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 71 | Sitting | Standing | nan | nan | 2.1 | 0.2 | 1.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 72 | Sitting | Standing | nan | nan | 2.2 | 0.2 | 2.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 73 | Sitting | Standing | nan | nan | 2.3 | 0.3 | 1.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 74 | Sitting | Standing | nan | nan | 2.5 | 0.3 | 7.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 75 | Sitting | Standing | nan | nan | 1.8 | 0.0 | 22.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 76 | Sitting | Standing | nan | nan | 1.6 | 0.1 | 4.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 77 | Sitting | Standing | nan | nan | 1.5 | 0.0 | 4.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 78 | Sitting | Standing | nan | nan | 1.4 | 0.2 | 1.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 79 | Sitting | Standing | nan | nan | 1.1 | 0.2 | 8.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 80 | Sitting | Standing | nan | nan | 0.5 | 0.1 | 18.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 81 | Sitting | Standing | nan | nan | 0.6 | 0.2 | 3.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 82 | Sitting | Standing | nan | nan | 1.5 | 0.2 | 25.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 83 | Sitting | Standing | nan | nan | 2.0 | 0.0 | 15.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Sitting | Standing | nan | nan | 2.7 | 0.1 | 19.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Sitting | Standing | nan | nan | 3.4 | 0.0 | 21.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Sitting | Standing | nan | nan | 4.2 | 0.1 | 23.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Sitting | Standing | nan | nan | 4.8 | 0.0 | 19.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Sitting | Standing | nan | nan | 6.7 | 0.0 | 54.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Sitting | Standing | nan | nan | 7.8 | 0.1 | 34.8 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Sitting | Standing | nan | nan | 7.9 | 0.2 | 1.8 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Sitting | Standing | nan | nan | 8.3 | 0.1 | 11.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Sitting | Standing | nan | nan | 8.8 | 0.2 | 16.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Sitting | Standing | nan | nan | 10.4 | 0.0 | 45.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Sitting | Standing | nan | nan | 11.2 | 0.1 | 24.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Sitting | Standing | nan | nan | 11.3 | 0.3 | 2.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Sitting | Standing | nan | nan | 12.1 | 1.2 | 26.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Sitting | Standing | nan | nan | 12.5 | 0.8 | 11.3 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Sitting | Standing | nan | nan | 12.0 | 0.1 | 14.3 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Sitting | Standing | nan | nan | 12.8 | 0.8 | 21.8 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Sitting | Standing | nan | nan | 13.3 | 0.6 | 15.8 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 101 | Sitting | Standing | nan | nan | 13.1 | 0.5 | 7.9 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 102 | Sitting | Standing | nan | nan | 13.1 | 0.1 | 0.5 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 103 | Sitting | Standing | nan | nan | 12.8 | 0.1 | 8.4 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 104 | Sitting | Standing | nan | nan | 13.0 | 0.0 | 5.6 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 105 | Sitting | Standing | nan | nan | 12.5 | 0.1 | 13.0 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 106 | Sitting | Standing | nan | nan | 12.4 | 0.1 | 4.0 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 107 | Sitting | Standing | nan | nan | 12.3 | 0.2 | 2.0 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 108 | Sitting | Standing | nan | nan | 12.3 | 0.1 | 0.8 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 109 | Sitting | Standing | nan | nan | 12.7 | 0.2 | 12.2 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 110 | Sitting | Standing | nan | nan | 12.7 | 0.2 | 0.4 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 111 | Sitting | Standing | nan | nan | 12.3 | 0.3 | 11.2 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 112 | Sitting | Standing | nan | nan | 10.8 | 1.2 | 45.8 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 113 | Sitting | Standing | nan | nan | 10.6 | 0.1 | 6.4 | 0.6 | 0.7 | 0.3 | T | F | Standing|Standing|Standing|Standing|Standing |
| 114 | Sitting | Standing | nan | nan | 9.8 | 0.6 | 21.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 115 | Sitting | Standing | nan | nan | 8.9 | 0.5 | 27.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 116 | Sitting | Standing | nan | nan | 7.8 | 0.5 | 33.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 117 | Sitting | Standing | nan | nan | 6.7 | 0.1 | 30.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 118 | Sitting | Standing | nan | nan | 5.6 | 0.6 | 34.8 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 119 | Sitting | Standing | nan | nan | 5.6 | 0.3 | 1.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 120 | Sitting | Standing | nan | nan | 5.1 | 0.1 | 16.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Sitting | Standing | nan | nan | 4.6 | 0.1 | 15.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Sitting | Standing | nan | nan | 3.1 | 0.2 | 43.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Sitting | Standing | nan | nan | 2.4 | 0.1 | 21.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Sitting | Standing | nan | nan | 1.6 | 0.1 | 22.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Sitting | Standing | nan | nan | 0.7 | 0.1 | 27.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Sitting | Standing | nan | nan | 0.5 | 0.1 | 7.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Sitting | Standing | nan | nan | 0.1 | 0.1 | 10.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Sitting | Standing | nan | nan | 0.7 | 0.1 | 17.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Sitting | Standing | nan | nan | 1.7 | 0.1 | 29.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Sitting | Standing | nan | nan | 2.3 | 0.1 | 18.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Sitting | Standing | nan | nan | 3.0 | 0.3 | 21.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Sitting | Standing | nan | nan | 3.3 | 0.1 | 8.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Sitting | Standing | nan | nan | 4.9 | 0.1 | 47.8 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Sitting | Standing | nan | nan | 4.2 | 0.1 | 20.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Sitting | Standing | nan | nan | 3.9 | 0.2 | 10.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Sitting | Standing | nan | nan | 3.7 | 0.0 | 6.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Sitting | Standing | nan | nan | 3.2 | 0.2 | 13.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Sitting | Standing | nan | nan | 3.1 | 0.3 | 3.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Sitting | Standing | nan | nan | 2.8 | 0.1 | 10.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Sitting | Standing | nan | nan | 2.5 | 0.0 | 7.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Sitting | Standing | nan | nan | 2.5 | 0.2 | 1.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Sitting | Standing | nan | nan | 2.2 | 0.1 | 9.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Sitting | Standing | nan | nan | 2.2 | 0.1 | 0.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Sitting | Standing | nan | nan | 2.1 | 0.1 | 4.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Sitting | Standing | nan | nan | 2.1 | 0.0 | 0.8 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Sitting | Standing | nan | nan | 1.5 | 0.1 | 16.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Sitting | Standing | nan | nan | 1.1 | 0.4 | 11.3 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 231 | Lying | Sitting | nan | nan | 116.2 | 0.1 | 13.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 232 | Lying | Sitting | nan | nan | 117.3 | 0.1 | 32.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 233 | Lying | Sitting | nan | nan | 117.1 | 0.2 | 5.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 234 | Lying | Sitting | nan | nan | 117.0 | 0.1 | 4.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 235 | Lying | Sitting | nan | nan | 117.2 | 0.1 | 7.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 236 | Lying | Sitting | nan | nan | 116.3 | 0.5 | 25.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 237 | Lying | Sitting | nan | nan | 115.6 | 0.1 | 20.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 238 | Lying | Sitting | nan | nan | 114.9 | 0.2 | 22.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 239 | Lying | Sitting | nan | nan | 114.6 | 0.3 | 9.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Lying |
| 240 | Lying | Sitting | nan | nan | 116.8 | 0.8 | 65.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Lying|Sitting |
| 241 | Lying | Sitting | nan | nan | 116.7 | 0.1 | 0.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Lying|Sitting|Sitting |
| 242 | Lying | Sitting | nan | nan | 116.8 | 0.1 | 0.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Lying|Sitting|Sitting|Sitting |
| 243 | Lying | Sitting | nan | nan | 118.9 | 0.5 | 62.8 | 0.4 | 0.7 | 0.2 | T | F | Lying|Sitting|Sitting|Sitting|Sitting |
| 244 | Lying | Sitting | nan | nan | 118.7 | 0.0 | 5.5 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 245 | Lying | Sitting | nan | nan | 117.5 | 0.3 | 36.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 246 | Lying | Sitting | nan | nan | 114.8 | 0.6 | 78.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 247 | Lying | Sitting | nan | nan | 115.5 | 0.2 | 19.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 248 | Lying | Sitting | nan | nan | 114.7 | 0.4 | 23.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 249 | Lying | Sitting | nan | nan | 116.2 | 0.4 | 42.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 250 | Lying | Sitting | nan | nan | 118.0 | 0.3 | 53.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 251 | Lying | Sitting | nan | nan | 118.7 | 0.4 | 22.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 252 | Lying | Sitting | nan | nan | 118.9 | 0.2 | 4.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 253 | Lying | Sitting | nan | nan | 118.3 | 0.3 | 16.5 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 254 | Lying | Sitting | nan | nan | 118.3 | 0.1 | 1.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 255 | Lying | Sitting | nan | nan | 119.1 | 0.3 | 25.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 256 | Lying | Sitting | nan | nan | 119.6 | 0.0 | 13.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 257 | Lying | Sitting | nan | nan | 119.9 | 0.1 | 10.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 258 | Lying | Sitting | nan | nan | 120.0 | 0.0 | 2.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 259 | Lying | Sitting | nan | nan | 119.7 | 0.1 | 8.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 260 | Lying | Sitting | nan | nan | 117.6 | 0.6 | 63.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 261 | Lying | Sitting | nan | nan | 116.9 | 0.2 | 20.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 262 | Lying | Sitting | nan | nan | 117.3 | 0.1 | 13.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 263 | Lying | Sitting | nan | nan | 117.6 | 0.0 | 7.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 264 | Lying | Sitting | nan | nan | 117.3 | 0.2 | 9.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 265 | Lying | Sitting | nan | nan | 116.9 | 0.1 | 10.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 266 | Lying | Sitting | nan | nan | 117.3 | 0.3 | 11.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 267 | Lying | Sitting | nan | nan | 117.3 | 0.1 | 1.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 268 | Lying | Sitting | nan | nan | 115.9 | 0.5 | 41.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 269 | Lying | Sitting | nan | nan | 117.2 | 0.2 | 37.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 270 | Lying | Sitting | nan | nan | 117.3 | 0.0 | 1.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 271 | Lying | Sitting | nan | nan | 117.5 | 0.1 | 8.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 272 | Lying | Sitting | nan | nan | 116.9 | 0.1 | 18.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 273 | Lying | Sitting | nan | nan | 116.7 | 0.5 | 5.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 274 | Lying | Sitting | nan | nan | 117.4 | 0.2 | 18.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 275 | Lying | Sitting | nan | nan | 117.1 | 0.2 | 7.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 276 | Lying | Sitting | nan | nan | 118.1 | 0.2 | 28.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 277 | Lying | Sitting | nan | nan | 118.1 | 0.0 | 1.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 278 | Lying | Sitting | nan | nan | 119.0 | 0.4 | 27.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 279 | Lying | Sitting | nan | nan | 118.9 | 0.2 | 1.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 280 | Lying | Sitting | nan | nan | 119.3 | 0.1 | 10.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 281 | Lying | Sitting | nan | nan | 118.3 | 0.3 | 30.5 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 282 | Lying | Sitting | nan | nan | 118.1 | 0.0 | 4.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 283 | Lying | Sitting | nan | nan | 117.4 | 0.2 | 19.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 284 | Lying | Sitting | nan | nan | 116.8 | 0.2 | 18.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 285 | Lying | Sitting | nan | nan | 116.8 | 0.1 | 0.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 286 | Lying | Sitting | nan | nan | 116.9 | 0.0 | 2.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 287 | Lying | Sitting | nan | nan | 116.6 | 0.1 | 8.5 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 288 | Lying | Sitting | nan | nan | 115.8 | 0.3 | 23.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 289 | Lying | Sitting | nan | nan | 117.6 | 0.7 | 52.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 290 | Lying | Sitting | nan | nan | 116.7 | 0.3 | 26.5 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 291 | Lying | Sitting | nan | nan | 117.8 | 0.4 | 31.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 292 | Lying | Sitting | nan | nan | 117.3 | 0.1 | 13.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 293 | Lying | Sitting | nan | nan | 118.6 | 0.3 | 37.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 294 | Lying | Sitting | nan | nan | 118.4 | 0.2 | 5.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 295 | Lying | Sitting | nan | nan | 119.9 | 0.5 | 43.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 296 | Lying | Sitting | nan | nan | 118.8 | 0.1 | 32.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 297 | Lying | Sitting | nan | nan | 118.5 | 0.1 | 6.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 298 | Lying | Sitting | nan | nan | 116.5 | 0.9 | 59.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 299 | Lying | Sitting | nan | nan | 116.4 | 0.0 | 5.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 300 | Lying | Sitting | nan | nan | 118.0 | 0.4 | 47.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 301 | Lying | Sitting | nan | nan | 118.5 | 0.2 | 17.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 302 | Lying | Sitting | nan | nan | 119.5 | 0.4 | 29.5 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 303 | Lying | Sitting | nan | nan | 117.4 | 0.7 | 64.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 304 | Lying | Sitting | nan | nan | 115.9 | 0.4 | 43.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 305 | Lying | Sitting | nan | nan | 116.2 | 0.5 | 9.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 306 | Lying | Sitting | nan | nan | 115.4 | 0.3 | 23.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 307 | Lying | Sitting | nan | nan | 116.8 | 0.3 | 40.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 308 | Lying | Sitting | nan | nan | 117.5 | 0.1 | 19.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 309 | Lying | Sitting | nan | nan | 117.6 | 0.1 | 5.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 310 | Lying | Sitting | nan | nan | 117.7 | 0.1 | 2.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 311 | Lying | Sitting | nan | nan | 117.5 | 0.0 | 5.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 312 | Lying | Sitting | nan | nan | 117.6 | 0.0 | 3.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 313 | Lying | Sitting | nan | nan | 116.4 | 0.4 | 38.2 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 314 | Lying | Sitting | nan | nan | 116.0 | 0.0 | 10.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 315 | Lying | Sitting | nan | nan | 116.0 | 0.1 | 0.1 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 316 | Lying | Sitting | nan | nan | 116.2 | 0.1 | 4.7 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 317 | Lying | Sitting | nan | nan | 117.1 | 0.4 | 26.6 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 318 | Lying | Sitting | nan | nan | 117.2 | 0.2 | 4.3 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 319 | Lying | Sitting | nan | nan | 117.4 | 0.1 | 4.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 320 | Lying | Sitting | nan | nan | 117.7 | 0.0 | 8.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 321 | Lying | Sitting | nan | nan | 117.6 | 0.1 | 0.9 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 322 | Lying | Sitting | nan | nan | 117.5 | 0.1 | 3.4 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 323 | Lying | Sitting | nan | nan | 117.5 | 0.1 | 2.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 324 | Lying | Sitting | nan | nan | 118.4 | 0.2 | 29.0 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 325 | Lying | Sitting | nan | nan | 118.7 | 0.2 | 7.8 | 0.4 | 0.7 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 415 | Sitting | Standing | nan | nan | 7.2 | 0.0 | 11.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 416 | Sitting | Standing | nan | nan | 7.2 | 0.0 | 0.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 417 | Sitting | Standing | nan | nan | 7.1 | 0.1 | 4.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 418 | Sitting | Standing | nan | nan | 7.1 | 0.1 | 0.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 419 | Sitting | Standing | nan | nan | 7.8 | 0.0 | 22.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 420 | Sitting | Standing | nan | nan | 7.9 | 0.0 | 2.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 421 | Sitting | Standing | nan | nan | 7.9 | 0.1 | 0.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 422 | Sitting | Standing | nan | nan | 7.7 | 0.1 | 6.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 423 | Sitting | Standing | nan | nan | 7.7 | 0.1 | 1.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 424 | Sitting | Standing | nan | nan | 7.5 | 0.0 | 7.8 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 425 | Sitting | Standing | nan | nan | 7.5 | 0.0 | 1.5 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 426 | Sitting | Standing | nan | nan | 7.5 | 0.1 | 0.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 427 | Sitting | Standing | nan | nan | 7.7 | 0.0 | 4.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 428 | Sitting | Standing | nan | nan | 7.6 | 0.2 | 1.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 429 | Sitting | Standing | nan | nan | 7.5 | 0.1 | 3.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 430 | Sitting | Standing | nan | nan | 7.4 | 0.0 | 3.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 431 | Sitting | Standing | nan | nan | 7.3 | 0.1 | 1.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 432 | Sitting | Standing | nan | nan | 6.9 | 0.1 | 14.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 433 | Sitting | Standing | nan | nan | 7.1 | 0.1 | 6.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 434 | Sitting | Standing | nan | nan | 7.0 | 0.0 | 2.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 435 | Sitting | Standing | nan | nan | 6.9 | 0.0 | 1.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 436 | Sitting | Standing | nan | nan | 6.9 | 0.1 | 0.4 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 437 | Sitting | Standing | nan | nan | 6.7 | 0.0 | 7.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 438 | Sitting | Standing | nan | nan | 6.5 | 0.1 | 4.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 439 | Sitting | Standing | nan | nan | 6.4 | 0.0 | 5.1 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 440 | Sitting | Standing | nan | nan | 6.3 | 0.0 | 1.7 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 441 | Sitting | Standing | nan | nan | 6.3 | 0.0 | 1.2 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 442 | Sitting | Standing | nan | nan | 6.2 | 0.0 | 0.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 443 | Sitting | Standing | nan | nan | 6.2 | 0.1 | 1.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 444 | Sitting | Standing | nan | nan | 6.0 | 0.1 | 6.5 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 445 | Sitting | Standing | nan | nan | 5.8 | 0.0 | 4.3 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 446 | Sitting | Standing | nan | nan | 5.8 | 0.0 | 0.7 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 447 | Sitting | Standing | nan | nan | 5.8 | 0.0 | 0.5 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 448 | Sitting | Standing | nan | nan | 6.0 | 0.0 | 5.7 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 449 | Sitting | Standing | nan | nan | 5.8 | 0.1 | 6.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 450 | Sitting | Standing | nan | nan | 5.8 | 0.0 | 0.6 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 451 | Sitting | Standing | nan | nan | 5.8 | 0.0 | 0.9 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 452 | Sitting | Standing | nan | nan | 5.7 | 0.0 | 2.3 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 453 | Sitting | Standing | nan | nan | 5.6 | 0.3 | 4.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 454 | Sitting | Standing | nan | nan | 5.1 | 0.1 | 15.0 | 0.6 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 455 | Sitting | Standing | nan | nan | 4.3 | 0.1 | 22.4 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 456 | Sitting | Standing | nan | nan | 3.9 | 0.1 | 11.6 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 457 | Sitting | Standing | nan | nan | 3.6 | 0.1 | 9.0 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |
| 458 | Sitting | Standing | nan | nan | 3.6 | 0.0 | 0.7 | 0.7 | 0.7 | 0.2 | T | F | Standing|Standing|Standing|Standing|Standing |

---

## Sitting_Lying_FewLandmarks (**posture<90%, false negative**)

**Posture accuracy:** 29.7%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 39.0%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 14 | 0 | 0 | 0 |
| **Sitting** | 50 | 32 | 0 | 0 |
| **Lying** | 0 | 59 | 0 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 59 | Sitting | Standing | nan | nan | 5.7 | 0.1 | 12.5 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 60 | Sitting | Standing | nan | nan | 6.4 | 0.0 | 19.7 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 61 | Sitting | Standing | nan | nan | 6.9 | 0.1 | 17.1 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 62 | Sitting | Standing | nan | nan | 7.8 | 0.1 | 25.1 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 63 | Sitting | Standing | nan | nan | 8.7 | 0.1 | 25.4 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 64 | Sitting | Standing | nan | nan | 9.2 | 0.1 | 17.3 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 65 | Sitting | Standing | nan | nan | 9.7 | 0.0 | 12.9 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 66 | Sitting | Standing | nan | nan | 9.7 | 0.1 | 0.6 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 67 | Sitting | Standing | nan | nan | 10.0 | 0.2 | 9.5 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 68 | Sitting | Standing | nan | nan | 10.1 | 0.1 | 3.5 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 69 | Sitting | Standing | nan | nan | 10.5 | 0.1 | 12.1 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 70 | Sitting | Standing | nan | 155.7 | 10.6 | 0.2 | 2.7 | 0.8 | 1.2 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 71 | Sitting | Standing | nan | 153.9 | 10.8 | 0.3 | 5.3 | 0.8 | 1.2 | 0.2 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 72 | Sitting | Standing | nan | 153.6 | 11.0 | 0.2 | 5.7 | 0.8 | 1.2 | 0.2 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 73 | Sitting | Standing | nan | 149.3 | 10.9 | 0.1 | 2.7 | 0.8 | 1.2 | 0.2 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 94 | Sitting | Standing | nan | nan | 7.6 | 0.0 | 4.3 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Sitting | Standing | nan | nan | 7.4 | 0.1 | 4.7 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Sitting | Standing | nan | nan | 7.3 | 0.0 | 2.7 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Sitting | Standing | nan | nan | 7.3 | 0.2 | 1.5 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Sitting | Standing | nan | nan | 7.3 | 0.0 | 0.7 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Sitting | Standing | nan | nan | 7.3 | 0.1 | 0.2 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Sitting | Standing | nan | nan | 7.3 | 0.0 | 0.2 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 101 | Sitting | Standing | nan | nan | 7.2 | 0.0 | 0.8 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 102 | Sitting | Standing | nan | nan | 7.2 | 0.1 | 2.4 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 103 | Sitting | Standing | nan | nan | 7.2 | 0.2 | 0.6 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 104 | Sitting | Standing | nan | nan | 7.2 | 0.1 | 0.2 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 105 | Sitting | Standing | nan | nan | 7.1 | 0.0 | 1.8 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 106 | Sitting | Standing | nan | nan | 7.1 | 0.1 | 0.5 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 107 | Sitting | Standing | nan | nan | 7.1 | 0.0 | 0.7 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 108 | Sitting | Standing | nan | nan | 7.2 | 0.2 | 1.3 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 109 | Sitting | Standing | nan | nan | 7.2 | 0.1 | 1.9 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 110 | Sitting | Standing | nan | nan | 7.3 | 0.0 | 3.3 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 111 | Sitting | Standing | nan | nan | 7.6 | 0.0 | 7.7 | 0.7 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 177 | Lying | Sitting | nan | 166.2 | 56.1 | 0.1 | 5.3 | 0.7 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 178 | Lying | Sitting | nan | 166.4 | 56.4 | 0.1 | 7.6 | 0.7 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 179 | Lying | Sitting | nan | 164.7 | 56.3 | 0.2 | 2.2 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 180 | Lying | Sitting | nan | 163.5 | 57.0 | 0.0 | 21.5 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 181 | Lying | Sitting | nan | 166.2 | 56.5 | 0.2 | 16.6 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 182 | Lying | Sitting | nan | 165.9 | 55.7 | 0.7 | 21.4 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 183 | Lying | Sitting | nan | 166.3 | 58.4 | 0.7 | 78.1 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 184 | Lying | Sitting | nan | 166.8 | 58.0 | 0.4 | 10.9 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 185 | Lying | Sitting | nan | 169.1 | 58.5 | 0.4 | 13.0 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 186 | Lying | Sitting | nan | 169.9 | 58.6 | 0.3 | 5.1 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 187 | Lying | Sitting | nan | 170.1 | 56.6 | 0.3 | 61.2 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 188 | Lying | Sitting | nan | 168.2 | 55.8 | 0.1 | 22.7 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 189 | Lying | Sitting | nan | 166.6 | 54.3 | 0.5 | 43.2 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 190 | Lying | Sitting | nan | 170.5 | 55.3 | 0.1 | 28.9 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 191 | Lying | Sitting | nan | 170.8 | 55.5 | 0.0 | 6.5 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 192 | Lying | Sitting | nan | 169.5 | 56.2 | 0.2 | 20.0 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 193 | Lying | Sitting | nan | 169.2 | 56.4 | 0.1 | 6.3 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 194 | Lying | Sitting | nan | 169.5 | 55.1 | 0.2 | 39.9 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 195 | Lying | Sitting | nan | 169.4 | 55.1 | 0.1 | 1.7 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 196 | Lying | Sitting | nan | 169.9 | 54.5 | 0.1 | 17.4 | 0.6 | 1.2 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 197 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 198 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Unknown|Unknown |
| 199 | Lying | Sitting | nan | 150.0 | 66.1 | 1.2 | 113.8 | 0.4 | 1.2 | 0.2 | F | F | Sitting|Sitting|Unknown|Unknown|Sitting |
| 200 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Sitting|Unknown |
| 201 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Unknown|Unknown |
| 202 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Unknown|Unknown |
| 203 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 204 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 205 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 206 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 207 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 208 | Lying | Sitting | nan | nan | 66.5 | 0.1 | 1.3 | 0.3 | 1.2 | 0.2 | T | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 209 | Lying | Sitting | nan | nan | 60.3 | 0.9 | 182.4 | 0.3 | 1.2 | 0.2 | T | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 210 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Sitting|Unknown |
| 211 | Lying | Sitting | nan | nan | 64.4 | 0.9 | 59.9 | 0.3 | 1.2 | 0.2 | T | F | Unknown|Sitting|Sitting|Unknown|Sitting |
| 212 | Lying | Sitting | nan | nan | 60.9 | 1.2 | 102.7 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 213 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Sitting|Sitting|Unknown |
| 214 | Lying | Sitting | nan | nan | 65.7 | 0.7 | 71.5 | 0.3 | 1.2 | 0.2 | T | F | Unknown|Sitting|Sitting|Unknown|Sitting |
| 215 | Lying | Sitting | nan | nan | 62.6 | 1.3 | 92.8 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 216 | Lying | Sitting | nan | nan | 58.3 | 0.9 | 124.6 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 217 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Sitting|Sitting|Unknown |
| 218 | Lying | Sitting | nan | nan | 63.1 | 0.4 | 69.9 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 219 | Lying | Sitting | nan | nan | 60.6 | 0.7 | 74.7 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 220 | Lying | Sitting | nan | nan | 56.8 | 0.5 | 111.5 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 221 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Sitting|Sitting|Unknown |
| 222 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Unknown|Unknown |
| 223 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Unknown|Unknown |
| 224 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 225 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 226 | Lying | Sitting | nan | nan | 65.5 | 0.3 | 42.9 | 0.3 | 1.2 | 0.2 | T | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 227 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Sitting|Unknown |
| 228 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Unknown|Unknown |
| 229 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Unknown|Unknown |
| 230 | Lying | Sitting | nan | nan | 64.3 | 0.1 | 8.8 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Unknown|Unknown|Unknown|Sitting |
| 231 | Lying | Sitting | nan | nan | 60.8 | 0.9 | 102.3 | 0.3 | 1.2 | 0.2 | T | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 232 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Sitting|Unknown |
| 233 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Sitting|Unknown|Unknown |
| 234 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Unknown|Unknown |
| 235 | Lying | Sitting | nan | nan | 67.4 | 0.6 | 48.6 | 0.3 | 1.2 | 0.2 | T | F | Sitting|Unknown|Unknown|Unknown|Sitting |
| 325 | Sitting | Standing | nan | nan | 3.6 | 0.0 | 0.8 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 326 | Sitting | Standing | nan | nan | 3.6 | 0.0 | 0.7 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 327 | Sitting | Standing | nan | nan | 3.6 | 0.0 | 1.0 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 328 | Sitting | Standing | nan | nan | 3.6 | 0.0 | 0.1 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 329 | Sitting | Standing | nan | nan | 3.5 | 0.0 | 2.3 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 330 | Sitting | Standing | nan | nan | 3.5 | 0.0 | 0.4 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 331 | Sitting | Standing | nan | nan | 3.5 | 0.0 | 0.6 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 332 | Sitting | Standing | nan | nan | 3.5 | 0.0 | 0.2 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 333 | Sitting | Standing | nan | nan | 3.3 | 0.1 | 6.1 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 334 | Sitting | Standing | nan | nan | 3.3 | 0.0 | 0.6 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 335 | Sitting | Standing | nan | nan | 3.3 | 0.0 | 0.4 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 336 | Sitting | Standing | nan | nan | 3.4 | 0.1 | 3.6 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 337 | Sitting | Standing | nan | nan | 3.8 | 0.1 | 9.6 | 0.6 | 1.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 338 | Sitting | Standing | nan | 144.0 | 4.2 | 0.1 | 12.9 | 0.7 | 1.2 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 339 | Sitting | Standing | nan | 143.9 | 4.3 | 0.0 | 4.2 | 0.7 | 1.2 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 340 | Sitting | Standing | nan | 143.1 | 4.4 | 0.0 | 1.2 | 0.7 | 1.2 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 341 | Sitting | Standing | nan | 142.3 | 4.3 | 0.1 | 2.6 | 0.7 | 1.2 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |

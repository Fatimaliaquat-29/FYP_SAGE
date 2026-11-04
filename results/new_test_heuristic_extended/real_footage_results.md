# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| Forward_fall | 92.6% | TP (latency 30 frames) |  |

---

## Backward_fall (**posture<90%, false negative**)

**Posture accuracy:** 29.5%

**Per-class accuracy:**

- Standing: 65.7%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 23 | 0 | 0 | 12 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 28 | 0 | 0 | 15 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | 170.9 | 171.8 | 2.7 | 0.0 | 0.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing |
| 3 | Standing | Unknown | 169.8 | 172.5 | 3.3 | 0.3 | 20.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing |
| 4 | Standing | Unknown | 170.6 | 172.7 | 2.7 | 0.1 | 19.7 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing |
| 5 | Standing | Unknown | 171.4 | 170.3 | 2.8 | 0.3 | 2.8 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 29 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 30 | Standing | Unknown | 170.5 | 172.9 | 4.9 | 0.2 | 15.7 | 0.2 | 0.2 | 0.3 | F | F | Standing|Standing|Standing|Unknown|Standing |
| 31 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Standing|Unknown |
| 32 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Standing|Unknown|Unknown |
| 33 | Standing | Unknown | 172.3 | 172.8 | 6.9 | 0.2 | 19.7 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Unknown|Unknown|Standing |
| 34 | Standing | Unknown | 173.9 | 171.6 | 7.8 | 0.4 | 28.9 | 0.2 | 0.2 | 0.3 | F | F | Standing|Unknown|Unknown|Standing|Standing |
| 35 | Standing | Unknown | 170.2 | 169.6 | 9.2 | 0.7 | 41.9 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 69 | Lying | Standing | 149.9 | 150.1 | 1.8 | 0.6 | 25.9 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 70 | Lying | Standing | 129.7 | 144.9 | 1.3 | 1.1 | 14.5 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 71 | Lying | Standing | 126.0 | 143.7 | 0.8 | 0.9 | 13.5 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 72 | Lying | Standing | 155.7 | 149.4 | 2.1 | 1.6 | 37.1 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Standing |
| 73 | Lying | Standing | 152.7 | 154.4 | 1.5 | 0.2 | 16.1 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Standing|Standing |
| 74 | Lying | Standing | 160.1 | 157.2 | 2.0 | 0.2 | 14.4 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 75 | Lying | Standing | 160.0 | 158.8 | 1.6 | 0.3 | 12.7 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 76 | Lying | Standing | nan | 152.1 | 0.9 | 0.4 | 20.2 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 77 | Lying | Standing | 169.5 | 161.6 | 2.4 | 1.0 | 44.9 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 78 | Lying | Standing | 170.0 | 162.6 | 2.7 | 0.9 | 8.7 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 79 | Lying | Standing | nan | 162.1 | 4.8 | 0.7 | 64.2 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 80 | Lying | Standing | 164.2 | 161.3 | 4.3 | 1.0 | 16.0 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 81 | Lying | Standing | 167.6 | 166.3 | 5.5 | 0.3 | 36.9 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 82 | Lying | Standing | 167.5 | 168.1 | 4.0 | 1.4 | 45.3 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 83 | Lying | Standing | 173.1 | 169.8 | 6.9 | 0.2 | 86.0 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Lying | Standing | 162.6 | 164.5 | 4.3 | 0.8 | 77.1 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Lying | Standing | 147.7 | 153.9 | 5.2 | 1.2 | 27.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Lying | Standing | 162.4 | 165.0 | 5.9 | 1.4 | 18.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Lying | Standing | 156.7 | 164.2 | 4.8 | 0.8 | 31.4 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Lying | Standing | 154.6 | 162.2 | 2.5 | 0.2 | 69.8 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Lying | Standing | 161.8 | 162.8 | 3.5 | 0.6 | 29.9 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Lying | Standing | 163.9 | 163.8 | 5.1 | 0.4 | 46.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Lying | Standing | 172.5 | 171.9 | 6.2 | 0.3 | 35.4 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Lying | Standing | 161.5 | 163.4 | 8.5 | 0.5 | 67.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Lying | Standing | 162.2 | 163.6 | 6.1 | 0.3 | 70.3 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Lying | Standing | 177.5 | 163.3 | 11.3 | 0.5 | 154.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Lying | Standing | 178.4 | 172.0 | 8.7 | 0.9 | 79.5 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Lying | Standing | 173.1 | 171.0 | 15.4 | 0.4 | 202.1 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 98 | Lying | Unknown | 172.7 | 169.4 | 7.8 | 0.2 | 113.9 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Unknown|Standing |
| 99 | Lying | Unknown | 171.4 | 169.7 | 13.0 | 0.5 | 154.6 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Unknown|Standing|Standing |
| 100 | Lying | Unknown | 173.4 | 165.9 | 15.5 | 0.3 | 76.9 | 0.2 | 0.3 | 0.1 | F | F | Standing|Unknown|Standing|Standing|Standing |
| 101 | Lying | Unknown | 168.8 | 169.9 | 2.1 | 1.2 | 402.9 | 0.3 | 0.3 | 0.1 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 102 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 103 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 104 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 105 | Lying | Unknown | 178.3 | 167.5 | 8.4 | 0.2 | 47.3 | 0.2 | 0.3 | 0.1 | F | F | Standing|Unknown|Unknown|Unknown|Standing |
| 106 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 107 | Lying | Unknown | 172.3 | 175.8 | 6.3 | 0.6 | 31.9 | 0.2 | 0.3 | 0.1 | F | F | Unknown|Unknown|Standing|Unknown|Standing |
| 108 | Lying | Unknown | 169.9 | 171.7 | 4.6 | 0.8 | 48.8 | 0.3 | 0.3 | 0.1 | F | F | Unknown|Standing|Unknown|Standing|Standing |
| 109 | Lying | Unknown | 173.2 | 179.0 | 6.8 | 1.0 | 65.8 | 0.2 | 0.3 | 0.1 | F | F | Standing|Unknown|Standing|Standing|Standing |
| 110 | Lying | Unknown | 171.0 | 169.2 | 16.3 | 0.6 | 285.1 | 0.2 | 0.3 | 0.1 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 111 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |

---

## Chair_fall (**posture<90%**)

**Posture accuracy:** 21.5%

**Per-class accuracy:**

- Standing: nan%
- Sitting: 0.0%
- Lying: 26.6%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 41 |
| **Lying** | 69 | 49 | 46 | 9 |

**Fall detection:** TP (latency 114 frames)

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
| 40 | Sitting | Unknown | 137.4 | 119.6 | 15.2 | 0.0 | 0.0 | 0.3 | 0.3 | 0.2 | F | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 41 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Sitting|Unknown |
| 78 | Lying | Standing | 167.8 | 162.8 | 10.1 | 0.6 | 21.3 | 0.3 | 0.5 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 79 | Lying | Standing | 177.0 | 166.7 | 10.5 | 0.6 | 11.8 | 0.4 | 0.5 | 0.1 | F | F | Standing|Standing|Standing|Standing|Standing |
| 80 | Lying | Standing | 168.7 | 165.1 | 9.3 | 0.9 | 37.2 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 81 | Lying | Standing | 163.4 | 165.3 | 10.9 | 0.6 | 49.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 82 | Lying | Standing | 178.4 | 171.1 | 9.9 | 0.7 | 30.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 83 | Lying | Standing | 176.1 | 173.0 | 8.1 | 1.1 | 54.0 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Lying | Standing | 171.8 | 167.3 | 11.7 | 1.2 | 107.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Lying | Standing | 171.8 | 172.5 | 12.1 | 0.6 | 11.1 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Lying | Standing | 174.8 | 168.4 | 12.5 | 0.3 | 12.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Lying | Standing | 171.5 | 162.6 | 16.1 | 0.3 | 106.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Lying | Standing | 167.0 | 155.3 | 20.7 | 1.5 | 138.8 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Lying | Standing | 163.9 | 143.6 | 24.5 | 0.1 | 113.2 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Lying | Standing | 168.3 | 160.3 | 17.7 | 1.1 | 204.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Lying | Standing | 165.1 | 159.8 | 15.8 | 0.8 | 56.6 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Lying | Standing | 165.5 | 156.8 | 18.4 | 0.7 | 77.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Lying | Standing | 166.6 | 164.9 | 14.6 | 0.7 | 113.8 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Lying | Standing | 168.7 | 143.1 | 25.8 | 2.2 | 335.0 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Lying | Standing | 173.6 | 149.1 | 20.5 | 1.4 | 158.2 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Lying | Standing | 166.5 | 157.9 | 16.2 | 0.5 | 127.8 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Lying | Standing | 149.4 | 156.0 | 16.0 | 0.5 | 6.1 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Lying | Standing | 146.4 | 158.1 | 12.9 | 0.1 | 93.0 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Lying | Standing | 158.1 | 168.4 | 11.6 | 0.6 | 38.0 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Lying | Standing | 146.5 | 157.0 | 15.2 | 0.8 | 108.6 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 101 | Lying | Standing | 149.4 | 167.7 | 6.5 | 1.5 | 262.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 102 | Lying | Standing | 147.4 | 164.6 | 3.8 | 0.3 | 78.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 103 | Lying | Standing | 162.5 | 169.4 | 0.4 | 0.5 | 101.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 104 | Lying | Standing | 157.7 | 169.1 | 3.7 | 1.3 | 98.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 105 | Lying | Standing | 164.6 | 166.3 | 4.4 | 0.3 | 20.6 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 106 | Lying | Standing | 172.9 | 164.4 | 4.9 | 0.3 | 13.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 107 | Lying | Standing | 170.6 | 165.7 | 6.1 | 0.6 | 36.0 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 108 | Lying | Standing | 173.6 | 166.7 | 5.0 | 0.2 | 33.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 109 | Lying | Standing | 171.9 | 165.4 | 7.3 | 0.3 | 70.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 110 | Lying | Standing | 166.8 | 163.6 | 10.0 | 0.4 | 79.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 111 | Lying | Standing | 165.3 | 166.2 | 10.6 | 0.3 | 17.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 112 | Lying | Standing | 169.3 | 165.5 | 10.3 | 0.4 | 9.1 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 113 | Lying | Standing | 164.6 | 165.0 | 12.1 | 0.2 | 54.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 114 | Lying | Standing | 167.0 | 164.8 | 10.9 | 0.7 | 36.2 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 115 | Lying | Standing | 166.1 | 164.3 | 12.8 | 0.3 | 55.4 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 116 | Lying | Standing | 168.9 | 167.0 | 13.1 | 0.3 | 9.1 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 117 | Lying | Standing | 166.1 | 167.7 | 14.3 | 0.7 | 36.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 118 | Lying | Standing | 169.0 | 167.5 | 12.6 | 0.6 | 50.2 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 119 | Lying | Standing | 168.9 | 167.6 | 15.0 | 0.5 | 70.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 120 | Lying | Standing | 166.3 | 165.8 | 15.2 | 0.2 | 7.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Lying | Standing | 172.5 | 164.3 | 17.7 | 0.3 | 73.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Lying | Standing | 167.4 | 166.3 | 17.0 | 0.5 | 20.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Lying | Standing | 176.1 | 163.4 | 18.2 | 0.2 | 37.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Lying | Standing | 173.0 | 163.4 | 17.6 | 0.3 | 18.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Lying | Standing | 178.5 | 163.6 | 17.4 | 0.1 | 5.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Lying | Standing | 172.6 | 162.4 | 17.7 | 0.1 | 9.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Lying | Standing | 172.7 | 162.6 | 16.9 | 0.2 | 24.2 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Lying | Standing | 171.8 | 162.3 | 17.9 | 0.4 | 29.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Lying | Standing | 172.6 | 161.8 | 16.8 | 0.0 | 34.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Lying | Standing | 171.3 | 163.8 | 15.8 | 0.0 | 30.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Lying | Standing | 173.6 | 162.1 | 17.0 | 0.6 | 35.8 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Lying | Standing | 173.2 | 163.0 | 14.2 | 0.2 | 82.6 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Lying | Standing | 174.1 | 162.4 | 12.9 | 0.3 | 37.2 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Lying | Standing | 174.8 | 160.8 | 13.3 | 0.4 | 11.4 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Lying | Standing | 173.1 | 162.3 | 13.7 | 0.5 | 10.3 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Lying | Standing | 177.2 | 160.4 | 12.6 | 0.3 | 32.6 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Lying | Standing | 173.1 | 163.3 | 10.1 | 0.2 | 72.7 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Lying | Standing | 175.1 | 158.6 | 11.7 | 0.9 | 47.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Lying | Standing | 173.9 | 157.1 | 11.8 | 0.1 | 2.0 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Lying | Standing | 177.5 | 157.3 | 9.1 | 0.5 | 80.5 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Lying | Standing | 175.8 | 157.4 | 9.2 | 0.5 | 2.4 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Lying | Standing | 177.0 | 155.5 | 9.0 | 0.4 | 4.8 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Lying | Standing | 175.5 | 157.4 | 9.5 | 1.2 | 13.9 | 0.3 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Lying | Standing | 175.4 | 154.6 | 9.6 | 0.3 | 3.0 | 0.2 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Lying | Standing | 173.5 | 148.3 | 11.5 | 0.3 | 55.4 | 0.2 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Lying | Standing | 163.7 | 144.2 | 11.3 | 1.1 | 4.3 | 0.2 | 0.5 | 0.2 | F | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 148 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 149 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 150 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 151 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 152 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 153 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 154 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 155 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 202 | Lying | Sitting | 136.8 | 145.4 | 6.1 | 2.9 | 158.8 | 0.2 | 0.5 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 203 | Lying | Sitting | 142.1 | 147.7 | 3.8 | 2.0 | 70.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 204 | Lying | Sitting | 126.6 | 142.5 | 0.4 | 3.2 | 100.9 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 205 | Lying | Sitting | 107.0 | 142.1 | 3.2 | 1.4 | 83.8 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 206 | Lying | Sitting | 135.6 | 131.1 | 0.7 | 0.6 | 74.8 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 207 | Lying | Sitting | 124.7 | 142.4 | 2.6 | 0.9 | 57.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 208 | Lying | Sitting | 108.4 | 142.6 | 1.5 | 0.2 | 34.6 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 209 | Lying | Sitting | 103.6 | 132.7 | 5.3 | 1.2 | 114.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 210 | Lying | Sitting | 111.7 | 122.4 | 1.0 | 3.3 | 128.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 211 | Lying | Sitting | 98.8 | 108.8 | 4.3 | 0.7 | 98.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 212 | Lying | Sitting | 90.6 | 102.6 | 8.1 | 1.0 | 112.2 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 213 | Lying | Sitting | 70.0 | 85.3 | 7.0 | 1.6 | 30.7 | 0.1 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 214 | Lying | Sitting | 50.4 | 61.6 | 8.9 | 1.8 | 54.7 | 0.1 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 215 | Lying | Sitting | 38.0 | 34.5 | 0.6 | 3.2 | 247.2 | 0.1 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 216 | Lying | Sitting | 24.4 | 32.2 | 1.9 | 2.5 | 40.2 | 0.1 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 217 | Lying | Sitting | 27.8 | 48.4 | 0.9 | 1.4 | 29.7 | 0.1 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 218 | Lying | Sitting | 34.8 | 56.2 | 9.0 | 3.8 | 241.3 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 219 | Lying | Sitting | 34.1 | 51.3 | 16.8 | 2.2 | 231.8 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 220 | Lying | Sitting | 47.2 | 61.4 | 24.3 | 1.9 | 226.4 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 221 | Lying | Sitting | 111.6 | 98.6 | 21.0 | 1.7 | 99.0 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 222 | Lying | Sitting | 60.3 | 74.3 | 7.7 | 2.9 | 398.5 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 223 | Lying | Sitting | 75.7 | 84.7 | 1.7 | 2.1 | 179.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 224 | Lying | Sitting | 85.6 | 84.4 | 4.6 | 1.0 | 86.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 225 | Lying | Sitting | 93.4 | 87.7 | 10.3 | 1.1 | 169.0 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 226 | Lying | Sitting | 97.9 | 93.6 | 0.1 | 2.5 | 303.0 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 227 | Lying | Sitting | 95.7 | 95.7 | 0.8 | 0.1 | 21.2 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 228 | Lying | Sitting | 102.4 | 99.7 | 0.1 | 0.2 | 22.9 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 229 | Lying | Sitting | 104.7 | 100.8 | 0.1 | 0.4 | 0.9 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 230 | Lying | Sitting | 106.3 | 101.8 | 1.1 | 0.6 | 31.3 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 231 | Lying | Sitting | 106.0 | 97.7 | 3.8 | 0.8 | 79.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 232 | Lying | Sitting | 111.3 | 100.3 | 2.4 | 0.4 | 40.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 233 | Lying | Sitting | 106.3 | 100.4 | 3.4 | 0.4 | 27.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 234 | Lying | Sitting | 102.5 | 102.4 | 4.1 | 0.7 | 22.3 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 235 | Lying | Sitting | 107.1 | 99.2 | 6.6 | 0.4 | 73.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 236 | Lying | Sitting | 102.4 | 87.3 | 8.3 | 0.6 | 52.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 237 | Lying | Sitting | 109.5 | 98.7 | 6.8 | 0.0 | 47.0 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 238 | Lying | Sitting | 116.3 | 100.0 | 7.5 | 0.2 | 21.9 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 239 | Lying | Sitting | 110.7 | 97.1 | 7.0 | 0.1 | 15.9 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 240 | Lying | Sitting | 106.4 | 99.6 | 4.9 | 0.5 | 60.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 241 | Lying | Sitting | 114.0 | 105.1 | 4.6 | 0.2 | 9.2 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 242 | Lying | Sitting | 119.0 | 112.1 | 3.6 | 0.3 | 32.5 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 243 | Lying | Sitting | 114.3 | 103.5 | 2.5 | 0.4 | 30.3 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 244 | Lying | Sitting | 109.2 | 102.9 | 4.0 | 0.4 | 44.5 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 245 | Lying | Sitting | 106.3 | 97.4 | 1.7 | 0.4 | 70.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 246 | Lying | Sitting | 108.7 | 100.8 | 3.8 | 0.4 | 63.5 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 247 | Lying | Sitting | 110.0 | 103.1 | 3.7 | 0.2 | 1.7 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 248 | Lying | Sitting | 114.6 | 105.7 | 3.5 | 0.3 | 7.1 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 249 | Lying | Sitting | 109.5 | 96.2 | 2.9 | 0.6 | 18.6 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 250 | Lying | Sitting | 112.6 | 99.4 | 2.9 | 0.3 | 0.8 | 0.2 | 0.5 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Fall_and_lie (**posture<90%**)

**Posture accuracy:** 54.4%

**Per-class accuracy:**

- Standing: 58.5%
- Sitting: nan%
- Lying: 53.8%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 24 | 0 | 0 | 17 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 2 | 149 | 126 |

**Fall detection:** TP (latency 8 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Standing | Unknown | 27.0 | 35.6 | 167.6 | 0.0 | 0.0 | 0.1 | 0.1 | 0.4 | F | F | Unknown|Unknown|Lying |
| 4 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Lying|Unknown |
| 5 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Lying|Unknown|Unknown |
| 6 | Standing | Unknown | 17.4 | 26.4 | 179.2 | 0.5 | 116.1 | 0.1 | 0.1 | 0.4 | F | F | Unknown|Lying|Unknown|Unknown|Lying |
| 7 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Unknown|Unknown|Lying|Unknown |
| 8 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Lying|Unknown|Unknown |
| 9 | Standing | Unknown | 176.8 | 165.6 | 0.5 | 4.6 | 720.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Lying|Unknown|Unknown|Standing |
| 10 | Standing | Unknown | 177.7 | 167.7 | 0.6 | 0.4 | 3.5 | 0.2 | 0.2 | 0.3 | F | F | Lying|Unknown|Unknown|Standing|Standing |
| 11 | Standing | Unknown | 179.1 | 170.4 | 0.5 | 0.3 | 4.5 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 12 | Standing | Unknown | 171.2 | 165.9 | 0.2 | 0.5 | 8.1 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 19 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 20 | Standing | Unknown | 175.0 | 169.3 | 0.2 | 0.1 | 8.4 | 0.2 | 0.2 | 0.3 | F | F | Standing|Standing|Standing|Unknown|Standing |
| 21 | Standing | Unknown | 173.3 | 169.5 | 0.4 | 0.1 | 7.6 | 0.2 | 0.2 | 0.3 | F | F | Standing|Standing|Unknown|Standing|Standing |
| 22 | Standing | Unknown | 173.9 | 172.8 | 1.8 | 0.4 | 39.7 | 0.2 | 0.2 | 0.3 | F | F | Standing|Unknown|Standing|Standing|Standing |
| 23 | Standing | Unknown | 176.0 | 168.2 | 0.2 | 0.4 | 47.1 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 143 | Lying | Sitting | 140.6 | 90.8 | 20.3 | 2.6 | 18.0 | 0.1 | 0.2 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 144 | Lying | Sitting | 36.0 | 89.9 | 27.0 | 1.4 | 200.2 | 0.1 | 0.2 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 145 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 146 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Unknown|Unknown |
| 147 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Unknown|Unknown |
| 148 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 149 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 150 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 151 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 152 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 153 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
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
| 265 | Lying | Unknown | 126.4 | 145.6 | 18.0 | 0.1 | 1.6 | 0.2 | 0.2 | 0.0 | F | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 266 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Sitting|Unknown |
| 267 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Unknown|Unknown |
| 268 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Unknown|Unknown |
| 269 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 270 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 271 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 272 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 273 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
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
| 285 | Lying | Unknown | nan | nan | 12.4 | 0.3 | 8.5 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 286 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 287 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 288 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 289 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 290 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 291 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 292 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 293 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 294 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 295 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 296 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 297 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 298 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 299 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 300 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 301 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 302 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 303 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 304 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 305 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 306 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 307 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 308 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 309 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 310 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 311 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 312 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 313 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 314 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 315 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 316 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 317 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 318 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 319 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 320 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 321 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 322 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 323 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 324 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 325 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 326 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 327 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 328 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 329 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 330 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 331 | Lying | Unknown | nan | nan | 13.9 | 0.0 | 1.0 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 332 | Lying | Unknown | nan | nan | 14.5 | 0.4 | 15.9 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 333 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Standing|Unknown |
| 334 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Standing|Unknown|Unknown |
| 335 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 336 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 337 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 338 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 339 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 340 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 341 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 342 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 343 | Lying | Unknown | nan | nan | 13.6 | 0.1 | 2.3 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 344 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 345 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 346 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 347 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 348 | Lying | Unknown | nan | nan | 20.9 | 0.4 | 43.8 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 349 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 350 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 351 | Lying | Unknown | nan | nan | 16.3 | 0.5 | 46.3 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Standing|Unknown|Unknown|Standing |
| 352 | Lying | Unknown | nan | 171.0 | 14.4 | 2.3 | 55.5 | 0.3 | 0.3 | -0.0 | F | F | Standing|Unknown|Unknown|Standing|Standing |
| 353 | Lying | Unknown | nan | nan | 9.8 | 1.8 | 139.5 | 0.3 | 0.3 | -0.0 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 354 | Lying | Unknown | nan | 173.6 | 16.9 | 1.8 | 212.6 | 0.3 | 0.3 | -0.0 | F | F | Unknown|Standing|Standing|Standing|Standing |

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

**Fall detection:** TP (latency 60 frames)

**Mismatched frames:**

_None_

---

## Occluded_fall (**posture<90%**)

**Posture accuracy:** 63.8%

**Per-class accuracy:**

- Standing: 0.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 50 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 88 | 0 |

**Fall detection:** TP (latency 57 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Sitting | 93.6 | 175.3 | 10.7 | 0.0 | 0.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting |
| 2 | Standing | Sitting | 89.0 | 175.6 | 7.9 | 1.0 | 85.7 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Sitting |
| 3 | Standing | Sitting | 89.4 | 172.5 | 10.2 | 0.2 | 68.6 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting |
| 4 | Standing | Sitting | 90.7 | 177.5 | 10.0 | 0.2 | 5.4 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting |
| 5 | Standing | Sitting | 93.4 | 172.3 | 8.6 | 0.4 | 41.7 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 6 | Standing | Sitting | 90.8 | 171.8 | 10.1 | 0.3 | 46.4 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 7 | Standing | Sitting | 94.5 | 175.6 | 9.4 | 0.1 | 20.9 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 8 | Standing | Sitting | 89.0 | 169.1 | 8.9 | 0.4 | 16.4 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 9 | Standing | Sitting | 101.5 | 175.3 | 7.6 | 0.3 | 38.2 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 10 | Standing | Sitting | 101.1 | 173.6 | 9.8 | 0.2 | 66.3 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 11 | Standing | Sitting | 92.0 | 176.2 | 7.0 | 0.1 | 84.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 12 | Standing | Sitting | 98.3 | 177.9 | 7.8 | 0.5 | 22.9 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 13 | Standing | Sitting | 94.1 | 175.4 | 4.9 | 0.8 | 87.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 14 | Standing | Sitting | 93.1 | 178.4 | 5.7 | 0.5 | 26.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 15 | Standing | Sitting | 94.6 | 175.7 | 5.5 | 0.1 | 7.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 16 | Standing | Sitting | 94.7 | 174.9 | 5.0 | 0.3 | 13.2 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 17 | Standing | Sitting | 100.3 | 173.0 | 6.4 | 0.4 | 41.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 18 | Standing | Sitting | 90.4 | 171.2 | 4.5 | 0.6 | 58.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 19 | Standing | Sitting | 88.1 | 171.3 | 3.6 | 0.1 | 25.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 20 | Standing | Sitting | 91.9 | 173.9 | 6.4 | 0.5 | 82.7 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 21 | Standing | Sitting | 93.0 | 175.4 | 6.8 | 0.6 | 10.4 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 22 | Standing | Sitting | 90.7 | 177.2 | 4.8 | 0.3 | 58.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 23 | Standing | Sitting | 86.6 | 175.1 | 4.6 | 0.3 | 5.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 24 | Standing | Sitting | 85.3 | 177.3 | 4.5 | 0.5 | 3.1 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 25 | Standing | Sitting | 97.9 | 170.4 | 7.4 | 0.8 | 87.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 26 | Standing | Sitting | 90.0 | 176.5 | 5.2 | 0.5 | 66.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 27 | Standing | Sitting | 94.1 | 176.3 | 5.5 | 0.4 | 8.3 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 28 | Standing | Sitting | 97.8 | 171.3 | 4.7 | 0.7 | 24.9 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 29 | Standing | Sitting | 99.6 | 172.2 | 5.1 | 0.4 | 12.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 30 | Standing | Sitting | 92.3 | 174.5 | 5.5 | 1.0 | 14.7 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 31 | Standing | Sitting | 105.5 | 175.1 | 2.9 | 1.4 | 78.9 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 32 | Standing | Sitting | 104.8 | 174.0 | 5.6 | 0.6 | 80.2 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 33 | Standing | Sitting | 113.1 | 178.9 | 1.8 | 0.5 | 113.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 34 | Standing | Sitting | 107.4 | 177.3 | 2.6 | 0.3 | 24.3 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 35 | Standing | Sitting | 112.8 | 172.1 | 2.8 | 0.2 | 5.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 36 | Standing | Sitting | 100.2 | 175.8 | 0.3 | 0.5 | 76.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 37 | Standing | Sitting | 108.2 | 171.6 | 1.9 | 1.2 | 48.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 38 | Standing | Sitting | 114.0 | 166.2 | 0.9 | 0.2 | 29.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 39 | Standing | Sitting | 112.6 | 175.6 | 1.2 | 0.1 | 9.2 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 40 | Standing | Sitting | 99.9 | 177.8 | 3.8 | 1.9 | 76.7 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 41 | Standing | Sitting | 99.8 | 176.3 | 3.4 | 1.0 | 10.7 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 42 | Standing | Sitting | 99.2 | 177.7 | 6.0 | 1.1 | 78.1 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 43 | Standing | Sitting | 130.5 | 173.3 | 7.2 | 1.9 | 34.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 44 | Standing | Sitting | 111.3 | 171.7 | 7.8 | 0.4 | 19.8 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 45 | Standing | Sitting | 117.0 | 178.4 | 7.5 | 0.7 | 9.8 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 46 | Standing | Sitting | 121.5 | 178.7 | 9.1 | 1.4 | 49.1 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 47 | Standing | Sitting | 116.5 | 170.1 | 12.3 | 0.5 | 95.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 48 | Standing | Sitting | 117.6 | 176.6 | 13.2 | 0.3 | 27.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 49 | Standing | Sitting | 117.2 | 171.4 | 11.2 | 1.4 | 60.1 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 50 | Standing | Sitting | 127.2 | 172.1 | 10.3 | 0.5 | 27.2 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |

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

**Fall detection:** TP (latency 66 frames)

**Mismatched frames:**

_None_

---

## Side_fall (**posture<90%**)

**Posture accuracy:** 77.2%

**Per-class accuracy:**

- Standing: 28.1%
- Sitting: nan%
- Lying: 93.7%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 9 | 0 | 0 | 23 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 89 | 6 |

**Fall detection:** TP (latency 73 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Standing | Unknown | 178.7 | 164.4 | 7.9 | 0.0 | 0.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing |
| 4 | Standing | Unknown | 176.2 | 162.5 | 8.0 | 0.2 | 3.7 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing |
| 5 | Standing | Unknown | 175.5 | 162.9 | 7.6 | 0.1 | 10.2 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 6 | Standing | Unknown | 177.9 | 163.3 | 7.0 | 0.1 | 19.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 12 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 13 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 14 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 15 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 16 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 17 | Standing | Unknown | 176.3 | 161.7 | 3.3 | 0.2 | 13.1 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 18 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Standing|Unknown |
| 19 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 20 | Standing | Unknown | 177.5 | 161.3 | 1.6 | 0.2 | 16.6 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Unknown|Unknown|Standing |
| 21 | Standing | Unknown | 178.4 | 163.1 | 1.9 | 0.5 | 9.9 | 0.2 | 0.2 | 0.3 | F | F | Standing|Unknown|Unknown|Standing|Standing |
| 22 | Standing | Unknown | 172.6 | 165.8 | 1.0 | 0.1 | 27.1 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 23 | Standing | Unknown | 174.0 | 165.2 | 2.0 | 0.5 | 27.8 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 24 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 25 | Standing | Unknown | 171.6 | 164.9 | 1.8 | 0.3 | 2.2 | 0.2 | 0.2 | 0.3 | F | F | Standing|Standing|Standing|Unknown|Standing |
| 26 | Standing | Unknown | 172.5 | 165.6 | 0.1 | 0.3 | 52.0 | 0.2 | 0.2 | 0.3 | F | F | Standing|Standing|Unknown|Standing|Standing |
| 27 | Standing | Unknown | 166.3 | 167.4 | 0.6 | 0.4 | 16.0 | 0.2 | 0.2 | 0.3 | F | F | Standing|Unknown|Standing|Standing|Standing |
| 28 | Standing | Unknown | 171.3 | 172.2 | 0.6 | 0.5 | 0.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 158 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 159 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 160 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 161 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 162 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 163 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |

---

## Slow_fall (**posture<90%**)

**Posture accuracy:** 71.7%

**Per-class accuracy:**

- Standing: 76.9%
- Sitting: nan%
- Lying: 67.5%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 50 | 0 | 13 | 2 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 6 | 54 | 20 |

**Fall detection:** TP (latency 50 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 43 | Standing | Lying | 165.8 | 149.8 | 61.7 | 13.0 | 546.7 | 0.1 | 0.2 | 0.4 | F | F | Standing|Lying|Sitting|Lying|Lying |
| 44 | Standing | Lying | 177.9 | 163.3 | 20.2 | 10.5 | 720.0 | 0.2 | 0.2 | 0.3 | F | F | Lying|Sitting|Lying|Lying|Standing |
| 45 | Standing | Lying | 167.8 | 159.1 | 23.2 | 0.7 | 91.4 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Lying|Lying|Standing|Standing |
| 46 | Standing | Lying | 158.5 | 117.7 | 50.3 | 6.4 | 720.0 | 0.2 | 0.2 | 0.3 | F | F | Lying|Lying|Standing|Standing|Lying |
| 47 | Standing | Lying | 152.2 | 108.7 | 59.0 | 2.0 | 260.0 | 0.2 | 0.2 | 0.3 | F | F | Lying|Standing|Standing|Lying|Lying |
| 48 | Standing | Lying | 146.6 | 107.4 | 61.3 | 1.0 | 69.6 | 0.2 | 0.2 | 0.3 | F | F | Standing|Standing|Lying|Lying|Lying |
| 49 | Standing | Lying | 170.0 | 162.9 | 20.1 | 8.7 | 720.0 | 0.2 | 0.2 | 0.3 | F | F | Standing|Lying|Lying|Lying|Standing |
| 50 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Standing|Unknown |
| 51 | Standing | Lying | 161.0 | 145.7 | 30.7 | 2.3 | 159.0 | 0.2 | 0.2 | 0.3 | F | F | Lying|Lying|Standing|Unknown|Standing |
| 52 | Standing | Lying | 172.0 | 169.9 | 15.9 | 5.3 | 443.8 | 0.2 | 0.2 | 0.3 | F | F | Lying|Standing|Unknown|Standing|Standing |
| 53 | Standing | Lying | 170.0 | 163.9 | 20.0 | 1.0 | 121.8 | 0.2 | 0.2 | 0.3 | F | F | Standing|Unknown|Standing|Standing|Standing |
| 54 | Standing | Lying | 172.6 | 167.3 | 13.5 | 0.9 | 194.8 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 63 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Sitting|Sitting|Unknown |
| 64 | Standing | Unknown | 71.6 | 120.0 | 63.6 | 6.2 | 513.8 | 0.1 | 0.2 | 0.3 | F | F | Standing|Sitting|Sitting|Unknown|Lying |
| 65 | Standing | Lying | 135.9 | 163.8 | 49.0 | 2.8 | 436.6 | 0.1 | 0.2 | 0.3 | F | F | Sitting|Sitting|Unknown|Lying|Lying |
| 180 | Lying | Sitting | 157.3 | 23.4 | 3.1 | 5.4 | 69.2 | 0.0 | 0.2 | 0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 181 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 182 | Lying | Unknown | 145.6 | 14.6 | 5.5 | 2.2 | 35.8 | 0.0 | 0.2 | 0.0 | F | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 183 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Sitting|Unknown |
| 184 | Lying | Unknown | 78.6 | 23.4 | 2.4 | 2.3 | 46.2 | 0.1 | 0.2 | 0.0 | F | F | Sitting|Unknown|Sitting|Unknown|Sitting |
| 185 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Sitting|Unknown |
| 186 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Sitting|Unknown|Unknown |
| 187 | Lying | Unknown | 62.3 | 25.6 | 12.6 | 3.9 | 102.4 | 0.1 | 0.2 | 0.0 | F | F | Unknown|Sitting|Unknown|Unknown|Sitting |
| 188 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Sitting|Unknown |
| 189 | Lying | Unknown | nan | 161.4 | 10.7 | 0.1 | 29.4 | 0.3 | 0.3 | 0.0 | F | F | Unknown|Unknown|Sitting|Unknown|Standing |
| 190 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Standing|Unknown |
| 191 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Standing|Unknown|Unknown |
| 192 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Standing|Unknown|Unknown|Unknown |
| 193 | Lying | Unknown | 35.6 | 40.2 | 12.1 | 1.2 | 10.4 | 0.1 | 0.2 | 0.0 | F | F | Standing|Unknown|Unknown|Unknown|Sitting |
| 194 | Lying | Unknown | 21.3 | 39.7 | 13.0 | 1.9 | 29.6 | 0.1 | 0.2 | 0.0 | F | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 195 | Lying | Unknown | 108.0 | 23.2 | 11.1 | 6.9 | 57.5 | 0.1 | 0.2 | 0.0 | F | F | Unknown|Unknown|Sitting|Sitting|Sitting |
| 196 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Sitting|Sitting|Unknown |
| 197 | Lying | Unknown | 1.1 | 48.6 | 11.7 | 3.0 | 9.3 | 0.1 | 0.2 | 0.0 | F | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 198 | Lying | Unknown | 35.1 | 61.4 | 9.0 | 1.9 | 81.3 | 0.1 | 0.2 | 0.0 | F | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 199 | Lying | Unknown | 24.0 | 64.4 | 9.2 | 3.3 | 5.2 | 0.1 | 0.2 | -0.0 | F | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 200 | Lying | Unknown | 45.7 | 17.5 | 7.6 | 6.5 | 49.3 | 0.1 | 0.2 | 0.0 | F | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 201 | Lying | Sitting | 50.7 | 21.5 | 8.6 | 5.2 | 30.2 | 0.1 | 0.2 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 202 | Lying | Sitting | nan | 158.7 | 11.8 | 2.0 | 95.6 | 0.3 | 0.3 | -0.0 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 203 | Lying | Sitting | 18.9 | 56.7 | 10.3 | 3.7 | 42.6 | 0.1 | 0.2 | -0.0 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 204 | Lying | Sitting | 67.3 | 24.1 | 11.2 | 4.6 | 27.2 | 0.1 | 0.2 | 0.0 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 205 | Lying | Sitting | nan | 132.5 | 12.2 | 2.2 | 28.2 | 0.2 | 0.2 | -0.0 | F | F | Sitting|Standing|Sitting|Sitting|Standing |

---

## Forward_fall

**Posture accuracy:** 92.6%

**Per-class accuracy:**

- Standing: 79.5%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 35 | 0 | 0 | 9 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 78 | 0 |

**Fall detection:** TP (latency 30 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 32 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 33 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 34 | Standing | Unknown | 156.2 | 156.3 | 8.2 | 0.2 | 67.3 | 0.2 | 0.2 | 0.3 | F | F | Standing|Standing|Unknown|Unknown|Standing |
| 35 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Standing|Unknown |
| 36 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Standing|Unknown|Unknown |
| 37 | Standing | Unknown | 177.2 | 168.5 | 8.6 | 0.9 | 3.2 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Unknown|Unknown|Standing |
| 38 | Standing | Unknown | 176.2 | 167.8 | 7.6 | 0.7 | 28.5 | 0.2 | 0.2 | 0.3 | F | F | Standing|Unknown|Unknown|Standing|Standing |
| 39 | Standing | Unknown | 174.9 | 167.2 | 10.3 | 1.7 | 80.4 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Standing|Standing|Standing |
| 40 | Standing | Unknown | 174.5 | 166.4 | 9.6 | 0.9 | 21.7 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |

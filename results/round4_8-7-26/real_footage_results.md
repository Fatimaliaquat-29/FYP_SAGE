# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| Bed_lie | 39.3% | TP (latency 0 frames) | **posture<90%** |
| Bed_lie_and_immediate_stand | 34.8% | FN | **posture<90%, false negative** |
| Bed_long_lie | 82.9% | FN | **posture<90%, false negative** |
| Bed_medium_pace_lie | 100.0% | TP (latency 48 frames) |  |
| Floor_lie | 63.7% | FP frames [77, 78, 79, 111, 112] | **posture<90%, false positive** |
| Floor_lie_and_immediate_stand | 30.6% | TP (latency 27 frames) | **posture<90%** |
| Floor_long_lie | 10.5% | TP (latency 9 frames) | **posture<90%** |
| Floor_medium_pace_lie | 80.0% | TP (latency 11 frames) | **posture<90%** |
| Floor_partly_lie_beside_bed | 7.2% | FN | **posture<90%, false negative** |
| Other_occluded_crouch | 59.9% | - | **posture<90%** |
| Other_occluded_stand | 100.0% | - |  |
| Other_sit_desk | 80.1% | - | **posture<90%** |
| Other_walk_out_and_back | 56.6% | FP frames [170, 171, 172, 173, 174] | **posture<90%, false positive** |
| Sofa_lie | 57.9% | FN | **posture<90%, false negative** |
| Sofa_lie_and_immediate_stand | 43.0% | FN | **posture<90%, false negative** |
| Sofa_long_lie | 100.0% | TP (latency 79 frames) |  |
| Sofa_medium_pace_lie | 44.6% | FN | **posture<90%, false negative** |

---

## Bed_lie (**posture<90%**)

**Posture accuracy:** 39.3%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 7.5%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 59 | 0 | 0 | 0 |
| **Sitting** | 55 | 9 | 56 | 0 |
| **Lying** | 0 | 0 | 4 | 0 |

**Fall detection:** TP (latency 0 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 75 | Sitting | Lying | nan | nan | 40.9 | 0.7 | 58.0 | 0.2 | 0.2 | 0.1 | T | F | Lying|Lying|Lying|Sitting|Sitting |
| 76 | Sitting | Lying | nan | nan | 38.0 | 0.6 | 89.5 | 0.2 | 0.2 | 0.1 | T | F | Lying|Lying|Sitting|Sitting|Sitting |
| 77 | Sitting | Lying | nan | nan | 34.9 | 0.5 | 90.3 | 0.2 | 0.2 | 0.1 | T | F | Lying|Sitting|Sitting|Sitting|Sitting |
| 83 | Sitting | Standing | nan | nan | 9.7 | 0.2 | 128.0 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 84 | Sitting | Standing | nan | nan | 5.6 | 0.3 | 124.6 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 85 | Sitting | Standing | nan | nan | 2.9 | 0.1 | 80.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 86 | Sitting | Standing | nan | nan | 1.0 | 0.3 | 58.0 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 87 | Sitting | Standing | nan | nan | 4.0 | 0.2 | 90.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 88 | Sitting | Standing | nan | nan | 6.7 | 0.1 | 82.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 89 | Sitting | Standing | nan | nan | 8.2 | 0.0 | 43.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 90 | Sitting | Standing | nan | nan | 8.5 | 0.2 | 8.2 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 91 | Sitting | Standing | nan | nan | 10.8 | 0.1 | 68.8 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 92 | Sitting | Standing | nan | nan | 12.2 | 0.2 | 43.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 93 | Sitting | Standing | nan | nan | 13.6 | 0.2 | 40.4 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 94 | Sitting | Standing | nan | nan | 14.4 | 0.0 | 23.4 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 95 | Sitting | Standing | nan | nan | 14.3 | 0.1 | 2.4 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 96 | Sitting | Standing | nan | nan | 15.3 | 0.0 | 29.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 97 | Sitting | Standing | nan | nan | 15.9 | 0.1 | 18.2 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 98 | Sitting | Standing | nan | nan | 16.5 | 0.0 | 19.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 99 | Sitting | Standing | nan | nan | 16.4 | 0.0 | 3.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 100 | Sitting | Standing | nan | nan | 16.5 | 0.1 | 2.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 101 | Sitting | Standing | nan | nan | 16.9 | 0.0 | 12.0 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 102 | Sitting | Standing | nan | nan | 16.9 | 0.0 | 1.4 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 103 | Sitting | Standing | nan | nan | 16.9 | 0.1 | 2.1 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 104 | Sitting | Standing | nan | nan | 17.3 | 0.1 | 9.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 105 | Sitting | Standing | nan | nan | 17.1 | 0.1 | 3.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 106 | Sitting | Standing | nan | nan | 16.8 | 0.0 | 9.4 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 107 | Sitting | Standing | nan | nan | 15.4 | 0.1 | 42.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 108 | Sitting | Standing | nan | nan | 15.0 | 0.0 | 11.8 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 109 | Sitting | Standing | nan | nan | 13.4 | 0.0 | 48.1 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 110 | Sitting | Standing | nan | nan | 13.4 | 0.2 | 0.1 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 111 | Sitting | Standing | nan | nan | 13.5 | 0.1 | 2.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 112 | Sitting | Standing | nan | nan | 12.8 | 0.0 | 22.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 113 | Sitting | Standing | nan | nan | 11.3 | 0.0 | 42.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 114 | Sitting | Standing | nan | nan | 11.3 | 0.0 | 2.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 115 | Sitting | Standing | nan | nan | 10.4 | 0.0 | 24.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 116 | Sitting | Standing | nan | nan | 10.0 | 0.1 | 14.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 117 | Sitting | Standing | nan | nan | 9.7 | 0.1 | 6.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 118 | Sitting | Standing | nan | nan | 9.7 | 0.1 | 0.1 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 119 | Sitting | Standing | nan | nan | 9.8 | 0.0 | 1.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 120 | Sitting | Standing | nan | nan | 9.8 | 0.0 | 0.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 121 | Sitting | Standing | nan | nan | 9.9 | 0.0 | 4.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Sitting | Standing | nan | nan | 10.0 | 0.1 | 1.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Sitting | Standing | nan | nan | 10.2 | 0.1 | 5.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Sitting | Standing | nan | nan | 10.9 | 0.1 | 20.2 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Sitting | Standing | nan | nan | 11.2 | 0.3 | 11.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Sitting | Standing | nan | nan | 13.5 | 0.1 | 67.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Sitting | Standing | nan | nan | 15.8 | 0.1 | 68.7 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Sitting | Standing | nan | nan | 17.7 | 0.3 | 57.8 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Sitting | Standing | nan | nan | 18.5 | 0.3 | 24.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Sitting | Standing | nan | nan | 21.7 | 0.1 | 95.3 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Sitting | Standing | nan | nan | 24.8 | 0.6 | 94.0 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Sitting | Standing | nan | nan | 26.7 | 0.1 | 54.5 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Sitting | Standing | nan | nan | 29.9 | 0.1 | 96.0 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Sitting | Standing | nan | nan | 33.0 | 0.5 | 95.2 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Standing|Sitting |
| 135 | Sitting | Standing | nan | nan | 35.1 | 0.3 | 62.9 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Standing|Sitting|Sitting |
| 136 | Sitting | Standing | nan | nan | 39.2 | 0.7 | 120.2 | 0.2 | 0.2 | 0.1 | T | F | Standing|Standing|Sitting|Sitting|Sitting |
| 137 | Sitting | Standing | nan | nan | 41.0 | 0.9 | 54.4 | 0.2 | 0.2 | 0.1 | T | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 142 | Sitting | Lying | nan | nan | 50.9 | 0.3 | 105.8 | 0.2 | 0.2 | 0.1 | T | F | Sitting|Sitting|Sitting|Lying|Lying |
| 143 | Sitting | Lying | nan | nan | 52.1 | 0.2 | 37.2 | 0.2 | 0.2 | 0.1 | T | F | Sitting|Sitting|Lying|Lying|Lying |
| 144 | Sitting | Lying | nan | nan | 57.3 | 1.4 | 155.7 | 0.2 | 0.2 | 0.1 | T | F | Sitting|Lying|Lying|Lying|Lying |
| 145 | Sitting | Lying | nan | nan | 61.7 | 0.6 | 130.8 | 0.2 | 0.2 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 146 | Sitting | Lying | nan | nan | 67.7 | 1.1 | 178.7 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 147 | Sitting | Lying | nan | nan | 70.6 | 0.5 | 89.7 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 148 | Sitting | Lying | nan | nan | 75.5 | 1.6 | 144.7 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 149 | Sitting | Lying | nan | nan | 78.2 | 0.6 | 82.8 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 150 | Sitting | Lying | nan | nan | 82.6 | 0.7 | 131.6 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 151 | Sitting | Lying | nan | nan | 86.6 | 0.1 | 118.0 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 152 | Sitting | Lying | nan | nan | 89.2 | 1.1 | 79.0 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 153 | Sitting | Lying | nan | nan | 91.3 | 0.2 | 63.2 | 0.3 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 154 | Sitting | Lying | nan | nan | 92.9 | 0.2 | 48.7 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 155 | Sitting | Lying | nan | nan | 94.3 | 1.0 | 40.2 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 156 | Sitting | Lying | nan | nan | 95.0 | 0.4 | 22.3 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 157 | Sitting | Lying | nan | nan | 95.9 | 0.3 | 26.0 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 158 | Sitting | Lying | nan | nan | 96.3 | 0.1 | 12.3 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 159 | Sitting | Lying | nan | nan | 96.3 | 0.1 | 1.0 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 160 | Sitting | Lying | nan | nan | 96.4 | 0.0 | 2.0 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 161 | Sitting | Lying | nan | nan | 96.7 | 0.1 | 8.0 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 162 | Sitting | Lying | nan | nan | 96.9 | 0.1 | 7.2 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 163 | Sitting | Lying | nan | nan | 97.1 | 0.1 | 6.1 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 164 | Sitting | Lying | nan | nan | 96.6 | 0.1 | 14.4 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 165 | Sitting | Lying | nan | nan | 96.6 | 0.1 | 0.1 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 166 | Sitting | Lying | nan | nan | 96.4 | 0.2 | 7.9 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 167 | Sitting | Lying | nan | nan | 96.0 | 0.5 | 9.8 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 168 | Sitting | Lying | nan | nan | 96.1 | 0.5 | 1.0 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 169 | Sitting | Lying | nan | nan | 95.7 | 0.2 | 11.4 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 170 | Sitting | Lying | nan | nan | 95.9 | 0.1 | 7.0 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 171 | Sitting | Lying | nan | nan | 96.0 | 0.2 | 2.8 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 172 | Sitting | Lying | nan | nan | 95.9 | 0.0 | 1.9 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 173 | Sitting | Lying | nan | nan | 95.9 | 0.5 | 0.1 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 174 | Sitting | Lying | nan | nan | 96.0 | 0.5 | 1.3 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 175 | Sitting | Lying | nan | nan | 95.9 | 0.0 | 3.5 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 176 | Sitting | Lying | nan | nan | 95.8 | 0.3 | 1.7 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 177 | Sitting | Lying | nan | nan | 95.9 | 0.7 | 3.1 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 178 | Sitting | Lying | nan | nan | 95.7 | 0.1 | 6.6 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 179 | Sitting | Lying | nan | nan | 95.5 | 0.2 | 7.2 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 180 | Sitting | Lying | nan | nan | 95.7 | 0.4 | 6.8 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 181 | Sitting | Lying | nan | nan | 95.7 | 0.0 | 0.3 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 182 | Sitting | Lying | nan | nan | 95.3 | 0.2 | 13.0 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 183 | Sitting | Lying | nan | nan | 95.1 | 0.2 | 4.6 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 184 | Sitting | Lying | nan | nan | 95.1 | 0.0 | 1.4 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 185 | Sitting | Lying | nan | nan | 95.1 | 0.4 | 0.3 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 186 | Sitting | Lying | nan | nan | 95.4 | 0.1 | 8.9 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 187 | Sitting | Lying | nan | nan | 95.7 | 0.1 | 7.9 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 188 | Sitting | Lying | nan | nan | 95.6 | 0.4 | 3.8 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 189 | Sitting | Lying | nan | nan | 95.6 | 0.4 | 0.4 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 190 | Sitting | Lying | nan | nan | 95.3 | 0.5 | 8.4 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 191 | Sitting | Lying | nan | nan | 95.3 | 0.2 | 0.8 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 192 | Sitting | Lying | nan | nan | 95.1 | 0.2 | 3.4 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 193 | Sitting | Lying | nan | nan | 95.2 | 0.7 | 1.9 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 194 | Sitting | Lying | nan | nan | 95.2 | 0.5 | 1.2 | 0.4 | 0.4 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |

---

## Bed_lie_and_immediate_stand (**posture<90%, false negative**)

**Posture accuracy:** 34.8%

**Per-class accuracy:**

- Standing: 63.9%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 23 | 1 | 0 | 12 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 30 | 0 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | 19.6 | 0.0 | 0.0 | 0.2 | 0.2 | 0.3 | T | F | Unknown|Standing |
| 3 | Standing | Unknown | nan | nan | 11.8 | 3.2 | 234.1 | 0.1 | 0.1 | 0.3 | T | F | Unknown|Standing|Standing |
| 4 | Standing | Unknown | nan | nan | 8.3 | 1.5 | 104.7 | 0.1 | 0.1 | 0.3 | T | F | Unknown|Standing|Standing|Standing |
| 5 | Standing | Unknown | nan | nan | 7.6 | 0.7 | 20.6 | 0.1 | 0.1 | 0.3 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 29 | Standing | Sitting | nan | nan | 49.5 | 1.7 | 133.4 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 75 | Lying | Sitting | nan | nan | 93.9 | 0.2 | 4.1 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 76 | Lying | Sitting | nan | nan | 93.9 | 0.2 | 0.3 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 77 | Lying | Sitting | nan | nan | 93.8 | 0.6 | 3.2 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 78 | Lying | Sitting | nan | nan | 94.8 | 1.2 | 27.5 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 79 | Lying | Sitting | nan | nan | 94.4 | 0.2 | 9.2 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 80 | Lying | Sitting | nan | nan | 93.7 | 0.3 | 21.3 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 81 | Lying | Sitting | nan | nan | 94.8 | 0.5 | 31.6 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 82 | Lying | Sitting | nan | nan | 94.3 | 0.3 | 13.7 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 83 | Lying | Sitting | nan | nan | 92.2 | 0.1 | 64.6 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 84 | Lying | Sitting | nan | nan | 91.8 | 0.3 | 12.1 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 85 | Lying | Sitting | nan | nan | 91.8 | 0.2 | 0.0 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 86 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 87 | Lying | Sitting | nan | nan | 86.5 | 2.5 | 78.9 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Unknown|Lying |
| 88 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Lying|Unknown |
| 89 | Lying | Sitting | nan | nan | 90.3 | 5.0 | 56.7 | 0.4 | 0.4 | 0.3 | T | F | Sitting|Unknown|Lying|Unknown|Sitting |
| 90 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Lying|Unknown|Sitting|Unknown |
| 91 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Unknown|Sitting|Unknown|Unknown |
| 92 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Unknown|Unknown |
| 93 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 94 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 95 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 96 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 97 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 98 | Lying | Sitting | nan | nan | 89.3 | 0.2 | 3.3 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 99 | Lying | Sitting | nan | nan | 89.0 | 1.6 | 9.9 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 100 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Sitting|Unknown |
| 101 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Sitting|Unknown|Unknown |
| 102 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Unknown|Unknown |
| 103 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 104 | Lying | Sitting | nan | nan | 88.4 | 0.1 | 3.2 | 0.4 | 0.4 | 0.3 | T | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 135 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 136 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 137 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 138 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 139 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 140 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 141 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |

---

## Bed_long_lie (**posture<90%, false negative**)

**Posture accuracy:** 82.9%

**Per-class accuracy:**

- Standing: 0.0%
- Sitting: 0.0%
- Lying: 91.2%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 29 |
| **Sitting** | 0 | 0 | 0 | 30 |
| **Lying** | 0 | 0 | 537 | 52 |

**Fall detection:** FN

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
| 60 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 61 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 62 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 63 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 64 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 65 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 66 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 67 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 68 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 69 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 70 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 71 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 72 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 73 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 74 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 75 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 76 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 77 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 78 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 79 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 80 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 81 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 82 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 83 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 84 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 85 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 86 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 87 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 88 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 89 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 97 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 98 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 99 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 100 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 101 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 102 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 103 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 104 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 105 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 106 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 107 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 108 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 109 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 110 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 111 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 112 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 113 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 114 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 115 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 116 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 117 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 118 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 119 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 120 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 121 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 122 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 123 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 124 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 125 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 126 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 127 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 128 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 129 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 130 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 131 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 132 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 133 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 134 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 135 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 136 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 137 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 138 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 139 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 140 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 141 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 142 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 143 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 144 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 145 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 146 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 147 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 148 | Lying | Unknown | nan | nan | 93.7 | 0.0 | 0.0 | 0.3 | 0.3 | 0.5 | T | F | Unknown|Unknown|Unknown|Unknown|Lying |

---

## Bed_medium_pace_lie

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
| **Lying** | 0 | 0 | 51 | 0 |

**Fall detection:** TP (latency 48 frames)

**Mismatched frames:**

_None_

---

## Floor_lie (**posture<90%, false positive**)

**Posture accuracy:** 63.7%

**Per-class accuracy:**

- Standing: 78.0%
- Sitting: 85.6%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 46 | 0 | 0 | 13 |
| **Sitting** | 13 | 77 | 0 | 0 |
| **Lying** | 10 | 0 | 0 | 34 |

**Fall detection:** FP frames [77, 78, 79, 111, 112]

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
| 9 | Standing | Unknown | 48.4 | 32.7 | 39.9 | 0.0 | 0.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 10 | Standing | Unknown | 161.1 | 143.9 | 22.6 | 6.2 | 518.6 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Unknown|Sitting|Standing |
| 11 | Standing | Unknown | 174.8 | 169.4 | 5.6 | 3.0 | 508.9 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Unknown|Sitting|Standing|Standing |
| 12 | Standing | Unknown | 169.0 | 171.3 | 3.9 | 1.5 | 51.2 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Sitting|Standing|Standing|Standing |
| 13 | Standing | Unknown | 170.5 | 167.5 | 6.6 | 0.5 | 79.5 | 0.2 | 0.2 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 135 | Sitting | Standing | nan | nan | 8.9 | 0.4 | 11.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Sitting | Standing | nan | nan | 9.8 | 0.3 | 26.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Sitting | Standing | nan | nan | 10.5 | 0.5 | 20.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Sitting | Standing | nan | 106.8 | 10.8 | 0.2 | 10.5 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 139 | Sitting | Standing | nan | 105.2 | 11.3 | 0.3 | 12.2 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 140 | Sitting | Standing | nan | 106.2 | 10.5 | 0.2 | 23.1 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 141 | Sitting | Standing | nan | 106.6 | 10.8 | 0.2 | 9.2 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 142 | Sitting | Standing | nan | nan | 10.4 | 0.3 | 12.9 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 143 | Sitting | Standing | nan | nan | 10.2 | 0.9 | 4.6 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 144 | Sitting | Standing | nan | 118.6 | 9.3 | 0.3 | 26.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Standing|Standing|Sitting |
| 145 | Sitting | Standing | nan | 122.8 | 8.3 | 0.2 | 30.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Standing|Standing|Sitting|Sitting |
| 146 | Sitting | Standing | nan | 125.2 | 8.1 | 0.3 | 6.3 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 147 | Sitting | Standing | nan | 140.8 | 7.8 | 0.4 | 8.4 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 255 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 256 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 257 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 258 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 259 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 260 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 261 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 262 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 263 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 264 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 265 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 266 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 267 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 268 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 269 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
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
| 285 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 286 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 287 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 288 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 289 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 290 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 291 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 292 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 293 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 294 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 295 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 296 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 297 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 298 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |

---

## Floor_lie_and_immediate_stand (**posture<90%**)

**Posture accuracy:** 30.6%

**Per-class accuracy:**

- Standing: 88.6%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 70 | 0 | 4 | 5 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 56 | 55 | 0 | 39 |

**Fall detection:** TP (latency 27 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | 174.3 | 170.8 | 9.3 | 0.0 | 0.0 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing |
| 3 | Standing | Unknown | 171.5 | 176.8 | 2.7 | 1.3 | 198.4 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing |
| 4 | Standing | Unknown | 174.0 | 173.7 | 2.2 | 1.0 | 13.7 | 0.2 | 0.2 | 0.3 | F | F | Unknown|Standing|Standing|Standing |
| 5 | Standing | Unknown | 176.8 | 172.0 | 4.1 | 0.4 | 56.1 | 0.3 | 0.3 | 0.3 | F | F | Unknown|Standing|Standing|Standing|Standing |
| 56 | Standing | Lying | nan | 118.1 | 56.4 | 1.7 | 336.9 | 0.2 | 0.3 | 0.2 | F | F | Standing|Standing|Standing|Lying|Lying |
| 57 | Standing | Lying | nan | 123.0 | 52.3 | 0.6 | 122.8 | 0.2 | 0.3 | 0.2 | F | F | Standing|Standing|Lying|Lying|Lying |
| 58 | Standing | Lying | nan | nan | 58.7 | 1.1 | 191.8 | 0.1 | 0.3 | 0.2 | T | F | Standing|Lying|Lying|Lying|Lying |
| 59 | Standing | Lying | nan | nan | 55.9 | 1.6 | 81.8 | 0.1 | 0.3 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 135 | Lying | Sitting | nan | 148.0 | 1.1 | 0.1 | 3.8 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 136 | Lying | Sitting | nan | 148.0 | 1.1 | 0.4 | 0.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 137 | Lying | Sitting | nan | 143.7 | 0.1 | 0.5 | 29.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 138 | Lying | Sitting | nan | 146.1 | 0.8 | 0.4 | 20.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 139 | Lying | Sitting | nan | 150.1 | 2.1 | 0.2 | 39.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 140 | Lying | Sitting | nan | 157.8 | 2.3 | 1.2 | 5.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 141 | Lying | Sitting | nan | 156.9 | 3.1 | 0.2 | 24.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 142 | Lying | Sitting | nan | 155.8 | 4.9 | 0.4 | 51.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 143 | Lying | Sitting | nan | 161.0 | 5.7 | 0.3 | 24.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 144 | Lying | Sitting | nan | 156.4 | 5.6 | 0.2 | 2.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 145 | Lying | Sitting | nan | 154.6 | 4.8 | 0.9 | 22.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 146 | Lying | Sitting | nan | 161.3 | 5.5 | 0.1 | 19.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 147 | Lying | Sitting | nan | 162.1 | 6.4 | 0.1 | 27.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 148 | Lying | Sitting | nan | 163.3 | 8.0 | 0.1 | 48.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 149 | Lying | Sitting | nan | nan | 8.5 | 0.3 | 14.1 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 150 | Lying | Sitting | nan | nan | 9.3 | 0.3 | 24.2 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 151 | Lying | Sitting | nan | nan | 9.9 | 0.7 | 17.4 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 152 | Lying | Sitting | nan | nan | 10.0 | 0.1 | 2.0 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 153 | Lying | Standing | nan | nan | 10.6 | 0.1 | 18.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 154 | Lying | Standing | nan | nan | 11.5 | 0.0 | 27.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 155 | Lying | Standing | nan | nan | 11.3 | 0.6 | 5.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 156 | Lying | Standing | nan | nan | 11.9 | 0.3 | 18.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 157 | Lying | Standing | nan | nan | 11.8 | 0.2 | 4.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 158 | Lying | Standing | nan | nan | 11.7 | 0.1 | 2.5 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 159 | Lying | Standing | nan | nan | 11.2 | 0.2 | 16.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 160 | Lying | Standing | nan | nan | 10.4 | 0.2 | 22.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 161 | Lying | Standing | nan | nan | 10.0 | 0.1 | 10.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 162 | Lying | Standing | nan | nan | 9.4 | 0.6 | 18.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 163 | Lying | Standing | nan | nan | 9.7 | 0.4 | 8.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 164 | Lying | Standing | nan | nan | 8.7 | 0.6 | 28.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 165 | Lying | Standing | nan | nan | 8.2 | 0.9 | 16.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 166 | Lying | Standing | nan | nan | 8.1 | 0.4 | 3.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 167 | Lying | Standing | nan | nan | 6.5 | 0.7 | 47.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 168 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 169 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Unknown|Unknown |
| 170 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Unknown|Unknown|Unknown |
| 171 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Unknown|Unknown|Unknown|Unknown |
| 172 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 173 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 174 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 175 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 176 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 177 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 178 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 179 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 180 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 181 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 182 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 183 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 184 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 185 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 186 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 187 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 188 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 189 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 190 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 191 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 192 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 193 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 194 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 195 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 196 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 197 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 198 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 199 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 200 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 201 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 202 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 203 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 204 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 205 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 206 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 207 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 208 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 209 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 210 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 211 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 212 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 213 | Lying | Unknown | nan | nan | 23.3 | 0.1 | 11.0 | 0.1 | 0.3 | 0.1 | T | F | Unknown|Unknown|Unknown|Unknown|Standing |
| 214 | Lying | Unknown | nan | nan | 17.3 | 0.9 | 180.2 | 0.1 | 0.3 | 0.1 | T | F | Unknown|Unknown|Unknown|Standing|Standing |
| 215 | Lying | Unknown | nan | nan | 7.0 | 1.5 | 308.5 | 0.1 | 0.3 | 0.1 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 216 | Lying | Unknown | nan | nan | 3.6 | 0.4 | 102.0 | 0.1 | 0.3 | 0.1 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 217 | Lying | Standing | nan | nan | 0.8 | 0.9 | 84.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 218 | Lying | Standing | nan | nan | 0.9 | 0.1 | 4.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 219 | Lying | Standing | nan | nan | 1.9 | 0.1 | 31.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 220 | Lying | Standing | nan | nan | 2.8 | 0.1 | 25.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 221 | Lying | Standing | nan | nan | 3.5 | 0.2 | 20.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 222 | Lying | Standing | nan | nan | 4.5 | 0.7 | 30.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 223 | Lying | Standing | nan | nan | 6.3 | 0.2 | 55.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 224 | Lying | Standing | nan | nan | 7.0 | 0.0 | 19.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 225 | Lying | Standing | nan | nan | 7.5 | 0.3 | 15.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 226 | Lying | Standing | nan | nan | 7.8 | 0.3 | 9.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 227 | Lying | Standing | nan | nan | 7.4 | 0.0 | 10.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 228 | Lying | Standing | nan | nan | 7.3 | 0.2 | 3.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 229 | Lying | Standing | nan | nan | 7.3 | 0.1 | 0.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 230 | Lying | Standing | nan | nan | 7.4 | 0.0 | 1.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 231 | Lying | Standing | nan | nan | 7.7 | 0.2 | 11.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 232 | Lying | Standing | nan | nan | 6.8 | 0.1 | 27.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 233 | Lying | Standing | nan | nan | 6.4 | 0.1 | 11.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 234 | Lying | Standing | nan | nan | 6.4 | 0.1 | 1.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 235 | Lying | Standing | nan | nan | 6.1 | 0.2 | 7.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 236 | Lying | Standing | nan | nan | 6.1 | 0.3 | 0.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 237 | Lying | Standing | nan | nan | 6.0 | 0.1 | 3.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 238 | Lying | Standing | nan | nan | 5.9 | 0.0 | 4.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 239 | Lying | Standing | nan | nan | 5.6 | 0.2 | 7.8 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 240 | Lying | Standing | nan | nan | 5.0 | 0.3 | 18.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 241 | Lying | Standing | nan | nan | 4.7 | 0.1 | 7.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 242 | Lying | Standing | nan | nan | 4.0 | 0.4 | 22.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 243 | Lying | Standing | nan | nan | 3.7 | 0.3 | 10.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 244 | Lying | Standing | nan | 135.4 | 3.3 | 0.2 | 11.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 245 | Lying | Standing | nan | 136.5 | 2.8 | 0.3 | 13.8 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 246 | Lying | Standing | nan | 137.6 | 2.6 | 0.4 | 6.2 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 247 | Lying | Standing | nan | 137.5 | 1.8 | 0.4 | 23.3 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 248 | Lying | Sitting | nan | 136.1 | 1.7 | 0.3 | 4.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 249 | Lying | Sitting | nan | 129.7 | 1.0 | 0.3 | 18.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 250 | Lying | Sitting | nan | 129.5 | 1.0 | 0.7 | 0.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 251 | Lying | Sitting | nan | 131.0 | 0.5 | 0.5 | 15.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 252 | Lying | Sitting | nan | 129.8 | 0.7 | 0.4 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 253 | Lying | Sitting | nan | 132.6 | 1.3 | 0.4 | 18.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 254 | Lying | Sitting | nan | 140.4 | 1.5 | 0.1 | 5.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 255 | Lying | Sitting | nan | 143.2 | 1.5 | 0.1 | 0.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 256 | Lying | Sitting | nan | 142.9 | 0.9 | 0.1 | 18.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 257 | Lying | Sitting | nan | 142.7 | 0.7 | 0.4 | 4.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 258 | Lying | Sitting | nan | 146.5 | 1.2 | 0.2 | 13.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 259 | Lying | Sitting | nan | 147.6 | 1.2 | 0.2 | 2.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 260 | Lying | Sitting | 130.3 | 150.1 | 1.5 | 0.2 | 7.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 261 | Lying | Sitting | 129.3 | 149.6 | 1.1 | 0.3 | 10.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 262 | Lying | Sitting | 133.9 | 149.6 | 1.1 | 0.4 | 1.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 263 | Lying | Sitting | 135.9 | 149.8 | 0.7 | 0.1 | 11.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 264 | Lying | Sitting | 139.9 | 147.3 | 1.1 | 0.4 | 11.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 265 | Lying | Sitting | 135.1 | 143.6 | 2.4 | 0.9 | 41.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 266 | Lying | Sitting | 134.2 | 142.9 | 2.7 | 0.6 | 9.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 267 | Lying | Sitting | 127.2 | 142.1 | 3.5 | 0.6 | 22.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 268 | Lying | Sitting | 117.0 | 137.4 | 10.6 | 0.4 | 211.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 269 | Lying | Sitting | 91.1 | 135.3 | 11.2 | 0.3 | 18.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 270 | Lying | Sitting | 97.9 | 134.9 | 13.7 | 0.2 | 76.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 271 | Lying | Sitting | 113.7 | 132.6 | 17.3 | 0.1 | 108.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 272 | Lying | Sitting | 71.6 | 129.4 | 18.0 | 0.4 | 19.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 273 | Lying | Sitting | 70.0 | 129.0 | 21.7 | 0.2 | 111.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 274 | Lying | Sitting | nan | 131.7 | 22.7 | 0.2 | 30.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 275 | Lying | Sitting | nan | 129.1 | 24.6 | 0.4 | 57.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 276 | Lying | Sitting | nan | 127.3 | 24.7 | 0.2 | 3.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 277 | Lying | Sitting | nan | 129.5 | 25.9 | 0.6 | 34.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 278 | Lying | Sitting | nan | 128.4 | 26.5 | 0.5 | 19.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 279 | Lying | Sitting | nan | 120.0 | 28.8 | 0.2 | 69.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 280 | Lying | Sitting | nan | 110.8 | 30.2 | 0.2 | 40.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 281 | Lying | Sitting | nan | 107.3 | 33.5 | 1.8 | 98.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 282 | Lying | Sitting | nan | 105.6 | 34.9 | 0.8 | 42.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 283 | Lying | Sitting | nan | 108.0 | 35.8 | 1.5 | 27.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 284 | Lying | Sitting | nan | 97.0 | 40.7 | 0.9 | 147.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Floor_long_lie (**posture<90%**)

**Posture accuracy:** 10.5%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 0.7%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 59 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 139 | 397 | 4 | 0 |

**Fall detection:** TP (latency 9 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 124 | Lying | Standing | nan | nan | 17.5 | 0.7 | 144.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Lying | Standing | nan | nan | 15.6 | 0.7 | 57.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Lying | Standing | nan | nan | 13.6 | 0.2 | 59.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Lying | Standing | nan | 152.8 | 10.8 | 0.2 | 83.6 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 128 | Lying | Standing | nan | 152.0 | 9.4 | 0.1 | 43.9 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 129 | Lying | Standing | nan | 149.7 | 11.2 | 0.8 | 55.7 | 0.3 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 130 | Lying | Standing | nan | 154.8 | 11.4 | 0.1 | 5.6 | 0.3 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 131 | Lying | Sitting | nan | 155.8 | 10.3 | 0.1 | 32.3 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 132 | Lying | Sitting | nan | 154.1 | 8.8 | 0.0 | 46.3 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 133 | Lying | Sitting | nan | 152.0 | 8.2 | 0.1 | 19.0 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 134 | Lying | Sitting | nan | 150.2 | 8.7 | 0.1 | 14.5 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 135 | Lying | Sitting | nan | 150.5 | 9.2 | 0.3 | 17.8 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 136 | Lying | Sitting | nan | 149.7 | 9.5 | 0.1 | 7.3 | 0.3 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 137 | Lying | Sitting | nan | 152.9 | 10.2 | 0.5 | 20.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 138 | Lying | Sitting | nan | 150.9 | 10.1 | 0.1 | 3.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 139 | Lying | Sitting | nan | 151.6 | 10.5 | 0.5 | 13.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 140 | Lying | Sitting | nan | 150.6 | 10.7 | 0.3 | 6.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 141 | Lying | Sitting | nan | 147.0 | 12.6 | 0.7 | 56.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 142 | Lying | Sitting | nan | 144.8 | 14.4 | 0.2 | 55.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 143 | Lying | Sitting | nan | 144.6 | 16.6 | 0.2 | 66.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 144 | Lying | Sitting | nan | 144.3 | 17.7 | 0.7 | 31.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 145 | Lying | Sitting | nan | 132.0 | 19.4 | 0.4 | 50.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 146 | Lying | Sitting | nan | 145.1 | 20.3 | 0.2 | 27.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 147 | Lying | Sitting | nan | 143.7 | 21.7 | 0.1 | 42.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 148 | Lying | Sitting | nan | 143.6 | 21.9 | 0.1 | 7.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 149 | Lying | Sitting | nan | 146.8 | 24.1 | 0.3 | 64.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 150 | Lying | Sitting | nan | 146.2 | 25.0 | 0.2 | 27.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 151 | Lying | Sitting | nan | 147.5 | 26.3 | 0.1 | 38.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 152 | Lying | Sitting | nan | 155.7 | 27.9 | 0.4 | 49.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 153 | Lying | Sitting | nan | 164.4 | 28.4 | 0.0 | 15.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 154 | Lying | Sitting | nan | 165.3 | 27.4 | 0.2 | 31.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 155 | Lying | Sitting | nan | 158.2 | 27.6 | 0.4 | 6.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 156 | Lying | Sitting | nan | nan | 28.2 | 1.2 | 18.0 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 157 | Lying | Sitting | nan | nan | 26.9 | 0.4 | 37.6 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 158 | Lying | Sitting | nan | nan | 25.3 | 0.2 | 49.8 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 159 | Lying | Sitting | nan | nan | 23.6 | 0.5 | 50.1 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 160 | Lying | Standing | nan | nan | 23.1 | 0.5 | 14.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 161 | Lying | Standing | nan | nan | 23.0 | 0.3 | 3.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 162 | Lying | Standing | nan | nan | 24.6 | 1.2 | 47.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 163 | Lying | Standing | nan | nan | 25.5 | 1.2 | 28.5 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 164 | Lying | Standing | nan | nan | 26.5 | 0.8 | 28.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 165 | Lying | Standing | nan | nan | 26.3 | 0.4 | 6.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 166 | Lying | Standing | nan | nan | 26.0 | 0.2 | 7.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 167 | Lying | Standing | nan | nan | 19.2 | 1.7 | 205.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 168 | Lying | Standing | nan | nan | 14.3 | 1.9 | 145.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 169 | Lying | Standing | nan | nan | 13.9 | 0.3 | 12.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 170 | Lying | Standing | nan | nan | 19.9 | 0.8 | 180.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 171 | Lying | Standing | nan | nan | 15.2 | 1.1 | 141.5 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 172 | Lying | Standing | nan | nan | 14.7 | 0.6 | 14.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 173 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Standing|Standing|Unknown |
| 174 | Lying | Standing | nan | nan | 4.1 | 3.1 | 158.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Unknown|Standing |
| 175 | Lying | Standing | nan | 165.6 | 4.8 | 1.0 | 18.5 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Unknown|Standing|Sitting |
| 176 | Lying | Standing | nan | 168.6 | 13.4 | 1.4 | 258.2 | 0.2 | 0.3 | 0.1 | F | F | Standing|Unknown|Standing|Sitting|Sitting |
| 177 | Lying | Standing | nan | 167.8 | 17.6 | 0.5 | 128.0 | 0.2 | 0.3 | 0.1 | F | F | Unknown|Standing|Sitting|Sitting|Sitting |
| 178 | Lying | Standing | nan | 169.2 | 18.0 | 0.2 | 11.8 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 179 | Lying | Sitting | nan | 169.7 | 18.3 | 0.1 | 8.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 180 | Lying | Sitting | nan | 168.7 | 18.9 | 0.1 | 16.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 181 | Lying | Sitting | nan | 169.5 | 19.3 | 0.1 | 12.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 182 | Lying | Sitting | nan | 169.6 | 19.1 | 0.0 | 5.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 183 | Lying | Sitting | nan | 168.9 | 19.2 | 0.1 | 3.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 184 | Lying | Sitting | nan | 166.5 | 19.3 | 0.1 | 1.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 185 | Lying | Sitting | nan | 165.3 | 19.7 | 0.1 | 12.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 186 | Lying | Sitting | nan | 162.5 | 20.1 | 0.1 | 13.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 187 | Lying | Sitting | nan | 164.3 | 20.2 | 0.1 | 0.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 188 | Lying | Sitting | nan | 163.9 | 20.3 | 0.2 | 5.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 189 | Lying | Sitting | nan | 164.3 | 20.8 | 0.2 | 12.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 190 | Lying | Sitting | nan | 164.8 | 20.9 | 0.2 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 191 | Lying | Sitting | nan | 165.6 | 20.9 | 0.0 | 2.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 192 | Lying | Sitting | nan | 165.8 | 20.8 | 0.1 | 0.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 193 | Lying | Sitting | nan | 167.1 | 20.8 | 0.0 | 1.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 194 | Lying | Sitting | nan | 166.1 | 20.7 | 0.0 | 2.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 195 | Lying | Sitting | nan | 166.5 | 20.7 | 0.0 | 0.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 196 | Lying | Sitting | nan | 165.6 | 20.5 | 0.1 | 6.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 197 | Lying | Sitting | nan | 168.2 | 20.4 | 0.0 | 3.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 198 | Lying | Sitting | nan | 164.6 | 20.3 | 0.0 | 4.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 199 | Lying | Sitting | nan | 164.6 | 20.1 | 0.1 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 200 | Lying | Sitting | nan | 166.0 | 19.9 | 0.1 | 6.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 201 | Lying | Sitting | nan | 166.1 | 20.0 | 0.0 | 2.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 202 | Lying | Sitting | nan | 166.8 | 20.1 | 0.0 | 2.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 203 | Lying | Sitting | nan | 165.3 | 20.3 | 0.1 | 7.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 204 | Lying | Sitting | nan | 167.7 | 20.3 | 0.0 | 0.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 205 | Lying | Sitting | nan | 169.0 | 20.3 | 0.0 | 1.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 206 | Lying | Sitting | nan | 169.6 | 19.8 | 0.1 | 13.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 207 | Lying | Sitting | nan | 167.5 | 20.0 | 0.1 | 6.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 208 | Lying | Sitting | nan | 169.0 | 20.0 | 0.1 | 0.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 209 | Lying | Sitting | nan | 169.0 | 19.7 | 0.0 | 9.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 210 | Lying | Sitting | nan | 166.8 | 19.5 | 0.0 | 7.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 211 | Lying | Sitting | nan | 166.9 | 19.8 | 0.0 | 8.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 212 | Lying | Sitting | nan | 165.0 | 19.2 | 0.0 | 15.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 213 | Lying | Sitting | nan | 164.8 | 19.2 | 0.0 | 2.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 214 | Lying | Sitting | nan | 164.4 | 18.9 | 0.1 | 8.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 215 | Lying | Sitting | nan | 165.8 | 18.7 | 0.1 | 4.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 216 | Lying | Sitting | nan | 167.0 | 19.1 | 0.1 | 11.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 217 | Lying | Sitting | nan | 167.3 | 20.0 | 0.1 | 26.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 218 | Lying | Sitting | nan | 166.9 | 20.1 | 0.0 | 2.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 219 | Lying | Sitting | nan | 168.0 | 20.0 | 0.2 | 2.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 220 | Lying | Sitting | nan | 167.7 | 20.0 | 0.1 | 1.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 221 | Lying | Sitting | nan | 168.4 | 19.6 | 0.0 | 10.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 222 | Lying | Sitting | nan | 169.2 | 19.9 | 0.1 | 8.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 223 | Lying | Sitting | nan | 169.5 | 19.9 | 0.1 | 1.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 224 | Lying | Sitting | nan | 169.2 | 19.4 | 0.1 | 15.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 225 | Lying | Sitting | nan | 167.2 | 19.9 | 0.1 | 16.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 226 | Lying | Sitting | nan | 164.2 | 20.4 | 0.4 | 13.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 227 | Lying | Sitting | nan | 160.4 | 19.7 | 0.3 | 19.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 228 | Lying | Sitting | nan | 162.4 | 19.5 | 0.4 | 5.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 229 | Lying | Sitting | nan | 163.1 | 19.1 | 0.0 | 13.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 230 | Lying | Sitting | nan | 163.4 | 19.4 | 0.1 | 10.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 231 | Lying | Sitting | nan | 163.5 | 19.4 | 0.0 | 1.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 232 | Lying | Sitting | nan | 164.8 | 19.5 | 0.1 | 3.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 233 | Lying | Sitting | nan | 166.8 | 19.7 | 0.0 | 6.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 234 | Lying | Sitting | nan | 167.3 | 19.7 | 0.0 | 1.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 235 | Lying | Sitting | nan | 167.3 | 19.2 | 0.2 | 14.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 236 | Lying | Sitting | nan | 166.7 | 19.2 | 0.1 | 0.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 237 | Lying | Sitting | nan | 164.7 | 19.3 | 0.1 | 3.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 238 | Lying | Sitting | nan | 164.1 | 19.5 | 0.2 | 5.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 239 | Lying | Sitting | nan | 164.2 | 19.5 | 0.0 | 1.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 240 | Lying | Sitting | nan | 165.0 | 19.1 | 0.0 | 12.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 241 | Lying | Sitting | nan | 166.4 | 19.0 | 0.1 | 0.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 242 | Lying | Sitting | nan | 166.7 | 18.6 | 0.2 | 13.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 243 | Lying | Sitting | nan | 164.4 | 19.0 | 0.1 | 11.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 244 | Lying | Sitting | nan | 167.6 | 19.2 | 0.2 | 7.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 245 | Lying | Sitting | nan | 167.7 | 19.3 | 0.0 | 3.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 246 | Lying | Sitting | nan | 168.0 | 19.2 | 0.1 | 3.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 247 | Lying | Sitting | nan | 167.8 | 19.2 | 0.0 | 1.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 248 | Lying | Sitting | nan | 166.7 | 19.1 | 0.0 | 2.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 249 | Lying | Sitting | nan | 166.5 | 19.1 | 0.0 | 1.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 250 | Lying | Sitting | nan | 166.7 | 18.9 | 0.0 | 8.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 251 | Lying | Sitting | nan | 166.2 | 18.9 | 0.1 | 2.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 252 | Lying | Sitting | nan | 164.6 | 18.8 | 0.0 | 4.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 253 | Lying | Sitting | nan | 163.3 | 18.6 | 0.0 | 5.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 254 | Lying | Sitting | nan | 164.2 | 18.6 | 0.0 | 0.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 255 | Lying | Sitting | nan | 163.0 | 19.1 | 0.1 | 14.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 256 | Lying | Sitting | nan | 163.5 | 20.1 | 0.2 | 29.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 257 | Lying | Sitting | nan | 164.2 | 19.9 | 0.1 | 4.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 258 | Lying | Sitting | nan | 162.3 | 19.7 | 0.1 | 7.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 259 | Lying | Sitting | nan | 163.8 | 19.6 | 0.0 | 3.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 260 | Lying | Sitting | nan | 163.1 | 19.2 | 0.1 | 10.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 261 | Lying | Sitting | nan | 161.9 | 19.4 | 0.1 | 6.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 262 | Lying | Sitting | nan | 163.8 | 20.0 | 0.3 | 18.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 263 | Lying | Sitting | nan | 165.3 | 20.4 | 0.3 | 11.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 264 | Lying | Sitting | nan | 165.4 | 20.5 | 0.0 | 1.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 265 | Lying | Sitting | nan | 166.3 | 20.4 | 0.0 | 1.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 266 | Lying | Sitting | nan | 166.9 | 20.5 | 0.1 | 3.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 267 | Lying | Sitting | nan | 166.0 | 20.7 | 0.0 | 3.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 268 | Lying | Sitting | nan | 162.6 | 21.0 | 0.0 | 8.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 269 | Lying | Sitting | nan | 162.9 | 20.7 | 0.0 | 7.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 270 | Lying | Sitting | nan | 163.7 | 20.7 | 0.0 | 1.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 271 | Lying | Sitting | nan | 163.9 | 20.4 | 0.1 | 11.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 272 | Lying | Sitting | nan | 162.1 | 20.6 | 0.1 | 7.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 273 | Lying | Sitting | nan | 162.2 | 20.7 | 0.2 | 1.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 274 | Lying | Sitting | nan | 161.0 | 20.8 | 0.1 | 3.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 275 | Lying | Sitting | nan | 155.4 | 21.1 | 0.2 | 10.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 276 | Lying | Sitting | nan | 146.7 | 21.8 | 0.2 | 20.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 277 | Lying | Sitting | nan | 149.6 | 21.9 | 0.1 | 3.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 278 | Lying | Sitting | nan | 154.6 | 21.9 | 0.0 | 0.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 279 | Lying | Sitting | nan | 154.5 | 21.8 | 0.1 | 3.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 280 | Lying | Sitting | nan | 160.2 | 21.6 | 0.1 | 5.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 281 | Lying | Sitting | nan | 163.2 | 21.6 | 0.0 | 0.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 282 | Lying | Sitting | nan | 165.5 | 21.0 | 0.2 | 17.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 283 | Lying | Sitting | nan | 167.1 | 21.0 | 0.1 | 0.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 284 | Lying | Sitting | nan | 167.4 | 20.7 | 0.2 | 7.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 285 | Lying | Sitting | nan | 166.6 | 20.4 | 0.0 | 10.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 286 | Lying | Sitting | nan | 167.2 | 20.6 | 0.1 | 6.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 287 | Lying | Sitting | nan | 165.1 | 20.6 | 0.3 | 1.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 288 | Lying | Sitting | nan | 164.6 | 20.5 | 0.0 | 1.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 289 | Lying | Sitting | nan | 164.2 | 20.6 | 0.0 | 1.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 290 | Lying | Sitting | nan | 162.9 | 20.8 | 0.1 | 5.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 291 | Lying | Sitting | nan | 164.2 | 21.0 | 0.0 | 7.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 292 | Lying | Sitting | nan | 165.2 | 20.8 | 0.0 | 7.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 293 | Lying | Sitting | nan | 165.6 | 20.9 | 0.0 | 4.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 294 | Lying | Sitting | nan | 166.0 | 20.9 | 0.1 | 1.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 295 | Lying | Sitting | nan | 166.2 | 20.9 | 0.2 | 1.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 296 | Lying | Sitting | nan | 165.5 | 20.4 | 0.1 | 15.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 297 | Lying | Sitting | nan | 166.4 | 20.4 | 0.0 | 0.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 298 | Lying | Sitting | nan | 167.7 | 20.7 | 0.0 | 7.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 299 | Lying | Sitting | nan | 167.4 | 20.4 | 0.1 | 8.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 300 | Lying | Sitting | nan | 168.9 | 19.7 | 0.1 | 19.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 301 | Lying | Sitting | nan | 169.6 | 19.9 | 0.1 | 6.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 302 | Lying | Sitting | nan | 169.4 | 19.9 | 0.2 | 0.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 303 | Lying | Sitting | nan | 169.3 | 20.3 | 0.1 | 11.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 304 | Lying | Sitting | nan | 172.2 | 20.0 | 0.1 | 9.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 305 | Lying | Sitting | nan | 172.5 | 20.6 | 0.1 | 19.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 306 | Lying | Sitting | nan | 173.4 | 20.0 | 0.2 | 18.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 307 | Lying | Sitting | nan | 174.5 | 20.1 | 0.1 | 1.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 308 | Lying | Sitting | nan | 173.2 | 20.2 | 0.1 | 2.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 309 | Lying | Sitting | nan | 170.9 | 19.9 | 0.1 | 7.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 310 | Lying | Sitting | nan | 170.9 | 20.2 | 0.0 | 7.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 311 | Lying | Sitting | nan | 170.7 | 19.6 | 0.1 | 16.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 312 | Lying | Sitting | nan | 171.1 | 19.2 | 0.0 | 11.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 313 | Lying | Sitting | nan | 169.5 | 19.3 | 0.1 | 1.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 314 | Lying | Sitting | nan | 168.3 | 19.1 | 0.1 | 3.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 315 | Lying | Sitting | nan | 168.4 | 19.4 | 0.0 | 9.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 316 | Lying | Sitting | nan | 168.1 | 18.7 | 0.1 | 22.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 317 | Lying | Sitting | nan | 167.1 | 18.9 | 0.1 | 6.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 318 | Lying | Sitting | nan | 168.1 | 18.7 | 0.0 | 7.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 319 | Lying | Sitting | nan | 168.2 | 18.0 | 0.4 | 21.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 320 | Lying | Sitting | nan | 169.2 | 18.5 | 0.3 | 16.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 321 | Lying | Sitting | nan | 170.6 | 18.1 | 0.1 | 11.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 322 | Lying | Sitting | nan | 168.7 | 19.0 | 0.1 | 24.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 323 | Lying | Sitting | nan | 168.6 | 19.2 | 0.0 | 8.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 324 | Lying | Sitting | nan | 168.9 | 19.5 | 0.1 | 8.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 325 | Lying | Sitting | nan | 165.9 | 19.7 | 0.3 | 6.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 326 | Lying | Sitting | nan | 165.6 | 19.6 | 0.0 | 4.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 327 | Lying | Sitting | nan | 163.3 | 19.3 | 0.1 | 8.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 328 | Lying | Sitting | nan | 162.7 | 19.4 | 0.0 | 3.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 329 | Lying | Sitting | nan | 163.4 | 19.5 | 0.1 | 1.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 330 | Lying | Sitting | nan | 165.6 | 19.3 | 0.0 | 6.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 331 | Lying | Sitting | nan | 167.1 | 19.0 | 0.1 | 7.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 332 | Lying | Sitting | nan | 167.9 | 18.7 | 0.1 | 9.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 333 | Lying | Sitting | nan | 167.4 | 18.9 | 0.2 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 334 | Lying | Sitting | nan | 170.3 | 19.1 | 0.0 | 6.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 335 | Lying | Sitting | nan | 170.2 | 18.8 | 0.1 | 8.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 336 | Lying | Sitting | nan | 170.7 | 18.9 | 0.1 | 4.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 337 | Lying | Sitting | nan | 172.2 | 18.9 | 0.1 | 1.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 338 | Lying | Sitting | nan | 172.1 | 19.1 | 0.1 | 6.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 339 | Lying | Sitting | nan | 168.1 | 19.1 | 0.0 | 0.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 340 | Lying | Sitting | nan | 168.2 | 19.2 | 0.0 | 4.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 341 | Lying | Sitting | nan | 157.8 | 19.2 | 0.2 | 0.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 342 | Lying | Sitting | nan | 160.4 | 19.3 | 0.1 | 1.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 343 | Lying | Sitting | nan | 164.4 | 18.3 | 0.2 | 28.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 344 | Lying | Sitting | nan | 165.1 | 18.1 | 0.1 | 6.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 345 | Lying | Sitting | nan | 166.3 | 17.9 | 0.1 | 5.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 346 | Lying | Sitting | nan | 167.8 | 17.1 | 0.5 | 22.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 347 | Lying | Sitting | nan | 172.8 | 15.9 | 0.1 | 37.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 348 | Lying | Sitting | nan | 172.2 | 14.3 | 0.2 | 47.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 349 | Lying | Sitting | nan | 173.1 | 14.8 | 0.2 | 14.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 350 | Lying | Sitting | nan | nan | 18.6 | 0.5 | 113.6 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 351 | Lying | Sitting | nan | nan | 19.6 | 0.3 | 31.3 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 352 | Lying | Sitting | nan | nan | 19.5 | 0.1 | 3.1 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 353 | Lying | Sitting | nan | nan | 19.8 | 0.1 | 8.2 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 354 | Lying | Standing | nan | nan | 20.8 | 0.1 | 31.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 355 | Lying | Standing | nan | nan | 21.5 | 0.2 | 18.3 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 356 | Lying | Standing | nan | nan | 21.3 | 0.2 | 4.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 357 | Lying | Standing | nan | nan | 21.9 | 0.0 | 16.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 358 | Lying | Standing | nan | nan | 21.4 | 0.2 | 14.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 359 | Lying | Standing | nan | nan | 21.1 | 0.3 | 6.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 360 | Lying | Standing | nan | 170.7 | 21.9 | 0.1 | 22.5 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 361 | Lying | Standing | nan | 171.6 | 22.8 | 0.2 | 28.1 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 362 | Lying | Standing | nan | 171.5 | 22.9 | 0.0 | 1.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 363 | Lying | Standing | nan | 171.2 | 22.8 | 0.0 | 3.6 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 364 | Lying | Sitting | nan | 172.2 | 23.0 | 0.1 | 6.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 365 | Lying | Sitting | nan | 170.4 | 22.8 | 0.1 | 4.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 366 | Lying | Sitting | nan | 167.7 | 22.6 | 0.0 | 8.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 367 | Lying | Sitting | nan | 170.4 | 22.7 | 0.0 | 4.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 368 | Lying | Sitting | nan | 168.9 | 22.5 | 0.1 | 6.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 369 | Lying | Sitting | nan | 167.0 | 22.8 | 0.1 | 8.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 370 | Lying | Sitting | nan | 167.9 | 22.9 | 0.1 | 4.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 371 | Lying | Sitting | nan | 169.3 | 22.9 | 0.0 | 0.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 372 | Lying | Sitting | nan | 170.7 | 23.1 | 0.0 | 5.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 373 | Lying | Sitting | nan | 169.9 | 23.3 | 0.0 | 6.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 374 | Lying | Sitting | nan | 167.5 | 23.5 | 0.1 | 6.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 375 | Lying | Sitting | nan | 167.9 | 23.8 | 0.1 | 9.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 376 | Lying | Sitting | nan | 169.4 | 24.1 | 0.0 | 7.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 377 | Lying | Sitting | nan | 170.4 | 23.9 | 0.0 | 3.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 378 | Lying | Sitting | nan | 166.7 | 23.9 | 0.0 | 1.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 379 | Lying | Sitting | nan | 167.8 | 23.9 | 0.0 | 1.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 380 | Lying | Sitting | nan | 166.6 | 24.1 | 0.0 | 5.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 381 | Lying | Sitting | nan | 168.3 | 24.2 | 0.1 | 1.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 382 | Lying | Sitting | nan | 168.0 | 23.7 | 0.1 | 15.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 383 | Lying | Sitting | nan | 171.3 | 23.5 | 0.0 | 6.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 384 | Lying | Sitting | nan | 172.5 | 23.6 | 0.1 | 5.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 385 | Lying | Sitting | nan | 170.6 | 23.7 | 0.0 | 1.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 386 | Lying | Sitting | nan | 172.8 | 23.9 | 0.0 | 6.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 387 | Lying | Sitting | nan | 170.7 | 23.4 | 0.1 | 15.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 388 | Lying | Sitting | nan | 168.9 | 23.6 | 0.1 | 5.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 389 | Lying | Sitting | nan | 169.3 | 22.6 | 0.1 | 29.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 390 | Lying | Sitting | nan | 171.2 | 22.9 | 0.2 | 7.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 391 | Lying | Sitting | nan | 170.4 | 22.5 | 0.1 | 12.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 392 | Lying | Sitting | nan | 169.2 | 22.6 | 0.1 | 4.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 393 | Lying | Sitting | nan | 169.9 | 22.8 | 0.2 | 3.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 394 | Lying | Sitting | nan | 170.5 | 22.7 | 0.1 | 0.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 395 | Lying | Sitting | nan | 168.7 | 22.8 | 0.1 | 2.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 396 | Lying | Sitting | nan | 167.7 | 22.9 | 0.0 | 2.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 397 | Lying | Sitting | nan | 168.3 | 23.1 | 0.1 | 6.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 398 | Lying | Sitting | nan | 169.2 | 23.2 | 0.1 | 3.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 399 | Lying | Sitting | nan | 169.9 | 22.7 | 0.1 | 15.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 400 | Lying | Sitting | nan | 164.4 | 23.0 | 0.1 | 10.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 401 | Lying | Sitting | nan | nan | 22.6 | 0.4 | 12.0 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 402 | Lying | Sitting | nan | nan | 22.7 | 0.0 | 2.6 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 403 | Lying | Sitting | nan | nan | 22.4 | 0.1 | 10.1 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 404 | Lying | Sitting | nan | nan | 22.4 | 0.0 | 1.1 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 405 | Lying | Standing | nan | nan | 22.0 | 0.1 | 10.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 406 | Lying | Standing | nan | nan | 22.8 | 0.2 | 22.6 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 407 | Lying | Standing | nan | nan | 22.9 | 0.1 | 4.7 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 408 | Lying | Standing | nan | nan | 23.3 | 0.1 | 10.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 409 | Lying | Standing | nan | nan | 23.1 | 0.1 | 5.4 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 410 | Lying | Standing | nan | nan | 23.3 | 0.1 | 6.1 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 411 | Lying | Standing | nan | nan | 23.5 | 0.2 | 7.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 412 | Lying | Standing | nan | nan | 22.8 | 0.1 | 22.5 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 413 | Lying | Standing | nan | nan | 22.7 | 0.0 | 0.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 414 | Lying | Standing | nan | nan | 22.5 | 0.2 | 7.9 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 415 | Lying | Standing | nan | nan | 21.9 | 0.1 | 16.0 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 416 | Lying | Standing | nan | nan | 21.3 | 0.2 | 18.2 | 0.2 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 417 | Lying | Standing | nan | nan | 21.1 | 0.2 | 5.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 418 | Lying | Standing | nan | nan | 21.3 | 0.5 | 5.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 419 | Lying | Standing | nan | nan | 19.8 | 0.0 | 47.1 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 420 | Lying | Standing | nan | nan | 19.3 | 0.1 | 14.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 421 | Lying | Standing | nan | nan | 18.4 | 0.6 | 24.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 422 | Lying | Standing | nan | 164.4 | 18.8 | 0.0 | 9.6 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 423 | Lying | Standing | nan | 161.7 | 18.9 | 0.1 | 5.0 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 424 | Lying | Standing | nan | nan | 19.7 | 0.2 | 22.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Sitting|Sitting|Standing |
| 425 | Lying | Standing | nan | 165.7 | 20.3 | 0.1 | 19.0 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Standing|Sitting |
| 426 | Lying | Standing | nan | 166.5 | 20.7 | 0.2 | 10.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 427 | Lying | Standing | nan | 165.8 | 20.3 | 0.2 | 10.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 428 | Lying | Standing | nan | 165.7 | 19.8 | 0.0 | 15.8 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 429 | Lying | Sitting | nan | 167.0 | 20.3 | 0.2 | 13.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 430 | Lying | Sitting | nan | 167.1 | 20.1 | 0.2 | 3.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 431 | Lying | Sitting | nan | 169.8 | 19.0 | 0.3 | 33.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 432 | Lying | Sitting | nan | 171.1 | 18.6 | 0.1 | 12.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 433 | Lying | Sitting | nan | 171.7 | 18.8 | 0.0 | 6.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 434 | Lying | Sitting | nan | nan | 19.2 | 0.2 | 12.9 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 435 | Lying | Sitting | nan | nan | 18.6 | 0.4 | 20.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 436 | Lying | Sitting | nan | nan | 19.5 | 0.2 | 26.5 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 437 | Lying | Sitting | nan | nan | 19.4 | 0.1 | 2.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 438 | Lying | Standing | nan | nan | 19.2 | 0.2 | 4.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 439 | Lying | Standing | nan | nan | 20.4 | 0.2 | 35.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 440 | Lying | Standing | nan | 168.9 | 20.2 | 0.1 | 7.2 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 441 | Lying | Standing | nan | 167.8 | 20.5 | 0.2 | 9.8 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 442 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Standing|Sitting|Sitting|Unknown |
| 443 | Lying | Standing | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Standing|Sitting|Sitting|Unknown|Unknown |
| 444 | Lying | Standing | nan | 162.3 | 24.7 | 1.3 | 41.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Unknown|Unknown|Sitting |
| 445 | Lying | Standing | nan | 168.3 | 12.4 | 3.3 | 366.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Unknown|Unknown|Sitting|Sitting |
| 446 | Lying | Standing | nan | 165.0 | 18.1 | 0.9 | 170.6 | 0.2 | 0.3 | 0.1 | F | F | Unknown|Unknown|Sitting|Sitting|Sitting |
| 447 | Lying | Standing | nan | 168.7 | 20.4 | 0.1 | 67.3 | 0.2 | 0.3 | 0.1 | F | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 448 | Lying | Sitting | nan | 169.9 | 20.3 | 0.1 | 3.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 449 | Lying | Sitting | nan | 171.4 | 21.1 | 0.2 | 23.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 450 | Lying | Sitting | nan | 169.9 | 21.8 | 0.2 | 23.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 451 | Lying | Sitting | nan | 169.7 | 21.5 | 0.1 | 9.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 452 | Lying | Sitting | nan | 172.3 | 20.1 | 0.2 | 44.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 453 | Lying | Sitting | nan | 172.1 | 19.7 | 0.2 | 11.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 454 | Lying | Sitting | nan | 171.8 | 19.9 | 0.2 | 5.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 455 | Lying | Sitting | nan | 171.0 | 20.0 | 0.1 | 2.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 456 | Lying | Sitting | nan | 169.6 | 20.0 | 0.1 | 1.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 457 | Lying | Sitting | nan | 169.3 | 20.2 | 0.1 | 6.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 458 | Lying | Sitting | nan | 164.9 | 21.0 | 0.2 | 21.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 459 | Lying | Sitting | nan | 165.5 | 20.7 | 0.1 | 6.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 460 | Lying | Sitting | nan | 165.4 | 20.7 | 0.1 | 2.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 461 | Lying | Sitting | nan | 164.7 | 20.6 | 0.0 | 3.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 462 | Lying | Sitting | nan | 162.8 | 20.7 | 0.0 | 5.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 463 | Lying | Sitting | nan | 162.8 | 20.5 | 0.0 | 6.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 464 | Lying | Sitting | nan | 164.7 | 19.9 | 0.1 | 18.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 465 | Lying | Sitting | nan | 166.4 | 19.6 | 0.1 | 9.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 466 | Lying | Sitting | nan | 166.2 | 20.0 | 0.0 | 12.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 467 | Lying | Sitting | nan | 166.9 | 19.9 | 0.1 | 1.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 468 | Lying | Sitting | nan | 167.0 | 20.2 | 0.0 | 7.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 469 | Lying | Sitting | nan | 166.7 | 20.1 | 0.1 | 1.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 470 | Lying | Sitting | nan | 166.3 | 19.6 | 0.2 | 15.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 471 | Lying | Sitting | nan | 166.1 | 18.9 | 0.2 | 20.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 472 | Lying | Sitting | nan | 168.1 | 18.9 | 0.0 | 2.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 473 | Lying | Sitting | nan | 168.1 | 19.2 | 0.1 | 9.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 474 | Lying | Sitting | nan | 169.3 | 19.7 | 0.4 | 14.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 475 | Lying | Sitting | nan | 170.6 | 19.6 | 0.1 | 0.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 476 | Lying | Sitting | nan | 170.6 | 19.9 | 0.1 | 6.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 477 | Lying | Sitting | nan | 169.7 | 19.8 | 0.1 | 0.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 478 | Lying | Sitting | nan | 170.3 | 20.2 | 0.1 | 12.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 479 | Lying | Sitting | nan | 159.4 | 21.0 | 0.2 | 22.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 480 | Lying | Sitting | nan | 160.3 | 21.0 | 0.0 | 0.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 481 | Lying | Sitting | nan | 161.1 | 21.2 | 0.2 | 7.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 482 | Lying | Sitting | nan | 159.5 | 21.0 | 0.1 | 6.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 483 | Lying | Sitting | nan | 160.3 | 21.2 | 0.1 | 6.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 484 | Lying | Sitting | nan | 159.7 | 20.7 | 0.0 | 16.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 485 | Lying | Sitting | nan | 160.0 | 21.3 | 0.2 | 18.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 486 | Lying | Sitting | nan | nan | 21.0 | 0.1 | 9.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 487 | Lying | Sitting | nan | 155.3 | 20.8 | 0.1 | 4.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 488 | Lying | Sitting | nan | 155.6 | 20.5 | 0.1 | 7.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 489 | Lying | Sitting | nan | 156.9 | 20.9 | 0.2 | 10.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 490 | Lying | Sitting | nan | 160.4 | 21.2 | 0.1 | 10.2 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 491 | Lying | Sitting | nan | 160.2 | 20.9 | 0.3 | 9.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 492 | Lying | Sitting | nan | 163.6 | 20.8 | 0.0 | 3.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 493 | Lying | Sitting | nan | 163.7 | 20.7 | 0.2 | 4.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 494 | Lying | Sitting | nan | 165.1 | 20.2 | 0.0 | 12.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 495 | Lying | Sitting | nan | 166.6 | 20.1 | 0.4 | 4.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 496 | Lying | Sitting | nan | 168.3 | 19.4 | 0.1 | 22.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 497 | Lying | Sitting | nan | 169.3 | 19.2 | 0.1 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 498 | Lying | Sitting | nan | 171.4 | 18.6 | 0.1 | 17.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 499 | Lying | Sitting | nan | 171.4 | 18.5 | 0.0 | 3.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 500 | Lying | Sitting | nan | 171.4 | 18.6 | 0.1 | 2.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 501 | Lying | Sitting | nan | 171.6 | 18.7 | 0.1 | 5.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 502 | Lying | Sitting | nan | 168.7 | 18.6 | 0.1 | 4.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 503 | Lying | Sitting | nan | 169.1 | 18.2 | 0.0 | 11.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 504 | Lying | Sitting | nan | 170.5 | 17.5 | 0.0 | 21.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 505 | Lying | Sitting | nan | 167.3 | 18.6 | 0.2 | 34.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 506 | Lying | Sitting | nan | 166.9 | 18.9 | 0.2 | 8.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 507 | Lying | Sitting | nan | 167.5 | 18.8 | 0.0 | 1.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 508 | Lying | Sitting | nan | 164.1 | 18.8 | 0.1 | 0.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 509 | Lying | Sitting | nan | 165.4 | 19.3 | 0.2 | 14.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 510 | Lying | Sitting | nan | 166.9 | 19.2 | 0.1 | 2.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 511 | Lying | Sitting | nan | 167.5 | 18.8 | 0.1 | 13.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 512 | Lying | Sitting | nan | 167.5 | 18.8 | 0.0 | 1.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 513 | Lying | Sitting | nan | 170.3 | 18.5 | 0.1 | 9.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 514 | Lying | Sitting | nan | 169.1 | 18.7 | 0.0 | 7.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 515 | Lying | Sitting | nan | 170.2 | 18.3 | 0.1 | 14.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 516 | Lying | Sitting | nan | 168.9 | 18.5 | 0.1 | 6.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 517 | Lying | Sitting | nan | 169.7 | 19.3 | 0.4 | 24.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 518 | Lying | Sitting | nan | 167.5 | 19.4 | 0.1 | 3.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 519 | Lying | Sitting | nan | 163.8 | 19.9 | 0.4 | 14.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 520 | Lying | Sitting | nan | nan | 19.4 | 0.5 | 13.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 521 | Lying | Sitting | nan | nan | 19.0 | 0.2 | 12.5 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 522 | Lying | Sitting | nan | nan | 18.9 | 0.1 | 5.0 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 523 | Lying | Sitting | nan | nan | 19.5 | 0.3 | 20.1 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 524 | Lying | Standing | nan | nan | 19.5 | 0.1 | 1.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 525 | Lying | Standing | nan | nan | 19.7 | 0.1 | 6.5 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 526 | Lying | Standing | nan | nan | 19.3 | 0.1 | 12.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 527 | Lying | Standing | nan | nan | 19.5 | 0.2 | 6.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 528 | Lying | Standing | nan | nan | 19.8 | 0.1 | 10.1 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 529 | Lying | Standing | nan | nan | 20.0 | 0.2 | 6.1 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 530 | Lying | Standing | nan | nan | 20.1 | 0.2 | 1.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 531 | Lying | Standing | nan | nan | 20.4 | 0.2 | 8.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 532 | Lying | Standing | nan | nan | 20.5 | 0.1 | 2.5 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 533 | Lying | Standing | nan | nan | 20.7 | 0.1 | 5.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 534 | Lying | Standing | nan | nan | 19.9 | 0.5 | 21.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 535 | Lying | Standing | nan | nan | 20.1 | 0.3 | 3.5 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 536 | Lying | Standing | nan | nan | 20.0 | 0.0 | 0.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 537 | Lying | Standing | nan | 169.8 | 20.0 | 0.0 | 0.2 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 538 | Lying | Standing | nan | 169.1 | 20.2 | 0.0 | 6.3 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 539 | Lying | Standing | nan | 169.8 | 20.3 | 0.0 | 1.3 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 540 | Lying | Standing | nan | 170.8 | 20.3 | 0.0 | 0.0 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 541 | Lying | Sitting | nan | 170.4 | 21.0 | 0.0 | 19.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 542 | Lying | Sitting | nan | 169.0 | 21.1 | 0.0 | 3.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 543 | Lying | Sitting | nan | 168.6 | 21.2 | 0.1 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 544 | Lying | Sitting | nan | 168.0 | 21.4 | 0.1 | 4.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 545 | Lying | Sitting | nan | 167.5 | 21.4 | 0.1 | 0.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 546 | Lying | Sitting | nan | 166.5 | 21.1 | 0.1 | 10.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 547 | Lying | Sitting | nan | 159.3 | 20.7 | 0.1 | 12.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 548 | Lying | Sitting | nan | 158.0 | 20.3 | 0.3 | 11.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 549 | Lying | Sitting | nan | 157.9 | 20.9 | 0.3 | 17.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 550 | Lying | Sitting | nan | 151.0 | 20.7 | 0.2 | 6.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 551 | Lying | Sitting | nan | 154.3 | 19.4 | 0.2 | 38.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 552 | Lying | Sitting | nan | 154.4 | 19.5 | 0.3 | 3.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 553 | Lying | Sitting | nan | 155.3 | 19.4 | 0.0 | 4.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 554 | Lying | Sitting | nan | 156.3 | 19.4 | 0.0 | 0.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 555 | Lying | Sitting | nan | 161.6 | 18.5 | 0.1 | 25.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 556 | Lying | Sitting | nan | 161.4 | 18.8 | 0.2 | 8.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 557 | Lying | Sitting | nan | 160.0 | 18.7 | 0.1 | 2.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 558 | Lying | Sitting | nan | 160.0 | 19.6 | 0.2 | 26.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 559 | Lying | Sitting | nan | 163.8 | 19.2 | 0.0 | 12.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 560 | Lying | Sitting | nan | 162.5 | 19.6 | 0.1 | 11.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 561 | Lying | Sitting | nan | 161.1 | 19.4 | 0.1 | 4.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 562 | Lying | Sitting | nan | 156.9 | 19.4 | 0.2 | 0.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 563 | Lying | Sitting | nan | 156.0 | 19.8 | 0.2 | 12.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 564 | Lying | Sitting | nan | nan | 20.8 | 0.5 | 28.2 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 565 | Lying | Sitting | nan | nan | 21.1 | 0.1 | 11.2 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 566 | Lying | Sitting | nan | nan | 21.1 | 0.1 | 2.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 567 | Lying | Sitting | nan | nan | 20.8 | 0.1 | 6.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 568 | Lying | Standing | nan | nan | 20.5 | 0.3 | 8.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 569 | Lying | Standing | nan | nan | 20.4 | 0.2 | 5.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 570 | Lying | Standing | nan | nan | 20.3 | 0.1 | 2.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 571 | Lying | Standing | nan | nan | 19.5 | 0.2 | 22.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 572 | Lying | Standing | nan | nan | 19.3 | 0.1 | 6.6 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 573 | Lying | Standing | nan | nan | 19.0 | 0.1 | 8.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 574 | Lying | Standing | nan | nan | 18.4 | 0.3 | 17.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 575 | Lying | Standing | nan | 166.3 | 18.4 | 0.0 | 0.7 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 576 | Lying | Standing | nan | 165.9 | 18.4 | 0.3 | 2.0 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 577 | Lying | Standing | nan | 166.3 | 18.3 | 0.0 | 2.6 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 578 | Lying | Standing | nan | 166.2 | 18.7 | 0.0 | 13.1 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 579 | Lying | Sitting | nan | 165.2 | 19.0 | 0.0 | 7.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 580 | Lying | Sitting | nan | 164.6 | 19.1 | 0.1 | 3.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 581 | Lying | Sitting | nan | 164.5 | 19.5 | 0.1 | 12.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 582 | Lying | Sitting | nan | nan | 19.4 | 0.1 | 2.7 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 583 | Lying | Sitting | nan | nan | 19.8 | 0.6 | 12.4 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 584 | Lying | Sitting | nan | nan | 19.9 | 0.0 | 0.7 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 585 | Lying | Sitting | nan | nan | 19.9 | 0.0 | 1.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 586 | Lying | Standing | nan | nan | 19.6 | 0.1 | 8.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 587 | Lying | Standing | nan | nan | 19.7 | 0.0 | 1.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 588 | Lying | Standing | nan | nan | 19.3 | 0.0 | 9.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 589 | Lying | Standing | nan | nan | 18.5 | 0.2 | 24.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 590 | Lying | Standing | nan | nan | 19.4 | 0.2 | 24.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 591 | Lying | Standing | nan | nan | 19.8 | 0.0 | 14.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 592 | Lying | Standing | nan | nan | 20.4 | 0.2 | 18.1 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 593 | Lying | Standing | nan | nan | 20.8 | 0.2 | 11.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 594 | Lying | Standing | nan | nan | 20.1 | 0.3 | 22.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 595 | Lying | Standing | nan | nan | 20.3 | 0.1 | 7.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 596 | Lying | Standing | nan | nan | 19.9 | 0.1 | 11.1 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 597 | Lying | Standing | nan | nan | 20.1 | 0.1 | 4.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 598 | Lying | Standing | nan | nan | 20.1 | 0.1 | 1.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 599 | Lying | Standing | nan | nan | 21.0 | 0.5 | 26.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 600 | Lying | Standing | nan | nan | 20.8 | 0.1 | 5.1 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 601 | Lying | Standing | nan | nan | 20.6 | 0.2 | 6.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 602 | Lying | Standing | nan | nan | 20.5 | 0.0 | 2.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 603 | Lying | Standing | nan | nan | 20.4 | 0.0 | 4.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 604 | Lying | Standing | nan | nan | 20.6 | 0.0 | 5.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 605 | Lying | Standing | nan | nan | 20.1 | 0.2 | 14.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 606 | Lying | Standing | nan | nan | 20.2 | 0.1 | 3.7 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 607 | Lying | Standing | nan | nan | 20.2 | 0.0 | 0.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 608 | Lying | Standing | nan | nan | 20.1 | 0.0 | 3.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 609 | Lying | Standing | nan | nan | 20.8 | 0.5 | 20.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 610 | Lying | Standing | nan | nan | 20.6 | 0.4 | 5.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 611 | Lying | Standing | nan | nan | 20.5 | 0.0 | 4.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 612 | Lying | Standing | nan | nan | 20.6 | 0.1 | 3.5 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 613 | Lying | Standing | nan | nan | 20.6 | 0.1 | 0.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 614 | Lying | Standing | nan | nan | 21.1 | 0.2 | 16.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 615 | Lying | Standing | nan | nan | 22.5 | 0.4 | 40.9 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 616 | Lying | Standing | nan | nan | 22.7 | 0.1 | 6.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 617 | Lying | Standing | nan | nan | 22.7 | 0.1 | 1.2 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 618 | Lying | Standing | nan | nan | 22.3 | 0.2 | 13.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 619 | Lying | Standing | nan | nan | 21.7 | 0.2 | 18.0 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 620 | Lying | Standing | nan | nan | 20.6 | 0.4 | 31.3 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 621 | Lying | Standing | nan | nan | 20.2 | 0.6 | 11.4 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 622 | Lying | Standing | nan | nan | 20.2 | 0.1 | 0.8 | 0.1 | 0.3 | 0.1 | T | F | Standing|Standing|Standing|Standing|Standing |
| 623 | Lying | Standing | nan | 166.2 | 20.4 | 0.0 | 5.6 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 624 | Lying | Standing | nan | 166.4 | 20.4 | 0.1 | 0.4 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 625 | Lying | Standing | nan | 167.8 | 20.0 | 0.1 | 12.9 | 0.2 | 0.3 | 0.1 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 626 | Lying | Standing | nan | 168.6 | 19.9 | 0.2 | 2.9 | 0.2 | 0.3 | 0.1 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 627 | Lying | Sitting | nan | 171.4 | 19.5 | 0.1 | 11.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 628 | Lying | Sitting | nan | 171.3 | 19.4 | 0.2 | 1.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 629 | Lying | Sitting | nan | 171.5 | 19.2 | 0.1 | 8.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 630 | Lying | Sitting | nan | 168.4 | 19.1 | 0.1 | 1.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 631 | Lying | Sitting | nan | 164.6 | 19.4 | 0.0 | 9.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 632 | Lying | Sitting | nan | 167.6 | 19.1 | 0.1 | 8.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 633 | Lying | Sitting | nan | 168.7 | 19.0 | 0.0 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 634 | Lying | Sitting | nan | 169.0 | 19.1 | 0.1 | 2.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 635 | Lying | Sitting | nan | 169.2 | 18.9 | 0.1 | 4.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 636 | Lying | Sitting | nan | 168.7 | 19.0 | 0.0 | 2.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 637 | Lying | Sitting | nan | 169.1 | 19.4 | 0.0 | 10.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 638 | Lying | Sitting | nan | 166.5 | 19.6 | 0.0 | 7.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 639 | Lying | Sitting | nan | 165.4 | 20.1 | 0.3 | 14.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 640 | Lying | Sitting | nan | 164.6 | 20.9 | 0.4 | 25.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 641 | Lying | Sitting | nan | 165.5 | 20.0 | 0.0 | 29.6 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 642 | Lying | Sitting | nan | 164.5 | 20.1 | 0.0 | 5.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 643 | Lying | Sitting | nan | 163.6 | 19.9 | 0.1 | 5.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 644 | Lying | Sitting | nan | 162.3 | 20.0 | 0.1 | 2.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 645 | Lying | Sitting | nan | 160.9 | 19.8 | 0.2 | 6.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 646 | Lying | Sitting | nan | 161.1 | 19.8 | 0.1 | 0.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 647 | Lying | Sitting | nan | 163.7 | 20.0 | 0.0 | 6.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 648 | Lying | Sitting | nan | 166.5 | 20.0 | 0.1 | 1.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 649 | Lying | Sitting | nan | 166.7 | 19.9 | 0.1 | 3.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 650 | Lying | Sitting | nan | 168.1 | 19.9 | 0.0 | 0.0 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 651 | Lying | Sitting | nan | 168.1 | 20.1 | 0.1 | 6.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 652 | Lying | Sitting | nan | 167.3 | 20.6 | 0.2 | 16.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 653 | Lying | Sitting | nan | 168.3 | 20.5 | 0.1 | 3.5 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 654 | Lying | Sitting | nan | 168.4 | 20.7 | 0.2 | 4.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 655 | Lying | Sitting | nan | 167.5 | 20.4 | 0.1 | 7.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 656 | Lying | Sitting | nan | 165.9 | 20.4 | 0.1 | 0.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 657 | Lying | Sitting | nan | 166.6 | 20.5 | 0.0 | 1.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 658 | Lying | Sitting | nan | 165.9 | 20.2 | 0.1 | 8.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 659 | Lying | Sitting | nan | 165.3 | 19.8 | 0.1 | 10.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Floor_medium_pace_lie (**posture<90%**)

**Posture accuracy:** 80.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 73.6%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 29 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 24 | 67 | 0 |

**Fall detection:** TP (latency 11 frames)

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 105 | Lying | Sitting | nan | 156.0 | 31.1 | 0.3 | 56.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 106 | Lying | Sitting | nan | 157.4 | 33.2 | 0.3 | 62.7 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 107 | Lying | Sitting | nan | 163.9 | 33.4 | 0.4 | 7.3 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 108 | Lying | Sitting | nan | 160.0 | 31.6 | 0.4 | 56.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 109 | Lying | Sitting | nan | 154.1 | 31.2 | 0.0 | 12.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 110 | Lying | Sitting | nan | 164.4 | 27.8 | 0.9 | 101.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 111 | Lying | Sitting | nan | 163.7 | 27.0 | 0.5 | 23.8 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 112 | Lying | Sitting | nan | 155.2 | 23.5 | 1.6 | 103.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 113 | Lying | Sitting | nan | 156.3 | 20.4 | 0.8 | 93.2 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 114 | Lying | Sitting | nan | 160.6 | 18.7 | 0.1 | 52.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 115 | Lying | Sitting | nan | 161.3 | 18.1 | 0.5 | 18.1 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 116 | Lying | Sitting | nan | 162.2 | 16.7 | 0.1 | 42.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 117 | Lying | Sitting | nan | 159.5 | 15.8 | 0.5 | 26.4 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 118 | Lying | Sitting | nan | 159.3 | 15.2 | 0.9 | 17.9 | 0.2 | 0.3 | 0.1 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 119 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 120 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Unknown|Unknown |
| 121 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Unknown|Unknown |
| 122 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 123 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 124 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 125 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 126 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 127 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 128 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |

---

## Floor_partly_lie_beside_bed (**posture<90%, false negative**)

**Posture accuracy:** 7.2%

**Per-class accuracy:**

- Standing: 9.6%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 10 | 35 | 15 | 44 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 35 |

**Fall detection:** FN

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
| 40 | Standing | Unknown | nan | nan | 30.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.1 | T | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 41 | Standing | Unknown | nan | nan | 27.4 | 0.2 | 77.9 | 0.3 | 0.3 | 0.1 | T | F | Unknown|Unknown|Unknown|Sitting|Standing |
| 42 | Standing | Unknown | nan | nan | 24.5 | 4.8 | 88.5 | 0.2 | 0.2 | 0.1 | T | F | Unknown|Unknown|Sitting|Standing|Standing |
| 43 | Standing | Unknown | nan | nan | 23.4 | 0.4 | 31.5 | 0.2 | 0.2 | 0.1 | T | F | Unknown|Sitting|Standing|Standing|Standing |
| 44 | Standing | Unknown | nan | nan | 22.8 | 2.5 | 17.4 | 0.2 | 0.2 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 55 | Standing | Sitting | nan | nan | 33.8 | 2.7 | 77.1 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 56 | Standing | Sitting | nan | nan | 36.5 | 4.2 | 81.2 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 57 | Standing | Sitting | nan | nan | 32.1 | 1.7 | 130.6 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 58 | Standing | Sitting | nan | nan | 28.6 | 2.1 | 104.6 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 59 | Standing | Sitting | nan | nan | 27.9 | 1.0 | 22.7 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 60 | Standing | Sitting | nan | nan | 27.6 | 0.2 | 8.0 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 61 | Standing | Sitting | nan | nan | 30.2 | 1.2 | 78.2 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Standing|Standing|Standing|Sitting |
| 62 | Standing | Sitting | nan | nan | 35.6 | 3.1 | 160.4 | 0.1 | 0.3 | 0.2 | T | F | Standing|Standing|Standing|Sitting|Sitting |
| 63 | Standing | Sitting | nan | nan | 40.0 | 1.6 | 133.3 | 0.1 | 0.3 | 0.2 | T | F | Standing|Standing|Sitting|Sitting|Sitting |
| 64 | Standing | Sitting | nan | nan | 37.7 | 1.4 | 70.7 | 0.1 | 0.3 | 0.2 | T | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 65 | Standing | Sitting | nan | nan | 37.2 | 0.9 | 14.4 | 0.1 | 0.3 | 0.2 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 66 | Standing | Sitting | nan | nan | 40.2 | 1.6 | 89.8 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 67 | Standing | Sitting | nan | nan | 41.9 | 1.7 | 51.6 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 68 | Standing | Sitting | nan | nan | 45.7 | 0.3 | 114.8 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 69 | Standing | Sitting | nan | nan | 46.7 | 1.0 | 28.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 70 | Standing | Sitting | nan | nan | 49.1 | 1.2 | 74.0 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 71 | Standing | Sitting | nan | nan | 48.8 | 1.1 | 8.8 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 72 | Standing | Sitting | nan | nan | 51.1 | 0.3 | 67.4 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 73 | Standing | Sitting | nan | nan | 49.6 | 1.3 | 44.2 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 74 | Standing | Sitting | nan | nan | 50.3 | 0.9 | 20.8 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 75 | Standing | Sitting | nan | nan | 44.7 | 3.2 | 167.8 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 76 | Standing | Sitting | nan | nan | 44.9 | 0.7 | 6.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 77 | Standing | Sitting | nan | nan | 44.3 | 0.6 | 17.1 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 78 | Standing | Sitting | nan | nan | 45.8 | 1.3 | 44.0 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 79 | Standing | Sitting | nan | nan | 48.5 | 1.7 | 79.0 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 80 | Standing | Sitting | nan | nan | 48.2 | 0.0 | 7.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 81 | Standing | Sitting | nan | nan | 49.7 | 0.7 | 45.7 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 82 | Standing | Sitting | nan | nan | 50.6 | 2.1 | 25.5 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Lying |
| 83 | Standing | Lying | nan | nan | 50.6 | 1.7 | 0.2 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Lying|Lying |
| 84 | Standing | Lying | nan | nan | 53.3 | 0.1 | 80.8 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Lying|Lying|Lying |
| 85 | Standing | Lying | nan | nan | 52.4 | 1.6 | 25.6 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Lying|Lying|Lying|Lying |
| 86 | Standing | Lying | nan | nan | 54.4 | 0.4 | 59.7 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 87 | Standing | Lying | nan | nan | 53.5 | 0.6 | 27.7 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 88 | Standing | Lying | nan | nan | 54.1 | 0.7 | 18.0 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 89 | Standing | Lying | nan | nan | 51.3 | 1.3 | 83.1 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 90 | Standing | Lying | nan | nan | 48.3 | 1.2 | 89.5 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 91 | Standing | Lying | nan | nan | 48.9 | 1.9 | 16.9 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 92 | Standing | Lying | nan | nan | 47.8 | 0.6 | 34.4 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 93 | Standing | Lying | nan | nan | 45.1 | 0.5 | 81.1 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Lying |
| 94 | Standing | Lying | nan | nan | 43.2 | 0.4 | 54.5 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Lying|Sitting |
| 95 | Standing | Lying | nan | nan | 40.8 | 0.4 | 73.0 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Lying|Sitting|Sitting |
| 96 | Standing | Lying | nan | nan | 39.0 | 1.9 | 53.0 | 0.2 | 0.3 | 0.1 | T | F | Lying|Lying|Sitting|Sitting|Sitting |
| 97 | Standing | Lying | nan | nan | 39.1 | 0.9 | 2.6 | 0.2 | 0.3 | 0.1 | T | F | Lying|Sitting|Sitting|Sitting|Sitting |
| 98 | Standing | Sitting | nan | nan | 35.8 | 0.2 | 99.6 | 0.2 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Standing | Sitting | nan | nan | 32.5 | 1.6 | 99.7 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Standing | Sitting | nan | nan | 32.5 | 1.3 | 0.2 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Standing | Sitting | nan | nan | 28.6 | 1.6 | 114.9 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 102 | Standing | Sitting | nan | nan | 27.5 | 1.0 | 33.5 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 103 | Standing | Sitting | nan | nan | 27.5 | 0.8 | 0.8 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 104 | Standing | Sitting | nan | nan | 26.7 | 1.4 | 25.3 | 0.1 | 0.3 | 0.1 | T | F | Sitting|Standing|Standing|Standing|Standing |
| 165 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 166 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 167 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 168 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 169 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 170 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 171 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 172 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 173 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 174 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 175 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 176 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 177 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 178 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 179 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 180 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 181 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 182 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 183 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 184 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 185 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 186 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 187 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 188 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 189 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 190 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 191 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 192 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 193 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 194 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 195 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 196 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 197 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 198 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 199 | Lying | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |

---

## Other_occluded_crouch (**posture<90%**)

**Posture accuracy:** 59.9%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: 49.1%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 59 | 0 | 0 | 0 |
| **Sitting** | 0 | 107 | 61 | 50 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 102 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 103 | Sitting | Unknown | nan | nan | 75.6 | 0.5 | 25.4 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Unknown|Unknown|Unknown|Lying |
| 104 | Sitting | Lying | nan | nan | 75.2 | 3.6 | 13.0 | 0.3 | 0.3 | 0.2 | T | F | Unknown|Unknown|Unknown|Lying|Lying |
| 105 | Sitting | Lying | nan | nan | 74.8 | 2.1 | 10.0 | 0.4 | 0.4 | 0.2 | T | F | Unknown|Unknown|Lying|Lying|Lying |
| 106 | Sitting | Lying | nan | nan | 75.7 | 1.4 | 26.5 | 0.3 | 0.3 | 0.2 | T | F | Unknown|Lying|Lying|Lying|Lying |
| 107 | Sitting | Lying | nan | nan | 75.7 | 0.4 | 0.3 | 0.4 | 0.4 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 108 | Sitting | Lying | nan | nan | 76.1 | 0.7 | 11.6 | 0.4 | 0.4 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 109 | Sitting | Lying | nan | nan | 75.3 | 1.4 | 24.5 | 0.3 | 0.3 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 110 | Sitting | Lying | nan | nan | 76.4 | 1.0 | 32.6 | 0.3 | 0.3 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 111 | Sitting | Lying | nan | nan | 76.8 | 1.0 | 10.7 | 0.3 | 0.3 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 112 | Sitting | Lying | nan | nan | 75.9 | 1.0 | 25.1 | 0.3 | 0.3 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 113 | Sitting | Lying | nan | nan | 75.6 | 0.7 | 8.2 | 0.4 | 0.4 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 114 | Sitting | Lying | nan | nan | 76.2 | 0.3 | 15.3 | 0.4 | 0.4 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 115 | Sitting | Lying | nan | nan | 78.3 | 0.1 | 64.1 | 0.4 | 0.4 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 116 | Sitting | Lying | nan | nan | 79.8 | 0.1 | 45.2 | 0.4 | 0.4 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 117 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Lying|Unknown |
| 118 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Unknown|Unknown |
| 119 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Unknown|Unknown|Unknown |
| 120 | Sitting | Lying | nan | nan | 76.8 | 7.6 | 22.4 | 0.1 | 0.2 | 0.3 | T | F | Lying|Unknown|Unknown|Unknown|Lying |
| 121 | Sitting | Lying | nan | nan | 78.4 | 0.7 | 47.0 | 0.1 | 0.2 | 0.3 | T | F | Unknown|Unknown|Unknown|Lying|Lying |
| 122 | Sitting | Lying | nan | nan | 80.6 | 1.0 | 67.8 | 0.1 | 0.2 | 0.3 | T | F | Unknown|Unknown|Lying|Lying|Lying |
| 123 | Sitting | Lying | nan | nan | 81.8 | 1.4 | 35.8 | 0.1 | 0.2 | 0.3 | T | F | Unknown|Lying|Lying|Lying|Lying |
| 124 | Sitting | Lying | nan | nan | 82.3 | 0.2 | 14.8 | 0.1 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 125 | Sitting | Lying | nan | nan | 83.2 | 1.3 | 26.8 | 0.1 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 126 | Sitting | Lying | nan | nan | 83.3 | 0.6 | 1.4 | 0.1 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 127 | Sitting | Lying | nan | nan | 83.9 | 0.2 | 20.4 | 0.1 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Sitting |
| 128 | Sitting | Lying | nan | nan | 84.4 | 0.1 | 14.3 | 0.1 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Sitting|Sitting |
| 129 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Sitting|Sitting|Unknown |
| 130 | Sitting | Lying | nan | nan | 84.4 | 3.8 | 0.1 | 0.2 | 0.2 | 0.3 | T | F | Lying|Sitting|Sitting|Unknown|Sitting |
| 131 | Sitting | Lying | nan | nan | 85.2 | 1.4 | 23.6 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 132 | Sitting | Lying | nan | nan | 86.4 | 1.1 | 36.6 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 133 | Sitting | Lying | nan | nan | 87.4 | 0.4 | 30.3 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 197 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 198 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 199 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 200 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 201 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 202 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 203 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 204 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 205 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 206 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 207 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 208 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 209 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 210 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 211 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 212 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 213 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 214 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 215 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 216 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 217 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 218 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 219 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 220 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 221 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 222 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 223 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 224 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 225 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 226 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 227 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 228 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 229 | Sitting | Unknown | nan | nan | 91.3 | 0.0 | 1.5 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 230 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Sitting|Unknown |
| 231 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Sitting|Unknown|Unknown |
| 232 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Unknown|Unknown |
| 233 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Unknown|Unknown|Unknown|Unknown |
| 234 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 235 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 236 | Sitting | Unknown | nan | nan | 92.9 | 0.9 | 6.8 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Unknown|Unknown|Unknown|Sitting |
| 237 | Sitting | Unknown | nan | nan | 92.4 | 1.1 | 16.7 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 238 | Sitting | Unknown | nan | nan | 91.7 | 1.2 | 18.8 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Unknown|Sitting|Sitting|Sitting |
| 239 | Sitting | Unknown | nan | nan | 92.2 | 1.0 | 12.9 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 240 | Sitting | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 241 | Sitting | Unknown | nan | nan | 94.1 | 1.5 | 29.0 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 242 | Sitting | Unknown | nan | nan | 94.0 | 0.9 | 4.1 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 243 | Sitting | Unknown | nan | nan | 94.6 | 1.1 | 18.5 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 244 | Sitting | Unknown | nan | nan | 93.7 | 1.0 | 25.3 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 257 | Sitting | Lying | nan | nan | 84.0 | 0.3 | 15.3 | 0.4 | 0.4 | 0.3 | T | F | Sitting|Sitting|Sitting|Lying|Lying |
| 258 | Sitting | Lying | nan | nan | 83.7 | 0.5 | 7.9 | 0.4 | 0.4 | 0.3 | T | F | Sitting|Sitting|Lying|Lying|Lying |
| 259 | Sitting | Lying | nan | nan | 82.6 | 0.3 | 34.0 | 0.4 | 0.4 | 0.3 | T | F | Sitting|Lying|Lying|Lying|Lying |
| 260 | Sitting | Lying | nan | nan | 81.3 | 0.3 | 39.8 | 0.4 | 0.4 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 261 | Sitting | Lying | nan | nan | 81.1 | 0.8 | 3.9 | 0.4 | 0.4 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 262 | Sitting | Lying | nan | nan | 80.3 | 0.4 | 23.9 | 0.4 | 0.4 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 263 | Sitting | Lying | nan | nan | 80.6 | 1.4 | 9.0 | 0.4 | 0.4 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 264 | Sitting | Lying | nan | nan | 80.7 | 5.0 | 1.7 | 0.4 | 0.4 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 265 | Sitting | Lying | nan | nan | 82.3 | 1.6 | 49.6 | 0.4 | 0.4 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 266 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Lying|Unknown |
| 267 | Sitting | Lying | nan | nan | 79.1 | 4.6 | 48.7 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Unknown|Sitting |
| 268 | Sitting | Lying | nan | nan | 79.8 | 0.4 | 20.5 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Unknown|Sitting|Sitting |
| 269 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Unknown|Sitting|Sitting|Unknown |
| 270 | Sitting | Lying | nan | nan | 84.5 | 1.0 | 70.3 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Sitting|Sitting|Unknown|Sitting |
| 271 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Unknown|Sitting|Unknown |
| 272 | Sitting | Lying | nan | nan | 77.5 | 1.9 | 104.2 | 0.2 | 0.2 | 0.3 | T | F | Sitting|Unknown|Sitting|Unknown|Sitting |
| 273 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Unknown|Sitting|Unknown |
| 274 | Sitting | Lying | nan | nan | 89.3 | 2.6 | 176.1 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Unknown|Sitting|Unknown|Sitting |
| 275 | Sitting | Lying | nan | nan | 89.7 | 1.7 | 12.6 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Sitting|Unknown|Sitting|Sitting |
| 276 | Sitting | Lying | nan | nan | 89.6 | 0.4 | 0.9 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 277 | Sitting | Lying | nan | nan | 89.8 | 1.3 | 4.5 | 0.3 | 0.3 | 0.3 | T | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 278 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Sitting|Unknown |
| 279 | Sitting | Lying | nan | nan | 94.4 | 1.2 | 68.4 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Unknown|Sitting |
| 280 | Sitting | Lying | nan | nan | 94.3 | 0.9 | 0.9 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Sitting|Unknown|Sitting|Sitting |
| 281 | Sitting | Lying | nan | nan | 94.2 | 0.1 | 4.2 | 0.3 | 0.3 | 0.3 | T | F | Sitting|Unknown|Sitting|Sitting|Sitting |
| 282 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Sitting|Sitting|Sitting|Unknown |
| 283 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Unknown|Unknown |
| 284 | Sitting | Lying | nan | nan | 85.4 | 0.8 | 87.5 | 0.4 | 0.4 | 0.3 | T | F | Sitting|Sitting|Unknown|Unknown|Sitting |
| 285 | Sitting | Lying | nan | nan | 86.1 | 0.5 | 20.4 | 0.4 | 0.4 | 0.3 | T | F | Sitting|Unknown|Unknown|Sitting|Sitting |
| 286 | Sitting | Lying | nan | nan | 87.4 | 0.5 | 37.1 | 0.4 | 0.4 | 0.3 | T | F | Unknown|Unknown|Sitting|Sitting|Sitting |
| 287 | Sitting | Lying | nan | nan | 87.2 | 1.3 | 4.0 | 0.4 | 0.4 | 0.3 | T | F | Unknown|Sitting|Sitting|Sitting|Sitting |

---

## Other_occluded_stand

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 198 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

_None_

---

## Other_sit_desk (**posture<90%**)

**Posture accuracy:** 80.1%

**Per-class accuracy:**

- Standing: 70.6%
- Sitting: 100.0%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 84 | 29 | 0 | 6 |
| **Sitting** | 0 | 57 | 0 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** -

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown |
| 2 | Standing | Unknown | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown |
| 3 | Standing | Unknown | nan | nan | 22.9 | 0.0 | 0.0 | 0.4 | 0.4 | 0.2 | T | F | Unknown|Unknown|Standing |
| 4 | Standing | Unknown | nan | nan | 21.6 | 1.9 | 39.0 | 0.4 | 0.4 | 0.2 | T | F | Unknown|Unknown|Standing|Standing |
| 5 | Standing | Unknown | nan | nan | 20.5 | 0.4 | 30.7 | 0.4 | 0.4 | 0.2 | T | F | Unknown|Unknown|Standing|Standing|Standing |
| 6 | Standing | Unknown | nan | nan | 19.8 | 1.8 | 22.0 | 0.4 | 0.4 | 0.2 | T | F | Unknown|Standing|Standing|Standing|Standing |
| 36 | Standing | Sitting | nan | 158.3 | 17.2 | 2.1 | 121.5 | 0.4 | 0.5 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 37 | Standing | Sitting | 161.2 | 157.7 | 15.6 | 1.8 | 49.8 | 0.4 | 0.5 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 38 | Standing | Sitting | 166.4 | 148.2 | 18.5 | 2.0 | 87.4 | 0.3 | 0.5 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 39 | Standing | Sitting | 165.2 | 152.1 | 19.3 | 2.0 | 24.8 | 0.3 | 0.5 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 40 | Standing | Sitting | 163.9 | 149.2 | 16.8 | 1.0 | 74.9 | 0.3 | 0.5 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 96 | Standing | Sitting | nan | nan | 34.2 | 0.4 | 8.6 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 97 | Standing | Sitting | nan | nan | 35.0 | 0.3 | 25.0 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 98 | Standing | Sitting | nan | nan | 33.9 | 0.5 | 32.4 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Standing | Sitting | nan | nan | 34.0 | 0.6 | 1.0 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Standing | Sitting | nan | nan | 32.2 | 0.7 | 51.6 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Standing | Sitting | nan | nan | 32.0 | 0.1 | 6.2 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 102 | Standing | Sitting | nan | nan | 32.5 | 0.0 | 13.5 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 103 | Standing | Sitting | nan | nan | 33.5 | 0.1 | 32.2 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 104 | Standing | Sitting | nan | nan | 33.7 | 0.4 | 4.7 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 105 | Standing | Sitting | nan | nan | 34.9 | 0.1 | 37.0 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 106 | Standing | Sitting | nan | nan | 35.2 | 0.1 | 6.8 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 107 | Standing | Sitting | nan | nan | 35.8 | 0.2 | 19.7 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 108 | Standing | Sitting | nan | nan | 37.3 | 0.2 | 44.7 | 0.2 | 0.5 | 0.4 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 109 | Standing | Sitting | 135.2 | 128.0 | 39.2 | 0.1 | 56.5 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 110 | Standing | Sitting | 138.3 | 125.1 | 41.0 | 0.2 | 54.3 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 111 | Standing | Sitting | 128.9 | 114.5 | 43.0 | 0.5 | 59.7 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 112 | Standing | Sitting | 114.6 | 102.2 | 46.5 | 0.4 | 106.1 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 113 | Standing | Sitting | 99.5 | 89.9 | 49.4 | 1.0 | 87.2 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 114 | Standing | Sitting | 83.8 | 87.2 | 54.2 | 0.1 | 143.7 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 115 | Standing | Sitting | 92.5 | 91.0 | 55.2 | 0.4 | 30.5 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 116 | Standing | Sitting | 105.8 | 96.1 | 55.1 | 0.2 | 5.2 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 117 | Standing | Sitting | 96.6 | 84.0 | 59.0 | 2.7 | 116.7 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 118 | Standing | Sitting | 109.2 | 82.7 | 61.1 | 1.7 | 63.6 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 119 | Standing | Sitting | 105.9 | 89.3 | 53.6 | 4.6 | 224.7 | 0.2 | 0.5 | 0.4 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |

---

## Other_walk_out_and_back (**posture<90%, false positive**)

**Posture accuracy:** 56.6%

**Per-class accuracy:**

- Standing: 67.7%
- Sitting: 44.3%
- Lying: nan%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 113 | 5 | 49 | 0 |
| **Sitting** | 0 | 66 | 83 | 0 |
| **Lying** | 0 | 0 | 0 | 0 |

**Fall detection:** FP frames [170, 171, 172, 173, 174]

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 114 | Standing | Sitting | 163.4 | 46.0 | 154.8 | 1.0 | 720.0 | 0.1 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 115 | Standing | Sitting | 163.9 | 41.6 | 154.5 | 0.4 | 10.5 | 0.1 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 116 | Standing | Sitting | 166.4 | 35.5 | 158.6 | 0.5 | 121.0 | 0.1 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 117 | Standing | Sitting | 168.0 | 27.3 | 163.9 | 0.3 | 159.9 | 0.1 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 118 | Standing | Sitting | 163.6 | 21.6 | 166.9 | 0.2 | 87.9 | 0.1 | 0.2 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 134 | Sitting | Lying | nan | nan | 177.3 | 0.5 | 2.7 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Unknown|Sitting|Sitting |
| 135 | Sitting | Lying | nan | nan | 175.8 | 1.6 | 43.9 | 0.2 | 0.2 | 0.3 | T | F | Lying|Unknown|Sitting|Sitting|Lying |
| 136 | Sitting | Lying | nan | nan | 173.0 | 1.1 | 86.0 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Sitting|Sitting|Lying|Lying |
| 137 | Sitting | Lying | nan | nan | 169.4 | 1.1 | 105.4 | 0.2 | 0.2 | 0.2 | T | F | Sitting|Sitting|Lying|Lying|Lying |
| 138 | Sitting | Lying | nan | nan | 167.0 | 1.5 | 72.9 | 0.2 | 0.2 | 0.2 | T | F | Sitting|Lying|Lying|Lying|Lying |
| 139 | Sitting | Lying | nan | nan | 165.8 | 1.1 | 36.5 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 140 | Sitting | Lying | nan | nan | 164.1 | 0.8 | 50.6 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 141 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Lying|Unknown |
| 142 | Sitting | Lying | nan | nan | 160.1 | 0.9 | 58.9 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Unknown|Lying |
| 143 | Sitting | Lying | nan | nan | 160.1 | 0.6 | 0.7 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Unknown|Lying|Lying |
| 144 | Sitting | Lying | nan | nan | 160.1 | 1.1 | 0.0 | 0.2 | 0.2 | 0.2 | T | F | Lying|Unknown|Lying|Lying|Lying |
| 145 | Sitting | Lying | nan | nan | 160.8 | 1.7 | 21.0 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Lying|Lying|Lying|Lying |
| 146 | Sitting | Lying | nan | nan | 158.9 | 1.5 | 57.7 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 147 | Sitting | Lying | nan | nan | 161.0 | 0.7 | 61.5 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 148 | Sitting | Lying | nan | nan | 161.1 | 0.6 | 5.2 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 149 | Sitting | Lying | nan | nan | 165.1 | 1.2 | 117.2 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 150 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Lying|Unknown |
| 151 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Unknown|Unknown |
| 152 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Unknown|Unknown|Unknown |
| 153 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Unknown|Unknown|Unknown|Unknown |
| 154 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 155 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 156 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 157 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 158 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 159 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 160 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 161 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 162 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 163 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 164 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 165 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 166 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 167 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 168 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 169 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Unknown|Unknown|Unknown|Unknown|Unknown |
| 170 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 171 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 172 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 173 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 174 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 175 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 176 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 177 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 178 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 179 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 180 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 181 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 182 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 183 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 184 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 185 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 186 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 187 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 188 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 189 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 190 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 191 | Sitting | Lying | nan | nan | 174.7 | 0.1 | 6.9 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Unknown|Unknown|Unknown|Lying |
| 192 | Sitting | Lying | nan | nan | 173.4 | 0.3 | 39.2 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Unknown|Unknown|Lying|Lying |
| 193 | Sitting | Lying | nan | nan | 171.7 | 0.3 | 50.9 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Unknown|Lying|Lying|Lying |
| 194 | Sitting | Lying | nan | nan | 171.1 | 0.8 | 17.9 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Lying|Lying|Lying|Lying |
| 195 | Sitting | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Lying|Lying|Lying|Lying|Unknown |
| 196 | Sitting | Lying | nan | nan | 166.2 | 1.5 | 73.1 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Unknown|Lying |
| 197 | Sitting | Lying | nan | nan | 166.3 | 0.2 | 3.5 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Unknown|Lying|Lying |
| 198 | Sitting | Lying | nan | nan | 165.8 | 0.4 | 16.8 | 0.2 | 0.2 | 0.2 | T | F | Lying|Unknown|Lying|Lying|Lying |
| 199 | Sitting | Lying | nan | nan | 166.0 | 0.4 | 8.5 | 0.2 | 0.2 | 0.2 | T | F | Unknown|Lying|Lying|Lying|Lying |
| 200 | Sitting | Lying | nan | nan | 164.5 | 0.4 | 46.9 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 201 | Sitting | Lying | nan | nan | 165.1 | 0.2 | 19.0 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 202 | Sitting | Lying | nan | nan | 164.3 | 0.8 | 24.6 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 203 | Sitting | Lying | nan | nan | 169.1 | 0.5 | 144.4 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 204 | Sitting | Lying | nan | nan | 172.8 | 0.6 | 108.8 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 205 | Sitting | Lying | nan | nan | 174.9 | 0.5 | 63.2 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 206 | Sitting | Lying | nan | nan | 174.1 | 0.2 | 24.1 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 207 | Sitting | Lying | nan | nan | 173.4 | 0.4 | 20.8 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 208 | Sitting | Lying | nan | nan | 175.8 | 1.0 | 73.2 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 209 | Sitting | Lying | nan | nan | 179.8 | 1.1 | 118.6 | 0.2 | 0.2 | 0.2 | T | F | Lying|Lying|Lying|Lying|Lying |
| 210 | Sitting | Lying | nan | nan | 176.0 | 1.0 | 114.6 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 211 | Sitting | Lying | nan | nan | 174.6 | 0.7 | 41.4 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 212 | Sitting | Lying | nan | nan | 171.6 | 0.9 | 88.8 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Lying |
| 213 | Sitting | Lying | nan | nan | 169.5 | 0.7 | 61.3 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Lying|Sitting |
| 214 | Sitting | Lying | nan | nan | 167.2 | 0.7 | 69.7 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Lying|Sitting|Sitting |
| 215 | Sitting | Lying | nan | nan | 166.2 | 0.3 | 30.7 | 0.2 | 0.2 | 0.3 | T | F | Lying|Lying|Sitting|Sitting|Sitting |
| 216 | Sitting | Lying | nan | nan | 165.8 | 0.2 | 11.2 | 0.2 | 0.2 | 0.3 | T | F | Lying|Sitting|Sitting|Sitting|Sitting |
| 298 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 299 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 300 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 301 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 302 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 303 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 304 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 305 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 306 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 307 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 308 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 309 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 310 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 311 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 312 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 313 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 314 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 315 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 316 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 317 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 318 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 319 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 320 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 321 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 322 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 323 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 324 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 325 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 326 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 327 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 328 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 329 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 330 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 331 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 332 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 333 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 334 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 335 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 336 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 337 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 338 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 339 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 340 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 341 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 342 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 343 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 344 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 345 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |
| 346 | Standing | Lying | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | T | Unknown|Unknown|Unknown|Unknown|Unknown |

---

## Sofa_lie (**posture<90%, false negative**)

**Posture accuracy:** 57.9%

**Per-class accuracy:**

- Standing: 70.5%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 179 | 75 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 31 | 24 | 0 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 137 | Standing | Sitting | nan | nan | 8.4 | 0.4 | 9.2 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 138 | Standing | Sitting | nan | nan | 7.8 | 0.6 | 15.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 139 | Standing | Sitting | nan | nan | 8.7 | 0.5 | 24.9 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 140 | Standing | Sitting | 162.8 | 173.8 | 9.9 | 1.0 | 37.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 141 | Standing | Sitting | 164.5 | 174.6 | 9.3 | 0.5 | 18.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 142 | Standing | Sitting | 165.9 | 174.7 | 8.7 | 0.1 | 18.1 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 143 | Standing | Sitting | 167.8 | 174.1 | 8.8 | 0.4 | 3.7 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 187 | Standing | Sitting | 162.1 | 124.2 | 50.5 | 0.4 | 41.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 188 | Standing | Sitting | 156.8 | 118.4 | 51.7 | 0.5 | 36.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 189 | Standing | Sitting | 153.9 | 110.4 | 56.9 | 0.4 | 156.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 190 | Standing | Sitting | 151.3 | 110.1 | 56.2 | 0.7 | 23.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 191 | Standing | Sitting | 145.8 | 106.3 | 56.6 | 1.2 | 11.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 192 | Standing | Sitting | 145.1 | 105.5 | 57.4 | 0.2 | 25.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 193 | Standing | Sitting | 139.9 | 100.3 | 58.8 | 0.8 | 40.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 194 | Standing | Sitting | 138.4 | 92.5 | 63.6 | 0.7 | 145.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 195 | Standing | Sitting | 130.9 | 84.1 | 64.4 | 1.6 | 24.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 196 | Standing | Sitting | 144.0 | 93.5 | 63.6 | 0.3 | 23.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 197 | Standing | Sitting | 140.9 | 89.1 | 64.1 | 0.5 | 14.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 198 | Standing | Sitting | 142.2 | 92.0 | 62.3 | 0.3 | 52.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 199 | Standing | Sitting | 145.8 | 91.4 | 64.3 | 0.9 | 60.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 200 | Standing | Sitting | 150.1 | 96.1 | 62.0 | 0.6 | 70.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 201 | Standing | Sitting | 131.8 | 87.1 | 62.9 | 2.6 | 26.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 202 | Standing | Sitting | 125.7 | 80.5 | 61.9 | 1.2 | 29.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 203 | Standing | Sitting | 125.3 | 78.9 | 63.3 | 0.3 | 40.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 204 | Standing | Sitting | 123.3 | 79.4 | 61.3 | 0.6 | 58.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 205 | Standing | Sitting | 118.3 | 77.7 | 61.3 | 0.4 | 0.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 206 | Standing | Sitting | 99.4 | 78.0 | 61.3 | 0.3 | 1.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 207 | Standing | Sitting | 104.5 | 73.8 | 61.2 | 1.2 | 4.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 208 | Standing | Sitting | 105.0 | 70.6 | 59.6 | 2.0 | 48.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 209 | Standing | Sitting | 107.7 | 68.9 | 60.7 | 0.5 | 34.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 210 | Standing | Sitting | 102.6 | 67.9 | 60.6 | 0.7 | 3.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 211 | Standing | Sitting | 110.0 | 70.0 | 58.9 | 0.4 | 51.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 212 | Standing | Sitting | 103.5 | 60.0 | 62.1 | 1.1 | 96.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 213 | Standing | Sitting | 93.9 | 56.8 | 60.9 | 1.0 | 35.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 214 | Standing | Sitting | 93.5 | 55.2 | 60.4 | 0.2 | 17.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 215 | Standing | Sitting | 88.6 | 56.4 | 58.9 | 0.7 | 42.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 216 | Standing | Sitting | 97.4 | 60.2 | 55.9 | 0.5 | 92.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 217 | Standing | Sitting | 97.0 | 63.7 | 52.4 | 0.0 | 104.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 218 | Standing | Sitting | 98.8 | 68.4 | 48.7 | 0.2 | 111.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 219 | Standing | Sitting | 101.7 | 74.5 | 41.0 | 0.3 | 229.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 220 | Standing | Sitting | 107.5 | 80.2 | 35.7 | 0.1 | 158.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 221 | Standing | Sitting | 110.2 | 82.6 | 31.6 | 0.3 | 123.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 222 | Standing | Sitting | 111.3 | 86.9 | 28.0 | 0.2 | 109.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 223 | Standing | Sitting | 112.5 | 89.3 | 23.9 | 0.1 | 123.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 224 | Standing | Sitting | 110.5 | 88.5 | 21.3 | 0.5 | 75.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 225 | Standing | Sitting | 112.4 | 94.7 | 16.3 | 0.4 | 151.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 226 | Standing | Sitting | 110.8 | 93.0 | 16.0 | 0.2 | 8.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 227 | Standing | Sitting | 111.0 | 96.9 | 10.8 | 0.5 | 156.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 228 | Standing | Sitting | 111.0 | 101.8 | 5.9 | 0.8 | 144.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 229 | Standing | Sitting | 108.8 | 103.1 | 2.3 | 0.5 | 108.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 230 | Standing | Sitting | 111.5 | 107.2 | 1.2 | 0.4 | 34.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 231 | Standing | Sitting | 110.6 | 107.7 | 0.2 | 0.1 | 28.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 232 | Standing | Sitting | 111.5 | 110.8 | 2.2 | 0.1 | 60.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 233 | Standing | Sitting | 111.2 | 112.1 | 3.5 | 0.2 | 36.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 234 | Standing | Sitting | 113.3 | 113.4 | 4.2 | 0.2 | 21.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 235 | Standing | Sitting | 113.5 | 114.8 | 5.5 | 0.1 | 40.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 236 | Standing | Sitting | 115.2 | 116.3 | 7.0 | 0.1 | 42.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 237 | Standing | Sitting | 115.8 | 118.4 | 7.6 | 0.2 | 19.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 238 | Standing | Sitting | 119.4 | 120.0 | 7.7 | 0.2 | 1.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 239 | Standing | Sitting | 119.1 | 120.7 | 8.0 | 0.0 | 9.1 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 240 | Standing | Sitting | 121.4 | 121.3 | 8.0 | 0.1 | 2.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 241 | Standing | Sitting | 116.0 | 119.3 | 8.0 | 0.0 | 1.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 242 | Standing | Sitting | 117.0 | 119.4 | 7.8 | 0.0 | 5.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 243 | Standing | Sitting | 119.0 | 120.4 | 7.3 | 0.1 | 13.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 244 | Standing | Sitting | 122.2 | 123.5 | 7.1 | 0.0 | 6.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 245 | Standing | Sitting | 117.5 | 119.1 | 5.7 | 0.3 | 42.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 246 | Standing | Sitting | 114.7 | 117.3 | 5.1 | 0.2 | 17.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 247 | Standing | Sitting | 112.9 | 116.1 | 4.6 | 0.0 | 16.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 248 | Standing | Sitting | 112.4 | 115.5 | 4.0 | 0.0 | 17.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 249 | Standing | Sitting | 113.6 | 115.3 | 2.8 | 0.0 | 35.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 250 | Standing | Sitting | 114.6 | 114.3 | 1.8 | 0.1 | 30.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 251 | Standing | Sitting | 116.4 | 115.3 | 1.5 | 0.1 | 7.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 252 | Standing | Sitting | 114.7 | 113.4 | 0.4 | 0.2 | 32.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 253 | Standing | Sitting | 114.4 | 113.2 | 0.3 | 0.1 | 3.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 254 | Standing | Sitting | 113.4 | 112.5 | 0.4 | 0.1 | 4.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 360 | Lying | Sitting | 150.5 | 142.7 | 68.7 | 0.1 | 17.8 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 361 | Lying | Sitting | 151.7 | 143.5 | 68.1 | 0.3 | 18.3 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 362 | Lying | Sitting | 153.0 | 144.3 | 68.7 | 0.1 | 18.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 363 | Lying | Sitting | 156.5 | 146.9 | 68.1 | 0.1 | 18.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 364 | Lying | Standing | 157.7 | 147.6 | 67.8 | 0.1 | 8.8 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 365 | Lying | Standing | 158.4 | 148.4 | 67.8 | 0.0 | 2.4 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 366 | Lying | Standing | 159.6 | 149.2 | 67.6 | 0.1 | 5.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 367 | Lying | Standing | 159.8 | 149.3 | 67.6 | 0.1 | 0.9 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 368 | Lying | Standing | 160.5 | 150.1 | 67.5 | 0.0 | 1.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 369 | Lying | Standing | 160.7 | 150.7 | 67.8 | 0.1 | 7.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 370 | Lying | Standing | 159.0 | 149.1 | 67.5 | 0.3 | 9.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 371 | Lying | Standing | 159.6 | 150.1 | 67.7 | 0.2 | 5.8 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 372 | Lying | Standing | 160.2 | 150.4 | 67.7 | 0.2 | 2.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 373 | Lying | Standing | 160.0 | 149.5 | 67.1 | 0.1 | 18.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 374 | Lying | Standing | 158.4 | 148.2 | 66.6 | 0.1 | 15.7 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 375 | Lying | Standing | 158.2 | 147.6 | 66.4 | 0.0 | 6.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 376 | Lying | Standing | 157.7 | 147.2 | 66.1 | 0.1 | 9.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 377 | Lying | Standing | 157.4 | 146.7 | 65.7 | 0.0 | 11.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 378 | Lying | Standing | 157.6 | 147.2 | 65.9 | 0.0 | 5.6 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 379 | Lying | Standing | 157.9 | 147.4 | 66.0 | 0.1 | 3.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 380 | Lying | Standing | 158.3 | 148.2 | 66.8 | 0.2 | 24.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 381 | Lying | Standing | 158.4 | 149.1 | 67.6 | 0.2 | 24.4 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 382 | Lying | Standing | 158.5 | 149.7 | 67.8 | 0.0 | 6.5 | 0.4 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 383 | Lying | Standing | 158.3 | 150.1 | 68.1 | 0.1 | 8.1 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 384 | Lying | Standing | 158.3 | 150.4 | 68.2 | 0.1 | 1.9 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 385 | Lying | Standing | 159.0 | 151.1 | 68.4 | 0.1 | 7.4 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 386 | Lying | Standing | 159.4 | 151.3 | 68.3 | 0.1 | 2.9 | 0.4 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 387 | Lying | Standing | nan | 151.4 | 67.9 | 0.0 | 12.1 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 388 | Lying | Standing | 159.8 | 150.8 | 67.5 | 0.1 | 12.5 | 0.4 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 389 | Lying | Standing | nan | 150.6 | 67.3 | 0.0 | 5.9 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 390 | Lying | Standing | 159.8 | 149.8 | 67.0 | 0.1 | 10.5 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 391 | Lying | Standing | nan | 149.9 | 67.1 | 0.1 | 3.7 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 392 | Lying | Standing | nan | 149.6 | 67.1 | 0.0 | 1.2 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 393 | Lying | Standing | nan | 150.4 | 67.4 | 0.1 | 7.5 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 394 | Lying | Standing | nan | 150.2 | 67.4 | 0.0 | 0.1 | 0.3 | 0.4 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 395 | Lying | Sitting | nan | 150.9 | 67.8 | 0.1 | 11.2 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 396 | Lying | Sitting | nan | 151.1 | 67.7 | 0.0 | 0.6 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 397 | Lying | Sitting | nan | 151.2 | 67.7 | 0.1 | 0.2 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 398 | Lying | Sitting | nan | 151.8 | 68.0 | 0.0 | 6.8 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 399 | Lying | Sitting | nan | 152.4 | 67.8 | 0.1 | 3.6 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 400 | Lying | Sitting | nan | 152.5 | 67.9 | 0.0 | 2.2 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 401 | Lying | Sitting | nan | 152.4 | 68.0 | 0.0 | 2.6 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 402 | Lying | Sitting | nan | 153.0 | 68.2 | 0.0 | 5.7 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 403 | Lying | Sitting | nan | 152.7 | 68.0 | 0.1 | 5.8 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 404 | Lying | Sitting | nan | 152.9 | 68.1 | 0.0 | 2.9 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 405 | Lying | Sitting | nan | 153.7 | 68.4 | 0.1 | 9.6 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 406 | Lying | Sitting | nan | 153.5 | 68.2 | 0.1 | 7.2 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 407 | Lying | Sitting | nan | 152.8 | 68.0 | 0.0 | 6.6 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 408 | Lying | Sitting | nan | 152.4 | 67.9 | 0.0 | 0.6 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Sitting |
| 409 | Lying | Sitting | nan | 151.9 | 67.1 | 0.2 | 26.4 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 410 | Lying | Sitting | nan | 151.9 | 67.2 | 0.0 | 2.8 | 0.3 | 0.4 | 0.3 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 411 | Lying | Sitting | nan | 151.0 | 66.7 | 0.1 | 12.4 | 0.3 | 0.4 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Standing |
| 412 | Lying | Sitting | nan | 150.6 | 66.8 | 0.0 | 1.9 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 413 | Lying | Sitting | nan | 150.2 | 66.9 | 0.0 | 4.1 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 414 | Lying | Sitting | nan | 150.2 | 67.1 | 0.3 | 6.0 | 0.3 | 0.4 | 0.3 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |

---

## Sofa_lie_and_immediate_stand (**posture<90%, false negative**)

**Posture accuracy:** 43.0%

**Per-class accuracy:**

- Standing: 93.2%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 96 | 7 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 30 | 90 | 0 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 58 | Standing | Sitting | 129.0 | 134.4 | 16.2 | 0.2 | 113.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 59 | Standing | Sitting | 131.3 | 140.5 | 16.2 | 0.7 | 0.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 90 | Lying | Sitting | 115.0 | 99.6 | 39.5 | 0.1 | 26.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 91 | Lying | Sitting | 118.6 | 101.0 | 39.7 | 0.3 | 8.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 92 | Lying | Sitting | 120.8 | 99.2 | 40.6 | 0.2 | 25.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 93 | Lying | Sitting | 125.6 | 102.2 | 43.2 | 0.9 | 77.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 94 | Lying | Sitting | 132.0 | 109.3 | 46.0 | 0.7 | 85.1 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 95 | Lying | Sitting | 131.0 | 108.1 | 46.3 | 0.2 | 6.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 96 | Lying | Sitting | 127.4 | 106.2 | 46.3 | 0.1 | 2.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 97 | Lying | Sitting | 132.7 | 109.5 | 46.2 | 0.1 | 3.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 98 | Lying | Sitting | 136.4 | 111.6 | 45.5 | 0.2 | 23.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 99 | Lying | Sitting | 141.8 | 116.0 | 45.5 | 0.0 | 1.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 100 | Lying | Sitting | 143.9 | 116.7 | 44.5 | 0.3 | 30.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 101 | Lying | Sitting | 147.3 | 122.0 | 47.0 | 0.3 | 75.3 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 102 | Lying | Sitting | 140.3 | 119.8 | 48.3 | 0.6 | 39.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 103 | Lying | Sitting | 137.5 | 119.5 | 49.6 | 0.3 | 38.7 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 104 | Lying | Sitting | 139.7 | 124.1 | 51.7 | 0.3 | 61.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 105 | Lying | Sitting | 135.5 | 123.4 | 53.2 | 0.3 | 46.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 106 | Lying | Sitting | 133.4 | 124.2 | 54.8 | 0.2 | 47.7 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 107 | Lying | Sitting | 133.1 | 125.5 | 55.8 | 0.1 | 30.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 108 | Lying | Sitting | 130.5 | 125.0 | 56.9 | 0.2 | 30.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 109 | Lying | Sitting | nan | 126.1 | 58.4 | 0.4 | 45.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 110 | Lying | Sitting | nan | 124.4 | 59.8 | 0.4 | 44.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 111 | Lying | Sitting | nan | 123.4 | 60.6 | 0.2 | 21.7 | 0.2 | 0.3 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 112 | Lying | Sitting | nan | 126.2 | 62.0 | 0.3 | 42.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 113 | Lying | Sitting | nan | nan | 63.9 | 0.6 | 58.0 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 114 | Lying | Sitting | nan | nan | 64.2 | 0.2 | 9.6 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 115 | Lying | Sitting | nan | nan | 64.3 | 0.1 | 2.3 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 116 | Lying | Sitting | nan | nan | 64.5 | 0.2 | 6.6 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 117 | Lying | Sitting | nan | nan | 64.5 | 0.1 | 1.0 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 118 | Lying | Sitting | nan | nan | 63.6 | 0.6 | 26.6 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 119 | Lying | Sitting | nan | nan | 62.9 | 0.3 | 19.3 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 120 | Lying | Sitting | nan | nan | 62.8 | 0.1 | 4.6 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 121 | Lying | Sitting | nan | nan | 63.5 | 0.2 | 19.8 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 122 | Lying | Sitting | nan | nan | 63.3 | 0.1 | 3.5 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 123 | Lying | Sitting | nan | nan | 63.0 | 0.1 | 10.4 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 124 | Lying | Sitting | nan | nan | 62.6 | 0.1 | 11.7 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 125 | Lying | Sitting | nan | nan | 63.2 | 0.9 | 18.6 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 126 | Lying | Sitting | nan | nan | 63.4 | 0.1 | 5.9 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 127 | Lying | Sitting | nan | nan | 63.9 | 0.2 | 15.0 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 128 | Lying | Sitting | nan | 136.2 | 64.8 | 0.4 | 27.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 129 | Lying | Sitting | nan | 136.1 | 64.9 | 0.1 | 2.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 130 | Lying | Sitting | nan | nan | 65.3 | 0.0 | 13.1 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Standing|Standing|Sitting |
| 131 | Lying | Sitting | nan | nan | 66.0 | 0.2 | 19.9 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Standing|Standing|Sitting|Sitting |
| 132 | Lying | Sitting | nan | 142.2 | 67.2 | 0.2 | 35.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Sitting|Sitting|Standing |
| 133 | Lying | Sitting | nan | 144.1 | 68.2 | 0.2 | 30.6 | 0.3 | 0.3 | 0.3 | F | F | Standing|Sitting|Sitting|Standing|Standing |
| 134 | Lying | Sitting | nan | 145.9 | 68.5 | 0.1 | 9.1 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 135 | Lying | Sitting | nan | 146.0 | 68.4 | 0.0 | 4.5 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 136 | Lying | Standing | nan | 145.7 | 68.0 | 0.1 | 10.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Lying | Standing | nan | 146.0 | 68.1 | 0.1 | 2.7 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Lying | Standing | 149.0 | 146.1 | 68.1 | 0.1 | 1.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Lying | Standing | 149.9 | 145.7 | 68.1 | 0.0 | 1.7 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Lying | Standing | 148.9 | 144.9 | 67.9 | 0.0 | 4.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Lying | Standing | 148.2 | 144.8 | 67.9 | 0.0 | 0.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Lying | Standing | 149.9 | 144.9 | 67.6 | 0.1 | 9.9 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Lying | Standing | 152.4 | 145.5 | 67.4 | 0.1 | 7.4 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Lying | Standing | 156.0 | 146.7 | 67.2 | 0.1 | 5.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Lying | Standing | 156.9 | 147.0 | 67.0 | 0.0 | 4.4 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Lying | Standing | 157.3 | 147.0 | 67.1 | 0.0 | 1.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Lying | Standing | 157.2 | 147.1 | 67.0 | 0.1 | 1.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 148 | Lying | Standing | 156.0 | 147.3 | 67.0 | 0.1 | 0.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 149 | Lying | Standing | 155.2 | 146.7 | 66.8 | 0.0 | 7.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 150 | Lying | Standing | 154.3 | 146.6 | 67.1 | 0.1 | 9.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 151 | Lying | Standing | 152.9 | 145.6 | 67.1 | 0.2 | 0.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 152 | Lying | Standing | 151.5 | 144.8 | 67.1 | 0.0 | 1.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 153 | Lying | Standing | 150.1 | 144.2 | 67.2 | 0.0 | 3.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 154 | Lying | Standing | 150.7 | 143.9 | 67.3 | 0.0 | 1.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 155 | Lying | Standing | 149.2 | 142.0 | 67.0 | 0.1 | 7.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 156 | Lying | Standing | 147.5 | 139.2 | 66.4 | 0.2 | 18.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 157 | Lying | Standing | 146.0 | 137.1 | 65.8 | 0.1 | 17.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 158 | Lying | Standing | 146.3 | 137.5 | 64.8 | 0.1 | 30.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 159 | Lying | Standing | 141.3 | 134.6 | 64.6 | 0.1 | 7.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 160 | Lying | Standing | 138.9 | 131.1 | 64.2 | 0.1 | 10.9 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 161 | Lying | Standing | 132.5 | 126.0 | 63.9 | 0.1 | 9.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 162 | Lying | Standing | 124.0 | 116.3 | 63.7 | 0.0 | 6.9 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Sitting |
| 163 | Lying | Standing | 119.0 | 109.8 | 63.1 | 0.1 | 18.6 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Sitting|Sitting |
| 164 | Lying | Standing | 119.3 | 106.4 | 62.5 | 0.1 | 16.5 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Sitting|Sitting|Sitting |
| 165 | Lying | Standing | 118.3 | 103.0 | 62.4 | 0.4 | 3.3 | 0.2 | 0.3 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 166 | Lying | Sitting | 108.3 | 91.9 | 61.8 | 0.4 | 16.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 167 | Lying | Sitting | 104.5 | 90.1 | 62.6 | 0.4 | 23.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 168 | Lying | Sitting | 99.9 | 86.0 | 61.5 | 0.3 | 33.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 169 | Lying | Sitting | 95.1 | 81.4 | 61.3 | 0.2 | 5.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 170 | Lying | Sitting | 112.8 | 108.5 | 61.7 | 0.2 | 10.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 171 | Lying | Sitting | 130.9 | 122.3 | 61.9 | 0.5 | 5.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 172 | Lying | Sitting | 123.7 | 113.2 | 60.7 | 0.6 | 35.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 173 | Lying | Sitting | 112.8 | 108.0 | 60.0 | 0.4 | 21.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 174 | Lying | Sitting | 69.1 | 63.0 | 56.6 | 1.6 | 100.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 175 | Lying | Sitting | 55.3 | 61.8 | 54.9 | 1.1 | 51.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 176 | Lying | Sitting | 46.9 | 65.1 | 56.4 | 1.0 | 46.0 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 177 | Lying | Sitting | 66.0 | 84.3 | 55.5 | 3.4 | 28.4 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 178 | Lying | Sitting | 111.5 | 124.5 | 54.2 | 0.3 | 40.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 179 | Lying | Sitting | 134.3 | 147.2 | 51.2 | 1.1 | 87.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 180 | Lying | Sitting | 147.6 | 153.4 | 48.3 | 0.2 | 88.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 181 | Lying | Sitting | nan | 147.8 | 44.8 | 0.5 | 104.4 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Sitting |
| 182 | Lying | Sitting | nan | 149.1 | 42.4 | 0.1 | 71.8 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Standing|Sitting|Sitting |
| 183 | Lying | Sitting | nan | 150.7 | 41.4 | 0.4 | 29.7 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Standing|Sitting|Sitting|Sitting |
| 184 | Lying | Sitting | nan | 149.4 | 40.3 | 0.3 | 32.4 | 0.1 | 0.3 | 0.3 | F | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 185 | Lying | Sitting | nan | 149.5 | 39.5 | 0.2 | 25.5 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 186 | Lying | Sitting | nan | 147.6 | 36.5 | 0.2 | 88.7 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 187 | Lying | Sitting | nan | 146.8 | 35.9 | 0.2 | 19.1 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 188 | Lying | Sitting | nan | 143.3 | 34.8 | 1.2 | 32.7 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 189 | Lying | Sitting | 139.4 | 141.0 | 32.4 | 0.9 | 72.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 190 | Lying | Sitting | 137.0 | 129.3 | 33.4 | 1.1 | 30.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 191 | Lying | Sitting | 139.6 | 127.7 | 32.3 | 0.4 | 31.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 192 | Lying | Sitting | 108.1 | 97.2 | 32.0 | 0.5 | 10.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 193 | Lying | Sitting | 106.6 | 94.8 | 31.4 | 0.2 | 18.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 194 | Lying | Sitting | 111.4 | 101.1 | 30.5 | 0.2 | 25.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 195 | Lying | Sitting | 109.4 | 111.1 | 28.7 | 0.1 | 52.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 196 | Lying | Sitting | 112.5 | 128.0 | 23.7 | 1.4 | 151.9 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 197 | Lying | Sitting | 122.5 | 132.4 | 21.4 | 0.5 | 68.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 198 | Lying | Sitting | 127.8 | 134.6 | 20.8 | 0.0 | 17.4 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 199 | Lying | Sitting | 155.7 | 154.1 | 19.4 | 1.1 | 40.9 | 0.1 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 200 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Sitting|Standing|Unknown |
| 201 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Sitting|Standing|Unknown|Unknown |
| 202 | Lying | Sitting | nan | nan | nan | 0.0 | 0.0 | nan | nan | nan | T | F | Sitting|Standing|Unknown|Unknown|Unknown |
| 203 | Lying | Sitting | 143.0 | 121.8 | 3.2 | 2.0 | 121.8 | 0.1 | 0.3 | 0.2 | F | F | Standing|Unknown|Unknown|Unknown|Sitting |
| 204 | Lying | Sitting | 72.4 | 63.9 | 9.4 | 0.8 | 186.8 | 0.1 | 0.3 | 0.2 | F | F | Unknown|Unknown|Unknown|Sitting|Sitting |
| 205 | Lying | Sitting | 142.1 | 129.0 | 15.4 | 1.6 | 178.6 | 0.1 | 0.3 | 0.2 | F | F | Unknown|Unknown|Sitting|Sitting|Sitting |
| 206 | Lying | Sitting | 137.5 | 124.4 | 22.2 | 3.6 | 204.4 | 0.1 | 0.3 | 0.2 | F | F | Unknown|Sitting|Sitting|Sitting|Sitting |
| 207 | Lying | Sitting | nan | 124.1 | 23.2 | 1.0 | 29.3 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 208 | Lying | Sitting | nan | 139.5 | 27.2 | 1.0 | 121.6 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 209 | Lying | Sitting | nan | 136.0 | 32.8 | 1.2 | 167.3 | 0.1 | 0.3 | 0.2 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 272 | Standing | Sitting | nan | nan | 14.5 | 0.0 | 14.8 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 273 | Standing | Sitting | nan | nan | 14.7 | 0.2 | 8.1 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 274 | Standing | Sitting | nan | nan | 15.3 | 0.1 | 17.3 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Standing|Standing |
| 275 | Standing | Sitting | nan | nan | 16.1 | 0.1 | 25.3 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Standing|Standing|Standing |
| 276 | Standing | Sitting | nan | nan | 16.2 | 0.1 | 1.4 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Standing|Standing|Standing|Standing |

---

## Sofa_long_lie

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
| **Lying** | 0 | 0 | 666 | 0 |

**Fall detection:** TP (latency 79 frames)

**Mismatched frames:**

_None_

---

## Sofa_medium_pace_lie (**posture<90%, false negative**)

**Posture accuracy:** 44.6%

**Per-class accuracy:**

- Standing: 98.3%
- Sitting: nan%
- Lying: 0.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 58 | 1 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 36 | 35 | 0 | 0 |

**Fall detection:** FN

**Mismatched frames:**

| Frame | GT | Pred | knee | hip | torso | vel | angvel | body_h | eff_max_bh | hip_h | lbo | tlaf | recent_labels |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 59 | Standing | Sitting | 144.0 | 136.4 | 12.1 | 2.6 | 279.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 105 | Lying | Sitting | 140.9 | 107.9 | 43.2 | 0.4 | 1.3 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 106 | Lying | Sitting | 143.7 | 110.7 | 44.1 | 0.1 | 28.2 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 107 | Lying | Sitting | 146.5 | 113.8 | 44.9 | 0.2 | 23.4 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 108 | Lying | Sitting | 150.3 | 117.8 | 45.9 | 0.5 | 28.6 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 109 | Lying | Sitting | 160.6 | 124.9 | 46.1 | 0.2 | 6.5 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 110 | Lying | Sitting | 166.0 | 131.2 | 48.0 | 0.3 | 56.6 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 111 | Lying | Sitting | 178.2 | 144.4 | 51.2 | 0.7 | 95.3 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 112 | Lying | Sitting | nan | nan | 50.1 | 0.4 | 30.6 | 0.1 | 0.3 | 0.3 | T | F | Sitting|Sitting|Standing|Standing|Sitting |
| 113 | Lying | Sitting | nan | nan | 49.0 | 1.0 | 34.6 | 0.1 | 0.3 | 0.3 | T | F | Sitting|Standing|Standing|Sitting|Sitting |
| 114 | Lying | Sitting | nan | nan | 48.1 | 0.8 | 25.6 | 0.1 | 0.3 | 0.3 | T | F | Standing|Standing|Sitting|Sitting|Sitting |
| 115 | Lying | Sitting | nan | nan | 48.0 | 0.5 | 3.2 | 0.1 | 0.3 | 0.3 | T | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 116 | Lying | Sitting | nan | nan | 47.2 | 0.2 | 23.6 | 0.1 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 117 | Lying | Sitting | nan | 137.1 | 46.1 | 0.2 | 35.0 | 0.3 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Sitting|Standing |
| 118 | Lying | Sitting | nan | 132.9 | 43.8 | 0.2 | 67.7 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Sitting|Standing|Standing |
| 119 | Lying | Sitting | nan | 134.8 | 45.0 | 0.3 | 35.0 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Sitting|Standing|Standing|Standing |
| 120 | Lying | Sitting | nan | 134.5 | 45.0 | 0.0 | 1.8 | 0.2 | 0.3 | 0.3 | F | F | Sitting|Standing|Standing|Standing|Standing |
| 121 | Lying | Standing | nan | 134.3 | 46.0 | 0.1 | 27.7 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 122 | Lying | Standing | nan | 132.3 | 46.7 | 0.1 | 20.9 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 123 | Lying | Standing | nan | 133.2 | 48.6 | 0.2 | 57.4 | 0.2 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 124 | Lying | Standing | nan | 137.6 | 52.9 | 0.2 | 129.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 125 | Lying | Standing | nan | 141.5 | 56.5 | 0.5 | 109.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 126 | Lying | Standing | nan | 145.2 | 59.0 | 0.1 | 75.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 127 | Lying | Standing | nan | 148.0 | 60.0 | 0.9 | 29.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 128 | Lying | Standing | 165.4 | 149.1 | 60.9 | 0.3 | 27.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 129 | Lying | Standing | 165.7 | 150.3 | 62.3 | 0.2 | 40.3 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 130 | Lying | Standing | 166.7 | 149.9 | 61.5 | 0.5 | 23.8 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 131 | Lying | Standing | 167.4 | 151.2 | 62.2 | 0.1 | 23.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 132 | Lying | Standing | 165.5 | 150.7 | 62.6 | 0.1 | 10.4 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 133 | Lying | Standing | 164.7 | 151.2 | 63.5 | 0.1 | 29.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 134 | Lying | Standing | 163.7 | 153.0 | 65.4 | 0.3 | 56.4 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 135 | Lying | Standing | 163.6 | 154.6 | 66.9 | 0.3 | 43.9 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 136 | Lying | Standing | 162.2 | 156.8 | 69.3 | 0.6 | 72.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 137 | Lying | Standing | 162.2 | 158.2 | 70.5 | 0.2 | 35.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 138 | Lying | Standing | 161.6 | 158.4 | 70.6 | 0.2 | 4.8 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 139 | Lying | Standing | 161.6 | 159.5 | 71.7 | 0.5 | 32.6 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 140 | Lying | Standing | 162.1 | 160.7 | 72.7 | 0.6 | 28.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 141 | Lying | Standing | 162.5 | 160.3 | 72.1 | 0.1 | 16.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 142 | Lying | Standing | 164.3 | 160.6 | 71.6 | 0.3 | 14.6 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 143 | Lying | Standing | 165.1 | 158.7 | 70.2 | 0.3 | 43.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 144 | Lying | Standing | 165.7 | 158.4 | 69.5 | 0.3 | 20.6 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 145 | Lying | Standing | 167.4 | 159.2 | 69.2 | 0.2 | 8.0 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 146 | Lying | Standing | 170.5 | 160.9 | 69.2 | 0.0 | 1.4 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 147 | Lying | Standing | 173.1 | 162.0 | 68.9 | 0.1 | 8.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 148 | Lying | Standing | 173.3 | 161.7 | 68.7 | 0.0 | 6.2 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 149 | Lying | Standing | 172.8 | 161.6 | 68.6 | 0.2 | 5.1 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 150 | Lying | Standing | 173.2 | 162.0 | 68.3 | 0.0 | 7.5 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 151 | Lying | Standing | nan | 163.7 | 69.2 | 0.5 | 26.7 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 152 | Lying | Standing | nan | 163.5 | 69.4 | 0.3 | 6.8 | 0.3 | 0.3 | 0.3 | F | F | Standing|Standing|Standing|Standing|Standing |
| 153 | Lying | Standing | nan | nan | 69.3 | 0.1 | 2.5 | 0.2 | 0.3 | 0.3 | T | F | Standing|Standing|Standing|Standing|Sitting |
| 154 | Lying | Standing | nan | nan | 69.5 | 0.2 | 5.4 | 0.2 | 0.3 | 0.3 | T | F | Standing|Standing|Standing|Sitting|Sitting |
| 155 | Lying | Standing | nan | nan | 69.2 | 0.1 | 8.3 | 0.2 | 0.3 | 0.3 | T | F | Standing|Standing|Sitting|Sitting|Sitting |
| 156 | Lying | Standing | nan | nan | 69.1 | 0.1 | 5.2 | 0.2 | 0.3 | 0.3 | T | F | Standing|Sitting|Sitting|Sitting|Sitting |
| 157 | Lying | Sitting | nan | nan | 69.7 | 1.2 | 20.3 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 158 | Lying | Sitting | nan | nan | 69.6 | 0.1 | 4.1 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 159 | Lying | Sitting | nan | nan | 70.2 | 0.6 | 16.7 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 160 | Lying | Sitting | nan | nan | 70.0 | 0.1 | 5.5 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 161 | Lying | Sitting | nan | nan | 70.3 | 0.2 | 11.1 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 162 | Lying | Sitting | nan | nan | 70.4 | 0.2 | 0.2 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 163 | Lying | Sitting | nan | nan | 70.6 | 0.0 | 6.4 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 164 | Lying | Sitting | nan | nan | 70.6 | 0.0 | 0.1 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 165 | Lying | Sitting | nan | nan | 70.5 | 0.2 | 3.0 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 166 | Lying | Sitting | nan | nan | 70.0 | 0.4 | 13.1 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 167 | Lying | Sitting | nan | nan | 69.3 | 0.6 | 21.2 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 168 | Lying | Sitting | nan | nan | 69.7 | 0.2 | 12.3 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 169 | Lying | Sitting | nan | nan | 69.9 | 0.2 | 4.9 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 170 | Lying | Sitting | nan | nan | 69.6 | 0.4 | 10.2 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 171 | Lying | Sitting | nan | nan | 69.9 | 0.4 | 8.7 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 172 | Lying | Sitting | nan | nan | 69.7 | 0.1 | 3.4 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 173 | Lying | Sitting | nan | nan | 69.6 | 0.1 | 4.1 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 174 | Lying | Sitting | nan | nan | 69.4 | 0.1 | 7.3 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |
| 175 | Lying | Sitting | nan | nan | 69.0 | 0.1 | 9.9 | 0.2 | 0.3 | 0.3 | T | F | Sitting|Sitting|Sitting|Sitting|Sitting |

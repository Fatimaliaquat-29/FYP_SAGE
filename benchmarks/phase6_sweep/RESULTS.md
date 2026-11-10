# Phase 6 RESULTS (updated after every finished run)

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

Generated 2026-11-08T15:23:58. Same harness as phase 5 (conf 0.4, imgsz 640, greedy same-class matching, exact McNemar). Rule: DECISION_RULE.md (written before training). Baseline = C.

| model | what changed |
|---|---|
| A | v7 (13 classes, old data) |
| C | baseline: lr 0.000588, linear, batch 16 |
| D | C + 4 clips re-added (filtered) |
| LR2 | learning rate x2 (0.001176) |
| B8 | batch 8 |
| COS | cosine LR schedule |
| DCOS | D data + cosine schedule (exploratory, chosen after results) |

## Control (A, person, IoU 0.5)

| set | recorded | measured | ok |
|---|---|---|---|
| heldout_objects | 58/93 | 58/93 | yes |
| reserved388_partial | 107/249 | 107/249 | yes |
| round6_heldout | 50/226 | 50/226 | yes |

## Verdicts (person, IoU 0.5, round6_heldout + reserved388_partial)

- **D (C + 4 clips re-added (filtered)) vs C: no clear difference.** round6_heldout: D-only 4 vs C-only 2, p = 0.688; reserved388_partial: D-only 7 vs C-only 1, p = 0.0703. vs A: no clear difference.
- **LR2 (learning rate x2 (0.001176)) vs C: no clear difference.** round6_heldout: LR2-only 1 vs C-only 3, p = 0.625; reserved388_partial: LR2-only 6 vs C-only 3, p = 0.508. vs A: no clear difference.
- **B8 (batch 8) vs C: no clear difference.** round6_heldout: B8-only 0 vs C-only 1, p = 1; reserved388_partial: B8-only 5 vs C-only 3, p = 0.727. vs A: no clear difference.
- **COS (cosine LR schedule) vs C: no clear difference.** round6_heldout: COS-only 0 vs C-only 1, p = 1; reserved388_partial: COS-only 39 vs C-only 4, p = 3.11e-08. vs A: no clear difference.
- **DCOS (D data + cosine schedule (exploratory, chosen after results)) vs C: no clear difference.** round6_heldout: DCOS-only 3 vs C-only 1, p = 0.625; reserved388_partial: DCOS-only 45 vs C-only 1, p = 1.34e-12. vs A: no clear difference.

**D bed question: fixed.** Per-box bed hits C vs D (IoU 0.5): reserved388_partial: C 1/128, D 26/128, D-only 26 vs C-only 1, p = 4.17e-07; heldout_objects: C 0/86, D 16/86, D-only 16 vs C-only 0, p = 3.05e-05; round6_heldout: C 145/298, D 297/298, D-only 152 vs C-only 0, p = 3.5e-46

## Person recall, IoU 0.5 (decision threshold)

| set | N | A | C | D | LR2 | B8 | COS | DCOS |
|---|---|---|---|---|---|---|---|---|
| heldout_objects | 93 | 58 (fp 1) | 54 (fp 1) | 57 (fp 2) | 58 (fp 2) | 59 (fp 7) | 57 (fp 0) | 60 (fp 2) |
| reserved388_partial | 249 | 107 (fp 3) | 104 (fp 12) | 110 (fp 1) | 107 (fp 22) | 106 (fp 6) | 139 (fp 24) | 148 (fp 4) |
| round6_heldout | 226 | 50 (fp 0) | 51 (fp 1) | 53 (fp 3) | 49 (fp 1) | 50 (fp 4) | 50 (fp 6) | 53 (fp 6) |
| cauca_s10 | 419 | 202 (fp 1) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) |
| exdark_test | 346 | 198 (fp 66) | 204 (fp 44) | 220 (fp 52) | 206 (fp 54) | 208 (fp 46) | 218 (fp 42) | 217 (fp 50) |

Paired vs C, IoU 0.5 (run-only / C-only, exact McNemar p):

| set | D | LR2 | B8 | COS | DCOS | A |
|---|---|---|---|---|---|---|
| heldout_objects | 3 / 0, p 0.25 | 5 / 1, p 0.219 | 5 / 0, p 0.0625 | 5 / 2, p 0.453 | 6 / 0, p 0.0312 | C-only 0 / A-only 4, p 0.125 |
| reserved388_partial | 7 / 1, p 0.0703 | 6 / 3, p 0.508 | 5 / 3, p 0.727 | 39 / 4, p 3.11e-08 | 45 / 1, p 1.34e-12 | C-only 2 / A-only 5, p 0.453 |
| round6_heldout | 4 / 2, p 0.688 | 1 / 3, p 0.625 | 0 / 1, p 1 | 0 / 1, p 1 | 3 / 1, p 0.625 | C-only 3 / A-only 2, p 1 |
| cauca_s10 | 0 / 0, p 1 | 0 / 0, p 1 | 0 / 0, p 1 | 0 / 0, p 1 | 0 / 0, p 1 | C-only 217 / A-only 0, p 9.5e-66 |
| exdark_test | 32 / 16, p 0.0293 | 22 / 20, p 0.878 | 20 / 16, p 0.618 | 26 / 12, p 0.0336 | 33 / 20, p 0.0984 | C-only 31 / A-only 25, p 0.504 |

## Person recall, IoU 0.3 (supplementary)

| set | N | A | C | D | LR2 | B8 | COS | DCOS |
|---|---|---|---|---|---|---|---|---|
| heldout_objects | 93 | 58 (fp 1) | 54 (fp 1) | 57 (fp 2) | 58 (fp 2) | 59 (fp 7) | 57 (fp 0) | 60 (fp 2) |
| reserved388_partial | 249 | 109 (fp 1) | 114 (fp 2) | 110 (fp 1) | 127 (fp 2) | 107 (fp 5) | 140 (fp 23) | 148 (fp 4) |
| round6_heldout | 226 | 50 (fp 0) | 51 (fp 1) | 55 (fp 1) | 49 (fp 1) | 51 (fp 3) | 51 (fp 5) | 53 (fp 6) |
| cauca_s10 | 419 | 202 (fp 1) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) | 419 (fp 0) |
| exdark_test | 346 | 213 (fp 51) | 215 (fp 33) | 234 (fp 38) | 223 (fp 37) | 219 (fp 35) | 227 (fp 33) | 233 (fp 34) |

Paired vs C, IoU 0.3 (run-only / C-only, exact McNemar p):

| set | D | LR2 | B8 | COS | DCOS | A |
|---|---|---|---|---|---|---|
| heldout_objects | 3 / 0, p 0.25 | 5 / 1, p 0.219 | 5 / 0, p 0.0625 | 5 / 2, p 0.453 | 6 / 0, p 0.0312 | C-only 0 / A-only 4, p 0.125 |
| reserved388_partial | 7 / 11, p 0.481 | 20 / 7, p 0.0192 | 6 / 13, p 0.167 | 31 / 5, p 1.29e-05 | 36 / 2, p 5.4e-09 | C-only 12 / A-only 7, p 0.359 |
| round6_heldout | 4 / 0, p 0.125 | 1 / 3, p 0.625 | 1 / 1, p 1 | 1 / 1, p 1 | 3 / 1, p 0.625 | C-only 3 / A-only 2, p 1 |
| cauca_s10 | 0 / 0, p 1 | 0 / 0, p 1 | 0 / 0, p 1 | 0 / 0, p 1 | 0 / 0, p 1 | C-only 217 / A-only 0, p 9.5e-66 |
| exdark_test | 32 / 13, p 0.00661 | 29 / 21, p 0.322 | 25 / 21, p 0.659 | 26 / 14, p 0.0807 | 34 / 16, p 0.0153 | C-only 33 / A-only 31, p 0.901 |

## Empty-room person false positives (4,101 frames)

| model | frames with a person box | boxes |
|---|---|---|
| A | 0/4101 | 0 |
| C | 0/4101 | 0 |
| D | 2/4101 | 2 |
| LR2 | 0/4101 | 0 |
| B8 | 0/4101 | 0 |
| COS | 0/4101 | 0 |
| DCOS | 0/4101 | 0 |

## Other classes, IoU 0.5 (tp/N, fp)

| set | class | A | C | D | LR2 | B8 | COS | DCOS |
|---|---|---|---|---|---|---|---|---|
| heldout_objects | bed | 7/86 (fp 35) | 0/86 (fp 39) | 16/86 (fp 47) | 2/86 (fp 54) | 2/86 (fp 72) | 0/86 (fp 78) | 3/86 (fp 27) |
| heldout_objects | chair | 18/90 (fp 14) | 19/90 (fp 8) | 18/90 (fp 13) | 18/90 (fp 24) | 18/90 (fp 3) | 22/90 (fp 42) | 18/90 (fp 3) |
| heldout_objects | sofa | 168/276 (fp 36) | 155/276 (fp 18) | 155/276 (fp 20) | 133/276 (fp 3) | 177/276 (fp 19) | 145/276 (fp 8) | 171/276 (fp 26) |
| heldout_objects | table | 8/94 (fp 1) | 4/94 (fp 27) | 0/94 (fp 19) | 0/94 (fp 15) | 1/94 (fp 19) | 13/94 (fp 46) | 7/94 (fp 17) |
| reserved388_partial | bed | 19/128 (fp 62) | 1/128 (fp 54) | 26/128 (fp 62) | 39/128 (fp 106) | 3/128 (fp 150) | 1/128 (fp 133) | 44/128 (fp 41) |
| reserved388_partial | chair | 18/90 (fp 19) | 19/90 (fp 49) | 18/90 (fp 61) | 18/90 (fp 81) | 18/90 (fp 12) | 22/90 (fp 110) | 18/90 (fp 11) |
| reserved388_partial | sofa | 231/450 (fp 98) | 228/450 (fp 57) | 236/450 (fp 62) | 203/450 (fp 47) | 261/450 (fp 66) | 230/450 (fp 70) | 265/450 (fp 87) |
| reserved388_partial | table | 8/94 (fp 7) | 4/94 (fp 28) | 0/94 (fp 19) | 0/94 (fp 15) | 1/94 (fp 19) | 13/94 (fp 48) | 7/94 (fp 19) |
| round6_heldout | bed | 146/298 (fp 0) | 145/298 (fp 0) | 297/298 (fp 1) | 145/298 (fp 0) | 145/298 (fp 0) | 145/298 (fp 0) | 296/298 (fp 1) |
| round6_heldout | chair | 326/443 (fp 2) | 374/443 (fp 25) | 439/443 (fp 3) | 351/443 (fp 30) | 410/443 (fp 23) | 378/443 (fp 8) | 438/443 (fp 3) |
| exdark_test | chair | 99/225 (fp 69) | 117/225 (fp 43) | 124/225 (fp 54) | 120/225 (fp 61) | 116/225 (fp 51) | 117/225 (fp 54) | 125/225 (fp 55) |
| exdark_test | table | 29/183 (fp 29) | 65/183 (fp 18) | 70/183 (fp 28) | 76/183 (fp 24) | 82/183 (fp 33) | 77/183 (fp 30) | 71/183 (fp 38) |
| exdark_test | bottle | 73/211 (fp 64) | 92/211 (fp 44) | 113/211 (fp 50) | 111/211 (fp 40) | 102/211 (fp 48) | 103/211 (fp 60) | 110/211 (fp 53) |
| exdark_test | cup | 55/199 (fp 35) | 99/199 (fp 41) | 96/199 (fp 44) | 95/199 (fp 38) | 96/199 (fp 45) | 99/199 (fp 40) | 94/199 (fp 46) |

## Person box fit on own footage (phase-5 box_fit method; 475 labelled people)

| model | matched | median coverage | good | tight (<90% covered) | loose (>25% extra) | very loose (>2x) |
|---|---|---|---|---|---|---|
| A | 159 | 93% | 80 | 65 | 14 | 2 |
| C | 165 | 95% | 92 | 59 | 24 | 10 |
| D | 165 | 94% | 102 | 53 | 11 | 1 |
| LR2 | 176 | 91% | 83 | 78 | 37 | 1 |
| B8 | 158 | 94% | 90 | 53 | 15 | 1 |
| COS | 191 | 90% | 85 | 95 | 16 | 0 |
| DCOS | 201 | 91% | 96 | 92 | 14 | 0 |

## Val metrics (same val set for C and every phase-6 run; best.pt epoch)

| model | best epoch | epochs run | mAP50 | mAP50-95 |
|---|---|---|---|---|
| C | 24 | 30 | 0.586 | 0.424 |
| D | 30 | 30 | 0.574 | 0.414 |
| LR2 | 29 | 30 | 0.572 | 0.415 |
| B8 | 25 | 30 | 0.586 | 0.421 |
| COS | 30 | 30 | 0.575 | 0.416 |
| DCOS | 29 | 30 | 0.573 | 0.415 |

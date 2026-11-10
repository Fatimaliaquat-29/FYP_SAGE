# RESULTS: A (v7) vs B (cleaned, 7 classes) vs C (cleaned + CAUCAFall + ExDark)

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

Scored 2026-11-07T09:10:20 to 2026-11-07T09:15:59. conf 0.4, imgsz 640, same-class greedy matching (score_v7_suite logic), all classes compared in the 7-class space. Decision rule: DECISION_RULE.md (written before training).

## Control: does A reproduce its recorded numbers? (person, IoU 0.5)

| set | recorded | measured | reproduced |
|---|---|---|---|
| heldout_objects | 58/93 | 58/93 | yes |
| reserved388_partial | 107/249 | 107/249 | yes |
| round6_heldout | 50/226 | 50/226 | yes |

## Verdict (DECISION_RULE.md applied literally)

- **B vs A: no clear difference.**
  - round6_heldout, IoU 0.5: B-only 2 vs A-only 2, exact McNemar p = 1
  - reserved388_partial, IoU 0.5: B-only 2 vs A-only 6, exact McNemar p = 0.2891
- **C vs A: no clear difference.**
  - round6_heldout, IoU 0.5: C-only 3 vs A-only 2, exact McNemar p = 1
  - reserved388_partial, IoU 0.5: C-only 2 vs A-only 5, exact McNemar p = 0.4531
- Empty-room frames with a person box: A 0/4101, B 0/4101, C 0/4101

## Person recall per set, IoU 0.5  (decision threshold)

hits/N (recall) [Wilson 95% CI]; FP = person false positives on those frames.

| set | N | A | B | C | FP A | FP B | FP C |
|---|---|---|---|---|---|---|---|
| heldout_objects | 93 | 58/93 (0.624) [0.522, 0.715] | 55/93 (0.591) [0.490, 0.686] | 54/93 (0.581) [0.479, 0.676] | 1 | 4 | 1 |
| reserved388_partial | 249 | 107/249 (0.430) [0.370, 0.492] | 103/249 (0.414) [0.354, 0.476] | 104/249 (0.418) [0.358, 0.480] | 3 | 4 | 12 |
| round6_heldout | 226 | 50/226 (0.221) [0.172, 0.280] | 50/226 (0.221) [0.172, 0.280] | 51/226 (0.226) [0.176, 0.284] | 0 | 2 | 1 |
| cauca_s10 (new; C trained on this domain) | 419 | 202/419 (0.482) [0.435, 0.530] | 163/419 (0.389) [0.344, 0.437] | 419/419 (1.000) [0.991, 1.000] | 1 | 3 | 0 |
| exdark_test (new; C trained on this domain) | 346 | 198/346 (0.572) [0.520, 0.623] | 180/346 (0.520) [0.468, 0.572] | 204/346 (0.590) [0.537, 0.640] | 66 | 36 | 44 |

### Paired person comparisons, IoU 0.5

| pair | set | clip | N | hits (first) | hits (second) | second-only | first-only | McNemar p |
|---|---|---|---|---|---|---|---|---|
| A vs B | heldout_objects | **all** | 93 | 58 | 55 | 2 | 5 | 0.4531 |
| A vs B | heldout_objects | With_people_Bedroom_Fall | 20 | 0 | 0 | 0 | 0 | 1 |
| A vs B | heldout_objects | With_people_Bedroom_Sit | 24 | 21 | 19 | 2 | 4 | 0.6875 |
| A vs B | heldout_objects | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs B | heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6 | 6 | 0 | 0 | 1 |
| A vs B | heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs B | heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs B | reserved388_partial | **all** | 249 | 107 | 103 | 2 | 6 | 0.2891 |
| A vs B | reserved388_partial | With_people_Bedroom_Fall | 62 | 21 | 20 | 0 | 1 | 1 |
| A vs B | reserved388_partial | With_people_Bedroom_Sit | 24 | 21 | 19 | 2 | 4 | 0.6875 |
| A vs B | reserved388_partial | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18 | 18 | 0 | 0 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16 | 16 | 0 | 0 | 1 |
| A vs B | round6_heldout | **all** | 226 | 50 | 50 | 2 | 2 | 1 |
| A vs B | round6_heldout | Behind_Bed_HM | 73 | 48 | 49 | 2 | 1 | 1 |
| A vs B | round6_heldout | Laying_Dim_HM | 153 | 2 | 1 | 0 | 1 | 1 |
| A vs B | cauca_s10 | **all** | 419 | 202 | 163 | 15 | 54 | 2.613e-06 |
| A vs B | exdark_test | **all** | 346 | 198 | 180 | 15 | 33 | 0.01328 |
| A vs C | heldout_objects | **all** | 93 | 58 | 54 | 0 | 4 | 0.125 |
| A vs C | heldout_objects | With_people_Bedroom_Fall | 20 | 0 | 0 | 0 | 0 | 1 |
| A vs C | heldout_objects | With_people_Bedroom_Sit | 24 | 21 | 18 | 0 | 3 | 0.25 |
| A vs C | heldout_objects | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs C | heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6 | 6 | 0 | 0 | 1 |
| A vs C | heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs C | heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs C | reserved388_partial | **all** | 249 | 107 | 104 | 2 | 5 | 0.4531 |
| A vs C | reserved388_partial | With_people_Bedroom_Fall | 62 | 21 | 21 | 1 | 1 | 1 |
| A vs C | reserved388_partial | With_people_Bedroom_Sit | 24 | 21 | 18 | 0 | 3 | 0.25 |
| A vs C | reserved388_partial | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18 | 18 | 0 | 0 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16 | 17 | 1 | 0 | 1 |
| A vs C | round6_heldout | **all** | 226 | 50 | 51 | 3 | 2 | 1 |
| A vs C | round6_heldout | Behind_Bed_HM | 73 | 48 | 47 | 1 | 2 | 1 |
| A vs C | round6_heldout | Laying_Dim_HM | 153 | 2 | 4 | 2 | 0 | 0.5 |
| A vs C | cauca_s10 | **all** | 419 | 202 | 419 | 217 | 0 | 9.496e-66 |
| A vs C | exdark_test | **all** | 346 | 198 | 204 | 31 | 25 | 0.5044 |
| B vs C | heldout_objects | **all** | 93 | 55 | 54 | 2 | 3 | 1 |
| B vs C | heldout_objects | With_people_Bedroom_Fall | 20 | 0 | 0 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_Bedroom_Sit | 24 | 19 | 18 | 2 | 3 | 1 |
| B vs C | heldout_objects | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6 | 6 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 15 | 15 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| B vs C | reserved388_partial | **all** | 249 | 103 | 104 | 4 | 3 | 1 |
| B vs C | reserved388_partial | With_people_Bedroom_Fall | 62 | 20 | 21 | 1 | 0 | 1 |
| B vs C | reserved388_partial | With_people_Bedroom_Sit | 24 | 19 | 18 | 2 | 3 | 1 |
| B vs C | reserved388_partial | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18 | 18 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 15 | 15 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16 | 17 | 1 | 0 | 1 |
| B vs C | round6_heldout | **all** | 226 | 50 | 51 | 4 | 3 | 1 |
| B vs C | round6_heldout | Behind_Bed_HM | 73 | 49 | 47 | 1 | 3 | 0.625 |
| B vs C | round6_heldout | Laying_Dim_HM | 153 | 1 | 4 | 3 | 0 | 0.25 |
| B vs C | cauca_s10 | **all** | 419 | 163 | 419 | 256 | 0 | 1.727e-77 |
| B vs C | exdark_test | **all** | 346 | 180 | 204 | 41 | 17 | 0.002233 |

## Person recall per set, IoU 0.3  (supplementary)

hits/N (recall) [Wilson 95% CI]; FP = person false positives on those frames.

| set | N | A | B | C | FP A | FP B | FP C |
|---|---|---|---|---|---|---|---|
| heldout_objects | 93 | 58/93 (0.624) [0.522, 0.715] | 55/93 (0.591) [0.490, 0.686] | 54/93 (0.581) [0.479, 0.676] | 1 | 4 | 1 |
| reserved388_partial | 249 | 109/249 (0.438) [0.378, 0.500] | 103/249 (0.414) [0.354, 0.476] | 114/249 (0.458) [0.397, 0.520] | 1 | 4 | 2 |
| round6_heldout | 226 | 50/226 (0.221) [0.172, 0.280] | 51/226 (0.226) [0.176, 0.284] | 51/226 (0.226) [0.176, 0.284] | 0 | 1 | 1 |
| cauca_s10 (new; C trained on this domain) | 419 | 202/419 (0.482) [0.435, 0.530] | 163/419 (0.389) [0.344, 0.437] | 419/419 (1.000) [0.991, 1.000] | 1 | 3 | 0 |
| exdark_test (new; C trained on this domain) | 346 | 213/346 (0.616) [0.563, 0.665] | 189/346 (0.546) [0.494, 0.598] | 215/346 (0.621) [0.569, 0.671] | 51 | 27 | 33 |

### Paired person comparisons, IoU 0.3

| pair | set | clip | N | hits (first) | hits (second) | second-only | first-only | McNemar p |
|---|---|---|---|---|---|---|---|---|
| A vs B | heldout_objects | **all** | 93 | 58 | 55 | 2 | 5 | 0.4531 |
| A vs B | heldout_objects | With_people_Bedroom_Fall | 20 | 0 | 0 | 0 | 0 | 1 |
| A vs B | heldout_objects | With_people_Bedroom_Sit | 24 | 21 | 19 | 2 | 4 | 0.6875 |
| A vs B | heldout_objects | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs B | heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6 | 6 | 0 | 0 | 1 |
| A vs B | heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs B | heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs B | reserved388_partial | **all** | 249 | 109 | 103 | 2 | 8 | 0.1094 |
| A vs B | reserved388_partial | With_people_Bedroom_Fall | 62 | 23 | 20 | 0 | 3 | 0.25 |
| A vs B | reserved388_partial | With_people_Bedroom_Sit | 24 | 21 | 19 | 2 | 4 | 0.6875 |
| A vs B | reserved388_partial | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18 | 18 | 0 | 0 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs B | reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16 | 16 | 0 | 0 | 1 |
| A vs B | round6_heldout | **all** | 226 | 50 | 51 | 2 | 1 | 1 |
| A vs B | round6_heldout | Behind_Bed_HM | 73 | 48 | 50 | 2 | 0 | 0.5 |
| A vs B | round6_heldout | Laying_Dim_HM | 153 | 2 | 1 | 0 | 1 | 1 |
| A vs B | cauca_s10 | **all** | 419 | 202 | 163 | 15 | 54 | 2.613e-06 |
| A vs B | exdark_test | **all** | 346 | 213 | 189 | 17 | 41 | 0.002233 |
| A vs C | heldout_objects | **all** | 93 | 58 | 54 | 0 | 4 | 0.125 |
| A vs C | heldout_objects | With_people_Bedroom_Fall | 20 | 0 | 0 | 0 | 0 | 1 |
| A vs C | heldout_objects | With_people_Bedroom_Sit | 24 | 21 | 18 | 0 | 3 | 0.25 |
| A vs C | heldout_objects | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs C | heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6 | 6 | 0 | 0 | 1 |
| A vs C | heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs C | heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs C | reserved388_partial | **all** | 249 | 109 | 114 | 12 | 7 | 0.3593 |
| A vs C | reserved388_partial | With_people_Bedroom_Fall | 62 | 23 | 31 | 11 | 3 | 0.05737 |
| A vs C | reserved388_partial | With_people_Bedroom_Sit | 24 | 21 | 18 | 0 | 3 | 0.25 |
| A vs C | reserved388_partial | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18 | 18 | 0 | 0 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16 | 15 | 0 | 1 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| A vs C | reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16 | 17 | 1 | 0 | 1 |
| A vs C | round6_heldout | **all** | 226 | 50 | 51 | 3 | 2 | 1 |
| A vs C | round6_heldout | Behind_Bed_HM | 73 | 48 | 47 | 1 | 2 | 1 |
| A vs C | round6_heldout | Laying_Dim_HM | 153 | 2 | 4 | 2 | 0 | 0.5 |
| A vs C | cauca_s10 | **all** | 419 | 202 | 419 | 217 | 0 | 9.496e-66 |
| A vs C | exdark_test | **all** | 346 | 213 | 215 | 33 | 31 | 0.9007 |
| B vs C | heldout_objects | **all** | 93 | 55 | 54 | 2 | 3 | 1 |
| B vs C | heldout_objects | With_people_Bedroom_Fall | 20 | 0 | 0 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_Bedroom_Sit | 24 | 19 | 18 | 2 | 3 | 1 |
| B vs C | heldout_objects | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6 | 6 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 15 | 15 | 0 | 0 | 1 |
| B vs C | heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| B vs C | reserved388_partial | **all** | 249 | 103 | 114 | 14 | 3 | 0.01273 |
| B vs C | reserved388_partial | With_people_Bedroom_Fall | 62 | 20 | 31 | 11 | 0 | 0.0009766 |
| B vs C | reserved388_partial | With_people_Bedroom_Sit | 24 | 19 | 18 | 2 | 3 | 1 |
| B vs C | reserved388_partial | With_people_Bedroom_Walk | 14 | 14 | 14 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18 | 18 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 15 | 15 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1 | 1 | 0 | 0 | 1 |
| B vs C | reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16 | 17 | 1 | 0 | 1 |
| B vs C | round6_heldout | **all** | 226 | 51 | 51 | 3 | 3 | 1 |
| B vs C | round6_heldout | Behind_Bed_HM | 73 | 50 | 47 | 0 | 3 | 0.25 |
| B vs C | round6_heldout | Laying_Dim_HM | 153 | 1 | 4 | 3 | 0 | 0.25 |
| B vs C | cauca_s10 | **all** | 419 | 163 | 419 | 256 | 0 | 1.727e-77 |
| B vs C | exdark_test | **all** | 346 | 189 | 215 | 45 | 19 | 0.001563 |

## Empty-room false positives (yolo_testing/Reserved/Empty, every frame)

| model | frames | frames with a person box | person boxes |
|---|---|---|---|
| A | 4101 | 0 | 0 |
| B | 4101 | 0 | 0 |
| C | 4101 | 0 | 0 |

## Other classes, IoU 0.5: recall tp/(tp+fn) and false positives (7-class space)

| set | class | A | B | C |
|---|---|---|---|---|
| heldout_objects | bed | 7/86 (fp 35) | 0/86 (fp 47) | 0/86 (fp 39) |
| heldout_objects | chair | 18/90 (fp 14) | 18/90 (fp 1) | 19/90 (fp 8) |
| heldout_objects | sofa | 168/276 (fp 36) | 111/276 (fp 14) | 155/276 (fp 18) |
| heldout_objects | table | 8/94 (fp 1) | 0/94 (fp 13) | 4/94 (fp 27) |
| reserved388_partial | bed | 19/128 (fp 62) | 1/128 (fp 82) | 1/128 (fp 54) |
| reserved388_partial | chair | 18/90 (fp 19) | 18/90 (fp 14) | 19/90 (fp 49) |
| reserved388_partial | sofa | 231/450 (fp 98) | 201/450 (fp 20) | 228/450 (fp 57) |
| reserved388_partial | table | 8/94 (fp 7) | 0/94 (fp 13) | 4/94 (fp 28) |
| round6_heldout | bed | 146/298 (fp 0) | 159/298 (fp 0) | 145/298 (fp 0) |
| round6_heldout | chair | 326/443 (fp 2) | 298/443 (fp 10) | 374/443 (fp 25) |
| exdark_test | chair | 99/225 (fp 69) | 94/225 (fp 55) | 117/225 (fp 43) |
| exdark_test | table | 29/183 (fp 29) | 23/183 (fp 21) | 65/183 (fp 18) |
| exdark_test | bottle | 73/211 (fp 64) | 79/211 (fp 41) | 92/211 (fp 44) |
| exdark_test | cup | 55/199 (fp 35) | 49/199 (fp 15) | 99/199 (fp 41) |

## Val metrics (not used for the decision; B and C have different val sets and classes from A)

- B: best epoch 19 (mAP50 0.59975, mAP50-95 0.45488); last epoch 29 of 29 logged
- C: best epoch 24 (mAP50 0.58562, mAP50-95 0.42413); last epoch 30 of 30 logged


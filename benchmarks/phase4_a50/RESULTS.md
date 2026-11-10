# RESULTS: A (v7, 30 epochs) vs A50 (50 epochs)

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

Scored 2026-10-19T07:55:18 to 2026-10-19T08:00:05. conf 0.4, imgsz 640, person class, same-class greedy matching (src/detection/score_v7_suite.py, unchanged). Decision rule: DECISION_RULE.md (written before scoring).

## Control: does A reproduce its recorded numbers? (person, IoU 0.5)

| set | recorded | measured | reproduced |
|---|---|---|---|
| heldout_objects | 58/93 | 58/93 | yes |
| reserved388_partial | 107/249 | 107/249 | yes |
| round6_heldout | 50/226 | 50/226 | yes |

## Person hits per set and clip, IoU 0.5  (decision threshold)

hits/N (recall) [Wilson 95% CI]. McNemar = exact two-sided test on boxes hit by only one model. FP = person false positives on those frames.

| set | clip | N | A | A50 | A50-only | A-only | McNemar p | FP A | FP A50 |
|---|---|---|---|---|---|---|---|---|---|
| heldout_objects | **all** | 93 | 58/93 (0.624) [0.522, 0.715] | 59/93 (0.634) [0.533, 0.725] | 2 | 1 | 1 | 1 | 0 |
| heldout_objects | With_people_Bedroom_Fall | 20 | 0/20 (0.000) [0.000, 0.161] | 0/20 (0.000) [0.000, 0.161] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 22/24 (0.917) [0.742, 0.977] | 2 | 1 | 1 | 0 | 0 |
| heldout_objects | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6/18 (0.333) [0.163, 0.563] | 6/18 (0.333) [0.163, 0.563] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | **all** | 249 | 107/249 (0.430) [0.370, 0.492] | 109/249 (0.438) [0.378, 0.500] | 4 | 2 | 0.6875 | 3 | 1 |
| reserved388_partial | With_people_Bedroom_Fall | 62 | 21/62 (0.339) [0.233, 0.463] | 22/62 (0.355) [0.247, 0.479] | 2 | 1 | 1 | 2 | 0 |
| reserved388_partial | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 22/24 (0.917) [0.742, 0.977] | 2 | 1 | 1 | 0 | 0 |
| reserved388_partial | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18/97 (0.186) [0.121, 0.274] | 18/97 (0.186) [0.121, 0.274] | 0 | 0 | 1 | 0 | 1 |
| reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 0 |
| reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16/35 (0.457) [0.305, 0.618] | 16/35 (0.457) [0.305, 0.618] | 0 | 0 | 1 | 0 | 0 |
| round6_heldout | **all** | 226 | 50/226 (0.221) [0.172, 0.280] | 51/226 (0.226) [0.176, 0.284] | 2 | 1 | 1 | 0 | 6 |
| round6_heldout | Behind_Bed_HM | 73 | 48/73 (0.658) [0.543, 0.756] | 50/73 (0.685) [0.571, 0.780] | 2 | 0 | 0.5 | 0 | 6 |
| round6_heldout | Laying_Dim_HM | 153 | 2/153 (0.013) [0.004, 0.046] | 1/153 (0.007) [0.001, 0.036] | 0 | 1 | 1 | 0 | 0 |

## Person hits per set and clip, IoU 0.3  (supplementary)

hits/N (recall) [Wilson 95% CI]. McNemar = exact two-sided test on boxes hit by only one model. FP = person false positives on those frames.

| set | clip | N | A | A50 | A50-only | A-only | McNemar p | FP A | FP A50 |
|---|---|---|---|---|---|---|---|---|---|
| heldout_objects | **all** | 93 | 58/93 (0.624) [0.522, 0.715] | 59/93 (0.634) [0.533, 0.725] | 2 | 1 | 1 | 1 | 0 |
| heldout_objects | With_people_Bedroom_Fall | 20 | 0/20 (0.000) [0.000, 0.161] | 0/20 (0.000) [0.000, 0.161] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 22/24 (0.917) [0.742, 0.977] | 2 | 1 | 1 | 0 | 0 |
| heldout_objects | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6/18 (0.333) [0.163, 0.563] | 6/18 (0.333) [0.163, 0.563] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | **all** | 249 | 109/249 (0.438) [0.378, 0.500] | 109/249 (0.438) [0.378, 0.500] | 3 | 3 | 1 | 1 | 1 |
| reserved388_partial | With_people_Bedroom_Fall | 62 | 23/62 (0.371) [0.262, 0.495] | 22/62 (0.355) [0.247, 0.479] | 1 | 2 | 1 | 0 | 0 |
| reserved388_partial | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 22/24 (0.917) [0.742, 0.977] | 2 | 1 | 1 | 0 | 0 |
| reserved388_partial | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18/97 (0.186) [0.121, 0.274] | 18/97 (0.186) [0.121, 0.274] | 0 | 0 | 1 | 0 | 1 |
| reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 0 |
| reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16/35 (0.457) [0.305, 0.618] | 16/35 (0.457) [0.305, 0.618] | 0 | 0 | 1 | 0 | 0 |
| round6_heldout | **all** | 226 | 50/226 (0.221) [0.172, 0.280] | 52/226 (0.230) [0.180, 0.289] | 3 | 1 | 0.625 | 0 | 5 |
| round6_heldout | Behind_Bed_HM | 73 | 48/73 (0.658) [0.543, 0.756] | 51/73 (0.699) [0.586, 0.792] | 3 | 0 | 0.25 | 0 | 5 |
| round6_heldout | Laying_Dim_HM | 153 | 2/153 (0.013) [0.004, 0.046] | 1/153 (0.007) [0.001, 0.036] | 0 | 1 | 1 | 0 | 0 |

## Empty-room false positives (yolo_testing/Reserved/Empty, every frame)

| model | frames | frames with a person box | person boxes |
|---|---|---|---|
| A | 4101 | 0 | 0 |
| A50 | 4101 | 0 | 0 |

## Other classes (official score_v7_suite output, IoU 0.5): recall tp/(tp+fn)

| set | class | A | A50 |
|---|---|---|---|
| heldout_objects | chair | 18/90 (fp 14) | 18/90 (fp 24) |
| heldout_objects | couch | 168/276 (fp 36) | 146/276 (fp 17) |
| heldout_objects | bed | 7/86 (fp 35) | 28/86 (fp 37) |
| heldout_objects | dining table | 8/94 (fp 1) | 5/94 (fp 0) |
| heldout_objects | tv | 0/1 (fp 1) | 0/1 (fp 1) |
| reserved388_partial | chair | 18/90 (fp 19) | 18/90 (fp 44) |
| reserved388_partial | couch | 231/450 (fp 98) | 191/450 (fp 70) |
| reserved388_partial | bed | 19/128 (fp 62) | 57/128 (fp 45) |
| reserved388_partial | dining table | 8/94 (fp 7) | 5/94 (fp 2) |
| reserved388_partial | tv | 0/1 (fp 1) | 0/1 (fp 1) |
| round6_heldout | chair | 326/443 (fp 2) | 438/443 (fp 4) |
| round6_heldout | bed | 146/298 (fp 0) | 169/298 (fp 0) |

## A50 val metrics (not used for the decision)

- best epoch by mAP50-95: epoch 40: mAP50 0.52358, mAP50-95 0.385
- last epoch (50 logged): epoch 50: mAP50 0.5173, mAP50-95 0.38005

## Verdict (DECISION_RULE.md applied literally)

- round6_heldout, IoU 0.5: A50-only 2 vs A-only 1, exact McNemar p = 1 -> does not meet the bar
- reserved388_partial, IoU 0.5: A50-only 4 vs A-only 2, exact McNemar p = 0.6875 -> does not meet the bar
- empty-room FP frames: A 0/4101, A50 0/4101

**Verdict: no clear difference.**


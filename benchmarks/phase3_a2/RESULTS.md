# A5 RESULTS: A (v7) vs A2

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

Scored 2026-10-18T04:34:24 to 2026-10-18T04:39:10. conf 0.4, imgsz 640, person class, same-class greedy matching (src/detection/score_v7_suite.py, unchanged). Decision rule: DECISION_RULE.md (written before scoring).

## Control: does A reproduce its recorded numbers? (person, IoU 0.5)

| set | recorded | measured | reproduced |
|---|---|---|---|
| heldout_objects | 58/93 | 58/93 | yes |
| reserved388_partial | 107/249 | 107/249 | yes |
| round6_heldout | 50/226 | 50/226 | yes |

## Person hits per set and clip, IoU 0.5  (decision threshold)

hits/N (recall) [Wilson 95% CI]. McNemar = exact two-sided test on boxes hit by only one model. FP = person false positives on those frames.

| set | clip | N | A | A2 | A2-only | A-only | McNemar p | FP A | FP A2 |
|---|---|---|---|---|---|---|---|---|---|
| heldout_objects | **all** | 93 | 58/93 (0.624) [0.522, 0.715] | 60/93 (0.645) [0.544, 0.735] | 2 | 0 | 0.5 | 1 | 8 |
| heldout_objects | With_people_Bedroom_Fall | 20 | 0/20 (0.000) [0.000, 0.161] | 0/20 (0.000) [0.000, 0.161] | 0 | 0 | 1 | 0 | 6 |
| heldout_objects | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 23/24 (0.958) [0.798, 0.993] | 2 | 0 | 0.5 | 0 | 0 |
| heldout_objects | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6/18 (0.333) [0.163, 0.563] | 6/18 (0.333) [0.163, 0.563] | 0 | 0 | 1 | 0 | 1 |
| heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 1 |
| heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | **all** | 249 | 107/249 (0.430) [0.370, 0.492] | 116/249 (0.466) [0.405, 0.528] | 10 | 1 | 0.01172 | 3 | 3 |
| reserved388_partial | With_people_Bedroom_Fall | 62 | 21/62 (0.339) [0.233, 0.463] | 29/62 (0.468) [0.349, 0.590] | 8 | 0 | 0.007812 | 2 | 0 |
| reserved388_partial | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 23/24 (0.958) [0.798, 0.993] | 2 | 0 | 0.5 | 0 | 0 |
| reserved388_partial | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18/97 (0.186) [0.121, 0.274] | 17/97 (0.175) [0.112, 0.263] | 0 | 1 | 1 | 0 | 2 |
| reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 1 |
| reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16/35 (0.457) [0.305, 0.618] | 16/35 (0.457) [0.305, 0.618] | 0 | 0 | 1 | 0 | 0 |
| round6_heldout | **all** | 226 | 50/226 (0.221) [0.172, 0.280] | 54/226 (0.239) [0.188, 0.299] | 5 | 1 | 0.2188 | 0 | 10 |
| round6_heldout | Behind_Bed_HM | 73 | 48/73 (0.658) [0.543, 0.756] | 49/73 (0.671) [0.557, 0.768] | 2 | 1 | 1 | 0 | 1 |
| round6_heldout | Laying_Dim_HM | 153 | 2/153 (0.013) [0.004, 0.046] | 5/153 (0.033) [0.014, 0.074] | 3 | 0 | 0.25 | 0 | 9 |

## Person hits per set and clip, IoU 0.3  (supplementary)

hits/N (recall) [Wilson 95% CI]. McNemar = exact two-sided test on boxes hit by only one model. FP = person false positives on those frames.

| set | clip | N | A | A2 | A2-only | A-only | McNemar p | FP A | FP A2 |
|---|---|---|---|---|---|---|---|---|---|
| heldout_objects | **all** | 93 | 58/93 (0.624) [0.522, 0.715] | 60/93 (0.645) [0.544, 0.735] | 2 | 0 | 0.5 | 1 | 8 |
| heldout_objects | With_people_Bedroom_Fall | 20 | 0/20 (0.000) [0.000, 0.161] | 0/20 (0.000) [0.000, 0.161] | 0 | 0 | 1 | 0 | 6 |
| heldout_objects | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 23/24 (0.958) [0.798, 0.993] | 2 | 0 | 0.5 | 0 | 0 |
| heldout_objects | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| heldout_objects | With_people_TV_Lounge_1_Fall | 18 | 6/18 (0.333) [0.163, 0.563] | 6/18 (0.333) [0.163, 0.563] | 0 | 0 | 1 | 0 | 1 |
| heldout_objects | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 1 |
| heldout_objects | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | **all** | 249 | 109/249 (0.438) [0.378, 0.500] | 116/249 (0.466) [0.405, 0.528] | 8 | 1 | 0.03906 | 1 | 3 |
| reserved388_partial | With_people_Bedroom_Fall | 62 | 23/62 (0.371) [0.262, 0.495] | 29/62 (0.468) [0.349, 0.590] | 6 | 0 | 0.03125 | 0 | 0 |
| reserved388_partial | With_people_Bedroom_Sit | 24 | 21/24 (0.875) [0.690, 0.957] | 23/24 (0.958) [0.798, 0.993] | 2 | 0 | 0.5 | 0 | 0 |
| reserved388_partial | With_people_Bedroom_Walk | 14 | 14/14 (1.000) [0.785, 1.000] | 14/14 (1.000) [0.785, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_1_Fall | 97 | 18/97 (0.186) [0.121, 0.274] | 17/97 (0.175) [0.112, 0.263] | 0 | 1 | 1 | 0 | 2 |
| reserved388_partial | With_people_TV_Lounge_1_Sit | 16 | 16/16 (1.000) [0.806, 1.000] | 16/16 (1.000) [0.806, 1.000] | 0 | 0 | 1 | 1 | 1 |
| reserved388_partial | With_people_TV_Lounge_1_Walk | 1 | 1/1 (1.000) [0.207, 1.000] | 1/1 (1.000) [0.207, 1.000] | 0 | 0 | 1 | 0 | 0 |
| reserved388_partial | With_people_TV_Lounge_2_Fall | 35 | 16/35 (0.457) [0.305, 0.618] | 16/35 (0.457) [0.305, 0.618] | 0 | 0 | 1 | 0 | 0 |
| round6_heldout | **all** | 226 | 50/226 (0.221) [0.172, 0.280] | 63/226 (0.279) [0.224, 0.341] | 14 | 1 | 0.0009766 | 0 | 1 |
| round6_heldout | Behind_Bed_HM | 73 | 48/73 (0.658) [0.543, 0.756] | 49/73 (0.671) [0.557, 0.768] | 2 | 1 | 1 | 0 | 1 |
| round6_heldout | Laying_Dim_HM | 153 | 2/153 (0.013) [0.004, 0.046] | 14/153 (0.092) [0.055, 0.148] | 12 | 0 | 0.0004883 | 0 | 0 |

## Empty-room false positives (yolo_testing/Reserved/Empty, every frame)

| model | frames | frames with a person box | person boxes |
|---|---|---|---|
| A | 4101 | 0 | 0 |
| A2 | 4101 | 0 | 0 |

## Other classes (official score_v7_suite output, IoU 0.5): recall tp/(tp+fn)

| set | class | A | A2 |
|---|---|---|---|
| heldout_objects | wine glass | 0/0 (fp 0) | 0/0 (fp 2) |
| heldout_objects | chair | 18/90 (fp 14) | 18/90 (fp 40) |
| heldout_objects | couch | 168/276 (fp 36) | 162/276 (fp 4) |
| heldout_objects | bed | 7/86 (fp 35) | 5/86 (fp 52) |
| heldout_objects | dining table | 8/94 (fp 1) | 0/94 (fp 8) |
| heldout_objects | tv | 0/1 (fp 1) | 0/1 (fp 0) |
| reserved388_partial | wine glass | 0/0 (fp 0) | 0/0 (fp 2) |
| reserved388_partial | chair | 18/90 (fp 19) | 18/90 (fp 82) |
| reserved388_partial | couch | 231/450 (fp 98) | 252/450 (fp 51) |
| reserved388_partial | bed | 19/128 (fp 62) | 21/128 (fp 74) |
| reserved388_partial | dining table | 8/94 (fp 7) | 0/94 (fp 8) |
| reserved388_partial | tv | 0/1 (fp 1) | 0/1 (fp 0) |
| round6_heldout | chair | 326/443 (fp 2) | 441/443 (fp 0) |
| round6_heldout | bed | 146/298 (fp 0) | 298/298 (fp 52) |

## A2 val metrics (not used for the decision)

- best epoch by mAP50-95: epoch 29: mAP50 0.52528, mAP50-95 0.38424
- last epoch (30 logged): epoch 30: mAP50 0.52528, mAP50-95 0.38423

## Verdict (DECISION_RULE.md applied literally)

- round6_heldout, IoU 0.5: A2-only 5 vs A-only 1, exact McNemar p = 0.2188 -> does not meet the bar
- reserved388_partial, IoU 0.5: A2-only 10 vs A-only 1, exact McNemar p = 0.01172 -> meets the bar
- empty-room FP frames: A 0/4101, A2 0/4101

**Verdict: no clear difference.**


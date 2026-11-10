# Phase 5 STATUS

- 2026-11-07 ~03:15 PLAN.md and DECISION_RULE.md written (before any build/training/scoring).
- ExDark box annotations downloaded (ExDark_Annno.zip, 5,080,194 B, sha256 37e535b7...d35d) + imageclasslist.txt into new datasets/ExDark/annotations_download.
- build_v8.py: ALL_OK. B train 11,397 / val 2,610; C train 15,552 / val 3,268; held-out new: cauca_s10 419, exdark_test 293.
- Spot check 1 (spotcheck_exdark_first_build.jpg): ExDark calls sofas "Chair", so pseudo sofa/bed boxes duplicated them. Fixed in build_v8.py (pseudo sofa on an ExDark Chair -> that box becomes sofa, 71 boxes; other overlapping pseudo boxes dropped, 83) and rebuilt. Spot check 2 (spotcheck_exdark.jpg, spotcheck_caucafall.jpg): OK.

## Overnight pipeline (started 2026-11-07 03:47:46)
- 2026-11-07 03:47:46 START train C pid=15372 cap=7h
- 2026-11-07 03:57:46 PROGRESS C: 10 min; epoch=1; train/box_loss=1.10838; val/box_loss=0.93345; metrics/mAP50(B)=0.4946; metrics/mAP50-95(B)=0.34096 (1/30)
- 2026-11-07 04:07:46 PROGRESS C: 20 min; epoch=2; train/box_loss=1.09287; val/box_loss=1.01026; metrics/mAP50(B)=0.46105; metrics/mAP50-95(B)=0.30457 (2/30)
- 2026-11-07 04:17:46 PROGRESS C: 30 min; epoch=4; train/box_loss=1.07703; val/box_loss=1.0113; metrics/mAP50(B)=0.46561; metrics/mAP50-95(B)=0.31998 (4/30)
- 2026-11-07 04:27:46 PROGRESS C: 40 min; epoch=5; train/box_loss=1.04188; val/box_loss=0.9789; metrics/mAP50(B)=0.50447; metrics/mAP50-95(B)=0.35048 (5/30)
- 2026-11-07 04:37:46 PROGRESS C: 50 min; epoch=7; train/box_loss=0.99648; val/box_loss=0.97056; metrics/mAP50(B)=0.49024; metrics/mAP50-95(B)=0.33924 (7/30)
- 2026-11-07 04:47:46 PROGRESS C: 60 min; epoch=8; train/box_loss=0.97754; val/box_loss=0.96141; metrics/mAP50(B)=0.49219; metrics/mAP50-95(B)=0.34481 (8/30)
- 2026-11-07 04:57:46 PROGRESS C: 70 min; epoch=10; train/box_loss=0.94808; val/box_loss=0.9107; metrics/mAP50(B)=0.51203; metrics/mAP50-95(B)=0.35744 (10/30)
- 2026-11-07 05:07:46 PROGRESS C: 80 min; epoch=12; train/box_loss=0.92736; val/box_loss=0.91521; metrics/mAP50(B)=0.53831; metrics/mAP50-95(B)=0.38351 (12/30)
- 2026-11-07 05:17:46 PROGRESS C: 90 min; epoch=13; train/box_loss=0.92445; val/box_loss=0.91653; metrics/mAP50(B)=0.55361; metrics/mAP50-95(B)=0.38813 (13/30)
- 2026-11-07 05:27:46 PROGRESS C: 100 min; epoch=15; train/box_loss=0.89847; val/box_loss=0.89528; metrics/mAP50(B)=0.51746; metrics/mAP50-95(B)=0.37032 (15/30)
- 2026-11-07 05:37:46 PROGRESS C: 110 min; epoch=16; train/box_loss=0.88723; val/box_loss=0.88085; metrics/mAP50(B)=0.54003; metrics/mAP50-95(B)=0.38645 (16/30)
- 2026-11-07 05:47:46 PROGRESS C: 120 min; epoch=18; train/box_loss=0.87075; val/box_loss=0.89273; metrics/mAP50(B)=0.56042; metrics/mAP50-95(B)=0.39933 (18/30)
- 2026-11-07 05:57:46 PROGRESS C: 130 min; epoch=19; train/box_loss=0.86435; val/box_loss=0.90373; metrics/mAP50(B)=0.55716; metrics/mAP50-95(B)=0.40305 (19/30)
- 2026-11-07 06:07:46 PROGRESS C: 140 min; epoch=21; train/box_loss=0.83351; val/box_loss=0.88627; metrics/mAP50(B)=0.57116; metrics/mAP50-95(B)=0.41262 (21/30)
- 2026-11-07 06:17:46 PROGRESS C: 150 min; epoch=22; train/box_loss=0.82356; val/box_loss=0.88608; metrics/mAP50(B)=0.5736; metrics/mAP50-95(B)=0.41521 (22/30)
- 2026-11-07 06:27:46 PROGRESS C: 160 min; epoch=24; train/box_loss=0.79889; val/box_loss=0.88566; metrics/mAP50(B)=0.58562; metrics/mAP50-95(B)=0.42413 (24/30)
- 2026-11-07 06:37:46 PROGRESS C: 170 min; epoch=26; train/box_loss=0.77699; val/box_loss=0.88553; metrics/mAP50(B)=0.57423; metrics/mAP50-95(B)=0.41298 (26/30)
- 2026-11-07 06:47:46 PROGRESS C: 180 min; epoch=28; train/box_loss=0.76199; val/box_loss=0.89273; metrics/mAP50(B)=0.58013; metrics/mAP50-95(B)=0.41859 (28/30)
- 2026-11-07 06:57:46 PROGRESS C: 190 min; epoch=29; train/box_loss=0.75267; val/box_loss=0.88393; metrics/mAP50(B)=0.58436; metrics/mAP50-95(B)=0.42236 (29/30)
- 2026-11-07 07:00:16 DONE train C exit 0 after 192 min; epoch=30; train/box_loss=0.74402; val/box_loss=0.88521; metrics/mAP50(B)=0.5837; metrics/mAP50-95(B)=0.42177 (30/30)
- 2026-11-07 07:00:16 START train B pid=27972 cap=7h
- 2026-11-07 07:10:16 PROGRESS B: 10 min; epoch=2; train/box_loss=1.02857; val/box_loss=0.94745; metrics/mAP50(B)=0.41286; metrics/mAP50-95(B)=0.29531 (2/30)
- 2026-11-07 07:20:16 PROGRESS B: 20 min; epoch=4; train/box_loss=1.014; val/box_loss=0.90655; metrics/mAP50(B)=0.45969; metrics/mAP50-95(B)=0.32852 (4/30)
- 2026-11-07 07:30:16 PROGRESS B: 30 min; epoch=6; train/box_loss=0.96235; val/box_loss=0.86111; metrics/mAP50(B)=0.45538; metrics/mAP50-95(B)=0.33375 (6/30)
- 2026-11-07 07:40:16 PROGRESS B: 40 min; epoch=8; train/box_loss=0.92446; val/box_loss=0.84521; metrics/mAP50(B)=0.4935; metrics/mAP50-95(B)=0.36764 (8/30)
- 2026-11-07 07:50:16 PROGRESS B: 50 min; epoch=10; train/box_loss=0.89324; val/box_loss=0.85587; metrics/mAP50(B)=0.48518; metrics/mAP50-95(B)=0.3555 (10/30)
- 2026-11-07 08:00:16 PROGRESS B: 60 min; epoch=13; train/box_loss=0.85705; val/box_loss=0.86606; metrics/mAP50(B)=0.50093; metrics/mAP50-95(B)=0.36673 (13/30)
- 2026-11-07 08:10:16 PROGRESS B: 70 min; epoch=15; train/box_loss=0.83888; val/box_loss=0.85018; metrics/mAP50(B)=0.52432; metrics/mAP50-95(B)=0.38791 (15/30)
- 2026-11-07 08:20:16 PROGRESS B: 80 min; epoch=17; train/box_loss=0.82079; val/box_loss=0.83918; metrics/mAP50(B)=0.51815; metrics/mAP50-95(B)=0.38321 (17/30)
- 2026-11-07 08:30:16 PROGRESS B: 90 min; epoch=19; train/box_loss=0.8029; val/box_loss=0.82788; metrics/mAP50(B)=0.59975; metrics/mAP50-95(B)=0.45488 (19/30)
- 2026-11-07 08:40:16 PROGRESS B: 100 min; epoch=21; train/box_loss=0.79033; val/box_loss=0.80926; metrics/mAP50(B)=0.54804; metrics/mAP50-95(B)=0.40874 (21/30)
- 2026-11-07 08:50:16 PROGRESS B: 110 min; epoch=24; train/box_loss=0.75352; val/box_loss=0.8347; metrics/mAP50(B)=0.55455; metrics/mAP50-95(B)=0.41418 (24/30)
- 2026-11-07 09:00:16 PROGRESS B: 120 min; epoch=26; train/box_loss=0.73334; val/box_loss=0.80419; metrics/mAP50(B)=0.58368; metrics/mAP50-95(B)=0.43899 (26/30)
- 2026-11-07 09:10:16 DONE train B exit 0 after 130 min; epoch=29; train/box_loss=0.70887; val/box_loss=0.79333; metrics/mAP50(B)=0.58554; metrics/mAP50-95(B)=0.43973 (29/30)
- 2026-11-07 09:16:02 DONE score_v8.py exit 0
- 2026-11-07 09:16:04 DONE plot_v8.py exit 0
- 2026-11-07 09:16:04 PIPELINE_END C rc=0, B rc=0

## Results (2026-11-07 09:16)
- Pipeline finished: C rc=0 (30 epochs, 192 min), B rc=0 (early stop after epoch 29, best epoch 19, 130 min), score_v8 and plot_v8 exit 0.
- Control reproduced exactly (58/93, 107/249, 50/226). Verdict per DECISION_RULE.md: B vs A and C vs A both "no clear difference". Empty room 0/4101 for all.
- Leakage check: no CAUCAFall S10 frames and no ExDark test images in C train/val.
- Bed regression on With_people_Bedroom sets traced (likely) to the 1,260 bed boxes in the removed clips.
- REPORT.md written (full report, figures, supervisor message).

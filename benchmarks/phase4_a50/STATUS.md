# Phase 4 STATUS: A50 (current recipe, 50 epochs)

**PROVISIONAL:** held-out scores are provisional (held-out labels follow no written convention yet; docs/LABELLING_SPEC.md v0.1 draft).

- Requested by Hussain on 2026-10-19 after the supervisor suggested more epochs. Hussain chose the A recipe on the full v7 data.
- build_A50.py: datasets\sage_merged_v7_A50 built and verified (build_verify.json ALL_OK); baseline_hashes_original.csv = 17,655 original label files.
- DECISION_RULE.md written before training.
- Training: supervise_A50.py launches train_A50.py (9 h cap, one resume retry on OOM / WinError 1455 only).

## A50 training progress
- 2026-10-19 01:17:11 START pid=32864 cap=9h poll=10min
- 2026-10-19 01:27:11 PROGRESS elapsed 10 min; epoch=1; train/box_loss=1.10182; train/cls_loss=2.0133; val/box_loss=0.94417; metrics/mAP50(B)=0.33459; metrics/mAP50-95(B)=0.22707 (1/50 epochs logged)
- 2026-10-19 01:37:11 PROGRESS elapsed 20 min; epoch=2; train/box_loss=1.10436; train/cls_loss=1.50043; val/box_loss=1.01203; metrics/mAP50(B)=0.26223; metrics/mAP50-95(B)=0.18058 (2/50 epochs logged)
- 2026-10-19 01:47:11 PROGRESS elapsed 30 min; epoch=3; train/box_loss=1.18643; train/cls_loss=1.57503; val/box_loss=1.06896; metrics/mAP50(B)=0.24257; metrics/mAP50-95(B)=0.163 (3/50 epochs logged)
- 2026-10-19 01:57:11 PROGRESS elapsed 40 min; epoch=5; train/box_loss=1.14251; train/cls_loss=1.48819; val/box_loss=0.97573; metrics/mAP50(B)=0.28756; metrics/mAP50-95(B)=0.19702 (5/50 epochs logged)
- 2026-10-19 02:07:11 PROGRESS elapsed 50 min; epoch=6; train/box_loss=1.09495; train/cls_loss=1.41486; val/box_loss=0.9392; metrics/mAP50(B)=0.29676; metrics/mAP50-95(B)=0.20366 (6/50 epochs logged)
- 2026-10-19 02:08:48 ABORTED the 01:17 attempt above after ~1 min (optimizer=auto switched to MuSGD lr 0.01). Files moved to aborted_musgd_attempt\. Relaunching with optimizer pinned to AdamW lr0 0.000588 momentum 0.9 (Hussain's choice).

## A50 training progress
- 2026-10-19 02:08:48 START pid=48864 cap=9h poll=10min
- 2026-10-19 02:18:48 PROGRESS elapsed 10 min; epoch=1; train/box_loss=1.10585; train/cls_loss=2.1326; val/box_loss=0.84028; metrics/mAP50(B)=0.44736; metrics/mAP50-95(B)=0.31169 (1/50 epochs logged)
- 2026-10-19 02:28:48 PROGRESS elapsed 20 min; epoch=2; train/box_loss=1.07007; train/cls_loss=1.54901; val/box_loss=0.887; metrics/mAP50(B)=0.36206; metrics/mAP50-95(B)=0.25052 (2/50 epochs logged)
- 2026-10-19 02:38:48 PROGRESS elapsed 30 min; epoch=3; train/box_loss=1.06027; train/cls_loss=1.43807; val/box_loss=0.86999; metrics/mAP50(B)=0.35163; metrics/mAP50-95(B)=0.24249 (3/50 epochs logged)
- 2026-10-19 02:48:48 PROGRESS elapsed 40 min; epoch=5; train/box_loss=1.01066; train/cls_loss=1.29416; val/box_loss=0.8992; metrics/mAP50(B)=0.36616; metrics/mAP50-95(B)=0.25232 (5/50 epochs logged)
- 2026-10-19 02:58:48 PROGRESS elapsed 50 min; epoch=6; train/box_loss=0.98386; train/cls_loss=1.24499; val/box_loss=0.86361; metrics/mAP50(B)=0.40194; metrics/mAP50-95(B)=0.28427 (6/50 epochs logged)
- 2026-10-19 03:08:48 PROGRESS elapsed 60 min; epoch=8; train/box_loss=0.93823; train/cls_loss=1.15968; val/box_loss=0.81456; metrics/mAP50(B)=0.42111; metrics/mAP50-95(B)=0.30193 (8/50 epochs logged)
- 2026-10-19 03:18:48 PROGRESS elapsed 70 min; epoch=9; train/box_loss=0.92627; train/cls_loss=1.13449; val/box_loss=0.90001; metrics/mAP50(B)=0.40241; metrics/mAP50-95(B)=0.28255 (9/50 epochs logged)
- 2026-10-19 03:28:48 PROGRESS elapsed 80 min; epoch=11; train/box_loss=0.89906; train/cls_loss=1.08896; val/box_loss=0.82824; metrics/mAP50(B)=0.45186; metrics/mAP50-95(B)=0.31871 (11/50 epochs logged)
- 2026-10-19 03:38:48 PROGRESS elapsed 90 min; epoch=12; train/box_loss=0.88781; train/cls_loss=1.06776; val/box_loss=0.83507; metrics/mAP50(B)=0.43798; metrics/mAP50-95(B)=0.30811 (12/50 epochs logged)
- 2026-10-19 03:48:48 PROGRESS elapsed 100 min; epoch=14; train/box_loss=0.87473; train/cls_loss=1.04591; val/box_loss=0.86507; metrics/mAP50(B)=0.44711; metrics/mAP50-95(B)=0.31971 (14/50 epochs logged)
- 2026-10-19 03:58:48 PROGRESS elapsed 110 min; epoch=15; train/box_loss=0.86511; train/cls_loss=1.02567; val/box_loss=0.83976; metrics/mAP50(B)=0.45991; metrics/mAP50-95(B)=0.32742 (15/50 epochs logged)
- 2026-10-19 04:08:48 PROGRESS elapsed 120 min; epoch=16; train/box_loss=0.8508; train/cls_loss=0.9996; val/box_loss=0.83862; metrics/mAP50(B)=0.46493; metrics/mAP50-95(B)=0.33124 (16/50 epochs logged)
- 2026-10-19 04:18:48 PROGRESS elapsed 130 min; epoch=18; train/box_loss=0.83693; train/cls_loss=0.97847; val/box_loss=0.82334; metrics/mAP50(B)=0.47523; metrics/mAP50-95(B)=0.33785 (18/50 epochs logged)
- 2026-10-19 04:28:48 PROGRESS elapsed 140 min; epoch=19; train/box_loss=0.83506; train/cls_loss=0.97033; val/box_loss=0.79312; metrics/mAP50(B)=0.48083; metrics/mAP50-95(B)=0.34889 (19/50 epochs logged)
- 2026-10-19 04:38:48 PROGRESS elapsed 150 min; epoch=21; train/box_loss=0.82606; train/cls_loss=0.95418; val/box_loss=0.81971; metrics/mAP50(B)=0.48942; metrics/mAP50-95(B)=0.35193 (21/50 epochs logged)
- 2026-10-19 04:48:48 PROGRESS elapsed 160 min; epoch=22; train/box_loss=0.81813; train/cls_loss=0.94139; val/box_loss=0.79218; metrics/mAP50(B)=0.49226; metrics/mAP50-95(B)=0.35702 (22/50 epochs logged)
- 2026-10-19 04:58:48 PROGRESS elapsed 170 min; epoch=24; train/box_loss=0.81619; train/cls_loss=0.92832; val/box_loss=0.79306; metrics/mAP50(B)=0.49054; metrics/mAP50-95(B)=0.35764 (24/50 epochs logged)
- 2026-10-19 05:08:48 PROGRESS elapsed 180 min; epoch=25; train/box_loss=0.80154; train/cls_loss=0.91052; val/box_loss=0.79445; metrics/mAP50(B)=0.50758; metrics/mAP50-95(B)=0.36652 (25/50 epochs logged)
- 2026-10-19 05:18:48 PROGRESS elapsed 190 min; epoch=26; train/box_loss=0.79691; train/cls_loss=0.90396; val/box_loss=0.80348; metrics/mAP50(B)=0.50378; metrics/mAP50-95(B)=0.36545 (26/50 epochs logged)
- 2026-10-19 05:28:48 PROGRESS elapsed 200 min; epoch=28; train/box_loss=0.78254; train/cls_loss=0.88435; val/box_loss=0.8021; metrics/mAP50(B)=0.51421; metrics/mAP50-95(B)=0.37703 (28/50 epochs logged)
- 2026-10-19 05:38:48 PROGRESS elapsed 210 min; epoch=29; train/box_loss=0.78423; train/cls_loss=0.8821; val/box_loss=0.80413; metrics/mAP50(B)=0.50939; metrics/mAP50-95(B)=0.37298 (29/50 epochs logged)
- 2026-10-19 05:48:48 PROGRESS elapsed 220 min; epoch=31; train/box_loss=0.77106; train/cls_loss=0.86061; val/box_loss=0.79438; metrics/mAP50(B)=0.51621; metrics/mAP50-95(B)=0.3736 (31/50 epochs logged)
- 2026-10-19 05:58:48 PROGRESS elapsed 230 min; epoch=32; train/box_loss=0.77213; train/cls_loss=0.86118; val/box_loss=0.79393; metrics/mAP50(B)=0.51318; metrics/mAP50-95(B)=0.37411 (32/50 epochs logged)
- 2026-10-19 06:08:48 PROGRESS elapsed 240 min; epoch=34; train/box_loss=0.76356; train/cls_loss=0.8452; val/box_loss=0.79121; metrics/mAP50(B)=0.51833; metrics/mAP50-95(B)=0.37992 (34/50 epochs logged)
- 2026-10-19 06:18:48 PROGRESS elapsed 250 min; epoch=35; train/box_loss=0.75556; train/cls_loss=0.83184; val/box_loss=0.77213; metrics/mAP50(B)=0.51873; metrics/mAP50-95(B)=0.38122 (35/50 epochs logged)
- 2026-10-19 06:28:48 PROGRESS elapsed 260 min; epoch=37; train/box_loss=0.74629; train/cls_loss=0.81042; val/box_loss=0.76713; metrics/mAP50(B)=0.51866; metrics/mAP50-95(B)=0.38081 (37/50 epochs logged)
- 2026-10-19 06:38:48 PROGRESS elapsed 270 min; epoch=38; train/box_loss=0.73877; train/cls_loss=0.80815; val/box_loss=0.77733; metrics/mAP50(B)=0.52093; metrics/mAP50-95(B)=0.38123 (38/50 epochs logged)
- 2026-10-19 06:48:48 PROGRESS elapsed 280 min; epoch=39; train/box_loss=0.73722; train/cls_loss=0.79795; val/box_loss=0.7797; metrics/mAP50(B)=0.52085; metrics/mAP50-95(B)=0.38263 (39/50 epochs logged)
- 2026-10-19 06:58:48 PROGRESS elapsed 290 min; epoch=41; train/box_loss=0.72094; train/cls_loss=0.73007; val/box_loss=0.77967; metrics/mAP50(B)=0.51734; metrics/mAP50-95(B)=0.38045 (41/50 epochs logged)
- 2026-10-19 07:08:48 PROGRESS elapsed 300 min; epoch=42; train/box_loss=0.71514; train/cls_loss=0.7169; val/box_loss=0.77818; metrics/mAP50(B)=0.51129; metrics/mAP50-95(B)=0.37733 (42/50 epochs logged)
- 2026-10-19 07:18:48 PROGRESS elapsed 310 min; epoch=44; train/box_loss=0.69946; train/cls_loss=0.69185; val/box_loss=0.7723; metrics/mAP50(B)=0.51005; metrics/mAP50-95(B)=0.37661 (44/50 epochs logged)
- 2026-10-19 07:28:48 PROGRESS elapsed 320 min; epoch=45; train/box_loss=0.69325; train/cls_loss=0.68625; val/box_loss=0.77746; metrics/mAP50(B)=0.51271; metrics/mAP50-95(B)=0.37672 (45/50 epochs logged)
- 2026-10-19 07:38:48 PROGRESS elapsed 330 min; epoch=47; train/box_loss=0.685; train/cls_loss=0.67136; val/box_loss=0.77816; metrics/mAP50(B)=0.51457; metrics/mAP50-95(B)=0.37732 (47/50 epochs logged)
- 2026-10-19 07:48:48 PROGRESS elapsed 340 min; epoch=49; train/box_loss=0.67198; train/cls_loss=0.6565; val/box_loss=0.77586; metrics/mAP50(B)=0.51888; metrics/mAP50-95(B)=0.38039 (49/50 epochs logged)
- 2026-10-19 07:54:48 DONE exit 0 after 346 min; epoch=50; train/box_loss=0.67144; train/cls_loss=0.65097; val/box_loss=0.77427; metrics/mAP50(B)=0.5173; metrics/mAP50-95(B)=0.38005 (50/50 epochs logged)

## Outcome (2026-10-19 08:03)
- Training: exit 0 after 346 min, 50/50 epochs, no retry, early stopping not triggered. Best epoch 40. Final val (best.pt): all mAP50 0.523 / mAP50-95 0.385 (A: 0.523 / 0.385); person mAP50 0.914.
- Scoring (score_A50.py -> RESULTS.md, a5_scores.json, hits_A.csv, hits_A50.csv): control reproduced 58/93, 107/249, 50/226. Person @IoU0.5: heldout_objects 58->59/93, reserved388_partial 107->109/249 (p=0.69), round6_heldout 50->51/226 (p=1.0). Empty room 0/4101 both.
- **Verdict (DECISION_RULE.md): no clear difference.**
- Integrity (integrity.json): CLEAN. No tracked files changed; no new top-level items in ROOT.
- Chart: A_A2_A50_training_curves.png.

# Overnight run -- STATUS

- updated: 2026-10-10 06:35:29
- run start: 2026-10-10 01:47  |  elapsed: 4.81 h  |  budget ends 13:47 (7.19 h left)

| stage | status | start | end | minutes | note |
|---|---|---|---|---|---|
| S0_preflight | done | 02:09:43 | 02:10:58 | 1.2 |  |
| S1_control | done | 02:10:58 | 02:14:58 | 4.0 |  |
| S2_stock | done | 02:14:58 | 02:25:28 | 10.5 |  |
| S3_enhance_A_stock | done | 02:25:28 | 02:31:28 | 6.0 |  |
| S4a_pose_score | done | 02:31:28 | 02:33:13 | 1.8 |  |
| S4b_pose_speed | done | 02:33:13 | 02:56:58 | 23.8 |  |
| S5_train_B | done | 02:56:58 | 06:28:59 | 212.0 | succeeded on attempt fresh |
| S5_train_B__attempt1_fresh | done | 02:56:58 | 06:28:59 | 212.0 |  |
| S5_score_B | done | 06:28:59 | 06:31:59 | 3.0 |  |
| S6_gate | done | 06:31:59 | 06:32:14 | 0.2 |  |
| S6_train_C | skipped |  |  |  | C SKIPPED: recall_within_0.02_on_each_set |
| S6_enhance_BC | done | 06:32:14 | 06:35:14 | 3.0 |  |
| S7_report | done | 06:35:14 | 06:35:29 | 0.2 |  |

- B_yolo26n_30ep: 31 epoch records; last epoch 31 took 413s; mAP50=0.5256 mAP50-95=0.3922

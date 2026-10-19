# Phase 3 STATUS

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

**STATE: ALL STAGES COMPLETE.** A5 verdict: **no clear difference** (see RESULTS.md). A6: CLEAN.

Started 2026-10-14T23:42+05:00. Paused before A4 on 2026-10-15. A4 started on Hussain's exact phrase on 2026-10-18 01:45. Finished 2026-10-18 04:41.

Sleep check: sleep after on AC = never; hibernate after on AC = never; laptop on AC. No warning.

| Part/Stage | Status | Notes |
|---|---|---|
| C1 venv + roboflow | DONE | roboflow 1.7.1 in D:\FYP\PROJECT FILES\_tools\venv_roboflow. 3 pip attempts failed or hung on the opencv wheel (ReadTimeoutError). The wheel was fetched from the same PyPI URL with resumable curl, SHA256 matched PyPI, and installed from the local file. Help output saved to roboflow\cli_help.txt. |
| C2 staging | DONE | 298 images + 298 labels (real copies), data.yaml with 13 names; ids 0/5/7 only. |
| C3 upload script | DONE, NOT RUN | All 3 refusal paths tested. The upload path itself is untested (needs a key). |
| C4 setup doc | DONE | Private-project availability on the free plan and the opt-out menu name: UNKNOWN (docs not reachable or 404). |
| C5 check_export + rescore | DONE | check_export ALL PASS on the staging folder. import_corrected_labels.py and rescore_suite.py syntax-checked only (they write to handlabels/, so Hussain runs them). |
| B review pack | DONE | 298 overlays, 153 brightened, review_sheet.csv (judgement columns blank), index.html offline. |
| A0 preflight | DONE | .venv2: ultralytics 8.4.115, torch 2.13.0+cu126, CUDA True. |
| A1 inventory | DONE | See a1_inventory.json, a1_provenance.csv. |
| A2 drop rule | DONE | 2450 dropped, 0 ambiguous. See A2_DROP_DECISION.md. |
| A3 build copy | DONE | train 12593, val 2610, ALL_OK (a3_verify.json). |
| Integrity re-check | DONE | Original labels 17655/17655 unchanged (hash + mtime), checked twice. |
| A4 train | DONE: exit 0, 169 min, 30/30 epochs, no retry. Final val (best.pt): all mAP50 0.525 / mAP50-95 0.384; person mAP50 0.907 / mAP50-95 0.643. | Exact phrase "START A2 TRAINING" received from Hussain in chat on 2026-10-18. Launched by supervise_A2.py; progress lines appended at the end of this file. |
| A5 score | DONE 04:34-04:39. Control reproduced 58/93, 107/249, 50/226. Verdict: no clear difference (round6_heldout McNemar p=0.219 fails; reserved388_partial p=0.0117 meets). Empty room 0/4101 both. | DECISION_RULE.md written 2026-10-18T01:46, before any scoring. Harness score_A5.py ready (dry run: 93 / 249 / 226 person boxes, 6 empty-room clips). It imports score_v7_suite.score_model unchanged; per-box hits come from an instrumented copy of the same loop, asserted equal; empty room via score_empty_false_positives.score_clip. It does NOT import overnight_yolo26/common.py, which hardcodes ROOT=D:\FYP\PROJECT FILES\fatima and creates folders there on import. |
| A6 integrity | DONE 04:41: CLEAN | Original labels 17655/17655 identical (hash, size, mtime), 0 new or missing files; 0 original images modified after training start. No files written to results/ or overnight_yolo26/raw/; no tracked file modified; nothing new at ROOT top level. |

## Deviations
- Ran Part B and A0-A3 while C1's pip install was stuck on the network. There is no dependency between them.
- Provenance uses byte identity OR canonical identity; byte identity alone matches only round5.
- Hardlinks only for images that end in FFD9 (all 15203 did).
- C1: the opencv wheel came via resumable curl from PyPI (hash-verified), not pip's own download.
- C4: the key is entered with Read-Host -AsSecureString, not `$env:... = "<paste>"`, because PSReadLine history would likely store the pasted key on disk.
- `roboflow import` exists (an alias of `image upload`). `-w` is a global option and goes before the subcommand. The upload script uses `roboflow -w <ws> image upload <dir> -p <project> -b <batch> -r 3`.

## A4 training progress
- 2026-10-18 01:45:02 START pid=22820 cap=6h poll=10min
- 2026-10-18 01:55:02 PROGRESS elapsed 10 min; epoch=1; train/box_loss=1.06451; train/cls_loss=2.06882; val/box_loss=0.855; metrics/mAP50(B)=0.40245; metrics/mAP50-95(B)=0.28539 (1/30 epochs logged)
- 2026-10-18 02:05:02 PROGRESS elapsed 20 min; epoch=2; train/box_loss=1.01682; train/cls_loss=1.4681; val/box_loss=0.87697; metrics/mAP50(B)=0.38217; metrics/mAP50-95(B)=0.26458 (2/30 epochs logged)
- 2026-10-18 02:15:02 PROGRESS elapsed 30 min; epoch=4; train/box_loss=0.99827; train/cls_loss=1.29334; val/box_loss=0.89625; metrics/mAP50(B)=0.38122; metrics/mAP50-95(B)=0.27023 (4/30 epochs logged)
- 2026-10-18 02:25:02 PROGRESS elapsed 40 min; epoch=6; train/box_loss=0.93192; train/cls_loss=1.16635; val/box_loss=0.88883; metrics/mAP50(B)=0.39941; metrics/mAP50-95(B)=0.28071 (6/30 epochs logged)
- 2026-10-18 02:35:02 PROGRESS elapsed 50 min; epoch=8; train/box_loss=0.8936; train/cls_loss=1.09827; val/box_loss=0.90192; metrics/mAP50(B)=0.43871; metrics/mAP50-95(B)=0.30919 (8/30 epochs logged)
- 2026-10-18 02:45:02 PROGRESS elapsed 60 min; epoch=9; train/box_loss=0.87869; train/cls_loss=1.05342; val/box_loss=0.84338; metrics/mAP50(B)=0.44284; metrics/mAP50-95(B)=0.3141 (9/30 epochs logged)
- 2026-10-18 02:55:02 PROGRESS elapsed 70 min; epoch=11; train/box_loss=0.85253; train/cls_loss=1.01654; val/box_loss=0.85207; metrics/mAP50(B)=0.44864; metrics/mAP50-95(B)=0.32218 (11/30 epochs logged)
- 2026-10-18 03:05:02 PROGRESS elapsed 80 min; epoch=13; train/box_loss=0.83011; train/cls_loss=0.97689; val/box_loss=0.8195; metrics/mAP50(B)=0.46075; metrics/mAP50-95(B)=0.32811 (13/30 epochs logged)
- 2026-10-18 03:15:02 PROGRESS elapsed 90 min; epoch=15; train/box_loss=0.80707; train/cls_loss=0.93913; val/box_loss=0.82187; metrics/mAP50(B)=0.47595; metrics/mAP50-95(B)=0.34123 (15/30 epochs logged)
- 2026-10-18 03:25:02 PROGRESS elapsed 100 min; epoch=17; train/box_loss=0.79506; train/cls_loss=0.91636; val/box_loss=0.7968; metrics/mAP50(B)=0.48543; metrics/mAP50-95(B)=0.35391 (17/30 epochs logged)
- 2026-10-18 03:35:02 PROGRESS elapsed 110 min; epoch=18; train/box_loss=0.78232; train/cls_loss=0.89312; val/box_loss=0.82565; metrics/mAP50(B)=0.4981; metrics/mAP50-95(B)=0.35975 (18/30 epochs logged)
- 2026-10-18 03:45:02 PROGRESS elapsed 120 min; epoch=20; train/box_loss=0.77166; train/cls_loss=0.86582; val/box_loss=0.79871; metrics/mAP50(B)=0.50742; metrics/mAP50-95(B)=0.3711 (20/30 epochs logged)
- 2026-10-18 03:55:02 PROGRESS elapsed 130 min; epoch=22; train/box_loss=0.74895; train/cls_loss=0.79849; val/box_loss=0.80321; metrics/mAP50(B)=0.51453; metrics/mAP50-95(B)=0.37826 (22/30 epochs logged)
- 2026-10-18 04:05:02 PROGRESS elapsed 140 min; epoch=24; train/box_loss=0.72571; train/cls_loss=0.75256; val/box_loss=0.82299; metrics/mAP50(B)=0.5087; metrics/mAP50-95(B)=0.37073 (24/30 epochs logged)
- 2026-10-18 04:15:02 PROGRESS elapsed 150 min; epoch=26; train/box_loss=0.70971; train/cls_loss=0.72754; val/box_loss=0.83195; metrics/mAP50(B)=0.51945; metrics/mAP50-95(B)=0.38157 (26/30 epochs logged)
- 2026-10-18 04:25:02 PROGRESS elapsed 160 min; epoch=28; train/box_loss=0.6867; train/cls_loss=0.69954; val/box_loss=0.8048; metrics/mAP50(B)=0.52132; metrics/mAP50-95(B)=0.38295 (28/30 epochs logged)
- 2026-10-18 04:34:02 DONE exit 0 after 169 min; epoch=30; train/box_loss=0.68109; train/cls_loss=0.67843; val/box_loss=0.80085; metrics/mAP50(B)=0.52528; metrics/mAP50-95(B)=0.38423 (30/30 epochs logged)

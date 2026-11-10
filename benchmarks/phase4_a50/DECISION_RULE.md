# DECISION RULE (pre-registered): A50 vs A

Written: 2026-10-19T01:16:44.4270853+05:00, before A50 training started and before any A50 scoring.

**PROVISIONAL:** every held-out score is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

**Question (from the supervisor):** does training the current recipe for 50 epochs instead of 30 improve the detector?

**A50:** the recorded v7 train_args with only these changes: epochs 30 -> 50, data = datasets/sage_merged_v7_A50/data_A50.yaml (a full hardlink copy of sage_merged_v7, nothing dropped), project/name, workers 0, device 0, exist_ok False. Starting weights = recorded models/yolov8n.pt. Unchanged: patience 10 (early stopping may end it before 50), close_mosaic 10 (mosaic switches off for the last 10 epochs, i.e. 41-50), the LR schedule decays over the full 50 epochs, seed 0, deterministic.

**Rule:** A50 is clearly better than A only if, on round6_heldout AND reserved388_partial, an exact McNemar test on per-box person hits (A vs A50) gives p < 0.05 with A50 hitting more boxes, AND the empty-room false-positive count is reported alongside. Anything else is 'no clear difference'.

**Fixed details:** person class, IoU 0.5, conf 0.4, imgsz 640, same-class greedy matching (src/detection/score_v7_suite.py), two-sided exact McNemar. Control: A must reproduce 58/93, 107/249, 50/226 or no comparison is reported. Val mAP is reported but not used for the decision.

## Amendment (2026-10-19T02:08:39.2343457+05:00), before any A50 result existed
The first launch (01:17) was stopped after ~1 minute: with epochs=50, optimizer=auto switched from AdamW (lr 0.000588, what A used) to MuSGD (lr 0.01), because Ultralytics picks SGD when total iterations exceed 10,000 (A: ~7,080; A50: ~11,800). Hussain chose to pin optimizer=AdamW, lr0=0.000588, momentum=0.9 so epochs is the only training difference. The aborted attempt is kept in aborted_musgd_attempt/. The decision rule itself is unchanged.

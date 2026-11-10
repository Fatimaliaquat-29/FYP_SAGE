# Phase 6 PLAN (2026-11-08 night): training settings sweep + re-adding the 4 clips

Requested by Hussain: try different learning rates, scheduling and batch size, and optionally re-add the 4 problem
clips; report with the same kind of images as A vs B vs C.

## Design
- **Baseline = phase-5 C** (not retrained). Every run changes exactly one thing vs C, so any difference is caused by
  that one change (plus training randomness: see caveat). Base args are read from phase-5 C's effective args file.
- **Runs** (30 epochs, patience 10, seed 0, YOLOv8n, workers 0, same as C):

  | run | change | why |
  |---|---|---|
  | LR2 | lr0 0.000588 -> 0.001176 | learning rate; 0.000588 was tuned for v7's 13 classes, never for the 7-class data |
  | COS | linear decay -> cosine schedule | scheduling |
  | B8 | batch 16 -> 8 | batch size (see note) |
  | D | C's data + 4 clips re-added after filtering | fix the bed regression (1,260 bed boxes lost with the clips) |

- **Batch-size note:** Ultralytics accumulates gradients up to a nominal batch of 64 (nbs=64), so the effective batch
  is 64 for batch 8, 16 or 32; batch size mainly changes BatchNorm statistics and speed. Batch 32 (~3.8 GB) cannot
  share the 6 GB GPU with a second run, so the parallel plan uses batch 8; B32 can run alone later.
- **Parallel lanes:** training is CPU-bound (GPU ~25% busy, 2.1 GB, at batch 16 with workers 0), so two runs share the
  GPU: lane 0 = LR2 then COS, lane 1 = D then B8 (supervise_p6.py, queue.json). ~4-4.5 h per run when paired.
- **D filter** (build_D.py): hand-labelled frames kept; Blanket_Cover_HM frames 710-1420 dropped (teammate); all other
  frames (MediaPipe frames of the Dim clips, Bedroom_Falll) kept only if model C, which never saw these clips,
  confirms every labelled person box (IoU >= 0.5) and sees no unlabelled person. Bias: also drops valid frames that
  C cannot see (dim scenes).
- **Scoring:** score_p6.py (phase-5 harness unchanged, cached per model) + plot_p6.py run automatically after every
  finished run. Decision rule in DECISION_RULE.md (written before training).

## Caveat known in advance
One run per setting (seed 0). Changing any setting also changes the random training path, so small differences
(a few boxes) can be training noise; the McNemar test treats each trained model as fixed and does not cover that.

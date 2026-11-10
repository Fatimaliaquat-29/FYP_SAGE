# Phase 6 DECISION RULE (written 2026-11-08 ~03:20, before any phase-6 training or scoring)

**PROVISIONAL:** held-out labels follow no consistent written convention (docs/LABELLING_SPEC.md v0.1 draft).

**Baseline = C** from phase 5 (benchmarks/phase5_v8/runs/C/weights/best.pt: sage_v8_full data, YOLOv8n, 30 epochs,
batch 16, AdamW lr0 0.000588 momentum 0.9, linear LR decay to lrf 0.01, warmup 3, patience 10, seed 0). C is NOT retrained.

**Runs** (each changes exactly one thing vs C; everything else identical):
- LR2: lr0 0.001176 (2x C's learning rate)
- COS: cos_lr=True (cosine LR schedule instead of linear)
- B32: batch 32 instead of 16
- D: C's recipe on sage_v8_fixclips = C's data + the 4 problem clips re-added after filtering (see PLAN.md)
- B8: batch 8 instead of 16 (replaces a parallel B32: batch 32 needs ~3.8 GB and cannot share the 6 GB GPU with another run; amended 03:20 before any result)
- (if time allows) B32 alone, LRH: lr0 0.000294

**Primary rule (person):** run X is "clearly better than C" only if, on round6_heldout AND reserved388_partial, an exact
two-sided McNemar test on per-box person hits (C vs X, IoU 0.5) gives p < 0.05 with X hitting more boxes. "Clearly
worse" is the mirror. Anything else is "no clear difference". Empty-room person false positives reported alongside.
Control: A must reproduce 58/93, 107/249, 50/226.

**Secondary (reported, not decisive):** paired person tests vs C on cauca_s10 and exdark_test (all runs saw the same
domains, so this is fair within the C family); val mAP50 / mAP50-95 (C and all runs share the same val set, so val is
comparable within this phase); IoU 0.3; box fit (box_fit method from phase 5).

**D-specific question (pre-stated):** does re-adding the filtered clips fix the bed regression? Answered by an exact
McNemar test on per-box BED hits, C vs D, IoU 0.5, on reserved388_partial: "fixed" only if p < 0.05 with D hitting more.

## Amendment 2 (2026-11-08 11:10, after LR2/D/COS results, before any DCOS training)
New run **DCOS** = D's data (sage_v8_fixclips) + cos_lr True: the two changes that each helped a different thing
(D: beds, box fit; COS: person lying on the bed in With_people_Bedroom_Fall). This is chosen AFTER seeing results, so
it is exploratory and its comparisons are reported as such.
- Primary (same rule as before): DCOS vs C, McNemar p < 0.05 with DCOS ahead on BOTH round6_heldout and
  reserved388_partial = "clearly better". round6_heldout's Laying_Dim_HM shares a room with D's re-added clips (known).
- Secondary, reported but not decisive: DCOS vs D and vs COS (paired person hits per set), bed hits on
  reserved388_partial + heldout_objects, empty-room false alarms, false person boxes, box fit.
- If DCOS cannot finish (cap/failure), it is reported as not done; nothing is inferred from partial curves.

# v6 calibration diagnostic — vs v5 on eval/heldout_objects

93 hand-drawn person boxes; v5 detects 73 of them (conf>=0.001, imgsz=640). Restricted to boxes v5 finds, since the question is what v6 does differently on cases v5 already solves.

- **both_hit** (72): v6 also matches at IoU>=0.5 -- confidence-only comparison.
- **v5_only** (1): v6's best candidate in that region never reaches IoU 0.5 -- a localisation miss, not just a low score.

## both_hit: is the confidence gap constant across difficulty?

Bucketed by v5's own confidence (proxy for how easy the frame is). A roughly constant v6/v5 ratio across buckets is consistent with a monotonic recalibration. A ratio that collapses in the low-v5-confidence bucket means v6 is genuinely less sure specifically on hard cases, which recalibration cannot safely fix.

| v5 conf range | n | mean v5 conf | mean v6 conf | mean v6/v5 ratio | mean v6 IoU |
|---|---|---|---|---|---|
| 0.0-0.4 | 14 | 0.099 | 0.229 | 10.707 | 0.608 |
| 0.4-0.6 | 13 | 0.522 | 0.728 | 1.418 | 0.858 |
| 0.6-0.8 | 16 | 0.717 | 0.786 | 1.103 | 0.795 |
| 0.8-1.0 | 29 | 0.863 | 0.858 | 0.995 | 0.863 |

## v5_only: localisation misses

1 boxes where v5 is correct and v6's best candidate never overlaps enough to count as the same detection (mean best-candidate IoU 0.14, threshold 0.5). Mean v5 confidence on these: 0.001. v6 produced literally no candidate anywhere near 0/1 of these boxes (vs. a wrong-shaped/mislocated one for the rest).
Not a threshold problem -- no confidence cutoff recovers a box that isn't there.

## Recalibration sweep (both_hit population only)

What fraction of the both_hit boxes would clear a given v6 confidence threshold -- i.e. how much of THIS gap (not the v5_only localisation gap) a lower operating point could recover, with no model change.

| v6 threshold | both_hit boxes recovered |
|---|---|
| 0.4 | 60/72 (83%) |
| 0.25 | 63/72 (88%) |
| 0.1 | 68/72 (94%) |
| 0.05 | 71/72 (99%) |
| 0.02 | 71/72 (99%) |
| 0.01 | 71/72 (99%) |

This confirms the calibration ratio table above: on the general held-out set v6 is
already near v5-parity, so lowering the threshold barely moves this population --
it was never suppressed here.

## Same split, but on laying_dim.MOV (the hard clip, not this eval set)

Re-deriving the earlier per-frame diagnostic
(`results/yolo_person_detection/laying_dim_diagnostic/report.md`) with the same
both_hit/miss split (IoU>=0.5 vs <0.5) shows a completely different regime:

| population | n | mean v5 conf | mean v6 conf | note |
|---|---|---|---|---|
| both_hit (IoU>=0.5) | 33/62 | 0.444 | **0.025** | correct location, ~18x lower confidence |
| localisation miss (IoU<0.5) | 29/62 | 0.407 | 0.050 (best overlap, mean IoU 0.21) | wrong box, not a threshold problem |

v6 threshold sweep on laying_dim's both_hit subset only:

| v6 threshold | recovered |
|---|---|
| 0.4 | 0/33 (0%) |
| 0.25 | 0/33 (0%) |
| 0.10 | 2/33 (6%) |
| 0.05 | 2/33 (6%) |
| 0.02 | 10/33 (30%) |
| 0.01 | 25/33 (76%) |

Mean v6 confidence on laying_dim's both_hit set (0.025) is roughly 10x lower than
the worst bucket on the general eval set (0.229, v5 conf 0.0-0.4). The suppression
is not a fixed global offset -- it is much more severe specifically on this
clip's dim/occluded condition.

## False-positive cost of lowering the threshold (Reserved/Empty, every frame, imgsz 640)

| model | conf | FP frame rate | FP boxes | worst clip |
|---|---|---|---|---|
| v5 | 0.4 (current gate) | 0.00% | 0 | - |
| v6 | 0.4 (current gate) | 0.00% | 0 | - |
| v6 | 0.02 | 0.98% | 49 | TV_Lounge_2_Empty.mov: 6.04% |
| v6 | 0.01 | 6.49% | 371 | TV_Lounge_2_Empty.mov: 43.06% |

Both models are clean at the current gate. Lowering v6's threshold to 0.02 (needed
to recover 30% of laying_dim's both_hit subset) already introduces false positives
on 0.98% of held-out empty frames, concentrated in one room (6.04%). At 0.01
(needed for 76% recovery) that room false-fires on person **43% of its frames** --
the threshold low enough to help laying_dim is far past the point where it breaks
elsewhere.

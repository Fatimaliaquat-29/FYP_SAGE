# DECISION RULE (pre-registered): C and B vs A

Written 2026-11-07 ~03:15, before either dataset was built and before any training or scoring.

**PROVISIONAL:** every held-out score is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

**Questions:** (1) does C (cleaned classes, problem clips removed, + CAUCAFall + ExDark) detect people better than A (v7)? (2) B vs A and C vs B are reported to show which change did what.

**Rule (same as phases 3 and 4):** a model is clearly better than A only if, on round6_heldout AND reserved388_partial, an exact two-sided McNemar test on per-box person hits gives p < 0.05 with that model hitting more boxes, AND the empty-room false-positive count is reported alongside. It is clearly worse if the same holds in A's favour on both sets. Anything else is "no clear difference".

**Fixed details:** person class, IoU 0.5 (0.3 supplementary), conf 0.4, imgsz 640, same-class greedy matching (score_v7_suite logic). Control: A must reproduce 58/93, 107/249, 50/226 on person or no comparison is reported. Other classes are compared in the 7-class space (couch -> sofa, dining table -> table; dropped classes ignored) and reported, not used for the verdict. Val mAP is reported but not used (B and C have different val sets and class lists from A).

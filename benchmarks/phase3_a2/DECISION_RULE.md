# DECISION RULE (pre-registered)

Written: 2026-10-18T01:46:11.7866720+05:00, while A2 was still training and before any A2 scoring had been run.

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

A2 is clearly better than A only if, on round6_heldout AND reserved388_partial, an exact McNemar test on per-box hits (A vs A2) gives p < 0.05 with A2 hitting more boxes, AND the empty-room false-positive count is reported alongside. Anything else is 'no clear difference'.

Fixed details (set now, before scoring):
- Person boxes (class 0), IoU 0.5, conf 0.4, imgsz 640. Same-class greedy matching in descending confidence order, as in src/detection/score_v7_suite.py.
- The test is two-sided exact McNemar (binomial on the discordant pairs). "A2 hitting more boxes" means b(A2 only) > c(A only).
- Control first: A must reproduce heldout_objects 58/93, reserved388_partial 107/249 and round6_heldout 50/226 at IoU 0.5. If it does not, no A2 comparison is reported.

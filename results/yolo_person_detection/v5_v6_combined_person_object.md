# v5 vs v6 — person + object, one combined pass

`src/detection/score_heldout_combined.py`. Single `model.predict()` per image per
model, all 13 classes at once, conf 0.4, imgsz 640, IoU-0.5 match — the same
settings used throughout this project, on `eval/heldout_objects/` (200 hand-labelled
frames, 640 hand-drawn boxes). No class filtering, so person and object scoring
come from the identical inference pass, not two separate runs.

## Per-class

| class | n | v5 P | v5 R | v5 IoU | v5 tp/fp/fn | v6 P | v6 R | v6 IoU | v6 tp/fp/fn |
|---|---|---|---|---|---|---|---|---|---|
| person | 93 | 0.91 | 0.62 | 0.83 | 58/6/35 | 0.94 | 0.65 | 0.84 | 60/4/33 |
| chair | 90 | 0.67 | 0.20 | 0.92 | 18/9/72 | 0.45 | 0.20 | 0.92 | 18/22/72 |
| couch | 276 | 0.70 | 0.55 | 0.84 | 153/67/123 | 0.87 | 0.62 | 0.78 | 170/26/106 |
| bed | 86 | 0.44 | 0.35 | 0.64 | 30/38/56 | 0.56 | 0.10 | 0.76 | 9/7/77 |
| dining table | 94 | 0.00 | 0.00 | nan | 0/17/94 | 0.00 | 0.00 | nan | 0/18/94 |
| tv | 1 * | 0.00 | 0.00 | nan | 0/16/1 | nan | 0.00 | nan | 0/0/1 |

\* n < 10 — too few to say anything about this class alone.

`bottle`, `cup`, `wine glass`, `bowl`, `toilet`, `sink`, `refrigerator`: **0 hand-drawn
boxes** in this eval set. Cannot be scored against ground truth here at all —
see the refrigerator note below.

Person and furniture recall/precision were checked from the same pass: no
evidence of a trade-off where gaining on one cost the other. v6 improves on
person (recall 0.62→0.65, precision 0.91→0.94) and on couch (both P and R up)
simultaneously, so those two didn't come at each other's expense in this data.

## The open question: couch/refrigerator empty-room gap

The v6 results doc flagged v6 finding fewer couches (4,123 vs 5,804) and zero
refrigerators against v5 on the empty-room false-positive test, unscored
against ground truth. Now scored:

**Couch: not a regression — the opposite.** Against 276 hand-drawn boxes, v6
beats v5 on both recall (0.62 vs 0.55) and precision (0.87 vs 0.70, i.e. v5 has
2.6x v6's false-positive rate here). v6's matched boxes are slightly looser
(mean IoU 0.78 vs 0.84) but it finds more real couches and invents fewer fake
ones. The empty-room count gap is very likely v5 over-firing (consistent with
its lower precision here), not v6 under-detecting — frame composition/model
behavior, not a ground-truth-verified miss.

**Refrigerator: still unknown.** Zero hand-drawn refrigerator boxes exist in
`eval/heldout_objects/`. The "v6 finds zero refrigerators" empty-room
observation cannot be checked against any ground truth with the current
labels — would need frames with a labelled refrigerator to test, which do not
currently exist in this eval set.

## bed: a real regression

v6's bed recall collapses to 0.10 (9/86) from v5's 0.35 (30/86) on the exact
same 86 hand-drawn boxes — precision improves (0.56 vs 0.44) but that's beside
the point when 77 of 86 real beds go undetected. This lines up with the
empty-room bed count also dropping (855 → 393) — unlike couch, this one is
corroborated by hand-drawn ground truth, not just raw counts. Worth treating
as a real cost of v6, alongside the laying_dim regression already flagged.

## dining table: 0% recall for BOTH models — a labeling artifact, not a miss

Visually checked (`dining_table_sanity_check.jpg`, saved alongside this file):
the hand-drawn "dining table" box on `Empty_TV_Lounge_1_Empty_000060.jpg` sits
on a **low coffee table**, and both models correctly box that exact object at
~0.86 confidence — labelled `couch` (0.86 v5, 0.86 v6), not `dining table`.
Both models DO fire a `dining table` prediction elsewhere in this eval set (17
and 18 times respectively — the nonzero FP counts) — they just never land on
these specific boxes. The most likely explanation is that "dining table" was
used as the hand-labelling catch-all for tables in general, including coffee
tables the SAGE_CLASSES schema has no separate name for, and the model's
"dining table" class (trained on COCO-style dining tables) doesn't generalize
to that shape. **This is not evidence either model fails to detect tables in
general** — chase it by checking a few more of the 94 boxes before trusting
the 0.00 number as a detector weakness, not by retraining.

## chair: low recall, unchanged between models

0.20 recall for both v5 and v6 on 90 hand-drawn boxes — v6 has notably worse
precision (0.45 vs 0.67, more than double the false positives: 22 vs 9). Not
new: furniture measurement against hand-drawn labels is new as of this
project's diagnostics (`score_heldout_objects.py`'s own docstring notes past
furniture numbers were scored against pseudo-labels, i.e. against the model's
own teacher). This may be a pre-existing weakness rather than something v6
introduced — v5 has the same low recall.

## Bottom line

- **No person/object trade-off** detected in this combined pass.
- **Couch "regression" in the empty-room test does not hold up** against hand-drawn
  labels — v6 is better on couch by every measured axis here.
- **Refrigerator claim remains unverifiable** — no ground truth exists for it.
- **Bed is a real, ground-truth-corroborated regression** in v6 (recall 0.35→0.10).
- **Dining table's 0% recall is very likely a labeling-taxonomy artifact**
  (coffee tables labelled as dining tables), not a detection failure — flagged
  rather than reported as fact, pending a fuller check of the other 93 boxes.

# A2 drop decision

**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).

Logged: 2026-10-15 (local), before any copy was built. Source tables: `a1_provenance.csv`, `a1_inventory.json` (from `a1_inventory.py`, read-only).

## Rule (as given)
Drop from the A2 **train** split every image that
(a) comes from clip `Sitting_Dim_HM` or `Standing_Walking_Dim_HM`, AND
(b) is NOT hand-drawn (its person box came from MediaPipe),
together with its repeat copies. Keep every hand-drawn frame, including hand-drawn frames from those two clips. Drop whole images, not boxes. Drop nothing else. Val is unchanged.

## How provenance was established
- The train stem has the form `own_<clip>_<frame:06d>[_r1]`. Base stem = the stem without `own_` and without `_r1`.
- A frame counts as **hand-drawn** if `handlabels/{round5,round6,round6_patch}/labels/<base>.txt` exists and either:
  - its bytes are identical to the train label (`hand_byte`), or
  - its boxes are identical after the canonical formatting that `src/detection/handlabels.py` applies before writing (int class, `%.6f` coords, blank lines dropped, order kept) (`hand_canon`).
- `hand_canon` was needed because `generate_bbox_dataset.py` and `build_merged_dataset.py` rewrite hand-label lines. A byte comparison alone misses all of round6 and round6_patch.
- A frame counts as **not hand-drawn** if no hand label with that base stem exists in any round.
- Ambiguity checks:
  - Same stem with different boxes: 0.
  - A no-hand frame whose boxes exactly equal some hand label under another name: 0.
  - Repeat copies with a label different from their base: 0.

## Counts (train)
| clip | provenance | base | _r1 copies |
|---|---|---|---|
| Sitting_Dim_HM | hand-drawn (round6_patch) | 211 | 211 |
| Sitting_Dim_HM | not hand-drawn (MediaPipe) | 650 | 650 |
| Standing_Walking_Dim_HM | hand-drawn (round6_patch) | 173 | 173 |
| Standing_Walking_Dim_HM | not hand-drawn (MediaPipe) | 575 | 575 |

- Ambiguous among the 3218 candidates: 0 (0.0%, limit 5%). The rule proceeds.
- Every one of the 1225 not-hand-drawn base frames carries exactly 1 person box, which is consistent with MediaPipe.
- Neither clip has any image in val.

## Decision
- **DROP 2450 train images:** 1225 base + 1225 `_r1`.
- **KEEP 12593 train images:** 15043 - 2450.
- Val: 2610 images, identical to the original.

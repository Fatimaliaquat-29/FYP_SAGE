# Round 5 → v6: what is left

Handoff note, 15 Aug 2026. Round-5 footage is recorded, rotation-verified and
hand-labelled (`55bad29`). **Nothing has been wired into a dataset yet.** Two
tasks remain, in this order.

---

## 1. Extract the empty clips as background negatives

`yolo_testing/Training/Empty/Bedroom_Emptyy.mov` (345 frames) and
`TV_Lounge_Emptyy.mov` (565 frames) were recorded alongside the fall clips and
are still untouched.

These need **no hand-labelling**. They feed the merge as background negatives
via `build_merged_dataset.py --empty_dir`, the same route
`yolo_testing/Training/Empty` already takes. Empty rooms are what keep the
false-positive rate down — v5 scores 0.00% on held-out empty rooms against v3's
0.39%, and that is worth protecting.

Rotation is already registered in `src/detection/footage_rotation.py`:
`Bedroom_Emptyy.mov` → **90 CCW**, `TV_Lounge_Emptyy.mov` → **none**. Both were
verified by eye. Do not re-derive them from metadata.

---

## 2. Build a merge path for hand-drawn labels

**This is the real work, and without it round 5 was pointless.**

`generate_bbox_dataset.py` produces person labels from MediaPipe and furniture
labels from stock YOLOv8n. It has **no path for hand-drawn labels**. The 118
frames in `handlabels/round5/` therefore cannot currently reach a training set.

What the merge has to do:

- Take frames from `handlabels/round5/{images,labels}` and emit them in the same
  YOLO layout `generate_bbox_dataset.py` writes, so `build_merged_dataset.py`
  can consume them unchanged.
- **Hand labels win over MediaPipe for any frame that has both.** That is the
  entire point: MediaPipe covers only ~46% of the hardest fall frames, and these
  frames were chosen to be that case. Falling back to MediaPipe here would
  reproduce exactly what made v5 fail to move the fall column.
- Keep the furniture boxes already drawn in these frames. They are real labels,
  not pseudo-labels, and dropping them would teach furniture-as-background —
  the failure recorded in `YOLO_Phase_Summary.md` §5.2.
- Do **not** run `--pseudo_objects` over these frames. Their furniture is
  hand-drawn; adding stock-YOLO boxes on top would produce duplicates.

### Regenerating the images

`handlabels/**/*.jpg` is gitignored (identifiable people, same rule as `eval/`).
Only the `.txt` labels are committed. The frames are regenerable from the clips
at **stride 10**, with rotation applied from `footage_rotation.py` — filenames
are `<clip_stem>_<1-based frame index, 6 digits>.jpg`. Any regeneration must
reproduce those exact names or the labels will orphan.

---

## What is already true, so nobody re-derives it

**The held-out set is clean.** Round-5 footage is under `Training/`, the eval
set under `Reserved/` is untouched. Scoring a v6 on it stays non-circular. Do
not move round-5 clips into `Reserved/`, and do not put anything from
`handlabels/` into `eval/heldout_objects/`.

**The train/val split will shift.** `generate_bbox_dataset.py` assigns val by
position in the sorted clip listing, so adding clips to
`Training/With people` changes which clips land in val. **A v6's val metrics
will not be comparable to v3's or v5's.** The held-out eval set is unaffected —
use it for any cross-model claim.

**The gate for v6 already exists:**

```bash
python src/detection/score_heldout_objects.py --classes person \
    --imgsz 640 --conf 0.4 --per_clip \
    --model models/yolov8n_sage_merged_v6.pt \
    --model models/yolov8n_sage_merged_v5.pt
```

Run it at `--iou 0.5` **and** `--iou 0.3`; the threshold changes the verdict for
v5 and will likely do so again. Baselines to beat, from
[`results/yolo_person_detection/reserved_heldout_posture_v5.md`](../results/yolo_person_detection/reserved_heldout_posture_v5.md)
on 388 hand-drawn boxes:

| | v3 | v5 |
|---|---|---|
| fall detection rate @ IoU 0.3 | 0.297 | **0.364** |
| `TV_Lounge_1_Fall` (97 boxes) | 0.15 | 0.18 |
| `Bedroom_Fall` (62 boxes) | 0.39 | **0.68** |
| overall precision @ IoU 0.3 | 0.953 | **0.990** |
| empty-room FP rate | 0.39% | **0.00%** |

**`TV_Lounge_1_Fall` is the number to watch.** Both models find ~15 of 97 boxes
there. It is the clip round 5 was recorded for, and it is where a real fix would
show up first. `Bedroom_Fall` is currently the *only* clip where v5 separates
from v3 — if v6 widens that to more clips, the round worked.

---

## Related

- [`results/yolo_person_detection/reserved_heldout_posture_v5.md`](../results/yolo_person_detection/reserved_heldout_posture_v5.md) — current model comparison, and why IoU 0.5 vs 0.3 changes the verdict
- [`TRAINING_v5_CONTEXT.md`](TRAINING_v5_CONTEXT.md) — the v5 runbook; the Colab procedure still applies
- [`YOLO_Merged_Training_Runbook.md`](YOLO_Merged_Training_Runbook.md) — end-to-end dataset build
- `src/detection/footage_rotation.py` — per-clip rotations, round-5 entries included

# Round 5 → v6: what is left

> **CLOSED, 15 Aug 2026.** Both tasks below are done and
> `datasets/sage_merged_v6/` is built. The runbook for the training run is
> [`TRAINING_v6_CONTEXT.md`](TRAINING_v6_CONTEXT.md); read that instead. This
> file is kept for the reasoning that led here, and for two claims in it that
> turned out to be wrong — see "Corrections" at the end.

Handoff note, 15 Aug 2026. Round-5 footage is recorded, rotation-verified and
hand-labelled (`55bad29`). **Nothing has been wired into a dataset yet.** Two
tasks remain, in this order.

---

## 1. Extract the empty clips as background negatives — DONE

*They needed no new flag: `--empty_dir` already rglobs them. What they needed
was rotation, which that path did not apply. 59 background frames added,
`Bedroom_Emptyy` rotating 90 CCW.*

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

## 2. Build a merge path for hand-drawn labels — DONE

*`src/detection/handlabels.py` plus `--handlabels_dir` / `--handlabels_only` /
`--extra_clip` on the generator. All four requirements below are met; all 118
frames reached the dataset and verified pixel-identical to the frames the boxes
were drawn on.*

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

## Corrections

Two things above were stated as fact and were wrong. Recorded rather than
silently edited, because both were reasonable inferences from the code.

**1. "The train/val split will shift" — it does not.** That assumed
`generate_bbox_dataset.py` discovers clips under `yolo_testing/Training/With
people`. It does not: `TRAINING_PEOPLE` points at `Testing/` (see
`footage_paths.py`), so the default `--testing_dir` never looks in that
directory and adding clips there shifts nothing. Round-5 reaches the dataset via
the new `--extra_clip`, which appends *after* the sorted listing and assigns to
train, so **v6's split is identical to v5's** and its val metrics are
comparable. The held-out set is still the right basis for cross-model claims.

**2. Rotation was not "already registered" in any path that mattered.**
`footage_rotation.py` did have the round-5 entries, but
`generate_bbox_dataset.py` never called it — only `sample_heldout_frames.py`
did. Since the hand labels were drawn on rotated frames (`Bedroom_Falll` is
stored 1080×1920 portrait, the labelled frames are 1920×1080), wiring the labels
in without first teaching the generator to rotate would have put every box 90°
out. Both dataset builders now apply rotation, and the merge verifies each
regenerated frame against the frame its boxes were drawn on.

One thing above was right and worth repeating: the held-out set is clean, and
scoring v6 on it stays non-circular.

---

## Related

- [`TRAINING_v6_CONTEXT.md`](TRAINING_v6_CONTEXT.md) — the runbook this note fed into
- [`results/yolo_person_detection/reserved_heldout_posture_v5.md`](../results/yolo_person_detection/reserved_heldout_posture_v5.md) — current model comparison, and why IoU 0.5 vs 0.3 changes the verdict
- [`TRAINING_v5_CONTEXT.md`](TRAINING_v5_CONTEXT.md) — the v5 runbook; the Colab procedure still applies
- [`YOLO_Merged_Training_Runbook.md`](YOLO_Merged_Training_Runbook.md) — end-to-end dataset build
- `src/detection/footage_rotation.py` — per-clip rotations, round-5 entries included

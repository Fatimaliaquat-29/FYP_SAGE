# Training v6 — context and runbook

Everything up to the Colab run is done. This file is the handoff: what changed,
what to run, and what to measure afterwards. It supersedes
[`NEXT_round5_to_v6.md`](NEXT_round5_to_v6.md), whose two open tasks are now
closed.

**Dataset ready:** `datasets/sage_merged_v6/` — 13,793 images, 52,867 boxes.

---

## Why v6 exists

v5 fixed the *label generator* (MediaPipe IMAGE → VIDEO mode) and it worked, but
only so far: fall detection rate moved 0.297 → 0.364 at IoU 0.3, and
`Bedroom_Fall` was the **only** clip where v5 genuinely separated from v3. The
hardest clip, `TV_Lounge_1_Fall`, sat at 0.15 → 0.18 on 97 boxes.

That clip already had **100% MediaPipe coverage** before the v5 fix. There were
no missing labels left to recover, so no relabelling of existing footage could
move it. Two training runs had now failed the same way.
[`reserved_heldout_posture_v5.md`](../results/yolo_person_detection/reserved_heldout_posture_v5.md)
named the binding factors instead: **dark clothing on dark furniture, dim light,
foreground occlusion** — with a person lying on furniture in *good* light
detected ~100% of the time, so posture alone is not the problem.

v6 is the first run that attacks that with **new footage of the missing
conditions, labelled by hand** rather than with new labels on old footage.

### What changed in the data

| | v5 (`sage_merged_v5`) | v6 (`sage_merged_v6`) |
|---|---|---|
| images | 13,498 | **13,793** |
| person boxes | 19,432 | **19,640** (+208) |
| — of which hand-drawn | 0 | **208** (104 boxes, ×2 by `--own_repeat`) |
| chair | 11,615 | 11,615 |
| couch | 943 | **1,279** |
| bed | 2,598 | **2,722** |
| dining table | 2,871 | **2,983** |
| background frames | 614 | **673** (4.9% of images) |
| fall/lying share of our person boxes | 27.8% | **29.9%** |

Three things changed, and nothing else:

1. **Round-5 footage added** — `Bedroom_Falll` and `TV_Lounge_Fallll`, 118
   hand-labelled frames, 104 person + 286 furniture boxes.
2. **Two new empty clips** — `Bedroom_Emptyy` (345 frames) and
   `TV_Lounge_Emptyy` (565 frames) as background negatives.
3. **Rotation is now applied when building training data** (see below). This
   affects **only** the round-5 clips; no clip in `Testing/` has a verified
   rotation, so v5's 28 clips produce byte-identical frames.

The 28 `Testing/` clips, the COCO subset, `--own_repeat 2` and the stride are
all unchanged from v5, and this was **checked rather than assumed**: excluding
the round-5 frames, v6's own-frames dataset has an identical frame set *and*
identical per-class box counts to v5's (4,380 frames, 9,055 boxes both ways).
Round-5's contribution is exactly 104 person + 168 couch + 62 bed + 56 dining
table, matching `55bad29`.

The held-out four are unchanged: `newTest`, `Sit_2`, `Normal_Fall_2`,
`Foward_fall`.

---

## Three things the handoff note did not know

Recorded here so nobody re-derives them.

### 1. The training-data path never applied rotation

`generate_bbox_dataset.py` read frames straight from `cv2.VideoCapture` and
never consulted `footage_rotation.py`. Only `sample_heldout_frames.py` did.

That matters because the hand labels were drawn on **rotated** frames:
`Bedroom_Falll_000010.jpg` is 1920×1080, while `Bedroom_Falll.mov` is stored
1080×1920 portrait. Attaching those labels to raw frames would have put every
box 90° out — on a normal-looking image, with a healthy loss curve.

Rotation is now applied in `generate_bbox_dataset.py` and in
`build_merged_dataset.py`'s background-negative path. The build confirms it:
`Bedroom_Falll` rotates 90 CCW in the person path, `Bedroom_Emptyy` 90 CCW in
the negatives path, and all 118 hand-labelled frames verify pixel-identical to
the frames the boxes were drawn on.

Unverified clips are still processed as stored — refusing them would gut the
training set — but are now **reported**: 23 clips under `Testing/` and 4 empty
clips (`empty_ground_myRoom1`, `empty_mid_bedroom1`, `empty_mid_bedroom_1`,
`empty_top_bedroom`) look rotated and nobody has checked which way. If any is
actually sideways, MediaPipe emits few or no poses for it and its frames are
quietly under-represented. **Verifying those by eye is the cheapest outstanding
lever in this pipeline** and is not blocked on anything.

### 2. `TRAINING_PEOPLE` points at `Testing/`, not `yolo_testing/Training/With people`

The handoff note assumed adding clips to `Training/With people` would shift the
train/val split. It would not have — the default `--testing_dir` never looks
there. The round-5 clips reach the dataset via the new `--extra_clip`, which
appends them **after** the sorted listing and assigns them to train, so
**v6's train/val split is identical to v5's**. Contrary to the note, val metrics
*are* comparable this time. Use the held-out set for cross-model claims anyway.

### 3. That directory also holds 6 never-trained-on clips

`people_ground_myRoom.MOV`, `people_ground_myRoom2.MOV`, `people_mid_bedroom.MOV`,
`people_mid_guest.MOV`, `people_top_bedroom.MOV`, `people_top_loungeSit.MOV` —
roughly 5,000 frames, in no training set to date.

**Deliberately excluded from v6.** Adding them would change two variables at
once and make any movement in the fall column unattributable. They remain
available: add `--extra_clip` entries for them in a later run.

---

## How the dataset was built (already done — for reproduction only)

```bash
python src/detection/generate_bbox_dataset.py \
    --stride 2 --pseudo_objects --object_conf 0.35 \
    --extra_clip "yolo_testing/Training/With people/Bedroom_Falll.mov" \
    --extra_clip "yolo_testing/Training/With people/TV_Lounge_Fallll.mov" \
    --handlabels_dir handlabels/round5 \
    --handlabels_only \
    --out_dir datasets/sage_person_finetune_v6

python src/detection/build_merged_dataset.py \
    --own_dir datasets/sage_person_finetune_v6 \
    --coco_dir datasets/coco_subset \
    --empty_dir "yolo_testing/Training/Empty" \
    --own_repeat 2 \
    --out_dir datasets/sage_merged_v6
```

### Why `--handlabels_only`

Without it, the round-5 clips would also contribute ~400 MediaPipe-labelled
frames at stride 2 — the guesses outvoting the hand-drawn ground truth about 4:1
on the exact footage MediaPipe is known to fail on. That is the mechanism the
round was recorded to escape. With the flag, those two clips contribute their
118 human-labelled frames and nothing else; every other clip keeps MediaPipe
labels as before.

### The guards this path added

`handlabels.py` aborts rather than warns, because every failure here is silent:

- **classes.txt must equal `SAGE_CLASSES`.** A bare `.txt` carries integers, not
  names, so there is nothing to remap by. Labels drawn against a different
  ordering would train `couch` as `wine glass` with a healthy loss curve.
- **A label no clip claims is a hard error.** Frame names are
  `<clip_stem>_<1-based index, 6 digits>`; a stride or re-encode change orphans
  them, and orphaned hand-drawn boxes cannot be regenerated by re-running
  anything.
- **Regenerated frames are checked against the committed `.jpg`.** All 118
  verified pixel-identical. A wrong rotation shows up as a transposed shape, a
  wrong frame index as a large pixel delta. `handlabels/**/*.jpg` is gitignored,
  so on a fresh clone this check is skipped and says so.
- **An empty label file means "a human looked and found nothing"** and is kept
  distinct from "not labelled". 14 of the 118 frames are exactly this: the
  opening frames before the subject walks in, with furniture labelled
  throughout, so they do not teach furniture-as-background.

---

## The Colab run

`datasets/sage_merged_v6.zip` is built and verified — 2.72 GB, 27,593 entries,
13,793 images and 13,793 labels one-to-one. Upload it to Drive, then:

```python
from google.colab import drive; drive.mount('/content/drive')

# copy to LOCAL disk then unzip -- do NOT train off the Drive mount,
# reading thousands of small files over Drive FUSE roughly doubles epoch time
!cp /content/drive/MyDrive/sage/sage_merged_v6.zip /content/
!unzip -q /content/sage_merged_v6.zip -d /content/sage_merged_v6

# REQUIRED: data.yaml carries the absolute path of the machine that built it
# (a Windows path here), which resolves to nothing on Colab.
!sed -i 's|^path:.*|path: /content/sage_merged_v6|' /content/sage_merged_v6/data.yaml
```

Check `!nvidia-smi` first — free tier does not guarantee a T4.

The rest is unchanged from v5 — see
[`TRAINING_v5_CONTEXT.md`](TRAINING_v5_CONTEXT.md). The two rules that must not
change still hold:

**1. Start from stock `yolov8n.pt`.** Never from v3/v4/v5. A fine-tuned
checkpoint whose head was reduced to one class cannot regrow the others.

**2. `imgsz=640`, not 320.** Every model in this project detects **zero** fallen
people at 320. Training or gating v6 at 320 would hide the result entirely.

```python
model = YOLO('/content/drive/MyDrive/sage/yolov8n.pt')   # STOCK weights
model.train(
    data='/content/sage_merged_v6/data.yaml',
    imgsz=640,
    epochs=30,
    project='/content/drive/MyDrive/sage/runs',
    name='merged_v6_640',
)
```

---

## Scoring afterwards

Bring the weights back to `models/yolov8n_sage_merged_v6.pt`, then run the gate
`NEXT_round5_to_v6.md` specified, at **both** IoU thresholds:

```bash
for iou in 0.5 0.3; do
python src/detection/score_heldout_objects.py --classes person \
    --imgsz 640 --conf 0.4 --per_clip --iou $iou \
    --model models/yolov8n_sage_merged_v6.pt \
    --model models/yolov8n_sage_merged_v5.pt
done

python src/detection/score_empty_false_positives.py \
    --imgsz 640 --conf 0.4 --stride 1 \
    --model models/yolov8n_sage_merged_v6.pt \
    --model models/yolov8n_sage_merged_v5.pt
```

**Compare at the same `--conf` AND `--imgsz`.** Mismatching either has produced
wrong conclusions twice in this project.

Report **both** IoU thresholds whichever way the result falls. IoU 0.3 flattered
v5, and picking the threshold after seeing the numbers is a trap this directory
has already fallen into.

### The numbers to beat

From [`reserved_heldout_posture_v5.md`](../results/yolo_person_detection/reserved_heldout_posture_v5.md),
388 hand-drawn boxes, 11 clips, 3 rooms:

| | v3 | v5 | v6 |
|---|---|---|---|
| fall detection rate @ IoU 0.3 | 0.297 | **0.364** | ? |
| fall detection rate @ IoU 0.5 | 0.290 | 0.283 | ? |
| walk/sit detection rate | 0.933 | **0.962** | ? |
| overall precision @ IoU 0.3 | 0.953 | **0.990** | ? |
| empty-room FP rate | 0.39% | **0.00%** | ? |

Per clip, the two that decide it:

| clip | boxes | v3 @ 0.3 | v5 @ 0.3 | v6 |
|---|---|---|---|---|
| **`TV_Lounge_1_Fall`** | 97 | 0.15 | 0.18 | ? |
| `TV_Lounge_1_Fall2` | 48 | 0.27 | 0.25 | ? |
| `Bedroom_Fall` | 62 | 0.39 | **0.68** | ? |

**`TV_Lounge_1_Fall` is the number to watch.** It is the clip round 5 was
recorded to match, both models find ~1 in 6 boxes there, and it cannot be fixed
by relabelling. If v6 moves it while holding the walk/sit column and the 0.00%
empty-room rate, the round worked.

`Bedroom_Fall` at 0.68 is the *other* thing to watch, in the opposite direction:
it is v5's one genuine win and v6 must not lose it.

---

## Expectations — be honest about these

**208 hand-drawn person boxes against v5's 19,432 is +1.1%.** The round-5 frames
are 236 of 13,793 images — 1.7% of the dataset. The fall/lying share of our own
person boxes moves 27.8% → 29.9%. This is a much smaller intervention than it
feels like, and the honest prior is a small effect or none.

**A null result here is informative, and is not a failed run.** v5's +385 boxes
(+2%) moved the fall column 0.297 → 0.364. If 104 boxes of the *right* footage
move `TV_Lounge_1_Fall` at all, that is evidence the binding constraint is
condition coverage rather than label volume — which is the question round 5 was
recorded to answer. If nothing moves, the next lever is **more of this footage,
not different labels**: 118 frames is one afternoon's hand-labelling, and the
finding would be that it takes more.

**If v6 regresses**, suspect the 118 frames are too few to help and numerous
enough to add noise, and check `--own_repeat` before concluding the footage is
wrong.

**Round 5 does not appear in the eval set.** The footage is under `Training/`,
the held-out set under `Reserved/` is untouched, and nothing from `handlabels/`
went near `eval/heldout_objects/`. Scoring v6 on it stays non-circular.

---

## Related

- [`NEXT_round5_to_v6.md`](NEXT_round5_to_v6.md) — the handoff this run closes
- [`results/yolo_person_detection/reserved_heldout_posture_v5.md`](../results/yolo_person_detection/reserved_heldout_posture_v5.md) — v5 vs v3, and why IoU 0.5 vs 0.3 changes the verdict
- [`results/yolo_person_detection/labeler_video_mode_fix.md`](../results/yolo_person_detection/labeler_video_mode_fix.md) — the IMAGE/VIDEO root cause behind v5
- [`TRAINING_v5_CONTEXT.md`](TRAINING_v5_CONTEXT.md) — the v5 runbook; the Colab procedure still applies
- `src/detection/handlabels.py` — the hand-label merge path and its guards
- `src/detection/footage_rotation.py` — per-clip rotations, round-5 entries included

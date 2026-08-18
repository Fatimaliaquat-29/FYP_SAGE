# Training v5 — context and runbook

Everything up to the Colab run is done. This file is the handoff: what changed,
what to run, and what to measure afterwards.

**Dataset ready:** `datasets/sage_merged_v5/` — 13,498 images, 52,087 boxes.

---

## Why v5 exists

`generate_bbox_dataset.py` — which produces every person label in the training
set — was still using MediaPipe's `RunningMode.IMAGE`. The runtime and
evaluation paths were switched to `VIDEO` in `b566685`; the label generator was
missed.

IMAGE mode re-runs MediaPipe's person detector from scratch on every frame with
no memory. VIDEO mode seeds the ROI from the previous frame's pose. In a fall
clip the subject is upright and easy to detect for the first second or two, and
VIDEO mode carries that tracking *through* the fall — where IMAGE mode discards
it and emits nothing once the person is dark, on furniture, or occluded.

Net effect: the labeller was dropping fallen-person frames, so the training set
under-represented them, so the fine-tuned model could not detect fallen people.

Full analysis: [`results/yolo_person_detection/labeler_video_mode_fix.md`](../results/yolo_person_detection/labeler_video_mode_fix.md)

### What changed in the data

| | v3 (`sage_merged`) | v5 (`sage_merged_v5`) |
|---|---|---|
| images | 13,147 | 13,498 |
| person boxes | 19,047 | **19,432** (+385) |
| chair | 11,585 | 11,615 |
| bed | 2,547 | 2,598 |
| fall/lying share of person boxes | 19.3% | **23.2%** |

Only person-label density changed. Same clips, same 24/4 split, same COCO
subset, same `--own_repeat 2`, same `--empty_dir`. **Any difference in results
is attributable to labels + resolution, nothing else.**

Held-out four confirmed unchanged: `newTest`, `Sit_2`, `Normal_Fall_2`,
`Foward_fall`.

---

## How the dataset was built (already done — for reproduction only)

```bash
python src/detection/generate_bbox_dataset.py \
    --stride 2 --pseudo_objects --object_conf 0.35 \
    --out_dir datasets/sage_person_finetune_video

python src/detection/build_merged_dataset.py \
    --own_dir datasets/sage_person_finetune_video \
    --coco_dir datasets/coco_subset \
    --empty_dir "yolo_testing/Training/Empty" \
    --own_repeat 2 \
    --out_dir datasets/sage_merged_v5
```

Note the rebuild is ~2x slower than before: VIDEO mode must run pose inference
on **every** frame to maintain the tracking chain, and `--stride` now controls
only which frames get written.

---

## The Colab run

Do this on Colab, not the laptop. Measured locally: ~28 min/epoch, ~14 hours for
30 epochs. Free-tier T4 is 20–40x faster.

```bash
# locally: zip and upload to Drive
python -c "import shutil; shutil.make_archive('datasets/sage_merged_v5','zip','datasets/sage_merged_v5')"
```

```python
# Colab cell
from google.colab import drive; drive.mount('/content/drive')

# copy to LOCAL disk then unzip -- do NOT train off the Drive mount,
# reading thousands of small files over Drive FUSE roughly doubles epoch time
!cp /content/drive/MyDrive/sage/sage_merged_v5.zip /content/
!unzip -q /content/sage_merged_v5.zip -d /content/sage_merged_v5

# point data.yaml at the local unzip location
!sed -i 's|^path:.*|path: /content/sage_merged_v5|' /content/sage_merged_v5/data.yaml

from ultralytics import YOLO
model = YOLO('/content/drive/MyDrive/sage/yolov8n.pt')   # STOCK weights
model.train(
    data='/content/sage_merged_v5/data.yaml',
    imgsz=640,           # <-- see below. NOT 320.
    epochs=30,
    project='/content/drive/MyDrive/sage/runs',
    name='merged_v5_640',
)
```

Check `!nvidia-smi` first — free tier does not guarantee a T4.

### Two things that must not change

**1. Start from stock `yolov8n.pt`.** Never from v3/v4. A fine-tuned checkpoint
whose head was reduced to one class cannot regrow the others.

**2. `imgsz=640`, not 320.** This matters more than the relabelling:

| model | imgsz | fallen-person detection |
|---|---|---|
| v3 | 320 | **0/52** |
| v3 | 640 | 30/52 |
| merged_640 | 320 | **0/52** |
| merged_640 | 640 | 32/52 |
| v4 | either | 0/52 |

Every model detects **zero** fallen people at 320. Training and gating v5 at 320
would likely hide the label improvement entirely. 640 also makes v5 directly
comparable to `merged_640`, the best model measured so far.

Cost: ~2x inference latency (v3@640 and merged_640@640 both measured 150 ms
median on a loaded laptop CPU — identical, since same architecture and input
size). Re-measure on the deployment device; the ratio should transfer, the
absolute numbers will not.

---

## Scoring afterwards

Bring the weights back to `models/yolov8n_sage_merged_v5.pt`, then:

```bash
# recall by clip, against 385 hand-drawn labels on held-out footage
python src/detection/score_heldout_objects.py --classes person \
    --imgsz 640 --conf 0.4 \
    --model models/yolov8n_sage_merged_v5.pt \
    --model models/yolov8n_sage_merged_v3.pt

# false positives, every frame of the held-out empty rooms
python src/detection/score_empty_false_positives.py \
    --imgsz 640 --conf 0.4 --stride 1 \
    --model models/yolov8n_sage_merged_v5.pt \
    --model models/yolov8n_sage_merged_v3.pt
```

**Compare both models at the same `--conf` AND `--imgsz`.** Mismatching either
has produced wrong conclusions twice in this project.

### The number that matters

v3 @ 640, detection rate per clip on hand-labelled held-out footage:

| activity | rate |
|---|---|
| walk / sit | **0.83 – 1.00** |
| **fall** | **0.25 – 0.45** |

Five fall clips, three rooms, no overlap between the groups. **If v5 lifts the
fall column and holds the walk/sit column, the fix worked.**

Baseline for reference (`reserved_heldout_posture.md`):

| model | imgsz | overall detection rate |
|---|---|---|
| v3 | 640 | 0.736 |
| merged_640 | 640 | 0.770 |
| stock | 640 | 0.588 |
| v4 | 640 | 0.520 |

---

## Expectations — be honest about these

**+385 person boxes on 19,047 is +2%.** Concentrated in fall frames (+26% of
that class), but small overall. This run tests whether the label fix helps *at
all*; a large jump would be surprising.

**Resolution is probably the bigger variable in this run.** If v5@640 beats
v3@320, that mostly measures resolution, not labels. The honest comparison is
**v5@640 vs v3@640**.

**This cannot fix everything.** `TV_Lounge_1_Fall` already had 100% MediaPipe
coverage yet v3 detects only 4/16 there — that failure is not about missing
labels. The held-out analysis showed the misses share a profile: person lying
*on* furniture, dark clothing against dark furniture, foreground occlusion. No
relabelling creates footage that was never shot.

**If v5 shows no improvement**, that is a real result, not a failed run. It
would mean label density was not the binding constraint, and the next lever is
recording the missing conditions — with hand-labelling budgeted in, because
MediaPipe covers only ~46% of the hardest fall frames even in VIDEO mode.

---

## Related

- [`results/yolo_person_detection/labeler_video_mode_fix.md`](../results/yolo_person_detection/labeler_video_mode_fix.md) — root cause, elimination testing, box verification
- [`results/yolo_person_detection/reserved_heldout_posture.md`](../results/yolo_person_detection/reserved_heldout_posture.md) — detection rate by activity, and the four measurement faults corrected along the way
- [`docs/YOLO_Merged_Training_Runbook.md`](YOLO_Merged_Training_Runbook.md) — the original end-to-end procedure
- `src/detection/footage_rotation.py` — per-clip rotation table; extraction refuses unverified clips

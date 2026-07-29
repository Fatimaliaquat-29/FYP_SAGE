# Runbook — Merged (multi-class) YOLO training for SAGE

Purpose: retrain YOLO so it detects **both** fallen/lying people **and** objects (chairs, beds, bottles), fixing the regression where the person-only fine-tune structurally replaced YOLOv8's 80-class head with a single class.

Do **not** fine-tune from `models/yolov8n_sage_person.pt`. Its head has one output class and cannot regrow the others. Always start from stock `models/yolov8n.pt`.

---

## Step 0 — Record empty-room footage (5 minutes, do this first)

### Where to put it — this matters more than it looks
```
Testing_EmptyRooms/          <-- repo root, SIBLING of Testing/ (NOT inside it)
    livingroom.mp4
    bedroom.mp4
    hallway.mp4
```

**Do not put these inside `Testing/`.** Both `generate_bbox_dataset.py` and `benchmark_footage.py` discover clips by rglobbing the whole `Testing/` tree and assign train/val by list index. Adding three clips there shifts every index and silently changes which clips are held out — verified: it drops `Sit_2` and `newTest` from the held-out set and swaps in three others, which would invalidate every before/after comparison in the report. Nothing errors; the numbers just quietly become meaningless.

`Testing_EmptyRooms/` is outside that rglob, so the held-out set is unaffected. Video files are already gitignored by extension, and the folder is now gitignored explicitly.

Subfolders are fine (`Testing_EmptyRooms/bedroom/clip1.mp4`) — frames are keyed on the path relative to the folder, so two rooms can both contain a `room.mp4` without colliding.

### How much to record
- **Rooms:** one per distinct environment in `Testing/` — roughly **3** covers it. More *angles per room* is worth more than more rooms, since the goal is teaching "this background contains no person," and it's the deployment backgrounds that matter.
- **Length:** 30–60s each is plenty. Include the spots where people usually are — an empty chair, an empty bed, a doorway — since those are where false positives are most likely.
- **Person strictly out of frame**, including hands, feet, and shadows-with-a-body-attached. A single frame with a person in it is a mislabeled example, because these are written with empty label files by definition.

At the default `--empty_stride 15`, 3 × 45s of 30fps video yields ~270 background frames against 1,832 person frames (~13%). That's about right — the merge warns if backgrounds exceed ~15%, because too many negatives bias the model toward predicting nothing and cost recall on real falls.

### Why this matters
Our person-only training set had **zero** background frames, so precision was never systematically measurable. These frames are what make a false-positive rate meaningful. (Encouraging preview: on the 40 genuinely empty frames at the end of `Normal_Fall_2.mov`, the current model produced **0** false detections.)

## Step 1 — Build the person dataset (already done, ~25 min if rerun)
```bash
python src/detection/generate_bbox_dataset.py --stride 2
```
Produces `datasets/sage_person_finetune/` — 2,331 train / 1,837 val auto-labeled frames. Skip if it already exists.

## Step 2 — Download the COCO subset (~800 MB, ~15–30 min)
```bash
pip install fiftyone
python src/detection/fetch_coco_subset.py
```
Pulls only images containing SAGE-relevant classes (~5k images), not the full 19 GB COCO. Person images are capped at 500 on purpose so COCO's ~64k upright people don't drown out our lying-pose frames.

## Step 3 — Merge everything
```bash
python src/detection/build_merged_dataset.py \
    --coco_dir datasets/coco_subset \
    --empty_dir Testing_EmptyRooms
```

**Read the printed class mapping before continuing.** It looks like:
```
[coco] class mapping resolved by name: 13/80 kept
      0 'person' -> 0 'person'
     56 'chair'  -> 5 'chair'
```
This is the one step that fails *silently* if wrong — a mismatched index trains `chair` boxes as `wine glass`, and the loss curves still look perfectly healthy. The script maps strictly by class **name** and aborts rather than guessing, but confirm the mapping looks sane anyway. Add `--strict` to hard-fail on any unrecognized class.

## Step 4 — Train (do this on Colab, not the laptop)
Local CPU: ~4+ hours per 12-epoch run. Free-tier Colab T4: ~10 minutes. Do not iterate on CPU.

```python
# Colab cell
!pip install ultralytics
from google.colab import drive; drive.mount('/content/drive')
# upload/copy datasets/sage_merged and models/yolov8n.pt to Drive first

from ultralytics import YOLO
model = YOLO('/content/drive/MyDrive/sage/yolov8n.pt')   # STOCK weights
model.train(
    data='/content/drive/MyDrive/sage/sage_merged/data.yaml',
    epochs=30, imgsz=320, batch=32, patience=10,
)
```
Note `data.yaml` contains an absolute `path:` — update it to the Colab path after uploading, or the run will fail to find images.

Bring `best.pt` back as `models/yolov8n_sage_merged.pt`.

Locally, the equivalent is:
```bash
python src/detection/finetune_person.py \
    --data datasets/sage_merged/data.yaml \
    --weights models/yolov8n.pt --epochs 30
```

## Step 5 — Re-run the benchmark and check for regressions
```bash
python src/detection/benchmark_footage.py \
    --model models/yolov8n_sage_merged.pt --imgsz 320 \
    --out results/yolo_person_detection/merged_320_results.md
```

Three things must all hold before calling this a success:

| Check | Target | Current person-only model |
|---|---|---|
| Lying/fall recall **must not regress** | ≥ 95% | 95.2% |
| Held-out fall/lying recall (person-present frames) | ≥ ~95% | ~95.9% |
| Objects detectable again | chair/bed/bottle found | **broken — 0 classes** |

Plus the new one that empty-room frames finally make measurable: **false-positive rate on background frames should be ~0%.**

The 4 held-out clips (`newTest.mov`, `Sit_2.mov`, `Normal_Fall_2.mov`, `Foward_fall.mp4`) must stay held out — `build_merged_dataset.py` preserves the existing train/val split, so this happens automatically as long as Step 1 isn't rerun with different settings.

Caveat carried forward: `Normal_Fall_2.mov` has **no person in frame for its last 40 frames** (the subject slides out of view). Raw detection-rate on that clip understates recall; split at frame 92 when interpreting it.

## Step 6 — Write up the result
Same standard as `docs/YOLO_Phase_Summary.md`: separate held-out from seen-in-training, state the circularity caveat (labels come from MediaPipe, so we are partly measuring agreement with MediaPipe), and report the sample size honestly.

---

## Out of scope here: the latency wall
The 15 FPS Jetson target allows 66.7 ms/frame. MediaPipe `pose_landmarker_full` alone costs ~110 ms — it exceeds the whole budget before YOLO (41 ms) runs at all, capping the pipeline at ~9 FPS even if YOLO were free. Frame-skipping YOLO cannot fix this.

The real lever is the **pose** stage (`pose_landmarker_lite`, lower pose input resolution, or duty-cycling pose estimation). That belongs to whoever owns the pose pipeline, not this branch.

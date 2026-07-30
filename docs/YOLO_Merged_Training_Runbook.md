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
Local CPU: 7,751 train images at the ~400s/epoch this machine measured on 1,832 images extrapolates to **~28 min/epoch, ~14 hours for 30 epochs** — not viable. Free-tier Colab T4 is roughly 20–40x faster on this workload.

**Upload the zip, not the folder.** `datasets/sage_merged.zip` (built by `shutil.make_archive`) is a single ~1.5 GB file — upload that to Drive rather than the 10,317 loose files in `datasets/sage_merged/`. Also upload `models/yolov8n.pt` (the stock weights, ~6 MB).

**Unzip onto Colab's local disk, don't train off the Drive mount.** Reading thousands of small files over the Drive FUSE mount is a known Colab bottleneck and can roughly double epoch time. Unzip to `/content/` (local, fast) instead of training directly against `/content/drive/...`.

```python
# Colab cell
!pip install ultralytics
from google.colab import drive; drive.mount('/content/drive')

# Copy the zip from Drive to local disk, then unzip locally -- do not train
# directly against the Drive-mounted path.
!cp /content/drive/MyDrive/sage/sage_merged.zip /content/
!unzip -q /content/sage_merged.zip -d /content/sage_merged

# data.yaml's `path:` is still the Windows machine's absolute path -- point it
# at the local unzip location instead of editing the yaml by hand.
import yaml
cfg = yaml.safe_load(open('/content/sage_merged/data.yaml'))
cfg['path'] = '/content/sage_merged'
yaml.safe_dump(cfg, open('/content/sage_merged/data.yaml', 'w'))

from ultralytics import YOLO
model = YOLO('/content/drive/MyDrive/sage/yolov8n.pt')   # STOCK weights, not the person-only checkpoint
model.train(
    data='/content/sage_merged/data.yaml',
    epochs=30, imgsz=320, batch=32, patience=10,
    project='/content/drive/MyDrive/sage/runs',  # save checkpoints straight to Drive
)
```

Check `!nvidia-smi` before starting — free-tier Colab doesn't guarantee a T4; a slower GPU (or none) changes the time estimate a lot.

`patience=10` means it may stop well before epoch 30 — the earlier person-only run peaked at epoch 11 of 12. That's expected, not a failure.

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
| **False positives on empty rooms** | **≤ ~2%** | **11.9%** ← the main thing being fixed |

The false-positive check is the one that matters most for a caregiver alerting system, and it is now measurable. Re-run it with:
```bash
python - <<'EOF'
import sys; sys.path.insert(0,'.')
import cv2
from pathlib import Path
from src.detection.yolo_objects import YOLOObjectDetector
det = YOLOObjectDetector(model_path='models/yolov8n_sage_merged.pt', imgsz=320, confidence_threshold=0.4)
tot=fp=0
for p in sorted(Path('Testing_EmptyRooms').rglob('*')):
    if p.suffix.lower() not in {'.mp4','.mov','.avi','.mkv'}: continue
    cap=cv2.VideoCapture(str(p)); idx=0
    while True:
        ret,f=cap.read()
        if not ret: break
        idx+=1
        if idx % 10: continue
        tot+=1
        if any(d['class']=='person' for d in det.detect(f)): fp+=1
    cap.release()
print(f"false positives: {fp}/{tot} = {100*fp/tot:.1f}%  (baseline to beat: 11.9%)")
EOF
```
Caveat: these empty-room frames are now *in* the training set, so this measures fit rather than generalization. A genuinely clean re-test needs one more empty-room clip from a room held back entirely — worth recording if the number looks too good.

The 4 held-out clips (`newTest.mov`, `Sit_2.mov`, `Normal_Fall_2.mov`, `Foward_fall.mp4`) must stay held out — `build_merged_dataset.py` preserves the existing train/val split, so this happens automatically as long as Step 1 isn't rerun with different settings.

Caveat carried forward: `Normal_Fall_2.mov` has **no person in frame for its last 40 frames** (the subject slides out of view). Raw detection-rate on that clip understates recall; split at frame 92 when interpreting it.

## Step 6 — Write up the result
Same standard as `docs/YOLO_Phase_Summary.md`: separate held-out from seen-in-training, state the circularity caveat (labels come from MediaPipe, so we are partly measuring agreement with MediaPipe), and report the sample size honestly.

---

## Out of scope here: the latency wall
The 15 FPS Jetson target allows 66.7 ms/frame. MediaPipe `pose_landmarker_full` alone costs ~110 ms — it exceeds the whole budget before YOLO (41 ms) runs at all, capping the pipeline at ~9 FPS even if YOLO were free. Frame-skipping YOLO cannot fix this.

The real lever is the **pose** stage (`pose_landmarker_lite`, lower pose input resolution, or duty-cycling pose estimation). That belongs to whoever owns the pose pipeline, not this branch.

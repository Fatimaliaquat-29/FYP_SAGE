# S.A.G.E. YOLO Object Detection Layer — Status and Findings
**Date:** July 2026
**Branch:** `YOLO_fatima`

## 1. The Goal
Per the Continuation Plan's Phase 5 prerequisite and the Scope Document's tech choice, add a YOLOv8-based object detection layer that runs alongside (not replacing) MediaPipe. This phase is scoped to: get YOLOv8 running per-frame, produce reliable person-detection confidence, take a first-pass look at COCO-adjacent classes as medicine-container/furniture placeholders, and measure real latency — not to wire anything into the live pipeline (that's a later, one-person integration step per the plan).

## 2. What Was Built
New, self-contained module, zero edits to any existing pipeline file:
```
src/detection/
  __init__.py
  yolo_objects.py            # YOLOObjectDetector: one method, detect(frame) -> list[dict]
  detect_test.py             # standalone single-clip/webcam viewer with live latency overlay
  benchmark_footage.py       # batch benchmark over an entire Testing/ tree -> markdown report
  generate_bbox_dataset.py   # auto-labels a YOLO training set from MediaPipe keypoints
  finetune_person.py         # fine-tunes YOLOv8n on that auto-labeled set
  sage_classes.py            # canonical SAGE class list (person at index 0)
  fetch_coco_subset.py       # downloads a class-filtered COCO subset via FiftyOne
  build_merged_dataset.py    # merges person frames + COCO subset + empty-room negatives
```
The last three exist to undo the person-only regression described in caveat 5 — see [`YOLO_Merged_Training_Runbook.md`](YOLO_Merged_Training_Runbook.md) for the end-to-end procedure.
`YOLOObjectDetector` wraps `ultralytics.YOLO`. The interface is deliberately minimal — `detect(frame) -> [{"class", "confidence", "bbox"}, ...]` — so swapping models, or wiring this into `realtime_fall_detection.py`, is mechanical. `ultralytics` was added to `requirements.txt`.

## 3. Baseline Finding: stock YOLO loses the person exactly when it matters
Ran `benchmark_footage.py` over all 28 clips across all three `Testing/` folders (9,188 frames), confidence 0.4, on this dev machine (Intel i5-10310U @ 1.7GHz, **CPU only, no CUDA**).

Stock YOLOv8n scored **82.3% overall** person detection — but that aggregate hides the failure mode that matters here:

| Activity state | Frames | Person-detection rate |
|---|---|---|
| Upright (standing/sitting clips) | 6,834 | **93.5%** |
| Falling / lying clips | 2,354 | **49.7%** |

COCO's training images are overwhelmingly upright people, so the stock model's confidence collapses once someone is on the floor. `Lying_straight.mov` (147 frames of a person lying still) scored **0.0%** — it never once detected the person. **The moment YOLO is most useful for a fall-detection system is the moment it stops working.**

## 4. The Fix: fine-tuning on auto-labeled fallen-person frames
Rather than accept that limitation, we fine-tuned YOLOv8n on our own footage. The key insight is that **no manual labeling was needed**: MediaPipe already extracts 33 body keypoints per frame for the existing posture pipeline, and a padded box around those keypoints *is* a bounding-box label. `generate_bbox_dataset.py` turns the `Testing/` tree into a YOLO dataset for free.

- **Dataset:** 1,832 train / 1,837 val labeled frames (every 2nd frame, 28 clips). See section 4.1 — the extraction script initially *reported* 2,331 train frames, but 499 were lost to a filename collision.
- **Split by whole clip, not by frame** — adjacent frames are near-duplicates, so a frame-level split would have leaked and inflated the results. This mirrors the `StratifiedGroupKFold` lesson from the LSTM phase, where a random split faked 93% accuracy.
- **Training:** 12 epochs, 320px, CPU, ~80 min. Best epoch 11: mAP50 **98.7%**, val recall 93.9%.
- Saved to `models/yolov8n_sage_person.pt` (the stock `models/yolov8n.pt` is untouched).

### Results — all three configs over the same 9,188 frames

| Config | Overall | Upright | Fall/lying | Latency |
|---|---|---|---|---|
| Stock YOLOv8n @640 | 82.3% | 93.5% | 49.7% | 98.8 ms (10.1 FPS) |
| Stock YOLOv8n @320 | 72.8% | 84.7% | 38.4% | 46.2 ms (21.6 FPS) |
| **Fine-tuned @320** | **96.9%** | **97.5%** | **95.2%** | **41.2 ms (24.3 FPS)** |

The stock-@320 row is there deliberately: without it we couldn't tell whether the gain came from fine-tuning or just from the smaller image size. It shows shrinking the input *hurts* the stock model (49.7% → 38.4%), so the improvement is genuinely from fine-tuning — which simultaneously **more than doubled fall/lying detection and cut latency by more than half.**

`Lying_straight.mov`, the clip the stock model scored 0.0% on, now scores **100%**.

### The honest number: held-out clips only
24 of the 28 clips contributed frames to training, so their scores are **not** a generalization test. Only 4 clips were fully held out:

| Subset | Frames | Stock @640 | Fine-tuned @320 |
|---|---|---|---|
| Held-out clips (all) | 3,905 | 90.3% | **94.3%** |
| Held-out fall/lying only | 285 | 58.2% | **82.5%** |

| Held-out clip | Stock @640 | Fine-tuned @320 |
|---|---|---|
| `Foward_fall.mp4` | 57.1% | **97.4%** |
| `newTest.mov` | 92.6% | 95.0% |
| `Sit_2.mov` | 99.3% | 100% |
| `Normal_Fall_2.mov` | 59.5% | 64.9% (see below — metric artifact) |

### 4.1 Two data-integrity issues found while building the merged dataset
Both were caught by cross-checking image counts, not by anything failing loudly.

**(a) `Testing/` contains duplicated footage.** `Hussain Testing 7-23-26/normal.mp4` and `Sanawar Testing 7-22-26/normal.mov` are **byte-identical** (same MD5), as are the two `old` clips — the same recordings filed under two sessions with different container extensions. The benchmark therefore counted 999 frames twice, and "28 clips / 9,188 frames" is really **26 unique clips / 8,189 unique frames**.

Deduplicated aggregates (the conclusions do not change; both duplicated clips are easy upright footage, so they mildly inflated every config equally):

| Config | As reported (9,188 fr) | Deduplicated (8,189 fr) |
|---|---|---|
| Stock @640 | 82.3% | 81.2% |
| Stock @320 | 72.9% | 71.8% |
| Fine-tuned @320 | 96.9% | **96.5%** |

**(b) A filename collision silently discarded 499 training frames.** `generate_bbox_dataset.py` originally keyed output frames on the clip's stem alone, so the two same-named clip pairs above overwrote each other — the script *reported* 2,331 train frames while only 1,832 reached disk. Here the loss was harmless (the overwritten frames were duplicates anyway), but with genuinely different clips sharing a name it would have destroyed real training data with no error. **Fixed:** frames are now keyed on the clip's full path relative to `Testing/`, verified to produce 28 unique keys for 28 clips.

Neither issue invalidates the results above, but both are the kind of silent failure worth checking for in the other branches' data pipelines too.

### `Normal_Fall_2.mov` is not a model failure — the metric is wrong on that clip
The apparently weak 64.9% initially looked like the fine-tuning failing to generalize. Inspecting the actual missed frames showed something else: **the subject slides out of the bottom of the camera's field of view around frame 84–92 and is completely absent from the frame for the last 40 of the clip's 131 frames.** The camera is pointed at a wall and door; there is no person to detect. Both models are *correct* to return nothing there.

Splitting that clip at the boundary gives a much more meaningful picture — and the project's first real precision measurement:

| `Normal_Fall_2.mov` | Stock @640 | Fine-tuned @320 |
|---|---|---|
| Recall, frames 1–91 (person visible) | 85.7% | **93.4%** |
| False-positive rate, frames 92–131 (**no person present**) | **0.0%** | **0.0%** |

So the fine-tuned model improved on this clip too (85.7% → 93.4%), and **neither model hallucinated a person in 40 consecutive genuinely empty frames.**

Correcting the held-out fall/lying figures to exclude the 40 person-absent frames (245 person-present frames rather than 285):

| Held-out fall/lying, person-present frames only | Stock @640 | Fine-tuned @320 |
|---|---|---|
| Recall over 245 frames | ~67.8% | **~95.9%** |

The gain on genuinely unseen footage is therefore larger than the raw table suggests, and does *not* rest on a single clip. It remains a small sample (2 fall/lying clips, 245 frames) and should be treated as promising rather than settled.

**Methodological note for the whole team:** person-detection rate silently assumes a person is present in every frame. That assumption is false in at least one of our clips and is worth re-checking before this metric is reused elsewhere.

## 5. Caveats — read before trusting these numbers
1. **Small held-out set.** 4 clips, 285 fall/lying frames. The 82.5% figure has wide error bars.
2. **Labels come from MediaPipe, so the evaluation is partly circular.** We taught YOLO to agree with MediaPipe and then measured it on similar footage. Frames where MediaPipe found no pose produced no label and were simply *absent* from training rather than taught as negatives — so the fine-tuned model inherits MediaPipe's blind spots by construction.
3. **The metric is detection rate, which measures recall only.** Precision is now partially evidenced rather than untested: the fine-tuned model returned zero detections on synthetic empty frames, on a person-free crop of a furnished room, and — the strongest evidence — across **40 consecutive real frames of an empty room in `Normal_Fall_2.mov`** (section 4). It has clearly not degenerated into "always predict a person." Still, the training set contained **no background/empty frames at all**, so precision has never been *systematically* measured. Adding empty-room negatives remains the right next step.
4. **Same rooms, same few people.** Nothing here shows it generalizes to new environments or new subjects.
5. **The fine-tuned model is person-only.** Passing a 1-class dataset made Ultralytics log `Overriding model.yaml nc=80 with nc=1` — this **structurally replaced the detection head**, so there is no longer a `chair` output neuron at all. Confirmed: on a room crop where the stock model found `chair` 0.84 and `bed` 0.77, the fine-tuned model found nothing.

   Worth being precise, because it dictates the fix: this is *not* catastrophic forgetting (gradual drift that could be countered with a lower learning rate, a frozen backbone, or EWC). Those mitigations would do nothing here. The only fix is to keep a multi-class label space — which is what `build_merged_dataset.py` and the [runbook](YOLO_Merged_Training_Runbook.md) now provide. Retraining must start from **stock** `yolov8n.pt`; the person-only checkpoint cannot regrow classes its head no longer has.

## 6. Medicine-container / furniture status
COCO includes furniture classes (`chair`, `couch`, `bed`, `dining table`, …) and container classes (`bottle`, `cup`, `bowl`). Spot checks confirm the **stock** model detects furniture plausibly (`Sit_1.mov`: person + bed; `Chair_fall.mp4`: person, chair, dining table). No `bottle` detections appeared in any clip, as expected — fall-testing footage doesn't stage medicine bottles, and COCO's "bottle" class is water/wine bottles, not pill bottles.

**Genuine medicine-container detection still needs a custom-labeled dataset** — and unlike the person labels above, that one *cannot* be auto-generated from MediaPipe, since MediaPipe only tracks human bodies. That is real manual labeling effort, comparable to the LeFD dataset work, and remains the honest blocker for the medication-adherence feature.

## 7. Recommendation for the integration phase
1. **Use the fine-tuned model for person detection.** It is better *and* faster than stock on every measured axis, which resolves the "YOLO is blind to fallen people" problem that would otherwise have forced awkward special-casing in the event schema.
2. **YOLO is no longer the latency problem — MediaPipe is.** Fine-tuned YOLO runs at 41 ms/frame; MediaPipe (`pose_landmarker_full.task`) runs at ~110 ms/frame. Sequentially that is ~151 ms (~6.6 FPS).

   The 15+ FPS Jetson target allows a budget of **66.7 ms/frame total**. MediaPipe alone is 110 ms — it **blows the entire budget by itself, before YOLO runs at all.** This means *no amount of YOLO optimization reaches the target*: even if YOLO were free, the ceiling is ~9.1 FPS. Frame-skipping YOLO every 4th frame only moves ~151 ms → ~120 ms (~8.3 FPS), still well short.

   The lever that actually matters is therefore the **pose model**, not the detector — e.g. `pose_landmarker_lite` instead of `_full`, a reduced input resolution, or running pose estimation itself on a duty cycle. That is a decision for whoever owns the pose pipeline, and it should be made before anyone invests further in YOLO-side optimization. (All figures are laptop CPU; Jetson will differ, but the *ratio* between the two stages is the point.)
3. **Plan for two models, not one.** Person detection now wants the fine-tuned person-only model; furniture/medication detection needs stock COCO or a future custom model. Running both re-opens the latency question — worth deciding deliberately rather than by accident.
4. **Before relying on this in production, add empty-room/background frames to the training set** and re-validate precision, per caveat 3.

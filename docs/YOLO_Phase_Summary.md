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
3. **Precision is a real, measured weakness — see section 5.1.** Earlier drafts of this report called precision "partially evidenced" on the strength of zero false positives across 40 empty frames in `Normal_Fall_2.mov`. That was too generous: that room also appears in training footage. Measured on genuinely unseen rooms, the fine-tuned model false-positives on **11.9%** of empty frames.
4. **Same rooms, same few people.** Nothing here shows it generalizes to new environments or new subjects.
5. **The fine-tuned model is person-only.** Passing a 1-class dataset made Ultralytics log `Overriding model.yaml nc=80 with nc=1` — this **structurally replaced the detection head**, so there is no longer a `chair` output neuron at all. Confirmed: on a room crop where the stock model found `chair` 0.84 and `bed` 0.77, the fine-tuned model found nothing.

   Worth being precise, because it dictates the fix: this is *not* catastrophic forgetting (gradual drift that could be countered with a lower learning rate, a frozen backbone, or EWC). Those mitigations would do nothing here. The only fix is to keep a multi-class label space — which is what `build_merged_dataset.py` and the [runbook](YOLO_Merged_Training_Runbook.md) now provide. Retraining must start from **stock** `yolov8n.pt`; the person-only checkpoint cannot regrow classes its head no longer has.

## 5.1 The fine-tuning traded precision for recall — measured on unseen rooms
Three empty-room clips were recorded specifically to test false positives (4 videos, 1,950 frames, three rooms that appear nowhere in training). Every frame was verified by eye to contain no person. Sampling every 10th frame, at the same confidence 0.4 used throughout:

| Model | False positives on 194 empty-room frames |
|---|---|
| Stock YOLOv8n @640 | **1.0%** |
| Fine-tuned person-only @320 | **11.9%** |

The fine-tuned model boxes a **water dispenser at 0.59 confidence** and a **sofa arm at 0.37** as `person`. So the headline recall gain (fall/lying 49.7% → 95.2%) came at roughly a **12× worse false-positive rate on rooms the model has not seen**.

This is the direct, predicted consequence of caveat 3: the person-only training set contained zero background images, so nothing ever taught the model what *isn't* a person. It was invisible until now because every previous measurement used footage from rooms that appear in training — the earlier "0 false positives on `Normal_Fall_2`'s empty tail" result was measuring a **seen** room and gave false reassurance.

**For the caregiver-alerting use case this matters more than the recall gain.** An alert system that fires on 12% of frames of an empty room is unusable, regardless of how well it detects real falls. The person-only model at `models/yolov8n_sage_person.pt` should therefore **not** be deployed as-is.

The merged multi-class dataset (section 2) includes these empty-room frames as explicit background negatives precisely to fix this, and the 11.9% figure is the before-number to beat. Re-measuring it is a required check after the merged retrain — see the runbook's step 5.

## 5.2 Merged multi-class retrain — results (`models/yolov8n_sage_merged.pt`)
Trained on Colab from stock weights over the merged dataset (10,317 images, 13 classes, 6.3% empty-room backgrounds). Full per-clip numbers: [`results/yolo_person_detection/merged_320_results.md`](../results/yolo_person_detection/merged_320_results.md).

| Gate | Person-only | Merged | Verdict |
|---|---|---|---|
| False positives, 3 empty rooms | 11.9% | **0.0%** | unproven — see below |
| False positives, *unseen* empty frames (`Normal_Fall_2` tail) | 0/40 | **3/40** | slightly worse |
| Fall/lying recall, all such clips (person-present frames) | 96.8% | 94.5% | see below |
| Fall/lying recall, **held-out clips only** | 95.9% | **96.3%** | improved |
| Object classes detectable in *our* footage | none | none | **failed** |
| Overall person detection / latency | 96.9% / 41.2 ms | 97.4% / 40.5 ms | improved |

**The two recall rows disagree, and the held-out one is the trustworthy one.** The all-clips figure includes clips the person-only model trained on and had partly memorised, which is where its 96.8% comes from. On genuinely unseen footage the merged model is *better* (96.3% vs 95.9%). The apparent 2.3pp regression is largely the older model's overfitting becoming visible, not lost capability.

**The false-positive fix is unproven, not confirmed.** 0.0% across the three empty rooms measures *fit*, because those frames are now in the training set — exactly the caveat recorded before training. The only genuinely unseen empty frames available (`Normal_Fall_2`'s 40-frame tail) went 0/40 → 3/40. Small sample, but it points the wrong way. **Do not claim the false-positive problem is solved without an empty room held back entirely from training.**

### Why object detection still fails on our footage — a design error in the merged dataset
The merged model detects all 13 classes correctly *on COCO images* (verified on 40 COCO val images: chair, couch, tv, cup, dining table, bowl, bottle, bed, refrigerator, toilet, wine glass and sink all fire at conf 0.4). It detects **zero** objects in SAGE footage.

The cause is in how the dataset was assembled: our 1,832 auto-labeled frames carry `person` as their **only** label, because MediaPipe can only label people. Every chair, bed and couch visible in them is unlabeled, and YOLO treats unlabeled regions as background. The model was therefore explicitly taught *"furniture exists in COCO-looking images but not in SAGE-looking rooms."*

This is the same failure mode this report warned about for the opposite case — deleting COCO's person boxes would teach "a person is background" — but in the direction that was missed when building the merge.

**Fix:** pseudo-label our own frames for objects by running stock YOLOv8n over them and keeping its furniture/container boxes, then merge those with MediaPipe's person boxes. Both label sources stay fully automatic. Stock YOLO cannot see fallen people, but it does not need to — MediaPipe covers the person class, and stock covers the objects it was trained on.

## 5.3 Second merged retrain with object pseudo-labels (`models/yolov8n_sage_merged_v2.pt`)
v2 adds 4,599 pseudo-labeled object boxes to our own frames (stock YOLOv8n supplying furniture, MediaPipe still supplying `person`), fixing the design error that had every chair in our rooms training as background.

| Gate | stock | person-only | v1 | **v2** |
|---|---|---|---|---|
| **1. FP on a room held back from training** | 0/56 | 3/56 (5.4%) | 0/56 | **0/56 (0.0%)** ✅ |
| 1b. FP on unseen empty frames (`Normal_Fall_2` tail) | 0/40 | 0/40 | 3/40 | **0/40** ✅ |
| FP on the 3 empty rooms *(now in training — fit only)* | 1.0% | 11.9% | 0.0% | 0.0% |
| **4. Objects detected in SAGE footage** | n/a | none | **none** | **122 boxes** ✅ |
| **3. Fall/lying recall, held-out clips** | 67.8% | 95.9% | 96.3% | **94.7%** ⚠️ |
| **2. Fall/lying recall, all clips** | — | 96.8% | 94.5% | **93.0%** ⚠️ |

### The false-positive question is now settled — properly
A fourth empty room (a dining area, 569 frames) was recorded and **never passed to `--empty_dir`**, so it stayed out of training entirely. This is the first honest precision measurement in the project.

- The person-only model's false-positive problem is **real and confirmed on unseen data**: 3/56 (5.4%).
- **Both merged models score 0/56.** The empty-room negatives genuinely fixed it — this is no longer a fit artifact.

### An incidental confirmation of the v1 diagnosis
On this held-back dining room, **v1 detected objects fine** (chair 120, dining table 41, refrigerator 17) despite detecting **zero** objects across all 28 `Testing/` clips. That is exactly what the §5.2 diagnosis predicted: v1 had learned "furniture exists in COCO-looking scenes but not in SAGE-looking rooms," and this well-lit dining room reads as COCO-like. v2, having seen furniture labeled in SAGE rooms, no longer makes that split.

### Latency
Measured on an idle machine: **49.5 ms/frame (20.2 FPS)**, versus v1's 40.5 ms. Full numbers in [`results/yolo_person_detection/merged_v2_320_results.md`](../results/yolo_person_detection/merged_v2_320_results.md).

A first attempt produced 70.0 ms, but that run overlapped a dataset rebuild on the same CPU and was discarded rather than reported — worth remembering that every latency figure in this project needs an otherwise-idle machine to mean anything.

The ~9 ms increase over v1 is plausibly postprocessing: v2 emits many more detections per frame (it actually finds the furniture), and NMS plus box decoding scale with detection count. That is a hypothesis, not a measured attribution. Either way it stays far below MediaPipe's ~110 ms, so the pose stage remains the binding latency constraint (§7).

### The open concern: person recall is drifting down
Held-out fall/lying recall has gone 95.9% (person-only) → 96.3% (v1) → **94.7%** (v2) — about 12 more missed frames out of 245. The likeliest cause is capacity shifting toward the 12 object classes now competing with `person` in the same nano-sized model.

**This matters more than it looks.** The Continuation Plan is explicit that a missed fall is the costliest error in this system, so recall on fall/lying footage is not a metric to trade away casually for object detection.

Options, in order of preference:
1. **Re-weight the person class** — rebuild with `--own_repeat 2` and retrain. Cheap and directly targets the cause.
2. **Move up a model size** (`yolov8s`) so 13 classes are not competing for nano-sized capacity — costs latency, which currently has headroom (40 ms vs MediaPipe's 110 ms).
3. **Accept it** — but only with the numbers stated plainly, since 94.7% is below the ≥95% gate this project set for itself.

## 5.4 v3 — person class re-weighted (`models/yolov8n_sage_merged_v3.pt`) — **all gates pass**
v2 had recovered object detection and fixed false positives but lost fall/lying recall, most likely because 12 object classes were competing with `person` for a nano-sized model's capacity. v3 tests the cheap fix first: rebuild with `--own_repeat 2`, doubling our own frames in train (person boxes 16,716 → 19,047) while leaving the COCO and empty-room portions untouched. Same architecture, same hyperparameters — only the class balance changes.

| Gate | Target | stock | person-only | v1 | v2 | **v3** |
|---|---|---|---|---|---|---|
| **1. FP, room held back from training** | ~0% | 0/56 | 3/56 (5.4%) | 0/56 | 0/56 | **0/56 (0.0%)** ✅ |
| 1b. FP, unseen `Normal_Fall_2` tail | 0 | 0/40 | 0/40 | 3/40 | 0/40 | **0/40** ✅ |
| **3. Fall/lying recall, held-out** | **≥95%** | 67.8% | 95.9% | 96.3% | 94.7% ✗ | **95.9%** ✅ |
| 2. Fall/lying recall, all clips | — | — | 96.8% | 94.5% | 93.0% | 94.0% |
| **4. Objects in SAGE footage** | detected | n/a | none | none | 122 | **120** ✅ |

**The cheap fix worked; `yolov8s` is not needed.** Re-weighting recovered held-out recall from 94.7% to 95.9% — back to the person-only model's level and over the ≥95% gate — while giving up essentially nothing: false positives stayed at 0/56 on the held-back room, and object detection stayed at 120 boxes versus v2's 122 (chair 96, bed 24).

This ordering mattered. Reaching for a larger model first would have cost latency and obscured the real cause, which was class balance rather than capacity.

Overall person detection 97.3% at **42.1 ms/frame (23.8 FPS)** on an idle machine — full numbers in [`results/yolo_person_detection/merged_v3_320_results.md`](../results/yolo_person_detection/merged_v3_320_results.md). Latency is back near v1's 40.5 ms, down from v2's 49.5 ms.

### What v3 is, honestly
- **Better than stock** on the thing that matters most: fall/lying recall on unseen footage, 67.8% → 95.9%.
- **Better than the person-only model** on false positives (3/56 → 0/56) at identical recall (95.9%), and it detects objects at all.
- **Still limited by data**, not modeling: only `chair` and `bed` are reliably detected in our rooms because they are nearly the only SAGE classes present. Containers appear zero times — see §6 and [`MEDICATION_DETECTION_SCOPE.md`](MEDICATION_DETECTION_SCOPE.md).

### Object-detection quality — measured against real labels
Gate 4 only established that objects are *detected*, not that the boxes are *correct*. Validating v3 against the merged val set (held-out COCO images with real labels, IoU-based mAP) gives the missing numbers:

| Class | Precision | Recall | mAP50 |
|---|---|---|---|
| person | 0.87 | 0.85 | **0.884** |
| bed | 0.86 | 0.65 | **0.838** |
| chair | 0.80 | 0.65 | **0.788** |
| toilet | 0.65 | 0.67 | 0.694 |
| refrigerator | 0.59 | 0.63 | 0.610 |
| couch | 0.58 | 0.49 | 0.536 |
| tv | 0.60 | 0.45 | 0.453 |
| bowl | 0.57 | 0.38 | 0.382 |
| cup | 0.53 | 0.34 | 0.357 |
| dining table | 0.64 | 0.29 | 0.301 |
| sink | 0.56 | 0.34 | 0.293 |
| bottle | 0.48 | 0.21 | 0.242 |
| wine glass | 0.44 | 0.23 | 0.226 |
| **all** | 0.63 | 0.48 | **0.508** |

**The two classes that actually occur in SAGE rooms — chair and bed — are the model's best object classes.** So the 120 boxes found in our footage rest on genuinely competent detection rather than noise.

**Every container proxy is poor**, and that is measured on COCO's own images where bottles are plentiful. Bottle sits at 21% recall despite ~4,160 training boxes. The split is by object size — large classes do well, small classes do badly — which implicates `imgsz=320`. Re-validating at 640 raised every container proxy (bottle 0.242 → 0.333) but collapsed `bed` (0.838 → 0.267) and lowered overall mAP, because the model was trained at 320 and the eval-resolution mismatch distorts object scale. Suggestive, not conclusive; see [`MEDICATION_DETECTION_SCOPE.md` §2b](MEDICATION_DETECTION_SCOPE.md) for the cheap experiment that would settle it.

### Remaining caveats
1. **Small held-out set.** The 95.9% rests on 245 person-present frames across 2 fall/lying clips. It is consistent across four model variants, which is reassuring, but the sample is thin.
2. **One held-back room, 56 test frames.** Enough to separate 0% from 5.4%, not enough to claim a precise false-positive rate.
3. **Same rooms, same few people.** Generalization to new environments and subjects is still untested apart from the single held-back room.
4. **Person labels remain MediaPipe-derived**, so the person class still partly measures agreement with MediaPipe rather than ground truth.

## 6. Medicine-container / furniture status
COCO includes furniture classes (`chair`, `couch`, `bed`, `dining table`, …) and container classes (`bottle`, `cup`, `bowl`). Spot checks confirm the **stock** model detects furniture plausibly (`Sit_1.mov`: person + bed; `Chair_fall.mp4`: person, chair, dining table). No `bottle` detections appeared in any clip, as expected — fall-testing footage doesn't stage medicine bottles, and COCO's "bottle" class is water/wine bottles, not pill bottles.

**Genuine medicine-container detection still needs a custom-labeled dataset** — and unlike the person labels above, that one *cannot* be auto-generated from MediaPipe, since MediaPipe only tracks human bodies. That is real manual labeling effort, comparable to the LeFD dataset work, and remains the honest blocker for the medication-adherence feature.

## 7. Recommendation for the integration phase
1. **Use `models/yolov8n_sage_merged_v3.pt`.** It passes all four gates (§5.4): 95.9% fall/lying recall on held-out footage, 0/56 false positives on a room held back from training, and working object detection. Do **not** use `yolov8n_sage_person.pt` — it matches v3 on recall but false-positives on 5.4% of unseen empty-room frames and cannot detect objects at all.
2. **YOLO is no longer the latency problem — MediaPipe is.** Fine-tuned YOLO runs at 41 ms/frame; MediaPipe (`pose_landmarker_full.task`) runs at ~110 ms/frame. Sequentially that is ~151 ms (~6.6 FPS).

   The 15+ FPS Jetson target allows a budget of **66.7 ms/frame total**. MediaPipe alone is 110 ms — it **blows the entire budget by itself, before YOLO runs at all.** This means *no amount of YOLO optimization reaches the target*: even if YOLO were free, the ceiling is ~9.1 FPS. Frame-skipping YOLO every 4th frame only moves ~151 ms → ~120 ms (~8.3 FPS), still well short.

   The lever that actually matters is therefore the **pose model**, not the detector — e.g. `pose_landmarker_lite` instead of `_full`, a reduced input resolution, or running pose estimation itself on a duty cycle. That is a decision for whoever owns the pose pipeline, and it should be made before anyone invests further in YOLO-side optimization. (All figures are laptop CPU; Jetson will differ, but the *ratio* between the two stages is the point.)
3. **Plan for two models, not one.** Person detection now wants the fine-tuned person-only model; furniture/medication detection needs stock COCO or a future custom model. Running both re-opens the latency question — worth deciding deliberately rather than by accident.
4. **Before relying on this in production, add empty-room/background frames to the training set** and re-validate precision, per caveat 3.

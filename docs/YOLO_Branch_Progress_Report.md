# S.A.G.E. — `YOLO_fatima` Branch Progress Report

**Date:** 31 July 2026
**Branch:** `YOLO_fatima` (11 commits, pushed to `origin`)
**Status:** Assigned scope **complete**. Remaining work is data collection and team decisions, not modeling.

---

## 1. TL;DR

A YOLOv8 object-detection layer now runs alongside MediaPipe as a standalone module, with a fine-tuned model that detects fallen people reliably — the thing stock YOLO fundamentally could not do.

**Ship this:** `models/yolov8n_sage_merged_v3.pt`

| Metric | Result |
|---|---|
| Fall/lying recall, held-out clips | **95.9%** |
| False positives, room held back from training | **0/56 (0.0%)** |
| Object detection in SAGE footage | **120 boxes** (chair, bed) |
| Latency | **42.1 ms/frame (23.8 FPS)** |

Stock YOLOv8n detected people in only **49.7%** of fall/lying frames. That is now **95.9%** on unseen footage.

Nothing was wired into the live pipeline — that is Section 5 integration work, deliberately out of scope per the implementation plan.

---

## 2. What was in scope

From the parallel implementation plan, §2 (`YOLO_fatima`):

| Task | Status |
|---|---|
| Install `ultralytics`, get YOLOv8n running | ✅ |
| Implement `YOLOObjectDetector` with the specified interface | ✅ |
| Standalone script; sanity-check person-detection reliability | ✅ |
| Measure per-frame latency honestly on the dev machine | ✅ |
| **Do not** wire into `realtime_fall_detection.py` | ✅ (deliberately not done) |
| Stretch: scope what custom medicine-container detection needs | ✅ |

The plan expected person detection to be "close to 100% given COCO pretraining." **It was not** — that discovery drove everything that followed.

---

## 3. What was delivered

### Code — `src/detection/` (new module, no edits to protected files)
| File | Purpose |
|---|---|
| `yolo_objects.py` | `YOLOObjectDetector` — `detect(frame) -> [{class, confidence, bbox}]` |
| `detect_test.py` | Standalone viewer (webcam or clip) with live latency overlay |
| `benchmark_footage.py` | Batch benchmark over a `Testing/` tree → markdown report |
| `generate_bbox_dataset.py` | Auto-labels training data from MediaPipe keypoints + object pseudo-labels |
| `finetune_person.py` | Fine-tuning entry point |
| `sage_classes.py` | Canonical 13-class list (`person` pinned at index 0) |
| `fetch_coco_subset.py` | Class-filtered COCO download via FiftyOne |
| `build_merged_dataset.py` | Merges our frames + COCO + empty-room negatives, remapping by class name |

### Models
| File | Notes |
|---|---|
| `yolov8n_sage_merged_v3.pt` | **Use this one** — passes all gates |
| `yolov8n_sage_merged_640.pt` | 640px experiment; better containers, fails fall gates |
| `yolov8n_sage_merged_v2.pt` / `.._merged.pt` / `.._person.pt` | Superseded; kept for comparison |

### Documentation
- `YOLO_Phase_Summary.md` — full technical write-up with all measurements
- `MEDICATION_DETECTION_SCOPE.md` — the container follow-up, sized
- `YOLO_Merged_Training_Runbook.md` — reproducible end-to-end procedure
- `results/yolo_person_detection/` — per-clip benchmark tables

---

## 4. How we got here

Each model fixed a defect the previous model's measurement exposed.

| # | Model | Fixed | Broke |
|---|---|---|---|
| 0 | stock YOLOv8n | — | Blind to fallen people (49.7% recall) |
| 1 | person-only fine-tune | Recall → 95.2% | Deleted all 79 object classes; 5.4% false positives |
| 2 | v1 merged (COCO re-added) | Objects on COCO images | Still **zero** objects in our rooms |
| 3 | v2 (+ object pseudo-labels) | Objects in our rooms; FP → 0 | Fall recall slipped to 94.7% |
| 4 | **v3 (person re-weighted)** | **Recall → 95.9%** | **Nothing — all gates pass** |
| 5 | 640px experiment | Containers +59% | Fails recall (90.6%) and latency (85.9 ms) |

Two decision points worth recording, because the cheap-first ordering paid off both times:

- **v2 → v3:** rather than jumping to a larger model (`yolov8s`), we first re-weighted the person class (`--own_repeat 2`). That recovered recall fully. The cause was class balance, not capacity — a bigger model would have cost latency and hidden the real reason.
- **Before container labeling:** rather than spending 2–5 hours labeling, we first tested whether `imgsz=320` was the blocker. It was. Labeling for a 320px model would have wasted that effort.

---

## 5. Final gate results

| Gate | Target | stock | person-only | v1 | v2 | **v3** | 640 |
|---|---|---|---|---|---|---|---|
| FP, room held back from training | ~0% | 0/56 | 3/56 | 0/56 | 0/56 | **0/56** ✅ | 0/56 |
| FP, unseen `Normal_Fall_2` tail | 0 | 0/40 | 0/40 | 3/40 | 0/40 | **0/40** ✅ | 0/40 |
| Fall/lying recall, **held-out** | ≥95% | 67.8% | 95.9% | 96.3% | 94.7% | **95.9%** ✅ | 90.6% ❌ |
| Objects in SAGE footage | detected | n/a | none | none | 122 | **120** ✅ | 139 |
| Latency | — | 98.8 ms | 41.2 ms | 40.5 ms | 49.5 ms | **42.1 ms** | 85.9 ms ❌ |

### Object-detection quality (mAP50, IoU-based, against real labels)
| person | bed | chair | toilet | refrigerator | couch | tv | bowl | cup | dining table | sink | bottle | wine glass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.884 | 0.838 | 0.788 | 0.694 | 0.610 | 0.536 | 0.453 | 0.382 | 0.357 | 0.301 | 0.293 | 0.242 | 0.226 |

`chair` and `bed` — the only two classes that actually occur in SAGE rooms — are the model's best object classes, so detections in our footage rest on competent detection rather than noise.

---

## 6. Findings beyond the models

**Three measurement bugs that would have produced confidently wrong conclusions:**

1. **`Normal_Fall_2.mov` "worst clip" was a metric artifact.** The subject slides out of frame for the final 40 of 131 frames. Recall on that clip is 93.4%, not the 64.9% raw detection rate implied — and those 40 empty frames became the project's first false-positive evidence.
2. **`Testing/` contains byte-identical duplicate footage.** `normal.mp4`/`normal.mov` and `old.mp4`/`old.mov` share MD5s. The corpus is **26 unique clips / 8,189 frames**, not 28 / 9,188.
3. **A filename collision silently discarded 499 training frames** while reporting success. Frames were keyed on clip stem alone, so same-named clips in different folders overwrote each other. Fixed; worth checking for in the other branches' pipelines.

**MediaPipe, not YOLO, is the latency wall.** 15 FPS allows 66.7 ms/frame. MediaPipe alone costs ~110 ms — it exceeds the entire budget before YOLO runs. Even with YOLO free, the ceiling is ~9.1 FPS. No YOLO-side optimization reaches the Jetson target.

**Container detection has two independent blockers**, not one: resolution (confirmed by experiment) *and* absent training data (zero container instances across all 28 clips).

---

## 7. Honest limitations

1. **Small held-out set.** The 95.9% rests on 245 person-present frames across 2 fall/lying clips.
2. **One held-back room, 56 frames.** Enough to separate 0% from 5.4%, not to claim a precise false-positive rate.
3. **Same rooms, same few people.** Generalization to new environments and subjects is largely untested.
4. **Person labels are MediaPipe-derived**, so that class partly measures agreement with MediaPipe rather than ground truth.
5. **`chair`/`bed`/`person` validation is partly circular** — majority pseudo-labels. Container classes are clean (100% real COCO annotation).
6. **Only `chair` and `bed` detect reliably in our footage**, because they are nearly the only SAGE classes present in it.

---

## 8. Next steps

### A. Medicine-container detection — the real remaining work
**Owner:** data collection (you) + a follow-up branch
**Effort:** ~2–4 hrs recording, ~2–5 hrs labeling, 1 Colab run

1. Record footage containing pill bottles / blister packs / pill organizers, in the same rooms, lighting and camera angles as the fall footage.
2. Label with tracking-assisted tooling (CVAT or Roboflow) — the source is video and containers are static, so interpolation cuts the effort several-fold.
3. Append new classes at indices **13+** in `sage_classes.py`. **Never reorder existing indices** — index order is part of every checkpoint's contract and changing it invalidates models silently rather than erroring.
4. Train as a **separate higher-resolution model on a low duty cycle**, not by changing the fall-detection model's resolution. Medication adherence happens over seconds to minutes and does not need 15 FPS, which sidesteps the latency conflict.

Full detail: [`MEDICATION_DETECTION_SCOPE.md`](MEDICATION_DETECTION_SCOPE.md)

### B. The pose-pipeline latency decision
**Owner:** whoever owns MediaPipe / the pose pipeline
Options: `pose_landmarker_lite` instead of `_full`, lower pose input resolution, or duty-cycling pose estimation. This is a bigger architectural question than anything left in this branch, and it gates the Jetson target.

### C. Integration into the live pipeline
**Owner:** team, one person at a time
Deliberately not started. Per the implementation plan this is gated on the TCN comparison landing first, since that decides what the structured event schema reasons over.

### D. Optional / low value
- A 30-epoch 640px run would resolve whether that model's recall drop was resolution or under-training. Latency disqualifies it either way.
- More held-out fall/lying clips, ideally in a new room with a new person, would tighten the 95.9% figure considerably.

---

## 9. Definition-of-done status

| Item | Status |
|---|---|
| All new code in a new module; no edits to protected files | ✅ |
| Markdown write-up in the style of `LSTM_Phase_Summary.md` | ✅ |
| `python -m unittest discover -s tests` | ⚠️ 36/37 — the failure is pre-existing (`tensorflow-cpu` has no wheel for this machine's Python 3.14), unrelated to this branch |
| No regression on `hybrid_evaluate.py` | ❌ **Not run.** Same TensorFlow gap would silently disable the LSTM half, making the comparison meaningless. This branch touches no pipeline files, so it is a formality — but it is untested |
| Branch kept in sync with `main` | ❌ **Not possible** — `main` does not exist locally or on the remote; `YOLO_fatima` is the only branch there |

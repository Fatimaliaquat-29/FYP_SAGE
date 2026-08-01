# Follow-up scope — Medicine-container detection

**Status:** not started. Explicitly **out of scope** for the current YOLO rounds.
**Branch:** `YOLO_fatima` (scoping only — implementation belongs in a follow-up branch)

This document exists so medicine-container detection is tracked as its own sized piece of work rather than something each YOLO retrain is vaguely expected to fix. It is the same call the original parallel implementation plan made when it flagged container detection as "realistically its own follow-up effort, comparable to how the LeFD dataset had to be added for fall detection."

---

## 1. Why this cannot ride along with the current work

Every other label in this project has been **free**:

| Label type | Source | Cost |
|---|---|---|
| `person` (incl. lying poses) | MediaPipe's 33 keypoints → padded box | automatic |
| `chair`, `bed`, `dining table`, `tv` | Stock COCO YOLOv8n pseudo-labels | automatic |
| Medicine containers | **nothing available** | **manual** |

Neither automatic source can produce these labels:

- **MediaPipe only tracks human bodies.** It has no concept of an object.
- **Stock COCO's `bottle` class is water/wine/soda bottles** — photographed at a different scale, context and shape from a pill bottle on a nightstand. It is a placeholder, not a detector for this task.

## 2. Evidence from this branch — the gap is measured, not assumed

Sampling every 60th frame across all 28 `Testing/` clips with stock YOLOv8n:

| Confidence | Container-proxy detections (`bottle`, `cup`, `bowl`, `wine glass`) |
|---|---|
| 0.50 | **0** |
| 0.35 | **0** |

Only `chair`, `bed`, `dining table` and `tv` appear at all. **Nine of the 13 SAGE classes never occur in our footage**, so no amount of pseudo-labeling or retraining on current data can produce a container detector. The blocker is data, not modeling.

## 2b. It may not be *only* a data problem — resolution is a second suspect

Earlier revisions of this document framed container detection as purely a data-collection gap. Validation of `yolov8n_sage_merged_v3` against held-out **COCO** labels (where bottles are plentiful and well-labeled) complicates that:

| Class | mAP50 @320 | Recall @320 |
|---|---|---|
| person | 0.884 | 0.85 |
| bed | 0.838 | 0.65 |
| chair | 0.788 | 0.65 |
| **bottle** | **0.242** | **0.21** |
| wine glass | 0.226 | 0.23 |
| cup | 0.357 | 0.34 |

The model detects bottles at **21% recall despite training on ~4,160 bottle boxes**. Large objects (bed, chair) do fine; small objects do badly. That pattern points at **`imgsz=320`**, chosen for the Jetson latency target, degrading small-object detection — containers are small, furniture is not.

Re-validating at 640 supports this but does **not** settle it:

| Class | mAP50 @320 | mAP50 @640 |
|---|---|---|
| bottle | 0.242 | 0.333 |
| cup | 0.357 | 0.408 |
| wine glass | 0.226 | 0.261 |
| bowl | 0.382 | 0.411 |
| bed | 0.838 | **0.267** |
| all | 0.508 | 0.421 |

Every container proxy improved, but `bed` collapsed and overall mAP fell — because the model was *trained* at 320, so evaluating at 640 shifts the object-scale distribution away from what it learned. **The container gains are therefore suggestive, not conclusive.**

## 2c. EXPERIMENT RUN — resolution confirmed as a real blocker, but 640 is not deployable

A model was trained natively at `imgsz=640` on the existing merged dataset (`models/yolov8n_sage_merged_640.pt`, 15 epochs vs v3's 30). **Container classes improved substantially, and the measurement is clean.**

Label-provenance check first, because it determines what can be trusted: every container class in the val set is **100% real COCO annotation with zero pseudo-label contamination** (`bottle` 0 own / 408 COCO, `cup` 0/301, `wine glass` 0/156, `bowl` 0/247). `person`, `chair` and `bed` are majority pseudo-labels and therefore partly circular.

| Class | v3 @320 (30 ep) | 640 (15 ep) | Change | Labels |
|---|---|---|---|---|
| **bottle** | 0.242 | **0.385** | **+59%** | clean |
| **wine glass** | 0.226 | **0.368** | **+63%** | clean |
| **cup** | 0.357 | **0.476** | **+33%** | clean |
| **bowl** | 0.382 | **0.493** | **+29%** | clean |
| sink | 0.293 | 0.465 | +59% | clean |
| all | 0.508 | 0.539 | +6% | mixed |

Every container proxy improved, on real labels, with **half the training epochs** — so the gain is if anything understated. **Resolution was a genuine constraint, not merely a data gap.** The earlier framing of this as purely a data-collection problem was wrong.

### But the 640 model fails the fall-detection gates

| Gate | v3 @320 | 640 model |
|---|---|---|
| FP, held-back room | 0/56 | **0/56** ✅ |
| FP, unseen `Normal_Fall_2` tail | 0/40 | **0/40** ✅ |
| Objects in SAGE footage | 120 | **139** ✅ |
| **Fall/lying recall, held-out** | **95.9%** | **90.6%** ❌ |
| Fall/lying recall, all clips | 94.0% | 90.6% ❌ |
| **Latency** | **42.1 ms** | **85.9 ms** ❌ |

Held-out fall/lying recall drops **5.3 points, far below the ≥95% gate**, and latency doubles. Since a missed fall is this project's costliest error, that disqualifies the 640 model as the fall-detection model regardless of its container advantage.

**Confound to be honest about:** the 640 model trained for 15 epochs against v3's 30, so part of the recall loss may be under-training rather than resolution. Notably its *val* person mAP is higher than v3's (0.911 vs 0.884) while its real-footage fall/lying recall is lower — val person is dominated by upright frames from `newTest`, so the two are not measuring the same thing. Resolving this cleanly needs a 30-epoch 640 run.

**Latency is decisive independent of that.** At 85.9 ms, YOLO alone nearly exceeds the entire 66.7 ms budget for 15 FPS, and MediaPipe's ~110 ms sits on top of it — ~196 ms combined (~5.1 FPS) versus v3's ~152 ms. No amount of extra training changes that arithmetic.

### Conclusion: this is a two-model problem, not a resolution setting
- **Keep `yolov8n_sage_merged_v3.pt` @320 as the fall-detection model.** It passes every gate.
- **Container detection needs its own model at higher resolution**, run at a low duty cycle rather than per frame — medication adherence is an event that happens on a timescale of seconds to minutes, so it does not need 15 FPS. This sidesteps the latency conflict entirely.
- **Labeling is still required**, and is now justified: resolution alone got `bottle` only to 0.385 mAP on COCO's own well-lit bottles. Real pill bottles in dim rooms will be harder, so labeled in-domain data remains the larger lever.

### Original framing, kept for the record
The experiment was proposed to run *before* labeling precisely so that 2–5 hours would not be spent training a 320px model that fundamentally could not resolve containers. That risk was real, and the ordering paid off.

## 3. What the work actually is

### 3a. Record footage (est. 2–4 hours)
Containers must appear in the same rooms, lighting and camera angles as the fall footage — a detector trained on product photos will not transfer to a nightstand at ceiling-camera angle.

Cover, per container type:
- Multiple positions (nightstand, table, held in hand, on the floor)
- Both distances the camera actually sees
- Partially occluded and partially out of frame
- The lighting conditions already present in `Testing/` (these rooms are fairly dim)

### 3b. Decide the class list
Recommended starting classes, kept deliberately small:

| Proposed class | Rationale |
|---|---|
| `pill_bottle` | The canonical case |
| `blister_pack` | Visually very different from a bottle; common for elderly medication |
| `pill_organizer` | Weekly day-boxes are extremely common in elderly care |

Three classes is enough to prove the pipeline. Adding `medicine_box` and `inhaler` later is cheap once the labeling workflow exists.

**Continuity requirement:** append these to `src/detection/sage_classes.py` as indices **13, 14, 15**. Do not reorder or renumber the existing 13 — index order is part of every trained checkpoint's contract, and changing it silently invalidates prior models rather than erroring.

### 3c. Label (est. 2–5 hours)
Rough sizing, based on typical single-class YOLO fine-tuning:

| Target | Instances per class | Images per class |
|---|---|---|
| Proof of concept | ~150–300 | ~200 |
| Reasonably robust | ~500+ | ~400 |

For three classes at proof-of-concept level that is **~600 labeled images**. At a realistic 4–8 images/minute for simple single-object boxes, that is **2–5 hours of manual work**.

**Cut this substantially with tracking-assisted labeling.** CVAT and Roboflow both let you box an object in one frame and propagate it across the clip, correcting only where it drifts. Since containers are largely static in a scene, this can reduce the effort several-fold versus labeling frame by frame. Given the footage is video, this is strongly recommended over frame-by-frame tools.

Suggested tooling: **CVAT** (free, self-hosted, good interpolation) or **Roboflow** (free tier, easier setup, exports YOLO format directly). Either must export YOLO-format `.txt` labels to drop into the existing merge pipeline.

### 3d. Merge and train (est. 1 hour + one Colab run)
The existing pipeline already handles this with no changes beyond the class list:
```bash
python src/detection/build_merged_dataset.py \
    --coco_dir datasets/coco_subset \
    --empty_dir Testing_EmptyRooms \
    --container_dir datasets/containers      # new source, same remap-by-name path
```
`build_merged_dataset.py` remaps every source strictly by class name and aborts on unknown names, so a container dataset slots in as a third source without touching the existing logic.

## 4. Deliverables
- A labeled container dataset (~600 images, 3 classes), stored outside `Testing/` so it cannot disturb the held-out split
- A retrained model detecting containers in SAGE rooms
- Precision/recall per container class on a held-out set of clips
- An honest write-up, in the style of `YOLO_Phase_Summary.md`, including how thin the validation set is

## 5. Definition of done
- [ ] Container classes appended to `SAGE_CLASSES` as indices 13+ with existing indices untouched
- [ ] ≥150 labeled instances per class
- [ ] Held-out clips reserved that were never labeled *or* trained on
- [ ] Person/fall gates re-run and **not regressed** — container support must not cost fall-detection recall
- [ ] False-positive rate re-measured on held-back empty rooms

## 6. Dependencies and sequencing
- **Blocked on:** recording and labeling. Nothing else.
- **Blocks:** the medication-adherence feature in the Scope Document, and any LLM reasoning layer that expects container events in its structured schema.
- **Independent of:** the current person-detection and false-positive work. These can proceed in parallel and should not wait on each other.

## 7. Explicitly not expected from the current rounds
The in-flight retrain is expected to recover detection of `chair`, `bed`, `dining table` and `tv` — the objects that genuinely appear in our rooms — and to answer the false-positive question. It is **not** expected to produce any container detection, and should not be judged against that.

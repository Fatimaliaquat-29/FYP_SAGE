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

### What this means for the plan
**Run the cheap experiment before the expensive one.** Before committing 2–5 hours to labeling, train one model at `imgsz=640` on the *existing* merged dataset and compare container-proxy mAP against v3. That is one Colab run and no new labeling, and it answers whether resolution is a real blocker.

- **If container mAP jumps at 640:** resolution is a genuine constraint, and container detection needs a bigger input than the current Jetson budget allows. That is a **latency/hardware decision that must be made before labeling**, since labeling for a 320px model that fundamentally cannot see containers would be wasted effort.
- **If it does not jump:** resolution is exonerated, the bottleneck really is data, and the labeling plan below proceeds as written.

This ordering mirrors the `--own_repeat` vs `yolov8s` decision in the phase summary: rule out the cheap cause before paying for the expensive fix.

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

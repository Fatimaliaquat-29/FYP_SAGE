# Re-scoring A and A2 on the corrected held-out labels

**PROVISIONAL:** until this step is done, every round6_heldout score is measured against labels that follow no consistent written convention (docs/LABELLING_SPEC.md, v0.1 draft).

This is the last step, after the retag in Roboflow (`ROBOFLOW_SETUP.md`). It needs:
- A2's weights at `benchmarks\phase3_a2\runs\A2\weights\best.pt` (they exist only after A4 has run);
- the `.venv2` interpreter (ultralytics 8.4.115, CUDA).

## 1. Check the export

```powershell
$py = 'D:\FYP\PROJECT FILES\main\.venv2\Scripts\python.exe'
$rf = 'D:\FYP\PROJECT FILES\main\benchmarks\phase3_a2\roboflow'
& $py "$rf\check_export.py" "$rf\export\sage-heldout-retag-1"
```

It must print `ALL PASS`. If the class order fails, do not continue: the ids in the label files mean different classes.

Frames with no boxes at all must be marked **Null** in Roboflow. Otherwise they are left out of the version, and the export has fewer than 298 images. A missing label file is treated by the scorer as "not labelled", so the frame is excluded; it is not counted as an empty frame.

## 2. Bring the corrected labels back under the original frame names

```powershell
& $py "$rf\import_corrected_labels.py" "$rf\export\sage-heldout-retag-1"
```

This creates `handlabels\round6_heldout_v2\`:
- `labels\` holds the export labels, renamed from `<stem>_jpg.rf.<hash>` back to `<stem>`;
- `images\` holds copies of the original frames;
- `classes.txt` is copied from round6_heldout.

`handlabels\round6_heldout\` is not touched, because it is the record of what v7 was scored on. The script re-runs `check_export.py` first and refuses to write if anything fails or if `round6_heldout_v2` already exists.

## 3. Score A and A2 on original vs corrected labels

`rescore_suite.py` imports `src/detection/score_v7_suite.py` unchanged. It swaps only:
- the model list: A = `models/yolov8n_sage_merged_v7.pt`, A2 = `runs/A2/weights/best.pt`;
- the eval sets: round6_heldout original and round6_heldout_v2 corrected;
- where the report is written.

Settings are the suite's own: conf 0.4, imgsz 640, same-class greedy matching by confidence.

```powershell
& $py "$rf\rescore_suite.py" 0.5
& $py "$rf\rescore_suite.py" 0.3
```

Reports go to `roboflow\rescore_out\results\yolo_person_detection\v7_suite_iou0.5.md` (and `iou0.3`). They do **not** overwrite the tracked `results\yolo_person_detection\v7_suite_iou*.md`.

Control: on the ORIGINAL labels, A must still show person recall 0.22 (50/226) at IoU 0.5, as in `results\yolo_person_detection\v7_suite_iou0.5.md`. If it does not, stop: something else changed.

## Limits of this step

- `score_v7_suite.py` reports per-class precision and recall only. It does not save per-box hit vectors, so it cannot give the paired McNemar test from the pre-registered decision rule. For that, use the A5 harness (`benchmarks\phase3_a2`) and point it at `round6_heldout_v2`.
- Corrected labels change the denominator. Compare A and A2 on the **same** label set; never compare one model on the original labels with the other on the corrected ones.

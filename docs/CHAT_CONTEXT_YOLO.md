# Chat context — YOLO track (handoff)

Last session: 14 Aug 2026. Branch `YOLO_fatima` @ `e715212`, pushed, clean.

**Where we stopped:** `datasets/sage_merged_v5/` is built and verified. The only
remaining step is the Colab training run, then scoring. See
[`TRAINING_v5_CONTEXT.md`](TRAINING_v5_CONTEXT.md).

---

## The one-paragraph version

Every furniture and person number this project had quoted was measured against
labels a model generated, not a human. We built the first hand-labelled held-out
evaluation set (385 label files, 11 clips, 3 rooms), and it showed v3 detects
people at 0.83–1.00 on walk/sit clips but only 0.25–0.45 on fall clips. Root
cause traced to `generate_bbox_dataset.py` still using MediaPipe `IMAGE` mode —
fixed, dataset rebuilt as v5, awaiting a training run.

---

## Findings that should not be re-derived

**1. Detection rate splits by activity, not room.** v3 @ imgsz 640, hand labels:
walk/sit **0.83–1.00**, fall **0.25–0.45**, five fall clips, three rooms, no
overlap. All misses are IoU 0.00 — no box emitted, not a localisation error.

**2. Why the misses happen.** Looked at all 51 (`eval/missed_falls/`). Motion
blur explains 2. The rest: person lying **on furniture** rather than open floor,
foreground occlusion (a glass table crosses the body in every missed
`TV_Lounge_1_Fall` frame), dark clothing on dark furniture. Control:
`people_(2)` is a fallen person on an **open floor** in light clothing —
detected 0.94. So the failure is "person merged with furniture in low contrast",
not "person is fallen".

**3. Root cause of the label gap.** `generate_bbox_dataset.py` used
`RunningMode.IMAGE`; the runtime and eval paths were switched to `VIDEO` in
`b566685` but the label generator was missed. IMAGE re-detects from scratch each
frame; VIDEO seeds the ROI from the previous frame and carries tracking through
a fall. Fixed in `02521f1`. Fall-clip label coverage 0.70 → 0.83.

**4. v4 should not ship.** 0/52 hand-labelled fallen people at *both*
resolutions, where v3 gets 30/52. Worse than v3 on upright too. Its only
advantage is a lower false-positive rate.

**5. `merged_640` was rejected on a bad gate.** It failed "fall recall" measured
against the pseudo-labelled split; on hand labels it is the *best* model
(0.854 upright, 32/52 lying). Its latency gate failure (85.9 ms) is real but is
the cost of **640**, not of that checkpoint — v3@640 and merged_640@640 measured
identical (150.3 vs 150.2 ms median, same architecture, same input size).

---

## Traps — every one of these produced a believable wrong number

- **imgsz.** Ultralytics `predict()` defaults to 640; the merged series trains
  at 320. Every model detects **0/52** fallen people at 320 and 30–32/52 at 640.
  Always pass `--imgsz` explicitly and match it across compared models.
- **conf.** Comparing v3 @ 0.25 against v4 @ 0.4 inflated v3's false-positive
  rate to 49.32% (21.26% at matched settings).
- **Frame rotation.** `cv2.VideoCapture` ignores rotation metadata. Eight clips
  are stored portrait. An unrotated `Bedroom_Fall` produced a fake "0/20 blind
  to falls" result *and* corrupted the labels, because posture was derived from
  box aspect ratio and a sideways standing person is wide. Now handled by
  `src/detection/footage_rotation.py` — eye-verified per clip, metadata used
  only to flag suspicion. Extraction **refuses** unverified clips.
- **Orphaned labels.** Re-extraction renamed images and silently detached 50
  hand labels, dropping 32 lying boxes out of scoring with no error. Always
  check `labels − images` is empty before trusting a score.
- **Aspect ratio as a posture proxy.** `w/h > 1` = "lying" is broken: three of
  five fall clips produce zero wide boxes (falling onto a bed keeps a tall box).
  Use per-clip detection rate instead; it needs no proxy.

---

## Layout

```
testing/            SHARED person+fall footage (also used by fall-detection track)
yolo_testing/
    Training/Empty/         background negatives
    Reserved/Empty|With people/   NEVER trained on
eval/heldout_objects/   images/ (gitignored) + labels/ (committed, 385 files)
```

`Reserved/` is protected by code, not convention: `assert_not_reserved()` in
`src/detection/footage_paths.py` aborts any training-data producer pointed at
it. Evaluation scripts are deliberately allowed to read it.

Footage is gitignored — it contains identifiable people. Hand labels are
committed; extracted stills are not.

---

## Tooling added this session

| script | purpose |
|---|---|
| `footage_paths.py` | canonical paths + reserved guard |
| `footage_rotation.py` | eye-verified per-clip rotation table |
| `report_label_sources.py` | which labels are pseudo vs human, per class |
| `sample_heldout_frames.py` | frame extraction + camera-drift detection |
| `score_heldout_objects.py` | recall vs hand labels (`--classes`, `--imgsz`) |
| `score_empty_false_positives.py` | FP over EVERY frame of empty rooms (needs no labels) |
| `label_frames.py` | local OpenCV labeller (unused now — labelImg works) |

**labelImg** is installed and patched for Python 3.14 (four float→int fixes in
`libs/canvas.py`, `labelImg.py`, `libs/zoomWidget.py`; backups as `*.py.bak`).
Launch: `& "C:\Users\DELL\AppData\Roaming\Python\Python314\Scripts\labelImg.exe" <images> eval\heldout_objects\classes.txt eval\heldout_objects\labels`
— **switch PascalVOC → YOLO before labelling.**

---

## Next actions

1. **Colab: train v5** from stock `yolov8n.pt` at `imgsz=640`. Full cell in
   [`TRAINING_v5_CONTEXT.md`](TRAINING_v5_CONTEXT.md). Cannot be done locally
   (~28 min/epoch, ~14 h for 30 epochs).
2. **Score v5 vs v3 at matched settings** — the number that matters is fall-clip
   detection against v3's 0.25–0.45, with walk/sit holding at 0.83–1.00.
3. **Open item:** empty-room false-positive rates were measured at imgsz 320
   (v3 2.70%, v4 0.39%). Re-run at 640 before using as a gate.
4. **Still unlabelled:** 148 frames, mostly upright `TV_Lounge_*` clips. Low
   value — upright is already well established.
5. **Tell Hussain:** `build_lstm_datasets.py` may have the same IMAGE-mode gap.

### Expectations, honestly

v5 adds +385 person boxes on 19,047 (+2%), concentrated in fall frames (+26% of
that class). This tests whether label density was the binding constraint. A
large jump would be surprising. If v5 shows no improvement that is a real
result — it would mean the next lever is recording the missing conditions
(person on furniture, dark, occluded), with hand-labelling budgeted in, because
MediaPipe covers only ~46% of the hardest fall frames even in VIDEO mode.

---

## Detailed reports

- [`results/yolo_person_detection/reserved_heldout_posture.md`](../results/yolo_person_detection/reserved_heldout_posture.md) — detection by activity, the four corrected measurement faults
- [`results/yolo_person_detection/labeler_video_mode_fix.md`](../results/yolo_person_detection/labeler_video_mode_fix.md) — root cause, elimination testing, box verification
- [`docs/TESTING_GUIDE.md`](TESTING_GUIDE.md) — footage layout
- `reserved_people_v3.md` / `_v4.md` carry caution blocks: their "Falling/lying
  clips 56.1%" is a per-frame rate over clips that *contain* a fall, mostly
  upright footage. Not a fall-detection rate.

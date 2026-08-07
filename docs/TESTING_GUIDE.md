# SAGE FYP — Testing Folders Guide

Maps every "testing" location in the repository, so team members know what each
one is for and what the rules are.

> **Layout changed (Aug 2026).** Footage used to live in four sibling
> directories (`Testing/`, `Testing_EmptyRooms/`, `Testing_EmptyHeldOut/`,
> `Testing_HeldOutEval/`). It now lives in **two** trees, split by *who needs
> it* rather than by *what it contains*. The authoritative, committed
> definition is the module docstring in
> [`src/detection/footage_paths.py`](../src/detection/footage_paths.py) — the
> READMEs inside the footage folders are gitignored and do not reach teammates.

---

## The two trees

```
Testing/                    SHARED — person + fall footage, with _gt.csv sidecars
    Hussain Testing 7-23-26/
    Sanawar Testing 7-22-26/
    Sanawar Testing 7-25-26/

yolo_testing/               YOLO-ONLY
    Training/               may be trained on
        Empty/                  empty rooms -> background negatives
        With people/            (empty; person source is Testing/)
    Reserved/               NEVER trained on
        Empty/                  held-out empty room  -> false-positive gate
        With people/            held-out room+person -> recall test
```

**Why `Testing/` was not folded in:** the fall-detection track reads those same
clips and their ground-truth CSVs. Restructuring it would break that work, so
YOLO reads it in place. A useful side effect is that the clip ordering never
changed, so the index-based train/val split still matches every previously
reported number.

---

## Quick Reference

| Folder | Purpose | In training? | Safe to evaluate against? |
|---|---|---|---|
| `Testing/` | Shared session footage (person + falls, with GT) | YES | No — treat as seen data |
| `yolo_testing/Training/Empty/` | Empty-room background negatives | YES | No — already in training |
| `yolo_testing/Training/With people/` | Future YOLO-only person footage | (empty) | — |
| `yolo_testing/Reserved/Empty/` | Held-out empty room | **NO** | **YES** — false-positive gate |
| `yolo_testing/Reserved/With people/` | Held-out room + person | **NO** | **YES** — recall test |
| `tests/` | pytest code tests | N/A | N/A — `pytest tests/ -v` |

---

## 1. `Testing/` — Shared Session Footage

Real-world recordings by team members. One subfolder per session, named
`{FirstName} Testing {M-DD-YY}/`. Clips plus matching `_gt.csv` label files.

**Used by**: `generate_bbox_dataset.py` and `benchmark_footage.py` (this is the
default `--testing_dir`), and by the fall-detection evaluation scripts.

> **Rules**
> 1. This footage **is** fed into training. Never treat clips here as "unseen".
> 2. **Do not restructure or rename.** Train/val is assigned by position in the
>    sorted listing, so reordering silently changes which clips are held out.
>    The current held-out four are `newTest`, `Sit_2`, `Normal_Fall_2`,
>    `Foward_fall`.
> 3. New sessions go in a new subfolder, never loose in the root.

See [`Testing/README.md`](../Testing/README.md) for session naming and GT format.

---

## 2. `yolo_testing/Training/` — YOLO Training Footage

`Empty/` holds empty-room clips that become background negatives — the frames
that make a false-positive rate measurable at all. Passed via
`build_merged_dataset.py --empty_dir`.

`With people/` is intentionally empty; person footage comes from `Testing/`.
It exists for footage recorded for YOLO alone. Clips placed there are **not**
picked up by the default `--testing_dir`, and using two person sources at once
shifts the index-based split.

> **Rule**: already in training — never use as a held-out benchmark.

---

## 3. `yolo_testing/Reserved/` — Held Out From Everything

Footage from rooms and people appearing in **no** training run. The only source
of honest numbers.

- `Empty/` — nobody in frame; measures **false positives**
- `With people/` — measures **recall**

> **This is enforced in code, not by convention.**
> `assert_not_reserved()` in [`footage_paths.py`](../src/detection/footage_paths.py)
> aborts any training-data producer pointed at it:

| script | on `Reserved/` |
|---|---|
| `generate_bbox_dataset.py` | **aborts** — produces training frames |
| `build_merged_dataset.py --empty_dir` | **aborts** — produces negatives |
| `benchmark_footage.py` | **allowed** — measuring is the point |
| `score_heldout_objects.py` | **allowed** — measuring is the point |

The distinction is *"does this path feed a training set"*, not *"does this path
get read"*. Evaluation scripts are supposed to read it.

> **Rule**: one-way. Its entire value is that no model has seen it. One training
> run ends that permanently, and moving files back does not restore it.

See [`yolo_testing/Reserved/README.md`](../yolo_testing/Reserved/README.md).

---

## 4. `tests/` — Python Unit & Integration Tests

Automated pytest code tests. Nothing to do with footage.

- `test_lstm_pipeline.py` — LSTM fall-detection pipeline
- `test_posture_pipeline.py` — posture/MediaPipe pipeline

```bash
pytest tests/ -v
```

---

## Adding New Footage — Checklist

- [ ] New real-world session? → `Testing/{Name} Testing {M-DD-YY}/` with a `_gt.csv`
- [ ] Empty room for training negatives? → `yolo_testing/Training/Empty/`
- [ ] Should NEVER touch training? → `yolo_testing/Reserved/Empty/` or `Reserved/With people/`
- [ ] Python unit test? → `tests/`, named `test_*.py`

**After adding anything to `Testing/`**, confirm the held-out set did not shift:

```bash
python -c "from src.detection.footage_paths import TRAINING_PEOPLE; \
from src.detection.generate_bbox_dataset import find_clips, split_clips; \
print(sorted(p.stem for p in split_clips(find_clips(TRAINING_PEOPLE))[1]))"
```

Expected: `['Foward_fall', 'Normal_Fall_2', 'Sit_2', 'newTest']`. If it differs,
every previously reported comparison is invalid until re-run.

**Recording tip:** prop the camera up rather than holding it. Handheld footage
drifts, which forces every evaluation frame to be labelled separately instead
of labelling one and copying it. `sample_heldout_frames.py` measures drift and
tells you which case you are in.

---

## Related Documentation

- [`src/detection/footage_paths.py`](../src/detection/footage_paths.py) — authoritative layout definition (committed)
- [`Testing/README.md`](../Testing/README.md) — session naming & GT CSV format
- [`yolo_testing/README.md`](../yolo_testing/README.md) — YOLO footage tree
- [`docs/YOLO_Merged_Training_Runbook.md`](YOLO_Merged_Training_Runbook.md) — training pipeline runbook
- [`docs/data_quality_improvement_plan.md`](data_quality_improvement_plan.md) — why held-out labels must be hand-drawn

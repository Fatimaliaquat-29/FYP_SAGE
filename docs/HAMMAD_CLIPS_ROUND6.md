# Hammad clips — round 6 labeling plan

10 clips recorded by Hammad, landed in `shared/Hammad Clips/`, moved to
`yolo_testing/held_out/Hammad Clips/` (nested under `held_out/` so they inherit
protection from the existing `heldout` marker in `footage_paths.py` — no code
change needed, `is_protected()` already returns `True` for anything under this
path). **Nothing here has entered any training dataset.**

Two clips were renamed on disk mid-session — `BehindFurniture_HM.mp4` →
`Behind_Bed_HM.mp4` and `Behind_Furniture_HM.mp4` → `Behind_Chair_HM.mp4`
(confirmed same files by identical size/mtime, not re-verified as new
recordings). `footage_rotation.py` and every script below use the new names.

Rotation: all 10 confirmed upright by eye (frame ~30% into each clip — same
fixed camera/room, walls/AC/door level throughout). Registered in
`footage_rotation.py`.

## Coverage-based triage (`coverage_hammad_clips.py`, every frame, VIDEO mode)

Initial triage was by coverage % alone; the investigate tier was then re-split
by miss-run length (`investigate_hammad_misses.py`), which is the number that
actually decides whether patching is safe:

| clip | coverage | miss-run pattern | final decision |
|---|---|---|---|
| LyingDown_HM, Sitting_Chair_HM, Standing_Walking_HM, PartiallyCovered_HM | 95–100% | n/a | auto-label + spot-check |
| Standing_Walking_Dim_HM | 87% | 33 runs, mean 5.2 frames (~1.3s) | **patch gaps only** |
| Sitting_Dim_HM | 86% | 55 runs, mean 3.8 frames (~1.1s) | **patch gaps only** |
| Behind_Chair_HM | 67% | 42 runs, mean **13.3 frames (~4.5s), up to 136** | moved to **full hand-label** — real dropouts, not flicker |
| Blanket_Cover_HM, Behind_Bed_HM, Laying_Dim_HM | 12.5–55.5% | n/a | full hand-label |

Actions taken:
- **Auto-label + spot-check** (4 clips): `autolabel_hammad_staging.py` →
  `datasets/hammad_autolabel_staging/` + spot-check renders in
  `results/yolo_person_detection/hammad_autolabel_spotcheck/`.
- **Full hand-label** (now 4 clips: Blanket_Cover_HM, Behind_Bed_HM,
  Laying_Dim_HM, Behind_Chair_HM): `sample_heldout_frames.py` →
  `handlabels/round6/images/` (619 frames total, stride 10), `labels/` empty
  and ready, `classes.txt` matching SAGE_CLASSES.
- **Patch only** (2 clips: Standing_Walking_Dim_HM, Sitting_Dim_HM):
  `extract_hammad_patch_frames.py` extracted the exact 173 + 211 = 384 missed
  frames (not a stride sample — every gap, so the patch has no holes) into
  `handlabels/round6_patch/images/`, `labels/` empty, `classes.txt` in place.
  Once labeled, pass `--handlabels_dir handlabels/round6_patch` to
  `generate_bbox_dataset.py` **without** `--handlabels_only`, so MediaPipe's
  own frames for these two clips are kept everywhere else and only these
  exact gaps get overridden.

Camera-drift check on the full-hand-label tier (from `sample_heldout_frames.py`):
Behind_Bed_HM and Blanket_Cover_HM are camera-STATIC (furniture boxes copyable
across frames, person box still per-frame). **Laying_Dim_HM and Behind_Chair_HM
both camera-MOVE — every frame needs labeling individually, no copying.**

## Staging outputs are NOT training data

`datasets/hammad_autolabel_staging/` is a preview only — it was written by
calling `assert_not_protected(..., allow_protected=True)` explicitly (printed
warning each time), the same override any real promotion would need, but none
of this project's `build_merged_dataset.py` / training runs reference this
directory. Promoting any of it requires a deliberate future step.

## Hold-back decision — CONFIRMED

**`Laying_Dim_HM.mp4` and `Behind_Bed_HM.mp4` are held back from ALL training,
kept purely as evaluation.** Both are being fully hand-labeled (so they carry
real ground truth for scoring) but must never be passed to
`build_merged_dataset.py` / `generate_bbox_dataset.py --extra_clip` — the same
reasoning `laying_dim.MOV` (the *other* clip, in `held_out/` directly, from
round 6's diagnostic — not to be confused with this batch's `Laying_Dim_HM.mp4`)
was protected for: a clip no model has trained on is the only way to tell "v7
actually got better at the hard case" from "v7 fit the new labels."

Everything else in this batch (auto-label tier, patch tier, and
`Behind_Chair_HM` / `Blanket_Cover_HM` from the full-hand-label tier) is
available for training once labeled.

**Enforcement note:** nothing in `footage_paths.py` currently distinguishes
"triaged, approved for training" clips from "triaged, held back for eval"
within the same folder — both look identical to `is_protected()`. Whoever
runs round 7 must apply this by hand (never pass `Laying_Dim_HM.mp4` or
`Behind_Bed_HM.mp4` via `--extra_clip`), not by moving files, since moving
files back and forth is exactly the kind of manual bookkeeping this project's
`held_out/` guard was built to replace with a hard refusal. Worth a
`--extra_clip` allowlist check if this pattern repeats in round 8.

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
- **Full hand-label** (4 clips: Blanket_Cover_HM, Behind_Bed_HM,
  Laying_Dim_HM, Behind_Chair_HM): `sample_heldout_frames.py` →
  `handlabels/round6/images/` (619 frames total, stride 10), `labels/` empty
  and ready, `classes.txt` matching SAGE_CLASSES. Labeling is now complete
  (verified against `handlabels.py`'s own loader) and the folder has since
  been split by hold-back status — see below.
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

## Hold-back decision — CONFIRMED, and now structural

**`Laying_Dim_HM.mp4` and `Behind_Bed_HM.mp4` are held back from ALL training,
kept purely as evaluation.** Both are fully hand-labeled (so they carry real
ground truth for scoring) but must never reach a training merge — the same
reasoning `laying_dim.MOV` (the *other* clip, in `held_out/` directly, from
round 6's diagnostic — not to be confused with this batch's `Laying_Dim_HM.mp4`)
was protected for: a clip no model has trained on is the only way to tell "v7
actually got better at the hard case" from "v7 fit the new labels."

Labeling is now done, and `handlabels.py`'s own guard turns "must never reach
a training merge" into something enforceable rather than a rule to remember:
`generate_bbox_dataset.py` hard-errors if a `--handlabels_dir` contains labels
for a clip not also passed via `--extra_clip` ("Hand labels reference clip(s)
not in this run"). Originally all four full-hand-label clips lived in one
`handlabels/round6/`, which would have forced a future round-7 run to either
include the held-back pair or crash. **Split after labeling finished:**

- `handlabels/round6/` — **trainable**: `Blanket_Cover_HM` (152 frames),
  `Behind_Chair_HM` (169 frames). 321 frames, 321 person boxes.
- `handlabels/round6_heldout/` — **eval-only, never pass to `--extra_clip`**:
  `Laying_Dim_HM` (153 frames), `Behind_Bed_HM` (145 frames). 298 frames,
  226 person boxes (Behind_Bed_HM has only 73/145 — plausible for an occlusion
  clip where the person is fully hidden behind the bed on some frames, not a
  labeling gap).
- `handlabels/round6_patch/` — **trainable, patch-only**: `Standing_Walking_Dim_HM`
  (173 frames), `Sitting_Dim_HM` (211 frames). 384 frames, 384 person boxes.

A round-7 run can now safely point `--handlabels_dir` at `round6/` and
`round6_patch/` (with the matching clips in `--extra_clip`, patch clips
**without** `--handlabels_only` per the note above) and the held-back pair is
physically absent from both — no allowlist to remember, no way to include
them by accident short of also pointing `--handlabels_dir` at
`round6_heldout/` directly, which is a deliberate act with its own clip in
`--extra_clip` to match.

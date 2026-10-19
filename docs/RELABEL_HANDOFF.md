# Re-labelling handoff: `round6_heldout` (298 frames)

Read this page and `docs/LABELLING_SPEC.md` (v0.1 draft) before you start. If anything below is unclear, ask Hussain. Do not guess.

## Why this job exists
`round6_heldout` is the yardstick we score every person detector against. Its boxes were drawn without a written rule, so some boxes sit on the visible person, some on the hidden part, and some on near-black areas nobody can verify. If the yardstick is inconsistent, the scores mean nothing. Your job is to make every frame follow the one spec.

## What "done" looks like
1. A corrected label file for each of the 298 frames, person boxes following the spec.
2. `review_sheet.csv` filled in for each of the 298 frames.
3. The original `handlabels/round6_heldout/` untouched. It is the record of what the models were scored on before the fix.

## The set
- 298 frames, 2 clips.
- `Behind_Bed_HM`: 145 frames. 73 have one person box, **72 have no person box**. Frames are 10 apart (`..._000010`, `..._000020`).
- `Laying_Dim_HM`: 153 frames, all with one person box. Mean luma is about 65 of 255, so these are dark. The viewer shows a brightened panel next to each one.
- Check the 72 no-box frames too. Either nobody is there (correct) or a box is missing.
- The frames show identifiable people. Keep them on the team's machines.

## Per frame
1. Open the frame in `review_pack/index.html`. Use the brightened panel for dark frames.
2. Ask: **can I identify a person here?** Missing toes or feet do not matter. The box ends where the visible person ends.
3. Decide, and fill `box_fits_spec` (these meanings are my proposal, confirm with Hussain):
   - `yes`: the existing box already follows the spec. Leave it.
   - `fix`: the box was wrong and you redrew it.
   - `no_person`: no person can be identified. Delete the person box.
   - `no`: the box does not follow the spec and you could not fix it. Also set `unsure=1`.
4. Fill the tags in `review_sheet.csv`:
   - `occ`: `none`, `partial`, or `heavy` (heavy = less than about half the body visible).
   - `cover`: `blanket` if the person is under a blanket, else `none`.
   - `lowlight`: 1 where `brightened_shown` is 1.
   - `unsure`: 1 if you cannot decide. Unsure frames are left out of scoring. Write why in `notes`.
5. Change **person boxes only**. Leave furniture boxes as they are. Never change class order or add classes.

## Rules that are easy to get wrong
- Do not run any model first and then correct its boxes. Do not look at model predictions while you label. That would bias the yardstick toward the model.
- Do not copy a box from the previous frame unless the person is clearly not moving. Check every frame anyway.
- A rumpled blanket on an empty bed gets no box. A blanket over a person you can see going under it keeps a box (`cover=blanket`).
- Do not edit the training sets (`round5`, `round6`, `round6_patch`). This job is `round6_heldout` only.

## Calibration (do this first)
You and Hussain each label the same 20 frames independently, then compare. Resolve every disagreement and write the answer into the spec. Then do the rest.

## Tool
Pick one route. Hussain tells you which.

**Local (no consent needed).** Work on a COPY of `benchmarks/phase3_a2/roboflow/upload_heldout/` (298 images, 298 YOLO label files, `data.yaml`). Save corrected labels to a new folder, not over the originals. A frame with no boxes at all must have an empty `.txt` file, not a missing one, because the scorer treats a missing file as "not labelled" and drops the frame. I have not checked which local tool (CVAT, labelImg, or another) works best.

**Roboflow (only if all of these hold).**
- The project is Private, confirmed in the UI.
- The data-use opt-out is on.
- Everyone visible in the frames agreed.
- You use your own login or an invite. Never paste an API key into chat or a file. Follow `benchmarks/phase3_a2/roboflow/ROBOFLOW_SETUP.md`. If you cannot confirm Private, stop and tell Hussain.

## Hand back
- Corrected labels (298 files) and the filled `review_sheet.csv`.
- Tell Hussain how long the first 20 frames took. He uses it to plan the rest.
- Hussain verifies the export (class order, counts, sizes) and runs the re-score. Do not use your own labels for scoring before that check.

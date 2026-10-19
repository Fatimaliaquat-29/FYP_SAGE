# v7 — training and eval results

Trained overnight, unattended, on the user's own machine (RTX 4050 Laptop, 6GB
VRAM) while they slept. 30 epochs, imgsz 640, stock `yolov8n.pt` base,
`--workers 0` (see below for why). **3.332 hours actual wall time** — close to
the 3.1h estimate from the pre-training benchmark.

Dataset: `datasets/sage_merged_v7/` — 17,653 images, 60,885 boxes (v6: 13,793 /
52,867). Full composition and the pinned-base / two-run build process are in
the prior turns of this session; not repeated here.

## One crash, self-recovered

The first training attempt crashed before reaching the GPU: Ultralytics'
default 8 DataLoader workers each need to reload torch's CUDA DLLs as a fresh
subprocess on Windows, and under this machine's tight memory that reload
failed (`WinError 1455`, paging file too small) -- the same failure mode hit
twice earlier in this session. Worse, Ultralytics respawned a new worker on
each failure instead of aborting, which piled up 13 stuck zombie processes and
made the memory pressure worse, not better. Killed the tree, added a
`--workers` flag to `finetune_person.py`, reran at `--workers 0` (loader in
the main process, no subprocess DLL reloads). The full 30-epoch run then
completed with no further issues -- confirmed by grepping the entire log for
`Traceback`/`Error`: none found outside the one fixed crash.

Weights: `models/yolov8n_sage_merged_v7.pt` (copied from
`runs/detect/runs/detect/v7_full_train/weights/best.pt`).

## Headline: person recall on the hard cases did NOT move

This is the number every prior round has tracked, same script, same clips:

| clip (IoU 0.5) | boxes | v5 | v6 | v7 |
|---|---|---|---|---|
| **TV_Lounge_1_Fall** | 18 | 6/18 (0.33) | 6/18 (0.33) | **6/18 (0.33)** |
| **Bedroom_Fall** | 20 | 0/20 (0.00) | 0/20 (0.00) | **0/20 (0.00)** |
| Bedroom_Sit | 24 | 21/24 (0.88) | 23/24 (0.96) | 21/24 (0.88) |
| Bedroom_Walk | 14 | 14/14 | 14/14 | 14/14 |
| TV_Lounge_1_Sit | 16 | 16/16 | 16/16 | 16/16 (1 FP) |
| TV_Lounge_1_Walk | 1 | 1/1 | 1/1 | 1/1 |
| **overall** | 93 | 58/93 (0.62), 6 FP | 60/93 (0.65), 4 FP | **58/93 (0.62), 1 FP** |

IoU 0.3 gives identical TV_Lounge_1_Fall / Bedroom_Fall numbers -- not a
threshold artifact, these are genuine misses, not near-misses.

**v7 detects exactly the same fall frames v5 and v6 did, on exactly the two
clips this whole project has used as its hardest fall benchmark.** All three
model versions are stuck at 33% on TV_Lounge_1_Fall and 0% on Bedroom_Fall.
What v7 *did* buy on this eval set is precision: 1 false positive vs v6's 4
and v5's 6, and it also regressed slightly vs v6 on Bedroom_Sit (21/24 vs
23/24) -- a small step back on an easy clip alongside no step forward on the
hard ones.

## The real test: round6_heldout (Laying_Dim_HM + Behind_Bed_HM, never trained on)

This is the clip pair held back specifically to answer "did v7 actually get
better at the hard case, or just fit the new labels" -- see
`docs/HAMMAD_CLIPS_ROUND6.md`. 298 frames, 967 hand-drawn boxes, at IoU 0.5:

| class | n | v5 | v6 | v7 |
|---|---|---|---|---|
| **person** | 226 | R 0.21 (47tp/3fp) | R 0.22 (49tp/2fp) | **R 0.22 (50tp/0fp)** |
| chair | 443 | R 0.31 (0 fp) | R 0.11 (regressed) | **R 0.74 (2 fp)** |
| bed | 298 | R 0.00 | R 0.01 | **R 0.49 (0 fp)** |

**Same story as the main gate: person recall is flat (0.21 -> 0.22 -> 0.22,
within noise) on the exact dark/occluded condition round 5 and round 6 were
both recorded to fix.** Precision improved to perfect (0 FP) but that is a
conservative model, not a more capable one, on this axis.

**But furniture detection in this same dark/occluded footage improved a lot.**
Chair recall goes from v6's regressed 0.11 to 0.74 -- more than double v5's
0.31. Bed recall goes from essentially 0 (v5: 0%, v6: 1%) to 0.49, with zero
false positives either version. This is a real, substantial win, just not the
one the round was aimed at: the new Hammad footage clearly taught the model
what chairs and beds look like in dark, cluttered rooms, but did not teach it
to find a *person* in those same rooms any better than before.

## General set (eval/heldout_objects) and empty-room FP -- no regressions

- **Empty-room false positives: 0.00% for v5, v6, and v7**, every clip, 4,101
  frames, conf 0.4 imgsz 640. Clean across the board.
- Couch: v7 roughly matches v6 (its own best round), both clearly ahead of
  v5.
- Bed on this GENERAL set (not the dark held-back clips): v5 R=0.72, v6
  R=0.17 (v6's regression), v7 R=0.40 -- partial recovery, still below v5.
  Notably different from round6_heldout's story, where v7 was the clear best
  on bed. The furniture gain is concentrated in dark/occluded conditions
  resembling the new training footage, not a general improvement.
- Chair stayed flat at R=0.20 across all three on the general set -- confirms
  the round6_heldout chair jump is condition-specific, not a broad fix.
- `dining table` picked up a handful of real detections in v7 (8 tp,
  P=0.89) vs 0/0 for v5 and v6 -- still mostly the labeling-taxonomy issue
  flagged earlier (coffee tables hand-labelled as dining table), not
  meaningfully fixed.

Full tables: `v7_suite_iou0.5.md`, `v7_suite_iou0.3.md` (same directory).

## Bottom line -- not a clear "ship v7" call

**Do not deploy v7 over v6 for the fall-detection mission specifically** --
it did not move the needle on the two hardest, most-tracked fall clips, on
the main gate or on the dedicated held-back eval built to test exactly this.
Precision improved and false positives dropped, which has real value, but the
core question ("does this version see a fallen person in a dark, occluded
room better than the last one") comes back "no" on every test that asks it
directly.

**Furniture/scene detection in dark, occluded conditions is a genuine win**
and may be worth keeping for that reason alone, independent of the
fall-detection question -- chair and bed recall in exactly the hard-case
lighting round 6 targeted roughly doubled or more, at equal-or-better
precision.

This is the same shape of result as v6 vs v5: real gains on a secondary axis,
flat on the primary one. Worth treating round 6's Hammad footage as
confirmation that *this kind of data collection helps furniture, not
person-in-hard-pose* -- which narrows what a round 8 needs to do
differently, the same way round 5's result narrowed round 6.

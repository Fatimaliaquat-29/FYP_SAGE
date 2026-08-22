# What MediaPipe misses — medium-coverage Hammad clips

Read-only investigation, no labels written. Per-frame VIDEO-mode tracking; a miss run is a maximal contiguous stretch of frames with no usable pose box.

| clip | frames | missed | miss runs | shortest run | longest run | mean run |
|---|---|---|---|---|---|---|
| Standing_Walking_Dim_HM.mp4 | 1330 | 173 (13.0%) | 33 | 1 | 38 (1.3s)| 5.2 |
| Sitting_Dim_HM.mp4 | 1507 | 211 (14.0%) | 55 | 1 | 33 (1.1s)| 3.8 |
| Behind_Chair_HM.mp4 | 1697 | 560 (33.0%) | 42 | 1 | 136 (4.5s)| 13.3 |

Many short runs (mean close to 1-2 frames) = scattered flicker, isolated failures within an otherwise-tracked clip -- patchable with a handful of hand-drawn boxes.
Few long runs = the person is being lost entirely for a stretch (occlusion, tracker losing the ROI) -- that stretch needs full hand-labeling, not a patch.

Sampled missed frames (raw, no boxes -- there is nothing to draw) are saved per clip, named `<clip>_<frame>_run<N>.jpg` so frames from the same dropout are identifiable as a group rather than looking like independent failures.

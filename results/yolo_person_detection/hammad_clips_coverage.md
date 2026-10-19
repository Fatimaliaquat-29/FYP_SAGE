# MediaPipe VIDEO-mode coverage — Hammad Clips (held_out/, untriaged)

10 clips, every frame (no stride), min_visibility=0.3.
`pose_coverage` = frames where MediaPipe found a person at all.
`bbox_coverage` = frames where enough of those landmarks clear min_visibility to form a usable auto-label box (what generate_bbox_dataset.py would actually write).

| clip | rotation | frames | pose coverage | usable bbox coverage |
|---|---|---|---|---|
| Laying_Dim_HM.mp4 | none | 1534 | 12.5% | 12.5% |
| BehindFurniture_HM.mp4 | none | 1455 | 36.6% | 36.6% |
| Blanket_Cover_HM.mp4 | none | 1520 | 55.5% | 55.5% |
| Behind_Furniture_HM.mp4 | none | 1697 | 67.0% | 67.0% |
| Sitting_Dim_HM.mp4 | none | 1507 | 86.0% | 86.0% |
| Standing_Walking_Dim_HM.mp4 | none | 1330 | 87.0% | 87.0% |
| PartiallyCovered_HM.mp4 | none | 977 | 95.5% | 95.5% |
| LyingDown_HM.mp4 | none | 1377 | 100.0% | 100.0% |
| Sitting_Chair_HM.mp4 | none | 1403 | 100.0% | 100.0% |
| Standing_Walking_HM.mp4 | none | 1632 | 100.0% | 100.0% |

## Reading this

High bbox coverage (roughly 80%+, in line with this project's easier clips) -- auto-labeling + spot-check is plausible.
Low coverage (well under that, in line with dim/occluded clips elsewhere in this project) -- MediaPipe's own detector is failing on these frames, which is exactly the condition full hand-labeling exists for; auto-labeling would silently under-represent them, same failure mode documented for TV_Lounge_1_Fall and laying_dim.MOV.

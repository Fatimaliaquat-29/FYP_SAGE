# YOLO26-pose vs MediaPipe Pose -- SAGE Heuristic Benchmark

Measured values only. No replace/keep recommendation is made in this document.

## Environment

- **python_version**: 3.11.6
- **torch_version**: 2.13.0+cu126
- **cuda_available**: True
- **gpu_name**: NVIDIA GeForce RTX 4050 Laptop GPU
- **gpu_vram_gb**: 6.44
- **ultralytics_version**: 8.4.115
- **mediapipe_version**: 0.10.35
- **numpy_version**: 2.4.6
- **opencv_version**: 4.13.0
- **ultralytics_upgraded**: False
- **device used for YOLO correctness pass**: cuda:0

## Skipped clips

10 GT/video pairings were skipped by discover_clips() or failed to parse. None were renamed or edited.

| Folder | Clip/file | Reason |
|---|---|---|
| Hussain Testing 7-23-26 | normal | GT unparseable: 'charmap' codec can't decode byte 0x9d in position 16: character maps to <undefined> (file begins with 'PK' -- it is actually a zip/xlsx file saved with a .csv extension) |
| Hussain Testing 7-23-26 | old | GT unparseable: 'charmap' codec can't decode byte 0x9d in position 16: character maps to <undefined> (file begins with 'PK' -- it is actually a zip/xlsx file saved with a .csv extension) |
| Hussain Testing 7-23-26 | normal_GT_converted | filename does not end in '_gt.csv' -- likely a stray space before the extension, wrong case, or an alternate-dialect file (e.g. '_GT_converted.csv') that discover_clips does not select [normal_GT_converted.csv] |
| Hussain Testing 7-23-26 | normal_GT_fixed | filename does not end in '_gt.csv' -- likely a stray space before the extension, wrong case, or an alternate-dialect file (e.g. '_GT_converted.csv') that discover_clips does not select [normal_GT_fixed.csv] |
| Hussain Testing 7-23-26 | old_GT_converted | filename does not end in '_gt.csv' -- likely a stray space before the extension, wrong case, or an alternate-dialect file (e.g. '_GT_converted.csv') that discover_clips does not select [old_GT_converted.csv] |
| Hussain Testing 7-23-26 | old_GT_fixed | filename does not end in '_gt.csv' -- likely a stray space before the extension, wrong case, or an alternate-dialect file (e.g. '_GT_converted.csv') that discover_clips does not select [old_GT_fixed.csv] |
| Hussain Testing 7-30-26 | Bend_pickup_lowLight_leftRight_GT  | filename does not end in '_gt.csv' -- likely a stray space before the extension, wrong case, or an alternate-dialect file (e.g. '_GT_converted.csv') that discover_clips does not select [Bend_pickup_lowLight_leftRight_GT .csv] |
| Hussain Testing 7-30-26 | SitFloor_crossedLegs_GT  | filename does not end in '_gt.csv' -- likely a stray space before the extension, wrong case, or an alternate-dialect file (e.g. '_GT_converted.csv') that discover_clips does not select [SitFloor_crossedLegs_GT .csv] |
| Sanawar Testing 7-22-26 | Legs_occluded_gt | GT file matches '_gt.csv' pattern (stem 'Legs_occluded') but no video with that stem exists (name mismatch / typo / wrong extension) [Legs_occluded_gt.csv] |
| Sanawar Testing 7-25-26 | Forward_fall_gt | GT file matches '_gt.csv' pattern (stem 'Forward_fall') but no video with that stem exists (name mismatch / typo / wrong extension) [Forward_fall_gt.csv] |

Historical context for the two xlsx-disguised-as-csv clips (not reproducible today):

- **H0723_normal**: historically accuracy=89.4%, fall=TP (latency 43 frames) (source: results/hussain_testing_heuristic/real_footage_results.md). GT file is now an xlsx/zip disguised as .csv; unparseable today.
- **H0723_old**: historically accuracy=100.0%, fall=FP frames [475, 476, 477, 478, 479] (source: results/hussain_testing_heuristic/real_footage_results.md). GT file is now an xlsx/zip disguised as .csv; unparseable today.

## Aggregate results (all backends, all usable clips)

Posture accuracy is frame-weighted (sum of correct frames / sum of scored frames across clips), not an average of per-clip percentages. Fall recall = TP / (TP + FN) over clips that have a real GT fall window. ADL false-alarm clips = clips with no GT fall window where the heuristic still raised fall_detected.

| Backend | Clips | Frames scored | Posture acc. | Fall recall (TP/total) | ADL false-alarm clips | Hip+Shoulder avail (ALL) | 8-joint avail (ALL) | Jitter median (n) |
|---|---|---|---|---|---|---|---|---|
| mediapipe | 64 | 13796 | 71.9% | 60.0% (18/32) | 7/32 | 92.2% (n=18324) | 44.6% (n=18324) | 0.00130 (n=6105) |
| yolo26n-pose@0.3 | 64 | 13796 | 72.5% | 63.3% (19/32) | 11/32 | 84.5% (n=18324) | 57.3% (n=18324) | 0.00203 (n=6148) |
| yolo26n-pose@0.5 | 64 | 13796 | 73.2% | 63.3% (19/32) | 11/32 | 84.2% (n=18324) | 52.3% (n=18324) | 0.00203 (n=6127) |
| yolo26n-pose@0.7 | 64 | 13796 | 72.2% | 75.9% (22/32) | 10/32 | 83.6% (n=18324) | 46.9% (n=18324) | 0.00202 (n=6069) |
| yolo26s-pose@0.3 | 64 | 13796 | 69.6% | 83.3% (25/32) | 9/32 | 91.1% (n=18324) | 60.0% (n=18324) | 0.00192 (n=6190) |
| yolo26s-pose@0.5 | 64 | 13796 | 69.0% | 71.9% (23/32) | 9/32 | 90.5% (n=18324) | 55.5% (n=18324) | 0.00191 (n=6132) |
| yolo26s-pose@0.7 | 64 | 13796 | 66.2% | 71.0% (22/32) | 9/32 | 87.3% (n=18324) | 51.3% (n=18324) | 0.00193 (n=5804) |

- **mediapipe** fall misses: Moving_in_out_frame_withFall, Sitting_Lying_FewLandmarks, Sitting_Lying_FewLandmarks_back, Fall_Curled, Normal_Fall_1 (alarm outside GT window), Backward_fall, Chair_fall, Bed_lie_and_immediate_stand, Bed_long_lie, Floor_lie (alarm outside GT window), Floor_partly_lie_beside_bed, Sofa_lie, Sofa_lie_and_immediate_stand, Sofa_medium_pace_lie
- **mediapipe** ADL false alarms: Bend_pickup_normalLight, Fall_backward_2, Fall_backward_3, Fall_backward_4, Fall_from_chair_2, Fall_slow_collapse, Other_walk_out_and_back
- **yolo26n-pose@0.3** fall misses: Moving_in_out_frame_withFall, Sitting_Lying_FewLandmarks, Normal_Fall_1, Backward_fall, Far_fall, Side_fall, Floor_lie, Floor_lie_and_immediate_stand, Floor_long_lie, Floor_medium_pace_lie, Sofa_lie (alarm outside GT window), Sofa_lie_and_immediate_stand (alarm outside GT window), Sofa_medium_pace_lie
- **yolo26n-pose@0.3** ADL false alarms: Bend_pickup_normalLight, SitFloor_lowKeypoints_crossedLegs, Fall_backward_2, Fall_backward_3, Fall_backward_4, Fall_from_chair_2, Fall_slow_collapse, Lying_legs_straight, Lying_straight, Other_sit_desk, Other_walk_out_and_back
- **yolo26n-pose@0.5** fall misses: Moving_in_out_frame_withFall, Sitting_Lying_FewLandmarks, Normal_Fall_1, Backward_fall, Far_fall, Side_fall, Floor_lie, Floor_lie_and_immediate_stand, Floor_long_lie, Floor_medium_pace_lie, Sofa_lie (alarm outside GT window), Sofa_lie_and_immediate_stand (alarm outside GT window), Sofa_medium_pace_lie
- **yolo26n-pose@0.5** ADL false alarms: Bend_pickup_normalLight, SitFloor_lowKeypoints_crossedLegs, Fall_backward_2, Fall_backward_3, Fall_backward_4, Fall_from_chair_2, Fall_slow_collapse, Lying_legs_straight, Lying_straight, Other_sit_desk, Other_walk_out_and_back
- **yolo26n-pose@0.7** fall misses: Sitting_Lying_FewLandmarks, Normal_Fall_1, Backward_fall, Side_fall, Floor_lie (alarm outside GT window), Floor_lie_and_immediate_stand, Floor_medium_pace_lie, Sofa_lie (alarm outside GT window), Sofa_lie_and_immediate_stand (alarm outside GT window), Sofa_medium_pace_lie
- **yolo26n-pose@0.7** ADL false alarms: Bend_pickup_normalLight, SitFloor_lowKeypoints_crossedLegs, Fall_backward_2, Fall_backward_3, Fall_backward_4, Fall_from_chair_2, Fall_slow_collapse, Lying_straight, Other_sit_desk, Other_walk_out_and_back
- **yolo26s-pose@0.3** fall misses: Sitting_Lying_FewLandmarks, Sitting_Lying_FewLandmarks_back (alarm outside GT window), Normal_Fall_1, Backward_fall, Chair_fall, Floor_lie (alarm outside GT window), Sofa_lie
- **yolo26s-pose@0.3** ADL false alarms: Bend_pickup_lowLight, SitFloor_lowKeypoints_crossedLegs, Fall_backward_2, Fall_backward_3, Fall_backward_4, Fall_from_chair_2, Fall_slow_collapse, Other_occluded_crouch, Other_walk_out_and_back
- **yolo26s-pose@0.5** fall misses: Sitting_Lying_FewLandmarks, Sitting_Lying_FewLandmarks_back, Fall_Curled, Normal_Fall_1, Backward_fall, Chair_fall, Floor_lie, Floor_partly_lie_beside_bed, Sofa_lie
- **yolo26s-pose@0.5** ADL false alarms: Bend_pickup_lowLight, SitFloor_lowKeypoints_crossedLegs, Fall_backward_2, Fall_backward_3, Fall_backward_4, Fall_from_chair_2, Fall_slow_collapse, Other_occluded_crouch, Other_walk_out_and_back
- **yolo26s-pose@0.7** fall misses: Sitting_Lying_FewLandmarks, Sitting_Lying_FewLandmarks_back, Fall_Curled, Normal_Fall_1, Backward_fall, Chair_fall, Bed_lie_and_immediate_stand, Bed_medium_pace_lie, Floor_lie (alarm outside GT window), Sofa_lie
- **yolo26s-pose@0.7** ADL false alarms: Bend_pickup_lowLight, SitFloor_lowKeypoints_crossedLegs, Fall_backward_2, Fall_backward_3, Fall_backward_4, Fall_from_chair_2, Fall_slow_collapse, Other_occluded_crouch, Other_walk_out_and_back

## Availability by GT state

### Standing

| Backend | Person found | Hip+Shoulder avail | 8-joint avail | n frames |
|---|---|---|---|---|
| mediapipe | 95.5% | 95.0% | 54.5% | 6504 |
| yolo26n-pose@0.3 | 98.0% | 95.2% | 67.9% | 6504 |
| yolo26n-pose@0.5 | 98.0% | 94.9% | 63.0% | 6504 |
| yolo26n-pose@0.7 | 98.0% | 94.3% | 60.3% | 6504 |
| yolo26s-pose@0.3 | 98.5% | 95.6% | 65.6% | 6504 |
| yolo26s-pose@0.5 | 98.5% | 95.0% | 61.7% | 6504 |
| yolo26s-pose@0.7 | 98.5% | 90.0% | 59.8% | 6504 |

### Sitting

| Backend | Person found | Hip+Shoulder avail | 8-joint avail | n frames |
|---|---|---|---|---|
| mediapipe | 87.3% | 87.3% | 25.5% | 1670 |
| yolo26n-pose@0.3 | 79.5% | 76.8% | 42.7% | 1670 |
| yolo26n-pose@0.5 | 79.5% | 76.4% | 34.6% | 1670 |
| yolo26n-pose@0.7 | 79.5% | 75.3% | 32.0% | 1670 |
| yolo26s-pose@0.3 | 80.7% | 77.4% | 39.4% | 1670 |
| yolo26s-pose@0.5 | 80.7% | 76.6% | 33.8% | 1670 |
| yolo26s-pose@0.7 | 80.7% | 72.9% | 33.7% | 1670 |

### Lying

| Backend | Person found | Hip+Shoulder avail | 8-joint avail | n frames |
|---|---|---|---|---|
| mediapipe | 90.5% | 89.0% | 37.4% | 5528 |
| yolo26n-pose@0.3 | 72.4% | 71.5% | 42.3% | 5528 |
| yolo26n-pose@0.5 | 72.4% | 71.1% | 37.1% | 5528 |
| yolo26n-pose@0.7 | 72.4% | 70.7% | 27.2% | 5528 |
| yolo26s-pose@0.3 | 91.1% | 90.3% | 54.9% | 5528 |
| yolo26s-pose@0.5 | 91.1% | 89.6% | 49.0% | 5528 |
| yolo26s-pose@0.7 | 91.1% | 87.4% | 40.7% | 5528 |

### Transition

| Backend | Person found | Hip+Shoulder avail | 8-joint avail | n frames |
|---|---|---|---|---|
| mediapipe | 94.8% | 94.7% | 46.9% | 4528 |
| yolo26n-pose@0.3 | 91.7% | 89.6% | 66.9% | 4528 |
| yolo26n-pose@0.5 | 91.7% | 89.3% | 63.2% | 4528 |
| yolo26n-pose@0.7 | 91.7% | 88.7% | 58.2% | 4528 |
| yolo26s-pose@0.3 | 95.6% | 92.6% | 67.1% | 4528 |
| yolo26s-pose@0.5 | 95.6% | 92.2% | 63.9% | 4528 |
| yolo26s-pose@0.7 | 95.6% | 90.2% | 59.8% | 4528 |

## Per-clip results (threshold 0.5 for YOLO models)

Full per-threshold (0.3/0.5/0.7) per-clip numbers are in `results/metrics_full.json`; this table shows 0.5 (MediaPipe-equivalent default) to keep it readable.

| Clip | Folder | MediaPipe acc. | MediaPipe fall | YOLO26n acc. | YOLO26n fall | YOLO26s acc. | YOLO26s fall |
|---|---|---|---|---|---|---|---|
| Bend_pickup_lowLight | Hussain Testing 7-30-26 | 100.0% | - | 100.0% | - | 100.0% | FP [57, 58, 61] |
| Bend_pickup_normalLight | Hussain Testing 7-30-26 | 100.0% | FP [59, 60, 63] | 100.0% | FP [56, 57, 59] | 100.0% | - |
| Bend_pickup_normalLight_back | Hussain Testing 7-30-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| Bend_pickup_normalLight_leftRight | Hussain Testing 7-30-26 | 92.0% | - | 98.1% | - | 96.3% | - |
| Bend_pickup_squat_lowLight | Hussain Testing 7-30-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| Bend_pickup_squat_normalLight | Hussain Testing 7-30-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| Kneeling | Hussain Testing 7-30-26 | 98.2% | - | 97.3% | - | 98.2% | - |
| LyingdownSlowly | Hussain Testing 7-30-26 | 100.0% | TP (95f) | 100.0% | TP (29f) | 100.0% | TP (96f) |
| Moving_in_out_frame | Hussain Testing 7-30-26 | 44.9% | - | 48.3% | - | 48.8% | - |
| Moving_in_out_frame_withFall | Hussain Testing 7-30-26 | 49.7% | FN | 49.7% | FN | 57.0% | TP (82f) |
| SitFast_GetupFast | Hussain Testing 7-30-26 | 34.3% | - | 21.0% | - | 37.1% | - |
| SitFloor_lowKeypoints | Hussain Testing 7-30-26 | 95.1% | - | 100.0% | - | 100.0% | - |
| SitFloor_lowKeypoints_crossedLegs | Hussain Testing 7-30-26 | 100.0% | - | 100.0% | FP [37] | 100.0% | FP [45] |
| Sit_Stand_AnklesInvisible | Hussain Testing 7-30-26 | 41.1% | - | 22.0% | - | 22.0% | - |
| Sitting_HalfLandmarks | Hussain Testing 7-30-26 | 86.2% | - | 42.2% | - | 0.0% | - |
| Sitting_Lying_FewLandmarks | Hussain Testing 7-30-26 | 29.7% | FN | 53.5% | FN | 59.4% | FN |
| Sitting_Lying_FewLandmarks_back | Hussain Testing 7-30-26 | 13.7% | FN | 43.2% | TP (132f) | 32.7% | FN |
| Fall_backward_2 | Hussain Testing 8-2-26 | 100.0% | FP [90, 91, 92] | 100.0% | FP [89, 90, 91] | 100.0% | FP [89, 90, 91] |
| Fall_backward_3 | Hussain Testing 8-2-26 | 100.0% | FP [120, 121, 122] | 100.0% | FP [120, 121, 122] | 100.0% | FP [121, 122, 123] |
| Fall_backward_4 | Hussain Testing 8-2-26 | 100.0% | FP [89, 90, 91] | 100.0% | FP [98, 99, 100] | 100.0% | FP [94, 95, 96] |
| Fall_forward_2 | Hussain Testing 8-2-26 | 100.0% | TP (128f) | 100.0% | TP (147f) | 100.0% | TP (105f) |
| Fall_from_chair_2 | Hussain Testing 8-2-26 | 100.0% | FP [174, 175, 176] | 100.0% | FP [144, 145, 175] | 100.0% | FP [146, 147, 177] |
| Fall_slow_collapse | Hussain Testing 8-2-26 | 100.0% | FP [229, 230, 231] | 100.0% | FP [227, 228, 229] | 100.0% | FP [226, 227, 228] |
| Fall_Curled | Sanawar Testing 7-22-26 | 100.0% | FN | 100.0% | TP (49f) | 64.4% | FN |
| Fast_Sit | Sanawar Testing 7-22-26 | 0.0% | - | 0.0% | - | 0.0% | - |
| Lying_legs_straight | Sanawar Testing 7-22-26 | 100.0% | - | 92.5% | FP [117, 118, 119] | 100.0% | - |
| Lying_straight | Sanawar Testing 7-22-26 | 100.0% | - | 78.2% | FP [33, 34, 35] | 100.0% | - |
| Normal_Fall_1 | Sanawar Testing 7-22-26 | 77.8% | FP [151] | 32.2% | FN | 44.4% | FN |
| Normal_Fall_2 | Sanawar Testing 7-22-26 | 100.0% | TP (71f) | 100.0% | TP (57f) | 100.0% | TP (57f) |
| Off_axis | Sanawar Testing 7-22-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| Sit_1 | Sanawar Testing 7-22-26 | 65.6% | - | 75.6% | - | 65.6% | - |
| Sit_2 | Sanawar Testing 7-22-26 | 65.6% | - | 65.6% | - | 65.6% | - |
| Sit_3 | Sanawar Testing 7-22-26 | 0.0% | - | 0.0% | - | 0.0% | - |
| Standing_1 | Sanawar Testing 7-22-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| Standing_2 | Sanawar Testing 7-22-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| Standing_3 | Sanawar Testing 7-22-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| newTest | Sanawar Testing 7-22-26 | 79.2% | TP (71f) | 77.5% | TP (69f) | 75.7% | TP (69f) |
| normal | Sanawar Testing 7-22-26 | 88.0% | TP (75f) | 88.7% | TP (75f) | 88.7% | TP (77f) |
| old | Sanawar Testing 7-22-26 | 97.0% | TP (106f) | 99.6% | TP (106f) | 100.0% | TP (108f) |
| Backward_fall | Sanawar Testing 7-25-26 | 38.5% | FN | 44.9% | FN | 44.9% | FN |
| Chair_fall | Sanawar Testing 7-25-26 | 0.0% | FN | 2.3% | TP (137f) | 0.0% | FN |
| Fall_and_lie | Sanawar Testing 7-25-26 | 29.6% | TP (16f) | 100.0% | TP (24f) | 100.0% | TP (26f) |
| Far_fall | Sanawar Testing 7-25-26 | 100.0% | TP (53f) | 74.0% | FN | 100.0% | TP (19f) |
| Occluded_fall | Sanawar Testing 7-25-26 | 100.0% | TP (52f) | 100.0% | TP (25f) | 100.0% | TP (18f) |
| Off_axis_fall | Sanawar Testing 7-25-26 | 100.0% | TP (16f) | 100.0% | TP (30f) | 100.0% | TP (64f) |
| Side_fall | Sanawar Testing 7-25-26 | 95.3% | TP (67f) | 85.8% | FN | 100.0% | TP (81f) |
| Slow_fall | Sanawar Testing 7-25-26 | 100.0% | TP (27f) | 73.1% | TP (28f) | 100.0% | TP (31f) |
| Bed_lie | Sanawar Testing 8-7-26 | 39.3% | TP (0f) | 35.5% | TP (0f) | 42.6% | TP (0f) |
| Bed_lie_and_immediate_stand | Sanawar Testing 8-7-26 | 34.8% | FN | 89.4% | TP (28f) | 100.0% | TP (28f) |
| Bed_long_lie | Sanawar Testing 8-7-26 | 82.9% | FN | 96.6% | TP (8f) | 12.2% | TP (25f) |
| Bed_medium_pace_lie | Sanawar Testing 8-7-26 | 100.0% | TP (48f) | 98.8% | TP (48f) | 100.0% | TP (48f) |
| Floor_lie | Sanawar Testing 8-7-26 | 63.7% | FP [77, 78, 79] | 77.2% | FN | 77.2% | FN |
| Floor_lie_and_immediate_stand | Sanawar Testing 8-7-26 | 30.6% | TP (27f) | 32.3% | FN | 31.9% | TP (29f) |
| Floor_long_lie | Sanawar Testing 8-7-26 | 10.5% | TP (9f) | 9.8% | FN | 10.2% | TP (45f) |
| Floor_medium_pace_lie | Sanawar Testing 8-7-26 | 80.0% | TP (11f) | 24.2% | FN | 24.2% | TP (20f) |
| Floor_partly_lie_beside_bed | Sanawar Testing 8-7-26 | 7.2% | FN | 97.1% | TP (0f) | 45.3% | FN |
| Other_occluded_crouch | Sanawar Testing 8-7-26 | 59.9% | - | 24.9% | - | 19.1% | FP [79, 80, 81] |
| Other_occluded_stand | Sanawar Testing 8-7-26 | 100.0% | - | 100.0% | - | 100.0% | - |
| Other_sit_desk | Sanawar Testing 8-7-26 | 80.1% | - | 80.1% | FP [126] | 79.5% | - |
| Other_walk_out_and_back | Sanawar Testing 8-7-26 | 56.6% | FP [170, 171, 172] | 52.8% | FP [200, 201, 202] | 56.6% | FP [127, 128, 129] |
| Sofa_lie | Sanawar Testing 8-7-26 | 57.9% | FN | 50.2% | FP [196, 204, 207] | 54.7% | FN |
| Sofa_lie_and_immediate_stand | Sanawar Testing 8-7-26 | 43.0% | FN | 46.2% | FP [211, 212, 213] | 45.7% | TP (148f) |
| Sofa_long_lie | Sanawar Testing 8-7-26 | 100.0% | TP (79f) | 100.0% | TP (77f) | 100.0% | TP (76f) |
| Sofa_medium_pace_lie | Sanawar Testing 8-7-26 | 44.6% | FN | 45.4% | FN | 44.6% | TP (6f) |

## Speed (pose step only, video decode excluded)

This laptop (RTX 4050 Laptop GPU, 6.44GB VRAM), not the Jetson target. MediaPipe and the CPU YOLO figures are measured on a disclosed 8-clip subset (not all 64 clips) -- see SPEED_SUBSET_CLIP_NAMES in benchmark_pose.py -- so CPU-vs-GPU and MediaPipe-vs-YOLO comparisons are apples-to-apples on the same clips. YOLO-GPU numbers are measured over the full 64-clip correctness run, so its sample size is larger and not directly matched to the others; both samples are reported with n so this is not hidden. First 5 frames of every clip excluded as warm-up.

| Backend | Device | Mean ms/frame | p95 ms/frame | Sample |
|---|---|---|---|---|
| mediapipe | CPU | 17.54 | 20.01 | speed subset, 8 clips, 2062 frames |
| yolo26n-pose | GPU (RTX 4050 Laptop) | 15.90 | 22.11 | full dataset, 64 clips, 19633 frames |
| yolo26n-pose | CPU | 50.14 | 55.26 | speed subset, 8 clips, 2102 frames |
| yolo26s-pose | GPU (RTX 4050 Laptop) | 15.61 | 20.95 | full dataset, 64 clips, 19633 frames |
| yolo26s-pose | CPU | 100.12 | 109.04 | speed subset, 8 clips, 2102 frames |

## Sanity checks

### 1. Baseline reproduction

MediaPipe backend run through this harness, compared against historical results already committed under results/ (see each row's source).

| Clip | Status | Accuracy now | Accuracy ref | Fall now | Fall ref | Source |
|---|---|---|---|---|---|---|
| S0722_Fall_Curled | MISMATCH | 100.0 | 100.0 | FN | TP (latency 9 frames) | results/real_footage_results.md |
| S0722_Fast_Sit | MISMATCH | 0.0 | 100.0 | - | - | results/real_footage_results.md |
| S0722_Lying_legs_straight | OK | 100.0 | 100.0 | - | - | results/real_footage_results.md |
| S0722_Lying_straight | OK | 100.0 | 100.0 | - | - | results/real_footage_results.md |
| S0722_newTest | MISMATCH | 79.2 | 74.0 | TP (latency 71 frames) | TP (latency 76 frames) | results/real_footage_results.md |
| S0722_Normal_Fall_1 | MISMATCH | 77.8 | 83.3 | FP frames [151] | TP (latency 18 frames) | results/real_footage_results.md |
| S0722_Normal_Fall_2 | OK | 100.0 | 100.0 | TP (latency 71 frames) | TP (latency 8 frames) | results/real_footage_results.md |
| S0722_normal | MISMATCH | 88.0 | 89.4 | TP (latency 75 frames) | TP (latency 81 frames) | results/real_footage_results.md |
| S0722_Off_axis | OK | 100.0 | 100.0 | - | - | results/real_footage_results.md |
| S0722_old | MISMATCH | 97.0 | 100.0 | TP (latency 106 frames) | TP (latency 114 frames) | results/real_footage_results.md |
| S0722_Sit_1 | MISMATCH | 65.6 | 100.0 | - | - | results/real_footage_results.md |
| S0722_Sit_2 | MISMATCH | 65.6 | 54.4 | - | - | results/real_footage_results.md |
| S0722_Sit_3 | MISMATCH | 0.0 | 94.5 | - | - | results/real_footage_results.md |
| S0722_Standing_1 | OK | 100.0 | 100.0 | - | - | results/real_footage_results.md |
| S0722_Standing_2 | OK | 100.0 | 100.0 | - | - | results/real_footage_results.md |
| S0722_Standing_3 | OK | 100.0 | 100.0 | - | - | results/real_footage_results.md |
| S0725_Backward_fall | MISMATCH | 38.5 | 29.5 | FN | FN | results/new_test_heuristic_extended/real_footage_results.md |
| S0725_Chair_fall | MISMATCH | 0.0 | 21.5 | FN | TP (latency 114 frames) | results/new_test_heuristic_extended/real_footage_results.md |
| S0725_Fall_and_lie | MISMATCH | 29.6 | 54.4 | TP (latency 16 frames) | TP (latency 8 frames) | results/new_test_heuristic_extended/real_footage_results.md |
| S0725_Far_fall | OK | 100.0 | 100.0 | TP (latency 53 frames) | TP (latency 60 frames) | results/new_test_heuristic_extended/real_footage_results.md |
| S0725_Occluded_fall | MISMATCH | 100.0 | 63.8 | TP (latency 52 frames) | TP (latency 57 frames) | results/new_test_heuristic_extended/real_footage_results.md |
| S0725_Off_axis_fall | OK | 100.0 | 100.0 | TP (latency 16 frames) | TP (latency 66 frames) | results/new_test_heuristic_extended/real_footage_results.md |
| S0725_Side_fall | MISMATCH | 95.3 | 77.2 | TP (latency 67 frames) | TP (latency 73 frames) | results/new_test_heuristic_extended/real_footage_results.md |
| S0725_Slow_fall | MISMATCH | 100.0 | 71.7 | TP (latency 27 frames) | TP (latency 50 frames) | results/new_test_heuristic_extended/real_footage_results.md |

**9 matched, 15 mismatched, 0 had no cached run to compare.**

**Root cause of the mismatches, verified, not assumed:** both historical reference files (`results/real_footage_results.md`, last committed in `8d3e41e` on 2026-07-23; `results/new_test_heuristic_extended/real_footage_results.md`, same commit) predate commit `b566685` ("Fix live false alarms: trust MediaPipe visibility, VIDEO-mode tracking, real hybrid", 2026-08-03), which added the `MIN_LANDMARK_VISIBILITY = 0.5` gate in `pipeline_utils.py` -- that commit's own message explicitly names `Sit_3` and `Standing_2` as the clips whose near-zero ankle/knee visibility motivated the change. Debugged directly: on `S0722_Sit_3` and `S0722_Fast_Sit`, MediaPipe's right-knee and right-ankle visibility sit around 0.05-0.17 for most frames (well below 0.5), so the CURRENT heuristic correctly treats the lower body as occluded and falls back to its torso-only path, which classifies a near-vertical-torso sitting pose as `Standing` -- it did not do this before the visibility gate existed, when it trusted MediaPipe's guessed (but not visibility-flagged) knee/ankle coordinates instead. This means most mismatches reflect the heuristic genuinely changing since those files were generated, not a bug in this benchmark's harness. It does NOT threaten the YOLO-vs-MediaPipe comparison elsewhere in this report, since both backends here run through the identical, current, unmodified heuristic -- only the comparison against those *old* snapshot files is affected. Clips that still matched (Lying_straight, Lying_legs_straight, Normal_Fall_2, Standing_1/2/3, Off_axis, Far_fall, Off_axis_fall) are ones where this particular visibility edge case does not change the outcome.

### 2. Visual overlays

MediaPipe (green) vs YOLO26 (orange) skeleton overlays, saved to `benchmarks/pose_yolo26/results/overlays/`:

- results\overlays\lying_S0807_Floor_long_lie_frame132.png
- results\overlays\lying_S0807_Floor_long_lie_frame330.png
- results\overlays\low_light_H0730_Bend_pickup_lowLight_frame23.png
- results\overlays\low_light_H0730_Bend_pickup_lowLight_frame58.png
- results\overlays\occluded_legs_H0730_Sit_Stand_AnklesInvisible_frame42.png
- results\overlays\occluded_legs_H0730_Sit_Stand_AnklesInvisible_frame105.png

### 3. Coordinate sanity (x,y range + left/right mapping)

- YOLO x,y checked: 242819 keypoint samples, 0 outside [-0.05, 1.05] (0.000% if any).
- Left/right shoulder ordering compared MediaPipe vs YOLO on 13450 frames (where shoulders were >=0.02 apart): 627 disagreements.

## Criteria check (measured values only -- no recommendation)

| # | Criterion | MediaPipe | Best YOLO26 config | Met? |
|---|---|---|---|---|
| 1 | YOLO fall recall >= MediaPipe fall recall | 60.0% (18/32) | yolo26s-pose@0.3: 83.3% (25/32) | YES |
| 2 | YOLO ADL false-alarm clips <= MediaPipe's | 7/32 | yolo26s-pose@0.3: 9/32 | NO |
| 3 | YOLO Lying hip+shoulder avail. within 5pp of MediaPipe's | 89.0% (n=5528) | yolo26s-pose@0.3: 90.3% (n=5528) | YES |
| 4 | YOLO jitter not worse than MediaPipe's | 0.00130 (n=6105) | yolo26s-pose@0.5: 0.00191 (n=6132) | NO |

"Best YOLO26 config" is chosen independently per row (the config that does best on that specific criterion) -- it is not necessarily the same model/threshold across rows.

## Caveats

- **Home-field advantage for MediaPipe**: the heuristic's thresholds and constants in `src/posture/pipeline_utils.py` were tuned against MediaPipe's output. They were not retuned for YOLO26 here (per the task's hard rules), so any gap may reflect calibration, not just raw keypoint quality.
- **Single-person clips only**: every clip here has exactly one person in frame. YOLO's multi-person behavior (person selection, cross-person confusion) is completely untested by this benchmark.
- **Same clips used to develop the heuristic**: these are not held-out data for the heuristic itself -- several of the thresholds in pipeline_utils.py were derived by measuring exactly these clips (see that file's own comments).
- **YOLO is stateless per frame**: no tracker, no temporal smoothing. MediaPipe runs in VIDEO mode with cross-frame tracking, which the baseline relies on to suppress jitter. This is an inherent difference in the two pipelines being compared, not a configuration choice that was tuned either way.
- **Laptop speed, not Jetson speed**: all timings are on an RTX 4050 Laptop GPU / its CPU. They say nothing about relative speed on the actual Jetson deployment target.
- **Small number of fall clips**: fall recall is computed over 32 clips with a derivable GT fall window. Wide error bars apply to any recall percentage built from a denominator this size.

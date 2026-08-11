# YOLO Person Detection - Real Footage Benchmark

> **CAUTION — do not read "Falling / lying clips 56.1%" as fall detection working.**
> That row is a per-frame *any-person-detected* rate over whole clips that
> **contain** a fall. Most of a fall clip is the subject still upright, and that
> upright majority is what carries the 56.1%. Scored per box on the frames where
> the person is actually horizontal, detection is **0 of 65 across three rooms**,
> for both v3 and v4. See
> [`reserved_heldout_posture.md`](reserved_heldout_posture.md).
>
> The "Held-out clips only" row is also not comparable with the same row in
> `reserved_people_v4.md` — the two runs held out *different clips*
> (`TV_Lounge_2_Sit` here, `TV_Lounge_1_Walk` there), so 20.1% -> 68.5% is a
> change of test set, not an improvement.



Model: yolov8n_sage_merged_v3.pt, confidence threshold 0.4, imgsz 320
Clips: 9, total frames: 4903
Overall person-detection rate: 63.7%
Overall mean latency: 18.8 ms/frame (53.2 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 3294 | 67.4% |
| Falling / lying clips | 1609 | 56.1% |
| Held-out clips only (never trained on) | 581 | 20.1% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 97.4% | 19.2 | 16.8 | 19.4 |
| Bedroom_Sit.mov | no | 740 | 85.0% | 18.2 | 17.8 | 21.3 |
| Bedroom_Walk.mov | no | 449 | 100.0% | 18.0 | 17.8 | 20.5 |
| TV_Lounge_1_Fall.mov | no | 628 | 29.1% | 18.5 | 18.2 | 21.4 |
| TV_Lounge_1_Sit.mov | no | 593 | 80.4% | 19.5 | 19.1 | 23.1 |
| TV_Lounge_1_Walk.mov | no | 406 | 73.4% | 19.6 | 19.0 | 23.1 |
| TV_Lounge_2_Fall.mov | no | 358 | 31.6% | 18.1 | 17.9 | 20.3 |
| TV_Lounge_2_Sit.mov | yes | 581 | 20.1% | 18.9 | 18.4 | 22.5 |
| TV_Lounge_2_Walk.mov | no | 525 | 47.4% | 19.2 | 18.9 | 21.8 |

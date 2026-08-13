# YOLO Person Detection - Real Footage Benchmark

> **CAUTION — read [`reserved_heldout_posture.md`](reserved_heldout_posture.md) first.**
>
> "Falling / lying clips 56.1%" is a per-frame *any-person-detected* rate over
> whole clips that **contain** a fall, most of which is the subject still
> upright. Scored per clip against hand-drawn boxes at imgsz 640, v3 detects
> **0.25–0.45** of person boxes on fall clips versus **0.83–1.00** on walk/sit
> clips — five fall clips, three rooms, no overlap between the two groups.
> Do not read 56.1% as evidence that falls are detected.
>
> **Resolution is decisive and invisible in this table.** The same weights lose
> about a third of their detections at imgsz 320. This benchmark runs at 640,
> which is correct — but the offline scoring scripts defaulted to 320, which is
> why they disagreed with these numbers for a long time.
>
> The "Held-out clips only" row is NOT comparable with the same row in
> `reserved_people_v4.md`: the two runs held out *different clips*
> (`TV_Lounge_2_Sit` here, `TV_Lounge_1_Walk` there) — a change of test set,
> not an improvement.

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

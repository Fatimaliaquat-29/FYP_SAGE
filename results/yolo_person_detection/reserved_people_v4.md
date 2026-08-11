# YOLO Person Detection - Real Footage Benchmark

> **CAUTION — see [`reserved_heldout_posture.md`](reserved_heldout_posture.md).**
> "Falling / lying clips 35.4%" is a per-frame rate over clips that *contain* a
> fall, most of which is upright footage. On frames where the person is actually
> horizontal, v4 detects **0 of 65**, the same as v3.
>
> The "Held-out clips only 68.5%" row is NOT comparable with the 20.1% in
> `reserved_people_v3.md`: the two runs held out different clips
> (`TV_Lounge_1_Walk` here, `TV_Lounge_2_Sit` there). That is a change of test
> set, not an improvement.
>
> At matched settings v4 also loses upright recall versus v3 (0.905 -> 0.757)
> while buying a lower false-positive rate (2.70% -> 0.39%).



Model: yolov8n_sage_merged_v4.pt, confidence threshold 0.4, imgsz 320
Clips: 10, total frames: 5850
Overall person-detection rate: 61.2%
Overall mean latency: 19.7 ms/frame (50.9 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4241 | 71.0% |
| Falling / lying clips | 1609 | 35.4% |
| Held-out clips only (never trained on) | 406 | 68.5% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 45.9% | 19.9 | 17.3 | 20.2 |
| Bedroom_Sit.mov | no | 740 | 65.3% | 19.7 | 19.5 | 23.0 |
| Bedroom_Walk.mov | no | 449 | 100.0% | 20.1 | 19.6 | 23.6 |
| people_ground_mahaRoom.MOV | no | 947 | 100.0% | 19.8 | 19.4 | 23.4 |
| TV_Lounge_1_Fall.mov | no | 628 | 27.7% | 20.0 | 19.6 | 23.1 |
| TV_Lounge_1_Sit.mov | no | 593 | 80.1% | 20.2 | 19.8 | 23.8 |
| TV_Lounge_1_Walk.mov | yes | 406 | 68.5% | 19.9 | 19.6 | 23.3 |
| TV_Lounge_2_Fall.mov | no | 358 | 30.7% | 18.8 | 18.5 | 22.0 |
| TV_Lounge_2_Sit.mov | no | 581 | 21.7% | 19.0 | 18.7 | 22.2 |
| TV_Lounge_2_Walk.mov | no | 525 | 48.2% | 19.2 | 18.6 | 22.9 |

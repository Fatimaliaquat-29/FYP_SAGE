# YOLO Person Detection - Real Footage Benchmark

> **CAUTION — read [`reserved_heldout_posture.md`](reserved_heldout_posture.md) first.**
>
> **v4 is worse than v3 at every resolution** on hand-labelled held-out footage
> (0.520 vs 0.736 overall detection rate at imgsz 640). Its only advantage is a
> lower empty-room false-positive rate (0.39% vs 2.70%, measured at imgsz 320
> and still to be re-checked at 640). For a fall detector a missed person costs
> more than a false alarm, so **v3 is preferred over v4**.
>
> "Falling / lying clips 35.4%" is a per-frame rate over clips that *contain* a
> fall, most of which is upright footage — it is not a fall-detection rate.
>
> The "Held-out clips only 68.5%" row is NOT comparable with the 20.1% in
> `reserved_people_v3.md`: different clips were held out in each run
> (`TV_Lounge_1_Walk` here, `TV_Lounge_2_Sit` there).

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

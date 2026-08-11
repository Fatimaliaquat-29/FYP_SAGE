# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v4.pt, confidence threshold 0.25, imgsz 320
Clips: 10, total frames: 5850
Overall person-detection rate: 69.3%
Overall mean latency: 21.8 ms/frame (45.9 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4241 | 74.2% |
| Falling / lying clips | 1609 | 56.4% |
| Held-out clips only (never trained on) | 406 | 71.7% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 96.8% | 20.8 | 18.5 | 21.4 |
| Bedroom_Sit.mov | no | 740 | 76.1% | 26.2 | 20.3 | 64.6 |
| Bedroom_Walk.mov | no | 449 | 100.0% | 21.9 | 21.0 | 30.3 |
| people_ground_mahaRoom.MOV | no | 947 | 100.0% | 21.4 | 21.0 | 24.8 |
| TV_Lounge_1_Fall.mov | no | 628 | 29.0% | 21.7 | 21.6 | 24.6 |
| TV_Lounge_1_Sit.mov | no | 593 | 80.6% | 21.6 | 21.4 | 24.3 |
| TV_Lounge_1_Walk.mov | yes | 406 | 71.7% | 21.8 | 21.5 | 24.9 |
| TV_Lounge_2_Fall.mov | no | 358 | 34.1% | 20.2 | 20.0 | 23.1 |
| TV_Lounge_2_Sit.mov | no | 581 | 25.6% | 20.2 | 19.8 | 23.1 |
| TV_Lounge_2_Walk.mov | no | 525 | 51.0% | 22.4 | 21.9 | 26.1 |

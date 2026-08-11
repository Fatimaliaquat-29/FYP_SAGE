# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v3.pt, confidence threshold 0.25, imgsz 320
Clips: 10, total frames: 5850
Overall person-detection rate: 72.0%
Overall mean latency: 34.7 ms/frame (28.8 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4241 | 77.1% |
| Falling / lying clips | 1609 | 58.4% |
| Held-out clips only (never trained on) | 406 | 75.6% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 99.0% | 40.7 | 37.8 | 65.4 |
| Bedroom_Sit.mov | no | 740 | 91.8% | 43.0 | 41.6 | 51.5 |
| Bedroom_Walk.mov | no | 449 | 100.0% | 43.7 | 42.5 | 53.7 |
| people_ground_mahaRoom.MOV | no | 947 | 100.0% | 42.4 | 40.8 | 52.7 |
| TV_Lounge_1_Fall.mov | no | 628 | 31.1% | 43.7 | 42.0 | 53.8 |
| TV_Lounge_1_Sit.mov | no | 593 | 83.8% | 42.1 | 40.8 | 51.6 |
| TV_Lounge_1_Walk.mov | yes | 406 | 75.6% | 26.6 | 23.2 | 43.0 |
| TV_Lounge_2_Fall.mov | no | 358 | 35.8% | 21.5 | 21.3 | 24.8 |
| TV_Lounge_2_Sit.mov | no | 581 | 21.2% | 21.8 | 21.3 | 25.7 |
| TV_Lounge_2_Walk.mov | no | 525 | 51.0% | 21.2 | 20.9 | 24.5 |

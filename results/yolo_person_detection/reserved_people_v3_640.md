# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v3.pt, confidence threshold 0.4, imgsz 640
Clips: 10, total frames: 5850
Overall person-detection rate: 65.9%
Overall mean latency: 13.6 ms/frame (73.6 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4241 | 78.2% |
| Falling / lying clips | 1609 | 33.6% |
| Held-out clips only (never trained on) | 406 | 65.0% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 38.2% | 16.6 | 12.6 | 17.1 |
| Bedroom_Sit.mov | no | 740 | 91.2% | 13.3 | 13.0 | 17.2 |
| Bedroom_Walk.mov | no | 449 | 100.0% | 13.2 | 12.6 | 17.5 |
| people_ground_mahaRoom.MOV | no | 947 | 99.0% | 12.6 | 12.1 | 16.3 |
| TV_Lounge_1_Fall.mov | no | 628 | 24.2% | 13.5 | 13.2 | 16.8 |
| TV_Lounge_1_Sit.mov | no | 593 | 72.7% | 13.6 | 13.4 | 17.4 |
| TV_Lounge_1_Walk.mov | yes | 406 | 65.0% | 13.7 | 13.4 | 17.3 |
| TV_Lounge_2_Fall.mov | no | 358 | 42.2% | 12.9 | 12.4 | 17.4 |
| TV_Lounge_2_Sit.mov | no | 581 | 44.1% | 13.2 | 12.9 | 17.1 |
| TV_Lounge_2_Walk.mov | no | 525 | 57.5% | 13.5 | 13.1 | 17.6 |

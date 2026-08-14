# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v5.pt, confidence threshold 0.4, imgsz 640
Clips: 10, total frames: 5850
Overall person-detection rate: 70.4%
Overall mean latency: 13.5 ms/frame (74.3 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4241 | 79.8% |
| Falling / lying clips | 1609 | 45.6% |
| Held-out clips only (never trained on) | 406 | 74.1% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 67.3% | 16.5 | 12.6 | 17.4 |
| Bedroom_Sit.mov | no | 740 | 85.1% | 12.9 | 12.5 | 17.3 |
| Bedroom_Walk.mov | no | 449 | 100.0% | 13.2 | 12.9 | 16.9 |
| people_ground_mahaRoom.MOV | no | 947 | 100.0% | 12.8 | 12.4 | 16.8 |
| TV_Lounge_1_Fall.mov | no | 628 | 27.4% | 13.2 | 13.0 | 16.8 |
| TV_Lounge_1_Sit.mov | no | 593 | 81.5% | 13.2 | 12.9 | 17.2 |
| TV_Lounge_1_Walk.mov | yes | 406 | 74.1% | 13.3 | 13.0 | 17.0 |
| TV_Lounge_2_Fall.mov | no | 358 | 39.9% | 13.3 | 12.7 | 17.8 |
| TV_Lounge_2_Sit.mov | no | 581 | 29.1% | 12.9 | 12.4 | 17.0 |
| TV_Lounge_2_Walk.mov | no | 525 | 77.5% | 13.1 | 12.7 | 17.4 |

# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n.pt, confidence threshold 0.4, imgsz 320
Clips: 9, total frames: 4903
Overall person-detection rate: 51.3%
Overall mean latency: 19.6 ms/frame (51.0 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 3294 | 60.4% |
| Falling / lying clips | 1609 | 32.4% |
| Held-out clips only (never trained on) | 581 | 20.0% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 33.7% | 19.8 | 17.1 | 19.9 |
| Bedroom_Sit.mov | no | 740 | 49.5% | 18.6 | 18.5 | 21.3 |
| Bedroom_Walk.mov | no | 449 | 99.8% | 20.5 | 20.0 | 24.9 |
| TV_Lounge_1_Fall.mov | no | 628 | 31.7% | 19.8 | 19.5 | 23.1 |
| TV_Lounge_1_Sit.mov | no | 593 | 85.0% | 20.1 | 19.8 | 23.1 |
| TV_Lounge_1_Walk.mov | no | 406 | 77.1% | 20.0 | 19.8 | 22.9 |
| TV_Lounge_2_Fall.mov | no | 358 | 31.6% | 19.3 | 19.0 | 21.7 |
| TV_Lounge_2_Sit.mov | yes | 581 | 20.0% | 19.3 | 19.0 | 21.9 |
| TV_Lounge_2_Walk.mov | no | 525 | 46.5% | 19.2 | 19.0 | 21.9 |

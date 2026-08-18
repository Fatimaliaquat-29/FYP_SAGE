# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n.pt, confidence threshold 0.4, imgsz 320
Clips: 5, total frames: 3089
Overall person-detection rate: 0.1%
Overall mean latency: 22.2 ms/frame (45.0 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 3089 | 0.1% |
| Held-out clips only (never trained on) | 343 | 0.0% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Empty.mov | no | 854 | 0.0% | 19.7 | 17.9 | 21.0 |
| TV_Lounge_1_Empty.mov | no | 826 | 0.0% | 21.7 | 21.0 | 27.5 |
| TV_Lounge_2_Empty.mov | no | 497 | 0.4% | 27.8 | 26.0 | 39.9 |
| WhatsApp Video 2026-07-31 at 5.49.30 PM.mp4 | no | 569 | 0.0% | 19.8 | 19.5 | 23.2 |
| WhatsApp Video 2026-07-31 at 7.44.22 PM.mp4 | yes | 343 | 0.0% | 22.0 | 21.8 | 24.6 |

# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v4.pt, confidence threshold 0.25, imgsz 320
Clips: 6, total frames: 4101
Overall person-detection rate: 0.0%
Overall mean latency: 27.2 ms/frame (36.7 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4101 | 0.0% |
| Held-out clips only (never trained on) | 569 | 0.0% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Empty.mov | no | 854 | 0.0% | 32.3 | 25.5 | 48.6 |
| empty_ground_mahaRoom.MOV | no | 1012 | 0.0% | 21.7 | 20.9 | 27.4 |
| TV_Lounge_1_Empty.mov | no | 826 | 0.0% | 30.1 | 25.0 | 49.3 |
| TV_Lounge_2_Empty.mov | no | 497 | 0.0% | 23.4 | 22.7 | 29.0 |
| WhatsApp Video 2026-07-31 at 5.49.30 PM.mp4 | yes | 569 | 0.0% | 34.0 | 36.1 | 49.6 |
| WhatsApp Video 2026-07-31 at 7.44.22 PM.mp4 | no | 343 | 0.0% | 21.9 | 21.4 | 25.3 |

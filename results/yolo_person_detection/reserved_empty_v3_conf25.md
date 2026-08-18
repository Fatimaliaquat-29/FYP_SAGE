# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v3.pt, confidence threshold 0.25, imgsz 320
Clips: 6, total frames: 4101
Overall person-detection rate: 0.0%
Overall mean latency: 43.8 ms/frame (22.8 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4101 | 0.0% |
| Held-out clips only (never trained on) | 569 | 0.0% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Empty.mov | no | 854 | 0.0% | 46.8 | 42.1 | 61.3 |
| empty_ground_mahaRoom.MOV | no | 1012 | 0.0% | 42.9 | 41.0 | 54.0 |
| TV_Lounge_1_Empty.mov | no | 826 | 0.0% | 43.5 | 42.1 | 56.1 |
| TV_Lounge_2_Empty.mov | no | 497 | 0.2% | 42.7 | 41.1 | 54.1 |
| WhatsApp Video 2026-07-31 at 5.49.30 PM.mp4 | yes | 569 | 0.0% | 40.9 | 39.8 | 48.5 |
| WhatsApp Video 2026-07-31 at 7.44.22 PM.mp4 | no | 343 | 0.0% | 46.2 | 44.2 | 63.1 |

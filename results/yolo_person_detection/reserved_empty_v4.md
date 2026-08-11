# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v4.pt, confidence threshold 0.4, imgsz 320
Clips: 6, total frames: 4101
Overall person-detection rate: 0.0%
Overall mean latency: 21.4 ms/frame (46.8 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4101 | 0.0% |
| Held-out clips only (never trained on) | 569 | 0.0% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Empty.mov | no | 854 | 0.0% | 22.5 | 19.2 | 22.2 |
| empty_ground_mahaRoom.MOV | no | 1012 | 0.0% | 19.5 | 19.0 | 23.6 |
| TV_Lounge_1_Empty.mov | no | 826 | 0.0% | 21.9 | 21.2 | 27.3 |
| TV_Lounge_2_Empty.mov | no | 497 | 0.0% | 23.3 | 22.7 | 29.4 |
| WhatsApp Video 2026-07-31 at 5.49.30 PM.mp4 | yes | 569 | 0.0% | 19.4 | 18.9 | 22.6 |
| WhatsApp Video 2026-07-31 at 7.44.22 PM.mp4 | no | 343 | 0.0% | 21.7 | 21.3 | 24.3 |

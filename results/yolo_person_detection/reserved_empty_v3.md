# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v3.pt, confidence threshold 0.4, imgsz 320
Clips: 5, total frames: 3089
Overall person-detection rate: 0.0%
Overall mean latency: 19.1 ms/frame (52.4 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 3089 | 0.0% |
| Held-out clips only (never trained on) | 343 | 0.0% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Empty.mov | no | 854 | 0.0% | 19.8 | 17.9 | 20.9 |
| TV_Lounge_1_Empty.mov | no | 826 | 0.0% | 18.4 | 18.2 | 21.1 |
| TV_Lounge_2_Empty.mov | no | 497 | 0.0% | 18.3 | 18.1 | 21.1 |
| WhatsApp Video 2026-07-31 at 5.49.30 PM.mp4 | no | 569 | 0.0% | 18.3 | 18.0 | 21.0 |
| WhatsApp Video 2026-07-31 at 7.44.22 PM.mp4 | yes | 343 | 0.0% | 20.5 | 20.2 | 23.2 |

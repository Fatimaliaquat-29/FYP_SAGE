# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged.pt, confidence threshold 0.4, imgsz 320
Clips: 28, total frames: 9188
Overall person-detection rate: 97.4%
Overall mean latency: 40.5 ms/frame (24.7 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 6834 | 98.9% |
| Falling / lying clips | 2354 | 93.0% |
| Held-out clips only (never trained on) | 3905 | 97.1% |
| Held-out falling / lying clips only | 285 | 83.9% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Hussain Testing 7-23-26\normal.mp4 | no | 384 | 100.0% | 39.5 | 41.5 | 53.1 |
| Hussain Testing 7-23-26\old.mp4 | no | 615 | 100.0% | 57.9 | 60.3 | 74.4 |
| Sanawar Testing 7-22-26\Fall_Curled.mov | no | 105 | 98.1% | 47.4 | 44.2 | 66.1 |
| Sanawar Testing 7-22-26\Fast_Sit.mov | no | 63 | 93.7% | 41.2 | 41.5 | 44.6 |
| Sanawar Testing 7-22-26\Legs occluded.mov | no | 155 | 100.0% | 43.9 | 41.8 | 59.3 |
| Sanawar Testing 7-22-26\Lying_legs_straight.mov | no | 147 | 100.0% | 42.2 | 41.3 | 48.9 |
| Sanawar Testing 7-22-26\Lying_straight.mov | no | 147 | 100.0% | 43.5 | 41.5 | 62.8 |
| Sanawar Testing 7-22-26\newTest.mov | yes | 3470 | 98.4% | 42.8 | 39.5 | 64.9 |
| Sanawar Testing 7-22-26\normal.mov | no | 384 | 100.0% | 37.4 | 37.3 | 42.3 |
| Sanawar Testing 7-22-26\Normal_Fall_1.mov | no | 163 | 98.2% | 40.3 | 40.5 | 44.2 |
| Sanawar Testing 7-22-26\Normal_Fall_2.mov | yes | 131 | 66.4% | 40.9 | 40.3 | 49.3 |
| Sanawar Testing 7-22-26\Off_axis.mov | no | 190 | 100.0% | 40.1 | 40.4 | 43.5 |
| Sanawar Testing 7-22-26\old.mov | no | 615 | 100.0% | 36.3 | 36.6 | 39.8 |
| Sanawar Testing 7-22-26\Sit_1.mov | no | 157 | 97.5% | 38.6 | 38.4 | 45.5 |
| Sanawar Testing 7-22-26\Sit_2.mov | yes | 150 | 90.7% | 40.2 | 40.4 | 44.8 |
| Sanawar Testing 7-22-26\Sit_3.mov | no | 176 | 99.4% | 41.1 | 41.0 | 46.2 |
| Sanawar Testing 7-22-26\Standing_1.mov | no | 168 | 100.0% | 40.2 | 40.5 | 43.5 |
| Sanawar Testing 7-22-26\Standing_2.mov | no | 180 | 100.0% | 40.4 | 40.5 | 45.2 |
| Sanawar Testing 7-22-26\Standing_3.mov | no | 127 | 100.0% | 40.6 | 40.8 | 44.5 |
| Sanawar Testing 7-25-26\Backward_fall.mp4 | no | 111 | 100.0% | 36.6 | 37.0 | 40.5 |
| Sanawar Testing 7-25-26\Chair_fall.mp4 | no | 250 | 76.0% | 39.3 | 38.4 | 48.5 |
| Sanawar Testing 7-25-26\Fall_and_lie.mp4 | no | 354 | 98.6% | 38.0 | 38.0 | 43.5 |
| Sanawar Testing 7-25-26\Far_fall.mp4 | no | 129 | 100.0% | 38.2 | 38.1 | 43.4 |
| Sanawar Testing 7-25-26\Foward_fall.mp4 | yes | 154 | 98.7% | 37.2 | 37.8 | 40.4 |
| Sanawar Testing 7-25-26\Occluded_fall.mp4 | no | 171 | 95.9% | 36.9 | 37.3 | 40.6 |
| Sanawar Testing 7-25-26\Off_axis_fall.mp4 | no | 124 | 98.4% | 36.9 | 37.2 | 40.2 |
| Sanawar Testing 7-25-26\Side_fall.mp4 | no | 163 | 100.0% | 37.8 | 37.9 | 42.9 |
| Sanawar Testing 7-25-26\Slow_fall.mp4 | no | 205 | 81.0% | 37.8 | 37.9 | 42.2 |

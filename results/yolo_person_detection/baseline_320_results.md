# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n.pt, confidence threshold 0.4, imgsz 320
Clips: 28, total frames: 9188
Overall person-detection rate: 72.8%
Overall mean latency: 46.2 ms/frame (21.6 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 6834 | 84.7% |
| Falling / lying clips | 2354 | 38.4% |
| Held-out clips only (never trained on) | 3905 | 82.6% |
| Held-out falling / lying clips only | 285 | 50.2% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Hussain Testing 7-23-26\normal.mp4 | no | 384 | 94.3% | 38.5 | 38.4 | 43.1 |
| Hussain Testing 7-23-26\old.mp4 | no | 615 | 73.5% | 39.6 | 38.5 | 49.3 |
| Sanawar Testing 7-22-26\Fall_Curled.mov | no | 105 | 53.3% | 43.7 | 41.0 | 60.1 |
| Sanawar Testing 7-22-26\Fast_Sit.mov | no | 63 | 88.9% | 38.9 | 39.4 | 41.2 |
| Sanawar Testing 7-22-26\Legs occluded.mov | no | 155 | 100.0% | 40.4 | 39.8 | 47.1 |
| Sanawar Testing 7-22-26\Lying_legs_straight.mov | no | 147 | 0.7% | 41.1 | 39.8 | 48.4 |
| Sanawar Testing 7-22-26\Lying_straight.mov | no | 147 | 0.0% | 39.4 | 39.4 | 44.5 |
| Sanawar Testing 7-22-26\newTest.mov | yes | 3470 | 84.7% | 39.5 | 38.4 | 48.8 |
| Sanawar Testing 7-22-26\normal.mov | no | 384 | 94.3% | 40.0 | 38.6 | 47.0 |
| Sanawar Testing 7-22-26\Normal_Fall_1.mov | no | 163 | 76.7% | 41.2 | 40.0 | 49.1 |
| Sanawar Testing 7-22-26\Normal_Fall_2.mov | yes | 131 | 55.0% | 41.2 | 40.2 | 49.2 |
| Sanawar Testing 7-22-26\Off_axis.mov | no | 190 | 100.0% | 39.8 | 39.6 | 47.7 |
| Sanawar Testing 7-22-26\old.mov | no | 615 | 73.5% | 39.0 | 38.4 | 47.6 |
| Sanawar Testing 7-22-26\Sit_1.mov | no | 157 | 65.6% | 54.7 | 40.8 | 109.7 |
| Sanawar Testing 7-22-26\Sit_2.mov | yes | 150 | 96.0% | 54.3 | 51.9 | 75.1 |
| Sanawar Testing 7-22-26\Sit_3.mov | no | 176 | 56.2% | 54.1 | 52.0 | 73.0 |
| Sanawar Testing 7-22-26\Standing_1.mov | no | 168 | 100.0% | 61.9 | 55.0 | 100.1 |
| Sanawar Testing 7-22-26\Standing_2.mov | no | 180 | 100.0% | 47.6 | 43.7 | 69.0 |
| Sanawar Testing 7-22-26\Standing_3.mov | no | 127 | 100.0% | 44.6 | 41.4 | 60.4 |
| Sanawar Testing 7-25-26\Backward_fall.mp4 | no | 111 | 67.6% | 38.5 | 38.7 | 43.3 |
| Sanawar Testing 7-25-26\Chair_fall.mp4 | no | 250 | 59.2% | 55.8 | 50.5 | 85.3 |
| Sanawar Testing 7-25-26\Fall_and_lie.mp4 | no | 354 | 14.4% | 42.3 | 39.7 | 55.5 |
| Sanawar Testing 7-25-26\Far_fall.mp4 | no | 129 | 47.3% | 51.6 | 49.5 | 63.8 |
| Sanawar Testing 7-25-26\Foward_fall.mp4 | yes | 154 | 46.1% | 61.1 | 52.5 | 81.9 |
| Sanawar Testing 7-25-26\Occluded_fall.mp4 | no | 171 | 39.8% | 52.1 | 50.7 | 63.6 |
| Sanawar Testing 7-25-26\Off_axis_fall.mp4 | no | 124 | 33.1% | 51.9 | 50.5 | 61.7 |
| Sanawar Testing 7-25-26\Side_fall.mp4 | no | 163 | 39.9% | 51.1 | 49.2 | 66.2 |
| Sanawar Testing 7-25-26\Slow_fall.mp4 | no | 205 | 34.6% | 50.3 | 49.0 | 63.2 |

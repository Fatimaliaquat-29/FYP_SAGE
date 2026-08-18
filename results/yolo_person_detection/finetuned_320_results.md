# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_person.pt, confidence threshold 0.4, imgsz 320
Clips: 28, total frames: 9188
Overall person-detection rate: 96.9%
Overall mean latency: 41.2 ms/frame (24.3 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 6834 | 97.5% |
| Falling / lying clips | 2354 | 95.2% |
| Held-out clips only (never trained on) | 3905 | 94.3% |
| Held-out falling / lying clips only | 285 | 82.5% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Hussain Testing 7-23-26\normal.mp4 | no | 384 | 100.0% | 55.1 | 51.2 | 80.4 |
| Hussain Testing 7-23-26\old.mp4 | no | 615 | 100.0% | 38.4 | 37.7 | 46.2 |
| Sanawar Testing 7-22-26\Fall_Curled.mov | no | 105 | 99.0% | 39.4 | 39.1 | 44.3 |
| Sanawar Testing 7-22-26\Fast_Sit.mov | no | 63 | 100.0% | 49.8 | 47.8 | 65.3 |
| Sanawar Testing 7-22-26\Legs occluded.mov | no | 155 | 100.0% | 46.7 | 44.0 | 63.4 |
| Sanawar Testing 7-22-26\Lying_legs_straight.mov | no | 147 | 100.0% | 55.9 | 52.7 | 74.2 |
| Sanawar Testing 7-22-26\Lying_straight.mov | no | 147 | 100.0% | 55.4 | 52.4 | 76.8 |
| Sanawar Testing 7-22-26\newTest.mov | yes | 3470 | 95.0% | 42.1 | 38.5 | 58.8 |
| Sanawar Testing 7-22-26\normal.mov | no | 384 | 100.0% | 36.7 | 37.0 | 41.4 |
| Sanawar Testing 7-22-26\Normal_Fall_1.mov | no | 163 | 100.0% | 38.1 | 38.3 | 41.1 |
| Sanawar Testing 7-22-26\Normal_Fall_2.mov | yes | 131 | 64.9% | 38.5 | 38.5 | 41.7 |
| Sanawar Testing 7-22-26\Off_axis.mov | no | 190 | 100.0% | 39.3 | 38.7 | 48.4 |
| Sanawar Testing 7-22-26\old.mov | no | 615 | 100.0% | 37.0 | 37.1 | 40.9 |
| Sanawar Testing 7-22-26\Sit_1.mov | no | 157 | 99.4% | 38.9 | 38.9 | 43.9 |
| Sanawar Testing 7-22-26\Sit_2.mov | yes | 150 | 100.0% | 39.1 | 38.8 | 41.9 |
| Sanawar Testing 7-22-26\Sit_3.mov | no | 176 | 100.0% | 38.2 | 38.7 | 41.3 |
| Sanawar Testing 7-22-26\Standing_1.mov | no | 168 | 100.0% | 38.2 | 38.5 | 41.7 |
| Sanawar Testing 7-22-26\Standing_2.mov | no | 180 | 100.0% | 38.7 | 38.8 | 46.5 |
| Sanawar Testing 7-22-26\Standing_3.mov | no | 127 | 100.0% | 38.5 | 38.7 | 41.5 |
| Sanawar Testing 7-25-26\Backward_fall.mp4 | no | 111 | 100.0% | 37.6 | 37.9 | 40.1 |
| Sanawar Testing 7-25-26\Chair_fall.mp4 | no | 250 | 83.6% | 38.3 | 38.2 | 42.2 |
| Sanawar Testing 7-25-26\Fall_and_lie.mp4 | no | 354 | 96.9% | 39.6 | 38.5 | 48.3 |
| Sanawar Testing 7-25-26\Far_fall.mp4 | no | 129 | 99.2% | 38.9 | 38.5 | 46.1 |
| Sanawar Testing 7-25-26\Foward_fall.mp4 | yes | 154 | 97.4% | 37.2 | 37.5 | 41.6 |
| Sanawar Testing 7-25-26\Occluded_fall.mp4 | no | 171 | 100.0% | 39.2 | 38.7 | 44.7 |
| Sanawar Testing 7-25-26\Off_axis_fall.mp4 | no | 124 | 92.7% | 37.5 | 38.0 | 40.6 |
| Sanawar Testing 7-25-26\Side_fall.mp4 | no | 163 | 100.0% | 38.0 | 38.2 | 40.6 |
| Sanawar Testing 7-25-26\Slow_fall.mp4 | no | 205 | 100.0% | 42.8 | 39.8 | 57.9 |

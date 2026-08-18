# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v3.pt, confidence threshold 0.4, imgsz 320
Clips: 28, total frames: 9188
Overall person-detection rate: 97.3%
Overall mean latency: 42.1 ms/frame (23.8 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 6834 | 99.0% |
| Falling / lying clips | 2354 | 92.4% |
| Held-out clips only (never trained on) | 3905 | 97.0% |
| Held-out falling / lying clips only | 285 | 82.5% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Hussain Testing 7-23-26\normal.mp4 | no | 384 | 100.0% | 30.1 | 27.8 | 35.8 |
| Hussain Testing 7-23-26\old.mp4 | no | 615 | 100.0% | 32.1 | 28.7 | 46.2 |
| Sanawar Testing 7-22-26\Fall_Curled.mov | no | 105 | 90.5% | 30.5 | 28.9 | 42.1 |
| Sanawar Testing 7-22-26\Fast_Sit.mov | no | 63 | 100.0% | 35.2 | 34.5 | 41.0 |
| Sanawar Testing 7-22-26\Legs occluded.mov | no | 155 | 100.0% | 36.3 | 32.1 | 64.2 |
| Sanawar Testing 7-22-26\Lying_legs_straight.mov | no | 147 | 100.0% | 30.8 | 29.9 | 35.6 |
| Sanawar Testing 7-22-26\Lying_straight.mov | no | 147 | 100.0% | 30.2 | 28.8 | 36.0 |
| Sanawar Testing 7-22-26\newTest.mov | yes | 3470 | 98.0% | 40.6 | 36.4 | 60.3 |
| Sanawar Testing 7-22-26\normal.mov | no | 384 | 100.0% | 39.3 | 37.3 | 51.3 |
| Sanawar Testing 7-22-26\Normal_Fall_1.mov | no | 163 | 91.4% | 38.2 | 38.5 | 41.9 |
| Sanawar Testing 7-22-26\Normal_Fall_2.mov | yes | 131 | 64.1% | 37.5 | 37.6 | 41.7 |
| Sanawar Testing 7-22-26\Off_axis.mov | no | 190 | 100.0% | 38.7 | 38.2 | 45.5 |
| Sanawar Testing 7-22-26\old.mov | no | 615 | 100.0% | 36.6 | 36.5 | 42.4 |
| Sanawar Testing 7-22-26\Sit_1.mov | no | 157 | 100.0% | 39.1 | 38.6 | 45.9 |
| Sanawar Testing 7-22-26\Sit_2.mov | yes | 150 | 100.0% | 38.8 | 38.5 | 42.6 |
| Sanawar Testing 7-22-26\Sit_3.mov | no | 176 | 100.0% | 37.7 | 37.9 | 41.1 |
| Sanawar Testing 7-22-26\Standing_1.mov | no | 168 | 100.0% | 38.5 | 38.0 | 44.5 |
| Sanawar Testing 7-22-26\Standing_2.mov | no | 180 | 100.0% | 38.8 | 38.6 | 43.5 |
| Sanawar Testing 7-22-26\Standing_3.mov | no | 127 | 100.0% | 37.7 | 38.0 | 40.2 |
| Sanawar Testing 7-25-26\Backward_fall.mp4 | no | 111 | 100.0% | 36.2 | 36.6 | 38.9 |
| Sanawar Testing 7-25-26\Chair_fall.mp4 | no | 250 | 70.8% | 43.2 | 38.4 | 60.6 |
| Sanawar Testing 7-25-26\Fall_and_lie.mp4 | no | 354 | 99.7% | 59.0 | 59.1 | 62.7 |
| Sanawar Testing 7-25-26\Far_fall.mp4 | no | 129 | 100.0% | 59.5 | 58.9 | 66.2 |
| Sanawar Testing 7-25-26\Foward_fall.mp4 | yes | 154 | 98.1% | 58.0 | 58.1 | 61.4 |
| Sanawar Testing 7-25-26\Occluded_fall.mp4 | no | 171 | 100.0% | 58.9 | 59.2 | 61.7 |
| Sanawar Testing 7-25-26\Off_axis_fall.mp4 | no | 124 | 99.2% | 60.1 | 59.9 | 66.6 |
| Sanawar Testing 7-25-26\Side_fall.mp4 | no | 163 | 97.5% | 58.2 | 58.5 | 61.3 |
| Sanawar Testing 7-25-26\Slow_fall.mp4 | no | 205 | 87.8% | 58.8 | 58.3 | 72.0 |

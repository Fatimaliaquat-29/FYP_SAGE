# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n_sage_merged_v2.pt, confidence threshold 0.4, imgsz 320
Clips: 28, total frames: 9188
Overall person-detection rate: 97.0%
Overall mean latency: 49.5 ms/frame (20.2 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 6834 | 98.9% |
| Falling / lying clips | 2354 | 91.4% |
| Held-out clips only (never trained on) | 3905 | 96.7% |
| Held-out falling / lying clips only | 285 | 81.4% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Hussain Testing 7-23-26\normal.mp4 | no | 384 | 100.0% | 29.0 | 27.8 | 32.2 |
| Hussain Testing 7-23-26\old.mp4 | no | 615 | 100.0% | 28.0 | 28.1 | 31.7 |
| Sanawar Testing 7-22-26\Fall_Curled.mov | no | 105 | 81.9% | 40.7 | 34.2 | 62.8 |
| Sanawar Testing 7-22-26\Fast_Sit.mov | no | 63 | 100.0% | 55.9 | 54.5 | 76.8 |
| Sanawar Testing 7-22-26\Legs occluded.mov | no | 155 | 100.0% | 54.8 | 56.4 | 67.3 |
| Sanawar Testing 7-22-26\Lying_legs_straight.mov | no | 147 | 100.0% | 51.8 | 51.9 | 69.6 |
| Sanawar Testing 7-22-26\Lying_straight.mov | no | 147 | 100.0% | 53.1 | 55.5 | 67.0 |
| Sanawar Testing 7-22-26\newTest.mov | yes | 3470 | 98.1% | 57.2 | 58.6 | 62.5 |
| Sanawar Testing 7-22-26\normal.mov | no | 384 | 100.0% | 32.8 | 27.9 | 58.9 |
| Sanawar Testing 7-22-26\Normal_Fall_1.mov | no | 163 | 100.0% | 29.9 | 28.8 | 34.3 |
| Sanawar Testing 7-22-26\Normal_Fall_2.mov | yes | 131 | 62.6% | 31.8 | 31.4 | 36.5 |
| Sanawar Testing 7-22-26\Off_axis.mov | no | 190 | 100.0% | 33.1 | 30.2 | 56.0 |
| Sanawar Testing 7-22-26\old.mov | no | 615 | 100.0% | 40.8 | 37.7 | 60.9 |
| Sanawar Testing 7-22-26\Sit_1.mov | no | 157 | 99.4% | 48.2 | 52.4 | 63.1 |
| Sanawar Testing 7-22-26\Sit_2.mov | yes | 150 | 94.0% | 55.1 | 55.1 | 62.5 |
| Sanawar Testing 7-22-26\Sit_3.mov | no | 176 | 100.0% | 53.3 | 54.4 | 60.2 |
| Sanawar Testing 7-22-26\Standing_1.mov | no | 168 | 100.0% | 54.6 | 54.9 | 61.8 |
| Sanawar Testing 7-22-26\Standing_2.mov | no | 180 | 100.0% | 53.6 | 54.3 | 60.7 |
| Sanawar Testing 7-22-26\Standing_3.mov | no | 127 | 100.0% | 54.5 | 54.7 | 59.4 |
| Sanawar Testing 7-25-26\Backward_fall.mp4 | no | 111 | 100.0% | 53.5 | 53.2 | 63.4 |
| Sanawar Testing 7-25-26\Chair_fall.mp4 | no | 250 | 71.2% | 52.4 | 53.0 | 58.1 |
| Sanawar Testing 7-25-26\Fall_and_lie.mp4 | no | 354 | 97.2% | 53.7 | 53.9 | 60.9 |
| Sanawar Testing 7-25-26\Far_fall.mp4 | no | 129 | 100.0% | 62.1 | 60.9 | 81.8 |
| Sanawar Testing 7-25-26\Foward_fall.mp4 | yes | 154 | 97.4% | 61.8 | 61.3 | 70.8 |
| Sanawar Testing 7-25-26\Occluded_fall.mp4 | no | 171 | 100.0% | 61.4 | 60.9 | 64.0 |
| Sanawar Testing 7-25-26\Off_axis_fall.mp4 | no | 124 | 99.2% | 60.4 | 60.1 | 63.8 |
| Sanawar Testing 7-25-26\Side_fall.mp4 | no | 163 | 99.4% | 60.4 | 60.7 | 64.1 |
| Sanawar Testing 7-25-26\Slow_fall.mp4 | no | 205 | 77.1% | 62.2 | 60.8 | 79.3 |

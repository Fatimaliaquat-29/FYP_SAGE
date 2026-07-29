# YOLO Person Detection - Real Footage Benchmark

Model: yolov8n.pt, confidence threshold 0.4, imgsz 640
Clips: 28, total frames: 9188
Overall person-detection rate: 82.3%
Overall mean latency: 98.8 ms/frame (10.1 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 6834 | 93.5% |
| Falling / lying clips | 2354 | 49.7% |
| Held-out clips only (never trained on) | 3905 | 90.3% |
| Held-out falling / lying clips only | 285 | 58.2% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Hussain Testing 7-23-26\normal.mp4 | no | 384 | 100.0% | 105.5 | 104.6 | 138.6 |
| Hussain Testing 7-23-26\old.mp4 | no | 615 | 85.9% | 117.9 | 110.3 | 166.4 |
| Sanawar Testing 7-22-26\Fall_Curled.mov | no | 105 | 63.8% | 93.4 | 90.7 | 113.5 |
| Sanawar Testing 7-22-26\Fast_Sit.mov | no | 63 | 85.7% | 99.8 | 92.3 | 139.4 |
| Sanawar Testing 7-22-26\Legs occluded.mov | no | 155 | 100.0% | 102.0 | 92.7 | 118.4 |
| Sanawar Testing 7-22-26\Lying_legs_straight.mov | no | 147 | 52.4% | 91.1 | 89.1 | 105.3 |
| Sanawar Testing 7-22-26\Lying_straight.mov | no | 147 | 0.0% | 86.1 | 86.1 | 92.6 |
| Sanawar Testing 7-22-26\newTest.mov | yes | 3470 | 92.6% | 94.8 | 85.0 | 134.2 |
| Sanawar Testing 7-22-26\normal.mov | no | 384 | 100.0% | 90.5 | 83.7 | 123.6 |
| Sanawar Testing 7-22-26\Normal_Fall_1.mov | no | 163 | 99.4% | 119.2 | 114.9 | 167.8 |
| Sanawar Testing 7-22-26\Normal_Fall_2.mov | yes | 131 | 59.5% | 87.5 | 86.9 | 94.3 |
| Sanawar Testing 7-22-26\Off_axis.mov | no | 190 | 100.0% | 89.0 | 87.2 | 104.2 |
| Sanawar Testing 7-22-26\old.mov | no | 615 | 85.9% | 94.8 | 90.1 | 125.7 |
| Sanawar Testing 7-22-26\Sit_1.mov | no | 157 | 100.0% | 113.5 | 112.3 | 149.9 |
| Sanawar Testing 7-22-26\Sit_2.mov | yes | 150 | 99.3% | 87.7 | 87.5 | 93.0 |
| Sanawar Testing 7-22-26\Sit_3.mov | no | 176 | 97.7% | 90.5 | 88.2 | 109.3 |
| Sanawar Testing 7-22-26\Standing_1.mov | no | 168 | 100.0% | 88.1 | 86.9 | 98.2 |
| Sanawar Testing 7-22-26\Standing_2.mov | no | 180 | 100.0% | 87.8 | 87.4 | 97.0 |
| Sanawar Testing 7-22-26\Standing_3.mov | no | 127 | 100.0% | 87.6 | 86.9 | 100.1 |
| Sanawar Testing 7-25-26\Backward_fall.mp4 | no | 111 | 100.0% | 87.5 | 83.6 | 107.8 |
| Sanawar Testing 7-25-26\Chair_fall.mp4 | no | 250 | 65.2% | 116.2 | 111.7 | 153.2 |
| Sanawar Testing 7-25-26\Fall_and_lie.mp4 | no | 354 | 14.7% | 108.6 | 105.1 | 135.2 |
| Sanawar Testing 7-25-26\Far_fall.mp4 | no | 129 | 46.5% | 114.2 | 108.4 | 147.6 |
| Sanawar Testing 7-25-26\Foward_fall.mp4 | yes | 154 | 57.1% | 109.0 | 106.6 | 131.4 |
| Sanawar Testing 7-25-26\Occluded_fall.mp4 | no | 171 | 40.4% | 109.9 | 107.2 | 139.7 |
| Sanawar Testing 7-25-26\Off_axis_fall.mp4 | no | 124 | 43.5% | 106.7 | 99.9 | 129.0 |
| Sanawar Testing 7-25-26\Side_fall.mp4 | no | 163 | 66.9% | 100.4 | 96.6 | 125.1 |
| Sanawar Testing 7-25-26\Slow_fall.mp4 | no | 205 | 38.5% | 88.4 | 84.4 | 120.5 |

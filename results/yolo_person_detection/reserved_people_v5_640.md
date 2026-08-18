# YOLO Person Detection - Real Footage Benchmark

> **These percentages are NOT recall and must not be compared between
> checkpoints as if they were.**
>
> `benchmark_footage.py` scores a frame as "person detected" if the model emits
> **any** person box anywhere in it — see the `any(d["class"] == "person" ...)`
> test at `src/detection/benchmark_footage.py:89`. There is no ground truth, no
> IoU check and no position check, so a false positive counts exactly like a
> correct detection. The metric also assumes a person is present in every frame
> of a "with people" clip, which is not true frame-by-frame.
>
> What it therefore measures is **coverage and latency** — how often the model
> fires, and how fast. That is a useful signal, and the latency columns below
> are sound.
>
> On this particular comparison the **direction** below held up under
> ground-truth scoring: `Bedroom_Fall` at 38.2% → 67.3% here corresponds to
> 0.35 → 0.75 against hand-drawn boxes at IoU 0.3. That agreement is a fact
> about this run, not a property of the metric — the metric cannot distinguish a
> tight box from a loose one or from a hallucination, so it could not have
> established that on its own.
>
> The `Bedroom_Sit` / `TV_Lounge_2_Sit` "regressions" below **are** artifacts:
> `Bedroom_Sit` improves against real labels (0.83 → 0.88 at IoU 0.5).
>
> For recall comparisons use `score_heldout_objects.py --classes person`, which
> scores against hand-drawn boxes with IoU matching. Result, including the
> threshold sensitivity that dominates this run:
> [`reserved_heldout_posture_v5.md`](reserved_heldout_posture_v5.md).

Model: yolov8n_sage_merged_v5.pt, confidence threshold 0.4, imgsz 640
Clips: 10, total frames: 5850
Overall person-detection rate: 70.4%
Overall mean latency: 13.5 ms/frame (74.3 FPS)

## Breakdown

| Subset | Frames | Person detected % |
|---|---|---|
| Upright (standing/sitting clips) | 4241 | 79.8% |
| Falling / lying clips | 1609 | 45.6% |
| Held-out clips only (never trained on) | 406 | 74.1% |

## Per-clip

| Clip | Held out | Frames | Person detected % | Mean ms/frame | Median ms/frame | p95 ms/frame |
|---|---|---|---|---|---|---|
| Bedroom_Fall.mov | no | 623 | 67.3% | 16.5 | 12.6 | 17.4 |
| Bedroom_Sit.mov | no | 740 | 85.1% | 12.9 | 12.5 | 17.3 |
| Bedroom_Walk.mov | no | 449 | 100.0% | 13.2 | 12.9 | 16.9 |
| people_ground_mahaRoom.MOV | no | 947 | 100.0% | 12.8 | 12.4 | 16.8 |
| TV_Lounge_1_Fall.mov | no | 628 | 27.4% | 13.2 | 13.0 | 16.8 |
| TV_Lounge_1_Sit.mov | no | 593 | 81.5% | 13.2 | 12.9 | 17.2 |
| TV_Lounge_1_Walk.mov | yes | 406 | 74.1% | 13.3 | 13.0 | 17.0 |
| TV_Lounge_2_Fall.mov | no | 358 | 39.9% | 13.3 | 12.7 | 17.8 |
| TV_Lounge_2_Sit.mov | no | 581 | 29.1% | 12.9 | 12.4 | 17.0 |
| TV_Lounge_2_Walk.mov | no | 525 | 77.5% | 13.1 | 12.7 | 17.4 |

### 7b. Plain-language reading (written after the run; every figure is quoted from the tables above)

**Which detector to carry forward.** B (YOLO26n, A's exact recipe) is not distinguishable from A on any person set:
Δrecall −0.065 (heldout_objects, 52 vs 58 of 93), −0.032 (rotfix, 63 vs 66 of 93), +0.008 (reserved388_partial, 109 vs 107
of 249), 0.000 (round6_heldout, 50 vs 50 of 226), with overlapping 95% CIs everywhere. B's gains are on the 13-class val
split (re-val mAP50-95 0.3920 vs 0.3850) and on chair in round6_heldout (346 vs 326 of 443). B has one concrete
regression: **22 person false positives on Laying_Dim_HM, where A has 0**. One rendered frame (Laying_Dim_HM_000430) shows the
box on the pillow/bedding beside the person, not a loose box on the person (0 TP even at IoU 0.3). That is the
dark-bedroom condition this project cares most about, so **do not switch the deployed detector from A to B on this evidence.**
C was not trained (gate failed on recall vs A on eval/heldout_objects; see raw/gate.json).

**The bigger finding is not B; it is that A (v7) is not the best person detector this run measured.** On reserved388_partial,
v6 finds 145/249 vs A's 107/249 (non-overlapping CIs). Almost all of that is Bedroom_Fall (58/62 vs 21/62). Stock
yolo26s at conf 0.4 finds 153/249 with 0.02% empty-room FP (1/4101 frames). Stock yolo26n finds 50/97 on TV_Lounge_1_Fall,
the clip earlier rounds called unsolved, where A finds 18/97 and v6 17/97. Two caveats:
(1) the v6 file records v6 going blind on the unlabelled `laying_dim.MOV`, and round6_heldout Laying_Dim_HM is ≤3/153 for each of A, v6, B and stock yolo26n
so no checkpoint wins everywhere; (2) these are 7 of 11 clips of the 388-box set, with frames correlated within clips.
The earlier claim that v7 "detects exactly the same fall frames v5 and v6 did" (v7_results.md) rested on the as-stored
heldout_objects set, whose 20 Bedroom_Fall frames are sideways. With them upright, A is 8/20 and v6 19/20.

**Model or labels?** B misses 93% of the same person boxes A misses on reserved388_partial, 99% on round6_heldout and 85% on the
rotfix set. In the per-clip table the misses sit in the same clips (Bedroom_Fall, TV_Lounge_1_Fall, Laying_Dim_HM). A second
architecture trained on the same labels reproduces the same blind spots, which points to the training data, not the
architecture. The stock models support this: stock yolo26n (not trained on SAGE data) shares only 76% of A's misses on
reserved388_partial and recovers TV_Lounge_1_Fall. So on TV_Lounge_1_Fall the frames are evidently detectable, and the
fine-tuned series loses something the COCO prior had. On Laying_Dim_HM all four per-clip-scored models (A, v6, B, stock yolo26n; stock shares 98% of A's round6 misses)
fails. That looks like a property of those frames (the darkest set: round6 dark-tercile luma ≤ 65.3) or of how they were
labelled. Look at those labels before recording more footage.

**Enhancement:** not worthwhile under the pre-registered rule. Gamma brightening lowers stock yolo26n's bright-frame recall by
0.21–0.23 and does not raise dark-frame recall for any model.

**Pose:** after fixing the fall-window and denominator defects, yolo26s-pose@0.3 has the most fall TPs (30/37, CI [0.66, 0.91])
vs MediaPipe 23/37 ([0.46, 0.76]), with 4/27 vs 2/27 ADL false alarms. The intervals overlap, so this is suggestive, not
conclusive. YOLO26-pose needs a GPU to match MediaPipe's latency (on this laptop's CPU: 87.88 ms yolo26s / 44.39 ms
yolo26n vs MediaPipe 17.16 ms; on GPU 13.99 / 14.94 ms). Every clip missed by all backends was classified a heuristic miss with a person found in
≥97% of the window, so for those clips the fall heuristic, not the keypoint source, is the limit.

**Extra hand checks from this reading:** (a) open a few Laying_Dim_HM frames with their labels; no model gets above 3/153 there,
so the labels themselves are worth a look; (b) look at B's 22 Laying_Dim_HM person boxes (raw/preds/B_yolo26n_30ep__round6_heldout__c0.4__none.json);
(c) look at stock yolo26n's TV_Lounge_1_Fall detections (50/97) and check that they are on the person.

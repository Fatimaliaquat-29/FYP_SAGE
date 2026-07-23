# Validation Summary

- Date/time: 2026-07-15 20:54:35
- Total scenarios tested: 13
- Passed scenarios: 11
- Failed scenarios: 2
- Success rate: 84.6%
- Average processing time: 16.59 ms
- Average confidence: 0.57

## Per Scenario Results

### Standing
- Outcome: PASS
- Detection: No fall
- Expected posture: Standing
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Standing | Standing=12, Sitting=0, Lying=0, Unknown=0 | Mean body height=0.630 | Mean torso angle=0.00 | Mean hip height=0.480 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Standing_near
- Outcome: PASS
- Detection: No fall
- Expected posture: Standing
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Standing | Standing=12, Sitting=0, Lying=0, Unknown=0 | Mean body height=0.819 | Mean torso angle=0.00 | Mean hip height=0.474 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Standing_far
- Outcome: PASS
- Detection: No fall
- Expected posture: Standing
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Standing | Standing=12, Sitting=0, Lying=0, Unknown=0 | Mean body height=0.315 | Mean torso angle=0.00 | Mean hip height=0.490 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Standing_drift
- Outcome: PASS
- Detection: No fall
- Expected posture: Standing
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Standing | Standing=12, Sitting=0, Lying=0, Unknown=0 | Mean body height=0.567 | Mean torso angle=0.00 | Mean hip height=0.482 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Sitting
- Outcome: PASS
- Detection: No fall
- Expected posture: Sitting
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Sitting | Standing=0, Sitting=12, Lying=0, Unknown=0 | Mean body height=0.427 | Mean torso angle=0.00 | Mean hip height=0.450 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Sitting_near
- Outcome: PASS
- Detection: No fall
- Expected posture: Sitting
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Sitting | Standing=0, Sitting=12, Lying=0, Unknown=0 | Mean body height=0.555 | Mean torso angle=0.00 | Mean hip height=0.435 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Sitting_far
- Outcome: PASS
- Detection: No fall
- Expected posture: Sitting
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Sitting | Standing=0, Sitting=12, Lying=0, Unknown=0 | Mean body height=0.214 | Mean torso angle=0.00 | Mean hip height=0.475 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Walking
- Outcome: PASS
- Detection: No fall
- Expected posture: Standing
- Posture accuracy: 100.0%
- Important observations: Predominant posture: Standing | Standing=12, Sitting=0, Lying=0, Unknown=0 | Mean body height=0.630 | Mean torso angle=0.00 | Mean hip height=0.480 | Transitions=0 | Posture accuracy=100.0%
- Possible reasons for failure: None

### Slow lying
- Outcome: PASS
- Detection: No fall
- Expected posture: N/A
- Posture accuracy: N/A
- Important observations: Predominant posture: Lying | Standing=5, Sitting=0, Lying=7, Unknown=0 | Mean body height=0.527 | Mean torso angle=52.50 | Mean hip height=0.346 | Transitions=1
- Possible reasons for failure: None

### Fake fall
- Outcome: PASS
- Detection: No fall
- Expected posture: N/A
- Posture accuracy: N/A
- Important observations: Predominant posture: Standing | Standing=12, Sitting=0, Lying=0, Unknown=0 | Mean body height=0.596 | Mean torso angle=0.00 | Mean hip height=0.475 | Transitions=0
- Possible reasons for failure: None

### Empty room
- Outcome: PASS
- Detection: No fall
- Expected posture: N/A
- Posture accuracy: N/A
- Important observations: Predominant posture: Unknown | Standing=0, Sitting=0, Lying=0, Unknown=12 | Transitions=0
- Possible reasons for failure: None

### Fall
- Outcome: FAIL
- Detection: No fall
- Expected posture: N/A
- Posture accuracy: N/A
- Important observations: Predominant posture: Lying | Standing=2, Sitting=0, Lying=10, Unknown=0 | Mean body height=0.590 | Mean torso angle=78.45 | Mean hip height=0.280 | Transitions=1
- Possible reasons for failure: Threshold mismatch or missing posture evidence

### Fall_far
- Outcome: FAIL
- Detection: No fall
- Expected posture: N/A
- Posture accuracy: N/A
- Important observations: Predominant posture: Lying | Standing=2, Sitting=0, Lying=10, Unknown=0 | Mean body height=0.295 | Mean torso angle=78.45 | Mean hip height=0.390 | Transitions=1
- Possible reasons for failure: Threshold mismatch or missing posture evidence

## Distance Variant Posture Accuracy

| Scenario | Expected Posture | Posture Accuracy | Result |
|---|---|---|---|
| Standing_near | Standing | 100.0% | PASS |
| Standing_far | Standing | 100.0% | PASS |
| Standing_drift | Standing | 100.0% | PASS |
| Sitting_near | Sitting | 100.0% | PASS |
| Sitting_far | Sitting | 100.0% | PASS |
| Fall_far |  | N/A | FAIL |

## Overall Analysis

- Strengths: The pipeline uses scale-invariant joint angles as the primary classification signal and time/scale-normalized velocity for fall detection.
- Weaknesses: Heuristics are tuned to temporal sequences and depend on consistent landmark availability.
- False positives: 0
- False negatives: 2
- Recommended threshold adjustments: Tune ANGLE_STANDING_MIN, ANGLE_SITTING_MAX, FALL_AVG_VELOCITY_FLOOR, and FALL_ANGULAR_VELOCITY_FLOOR against recorded validation clips.

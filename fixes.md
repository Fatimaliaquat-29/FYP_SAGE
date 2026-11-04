# S.A.G.E. — Posture & Fall Detection Fix Plan

**Branch analyzed:** `fatima`
**Files in scope:** `src/posture/pipeline_utils.py`, `src/posture/posture_classifier.py`, `src/posture/posture_features.py`, `src/posture/lstm/lstm_dataset.py`
**Author:** Claude (code analysis), for Hussain / S.A.G.E. team

---

## TL;DR — Root Cause

Both bugs come from the **same underlying mistake**: the pipeline makes decisions using **raw normalized image-space quantities** (pixel-space distances and per-frame pixel displacement) as if they were real-world measurements. Neither is invariant to:

1. **Distance from camera** — a person 3 m away produces smaller normalized coordinates than the same person at 1 m, even in an identical pose.
2. **Frame rate** — fall "velocity" is computed as raw per-frame pixel displacement, never divided by elapsed time, so it silently assumes a constant FPS.

Fix strategy: replace distance-dependent features with **scale-invariant** ones (joint angles, and time/scale-normalized velocity) wherever possible, and use the distance-dependent ones only as a documented fallback.

---

## Fix A — Posture Classification (Standing vs Sitting)

### A.1 The problem

`pipeline_utils.py` (and a near-duplicate copy in `posture_classifier.py`) classifies posture mainly off `body_height`:

```python
# pipeline_utils.py, ~line 356
elif body_height >= 0.92 * effective_max_bh:
    raw_posture_label = "Standing"
elif body_height < 0.88 * effective_max_bh:
    raw_posture_label = "Sitting"
```

- `body_height` = pixel-space distance between shoulder-midpoint and ankle-midpoint, in MediaPipe's `[0,1]` normalized image coordinates.
- `effective_max_bh` = the *largest* `body_height` ever seen so far in the session (a running max that only grows, never resets or decreases).

Two failure modes follow directly:
- **Distance dependency:** if you're closer to the camera when the running max gets set, then step back while standing normally, `body_height` shrinks below `0.88 × max` → classified as **Sitting** while actually standing. This is the exact bug you reported.
- **Cold-start bias:** if the very first frames captured aren't a clean, camera-facing full-height view (occlusion, angle, partial frame), the whole session's calibration is wrong from the start and can't self-correct downward.

There's also a secondary, lower-impact issue: the "torso-only" fallback path (when legs are occluded) uses a fixed `hip_height > 0.55` cutoff, which is itself frame-composition dependent (assumes a specific camera framing/mount height).

### A.2 The fix — lead with joint angles, not distances

Joint angles are **scale-invariant**: a straight knee reads ~170–180° whether the subject is 1 m or 3 m from the camera. The codebase already computes `knee_angle` via `_compute_knee_angle()` but only uses it as a secondary check inside the Standing branch. There is **no `hip_angle`** yet, and it's easy to add with the same pattern.

**Add `_compute_hip_angle` next to the existing `_compute_knee_angle` in `pipeline_utils.py`:**

```python
def _compute_hip_angle(shoulder, hip, knee):
    """Angle at the hip joint: shoulder -> hip -> knee.
    ~170-180 deg when standing upright (torso in line with legs).
    ~70-110 deg when sitting (torso folded over thighs)."""
    if shoulder is None or hip is None or knee is None:
        return np.nan
    if any(np.isnan(v) for v in shoulder) or any(np.isnan(v) for v in hip) or any(np.isnan(v) for v in knee):
        return np.nan
    v1 = np.array(shoulder, dtype=float) - np.array(hip, dtype=float)
    v2 = np.array(knee, dtype=float) - np.array(hip, dtype=float)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < 1e-6 or n2 < 1e-6:
        return np.nan
    cos_theta = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_theta)))
```

**Rewrite the classification priority order** (inside `classify_posture_and_fall`, replacing the current Rule 2/3/4 block):

```python
# Compute both joint angles when hip/knee are visible (add near knee_angle calc)
if hp_ok and kn_ok:
    hip_angle = float(np.mean([
        a for a in [
            _compute_hip_angle(sh_l, hp_l, kn_l),
            _compute_hip_angle(sh_r, hp_r, kn_r),
        ] if not np.isnan(a)
    ])) if any(not np.isnan(a) for a in [
        _compute_hip_angle(sh_l, hp_l, kn_l), _compute_hip_angle(sh_r, hp_r, kn_r)
    ]) else np.nan
else:
    hip_angle = np.nan

row["hip_angle"] = hip_angle

ANGLE_STANDING_MIN = 155.0   # both knee & hip angle above this -> confidently Standing
ANGLE_SITTING_MAX  = 125.0   # either angle below this -> confidently Sitting

angles_available = not np.isnan(knee_angle) and not np.isnan(hip_angle)

if torso_angle >= 45.0 or (not lower_body_occluded and vertical_span < 0.40 * effective_max_span):
    raw_posture_label = "Lying"
    other_labels.append("horizontal_torso" if torso_angle >= 45.0 else "horizontal_span")
elif lower_body_occluded:
    # unchanged torso-only fallback (see A.3 note below)
    ...
elif angles_available and knee_angle >= ANGLE_STANDING_MIN and hip_angle >= ANGLE_STANDING_MIN:
    raw_posture_label = "Standing"
    other_labels.append("angle_standing")
elif angles_available and (knee_angle <= ANGLE_SITTING_MAX or hip_angle <= ANGLE_SITTING_MAX):
    raw_posture_label = "Sitting"
    other_labels.append("angle_sitting")
else:
    # Ambiguous angle zone, or knees/hips not confidently visible:
    # fall back to the existing body_height ratio heuristic as a secondary signal
    if body_height >= 0.92 * effective_max_bh:
        raw_posture_label = "Standing"
        other_labels.append("fallback_height_standing")
    elif body_height < 0.88 * effective_max_bh:
        raw_posture_label = "Sitting"
        other_labels.append("fallback_height_sitting")
    else:
        raw_posture_label = "Standing"
        other_labels.append("fallback_default")
```

This keeps the old logic **alive as a fallback** for the case where knees/hips are occluded (e.g. seated close-up, blanket covering legs) — it doesn't throw anything away, it just stops being the primary decision-maker.

> **Note on the numbers:** 155°/125° are reasonable starting points based on typical standing/sitting biomechanics, but MediaPipe joint noise varies by camera angle and mount height. Treat these as tunable constants — see the Validation Plan (Section C) for how to set them from your own footage instead of guessing.

### A.3 Fix the code duplication

`posture_classifier.py` (the offline/batch script) re-implements the **same** rule block independently of `pipeline_utils.py` (the live path), including the same magic numbers (`0.92`, `0.88`, `0.40`, `45.0`). Right now, fixing the bug in one file does **not** fix it in the other — that's how bugs like this survive a "fix" and come back later.

**Recommendation:** delete the duplicated logic in `posture_classifier.py` and have it call `pipeline_utils.classify_posture_and_fall()` row-by-row instead (looping over the DataFrame, feeding `previous_rows` as it goes). One implementation, one place to fix things.

### A.4 Follow-up: fix the LSTM training pipeline

Two problems here compound the heuristic bug rather than escaping it:

1. **Weak-supervision contamination.** `lstm_dataset.py` derives training labels straight from `posture_label` in `posture_output.csv` — which is produced by the *buggy* rule-based classifier. Training the LSTM on these labels teaches it to reproduce the same distance-confusion, just with extra steps.
   **Fix:** regenerate `posture_output.csv` with the corrected heuristic (Fix A.2) *before* rebuilding the LSTM dataset. Treat the corrected heuristic as your new (still imperfect, but much better) weak-supervision source.

2. **No scale/translation augmentation in synthetic data.** `_make_standing_kps()` / `_make_sitting_kps()` in `lstm_dataset.py` place landmarks at **fixed absolute coordinates** (e.g. standing hips always at `y=0.52`). The model only ever sees one camera distance and one framing for each class, so on real footage where the subject is closer, farther, or off-center, it has no reason to generalize correctly.
   **Fix:** add random scale (`0.6×–1.4×`) and translation jitter around the torso center when generating synthetic windows, so the model learns the *shape* of standing/sitting rather than *where on screen* it appears.

```python
def _augment_scale_translate(kps: np.ndarray, scale_range=(0.6, 1.4), shift_range=0.15) -> np.ndarray:
    """Apply random uniform scale + translation to a keypoint vector (in-place-safe)."""
    scale = np.random.uniform(*scale_range)
    shift_x = np.random.uniform(-shift_range, shift_range)
    shift_y = np.random.uniform(-shift_range, shift_range)
    out = kps.copy()
    # scale around frame center (0.5, 0.5), then shift
    for i in range(0, len(out), 2):
        if not np.isnan(out[i]):
            out[i] = (out[i] - 0.5) * scale + 0.5 + shift_x
        if not np.isnan(out[i + 1]):
            out[i + 1] = (out[i + 1] - 0.5) * scale + 0.5 + shift_y
    return out
```
Call this on each synthetic frame in `_make_standing_kps` / `_make_sitting_kps` / `_make_lying_kps` before adding noise.

---

## Fix B — Fall Detection Accuracy

### B.1 The problem

`_compute_velocity()` in `pipeline_utils.py` returns the raw pixel-space displacement of the hip midpoint between two consecutive rows — nothing else:

```python
return float(np.linalg.norm(
    np.array(curr_hip, dtype=float) - np.array(prev_hip, dtype=float)))
```

This is then compared against fixed constants:

```python
FALL_VELOCITY_THRESHOLD  = 0.05
FALL_AVG_VELOCITY_FLOOR  = 0.03
```

Same two problems as posture, plus a third one specific to fall detection:

- **Distance dependency:** identical real fall speed produces a smaller measured "velocity" the farther the person is from the camera — meaning falls farther from the camera are more likely to be **missed** (a false negative on the single most safety-critical event this system exists to catch).
- **Frame-rate dependency:** velocity is per-*frame*, not per-*second*. There's no division by elapsed time anywhere — `_compute_velocity` never touches `row["timestamp"]`. If the Jetson drops frames under load, or a test video's FPS differs from the live webcam's FPS, the same real motion produces different measured velocities, and the fixed thresholds silently stop being correct.
- **An already-computed, unused, scale-invariant signal is being ignored:** `torso_angle_delta` is computed every frame (`row["torso_angle_delta"] = torso_angle_delta`, line ~411) but is **never referenced** in the actual fall decision (`is_fall_motion` only looks at hip velocity). A real fall inherently involves the torso angle swinging rapidly from near-vertical to near-horizontal — that's a much more direct, and already scale-invariant, fall signature than hip translation alone.

Timestamps are stored consistently as `time.time()` epoch floats (confirmed in both `save_keypoints.py` and `pose_test.py`), so computing a proper `dt` is straightforward — the data needed for the fix is already being collected, it's just unused.

### B.2 The fix — normalize velocity by both time and body scale, and use the angle signal you already compute

**Rewrite `_compute_velocity` to return a scale- and time-normalized speed** (units: "body-heights per second" instead of "pixels per frame"):

```python
def _compute_velocity(previous_row: dict, current_row: dict) -> float:
    """Hip-center speed, normalized by elapsed time and by body scale.

    Returns speed in units of (body_height fractions) per second, so the
    same real-world fall speed reads the same regardless of camera distance
    or frame rate.
    """
    prev_pairs = _extract_keypoint_pairs(previous_row)
    curr_pairs = _extract_keypoint_pairs(current_row)
    if not prev_pairs or not curr_pairs or len(prev_pairs) <= 24 or len(curr_pairs) <= 24:
        return 0.0

    prev_hip = ((prev_pairs[23][0] + prev_pairs[24][0]) / 2.0,
                (prev_pairs[23][1] + prev_pairs[24][1]) / 2.0)
    curr_hip = ((curr_pairs[23][0] + curr_pairs[24][0]) / 2.0,
                (curr_pairs[23][1] + curr_pairs[24][1]) / 2.0)
    if any(np.isnan(v) for v in prev_hip) or any(np.isnan(v) for v in curr_hip):
        return 0.0

    raw_disp = float(np.linalg.norm(np.array(curr_hip) - np.array(prev_hip)))

    # 1. Time-normalize: convert to displacement-per-second.
    try:
        dt = float(current_row.get("timestamp", 0)) - float(previous_row.get("timestamp", 0))
    except (TypeError, ValueError):
        dt = 0.0
    if dt <= 0:
        dt = 1.0 / 30.0  # fallback: assume ~30 FPS if timestamps are missing/bad

    speed_per_sec = raw_disp / dt

    # 2. Scale-normalize: divide by current body_height (falls back to 1.0
    #    if body_height is unavailable, e.g. legs occluded).
    body_scale = current_row.get("body_height", np.nan)
    if body_scale is None or np.isnan(body_scale) or body_scale < 1e-3:
        body_scale = 1.0

    return speed_per_sec / body_scale
```

**Incorporate `torso_angle_delta` (also time-normalize it) as a second, independent fall signal**, combined with velocity via AND (both must agree — this is what should separate a real fall from, e.g., quickly sitting down):

```python
# time-normalize the existing torso_angle_delta into deg/sec
dt_for_angle = 1.0 / 30.0
if previous_rows:
    try:
        dt_for_angle = float(row.get("timestamp", 0)) - float(previous_rows[-1].get("timestamp", 0))
    except (TypeError, ValueError):
        pass
    if dt_for_angle <= 0:
        dt_for_angle = 1.0 / 30.0
torso_angular_velocity = torso_angle_delta / dt_for_angle  # deg/sec
row["torso_angular_velocity"] = torso_angular_velocity
```

```python
# New fall trigger condition (replaces the velocity-only is_fall_motion):
is_fall_motion = (
    fast_frame_count >= FALL_SUSTAINED_COUNT
    and avg_recent_velocity > FALL_AVG_VELOCITY_FLOOR       # now body-heights/sec
    and torso_angular_velocity > FALL_ANGULAR_VELOCITY_FLOOR  # deg/sec, new
)
```

### B.3 Re-tune the thresholds — the units changed, so the old numbers no longer apply

`FALL_VELOCITY_THRESHOLD = 0.05` and `FALL_AVG_VELOCITY_FLOOR = 0.03` were tuned (however loosely) against *pixels-per-frame*. After B.2, velocity is in *body-heights-per-second*, so these numbers are meaningless and need to be re-derived — don't just carry them over. Do not guess new constants; derive them from your own footage (see Validation Plan below). `FALL_ANGULAR_VELOCITY_FLOOR` is a brand new constant with no prior value at all — same treatment.

---

## C — Validation Plan (so you can *prove* the fix worked, not just hope)

Right now there's no labeled test set, so there's no way to numerically confirm any fix actually helps — everything is "looks better" by eyeballing frame timelines. Before/after this fix, record a small validation set:

1. **Distance sweep (posture):** stand and sit at 3 distances from the camera (~1 m, ~2 m, ~3.5 m), ~10 s each, directly facing the camera. Run both old and new classifiers on this clip. The old one should show `Standing→Sitting` mislabels appear at the farther distances; the new one shouldn't.
2. **Off-angle sweep (posture):** repeat at a couple of camera angles (not just face-on) if your final camera mount won't always be head-on.
3. **Fall clips at multiple distances (fall detection):** a few staged/controlled falls (onto a mat, obviously — don't actually hurt anyone) at near/mid/far distance, plus a few *non-fall* fast movements (sitting down quickly, bending to pick something up) to check false-positive rate.
4. Use these clips to **pick** `ANGLE_STANDING_MIN`, `ANGLE_SITTING_MAX`, `FALL_AVG_VELOCITY_FLOOR`, and `FALL_ANGULAR_VELOCITY_FLOOR` empirically (e.g. plot the normalized-velocity distribution for fall vs. non-fall windows and pick a threshold that separates them), instead of hand-picking numbers.

This validation set is also exactly what you want anyway for the FYP writeup/demo — "accuracy at varying distance" is a much stronger evaluation story than "works in my test video."

---

## D — Rollout Order

Doing these out of order will waste time (e.g. retraining the LSTM before fixing the labels it learns from). Suggested order:

1. Add `_compute_hip_angle`, rewire posture rules (A.2).
2. Fix `posture_classifier.py` duplication → delegate to `pipeline_utils` (A.3).
3. Fix `_compute_velocity` + add angular-velocity signal (B.2).
4. Record the validation clips (Section C) and tune the new thresholds against them (A.2 angle thresholds, B.3 velocity/angular thresholds).
5. Re-run the fixed pipeline over your existing raw footage to regenerate `posture_output.csv` with corrected labels.
6. Add synthetic-data augmentation to `lstm_dataset.py` (A.4.2).
7. Rebuild the LSTM dataset from the corrected labels (A.4.1) and retrain.
8. Compare LSTM accuracy before/after against the validation set from Section C.

---

## Summary Table

| Issue | File(s) | Root cause | Fix |
|---|---|---|---|
| Standing misread as Sitting | `pipeline_utils.py`, `posture_classifier.py` | `body_height` ratio vs. running max — distance-dependent | Lead with `knee_angle` + new `hip_angle`; keep height ratio as occlusion fallback |
| Rule duplication | `posture_classifier.py` | Same logic reimplemented in two places | Delegate to `pipeline_utils.classify_posture_and_fall` |
| LSTM inherits posture bug | `lstm_dataset.py` | Labels sourced from buggy heuristic | Regenerate labels after Fix A; add scale/translation augmentation |
| Falls missed at distance | `pipeline_utils.py` | Raw pixel velocity — no scale normalization | Divide by `body_height` |
| Falls missed on frame drops | `pipeline_utils.py` | Raw per-frame velocity — no time normalization | Divide by real `dt` from timestamps |
| Unused fall signal | `pipeline_utils.py` | `torso_angle_delta` computed but never used | Add as second, AND-combined fall condition |
| Unvalidated thresholds | `pipeline_utils.py` | Constants hand-picked, no labeled test set | Derive from recorded validation clips (Section C) |

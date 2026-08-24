# Gait/Fall-Risk Data Availability Assessment

Per `docs/IMPLEMENTATION_PLAN.md` Section 3's instruction to do an "honest
data-availability assessment" before investing further in modeling. Short
answer: **no usable gait dataset exists in this project, and none of the
validation below should be mistaken for clinical validation.**

**Standing caveat, true of every section below**: every real clip
referenced in this document -- the original 28 `test_footage/` clips and
the 10 newer `GAIT_Analysis_Test_Footages/` clips alike -- is a
self-recorded video of a **single (N=1) subject**. Nothing in this
document's findings, fixes, or "verified"/"validated" language
generalizes to a population, a different body type, age group, or gait
style. This was already stated explicitly elsewhere in this project
(`docs/GAIT_CALIBRATION_DATASET_PLAN.md` Section 9,
`docs/GAIT_ANGLE_NOISE_INVESTIGATION_REPORT.md` Section D) but had not
been stated in THIS document, which is the one most sessions have added
real-footage findings to -- added here so the caveat is not accidentally
absent from the one place a reader is most likely to be looking at
validation claims.

## 1. What data exists, and why none of it fits

| Source | What it actually is | Why it doesn't work for gait analysis |
|---|---|---|
| UR Fall Dataset (`data/ADL`, `data/Fall`) | Short RGB clips (ADL: ~150-400 frames each) of individual activities-of-daily-living or a single fall | Centered on one activity/fall event, not an extended walking bout; no fall-risk label of any kind exists for these subjects |
| UP-Fall Dataset | 3D skeleton data, multiple subjects, multiple fall activities | Same issue: short activity-centered clips, not gait sequences |
| LeFD (Le2i) | 130 annotated videos (96 falls + 34 ADL) | Same issue, plus annotations are fall-timing labels (fall_start/fall_end), not gait-quality or fall-risk labels |
| `test_footage/` (Sanawar + Hussain sets) | Labelled posture/fall clips used for TCN/LSTM/RF evaluation | Same issue: built for per-frame posture/fall labels, not walking-bout gait quality; some clips (e.g. `Moving_in_out_frame`) contain walking but with no gait-quality ground truth |

**Conclusion**: there is no dataset in this repository, and none was found
to exist among the project's already-integrated sources, containing (a)
extended walking sequences and (b) any fall-risk or gait-quality ground
truth label. This confirms `docs/IMPLEMENTATION_PLAN.md`'s own prediction
("None of the existing datasets... are built for this").

**Not done in this session** (out of scope for a code-focused
implementation pass, and explicitly called out in the plan as something to
decide deliberately, not assume): searching for an external public gait
dataset (e.g. from Parkinson's/elderly-gait research) or planning new
self-recorded walking footage. Both remain real options for making this
module's validation genuine rather than a proxy — see "Next steps" below.

## 2. What validation *was* done this session, and its real limits

Since no real gait-risk-labeled data exists, validation followed the
plan's own suggested fallback: synthetic steady-vs-unsteady walking as "a
rough proxy," plus a smoke test against real (but gait-unlabeled) footage.

### 2a. Synthetic steady vs. unsteady walking

Two synthetic 210-frame (7s) walking sequences were generated
(`GaitRiskAssessor` has no test-only code path — the *inputs* were
synthetic pose keypoints, run through the exact same production code):
"steady" (speed=0.18, low stride/speed jitter, minimal sway) and
"unsteady" (speed=0.07 — deliberately slower — higher stride-timing
jitter, larger postural sway). Result: `assess_risk()` scored unsteady
higher (0.518) than steady (0.443), and every individual signal moved in
the expected direction (unsteady: slower speed, higher stride-interval CV,
present sway; steady: faster speed, lower CV, no sway detected since it
never stopped translating long enough to qualify).

**Three real bugs were found and fixed via this process** (not just "the
code ran"):
1. Position-based features (`compute_walking_speed`, `compute_postural_sway`)
   initially reused `lstm_features.normalize_frame`'s hip-CENTERED
   coordinates (each frame independently re-centered on its own hip
   midpoint) — correct for posture classification, but this makes hip
   position identically (0,0) in every frame by construction, silently
   destroying the exact translational signal these two gait features need.
   Fixed by adding `_torso_scaled_hip_track()`, which scales by torso
   length (camera-distance invariance, same idea as `normalize_frame`)
   without re-centering each frame.
2. Finite-differencing raw (even lightly noisy) position into velocity
   amplifies that noise significantly at 30fps — without smoothing, this
   noise floor dominated the actual walking-speed signal in early
   validation runs badly enough that a synthetic "slower" walker read as
   faster than a "steady" one. Fixed by adding a NaN-aware centered
   moving-average smoothing step inside `_torso_scaled_hip_track`. This is
   a genuine production-code robustness fix (real MediaPipe tracking
   jitter on live video would cause the same problem), not just a
   test-fixture patch.
3. `gait_risk.py::_stride_cv_risk`'s risk-mapping threshold originally
   reused the ~5% figure informally associated with IMU stride-*time*
   variability literature. This module's stride-regularity signal is a
   video-derived spatial-oscillation-peak proxy, not the same
   measurement, and empirically produces values roughly 4-6x larger
   (~0.15-0.35) — reusing the literature's number saturated the risk
   function near 1.0 regardless of actual regularity, silently destroying
   the signal's ability to discriminate. Fixed by recentering the
   threshold on this proxy's own observed scale (documented in the code
   as a scale-matching choice, explicitly NOT a clinical threshold).

A fourth and fifth issue were found and fixed in the *validation script*
itself (shared mutable RNG state across scenarios producing
non-reproducible comparisons, and default synthetic-position noise large
enough to jitter derived joint angles by ~20 degrees against an 18-degree
decision gap) — these don't affect `src/gait/`'s production code, only the
one-off validation script used to check it.

### 2b. Sit-to-stand: smooth vs. shaky

A synthetic sitting->standing transition was generated two ways: smooth
(monotonic angle ramp) and shaky (same ramp plus jitter causing
direction-reversals). Result: shaky scored higher risk (0.566) than smooth
(0.287), driven mostly by the reversal count (4 vs. 0) as intended.

### 2c. Smoke test on real (but unlabeled) ADL keypoint sequences

8 real UR-Fall-Dataset ADL sequences (already extracted in
`data/processed_keypoints/pose_keypoints.csv`, 150-230 frames each) were
run through `GaitRiskAssessor.assess_risk()` unmodified. **Zero crashes**,
risk scores in a sensible 0.30-0.52 range, 2-4 of 4 signals available
depending on the clip's actual content (as expected — not every clip
contains a detectable walking bout or sit-to-stand event). This confirms
the module survives real, noisy human-tracking data, but **there is no
ground-truth risk label for any of these subjects, so this is a shape/
crash/plausibility check only — it says nothing about whether the risk
scores are accurate.**

## 3. What this validation does NOT establish

Be precise about the limits here, echoing the plan's own honesty mandate:

- **No sensitivity/specificity numbers exist for this module**, because no
  dataset with actual fall-risk outcomes was available to compute them
  against. Any accuracy claim beyond "moves in the expected direction on
  synthetic data" would be fabricated.
- **All risk-mapping thresholds in `gait_risk.py` are heuristic**, chosen
  either to echo (loosely) the reviewed literature's *direction* or to keep
  this proxy's own sigmoid mappings from saturating — never fit to real
  outcome data, because none exists. Every one is marked
  `"calibrated": False` in `assess_risk()`'s own signal output.
- **The synthetic walking/sit-to-stand generators are simplified 2D
  kinematic approximations**, not motion-captured or real human data —
  they were good enough to catch three real implementation bugs (a
  meaningful result), but passing this validation is a floor, not a
  ceiling, on correctness.

## 4. Next steps (real, not just implied)

1. Either find a public elderly-gait/fall-risk dataset (e.g. from
   Parkinson's or geriatric-gait research communities) with actual outcome
   labels, or record new self-labeled walking footage (normal vs.
   deliberately unsteady/shuffling, per the plan's own suggestion) —
   without one of these, `risk_score`'s absolute scale and thresholds
   cannot be honestly validated beyond what this document already claims.
2. Re-run this module's `_stride_cv_risk`/`_sway_risk`/`_speed_risk`
   threshold choices once real data exists — they are placeholders chosen
   to be non-degenerate on synthetic data, not fitted to anything real.
3. Consider whether `compute_stride_regularity`'s ankle-height-peak
   detection is robust enough on real (occlusion-heavy, camera-angle-
   varying) footage — the synthetic validation used a clean, front-facing
   synthetic walker; real footage will be messier.

## 5. Follow-up debugging/optimization pass (a later session)

Asked to specifically debug and optimize this module further, beyond the
three bugs already listed above. Found and fixed two more real issues,
plus one genuine (if modest) performance win:

1. **`compute_sit_to_stand`'s left/right joint selection never actually
   fell back to the other side on occlusion.** It used
   `_joint_point(pairs, LEFT) or _joint_point(pairs, RIGHT)` -- but a
   Python tuple is truthy even when it holds `(nan, nan)`, so the `or`
   only ever triggers when the landmark index is literally out of range,
   which never happens. A window with a perfectly good RIGHT hip angle but
   an occluded LEFT one silently computed NaN for that frame instead of
   using the visible side. Fixed to compute both sides and average
   whichever pass `is_landmark_valid()`, mirroring
   `pipeline_utils.py::_classify_heuristic`'s own knee-angle/hip-angle
   averaging convention rather than a one-sided pick. This also means
   `is_landmark_valid` (previously imported but never actually called,
   despite a docstring claiming otherwise) is now genuinely used. Covered
   by a new regression test
   (`test_sit_to_stand_detected_despite_one_sided_occlusion`).
2. **Every risk-mapping function was computed twice per signal** in
   `GaitRiskAssessor.assess_risk()` -- once to build the signal entry,
   once more for the weighted sum. Harmless numerically (deterministic,
   pure functions) but wasteful and a real maintenance risk if the two
   call sites were ever edited independently and drifted apart. Refactored
   `assess_risk()` into a single data-driven loop over `_SIGNAL_SPECS`
   that computes each signal's risk contribution exactly once.
3. **Redundant window parsing, found via profiling.** Each of the four
   signal functions independently re-parsed the same window into raw
   `(T, 66)` keypoints (`gait_features._raw_keypoint_array`) -- up to 3
   separate full-window parses per single `assess_risk()` call.
   `compute_walking_speed`/`compute_postural_sway`/
   `compute_stride_regularity`/`compute_sit_to_stand` now all accept an
   optional pre-parsed array (`_hip_track`/`_raw`), and `assess_risk()`
   computes it once and shares it across all four. Measured latency:
   ~143ms -> ~128ms for a 300-frame window (warmed up, excluding one-time
   `scipy` import cost) -- a real but modest win, consistent with this
   not being a per-frame hot path (`assess_risk()` runs once per
   multi-second window, not once per video frame like the posture
   classifiers). All 19 gait tests pass byte-identically before and after
   both the correctness fixes and this optimization.

## 6. Angle-noise ambiguity fix + provisional footage-based validation (a later session)

Asked to investigate a known remaining limitation: `reversal_count` in
`compute_sit_to_stand` could reach spuriously high values (e.g. 12) purely
from landmark noise, with no genuine hip translation, on
`Sitting_Lying_FewLandmarks.MOV`. Root-caused (not assumed) via full
signal tracing to single-sided landmark visibility (one of
shoulder/hip/knee dropping out on one side only) during which the
resulting single-sided hip-angle estimate has sub-1.3-degree frame-to-frame
noise that nonetheless flips sign almost every frame -- magnitude alone
cannot separate this from genuine shakiness (a real shaky-transition test
fixture has an overlapping 0.6-degree delta). Fixed by gating
`_count_reversals` on a `confident` mask (both landmark sides valid),
reusing the already-computed `valid_l`/`valid_r` arrays -- no new
computation beyond a boolean AND. See `src/gait/gait_features.py` and
`tests/test_gait_risk.py::SitToStandAngleNoiseConfidenceTests` for detail.
Zero effect on `walking_speed`/`postural_sway`/`stride_regularity`,
zero change to any real-footage clip outside the 3 that showed the
noise-driven reversal pattern, all previously-fixed real-footage behavior
(including the fall-adjacent translation guard and `MIN_AMBULATION_PATH`
fix) unchanged.

**This same session used the project's existing 28 `test_footage/` clips
(the same footage previously used for LSTM/TCN/RF posture-classifier
evaluation) for further provisional checks.** Restating the same limits as
throughout this document: these clips were built for per-frame
posture/fall labels, not gait-quality or fall-risk ground truth, so this
remains structural/behavioural/plausibility/regression checking only -- no
sensitivity/specificity/accuracy number is claimed, and none of the
existing risk thresholds were changed to make any result "look better."
Two real, pre-existing (not introduced this session) limitations were
found this way and are recorded as open items rather than patched under
time pressure, precisely to avoid the kind of unvalidated threshold change
this document has warned against since Section 3:

1. **Geometric degeneracy: hip angle alone cannot distinguish a deep
   bend/squat from a shallow chair sit-to-stand.** Both produce the same
   torso-hip-knee angle signature, so `compute_sit_to_stand`'s primary
   (confirmed-sit-run) path legitimately fires on several `Bend_pickup_*`
   clips whose ground truth never contains a "Sitting" state. Confirmed
   present identically in both the pre- and post-fix validation runs, so
   this is unrelated to the angle-noise fix above.
2. **`compute_walking_speed`'s ambulation gate (`MIN_AMBULATION_PATH`/
   `MIN_AMBULATION_COHERENCE`) does not check translation direction.** A
   coherent, high-net-displacement, purely *vertical* hip drop (e.g.
   kneeling down) satisfies the same gate as genuine horizontal
   locomotion, so `Kneeling.MOV`'s kneel-down segment reads as slow
   walking, disproportionately raising overall risk. A horizontal-
   dominance check on the already-computed hip track is the natural fix,
   but the corpus only contains two short (2-3s) genuine walking bursts --
   not enough to validate that such a gate wouldn't also suppress
   recall on off-axis genuine walking, so it was deliberately left
   unfixed pending new walking footage rather than shipped unvalidated.

Full detail, the complete real-footage categorization, edge-case
breakdown, and recording plan for closing both gaps are in the session's
own final report (not duplicated here to avoid drift between the two
documents).

## 7. New GAIT_Analysis_Test_Footages corpus: validation, one confirmed
##    bug found and fixed, and honest status of the two prior open gaps
##    (a later session)

10 new self-recorded clips (`test_footage/GAIT_Analysis_Test_Footages/`,
each with a `start_time,end_time,state,label` GT CSV in the existing
convention) were added specifically to close the two gaps Section 6 left
open pending footage: `Deep_Bend.mov`/`Shallow_Bending.mov` (bend/squat
vs. sit), `Diagonal_Walk_1.mov`/`Lateral_Walk.mov`/`Stride*.mov` (walking
direction at multiple camera angles / genuine gait signals generally).
Every clip was run through the actual extraction+assessment pipeline
(`benchmarks/validate_new_gait_footage.py`) and cross-referenced against
its GT CSV.

**Gap 2 (walking-direction gate) -- now closed.** `MIN_HORIZONTAL_
DOMINANCE_RATIO=1.0` was validated against 6 real walking clips spanning
3 camera angles (lateral, diagonal, toward-camera) and does not
over-suppress genuine walking recall at any of them -- see that
constant's own docstring in `gait_features.py` for the full per-clip
ratio/recall breakdown. No threshold change was made; this closes the
gap with evidence rather than changing the number.

**Gap 1 (bend/squat vs. sit geometric degeneracy) -- partially
characterized, still open, NOT silently claimed fixed.**
`Shallow_Bending.mov` (a sustained waist bend, legs straight, GT
explicitly "NOT sitting") never once produces a spurious `sit_to_stand`
detection across its whole 15.4s -- a genuine positive result, consistent
with a shallow bend's hip angle staying above the sitting threshold.
`Deep_Bend.mov` (a sustained deep bend/kneel, GT again explicitly "NOT
sitting", 5.5-15.5s) is messier: MediaPipe tracking during the sustained
kneel is heavily occluded (ankle visibility 0.54 over the clip), and one
90-frame window (7.1-10.2s, squarely inside the "sustained bend" GT
span, nowhere near the real 15.5-16.8s "Getting up" event) produces a
spurious `sit_to_stand` detection (duration=1.73s, reversal=0). Traced to
root cause (not assumed): every frame in both the "confirmed sit" and
"confirmed stand" reference runs this detection anchors on has ZERO
double-sided landmark confidence (`both_sides_confident` is False for
100% of both runs' frames) -- i.e. the detection is built entirely from
single-sided estimates during severe self-occlusion, and the module's own
`reliability` metadata correctly flags this: 0.038 (3.8%), far below any
other real detection's reliability seen this session. This is consistent
with -- not a new violation of -- this project's own prior, disclosed
design boundary (`gait_risk.py`'s own docstring: `reliability` is
transparency metadata, deliberately not wired into `risk_score` or any
availability gate, "left as an explicit, disclosed decision point for a
future session"). Turning `reliability` into a hard gate now would be
exactly that deferred, out-of-scope decision, not a small fix to this
specific finding.

**Follow-up (a later session): this specific occlusion-driven false
positive fixed, WITHOUT a `reliability` threshold.** Comparing the
implicated `Deep_Bend.mov` window against a genuine primary-path
detection with comparable single-sidedness (`SitFloor_lowKeypoints.MOV`,
stand-run both-sided-confidence fraction 0.44) revealed the actual
distinguishing signal: in `SitFloor_lowKeypoints.MOV`, the SAME side
(right) attests BOTH the sit-run and stand-run (100%/44% coverage, real
partial occlusion, one side stays reliably visible); in `Deep_Bend.mov`'s
false positive, the sit-run was covered ENTIRELY by the right side while
the stand-run was covered ENTIRELY by the left side -- the two "confirmed"
states share NO common corroborating side. Measured across all 24
primary-path detections in the project's full real-footage corpus (8
clips, old + new), every genuine one has `both_sides_confident > 0` in
both anchor runs (lowest 0.39); only `Deep_Bend.mov`'s two false
positives are entirely single-sided in both runs, and only they switch
which side provides coverage between the two states. Fixed by adding an
anchor-run side-switching guard to `compute_sit_to_stand`'s primary path:
rejects only when BOTH anchor runs are entirely single-sided AND share no
common side -- narrower than, and orthogonal to, both the existing
`reliability` metric and the `MIN_STAND_HIP_RISE` guard. A first, broader
attempt (reject whenever either anchor run has zero both-sided-confident
frames, without the side-sharing check) was tried and rejected: it broke
two existing tests that deliberately depend on a real, different, and
already-supported scenario -- one side occluded for an ENTIRE clip, with
the other side reliably covering both phases (documented as a dead end in
the guard's own code comment, not silently discarded). Verified: the
`Deep_Bend.mov` spurious detection (dur=1.73s, reversal=0,
reliability=0.038) is now rejected; `SitFloor_lowKeypoints.MOV`'s genuine
detection and every other of the 24 real primary-path detections in the
full corpus are unaffected (see `benchmarks/regression_check_old_corpus_
sts.py`'s output for exact before/after duration/reversal values). Two
new regression tests added
(`SitToStandAnchorRunSideSwitchingGuardTests`).

**Net honest status of Gap 1: still open, but narrower.** `Deep_Bend.mov`
still produces detections near its real "Getting up"/"Standing" span
(dur=0.14s, reversal=2, reliability=1.0 -- fully both-sided-confident,
unaffected by this fix, since these runs do NOT switch sides) that don't
precisely align with the GT's 15.5-16.8s "Getting up" window. These are
NOT the occlusion-driven false positive this follow-up fixed -- they are
the SAME originally-hypothesized geometric degeneracy (a sustained,
well-tracked bend/kneel's hip angle can legitimately cross both
thresholds in ways hip-angle-alone geometry cannot cleanly resolve from a
genuine transition), still unsolved, still requiring either a second
discriminating signal or footage that isolates a deep bend held with
full landmark confidence (this corpus's one deep-bend clip happens to
also be heavily occluded, confounding the two mechanisms). The
originally-hypothesized mechanism and the occlusion mechanism turned out
to be separable and were fixed/characterized independently, rather than
one fix accidentally papering over both.

**One real bug found and fixed this session (not one of the two
pre-planned gaps -- found by tracing the actual pipeline output against
the new footage's GT, not assumed):** `MIN_STAND_HIP_RISE` (added in a
prior pass, cited in its own docstring as derived from `Sit_Stand_1.mov`/
`Sit_Stand_2.mov`/`Deep_Bend.mov`) was wired into `compute_sit_to_stand`'s
PRIMARY (confirmed-sit-run) path only. Running the actual pipeline
against `Sit_Stand_2.mov` -- the exact clip that guard's docstring cites
as its own motivating evidence -- showed the identical spurious detection
its docstring claims is fixed (duration=0.895s, reversal=18, during the
GT `Sitting` span) still firing, because in the specific implicated
window `compute_sit_to_stand` found no CONFIRMED sit run at all (the
reclining motion's hip angle only reaches the 125-143 dead zone, never
the full sitting floor for `_STATE_CONFIRM_FRAMES` straight frames) and
therefore fell through to the FALLBACK path
(`_detect_fast_shallow_transition`), which had no rise guard of its own.
Measured directly: trough-to-standing-run rise was 0.030-0.031
torso-lengths in the implicated window, far below `MIN_STAND_HIP_RISE`'s
own 0.08 threshold. Fixed by adding the identical `_hip_vertical_rise`
guard to the fallback path (see that function's guard #5 docstring in
`gait_features.py`). Verified: the spurious `Sit_Stand_2.mov` detection
is now correctly rejected (`None`), and the fallback path's one genuine
real reference (`SitFast_GetupFast.MOV`) is still recovered unchanged
(duration=0.216s, matching the pre-fix value exactly). Two new regression
tests added (`SitToStandFallbackHipRiseGuardTests`); three pre-existing
synthetic test fixtures (`_double_sit_to_stand_window`,
`_n_frame_gap_primary_path_window`, `_sustained_held_bend_window`) were
also found to be stale -- written before `MIN_STAND_HIP_RISE` existed, so
they modeled zero hip rise on their "genuine stand" segments and were
failing at the START of this session, for a reason unrelated to what each
actually tests -- updated to model a real rise via the existing
`_hip_cy_for_angle` helper, consistent with how every other sit-to-stand
fixture in the suite already does it.

**Other signals checked against the new corpus, no issues found:**
`compute_stride_regularity` never fabricates a signal during non-walking
segments of any new clip (correctly absent during `Deep_Bend`/
`Shallow_Bending`'s static holds), and produces plausible, non-degenerate
cadence values (53-193 steps/min) across all 6 walking clips including
the deliberately irregular ones (`Stride_Inconsistent_Pace.mov`,
`Stride_Pause.mov`) -- higher CV on those clips than on the more regular
`Stride.mov`/`Diagonal_Walk_1.mov`, moving in the expected direction.

## 8. Triage of the 12 open issues from the prior session's assessment
##    (a still-later session) -- Group B recording spec

The prior session's assessment sorted its 12 open findings into two
groups: those fixable this-session with real code/test work (Group A --
see the module's own docstrings and `tests/test_gait_risk.py` for what was
done: a nearest-valid-frame fallback for guard #5's hip-rise reference, a
verified-not-just-accepted re-check of `compute_postural_sway`'s tiling
harmlessness, a confirmed-accurate disclosure check on
`_drop_runs_after_long_gap`'s index-0 blind spot, and a strengthened
regression test for the single-transition-per-window contract), and those
that explicitly must NOT be patched with existing clips or synthetic data
(Group B) because they need footage or outcome data this project does not
have. This section is the honest supporting work for two Group B items:
writing down EXACTLY what footage would close them, rather than
attempting a fix with what's on hand.

**Do not treat either spec below as already fulfilled by any existing
clip.** Every clip currently in `test_footage/` (including
`GAIT_Analysis_Test_Footages/`) was checked against both specs while
writing them; none satisfies either one -- see the "why existing footage
doesn't already cover this" note under each.

### 8.1 Recording spec: a second camera angle for sit-to-stand

**Closes**: the camera-angle-dependence gap (`Sit_Stand_AnklesInvisible.MOV`,
old corpus -- a GT-confirmed sitting period, 1-4.9s, whose hip_angle never
drops below ~156 degrees, well above `_HIP_ANGLE_SITTING_MAX=125`, at that
clip's specific camera framing -- see `docs/GAIT_CODE_REVIEW.md` finding
#11). `Sit_Stand_1.mov`/`Sit_Stand_2.mov` (this project's newest sit-to-stand
references) are front-on, the SAME general framing as the working
reference clips -- they add repetition, not a new angle, so they cannot
tell us whether `_HIP_ANGLE_SITTING_MAX`/`_HIP_ANGLE_STANDING_MIN` (both
2D-image-space angle thresholds) generalize to a different camera
position.

| Field | Spec |
|---|---|
| Subject | Same subject as the existing sit-to-stand clips (for a same-subject, different-angle comparison -- isolates the camera-angle variable from a body-proportion variable) |
| Camera position | **Side-on / profile view** (~90 degrees from the front-on framing already used in `Sit_Stand_1.mov`/`Sit_Stand_2.mov`), ~1.5-2m from the chair, camera height at approximately seated-hip height |
| Chair | Same chair (or a chair of the same approximate seat height) used in the existing sit-to-stand clips, so seat-height is held constant and camera angle is the only isolated variable |
| Lighting | Normal indoor lighting, consistent with the existing corpus (no specific lighting manipulation needed -- this gap is about geometry, not landmark visibility) |
| Scenario | Standing -> sit down -> hold seated (>=3s, enough to form a `_STATE_CONFIRM_FRAMES`-long confirmed sitting run even from a possibly-harder-to-read angle) -> stand up -> hold standing |
| Duration | 8-12s total (matches `Sit_Stand_1.mov`'s 7.8s / `Sit_Stand_2.mov`'s 14.9s order of magnitude) |
| Repetitions | >= 3, to distinguish "this angle genuinely changes the threshold" from "this one take happened to be ambiguous" |
| Ground truth | Same `start_time,end_time,state,label` CSV convention already used by every clip in `test_footage/` |
| What it would let a future session do | Directly measure hip_angle at this new camera angle during a GT-confirmed sit, the same way `Sit_Stand_AnklesInvisible.MOV` was traced this project's own real-footage way (not assumed) -- either confirms `_HIP_ANGLE_SITTING_MAX`/`_STANDING_MIN` generalize across at least these two angles, or gives a second real measurement to characterize how much they'd need to vary by viewing angle |

### 8.2 Recording spec: a deep bend held with full, unoccluded landmark confidence

**Closes**: isolates the ORIGINALLY-hypothesized bend/squat-vs-sit
geometric degeneracy (hip-angle alone cannot distinguish a deep bend from
a genuine sit) from the DIFFERENT, occlusion-driven mechanism this
project already found and fixed on `Deep_Bend.mov` (an anchor-run
side-switching false positive, root-caused to severe self-occlusion --
ankle visibility 0.54, hip 0.86 -- during that specific sustained kneel).
`Deep_Bend.mov` cannot answer the geometric question because its own
occlusion confounds it; a well-tracked deep bend is needed to test the
angle-alone hypothesis on its own.

| Field | Spec |
|---|---|
| Subject | Same subject as `Deep_Bend.mov`, for comparability |
| Camera position | Front-on, ~2-2.5m distance -- far enough back that a full standing-to-bent silhouette (head to ankles) stays in frame throughout, closer than `Deep_Bend.mov`'s apparent framing if that clip cropped the lower body during the kneel (visually confirm ankles/knees stay in-frame during a test recording before the real take) |
| Lighting | Bright, even, frontal lighting -- specifically to maximize MediaPipe landmark-visibility confidence on BOTH left and right shoulder/hip/knee throughout the bend, not just at the standing start/end. This is the one lighting-sensitive spec in this document, precisely because the gap being closed is about confidence, not geometry, on the occlusion side, even though the SIGNAL being tested (hip angle) is geometric |
| Surface / clothing | Fitted (non-baggy) clothing at the hip/knee, matte flooring with contrast against footwear -- both known MediaPipe landmark-confidence aids, not new project-specific requirements |
| Scenario | Standing -> bend forward at the waist to a DEEP angle (comparable depth to `Deep_Bend.mov`'s own bend, not a shallow one like `Shallow_Bending.mov`) WITHOUT kneeling (a standing deep bend keeps both legs' landmarks more consistently in-frame than a kneel does) -> hold the deep bend >= 5s -> stand back up |
| Duration | 10-15s total, with the held-bend portion specifically >= 5s (long enough to form multiple `_STATE_CONFIRM_FRAMES`-long confirmed-sitting-range runs if the hypothesis is correct, not just one marginal one) |
| Repetitions | >= 3 |
| Ground truth | Same convention, with the held-bend period explicitly labeled "NOT sitting" exactly as `Deep_Bend.mov`/`Shallow_Bending.mov` already do |
| Diagnostic to run once recorded | Compare this clip's raw ankle/hip visibility ratio (via the same `benchmarks/validate_new_gait_footage.py` `raw_visibility` reporting already used for every clip in this corpus) against `Deep_Bend.mov`'s 0.54/0.86 -- if visibility is meaningfully higher and `compute_sit_to_stand` STILL fires a spurious detection, that would be real, direct evidence FOR the originally-hypothesized angle-only degeneracy (as opposed to the occlusion mechanism already fixed); if it does NOT fire, that narrows the sustained-held-bend residual limitation (`SitToStandBendSquatGuardTests::test_sustained_held_bend_residual_limitation_documented`) to only the fast/brief case that fixture already tests, not the sustained case too |

No code or threshold was changed to write this section -- both specs are
planning only, per this document's own established convention (see
Section 6's opening line). Neither gap is claimed closed; both remain
open, tracked in `docs/GAIT_CODE_REVIEW.md`'s own findings table.

## 9. New footage recorded against Section 8's specs: results, and a new
##    root-caused (not yet fixable) bug found on real data (a later session)

6 new real clips recorded against Section 8.1/8.2's specs, added to
`test_footage/GAIT_Analysis_Test_Footages/`: `Sit_Stand_SideAngle_1/2/3.mov`
(side-on sit-to-stand, closes 8.1) and `Deep_Bend_1/2/3.mov` (standing deep
bend, closes 8.2). Same subject as the existing reference clips, per each
spec. Ground truth (`*_GT.csv`, same `start_time,end_time,state,label`
convention) was derived by sampling each clip at ~0.35-0.7s intervals and
visually reading off state transitions -- footage-derived, not fabricated,
but precision is bounded by that sampling interval (consistent with the
existing corpus's own round-number GT granularity).

**Section 8.1 gap (camera-angle generalization) -- closed, with real
evidence.** All 3 `Sit_Stand_SideAngle_*.mov` clips correctly fire
`compute_sit_to_stand` near their real "Standing up" GT span (durations
0.085-0.118s, reversal_count=0 in all three -- a smooth real stand), and
never fire spuriously elsewhere in any of the three clips.
`_HIP_ANGLE_SITTING_MAX`/`_HIP_ANGLE_STANDING_MIN` generalize to a
side/profile framing for this subject. This is 3 clips from one subject
(dev-set evidence, not a strict dev/held-out split), not a population
claim.

**Section 8.2 gap -- a NEW, real, root-caused bug found instead of the
originally-targeted question.** The deep-bend clips (captured at ~58-60fps,
1080x1920 portrait, closer framing than the old `Deep_Bend.mov`) exposed a
different, more consequential problem before the original occlusion-vs-
geometry question could even be tested: `Deep_Bend_2.mov`'s sustained
standing bend produces `walking_speed` values up to 15.8 torso-lengths/sec
and `postural_sway` up to 0.29 torso-lengths -- both far outside any
plausible real-footage range this project has ever measured (walking_speed
elsewhere: 0.49-2.94; postural_sway elsewhere: 0.002-0.09) -- while the
subject is provably stationary (GT-confirmed sustained bend; raw hip
position barely moves: x in [0.756,0.777], y in [0.267,0.303] across the
affected span).

Root-caused, not assumed: `_torso_scaled_hip_track` divides raw hip
position by EACH FRAME'S OWN torso_len (shoulder-mid to hip-mid distance).
During this subject's deep standing fold, torso_len genuinely collapses to
~31% of their own standing value (median 0.166 standing vs. 0.052 during
the bend, measured directly) -- a real 2D-projection consequence of
folding the torso toward horizontal, not just MediaPipe noise. Dividing a
near-stationary raw position by this near-degenerate, noisy denominator
numerically amplifies small residual estimation error into large apparent
translation -- the same "shrinking-reference-scale" failure class this
project already identified and fixed for the sit-to-stand fallback path
(`_peak_translation_speed`'s fixed-reference-scale design), but never
applied to `_torso_scaled_hip_track` itself, which
`compute_walking_speed`/`compute_postural_sway`/`compute_stride_regularity`'s
shared ambulation gate all depend on.

**Three candidate fixes were tried and rejected, honestly, rather than
shipping a partially-working one:**
1. Smoothing `torso_len` before dividing (instead of smoothing the
   already-divided track, the current behavior) reduces but does not
   eliminate the artifact even at a 21-frame window (15.5 -> 6.8
   torso-lengths/sec measured directly on the implicated real window --
   still wildly implausible).
2. A per-window torso_len coefficient-of-variation gate does not
   discriminate: genuine toward-camera walking (`Moving_in_out_frame`,
   already in the corpus) measures CV up to 0.38, overlapping the
   artifact's own 0.10-0.44 range.
3. A per-window torso_len-percentile-ratio gate (reject frames below X% of
   the window's own 90th percentile) fails for a structural reason, not a
   tuning one: the worst implicated real window (t=6.29-7.78s) is ENTIRELY
   inside the sustained bend -- no genuinely-standing frame exists anywhere
   in that specific 90-frame window to serve as a local reference, so ANY
   per-window-relative threshold is computed against an already-corrupted
   baseline and cannot catch it (verified: max spurious value stayed
   15.766, unchanged, across ratio thresholds 0.3-0.6).

**Not fixed this session -- genuinely blocked, not deferred.** A safe fix
needs either an absolute (not per-window-relative) torso_len plausibility
reference, which requires calibration data across more subjects/camera
distances than this project has (risking exactly the "tune to fit two new
videos" failure mode this project has repeatedly guarded against), or a
session-level "confirmed standing" calibration reference threaded through
from a stable anchor period -- an architectural change larger than a
threshold tweak, not attempted without dedicated design review. Zero
source changes were made to `src/gait/gait_features.py` in pursuit of
this; all 143 existing tests still pass unchanged.

**Recommended next step**: record 2-3 more subjects performing the same
standing-deep-bend motion (varying body proportions and camera distance)
specifically to characterize how far torso_len can legitimately collapse
during a genuine bend versus how far genuine walking's own momentary
torso_len dips go, across more than one body type -- the data needed to
set an absolute plausibility floor without guessing.

## 9.1 Independent audit session (later): `compute_stride_regularity` had
##     the identical unfixed degeneracy Section 9 found for `walking_speed`
##     -- found, root-caused, fixed, and validated on real footage

A full independent audit of the GAIT pipeline (prompted by two already-known,
data-dependent open issues; scope explicitly not limited to those two) traced
whether `compute_stride_regularity` was exposed to the same torso-length-
collapse degeneracy Section 9 found and Section 10/12 gated for
`walking_speed`/`postural_sway`. It was -- and, unlike those two signals, had
never been given the fix, despite sharing the identical root cause: its own
ambulation gate calls `_ambulation_check` on the SAME 2D `_torso_scaled_hip_
track` `compute_walking_speed` uses, and its ankle-oscillation signal
(`_normalized_positions`) divides by the same collapsing per-frame torso
length.

**Confirmed on real footage first, not assumed**: ran the actual production
path (`StreamingGaitRiskAssessor` -> `assess_risk()`, the same call
`gait_stream.py`'s `GaitPipeline` makes, via a fresh MediaPipe extraction of
`Deep_Bend_2.mov`) with no baseline supplied (the only way this pipeline is
ever actually invoked in this repository today -- see the new "Wiring gap"
note below). `walking_speed` reproduced the exact same 15.766 torso-lengths/
sec spike Section 9 originally reported (confirming the Section 10/12 gate is
real but, as that note explains, inert without a caller supplying it), and
`compute_stride_regularity` ALSO fired spuriously multiple times squarely
inside the clip's GT-confirmed "Deep bend sustained (NOT sitting)" span (CV
up to 0.429, n_events=4-6, reliability=1.0) -- a physically implausible
signal (nobody is taking 4-6 steps while holding a static bend) that would
have entered `risk_score` at weight 1.2, the highest of the four signals.
Reproduced independently with a clean synthetic fixture (a fully-bent,
near-motionless hip with only realistic per-frame ankle-tracking jitter, no
walking at all): CV=0.286, cadence=244 steps/min (itself an implausible
number -- real human cadence tops out around 130-140 steps/min even walking
briskly), reliability=1.0.

**Fix**: `compute_stride_regularity` now accepts the same opt-in
`_torso_baseline`/`_world_raw` parameters `compute_walking_speed` already
has, reusing -- not reinventing -- the exact same gate: identical
`_ambulation_check` output, identical `MIN_TORSO_BASELINE_RATIO`/
`MIN_TORSO_BASELINE_RATIO_3D` thresholds, identical worst-single-frame
aggregation (justified the same way: this gate, like walking_speed's, only
ever runs on windows that already cleared the ambulation gate, so genuine
sitting/standing-still windows never reach it). `GaitRiskAssessor.assess_
risk()` now threads `_torso_baseline`/`_world_raw` into the `stride_
regularity` branch the same way it already does for `walking_speed`. Placed
immediately after the (cheaper) ambulation gate, before the expensive
normalization/`find_peaks` work, matching this module's existing
cheapest-first gating convention.

**Validated, both synthetically and on real footage, before considering this
closed**:
- New unit tests (`tests/test_gait_risk.py::StrideRegularityTorsoBaselineTests`,
  6 tests): the fixture fabricates without a baseline; a confirmed-standing
  baseline correctly marks it unavailable during the fabricated case;
  genuine synthetic walking (`_walking_window`) is completely unaffected;
  default (no-baseline) behavior is provably unchanged; the 3D-mode gate
  also catches a moderate-severity residual case the 2D gate alone cannot
  (mirroring `WorldLandmarkRootCauseFixTests`' own walking_speed test).
- Real footage (fresh MediaPipe extraction, cached locally for this session
  only -- not committed): `Deep_Bend_2.mov`'s spurious stride_regularity
  windows during the sustained bend went from 5 (before the gate) to 0
  (after), using a baseline computed from the clip's own first ~1s
  (GT-confirmed standing). `Stride.mov` (genuine walking): all 10 previously-
  available stride_regularity windows remained available after the gate --
  zero recall loss.
- Full test suite: 212/212 tests pass (`python -m unittest discover -s
  tests`), no regressions in any other module.

**Validation scope, disclosed honestly (narrower than walking_speed's own
full-44-clip validation)**: this reuses walking_speed's already-validated
mask/threshold/aggregation exactly, and was additionally spot-checked
against one degenerate clip and one genuine-walking clip in this session --
but was NOT re-run against the full 44-clip real corpus specifically for
stride_regularity's own recall the way walking_speed's gate was. Low
incremental risk (any window this newly rejects is a window walking_speed's
own gate already rejects, for the identical reason), not zero. Left as an
explicit, disclosed residual validation gap rather than claimed complete --
see `gait_features.MIN_TORSO_BASELINE_RATIO`'s own "STRIDE_REGULARITY
VALIDATION SCOPE" docstring note.

**Files changed**: `src/gait/gait_features.py` (`compute_stride_regularity`
signature/body/docstring, `MIN_TORSO_BASELINE_RATIO`/`MIN_TORSO_BASELINE_
RATIO_3D` docstrings), `src/gait/gait_risk.py` (`assess_risk()`'s
`stride_regularity` dispatch branch, module docstring), `tests/
test_gait_risk.py` (new fixture + 6 new tests). No changes to `gait_stream.py`,
`gait_risk.py`'s output contract, or any other signal's behavior (verified:
every pre-existing test in the full 212-test suite still passes unchanged).

## 9.2 Wiring gap, found and confirmed the same audit session: NONE of the
##     torso-baseline/3D-world-landmark gating (Sections 9-14, plus 9.1
##     above) is reachable from any code path this repository actually runs

Every one of the fixes in Sections 10-14 (and 9.1) is real, and every one of
their own unit tests passes -- but `_torso_baseline` is an OPT-IN parameter,
and this session traced, end to end, who actually supplies it. Answer:
**nobody, anywhere in this repository outside `tests/test_gait_risk.py`'s
own synthetic fixtures.** Confirmed by direct inspection and by running the
actual production path against real footage (Section 9.1 above), not
assumed:

- `pipeline_utils.build_pose_row()` -- the ONE function every real capture/
  extraction path in this repo uses to build a pose row (`realtime_fall_
  detection.py`, `evaluate_real_footage.py`'s own `extract_pose_rows`-style
  helpers, every `benchmarks/validate_*.py` script) -- has NO
  `world_keypoints` parameter and never populates that key. Confirmed
  directly: a row built this way has keys `{timestamp, frame, posture_label,
  fall_detected, confidence, other_labels, keypoints, n_low_visibility}` --
  no `world_keypoints`. Section 14.1's "production wiring" fix only added
  `pose_world_landmarks` capture to `evaluate_real_footage.py`'s own raw
  keypoint-CSV extraction path (`extract_keypoints`/`_world_keypoints_from_
  row`) -- it was never threaded through `build_pose_row`, the function that
  actually produces the row dicts `GaitRiskAssessor`/`gait_stream.py`
  consume. So even a caller that WANTED to opt in via `window[i]["world_
  keypoints"]` has no ready-made helper in this repo's production code to
  populate it with.
- `gait_stream.py`'s `StreamingGaitRiskAssessor.push_frame()` -- the ONE
  streaming-ready component in this repo, and the intended eventual live-
  camera entry point per its own module docstring -- calls
  `self._assessor.assess_risk(window)` with no `_torso_baseline` argument at
  all. It has no mechanism to compute or hold a session-level "confirmed
  standing" baseline. Same for every benchmark script
  (`benchmarks/validate_new_gait_footage.py`, `validate_gait_on_footage.py`)
  -- all of them go through `StreamingGaitRiskAssessor` exactly this way.
- `realtime_fall_detection.py` -- the actual live-camera driver -- contains
  zero references to `gait`, `GaitRiskAssessor`, or `gait_stream` at all
  (confirmed by direct search), consistent with this module's own docstring
  ("None of this is wired into realtime_fall_detection.py... a deliberate,
  later... integration step").

**Net effect, confirmed empirically (Section 9.1's real-footage run)**: if
`GaitPipeline`/`StreamingGaitRiskAssessor` were connected to a live camera
feed TODAY exactly as this repository's own code currently stands, every one
of the torso-baseline/3D-world-landmark protections from Sections 10-14
(walking_speed's and postural_sway's collapse gates, and this session's new
stride_regularity gate) would be silently INERT -- `Deep_Bend_2.mov`
processed through the actual `StreamingGaitRiskAssessor` path reproduces the
full, un-gated 15.766 torso-lengths/sec `walking_speed` spike and the
un-gated stride_regularity fabrication, byte-for-byte matching the
"un-fixed" behavior these sections describe as closed. The fixes are real
and correctly implemented; they are just unreachable from every script this
repository can currently execute except the unit tests. This is a different
kind of gap from anything else in this document: not insufficient data, not
an unvalidated threshold, but a genuine integration/wiring gap between two
otherwise-correct pieces of work (the gating logic, and the row-building/
streaming code that would need to supply its inputs).

**Not fixed this session, and deliberately not attempted**: closing this
requires product/architecture decisions this session's own no-speculative-
changes standard puts out of scope -- specifically, WHEN in a live session a
"confirmed standing" reference should be established (at session start? on
detecting a stable standing period? re-established periodically?), and
whether `build_pose_row`/`realtime_fall_detection.py` should be modified to
carry 3D world landmarks through to production at all (a decision that
touches the shared, RF/LSTM/TCN-consumed row schema, not just GAIT). Recorded
here as a concrete, actionable finding for whoever makes that integration
decision, rather than silently left for a future session to rediscover from
scratch.

## 10. Fixed-reference-scale fix for walking_speed, partial and validated;
##    postural_sway and shoulder-width both tried and rejected with
##    real-corpus evidence (a later session)

Followed up on Section 9's "genuinely blocked, not deferred" conclusion by
building the session-level "confirmed standing" calibration reference that
section named as one of the two remaining architectural options (the other,
an absolute plausibility floor from multiple subjects, still requires
footage this project doesn't have -- not attempted here). Extracted raw
MediaPipe keypoints for the FULL real corpus this project has (44 clips: the
original 28 `test_footage/` clips + all 16 `GAIT_Analysis_Test_Footages/`
clips, cached once and reused for every candidate tested below) rather than
tuning against Deep_Bend_2.mov alone.

**What shipped**: `gait_features.compute_torso_baseline(window)` -- given a
span of frames believed to represent confirmed standing (e.g. a clip's first
~3s), returns the median torso length over the segment with the LOWEST local
coefficient of variation found in that span (deliberately not "first N
frames blindly": measured directly on `Stride.mov`, using a blind
first-30-frame average as the baseline produces a spurious ~13-22% minimum
ratio during nominally "genuine walking" -- but tracing that dip frame-by-
frame shows it falls entirely inside ~0.5-0.8s of MediaPipe acquisition
jitter right at the clip's start, subject still entering frame / tracker
not yet converged, not gait at all; a stable-segment baseline avoids that
window and the same clip's genuine mid-walk floor is a comfortable 0.54).
Threaded
through as a new OPT-IN parameter: `compute_walking_speed(..., 
_torso_baseline=...)` and `GaitRiskAssessor.assess_risk(window,
_torso_baseline=...)`, default `None` everywhere (byte-identical behavior
confirmed: all 143 pre-existing tests pass unchanged). When supplied, a
window's `walking_speed` is reported UNAVAILABLE -- not a corrected number
-- if the window's own worst-single-frame raw torso length falls below
`gait_features.MIN_TORSO_BASELINE_RATIO` (0.40) of that reference. The value
itself is never rescaled by the fixed reference (unlike
`_peak_translation_speed`'s pattern) -- doing so would reintroduce
camera-distance non-invariance for genuine toward/away-camera walking, which
still needs each frame's OWN torso length as its scale.

**Why this differs from the three approaches Section 9 rejected**: those
all tried to build a reference from INSIDE the same window being assessed,
which structurally cannot work for the worst real case (no standing frame
exists anywhere in it). `compute_torso_baseline` is explicit that it must be
called ONCE, from OUTSIDE the window(s) it will later gate -- the same
fixed-external-reference pattern `_peak_translation_speed` already uses
successfully for `compute_sit_to_stand`'s fallback path, applied here for
the first time to `_torso_scaled_hip_track`'s own consumers.

**Full-corpus validation (all 44 real clips, both the scratch design pass
and the FINAL shipped source code re-checked end-to-end)**:
- Zero regressions: no window in the full corpus that previously reported
  an available `walking_speed` value lost it, across every walking clip
  (`Stride.mov`, `Stride_Big_Starting_Leap.mov`, `Stride_Inconsistent_Pace.mov`,
  `Stride_Pause.mov`, `Diagonal_Walk_1.mov`, `Lateral_Walk.mov`,
  `Moving_in_out_frame.MOV`) -- including the two clips this task was
  specifically asked to guard, `Stride.mov`/`Stride_Big_Starting_Leap.mov`.
  The tightest real constraint found was `Moving_in_out_frame.MOV` (a
  genuine, already-in-corpus toward/away-camera walk): its available,
  previously-documented-plausible (0.49-1.72 torso-lengths/sec) windows
  have a worst-single-frame ratio of 0.451 to their own clip's baseline --
  a real, SUSTAINED effect (the subject genuinely walks ~2x farther from
  the camera partway through), not noise. 0.40 sits below that with real
  but modest (~11%) margin -- narrower than most other margins in this
  file, disclosed as such in `MIN_TORSO_BASELINE_RATIO`'s own docstring,
  because this is the single closest real reference available, not because
  a wider margin wasn't wanted.
- `Deep_Bend_3.mov`'s entire spurious `walking_speed` artifact (previously
  2.7-7.7 torso-lengths/sec throughout its sustained bend) is eliminated.
- `Deep_Bend_2.mov`'s most severe windows (previously up to 15.8
  torso-lengths/sec) are eliminated down to a residual worst case of 6.17 --
  a real, disclosed, NOT-fully-solved remainder (moderate-severity windows
  at worst-frame ratio 0.42-0.60 aren't caught by this threshold), comparable
  to or somewhat better than the smoothing-based fix Section 9 already tried
  and rejected (15.5 -> 6.8), but achieved via an availability gate (report
  nothing rather than a less-wrong number) rather than a numeric correction.
- Two unrelated pre-existing false positives (`LyingdownSlowly.MOV` reading
  2.39 torso-lengths/sec of "walking speed" while GT-confirmed lying down;
  `SitFloor_crossedLegs.MOV` reading 3.99 while GT-confirmed sitting) were
  also caught by the same mechanism -- a real side benefit, not this
  session's target, left as-is rather than separately investigated.

**`postural_sway` deliberately NOT given this same gate, despite being
asked to test it, based on real-corpus evidence, not assumption.**
`compute_postural_sway`'s own docstring already covers sway "while
standing/sitting still" -- and genuine seated sway legitimately collapses
torso_len relative to a standing baseline, often far more than the bend
this gate targets. Measured directly: `Sit_Stand_1.mov`/`Sit_Stand_2.mov`'s
real, currently-correct seated-sway windows show torso_len/standing-baseline
ratios as low as 0.013-0.27. Applying this gate to `postural_sway` would
have marked most of the pipeline's genuine, working sitting-sway output
unavailable -- a regression far larger than the bug it would reduce.
Fixing postural_sway's own version of this degeneracy needs a way to tell
"genuinely sitting" apart from "genuinely bending" that this module doesn't
have today (e.g. a posture-state signal threaded in from outside) -- left
open, not attempted here.

**Shoulder width (horizontal), the secondary candidate this task asked to
check, also tried and rejected with real-corpus evidence.** It IS true on
real footage that shoulder width resists collapse during a forward bend:
directly measured on `Deep_Bend_2.mov`/`Deep_Bend_3.mov`, shoulder width
stays ~0.13-0.17 throughout the sustained bend while torso_len collapses to
~0.05. But shoulder width has its OWN severe 2D-projection collapse under a
SIDE/PROFILE camera angle -- and this project's corpus specifically
includes side-angle footage, recorded in an earlier session for exactly the
camera-angle-generalization question (Section 8.1/9's
`Sit_Stand_SideAngle_*.mov` clips). Measured directly: those clips' genuine
standing-transition windows have torso_len/shoulder_width ratios as low as
0.167-0.301 relative to their own baseline -- a WORSE floor than the plain
torso_len approach's genuine-walking floor (0.451) above. Rejected in favor
of the simpler, better-validated metric.

**Net honest status**: the walking_speed half of Section 9's bug is
partially, validatedly fixed (worst cases eliminated, moderate cases
disclosed as still open, zero corpus regression). The postural_sway half is
UNFIXED, with a real-corpus-evidenced reason a same-shaped fix can't safely
apply there. No threshold or design choice here was tuned to fit fewer than
the full 44-clip corpus.

## 11. Follow-up on Section 10's two disclosed open issues: neither is
##    safely fixable with current real footage -- confirmed with more
##    evidence, not assumed (a later session)

Treated both of Section 10's disclosures as open bugs, not accepted
limitations, and tried to close them further before accepting "still open"
again. Both investigations used the same cached full 44-clip corpus.

### 11.1 walking_speed's residual 0.42-0.60 ratio band

**Checked whether the FULL corpus (not just `Moving_in_out_frame.MOV`)
supports a wider margin.** Pulled every currently-available `walking_speed`
window's worst-frame torso-ratio across all 8 walking clips (58 windows
total), not just the one tightest clip. Result: the 0.451 floor is not a
one-window fluke -- 8 separate `Moving_in_out_frame.MOV` windows sit at
essentially the same value (p0-p5 percentile = 0.4511), a real, sustained
plateau (the subject genuinely holds ~2x farther from the camera for
several seconds). No other walking clip comes anywhere close (`Stride.mov`
is next-lowest at 0.539+). **The margin cannot be safely widened using more
of this corpus -- 0.40 remains the best-evidenced choice, now confirmed by
a fuller distribution rather than a single window.**

**Investigated three candidate second signals to combine with the ratio
gate, since it's confirmed structurally maxed out:**
1. *Relative rate of torso-length decline* (first-quarter vs. last-quarter
   window mean, per second): Deep_Bend_2.mov's 4 residual windows measure
   -0.18 to -0.44/sec; `Moving_in_out_frame.MOV`'s own genuine low-ratio
   windows measure -0.14 to -0.27/sec over the same real footage -- direct
   overlap, no separating threshold exists.
2. *Raw (unscaled, image-space) hip path length over the window* -- the
   root-cause-adjacent signal (a bend amplifies noise on a near-STATIONARY
   raw position; genuine walking has real raw displacement). This one shows
   real, if partial, promise: the genuine-walking floor across all 58
   available windows is 0.1497 (image-space units), and 2 of Deep_Bend_2.mov's
   4 residual windows measure well below it (0.0898, 0.1380). But the other
   2 -- specifically the worst-value ones (val=4.70, 6.17 torso-lengths/sec)
   -- measure 0.1779 and 0.2087, ABOVE the genuine floor: by the time the
   bend has progressed this far, the raw hip position genuinely has drifted
   as much as some real walking does, because the torso is now visibly
   rotating in image space too, not just the hip translating. Combining
   this would only catch the two MILDEST residual windows (val 2.0, 3.4),
   leaving the two worst (4.7, 6.17 -- the ones that matter most) exactly
   as uncaught as today, for the cost of a second single-clip-derived
   threshold with its own thin margin.
3. *Direction-reversal rate in the raw hip track* (fraction of frame-to-frame
   steps along the net-motion axis that reverse sign): Deep_Bend_2.mov's
   residual windows measure 34-51% reversals; `Moving_in_out_frame.MOV`'s
   own genuine windows measure 21-46% over the SAME real footage -- again
   direct overlap (this specific clip's tracking is comparatively noisy in
   general, which mimics a bend's own noise-dominated signature on this
   metric specifically).

**Conclusion: not shipped.** None of the three candidates achieves a clean
separation with real margin; the one partial exception (raw path length)
would add a second thin-margin, single-clip-derived threshold to catch only
the two least-wrong residual windows while leaving the two most-wrong ones
unchanged -- not a good complexity/benefit trade by this project's own
"wide margin over the one real reference available" standard, and not
attempted. **What would actually close this**: more real toward/away-camera
walking footage, ideally from a subject/framing with less tracking noise
than `Moving_in_out_frame.MOV` (to get a cleaner "genuine floor" reference
than a single, somewhat messy clip), and/or footage that specifically
captures a bend's ONSET moment (not just its sustained hold) alongside a
walking transition's onset, so a rate-based signal could be tested against
less confounded real examples than currently exist.

### 11.2 postural_sway's degeneracy: checked for an existing signal, found
###     none is safe, spec written for a future one

**Checked the pipeline's one already-existing posture-state signal --
`pipeline_utils.classify_posture_and_fall`/`_classify_heuristic`'s own
Standing/Sitting/Lying classifier -- rather than inventing something new.**
Ran it exactly as production would (stateful, sequential, `reset_session_state()`
once per clip) over the real cached corpus. Result: it labels `Deep_Bend_2.mov`'s
sustained standing bend as "Sitting" 98-100% of the time (`Deep_Bend_3.mov`:
98%; `Shallow_Bending.mov`: 33%, less severe but still real). **This is not
a new finding -- it directly reproduces this project's own already-documented
"Gap 1" (Section 6/7: "hip angle alone cannot distinguish a deep bend/squat
from a shallow chair sit-to-stand... both produce the same torso-hip-knee
angle signature")**, confirmed again here on the newer Section 9 clips this
classifier hadn't been checked against before. This existing signal does not
solve postural_sway's problem -- it HAS the same problem.

**Investigated `knee_angle` (hip-knee-ankle, already computed in
`pipeline_utils._compute_knee_angle` for the SAME heuristic classifier, but
not currently exposed to `gait_features.py`) as a candidate NEW
discriminator** -- unlike hip_angle/torso_angle, it's a genuinely different
physical measurement: sitting IN A CHAIR bends the knee to ~90-130 degrees;
`Deep_Bend`/`Shallow_Bending`'s GT explicitly describes "legs relatively
straight," a standing bend at the waist, not the knee. Measured directly:
`Sit_Stand_1.mov`'s confirmed-sitting span has knee_angle median 122.7
(max 129.4); `Deep_Bend_2.mov`'s sustained bend has knee_angle median 153.5
(p90 159.8) -- real separation in this one comparison.

**Validated a combined (torso-ratio AND knee_angle) gate against the FULL
corpus before trusting it, and found real conflicts, not just theoretical
risk.** Two structural problems, both confirmed with actual clips already
in this project:
1. Squats/kneels genuinely bend the knee too (`Bend_pickup_squat_normalLight.MOV`
   measures knee_angle median 139.5 during a genuine squat) -- knee_angle
   cannot and structurally never will separate "squatting" from "sitting,"
   only "standing-bend-at-the-waist" from "sitting." A real, disclosed,
   different limitation from the ratio band above, not a tuning problem.
2. More importantly: 5 real windows across 3 clips already in this
   project's OWN corpus have BOTH a straight-ish knee (>=150 degrees) AND a
   collapsed torso ratio (<0.40) while GT-confirmed to be genuine, currently-
   working, non-bend content -- `Sit_Stand_1.mov`/`Sit_Stand_2.mov` each have
   one such window during their own sit-DOWN transition (torso drops before
   the knee finishes bending -- the same transition-phase ambiguity Gap 1
   already describes, now shown to affect knee_angle too, not just
   hip_angle), and `SitFloor_lowKeypoints.MOV` (a clip whose own name
   flags degraded landmark confidence) has 3 such windows during its
   GT-confirmed STANDING span, most likely a tracking-quality artifact of
   that specific clip rather than a posture-geometry one. A combined gate
   using this signal, shipped as designed, would have wrongly suppressed
   currently-correct sway output on exactly the clips Section 10 named as
   the ones that must not break.

**Conclusion: not shipped, per this project's own standing rule against
forcing a fix without real evidence.** No architectural change (posture-state
signal threading) was attempted either -- there isn't yet a validated signal
to thread in.

**Spec for what a posture-state input would need, for a future session (or
a decision to build a proper posture classifier) to have a concrete starting
point instead of a vague note:**

| Requirement | Detail |
|---|---|
| Output | At minimum a 3-way state per frame: STANDING-OR-BENDING (torso may be rotated forward, weight NOT supported by a seat/floor), SITTING (weight supported by a seat/floor -- includes floor-sitting with legs extended, which this session found breaks a knee-angle-only signal), SQUAT-OR-KNEEL (weight on the legs, both hip and knee flexed, not supported by a seat). Collapsing squat/kneel into "sitting" is exactly the failure mode this session re-confirmed -- keep it a separate class even if this project doesn't need to act on it differently yet. |
| Granularity | Per-frame, so it can be aggregated per-GAIT-window the same way `_ambulation_check`'s own masks are (e.g. require >=X% of a window's frames to agree on a state before trusting it) -- a single per-window label would blur exactly the sit-down/stand-up TRANSITION frames this session found are where the real conflicts concentrate. |
| Must NOT depend on | Any signal that collapses the same way `_torso_scaled_hip_track`'s per-frame torso length does during a bend -- this rules out `torso_angle`/hip_angle-based classification alone (confirmed failing, see above) as a sufficient basis, though it can remain ONE input among several. |
| Robustness requirement found this session, not assumed | Must handle floor-sitting-with-legs-extended (real clips: `SitFloor_lowKeypoints.MOV`, `Sitting_HalfLandmarks.MOV`) without confusing it for standing -- a chair-sitting-only assumption (knee bent under the seat) will misfire on this project's own existing floor-sitting footage. |
| Validation gate before shipping | The same full-corpus, no-fewer-than-44-real-clips, before/after-diff standard this session and Section 10 both used -- specifically re-check `Sit_Stand_1.mov`/`Sit_Stand_2.mov`'s sit-down TRANSITION frames (not just their steady seated hold), since that is where this session's investigation found the sharpest real conflicts, not in the steady states either candidate signal handles reasonably on its own. |
| Candidate sources not evaluated this session | The project's existing RF/LSTM/TCN posture classifiers (Fall/Lying/Sitting/Standing/Unknown) were NOT run against this exact sit-vs-bend-vs-squat question here -- they are trained on labeled data and might have learned cues beyond raw joint angles that could resolve what a hand-tuned geometric heuristic cannot, but using one would add a full ML-model runtime dependency to a currently pure-geometry module, and RF code specifically was out of scope for this session. Worth checking first, before designing a new geometric signal from scratch, given a classifier already exists and Gap 1's own hip-angle failure mode has already been characterized against it. |

No threshold, gate, or architectural change was added to `src/gait/` this
session for either issue -- both remain exactly as disclosed in Section 10,
now with more real evidence for why, not less.

## 12. Root-cause fix using MediaPipe 3D world landmarks -- closes most of
##    Section 11's walking_speed residual band and fixes postural_sway's
##    sit-vs-bend problem (a later session)

Pursued Section 11's own recommendation (option 1 of its closing summary):
fix the torso-length scale-degeneracy bug at its root -- a single 2D camera
image cannot distinguish "the torso rotated toward horizontal" (a bend)
from "the camera got farther away" (genuine locomotion), because both
shrink projected torso length the same way -- rather than adding another
2D-derived threshold.

### 12.1 Phase 1: scoping, done before writing any fix logic

**Confirmed, not assumed: MediaPipe's `pose_world_landmarks` (a second,
real-world-metric 3D output) was already being computed on every frame of
this project's existing extraction pipeline, and was never read.**
`evaluate_real_footage.py::extract_keypoints()` already runs
`mp.tasks.vision.PoseLandmarker.detect_for_video()`, whose result object
(`mp.tasks.vision.PoseLandmarkerResult`, confirmed directly via
`inspect.signature`) carries both `pose_landmarks` (2D, the only field this
project's code read) and `pose_world_landmarks` (3D, x/y/z in real-world
meters, roughly hip-relative) -- the extraction code only ever read the
first. No new model, no new inference cost: purely reading data already
computed and previously discarded (the 2D field's own `.z`, a *relative*
depth component distinct from the world-landmark output, was already
being extracted and then thrown away one step later, in
`_keypoints_from_row`).

**Pulled real 3D data for the specific failing/reference clips before
writing any fix code**, per this project's own no-fix-without-evidence
rule: `Deep_Bend_2.mov`/`Deep_Bend_3.mov` (the failing case),
`Moving_in_out_frame.MOV`/`Stride.mov`/`Stride_Big_Starting_Leap.mov` (the
walking-recall clips that must not regress), `Sit_Stand_1.mov`/
`Sit_Stand_2.mov`/`SitFloor_lowKeypoints.MOV` (the sitting clips that must
not regress). Measured, not assumed:
- 3D torso length is genuinely far more stable than 2D under camera-
  distance change: `Stride.mov`'s 2D torso-length CV is 0.359/0.249 across
  its toward/away halves; 3D's CV is 0.065/0.023 over the SAME frames.
  It is also far more robust to a previously undiagnosed noise source:
  `Stride.mov`'s own ~0.3s MediaPipe acquisition-jitter window collapses 2D
  torso length to 0.017-0.062 while 3D torso length stays a stable
  0.28-0.47m across the SAME frames.
- 3D torso length shows real separation between genuine sitting and a
  genuine bend where 2D and Section 11's knee-angle candidate did not (see
  12.2 below for the exact numbers).
- Reliability check, done because it was explicitly asked for, not
  skipped: 3D landmark VALIDITY tracks 2D validity almost exactly on every
  real clip checked (both come from the same MediaPipe detection pass),
  and 3D landmark NOISE (once present) is, if anything, LOWER than 2D's
  for torso length specifically. No clip showed 3D data shakier than 2D.

This evidence supported moving to Phase 2.

### 12.2 Phase 2: implementation, including a design that was tried and
###      reverted after full-corpus validation caught it

**First design (NOT shipped): make `_torso_scaled_hip_track` itself use 3D
torso length as its scale factor when available** -- i.e. divide the
existing 2D hip position by a 3D-metric torso length instead of a 2D one.
This reduced `Deep_Bend_2.mov`/`Deep_Bend_3.mov`'s spurious walking_speed
values substantially even without any gate. **Full-44-clip validation
(not just the two target clips) caught a serious regression before this
shipped**: `Stride.mov` lost `walking_speed` availability on 18 of 18
previously-available windows. Root-caused, not just observed: 2D torso
length GROWS as a subject walks toward the camera (real perspective
growth), and dividing 2D hip position by that SAME growing 2D quantity is
what cancels most of that perspective effect -- exactly the "camera-
distance invariance" `_torso_scaled_hip_track`'s own docstring already
described. 3D torso length does NOT grow with distance (precisely its
value elsewhere) -- so dividing 2D hip position by a roughly-CONSTANT 3D
quantity leaves that perspective growth uncanceled. Measured directly on
the implicated window (`Stride.mov`, t=6.21s): with a 3D-scaled
denominator, the resulting track's net displacement has dx=0.233,
dy=0.556 (vertical-dominant, failing `MIN_HORIZONTAL_DOMINANCE_RATIO`),
versus the same window's 2D-scaled track, dx=3.51, dy=1.90 (correctly
horizontal-dominant). **Reverted.** `_torso_scaled_hip_track` stays 100%
2D, byte-identical to before this session.

**Shipped design: 3D torso length is used ONLY inside the existing
fixed-baseline AVAILABILITY GATE (`_torso_baseline`/
`MIN_TORSO_BASELINE_RATIO`, Section 10), never mixed with the 2D
hip-position track.** This is safe specifically because the gate only
ever compares a length against a length (same-kind, scalar), never a
position/direction against anything -- the exact distinction the reverted
design's failure mode exposed. New: `gait_features._raw_world_keypoint_array`
(parses an OPTIONAL `"world_keypoints"` field a pose row MAY carry -- 99
floats, 33 landmarks x x/y/z meters -- purely additive to the existing 2D
`"keypoints"` contract, absent on every existing caller),
`_raw_torso_len_3d`, `_has_sufficient_world_coverage` (a whole-window,
never per-frame, 2D-vs-3D decision -- MIN_WORLD_LANDMARK_COVERAGE=0.5),
and `MIN_TORSO_BASELINE_RATIO_3D` (0.70) alongside the existing
2D `MIN_TORSO_BASELINE_RATIO` (0.40) -- a different constant because 3D
torso length collapses far less severely during a bend than 2D does
(measured: 3D drops to 49-67% of standing vs. 2D's 32-44%). `compute_
torso_baseline` and `compute_walking_speed`/`compute_postural_sway` all
gained an optional `_world_raw` parameter, default `None`, preserving
byte-identical behavior for every existing caller (verified: all 143
pre-existing tests plus the earlier session's 6 pass unchanged).
`GaitRiskAssessor.assess_risk()` computes `_raw_world_keypoint_array` from
`window` automatically (it's per-frame INPUT data carried on the rows
themselves, unlike `_torso_baseline`, which stays an explicit external
parameter the caller must supply, exactly as in Section 10).

**`postural_sway` is now ALSO gated (3D-mode only) -- reversing Section
11's "not shippable" conclusion, with real evidence it's now safe.**
Window-level (90-frame, matching `MIN_WINDOW_FRAMES`) median 3D-torso/
baseline ratio, measured across the full corpus: `Deep_Bend_2.mov`/
`Deep_Bend_3.mov`'s sustained-bend windows measure 0.42-0.69;
`Sit_Stand_1.mov`/`Sit_Stand_2.mov`'s confirmed-sitting windows measure
0.85-0.89; `SitFloor_lowKeypoints.MOV`'s genuine floor-sitting (legs
extended, the harder case that broke Section 11's knee-angle candidate)
measures 0.72-0.95. The tightest real gap is `Deep_Bend_3.mov`'s ceiling
(0.693) vs. `SitFloor_lowKeypoints.MOV`'s floor (0.718) -- thin (~3.6%)
but real, and confirmed (see 12.3) not to actually overlap anywhere in
this corpus.

**A second bug, also caught by full-corpus validation, also fixed before
shipping: aggregation (worst-single-frame vs. median) needed to differ by
signal.** An intermediate version used worst-single-frame 3D ratio for
BOTH signals (matching `MIN_TORSO_BASELINE_RATIO`'s own established 2D
convention, for consistency). This shipped a real regression: `Sit_Stand_1.
mov`'s ENTIRE genuine seated-sway signal (7/7 windows) and `SitFloor_
lowKeypoints.MOV`'s floor-sitting sway (12/15 windows) have real,
single-frame 3D-ratio dips as low as 0.45-0.61 during otherwise-genuine,
currently-correct sitting -- a worst-single-frame check wrongly suppressed
them; their window-MEDIAN ratios (0.72-0.95, the numbers the 0.70
threshold was actually derived from) do not have this problem. Fixed:
`compute_postural_sway`'s 3D gate uses MEDIAN. `compute_walking_speed`'s
3D gate keeps worst-single-frame, deliberately -- its gate only ever runs
on windows that already passed `_ambulation_check` (already show apparent
translation), so genuine sitting/standing-still windows never reach it at
all (confirmed: zero regressions anywhere outside the two target clips
using worst-single-frame there), and worst-single-frame is strictly more
sensitive, catching real transient bend-onset spikes a median would
dilute away.

### 12.3 Phase 3: full-44-clip validation, every signal, every window

Ran the complete real corpus (not just the two target clips) through
`GaitRiskAssessor.assess_risk()` three ways per window -- 2D-only (today's
behavior, no `"world_keypoints"`), 3D-available with no gate, and
3D-available with the gate -- across all FOUR signals (`walking_speed`,
`postural_sway`, `stride_regularity`, `sit_to_stand`), not just the two
this fix targets, per this project's own "validate every dependent signal,
not just the two being fixed" standard.

**Result: zero windows changed in any of the other 42 clips, for any of
the four signals.** `stride_regularity` and `sit_to_stand` show zero diffs
across the ENTIRE 44-clip corpus (neither was wired to 3D data at all --
`stride_regularity`'s ambulation gate reuses the now-2D-only shared hip
track unchanged; `sit_to_stand` was untouched by design). Specifically
confirmed, the exact claims this session was asked to verify:
- `Deep_Bend_2.mov`/`Deep_Bend_3.mov`'s `walking_speed` and
  `postural_sway` no longer spike (see below for the residual detail).
- `Sit_Stand_1.mov`/`Sit_Stand_2.mov`'s genuine seated sway is
  byte-identical before and after -- zero windows changed.
- No walking clip in the corpus lost recall -- `Moving_in_out_frame.MOV`,
  `Stride.mov`, `Stride_Big_Starting_Leap.mov`, and every other walking
  clip (`Diagonal_Walk_1.mov`, `Lateral_Walk.mov`,
  `Stride_Inconsistent_Pace.mov`, `Stride_Pause.mov`) show zero diffs.

**In the two target clips, compared against the ALREADY-SHIPPED Section 10
2D gate (not the original, fully-ungated bug) -- the fair "did this
actually improve on what's already deployed" comparison:**
- `Deep_Bend_3.mov`: no change -- the 2D gate already fully eliminated its
  spurious `walking_speed` artifact; the 3D gate matches that (still
  fully eliminated). `postural_sway` (which the 2D gate could never touch
  at all, per Section 10/11) is now fully unavailable throughout the
  sustained bend -- a wholly NEW fix, not previously possible.
- `Deep_Bend_2.mov`: the 2D gate's own disclosed residual worst-case (6.17
  torso-lengths/sec, `t=2.53s`, uncaught) is now caught -- along with the
  `t=2.03s`/`t=2.28s` windows (3.42/4.70 torso-lengths/sec) -- by the 3D
  gate. ONE window remains uncaught (`t=1.77s`, 2.04 torso-lengths/sec) --
  a real, disclosed, NOT fully eliminated residual, not silently claimed
  fixed: this window is mostly-standing by its own median 3D ratio (0.996
  -- comfortably above threshold), with a brief bend-onset spike entering
  only the window's tail end, which the ambulation-check's mean-speed
  computation still picks up as elevated. `postural_sway`'s entire
  previous artifact (0.09-0.29, "far outside any plausible real-footage
  range... 0.002-0.09" per Section 9) is now fully unavailable throughout
  -- again, wholly new.

**Net honest status**: `postural_sway`'s sit-vs-bend problem, disclosed in
Section 11 as blocked without a validated posture-state signal, is now
fixed, validated against the full corpus, zero regressions.
`walking_speed`'s residual band (Section 11.1, also disclosed as
structurally maxed out under 2D-only signals) is substantially -- not
completely -- further closed: one moderate window out of the four Section
10 originally left open remains available at a still-elevated (though
much reduced from the original 15.8) 2.04 torso-lengths/sec. No threshold
was tuned against fewer than the full 44-clip corpus; no synthetic data
was used for any validation number in this section (synthetic fixtures
were used only for the unit-test regression suite, `tests/test_gait_risk.
py::WorldLandmarkRootCauseFixTests`, which exercises the gating MECHANISM,
not the threshold VALUES).

## 13. `compute_sit_to_stand`'s standing-bend blind spot -- found by testing
##     docs/GAIT_CODE_REVIEW.md finding #3 in isolation, root-caused, and
##     fixed with a real, corpus-validated second signal (a later session)

Tested finding #3 (bend/squat vs. sit geometric degeneracy) directly
against `Deep_Bend_1.mov`/`Deep_Bend_2.mov`/`Deep_Bend_3.mov` -- the
footage Section 8.2/9 recorded specifically to isolate it, with ~100%
landmark confidence (vs. the original `Deep_Bend.mov`'s 0.54/0.86
ankle/hip). Result was different from what the finding anticipated:
**zero false positives during the sustained bend, but also zero true
positives during the real "Getting up" recovery, in any of the three
clips.** Not the originally-hypothesized angle-only geometric degeneracy
(hip angle correctly tracks bent-vs-upright: median ~76-80 degrees during
the bend, recovering to ~159-166 degrees afterward) -- a genuine blind
spot instead.

**Root-caused, not assumed**: `MIN_STAND_HIP_RISE` (0.08 torso-lengths,
calibrated from chair-stand/kneel-stand references, +0.128 to +0.403)
rejects every real recovery. Measured directly: `hip_rise` is NEGATIVE in
all 7 real recovery windows found across the three clips (-0.454 to
-0.006). This makes physical sense -- recovering from a STANDING bend
straightens the torso while the feet never leave standing height, unlike
a chair-stand's hip traveling a real vertical distance -- so the guard
built to reject seated repositioning (Section 7's `Sit_Stand_2.mov` fix)
rejects this different, genuine transition as a side effect.

**Fix: a knee-angle exemption, validated against the full corpus before
shipping, not just the target clips.** A standing bend keeps the knee
straight throughout (only the torso rotates); genuine seated repositioning
keeps the knee bent throughout (the whole point of being seated) -- the
same second angle `pipeline_utils.py::_classify_heuristic` already
combines with hip angle (finding #4), not currently used anywhere in
`compute_sit_to_stand`. Measured directly, full 44-clip corpus, every
window where `MIN_STAND_HIP_RISE` currently rejects a pairing (not just
the three target clips): `Deep_Bend_1/2/3.mov`'s 7 genuine recoveries
measure knee angle 156.4-178.1 degrees at both reference points;
`Shallow_Bending.mov`'s own real recovery (a fourth, independent clip,
not part of the original target set) measures 162.3-162.8;
`Sit_Stand_2.mov`'s two real, already-documented seated-repositioning
false positives measure 117.1-122.7 -- a completely disjoint range, ~34
degrees of margin. Every other real hip-rise-rejected pairing anywhere in
the corpus (an occlusion-confounded case, and incidental hip-angle-noise
crossings during walking/sitting/lying on 5 other clips) has knee angle
well below the standing range and correctly stays rejected.
`_KNEE_ANGLE_STANDING_MIN` reuses `pipeline_utils.py`'s own
`ANGLE_STANDING_MIN` value (143.0) rather than inventing a new number --
already this project's established "knee straight enough to call this
standing" cut-point, sitting with large margin on both sides of the real
gap found.

**One real false-exemption risk found and closed before shipping, same
full-corpus-validation standard as every fix in this project**:
`Stride_Big_Starting_Leap.mov` has a hip-rise-rejected pairing with a
straight knee that would otherwise be wrongly exempted. Traced directly:
its reference frames sit inside a severe MediaPipe acquisition-jitter
window (the same artifact class as Section 10/11's `Stride.mov`
findings -- torso_len collapses to 0.016-0.025 there, vs. a stable
~0.15-0.30 later in the clip), and its `hip_rise` is -6.051 -- over 13x
more extreme than the worst REAL standing-bend case (-0.454).
`MAX_PLAUSIBLE_HIP_DROP_FOR_BEND_EXEMPTION` (-1.0) bounds the exemption to
plausible values, with real margin on both sides, closing this off.

**Validated result**: re-ran `compute_sit_to_stand` across every sliding
window of all 44 real clips and classified every detection found as
"needed the new exemption" or "pre-existing" (by checking whether
`hip_rise` was below `MIN_STAND_HIP_RISE` at that exact window). Every
single new detection (11 windows total) is in `Deep_Bend_1.mov`/
`Deep_Bend_2.mov`/`Deep_Bend_3.mov`/`Shallow_Bending.mov`, and every one
overlaps a real, GT-confirmed "Getting up"/"Standing" transition -- not a
single new detection anywhere else in the corpus, and not a single
spurious detection during any purely-static bend/sit/kneel/lying hold.
4 new regression tests
(`tests/test_gait_risk.py::StandingBendHipRiseExemptionTests`) lock in:
the core fix (straight knee + no rise -> now detected), the safety case
(bent knee + no rise -> still rejected, protecting `Sit_Stand_2.mov`'s
fix), the glitch bound (implausible hip drop -> still rejected even with
a straight knee), and that every pre-existing sit-to-stand fixture in this
file (none of which ever set an ankle keypoint, so knee angle is NaN
throughout) is a byte-identical no-op. All 159 tests pass (155 before this
session's addition).

**Not attempted**: the fallback path (`_detect_fast_shallow_transition`)
has its own, separately-added hip-rise guard (Section 9) -- whether it has
the same standing-bend blind spot was not tested; every new detection this
session found went through the PRIMARY path (a candidate sit run always
existed), so the fallback path's behavior here is simply unknown, not
confirmed either way. `test_sustained_held_bend_residual_limitation_
documented`'s own residual case (a held bend WITH a genuine hip rise,
where hip-angle geometry alone still can't distinguish it from a real sit)
is untouched by this fix and remains exactly as disclosed -- this session
only closes the "no hip rise at all" case, not that one.

## 14. Follow-up session: wiring the 3D fix into production, and three
##    more open-issue investigations (budget-limited, prioritized)

### 14.1 Production wiring (the most important remaining gap, now closed)

Section 12's entire 3D fix was validated but INERT in real use: the
production extraction script, `evaluate_real_footage.py::extract_keypoints()`,
never read `result.pose_world_landmarks` -- every validation in Sections
12-13 ran through a scratch harness that duplicated the extraction logic,
not the real pipeline. Fixed with the minimal addition Section 12 itself
scoped: `extract_keypoints()` now also captures `pose_world_landmarks`
into `lm_{i}_world_x/y/z` fields (same per-landmark convention as the
existing `lm_{i}_x/y/z` 2D fields, purely additive -- every existing
consumer, e.g. posture/fall classification, ignores the new fields
entirely), and a new `_world_keypoints_from_row()` helper (mirroring
`_keypoints_from_row`) flattens them into the `"world_keypoints"` field
`gait_features.py` already expects. Ten lines, no design left to do.

**Re-ran the full 44-clip corpus through the ACTUAL production script**
(fresh MediaPipe extraction, not the cached scratch data) and re-validated
both Section 12's gate and Section 13's exemption against it. Section 12
reproduced EXACTLY: `Deep_Bend_2.mov`/`Deep_Bend_3.mov` show the same
15/12 and 12/12 diffs as before, zero diffs anywhere else in the corpus.

**Section 13 reproduced with one real, additional, CORRECT catch, and one
honest methodological caveat surfaced by re-extracting from scratch:**
`Bend_pickup_normalLight_leftRight.MOV` now ALSO shows 3 new exemption-
driven detections (t=1.58-5.68s) that the earlier extraction run didn't
expose to the primary path at all. Traced directly, not assumed: comparing
the two extraction passes frame-by-frame, 177 of 333 frames differ in
landmark visibility/NaN pattern (not just floating-point noise -- some
frames are NaN in one pass and valid in the other) for this specific,
visually challenging clip (a left/right bend with more self-occlusion than
the other Deep_Bend clips). MediaPipe's VIDEO-mode extraction is NOT
perfectly deterministic run-to-run for this footage. Confirmed the new
detections are genuinely correct, not a regression introduced by this
session's code: all 5 total detections in the freshly-extracted data
(2 pre-existing + 3 new) overlap real, GT-confirmed "Getting up"/"Standing"
transitions -- the 3 new ones cover the clip's first bend-and-recover event
("bending down left" -> "Getting up" -> "Standing", GT 0.6-6.0s), which the
earlier extraction's noisier tracking simply never packaged into a
confirmed sit-run/stand-run pairing for the primary path to see at all.
**Honest implication**: the exact SET of clips a given fix "touches" in
this project's validation write-ups is a property of one specific
extraction run, not a guaranteed-reproducible fact about the video file --
the underlying gating LOGIC (confirmed deterministic given fixed input
keypoints, verified via the unit-test suite) is what should be treated as
validated, not the literal list of clip names. No corpus-wide re-validation
of Section 9-12's other, less occlusion-heavy findings was attempted here
(out of scope/budget for this pass) -- flagged as a real, if narrow,
caveat on this project's whole validation methodology, not swept aside.

Full test suite: 159/159 pass, unchanged.

### 14.2 `compute_sit_to_stand`'s fallback path -- investigated, NOT extended

Scanned the full 44-clip corpus for `_detect_fast_shallow_transition`
candidates that pass guards #1-#4 but fail guard #5 (hip_rise), mirroring
the exact method used for the primary path. Found only 9 candidates
total (far fewer than the primary path's real evidence), and critically:
knee angle does NOT cleanly separate them the way it did for the primary
path. `Occluded_fall.MOV` -- a FALL clip, not a bend -- has a candidate
with BOTH reference points straight-kneed (146.8/146.0 degrees); extending
the exemption here would create a false positive on fall-adjacent motion,
exactly what guard #4 (translation speed) exists to prevent.
`Sit_Stand_2.mov`/`SitFast_GetupFast.MOV`'s candidates show knee angle in
an ambiguous 132-148 degree band, not the clean bimodal split
(~120 vs ~156+) the primary path showed. **Not extended -- real evidence
against it, not just caution.** The fallback path's own hip-rise guard is
left exactly as it was; this is a real, disclosed, still-open question
(different from, and structurally rarer than, the primary path's blind
spot, since guard #3 already excludes any candidate whose trough goes
past the sitting threshold -- i.e. anything as deep as `Deep_Bend_2/3.mov`'s
own bends never reaches guard #5 via this path at all).

### 14.3 `walking_speed`'s residual window -- 3D versions of Section 11's
###     candidates re-tried, both fail for a NEW, real reason

Re-tried two of Section 11's three rejected 2D second-signals using 3D
data, targeting `Deep_Bend_2.mov`'s one remaining residual window
(t=1.77s, 2.04 torso-lengths/sec). Both looked promising against the
walking-clip subset checked first, and both failed once checked against
the FULL 44-clip corpus (not just walking clips) -- the same "looked clean
until the fuller corpus" pattern Sections 11/12 already found more than
once, here for a genuinely new reason:
- *3D torso-length rate-of-decline*: target window measures -0.080/sec;
  every genuine walking clip's own available windows measure no steeper
  than -0.059/sec -- a real gap, UNTIL checked against the full corpus:
  `Sit_Stand_SideAngle_1.mov`/`Sit_Stand_SideAngle_2.mov`'s own genuine,
  currently-available `walking_speed` windows measure as steep as -0.120,
  -0.119 -- steeper than the target.
- *Raw (unscaled) hip path length*: same pattern -- `Sit_Stand_SideAngle_3.mov`'s
  genuine windows measure as low as 0.051 (image-space units), below the
  target's own 0.090.
Root cause, consistent across both: a SIDE-ANGLE sit-to-stand (recorded
specifically for camera-angle generalization, Section 8.1/9) produces real
torso/hip dynamics -- foreshortening, some translation -- structurally
similar to a forward bend's, for the same underlying 2D-projection reason.
The third Section 11 candidate (reversal count) was NOT separately
re-tried given this consistent two-signal pattern and session budget --
likely to show the same conflict, not confirmed. **Not shipped.** The
residual window (2.04 torso-lengths/sec, down from the original 15.8 via
Sections 10 and 12 combined) remains open, exactly as Section 12 last
left it.

### 14.4 "Held bend WITH genuine hip rise" -- inconclusive, no real footage
###     to test against

Checked whether the current 44-clip corpus (rather than the older,
smaller corpus the original "knee angle doesn't help" conclusion was
based on) contains a real, SUSTAINED held-bend event that also shows a
genuine hip rise on recovery -- the specific residual case `test_
sustained_held_bend_residual_limitation_documented` documents as still
open. It does not. Every `Bend_pickup_*.MOV` clip's own GT is a brief
bend-and-recover (already handled by the trough-depth/minimum-gap guards
added in an earlier session), not a sustained hold. The corpus's only
real sustained-hold clips (`Deep_Bend_1/2/3.mov`, `Shallow_Bending.mov`)
all show near-zero or NEGATIVE hip rise on recovery, per Section 13 --
none reproduces the "genuine rise" half of this specific residual case at
all. Per this project's own no-synthetic-data-for-validation rule, this
question was NOT forced with a synthetic-only re-test. **Left exactly as
documented -- still open, no new evidence either way.** Closing it for
real would need new footage: a sustained held bend recorded specifically
so that its recovery shows a genuine, real vertical hip rise (unlike this
subject's own standing-bend recoveries measured so far).

### 14.5 Explicitly skipped this session (per direct instruction)

Thin threshold margins (`MIN_TORSO_BASELINE_RATIO`/`MIN_TORSO_BASELINE_RATIO_3D`/
`FALLBACK_MAX_TRANSLATION_SPEED`) and the lack of clinical/outcome
validation are both data-collection needs, not code fixes -- left exactly
as documented in Sections 3 and 10-12, not attempted here.

## 15. GAIT wired into `realtime_fall_detection.py` -- closes Section 9.2's
##     wiring gap, and exposes (and fixes) a real bug that gap had been
##     hiding (a later session)

Directly followed up on Section 9.2's own finding ("nobody, anywhere in
this repository outside `tests/test_gait_risk.py`'s own synthetic
fixtures" supplies `_torso_baseline`) with the integration work that
finding said was needed. Per `docs/IMPLEMENTATION_PLAN.md` Section 5.3's
own description of GAIT as "a separate, parallel output ... wired into a
dashboard/alert system as its own independent signal" -- not a change to
the fall-detection decision path itself.

### 15.1 What was built

- **`pipeline_utils.build_pose_row()`** gained an optional `world_landmarks`
  parameter (purely additive -- every existing caller is unaffected) that
  populates `row["world_keypoints"]`, applying the same per-landmark
  visibility drop as the existing 2D `keypoints`. This is the piece Section
  9.2 found missing: `evaluate_real_footage.py`'s own extraction script had
  been fixed to CAPTURE `pose_world_landmarks` (Section 14.1), but nothing
  threaded it through the ONE function every real pose-row consumer
  (including `realtime_fall_detection.py`) actually calls.
- **`realtime_fall_detection.py`** now extracts `result.pose_world_landmarks`
  from the SAME `detect_for_video()` call already producing the 2D
  landmarks (zero extra inference cost) and passes it through
  `build_pose_row`. A `StreamingGaitRiskAssessor` is constructed alongside
  the existing LSTM/object-detector (same defensive try/except loading
  pattern), fed every frame's `row`, and its output is surfaced via a new
  `on_gait_update` callback plus an on-screen overlay -- never merged into
  `fall_flags`/`alarm_active`/the debounced alarm decision. See that
  module's own "GAIT integration" docstring (on `run()`) for the full
  contract.
- **`gait_stream.TorsoBaselineCalibrator`** (new class) establishes the
  one-time session torso-length baseline from a confirmed-Standing,
  non-fall run -- reusing the SAME `classify_posture_and_fall()` verdict
  the fall decision already computes every frame, rather than inventing a
  second, independently-tuned "is this person standing" signal inside
  the GAIT module (see that class's own docstring for the full reasoning).
  Calibrates exactly once per session; `compute_torso_baseline()`'s own
  internal least-noisy-20-frame-sub-segment search and `CALIBRATION_MIN_
  VALID_FRAMES` floor are what actually protect against calibrating on
  poor tracking, reused rather than re-implemented.
- **`gait_stream.StreamingGaitRiskAssessor.set_torso_baseline()`** (new
  method) is the mutable link between the two: the calibrator's result is
  threaded into every subsequent `assess_risk()` call this instance makes.

### 15.2 A real, previously-invisible bug found by this integration, root-
###      caused and fixed: `compute_torso_baseline()`'s fps estimate broke
###      on real wall-clock timestamps

Running the ACTUAL `realtime_fall_detection.run()` loop (not a hand-wired
`assess_risk()` call) against `Deep_Bend_2.mov` -- the same real-footage
smoke test this section's own integration tests
(`tests/test_realtime_gait_integration.py`) now run automatically --
`compute_torso_baseline()` returned `None` on every single attempt, for
the ENTIRE ~16s clip, despite a genuine, clean, 45-frame GT-confirmed
standing hold with 45/45 valid, low-noise torso-length samples (measured
directly: 2D torso length 0.160-0.165, essentially flat). Every prior
validation of this function -- the unit tests in
`TorsoBaselineCalibrationTests`/`WorldLandmarkRootCauseFixTests`, and every
real-footage check in Sections 9-14 above -- used ZERO-BASED relative
timestamps (`i/30.0`, or `evaluate_real_footage.py`'s frame-index-derived
seconds), because that is what every extraction script and every synthetic
fixture in this project has ever produced. `realtime_fall_detection.py`'s
real frame loop is the FIRST caller anywhere in this repository to supply
`compute_torso_baseline()` with genuine wall-clock timestamps
(`str(time.time())`, an absolute Unix epoch value, ~1.7e9 seconds) -- and
the function's internal fps estimate, `len(ts) / ts[-1]`, implicitly
assumed `ts[0] == 0`. Against an epoch timestamp this produces a "fps" on
the order of `1e-8`, collapsing the internal search-frame-count (`n_search`)
to 0 and making the search loop never execute -- `compute_torso_baseline`
returned `None` unconditionally, no matter how clean the underlying data
was, for every wall-clock-timestamped caller, silently.

This is exactly the class of bug the whole reason for doing REAL end-to-end
integration testing (rather than trusting that a unit-tested function must
therefore work everywhere it's called) exists to catch -- it was invisible
in 14 prior audit sessions' worth of real-footage validation because none
of them used the real production timestamp convention.

**Fix**: use the window's own elapsed duration (`ts[-1] - ts[0]`) instead
of the raw final timestamp -- invariant to whether `ts` is relative-from-0
or an absolute epoch value, matching how every OTHER duration computation
in this module already works (e.g. `compute_sit_to_stand`'s
`duration_sec = ts[b] - ts[a]`, always a difference, never an absolute
value). Verified: `compute_torso_baseline` now succeeds against BOTH real
wall-clock timestamps and the existing relative-timestamp convention,
producing numerically consistent results either way (new regression test,
`TorsoBaselineCalibrationTests::test_baseline_recovers_from_real_wall_
clock_timestamps`). All 222 pre-existing tests (212 audited in the prior
session, plus this session's own 10 new `gait_stream`/`gait_risk` unit
tests added before this bug was found) continued to pass unchanged, since
every one of them used relative timestamps that happen to produce the
SAME `n_search` behavior either way for the window lengths this project
actually tests with -- this bug was reachable ONLY through the real
wall-clock path, confirming it was invisible to the existing suite by
construction, not by oversight in how the existing suite was written.

### 15.3 Real-footage validation of the full, wired chain (not a unit test
###      in isolation)

Ran the ACTUAL `realtime_fall_detection.run()` loop against
`Deep_Bend_2.mov` end-to-end (headless, LSTM/object-detector disabled --
neither relevant to what this validates), inspecting every `on_gait_update`
payload across the full ~973-frame clip:

- Torso baseline established at frame 45 (well within the clip's own
  ~192-frame/3.2s GT-confirmed standing hold), 3D-mode, value ~0.494-0.496
  (two separate runs; MediaPipe's own VIDEO-mode extraction is not
  perfectly deterministic run-to-run for this footage, consistent with
  Section 14.1's own prior finding of the same non-determinism -- the two
  runs' baseline values differ by <0.5%, not a concern).
- **`walking_speed` never exceeded 0.47 torso-lengths/sec anywhere in the
  entire clip** -- including through the full sustained bend this exact
  clip was previously documented (Section 9, and Section 9.1's own
  real-footage confirmation) as producing up to ~15.8-15.9 torso-lengths/
  sec when the SAME clip is run WITHOUT a baseline (reproduced directly in
  this session, via the real `run()` loop, before the timestamp-bug fix
  above: the un-gated 15.766 value reappeared byte-for-byte). This is the
  concrete, real-footage proof that the torso-collapse protection is now
  actually active end-to-end, not merely present in the source and
  unit-tested.
- Automated as `tests/test_realtime_gait_integration.py` (5 tests, ~57s
  wall time -- real MediaPipe inference over the whole clip, deliberately
  kept in `tests/` rather than `benchmarks/` specifically because it
  asserts WIRING correctness, which should fail an automated run like any
  other regression, not only be caught by someone manually running a
  validation script).

**One additional, real, NOT-yet-fixed observation surfaced by this same
real end-to-end run (a genuinely new finding, not previously visible
because nothing before this ran the full wired chain against real
footage)**: at one window (t≈2.8s, still inside the clip's own GT-confirmed
"Standing" span, shortly before the bend begins), `stride_regularity`
reported CV≈0.91-0.97 (two runs) from only `n_events=3-4` detected
ankle-height peaks, with `walking_speed` simultaneously and correctly
reporting a low, plausible 0.22 torso-lengths/sec for the same window --
i.e. this is NOT the torso-collapse degeneracy Section 9.1 fixed (that
gate is confirmed working here, since `walking_speed` stays plausible).
Root cause, as far as it can be established without more data: brief,
genuine weight-shift motion immediately preceding the bend produces just
enough ankle-height oscillation to pass `STRIDE_PEAK_PROMINENCE_FRACTION`
and the ambulation gate, but a coefficient of variation computed from only
3-4 detected events is intrinsically high-variance -- this function's own
`n_events`/`reliability` metadata already exists precisely to flag this
("a CV from 3 detected events is less to be trusted than one from 15," per
`compute_stride_regularity`'s own docstring), but there is no HARD
availability gate on a minimum event count today. Not fixed here: adding
one would be a new threshold requiring the same real-corpus validation
standard every other threshold in this file was held to (see Section 8's
own methodology) -- a single window from a single clip is not that
evidence. Recorded as a new, disclosed, data-dependent open item (see
Section 16.4.D below), not silently patched.

### 15.4 Performance

`TorsoBaselineCalibrator.observe()`'s only non-trivial cost
(`compute_torso_baseline()`, called once the candidate run reaches
`min_run_frames`) measured at ~115 microseconds/call even in its
WORST-CASE repeated-failure path (an all-NaN 45-frame candidate, retried
every single frame indefinitely) -- three orders of magnitude below a
single MediaPipe pose-inference call (tens of milliseconds), so no
throttling was added; doing so would be solving a measured non-problem.
Calibration itself only ever runs to completion ONCE per session
(`TorsoBaselineCalibrator`'s own documented single-baseline-per-instance
contract), after which `observe()` is an O(1) no-op check.
`StreamingGaitRiskAssessor.push_frame()`'s own O(window length) cost is
unchanged by any of this session's work (still ~2-6ms per
`benchmarks/profile_gait_pipeline.py`, amortized over
`reassess_every_n_frames` frames, exactly as before).

### 15.5 Tests

- `tests/test_gait_stream.py`: 15 new tests (`TorsoBaselineCalibratorTests`,
  `StreamingGaitRiskAssessorTorsoBaselineTests`) -- calibration from a
  confirmed-Standing run, non-Standing/fall-detected frames never
  calibrating, contiguous-run-interruption resetting the count,
  calibrate-exactly-once, `reset()`, and `set_torso_baseline()` actually
  reaching `assess_risk()` through the streaming path.
- `tests/test_gait_risk.py`: 1 new regression test for the wall-clock
  timestamp bug (Section 15.2).
- `tests/test_realtime_gait_integration.py` (new file): 5 tests running
  the REAL `realtime_fall_detection.run()` loop against real footage --
  see Section 15.3.
- Full suite: 228/228 pass (`python -m unittest discover -s tests`), zero
  regressions in RF/LSTM/TCN/posture code -- none of it was touched.

### 15.6 What was deliberately NOT done

- `GaitPipeline` (the threaded producer/consumer wrapper) was not used --
  `StreamingGaitRiskAssessor.push_frame()` is called synchronously from the
  main frame loop instead, judged sufficient given the measured ~2-6ms
  `assess_risk()` cost against a real camera's frame budget. Left available
  for a future session if profiling a real deployment shows otherwise.
- No periodic/re-triggerable recalibration was added -- the baseline is
  established once per session and held for its duration (matching
  `compute_torso_baseline()`'s own documented contract). If a real
  deployment's camera-to-subject distance changes permanently mid-session
  (e.g. a camera physically moved), the baseline would go stale with no
  mechanism to detect or correct it -- a known, disclosed limitation (see
  Section 16.4.B below), not attempted here because doing so safely needs
  a design decision (when is it safe to distrust and re-establish a
  baseline mid-session) this session's own no-speculative-changes standard
  puts out of scope.
- The `n_events`-based `stride_regularity` reliability question (Section
  15.3's closing observation) was not turned into a new threshold.
- YOLO/temporal-model event-schema integration
  (`docs/IMPLEMENTATION_PLAN.md` Section 5, points 1-2) was not attempted
  -- out of scope for this session, genuinely a separate piece of work.

## 16. Remaining GAIT problems, re-triaged after Section 15's integration
##     work (a later session)

Re-classifying the audit's own open-issues list against the categories it
was asked to use, now that GAIT is actually reachable in the live pipeline.

**A. Can be fixed now, and WAS fixed this session:**
- Section 15.2's wall-clock timestamp bug in `compute_torso_baseline()`.

**B. Requires future architectural/product work (not attempted):**
- Periodic/mid-session baseline recalibration (Section 15.6).
- Whether/how to fold `reliability`/`n_events` into a hard availability
  gate anywhere (still purely transparency metadata everywhere in this
  module, per `gait_risk.py`'s own long-standing, disclosed design
  decision).
- `GaitPipeline`'s threaded path remains unused; revisit only if a real
  deployment's profiling shows the synchronous call is a bottleneck.

**C. Intentional design limitations, left unchanged, with reasons
restated for continuity:**
- `compute_sit_to_stand`'s single-transition-per-window contract (Section
  9 of `docs/GAIT_CODE_REVIEW.md`).
- Every risk-mapping threshold in `gait_risk.py` stays heuristic and
  `"calibrated": False` -- no clinical/outcome data exists anywhere in this
  project.
- Single-subject-tracking assumption throughout `gait_features.py`/
  `gait_risk.py` -- an architectural property of the whole module, not
  something this session's integration work changed or could safely
  change alone.

**D. Requires additional recorded data (not fabricated or guessed here):**
- `walking_speed`'s own disclosed residual band (Section 11.1/14.3) --
  unchanged by this session's work; still needs more toward/away-camera
  walking footage from a cleaner-tracked subject.
- `compute_stride_regularity`'s new (this session's own audit, Section
  9.1) torso-baseline gate has real-footage confirmation on 3 clips total
  (`Deep_Bend_2.mov`, `Stride.mov` from the prior session, plus this
  session's own full real-time run) but not the full 44-clip corpus
  `walking_speed`'s gate was validated against.
- Section 15.3's new observation: whether a minimum `n_events` floor on
  `stride_regularity` would help or over-suppress genuine short walking
  bouts needs real multi-window evidence (ideally from Category A/Category
  D footage already specified in
  `docs/GAIT_ANGLE_NOISE_INVESTIGATION_REPORT.md` Section H), not a
  single observed window from a single clip.
- Multi-subject validation of `TorsoBaselineCalibrator`'s own 60-frame
  (default `GAIT_MIN_CALIBRATION_FRAMES`)/45-frame (this session's test
  default) contiguous-Standing requirement -- this project's whole corpus
  remains single-subject (see the standing caveat at the top of this
  document), so how reliably a DIFFERENT subject's posture classifier
  produces a clean enough confirmed-Standing run to calibrate from is
  untested.

## 17. Dedicated risk-mapping audit (`gait_risk.py`) -- full-44-clip
##     empirical distributions, two real fixes shipped, several thresholds
##     investigated and deliberately left unchanged (a later session)

A dedicated session audited `gait_risk.py`'s risk-mapping architecture
specifically (`_speed_risk`/`_stride_cv_risk`/`_sway_risk`/
`_sit_to_stand_risk`, `_SIGNAL_WEIGHTS`, the weighted-average blend in
`GaitRiskAssessor.assess_risk()`), asked to determine whether it is
mathematically, statistically, and behaviorally defensible -- not to
retune numbers until they "look better." New tooling
(`benchmarks/gait_risk_distribution_analysis.py`) runs the ACTUAL
production path (`build_pose_row` -> `classify_posture_and_fall` ->
`TorsoBaselineCalibrator` -> `StreamingGaitRiskAssessor`, the same one
`realtime_fall_detection.py` uses) over the FULL real corpus (44 clips: all
28 of the original `test_footage/Hussain Testing 7-30-26/` +
`test_footage/Sanawar Testing 7-22-26/` clips, plus all 16
`GAIT_Analysis_Test_Footages/` clips), caching raw MediaPipe extraction
separately from the classification/GAIT pass so repeated analysis iterations
don't re-pay extraction cost. Zero extraction errors across all 44 clips.

### 17.1 Architecture trace (confirmed, not assumed)

```
raw pose/keypoints -> gait_features.compute_*() -> raw value
    -> gait_risk._speed_risk / _stride_cv_risk / _sway_risk / _sit_to_stand_risk
       (per-signal sigmoid, always in the OPEN interval (0,1))
    -> risk_contribution, clipped to [RISK_CONTRIBUTION_FLOOR, RISK_CONTRIBUTION_CEILING] (NEW, see 17.3)
    -> weight_confidence (NEW, stride_regularity only, see 17.2) applied to
       the signal's nominal _SIGNAL_WEIGHTS entry, producing an
       "effective weight"
    -> weighted_sum / weight_total over every AVAILABLE signal
       (renormalized -- weights of unavailable signals simply don't
       enter either sum, confirmed by the pre-existing WeightBlendingTests)
    -> risk_score
```

**Monotonicity**: verified directly (`RiskMappingMonotonicityTests`, new
this session), not just implied by "it's a sigmoid" -- every one of the
four risk-mapping functions is monotonic in its documented direction
(lower speed/higher CV/higher sway/longer-or-shakier sit-to-stand all
strictly increase risk), and the full blended `risk_score` is non-decreasing
as stride irregularity worsens end-to-end (through the new weight_
confidence + clipping mechanisms together, not just the raw sigmoid).
**Bounds**: `risk_score` is a weighted average of values each already in
(0,1) (now additionally clipped to [0.02, 0.98] before blending), so it is
mathematically guaranteed to stay in that same range -- verified directly
across representative real-scale inputs (`RiskScoreBoundsTests`), not left
as an unverified implication of the arithmetic.

### 17.2 Fix #1: stride_regularity's small-sample-size noise now discounted
###      in the blend, not just reported as inert metadata

**Problem, evidenced across the full corpus**: of the 56 real windows in
this corpus where `stride_regularity` was available, 29 (52%) had exactly
`n_events=3` -- this project's own hard minimum for computing a CV at
all -- and only 2 (3.6%) reached 8 or more. Yet EVERY one of these 56
readings previously entered `risk_score` at the identical nominal weight
(1.2, tied for the highest of the four signals), with `n_events` reported
only as inert `signals[...]["n_events"]` metadata. This is the exact
"small-`n_events` CV noise" case the real-time-integration audit
(Section 15.3) first found (`Deep_Bend_2.mov`, CV≈0.9-0.97 from n_events=3-4
during a brief pre-bend weight-shift, mapping to risk_contribution≈0.9997).

**Why NOT a hard n_events floor (rejected, with evidence)**: checked
directly against the corpus -- `Moving_in_out_frame.MOV`, a real GT-
confirmed WALKING clip, produces genuine, plausible CV values (0.27-0.33)
from only 4-5 events per 90-frame window, simply because ~3s at a normal
cadence only contains that many real steps. A hard floor set high enough
to exclude the noise case would also exclude this genuine evidence --
exactly the "do not simply suppress the signal universally" failure the
task explicitly warned against.

**Fix shipped**: `gait_risk._stride_regularity_confidence(n_events)`, a
smooth (sqrt-shaped, statistically motivated -- not a literal standard-
error formula, since this proxy's distributional assumptions are
unproven) ramp from `STRIDE_EVENTS_CONFIDENCE_FLOOR=0.35` (at the hard
minimum, n_events=3) to `1.0` (at `STRIDE_EVENTS_FULL_CONFIDENCE=8`, the
real observed P99/near-maximum across the full corpus). Applied as a
multiplier on stride_regularity's WEIGHT in the blend, not on
`risk_contribution` itself (which stays the raw, transparent sigmoid
mapping -- fully unchanged and inspectable). A new `weight_confidence`
field on each signal entry reports exactly what multiplier was applied
(1.0, unchanged, for the other three signals and for any window that
doesn't supply n_events). `None` (no n_events information at all, only
reachable via direct/synthetic use of the risk-mapping functions, never
through a real `assess_risk()` call) is treated as NEUTRAL (1.0), not the
floor -- assuming the worst from an absence of information would be a
stronger, unevidenced claim than assuming no adjustment.

**A real iteration caught during this session's own re-audit loop, not
shipped on the first attempt**: an earlier draft of
`STRIDE_EVENTS_FULL_CONFIDENCE` was set to 8 from first-principles window-
duration physics alone (not yet checked against real data), then revised
down to 6 after a PARTIAL (37/44-clip) background extraction run showed no
window exceeding 5 events -- then revised back to 8 once the FULL 44-clip
run completed and revealed two windows (`Shallow_Bending.mov`: 8-9 events;
neither previously seen in the partial run) that the 37-clip snapshot had
simply not reached yet. Documented here as a concrete example of the
"detect -> analyze -> modify -> test -> validate -> re-audit -> repeat"
loop the task required actually catching something.

### 17.3 Fix #2: risk_contribution can no longer report near-total
###      certainty at either extreme (general, all four signals)

**Problem, evidenced across the full corpus**: `_speed_risk` reported
risk_contribution as low as 0.00015-0.005 during the ACTIVE-FALL portion
of multiple real fall clips (`Chair_fall.mp4`, `Side_fall.mp4`,
`Far_fall.mp4`) -- not a degenerate/glitched reading (the underlying
speed, 1.8-3.9 torso-lengths/sec, is a real, already-plausibility-gated
measurement; `gait_features.MAX_PLAUSIBLE_HIP_SPEED` already screens out
genuinely impossible per-frame speeds, a different, already-solved
problem), but reported with a confidence (99.98%+ certain "not at risk")
this admittedly-uncalibrated, `"calibrated": False` heuristic sigmoid was
never validated to support. `_stride_cv_risk` symmetrically reached ~0.999
on real footage.

**Investigated and REJECTED first**: a targeted fix -- capping the walking-
speed INPUT at a "plausible normal walking" ceiling before mapping to risk
-- was tried first and found NOT safely separable on the full real corpus.
Genuine brisk walking (`Diagonal_Walk_1.mov`, recorded specifically for
oblique-walking validation) measures up to 3.430 torso-lengths/sec, which
overlaps the real fall-onset speed range (1.8-3.9) almost entirely --
`Side_fall.mp4` alone reaches 3.6-3.9, inside `Diagonal_Walk_1.mov`'s own
real range. A cap tight enough to blunt the fall cases would also blunt
genuine fast walking; one loose enough to spare it would barely touch the
fall cases. Consistent with this project's own established standard (see
Section 11's rejected `walking_speed` residual-band candidates for the
identical "did not cleanly separate on the full corpus, so not shipped"
reasoning) -- **not fixed**; genuinely needs either a second discriminating
signal (this module has none that separates "fast walking" from "fast
falling" using position/speed alone) or more data. Recorded as an open,
disclosed, data-dependent limitation (see Section 18.A below), not
silently patched with a threshold that would not have actually worked.

**What was shipped instead**: `RISK_CONTRIBUTION_FLOOR=0.02` /
`RISK_CONTRIBUTION_CEILING=0.98`, applied uniformly to all four signals'
`risk_contribution` (not risk_score directly, and not a per-signal,
scenario-specific rule) -- reflecting that an unvalidated heuristic sigmoid
should never assert near-total certainty at either end, regardless of
which signal or real situation produced the extreme input. A strictly
WEAKER claim than the rejected targeted fix: this does not claim to solve
the walking_speed/fall-speed overlap, only to stop this module from
reporting more confidence than it can honestly support. Verified: every
genuine-walking/genuine-transition `risk_contribution` found anywhere in
the real 44-clip corpus already fell inside [0.02, 0.98] on its own; ONLY
the fall-onset walking_speed cases and the smallest-n_events stride_
regularity cases were ever actually clipped by the new bound (confirmed by
re-running the full corpus after shipping: `walking_speed`'s minimum
across all 212 real available windows is now exactly 0.0200 -- the floor,
hit only by the fall-onset cases; `stride_regularity`'s maximum across all
56 is now exactly 0.9800 -- the ceiling, hit only by `Stride_Pause.mov`'s
own genuinely-irregular-by-design paused walk).

### 17.4 Investigated, evidenced, and DELIBERATELY left unchanged

Per the task's own explicit instruction not to retune values just because
more real data existed, or to overfit a single-subject corpus:

- **`_speed_risk`'s center (1.0) and slope (3.0)**: real walking speeds
  across the full corpus span a much wider range than the module's own
  prior documentation stated (0.49-3.43 torso-lengths/sec, not 0.49-1.72
  -- `Diagonal_Walk_1.mov`'s oblique walking reaches the new upper end).
  The center sits within this wider range; the slowest real walking on
  file (0.49) reads as ~82% risk, which is a plausible reading of
  "genuinely this subject's own slowest pace" rather than an obvious
  defect, and no clean evidence exists (single subject) for where a
  "more correct" center would sit. Left unchanged -- flagged as needing
  multiple subjects to responsibly retune (Section 18.A).
- **`_stride_cv_risk`'s center (0.30) and slope (12.0)**: the 11
  well-evidenced (n_events>=5) real CV readings span 0.16-0.72, with a
  semantically SENSIBLE pattern (steady real walking clips ~0.27-0.39;
  `Stride_Pause.mov`, a clip recorded with a deliberate mid-walk pause,
  reads highest at 0.70-0.72) -- genuine, if thin (n=11, one subject),
  evidence that the mapping's DIRECTION and rough scale are sound. Some
  evidence the center could sit a little higher (steady walking already
  reads 41-75% risk) was found but judged too thin (11 samples, 1
  subject) to retune without risking exactly the overfitting the task
  warned against. Left unchanged; documented as an open question for
  multi-subject data, not silently adjusted.
- **`_sway_risk`'s center (0.05) and slope (15.0)**: checked against 680
  real postural_sway windows -- median 0.0124, P95 0.0385, P99 0.0718,
  max 0.4597 (a real outlier, from `Fall_and_lie.mp4`'s own fall motion,
  now correctly clipped at the new ceiling). The bulk of real, ordinary
  values (P10-P90: 0.0049-0.0280) maps to risk_contribution roughly
  0.31-0.55 -- a real, non-degenerate spread, NOT compressed into a flat
  band as initially suspected before checking. No change made; this
  mapping's shape is supported by the evidence, not merely un-contradicted.
- **`_sit_to_stand_risk`'s center (2.0s duration / 2.0 reversals)**:
  checked against 82 real sit_to_stand windows -- all but one real
  duration is under 0.5s (median ~0.14s), reflecting this project's single,
  young, healthy subject; the function's own HIGH-risk regime (multi-second
  transitions) has literally never been exercised by any real footage this
  project has. This is a DATA-POPULATION gap, not evidence the mapping
  itself is wrong -- there is no real slow/at-risk transition on file to
  check the function's other half against. Left unchanged.
- **`_SIGNAL_WEIGHTS` (1.0/1.2/1.2/0.8)**: a sensitivity analysis (+/-10%
  perturbation around realistic real-median baselines, all four signals
  simultaneously available) found walking_speed and stride_regularity
  the most locally REACTIVE signals at typical real operating points
  (Δrisk_score +0.019 and +0.012 respectively for a 10% worsening),
  postural_sway and sit_to_stand comparatively FLAT (+0.0013, +0.0001) --
  because their sigmoid centers sit far from where real data typically
  falls, not because their nominal weights are too low. No single signal
  was found to disproportionately dominate risk_score in this test; if
  anything, postural_sway/sit_to_stand are UNDER-reactive relative to
  their nominal weight at typical values. Left unchanged -- re-centering
  either function to be more locally reactive at typical values is a
  different, larger change than this session's evidenced scope, and would
  itself need multi-subject validation before shipping.
- **Cross-signal correlation** (item explicitly requested): computed
  directly over the real corpus's co-available windows.
  walking_speed-vs-stride_regularity risk_contribution: Pearson r=0.27
  (56 windows). walking_speed-vs-postural_sway: r=-0.33 (132 windows).
  Neither indicates strong redundancy/double-counting (|r|<0.5 in both
  cases) -- no weight change made on this basis.

### 17.5 Terminology: empirically tuned, NOT calibrated

Every `"calibrated": False` marker in this module's output remains
accurate and unchanged. This session's fixes are grounded in real,
full-corpus EMPIRICAL EVIDENCE (56-680 real windows per signal, 44 real
clips, zero synthetic-only threshold decisions) -- a genuine improvement
over the prior "non-degenerate on synthetic data" standard -- but this is
**empirical tuning on available project footage**, not **clinical/outcome
calibration**: there is still no fall-risk OUTCOME label anywhere in this
project (a subject's later fall history, a clinical assessment score) to
validate risk_score's absolute scale against, and the entire evidence base
remains a single subject (see this document's own standing caveat).
`docs/GAIT_LITERATURE_REVIEW.md`'s reviewed clinical cut-points (e.g.
"<1.0 m/s" gait-speed thresholds) still cannot be applied directly, for
the same reason stated throughout this document: no real-world unit
calibration (subject height, camera distance) exists in this pipeline.

### 17.6 Tests and validation

New test classes in `tests/test_gait_risk.py`:
`StrideRegularityConfidenceWeightingTests` (6 tests -- ramp shape, None-is-
neutral, direct proof `weight_confidence` reaches `risk_score` through
`assess_risk()`, default-1.0 for other signals, None when unavailable),
`RiskContributionBoundsTests` (3 tests -- extreme-value clipping for both
directions, recall check that ordinary values are never touched),
`RiskMappingMonotonicityTests` (6 tests -- each risk function's own
monotonicity, plus an end-to-end "progressively worse CV never decreases
risk_score" test exercising the full pipeline), `RiskScoreBoundsTests` (1
parametrized test -- risk_score stays in [0,1] across a grid of
representative and extreme inputs). All pre-existing tests (`WeightBlendingTests`
etc.) pass UNCHANGED, confirming the new mechanisms default to a true no-op
for every scenario that doesn't specifically exercise them.

Full suite: 243/243 pass (`python -m unittest discover -s tests`; was
228/228 before this session -- 15 new tests, zero regressions), including
`tests/test_realtime_gait_integration.py`'s 5 real-footage end-to-end
tests, which now also implicitly exercise the new risk-mapping code
through the actual production path.

### 17.7 Files changed

`src/gait/gait_risk.py` (the two fixes above, plus `weight_confidence`
field, updated module docstring), `tests/test_gait_risk.py` (16 new
tests), `benchmarks/gait_risk_distribution_analysis.py` (new -- reusable
tooling for future GAIT threshold work, following this project's existing
`benchmarks/validate_*.py` convention), `docs/GAIT_DATA_ASSESSMENT.md`
(this section).

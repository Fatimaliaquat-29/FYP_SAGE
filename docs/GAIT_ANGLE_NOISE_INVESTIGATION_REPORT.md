# GAIT Risk Pipeline: Angle-Noise Fix, Footage Validation, and Recording Plan

Session scope: investigate and (where safely possible) fix the pure
angle-noise ambiguity in `compute_sit_to_stand`'s `reversal_count`
(documented as a known remaining limitation at the end of the prior
session), validate against the project's existing real footage, map out
adversarial edge cases, and produce a concrete plan for the risk-assessment
recording this project still needs. **Random Forest code
(`src/posture/rf/`, `models/rf_*`) was not touched in this session** — see
Section F for explicit verification.

**Standing limitation, restated up front and true throughout this report:**
this project has no clinically labelled fall-risk dataset, no clinical
ground truth, and no clinically calibrated risk thresholds. Nothing below
should be read as a clinical accuracy, sensitivity, specificity, or
medical-grade-reliability claim. The 28 `test_footage/` clips used for
validation in this report were built for frame-level posture/fall
classification (LSTM/TCN/RF work), not fall-risk assessment — they are
used here only for structural, behavioural, plausibility, regression, and
robustness checking against real (but risk-unlabeled) footage.

---

## Results table: GAIT pipeline run on all 28 real footage clips

All 28 `test_footage/` clips (the same clips previously used for LSTM/TCN/
RF posture-classifier evaluation) run through `GaitRiskAssessor` via
`benchmarks/validate_gait_on_footage.py`, post-fix. These are **provisional
GAIT validation footage, not clinically labelled risk-assessment ground
truth** — "Scenario" comes from each clip's existing posture/fall-timing
GT CSV (never from filenames); no fall-risk or gait-quality label exists
for any of them, so no cell below should be read as a risk-score
correctness claim. `N/A` = signal not applicable given the clip's known
scenario; `Not detected` = signal never fired where one might expect it;
`No ground truth` = no reliable expected value exists to grade against.
"Runtime" is total MediaPipe-extraction + assessment wall time for the
whole clip (dominated by pose extraction, not the GAIT math itself — see
Section G for GAIT-only per-call timing).

| # | Video/Clip | Scenario | Ambulation | Walking Speed (torso-len/s) | Sit-to-Stand | Postural Sway (torso-len) | Fall/Instability Signals | Risk Score | Runtime | Status | Notes |
|---:|---|---|---|---:|---|---:|---|---:|---:|---|---|
| 1 | Bend_pickup_lowLight | Stand→bend→get up→stand (1x), low light | Not detected (0/2) | N/A | N/A (no GT sitting event) | 0.0131-0.0181 | N/A (non-fall clip) | 0.504-0.525 | 5.3s | OK | No GT sitting event; sit_to_stand correctly N/A |
| 2 | Bend_pickup_lowLight_leftRight | Stand→bend→get up (2x, alt. sides), low light | Detected (5/11 win) | 1.089-2.234 | Detected (3/11 win); rev=0; dur=0.08s | 0.0112-0.0308 | N/A (non-fall clip) | 0.192-0.639 | 10.0s | Flagged | sit_to_stand fires 3/11 wins — geometric degeneracy (bend dips into sitting-angle range; GT has no Sitting state) |
| 3 | Bend_pickup_normalLight | Stand→bend→get up→stand (1x), normal light | Not detected (0/4) | N/A | N/A (no GT sitting event) | 0.0029-0.0123 | N/A (non-fall clip) | 0.383-0.823 | 9.6s | OK | No GT sitting event; sit_to_stand correctly N/A |
| 4 | Bend_pickup_normalLight_back | 3x bend/squat/get-up cycles, filmed from behind | Detected (14/23 win) | 0.858-2.304 | Detected (4/23 win); rev=0; dur=0.10-0.48s | 0.0062-0.0669 | N/A (non-fall clip) | 0.410-0.781 | 20.0s | Flagged | sit_to_stand fires 4/23 wins (geometric degeneracy); also 2nd confirmed instance of the angle-noise pattern fixed this session (reversal_count 2→0) |
| 5 | Bend_pickup_normalLight_leftRight | Stand→bend→get up (2x, L/R), normal light | Detected (12/17 win) | 0.226-3.691 | Detected (6/17 win); rev=0-8; dur=0.10-0.62s | 0.0060-0.0149 | N/A (non-fall clip) | 0.203-0.731 | 14.2s | Flagged | sit_to_stand fires 6/17 wins — geometric degeneracy |
| 6 | Bend_pickup_squat_lowLight | Stand→deep squat→get up→stand, low light | Detected (4/6 win) | 2.977-4.212 | Detected (2/6 win); rev=0; dur=0.07s | 0.0019-0.0058 | N/A (non-fall clip) | 0.211-0.692 | 6.4s | Flagged | dur~0.07s is implausibly fast for a real sit — geometric degeneracy |
| 7 | Bend_pickup_squat_normalLight | Stand→deep squat→get up→stand, normal light | Detected (4/5 win) | 2.030-2.666 | N/A (no GT sitting event) | 0.0126-0.0165 | N/A (non-fall clip) | 0.007-0.473 | 8.1s | OK | sit_to_stand correctly 0/5 this take |
| 8 | Kneeling | Stand→kneel (GT state="Sitting")→get up→stand | Detected (7/7 win) | 0.320-0.540 | Detected (2/7 win); rev=2; dur=0.25s | 0.0089-0.0113 | N/A (non-fall clip) | 0.442-0.548 | 8.4s | Flagged | sit_to_stand correct, BUT kneel-down's vertical hip drop reads as slow "walking" → high risk contribution (direction-of-translation gap, not fixed this session) |
| 9 | LyingdownSlowly | Stand→slow lie down→lying→slow get up (no GT "Sitting" state) | Detected (12/20 win) | 0.306-5.191 | Detected (4/20 win); rev=2; dur=0.14s | 0.0078-0.0386 | N/A (non-fall clip) | 0.275-0.660 | 16.6s | OK | sit_to_stand firing here is plausible, not a bug — a slow recline geometrically passes through sitting-like hip angles |
| 10 | Moving_in_out_frame | Walk out of frame→absent→walk back in | Detected (8/9 win) | 0.490-1.724 | N/A (no GT sitting event) | 0.0111-0.0307 | N/A (non-fall clip) | 0.270-0.590 | 8.1s | OK | Only clean genuine-walking clip in the corpus; bursts short (2-3s), marginal sample size |
| 11 | Moving_in_out_frame_withFall | Walk out→absent→walk in→fall→lying | Detected (6/9 win) | 0.842-3.519 | N/A (no GT sitting event) | N/A | N/A (non-fall clip) | 0.001-0.617 | 7.5s | OK | postural_sway/stride_regularity correctly N/A (never a stable bout long enough) |
| 12 | SitFast_GetupFast | Stand→sit fast (0.7s GT)→sitting→stand up (1.5s GT) | Detected (4/6 win) | 0.187-0.948 | Detected (2/6 win); rev=2; dur=0.22s | 0.0043-0.0124 | N/A (non-fall clip) | 0.344-0.581 | 7.4s | OK | Reference fast-sit-to-stand clip — unaffected by this session's fix; recall confirmed intact |
| 13 | SitFloor_crossedLegs | Lie onto floor→sit cross-legged→get up | Detected (11/14 win) | 0.200-3.995 | Detected (1/14 win); rev=6; dur=0.31s | 0.0066-0.0276 | N/A (non-fall clip) | 0.295-0.639 | 11.9s | OK | Floor-sit geometry differs from chair but still registers |
| 14 | SitFloor_lowKeypoints | Stand→sit on floor→stand up | Detected (12/15 win) | 0.703-3.237 | Detected (1/15 win); rev=0; dur=0.24s | 0.0072-0.0943 | N/A (non-fall clip) | 0.253-0.587 | 15.4s | OK | — |
| 15 | SitFloor_lowKeypoints_crossedLegs | Lie onto floor→sit cross-legged→get up | Detected (13/16 win) | 0.385-2.987 | Detected (2/16 win); rev=0; dur=0.10s | 0.0080-0.0202 | N/A (non-fall clip) | 0.202-0.984 | 14.3s | Flagged | risk_score spike (0.51→0.98→0.51) traced to signal-availability-driven aggregation, not a per-signal bug |
| 16 | Sit_Stand_AnklesInvisible | Stand→sit→sitting (GT 1-4.9s)→stand up (GT 5-6s)→stand | Detected (6/8 win) | 0.275-1.030 | **Not detected (MISS — GT confirms sitting event)** | 0.0075-0.0151 | N/A (non-fall clip) | 0.346-0.597 | 8.5s | Flagged | Traced: hip_angle stays 156-180° throughout, never crossing the 125° sitting threshold even mid-GT-"Sitting" — camera/seat-geometry-dependent, unrelated to this session's fix |
| 17 | Sitting_HalfLandmarks | Stand→sit down→sitting→stand up | Detected (7/9 win) | 0.504-1.174 | Detected (5/9 win); rev=0; dur=0.10s | 0.0092-0.0235 | N/A (non-fall clip) | 0.251-0.565 | 10.7s | OK | — |
| 18 | Sitting_Lying_FewLandmarks | Stand→sit→sitting→lie down→lying→**get up (GT 8-11s, genuine)**→sit→get up | Detected (16/21 win) | 0.516-2.310 | Detected (13/21 win); rev=0; dur=0.03-0.64s | 0.0079-0.0717 | N/A (non-fall clip) | 0.224-0.513 | 24.7s | OK (fixed) | **This session's primary fix target** — reversal_count 12→0 at the false-positive window (1.5-4.5s; GT confirms this is the sit→lying transition, not the real 8-11s get-up) |
| 19 | Sitting_Lying_FewLandmarks_back | Same structure, filmed from behind, longer | Detected (17/27 win) | 0.565-2.003 | Detected (5/27 win); rev=0; dur=0.20s | 0.0072-0.0358 | N/A (non-fall clip) | 0.197-0.556 | 27.0s | OK (fixed) | 2nd confirmation instance of the fix (reversal_count 2→0) |
| 20 | Backward_fall | Standing→falling backward→fallen/lying | Detected (2/2 win) | 2.869-3.092 | N/A (no genuine stand-up in GT; guard holds) | N/A | No spurious sit-to-stand; risk moves as expected post-fall | 0.226-0.256 | 4.9s | OK | walking_speed fires from the fall's own translation but maps to near-zero risk contribution |
| 21 | Chair_fall | Sitting on chair→falling off chair→fallen/lying (5.8s lying) | Detected (5/11 win) | 1.954-3.601 | N/A (no genuine stand-up in GT; guard holds) | 0.0173 | No spurious sit-to-stand; risk moves as expected post-fall | 0.000-0.972 | 12.2s | OK | Not misread as a stand-up despite starting from Sitting; risk rises 0.00→0.97 exactly as the window absorbs the fall (traced — directionally correct, not flicker) |
| 22 | Fall_and_lie | Standing→falling→fallen/lying (9.2s lying) | Detected (9/18 win) | 0.695-3.746 | N/A (no genuine stand-up in GT; guard holds) | 0.0170-0.0473 | No spurious sit-to-stand; risk moves as expected post-fall | 0.000-0.623 | 20.8s | OK | — |
| 23 | Far_fall | Standing→falling at distance from camera→fallen/lying | Detected (2/3 win) | 2.696-2.870 | N/A (no genuine stand-up in GT; guard holds) | 0.0076-0.0289 | No spurious sit-to-stand; risk moves as expected post-fall | 0.192-0.422 | 4.7s | OK | Small-in-frame subject; signals still compute without crashing |
| 24 | Foward_fall (sic; GT/report: Forward_fall) | Standing→falling forward→fallen/lying | Not detected (0/5) | N/A | N/A (no genuine stand-up in GT; guard holds) | 0.0140 | No spurious sit-to-stand; risk moves as expected post-fall | 0.156-0.278 | 6.7s | OK | walking_speed never available here (window-dependent, not investigated further) |
| 25 | Occluded_fall | Standing→falling **with occlusion** (GT-confirmed)→fallen/lying | Detected (6/6 win) | 1.598-3.193 | Detected (3/6 win); rev=0; dur=0.03s | 0.0187-0.0316 | No spurious sit-to-stand; risk moves as expected post-fall | 0.001-0.246 | 6.0s | OK | Short (~0.03s) blips consistent with fall-recoil, not a real stand-up; lowest risk range of the fall set |
| 26 | Off_axis_fall | Standing→falling off-axis→fallen/lying | Not detected (0/3) | N/A | N/A (no genuine stand-up in GT; guard holds) | 0.0225-0.0295 | No spurious sit-to-stand; risk moves as expected post-fall | 0.424-0.579 | 4.1s | OK | — |
| 27 | Side_fall | Standing→falling sideways→fallen/lying | Detected (4/5 win) | 2.290-3.927 | Detected (1/5 win); rev=0; dur=0.07s | 0.0220 | No spurious sit-to-stand; risk moves as expected post-fall | 0.327-0.445 | 6.6s | OK | Short dur=0.07s consistent with fall-recoil, not a guard failure |
| 28 | Slow_fall | Standing→**slow** falling (2.0s transition, longest of set)→fallen/lying | Not detected (0/8) | N/A | N/A (no genuine stand-up in GT; guard holds) | 0.0214-0.0235 | No spurious sit-to-stand; risk moves as expected post-fall | 0.644-0.831 | 8.0s | OK | Translation guard (fixed prior session) holds even for the slowest fall; highest risk range of the whole corpus |

No crashes, no `error` entries, and no out-of-[0,1]/non-finite `risk_score`
anywhere across all 28 clips.

## GAIT summary table

| GAIT Component | Tests/Clips | Passed | Failed | Partial/Uncertain | Main Finding |
|---|---:|---:|---:|---:|---|
| Ambulation / Walking (gate) | 28 | 7 | 1 | 20 | Gate correctly requires coherent, high-net-displacement translation, but does not check *direction* — fires on incidental vertical motion (kneeling, falls) as well as genuine horizontal walking. Usually low risk impact (fall clips), one clear failure (Kneeling). |
| Walking Speed (value) | 28 | 0 | 0 | 28 | No absolute-unit ground truth exists to grade values against (torso-lengths/sec is not independently calibrated). Relative pattern is plausible: genuine-walking clips (0.49-1.72) read slower than incidental-motion clips (up to 5.19), consistent with brief lurches producing fast torso translation, but this is not confirmed against any outcome label. |
| Sit-to-Stand | 28 | 22 | 1 | 5 | Correctly fires on 8/9 clips with a genuine GT sitting event, correctly stays silent on 5/5 clips with no sitting event and no ambiguous motion, and correctly never misreads any of the 9 fall clips as a full stand-up. 1 miss (`Sit_Stand_AnklesInvisible`, traced to a camera/seat-geometry case where hip_angle never enters sitting range at all). 5 "partial" firings on bend/squat/recline clips reflect genuine geometric degeneracy, not a computation bug. |
| Postural Sway | 28 | 27 | 0 | 1 | Computes a plausible, small (~0.002-0.09 torso-length), non-crashing value in 27/28 clips; no independent ground truth exists for magnitude, so this is a plausibility check only, not a correctness check. |
| Fall/Instability Detection | 9 (fall clips) | 9 | 0 | 0 | No fall is ever misread as a confident sit-to-stand transition (the fall-adjacent guard from a prior session holds on all 9, including the slowest fall). GAIT itself has no dedicated "fall detected" signal — that is the RF/LSTM/TCN classifiers' job; this row checks GAIT's fall-adjacent *sit-to-stand suppression* specifically. |
| Risk Score Behaviour | 28 | 26 | 0 | 2 | risk_score stayed in [0,1] and finite on every one of 28 clips × all windows. 2 clips showed a large window-to-window jump; both traced to explainable causes (Chair_fall: window composition catching up with the fall, directionally correct; SitFloor_lowKeypoints_crossedLegs: signal-availability-driven aggregation, not a per-signal bug) rather than a raw computation defect. |

## Known limitations table

| Issue | Current Behaviour | Evidence | Fixed? | Remaining Limitation |
|---|---|---|---|---|
| MIN_AMBULATION_PATH jitter | Gated by `MIN_AMBULATION_PATH=0.5` + `MIN_AMBULATION_COHERENCE=0.2` (net-displacement/path-length ratio) to suppress stationary jitter from reading as walking | 0 changes to `walking_speed`/`postural_sway` values across all 28 clips in this session's before/after comparison (fix from a prior session remains stable) | Yes (prior session) | Checks magnitude/coherence of translation but not its *direction* — a coherent purely-vertical motion (e.g. kneeling down) still passes the gate; see Kneeling row above |
| Fall-adjacent sit-to-stand | `_peak_translation_speed` measures hip translation against a fixed pre-fall torso-length reference; `FALLBACK_MAX_TRANSLATION_SPEED=1.0` suppresses the shallow-transition fallback path when translation exceeds it | All 9 fall clips show 0 long/confident sit-to-stand detections misreading the fall as a stand-up this session (2 short ~0.03-0.07s fall-recoil blips, not full detections); `Slow_fall` (kinematically closest to a slow sit) still correctly shows 0/8 | Yes (prior session), reconfirmed intact this session | Relies on a fixed pre-fall reference scale — a fall occurring before any confirmed standing reference exists (e.g. clip starts mid-fall) is untested |
| Pure angle-noise ambiguity | `_count_reversals` now gated on both-sides-landmark-confidence | `Sitting_Lying_FewLandmarks` reversal_count 12→0; `Bend_pickup_normalLight_back` reversal_count 2→0 (independent 2nd instance); `SitFast_GetupFast` unaffected (rev=2 unchanged) | Yes (this session) | Does not address the separately-discovered geometric degeneracy (bend/squat vs. sit) or walking-direction gap — different mechanisms, found this session, deliberately left open pending new footage |
| Uncalibrated risk thresholds | All risk-mapping functions in `gait_risk.py` are heuristic, explicitly marked `"calibrated": False`, chosen to be non-degenerate on synthetic/real-but-unlabeled data | No risk-outcome ground truth exists anywhere in the project (`docs/GAIT_DATA_ASSESSMENT.md` Section 3); no threshold was changed this session to improve any result's appearance | No — not fixable without ground truth; out of scope for a code-only session | `risk_score`'s absolute scale/thresholds cannot be validated as clinically meaningful until real fall-risk-outcome data exists (Section H) |

---

## A. The angle-noise issue: root cause, fix, and why it's safe

**Symptom** (from the prior session): on `Sitting_Lying_FewLandmarks.MOV`,
`compute_sit_to_stand` could report `reversal_count=12` for a segment with
`translation ≈ 0.46` torso-lengths/sec — safely under
`FALLBACK_MAX_TRANSLATION_SPEED=1.0` — with no genuine standing-up event
in that time window. High reversal counts are supposed to mean "shaky,
higher-risk transition"; here they were pure measurement noise.

**Root cause** (traced end-to-end, not assumed): frames 44-66 of the
implicated window have the right shoulder/hip landmark pair dropping below
MediaPipe's confidence floor for ~20 consecutive frames, while the left
side stays valid. `compute_sit_to_stand` averages left/right hip angle
over whichever side(s) are currently valid — correct behavior for
occlusion robustness in general — but during this stretch the hip angle is
carried by the left side *alone*, and that single-sided estimate has
frame-to-frame noise **up to ~1.27 degrees**, small in absolute terms but
large enough to flip sign on almost every frame. `_count_reversals` had no
way to tell this apart from genuine shakiness.

**Why a simple magnitude threshold was rejected**: a real shaky-transition
test fixture already used by this project produces legitimate deltas as
small as 0.6 degrees — inside the noise case's own 0-1.27 degree range.
Any fixed magnitude cutoff would either still count the noise as
reversals, or start discarding genuine small-magnitude shakiness. This is
exactly the trap the task asked me to avoid: tuning a number without a
behavioural reason.

**The fix**: gate `_count_reversals` on landmark confidence, not angle
magnitude. `compute_sit_to_stand` already computes `valid_l`/`valid_r`
(per-frame booleans for whether each side's shoulder/hip/knee triplet is
in range and non-NaN) before this fix — the fix adds one boolean AND
(`both_sides_confident = valid_l & valid_r`) and only counts a
frame-to-frame angle reversal when **both endpoints of that delta were
double-sided-confident**. In the real clip this cleanly separates the two
cases: the noise stretch is 0% both-sides-confident (100% single-sided);
the genuine reversals used elsewhere in the corpus stay 100%
both-sides-confident. No new expensive computation — `valid_l`/`valid_r`
were already being computed for the angle averaging itself.

**Why this can't hurt genuine detection**: the gate only ever *removes*
reversal counts, never adds any; `duration_sec` (computed independently
from the sit/stand run boundaries) is completely untouched; and the
translation-based fall-adjacent guard from the previous session (a
different mechanism, checking `_peak_translation_speed` against
`FALLBACK_MAX_TRANSLATION_SPEED`) is unmodified. Verified concretely:

| | Before | After |
|---|---|---|
| `Sitting_Lying_FewLandmarks` reversal_count | 12 | 0 |
| `Sitting_Lying_FewLandmarks` sit-to-stand risk contribution | 0.469 | 0.137 |
| `Sitting_Lying_FewLandmarks` overall risk_score (worst affected frame) | 0.398 | 0.265 |
| `SitFast_GetupFast` (genuine fast sit-to-stand) reversal_count | 2 | 2 (unchanged) |
| `SitFast_GetupFast` detection still fires | yes | yes |

A second, independent real-footage case of the same noise pattern was
found by the full-corpus re-validation (Section C): `Bend_pickup_
normalLight_back` also had a noise-driven `reversal_count` (2→0) at two
frames, with the identical single-sided-visibility mechanism. This is
useful corroborating evidence that the fix addresses a real, recurring
failure mode rather than one clip's idiosyncrasy.

Regression coverage: 5 new tests in
`tests/test_gait_risk.py::SitToStandAngleNoiseConfidenceTests`, including
a fixture that reproduces the single-sided-noise pattern synthetically and
asserts `reversal_count == 0`, and a test confirming the existing
both-sided shaky fixture's `reversal_count == 6` is completely unaffected.

---

## B. LSTM/TCN validation footage: what it actually shows

Per the instruction not to assume video content from filenames, every
clip's ground-truth CSV (used for the prior LSTM/TCN/RF posture-classifier
evaluation — see `results/all_models_hussain/all_models_comparison.md`,
which confirms these are the same 28 clips) was read directly. Camera
metadata (resolution, fps, duration) was read from the video files
themselves, not inferred. The table below is Section C's categorization,
built entirely from this evidence.

**Two independently-shot sets exist and differ in ways worth knowing about
before drawing any cross-clip conclusion**: the Hussain set (19 clips,
`test_footage/Hussain Testing 7-30-26/`) is 1280×720 landscape at a
variable ~23-30fps; the Sanawar set (9 clips,
`test_footage/Sanawar Testing 7-22-26/`, all falls) is 576×1024 portrait
at a steady ~30fps. This is genuine, verified diversity (useful — the
pipeline is exercised under two real aspect ratios), but it also means
nothing about the Sanawar fall clips' behavior can be assumed to transfer
to the Hussain set's motion types, or vice versa.

**Interpretability without ground truth**: none of these 28 clips carry a
fall-risk or gait-quality label — only posture/fall-state timing labels.
"Useful for" below means *which GAIT signal's plausible behavior can be
sanity-checked against this clip's known posture sequence*, not that the
clip validates any risk-score value.

---

## C. Categorization table (all 28 clips)

Durations/fps from direct video inspection. Scenario column from the GT
CSVs, cross-checked against the video, not from filenames.

| Video | Observable scenario (from GT) | Useful for | Limitations |
|---|---|---|---|
| Bend_pickup_lowLight (5.2s) | Stand → bend down → get up → stand (1 cycle), low light | sit_to_stand false-positive suppression (no real "Sitting" state exists) | Lighting quality not independently measured beyond visual/GT label |
| Bend_pickup_lowLight_leftRight (9.9s) | Two bend/get-up cycles, alternating sides, low light | Same + repeated-cycle robustness | Same |
| Bend_pickup_normalLight (5.7s) | One bend/get-up cycle, normal light | Lighting-free baseline for above | — |
| Bend_pickup_normalLight_back (15.2s) | Three bend/squat/get-up cycles, filmed from behind | FP-suppression under back-facing geometry; source of a 2nd confirmed angle-noise case (Section A) | Back-facing landmark degradation pattern not independently quantified |
| Bend_pickup_normalLight_leftRight (11.8s) | Two bend/get-up cycles, left then right | Repeated-cycle robustness | — |
| Bend_pickup_squat_lowLight (6.1s) | One deep-squat/get-up cycle, low light | Confirms geometric-degeneracy limitation (Section D/J item 2) | Same lighting caveat |
| Bend_pickup_squat_normalLight (5.7s) | One deep-squat/get-up cycle, normal light | Baseline for above | — |
| Kneeling (7.0s) | Stand → kneel (GT itself labels this "Sitting" state) → get up → stand | sit_to_stand on a non-chair sit-like posture; surfaced the walking_speed direction issue (Section D/J item 3) | — |
| LyingdownSlowly (13.1s) | Stand → very slow lie-down (3s) → lying (4s) → very slow get-up (4s), never passes through a confirmed "Sitting" state | Slow floor-transition robustness, postural_sway baseline (extended standing/lying segments) | — |
| Moving_in_out_frame (7.3s) | Walk out of frame (2s) → absent (2s) → walk back in (3s) | walking_speed — one of only 2 genuine-walking clips in the whole corpus | Bursts are 2-3s; likely too short/marginal for confident ambulation-gate readings — must check output, not assume |
| Moving_in_out_frame_withFall (7.6s) | Walk out → absent → walk in → fall → lying | Post-occlusion fall-signal robustness | Same walking-burst caveat |
| SitFast_GetupFast (6.8s) | Stand → sit fast (0.7s, GT-confirmed) → sitting (3s) → stand up (1.5s) | **The** genuine-fast-sit-to-stand recall check — confirmed unaffected by this session's fix | Single clip, single subject, single trial |
| SitFloor_crossedLegs (10.0s) | Lie onto floor slowly → sit cross-legged → get up | Floor-sitting geometry (differs from chair) | — |
| SitFloor_lowKeypoints (10.8s) | Stand → sit on floor → stand up | Reduced-landmark robustness (per filename; exact drop pattern is **unknown** without a direct per-frame visibility trace) | Landmark-loss specifics not independently confirmed |
| SitFloor_lowKeypoints_crossedLegs (11.5s) | Lie onto floor → sit cross-legged → get up | Combines both above; source of the aggregation-availability finding (Section D) | Same |
| Sit_Stand_AnklesInvisible (8.0s) | Stand → sit → sitting → stand up | Ankle occlusion shouldn't affect hip-angle math directly (hip angle uses shoulder/hip/knee only) — good check that it indeed doesn't | Whether ankles are *actually* invisible throughout is unverified beyond the filename/GT label |
| Sitting_HalfLandmarks (7.9s) | Stand → sit down → sitting → stand up | Reduced-landmark robustness | Exact landmark subset unknown without direct trace |
| Sitting_Lying_FewLandmarks (13.8s) | Stand → sit → sitting → lie down → lying → **get up (8.0-11.0s, genuine)** → sit → get up | **The** angle-noise fix's source clip; GT confirms the fixed false-positive (at ~1.5-4.5s) occurred *before*, not during, the one real stand-up event | — |
| Sitting_Lying_FewLandmarks_back (16.7s) | Same structure, filmed from behind, longer | Second confirmed-fix verification angle | — |
| Backward_fall (3.7s) | Standing → falling backward → fallen/lying | Fall-adjacent-motion regression check (prior session's fix) | Acted/simulated fall by a presumably able-bodied subject — kinematics may not represent a genuine unplanned elderly fall |
| Chair_fall (8.4s) | Sitting on chair → falling off chair → fallen/lying | Confirms a fall starting from "Sitting" isn't misread as sit_to_stand; risk-score directional check (Section 13) | Same acted-fall caveat |
| Fall_and_lie (11.8s) | Standing → falling → fallen/lying (longest lying segment, 9.2s) | Sustained post-fall stability of the risk signal | Same |
| Far_fall (4.3s) | Standing → falling at distance from camera → fallen/lying | Small-in-frame / reduced-pixel-density landmark case | Same |
| Foward_fall (5.2s; filename typo for "Forward") | Standing → falling forward → fallen/lying | Fall-direction diversity | Same |
| Occluded_fall (5.7s) | Standing → falling **with occlusion** (GT-confirmed, not filename-guessed) → fallen/lying | Genuine occlusion-during-fall case | Same |
| Off_axis_fall (4.2s) | Standing → falling off-axis → fallen/lying | Non-standard camera-relative fall direction | Same |
| Side_fall (5.5s) | Standing → falling sideways → fallen/lying | Fall-direction diversity | Same |
| Slow_fall (6.8s) | Standing → **slow** falling (2.0s transition, longest of the fall set) → fallen/lying | Slow-fall vs. slow-sit-to-stand discrimination (translation-guard stress test) | Same |

**No usable clips exist for**: `stride_regularity` validation against a
known-cadence walking bout (no clip has a sustained multi-step walk), or
any multi-person scenario (every clip is single-subject — see Section D).

---

## D. Cross-referencing GAIT outputs against GT, and edge-case analysis

Ran the full pipeline over all 28 clips (before/after this session's fix)
via `benchmarks/validate_gait_on_footage.py`. No crashes, no
out-of-[0,1] or non-finite risk scores, anywhere.

### Findings that were traced and turned out **not** to be bugs

- **Chair_fall's risk_score jumps from ~0.001 to ~0.97** between early and
  late windows. Traced: this is directionally *correct* — the early
  windows only contain the calm pre-fall sitting segment (correctly low
  risk), and the jump happens exactly once the sliding window has
  absorbed enough of the fall+fallen-lying segment. Not flicker.
- **SitFloor_lowKeypoints_crossedLegs risk_score spikes to 0.98** at one
  frame, between neighboring frames of 0.53 and 0.51. Traced: no
  individual signal is unstable (`stride_regularity` stays ~0.6 across
  all three frames). The spike is entirely explained by which of the 4
  signals happen to be `available` in that specific window —
  `stride_regularity` alone (already high-risk) carries the *entire*
  weighted average when the other 3 signals drop out for one window, and
  gets diluted back down once they return. This is a real property of
  the weighted-average aggregation under fluctuating signal availability,
  not a computation bug in any one feature — worth knowing about, not
  worth threshold-patching under this task's "no unjustified threshold
  change" constraint.

### Findings that are real, pre-existing (not introduced this session) limitations

1. **Geometric degeneracy — bend/squat vs. shallow chair sit.** Hip angle
   alone cannot distinguish a deep bend or squat from sitting down on a
   chair; both produce the same shoulder-hip-knee angle signature.
   `compute_sit_to_stand`'s primary path legitimately fires on several
   `Bend_pickup_*`/`Bend_pickup_squat_*` clips whose GT never contains a
   "Sitting" state. **Confirmed present identically in the before-fix and
   after-fix validation runs** (same clip, same frame, same
   `reversal_count`/`duration_sec`) — this is not a regression from this
   session's work. A fix would need an additional discriminating signal
   (e.g. duration, or a translation/approach-to-a-fixed-point check) and
   real validation footage of both classes side-by-side to justify a
   threshold safely — recommended as recording-plan Category D (Section
   H) rather than patched now.
2. **`compute_walking_speed`'s ambulation gate doesn't check translation
   direction.** Traced on `Kneeling.MOV`: the kneel-down phase produces a
   large (net_disp≈1.2 torso-lengths), highly coherent (0.75-0.81)
   *vertical* hip translation — exactly what `MIN_AMBULATION_PATH`/
   `MIN_AMBULATION_COHERENCE` were designed to require, except the motion
   is a postural drop, not locomotion. This reads as "slow walking"
   (0.32-0.54 torso-lengths/sec) with correspondingly high risk
   contribution (0.80-0.89). The natural, cheap fix (reusing the
   already-computed hip track) is to additionally require the net
   displacement be predominantly horizontal rather than vertical — but
   the corpus has only two genuine walking bursts (2-3s each,
   `Moving_in_out_frame*`), not enough to confirm such a gate wouldn't
   also suppress recall for someone walking somewhat toward/away from the
   camera. Left unfixed, documented here, and flagged as the top-priority
   item for new walking footage (Section H, Category A).

### Adversarial edge-case coverage

| Category | Testable with existing footage? | Notes |
|---|---|---|
| Landmark dropout (single-side) | Yes — real, used for Section A's fix and its 2nd confirmed instance | |
| Landmark dropout (both sides / long gap) | Partially — `SitFloor_lowKeypoints*`, `Sitting_HalfLandmarks`, `Sitting_Lying_FewLandmarks*` labelled as reduced-landmark by their creators, but the *exact* drop pattern is unverified without a per-frame visibility trace (marked "unknown" in Section C, not guessed) | |
| Full occlusion / subject leaves frame | Yes — `Moving_in_out_frame*` (~1-2s absence) | Not tested: absence longer than `_MAX_TRUSTED_GAP_BEFORE_STATE` |
| Low light | Yes — `Bend_pickup_lowLight*` (3 clips) | Not tested: near-dark / IR footage |
| Portrait vs. landscape camera | Yes — verified real difference between the two sets (Section B) | |
| Back-facing subject | Yes — `Bend_pickup_normalLight_back` | Not tested: fully-frontal-toward-camera or 45-degree oblique angles |
| Far-from-camera / small-in-frame subject | Yes — `Far_fall` | Not tested: multiple distances for the *same* motion type |
| Off-axis / non-frontal fall | Yes — `Off_axis_fall`, `Side_fall` | |
| Slow vs. fast transition discrimination | Yes — `Slow_fall` vs. the fast-fall clips; `SitFast_GetupFast` vs. `LyingdownSlowly` | |
| Geometric ambiguity (bend/squat vs. sit) | Yes — see finding above | Needs new footage to fix safely, not just to detect |
| Direction-of-translation ambiguity (kneel vs. walk) | Yes — see finding above | Same |
| Multiple people in frame | **No — cannot be tested with existing footage; this is an architectural limitation, not something covered by current data.** The pipeline assumes exactly one tracked subject throughout (`GaitRiskAssessor`/`gait_features.py` never disambiguates between multiple detected poses). This is a real gap, not a false negative — say so plainly rather than pretend it's covered. | |
| Camera movement / handheld shake | No real footage available; all 28 clips appear tripod-fixed (unverified beyond visual inspection — no metadata confirms this) | Needs new recording |
| Extreme lighting (backlit, overexposed) | No | Needs new recording |
| Partial-frame subject (cropped by frame edge) | No dedicated clip; would need to inspect frame-by-frame for incidental occurrences, not attempted this session given time budget | Needs new recording or targeted frame inspection |
| Rapid state alternation (sit-stand-sit-stand in quick succession) | No — closest is the two-cycle `Bend_pickup_*_leftRight` clips, which are bend/get-up not sit/stand | Needs new recording |

Cases not simulated with synthetic fixtures this session beyond what
already exists in `tests/test_gait_risk.py`: multi-person tracking (the
architecture has no per-subject identity concept to attach a synthetic
second track to, so a meaningful synthetic test isn't possible without
first deciding how multi-person *should* behave — an architectural
decision, not a test-authoring one).

---

## E. Bugs fixed this session

1. **`_count_reversals` angle-noise false-positive** (Section A) — the
   only production-code change this session.

No other production-code changes were made. The two findings in Section D
(geometric degeneracy, walking-direction gate) were deliberately **not**
fixed — see the reasoning given there.

---

## F. Regression status

- **`MIN_AMBULATION_PATH`/`MIN_AMBULATION_COHERENCE` fix (prior session)**:
  intact — 0 changes to `walking_speed` or `postural_sway` values across
  all 28 clips, before vs. after this session's fix.
- **Fall-adjacent sit-to-stand translation guard (prior session)**: intact
  — `_peak_translation_speed`/`FALLBACK_MAX_TRANSLATION_SPEED` code path
  unmodified; all 9 fall clips' `sit_to_stand` availability unchanged
  (only `Chair_fall` ever has a sitting-adjacent phase, and it shows 0
  `sit_to_stand` detections in both runs — the fall is not misread as a
  sit-to-stand in either).
- **Postural-sway protection (prior session)**: intact — 0
  `postural_sway` value changes across the full corpus.
- **Previously-fixed synthetic tests remain meaningful**: all pre-existing
  fixtures/classes (`_ambiguous_rapid_angle_noise_window`,
  `_fall_adjacent_shallow_transition_window`,
  `SitToStandTranslationDiscriminationTests`) still pass unmodified.
- **Full test suite**: 111/111 tests pass (`python -m unittest discover -s
  tests`), including all `test_gait_risk.py` and `test_gait_stream.py`
  tests, all RF tests (untouched — see below), LSTM/posture pipeline
  tests.
- **Random Forest code explicitly confirmed untouched this session.**
  `git status` shows `src/posture/rf/rf_classifier.py`,
  `src/posture/rf/rf_trainer.py`, `models/rf_posture.joblib`, and
  `models/rf_label_encoder.json` as modified in the working tree — but
  their filesystem last-modified timestamp is **2026-08-11 21:04**, two
  full days before this session (which began 2026-08-13 and only ever
  touched `src/gait/gait_features.py` and `tests/test_gait_risk.py`,
  both timestamped 2026-08-13 09:10-09:15). These RF modifications
  predate this session entirely and were not created, edited, staged, or
  otherwise interacted with here.

---

## G. Performance

`benchmarks/profile_gait_pipeline.py` (150-frame window, 300 repeats):

| Stage | Time |
|---|---|
| `assess_risk()` end-to-end (walking window) | 4.41 ms/call |
| `assess_risk()` end-to-end (sit-to-stand window) | 5.71 ms/call |
| `compute_sit_to_stand` alone (sit-to-stand window) | 0.63 ms/call |

Implied throughput: ~227 `assess_risk()` calls/sec single-threaded — this
module runs once per multi-second window, not per video frame, so this is
comfortably within budget.

**This session's specific fix, isolated** (monkeypatch-based before/after
comparison, same process/warm caches, 500 repeats):

| | ms/call |
|---|---|
| `compute_sit_to_stand`, pre-fix reversal counting | 0.807 |
| `compute_sit_to_stand`, confidence-gated (this session) | 0.932 |
| Delta | +0.125 ms/call (+15.4%) |

The relative increase looks large but the absolute cost is sub-millisecond
and the extra work is a single boolean AND plus array slicing over
already-computed arrays — no new allocation-heavy or O(n²) work was
introduced. No incremental/streaming behavior was changed; the fix does
not add any historical rescanning.

---

## H. Risk-assessment recording plan

Prioritized by what's currently missing and would close the two open
findings in Section D, plus the multi-person and camera-motion gaps.

**Category A — baseline normal behaviour (highest priority — currently the
single biggest gap).** Sustained (10-15s, multiple full gait cycles)
walking bouts: normal pace, front-on, oblique (~30-45 degrees to camera),
and side-on. 3 subjects × 3 camera angles × 2 repetitions = 18 clips
minimum. This directly targets both open findings (enough genuine walking
data to validate a horizontal-dominance gate on `compute_walking_speed`,
and a clean, unambiguous walking baseline to double-check
`stride_regularity` against).

**Category B — mobility/instability.** Deliberately slow/shuffling walk,
uneven/hesitant gait, walking with a hand-held support prop (cane/rail
simulation), stopping mid-walk and resuming. 2-3 repetitions each.

**Category C — actual fall scenarios.** The project already has 9 acted
fall clips (Sanawar set); **do not recommend recording additional real
falls performed by an untrained person** — that is an unsafe recording
practice and out of scope to suggest. If more fall diversity is wanted,
safer alternatives are: crash-mat-cushioned controlled falls performed by
someone trained in stunt/fall technique, or continuing to rely on the
existing acted-fall corpus supplemented by the synthetic fixtures already
in `tests/test_gait_risk.py`.

**Category D — ambiguous/non-fall movements (2nd priority — targets the
geometric-degeneracy finding directly).** Genuine shallow/deep chair
sit-to-stand at multiple speeds, deliberate bend-to-pick-up-object,
deliberate squat, kneel-and-rise, reaching/leaning without sitting. Same
subject performing both a real sit and a squat back-to-back, so the two
classes can be directly compared under matched lighting/camera/clothing.
3 subjects × 4 motion types × 2 speeds = 24 clips.

**Category E — pose-estimation failure cases.** Deliberately loose/baggy
clothing, low light, partial-frame cropping, subject partially behind
furniture. Builds on what the existing `Bend_pickup_lowLight*` and
`*lowKeypoints*` clips already partially cover.

**Category F — stationary jitter cases.** Standing still, sitting still,
fidgeting in place, weight-shifting without stepping — explicitly *no*
translation — to stress-test that `MIN_AMBULATION_COHERENCE` and the
sit-to-stand confidence gate both correctly report "not available" rather
than a spurious detection.

**Category G — multi-person cases.** **This is an architectural
limitation of the current pipeline, not a data gap** — `GaitRiskAssessor`
assumes exactly one tracked subject and has no mechanism to select or
disambiguate between multiple detected poses. Recording multi-person
footage would not be usable until that architectural decision is made
first (which pose to track, how to handle a second person entering
frame). Flagging this explicitly rather than pretending it's covered by
any amount of new recording.

**Protocol specifics**: 1280×720 or better, ≥25fps, tripod-fixed unless a
clip specifically targets camera movement (not yet planned — lower
priority than A/D above), consistent ~2m subject-to-camera distance where
not testing Far_fall-style distance variation, filename convention
`<category>_<motiontype>_<variant>_<subjectID>_<takeN>.mp4` (e.g.
`A_walk_frontal_S1_01.mp4`), and a companion GT CSV per clip in the same
`start_time,end_time,state,label` format already used by the existing
corpus, so `benchmarks/validate_gait_on_footage.py` and
`compare_all_models.py` both work unmodified against it.

---

## I. Dataset split: development vs. held-out validation

No split currently exists because no new footage has been recorded yet —
this section is the plan for when it is. To prevent the threshold-tuning
leakage this task explicitly warned about:

1. **Split at the subject level, decided before any footage is reviewed
   frame-by-frame.** E.g. with 3 subjects recorded, designate one
   subject's entire contribution as held-out before any clip from them is
   watched or used to tune anything.
2. **Development set**: used freely for root-causing bugs, picking
   feature representations, and choosing which signal to gate on (as
   Section A's confidence-gating decision was made by tracing the
   existing corpus) — but any *threshold value* justified this way must
   still be re-checked against the held-out set before being called
   final.
3. **Held-out validation set**: touched only to report a final
   pass/fail-style check ("does the fix still separate case X from case Y
   on data that wasn't used to pick the fix"), never to iterate on
   thresholds. If a held-out clip fails, the fix goes back to the
   development set for revision and a *new* held-out check is needed
   afterward — never patch directly against the held-out result.
4. **Document every threshold's provenance** (which development clips
   justified it, and what the held-out check showed) in the same style
   `docs/GAIT_DATA_ASSESSMENT.md` already uses (`"calibrated": False`
   markers, explicit non-clinical framing) — do not let a future
   iteration quietly start treating a held-out pass as if it were a
   calibration result.
5. This project's existing 28 `test_footage/` clips were never split this
   way (they were used purely for posture/fall classification, then
   reused wholesale for this session's GAIT plausibility checks) — they
   should **not** be retroactively treated as a valid dev/held-out split
   for GAIT-specific threshold work, since the same clips have already
   been looked at repeatedly across multiple sessions while tuning GAIT
   behavior. Only genuinely new footage (Section H) can serve as a clean
   held-out set for GAIT thresholds going forward.

---

## J. Remaining limitations

**Fixed this session:**
- Angle-noise-driven spurious `reversal_count` in `compute_sit_to_stand`
  (Section A).

**Known limitations, found but not fixed (deliberately, per the
task's own no-unjustified-threshold-change constraint):**
- Geometric degeneracy between deep bend/squat and shallow chair
  sit-to-stand (Section D finding 1).
- `compute_walking_speed`'s ambulation gate doesn't check translation
  direction, so a vertical postural drop (e.g. kneeling) can read as slow
  walking (Section D finding 2).
- The weighted-average risk aggregation can swing significantly between
  adjacent windows purely because of which signals happen to be
  `available`, even when every individual signal's own value is stable
  (Section D, `SitFloor_lowKeypoints_crossedLegs` case).

**Uncalibrated heuristics** (unchanged from
`docs/GAIT_DATA_ASSESSMENT.md`, restated for completeness): every
risk-mapping threshold in `gait_risk.py` remains a placeholder chosen to
be non-degenerate on synthetic/real-but-unlabeled data, explicitly marked
`"calibrated": False`, never fit to outcome data.

**Unavailable clinical ground truth**: no fall-risk or gait-quality label
exists anywhere in this project's data. Nothing in this report establishes
clinical accuracy, sensitivity, specificity, or medical-grade reliability
— see the standing limitation restated at the top of this document.

**Scenarios needing more footage before they can be addressed at all**:
multi-person tracking (architectural, Section D/H Category G), sustained
multi-cycle walking at varied camera angles (Section H Category A),
matched bend/squat-vs-sit comparison footage (Section H Category D),
camera-movement robustness, extreme lighting, and rapid state alternation
(all Section H, lower priority).

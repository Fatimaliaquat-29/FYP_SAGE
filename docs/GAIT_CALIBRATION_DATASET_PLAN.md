# GAIT Risk Threshold Calibration: Dataset Design

**No code or thresholds were changed to produce this document.** This is a
planning document only, tracing the actual current implementation
(`src/gait/gait_risk.py`, `src/gait/gait_features.py`, read in full for
this task) and laying out what data would be needed to move from the
current heuristic thresholds (documented as uncalibrated in
`docs/GAIT_DATA_ASSESSMENT.md`) toward evidence-based ones.

---

## 1. Current implementation, traced from the actual code

### 1.1 Signal pipeline overview

`GaitRiskAssessor.assess_risk(window)` (`gait_risk.py:237`) computes 4
independent signals from one caller-supplied window of pose rows, maps
each through its own sigmoid risk function, and combines them as a
**weighted average, renormalized over whichever signals are available**
for that specific window (`gait_risk.py:264-281`):

```
risk_score = Σ(weight[s] * risk_contribution[s] for s available)
             / Σ(weight[s] for s available)
```

Weights (`_SIGNAL_WEIGHTS`, `gait_risk.py:126-131`): `walking_speed=1.0`,
`stride_regularity=1.2`, `postural_sway=1.2`, `sit_to_stand=0.8` — picked
"to reflect the reviewed literature's relative emphasis," explicitly **not
fit to any outcome data**.

**Continuous or categorical?** Continuous only. `risk_score` is a float in
`[0.0, 1.0]`, or `None` if zero signals were available. There is no
categorical/banded label (no "low/medium/high risk" tier) anywhere in this
code today — any such banding would be a new addition, not a recalibration
of an existing one.

**Temporal windows**: `MIN_WINDOW_FRAMES=90` (~3s @ 30fps) is the hard
floor for even attempting extraction (`gait_features.py:102`, enforced in
`gait_risk.py:304`); there is no fixed "ideal" window length beyond that —
the caller decides how many frames go into one `assess_risk()` call
(`benchmarks/validate_gait_on_footage.py`'s streaming harness is the only
current caller with a windowing/stride policy, and that lives outside this
module). Inside the module, `postural_sway` further subdivides into
15-frame sub-windows (`stable_subwindow=15`, `gait_features.py:725`), and
`stride_regularity`'s peak detector requires peaks spaced ≥5 frames apart
(`find_peaks(..., distance=5)`, `gait_features.py:709`).

**Smoothing/debouncing**: a 5-frame centered moving average
(`smooth_window=5`) is applied to the hip track used by `walking_speed`/
`postural_sway` (`_torso_scaled_hip_track`, `gait_features.py:415-453`).
`sit_to_stand`'s state machine debounces via `_STATE_CONFIRM_FRAMES=3`
consecutive frames before trusting a sitting/standing state at all.
`stride_regularity` has **no smoothing** beyond linear NaN-gap
interpolation before peak detection.

**Fallback logic**: only `sit_to_stand` has one — a primary
confirmed-sit-run-based path, falling back to
`_detect_fast_shallow_transition` (a shallow-trough detector) when no
confirmed sitting run precedes a confirmed stand (`gait_features.py:1131-
1135`). `walking_speed`, `stride_regularity`, and `postural_sway` have no
fallback: if their gates aren't satisfied, the signal is simply
unavailable (`None`) for that window.

### 1.2 Threshold trace table

Every constant that gates a signal's *availability* or maps a feature to a
*risk value*, traced from the code (not documentation) with line
references:

| Risk Signal | Feature | Current Threshold | Direction | Meaning | Risk Contribution | Known Problem |
|---|---|---:|---|---|---|---|
| *(global)* | Window length | `MIN_WINDOW_FRAMES = 90` frames | Lower bound | Minimum frames to even attempt extraction | N/A — hard gate, raises `ValueError` below it | Frame-count, not time-based; behaves differently at non-30fps sources |
| Walking Speed | Path length | `MIN_AMBULATION_PATH = 0.5` torso-lengths | Lower bound | Below this, treated as "no walking bout," not "slow walking" | N/A — availability gate | Alone insufficient (jitter can cross it) — needs coherence check below |
| Walking Speed | Path coherence | `MIN_AMBULATION_COHERENCE = 0.2` (net÷path ratio) | Lower bound | Distinguishes directed walking from stationary jitter | N/A — availability gate | Does **not** check translation *direction* — a coherent vertical drop (kneeling down) passes this exactly like horizontal walking (found this session, `Kneeling.MOV`) |
| Walking Speed + Postural Sway | Instantaneous hip speed | `MAX_PLAUSIBLE_HIP_SPEED = 50.0` torso-len/s | Upper bound | Excludes tracking-glitch/fall frame-pairs from the mean | N/A — per-frame-pair inclusion gate | Derived from an unrelated pipeline constant (`pipeline_utils.VELOCITY_CAP`) × an approximate body-height/torso-length ratio, not this feature's own fitted data |
| Walking Speed | Speed → risk mapping | Sigmoid center `1.0` torso-len/s, slope `3.0` | Transition point | Lower speed ⇒ higher risk | **Yes** — direct sigmoid output | Explicitly documented as *not* a clinical cut-point; picked only to avoid saturating over this proxy's own ~0.6-1.4 synthetic range |
| Stride Regularity | Ankle-track completeness | Need ≥50% of frames with valid raw ankle-y | Lower bound | Availability gate | N/A | Arbitrary round-number cutoff |
| Stride Regularity | Peak spacing | `find_peaks(..., distance=5)` frames | Lower bound | Minimum spacing between accepted step-peaks | N/A — detection parameter | Untested against varied real cadence/fps combinations |
| Stride Regularity | Peak count | Need ≥3 peaks, ≥2 valid intervals | Lower bound | Minimum data to compute a variability statistic | N/A — availability gate | — |
| Stride Regularity | CV → risk mapping | Sigmoid center `0.30`, slope `12.0` | Transition point | Higher CV (less regular) ⇒ higher risk | **Yes** | Explicitly documented as *not* the ~5% IMU-literature figure (this is a video-spatial proxy, ~4-5x larger scale); scale-matched only to this proxy's own synthetic 0.15-0.35 range |
| Postural Sway | "Stable" sub-window definition | `stable_subwindow=15` frames, `displacement_thresh=0.15` torso-lengths | Upper bound (displacement) | Only sub-windows below this net displacement count as "standing still" | N/A — inclusion gate | Round numbers, not derived from a measured natural-sway-vs-transition boundary |
| Postural Sway | Sway → risk mapping | Sigmoid center `0.05` torso-lengths, slope `15.0` | Transition point | Higher sway ⇒ higher risk | **Yes** | Docstring itself says: "no established population baseline is available in this codebase" — the most explicitly-acknowledged-uncalibrated threshold in the module |
| Sit-to-Stand | State definition | `_HIP_ANGLE_SITTING_MAX=125°`, `_HIP_ANGLE_STANDING_MIN=143°` | Upper / lower bound | Hip angle ranges defining "sitting" / "standing" | N/A — state-detection gate | Camera-angle/seat-geometry dependent — this session found a real miss (`Sit_Stand_AnklesInvisible.MOV`) where a GT-confirmed seated subject's hip angle never dropped below 156° |
| Sit-to-Stand | State debounce | `_STATE_CONFIRM_FRAMES=3` consecutive frames | Lower bound | Minimum run length to trust a state | N/A — gate | Frame-count, not time-based |
| Sit-to-Stand | Tracking-blackout distrust | `_MAX_TRUSTED_GAP_BEFORE_STATE=10` frames | Upper bound | A state emerging right after this long a blackout isn't trusted | N/A — gate | Mirrors an unrelated pipeline constant, not fit to this specific problem; frame-count based |
| Sit-to-Stand (fallback) | Minimum dip depth | `FAST_SIT_MIN_DESCENT_DEGREES=7.0°` | Lower bound | Minimum angle drop below the preceding stand's own mean to count as a "sit," in the fallback path | N/A — fallback-activation gate | Derived from a single real reference clip (~9.7° measured) with margin — thin evidentiary base |
| Sit-to-Stand (fallback) | Fall-adjacent translation guard | `FALLBACK_MAX_TRANSLATION_SPEED=1.0` torso-len/s | Upper bound | Rejects a candidate "stand" whose hip translates like a fall, not a postural change | N/A — gate | Derived from only 2 non-fall + 2 fall reference measurements (0.35, 0.46 vs. 2.88, 17.79) |
| Sit-to-Stand | Duration/reversal → risk mapping | Duration sigmoid center `2.0s` slope `1.5`; reversal sigmoid center `2.0` slope `0.8`; blend `0.6·duration + 0.4·reversal` | Transition points + blend weight | Longer/shakier ⇒ higher risk | **Yes** | Entirely unvalidated against any real TUG-style timing distribution; the 0.6/0.4 blend split is itself unjustified |
| *(aggregation)* | Signal weights | `walking_speed=1.0, stride_regularity=1.2, postural_sway=1.2, sit_to_stand=0.8` | Relative weights | How sub-scores combine into `risk_score` | **Determines the final score directly** | Not fit to outcome data; renormalizing over a variable-availability signal set can swing `risk_score` window-to-window purely from *which* signals happened to be available, even when each individual value is stable (found this session, `SitFloor_lowKeypoints_crossedLegs.MOV`) |

### 1.3 False positive / false negative sources found by direct tracing (this session and prior)

- **False positive** — `sit_to_stand` fires on deep bends/squats (no GT
  sitting event exists): hip angle alone cannot distinguish a deep squat
  from sitting on a chair (geometric degeneracy, `Bend_pickup_squat_*`,
  `Bend_pickup_*_leftRight`/`_back` clips).
- **False positive (directional)** — `walking_speed`'s ambulation gate
  fires on a purely vertical, non-locomotor translation (kneeling down),
  reading as slow walking with real risk impact.
- **False negative** — `sit_to_stand` misses a GT-confirmed genuine sit
  (`Sit_Stand_AnklesInvisible.MOV`) because hip angle never crosses
  `_HIP_ANGLE_SITTING_MAX` for that camera angle/seat geometry.
- **False negative (structural)** — `stride_regularity` requires ≥3
  detected peaks over ≥50% ankle-valid frames; any short, occluded, or
  slow-cadence bout below that floor silently returns unavailable rather
  than a (possibly still meaningful) partial estimate.
- **False negative (structural)** — `postural_sway` requires an entire
  15-frame sub-window with net displacement below `0.15` and no
  implausible interior speed; a person who sways continuously without ever
  holding still for 15 straight frames produces *no* sway reading at all,
  even though continuous sway is itself a strong instability signal.

---

## 2. What "calibration" can realistically mean here

Four distinct things are easy to conflate under "validation" — keeping
them separate is the difference between an honest dataset plan and an
overclaimed one.

| Level | What it means | What it needs | Can self-recorded footage achieve it? |
|---|---|---|---|
| **A. Structural/plausibility validation** | Does the pipeline run without crashing, produce values in a sane range, and move in the expected *direction* for an obviously-labeled scenario (e.g. does `risk_score` go up during an obvious instability clip)? | Any footage + your own eyeball judgment of what happened | **Yes** — this is what the last session's 28-clip validation already did |
| **B. Threshold calibration** | Given a *labeled* set of windows, choose numeric threshold/sigmoid-center values so the mapped risk values match the *relative ordering* your labels imply (e.g. "near-fall" windows should score higher than "normal walking" windows) | A labeled dataset spanning the actual range of behaviors each signal is meant to discriminate, with enough repetitions per category to see the natural spread, not just one example each | **Partially** — self-recorded footage with self-assigned behavioral labels (not clinical outcomes) *can* support this, with real caveats (see below) |
| **C. Predictive validation** | Given thresholds, measure how well `risk_score` predicts an actual future adverse outcome (a real fall, a clinical fall-risk assessment score) in a population | Outcome labels — a real fall event, or a validated clinical instrument score (e.g. Berg Balance Scale, TUG time cutoff, clinician fall-risk rating) attached to real subjects, ideally prospective | **No** — impossible without either real clinical outcome data or a validated instrument administered by a qualified assessor |
| **D. Clinical validation** | Level C, performed under a protocol suitable to support a clinical claim (ethics approval, defined population, statistical power, external replication) | All of C, plus formal study design | **No** — explicitly and permanently out of scope for a self-recorded FYP dataset; do not claim this regardless of how much footage is collected |

**What this session's plan targets: B, explicitly bounded.** Self-recorded
footage with behavioral labels you assign yourself (e.g. "this clip is a
deliberately slow/shuffling walk," "this clip is a fast, confident
sit-to-stand") lets you check that the *relative ordering* of signal
values matches what you intended to perform, and lets you replace an
arbitrary sigmoid center with one actually centered on your own measured
distribution's mid-point (e.g. "my normal-walking speed values cluster at
X, my deliberately-slow-walking values cluster at Y — center the sigmoid
between them," rather than the current practice of centering only to
avoid numerical saturation). **This is not the same as knowing that Y
actually corresponds to elevated real-world fall risk** — that would
require Level C/D labels (an actual fall outcome, or a validated clinical
instrument score) that no self-recorded dataset can supply. Every table
below is built for Level B. If the risk score is ever meant to support a
Level C/D claim, the labels required are outcome labels (real fall
occurrence, or a clinician-administered validated instrument score) tied
to real subjects over time — categorically different from anything a
single person recording themselves can produce.

---

## 3-9. Recording plan

Built directly from the threshold trace in Section 1 — each scenario is
chosen because it exercises a specific gate or risk-mapping function, not
generically. "Risk Signals Covered" names the exact signal(s)/threshold(s)
from Section 1.2 each scenario helps characterize.

### TABLE 2 — Videos to record

| Priority | Scenario | Label | Repetitions | Duration | Purpose | Risk Signals Covered | Dev/Test |
|---|---|---|---:|---:|---|---|---|
| P0 | Normal-pace walking, straight line, front-on | normal_walk | 10 | 10-15s | Establish baseline walking-speed/stride distribution | `walking_speed` center, `stride_regularity` center | Dev |
| P0 | Normal-pace walking, side-on | normal_walk_side | 6 | 10-15s | Camera-angle sensitivity of the same baseline | `walking_speed`, `stride_regularity` | Dev |
| P0 | Deliberately slow/shuffling walk | slow_walk | 10 | 10-15s | Populates the "elevated risk" tail of walking-speed distribution | `_speed_risk` upper tail | Dev |
| P0 | Fast/brisk walk | fast_walk | 8 | 8-12s | Populates the "low risk" tail; confirms sigmoid doesn't saturate too early | `_speed_risk` lower tail | Dev |
| P0 | Normal chair sit-to-stand, comfortable pace | sts_normal | 15 | 4-6s | Core sit-to-stand duration/reversal baseline | `_sit_to_stand_risk` duration center | Dev |
| P0 | Fast/perch-style sit-to-stand | sts_fast | 10 | 3-5s | Confirms `FAST_SIT_MIN_DESCENT_DEGREES`/fallback path still fires correctly across many trials, not just the one existing reference clip | `FAST_SIT_MIN_DESCENT_DEGREES`, `sit_to_stand` fallback | Dev |
| P0 | Quiet standing (arms relaxed) | quiet_stand | 10 | 8-10s | Baseline (low) `postural_sway` distribution | `_sway_risk` center | Dev |
| P0 | Deep bend/squat to pick something up (no chair) | bend_pickup | 12 | 4-6s | **Directly targets the confirmed geometric-degeneracy false-positive** — needed to see how far bend-angle overlaps sit-angle across many trials/subjects | `_HIP_ANGLE_SITTING_MAX` boundary, false-positive rate | Dev |
| P0 | Kneel down and back up | kneel | 8 | 4-6s | **Directly targets the confirmed walking-direction false positive** — populates vertical-translation cases for a future direction-aware gate | `MIN_AMBULATION_COHERENCE`, false-positive rate | Dev |
| P1 | Prolonged standing (30-60s, natural micro-shifts allowed) | prolonged_stand | 6 | 30-60s | Tests whether `stable_subwindow=15` correctly finds multiple stable sub-windows over a longer bout, and whether natural weight-shifting still registers as "stable" | `postural_sway` sub-window gate | Dev |
| P1 | Walking with a brief stop-and-resume mid-bout | walk_stop_start | 8 | 10-15s | Tests `MIN_AMBULATION_PATH`/coherence gates under a realistic non-uniform bout | `walking_speed` availability gates | Dev |
| P1 | Turning while walking (~180°) | walk_turn | 8 | 6-10s | Turning changes apparent hip-track direction sharply — tests whether coherence check spuriously fails a real walking bout | `MIN_AMBULATION_COHERENCE` | Dev |
| P1 | Unstable/irregular gait (deliberately uneven step timing, feet wider) | unstable_walk | 10 | 10-15s | Populates elevated `stride_regularity` CV range with a *sustained* bout (existing 28-clip corpus has none) | `_stride_cv_risk` upper tail | Dev |
| P1 | Repeated small balance corrections while standing (deliberate sway/wobble) | sway_wobble | 10 | 10-15s | Populates elevated `postural_sway` range directly (currently has zero real reference — most-uncalibrated threshold in the module) | `_sway_risk` upper tail | Dev |
| P1 | Slow, controlled stand-to-sit (reverse of sts_normal) | sit_down_normal | 10 | 4-6s | `compute_sit_to_stand` only detects the sit→stand direction; recording the reverse motion checks it does *not* spuriously fire in the wrong direction | `sit_to_stand` false-positive check | Dev |
| P1 | Difficulty initiating walking (a pause before the first step) | walk_init_delay | 6 | 8-12s | Common real mobility-impairment marker not currently captured by any signal — check whether it distorts `walking_speed`'s mean or is silently invisible to the current feature set | `walking_speed` (diagnostic — may reveal a feature gap, not just a threshold gap) | Dev |
| P1 | Stumble with recovery (deliberate, controlled, low height) | stumble_recover | 10 | 5-8s | **The single most important ambiguous-motion class** — must not read identically to a real fall | `FALLBACK_MAX_TRANSLATION_SPEED`, `MAX_PLAUSIBLE_HIP_SPEED` | Both (see Section 6) |
| P1 | Sudden fast turn / quick stop | quick_turn_stop | 8 | 4-6s | Fast but non-fall movement — checks `MAX_PLAUSIBLE_HIP_SPEED`'s margin isn't so tight it excludes genuine brisk motion | `MAX_PLAUSIBLE_HIP_SPEED` boundary | Dev |
| P2 | Lying down intentionally (controlled, onto a mat/bed) | lie_down | 6 | 5-8s | Confirms sway/speed signals correctly go unavailable (not spuriously high-risk) during a controlled floor transition | Availability-gate correctness | Dev |
| P2 | Getting up from the floor (controlled, from `lie_down`) | floor_getup | 6 | 5-8s | Different geometry than a chair stand — checks whether `_HIP_ANGLE_STANDING_MIN` generalizes | `sit_to_stand` geometry generalization | Dev |
| P2 | Reaching down without fully bending (light stretch) | reach_down | 8 | 3-5s | Milder version of `bend_pickup` — checks whether the false-positive boundary is graded or a hard cliff | `_HIP_ANGLE_SITTING_MAX` boundary, finer resolution | Dev |
| P2 | Repeated cycles of any P0 scenario back-to-back (e.g. 3x sit-stand-sit-stand) | rapid_cycles | 6 | 10-15s | Stress-tests the state debounce (`_STATE_CONFIRM_FRAMES`) and window-boundary behavior under rapid state alternation | `_STATE_CONFIRM_FRAMES` | Dev |
| P2 | Same normal-walk scenario at 3 camera distances | walk_distance_var | 3×3=9 | 10-15s | Torso-length-scaled features should be distance-invariant by design — direct empirical check, not just a code-review claim | Cross-cutting (scale-invariance assumption) | Dev |

**Held-out validation set**: once the Dev-set recordings above have been
used to *pick* any threshold value, a **separate batch of the same
scenarios from held-out subjects/sessions** (see Section 14) is what
belongs in Test — none of Table 2's Dev-labeled clips should double as
Test data.

### Section 4 — Normal/low-risk coverage, mapped to necessity

Going through your listed candidates against what the code actually uses:

| Candidate scenario | Necessary? | Why |
|---|---|---|
| Normal standing | **Yes** (P0 `quiet_stand`) | Directly populates `_sway_risk`'s low end — currently has zero real-footage reference |
| Normal walking | **Yes** (P0 `normal_walk`) | Populates `_speed_risk`/`_stride_cv_risk` low-risk end |
| Slow walking | **Yes** (P0 `slow_walk`) | Populates the high-risk tail the sigmoid is supposed to discriminate |
| Fast walking | **Yes** (P0 `fast_walk`) | Confirms the sigmoid's low-risk end doesn't saturate prematurely |
| Prolonged standing | **Yes but P1**, not P0 | Tests sub-window mechanics over a longer bout, not a new distribution per se |
| Normal sitting (static, no transition) | **No** | No signal in this module measures static sitting posture at all — GAIT here only measures the *transition* (sit-to-stand), not a seated-stillness signal; recording this teaches nothing about any current threshold |
| Normal sit-to-stand | **Yes** (P0 `sts_normal`) | Core of the sit-to-stand duration/reversal calibration |
| Normal stand-to-sit | **Yes but P1** | `compute_sit_to_stand` doesn't score this direction at all today — recording it is a *false-positive check* (confirm it correctly stays silent), not a calibration source for an existing threshold |
| Normal turning | **Yes but P1** (`walk_turn`) | Directly threatens the coherence gate's assumption of straight-line motion |
| Walking at different speeds | **Yes** — already covered by `slow_walk`/`normal_walk`/`fast_walk` as 3 distinct labeled tiers rather than one vague "varied speed" bucket, since the sigmoid needs distinguishable tiers, not a blended sample |
| Repeated walking (same bout multiple times) | **Yes, via repetition counts** (Section 10) rather than a separate scenario — the repetitions *are* this |
| Stopping and starting | **Yes but P1** (`walk_stop_start`) | Directly exercises `MIN_AMBULATION_PATH` under a realistic broken bout |

---

## 5. High-risk / instability coverage

| Candidate | Priority | Why it matters for the current code |
|---|---|---|
| Unstable/irregular gait | P1 (`unstable_walk`) | Directly populates `stride_regularity`'s CV upper tail — the corpus used this session has **zero** sustained real examples of this |
| Slow/shuffling gait | Covered by `slow_walk` (P0) | Same mechanism as slow walking; a genuinely shuffling gait (short, frequent steps) additionally stresses `stride_regularity`'s peak-detection spacing (`distance=5`) — worth a distinct sub-label if time allows (P2) |
| Excessive sway | P1 (`sway_wobble`) | The single most under-referenced threshold in the whole module (`_sway_risk` center has *zero* real-footage grounding today) |
| Repeated balance corrections | Same as `sway_wobble` — a corrective wobble and continuous sway look similar to `postural_sway`'s std-based measurement; one scenario, not two |
| Difficulty initiating walking | P1 (`walk_init_delay`) | Not measured by any current signal — recording this is diagnostic (does it distort `walking_speed`'s mean, or is it invisible?), not calibration of an existing number |
| Difficulty stopping | P2 | Related to `quick_turn_stop`; lower priority since no threshold specifically targets stopping behavior |
| Unstable turning | P2 | Combination of `walk_turn` + `sway_wobble`; useful once both individually understood |
| Near-fall / stumble → recovery | **P1, highest priority in this category** (`stumble_recover`) | This is the exact ambiguous case `FALLBACK_MAX_TRANSLATION_SPEED` and `MAX_PLAUSIBLE_HIP_SPEED` were tuned against using only 2 fall + 2 non-fall reference clips — needs many more examples to check the 1.0 torso-len/s and 50.0 torso-len/s boundaries aren't miscalibrated |
| Prolonged instability | P2 | Extended version of `sway_wobble`/`unstable_walk` — useful for confirming behavior doesn't degrade over a longer window, not for calibrating a new threshold |

---

## 6. Fall scenarios — safety-bounded

**Do not perform real, uncontrolled falls yourself.** This is not a hedge
— it's the direct instruction for this section, and it's not overly
cautious given what's actually needed: the existing `FALLBACK_MAX_TRANSLATION_SPEED`/
`MAX_PLAUSIBLE_HIP_SPEED` thresholds were already derived from the
project's existing 9 acted-fall clips (`test_footage/Sanawar Testing
7-22-26/`) plus a labelled-fall-dataset-derived constant
(`pipeline_utils.VELOCITY_CAP`) — you do not need to personally fall down
to add fall-adjacent signal coverage.

| Scenario | Safe to self-record? | Approach |
|---|---|---|
| Forward / backward / sideways fall | **No** | Already covered by the existing 9 Sanawar-set clips (`Backward_fall`, `Forward_fall`, `Side_fall`, `Off_axis_fall`); do not re-attempt these yourself |
| Fall during walking | **No** | Same — `Fall_and_lie.mp4`/`Far_fall.mp4` already cover this pattern |
| Sudden collapse / slow collapse | **No** | Same — `Slow_fall.mp4` already covers the slow-collapse case specifically |
| Stumble → recovery | **Yes** | This is `stumble_recover` in Table 2 — a genuinely controlled, low-amplitude loss-of-balance-then-catch, safe at normal standing height with no intent to actually fall |
| Stumble → fall / loss of balance → fall | **No** | This is where "stumble" tips into "fall" — do not perform this deliberately; if more of this specific transition is needed, it requires either professionally staged stunt-fall footage (padded surfaces, trained faller, spotter) or continued use of the existing acted-fall clips |
| Loss of balance → recovery | **Yes** | Same as `stumble_recover` — controlled, low-amplitude, no ground contact intended |

**If more fall diversity is genuinely needed beyond the existing 9 clips**:
the safer alternative is professionally staged footage — a stunt
performer or physical-therapy fall-training session on a crash mat, with
a spotter — not an untrained person (including yourself) performing
additional falls. For anything approaching Level C/D validation (Section
2), the correct source is a proper clinical/geriatric-fall dataset
collected under an ethics-approved protocol, not self-recorded footage of
any kind, staged or otherwise.

---

## 7. Ambiguous non-fall scenarios (false-positive characterization)

This directly targets the two confirmed false-positive mechanisms found
this session, so it's prioritized above generic coverage:

| Scenario | Priority | Why (tied to actual code weakness) |
|---|---|---|
| Bending down / picking something up | **P0** | Confirmed false-positive source (geometric degeneracy) — highest priority in this whole section |
| Squatting | **P0** | Same mechanism, deeper angle excursion — confirmed false-positive source |
| Kneeling | **P0** | Confirmed false-positive source (walking-direction gate) |
| Crouching | P1 | Intermediate between bending and squatting — useful for mapping *how* the false-positive rate changes with dip depth, not a new mechanism |
| Sitting quickly (fast, controlled) | **P0** (already `sts_fast`) | Must not read as a fall via the translation guard |
| Lying down intentionally | P1 (already `lie_down`) | Must not read as elevated risk via any of the 4 signals |
| Getting up from the floor | P1 (already `floor_getup`) | Different geometry than a chair-stand — tests whether `_HIP_ANGLE_STANDING_MIN` generalizes |
| Reaching down (light, no real bend) | P2 (already `reach_down`) | Boundary-resolution case for the bend/squat false positive |
| Turning quickly | P1 (already `quick_turn_stop`) | Tests `MAX_PLAUSIBLE_HIP_SPEED`'s margin against genuine (non-fall) fast motion |
| Sudden stopping | P1 (already part of `walk_stop_start`/`quick_turn_stop`) | Same |
| Sudden acceleration | P2 | Lower priority — no threshold specifically keys on acceleration (only frame-pair speed) |
| Fast sit-to-stand | **P0** (already `sts_fast`) | Directly the scenario `FAST_SIT_MIN_DESCENT_DEGREES`/the fallback path exists for |
| Stumbling but recovering | **P1** (already `stumble_recover`) | Highest-value ambiguous case overall (Section 5/6) |
| Deliberately moving quickly (no turn, no stop, just brisk) | Covered by `fast_walk` (P0) | Not a distinct new scenario |

---

## 8. Pose-estimation / real-world edge cases

Split into **Calibration** (changes what a threshold *should* be) vs.
**Robustness** (checks the pipeline doesn't crash/misbehave, but doesn't
inform a threshold *value*) — conflating these wastes recording effort on
cases that can't actually move a number.

| Category | Case | Calibration or Robustness? | Why |
|---|---|---|---|
| Landmark | Jitter | Robustness | Already synthetically covered (`tests/test_gait_risk.py` fixtures); real jitter mainly stress-tests the confidence-gating fixed this session, not a threshold value |
| Landmark | Missing/partial landmarks | Robustness | Tests availability-gate correctness (does the signal correctly go `None` rather than producing a garbage value), not a threshold's numeric center |
| Landmark | Low-confidence landmarks | Robustness | Same |
| Landmark | Temporary landmark loss | Robustness | Exercises `_MAX_TRUSTED_GAP_BEFORE_STATE` — worth **one or two P2 clips** to confirm the 10-frame boundary behaves, but does not by itself justify changing that number without many more trials |
| Landmark | Sudden landmark jumps | Robustness | Exercises `MAX_PLAUSIBLE_HIP_SPEED`'s glitch-rejection — same, P2 only |
| Occlusion | Partial/lower/upper body occlusion | Robustness | Availability-gate correctness, already partially covered by the existing 28-clip corpus (`*lowKeypoints*`, `*HalfLandmarks*`) |
| Occlusion | Furniture obstruction | Robustness | Same, lower priority — no existing clip type |
| Camera | Front/side/oblique view | **Calibration** | `_HIP_ANGLE_SITTING_MAX`/`_HIP_ANGLE_STANDING_MIN` are angle thresholds measured in 2D image space — camera angle directly changes the *apparent* hip angle, so this is exactly what caused the confirmed `Sit_Stand_AnklesInvisible` miss. **This should be built into Table 2's scenarios directly** (record `sts_normal`/`bend_pickup`/etc. from ≥2 angles each) rather than treated as a separate pass |
| Camera | Different heights/distances | **Calibration** for distance (tests the scale-invariance assumption directly, already in Table 2 as `walk_distance_var`); **Robustness** for height (no threshold is height-sensitive by design, assuming the scale-invariance assumption holds) |
| Camera | Low lighting | Robustness | Affects MediaPipe's landmark confidence, not the GAIT thresholds themselves once landmarks exist |
| Camera | Camera shake | Robustness | Same category as landmark jitter |
| Camera | Subject entering/leaving frame | Robustness | Exercises availability-gate correctness at window boundaries, not a threshold value |
| Movement | Slow/fast/short/long movement | **Calibration** | Already the core of Table 2 (`slow_walk`/`fast_walk`/duration variation) |
| Movement | Turning, stopping, starting | **Calibration** | Already in Table 2 (`walk_turn`, `walk_stop_start`) |
| Movement | Movement across window boundaries | Robustness | Depends on the caller's windowing/stride policy (outside this module), not a `gait_risk.py` threshold |

**Practical implication**: most of Section 8's list is robustness, not
calibration — don't spend your limited recording budget there. The one
calibration-relevant item hiding in this section is **camera angle**,
which should be folded into the P0/P1 scenarios above (shoot each from
≥2 angles) rather than treated as its own separate video category.

---

## 9. Subject variability

**If you record alone**: every threshold calibrated this way is
calibrated to *your own* body proportions, gait style, and habitual
movement speed. This is a real, unavoidable limitation — it does **not**
generalize to other people's normal ranges, and absolutely does not
generalize across age groups (the population this risk score is
conceptually aimed at). Say this explicitly in any write-up: *"thresholds
calibrated against N=1 self-recorded footage reflect that one subject's
movement distribution, not a population baseline."*

**Sources of variability that matter for these specific thresholds**:
- Height/torso length: mostly absorbed by the module's torso-length
  scaling (by design) — lower priority to vary deliberately.
- Body proportions (limb-length ratios): directly affects hip-angle
  geometry (`_HIP_ANGLE_SITTING_MAX`/`_HIP_ANGLE_STANDING_MIN`) — matters.
- Walking style/speed habits: directly shifts where your personal
  "normal" sits relative to `_speed_risk`'s center — matters most.
- Clothing (loose/baggy vs. fitted): affects MediaPipe landmark
  confidence, a robustness concern more than a threshold-calibration one.
- Camera distance/orientation: already addressed via the scale-invariance
  design and `walk_distance_var` — matters for confirming the *design*
  works, not for expanding subject diversity per se.

**Minimum practical number for a useful *development* dataset**: **3
subjects**, if more than one person is available to you. This is not
enough for any generalization claim, but 1 subject can't distinguish "this
threshold is wrong" from "this subject is unusual"; 3 gives at least a
crude sense of between-subject spread without requiring a large
coordination effort. If only you are available, proceed with N=1, record
that limitation explicitly everywhere the resulting thresholds are
described, and treat any resulting threshold as a personally-tuned
starting point, not a general one.

---

## 10. Repeated trials

**Recommendation: 8-15 repetitions per P0 scenario, 5-10 per P1, 3-6 per
P2** (the specific numbers already used in Table 2), not a single
round number applied everywhere. Reasoning, not an arbitrary pick:

- A sigmoid center chosen from **1 example** is indistinguishable from
  noise — you cannot tell whether that one clip was typical or an outlier.
- The current code's own precedent (`FALLBACK_MAX_TRANSLATION_SPEED`,
  derived from exactly 2 non-fall + 2 fall clips) is explicitly flagged in
  its own docstring as a "thin evidentiary base" — repeating that mistake
  at a larger scale is exactly what this dataset plan exists to fix.
- **You need enough repetitions to see a *distribution*, not a point
  estimate** — with 8-15 reps you can compute a mean and spread (e.g.
  min/max/std) for each scenario's feature values, which is the minimum
  needed to *justify* moving a sigmoid center (Section 15), versus
  picking a new arbitrary single number.
- Diminishing returns set in well before 20: for a single-subject,
  single-condition scenario, the within-condition variance is unlikely to
  need more than ~10-15 samples to characterize with the precision this
  heuristic system needs (this is not a clinical-trial power calculation
  — it's proportionate to how the resulting number will actually be used,
  as a non-clinical sigmoid center).

---

## 11. Video length recommendations

| Type | Recommended duration | Why |
|---|---:|---|
| Stationary (quiet stand, prolonged stand) | 8-10s (30-60s for `prolonged_stand`) | Must clear `MIN_WINDOW_FRAMES` (90 frames/~3s) with margin, and give `postural_sway`'s 15-frame sub-windows several full sub-windows to average over |
| Walking bouts | 10-15s | Needs multiple full gait cycles for `stride_regularity` (≥3 peaks) with margin, not just the bare minimum |
| Sit-to-stand / stand-to-sit | 4-6s (3-5s for fast variants) | The transition itself is brief (~1-2s observed in existing footage); a few seconds of stable state before/after is needed so the state-confirmation debounce (`_STATE_CONFIRM_FRAMES`) has something to confirm against |
| Instability (sway, unstable walk) | 10-15s | Same reasoning as walking bouts — needs several cycles of the unsteady behavior, not one blip |
| Near-fall / stumble-recover | 5-8s | Long enough to capture pre-stumble baseline, the event itself, and post-recovery stabilization as distinguishable phases |
| Fall (existing corpus only — do not self-record) | N/A | Already fixed by the existing clips (3.7-11.8s each) |
| Recovery (post-instability stabilization) | Included within the parent clip (5-8s tail), not a separate recording | Recovery only makes sense as the tail of an instability/stumble clip, not standalone |

All of the above are practical relative to `MIN_WINDOW_FRAMES=90`
(~3s) — nothing here should be recorded shorter than ~4s even for the
briefest transitions, to leave margin for the debounce/confirmation gates.

---

## 12. Labeling protocol

| Field | Required? | Example | Why needed |
|---|---|---|---|
| `subject_id` | Yes | `S1` | Enables subject-level split (Section 14) and subject-variability analysis (Section 9) |
| `scenario` | Yes | `bend_pickup` | Matches Table 2's scenario taxonomy directly |
| `trial_number` | Yes | `03` | Distinguishes repetitions of the same scenario/subject |
| `camera_config` | Yes | `front_1.5m_1m-height` | Camera angle directly affects hip-angle thresholds (Section 8) — must be recorded, not assumed constant |
| `event_start_time` / `event_end_time` | Yes, per labeled event within the clip | `2.3` / `3.9` (seconds) | Needed for event-level labeling (Section 13) — matches the existing `start_time,end_time,state,label` convention already used by `test_footage/*_GT.csv` |
| `behaviour_label` | Yes | `sit_to_stand_fast` | The actual scenario performed in that time span |
| `fall_or_no_fall` | Yes | `no_fall` | Every self-recorded clip should be `no_fall` except references to the existing acted-fall corpus — do not invent a "fall" label for anything you record yourself under this plan (Section 6) |
| `intentional_or_unintentional` | Yes | `intentional` | Everything you deliberately perform is `intentional`; this field exists so that if any genuinely unintentional stumble/wobble happens during recording, it can be flagged and reviewed separately rather than silently mixed into the intentional labels |
| `recovery_or_no_recovery` | Only for instability/stumble clips | `recovery` | Distinguishes `stumble_recover` (planned, always recovery) from any unplanned event |
| `severity` | **Do not include**, per your own instruction | — | No meaningful basis exists for a severity scale from self-recorded, non-clinical footage — inventing one would misrepresent the data's actual information content |
| `notes` | Optional but recommended | `"slight camera shake at 4s"` | Freeform space for anything not captured by the structured fields — cheap to include, expensive to reconstruct later if omitted |

---

## 13. Event-level vs. video-level labels

**Label at all three levels the existing corpus already effectively
uses, and this plan should keep**:

1. **Video-level** (`scenario`, `subject_id`, `camera_config`): one row of
   metadata per file — cheap, always available, needed for the
   dev/test split.
2. **Event-level** (`event_start_time`/`event_end_time`/`behaviour_label`
   per labeled segment): **the one that actually matters most for
   threshold calibration**, because — exactly as you note — a single
   video may contain `normal_walk → stumble → recovery` or
   `standing → sit-to-stand → walking` as distinct phases, and a
   threshold can only be meaningfully calibrated against the specific
   phase it's meant to characterize, not the whole clip's average. Use
   the same `start_time,end_time,state,label` CSV format already used by
   `test_footage/*_GT.csv` — this is directly compatible with
   `benchmarks/validate_gait_on_footage.py` without any format changes.
3. **Temporal-window-level**: **do not hand-label this** — it's
   derivable automatically from (2) by intersecting each `assess_risk()`
   window's `[start, end]` timestamps against the event-level CSV, the
   same way this session's cross-referencing against the existing
   `test_footage/*_GT.csv` files was done. Hand-labeling every
   90-frame-window separately would be redundant effort on top of (2)
   and a source of label drift if the two ever disagreed.

---

## 14. Train / calibration / validation split

**No split exists yet** — none has been recorded. The design, so it's
ready the moment recording starts:

| Split | Purpose | Recommended proportion | Subject separation |
|---|---|---:|---|
| Development/calibration | Free iteration — trace bugs, pick which signal to gate on, choose candidate threshold values from observed distributions | ~60% of subjects/sessions | Used freely, watched repeatedly |
| Validation | Check candidate thresholds generalize before calling them final | ~20% | Different subject(s)/session(s) from Dev where possible |
| Held-out (final) | Touched exactly once, to report a final check | ~20% | Different subject(s)/session(s) from both above |

**Same subject in multiple sets?** Avoid if you have ≥2 subjects — put
each subject entirely in one split. With only 1 subject available, the
next-best separation is by **recording session/day** (e.g. everything
recorded on day 1 is Dev, day 2 is Validation, day 3 is Held-out) so at
least clothing/lighting/exact positioning differ between splits, even
though the underlying body and movement style don't — and say explicitly
that this is a weaker separation than a true subject-level split, not a
substitute for one.

**Leakage prevention**: 
- Decide the split **before** watching any footage frame-by-frame, the
  same principle already applied in the previous session's report
  (`docs/GAIT_ANGLE_NOISE_INVESTIGATION_REPORT.md` Section I).
- Once a threshold value is picked using Dev-set distributions, check it
  against Validation. If it fails, **revise using Dev only**, then
  re-check against Validation — never adjust directly against Validation
  or Held-out results.
- Held-out is used **once**, at the very end, only to report how the
  final chosen thresholds behave — not to iterate further. If Held-out
  reveals a problem, that is a finding to report honestly (and grounds
  for a *new* recording round), not something to patch by going back and
  re-tuning against the same Held-out set.
- The existing 28 `test_footage/` clips (already reused across multiple
  sessions for GAIT plausibility checks) should **not** be retroactively
  treated as this split's Validation or Held-out set — they've already
  been looked at too many times while iterating on GAIT behavior to serve
  as a clean check (same conclusion as the prior session's report,
  Section I).

---

## 15. How thresholds would actually be recalibrated (procedure only — not implemented here)

Once Section 3-14's data exists, per threshold:

- **Gate thresholds** (`MIN_AMBULATION_PATH`, `MIN_AMBULATION_COHERENCE`,
  `MAX_PLAUSIBLE_HIP_SPEED`, `_HIP_ANGLE_SITTING_MAX`/`_STANDING_MIN`,
  `_STATE_CONFIRM_FRAMES`, `_MAX_TRUSTED_GAP_BEFORE_STATE`,
  `FAST_SIT_MIN_DESCENT_DEGREES`, `FALLBACK_MAX_TRANSLATION_SPEED`): these
  are **classification boundaries** between two labeled classes (e.g.
  "genuine walking" vs. "stationary jitter," "postural stand" vs.
  "fall-adjacent motion"). With enough labeled examples of both classes,
  the right tool is **ROC analysis** (to see the full
  sensitivity/specificity trade-off curve across candidate cutoffs) plus
  **Youden's J statistic** (to pick a single default cutoff that
  maximizes `sensitivity + specificity - 1`) as a starting point — then
  adjusted via **cost-sensitive thresholding** if false positives and
  false negatives matter differently in practice (they likely do here: a
  missed instability signal is arguably worse than an over-cautious one,
  which would argue for a cutoff shifted from Youden's J toward higher
  sensitivity).
- **Sigmoid centers/slopes** (`_speed_risk`, `_stride_cv_risk`,
  `_sway_risk`, `_sit_to_stand_risk`'s two components): these map a
  *continuous* feature to a *continuous* risk contribution, not a
  binary decision — the right approach is to first plot the **empirical
  distribution** (histogram/percentiles) of each feature across your
  labeled scenario categories (e.g. `quiet_stand` vs. `sway_wobble` for
  `postural_sway`), place the sigmoid center at a percentile that
  separates the bulk of the "normal" category from the bulk of the
  "elevated" category (e.g. the 90th percentile of `quiet_stand` /
  10th percentile of `sway_wobble`, adjusted toward whichever direction
  cost-sensitivity favors), and check the resulting mapping with a
  **calibration curve** (does the mapped risk value track the empirical
  frequency of the "elevated" label across bins) rather than trusting the
  curve shape by construction.
- **Signal weights** (`_SIGNAL_WEIGHTS`): once individual signals are
  individually calibrated, **precision-recall analysis** on the combined
  `risk_score` against whatever event-level label is being predicted
  (e.g. "this window overlaps an ambiguous/elevated-risk event") is the
  natural next step to check whether the current 1.0/1.2/1.2/0.8 split is
  actually pulling its weight, or whether one signal should count for
  more/less than it currently does.

**Critical caveat, restated because it's easy to lose sight of once a
procedure exists**: everything in this section calibrates thresholds
against **your own behavioral labels** ("I intended this to be a slow
walk," "I intended this to be a stumble"), which is Level B calibration
only (Section 2). **If you only ever have "normal" and "fall" labels**,
that is *not* sufficient to calibrate the intermediate risk states this
system actually has — `walking_speed`, `stride_regularity`,
`postural_sway`, and `sit_to_stand` are each continuous, graded signals
with their own sigmoid, and a two-class normal/fall label collapses all
of that gradation into one boundary, telling you nothing about, say,
where the `postural_sway` sigmoid's center should sit relative to a
"mild wobble" versus "normal" distinction. The scenario taxonomy in
Table 2 exists specifically to avoid this collapse — it provides graded
labels (`slow_walk` vs. `normal_walk` vs. `fast_walk`, not just
"normal"/"not normal") matching the number of distinct behavioral tiers
each signal is actually meant to discriminate.

None of the above should be implemented until the data described in
Sections 3-14 actually exists — this section describes the eventual
procedure only.

---

## 16. Safety summary

| Category | Examples | Who/how |
|---|---|---|
| Safe to self-record | Everything in Table 2 except fall scenarios: walking (all speeds/turns), sit-to-stand (all speeds), standing/sway, bends/squats/kneels, stumble-and-recover (controlled, low-amplitude, no ground contact) | You, alone or with volunteer subjects, no special equipment beyond a camera and clear floor space |
| Requires controlled/staged simulation, not self-recording | Additional fall diversity beyond the existing 9 clips, if ever needed | A trained stunt performer or physical-therapy fall-training session, crash mat, spotter present |
| Should come from professionally collected datasets | Any Level C/D validation (Section 2) — real fall-outcome labels or clinician-administered validated instrument scores tied to real (especially elderly/at-risk) subjects | An ethics-approved clinical/geriatric-fall research dataset, not this project's own recording effort at any scale |

---

## 17. Final deliverable

### TABLE 1 — Current risk features

| Risk Signal | Feature | Current Threshold | Direction | Purpose | Calibration Data Needed |
|---|---|---:|---|---|---|
| Walking Speed | Mean hip speed (torso-len/s) | Gate: path≥0.5, coherence≥0.2, speed≤50.0/frame-pair; risk center=1.0, slope=3.0 | Lower speed → higher risk | Gait-speed fall-risk proxy | Graded walking-speed distribution across ≥3 deliberate speed tiers (Table 2 P0) |
| Stride Regularity | CV of ankle-oscillation interval | Gate: ≥50% ankle-valid, ≥3 peaks, spacing≥5 frames; risk center=0.30, slope=12.0 | Higher CV → higher risk | Step-timing-consistency proxy | Sustained normal + sustained deliberately-irregular walking bouts (Table 2 P0/P1) |
| Postural Sway | Std-dev of stable-subwindow hip position | Gate: subwindow=15 frames, displacement≤0.15; risk center=0.05, slope=15.0 | Higher sway → higher risk | Trunk-stability proxy | Quiet-standing baseline + deliberate-sway range (Table 2 P0/P1) — currently has **zero** real reference |
| Sit-to-Stand | Transition duration + reversal count | State bounds 125°/143°; debounce=3 frames; blackout=10 frames; fallback dip≥7.0°, translation≤1.0 len/s; risk: duration center=2.0s, reversal center=2.0 | Longer/shakier → higher risk | TUG-style transition-quality proxy | Many-trial normal + fast sit-to-stand, plus bend/squat/kneel negative controls (Table 2 P0) |

### TABLE 2 — Videos to record

*(See Section 3-9 full table above — 23 scenarios, priority-tagged P0/P1/P2.)*

### TABLE 3 — Edge cases

*(See Section 8 full table above.)*

### TABLE 4 — Dataset split

| Dataset | Purpose | Recommended size | Subject separation | Used for |
|---|---|---:|---|---|
| Development/calibration | Free iteration, pick candidate threshold values | ~60% of subjects/sessions | Own subjects/sessions, watched freely | Choosing sigmoid centers, gate boundaries |
| Validation | Confirm candidates generalize before finalizing | ~20% | Different subject(s)/session(s) from Dev | Revising thresholds if they fail here (loop back to Dev) |
| Held-out (final) | One-time final check | ~20% | Different subject(s)/session(s) from both above | Reporting final behavior only — never re-tuned against |

### TABLE 5 — Labeling requirements

*(See Section 12 full table above.)*

### TABLE 6 — Prioritized recording plan

| Priority | What to record | Why | Minimum number |
|---|---|---|---:|
| 1 | `normal_walk` (front + side) | Baseline for `walking_speed`/`stride_regularity` — everything else is relative to this | 16 clips (10 front + 6 side) |
| 2 | `sts_normal` + `sts_fast` | Core sit-to-stand duration/reversal calibration, and confirms the fallback path across many trials (currently 1 reference clip) | 25 clips (15 + 10) |
| 3 | `bend_pickup` + `kneel` | Directly targets the two confirmed false-positive mechanisms from this session's investigation | 20 clips (12 + 8) |
| 4 | `quiet_stand` + `sway_wobble` | `postural_sway` currently has **zero** real-footage reference at either end of its range — highest-leverage single gap in the whole module | 20 clips (10 + 10) |
| 5 | `slow_walk` + `fast_walk` | Populates both tails of the walking-speed sigmoid | 18 clips (10 + 8) |
| 6 | `stumble_recover` | Highest-value ambiguous-motion class; directly stress-tests the fall-adjacent translation guard beyond its current 2-clip evidentiary base | 10 clips |

**Total for priorities 1-6: ~109 clips.** If starting smaller:

**If you record only 20-30 videos initially, record these first (in this
order), based directly on the weakest-evidenced thresholds found by
tracing the actual code:**

1. `quiet_stand` × 6 — `postural_sway`'s risk center currently has zero
   real grounding; this is the single highest-leverage gap.
2. `sts_normal` × 6 — core sit-to-stand baseline.
3. `bend_pickup` × 5 — confirmed false-positive mechanism #1.
4. `kneel` × 4 — confirmed false-positive mechanism #2.
5. `normal_walk` (front-on) × 5 — walking-speed/stride baseline.
6. `sts_fast` × 3 — fallback-path evidence beyond the single existing
   reference clip.
7. `sway_wobble` × 2 — populates `postural_sway`'s currently-empty
   elevated-risk end.

That's 31 clips prioritized by evidentiary weakness, not generic
coverage — trim `sway_wobble` to 1 or drop `kneel` to 3 if you need to
land closer to 20.

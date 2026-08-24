"""
gait_risk.py
============
GaitRiskAssessor.assess_risk(window) -> {"risk_score": ..., "signals": [...]}

THIS IS A RISK-SCORE INTERFACE, NOT A FALL/NO-FALL CLASSIFIER. It exposes a
continuous, graded assessment of longer-term fall risk inferred from gait
quality (see gait_features.py and docs/GAIT_LITERATURE_REVIEW.md), which is
conceptually distinct from -- and does not replace -- the existing per-frame
Fall/Lying/Sitting/Standing/Unknown classifiers in src/posture/. There is no
`fall_detected` boolean anywhere in this module's output, and there is no
external API of any kind (no HTTP/REST/cloud service) -- this is a plain
local Python class, called directly.

======================================================================
INPUT CONTRACT
======================================================================
`window`: List[dict], one dict per video frame, in chronological order.
Same row schema `pipeline_utils.build_pose_row()` already produces:
    {
        "timestamp": float | str(float),  # seconds; frame index / 30 is
                                           # used as a fallback if missing
                                           # or non-numeric (same fallback
                                           # pipeline_utils._compute_velocity
                                           # uses)
        "keypoints": List[float],         # flat [x1,y1,x2,y2,...,x33,y33],
                                           # MediaPipe-normalized to [0,1]
                                           # image coordinates; NaN for any
                                           # landmark not confidently seen
                                           # (see pipeline_utils.build_pose_row's
                                           # visibility-masking).
    }
Only `keypoints` (and `timestamp`, for velocity/duration computations) are
read; `posture_label`/`fall_detected`/other build_pose_row fields are
ignored if present.

- **Single window only, not a batch.** One call = one risk assessment over
  one extended time span. There is no batch dimension the way
  LSTM/TCN/RF's `.predict()` accepts one fixed-size window per call --
  gait signals (a walking bout, a sit-to-stand event) don't have a fixed
  length the way a 30-frame posture window does, so batching many
  different-length windows into one array isn't a natural fit here. Call
  `assess_risk()` once per window you want scored.
- **Minimum length**: `gait_features.MIN_WINDOW_FRAMES` (90 frames, ~3s at
  30fps) is enforced -- shorter windows raise `ValueError` rather than
  returning a silently-unreliable score. In practice, useful stride/sway
  signals typically need noticeably more than the floor (multiple gait
  cycles) -- see "insufficient_data" behavior below.
- **Preprocessing**: none required from the caller. Normalization
  (hip-centered, torso-length-scaled position) and NaN/Inf handling happen
  inside this module -- pass raw MediaPipe-derived rows directly.
- **No camera/subject calibration exists in this pipeline BY DEFAULT** (no
  known subject height, no known camera distance) -- see gait_features.py's
  module docstring. All position-based signals are body-scale-normalized
  proxies, not real-world (meters, seconds-to-clinical-cutoff) units. The
  one opt-in exception: `assess_risk()`'s `_torso_baseline` parameter lets
  a caller that has independently established a same-subject, same-session
  "confirmed standing" reference (gait_features.compute_torso_baseline())
  pass it in to gate `walking_speed`'s availability during a severe torso
  foreshortening (e.g. a sustained forward bend) -- see that parameter's
  own docstring. This is still self-referential (the subject's own earlier
  measurement), not external ground truth (no known height/distance is
  introduced), and remains fully inert unless a caller explicitly opts in.

======================================================================
OUTPUT CONTRACT
======================================================================
    {
        "risk_score": float in [0.0, 1.0] | None,
        "signals": [ {...}, ... ],
    }

`risk_score`:
    0.0 = lower assessed risk, 1.0 = higher assessed risk, on this
    module's own internal (uncalibrated) scale -- NOT a probability of a
    fall occurring, and NOT a clinically validated cut-off scale. It is a
    weighted average of whichever of the four sub-signals below could
    actually be computed from this window (see gait_features.py per-signal
    docstrings for the literature basis and exact computation).

    `None` when NONE of the four signals could be computed (e.g. a mostly
    static window with no detected strides, no sit-to-stand transition, and
    no valid hip tracking for sway) -- returning a fabricated middle value
    in that case would be silently-incorrect output, so this contract
    returns None instead and explains why via `signals`. Check
    `signals` for the reason before treating a None score as "low risk."

`signals`: List[dict], one entry per candidate gait signal (always 4
entries, regardless of availability), each:
    {
        "name": str,                 # "walking_speed" | "stride_regularity"
                                      # | "postural_sway" | "sit_to_stand"
        "available": bool,           # whether this window let this signal
                                      # be computed at all
        "value": float | dict | None,# the RAW measured value (see
                                      # gait_features.py for units/meaning);
                                      # None when available=False
        "risk_contribution": float | None,  # this signal's sub-score as
                                      # used in the risk_score blend, clipped
                                      # to [RISK_CONTRIBUTION_FLOOR,
                                      # RISK_CONTRIBUTION_CEILING] = [0.02,
                                      # 0.98] (see that constant's own
                                      # docstring) -- an uncalibrated
                                      # heuristic sigmoid should not report
                                      # near-total certainty at either
                                      # extreme; None when available=False
        "calibrated": bool,          # always False currently -- no signal
                                      # here has real clinical/population
                                      # calibration, see module docstrings
        "description": str,          # human-readable explanation
        "category": str,             # "gait" | "postural" -- see below
        "reliability": float | None, # [0,1] or None -- see below
        "weight_confidence": float | None,  # [0,1] or None -- see below;
                                      # UNLIKE reliability, this DOES affect
                                      # risk_score's blend (stride_regularity
                                      # only currently -- see below)
        # stride_regularity ONLY, additionally:
        "cadence_steps_per_min": float,  # see below
        "n_events": int,
    }
These are genuinely computed from `gait_features.py`, not fabricated --
if a signal isn't available for this window, `available` is False and
`value`/`risk_contribution` are None; nothing is invented to fill the gap.

`category`: purely informational grouping, ADDITIVE to this contract (does
not affect risk_score) -- "gait" for signals that measure active locomotion
quality (walking_speed, stride_regularity), "postural" for signals that
measure static/transitional stability (postural_sway, sit_to_stand). Makes
explicit a split that already existed implicitly in which four signals this
module chose to combine.

======================================================================
SIGNAL QUALITY / RELIABILITY
======================================================================
`reliability`: float in [0, 1], or None when `available` is False --
graded confidence in a signal's own VALUE, distinct from the existing
binary `available` gate. `available=True` already means a signal cleared
every existing hard gate (landmark validity, ambulation/stationarity,
peak-prominence filtering, etc. -- see gait_features.py); `reliability`
answers a DIFFERENT question that binary gate cannot: of the signals that
DID clear their gates, how much real, usable data actually supported the
reported number? A stride-regularity CV computed from a window with 98%
valid ankle tracking is better-evidenced than the same CV computed from a
window that barely cleared the 50% coverage floor -- both currently read
as `available=True` with no way to tell them apart; `reliability` is that
distinction, made explicit.

Concretely, per signal (see each gait_features.compute_*'s own
`_quality_out` docstring for the exact derivation):
  - walking_speed / stride_regularity: fraction of frame-pairs/frames with
    valid, plausible landmark tracking that actually contributed to the
    reported value.
  - postural_sway: fraction of the window's candidate stable sub-windows
    that actually qualified and contributed to the mean.
  - sit_to_stand: fraction of the reported transition's own frames where
    BOTH left and right sides were confidently tracked (reuses the
    existing `both_sides_confident` mechanism -- see
    gait_features._count_reversals' docstring).

IMPORTANT -- `reliability` itself is STILL reported as TRANSPARENCY
METADATA ONLY and does NOT affect risk_score/weight_total/any other
computation in assess_risk() below, exactly as before. A SEPARATE field,
`weight_confidence` (see below), was added in a later session and DOES
affect risk_score -- for stride_regularity only, and derived from
`n_events` (small-SAMPLE-SIZE confidence), not from `reliability`
(landmark-TRACKING confidence) -- these answer genuinely different
questions (see `_stride_regularity_confidence`'s own module-level
docstring in this file for the full rationale and real-footage evidence:
a stride-regularity CV computed from only 3-4 detected peak events is a
noisier statistical estimate than one computed from many, independent of
how cleanly those few events were tracked). This was the exact "explicit,
disclosed decision point" the previous paragraph's earlier version left
open for reliability -- resolved here for n_events specifically, with
real evidence, not decided silently and not extended to `reliability`
itself or to the other three signals without separate evidence for each.

`weight_confidence`: float in [0, 1], or None when `available` is False --
the multiplier actually applied to this signal's nominal `_SIGNAL_WEIGHTS`
entry in the weighted-average blend below. 1.0 (no dampening) for every
signal/window except stride_regularity windows with fewer than
`STRIDE_EVENTS_FULL_CONFIDENCE` detected events -- see
`_stride_regularity_confidence`'s docstring for the exact ramp and its
real-footage derivation. Reported so a caller can see exactly how much
(if any) discount was applied, not just infer it from `n_events` alone.

`cadence_steps_per_min` / `n_events` (stride_regularity ONLY -- absent
from the other three signals' entries, since cadence is not a meaningful
concept for them): the detected step rate and the number of step-scale
events it was estimated from. `cadence_steps_per_min` is `60 / mean(peak
interval)` -- a PROXY (peak-detection rate), NOT a clinically validated
measurement, same caveat as `walking_speed`'s torso-lengths/sec.

TERMINOLOGY, VERIFIED NOT ASSUMED (see docs/GAIT_CODE_REVIEW.md's gait-
event audit): the underlying `ankle_y` signal is `(LEFT_ANKLE_y +
RIGHT_ANKLE_y) / 2` -- BOTH ankles averaged together, not tracked
separately -- so each detected peak corresponds to ONE FOOT's swing-phase
excursion (a STEP), not a full gait cycle (a STRIDE = both feet, left
heel-strike to the next left heel-strike). Verified directly against this
module's own synthetic walking generator (tests/test_gait_risk.py::
_walking_window, whose own internal stride period parameter is known):
detected peak-to-peak intervals measured almost exactly HALF that known
stride period -- i.e. two peaks per stride, matching the standard
biomechanical fact that a two-legged gait cycle produces two step events.
`cadence_steps_per_min` is named and computed accordingly (STEPS, the
correct unit for the standard clinical "cadence" parameter, which IS
conventionally steps/minute, not strides/minute) -- calling this field
"...strides_per_min" would have been the terminology error, not the other
way around. The pre-existing `stride_regularity`/"stride-to-stride
interval" naming (this same peak interval, used for the CV above) predates
this finding and is NOT renamed here -- that name is used pervasively
across this module's docstrings, tests, and the `_SIGNAL_SPECS` table
below, and rehoming it is a larger, separate decision than fixing this
session's own newly-added field names; the underlying CV signal's
VALIDITY as a step-to-step regularity proxy is unaffected either way (see
gait_features.compute_stride_regularity's own docstring for an explicit
note on this).

Reuses gait_features._detect_gait_events, the same peak-detection this
module's CV is already computed from -- no new gate, no new data
requirement, essentially free.

======================================================================
Example
======================================================================
    from src.gait.gait_risk import GaitRiskAssessor
    assessor = GaitRiskAssessor()
    result = assessor.assess_risk(window)   # window: 5-10+ seconds of rows
    result["risk_score"]   # -> 0.63, or None if nothing was measurable
    result["signals"]      # -> list of 4 signal dicts (see above)
"""

import math
from typing import List, Optional, Dict, Any

from src.gait import gait_features as gf

# Sub-score weights when a signal IS available. Renormalized (weighted
# sum / sum of weights of AVAILABLE signals only) over whichever subset of
# signals is actually available for a given window -- see assess_risk()'s
# `weighted_sum`/`weight_total` loop below. Weights reflect the reviewed
# literature's relative emphasis (stride variability and postural sway
# reported as at least as informative as gait speed alone; sit-to-stand is
# a single-event bonus signal, weighted lower since it's frequently just
# absent from a given window) -- these are a starting point pending real
# validation data, not derived from a fitted model (see
# docs/GAIT_DATA_ASSESSMENT.md for why no such fit is possible yet).
#
# IMPORTANT (see docs/GAIT_CODE_REVIEW.md finding #17): these weights only
# affect the blend when TWO OR MORE signals are simultaneously available.
# When exactly one signal is available for a window (common -- sit_to_stand
# in particular is absent from most windows by design, and the others can
# each independently be unavailable too), that signal's risk_contribution
# IS risk_score exactly, regardless of its nominal weight -- a single-term
# weighted average always reduces to the one term, since the weight appears
# in both numerator and denominator and cancels. This is mathematically
# correct (see WeightBlendingTests in tests/test_gait_risk.py for a direct
# regression test of this and the >=2-signal weighted-average case), just
# easy to misread the table above as "sit_to_stand always counts less" --
# it doesn't, when it's the only signal present.
_SIGNAL_WEIGHTS = {
    "walking_speed": 1.0,
    "stride_regularity": 1.2,
    "postural_sway": 1.2,
    "sit_to_stand": 0.8,
}


# ======================================================================
# RISK-CONTRIBUTION EPISTEMIC-HUMILITY BOUNDS
# ======================================================================
# Every risk-mapping function below (`_speed_risk`/`_stride_cv_risk`/
# `_sway_risk`/`_sit_to_stand_risk`) is a sigmoid, which is mathematically
# monotonic and bounded in (0, 1) by construction but can still get
# ARBITRARILY close to 0 or 1 for an input far enough from its center --
# and, on real footage, does: found via this project's own full-corpus
# risk-mapping audit (benchmarks/gait_risk_distribution_analysis.py, all
# ~44 real clips), `_speed_risk` reports risk_contribution as low as
# 0.00015-0.005 during the ACTIVE-FALL portion of multiple real fall clips
# (Chair_fall.mp4, Side_fall.mp4, Far_fall.mp4) -- not a degenerate/
# implausible reading (the underlying speed, 1.8-3.9 torso-lengths/sec, is
# a real, already-plausibility-gated measurement; see
# gait_features.MAX_PLAUSIBLE_HIP_SPEED, which guards against genuinely
# IMPOSSIBLE per-frame glitches, a different and already-solved problem)
# -- but reported with a confidence (99.98%+ certain "not at risk") this
# admittedly uncalibrated, heuristic, `"calibrated": False` sigmoid mapping
# was never validated to actually support. Symmetrically, `_stride_cv_risk`
# reaches risk_contribution up to ~0.999 on real footage (see
# `_stride_regularity_confidence`'s own docstring for the small-n_events
# case this overlaps with).
#
# INVESTIGATED AND REJECTED: a targeted fix specifically for the
# walking_speed-during-a-fall case (e.g. capping the INPUT speed at a
# "plausible normal walking" ceiling before mapping to risk) was tried
# first and found NOT safely separable on this project's own real corpus
# -- genuine brisk walking (Diagonal_Walk_1.mov, recorded specifically for
# oblique/diagonal walking validation) measures up to 3.430 torso-lengths/
# sec, which OVERLAPS the fall-onset speed range above (1.8-3.9) almost
# entirely. A speed-based cap tight enough to blunt the fall cases would
# also blunt this genuine fast-walking clip's own real signal; one loose
# enough to spare it would barely touch the fall cases (Side_fall.mp4
# alone reaches 3.6-3.9, inside Diagonal_Walk_1.mov's own real range).
# Consistent with this project's own established standard elsewhere (see
# docs/GAIT_DATA_ASSESSMENT.md Section 11's rejected walking_speed
# residual-band candidates for the same "did not cleanly separate on the
# full corpus, so not shipped" reasoning) -- NOT fixed here; genuinely
# needs either a second discriminating signal (this module has none that
# distinguishes "fast walking" from "fast falling" using position/speed
# alone) or more data, not a threshold guess. Recorded as an open,
# disclosed, data-dependent limitation.
#
# WHAT WAS SHIPPED INSTEAD: a general, signal-agnostic, symmetric floor/
# ceiling on the REPORTED risk_contribution (not a per-signal, scenario-
# specific rule) -- reflecting that a heuristic, `"calibrated": False`
# sigmoid should never assert near-total certainty of "no risk" or
# "extreme risk" from a single window, regardless of which signal or
# which real-world situation produced the extreme input. This is a
# STRICTLY WEAKER claim than trying to detect and specifically handle
# fall-adjacent motion (which the rejected candidate above shows this
# module cannot currently do reliably) -- it does not claim to fix the
# walking_speed/fall-speed overlap; it only prevents this module from
# reporting more confidence than an unvalidated heuristic can honestly
# support, at either end of its range, for any of the four signals.
# 0.02/0.98 is a small, symmetric margin (98% of the full theoretical
# range is untouched) chosen to affect only the genuinely-extreme tail
# values found above, not to compress or re-center the mapping's ordinary
# behavior -- verified: every genuine-walking/genuine-transition
# risk_contribution value found anywhere in the real corpus during this
# audit falls well inside [0.02, 0.98] already; only the fall-onset
# walking_speed cases and the smallest-n_events stride_regularity cases
# were ever clipped.
RISK_CONTRIBUTION_FLOOR = 0.02
RISK_CONTRIBUTION_CEILING = 0.98


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


# ======================================================================
# STRIDE-REGULARITY SMALL-SAMPLE CONFIDENCE WEIGHTING
# ======================================================================
# Addresses a real, evidenced problem (found via this project's own
# real-time-integration audit, see docs/GAIT_DATA_ASSESSMENT.md Section
# 15.3): a stride-regularity CV computed from very few detected peak
# events (gait_features.compute_stride_regularity's own hard floor is 3 --
# fewer than that and the signal is unavailable, not merely low-confidence)
# is a genuinely noisier statistical estimate than the SAME CV formula
# computed from many events, yet BOTH previously entered `risk_score` at
# the identical nominal weight (1.2, the highest of the four signals),
# with `n_events` reported only as inert transparency metadata. Confirmed
# on real footage: a real, GT-confirmed "sustained standing" window on
# Deep_Bend_2.mov produced CV=0.91-0.97 from n_events=3-4 (brief pre-bend
# weight-shift, not gait), which -- combined with `_stride_cv_risk`'s own
# steep slope, see that function's docstring -- saturates risk_contribution
# to ~0.999, i.e. the SAME as a robustly-evidenced severely-irregular gait.
#
# WHY WEIGHT, NOT AVAILABILITY: a hard n_events floor (reject below N)
# was considered and rejected. Real genuine walking already in this
# project's own corpus can legitimately have few events within a single
# gait_features.MIN_WINDOW_FRAMES (90-frame, ~3s) window -- measured
# directly: Moving_in_out_frame.MOV (a real, GT-confirmed walking clip)
# produces genuine, plausible CV values (0.27-0.33, matching this
# project's own documented "normal" range) from only 4-5 detected events
# per 90-frame window, simply because ~3s at a normal ~100-120 steps/min
# cadence only contains that many real steps. A hard floor set high enough
# to exclude the Deep_Bend_2.mov noise case (n_events=3-4) would ALSO
# reject this genuine walking evidence -- exactly the "do not simply
# suppress the signal universally" failure this mechanism is required to
# avoid. Down-WEIGHTING (this section) lets both cases still report a
# value and a risk_contribution (fully transparent, unchanged), while
# letting the BLEND lean on high-n_events evidence more than low-n_events
# evidence -- the same statistical intuition behind why a sample mean's
# trustworthiness (standard error) shrinks with sqrt(n), applied here as a
# smooth, bounded weight adjustment rather than a literal standard-error
# calculation (this proxy's peak-interval CV is not proven to follow the
# same distributional assumptions those formulas require, so a smooth,
# monotonic APPROXIMATION of "more events = more trustworthy" is used,
# not a claim of statistical exactness).
#
# THRESHOLD DERIVATION (real FULL-corpus evidence -- ran
# benchmarks/gait_risk_distribution_analysis.py over all 44 real clips in
# test_footage/, both older corpora plus GAIT_Analysis_Test_Footages/, zero
# extraction errors; see docs/GAIT_DATA_ASSESSMENT.md's own later section
# for the complete write-up): across every one of the 56 stride_regularity
# -available windows found in the ENTIRE corpus, n_events distributes as
# 3 (29 windows, 52%) / 4 (16) / 5 (7) / 6 (2) / 8 (1) / 9 (1) -- i.e.
# MORE THAN HALF of every real stride_regularity reading this pipeline has
# ever produced sits at the hard minimum (3), and only 2 of 56 (3.6%)
# reach 8 or more. This distribution itself is real evidence FOR this
# mechanism's necessity (most real readings genuinely are minimally
# evidenced), not just for where to place the plateau. STRIDE_EVENTS_
# FULL_CONFIDENCE=8 sits at the real P99 (8.5) / observed maximum (9) --
# reachable (unlike an earlier, unvalidated draft of this constant that
# checked only a 37/44-clip partial run and, missing the two highest-
# evidence real windows, set this at 6), but only by the genuinely
# best-evidenced tail, not the typical case. A per-fps caveat, disclosed
# rather than solved here: this corpus spans real capture rates from ~23fps
# to ~60fps, and gait_features.compute_stride_regularity's 90-FRAME (not
# 90-frame-normalized-to-time) window means a 60fps clip's window covers
# meaningfully less real wall-clock time (and therefore fewer achievable
# real step events at any given cadence) than a 23fps clip's -- n_events
# is not perfectly comparable across clips of different capture rates as a
# result. Not addressed here (would mean changing gait_features.py's
# window semantics, a larger change than this risk-mapping session's own
# scope); flagged as a known contributing source of the spread above, not
# hidden. STRIDE_EVENTS_CONFIDENCE_FLOOR (applied at the hard n_events=3
# minimum, i.e. the MAJORITY of real windows) is deliberately NOT zero --
# a 3-event CV is weaker evidence, not NO evidence, and this module's own
# weighted-average renormalization (see `assess_risk()` below) already
# means a fully-suppressed (zero-weight) signal is indistinguishable from
# `available=False`, which would misrepresent what actually happened (a
# real value WAS computed; it is reported LESS TRUSTED, not treated as
# absent).
MIN_STRIDE_EVENTS_FOR_CV = 3  # mirrors gait_features.compute_stride_regularity's
# own hard `len(peaks) < 3: return None` floor -- the confidence ramp below
# starts exactly where availability itself starts, never below it.
STRIDE_EVENTS_FULL_CONFIDENCE = 8
STRIDE_EVENTS_CONFIDENCE_FLOOR = 0.35


def _stride_regularity_confidence(n_events: Optional[int]) -> float:
    """[STRIDE_EVENTS_CONFIDENCE_FLOOR, 1.0] confidence multiplier applied
    to stride_regularity's EFFECTIVE weight in assess_risk()'s blend (see
    this section's own module-level docstring for the full rationale) --
    does NOT change `risk_contribution` itself (that stays the raw,
    transparent sigmoid mapping of the measured CV) or `available`.

    sqrt-shaped ramp between the two anchors (statistically motivated, not
    an exact formula -- see this section's docstring): rises quickly just
    above the floor, then flattens as it approaches 1.0, mirroring how an
    estimator's own marginal trustworthiness gain per additional sample
    shrinks as the sample count grows (the same qualitative shape behind
    a ~1/sqrt(n) standard-error curve), rather than a straight line that
    would treat the 3rd and 8th additional event as equally informative.

    <= MIN_STRIDE_EVENTS_FOR_CV -> the floor (the least this mechanism ever
    trusts an available value, applied when n_events is KNOWN to be small);
    >= STRIDE_EVENTS_FULL_CONFIDENCE -> 1.0 (no dampening, byte-identical
    to this module's pre-existing behavior for a well-evidenced window).
    `None` (n_events genuinely unknown, e.g. a caller that supplies a risk-
    mapping function directly without going through compute_stride_
    regularity's own `_quality_out` reporting -- every REAL assess_risk()
    call always has it populated whenever stride_regularity is available,
    since that function unconditionally sets it) is deliberately NEUTRAL
    (1.0), not the floor -- with no n_events evidence at all, there is no
    basis to either trust or distrust this specific dimension more than
    the module already does by computing risk_contribution at all; assuming
    the worst case from an absence of information would be a stronger,
    unevidenced claim than assuming no adjustment, matching this module's
    existing convention elsewhere (e.g. `_torso_baseline=None` means "don't
    gate," not "assume the worst")."""
    if n_events is None:
        return 1.0
    if n_events <= MIN_STRIDE_EVENTS_FOR_CV:
        return STRIDE_EVENTS_CONFIDENCE_FLOOR
    if n_events >= STRIDE_EVENTS_FULL_CONFIDENCE:
        return 1.0
    frac = (n_events - MIN_STRIDE_EVENTS_FOR_CV) / float(STRIDE_EVENTS_FULL_CONFIDENCE - MIN_STRIDE_EVENTS_FOR_CV)
    return float(STRIDE_EVENTS_CONFIDENCE_FLOOR + (1.0 - STRIDE_EVENTS_CONFIDENCE_FLOOR) * math.sqrt(frac))


def _speed_risk(speed: float) -> float:
    """Lower speed -> higher risk.

    Center chosen the same way _stride_cv_risk's was (see that function's
    docstring): matched to this metric's own observed scale, not an
    imported clinical number. An earlier version centered this at 1.75
    torso-lengths/sec by analogy to a quick isolated debug measurement that
    turned out not to represent this function's real operating range --
    this module's own steady/unsteady walking validation (see
    docs/GAIT_DATA_ASSESSMENT.md) produces smoothed speeds around
    ~0.6-1.4 torso-lengths/sec for both a brisk and a slow synthetic
    walker, so a 1.75 center left both saturated at the "slow" end of the
    sigmoid, compressing away the exact contrast this signal exists to
    detect. 1.0 is the midpoint of that observed range -- still a
    heuristic, uncalibrated choice (torso-lengths/sec has no established
    real-world cut-point), just one that isn't degenerate on the scale
    this function actually receives."""
    return float(_sigmoid(-(speed - 1.0) * 3.0))


def _stride_cv_risk(cv: float) -> float:
    """Higher stride-interval CV -> higher risk.

    The center below is NOT the ~5% figure the IMU stride-TIME-variability
    literature uses -- an earlier version of this function used that value
    directly and it was wrong: this module's CV comes from ankle-height
    PEAK-DETECTION on a video-derived spatial oscillation, a fundamentally
    different (and, empirically, ~4-5x larger-scale) measurement than
    IMU-derived stride TIMING, so reusing the literature's absolute number
    just saturated this function near 1.0 for every window regardless of
    actual regularity, silently destroying this signal's ability to
    discriminate anything (caught by this module's own steady-vs-unsteady
    synthetic validation -- see docs/GAIT_DATA_ASSESSMENT.md). 0.30 is
    chosen only to keep the sigmoid non-degenerate over the range this
    proxy actually produces (~0.15-0.35 in validation) -- it is a
    scale-matching choice, not a clinical threshold of any kind, and
    should be replaced once real gait footage lets this be calibrated
    against actual outcomes."""
    return float(_sigmoid((cv - 0.30) * 12.0))


def _sway_risk(sway: float) -> float:
    """Higher postural sway -> higher risk. Heuristic center; no
    established population baseline is available in this codebase."""
    return float(_sigmoid((sway - 0.05) * 15.0))


def _sit_to_stand_risk(result: Dict[str, float]) -> float:
    """Longer duration and more direction-reversals ("shakier") during the
    sit-to-stand transition -> higher risk, in the same spirit as clinical
    Timed-Up-and-Go scoring, but on this module's own uncalibrated scale."""
    duration_risk = _sigmoid((result["duration_sec"] - 2.0) * 1.5)
    reversal_risk = _sigmoid((result["reversal_count"] - 2.0) * 0.8)
    return float(0.6 * duration_risk + 0.4 * reversal_risk)


class GaitRiskAssessor:
    """Rule-based, first-pass fall-risk assessor over gait-quality signals.

    See this module's docstring for the full input/output contract. Holds
    no state between calls (each assess_risk() call is independent) and
    loads no model file -- this is a deliberately simple, interpretable
    rule-based scorer per docs/IMPLEMENTATION_PLAN.md Section 3's own
    recommendation to start simple given the lack of gait-specific training
    data, not a placeholder for a model that's actually implemented
    elsewhere.
    """

    # (signal name, feature-extraction fn, risk-mapping fn, category,
    # description) -- a single data-driven table instead of four
    # hand-copied blocks. The previous version called each risk-mapping
    # function (_speed_risk, _stride_cv_risk, ...) TWICE per signal -- once
    # to build the signal entry, once more for the weighted sum -- pure
    # duplicated work, and a real correctness risk if the two call sites
    # were ever edited independently and drifted apart. Now each is
    # computed exactly once per signal and reused for both.
    #
    # `category` ("gait" | "postural") is a purely INFORMATIONAL grouping,
    # not used anywhere in the risk_score computation below -- it makes
    # explicit a split that already existed implicitly in which signals
    # measure ACTIVE LOCOMOTION quality (walking_speed, stride_regularity)
    # versus STATIC/TRANSITIONAL stability (postural_sway, sit_to_stand).
    # Exposed on each signal entry (see _signal_entry) so a caller can
    # group/filter without needing to hardcode this project's own
    # four-signal names elsewhere.
    _SIGNAL_SPECS = (
        ("walking_speed", gf.compute_walking_speed, _speed_risk, "gait",
         "Mean hip-center speed across the window, in torso-lengths/second "
         "(not meters/second -- no camera/subject calibration exists). "
         "Lower speed is treated as higher risk."),
        ("stride_regularity", gf.compute_stride_regularity, _stride_cv_risk, "gait",
         "Coefficient of variation of stride-to-stride interval, estimated "
         "from ankle-height oscillation peaks. Higher (less regular) is "
         "treated as higher risk. None if fewer than 3 strides were "
         "detected in this window."),
        ("postural_sway", gf.compute_postural_sway, _sway_risk, "postural",
         "Standard deviation of hip-center position (torso-lengths) during "
         "sub-windows where the person is not substantially translating. "
         "Higher sway is treated as higher risk. None if no sufficiently "
         "still sub-window was found (e.g. the person is moving throughout)."),
        ("sit_to_stand", gf.compute_sit_to_stand, _sit_to_stand_risk, "postural",
         "Duration (seconds) and direction-reversal count of a detected "
         "sitting->standing transition, in the spirit of Timed-Up-and-Go "
         "scoring. Longer/shakier is treated as higher risk. None if no "
         "clean sit-to-stand transition was observed in this window "
         "(the common case -- most windows won't contain one)."),
    )

    def assess_risk(self, window: List[dict], _torso_baseline: Optional[float] = None) -> Dict[str, Any]:
        """See this module's docstring for the full contract.

        3D WORLD LANDMARKS (see gait_features.WORLD_LANDMARKS_ROOT_CAUSE_FIX's
        docstring): if any row in `window` carries an OPTIONAL
        `"world_keypoints"` key (MediaPipe's pose_world_landmarks, flat
        x/y/z x 33 landmarks, real-world meters -- see
        gait_features._raw_world_keypoint_array), it does NOT change
        `walking_speed`/`postural_sway`/`stride_regularity`'s underlying
        hip-position track by itself (that stays 2D-only -- see
        gait_features._torso_scaled_hip_track's own docstring for why
        mixing a 2D hip-position track with a 3D torso-length scale was
        tried and reverted: it broke genuine toward-camera walking
        recall). 3D world landmarks only ever matter when `_torso_baseline`
        (below) is ALSO supplied, as a same-kind (length-to-length) input
        to that gate.

        `_torso_baseline`: OPTIONAL, opt-in, NOT part of this method's
        stable output contract -- a fixed reference torso length from
        gait_features.compute_torso_baseline(), established by the CALLER
        from a span of this same clip/session believed to represent
        confirmed standing (see that function's own docstring). When
        supplied, gates `walking_speed`'s and `stride_regularity`'s
        availability against it always (both share the identical 2D
        hip-track degeneracy this gate targets -- see gait_features.
        MIN_TORSO_BASELINE_RATIO's own "STRIDE_REGULARITY VALIDATION
        SCOPE" note for when stride_regularity's own gate was added), and
        ALSO gates `postural_sway`'s availability against it WHEN 3D world
        landmarks are present (see gait_features.MIN_TORSO_BASELINE_RATIO's
        own "2D-MODE / 3D-MODE" docstring for why the 2D version of this
        gate deliberately excludes postural_sway, while the 3D version
        covers all three). Still NOT wired into `sit_to_stand` (a different
        mechanism -- hip-angle geometry, not `_torso_scaled_hip_track`
        translation -- not exposed to this same degeneracy).
        `_torso_baseline` must have
        been computed with `_world_raw` supplied just as consistently as
        this call will supply `window`'s own world landmarks, or the ratio
        check compares mismatched units (2D image-fraction vs. 3D meters)
        -- see compute_torso_baseline's own docstring. Leave as None (the
        default) to preserve today's exact behavior -- this class still
        holds no state between calls either way; the caller must supply
        this on every call where it wants the gate active, matching this
        method's existing stateless, single-call contract."""
        self._validate_window(window)

        # Computed ONCE and shared across all four signal functions below.
        # Before this, each of compute_walking_speed/compute_postural_sway/
        # compute_stride_regularity/compute_sit_to_stand independently
        # re-parsed the same window into raw (T, 66) keypoints via
        # gait_features._raw_keypoint_array() -- profiling a full
        # assess_risk() call showed that parse (window rows -> keypoint
        # pairs, via pipeline_utils._extract_keypoint_pairs) was the single
        # largest cost, repeated 3 times for no reason. Doesn't change any
        # function's result, only whether the work is done once or
        # multiple times (verified by the existing tests still passing
        # byte-identically after this change).
        #
        # `shared_ts` follows the same pattern for gait_features._timestamps():
        # after the vectorization work above, compute_walking_speed /
        # compute_postural_sway / compute_stride_regularity / compute_sit_to_stand
        # each independently recomputing it was measured at ~24% of a full
        # assess_risk() call (see _timestamps' own docstring) -- computed
        # once here instead. compute_postural_sway only started needing this
        # once its own plausibility gate (mirroring compute_walking_speed's)
        # was added -- see that function's docstring.
        shared_raw = gf._raw_keypoint_array(window)
        # Optional (see this method's own docstring) -- an all-NaN array for
        # any window whose rows don't carry `"world_keypoints"`. Used ONLY
        # by the walking_speed/postural_sway availability gate below (NOT
        # by shared_hip_track, which stays 2D-only -- see
        # _torso_scaled_hip_track's own docstring for why a 2D/3D mix was
        # tried there and reverted). Computed once here for the same
        # sharing reason `shared_raw` is.
        shared_world_raw = gf._raw_world_keypoint_array(window)
        shared_hip_track = gf._torso_scaled_hip_track(window, _raw=shared_raw)
        shared_ts = gf._timestamps(window)

        signals: List[Dict[str, Any]] = []
        weighted_sum = 0.0
        weight_total = 0.0

        for name, feature_fn, risk_fn, category, description in self._SIGNAL_SPECS:
            # Fresh per-signal dict each iteration -- each compute_* function
            # fills this in (as a side effect, not via its return value) with
            # signal-quality/reliability metadata ONLY when it returns a real
            # value (see e.g. gait_features.compute_walking_speed's own
            # `_quality_out` docstring). Passing a fresh `{}` here rather than
            # a shared one keeps one signal's quality info from ever leaking
            # into another's entry.
            quality_out: Dict[str, Any] = {}
            if name == "stride_regularity":
                # Needs BOTH _raw (ankle positions) AND _hip_track (its own
                # ambulation/stationarity gate, added to close the false-
                # positive class documented in gait_features.compute_stride_
                # regularity's docstring -- a stationary subject's ankle
                # jitter must not fabricate a stride-regularity signal).
                # `_torso_baseline`/`_world_raw` passed for the same reason
                # as walking_speed below (a later session, see
                # gait_features.MIN_TORSO_BASELINE_RATIO's "STRIDE_
                # REGULARITY VALIDATION SCOPE" note): this signal's
                # ambulation gate runs on the identical 2D hip track
                # walking_speed's does, so it needs the identical torso-
                # collapse gate, not a separately-invented one.
                value = feature_fn(window, _raw=shared_raw, _hip_track=shared_hip_track, _ts=shared_ts,
                                    _quality_out=quality_out, _torso_baseline=_torso_baseline,
                                    _world_raw=shared_world_raw)
            elif name == "walking_speed":
                # `_torso_baseline` is intentionally passed ONLY here (and
                # to postural_sway below, 3D-mode only) -- see this method's
                # own docstring and gait_features.MIN_TORSO_BASELINE_RATIO's
                # "2D-MODE / 3D-MODE" docstring.
                value = feature_fn(window, _raw=shared_raw, _hip_track=shared_hip_track, _ts=shared_ts,
                                    _quality_out=quality_out, _torso_baseline=_torso_baseline,
                                    _world_raw=shared_world_raw)
            elif name == "postural_sway":
                value = feature_fn(window, _raw=shared_raw, _hip_track=shared_hip_track, _ts=shared_ts,
                                    _quality_out=quality_out, _torso_baseline=_torso_baseline,
                                    _world_raw=shared_world_raw)
            elif name == "sit_to_stand":
                value = feature_fn(window, _raw=shared_raw, _ts=shared_ts, _quality_out=quality_out)
            else:
                # Unreachable with the current fixed _SIGNAL_SPECS (all 4
                # entries are covered by the branches above) -- kept as a
                # defensive fallback, not dead code to delete: if a 5th
                # signal were ever added here without also updating this
                # dispatch, it would land here and only get `_raw` shared
                # (no `_hip_track`/`_ts`/`_quality_out`). That's not silently
                # wrong -- every compute_* function already falls back to
                # computing its own `_ts`/`_hip_track` internally when not
                # supplied (see each function's own docstring), and treats a
                # missing `_quality_out` as "don't bother reporting
                # reliability" -- just a lost sharing/reporting optimization,
                # not a correctness bug, so this branch is deliberately left
                # in place rather than removed or replaced with a raise.
                value = feature_fn(window, _raw=shared_raw)
            risk_contribution = risk_fn(value) if value is not None else None
            if risk_contribution is not None:
                # Epistemic-humility clip -- see RISK_CONTRIBUTION_FLOOR's
                # own module-level docstring for the full real-footage
                # evidence and why a targeted (rather than this general)
                # fix was tried first and rejected. Applied uniformly to
                # all four signals, not just the one that motivated it.
                risk_contribution = min(max(risk_contribution, RISK_CONTRIBUTION_FLOOR), RISK_CONTRIBUTION_CEILING)
            # weight_confidence: [0, 1] multiplier on this signal's WEIGHT
            # in the blend below (see _stride_regularity_confidence's own
            # module-level docstring for the full rationale) -- distinct
            # from `risk_contribution`, which is left untouched (still the
            # raw, transparent risk-mapping of the measured value) and from
            # `reliability` (landmark-tracking confidence, a DIFFERENT axis
            # -- see this module's own "SIGNAL QUALITY / RELIABILITY"
            # docstring section). Defaults to 1.0 (no dampening,
            # byte-identical to this module's behavior before this
            # mechanism existed) for every signal/window that doesn't
            # supply the specific quality metric a confidence function
            # needs -- currently only stride_regularity's `n_events` feeds
            # one; walking_speed/postural_sway/sit_to_stand are therefore
            # completely unaffected by this change.
            weight_confidence = 1.0
            if name == "stride_regularity" and risk_contribution is not None:
                weight_confidence = _stride_regularity_confidence(quality_out.get("n_events"))
            signals.append(self._signal_entry(name, value, risk_contribution, category, description,
                                               quality_out, weight_confidence if risk_contribution is not None else None))
            if risk_contribution is not None:
                effective_weight = _SIGNAL_WEIGHTS[name] * weight_confidence
                weighted_sum += effective_weight * risk_contribution
                weight_total += effective_weight

        risk_score = (weighted_sum / weight_total) if weight_total > 0 else None

        return {"risk_score": risk_score, "signals": signals}

    @staticmethod
    def _signal_entry(name, value, risk_contribution, category, description,
                       quality: Optional[Dict[str, Any]] = None,
                       weight_confidence: Optional[float] = None) -> Dict[str, Any]:
        # `reliability`/`category`/`weight_confidence` are ADDITIVE fields on
        # top of this module's existing signal-entry contract (name/
        # available/value/risk_contribution/calibrated/description, all
        # unchanged in meaning and type) -- see this module's own docstring,
        # "SIGNAL QUALITY / RELIABILITY" section, for what each means.
        # `reliability` is always present (None when unavailable, mirroring
        # `value`/`risk_contribution`'s own convention); `cadence_steps_
        # per_min`/`n_events` are only present on the stride_regularity
        # entry, since cadence is not a meaningful concept for the other
        # three signals. `weight_confidence` -- UNLIKE `reliability` -- DOES
        # affect risk_score (see assess_risk()'s own weighting loop and
        # _stride_regularity_confidence's docstring): reported here so a
        # caller can see exactly how much this signal's nominal weight was
        # discounted, not just that it was. Defaults to 1.0 for any
        # available signal that isn't stride_regularity, matching that this
        # mechanism does not currently apply to them.
        entry = {
            "name": name,
            "available": value is not None,
            "value": value,
            "risk_contribution": risk_contribution,
            "calibrated": False,
            "description": description,
            "category": category,
            "reliability": (quality or {}).get("reliability"),
            "weight_confidence": weight_confidence if value is not None else None,
        }
        if quality and "cadence_steps_per_min" in quality:
            entry["cadence_steps_per_min"] = quality["cadence_steps_per_min"]
            entry["n_events"] = quality.get("n_events")
        return entry

    @staticmethod
    def _validate_window(window) -> None:
        if window is None:
            raise TypeError("assess_risk(window): window must be a list of pose row dicts, got None.")
        if not isinstance(window, (list, tuple)):
            raise TypeError(f"assess_risk(window): window must be a list of pose row dicts, got {type(window).__name__}.")
        if len(window) == 0:
            raise ValueError("assess_risk(window): window is empty -- at least gait_features.MIN_WINDOW_FRAMES rows are required.")
        if len(window) < gf.MIN_WINDOW_FRAMES:
            raise ValueError(
                f"assess_risk(window): window has {len(window)} frames, needs at least "
                f"{gf.MIN_WINDOW_FRAMES} (~3s at 30fps) to attempt gait feature extraction. "
                "This is a hard floor for even attempting extraction -- reliable "
                "stride/sway signals typically need noticeably more (multiple gait cycles)."
            )
        # Timestamp monotonicity (see docs/GAIT_CODE_REVIEW.md finding #8):
        # checked against the RAW per-row `timestamp` field, not against
        # gait_features._timestamps()'s post-fallback resolved array --
        # deliberately, to avoid a false alarm this check could otherwise
        # cause on its own: a single row with a missing/non-numeric
        # timestamp gets replaced by _timestamps() with an i/30.0
        # frame-index fallback (see that function's own docstring), which
        # has no relationship to a real (e.g. wall-clock) timestamp scale
        # used by the surrounding rows -- comparing the POST-fallback array
        # could flag an artifact of the fallback itself as "out of order."
        # Only rows with an actually-present, well-formed numeric timestamp
        # are compared to each other here; rows without one are skipped
        # (their fallback ordering is trivially monotonic with array index
        # anyway, so they can't be the source of a genuine problem this
        # check exists to catch). Consecutive EQUAL timestamps are allowed
        # (not flagged) -- most downstream math already excludes zero-dt
        # pairs gracefully (`dt_positive` gates throughout gait_features.py);
        # it's a genuine DECREASE that indicates frames are out of
        # chronological order, which nothing downstream is designed to
        # detect or recover from (see _confirmed_runs' docstring: state-run
        # detection operates on array-index order, not verified
        # chronological order).
        last_ts = None
        for i, row in enumerate(window):
            if not isinstance(row, dict):
                raise TypeError(f"assess_risk(window): window[{i}] must be a dict (pose row), got {type(row).__name__}.")
            if "keypoints" not in row:
                raise ValueError(f"assess_risk(window): window[{i}] is missing required key 'keypoints'.")
            try:
                ts_num = float(row.get("timestamp"))
            except (TypeError, ValueError):
                ts_num = None
            if ts_num is not None and math.isfinite(ts_num):
                if last_ts is not None and ts_num < last_ts:
                    raise ValueError(
                        f"assess_risk(window): window[{i}]['timestamp']={ts_num} is earlier than "
                        f"an earlier row's timestamp {last_ts} -- frames must be in non-decreasing "
                        "chronological order."
                    )
                last_ts = ts_num

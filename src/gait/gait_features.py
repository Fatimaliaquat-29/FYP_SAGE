"""
gait_features.py
=================
Feature extraction for gait analysis / fall-risk assessment (see
docs/IMPLEMENTATION_PLAN.md Section 3 -- "GAIT_hussain").

This module is conceptually distinct from the rest of src/posture/: it does
not classify a single frame or a short (30-frame, ~1s) window into
Fall/Lying/Sitting/Standing/Unknown. It measures slower, trend-based
movement-quality signals over a LONGER window (multiple seconds, ideally
multiple gait cycles) that the clinical fall-risk literature associates with
elevated risk of a FUTURE fall, independent of whether any fall occurs in
the window itself.

Literature basis for the four signals implemented here (see
docs/GAIT_LITERATURE_REVIEW.md for the full review with sources):
  - Gait speed: slower walking speed is a widely used, clinically convenient
    fall-risk indicator, though only moderately discriminative alone
    (typical clinical cut-points ~0.8-1.0 m/s; see literature review).
  - Stride-time variability: increased step-to-step timing variability is
    reported as MORE sensitive to fall risk than gait speed alone in several
    of the reviewed studies.
  - Postural sway: trunk/postural stability during quiet standing is
    highlighted as one of the most relevant kinematic fall-risk indicators
    in the reviewed wearable-sensor literature, and is reported to be
    related to stride-time variability (i.e. these two signals are not
    fully independent).
  - Sit-to-stand time/smoothness: the Timed-Up-and-Go test (stand from a
    chair, walk, turn, sit) is a widely used clinical fall-risk screening
    tool; the sit-to-stand phase specifically is also assessed on its own
    (e.g. the five-times-sit-to-stand test).

IMPORTANT — what this module does NOT have, and why every function below
returns a body-scale-normalized proxy rather than a clinically-calibrated
number:
  - No depth/metric calibration. Input is 2D MediaPipe landmarks normalized
    to the image frame, not real-world coordinates -- there is no subject
    height or camera-distance calibration anywhere in this pipeline (see
    src/posture/lstm/lstm_features.py's docstring for the same caveat
    applied to the fall-detection features). "Walking speed" here is
    torso-lengths-per-second, NOT meters-per-second, so the literature's
    absolute cut-points (e.g. "<1.0 m/s") CANNOT be applied directly and
    are not used as hard thresholds anywhere in this codebase.
  - No dataset to validate against. None of this project's existing
    training data (UR Fall, UP-Fall, LeFD -- all short clips centered on a
    single fall event) contains extended walking sequences or any fall-risk
    ground truth. See docs/GAIT_DATA_ASSESSMENT.md. Validation in this
    session is limited to (a) synthetic steady-vs-unsteady walking
    sequences sanity-checking that the risk score moves in the clinically
    expected direction, and (b) a crash/shape smoke test against real
    (unlabeled) ADL keypoint sequences already in data/processed_keypoints/.
    This is NOT the same as clinical validation.

All position/displacement-based features (speed, sway, stride detection)
use lstm_features.normalize_frame() (hip-centered, torso-length-scaled)
rather than raw screen-space coordinates -- using raw pixel positions here
would reproduce the exact "distance-from-camera confound" bug already found
and fixed once in this project's LSTM feature pipeline (see
lstm_features.py's own docstring). Angle-based features (hip/knee/torso
angle) are scale-invariant by construction, so they reuse pipeline_utils.py's
existing angle helpers directly on raw keypoint pairs.

Everything here is a READ-ONLY import from pipeline_utils.py and
lstm_features.py -- per docs/IMPLEMENTATION_PLAN.md Section 0, this module
does not edit either file.

======================================================================
THE HIERARCHY THIS MODULE ACTUALLY IMPLEMENTS (documented explicitly here,
not a new mechanism -- every stage below already existed before this
paragraph was written; this just names the levels the code already
enforces, since the project has repeatedly hit real bugs that were
exactly a MISSING or WEAK level in this hierarchy -- kneeling read as
walking, stationary jitter read as stride activity, bending read as
sitting -- see docs/GAIT_CODE_REVIEW.md for the specific fixes):
======================================================================
    1. Is the MEASUREMENT valid at all?
       -> _validate_window (gait_risk.py): type/shape checks, the
          MIN_WINDOW_FRAMES floor, timestamp monotonicity.
    2. Is the LANDMARK DATA trustworthy, frame by frame?
       -> _batch_landmark_valid / NaN-aware masking throughout this module.
    3. Is the subject actually MOVING / ambulating?
       -> _ambulation_check (path length, plausibility, directional
          coherence, horizontal dominance).
    4. What GAIT/POSTURAL characteristics does the movement show?
       -> compute_walking_speed / compute_stride_regularity (via the
          shared _detect_gait_events event detector) / compute_postural_sway
          / compute_sit_to_stand.
    5. HOW RELIABLE is the evidence behind each characteristic?
       -> each compute_*'s optional `_quality_out` reliability score (see
          gait_risk.py's module docstring, "SIGNAL QUALITY / RELIABILITY"
          section) -- the one level that was previously only implicit
          (binary available/unavailable, no gradient beneath it).
    6. What is the resulting RISK?
       -> gait_risk.py's per-signal risk-mapping + weighted blend.
Levels 1-4 and 6 are pre-existing; level 5 is this session's addition
(Concepts 1/7 of the accompanying investigation) -- see gait_risk.py for
where it's exposed. This is a DOCUMENTATION addition, not a new state
machine or control-flow change -- deliberately, since the existing
early-exit/gate structure already enforces this ordering correctly (each
gate already runs before the more expensive step it protects; see e.g.
compute_stride_regularity's own "cheapest-first" ordering comments).
"""

import sys
import warnings
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any

import numpy as np
import pandas as pd

# scipy is a hard requirement (see requirements.txt), but compute_stride_regularity
# degrades gracefully (returns None) instead of crashing the whole module if it's
# somehow missing in a given environment -- same contract as before, just checked
# once at import time instead of via a try/except on every call.
try:
    from scipy.signal import find_peaks
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import _extract_keypoint_pairs
from src.posture.lstm import lstm_features as lf

LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_HIP, RIGHT_HIP = 23, 24
LEFT_KNEE, RIGHT_KNEE = 25, 26
LEFT_ANKLE, RIGHT_ANKLE = 27, 28

# A gait window needs to be long enough to plausibly contain a walking bout
# with multiple steps, not a single fall-detection-style ~1s window. 90
# frames (~3s at 30fps) is an absolute floor to even attempt feature
# extraction; stride_regularity in particular usually needs more (multiple
# full gait cycles) and returns None below that regardless of this floor.
MIN_WINDOW_FRAMES = 90

# Minimum fraction of a window's rows that must have used _timestamps()'s
# 30fps frame-index fallback (missing/non-numeric 'timestamp') before that
# function warns about it -- see that function's own "OBSERVABILITY" note.
# 0.05 (5%) is chosen to distinguish "a non-trivial fraction of this
# window's timing is fabricated" from an isolated single bad row, which
# would be normal, low-impact noise not worth a warning.
_FALLBACK_WARN_FRACTION = 0.05

# Mirrors ONLY the two numeric hip-angle threshold VALUES (function-local,
# not module-exported) from pipeline_utils.py's _classify_heuristic --
# duplicated here, not imported, because pipeline_utils.py does not expose
# them as module-level constants and Section 0 of the implementation plan
# forbids editing that file to expose them (and, separately, per this
# project's Random-Forest firewall for this session, pipeline_utils.py is
# read-only regardless -- it's read by the RF/posture pipeline too).
#
# IMPORTANT -- what "mirrors" does NOT mean here (see
# docs/GAIT_CODE_REVIEW.md findings #3/#4): this is a mirror of the two
# DEGREE VALUES only, not of _classify_heuristic's full Standing/Sitting
# DECISION RULE. _classify_heuristic's primary path requires BOTH
# hip_angle AND knee_angle to individually cross these same thresholds
# (`knee_angle >= ANGLE_STANDING_MIN and hip_angle >= ANGLE_STANDING_MIN`
# for Standing; EITHER angle <= ANGLE_SITTING_MAX for Sitting) --
# compute_sit_to_stand's own STATE DEFINITION (`sitting_mask`/
# `standing_mask`, i.e. what counts as a confirmed sit/stand run at all)
# still uses HIP ANGLE ALONE, unchanged from when finding #4 was first
# written. This is a deliberate, NOT accidental, simplification for this
# module specifically: GAIT's sit-to-stand detection needs a state signal
# that stays usable when knees are occluded -- which happens often in
# exactly the seated/low-camera framings this module cares about (e.g.
# Sit_Stand_AnklesInvisible.MOV, SitFloor_lowKeypoints*.MOV in
# test_footage/) -- and the hip-angle-only definition is cheaper besides.
# The two modules' "Standing"/"Sitting" ARE NOT guaranteed to agree
# frame-for-frame: a frame with an upright torso but one bent knee
# (mid-stride, an asymmetric stance) can register as GAIT-"standing"
# (hip_angle alone crosses the floor) while _classify_heuristic would not
# call that same frame "Standing" (its knee gate fails). This divergence
# is accepted, not a bug.
#
# UPDATE (a later session, see docs/GAIT_DATA_ASSESSMENT.md Section 13):
# knee_angle IS now computed and used elsewhere in this function -- the
# standing-bend hip-rise EXEMPTION (`_KNEE_ANGLE_STANDING_MIN`,
# MAX_PLAUSIBLE_HIP_DROP_FOR_BEND_EXEMPTION) reuses this SAME
# ANGLE_STANDING_MIN value to decide whether a hip-rise-guard rejection
# should be overridden. This does NOT fold knee_angle into the core
# Standing/Sitting state definition described above (sitting_mask/
# standing_mask are still hip-angle-only, and the frame-for-frame
# divergence from _classify_heuristic described above is unchanged) -- it
# is a narrower, second, independent use of the same threshold value for a
# different guard, not the "fold knee_angle into compute_sit_to_stand"
# change this docstring previously described as a hypothetical, not-yet-
# needed future option. That broader change (making the state definition
# itself two-angle) remains not made, still without evidence it's needed.
#
# Keep the VALUES below in sync if pipeline_utils.py's own copies change --
# HipAngleConstantSyncTests in tests/test_gait_risk.py enforces this via a
# read-only source-inspection regression test (pipeline_utils.py's own
# copies are function-local, not importable, so the test parses
# _classify_heuristic's source rather than importing a module constant;
# still zero behavioral coupling and does not edit pipeline_utils.py).
_HIP_ANGLE_SITTING_MAX = 125.0
_HIP_ANGLE_STANDING_MIN = 143.0

# Minimum consecutive frames hip_angle must stay within a state (sitting or
# standing range) before compute_sit_to_stand trusts that state as real,
# rather than a single-frame landmark-noise/occlusion-recovery spike. Same
# idea as pipeline_utils.py's own consecutive-frame confirmation gates
# (ANGVEL_SUSTAIN_FRAMES=3, the two-consecutive-raw-Lying-frames rule in
# _classify_heuristic) -- one noisy frame doesn't get to define a state
# transition anywhere else in this codebase, and this function shouldn't be
# the exception. Found via real-footage validation on
# SitFloor_lowKeypoints_crossedLegs.MOV: a person sitting cross-legged on
# the floor the entire clip (never standing) produced ONE frame where a
# transient right-side landmark dropout pushed the averaged hip_angle to
# 148.9 degrees (>= _HIP_ANGLE_STANDING_MIN) for exactly 1 frame, surrounded
# on both sides by clearly-sitting angles. The un-gated version below
# treated that single frame as "the stand," anchored the transition to the
# EARLIEST sitting frame anywhere in the whole window (2.86s away), and
# counted 33 direction-reversals across that whole span of ordinary
# cross-legged fidgeting as if it were transition "shakiness" -- driving
# sit_to_stand's risk_contribution to ~1.0 for a person who never stood up.
_STATE_CONFIRM_FRAMES = 3

# Minimum hip_angle descent (degrees), measured against the immediately
# preceding confirmed-standing run's OWN mean angle, before
# _detect_fast_shallow_transition (compute_sit_to_stand's fallback path)
# accepts a dip between two confirmed-standing runs as a genuine (if fast
# and shallow) sit-to-stand rather than ordinary standing-still angle
# jitter. Roughly a third of the existing _HIP_ANGLE_STANDING_MIN -
# _HIP_ANGLE_SITTING_MAX gap (18 degrees) -- not an independently invented
# number -- chosen with margin below the real value this fallback exists to
# recover: SitFast_GetupFast.MOV (see compute_sit_to_stand's docstring), a
# genuine fast sit-to-stand whose hip_angle trough only reached ~135.6
# degrees, a ~9.7-degree drop below the preceding confirmed-standing run's
# own mean (~145.3) -- never crossing the full 125-degree sitting floor at
# all, which is exactly why the primary (sit-run-based) path misses it.
# Re-validated against the rest of this project's real test_footage clips
# (see benchmarks/gait_footage_validation_report.md) to confirm this
# threshold does not fire on ordinary standing-still jitter elsewhere.
FAST_SIT_MIN_DESCENT_DEGREES = 7.0

# How many consecutive frames with NO valid hip_angle at all (both left and
# right sides unavailable) immediately before a run disqualifies that run
# from "confirming" a sitting/standing state. Mirrors pipeline_utils.py's
# own NAN_AFTER_FALL_THRESHOLD (10 consecutive all-NaN frames) -- the
# existing, already-calibrated project threshold for "a tracking gap long
# enough to be a real discontinuity, not noise, and therefore not something
# to extrapolate confidently through" (see that constant's own comment;
# same mirroring rationale as _HIP_ANGLE_SITTING_MAX/_HIP_ANGLE_STANDING_MIN
# above -- pipeline_utils.py does not expose it for import and Section 0 of
# the implementation plan forbids editing that file to add one).
# Found via real-footage validation on Sitting_Lying_FewLandmarks_back.MOV:
# 12 consecutive frames of total landmark loss were immediately followed by
# exactly 3 frames reading in the STANDING range -- a MediaPipe
# re-acquisition artifact (VIDEO-mode's temporal smoothing "catching up"
# right after a blackout), not a real stand, that plain consecutive-frame
# confirmation alone (_STATE_CONFIRM_FRAMES) cannot distinguish from a
# genuine sustained state. Applied to both sitting_mask and standing_mask so
# the same protection covers compute_sit_to_stand's primary path and
# _detect_fast_shallow_transition's fallback identically.
_MAX_TRUSTED_GAP_BEFORE_STATE = 10

# Maximum plausible hip TRANSLATIONAL speed (torso-lengths/sec) during a
# genuine voluntary sit-to-stand's trough-to-standing segment, before
# _detect_fast_shallow_transition treats the dip as fall-adjacent/ballistic
# motion rather than a real stand. Standing up is primarily a POSTURAL
# (hip-angle) change -- the hip translates only modestly, a body rising
# roughly in place -- unlike a fall, where the hip translates rapidly and
# substantially as the body moves/collapses through space. This is a
# DIFFERENT axis of information than FAST_SIT_MIN_DESCENT_DEGREES (angle
# shape) or MAX_PLAUSIBLE_HIP_SPEED (physically-IMPOSSIBLE tracking
# glitches, 50.0) -- this constant screens out physically-PLAUSIBLE-but-
# fall-like whole-body translation that hip-angle geometry alone cannot see
# (see this project's own audit finding: the fallback's known limitation is
# specifically that hip-angle-only geometry can't always distinguish a
# voluntary stand from fall-adjacent motion).
#
# Derived from direct measurement on real footage in this session (not
# assumed), using the FIXED-reference-scale method _peak_translation_speed
# implements (raw hip displacement divided by the preceding confirmed
# stand's own mean torso length -- NOT the per-frame-varying
# _torso_scaled_hip_track; an earlier attempt using that per-frame-scaled
# version measured a spurious ~19 torso-lengths/sec "translation" for a
# synthetic transition whose raw hip position never moved at all, purely
# from torso_len shrinking as posture changed -- see
# _peak_translation_speed's own docstring):
#   - SitFast_GetupFast.MOV (the one confirmed genuine fast stand this
#     fallback exists to recover): peak = 0.35 torso-lengths/sec.
#   - Sitting_Lying_FewLandmarks.MOV's previously-flagged AMBIGUOUS (but
#     non-fall, angle-noise-driven) case: peak = 0.46 torso-lengths/sec --
#     close to the genuine reference, confirming this check targets
#     fall-adjacent translation specifically and leaves that separate,
#     harder angle-only ambiguity untouched (see compute_sit_to_stand's
#     module docs for why that residual ambiguity remains a disclosed,
#     bounded limitation rather than something this specific check fixes).
#   - Backward_fall.mp4 (a real clip where the fallback previously fired on
#     fall-adjacent motion): peak = 2.88 torso-lengths/sec (~6x higher than
#     the genuine reference).
#   - Slow_fall.mp4 (same): peak = 17.79 torso-lengths/sec (~39x higher).
# 1.0 sits with margin above both non-fall references (~2x the genuine
# case, ~2x the ambiguous-but-legitimate case -- this project has no
# extended, gait-risk-labeled dataset, see docs/GAIT_DATA_ASSESSMENT.md, so
# a wider margin is used here than MAX_PLAUSIBLE_HIP_SPEED's tighter,
# many-real-fall-derived one) while staying comfortably below both
# fall-adjacent references.
FALLBACK_MAX_TRANSLATION_SPEED = 1.0

# Minimum vertical hip RISE (torso-lengths, raw image-y decreasing = hip
# moving up), measured with a FIXED reference torso length from the
# preceding confirmed SIT run (same fixed-reference-scale methodology as
# _peak_translation_speed -- see that function's own docstring for why a
# fixed, not per-frame-varying, scale matters here), before
# compute_sit_to_stand's PRIMARY (sit-run-based) path trusts a confirmed-
# sit -> confirmed-stand pairing as a GENUINE stand rather than ordinary
# seated repositioning (reclining back in a chair, crossing/uncrossing
# legs) that swings the 2D hip-shoulder-knee angle across BOTH the sitting
# and standing thresholds without the person ever leaving the chair.
#
# WHY THIS IS A DIFFERENT FAILURE MODE FROM EVERY PRIOR SIT-TO-STAND GUARD
# (see FAST_SIT_MIN_DESCENT_DEGREES, the minimum-gap guard above, and
# _detect_fast_shallow_transition's guards #3/#4): all of those target
# FAST or DEEP or FAST-TRANSLATING crossings. This one is none of those --
# the false positives it targets have PLAUSIBLE-LOOKING durations (0.24s,
# 0.90s), BOTH SIDES fully landmark-confident throughout (not a tracking-
# quality issue -- `reliability` reads 1.0 for these), and only MODEST hip
# translation (a person reclining in a chair doesn't launch across the
# room). What none of them have -- and what a genuine stand always does,
# by simple physics -- is the hip actually RISING: a chair seat stays at a
# fixed height whether someone reclines, leans forward, or crosses their
# legs in it, so no amount of seated repositioning raises the hip off the
# seat, while actually standing up necessarily does.
#
# Confirmed on real footage, not assumed (see docs/GAIT_CODE_REVIEW.md's
# camera-angle/sit-to-stand follow-up investigation): Sit_Stand_2.mov
# contains an ~8.5s seated hold during which the subject reclines/
# repositions -- this produced MULTIPLE spurious primary-path "sit-to-
# stand" detections (duration=0.241s/reversal=6, duration=0.895s/
# reversal=18) purely from natural seated movement. Measured hip rise
# (sit run -> each spurious "stand" run, fixed-reference scale) was
# ~0.00 torso-lengths (i.e. no measurable rise at all) in every spurious
# case, while the SAME clip's own genuine final stand-up measured +0.128
# torso-lengths of rise, and two OTHER real genuine stands (Sit_Stand_1.
# mov: +0.283; Deep_Bend.mov's kneel-to-stand: +0.403) confirm this isn't
# a one-clip coincidence -- three independent real genuine stands ranged
# 0.128-0.403 torso-lengths of rise, while every spurious (non-standing)
# case measured ~0.00. 0.08 sits with real margin below the smallest
# genuine case (>1.6x) and real margin above the spurious cases (which
# were indistinguishable from zero, not just small).
MIN_STAND_HIP_RISE = 0.08


# ======================================================================
# STANDING-BEND HIP-RISE EXEMPTION -- closes (with real evidence, not
# assumed) the "does compute_sit_to_stand ever detect a genuine standing-
# bend recovery" question docs/GAIT_CODE_REVIEW.md finding #3 left open
# ("the originally-hypothesized mechanism... remains open and untested in
# isolation"), using footage recorded specifically to test it
# (Deep_Bend_1.mov/Deep_Bend_2.mov/Deep_Bend_3.mov, ~100% landmark
# confidence, unlike the original occlusion-confounded Deep_Bend.mov).
#
# WHAT WAS FOUND, TESTED DIRECTLY AGAINST THAT FOOTAGE, NOT ASSUMED: no
# false positives fire during the sustained bend itself (hip_angle
# genuinely tracks bent-vs-upright correctly) -- but ALSO no true
# positives fire during the REAL "Getting up" recovery in any of the three
# clips. Root-caused: MIN_STAND_HIP_RISE, calibrated from chair-stand/
# kneel-stand references (+0.128 to +0.403 torso-lengths of real hip-
# height rise), rejects every one -- measured directly, hip_rise is
# NEGATIVE in all 7 real recovery windows found across the three clips
# (-0.454 to -0.006). This makes physical sense: recovering from a
# STANDING bend straightens the TORSO while the FEET/LEGS never leave
# standing height, unlike a chair-stand's hip traveling a real vertical
# distance -- so MIN_STAND_HIP_RISE's own guard, built to reject seated
# repositioning, rejects this different, genuine transition as a side
# effect. A blind spot (missed detection), not a false-alarm risk.
#
# THE DISCRIMINATING SIGNAL: KNEE ANGLE (hip-knee-ankle), NOT currently
# used anywhere in this function -- the same second angle
# pipeline_utils.py::_classify_heuristic already combines with hip angle
# (see docs/GAIT_CODE_REVIEW.md finding #4). A standing bend keeps the
# knee relatively STRAIGHT throughout (legs don't bend, only the torso
# rotates); genuine seated repositioning keeps the knee BENT throughout
# (the whole point of "seated"). Measured directly, full 44-clip corpus,
# every window where MIN_STAND_HIP_RISE currently rejects a pairing (not
# just the two target clips):
#   - Deep_Bend_1.mov/Deep_Bend_2.mov/Deep_Bend_3.mov (7 windows, the
#     genuine standing-bend recoveries this exemption targets): knee angle
#     156.4-178.1 degrees at BOTH the sit-run and stand-run reference.
#   - Shallow_Bending.mov's own real "Getting up" recovery (a DIFFERENT
#     clip than the three this was designed against -- a real, independent
#     confirmation, not cherry-picked): 162.3-162.8 degrees.
#   - Sit_Stand_2.mov's two real, already-documented seated-repositioning
#     false positives (the ones MIN_STAND_HIP_RISE exists to reject):
#     knee angle 117.1-122.7 degrees -- a completely disjoint range, ~34
#     degrees of margin from the standing-bend cases.
#   - Every OTHER real hip_rise-rejected pairing found anywhere in the
#     corpus (Deep_Bend.mov's occlusion-confounded case; Lateral_Walk.mov/
#     Sit_Stand_SideAngle_2.mov/Sit_Stand_SideAngle_3.mov/Sitting_Lying_
#     FewLandmarks_back.mov's incidental hip-angle-noise crossings during
#     walking/sitting/lying) has knee angle well below the standing
#     threshold (24.5-134 degrees, one NaN) -- correctly stays rejected.
# _KNEE_ANGLE_STANDING_MIN reuses pipeline_utils.py's own ANGLE_STANDING_MIN
# value (143.0, already the project's established "knee straight enough to
# call this standing" cut-point, used for the SAME two-angle Standing
# definition finding #4 already documents diverging from this module's
# hip-angle-only one) -- not a newly invented number. It sits with large
# margin on both sides of the real gap above (~13-20 degrees below the
# standing-bend floor, ~20 degrees above the seated-repositioning ceiling).
#
# ONE REAL FALSE-EXEMPTION RISK FOUND AND GUARDED (full-corpus validation
# catching it before shipping, same standard as every fix in this
# project): Stride_Big_Starting_Leap.mov has a hip_rise-rejected pairing
# with a straight knee (151.7/165.8 degrees) that would otherwise be
# exempted -- but it is not a real posture event at all. Traced directly:
# this pairing's reference frames sit inside a severe MediaPipe
# acquisition-jitter window (the same artifact class characterized in
# docs/GAIT_DATA_ASSESSMENT.md Section 10/11 -- torso_len collapses to
# 0.016-0.025, versus a stable ~0.15-0.30 later in the same clip), and its
# hip_rise is -6.051 -- over 13x more extreme than the worst REAL standing-
# bend case (-0.454). MAX_PLAUSIBLE_HIP_DROP_FOR_BEND_EXEMPTION bounds the
# exemption to hip_rise values no more extreme than that, with real (~2.2x)
# margin below the worst genuine case and comfortably above the one real
# glitch found. `hip_rise` this negative or more is symptomatic of
# corrupted/glitched underlying tracking, not a slow, gentle standing-bend
# recovery, regardless of what the knee angle says.
_KNEE_ANGLE_STANDING_MIN = 143.0
MAX_PLAUSIBLE_HIP_DROP_FOR_BEND_EXEMPTION = -1.0


def _confirmed_runs(mask: np.ndarray, min_len: int) -> List[tuple]:
    """Indices of maximal runs of consecutive True values in `mask` that are
    at least `min_len` long, as a list of (start, end_inclusive) pairs in
    the order they occur. Runs shorter than `min_len` (isolated noisy
    frames) are dropped entirely -- they don't get to "confirm" a state."""
    runs = []
    start = None
    n = len(mask)
    for i in range(n + 1):
        val = mask[i] if i < n else False
        if val and start is None:
            start = i
        elif not val and start is not None:
            if i - start >= min_len:
                runs.append((start, i - 1))
            start = None
    return runs


def _drop_runs_after_long_gap(runs: List[tuple], invalid: np.ndarray, max_gap: int) -> List[tuple]:
    """Removes any (start, end) run whose start is immediately preceded by
    >= max_gap consecutive frames with no valid hip_angle at all -- see
    _MAX_TRUSTED_GAP_BEFORE_STATE's docstring for why a state that emerges
    right out of a tracking blackout isn't trusted as a "confirmed" state.

    KNOWN LEFT-EDGE BLIND SPOT (see docs/GAIT_CODE_REVIEW.md finding #12,
    inherent to this function, not fixable without look-behind data it
    doesn't have): a run whose `start` is 0 (the very first frame of the
    window) is NEVER treated as "emerging from a blackout" -- the backward
    scan (`i = start - 1; while i >= 0 ...`) terminates immediately at
    `i = -1` regardless of what was actually happening just before this
    window began, since no frame data exists before index 0 of whatever
    list was passed in. This means _MAX_TRUSTED_GAP_BEFORE_STATE's
    protection has a blind spot specifically at the first few frames of any
    window: a state run that starts at/near index 0 is always kept here no
    matter how it would have looked with one more frame of prior context.
    Not attempted to be fixed here -- there is no historical data to invent
    it from, and gait_stream.py's sliding window means any given real state
    change will appear away from index 0 in most (though not all)
    re-assessments as the window slides forward. See
    test_run_starting_at_window_edge_is_not_penalized_for_missing_lookbehind
    in tests/test_gait_risk.py for a regression test locking in this
    documented (not accidental) behavior."""
    kept = []
    for start, end in runs:
        gap = 0
        i = start - 1
        while i >= 0 and invalid[i]:
            gap += 1
            i -= 1
        if gap < max_gap:
            kept.append((start, end))
    return kept


def _timestamps(window: List[dict]) -> np.ndarray:
    """Row timestamps as float seconds, falling back to a 30fps frame-index
    assumption when timestamps are missing/non-numeric (same fallback
    pipeline_utils._compute_velocity uses).

    Perf note: profiling showed this was being called 3x per assess_risk()
    (independently by compute_walking_speed, compute_stride_regularity,
    compute_sit_to_stand for the same window) -- ~24% of a full call after
    the other vectorization work here, for the exact same result computed
    three times. GaitRiskAssessor.assess_risk() now computes this ONCE and
    passes it to all three via `_ts`, the same sharing pattern already used
    for `_raw`/`_hip_track`. Leave `_ts` as None to compute standalone.

    The fast path below handles the common case (every row already has a
    plain numeric timestamp -- true for every real MediaPipe-derived row)
    in one vectorized array conversion instead of T individual
    try/except-guarded float() calls. It falls back to the exact original
    per-row loop -- not an approximation -- whenever that conversion raises
    OR produces any NaN, since NaN can come from two different sources that
    must NOT be treated the same: a genuinely NaN timestamp value (which
    the original loop keeps as NaN, since float(nan) doesn't raise) vs. a
    missing/None timestamp (which the original loop replaces with i/30.0).
    Falling back on any NaN -- rather than trying to disambiguate the two
    in the vectorized path -- keeps this byte-identical to the original in
    every case, at the cost of only using the fast path when it's
    unambiguously safe to.

    OBSERVABILITY (see docs/GAIT_CODE_REVIEW.md finding #10): the fallback
    itself is KEPT exactly as-is -- it's consistent with the rest of this
    pipeline (pipeline_utils._compute_velocity uses the same 30fps
    assumption) and every GAIT signal is time-dependent, so silently
    producing SOME duration/speed number beats refusing to compute one.
    What was silent before is now observable: if the missing/non-numeric-
    timestamp fallback fires for at least _FALLBACK_WARN_FRACTION of this
    window's rows, a single `RuntimeWarning` is emitted for the whole call
    (not one per affected row -- that would be noisy for a window with many
    affected rows and drown out anything else being logged). A single row
    with an occasional malformed timestamp -- not a "meaningful situation"
    -- stays silent, matching normal operation for real MediaPipe-derived
    rows (which never hits this at all, since it exits via the fast path
    above with no fallback and no warning).
    """
    raw_vals = [row.get("timestamp") for row in window]
    try:
        fast = np.asarray(raw_vals, dtype=np.float64)
        if not np.isnan(fast).any():
            return fast
    except (TypeError, ValueError):
        pass

    ts = []
    fallback_count = 0
    for i, v in enumerate(raw_vals):
        try:
            ts.append(float(v))
        except (TypeError, ValueError):
            ts.append(i / 30.0)
            fallback_count += 1
    if raw_vals and fallback_count / len(raw_vals) >= _FALLBACK_WARN_FRACTION:
        warnings.warn(
            f"_timestamps(): {fallback_count}/{len(raw_vals)} row(s) in this window had a "
            "missing/non-numeric 'timestamp' and used the 30fps frame-index fallback (i/30.0) -- "
            "every GAIT signal is time-dependent, so results from this window may be calibrated "
            "for the wrong frame rate if the real capture rate differs from 30fps.",
            RuntimeWarning,
        )
    return np.array(ts, dtype=np.float64)


def _row_keypoints_fast(keypoints) -> Optional[np.ndarray]:
    """Vectorized fast path for the common case: `keypoints` is already a
    flat list/tuple/ndarray of numbers (the documented input contract --
    see this module's docstring). Returns None (never raises) if the value
    isn't numeric end-to-end, so the caller can fall back to
    `pipeline_utils._extract_keypoint_pairs`'s slower per-item parsing
    (which also handles the legacy string-serialized "x1,y1,..." case) --
    this keeps behavior byte-for-byte identical to that fallback for every
    input shape, only skipping the expensive per-item Python float()/tuple
    construction it does when it isn't needed.

    Mirrors `_extract_keypoint_pairs` + the re-flatten it used to require:
    an odd-length input drops its last element (can't pair it), then only
    the first 66 values are kept (matching `_extract_keypoint_pairs`
    returning pairs of arbitrary length, re-flattened, then truncated to 66
    by the caller).
    """
    if isinstance(keypoints, str) or not isinstance(keypoints, (list, tuple, np.ndarray)):
        return None
    n = len(keypoints)
    if n == 0:
        return np.array([], dtype=np.float64)
    if n % 2 != 0:
        n -= 1
    try:
        arr = np.asarray(keypoints[:n], dtype=np.float64)
    except (TypeError, ValueError):
        return None
    if arr.ndim != 1:
        return None
    return arr[:66]


def _raw_keypoint_array(window: List[dict]) -> np.ndarray:
    """(T, 66) raw x/y keypoints from a list of pose row dicts.

    Non-finite values (Inf/-Inf, which can reach here from a corrupted
    upstream source -- MediaPipe itself never emits these, but this module
    doesn't assume that) are treated the same as NaN: "landmark not
    trustworthy", not a real coordinate. Every downstream computation in
    this module is already NaN-aware (masking via lstm_features.normalize_frame
    and the is_landmark_valid-style checks), so sanitizing here is enough to
    make the whole module Inf-safe without special-casing it everywhere else.

    Perf note: this used to call pipeline_utils._extract_keypoint_pairs
    (per-item Python float() + tuple construction) for every one of the T
    rows -- profiling a full assess_risk() call showed this was ~8% of
    total latency for no reason, since the overwhelmingly common case (a
    real MediaPipe-derived row, per this module's input contract) is
    already a flat list of Python floats/NaNs that numpy can ingest
    directly. `_row_keypoints_fast` takes that path; only rows that aren't
    plain numeric lists (e.g. the legacy string-serialized form some CSV
    sources produce) fall back to the original per-item parser, so output
    is identical to before for every input this module's tests cover.
    """
    out = np.full((len(window), 66), np.nan, dtype=np.float32)
    for i, row in enumerate(window):
        fast = _row_keypoints_fast(row.get("keypoints"))
        if fast is not None:
            out[i, :len(fast)] = fast
            continue
        pairs = _extract_keypoint_pairs(row)
        flat = [c for pair in pairs for c in pair]
        n = min(len(flat), 66)
        out[i, :n] = flat[:n]
    out[~np.isfinite(out)] = np.nan
    return out


# Minimum fraction of a window's frames that must have valid 3D world-landmark
# data before _torso_scaled_hip_track/compute_torso_baseline trust it for
# that WHOLE window/call, rather than falling back to the existing all-2D
# path -- see WORLD_LANDMARKS_ROOT_CAUSE_FIX's docstring for the full
# rationale. Deliberately a WHOLE-WINDOW (not per-frame) decision: mixing
# 2D-fraction-scaled and 3D-meter-scaled position values frame-to-frame
# within the same track would create an artificial unit-discontinuity
# velocity spike exactly at the switch point -- the same class of artifact
# this whole fix exists to remove, not something to reintroduce. 0.5 matches
# this file's existing convention for "enough of the window to trust"
# (e.g. compute_stride_regularity's raw_ankle_valid gate).
MIN_WORLD_LANDMARK_COVERAGE = 0.5


def _raw_world_keypoint_array(window: List[dict]) -> np.ndarray:
    """(T, 99) raw x/y/z MediaPipe pose_world_landmarks per frame (33
    landmarks x 3 coordinates, real-world METERS, roughly hip-relative --
    see WORLD_LANDMARKS_ROOT_CAUSE_FIX's docstring), NaN where a row has no
    `"world_keypoints"` key or a malformed one.

    This is an ENTIRELY OPTIONAL, ADDITIVE key on top of this module's
    existing `"keypoints"` (2D) input contract -- see this module's own
    docstring. A row missing `"world_keypoints"` (every existing caller,
    including every current GaitRiskAssessor/gait_stream.py call site) is
    NOT an error here; it just contributes an all-NaN row, which every
    consumer of this array already treats as "no 3D data for this frame"
    and falls back to 2D for accordingly.

    Mirrors `_raw_keypoint_array`'s fast-path shape (a flat numeric
    list/tuple/ndarray, no legacy string-serialized format to support here
    since this is a new field with no prior producer to stay compatible
    with)."""
    out = np.full((len(window), 99), np.nan, dtype=np.float32)
    for i, row in enumerate(window):
        wk = row.get("world_keypoints")
        if wk is None or isinstance(wk, str) or not isinstance(wk, (list, tuple, np.ndarray)):
            continue
        try:
            arr = np.asarray(wk[:99], dtype=np.float64)
        except (TypeError, ValueError):
            continue
        if arr.ndim != 1:
            continue
        out[i, :len(arr)] = arr
    out[~np.isfinite(out)] = np.nan
    return out


def _normalized_positions(window: List[dict], _raw: Optional[np.ndarray] = None) -> np.ndarray:
    """(T, 33, 2) hip-CENTERED, torso-length-scaled positions (each frame
    independently re-centered on its own hip midpoint, via
    lstm_features.normalize_frame). Correct for signals about body SHAPE/
    limb configuration RELATIVE to the torso (e.g. ankle swing relative to
    the hip for stride detection) -- but hip position itself is identically
    (0, 0) in every single frame by construction, so this representation
    cannot see overall translation. Use _torso_scaled_hip_track for any
    signal that needs to measure how far the hip itself actually moved
    (walking speed, postural sway).

    `_raw`: internal -- an already-computed _raw_keypoint_array(window), so
    callers that need it can share one parse instead of each independently
    re-parsing the window (profiling showed this parse -- window rows ->
    keypoint pairs, via pipeline_utils._extract_keypoint_pairs -- was the
    single largest cost in a full assess_risk() call, done 3 separate times
    for the same window before this).

    Perf note: this used to call lstm_features.normalize_frame() once per
    frame in a Python loop (45,000 calls for a 300-call/150-frame profiling
    run -- profiling showed this was ~29% of a full assess_risk() call).
    normalize_frame's own math (hip-center, torso-length scale, subtract,
    divide) has no cross-frame dependency, so it's fully batchable over the
    window's T dimension -- the per-frame version just paid T-1 extra
    Python function-call overheads for identical arithmetic. This computes
    byte-for-byte the same thing (same hip/shoulder indices, same
    NaN-whole-frame and degenerate-scale rules as normalize_frame) in one
    vectorized pass instead."""
    raw = _raw if _raw is not None else _raw_keypoint_array(window)
    pts = raw.astype(np.float32, copy=False).reshape(-1, 33, 2)

    hip_l, hip_r = pts[:, LEFT_HIP, :], pts[:, RIGHT_HIP, :]
    sh_l, sh_r = pts[:, LEFT_SHOULDER, :], pts[:, RIGHT_SHOULDER, :]

    hip_center = (hip_l + hip_r) / 2.0
    sh_center = (sh_l + sh_r) / 2.0
    scale = np.linalg.norm(sh_center - hip_center, axis=1)

    invalid = (
        np.isnan(hip_l).any(axis=1) | np.isnan(hip_r).any(axis=1)
        | np.isnan(sh_l).any(axis=1) | np.isnan(sh_r).any(axis=1)
        | (scale < 1e-3)
    )
    safe_scale = np.where(scale < 1e-3, 1.0, scale)  # placeholder to avoid /0; row is masked to NaN below anyway
    normalized = (pts - hip_center[:, None, :]) / safe_scale[:, None, None]
    normalized[invalid] = np.nan
    return normalized.astype(np.float32, copy=False)


def _raw_torso_len(window: List[dict], _raw: Optional[np.ndarray] = None) -> np.ndarray:
    """(T,) raw (unsmoothed) 2D shoulder-mid-to-hip-mid distance per frame
    (image-normalized units), NaN where degenerate (< 1e-3) or missing --
    the per-frame denominator _torso_scaled_hip_track divides by WHEN NO
    trustworthy 3D world-landmark data is available (see
    WORLD_LANDMARKS_ROOT_CAUSE_FIX's docstring) -- factored out so
    compute_torso_baseline and compute_walking_speed's optional
    calibrated-baseline gate (see MIN_TORSO_BASELINE_RATIO) can reuse it
    without duplicating the shoulder/hip-midpoint math or silently drifting
    out of sync with it."""
    raw = _raw if _raw is not None else _raw_keypoint_array(window)
    pairs_per_frame = raw.reshape(-1, 33, 2)
    sh_mid = (pairs_per_frame[:, LEFT_SHOULDER, :] + pairs_per_frame[:, RIGHT_SHOULDER, :]) / 2.0
    hip_mid = (pairs_per_frame[:, LEFT_HIP, :] + pairs_per_frame[:, RIGHT_HIP, :]) / 2.0
    torso_len = np.linalg.norm(sh_mid - hip_mid, axis=1)
    return np.where(torso_len < 1e-3, np.nan, torso_len)


def _raw_torso_len_3d(world_raw: np.ndarray) -> np.ndarray:
    """(T,) 3D shoulder-mid-to-hip-mid Euclidean distance, in real-world
    METERS, from an already-parsed _raw_world_keypoint_array() result. NaN
    where degenerate (< 1e-3) or missing -- same convention as
    _raw_torso_len, just computed from MediaPipe's pose_world_landmarks
    (x/y/z in meters) instead of pose_landmarks (x/y normalized to the
    image frame). See WORLD_LANDMARKS_ROOT_CAUSE_FIX's docstring for why
    this is a materially more distance/bend-robust scale reference than
    _raw_torso_len, and for its own real, measured limits."""
    pairs_per_frame = world_raw.reshape(-1, 33, 3)
    sh_mid = (pairs_per_frame[:, LEFT_SHOULDER, :] + pairs_per_frame[:, RIGHT_SHOULDER, :]) / 2.0
    hip_mid = (pairs_per_frame[:, LEFT_HIP, :] + pairs_per_frame[:, RIGHT_HIP, :]) / 2.0
    torso_len = np.linalg.norm(sh_mid - hip_mid, axis=1)
    return np.where(torso_len < 1e-3, np.nan, torso_len)


def _has_sufficient_world_coverage(world_raw: Optional[np.ndarray]) -> bool:
    """True if `world_raw` (see _raw_world_keypoint_array) has a valid 3D
    torso length for at least MIN_WORLD_LANDMARK_COVERAGE of its frames --
    the single, shared "is 3D data trustworthy enough for this whole call"
    decision reused identically by _torso_scaled_hip_track,
    compute_torso_baseline, and compute_walking_speed's/compute_postural_
    sway's availability gate, so all of them make the SAME 2D-vs-3D choice
    for a given window rather than risking a per-frame or per-function
    mismatch (see MIN_WORLD_LANDMARK_COVERAGE's own docstring)."""
    if world_raw is None or len(world_raw) == 0:
        return False
    torso_3d = _raw_torso_len_3d(world_raw)
    return float(np.isfinite(torso_3d).sum()) / len(torso_3d) >= MIN_WORLD_LANDMARK_COVERAGE


# ======================================================================
# WORLD_LANDMARKS_ROOT_CAUSE_FIX -- root-cause fix for the torso-length
# scale-degeneracy bug documented in docs/GAIT_DATA_ASSESSMENT.md Sections
# 9-11 (a later session's follow-up), referenced by _raw_torso_len_3d,
# _torso_scaled_hip_track, compute_torso_baseline, MIN_WORLD_LANDMARK_
# COVERAGE, and MIN_TORSO_BASELINE_RATIO_3D.
#
# ROOT CAUSE, restated precisely: every prior fix attempt (Section 9's
# three rejected candidates, Section 10's shipped-but-partial fixed-
# baseline gate, Section 11's rejected knee-angle/shoulder-width
# candidates) worked ENTIRELY from MediaPipe's 2D pose_landmarks (image-
# normalized x/y). A single 2D camera image cannot distinguish "the torso
# rotated toward horizontal" (a bend) from "the camera got farther away"
# (genuine locomotion) using projected torso length alone, because BOTH
# physically different events shrink that one 2D measurement the same way
# -- this is a genuine information-theoretic limit of 2D projection, not a
# threshold-tuning problem (see Section 11's own honest conclusion).
#
# MediaPipe's PoseLandmarker ALREADY computes a second output,
# pose_world_landmarks (real-world-metric x/y/z, roughly hip-relative),
# alongside pose_landmarks on every call -- confirmed directly, not
# assumed: `mp.tasks.vision.PoseLandmarkerResult` has both fields, and this
# project's own extraction code (evaluate_real_footage.py::extract_
# keypoints) was already running the full model that produces
# pose_world_landmarks, it just never read that field. No new model, no
# new inference cost -- purely reading data already being computed.
#
# WHAT WAS ACTUALLY MEASURED before writing any of this (all 4 conclusions
# below are from real footage in this project's own corpus, not assumed):
#
#   1. 3D torso length is NOT a perfectly rigid/invariant anatomical
#      measurement the way "world coordinates" might suggest -- MediaPipe's
#      3D estimate is itself inferred from the same single 2D image (no
#      depth sensor), so it inherits SOME of the same foreshortening
#      confusion, just far less severely. Measured on Deep_Bend_2.mov/
#      Deep_Bend_3.mov: 3D torso length during the sustained bend drops to
#      49-67% of its own standing value (vs. 2D's 32-44% -- a much deeper
#      collapse). Real, disclosed, NOT eliminated -- see point 3.
#
#   2. For genuine camera-DISTANCE change (the walking_speed problem, see
#      Section 11.1), 3D torso length is dramatically more stable than 2D:
#      measured on Stride.mov (walking toward/away), 2D torso length's
#      coefficient of variation is 0.359/0.249 across the two halves of the
#      clip; 3D torso length's CV is 0.065/0.023 over the SAME frames --
#      roughly 5-10x less variance. It is ALSO far more robust to a
#      different, previously undiagnosed noise source: Stride.mov's own
#      ~0.3s MediaPipe acquisition-jitter window (subject still entering
#      frame) collapses 2D torso length to 0.017-0.062 (spurious, see
#      MIN_TORSO_BASELINE_RATIO's own docstring) while 3D torso length
#      stays a stable 0.28-0.47m across the SAME frames -- confirmed frame-
#      by-frame, not inferred.
#
#   3. For genuine SITTING vs. a genuine BEND (the postural_sway problem,
#      Section 11.2, where Section 11's knee-angle candidate produced real
#      conflicts on this project's own corpus), 3D torso length shows real
#      separation where 2D and knee-angle did not. Measured directly
#      (window-level, 90-frame sliding windows, same methodology as
#      Section 10/11): Deep_Bend_2.mov/Deep_Bend_3.mov's sustained-bend
#      windows have a 3D-torso/baseline ratio of 0.42-0.69 (median across
#      all windows); Sit_Stand_1.mov/Sit_Stand_2.mov's confirmed-sitting
#      windows measure 0.85-0.89; SitFloor_lowKeypoints.MOV's genuine
#      floor-sitting (a harder case -- legs extended, not tucked under a
#      chair, which broke the knee-angle candidate in Section 11) measures
#      0.72-0.95. The tightest real gap found is Deep_Bend_3.mov's ceiling
#      (0.693) vs. SitFloor_lowKeypoints.MOV's floor (0.718) -- thin
#      (~3.6%) but REAL, and unlike knee-angle, no actual overlapping
#      window was found in this project's corpus at the time this was
#      measured (see MIN_TORSO_BASELINE_RATIO_3D's own docstring for the
#      full validation this was re-checked against before shipping).
#
#   4. Reliability concern (checked, not assumed, per this project's own
#      "flag if 3D is shakier than 2D" standard): 3D landmark VALIDITY
#      (non-NaN) tracks 2D validity almost exactly in every real clip
#      checked -- both come from the same underlying MediaPipe detection
#      pass, so if a frame's pose is detected at all, both fields are
#      populated together. 3D landmark NOISE (once present) is, if
#      anything, LOWER than 2D's for the specific quantity this fix
#      uses (torso length) -- see point 2's CV comparison. No clip checked
#      showed 3D data that was noisier or less available than 2D.
#
# DESIGN: hip TRANSLATION still uses 2D hip position (pose_world_landmarks'
# hip is ALWAYS ~(0,0,0) by construction -- MediaPipe's world coordinate
# frame is subject-relative/hip-centered, the exact same "hip-centering
# destroys translation" issue this file's own _normalized_positions
# docstring already documents for lstm_features.normalize_frame, just
# extended to 3D. There is no usable ABSOLUTE 3D translation signal here --
# confirmed directly: pose_world_landmarks' hip sits at ~(0.000, -0.001,
# 0.001) for essentially every frame of both a stationary clip
# (Deep_Bend_2.mov) and an actively-walking one (Stride.mov)).
#
# TRIED AND REVERTED: substituting 3D torso length as _torso_scaled_hip_
# track's OWN scale factor (i.e. hip2d / torso_len_3d, still using 2D hip
# position for translation) -- this was the first design attempted, and it
# DOES reduce Deep_Bend_2/3's spurious values, but full-44-clip validation
# (not just the two target clips) caught a real regression before this
# shipped: Stride.mov lost walking_speed availability on 18/18 previously-
# available windows. Root-caused, not just observed: 2D torso length
# GROWS as a subject walks toward a camera (real 2D perspective growth),
# and dividing 2D hip position by that SAME growing 2D quantity cancels
# most of that perspective effect from the resulting scaled track --
# exactly the "camera-distance invariance" this function's own docstring
# already describes. 3D torso length does NOT grow with distance (that is
# precisely its value for the AVAILABILITY GATE below) -- so dividing 2D
# hip position by a roughly-CONSTANT 3D quantity leaves that same
# perspective growth UNCANCELED in the numerator. Measured directly on the
# implicated Stride.mov window (t=6.21s): with a 3D-scaled denominator, the
# resulting track's net displacement has dx=0.233, dy=0.556 -- vertical-
# dominant, failing MIN_HORIZONTAL_DOMINANCE_RATIO -- versus the same
# window's 2D-scaled track, dx=3.51, dy=1.90, correctly horizontal-
# dominant. Mixing a 2D numerator with a 3D denominator is therefore NOT a
# safe substitute for _torso_scaled_hip_track's own per-frame 2D scaling,
# despite 3D torso length's real, separately-useful stability (see the
# AVAILABILITY GATE below, which uses 3D torso length ONLY as a same-kind
# (length-to-length) ratio, never mixed with a 2D-computed direction/
# position -- the mixing is specifically what breaks, not 3D data itself).
# `_torso_scaled_hip_track` therefore stays 100% 2D, unchanged from before
# this session -- see MIN_TORSO_BASELINE_RATIO_3D below for where the 3D
# fix actually lives.
# ======================================================================


def _torso_scaled_hip_track(window: List[dict], smooth_window: int = 5, _raw: Optional[np.ndarray] = None) -> np.ndarray:
    """(T, 2) raw 2D hip-center position scaled by that frame's own 2D
    torso length -- camera-distance-invariant like _normalized_positions,
    but WITHOUT re-centering each frame on its own hip position. This is
    the deliberate difference from lstm_features.normalize_frame:
    hip-centering is exactly right for posture classification (translation
    shouldn't matter to Fall/Lying/Sitting/Standing) but is wrong here,
    since it makes hip position identically (0, 0) in every frame by
    construction -- silently destroying the walking translation these gait
    signals exist to measure. (Caught by this module's own synthetic-
    walking validation: compute_walking_speed/compute_postural_sway read
    as ~0 for genuinely walking synthetic data before this fix.)

    A NaN-aware centered moving average (`smooth_window` frames) is applied
    before returning. This matters because computing per-frame VELOCITY by
    finite-differencing raw position amplifies whatever per-frame position
    noise is present (MediaPipe landmark jitter on real video, or the
    Gaussian noise this module's own synthetic validation adds) -- without
    smoothing, that noise floor dominated the actual walking signal badly
    enough in validation to make a synthetic "unsteady/slower" walk read as
    FASTER than a "steady" one, purely from noise amplification, not signal.

    DELIBERATELY 2D-ONLY, NOT 3D -- see WORLD_LANDMARKS_ROOT_CAUSE_FIX's
    docstring: mixing this function's 2D hip-position numerator with a 3D
    torso-length denominator was tried and reverted after full-corpus
    validation caught it breaking genuine toward-camera walking (loses the
    perspective-growth cancellation 2D-on-2D division provides). The 3D
    fix instead lives entirely in the separate AVAILABILITY GATE
    (MIN_TORSO_BASELINE_RATIO_3D), which only ever compares a 3D length
    against a 3D length, never mixes with this function's 2D track.

    `_raw`: internal -- see _normalized_positions's docstring.
    """
    raw = _raw if _raw is not None else _raw_keypoint_array(window)
    pairs_per_frame = raw.reshape(-1, 33, 2)
    hip_mid = (pairs_per_frame[:, LEFT_HIP, :] + pairs_per_frame[:, RIGHT_HIP, :]) / 2.0
    torso_len = _raw_torso_len(window, _raw=raw)
    track = hip_mid / torso_len[:, None]

    if smooth_window > 1 and len(track) > 1:
        smoothed = pd.DataFrame(track).rolling(
            window=smooth_window, center=True, min_periods=1
        ).mean().to_numpy()
        return smoothed
    return track


# Search span (seconds, from the start of whatever window is passed to
# compute_torso_baseline) and segment length (frames) used to find a
# "confirmed standing" reference torso length -- see that function's own
# docstring for the full rationale. Deliberately NOT "just the first N
# frames": real footage (this project's own Stride.mov) shows MediaPipe
# acquisition jitter in the first ~0.5-0.8s (subject still entering frame /
# tracker not yet converged) that pollutes a blind first-N-frames average --
# measured directly, a naive first-30-frame median on Stride.mov produces a
# spurious minimum ratio of 0.222 relative to itself, entirely from this
# acquisition-noise window, not genuine gait. Scanning for the segment with
# the LOWEST local coefficient of variation avoids that window instead of
# needing to special-case it.
CALIBRATION_SEARCH_SPAN_SEC = 3.0
CALIBRATION_SEGMENT_FRAMES = 20
CALIBRATION_MIN_VALID_FRAMES = 15


def compute_torso_baseline(window: List[dict], _raw: Optional[np.ndarray] = None,
                            _ts: Optional[np.ndarray] = None,
                            _world_raw: Optional[np.ndarray] = None) -> Optional[float]:
    """A single fixed reference torso length (median shoulder-mid-to-hip-mid
    distance over the most stable segment found), intended to be computed
    ONCE from a span of a clip/session believed to represent the subject
    CONFIRMED STANDING -- e.g. the first few seconds of a clip, or any other
    span established independently of a later bend/kneel/sit -- and then
    passed as `_torso_baseline` to compute_walking_speed (directly, or via
    GaitRiskAssessor.assess_risk()'s own `_torso_baseline` parameter) for
    EVERY SUBSEQUENT window of that same clip/session.

    DO NOT call this once per assess_risk() window on a sliding-window
    stream and expect it to "recalibrate" -- if the window passed in is
    itself already inside the degenerate span (e.g. a sustained forward
    bend), this will simply find the least-bad segment WITHIN that same
    degenerate span and return a still-collapsed value, which is exactly
    why three EARLIER candidate fixes in this project failed (see
    MIN_TORSO_BASELINE_RATIO's docstring, and docs/GAIT_DATA_ASSESSMENT.md
    Section 9's "per-window torso_len coefficient-of-variation gate" /
    "per-window torso_len-percentile-ratio gate" write-ups): the worst real
    implicated window (Deep_Bend_2.mov, t=6.29-7.78s) is ENTIRELY inside the
    sustained bend, with no genuinely-standing frame anywhere inside it --
    no function operating on THAT SAME WINDOW ALONE can recover a trustworthy
    reference from it. This function's value only means anything when given
    frames from OUTSIDE the window(s) it will later be compared against.

    Method: scans `window` for the `CALIBRATION_SEGMENT_FRAMES`-frame segment
    (within the first `CALIBRATION_SEARCH_SPAN_SEC` seconds, or the whole
    input if shorter) with the LOWEST coefficient of variation (std/mean) in
    raw torso length among segments with at least `CALIBRATION_MIN_VALID_FRAMES`
    valid (non-NaN) frames, and returns the median torso length over that
    segment. Returns None if no segment anywhere in the search span has
    enough valid frames (e.g. `window` is shorter than
    CALIBRATION_SEGMENT_FRAMES, or landmark tracking is too sparse
    throughout) -- callers must treat None as "no baseline available," not
    retry with a smaller floor; compute_walking_speed's own `_torso_baseline`
    parameter already treats None as "don't gate" (its default), so passing
    this function's None straight through is always safe.

    `_raw`/`_ts`: internal -- see _normalized_positions's/_timestamps' own
    docstrings; lets a caller that already parsed `window` share that work.

    `_world_raw`: internal/opt-in -- an already-computed
    _raw_world_keypoint_array(window) (see WORLD_LANDMARKS_ROOT_CAUSE_FIX's
    docstring). When supplied AND this window has sufficient 3D coverage
    (_has_sufficient_world_coverage), the baseline is computed from 3D
    world-landmark torso length (meters) instead of 2D projected torso
    length -- MUST then be passed just as consistently to whichever
    compute_walking_speed()/compute_postural_sway() calls will compare
    against this baseline later, or the ratio check silently compares
    mismatched units (2D image-fraction vs. 3D meters). Leave as None (the
    default) for the original all-2D behavior.
    """
    raw = _raw if _raw is not None else _raw_keypoint_array(window)
    ts = _ts if _ts is not None else _timestamps(window)
    use_3d = _world_raw is not None and _has_sufficient_world_coverage(_world_raw)
    torso_len = _raw_torso_len_3d(_world_raw) if use_3d else _raw_torso_len(window, _raw=raw)

    # fps estimate, used only to convert CALIBRATION_SEARCH_SPAN_SEC (a
    # duration) into a frame count. BUG FIXED (found via this project's own
    # first real-time-pipeline integration test, not on any synthetic or
    # extraction-script fixture -- every prior caller of this function used
    # ZERO-BASED relative timestamps, e.g. i/30.0 or evaluate_real_footage.py's
    # frame-index-derived seconds, so this bug was invisible until a caller
    # supplied realtime_fall_detection.py's own real wall-clock timestamps,
    # `str(time.time())` -- a ~1.7e9-second absolute Unix epoch value, NOT
    # relative to 0): the ORIGINAL version computed `len(ts) / ts[-1]`,
    # implicitly assuming `ts[0] == 0` (frame count over elapsed time FROM
    # THE EPOCH, not from the start of `window`). Against a genuine
    # wall-clock timestamp this silently produces a "fps" on the order of
    # 1e-8 (45 frames / ~1.7e9 seconds) instead of ~30-60 -- `n_search`
    # collapses to 0, the search loop below never executes even once, and
    # this function returns None unconditionally, no matter how clean the
    # underlying landmark data is (confirmed directly: reproduced on real
    # MediaPipe-tracked frames from Deep_Bend_2.mov run through the ACTUAL
    # realtime_fall_detection.py frame-building code, where 45/45 frames had
    # perfectly valid, low-noise torso-length data yet this function still
    # returned None every time). Fixed by using the window's own ELAPSED
    # DURATION (`ts[-1] - ts[0]`, invariant to whether `ts` is relative-from-0
    # or an absolute epoch value -- every other duration computation in this
    # module already uses a difference for exactly this reason, e.g.
    # compute_sit_to_stand's `duration_sec = ts[b] - ts[a]`) rather than the
    # raw final timestamp. `len(ts) - 1` (interval count, not sample count)
    # matches how many actual frame-to-frame gaps span that duration.
    duration = float(ts[-1] - ts[0]) if len(ts) > 0 else 0.0
    if len(ts) > 1 and duration > 0:
        n_search = int(CALIBRATION_SEARCH_SPAN_SEC * ((len(ts) - 1) / duration))
    else:
        n_search = len(torso_len)
    n_search = min(n_search, len(torso_len) - CALIBRATION_SEGMENT_FRAMES)

    best_cov, best_start = None, None
    for start in range(0, max(n_search, 0)):
        seg = torso_len[start:start + CALIBRATION_SEGMENT_FRAMES]
        valid = np.isfinite(seg)
        if int(valid.sum()) < CALIBRATION_MIN_VALID_FRAMES:
            continue
        mean = float(np.nanmean(seg))
        if mean <= 1e-6:
            continue
        cov = float(np.nanstd(seg)) / mean
        if best_cov is None or cov < best_cov:
            best_cov, best_start = cov, start

    if best_start is None:
        return None
    return float(np.nanmedian(torso_len[best_start:best_start + CALIBRATION_SEGMENT_FRAMES]))


# Minimum ratio of a window's own (worst-frame) raw torso length to a
# caller-supplied compute_torso_baseline() reference, below which
# compute_walking_speed treats the window's walking_speed as UNAVAILABLE
# rather than returning a value -- an opt-in fixed-reference AVAILABILITY
# gate, not a rescaling of the value itself (see _torso_scaled_hip_track's
# "KNOWN REMAINING DEGENERACY" note for why rescaling by a fixed reference
# isn't used: it would break camera-distance invariance for genuine
# toward/away-camera walking, where torso_len legitimately and correctly
# grows/shrinks as the subject's distance from the camera changes across
# the window -- exactly what _torso_scaled_hip_track's per-frame scaling
# exists to normalize away).
#
# 2D-MODE (this constant): WIRED INTO compute_walking_speed AND (a later
# session) compute_stride_regularity -- both signals' ambulation gates run
# `_ambulation_check` on the identical 2D `_torso_scaled_hip_track`, so both
# are exposed to the exact same torso-length-collapse degeneracy and both
# only ever reach this gate AFTER already clearing that same ambulation
# check (see compute_stride_regularity's own docstring for the real-footage
# and synthetic evidence that motivated wiring it in: a sustained bend's
# collapsed torso length amplifies ordinary ankle-tracking noise into a
# fabricated stride-regularity CV the same way it amplifies hip noise into
# a fabricated walking_speed). DELIBERATELY NOT compute_postural_sway
# (despite gait_risk.py's own docstring calling for "test gating
# walking_speed/postural_sway" -- this was tried and rejected using this
# project's own real corpus, not assumed): compute_postural_sway is
# legitimately used to measure sway during SITTING, not just standing (see
# that function's own docstring, "postural sway while standing/sitting
# still") -- and sitting genuinely collapses 2D torso_len relative to a
# standing baseline, often far more severely than the bend this gate
# targets. Measured directly on this project's own real footage:
# Sit_Stand_1.mov/Sit_Stand_2.mov's genuine, currently-working seated-sway
# windows show 2D torso_len/standing-baseline ratios as low as 0.013-0.27 --
# applying this same 2D-based gate to postural_sway would mark most of the
# pipeline's real, currently-correct seated-sway output unavailable, a
# regression far larger than the bug this gate exists to reduce.
#
# STRIDE_REGULARITY VALIDATION SCOPE, disclosed honestly (narrower than
# walking_speed's own full-44-clip validation above): confirmed the
# fabrication this gate closes on real footage (Deep_Bend_2.mov, production
# extraction path, CV up to 0.429 during the GT-confirmed sustained bend)
# and confirmed genuine-walking recall is unaffected on this project's own
# synthetic walking generator (tests/test_gait_risk.py::_walking_window) --
# but NOT re-run against the full 44-clip real corpus specifically for
# stride_regularity's own recall (only walking_speed's gate has that). Low
# incremental risk, not zero: this reuses walking_speed's already-validated
# mask/threshold/aggregation exactly (same `_ambulation_check` output, same
# MIN_TORSO_BASELINE_RATIO, same worst-single-frame convention) rather than
# an independently re-tuned one, so any window it newly rejects is a window
# compute_walking_speed's own gate already rejects for the identical reason
# -- but stride_regularity's OWN peak-detection recall on the marginal
# (surviving) windows was not separately re-checked against the full real
# corpus. Flagged in docs/GAIT_CODE_REVIEW.md as a residual, data-dependent
# validation gap, not silently claimed complete.
#
# 3D-MODE (see MIN_TORSO_BASELINE_RATIO_3D below) closes exactly this gap:
# once WORLD_LANDMARKS_ROOT_CAUSE_FIX's 3D torso length is available, real
# separation between genuine sitting and a genuine bend DOES exist (unlike
# 2D torso_len, and unlike Section 11's rejected knee-angle candidate) --
# see that constant's own docstring for the full validation. compute_
# postural_sway's gate is therefore wired to 3D-mode ONLY -- 2D-mode stays
# walking_speed/stride_regularity-only, exactly as before.
#
# A SHOULDER-WIDTH-RELATIVE alternative (torso_len / shoulder_width,
# baselined the same way, on the theory that shoulder width shouldn't
# collapse under a forward bend the way vertical torso length does) was
# also tried and rejected using the real corpus. It IS true on real footage
# that shoulder_width stays comparatively stable through Deep_Bend_2.mov/
# Deep_Bend_3.mov's sustained bend while torso_len collapses (measured
# directly: shoulder_width stays ~0.13-0.17 throughout while torso_len
# drops to ~0.05, versus both starting near parity) -- but shoulder_width
# has its OWN severe 2D-projection collapse under a SIDE/PROFILE camera
# angle, which this project's corpus specifically includes (recorded for
# exactly this camera-angle-generalization purpose, see
# docs/GAIT_DATA_ASSESSMENT.md Section 8.1/9): Sit_Stand_SideAngle_1.mov/
# Sit_Stand_SideAngle_3.mov's genuine standing-transition windows measure
# torso_len/shoulder_width ratios as low as 0.167-0.301 relative to their
# own baseline -- a WORSE floor than the plain torso_len approach's
# genuine-walking floor below, so it was rejected in favor of the simpler
# metric rather than combined with it.
#
# THRESHOLD DERIVATION (real full-corpus validation, all 44 real clips in
# test_footage/, using compute_torso_baseline()'s stable-segment method as
# the reference for each clip): the TIGHTEST real constraint is
# Moving_in_out_frame.MOV -- a genuine toward/away-camera walking clip
# already in this project's corpus -- whose currently-available,
# plausible-valued (0.49-1.72 torso-lengths/sec, matching this exact
# clip's previously-documented real range) windows have a worst-single-frame
# ratio of 0.451 to their own clip's stable-segment baseline (this is a
# REAL, SUSTAINED effect -- the subject genuinely walks ~2x farther from
# the camera partway through the clip -- not single-frame noise; directly
# confirmed by inspecting the raw torso_len trace). 0.40 sits below that
# floor with real, if MODEST (~11%), margin -- deliberately narrower than
# most other margins in this file (e.g. FALLBACK_MAX_TRANSLATION_SPEED's
# ~2x), because this is the single closest real reference this project has,
# not because a wide margin wasn't wanted. At this threshold: Deep_Bend_3.mov's
# ENTIRE spurious walking_speed artifact (previously 2.7-7.7 torso-lengths/sec
# throughout its sustained bend) is eliminated; Deep_Bend_2.mov's most
# severe windows (previously up to 15.8 torso-lengths/sec) are eliminated
# down to a residual worst case of 6.17 (a >60% reduction, comparable to or
# better than the smoothing-based fix already tried and rejected in
# docs/GAIT_DATA_ASSESSMENT.md Section 9, which reduced but did not
# eliminate: 15.5 -> 6.8). The residual moderate-severity Deep_Bend_2.mov
# windows (worst-frame ratio 0.42-0.60, values 2.0-6.2 torso-lengths/sec)
# are NOT caught -- a real, disclosed, remaining limitation of this gate,
# not silently claimed fixed. No walking clip in the full 44-clip corpus
# (including Stride.mov/Stride_Big_Starting_Leap.mov, both flagged in prior
# sessions as showing genuine torso-length dips during real walking) loses
# any previously-available walking_speed window at this threshold -- the
# apparent Stride.mov dips traced, on inspection, to the SAME first-second
# acquisition-noise window compute_torso_baseline's stable-segment search
# is specifically designed to avoid, not to genuine mid-walk degeneracy.
MIN_TORSO_BASELINE_RATIO = 0.40


# 3D-MODE equivalent of MIN_TORSO_BASELINE_RATIO -- compares a 3D world-
# landmark torso length (see WORLD_LANDMARKS_ROOT_CAUSE_FIX's docstring,
# _raw_torso_len_3d) against a compute_torso_baseline() reference that was
# ITSELF computed with `_world_raw` supplied. A DIFFERENT constant from
# MIN_TORSO_BASELINE_RATIO because 3D torso length collapses far less
# severely than 2D during a genuine bend (measured: 3D drops to 49-67% of
# standing vs. 2D's 32-44%, see WORLD_LANDMARKS_ROOT_CAUSE_FIX point 1) --
# reusing the 2D threshold here would fail to catch almost anything.
#
# AGGREGATION DIFFERS BY SIGNAL, deliberately, and this was caught (not
# assumed) by full-44-clip validation before shipping: compute_walking_speed
# (and, a later session, compute_stride_regularity, for the identical
# reason -- see MIN_TORSO_BASELINE_RATIO's own "STRIDE_REGULARITY
# VALIDATION SCOPE" note) compares this window's WORST-SINGLE-FRAME 3D
# ratio (matching MIN_TORSO_BASELINE_RATIO's own convention), while
# compute_postural_sway compares the window's MEDIAN 3D ratio. An earlier
# version of this fix
# used worst-single-frame for BOTH, on the assumption that consistency was
# safer -- full-corpus validation caught this shipping a real regression:
# Sit_Stand_1.mov's ENTIRE genuine seated-sway signal (7/7 windows) and
# SitFloor_lowKeypoints.MOV's floor-sitting sway (12/15 windows) have real,
# single-frame 3D-ratio dips as low as 0.45-0.61 during otherwise-genuine,
# currently-correct sitting -- a worst-single-frame check wrongly
# suppressed them. Their WINDOW-MEDIAN ratios (0.72-0.95) do not have this
# problem, so compute_postural_sway uses median. compute_walking_speed
# keeps worst-single-frame because ITS gate only ever runs on windows that
# already passed `_ambulation_check` (i.e. already show apparent
# translation) -- genuine sitting/standing-still windows never reach it at
# all (confirmed: worst-single-frame produces ZERO regressions outside
# Deep_Bend_2.mov/Deep_Bend_3.mov across the full 44-clip corpus), and
# worst-single-frame is MORE sensitive there, catching real transient
# bend-onset spikes a median would dilute away.
#
# THRESHOLD DERIVATION (full 44-clip real corpus, same standard as
# MIN_TORSO_BASELINE_RATIO): window-level (90-frame, matching
# MIN_WINDOW_FRAMES) MEDIAN 3D-torso/baseline ratio measured across every
# GT-confirmed sustained-bend window (Deep_Bend_2.mov: 0.422-0.515;
# Deep_Bend_3.mov: 0.517-0.693) and every GT-confirmed genuine-sitting
# window across every sitting-family clip in the corpus, INCLUDING
# floor-sitting with legs extended (Sit_Stand_1.mov/Sit_Stand_2.mov:
# 0.854-0.893; SitFloor_lowKeypoints.MOV, a harder case that broke Section
# 11's knee-angle candidate: 0.718-0.947). The tightest real gap is
# Deep_Bend_3.mov's ceiling (0.693) vs. SitFloor_lowKeypoints.MOV's floor
# (0.718) -- thin (~3.6%), narrower than MIN_TORSO_BASELINE_RATIO's own
# already-narrow ~11% margin, disclosed as such rather than rounded to look
# more confident than the evidence supports. 0.70 sits inside that gap.
#
# VALIDATED RESULT (full 44-clip corpus, both signals, EVERY window, not
# just the two target clips -- see docs/GAIT_DATA_ASSESSMENT.md Section 12
# for the complete run): zero windows changed in any of the other 42
# clips, for either walking_speed or postural_sway. In the two target
# clips: Deep_Bend_3.mov's spurious walking_speed (previously eliminated
# down to 0 by the already-shipped 2D gate) and postural_sway (previously
# untouched) are both now fully unavailable throughout the sustained bend.
# Deep_Bend_2.mov's walking_speed residual (Section 10's disclosed
# worst-case, 6.17 torso-lengths/sec, left uncaught by the 2D gate) is
# reduced further to 2.04 -- a genuine additional improvement, though NOT
# fully eliminated (one moderate-severity window, mostly-standing by
# median but with a brief bend-onset spike at its tail end, remains
# available at 2.04 torso-lengths/sec -- disclosed, not hidden). Deep_
# Bend_2.mov's postural_sway (previously 0.09-0.29, "far outside any
# plausible real-footage range... 0.002-0.09" per docs/
# GAIT_DATA_ASSESSMENT.md Section 9) is now fully unavailable throughout.
MIN_TORSO_BASELINE_RATIO_3D = 0.70


# Minimum total hip-center path length (torso-lengths) over the window
# before compute_walking_speed treats the window as containing an actual
# walking bout at all. Without this gate, a perfectly stationary person
# (hip displacement ~0 every frame) reads as "extremely slow gait speed"
# and gets penalized as high-risk for not walking rather than correctly
# being reported as "no gait to assess" -- standing still is not the same
# clinical situation as an observed slow/shuffling walk, and conflating
# them was a real bug caught in this module's own smoke testing.
MIN_AMBULATION_PATH = 0.5

# Maximum physically plausible instantaneous hip speed, in torso-lengths/sec
# -- the upper counterpart of MIN_AMBULATION_PATH above. Without this gate, a
# fall's rapid hip displacement over 1-2 frames (real footage measured
# 40-70+ torso-lengths/sec -- see benchmarks/gait_footage_validation_report.md's
# "flicker" entries, e.g. Fall_and_lie hit 75.28) gets averaged in as if it
# were genuine locomotion. That's not just an inflated number: _speed_risk
# in gait_risk.py maps FASTER speed to LOWER risk (a real walking-speed
# proxy, by design -- see that function's own docstring), so an absurd
# "speed" from a fall reads as CONFIDENTLY LOW risk at the exact moment risk
# is highest -- the failure mode this constant exists to close off.
#
# Derived from this project's OWN existing translational-implausibility
# precedent rather than an arbitrary or literature-imported number (per this
# module's docstring, literature absolute cut-points don't transfer to this
# proxy's uncalibrated scale):
#   pipeline_utils.VELOCITY_CAP = 25.0 body-heights/sec -- itself derived by
#   measuring peak hip speed across every labelled real fall in this
#   project's training data; genuine falls never exceeded 20.3
#   body-heights/sec (see VELOCITY_CAP's own docstring/comment).
#   x 2.0 torso-lengths per body-height -- the SAME approximation
#   pipeline_utils.build_pose_row already uses elsewhere to derive
#   body_height from the torso segment alone (`body_height = torso_len * 2.0`,
#   pipeline_utils.py's lower-body-occluded fallback branch), so this reuses
#   an existing, already-justified conversion rather than inventing one.
#   = 50.0 torso-lengths/sec.
# Cross-checked against this project's own real MediaPipe-tracked data
# (data/processed_keypoints/pose_keypoints.csv, ~8800 frames with ankles
# visible): the actual body_height/torso_length ratio has median 2.31 (IQR
# 2.02-2.43) -- so the 2.0 factor above is a slightly conservative (lower,
# i.e. stricter) stand-in for the real ratio, not an overestimate that would
# let genuine artifacts slip through uncaught.
#
# Applied per FRAME-PAIR (instantaneous speed), not to the window's mean --
# a fall's huge displacement typically happens over 1-2 frames out of an
# entire multi-second window, so gating the instantaneous value catches it
# at the source (excluding just those frame-pairs, the same way an invalid/
# NaN pair is already excluded) instead of letting one glitched pair drag an
# averaged "walking speed" up to where it reads as confidently low risk.
MAX_PLAUSIBLE_HIP_SPEED = 50.0

# Minimum ratio of NET (straight-line, first-to-last) hip displacement to
# TOTAL accumulated path length, in [0, 1] (dimensionless -- a ratio of two
# torso-length quantities), before compute_walking_speed trusts an
# accumulated path as genuine ambulation rather than stationary tracking
# jitter that accumulates "distance" through incoherent back-and-forth
# noise. MIN_AMBULATION_PATH alone only floors the absolute path length --
# it says nothing about whether that path went anywhere. A real walking
# trajectory is directionally coherent (net displacement stays close to the
# path length); jitter around a fixed point is not (many small, largely
# canceling steps in random directions inflate path length while net
# displacement stays small) -- this is the standard signature of a random
# walk (net displacement grows ~sqrt(N) with more samples while path length
# grows ~N, so the ratio trends toward 0 as the window gets longer).
#
# Value derived from direct measurement, real and synthetic, in this
# session (not assumed):
#   - Synthetic per-frame landmark jitter, calibrated to match REAL
#     measured quiet-standing frame-to-frame hip displacement (~0.07-0.12
#     torso-lengths/pair, from SitFast_GetupFast.MOV frames 0-38 and
#     Chair_fall.mp4 frames 0-47), produces a ratio that falls as window
#     length grows: 0.048 (90 frames) -> 0.017 (150) -> 0.013 (300) ->
#     0.001 (600) -- the random-walk signature above.
#   - The SAME two real "quiet standing" clips (which include natural
#     small movements -- weight-shifting, minor repositioning -- not pure
#     noise) measured 0.55-0.59.
#   - Genuine directed walking (this module's own validated synthetic
#     walking generator, see tests/test_gait_risk.py::_walking_window)
#     measures ~1.0 at every tested speed (a straight walking trajectory is
#     maximally coherent by construction).
# 0.2 sits with wide margin above the worst pure-jitter case observed (>4x
# the 90-frame case, >15x the longer-window cases) and well below both real
# quasi-still motion and genuine walking -- chosen conservatively low (not
# centered between the two clusters) so it only screens out windows that
# are OVERWHELMINGLY incoherent, minimizing the risk of suppressing a
# genuine short or slow movement.
MIN_AMBULATION_COHERENCE = 0.2

# Minimum ratio of |net horizontal displacement| to |net vertical displacement|
# (both first-to-last, on the same _torso_scaled_hip_track used by
# MIN_AMBULATION_COHERENCE) before the ambulation gate trusts a coherent,
# sufficiently-long path as genuine WALKING rather than some other
# coherent-but-non-ambulatory postural change. MIN_AMBULATION_PATH and
# MIN_AMBULATION_COHERENCE together only establish that the hip moved a
# meaningful distance in a consistent direction -- neither says anything
# about which direction. A voluntary vertical translation (kneeling down,
# crouching) is exactly as "coherent" by that definition as horizontal
# locomotion is: the hip drops in a straight, sustained line, which passes
# both existing checks with margin to spare.
#
# Confirmed on real footage this project already has (Kneeling.MOV, see
# docs/GAIT_CODE_REVIEW.md finding #2): the kneel-down phase was measured
# (5 overlapping 90-frame windows spanning the kneel) at |net_dx|/|net_dy|
# ratios of 0.075-0.171 -- i.e. the vertical component was 5.8x-13.3x
# LARGER than the horizontal one in every window, while
# compute_walking_speed still read this as ~0.32-0.54 torso-lengths/sec of
# "walking" (risk_contribution ~0.80-0.89). 1.0 (horizontal component must
# be at least as large as vertical) sits with a 5.8x-13.3x margin above
# every measured kneeling ratio -- the same "wide margin over the one real
# non-ambulatory reference available" approach MIN_AMBULATION_COHERENCE and
# FALLBACK_MAX_TRANSLATION_SPEED already use elsewhere in this module.
#
# REAL WALKING FOOTAGE VALIDATION (closes the gap this docstring previously
# flagged as open -- see docs/GAIT_CALIBRATION_DATASET_PLAN.md Section 3
# Table 2, `normal_walk`/`normal_walk_side` scenarios): when this constant
# was first added, this project had NO real footage of a person actually
# WALKING at any camera angle -- it was validated only against this
# module's own synthetic walking generator (purely horizontal by
# construction) and ONE real non-ambulatory clip (Kneeling.MOV). Six new
# real walking clips at THREE distinct camera angles
# (test_footage/GAIT_Analysis_Test_Footages/) now close that gap:
#   - Lateral_Walk.mov (side-on, classic gait profile): net |dx|/|dy| per
#     90-frame sliding window ranged 0.58-180.96 (median 4.20) -- 11/12
#     windows still cleared this gate (the one exclusion, ratio 0.58, was a
#     genuinely non-dominant-horizontal moment, not over-suppression).
#   - Diagonal_Walk_1.mov (oblique -- combined lateral + depth motion):
#     ratio ranged 0.03-25.12 (median 3.84) -- 8/9 windows cleared it.
#   - Stride.mov / Stride_Big_Starting_Leap.mov / Stride_Inconsistent_Pace.mov
#     / Stride_Pause.mov (walking TOWARD/away from a portrait-oriented
#     camera -- the case expected to stress this gate most, since a
#     portrait frame's perspective growth as a subject approaches is
#     largely VERTICAL): ratio ranged 0.72-5.46 across all four clips
#     (medians 1.22-1.84) -- closer to the 1.0 threshold than the
#     lateral/diagonal clips, as expected, but still predominantly above
#     it: 18/22, 2/4, 5/7, and 3/3 windows respectively still cleared the
#     gate and reported a walking_speed value.
# Net conclusion: MIN_HORIZONTAL_DOMINANCE_RATIO=1.0 is NOT over-restrictive
# for any of the three camera framings actually tested -- toward-camera
# walking sits closest to the boundary (by real optical-perspective
# geometry, not a threshold-tuning artifact) but still clears it in the
# large majority of windows across four independent toward-camera clips.
# No threshold change was made -- this validates the EXISTING 1.0 value
# against real, multi-angle evidence rather than adjusting it to fit any
# single clip (per this project's own calibration-plan guidance against
# single-video tuning). The original kneeling-derived margin (a
# 5.8x-13.3x ratio gap between genuine horizontal walking and the one
# vertical-motion false positive on file) remains the constant's primary
# justification; this validation only confirms it against real walking,
# not vertical motion.
MIN_HORIZONTAL_DOMINANCE_RATIO = 1.0


def _ambulation_check(hip_center: np.ndarray, ts: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Shared stationarity/ambulation gate over a torso-scaled hip track --
    factored out of compute_walking_speed so compute_stride_regularity can
    reuse the exact same gate (see that function's docstring) instead of
    duplicating this logic or inventing a separate, independently-tuned
    check. Not a change in behavior for compute_walking_speed: this is a
    pure extraction of what was previously inline in that function's body,
    verified to still return the identical mask/instantaneous_speed pair.

    Returns `(None, None)` if the track does not represent genuine
    ambulation (too few valid frames, too little plausible path, path
    dominated by implausible/glitched pairs, path not directionally
    coherent, or -- see MIN_HORIZONTAL_DOMINANCE_RATIO -- net displacement
    not horizontally dominant). Otherwise returns `(mask, instantaneous_speed)`:
    `mask` is the boolean (T-1,)-shaped array of frame-pairs that are valid,
    plausible, and therefore trustworthy; `instantaneous_speed` is the
    (T-1,)-shaped per-pair speed array `mask` indexes into (some entries
    outside `mask` may be meaningless/undefined -- only `instantaneous_speed[mask]`
    is guaranteed valid, exactly as compute_walking_speed always used it).

    BOUNDARY-GLITCH FIX (see docs/GAIT_CODE_REVIEW.md's follow-up audit):
    the coherence check's net-displacement numerator is now derived from the
    SAME `mask` (valid + plausible + dt>0) used for `plausible_path`'s
    denominator, not from the broader `valid` (NaN-only) filter this used to
    use. Before this fix, a single implausible frame-pair sitting at the
    window's first or last VALID (but not necessarily plausible-paired)
    frame was excluded from `plausible_path` (correctly) but NOT from the
    net-displacement endpoints (incorrectly) -- so one bad boundary frame
    (e.g. a single MediaPipe misdetection) could inflate net_disp while
    contributing nothing to plausible_path, pushing net_disp/plausible_path
    past MIN_AMBULATION_COHERENCE for a subject who never moved. Reproduced
    directly: a 600-frame pure random-walk jitter track (calibrated to real
    quiet-standing footage, correctly rejected -- None -- by this gate)
    flips to a fabricated ~1.07 torso-lengths/sec "walking speed" once a
    single one-frame, 4.0-torso-length position offset is injected at frame
    0 -- exactly the "stationary subject reads as gait" failure class this
    module has already fixed for compute_postural_sway (see
    PosturalSwayPlausibilityTests) and for direction-of-translation
    (MIN_HORIZONTAL_DOMINANCE_RATIO), but had not closed for this specific
    numerator/denominator mismatch. See
    test_boundary_glitch_does_not_inflate_net_displacement in
    tests/test_gait_risk.py for the regression test locking this in.
    """
    valid = ~np.isnan(hip_center).any(axis=1)
    if valid.sum() < 2:
        return None, None

    # Vectorized equivalent of the old per-frame loop: a consecutive pair
    # (i-1, i) contributes iff both frames are valid AND dt > 0, exactly
    # the same gate the loop applied before accumulating plausible_path/speeds.
    pair_valid = valid[1:] & valid[:-1]
    dt = np.diff(ts)
    dt_positive = dt > 0

    disp = np.linalg.norm(np.diff(hip_center, axis=0), axis=1)
    # Safe denominator only to avoid a division warning on dt<=0 pairs --
    # those are already excluded by dt_positive below regardless of what
    # this division produces for them, so the placeholder value is never used.
    safe_dt = np.where(dt_positive, dt, 1.0)
    instantaneous_speed = disp / safe_dt
    with np.errstate(invalid="ignore"):
        plausible = instantaneous_speed <= MAX_PLAUSIBLE_HIP_SPEED

    raw_valid = pair_valid & dt_positive
    mask = raw_valid & plausible
    if not mask.any():
        return None, None

    plausible_path = float(disp[mask].sum())
    if plausible_path < MIN_AMBULATION_PATH:
        return None, None

    excluded_path = float(disp[raw_valid & ~plausible].sum())
    if excluded_path > plausible_path:
        return None, None

    # Trajectory-coherence check (see MIN_AMBULATION_COHERENCE's docstring):
    # O(1) extra work reusing the already-computed `mask` array -- no new
    # loop, no re-parsing, no additional smoothing. Net-displacement
    # endpoints are the first and last FRAME that participate in a masked
    # (valid + plausible + dt>0) pair, NOT merely the first/last NaN-valid
    # frame -- see this function's own "BOUNDARY-GLITCH FIX" docstring note
    # above for why that distinction matters.
    mask_pair_idx = np.flatnonzero(mask)
    start_frame = int(mask_pair_idx[0])
    end_frame = int(mask_pair_idx[-1]) + 1
    net_vector = hip_center[end_frame] - hip_center[start_frame]
    net_disp = float(np.linalg.norm(net_vector))
    if net_disp < plausible_path * MIN_AMBULATION_COHERENCE:
        return None, None

    # Horizontal-dominance / translation-direction check (see
    # MIN_HORIZONTAL_DOMINANCE_RATIO's own docstring): a coherent, plausible,
    # sufficiently long path can still be a purely VERTICAL postural change
    # (kneeling down) rather than locomotion -- this rejects that case.
    net_dx, net_dy = abs(float(net_vector[0])), abs(float(net_vector[1]))
    if net_dx < MIN_HORIZONTAL_DOMINANCE_RATIO * net_dy:
        return None, None

    return mask, instantaneous_speed


def compute_walking_speed(window: List[dict], _hip_track: Optional[np.ndarray] = None,
                           _ts: Optional[np.ndarray] = None,
                           _quality_out: Optional[Dict[str, Any]] = None,
                           _raw: Optional[np.ndarray] = None,
                           _torso_baseline: Optional[float] = None,
                           _world_raw: Optional[np.ndarray] = None) -> Optional[float]:
    """
    Mean hip-center speed across the window, in torso-lengths/second (NOT
    meters/second -- see module docstring). Lower values correspond to the
    literature's "slower gait speed" fall-risk indicator, in relative
    (not absolute/clinical) terms only.

    Returns None if fewer than 2 frames have a valid (non-NaN) hip position,
    OR if the total path traveled (using only PLAUSIBLE frame-pairs -- see
    below) never exceeds MIN_AMBULATION_PATH -- i.e. this window doesn't
    contain a walking bout at all (e.g. the person is standing/sitting still
    throughout), which is a different situation from "walking slowly" and
    must not be scored as if it were.

    Frame-pairs whose instantaneous speed exceeds MAX_PLAUSIBLE_HIP_SPEED
    are excluded from both the path-length check and the mean -- the same
    way an invalid (NaN) or non-positive-dt pair already is -- rather than
    letting a single fall-glitched frame-pair drag the window's average up
    to where it misreads as fast, confidently-low-risk walking (see
    MAX_PLAUSIBLE_HIP_SPEED's own docstring). A window whose only real
    displacement comes from such a spike therefore reports None here (no
    genuine gait observed), not an inflated speed.

    Also returns None if the EXCLUDED (implausible) frame-pairs account for
    MORE of the window's total raw path than the plausible ones do -- i.e.
    this window's overall motion is majority artifact, not signal. Found on
    real footage (Fall_and_lie.mp4): excluding only the individual
    implausible pairs left a residual "plausible" mean of ~10-13
    torso-lengths/sec even though 86-87% of the window's total raw path
    came from just a dozen frame-pairs peaking at 753 torso-lengths/sec (an
    unambiguous tracking glitch, not a person moving) -- a residual average
    over the remaining, much smaller fraction of genuinely-observed motion
    is not a trustworthy "this person was walking at ~10-13 torso-lengths/
    sec" reading, the same reasoning MIN_AMBULATION_PATH already applies to
    "not enough real signal," extended to "what little signal exists is
    outweighed by noise."

    Also returns None if the ratio of net (first-to-last) displacement to
    the accumulated path falls below MIN_AMBULATION_COHERENCE -- i.e. the
    path went nowhere in particular. MIN_AMBULATION_PATH alone can be
    crossed by a stationary subject purely from accumulated per-frame
    tracking jitter (reproduced directly: independent per-frame landmark
    noise, even at magnitudes calibrated from real quiet-standing footage,
    accumulates path length as the window grows even though the person
    never moved) -- see MIN_AMBULATION_COHERENCE's own docstring for the
    full derivation. This check is what actually distinguishes that case
    from genuine (if slow or brief) ambulation, which MIN_AMBULATION_PATH's
    absolute floor cannot do alone.

    Also returns None if the net displacement isn't horizontally dominant
    (see MIN_HORIZONTAL_DOMINANCE_RATIO's own docstring) -- a coherent,
    sufficiently long, plausible path can still be a purely VERTICAL
    postural change (e.g. kneeling down) rather than locomotion; none of
    the checks above can see that, since they only look at path length and
    straightness, not direction. Confirmed real false positive this closes
    off: Kneeling.MOV previously read as ~0.32-0.54 torso-lengths/sec
    "walking speed".

    All four gates above are implemented in the shared `_ambulation_check`
    helper (also reused by compute_stride_regularity -- see that function's
    docstring) rather than inline here.

    `_hip_track`: internal -- lets GaitRiskAssessor.assess_risk() pass in an
    already-computed _torso_scaled_hip_track() so it isn't independently
    recomputed here AND in compute_postural_sway() for the same window
    (each call re-parses+smooths the full window, an O(T) pass repeated
    twice for no reason when both are called back-to-back, which is exactly
    what assess_risk() does). Leave as None to compute it standalone -- this
    parameter doesn't change any result, only whether the work is shared.

    `_ts`: internal -- an already-computed _timestamps(window), shared the
    same way (see _timestamps' own docstring for why this mattered).

    `_quality_out`: internal, OPTIONAL -- if a dict is passed, this
    function fills in `"reliability"` (fraction of frame-pairs in the
    window that were valid, plausible, and therefore actually used in the
    mean -- i.e. `len(mask.nonzero()) / len(mask)`, in [0, 1]) as a side
    effect, ONLY when returning a real value. See compute_stride_
    regularity's `_quality_out` docstring for the shared rationale (this is
    the same reliability CONCEPT -- "how much of the window's data
    supported this number" -- applied to this signal's own gate).

    `_raw`: internal -- an already-computed _raw_keypoint_array(window),
    shared the same way `_hip_track`/`_ts` are. Only actually used when
    `_torso_baseline` is also supplied (see below); harmless to pass
    otherwise.

    `_torso_baseline`: OPTIONAL, opt-in, NOT an internal sharing parameter
    like the others above -- a fixed reference torso length from
    compute_torso_baseline(), established by the CALLER from a span of this
    same clip/session believed to represent confirmed standing (see that
    function's own docstring for how to compute one, and why it must NOT be
    recomputed per-window). When supplied, this window's walking_speed is
    reported as UNAVAILABLE (None) -- the value itself is never rescaled --
    if this window's own worst-single-frame raw torso length falls below
    `MIN_TORSO_BASELINE_RATIO` of that reference (see that constant's own
    docstring for the full real-footage derivation, what it catches, and
    its disclosed residual limitations). Leave as None (the default -- every
    current caller, including every existing GaitRiskAssessor/gait_stream.py
    call site) to preserve today's exact behavior: this pipeline still has
    no session-level calibration wired in by default (see gait_risk.py's
    "no camera/subject calibration exists" module docstring) -- this
    parameter exists so a caller that HAS established one can opt in.

    `_world_raw`: internal/opt-in -- an already-computed
    _raw_world_keypoint_array(window) (see WORLD_LANDMARKS_ROOT_CAUSE_FIX's
    docstring). Does NOT change `hip_center`'s own scale factor (that stays
    2D-only -- see _torso_scaled_hip_track's own docstring for why a 2D/3D
    mix was tried there and reverted). ONLY affects the availability gate:
    when supplied AND this window has sufficient 3D coverage AND
    `_torso_baseline` is ALSO supplied, the gate compares 3D-to-3D using
    MIN_TORSO_BASELINE_RATIO_3D instead of 2D-to-2D using
    MIN_TORSO_BASELINE_RATIO -- a same-kind (length-to-length) ratio
    comparison, not a position/direction one, which is why mixing is safe
    here even though it isn't for the track itself. `_torso_baseline` MUST
    have been computed by compute_torso_baseline() with `_world_raw`
    supplied just as consistently, or this compares mismatched units.
    Leave as None (the default) for the original all-2D behavior.
    """
    need_raw = _torso_baseline is not None or _world_raw is not None
    raw = _raw if _raw is not None else (_raw_keypoint_array(window) if need_raw else None)
    hip_center = _hip_track if _hip_track is not None else _torso_scaled_hip_track(window, _raw=raw)
    ts = _ts if _ts is not None else _timestamps(window)

    mask, instantaneous_speed = _ambulation_check(hip_center, ts)
    if mask is None:
        return None

    if _torso_baseline is not None and _torso_baseline > 1e-6:
        use_3d = _world_raw is not None and _has_sufficient_world_coverage(_world_raw)
        valid_torso_len = None
        if use_3d:
            torso_len = _raw_torso_len_3d(_world_raw)
            valid_torso_len = torso_len[np.isfinite(torso_len)]
            # Worst-single-frame, like 2D-mode -- NOT median. compute_postural_
            # sway's 3D gate uses median instead (see its own comment) because
            # IT is regularly evaluated on genuine sitting windows, where a
            # min()-based check has real false positives (Sit_Stand_1.mov/
            # SitFloor_lowKeypoints.MOV, see MIN_TORSO_BASELINE_RATIO_3D's
            # docstring). walking_speed's gate only ever runs on windows that
            # already passed _ambulation_check (i.e. already show apparent
            # translation) -- genuine sitting/standing-still windows never
            # reach it at all (confirmed on the full 44-clip corpus: min()
            # here produces zero regressions outside Deep_Bend_2.mov/
            # Deep_Bend_3.mov), so the more sensitive min() is safe and
            # strictly better here: it catches real transient bend-onset
            # spikes a median would dilute away (e.g. Deep_Bend_2.mov's
            # t=1.77-2.53s windows, mostly-standing by median but already
            # producing a spurious 2.0-6.2 torso-lengths/sec spike from the
            # bend just entering the window's tail end).
            ratio = float(np.min(valid_torso_len)) / _torso_baseline if valid_torso_len.size else None
            threshold = MIN_TORSO_BASELINE_RATIO_3D
        else:
            torso_len = _raw_torso_len(window, _raw=raw)
            valid_torso_len = torso_len[np.isfinite(torso_len)]
            # 2D-mode keeps the ORIGINAL worst-single-frame check -- this was
            # validated (and re-validated on the full corpus) against min(),
            # not median; see MIN_TORSO_BASELINE_RATIO's own docstring.
            ratio = float(np.min(valid_torso_len)) / _torso_baseline if valid_torso_len.size else None
            threshold = MIN_TORSO_BASELINE_RATIO
        if ratio is None or ratio < threshold:
            return None

    if _quality_out is not None and len(mask) > 0:
        _quality_out["reliability"] = float(np.count_nonzero(mask)) / float(len(mask))

    return float(np.mean(instantaneous_speed[mask]))


# ======================================================================
# TORSO ANGULAR VELOCITY -- STANDALONE DIAGNOSTIC, NOT WIRED INTO
# risk_score ANYWHERE (see docs/GAIT_DATA_ASSESSMENT.md's risk-mapping
# audit follow-up session for the full investigation this belongs to)
# ======================================================================
# Candidate SECOND signal to discriminate "fast walking" from "fast
# falling" within compute_walking_speed's own available range --
# motivated by a real, evidenced gap the risk-mapping audit found and
# explicitly left open (see docs/GAIT_DATA_ASSESSMENT.md Section 17.3):
# hip TRANSLATION SPEED alone cannot separate the two on this project's
# real corpus (Diagonal_Walk_1.mov's genuine brisk walking reaches 3.43
# torso-lengths/sec, overlapping real fall-onset speeds of 1.8-3.9
# torso-lengths/sec almost entirely; a targeted fix -- capping the speed
# INPUT -- was tried and rejected because it would suppress the genuine
# fast-walking case along with the ambiguous one).
#
# WHY TORSO ANGLE, NOT ANOTHER TRANSLATION-BASED MEASURE: walking and
# falling both move the hip through space at comparable speeds (confirmed
# above) -- but they are fundamentally different POSTURAL events. Brisk
# walking, however fast, keeps the trunk close to upright throughout (a
# normal gait cycle's torso pitch varies by only a few degrees). A fall --
# forward, backward, or sideways -- necessarily rotates the trunk away
# from vertical as the body goes down, and does so FAST relative to how
# long a stride takes. This is not a new hypothesis invented for this
# module: `pipeline_utils.py`'s own existing heuristic fall classifier
# already computes and thresholds an equivalent quantity
# (`torso_angular_velocity`, gated at 150-250 deg/sec depending on the
# code path, with a 720 deg/sec hard implausibility cap) as one of its
# real, already-shipped fall signals -- independent evidence that this
# measurement is a meaningful discriminator in THIS codebase's own real
# footage, for a closely related problem. This module does NOT import or
# call that code (per this project's own established boundary --
# pipeline_utils.py stays read-only from gait_features.py, never edited
# to expose internals, and Random Forest / heuristic fall-detection code
# is out of scope to touch here) -- it independently RE-DERIVES the same
# underlying measurement (torso pitch angle rate of change, in
# degrees/second) from the landmarks this module already parses, exactly
# the way `_HIP_ANGLE_SITTING_MAX`/`_HIP_ANGLE_STANDING_MIN` above already
# duplicate (not import) two of pipeline_utils.py's own threshold VALUES.
# No new landmark, sensor, or external input of any kind -- shoulder and
# hip are already read by every function in this module.
#
# THIS IS DIAGNOSTIC-ONLY, DELIBERATELY. Per this project's own no-
# speculative-blending standard (every other gate/threshold in this file
# was shipped only after real-footage evidence, not before): before this
# measurement is allowed to affect risk_score at all, it must first be
# shown to actually separate real fall clips from real brisk-walking
# clips on this project's own corpus -- see
# benchmarks/torso_angular_velocity_diagnostic.py, which runs this
# function against all 44 real clips and reports the raw distributions
# for both populations. Nothing in gait_risk.py reads this function's
# output; it is not part of `assess_risk()`'s signal contract.
def _batch_torso_angle(shoulder: np.ndarray, hip: np.ndarray) -> np.ndarray:
    """Vectorized torso-pitch angle (degrees from vertical) -- mirrors
    pipeline_utils.py's own `_compute_torso_angle` formula (independently
    re-derived, not imported -- see this section's own docstring above).
    0 degrees = shoulder directly above hip (upright); 90 degrees =
    shoulder level with hip (horizontal torso, e.g. lying/falling). Gated
    by the same per-point validity rule `_batch_hip_angle` uses (NaN-or-
    out-of-[-margin, 1+margin]-range -> invalid -> NaN angle for that
    frame)."""
    shoulder = shoulder.astype(np.float64, copy=False)
    hip = hip.astype(np.float64, copy=False)
    valid = _batch_landmark_valid(shoulder) & _batch_landmark_valid(hip)
    dx = shoulder[:, 0] - hip[:, 0]
    dy = shoulder[:, 1] - hip[:, 1]
    dist = np.sqrt(dx ** 2 + dy ** 2)
    valid &= dist > 1e-6
    safe_dist = np.where(dist > 1e-6, dist, 1.0)
    with np.errstate(invalid="ignore"):
        cosine = -dy / safe_dist
    cosine = np.clip(np.nan_to_num(cosine, nan=0.0), -1.0, 1.0)
    angles = np.degrees(np.arccos(cosine))
    return np.where(valid, angles, np.nan)


# Reused (not re-derived) from pipeline_utils.py's own already-shipped,
# already-validated heuristic fall detector -- its own `torso_angular_
# velocity` gates real fall detections at 150-250 deg/sec depending on the
# code path (`FALL_PRELYING_ANGVEL_FLOOR=250.0` is the stricter of the
# two; 150 is the looser floor used elsewhere in that same function,
# always combined with a multi-frame sustain requirement,
# `ANGVEL_SUSTAIN_FRAMES`). This module does not import that constant
# (pipeline_utils.py stays read-only from here, per this project's
# established boundary), but reuses the SAME real number as a reference
# point for this diagnostic's own sustain check, rather than inventing an
# independent one -- consistent with how `_HIP_ANGLE_SITTING_MAX`/
# `_HIP_ANGLE_STANDING_MIN` elsewhere in this file already duplicate two
# of that module's own threshold VALUES for the same reason.
_DIAGNOSTIC_SUSTAIN_ANGVEL_FLOOR = 150.0


def _batch_torso_angle_3d(shoulder: np.ndarray, hip: np.ndarray) -> np.ndarray:
    """3D generalization of `_batch_torso_angle`, for MediaPipe world
    landmarks (`pose_world_landmarks`, real-world-metric meters -- see
    WORLD_LANDMARKS_ROOT_CAUSE_FIX's own docstring elsewhere in this file
    for the established precedent this mirrors: 2D-projected TORSO LENGTH
    was found confounded by camera distance/bend, and a 3D version fixed
    it without inventing a new sensor input -- MediaPipe already computes
    pose_world_landmarks on every call). Confirmed directly on real footage
    (not assumed) before writing this: MediaPipe's world-landmark Y axis
    uses the SAME sign convention as the 2D image Y axis (more negative =
    higher up the body -- a real standing frame from Diagonal_Walk_1.mov
    measures shoulder Y around -0.47 to -0.48 against hip Y near 0), so
    `-dy/dist` (this function) and `-dy/dist` (`_batch_torso_angle`, 2D)
    mean the same thing: 0 degrees = shoulder directly above hip
    (upright); the only structural difference is `dist` here is the full
    3D (x, y, z) vector norm, not the 2D (x, y) one."""
    shoulder = shoulder.astype(np.float64, copy=False)
    hip = hip.astype(np.float64, copy=False)
    valid = ~(np.isnan(shoulder).any(axis=1) | np.isnan(hip).any(axis=1))
    diff = shoulder - hip
    dist = np.linalg.norm(diff, axis=1)
    valid &= dist > 1e-6
    safe_dist = np.where(dist > 1e-6, dist, 1.0)
    with np.errstate(invalid="ignore"):
        cosine = -diff[:, 1] / safe_dist
    cosine = np.clip(np.nan_to_num(cosine, nan=0.0), -1.0, 1.0)
    angles = np.degrees(np.arccos(cosine))
    return np.where(valid, angles, np.nan)


def compute_torso_angular_velocity_diagnostic(window: List[dict], _raw: Optional[np.ndarray] = None,
                                               _ts: Optional[np.ndarray] = None,
                                               _world_raw: Optional[np.ndarray] = None) -> Optional[Dict[str, Any]]:
    """DIAGNOSTIC ONLY -- see this file's "TORSO ANGULAR VELOCITY" section
    docstring immediately above. NOT called anywhere in assess_risk() or
    any other production path; a standalone measurement for
    benchmarks/torso_angular_velocity_diagnostic.py to log across real
    footage before any decision is made about using it.

    Returns None if fewer than one valid (both endpoints tracked, dt > 0)
    frame-pair exists in the window, otherwise:
        {"peak_deg_per_sec": float, "mean_deg_per_sec": float,
         "n_valid_pairs": int, "coverage": float}

    `peak_deg_per_sec`: the single largest frame-to-frame torso-angle
    change rate found in the window -- the quantity most likely to catch a
    brief, sharp postural collapse inside an otherwise-unremarkable
    window, mirroring `_peak_translation_speed`'s own "report the peak,
    not the mean" choice elsewhere in this file for the identical reason
    (an averaged rate would dilute a short, sharp event across the rest of
    a longer window).
    `mean_deg_per_sec`: reported alongside for comparison only -- this
    function makes no decisions and applies no threshold of any kind.
    `n_valid_pairs` / `coverage`: how many frame-pairs (and what fraction
    of the window) actually contributed, the same reliability-reporting
    convention used throughout this module's `_quality_out` mechanism --
    reported directly in the return dict here since this is not part of
    `assess_risk()`'s existing signal contract and has no `_quality_out`
    parameter of its own.

    Deliberately UNCAPPED and UNSMOOTHED (unlike pipeline_utils.py's own
    `torso_angular_velocity`, which applies a 720 deg/sec implausibility
    cap and a 3-frame rolling median) -- this is a first-pass diagnostic
    meant to show the RAW real distribution, including whatever noise
    exists, before any cleanup decision is made with real evidence rather
    than assumed in advance.

    `_world_raw`: internal/opt-in, mirrors compute_walking_speed's own
    parameter of the same name -- an already-computed
    _raw_world_keypoint_array(window). When supplied AND this window has
    sufficient 3D coverage (_has_sufficient_world_coverage), the angle is
    computed from 3D world landmarks (_batch_torso_angle_3d) instead of
    the 2D projection -- added to test whether the SAME 2D-projection
    confound already found and fixed for torso LENGTH (see
    WORLD_LANDMARKS_ROOT_CAUSE_FIX) also affects this angle measurement;
    see benchmarks/torso_angular_velocity_diagnostic.py for the real-
    footage comparison this was checked against. Adds a `"mode": "2d"|"3d"`
    key to the returned dict so a caller/analysis script can tell which
    was used. Leave as None (the default) for 2D-only behavior."""
    raw = _raw if _raw is not None else _raw_keypoint_array(window)
    ts = _ts if _ts is not None else _timestamps(window)
    use_3d = _world_raw is not None and _has_sufficient_world_coverage(_world_raw)
    if use_3d:
        world_pts = _world_raw.reshape(-1, 33, 3)
        sh_mid = (world_pts[:, LEFT_SHOULDER, :] + world_pts[:, RIGHT_SHOULDER, :]) / 2.0
        hip_mid = (world_pts[:, LEFT_HIP, :] + world_pts[:, RIGHT_HIP, :]) / 2.0
        angle = _batch_torso_angle_3d(sh_mid, hip_mid)
    else:
        pts = raw.reshape(-1, 33, 2)
        sh_mid = (pts[:, LEFT_SHOULDER, :] + pts[:, RIGHT_SHOULDER, :]) / 2.0
        hip_mid = (pts[:, LEFT_HIP, :] + pts[:, RIGHT_HIP, :]) / 2.0
        angle = _batch_torso_angle(sh_mid, hip_mid)

    valid = ~np.isnan(angle)
    pair_valid = valid[1:] & valid[:-1]
    dt = np.diff(ts)
    dt_positive = dt > 0
    mask = pair_valid & dt_positive
    if not mask.any():
        return None

    dtheta = np.abs(np.diff(angle))
    safe_dt = np.where(dt_positive, dt, 1.0)
    angvel = dtheta / safe_dt

    # Longest run of CONSECUTIVE valid frame-pairs at/above
    # _DIAGNOSTIC_SUSTAIN_ANGVEL_FLOOR (150 deg/sec) -- a single-frame
    # spike can be landmark jitter; a SUSTAINED elevated rate is the
    # signature pipeline_utils.py's own already-shipped, already-validated
    # heuristic fall detector actually uses (its `torso_angular_velocity`
    # is gated at 150-250 deg/sec depending on the code path, confirmed
    # via `ANGVEL_SUSTAIN_FRAMES` requiring multiple consecutive frames,
    # not a single one -- see this section's own module-level docstring).
    # 150 here is that SAME already-validated real number, reused (not
    # re-invented) as a reference point for this diagnostic; a run that
    # is NOT bridged across an invalid (masked-out) frame-pair, matching
    # `_confirmed_runs`' own established convention elsewhere in this file.
    above = (angvel >= _DIAGNOSTIC_SUSTAIN_ANGVEL_FLOOR) & mask
    max_run = 0
    current_run = 0
    for is_above in above:
        if is_above:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0

    return {
        "peak_deg_per_sec": float(np.max(angvel[mask])),
        "mean_deg_per_sec": float(np.mean(angvel[mask])),
        "n_valid_pairs": int(mask.sum()),
        "coverage": float(mask.sum()) / float(len(mask)),
        "max_consecutive_pairs_above_150": int(max_run),
        "mode": "3d" if use_3d else "2d",
    }


# Minimum peak prominence (see scipy.signal.find_peaks' `prominence` arg),
# as a fraction of the ankle-y signal's own peak-to-peak range within the
# window, before compute_stride_regularity trusts a local maximum as a real
# heel-strike-proxy peak rather than a minor wiggle riding on top of the
# real signal (or, prior to the _ambulation_check gate below existing,
# on top of pure noise). Deliberately SELF-SCALING (a fraction of this
# window's own observed range) rather than a fixed absolute value in
# torso-length units: this module has no real-footage-derived reference
# for genuine ankle-oscillation amplitude to calibrate an absolute number
# against (no walking footage exists in this project -- see
# MIN_HORIZONTAL_DOMINANCE_RATIO's docstring for the same gap), so a
# relative threshold is the more defensible choice available -- it can't be
# "the wrong scale" for a given video/frame-rate/camera-distance the way an
# invented absolute number could be, though it also can't reject a
# uniformly-noisy signal with no real peak taller than its noise (that
# case is what the ambulation gate below is for; this is a secondary,
# narrower defense against small spurious wiggles superimposed on an
# otherwise-genuine oscillation, not the primary fix for stationary/jitter
# false positives). 0.15 (a peak must stand out by at least 15% of the
# window's own total ankle-y excursion) is a conservative, round starting
# value pending real-footage calibration, not a clinically or empirically
# derived cut-point.
STRIDE_PEAK_PROMINENCE_FRACTION = 0.15

# Maximum ratio of (largest raw frame-to-frame dt spanned by a peak-to-peak
# interval) to (this window's own MEDIAN frame-to-frame dt) before
# _detect_gait_events excludes that interval from the CV/cadence
# calculation entirely, treating it as a DATA-COLLECTION discontinuity
# (dropped/uncaptured frames -- e.g. a live-streaming hiccup, see
# gait_stream.py) rather than a genuine (if unusually slow) stride.
#
# WHY THIS IS SAFE TO DERIVE STRUCTURALLY, NOT EMPIRICALLY (unlike most
# other constants in this module, which explicitly wait for real footage):
# frame-to-frame TIMESTAMP SPACING is a property of the CAPTURE SYSTEM
# (camera frame rate), not of the subject's movement -- unlike ankle
# POSITION, which genuinely varies with how the person is moving, the time
# between two consecutive captured frames should stay approximately
# constant for a healthy camera feed regardless of what the subject is
# doing. A frame-to-frame gap many times larger than the rest of the same
# window's own frame spacing is therefore virtually always a capture
# artifact, not a real slow movement -- this is a logical/structural
# argument about what dt physically represents, not a fitted or assumed
# behavioral cut-point, which is why it's safe to set now rather than
# deferred pending real footage (contrast with STRIDE_PEAK_PROMINENCE_
# FRACTION just above, which genuinely does need real walking footage to
# calibrate, since it bounds ankle AMPLITUDE -- a quantity that legitimately
# varies with the subject's gait).
#
# 5.0 (a frame-pair must be 5x this window's own median frame spacing to
# count as a gap) is chosen with wide margin above ordinary camera jitter
# (real MediaPipe/webcam capture frame-to-frame timing varies by a small
# fraction, not multiples, under normal conditions) while easily catching
# an actual multi-frame drop or streaming stall (a genuine dropped-frame
# gap is typically orders of magnitude larger than one frame interval, not
# marginally larger) -- confirmed by direct reproduction: a 5-second gap
# inserted into an otherwise-clean 30fps synthetic window measured ~165x
# the window's own median frame dt, comfortably clearing this margin, while
# every genuine frame-to-frame interval in a clean synthetic walking window
# measures ~1x by construction (no false rejection risk for normal data).
MAX_INTERVAL_GAP_RATIO = 5.0

# Minimum real TIME (seconds) between two detected gait-event peaks, before
# _detect_gait_events converts this into a frame-count `distance` for
# `scipy.signal.find_peaks` (which only accepts a sample count, not a
# duration) using THIS window's own median frame spacing -- the same
# median-dt computation MAX_INTERVAL_GAP_RATIO's gap guard already needs,
# reused rather than duplicated (see docs/GAIT_CODE_REVIEW.md's follow-up
# audit: previously a hardcoded `distance=5` frame-count, which silently
# assumed ~30fps capture. This project's OWN real footage is not uniformly
# 30fps -- the Hussain set is documented at a variable ~23-30fps
# (docs/GAIT_ANGLE_NOISE_INVESTIGATION_REPORT.md Section B) -- so a fixed
# frame-count distance let the effective minimum inter-step time floor drift
# with capture rate, unlike every other timing-sensitive threshold in this
# module (MAX_INTERVAL_GAP_RATIO, all `_timestamps`-based durations), which
# are already frame-rate-independent by design.
#
# 5.0 / 30.0 = 0.1667s is chosen to exactly REPRODUCE the old `distance=5`
# behavior at 30fps (the frame rate every one of this project's synthetic
# test fixtures uses, and the frame rate of most of its real footage) --
# this is a like-for-like conversion of the existing, already-validated
# assumption into explicit time units, not a new or re-tuned threshold. At a
# lower real capture rate (e.g. Hussain's ~23fps), this now correctly
# resolves to a SMALLER frame-count distance (~4 frames, not 5) so the same
# real-world ~0.167s minimum step separation is enforced regardless of fps,
# rather than silently loosening to ~0.217s purely because the camera
# captured fewer frames per second.
MIN_STEP_INTERVAL_SEC = 5.0 / 30.0


def _detect_gait_events(ankle_y_filled: np.ndarray, ts: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Shared gait-event detector: finds ankle-height oscillation peaks
    (heel-strike/swing-apex proxy -- see compute_stride_regularity's
    docstring) in an already-NaN-filled ankle-Y signal, and returns
    `(peak_indices, intervals)`:
      - `peak_indices`: int array indices into `ankle_y_filled`/`ts` where a
        detected gait event occurred (same `find_peaks(distance=..., prominence=...)`
        call compute_stride_regularity always used inline -- `distance` is a
        time-based minimum, in frame-count units derived from this window's
        own median dt; see MIN_STEP_INTERVAL_SEC's own docstring).
      - `intervals`: `np.diff(ts[peak_indices])`, already filtered to
        strictly-positive entries (a tied/duplicate timestamp between two
        adjacent peaks would produce a zero or negative "interval," which
        is not a real duration -- same filter the pre-extraction inline
        code already applied).

    NAMING, DELIBERATE (see docs/GAIT_CODE_REVIEW.md's gait-event audit):
    called "gait EVENTS," not "gait CYCLES" or "strides" -- `ankle_y` is
    `(LEFT_ANKLE_y + RIGHT_ANKLE_y) / 2`, both feet averaged together, so
    each detected peak is empirically ONE FOOT's swing-phase excursion (a
    STEP-scale event), not a full two-legged gait cycle (a STRIDE).
    Verified directly, not assumed: against this module's own synthetic
    walking generator (tests/test_gait_risk.py::_walking_window, whose
    internal stride period is a known parameter), detected peak-to-peak
    intervals measured almost exactly HALF that known period -- i.e. two
    peaks per stride, the expected signature of an alternating two-legged
    gait. See compute_stride_regularity's `_quality_out` docstring for how
    this affects (and doesn't affect) that function's own CV and cadence
    outputs.

    Factored out of compute_stride_regularity's body as a reusable
    representation (not a behavior change -- verified byte-identical output
    for every existing test) so a second consumer can reuse the identical
    detection instead of re-running find_peaks independently and risking
    the two silently drifting apart. Currently used by compute_stride_
    regularity (CV) and its own cadence calculation (see that function's
    `_quality_out["cadence_steps_per_min"]`) -- not exposed outside this
    module; this is an internal-reuse extraction, not new public API
    surface, since nothing outside gait_features.py currently needs raw
    event boundaries.

    TIMESTAMP-GAP GUARD (see MAX_INTERVAL_GAP_RATIO's own docstring):
    `peak_indices` itself is untouched -- a detected peak remains a real
    observation regardless of what happens around it -- but an interval is
    EXCLUDED if the raw frame-to-frame timestamps it spans contain a gap
    many times larger than this window's own typical (median) frame
    spacing. Confirmed real failure mode this closes: a batch of dropped/
    uncaptured frames during live streaming (see gait_stream.py) previously
    produced ONE artificially huge peak-to-peak interval that dominated
    compute_stride_regularity's CV (reproduced directly: a single 5-second
    gap inserted into an otherwise clean, perfectly-regular synthetic
    walking window inflated the reported CV from ~0.026 to ~1.46 -- a data-
    collection artifact misread as extreme stride irregularity, exactly the
    "poor measurement quality" vs. "genuinely abnormal gait" confusion this
    module's reliability mechanism otherwise exists to keep separate). This
    guard does NOT reject genuinely slow individual strides -- only
    intervals whose underlying FRAME timing itself (not the person's
    movement) was anomalous.

    TIME-BASED PEAK DISTANCE (see MIN_STEP_INTERVAL_SEC's own docstring):
    `find_peaks`'s `distance` argument only accepts a sample (frame) count,
    not a duration -- this window's own median frame spacing (`median_dt`,
    the SAME quantity the timestamp-gap guard above already needs) is used
    to convert MIN_STEP_INTERVAL_SEC into the equivalent frame count for
    THIS window's actual capture rate, computed once and shared by both
    this conversion and the gap guard below (no duplicate work, no new
    loop -- `np.median` was already being called here). At 30fps (every
    synthetic test fixture in this module, and most of this project's real
    footage) this resolves to exactly 5, byte-identical to the old hardcoded
    value; at a lower real capture rate it resolves smaller, keeping the
    real-world minimum step separation constant instead of drifting with fps.
    """
    frame_dt = np.diff(ts)
    positive_frame_dt = frame_dt[frame_dt > 0]
    median_dt = float(np.median(positive_frame_dt)) if positive_frame_dt.size > 0 else None
    distance_frames = max(1, int(round(MIN_STEP_INTERVAL_SEC / median_dt))) if median_dt else 5

    signal_range = float(np.ptp(ankle_y_filled))
    min_prominence = max(signal_range * STRIDE_PEAK_PROMINENCE_FRACTION, 1e-6)
    peaks, _ = find_peaks(ankle_y_filled, distance=distance_frames, prominence=min_prominence)
    if len(peaks) < 2:
        return peaks, np.array([], dtype=np.float64)

    peak_times = ts[peaks]
    raw_intervals = np.diff(peak_times)
    keep = raw_intervals > 0

    if median_dt:
        gap_threshold = MAX_INTERVAL_GAP_RATIO * median_dt
        for i in range(len(peaks) - 1):
            span_dt = frame_dt[peaks[i]:peaks[i + 1]]
            if span_dt.size > 0 and float(np.max(span_dt)) > gap_threshold:
                keep[i] = False

    return peaks, raw_intervals[keep]


def compute_stride_regularity(window: List[dict], _raw: Optional[np.ndarray] = None,
                               _hip_track: Optional[np.ndarray] = None,
                               _ts: Optional[np.ndarray] = None,
                               _quality_out: Optional[Dict[str, Any]] = None,
                               _torso_baseline: Optional[float] = None,
                               _world_raw: Optional[np.ndarray] = None) -> Optional[float]:
    """
    Coefficient of variation (std/mean) of stride-to-stride interval,
    estimated from the periodicity of ankle vertical oscillation
    (heel-strike proxy). Higher CV = less regular stride timing, which the
    reviewed literature associates with elevated fall risk (reported as
    potentially more sensitive than gait speed alone).

    This is a video-derived SPATIAL oscillation period, not an IMU-derived
    stride TIME the way most of the cited literature measures it -- treat
    as a rough proxy for the same underlying idea (step-to-step timing
    consistency), not an equivalent measurement.

    TERMINOLOGY NOTE (see _detect_gait_events' docstring for the full
    derivation): "stride-to-stride interval" above is this function's own
    established name for the underlying peak-to-peak interval, kept as-is
    here since it is used pervasively across this module's docstrings,
    tests, and gait_risk.py's `_SIGNAL_SPECS` table -- but the detected
    peaks are, empirically, STEP-scale events (one per foot's swing, since
    `ankle_y` averages both ankles together), not full two-legged gait
    cycles. This does not change what the CV measures or its validity as a
    step-to-step regularity proxy (irregular STEP timing is itself a
    legitimate, literature-relevant signal -- arguably more sensitive than
    stride-only timing, since it can also reflect a left/right timing
    asymmetry that a stride-only measure would average away) -- it only
    means "stride" here is a proxy label, not a literal claim, exactly the
    same caveat already applied to `walking_speed`'s torso-lengths/sec.
    This function's own newly-added `_quality_out["cadence_steps_per_min"]`
    below is named accurately for the same underlying events.

    Returns None if fewer than 3 ankle peaks (after prominence filtering --
    see STRIDE_PEAK_PROMINENCE_FRACTION) are detected (need at least 2 full
    strides to compute a variability statistic that means anything).

    AMBULATION GATE (added -- see docs/GAIT_CODE_REVIEW.md finding #1):
    also returns None unless the window's hip track passes the exact same
    `_ambulation_check` gate compute_walking_speed uses (path length,
    plausibility, directional coherence, and horizontal dominance -- see
    that function's docstring and each constant's own docstring). Before
    this gate existed, this function had NO stationarity check at all
    (unlike compute_walking_speed and compute_postural_sway, which both
    have one) -- an ordinary stationary subject's ankle jitter (weight-
    shifting, MediaPipe frame-to-frame noise) could produce >=3 spurious
    local maxima more than `distance=5` frames apart and fabricate a CV
    value that then entered risk_score at weight 1.2, the HIGHEST of the
    four signals. Real strides only happen while the person is actually
    walking, so requiring the same hip-translation evidence
    compute_walking_speed already requires is the direct fix: it reuses
    the hip-track/validity work already computed elsewhere in the same
    assess_risk() call (via `_hip_track`) rather than inventing a
    separate, independently-tuned ankle-specific stationarity check.

    `_hip_track`: internal -- an already-computed _torso_scaled_hip_track(),
    shared the same way `_raw`/`_ts` are (see compute_walking_speed's
    docstring for why this sharing matters). Leave as None to compute it
    standalone from `_raw`/`window` -- this parameter doesn't change any
    result, only whether the work is shared.

    `_ts`: internal -- an already-computed _timestamps(window), shared the
    same way `_raw` is (see _timestamps' own docstring).

    `_torso_baseline`/`_world_raw`: OPTIONAL, opt-in -- see compute_walking_
    speed's own docstring for the full contract; wired in here for the same
    reason, sharing the exact same gate rather than inventing a second one.
    This function's ambulation gate (above) runs `_ambulation_check` on the
    SAME 2D `_torso_scaled_hip_track` compute_walking_speed uses, so it is
    exposed to the identical torso-length-collapse degeneracy a sustained
    bend causes (see MIN_TORSO_BASELINE_RATIO's docstring and
    docs/GAIT_DATA_ASSESSMENT.md Section 9) -- and, empirically, not just in
    principle: a collapsed torso length doesn't only inflate the HIP track,
    it also inflates whatever ANKLE-position noise `_normalized_positions`
    divides by that same collapsing per-frame torso length, so ordinary
    tracking jitter on an otherwise-motionless, sustained-bent subject can
    clear both the ambulation gate above AND STRIDE_PEAK_PROMINENCE_FRACTION
    (the window's own noise floor becomes the window's own dominant
    "oscillation" once the denominator is small enough), fabricating a
    non-trivial CV with a physically-implausible cadence. Confirmed both
    ways: on real footage (Deep_Bend_2.mov, ~100% landmark confidence,
    production extraction path) at CV up to 0.429 (n_events=4-6) at multiple
    windows squarely inside its GT-confirmed "Deep bend sustained (NOT
    sitting)" span, and reproduced with a synthetic fixture (a fully-bent,
    near-motionless hip with only realistic per-frame ankle jitter, no
    walking) at CV=0.286, reliability=1.0, cadence=244 steps/min -- itself
    an implausible cadence for a real gait, though this gate targets the
    root cause (the collapsed-scale amplification), not cadence
    plausibility specifically. This CV was previously unconditionally
    included in `risk_score` at weight 1.2 -- the HIGHEST of the four
    signals -- exactly the failure class docs/GAIT_CODE_REVIEW.md finding
    #1 already fixed for stationary-subject ankle jitter WITHOUT a torso
    collapse; this closes the same class of bug for the torso-collapse
    case specifically, which finding #1's plain `_ambulation_check` gate
    (present since that fix) does not by itself prevent, since the hip
    track it checks is exactly what's degenerate here.

    Same worst-single-frame (not median) aggregation as compute_walking_
    speed's own gate, for the identical reason given there: this gate only
    ever runs on windows that already cleared `_ambulation_check` (i.e.
    already show apparent hip translation), so genuine sitting/standing-
    still windows -- where a worst-frame check would be too aggressive, see
    MIN_TORSO_BASELINE_RATIO_3D's docstring -- never reach it at all. Since
    this reuses the exact same `_ambulation_check` output, threshold
    constants, and aggregation convention compute_walking_speed's already-
    corpus-validated gate uses (rather than an independently re-tuned one),
    any window this rejects is a window compute_walking_speed's own gate
    would also reject for the same reason. Leave both as None (the default
    -- every existing caller) to preserve today's exact behavior.

    `_quality_out`: internal, OPTIONAL -- if a dict is passed, this
    function fills it in (as a side effect, WITHOUT changing its own float
    return type) with additional signal-quality/reliability information
    ONLY when it is about to return a real (non-None) value:
      - `"reliability"`: fraction of this window's frames that had valid
        RAW ankle tracking (the same `raw_ankle_valid` fraction already
        computed for this function's own early-exit gate, in [0, 1]) --
        how much real landmark data actually supported this CV estimate,
        as distinct from WHETHER the estimate looks regular or irregular.
        See GaitRiskAssessor's module docstring (docs/GAIT_CODE_REVIEW.md
        follow-up) for why this is reported as metadata rather than folded
        into risk_score: doing the latter would change this module's
        existing risk-score contract, which is out of scope here.
      - `"cadence_steps_per_min"`: `60 / mean(intervals)` -- the detected
        STEP rate (see this function's own "TERMINOLOGY NOTE" above and
        _detect_gait_events' docstring for why "steps," not "strides," is
        the verified-correct unit here). A video-derived peak-detection
        rate, NOT a clinically validated measurement -- same proxy caveat
        as `compute_walking_speed`'s torso-lengths/sec -- but "steps per
        minute" IS the standard clinical definition of gait cadence, so
        this field's naming/units match established terminology exactly,
        not just this module's own internal convention. Directly
        interpretable and essentially free once gait events are already
        detected for the CV -- added because it needs no new data or
        gates beyond what this function already computes.
      - `"n_events"`: number of detected step-scale events used, int -- how
        many the CV/cadence above were actually estimated from (useful
        context: a CV from 3 detected events is less to be trusted than
        one from 15).
    Left untouched (not set) on any early-exit path -- mirrors `value`'s
    own None-when-unavailable convention: reliability of a value that
    doesn't exist is not a meaningful concept.
    """
    if not _HAS_SCIPY:
        return None

    raw = _raw if _raw is not None else _raw_keypoint_array(window)
    ts = _ts if _ts is not None else _timestamps(window)

    # Cheap, PROVABLY-SAFE early exit before the more expensive
    # normalization + find_peaks pass below: a frame's normalized ankle_y
    # is NaN if EITHER the raw ankle itself is NaN OR normalization
    # invalidated the whole frame (bad hip/shoulder) -- so the count of
    # frames with a valid RAW ankle-y is always >= the count with a valid
    # NORMALIZED ankle-y. If the raw count already can't clear the 50%
    # threshold below, the normalized count provably can't either, so
    # there's no need to run normalization or find_peaks at all to know
    # this window will return None. This changes nothing about the
    # returned value -- only whether the work to compute it happens.
    raw_pts = raw.reshape(-1, 33, 2)
    raw_ankle_valid = ~(np.isnan(raw_pts[:, LEFT_ANKLE, 1]) | np.isnan(raw_pts[:, RIGHT_ANKLE, 1]))
    if raw_ankle_valid.sum() < len(window) * 0.5:
        return None

    # Ambulation gate -- next-cheapest check (reuses the already-parsed
    # `raw` array; _torso_scaled_hip_track only does an O(T) reshape/smooth
    # pass, no re-parsing of the window's rows) -- before the most expensive
    # step (normalization + find_peaks) below. See this function's own
    # docstring and _ambulation_check's docstring.
    hip_center = _hip_track if _hip_track is not None else _torso_scaled_hip_track(window, _raw=raw)
    ambulation_mask, _ = _ambulation_check(hip_center, ts)
    if ambulation_mask is None:
        return None

    # Torso-baseline collapse gate -- see this function's own docstring for
    # why this signal needs the SAME gate compute_walking_speed's ambulation
    # gate already has (identical hip_center degeneracy), placed here
    # (cheapest-first, before normalization/find_peaks) exactly like
    # compute_walking_speed's own placement immediately after its ambulation
    # gate. Byte-identical worst-single-frame/threshold logic to that
    # function's block -- kept as its own inline copy rather than a shared
    # helper, matching this module's existing convention (compute_walking_
    # speed and compute_postural_sway each inline their own copy too).
    if _torso_baseline is not None and _torso_baseline > 1e-6:
        use_3d = _world_raw is not None and _has_sufficient_world_coverage(_world_raw)
        if use_3d:
            torso_len_for_gate = _raw_torso_len_3d(_world_raw)
            threshold = MIN_TORSO_BASELINE_RATIO_3D
        else:
            torso_len_for_gate = _raw_torso_len(window, _raw=raw)
            threshold = MIN_TORSO_BASELINE_RATIO
        valid_torso_len = torso_len_for_gate[np.isfinite(torso_len_for_gate)]
        ratio = float(np.min(valid_torso_len)) / _torso_baseline if valid_torso_len.size else None
        if ratio is None or ratio < threshold:
            return None

    pos = _normalized_positions(window, _raw=raw)
    ankle_y = (pos[:, LEFT_ANKLE, 1] + pos[:, RIGHT_ANKLE, 1]) / 2.0

    valid = ~np.isnan(ankle_y)
    if valid.sum() < len(window) * 0.5:
        return None  # too much missing ankle tracking to trust peak detection

    # Interpolate short NaN gaps so find_peaks sees a continuous signal;
    # leave as-is (find_peaks will just see fewer candidate points) if the
    # whole series is unusable.
    idx = np.arange(len(ankle_y))
    if valid.sum() >= 2:
        ankle_y_filled = np.interp(idx, idx[valid], ankle_y[valid])
    else:
        return None

    peaks, intervals = _detect_gait_events(ankle_y_filled, ts)
    if len(peaks) < 3:
        return None
    if len(intervals) < 2:
        return None

    mean_interval = float(np.mean(intervals))
    if mean_interval < 1e-6:
        return None
    cv = float(np.std(intervals) / mean_interval)

    if _quality_out is not None:
        _quality_out["reliability"] = float(raw_ankle_valid.mean())
        _quality_out["cadence_steps_per_min"] = float(60.0 / mean_interval)
        _quality_out["n_events"] = int(len(peaks))

    return cv


def compute_postural_sway(window: List[dict], stable_subwindow: int = 15, displacement_thresh: float = 0.15,
                           _hip_track: Optional[np.ndarray] = None, _ts: Optional[np.ndarray] = None,
                           _quality_out: Optional[Dict[str, Any]] = None,
                           _raw: Optional[np.ndarray] = None,
                           _torso_baseline: Optional[float] = None,
                           _world_raw: Optional[np.ndarray] = None) -> Optional[float]:
    """
    Standard deviation of hip-center position (torso-lengths) during
    sub-windows where the person is NOT substantially translating --
    i.e. an approximation of "postural sway while standing/sitting still",
    the trunk-stability signal the reviewed wearable-sensor literature
    flags as one of the most relevant kinematic fall-risk indicators.

    Sub-windows are `stable_subwindow` frames long; a sub-window counts as
    "stable" if BOTH (a) the hip center's net (first-to-last) displacement
    stays low (i.e. it isn't a walking bout), AND (b) no consecutive-frame
    pair inside the sub-window exceeds MAX_PLAUSIBLE_HIP_SPEED. (b) exists
    because (a) alone is blind to a tracking glitch that spikes mid-segment
    and returns to baseline by the sub-window's last frame -- net_disp stays
    exactly 0 regardless of how large that interior spike is (reproduced
    directly: a single glitched frame placed mid-segment leaves net_disp
    unchanged at 0.0 while the reported sway scales linearly and unboundedly
    with the glitch's magnitude), so an artifact could otherwise dominate
    this segment's std() while sailing through the net-displacement check
    untouched. Same constant and reasoning as compute_walking_speed's own
    plausibility gate -- an artifact-inflated sway would misread as
    confidently HIGH risk (the mirror image of compute_walking_speed's
    "confidently LOW risk" failure mode, since _sway_risk maps higher sway
    to higher risk) at the exact moment the reading is least trustworthy.
    Returns the mean sway across all stable sub-windows found, or None if
    none qualify (e.g. the person is walking/moving for the entire input
    window, or every otherwise-stable sub-window contains a glitch).

    TILING IS NON-OVERLAPPING AND PHASE-LOCKED TO THIS WINDOW'S OWN INDEX 0
    (see docs/GAIT_CODE_REVIEW.md finding #9) -- a documented, ACCEPTED
    approximation. Re-verified (not merely re-accepted) against this
    project's actual real call sites, with computed numbers, not just the
    prior claim's word:
      1. TRAILING-FRAME DROP: `range(0, n - stable_subwindow + 1,
         stable_subwindow)` only ever visits FULL stable_subwindow-length
         tiles -- any trailing `n % stable_subwindow` frames past the last
         full tile are silently excluded from consideration entirely (up to
         `stable_subwindow - 1` = 14 frames for the default). Both window
         lengths this module is actually ever called with --
         gait_features.MIN_WINDOW_FRAMES=90 (used by every current
         benchmark script's WINDOW_FRAMES) and gait_stream's own
         constructor default window_frames=150 (the intended live-streaming
         default, not currently overridden by any caller in this repo) --
         are EXACT multiples of the default `stable_subwindow=15`: computed
         directly, `range(0, 90-15+1, 15)` and `range(0, 150-15+1, 15)`
         cover 90/90 and 150/150 frames respectively -- 0 frames dropped at
         either length, not merely "few." Only matters for a window length
         that ISN'T a multiple of `stable_subwindow`, which no current
         caller passes.
      2. PHASE SENSITIVITY ACROSS SLIDING WINDOWS: tile boundaries are
         anchored to THIS CALL's window start (local index 0), not to any
         absolute/wall-clock frame index -- in principle, the same real
         15-frame span of quiet standing could fall inside different tile
         boundaries across consecutive re-assessments purely because the
         window's start index shifted. Simulated directly (not assumed):
         with gait_stream.py's own actual default cadence
         (`reassess_every_n_frames=15`, StreamingGaitRiskAssessor's own
         constructor default -- every current benchmark script's
         REASSESS_EVERY_N also uses 15), each re-assessment's window start
         advances by EXACTLY 15 real frames -- the same as
         `stable_subwindow` -- so every re-assessment's tile boundaries
         land on the SAME absolute-frame residue class mod 15 (simulated
         over 191 re-assessments across 3000 frames: exactly 1 distinct
         residue, not several). Phase sensitivity is therefore ALSO
         structurally absent given this module's actual current defaults --
         NOT because the underlying mechanism doesn't exist (it does, and
         is real for any `reassess_every_n_frames` that is NOT a multiple
         of `stable_subwindow`, e.g. an odd cadence a future caller might
         choose), but because every current real call site's parameters
         happen to avoid it entirely.
    Neither is redesigned (e.g. into an overlapping or absolute-clock-
    anchored tiling) without repo evidence that it's actually degrading the
    signal for real usage -- see test_window_length_not_divisible_drops_
    trailing_frames in tests/test_gait_risk.py for a regression test that
    locks in (rather than accidentally changes) the trailing-drop behavior
    for a window length where it DOES apply.

    `_hip_track`: internal -- see compute_walking_speed's docstring for why
    this exists (letting assess_risk() share one _torso_scaled_hip_track()
    computation between this function and compute_walking_speed instead of
    each independently re-parsing+smoothing the same window).

    `_ts`: internal -- an already-computed _timestamps(window), shared the
    same way (see _timestamps' own docstring).

    `_quality_out`: internal, OPTIONAL -- if a dict is passed, this
    function fills in `"reliability"` as a side effect, ONLY when returning
    a real value: the fraction of ATTEMPTED tiles (`len(range(0, n -
    stable_subwindow + 1, stable_subwindow))`) that actually qualified as
    "stable" and contributed to the mean, in [0, 1]. Distinct in KIND from
    compute_walking_speed's/compute_stride_regularity's reliability (which
    are per-FRAME landmark-coverage fractions) -- this one is a per-TILE
    temporal-coverage fraction, the more meaningful "how much of this
    window's data was usable" question for a tiled signal. See
    compute_stride_regularity's `_quality_out` docstring for the shared
    reliability concept and why it's reported as metadata rather than
    folded into risk_score.

    `_raw`: internal -- an already-computed _raw_keypoint_array(window),
    shared the same way compute_walking_speed's own `_raw` is. Only
    actually used when `_torso_baseline` is also supplied.

    `_torso_baseline`/`_world_raw`: internal/opt-in, 3D-MODE ONLY -- see
    WORLD_LANDMARKS_ROOT_CAUSE_FIX's and MIN_TORSO_BASELINE_RATIO_3D's
    docstrings. Does NOT change `hip_center`'s own scale factor (stays
    2D-only, see _torso_scaled_hip_track's docstring for why). ONLY affects
    the availability gate, which -- unlike compute_walking_speed's -- ONLY
    ever activates when `_world_raw` is supplied AND this window has
    sufficient 3D coverage: `_torso_baseline` supplied WITHOUT usable
    `_world_raw` data is a no-op here (see MIN_TORSO_BASELINE_RATIO's own
    "2D-MODE / 3D-MODE" docstring for why the 2D version of this gate is
    deliberately NOT applied to postural_sway -- genuine seated sway
    collapses 2D torso_len even more than a bend does). `_torso_baseline`
    MUST have been computed by compute_torso_baseline() with `_world_raw`
    supplied just as consistently, or this compares mismatched units.
    """
    need_raw = _torso_baseline is not None or _world_raw is not None
    raw = _raw if _raw is not None else (_raw_keypoint_array(window) if need_raw else None)
    hip_center = _hip_track if _hip_track is not None else _torso_scaled_hip_track(window, _raw=raw)
    ts = _ts if _ts is not None else _timestamps(window)
    valid = ~np.isnan(hip_center).any(axis=1)

    if _torso_baseline is not None and _torso_baseline > 1e-6 and _world_raw is not None \
            and _has_sufficient_world_coverage(_world_raw):
        # MEDIAN, not worst-single-frame -- see MIN_TORSO_BASELINE_RATIO_3D's
        # own docstring and compute_walking_speed's matching comment: a
        # min()-based check here wrongly suppressed real seated-sway windows
        # on Sit_Stand_1.mov/Sit_Stand_2.mov/SitFloor_lowKeypoints.MOV (real
        # single-frame 3D-ratio dips to 0.45-0.61 during otherwise-genuine
        # sitting), caught by full-corpus validation before shipping.
        torso_len_3d = _raw_torso_len_3d(_world_raw)
        valid_torso_3d = torso_len_3d[np.isfinite(torso_len_3d)]
        if valid_torso_3d.size == 0 or float(np.median(valid_torso_3d)) / _torso_baseline < MIN_TORSO_BASELINE_RATIO_3D:
            return None

    sways = []
    n = len(window)
    tile_starts = range(0, n - stable_subwindow + 1, stable_subwindow)
    n_tiles_attempted = 0
    for start in tile_starts:
        n_tiles_attempted += 1
        seg = hip_center[start:start + stable_subwindow]
        seg_valid = valid[start:start + stable_subwindow]
        if seg_valid.sum() < stable_subwindow * 0.7:
            continue
        seg_ts = ts[start:start + stable_subwindow][seg_valid]
        seg = seg[seg_valid]
        net_disp = float(np.linalg.norm(seg[-1] - seg[0]))
        if net_disp > displacement_thresh:
            continue  # this sub-window is a walking/translating bout, not quiet standing

        if len(seg) >= 2:
            seg_dt = np.diff(seg_ts)
            seg_disp = np.linalg.norm(np.diff(seg, axis=0), axis=1)
            dt_positive = seg_dt > 0
            seg_speed = np.where(dt_positive, seg_disp / np.where(dt_positive, seg_dt, 1.0), 0.0)
            if np.any(seg_speed > MAX_PLAUSIBLE_HIP_SPEED):
                continue  # an implausible interior jump, not genuine postural sway

        sways.append(float(np.std(np.linalg.norm(seg - seg.mean(axis=0), axis=1))))

    if not sways:
        return None

    if _quality_out is not None and n_tiles_attempted > 0:
        _quality_out["reliability"] = float(len(sways)) / float(n_tiles_attempted)

    return float(np.mean(sways))


def _batch_landmark_valid(pts: np.ndarray, margin: float = 0.1) -> np.ndarray:
    """Vectorized equivalent of pipeline_utils.is_landmark_valid, applied to
    every row of an (T, 2) point array in one pass instead of once per
    frame. Same rule: NaN in either coordinate -> invalid; otherwise valid
    only within [-margin, 1+margin] on both axes (matches
    is_landmark_valid's own image-frame-plus-margin check, including that
    it does NOT separately reject Inf -- Inf/-Inf already fail the range
    check the same way is_landmark_valid's does)."""
    not_nan = ~np.isnan(pts).any(axis=1)
    in_range = (
        (pts[:, 0] >= -margin) & (pts[:, 0] <= 1.0 + margin)
        & (pts[:, 1] >= -margin) & (pts[:, 1] <= 1.0 + margin)
    )
    return not_nan & in_range


def _batch_hip_angle(shoulder: np.ndarray, hip: np.ndarray, knee: np.ndarray) -> np.ndarray:
    """Vectorized angle-at-the-hip computation (shoulder -> hip -> knee),
    applied to every frame of (T, 2) shoulder/hip/knee arrays in one pass.
    Same underlying trigonometry as pipeline_utils._compute_hip_angle, but
    NOT a byte-for-byte/behaviorally-exact port of it -- see
    docs/GAIT_CODE_REVIEW.md finding #5 -- gated by an ADDITIONAL
    per-point validity rule (_batch_landmark_valid: NaN-or-out-of-
    [-margin, 1+margin]-range -> invalid) that pipeline_utils._compute_hip_angle
    itself does NOT apply (that function only rejects None/NaN on its three
    points; it has no range check at all, so it will compute and return an
    angle from a non-NaN but wildly out-of-frame-range point -- e.g. a
    MediaPipe extrapolation artifact -- where this function instead treats
    that same point as invalid and returns NaN for the frame). This is a
    deliberate STRENGTHENING added on top of _compute_hip_angle's math, not
    an equivalence claim: for any point within [-margin, 1+margin], the two
    produce numerically identical angles (same three-point trigonometry);
    outside that range they can disagree by design, and this function's
    behavior (reject) is the more defensible of the two for this module's
    purposes.

    This -- plus the same batching applied on the other (left/right) side
    -- replaces what used to be a per-frame Python loop calling
    is_landmark_valid()/_compute_hip_angle() up to 6 times per frame
    (3 points x 2 checks). Profiling showed that loop alone was ~53% of a
    full assess_risk() call (see compute_sit_to_stand's docstring); the
    arithmetic itself has no cross-frame dependency, so it batches over T
    with no behavior change relative to what THIS module's own prior
    per-frame loop did (which already applied is_landmark_valid the same
    way _batch_landmark_valid does here) -- returns NaN for exactly the
    frames that per-frame loop would have."""
    shoulder = shoulder.astype(np.float64, copy=False)
    hip = hip.astype(np.float64, copy=False)
    knee = knee.astype(np.float64, copy=False)

    valid = _batch_landmark_valid(shoulder) & _batch_landmark_valid(hip) & _batch_landmark_valid(knee)

    v1 = shoulder - hip
    v2 = knee - hip
    n1 = np.linalg.norm(v1, axis=1)
    n2 = np.linalg.norm(v2, axis=1)
    valid &= (n1 > 1e-6) & (n2 > 1e-6)

    denom = n1 * n2
    with np.errstate(invalid="ignore", divide="ignore"):
        cos_theta = np.sum(v1 * v2, axis=1) / denom
    # Rows where denom is ~0 (already excluded from `valid`) produce inf/nan
    # here -- sanitize before clip/arccos purely to avoid a RuntimeWarning;
    # `valid` is what actually decides the returned value below.
    cos_theta = np.nan_to_num(cos_theta, nan=0.0, posinf=0.0, neginf=0.0)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    angles = np.degrees(np.arccos(cos_theta))
    return np.where(valid, angles, np.nan)


def _count_reversals(segment: np.ndarray, confident: Optional[np.ndarray] = None) -> float:
    """Number of local direction reversals in a hip_angle segment's
    frame-to-frame delta -- shared by compute_sit_to_stand's primary and
    fallback (_detect_fast_shallow_transition) paths so the "shakiness"
    metric means the same thing regardless of which path found the
    transition.

    `confident`: optional boolean mask, same length as `segment` -- True
    where that frame's hip_angle was averaged from BOTH left and right
    sides (compute_sit_to_stand's n_valid == 2), the pipeline's normal and
    most reliable case. A delta between segment[i] and segment[i+1] only
    participates in reversal-counting if BOTH of those frames were fully
    confident. Found via real-footage tracing (Sitting_Lying_FewLandmarks.MOV):
    when only ONE side is visible for a stretch of frames (the other side's
    shoulder or knee -- not necessarily the hip itself -- drops below
    landmark-visibility confidence), the single-side angle estimate has no
    second measurement averaging its noise down, and can drift by under a
    degree per frame while still flipping sign almost every frame -- 21
    consecutive single-sided frames measured 13 raw sign changes despite
    every individual delta staying under 1.3 degrees (versus a genuine
    transition's deltas, which ran 0.6-3.4 degrees while BOTH sides stayed
    valid the entire time -- see FALLBACK_MAX_TRANSLATION_SPEED's docstring
    for the same clip's translation measurement). A magnitude threshold
    alone can't safely separate these: the genuine "shaky" synthetic
    transition this module is validated against has an intentional
    real-scale reversal of only 0.6 degrees too, in a small-but-genuine
    fraction of its deltas -- overlapping the noise-floor case's range.
    Landmark confidence, not delta magnitude, is what actually explains the
    difference (see docs/GAIT_DATA_ASSESSMENT.md for related landmark-
    confidence caveats elsewhere in this project). Omitted (None) preserves
    this function's original behavior for any caller that doesn't have
    per-frame confidence available.

    ZERO-DELTA BRIDGING FIX (see docs/GAIT_CODE_REVIEW.md's follow-up
    audit): a delta of EXACTLY zero (two consecutive identical hip-angle
    readings -- plausible given MediaPipe's own temporal smoothing, which
    can genuinely repeat a value frame-to-frame) used to make this function
    skip BOTH comparisons touching it, which silently dropped a genuine
    reversal whenever it happened to be bridged by one such flat frame (e.g.
    deltas [+1, 0, -1] previously counted 0 reversals instead of the real
    1). Fixed by tracking the sign of the last NON-ZERO delta seen and
    comparing each new non-zero delta's sign against that, so a zero delta
    is skipped for comparison purposes without breaking the chain across it
    -- strictly a superset of the old behavior for any segment with no exact
    zero deltas (verified: for an all-nonzero-delta sequence this produces
    byte-identical counts to the old adjacent-pair comparison, since "last
    non-zero delta" and "previous delta" are the same thing when there are
    no zeros to bridge). See test_reversal_bridges_across_exact_zero_delta
    in tests/test_gait_risk.py for the regression test.
    """
    deltas = np.diff(segment)
    valid_mask = ~np.isnan(deltas)
    if confident is not None:
        # A delta spanning segment[i]->segment[i+1] is only trustworthy if
        # BOTH endpoints were fully (both-sides) confident.
        valid_mask = valid_mask & confident[:-1] & confident[1:]
    deltas = deltas[valid_mask]
    reversal_count = 0
    last_sign = 0
    for d in deltas:
        if d == 0:
            continue
        sign = 1 if d > 0 else -1
        if last_sign != 0 and sign != last_sign:
            reversal_count += 1
        last_sign = sign
    return float(reversal_count)


def _peak_translation_speed(hip_mid_raw: Optional[np.ndarray], torso_len_raw: Optional[np.ndarray],
                             ts: np.ndarray, ref_start: int, ref_end: int, seg_start: int, seg_end: int) -> float:
    """Peak frame-to-frame hip TRANSLATIONAL speed (torso-lengths/sec)
    within [seg_start, seg_end] -- used by _detect_fast_shallow_transition
    to tell a mostly-in-place postural change (genuine stand) apart from
    whole-body translation (fall-adjacent motion).

    Deliberately does NOT reuse the module's usual per-frame
    _torso_scaled_hip_track (hip position divided by THAT SAME frame's own
    torso length): during a genuine sit-to-stand, torso_len itself changes
    a lot as posture straightens (projected shoulder-hip distance grows),
    so dividing by the per-frame value makes hip position appear to move
    even when it hasn't -- reproduced directly (a synthetic transition with
    a raw hip position frozen at a single fixed point still measured a peak
    of ~19 torso-lengths/sec under the per-frame-scaled version, purely
    from torso_len shrinking during the posture change, not real motion).

    Instead, raw (unscaled) hip position is divided by a SINGLE reference
    torso length -- the mean over [ref_start, ref_end] (the CONFIRMED
    standing run immediately preceding the dip, already validated as a
    stable state by the caller) -- so the scale used to convert pixels to
    "torso-lengths" stays fixed for the whole measurement instead of
    drifting with the very posture change being measured.

    Returns 0.0 (i.e. "no evidence of implausible translation") if the raw
    arrays aren't supplied, the reference scale can't be established, or
    the segment has fewer than 2 valid frames -- this check only ever makes
    _detect_fast_shallow_transition MORE conservative, so missing data must
    not itself cause a rejection.

    Pre-checks the reference slice for all-NaN before calling np.nanmean on
    it (rather than relying on try/np.errstate) -- np.nanmean on an
    all-NaN slice emits a RuntimeWarning ("Mean of empty slice") via
    Python's warnings module, which np.errstate does NOT suppress (that
    only governs floating-point error-state warnings like divide/invalid,
    not this one) -- purely cosmetic (the fallback 0.0 return is already
    correct either way), but noisy in logs and could bury a more important
    warning during debugging.
    """
    if hip_mid_raw is None or torso_len_raw is None:
        return 0.0
    ref_slice = torso_len_raw[ref_start:ref_end + 1]
    if np.all(np.isnan(ref_slice)):
        return 0.0
    ref_torso_len = float(np.nanmean(ref_slice))
    if not np.isfinite(ref_torso_len) or ref_torso_len < 1e-3:
        return 0.0

    seg_hip = hip_mid_raw[seg_start:seg_end + 1] / ref_torso_len
    seg_ts = ts[seg_start:seg_end + 1]
    seg_valid = ~np.isnan(seg_hip).any(axis=1)
    if seg_valid.sum() < 2:
        return 0.0
    valid_hip = seg_hip[seg_valid]
    valid_ts = seg_ts[seg_valid]
    seg_dt = np.diff(valid_ts)
    seg_disp = np.linalg.norm(np.diff(valid_hip, axis=0), axis=1)
    dt_positive = seg_dt > 0
    if not dt_positive.any():
        return 0.0
    with np.errstate(invalid="ignore"):
        seg_speed = np.where(dt_positive, seg_disp / np.where(dt_positive, seg_dt, 1.0), 0.0)
    return float(np.max(seg_speed))


def _hip_vertical_rise(hip_mid_raw: Optional[np.ndarray], torso_len_raw: Optional[np.ndarray],
                        sit_start: int, sit_end: int, stand_start: int, stand_end: int) -> Optional[float]:
    """Vertical hip RISE (torso-lengths, positive = hip moved UP in real
    space) between a confirmed SIT run and a confirmed STAND run, used by
    compute_sit_to_stand's primary path to reject seated repositioning
    (reclining, leg-crossing) that swings hip_angle across both state
    thresholds without a genuine stand -- see MIN_STAND_HIP_RISE's own
    docstring for the full real-footage evidence and rationale.

    Uses a SINGLE FIXED reference torso length (the mean over the SIT run)
    for both endpoints -- the same fixed-reference-scale approach
    _peak_translation_speed already uses and for the identical reason: a
    genuine stand changes torso_len itself substantially as posture
    straightens, so dividing by each frame's OWN (per-frame-varying) torso
    length would make the rise measurement drift with the very posture
    change being measured, rather than reflecting real vertical motion.

    Returns None (i.e. "cannot evaluate -- do not let this guard reject on
    missing data") if the raw arrays aren't supplied or the reference scale
    can't be established, mirroring _peak_translation_speed's own
    missing-data convention.
    """
    if hip_mid_raw is None or torso_len_raw is None:
        return None
    ref_slice = torso_len_raw[sit_start:sit_end + 1]
    if np.all(np.isnan(ref_slice)):
        return None
    ref_torso_len = float(np.nanmean(ref_slice))
    if not np.isfinite(ref_torso_len) or ref_torso_len < 1e-3:
        return None

    sit_y = float(np.nanmean(hip_mid_raw[sit_start:sit_end + 1, 1]))
    stand_y = float(np.nanmean(hip_mid_raw[stand_start:stand_end + 1, 1]))
    if not (np.isfinite(sit_y) and np.isfinite(stand_y)):
        return None

    # Image y increases DOWNWARD, so a rise (moving up) is a DECREASE in y --
    # (sit_y - stand_y) is positive when stand_y < sit_y, i.e. the hip is
    # higher in the image during the "stand" run than during the "sit" run.
    return float((sit_y - stand_y) / ref_torso_len)


def _nearest_valid_hip_frame(hip_mid_raw: Optional[np.ndarray], torso_len_raw: Optional[np.ndarray],
                              center_idx: int, lo: int, hi: int) -> Optional[int]:
    """Index nearest to `center_idx`, within `[lo, hi]` inclusive, where
    BOTH `hip_mid_raw` (both x and y) and `torso_len_raw` are finite --
    searching outward by increasing distance (`center_idx` itself first,
    then +1/-1, +2/-2, ...; on a tie at the same distance, +offset is
    checked before -offset, an arbitrary but deterministic and irrelevant
    tie-break since both are equally "nearest"). Returns None if no frame
    in `[lo, hi]` has valid raw hip data at all.

    Added to close a real robustness gap in
    _detect_fast_shallow_transition's guard #5 (see that function's own
    docstring): the guard's hip-rise reference was previously ALWAYS a
    single fixed frame (`trough_idx`), so if that ONE frame's raw hip
    landmarks happened to be NaN on either side (a frame can have a valid
    hip_angle -- computed from shoulder/hip/knee on whichever side IS
    visible -- while hip_mid_raw, which needs BOTH left and right hip
    points to average, is simultaneously NaN if the other side's hip
    specifically is occluded), the guard silently skipped itself (its
    documented, unchanged "missing data must not reject" behavior) even
    though a neighboring frame just one or two positions away, well within
    the same confirmed gap, likely has a very similar real hip height and
    could have supplied a usable reference. Bounded ONLY by the gap's own
    natural limits passed in as `lo`/`hi` (never an invented tolerance
    radius) -- this keeps the search from ever reaching into either
    adjacent CONFIRMED STANDING run, which would corrupt the measurement
    (comparing the standing run to itself), and needs no new,
    independently-tuned magic number: the caller already has a
    well-defined, already-justified range (the gap between the two
    confirmed standing runs) to search within.

    Returns `center_idx` unchanged, with zero extra work beyond the single
    up-front validity check, whenever that frame is already valid -- this
    function only ever WIDENS the search when the exact trough frame
    itself is unusable, so every existing case where guard #5 already
    worked is untouched."""
    if hip_mid_raw is None or torso_len_raw is None:
        return None

    def _is_valid(idx: int) -> bool:
        return bool(np.isfinite(torso_len_raw[idx]) and np.all(np.isfinite(hip_mid_raw[idx])))

    if lo <= center_idx <= hi and _is_valid(center_idx):
        return center_idx

    max_dist = max(center_idx - lo, hi - center_idx)
    for dist in range(1, max_dist + 1):
        for idx in (center_idx + dist, center_idx - dist):
            if lo <= idx <= hi and _is_valid(idx):
                return idx
    return None


def _detect_fast_shallow_transition(hip_angles: np.ndarray, stand_runs: List[tuple], ts: np.ndarray,
                                     hip_mid_raw: Optional[np.ndarray] = None,
                                     torso_len_raw: Optional[np.ndarray] = None,
                                     confident: Optional[np.ndarray] = None,
                                     _quality_out: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, float]]:
    """Fallback for compute_sit_to_stand: a genuine but FAST sit-to-stand
    whose hip_angle trough never reaches the full _HIP_ANGLE_SITTING_MAX
    depth (see compute_sit_to_stand's docstring -- SitFast_GetupFast.MOV is
    the real clip this recovers: a rapid crouch/perch, not a fully-seated
    posture, so the primary sit-run-based path never finds a confirmed
    sitting run to anchor on).

    Looks for the first CONFIRMED-standing -> dip -> CONFIRMED-standing
    excursion between consecutive entries of `stand_runs`. Four guards
    keep this from reintroducing false positives / misreading fall-adjacent
    motion, or a full bend/squat, as a stand:
      1. Both sides of the dip must already be a _STATE_CONFIRM_FRAMES-long
         CONFIRMED standing run (the same gate the primary path uses) --
         SitFloor_lowKeypoints_crossedLegs.MOV (a person who never actually
         stands) never produced even one, so it can never reach this
         function's search loop at all via compute_sit_to_stand's call site.
      2. The gap between the two runs must itself be at least
         _STATE_CONFIRM_FRAMES long, and its deepest point must drop at
         least FAST_SIT_MIN_DESCENT_DEGREES below the preceding run's own
         mean angle -- so a single boundary-jitter frame (the hip_angle
         estimate flickering a fraction of a degree either side of
         _HIP_ANGLE_STANDING_MIN) can't masquerade as a "sit."
      3. The trough itself must stay ABOVE _HIP_ANGLE_SITTING_MAX -- i.e.
         genuinely SHALLOW, per this function's own name/purpose (recovering
         a fast stand whose dip never reaches full sitting depth, not a
         substitute sitting-detector with no floor). This guard was ADDED
         after a real false positive was traced to its absence: guard #2
         only checks a MINIMUM descent, with no corresponding maximum/depth
         bound, so a fast BEND (torso folding forward at the waist, not a
         sit) satisfies "descended at least 7 degrees" just as trivially as
         a genuine shallow perch does -- confirmed on real footage
         (Bend_pickup_normalLight_leftRight.MOV: trough 39.6/88.8 degrees,
         descent 123.9/81.6 degrees; Bend_pickup_normalLight_back.MOV:
         trough 76.6 degrees, descent 94.6 degrees -- all deep excursions
         WAY past _HIP_ANGLE_SITTING_MAX=125, nothing "shallow" about them,
         yet all satisfied guard #2's floor-only check). The one genuine
         reference this project has for what this function is FOR
         (SitFast_GetupFast.MOV) troughs at 135.6 degrees -- comfortably
         above 125, i.e. genuinely shallow, exactly the case this guard is
         designed to keep passing.
      4. The candidate segment's peak hip TRANSLATIONAL speed -- measured
         against a FIXED reference scale from the preceding confirmed
         standing run, not the per-frame-varying torso length (see
         _peak_translation_speed's own docstring for why that distinction
         matters) -- must stay under FALLBACK_MAX_TRANSLATION_SPEED. A
         genuine stand is primarily a postural (angle) change with the hip
         translating only modestly; fall-adjacent motion additionally
         involves the hip moving rapidly through space, which hip-angle
         geometry alone cannot see. Skipped (not rejected) if
         `hip_mid_raw`/`torso_len_raw` aren't supplied, preserving this
         function's prior behavior for any caller that doesn't have them.
         (This guard alone already rejected one of the two false-positive
         bend clips' OTHER candidate pair -- e.g. Bend_pickup_normalLight_
         leftRight.MOV's first stand-run pair measured peak_translation=1.278,
         over FALLBACK_MAX_TRANSLATION_SPEED=1.0 -- but each clip had a
         SECOND candidate pair with low enough translation to still slip
         through without guard #3 above.)
      5. The trough must show a genuine vertical hip RISE into the
         FOLLOWING confirmed-standing run (`post_start`/`post_end`), using
         the same fixed-reference-scale `_hip_vertical_rise` helper and
         MIN_STAND_HIP_RISE threshold the PRIMARY path already applies (see
         that constant's own docstring) -- with a single frame near the
         trough standing in for the primary path's confirmed-sit-run
         reference, since this fallback has no such run by definition.
         Which single frame: `trough_idx` itself if its own raw hip
         landmarks are usable, otherwise the NEAREST frame within this same
         gap that is (`_nearest_valid_hip_frame`, added in a later
         robustness pass -- see that function's own docstring for why this
         is needed: a frame's hip_angle can be valid from only ONE side's
         shoulder/hip/knee while hip_mid_raw, which needs BOTH hip points,
         is simultaneously NaN). Skipped -- not rejected -- if no frame
         anywhere in the gap has usable raw hip data, unchanged from before
         this robustness pass: the guard's missing-data convention (see
         below) is about WHETHER a reference frame can be found at all, not
         about accepting a worse one than necessary. ADDED after this exact real false positive was traced
         (not assumed) directly on Sit_Stand_2.mov: guards #1-#4 above,
         acting ALONE, do not close the seated-repositioning false positive
         MIN_STAND_HIP_RISE's own docstring describes -- that guard is wired
         into the PRIMARY (confirmed-sit-run) path only, and the specific
         spurious detection its docstring cites as evidence (duration=0.895,
         reversal=18) was traced this session to `compute_sit_to_stand`
         finding NO confirmed sit run in the implicated 90-frame window at
         all (the reclining motion's hip angle dips only into the shallow
         125-143 dead zone, never past the 125 sitting floor for
         _STATE_CONFIRM_FRAMES straight frames) -- so it falls through to
         THIS fallback instead, which had no rise guard of its own. Measured
         directly on the real window: trough-to-preceding-stand-run rise =
         0.031 torso-lengths, trough-to-following-stand-run rise = 0.030 --
         both far below MIN_STAND_HIP_RISE=0.08 (and, for comparison, far
         below the 0.128-0.403 range measured for genuine stands elsewhere
         in that constant's own docstring) -- confirming this candidate is
         the same seated-repositioning pattern, just reached via a different
         code path than the one already guarded. Skipped (not rejected) if
         `hip_mid_raw`/`torso_len_raw` aren't supplied, mirroring guard #4's
         own missing-data convention.

    NOTE: guards #3 and #4 are complementary, not redundant -- #4 catches
    deep bends that also involve real hip translation (a step, a lunge);
    #3 catches deep bends/squats that stay roughly in place (translation
    alone would not reject them, as measured above: 0.912/0.956 -- under
    the 1.0 cap -- for the two real false positives #3 was specifically
    added to close). Guard #5 is a THIRD, independent axis (vertical
    position, not angle depth or translation speed) -- a seated
    repositioning can be simultaneously shallow (passes #3), translation-free
    (passes #4), and rise-free (caught only by #5).

    `confident` (if supplied) is passed through to _count_reversals so a
    stretch of single-sided-visibility angle noise can't masquerade as a
    "shaky" transition -- see that function's own docstring.

    `_quality_out`: internal, OPTIONAL -- see compute_sit_to_stand's own
    `_quality_out` docstring (this function is one of its two return
    paths; both report reliability the same way).
    """
    for k in range(len(stand_runs) - 1):
        pre_start, pre_end = stand_runs[k]
        post_start, post_end = stand_runs[k + 1]
        gap = hip_angles[pre_end + 1: post_start]
        if gap.size < _STATE_CONFIRM_FRAMES or np.all(np.isnan(gap)):
            continue

        trough_local = int(np.nanargmin(gap))
        trough_angle = float(gap[trough_local])
        baseline = float(np.nanmean(hip_angles[pre_start:pre_end + 1]))
        if baseline - trough_angle < FAST_SIT_MIN_DESCENT_DEGREES:
            continue
        if trough_angle <= _HIP_ANGLE_SITTING_MAX:
            continue  # not "shallow" -- a full/deep excursion (bend/squat/genuine sit), not this fallback's target

        trough_idx = pre_end + 1 + trough_local
        first_stand_after = post_start
        duration_sec = float(ts[first_stand_after] - ts[trough_idx])
        if duration_sec <= 0:
            continue

        peak_translation = _peak_translation_speed(
            hip_mid_raw, torso_len_raw, ts, pre_start, pre_end, trough_idx, first_stand_after)
        if peak_translation > FALLBACK_MAX_TRANSLATION_SPEED:
            continue  # fall-adjacent whole-body translation, not a stand -- keep searching later runs

        # Nearest-valid-frame fallback for the rise reference (see
        # _nearest_valid_hip_frame's own docstring): if trough_idx's OWN raw
        # hip landmarks are NaN (possible even though its hip_angle is
        # valid -- angle needs only ONE side's shoulder/hip/knee, hip_mid_raw
        # needs BOTH hips), search outward within this SAME gap (never into
        # either adjacent confirmed standing run) for the nearest frame that
        # does have usable raw hip data, rather than unconditionally giving
        # up on measuring rise for this candidate at all.
        rise_ref_idx = _nearest_valid_hip_frame(hip_mid_raw, torso_len_raw, trough_idx, pre_end + 1, post_start - 1)
        if rise_ref_idx is not None:
            hip_rise = _hip_vertical_rise(hip_mid_raw, torso_len_raw, rise_ref_idx, rise_ref_idx, post_start, post_end)
        else:
            hip_rise = None
        if hip_rise is not None and hip_rise < MIN_STAND_HIP_RISE:
            continue  # no genuine vertical rise out of the trough -- seated repositioning, not a stand

        segment = hip_angles[trough_idx:first_stand_after + 1]
        seg_confident = confident[trough_idx:first_stand_after + 1] if confident is not None else None
        if _quality_out is not None and seg_confident is not None and len(seg_confident) > 0:
            _quality_out["reliability"] = float(np.mean(seg_confident))
        return {"duration_sec": duration_sec, "reversal_count": _count_reversals(segment, confident=seg_confident)}
    return None


def compute_sit_to_stand(window: List[dict], _raw: Optional[np.ndarray] = None,
                          _ts: Optional[np.ndarray] = None,
                          _quality_out: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, float]]:
    """
    Detects THE FIRST (see contract note below) sitting -> standing
    transition inside the window (hip_angle crossing from
    <= _HIP_ANGLE_SITTING_MAX to >= _HIP_ANGLE_STANDING_MIN) and measures:
      - duration_sec: time from the last sitting-range frame to the first
        standing-range frame.
      - reversal_count: number of local direction reversals in hip_angle's
        frame-to-frame delta during the transition -- a rough "smoothness"
        proxy (more reversals = shakier, less monotonic movement out of the
        chair), in the same spirit as the Timed-Up-and-Go test's qualitative
        "steadiness" observation.

    SINGLE-TRANSITION-PER-WINDOW CONTRACT (see docs/GAIT_CODE_REVIEW.md
    finding #7): this is a deliberate, not accidental, limitation. Only the
    FIRST confirmed sit->stand transition in the window is ever reported
    (`first_stand_after = stand_runs[0][0]`, unconditionally, below) -- a
    window containing two full cycles (sit->stand->sit->stand, e.g. someone
    attempting to stand, failing, sitting back down, and trying again)
    silently reports only the first. This keeps the function's contract
    simple (one call -> at most one transition, matching duration_sec/
    reversal_count's own singular meaning) rather than returning a variable-
    length list of transitions, which would change this function's return
    type/shape and every caller's expectations. In the live streaming case
    (gait_stream.py's sliding window) a later re-assessment will eventually
    surface a second cycle once the first has scrolled out of the buffer,
    so this isn't a total blind spot over a whole session -- but any SINGLE
    assess_risk() call cannot reflect "repeated attempts" in one window,
    which is itself a potentially clinically meaningful pattern this
    output has no way to represent today. See
    test_first_of_two_transitions_in_one_window_is_reported in
    tests/test_gait_risk.py for a regression test locking in this exact
    behavior.

    If no frame in the window drops low enough to confirm a genuine SITTING
    run (<= _HIP_ANGLE_SITTING_MAX for _STATE_CONFIRM_FRAMES consecutive
    frames), falls back to _detect_fast_shallow_transition -- a genuinely
    fast sit-to-stand (e.g. a quick perch/touch-and-go) can reverse
    direction before hip_angle ever reaches a fully-seated depth, which is
    a real, distinct scenario from "no transition happened at all" (see
    that function's docstring; found via real-footage validation on
    SitFast_GetupFast.MOV, which the un-augmented sit-run-based path below
    missed entirely despite containing a genuine fast stand-up). That
    fallback also rejects candidates whose hip TRANSLATES too fast to be a
    stand-in-place -- see FALLBACK_MAX_TRANSLATION_SPEED's own docstring.

    Returns None if neither path finds a transition (this is the expected/
    common case, not an error -- most windows won't happen to contain one).

    `_raw`: internal -- see _normalized_positions's docstring. Profiling
    showed this function's own per-row `_extract_keypoint_pairs(row)` calls
    were the single largest cost in a full assess_risk() call (a third
    independent re-parse of the same window, on top of the two
    `_torso_scaled_hip_track`/`_normalized_positions` already did) -- reusing
    a shared raw array removes that redundancy entirely.

    `_ts`: internal -- an already-computed _timestamps(window), shared the
    same way (see _timestamps' own docstring).

    `_quality_out`: internal, OPTIONAL -- if a dict is passed, this
    function (via either return path -- the primary sit-run-based one
    below, or _detect_fast_shallow_transition) fills in `"reliability"` as
    a side effect, ONLY when returning a real (non-None) transition: the
    fraction of the reported transition's own frames (`last_sit`/
    `trough_idx` through `first_stand_after` inclusive) where BOTH left and
    right sides were confidently tracked (the same `both_sides_confident`
    mask _count_reversals already uses to suppress single-sided-visibility
    angle noise -- see that function's docstring). A transition detected
    almost entirely from single-sided landmarks is real (it still passed
    every existing correctness guard) but less well-evidenced than one
    tracked from both sides throughout -- this reports that distinction
    rather than collapsing it into a single available/unavailable bit.
    """
    raw = _raw if _raw is not None else _raw_keypoint_array(window)
    pairs_per_frame = raw.reshape(-1, 33, 2)

    # Raw (unscaled) hip midpoint + per-frame torso length -- cheap
    # vectorized byproducts of the SAME pairs_per_frame array already
    # parsed above, needed only if the fallback path's translation check
    # (see _peak_translation_speed) ends up running. No re-parsing.
    hip_mid_raw = (pairs_per_frame[:, LEFT_HIP, :] + pairs_per_frame[:, RIGHT_HIP, :]) / 2.0
    sh_mid_raw = (pairs_per_frame[:, LEFT_SHOULDER, :] + pairs_per_frame[:, RIGHT_SHOULDER, :]) / 2.0
    torso_len_raw = np.linalg.norm(sh_mid_raw - hip_mid_raw, axis=1)

    def _pt(idx):
        return pairs_per_frame[:, idx, :]  # (T, 2), may contain NaN rows

    # BUG FIXED (was `_joint_point(...) or _joint_point(...)`): a Python
    # tuple is truthy even when it holds (nan, nan), so that pattern never
    # actually fell back to the other side on occlusion -- a window with a
    # perfectly good RIGHT hip angle but an occluded LEFT one silently
    # computed NaN and lost the frame, instead of using the side that was
    # actually visible. Fixed to compute both sides and average whichever
    # are valid per frame, mirroring pipeline_utils.py's own knee_angle/
    # hip_angle averaging convention (see _classify_heuristic), vectorized
    # over the whole (T, 2) arrays via _batch_hip_angle instead of a
    # per-frame Python loop (see that function's docstring for why this
    # mattered).
    l_sh, r_sh = _pt(LEFT_SHOULDER), _pt(RIGHT_SHOULDER)
    l_hp, r_hp = _pt(LEFT_HIP), _pt(RIGHT_HIP)
    l_kn, r_kn = _pt(LEFT_KNEE), _pt(RIGHT_KNEE)
    l_ank, r_ank = _pt(LEFT_ANKLE), _pt(RIGHT_ANKLE)

    left_angle = _batch_hip_angle(l_sh, l_hp, l_kn)
    right_angle = _batch_hip_angle(r_sh, r_hp, r_kn)
    valid_l = ~np.isnan(left_angle)
    valid_r = ~np.isnan(right_angle)
    n_valid = valid_l.astype(np.float64) + valid_r.astype(np.float64)
    angle_sum = np.where(valid_l, left_angle, 0.0) + np.where(valid_r, right_angle, 0.0)
    with np.errstate(invalid="ignore"):
        hip_angles = np.where(n_valid > 0, angle_sum / np.where(n_valid > 0, n_valid, 1.0), np.nan)
    ts = _ts if _ts is not None else _timestamps(window)

    # Knee angle (hip-knee-ankle), the SAME two-angle geometry
    # pipeline_utils.py::_classify_heuristic already uses alongside hip
    # angle -- computed here ONLY for the STANDING-BEND HIP-RISE EXEMPTION
    # below (see MIN_STAND_HIP_RISE's own docstring); not used anywhere
    # else in this function, and not returned. `_batch_hip_angle`'s name is
    # generic three-point-angle math (shoulder-hip-knee for hip angle,
    # hip-knee-ankle for knee angle), reused as-is rather than duplicated.
    knee_left_angle = _batch_hip_angle(l_hp, l_kn, l_ank)
    knee_right_angle = _batch_hip_angle(r_hp, r_kn, r_ank)
    knee_valid_l = ~np.isnan(knee_left_angle)
    knee_valid_r = ~np.isnan(knee_right_angle)
    knee_n_valid = knee_valid_l.astype(np.float64) + knee_valid_r.astype(np.float64)
    knee_angle_sum = np.where(knee_valid_l, knee_left_angle, 0.0) + np.where(knee_valid_r, knee_right_angle, 0.0)
    with np.errstate(invalid="ignore"):
        knee_angles = np.where(knee_n_valid > 0, knee_angle_sum / np.where(knee_n_valid > 0, knee_n_valid, 1.0), np.nan)

    # Both-sides-valid mask -- reused by _count_reversals (via `confident`)
    # so a stretch where only ONE side is visible can't manufacture spurious
    # "reversals" from single-sided angle noise (see _count_reversals'
    # own docstring for the real-footage failure mode this guards against).
    both_sides_confident = valid_l & valid_r

    sitting_mask = hip_angles <= _HIP_ANGLE_SITTING_MAX
    standing_mask = hip_angles >= _HIP_ANGLE_STANDING_MIN

    # Require each state to be CONFIRMED by _STATE_CONFIRM_FRAMES consecutive
    # frames before it counts as "sitting" or "standing" at all -- see
    # _STATE_CONFIRM_FRAMES's docstring for the real false-positive this
    # fixes (a single noisy frame is not a state, real human posture doesn't
    # flip states in one video frame). A confirmed run is further discarded
    # if it emerges right out of a long tracking blackout -- see
    # _MAX_TRUSTED_GAP_BEFORE_STATE's docstring for the real false-positive
    # THAT fixes (a MediaPipe re-acquisition artifact, not a real state).
    invalid = np.isnan(hip_angles)
    stand_runs = _drop_runs_after_long_gap(
        _confirmed_runs(standing_mask, _STATE_CONFIRM_FRAMES), invalid, _MAX_TRUSTED_GAP_BEFORE_STATE)
    if not stand_runs:
        return None
    first_stand_after = stand_runs[0][0]  # start of the earliest CONFIRMED standing run

    sit_runs = _drop_runs_after_long_gap(
        _confirmed_runs(sitting_mask, _STATE_CONFIRM_FRAMES), invalid, _MAX_TRUSTED_GAP_BEFORE_STATE)
    # The confirmed sitting run immediately preceding the confirmed stand --
    # not just any earlier sitting frame in the window -- so duration_sec/
    # reversal_count measure the actual localized transition, not however
    # much unrelated sitting/fidgeting happened earlier in a multi-second
    # window (the second half of the same real-footage bug: the old code
    # anchored to the EARLIEST sit frame in the whole window regardless of
    # how far it was from the stand).
    candidate_sit_runs = [r for r in sit_runs if r[1] < first_stand_after]
    if not candidate_sit_runs:
        return _detect_fast_shallow_transition(
            hip_angles, stand_runs, ts, hip_mid_raw=hip_mid_raw, torso_len_raw=torso_len_raw,
            confident=both_sides_confident, _quality_out=_quality_out)
    last_sit = candidate_sit_runs[-1][1]  # last frame of the nearest preceding confirmed sit run

    # Minimum-gap guard (see docs/GAIT_CODE_REVIEW.md's bend/squat follow-up
    # investigation): requires at least _STATE_CONFIRM_FRAMES between the
    # last confirmed-sit frame and the first confirmed-stand frame, mirroring
    # the gap-length guard _detect_fast_shallow_transition's fallback path
    # ALREADY applies to its own candidate gaps (`gap.size < _STATE_CONFIRM_FRAMES`
    # a few lines below in that function) -- the primary path had no
    # equivalent protection. Confirmed real false positive this closes:
    # Bend_pickup_squat_lowLight.MOV, two overlapping 90-frame sliding
    # windows (frames [60:149] and [75:164]) -- during the RISING phase of a
    # squat, hip_angle sweeps rapidly and continuously from a transient
    # confirmed-sitting-range dip straight through to a confirmed-standing
    # reading in as little as 2 frames (measured: last_sit=31, first_stand_
    # after=33, ~0.068s at this clip's ~29.4fps) -- ~3x faster than the
    # fastest GENUINE sit-to-stand this project has on file
    # (SitFast_GetupFast.MOV's fallback-path detection: 0.216s). A gap this
    # short is not a plausible voluntary sit-to-stand transition by either
    # of this project's own real references; it is the sitting-range
    # threshold being crossed in passing during continuous motion, not a
    # confirmed STATE being held and then left. Requiring the same minimum
    # gap already trusted elsewhere in this same function is not a new,
    # independently-tuned magic number -- it is applying an existing,
    # already-justified constant symmetrically to a code path that was
    # missing it.
    #
    # OFF-BY-ONE FIX (found in a later audit pass -- see
    # docs/GAIT_CODE_REVIEW.md's cross-module consistency follow-up): the
    # ORIGINAL version of this guard compared `first_stand_after - last_sit`
    # (an INDEX DISTANCE, which counts one MORE than the number of frames
    # actually lying strictly between the two states) directly against
    # _STATE_CONFIRM_FRAMES. _detect_fast_shallow_transition's own gap
    # check, a few lines below in this same module, compares `gap.size`
    # -- literally `post_start - pre_end - 1`, i.e. the COUNT OF FRAMES
    # STRICTLY BETWEEN the two states -- against the exact same constant.
    # These are NOT the same quantity (index distance = frames-between + 1),
    # so the original version was systematically one frame MORE PERMISSIVE
    # than the fallback path's own pre-existing check for the identical
    # physical situation (verified directly: last_sit=10, first_stand_
    # after=13 -- 2 frames, 11 and 12, strictly between -- was ACCEPTED by
    # the original primary-path check, `3 < 3` is False, while the
    # equivalent fallback-path gap, `gap.size=2`, is REJECTED by `2 < 3`).
    # The `- 1` below makes both paths apply the IDENTICAL "frames strictly
    # between" definition to the same constant, closing that inconsistency
    # -- strictly MORE conservative than before (rejects one additional
    # frame-gap value, 3, that previously slipped through), so it cannot
    # reintroduce any previously-fixed false positive; it can only reject
    # additional, even-faster implausible crossings.
    if first_stand_after - last_sit - 1 < _STATE_CONFIRM_FRAMES:
        return None

    # Anchor-run side-switching guard (found via real-footage tracing on
    # Deep_Bend.mov, a sustained deep bend/kneel with heavy self-occlusion
    # -- ankle visibility 0.54, hip 0.86 over the clip). This is a
    # DIFFERENT mechanism from the geometric (angle-only) bend/squat
    # degeneracy this module has long documented as unsolved -- it is not
    # about what the angle measures, but about whether the two "confirmed"
    # states it measured are corroborated by a CONSISTENT source.
    #
    # First cut of this guard (rejected -- kept here as a documented dead
    # end, not silently discarded): reject whenever an anchor run has NO
    # frame with both_sides_confident at all. This over-rejected: it broke
    # test_sit_to_stand_detected_despite_one_sided_occlusion and
    # test_sit_to_stand_reliability_reflects_landmark_confidence, both of
    # which deliberately test (and depend on) a real, different scenario
    # this project already explicitly supports -- ONE side occluded for an
    # ENTIRE clip (furniture, camera angle, another person), where the
    # OTHER side stays reliably visible throughout BOTH the sit and stand
    # phases. That case also has zero both-sided-confident frames by
    # construction, but is not the Deep_Bend failure mode.
    #
    # Root cause, isolated by comparing per-side (not just per-pair)
    # validity between the two cases: in the one-sided-occlusion case, the
    # SAME side (e.g. right) is the one providing coverage in BOTH the
    # sit-run and the stand-run -- a stable, physically plausible pattern
    # (one camera-relative side genuinely stayed blocked the whole time).
    # In Deep_Bend's actual spurious detections, measured directly: the
    # sit-run (frames 24-26) was covered ENTIRELY by the RIGHT side
    # (left_frac=0.0, right_frac=1.0), while the stand-run (frames 77-80)
    # was covered ENTIRELY by the LEFT side (left_frac=1.0, right_frac=0.0)
    # -- the two states share NO common corroborating side at all. That is
    # not a stable occlusion pattern; it is MediaPipe's per-frame guess at
    # which side to trust flipping between the two states, which is a
    # meaningfully weaker basis for treating them as the same real
    # transition than either "both sides agree" or "one side reliably
    # tracked the whole way through."
    #
    # This guard therefore only rejects when BOTH anchor runs are entirely
    # single-sided (no both-sided-confident frame in either -- same
    # pre-check as the rejected first cut) AND the two runs share NO
    # commonly-valid side. Verified this preserves every currently-known
    # real detection in the project's full corpus (8 clips, 24 detections,
    # both the pre-existing 28-clip set and GAIT_Analysis_Test_Footages) --
    # none of them are entirely single-sided in the first place (all have
    # both_sides_confident fraction >= 0.39 in both anchor runs, so they
    # never reach this guard's condition at all) -- while rejecting
    # Deep_Bend.mov's two false positives specifically, and preserving the
    # one-sided-occlusion synthetic fixture (same right side valid in both
    # runs -> a shared side exists -> not rejected).
    sit_slice = slice(candidate_sit_runs[-1][0], last_sit + 1)
    stand_slice = slice(first_stand_after, stand_runs[0][1] + 1)
    sit_both_conf = both_sides_confident[sit_slice]
    stand_both_conf = both_sides_confident[stand_slice]
    if not sit_both_conf.any() and not stand_both_conf.any():
        shares_left = valid_l[sit_slice].any() and valid_l[stand_slice].any()
        shares_right = valid_r[sit_slice].any() and valid_r[stand_slice].any()
        if not shares_left and not shares_right:
            return None

    # Vertical hip-rise guard (see MIN_STAND_HIP_RISE's own docstring for
    # the real-footage evidence): a genuine sit-run -> stand-run pairing
    # requires the hip to have actually RISEN -- ordinary seated
    # repositioning (reclining, leg-crossing) can swing hip_angle across
    # both thresholds without the hip ever leaving the chair seat's
    # height. Skipped (not rejected) if the raw hip-position arrays aren't
    # available, matching _peak_translation_speed's own missing-data
    # convention -- this check only ever makes the primary path MORE
    # conservative, so missing data must not itself cause a rejection.
    sit_run_start = candidate_sit_runs[-1][0]
    stand_run_end = stand_runs[0][1]
    hip_rise = _hip_vertical_rise(hip_mid_raw, torso_len_raw, sit_run_start, last_sit,
                                   first_stand_after, stand_run_end)
    if hip_rise is not None and hip_rise < MIN_STAND_HIP_RISE:
        # STANDING-BEND EXEMPTION (see MAX_PLAUSIBLE_HIP_DROP_FOR_BEND_
        # EXEMPTION's own docstring for the full real-footage derivation):
        # a genuine standing-bend recovery ALSO fails this guard (the feet
        # never leave standing height, so the hip barely rises, sometimes
        # even measuring as a net drop) -- but unlike seated repositioning,
        # the knee stays straight throughout, since the legs never bent in
        # the first place. Only exempted when the knee is straight at BOTH
        # reference points AND hip_rise isn't so extreme it more likely
        # reflects corrupted tracking than a real gentle recovery.
        sit_knee_seg = knee_angles[sit_run_start:last_sit + 1]
        stand_knee_seg = knee_angles[first_stand_after:stand_run_end + 1]
        sit_knee = float(np.nanmean(sit_knee_seg)) if np.isfinite(sit_knee_seg).any() else None
        stand_knee = float(np.nanmean(stand_knee_seg)) if np.isfinite(stand_knee_seg).any() else None
        is_standing_bend_recovery = (
            sit_knee is not None and stand_knee is not None
            and sit_knee >= _KNEE_ANGLE_STANDING_MIN and stand_knee >= _KNEE_ANGLE_STANDING_MIN
            and hip_rise >= MAX_PLAUSIBLE_HIP_DROP_FOR_BEND_EXEMPTION
        )
        if not is_standing_bend_recovery:
            return None

    duration_sec = float(ts[first_stand_after] - ts[last_sit])
    if duration_sec <= 0:
        return None

    segment = hip_angles[last_sit:first_stand_after + 1]
    seg_confident = both_sides_confident[last_sit:first_stand_after + 1]
    if _quality_out is not None and len(seg_confident) > 0:
        _quality_out["reliability"] = float(np.mean(seg_confident))
    return {"duration_sec": duration_sec, "reversal_count": _count_reversals(segment, confident=seg_confident)}

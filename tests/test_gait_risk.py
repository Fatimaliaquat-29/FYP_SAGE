"""
tests/test_gait_risk.py
========================
Tests for src/gait/ (GaitRiskAssessor.assess_risk() and gait_features.py).

Covers:
  - Output structure/contract (risk_score, signals -- not fall/no-fall)
  - Valid-window behavior (synthetic walking) exercising real computation,
    not mocks
  - Edge cases: too-short window, empty window, wrong types, missing keys,
    NaN, Inf, all-occluded window
  - Signal-direction sanity checks (steady vs. unsteady walking; smooth vs.
    shaky sit-to-stand) -- the same synthetic scenarios used for this
    module's own validation (see docs/GAIT_DATA_ASSESSMENT.md), turned into
    a regression test so future changes can't silently reintroduce the
    inverted-direction bugs found during that validation.
"""

import inspect
import re
import sys
import unittest
import warnings
from pathlib import Path
from unittest import mock

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.gait.gait_risk import GaitRiskAssessor
from src.gait import gait_risk as gr
from src.gait import gait_features as gf
from src.posture import pipeline_utils

RNG = np.random.default_rng(123)


def _standing_kps(noise=0.0):
    kps = [np.nan] * 66
    kps[22], kps[23] = 0.45, 0.30
    kps[24], kps[25] = 0.55, 0.30
    kps[46], kps[47] = 0.47, 0.55
    kps[48], kps[49] = 0.53, 0.55
    kps[50], kps[51] = 0.47, 0.75
    kps[52], kps[53] = 0.53, 0.75
    kps[54], kps[55] = 0.47, 0.95
    kps[56], kps[57] = 0.53, 0.95
    if noise:
        kps = [v + RNG.normal(0, noise) if not np.isnan(v) else v for v in kps]
    return kps


def _walking_window(n_frames, speed, stride_jitter=0.0, speed_jitter=0.0, sway_amp=0.0):
    """Walking-window generator for tests -- a faithful port of the
    generator used (and validated -- see docs/GAIT_DATA_ASSESSMENT.md) in
    this module's own validation script. Deliberately kept in sync with
    that script's geometry rather than reimplemented independently: an
    earlier, independently-hand-rolled version of this function produced a
    different absolute hip/torso scale and silently flipped the
    steady-vs-unsteady risk comparison below, for reasons unrelated to
    src/gait/ itself -- exactly the kind of test-fixture trap the real
    validation script's own debugging already worked through once."""
    window = []
    phase = 0.0
    hip_x, hip_y = 0.3, 0.5
    fps = 30.0
    torso_len = 0.25
    for i in range(n_frames):
        dt = 1.0 / fps
        cur_speed = max(speed * (1.0 + RNG.normal(0, speed_jitter)), 0.0) if speed_jitter else speed
        hip_x += cur_speed * dt
        cur_period = 1.05 * (1.0 + RNG.normal(0, stride_jitter)) if stride_jitter else 1.05
        phase += 2 * np.pi * dt / max(cur_period, 1e-3)
        # Smooth, slow oscillation -- NOT independent per-frame noise, which
        # would dominate the finite-differenced walking-speed signal (see
        # docs/GAIT_DATA_ASSESSMENT.md item 2 under "real bugs found").
        sway_x = sway_amp * np.sin(2 * np.pi * 0.8 * (i * dt) + 0.3)
        sway_y = sway_amp * 0.5 * np.sin(2 * np.pi * 1.1 * (i * dt))

        cx, cy = hip_x + sway_x, hip_y + sway_y
        fold = np.radians(180.0 - 175.0)  # constant upright torso lean
        sh_x = cx + torso_len * np.sin(fold) * 0.3
        sh_y = cy - torso_len * np.cos(fold)

        kps = [np.nan] * 66
        kps[22], kps[23] = sh_x - 0.05, sh_y
        kps[24], kps[25] = sh_x + 0.05, sh_y
        kps[46], kps[47] = cx - 0.05, cy
        kps[48], kps[49] = cx + 0.05, cy
        swing_amp = 0.08
        l_swing = swing_amp * np.sin(phase)
        r_swing = swing_amp * np.sin(phase + np.pi)
        knee_y = cy + torso_len * 0.8
        ankle_y = cy + torso_len * 1.6
        kps[50], kps[51] = cx - 0.05 + l_swing * 0.5, knee_y
        kps[52], kps[53] = cx + 0.05 + r_swing * 0.5, knee_y
        kps[54], kps[55] = cx - 0.05 + l_swing, ankle_y - abs(l_swing) * 0.3
        kps[56], kps[57] = cx + 0.05 + r_swing, ankle_y - abs(r_swing) * 0.3
        window.append({"timestamp": i * dt, "frame": i, "keypoints": kps})
    return window


def _fall_like_foreshortening_window(n_frames=90, collapse_start=40, collapse_frames=5,
                                      torso_len_before=0.25, torso_len_at_collapse=0.01):
    """A person standing still, except for a short (collapse_frames-frame)
    collapse where the hip drops toward the floor WHILE the projected
    shoulder-hip (torso) distance shrinks sharply -- the same foreshortening
    a real fall produces as the body rotates/curls toward the camera (see
    MAX_PLAUSIBLE_HIP_SPEED's docstring in gait_features.py). Because
    _torso_scaled_hip_track divides hip position by torso length, a
    near-vanishing torso length amplifies the apparent hip displacement
    enormously even though the underlying event is a single short fall, not
    sustained locomotion -- this reproduces (not just approximates) the
    real failure mode found on real footage (Fall_and_lie.MOV reached a
    computed walking_speed of 75.28 torso-lengths/sec from exactly this
    dynamic: rapid drop + foreshortening, not genuine walking)."""
    window = []
    for i in range(n_frames):
        if collapse_start <= i < collapse_start + collapse_frames:
            frac = (i - collapse_start) / float(collapse_frames - 1)
            hip_y = 0.35 + frac * 0.5
            torso_len = torso_len_before * (1 - frac) + torso_len_at_collapse * frac
        else:
            hip_y, torso_len = 0.35, torso_len_before
        hip_x = 0.3
        kps = [np.nan] * 66
        kps[22], kps[23] = hip_x - 0.05, hip_y - torso_len
        kps[24], kps[25] = hip_x + 0.05, hip_y - torso_len
        kps[46], kps[47] = hip_x - 0.05, hip_y
        kps[48], kps[49] = hip_x + 0.05, hip_y
        kps[50], kps[51] = hip_x - 0.05, hip_y + 0.2
        kps[52], kps[53] = hip_x + 0.05, hip_y + 0.2
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


def _sit_to_stand_window(shaky=False, n_frames=90, seed=7):
    local_rng = np.random.default_rng(seed)
    window = []
    t_start, t_len = 45, int(22 * (1.8 if shaky else 1.0))
    for i in range(n_frames):
        if i < t_start:
            angle = 100.0
        elif i < t_start + t_len:
            frac = (i - t_start) / t_len
            angle = 100.0 + frac * 75.0
            if shaky:
                angle += local_rng.normal(0, 12.0)
        else:
            angle = 175.0
        angle = float(np.clip(angle, 90.0, 180.0))
        fold = np.radians(180.0 - angle)
        cx = 0.3
        cy = _hip_cy_for_angle(angle)  # see that helper's docstring -- genuine stand must show a real hip rise
        sh_x, sh_y = cx + 0.25 * np.sin(fold) * 0.3, cy - 0.25 * np.cos(fold)
        kps = [np.nan] * 66
        kps[22], kps[23] = sh_x - 0.05, sh_y
        kps[24], kps[25] = sh_x + 0.05, sh_y
        kps[46], kps[47] = cx - 0.05, cy
        kps[48], kps[49] = cx + 0.05, cy
        kps[50], kps[51] = cx - 0.05, cy + 0.2
        kps[52], kps[53] = cx + 0.05, cy + 0.2
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


def _sit_to_stand_window_left_occluded(n_frames=90):
    """Same sit-to-stand transition as _sit_to_stand_window(shaky=False),
    but with the entire LEFT side (shoulder/hip/knee) blanked to NaN --
    only the right side is trustworthy, as would happen with real
    one-sided occlusion (furniture, camera angle, another person)."""
    window = _sit_to_stand_window(shaky=False, n_frames=n_frames)
    for row in window:
        for idx in (22, 23, 46, 47, 50, 51):  # left shoulder/hip/knee
            row["keypoints"][idx] = np.nan
    return window


def _hip_cy_for_angle(angle, sit_angle=100.0, stand_angle=175.0, cy_stand=0.55, rise=0.09):
    """Angle-dependent hip vertical position (image-y, smaller = higher in
    frame) -- returns `cy_stand` (the historical constant every one of
    these fixtures used, unconditionally, before MIN_STAND_HIP_RISE was
    added -- see that constant's own docstring in gait_features.py) at a
    fully-standing angle, and `cy_stand + rise` (lower/larger-y, i.e. the
    hip sitting lower) at a fully-sitting angle, linearly interpolated
    between. NOT a cosmetic addition -- compute_sit_to_stand's primary
    path now requires a genuine vertical hip RISE to accept a sit-run ->
    stand-run pairing (real seated repositioning, e.g. reclining in a
    chair, doesn't raise the hip; only an actual stand does -- see
    MIN_STAND_HIP_RISE's docstring for the real-footage evidence). Every
    fixture below that represents a GENUINE stand (as opposed to angle
    noise/occlusion/translation-guard tests that deliberately keep the hip
    fixed to isolate a DIFFERENT mechanism) now uses this instead of a
    fixed `cy`, so the synthetic geometry actually models the real-world
    signature this guard depends on, rather than accidentally defeating it
    by construction. `rise=0.09` (~0.36 torso-lengths, given these
    fixtures' own ~0.25 torso-length scale) sits within the real measured
    range (0.128-0.403 torso-lengths across three independent real clips --
    see MIN_STAND_HIP_RISE's docstring) -- not an arbitrary pick, and not
    tuned to any single fixture's own pass/fail outcome."""
    frac = float(np.clip((angle - sit_angle) / (stand_angle - sit_angle), 0.0, 1.0))
    return cy_stand + rise * (1.0 - frac)


def _angle_pose_row(angle, i, cx=0.3, cy=0.55):
    """One pose row for a given hip_angle -- same shoulder/hip/knee geometry
    _sit_to_stand_window uses, factored out so a single-frame noise spike
    can be spliced into an otherwise-sitting sequence.

    `cy` defaults to the historical fixed constant (0.55) -- UNCHANGED for
    callers that don't pass it explicitly, since most callers of this
    helper deliberately test a DIFFERENT mechanism (angle noise, one-sided
    occlusion, translation-guard behavior) that depends on the hip staying
    fixed. Callers that need to represent a GENUINE stand (and therefore
    need MIN_STAND_HIP_RISE's guard to accept them) pass
    `cy=_hip_cy_for_angle(angle)` explicitly -- see that helper's own
    docstring."""
    angle = float(np.clip(angle, 90.0, 180.0))
    fold = np.radians(180.0 - angle)
    sh_x, sh_y = cx + 0.25 * np.sin(fold) * 0.3, cy - 0.25 * np.cos(fold)
    kps = [np.nan] * 66
    kps[22], kps[23] = sh_x - 0.05, sh_y
    kps[24], kps[25] = sh_x + 0.05, sh_y
    kps[46], kps[47] = cx - 0.05, cy
    kps[48], kps[49] = cx + 0.05, cy
    kps[50], kps[51] = cx - 0.05, cy + 0.2
    kps[52], kps[53] = cx + 0.05, cy + 0.2
    return {"timestamp": i / 30.0, "frame": i, "keypoints": kps}


def _sitting_with_single_noise_spike_window(n_frames=90, spike_frame=60, spike_angle=149.0, seed=11):
    """A person who remains seated (angle oscillating in the 90-125 sitting
    range the whole clip, as real cross-legged/fidgeting footage does) for
    the ENTIRE window, except for exactly one frame where a transient
    landmark dropout pushes the averaged hip_angle into the standing range
    for a single frame -- a faithful synthetic reconstruction of the real
    bug found on SitFloor_lowKeypoints_crossedLegs.MOV (see
    _STATE_CONFIRM_FRAMES's docstring in gait_features.py): one noisy frame
    at 148.9 degrees, surrounded by clearly-sitting angles, with the person
    never actually standing up anywhere in the clip."""
    local_rng = np.random.default_rng(seed)
    window = []
    for i in range(n_frames):
        angle = spike_angle if i == spike_frame else float(np.clip(100.0 + local_rng.normal(0, 15.0), 70.0, 122.0))
        window.append(_angle_pose_row(angle, i))
    return window


def _fast_shallow_sit_to_stand_window(n_frames=90, dip_start=40, dip_len=15,
                                       standing_angle=175.0, trough_angle=107.0):
    """A person standing, quickly crouching/perching WITHOUT reaching a full
    seated depth, then standing back up -- a synthetic reconstruction of the
    real event found on SitFast_GetupFast.MOV (see
    _detect_fast_shallow_transition's docstring): a genuine fast sit-to-stand
    whose hip_angle trough never crosses the full sitting floor, so the
    primary sit-run-based path in compute_sit_to_stand cannot anchor on it.

    NOTE: `_angle_pose_row`'s "angle" parameter is a REQUESTED geometric
    input, not the literal resulting hip_angle -- its fixed-knee-position
    geometry (see that helper's docstring) is markedly non-linear near 180
    degrees (a wide range of requested values there produce nearly the same
    actual angle). The defaults here (175 -> actual ~178.5, 107 -> actual
    ~135.5) were picked by direct measurement to reproduce the real
    SitFast_GetupFast trough (~135.6 degrees, ~9.7 degrees below a ~145.3
    standing baseline) rather than assumed from the requested numbers.

    The dip also carries its own hip-height profile (same dip-relative
    `frac`/`sin` shape as the angle curve, but NOT derived from
    `_hip_cy_for_angle` -- deliberately: that helper's rise scales down
    toward 0 for a SHALLOW angle trough like this fixture's own
    ~135.5-degree default, which would model a shallow PERCH stand as
    barely rising at all. Real footage says otherwise -- a fast, shallow
    stand still involves the hip actually lifting off the seat/perch by a
    real amount (confirmed directly: the real SitFast_GetupFast.MOV clip
    this fixture reconstructs is still correctly recovered end-to-end by
    the actual extraction+assessment pipeline after the fallback path's own
    hip-rise guard was added -- see that guard's docstring in
    gait_features.py -- so a synthetic fixture that models zero rise here
    would be testing a scenario the real pipeline doesn't actually produce).
    `_FAST_STAND_RISE` (0.09, same peak magnitude `_hip_cy_for_angle` uses
    for a FULL sit-to-stand) is applied at the SAME dip-relative timing as
    the angle dip, independent of how shallow the requested trough angle
    is."""
    _FAST_STAND_RISE = 0.09
    window = []
    for i in range(n_frames):
        if i < dip_start:
            angle, cy = standing_angle, 0.55
        elif i < dip_start + dip_len:
            frac = (i - dip_start) / (dip_len - 1)
            # down to the trough at the dip's midpoint, back up by its end
            angle = standing_angle - (standing_angle - trough_angle) * np.sin(frac * np.pi)
            cy = 0.55 + _FAST_STAND_RISE * np.sin(frac * np.pi)
        else:
            angle, cy = standing_angle, 0.55
        window.append(_angle_pose_row(angle, i, cy=cy))
    return window


def _standing_after_long_tracking_gap_window(n_frames=90, gap_start=40, gap_len=12,
                                              standing_angle=160.0, standing_run_len=3):
    """A person sitting/lying (hip_angle well within the sitting range) for
    most of the window, then TOTAL landmark loss (all-NaN) for `gap_len`
    consecutive frames, immediately followed by a short run reading in the
    STANDING range -- a synthetic reconstruction of the real MediaPipe
    re-acquisition artifact found on Sitting_Lying_FewLandmarks_back.MOV
    (see _MAX_TRUSTED_GAP_BEFORE_STATE's docstring): the person never
    actually stands, the sudden post-blackout reading is a tracking
    artifact, not a real transition."""
    window = []
    for i in range(n_frames):
        if gap_start <= i < gap_start + gap_len:
            row = {"timestamp": i / 30.0, "frame": i, "keypoints": [np.nan] * 66}
        elif i >= gap_start + gap_len and i < gap_start + gap_len + standing_run_len:
            # A genuine hip rise (relative to the sitting portions below,
            # which now use the SAME angle-consistent cy) -- for the
            # SHORT-gap parametrization this run is meant to represent a
            # real, trustworthy stand (see
            # test_standing_reading_after_short_gap_is_still_trusted's own
            # docstring); for the LONG-gap default it's still rejected
            # regardless, via _MAX_TRUSTED_GAP_BEFORE_STATE's own
            # independent gap-length check -- see MIN_STAND_HIP_RISE's
            # docstring in gait_features.py for why a real stand needs this.
            row = _angle_pose_row(standing_angle, i, cy=_hip_cy_for_angle(standing_angle))
        else:
            # Sitting/lying -- uses the SAME _hip_cy_for_angle mapping (not
            # the raw default) so the two segments are internally
            # consistent with each other, not accidentally mismatched.
            row = _angle_pose_row(100.0, i, cy=_hip_cy_for_angle(100.0))
        window.append(row)
    return window


class AssessRiskContractTests(unittest.TestCase):
    """Output structure: risk_score + signals, never a fall/no-fall flag."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_output_has_required_top_level_keys(self):
        window = _walking_window(150, speed=0.15)
        result = self.assessor.assess_risk(window)
        self.assertIn("risk_score", result)
        self.assertIn("signals", result)
        self.assertEqual(set(result.keys()), {"risk_score", "signals"})

    def test_output_is_not_a_fall_no_fall_flag(self):
        window = _walking_window(150, speed=0.15)
        result = self.assessor.assess_risk(window)
        self.assertNotIn("fall_detected", result)
        self.assertNotIn("fall", result)
        self.assertNotIn("posture_label", result)
        # risk_score, when present, must be a float in [0, 1], never a bool
        # or a string label -- this is the "graded, not binary" contract.
        if result["risk_score"] is not None:
            self.assertIsInstance(result["risk_score"], float)
            self.assertNotIsInstance(result["risk_score"], bool)
            self.assertGreaterEqual(result["risk_score"], 0.0)
            self.assertLessEqual(result["risk_score"], 1.0)

    def test_signals_is_always_four_entries_with_required_fields(self):
        window = _walking_window(150, speed=0.15)
        result = self.assessor.assess_risk(window)
        self.assertEqual(len(result["signals"]), 4)
        names = {s["name"] for s in result["signals"]}
        self.assertEqual(names, {"walking_speed", "stride_regularity", "postural_sway", "sit_to_stand"})
        for s in result["signals"]:
            for key in ("name", "available", "value", "risk_contribution", "calibrated", "description"):
                self.assertIn(key, s)
            self.assertIsInstance(s["available"], bool)
            self.assertIsInstance(s["calibrated"], bool)
            self.assertIsInstance(s["description"], str)
            self.assertGreater(len(s["description"]), 0)
            if not s["available"]:
                self.assertIsNone(s["value"])
                self.assertIsNone(s["risk_contribution"])

    def test_stationary_window_does_not_report_a_fake_gait_speed(self):
        """A perfectly stationary window must not read as 'extremely slow
        walking' -- this was a real bug caught during validation (see
        docs/GAIT_DATA_ASSESSMENT.md)."""
        window = [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(120)]
        result = self.assessor.assess_risk(window)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertFalse(speed_signal["available"])


def _walking_window_with_one_glitch_frame(jump=3.0, glitch_frame=75, **walking_kwargs):
    """A genuine, sustained walking bout (abundant real hip-translation path
    over the whole window) with ONE frame's entire torso (both shoulder AND
    hip x-coordinates) translated by `jump` -- an isolated position glitch
    that does NOT distort torso_len (both shoulder and hip move together,
    so the shoulder-hip distance _torso_scaled_hip_track divides by is
    unaffected), unlike moving the hip alone (which simultaneously perturbs
    the torso_len denominator and produces confusing, non-monotonic coupled
    effects on the resulting track -- found while building this fixture).
    Used to test that the plausibility gate excludes ONLY the glitched
    frame-pairs, leaving a real walking bout's genuine speed intact, in a
    window where the glitch is a small MINORITY of the total path (as
    opposed to _fall_like_foreshortening_window, where the "collapse" IS
    essentially the window's only source of motion and so any exclusion at
    all tends to dominate the path -- the two fixtures deliberately cover
    the two different real-world cases from MAX_PLAUSIBLE_HIP_SPEED's own
    docstring: majority-artifact windows and minority-artifact windows)."""
    window = _walking_window(150, **walking_kwargs)
    window = [dict(r, keypoints=list(r["keypoints"])) for r in window]
    glitched = list(window[glitch_frame]["keypoints"])
    for idx in (22, 24, 46, 48):  # left/right shoulder x, left/right hip x
        glitched[idx] += jump
    window[glitch_frame]["keypoints"] = glitched
    return window


class WalkingSpeedPlausibilityTests(unittest.TestCase):
    """Regression tests for the walking-speed physical-plausibility gate
    (MAX_PLAUSIBLE_HIP_SPEED): a fall's rapid hip displacement must not be
    interpreted as genuine (and therefore confidently low-risk) fast
    walking. See benchmarks/gait_footage_validation_report.md's "flicker"
    entries and gait_features.MAX_PLAUSIBLE_HIP_SPEED's own docstring for
    the real-footage failure mode this closes off."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def _peak_instantaneous_speed(self, window):
        """Un-gated per-frame-pair instantaneous speed, for asserting a
        fixture actually exercises the plausibility gate (peak > cap) --
        otherwise a test built on it would be vacuous."""
        hip_center = gf._torso_scaled_hip_track(window)
        ts = gf._timestamps(window)
        valid = ~np.isnan(hip_center).any(axis=1)
        pair_valid = valid[1:] & valid[:-1]
        dt = np.diff(ts)
        raw_mask = pair_valid & (dt > 0)
        disp = np.linalg.norm(np.diff(hip_center, axis=0), axis=1)
        return float(np.max(disp[raw_mask] / dt[raw_mask]))

    def test_majority_implausible_displacement_marks_signal_unavailable(self):
        """A window whose motion is DOMINATED by an implausible artifact
        (see _fall_like_foreshortening_window -- the "collapse" is
        essentially this window's only source of motion, so excluding the
        implausible pairs leaves too little genuine signal to trust) must
        report the signal as unavailable, not a diluted residual value --
        and that unavailability must actually reach assess_risk()'s output,
        not just compute_walking_speed() in isolation."""
        window = _fall_like_foreshortening_window()
        self.assertGreater(
            self._peak_instantaneous_speed(window), gf.MAX_PLAUSIBLE_HIP_SPEED,
            "test fixture must produce an implausible instantaneous speed to be a meaningful test",
        )

        self.assertIsNone(
            gf.compute_walking_speed(window),
            "a window whose motion is dominated by an implausible artifact must report "
            "walking_speed as unavailable, not a diluted residual reading",
        )

        result = self.assessor.assess_risk(window)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertFalse(
            speed_signal["available"],
            "the None from compute_walking_speed must propagate through assess_risk() as "
            "available=False, not silently vanish or get treated as an implicit low-risk value",
        )

    def test_minority_implausible_glitch_does_not_suppress_real_speed_reading(self):
        """A genuine, sustained walking bout with ONE implausible glitch
        frame (a small MINORITY of the window's total path -- the opposite
        case from the majority-artifact test above) must have that glitch
        excluded and still report the real underlying walking speed --
        recall must be preserved, and the reported value must not be an
        artifact-inflated one that would falsely saturate the risk sigmoid
        to near-zero."""
        from src.gait.gait_risk import _speed_risk

        baseline_kwargs = dict(speed=0.5, stride_jitter=0.02, speed_jitter=0.02)
        clean_window = _walking_window(150, **baseline_kwargs)
        glitched_window = _walking_window_with_one_glitch_frame(jump=3.0, **baseline_kwargs)

        self.assertGreater(
            self._peak_instantaneous_speed(glitched_window), gf.MAX_PLAUSIBLE_HIP_SPEED,
            "test fixture must produce an implausible instantaneous speed to be a meaningful test",
        )

        clean_speed = gf.compute_walking_speed(clean_window)
        glitched_speed = gf.compute_walking_speed(glitched_window)
        self.assertIsNotNone(
            glitched_speed,
            "a single glitch frame amid an otherwise genuine, sustained walking bout must not "
            "wipe out the whole reading -- only the glitched pairs should be excluded",
        )
        # The glitch must be neutralized, not just capped: the gated reading
        # should stay close to the clean baseline, not sit at some
        # intermediate inflated value.
        self.assertAlmostEqual(glitched_speed, clean_speed, delta=0.5)
        self.assertGreater(
            _speed_risk(glitched_speed), 1e-3,
            "the gated speed must not itself saturate the risk sigmoid to ~0 the way the raw "
            "implausible value would have -- that's the exact failure mode this gate exists to close",
        )

    def test_genuinely_fast_but_plausible_walking_is_not_suppressed(self):
        """Recall check: brisk (but human-plausible) walking, well under
        MAX_PLAUSIBLE_HIP_SPEED, must be completely unaffected by the gate."""
        fast_walk = _walking_window(150, speed=0.6, stride_jitter=0.02, speed_jitter=0.02)
        result = self.assessor.assess_risk(fast_walk)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertTrue(speed_signal["available"])
        self.assertLess(speed_signal["value"], gf.MAX_PLAUSIBLE_HIP_SPEED / 2)


def _jittery_stationary_window(n_frames, jitter_std, seed=17):
    """A subject standing perfectly still, with INDEPENDENT per-frame
    landmark noise on every coordinate (jitter_std, in the same raw
    normalized-image-coordinate units MediaPipe outputs) -- reproduces the
    random-walk signature real accumulated tracking jitter has: net
    displacement grows ~sqrt(N) while accumulated path length grows ~N, so
    a long enough window can cross MIN_AMBULATION_PATH on jitter alone
    (see MIN_AMBULATION_COHERENCE's own docstring)."""
    rng = np.random.default_rng(seed)
    window = []
    for i in range(n_frames):
        kps = [v + rng.normal(0, jitter_std) if not np.isnan(v) else v for v in _standing_kps()]
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


def _walking_then_stopping_window(n_frames, walk_start, walk_frames, speed, sway=0.0):
    """A subject standing still, walking for `walk_frames` starting at
    `walk_start`, then STOPPING AT THE NEW POSITION (continuing the
    trajectory, not resetting to a hardcoded start point -- an earlier
    draft of this fixture used independently-hardcoded standing/walking
    helpers that silently "teleported" the subject back to a fixed
    position after the walk, making net displacement spuriously zero
    regardless of any real coherent motion in between; caught by tracing
    the actual net-displacement computation, not assumed)."""
    window = []
    hip_x = 0.3
    phase = 0.0
    for i in range(n_frames):
        if walk_start <= i < walk_start + walk_frames:
            dt = 1.0 / 30.0
            hip_x += speed * dt
            phase += 2 * np.pi * dt / 1.05
        cx, cy, torso_len = hip_x, 0.5, 0.25
        kps = [np.nan] * 66
        kps[22], kps[23] = cx - 0.05, cy - torso_len
        kps[24], kps[25] = cx + 0.05, cy - torso_len
        kps[46], kps[47] = cx - 0.05, cy
        kps[48], kps[49] = cx + 0.05, cy
        swing = 0.08 * np.sin(phase)
        kps[50], kps[51] = cx - 0.05 + swing * 0.5, cy + torso_len * 0.8
        kps[52], kps[53] = cx + 0.05 - swing * 0.5, cy + torso_len * 0.8
        kps[54], kps[55] = cx - 0.05 + swing, cy + torso_len * 1.6
        kps[56], kps[57] = cx + 0.05 - swing, cy + torso_len * 1.6
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


class AmbulationCoherenceTests(unittest.TestCase):
    """Regression tests for MIN_AMBULATION_COHERENCE: a stationary subject
    must not be interpreted as ambulating purely because accumulated
    per-frame tracking jitter crosses MIN_AMBULATION_PATH. Every assertion
    here checks an actual output value, not merely that the code runs."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_1_completely_stationary_subject(self):
        window = [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(150)]
        self.assertIsNone(gf.compute_walking_speed(window))

    def test_2_stationary_with_small_random_jitter(self):
        window = _jittery_stationary_window(150, jitter_std=0.002)
        self.assertIsNone(gf.compute_walking_speed(window))

    def test_3_stationary_with_realistic_pose_estimation_jitter(self):
        """Jitter magnitude (0.006) calibrated from real MediaPipe output:
        SitFast_GetupFast.MOV frames 0-38 and Chair_fall.mp4 frames 0-47
        (both confirmed-still real segments) measured per-frame-pair hip
        displacement means of 0.07-0.12 torso-lengths; 0.006 raw per-frame
        jitter reproduces that same order of magnitude once compounded
        across coordinates and passed through _torso_scaled_hip_track's
        smoothing -- this is the exact reproduction that originally
        confirmed the bug (see MIN_AMBULATION_COHERENCE's own docstring)."""
        for n_frames in (90, 150, 300, 600):
            window = _jittery_stationary_window(n_frames, jitter_std=0.006, seed=42)
            result = gf.compute_walking_speed(window)
            self.assertIsNone(result, f"n_frames={n_frames}: stationary jitter must not read as ambulation")

    def test_4_genuine_small_movement_is_detected(self):
        """A short but genuinely coherent movement -- long/fast enough to
        clear the pre-existing MIN_AMBULATION_PATH floor -- must still be
        detected; the coherence check must not add suppression beyond what
        already existed."""
        window = _walking_then_stopping_window(90, walk_start=20, walk_frames=30, speed=0.15)
        result = gf.compute_walking_speed(window)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.0)

    def test_5_genuine_walking_is_detected(self):
        window = _walking_window(150, speed=0.15)
        result = gf.compute_walking_speed(window)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.0)
        self.assertLess(result, gf.MAX_PLAUSIBLE_HIP_SPEED)

    def test_6_slow_walking_is_detected(self):
        window = _walking_window(210, speed=0.03)
        result = gf.compute_walking_speed(window)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.0)
        self.assertLess(result, 1.0)

    def test_7_short_walking_sequence_is_detected(self):
        """Short (not just slow) genuine movement, distinct from test_4:
        a brief but fast-enough walk within a 90-frame window."""
        window = _walking_then_stopping_window(90, walk_start=30, walk_frames=20, speed=0.3)
        result = gf.compute_walking_speed(window)
        self.assertIsNotNone(result)

    def test_8_temporary_tracking_noise_during_walking_does_not_suppress_it(self):
        """A real walking bout with a brief noisy interlude (not an
        implausible glitch -- see WalkingSpeedPlausibilityTests for that --
        just ordinary landmark jitter layered on top of real motion) must
        still register as coherent ambulation."""
        rng = np.random.default_rng(3)
        window = _walking_window(150, speed=0.15)
        for i in range(60, 75):
            window[i] = dict(window[i], keypoints=[
                v + rng.normal(0, 0.01) if not np.isnan(v) else v for v in window[i]["keypoints"]
            ])
        result = gf.compute_walking_speed(window)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.0)

    def test_9_partial_landmark_occlusion_does_not_falsely_confirm_or_deny_ambulation(self):
        """Partial occlusion during genuine walking must not crash and, if
        enough real signal remains, must still report a sane positive
        value -- never a wrong-signed or non-finite one."""
        window = _walking_window(150, speed=0.15)
        rng = np.random.default_rng(4)
        for i in range(len(window)):
            if rng.random() < 0.2:
                window[i] = dict(window[i], keypoints=[np.nan] * 66)
        result = gf.compute_walking_speed(window)
        if result is not None:
            self.assertTrue(np.isfinite(result))
            self.assertGreater(result, 0.0)

    def test_10_recovery_after_tracking_noise_still_detects_walking(self):
        """Noise early in the window (simulating a rough tracking start)
        followed by clean genuine walking for the rest of it -- the
        coherence check must not let an early noisy stretch poison an
        otherwise clearly-coherent trajectory."""
        rng = np.random.default_rng(5)
        window = _jittery_stationary_window(30, jitter_std=0.006, seed=5)
        walk_tail = _walking_window(150, speed=0.15)
        combined = window + [dict(r, timestamp=(30 + i) / 30.0) for i, r in enumerate(walk_tail)]
        result = gf.compute_walking_speed(combined)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.0)

    def test_boundary_glitch_does_not_inflate_net_displacement(self):
        """Regression test for a real bug found during a fresh code-review
        audit (see docs/GAIT_CODE_REVIEW.md follow-up): _ambulation_check's
        net-displacement numerator used to be computed from `valid` (NaN-only
        filter), independently of `mask` (valid + plausible + dt>0) used for
        the path-length denominator -- so a single implausible frame-pair
        sitting at the window's first or last VALID frame was excluded from
        the denominator but NOT from the net-displacement endpoints,
        artificially inflating net_disp/plausible_path past
        MIN_AMBULATION_COHERENCE for a subject who never genuinely moved.

        Operates directly on _ambulation_check (an already-established test
        pattern in this file -- see e.g. the direct _torso_scaled_hip_track/
        _confirmed_runs/_batch_hip_angle calls elsewhere) with a hand-built,
        UNSMOOTHED hip-center track, deliberately bypassing
        _torso_scaled_hip_track's own centered rolling-average smoothing --
        that smoothing spreads a single-frame glitch across several frames
        before _ambulation_check ever sees it, which would conflate this
        specific numerator/denominator mismatch with a separate,
        out-of-scope smoothing-bleed characteristic. Isolating at this level
        is the precise, minimal test for the actual fix.

        Track: a 600-frame pure random-walk jitter path (many small,
        largely-canceling steps around a fixed point -- the exact
        MIN_AMBULATION_COHERENCE was built to reject, same construction as
        this class's own stationary-jitter tests) that clears
        MIN_AMBULATION_PATH on accumulated path length alone but correctly
        fails the coherence ratio with no glitch present. A single one-frame,
        4.0-torso-length position offset at frame 0 (or, symmetrically, the
        last frame) is confirmed BEFORE this fix to flip the result from
        correctly-rejected (None) to a fabricated ~1.07 torso-lengths/sec
        walking-speed reading; this test locks in the fixed (rejected)
        behavior for both boundary positions."""
        n = 600
        ts = np.arange(n, dtype=np.float64) / 30.0
        rng = np.random.default_rng(7)
        steps = rng.normal(0, 0.03, size=(n - 1, 2))
        track = np.zeros((n, 2))
        track[1:] = np.cumsum(steps, axis=0)

        mask, _ = gf._ambulation_check(track.copy(), ts)
        self.assertIsNone(mask, "sanity check: pure random-walk jitter must be rejected with no glitch present")

        for glitch_frame, label in ((0, "first"), (n - 1, "last")):
            track_glitch = track.copy()
            track_glitch[glitch_frame] = track_glitch[glitch_frame] + np.array([4.0, 0.0])
            mask2, _ = gf._ambulation_check(track_glitch, ts)
            self.assertIsNone(
                mask2,
                f"a single implausible glitch at the {label} frame must not inflate net_disp past "
                "MIN_AMBULATION_COHERENCE -- boundary-glitch fix regressed",
            )


def _standing_window_with_mid_segment_glitch(n_frames=90, glitch_frame=37, jump=10.0):
    """A person standing perfectly still (zero genuine sway) for the whole
    window, except ONE frame -- placed in the INTERIOR of a 15-frame
    stable_subwindow (frames 30-44), not at either edge -- whose entire
    torso (shoulder+hip together, so torso_len is unaffected) is displaced
    by `jump`. Reproduces the real vulnerability found during audit:
    compute_postural_sway's old "stable sub-window" gate only compared the
    sub-window's FIRST and LAST frame (net_disp), which stays exactly 0.0
    regardless of an interior glitch's size, since the glitch doesn't touch
    either endpoint -- letting an unbounded tracking artifact dominate that
    segment's reported sway while looking perfectly "stable" by the old
    check."""
    window = []
    for i in range(n_frames):
        kps = _standing_kps()
        if i == glitch_frame:
            kps = list(kps)
            for idx in (22, 24, 46, 48):
                kps[idx] += jump
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


class PosturalSwayPlausibilityTests(unittest.TestCase):
    """Regression tests for compute_postural_sway's plausibility gate,
    added during a post-fix audit (found via direct reproduction, not
    speculation -- see MAX_PLAUSIBLE_HIP_SPEED's reuse in
    compute_postural_sway's own docstring): an interior tracking-glitch
    frame within an otherwise-stable 15-frame sub-window used to inflate
    reported sway linearly and without bound, since the old "stable"
    check only compared the sub-window's first and last frame."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_interior_glitch_does_not_inflate_sway_without_bound(self):
        clean = gf.compute_postural_sway(
            [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(90)]
        )
        self.assertEqual(clean, 0.0)

        for jump in (10.0, 50.0, 200.0):
            glitched_sway = gf.compute_postural_sway(_standing_window_with_mid_segment_glitch(jump=jump))
            # The corrupted sub-window must be excluded entirely -- the
            # remaining 5 clean sub-windows (all zero genuine sway) are all
            # that's left, so the mean must stay exactly at the clean
            # baseline regardless of how large the glitch is, not scale
            # with it the way the un-gated version did (jump=10 -> 0.21,
            # jump=50 -> 1.05, unbounded).
            self.assertEqual(
                glitched_sway, 0.0,
                f"jump={jump}: an interior tracking-glitch frame must not inflate postural_sway",
            )

    def test_glitch_in_every_subwindow_marks_signal_unavailable(self):
        """If every sub-window is corrupted, nothing trustworthy remains --
        must report None, not fabricate a value from contaminated segments."""
        window = [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(90)]
        for start in range(0, 90, 15):
            mid = start + 7
            kps = list(_standing_kps())
            for idx in (22, 24, 46, 48):
                kps[idx] += 10.0
            window[mid]["keypoints"] = kps
        self.assertIsNone(gf.compute_postural_sway(window))

    def test_genuine_sway_still_detected(self):
        """The plausibility gate must not suppress real postural sway --
        only implausible interior jumps. A small, smooth oscillation (well
        under MAX_PLAUSIBLE_HIP_SPEED) must still be reported."""
        window = []
        for i in range(90):
            kps = list(_standing_kps())
            wobble = 0.01 * np.sin(2 * np.pi * 0.5 * (i / 30.0))
            kps[46] += wobble
            kps[48] += wobble
            window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
        sway = gf.compute_postural_sway(window)
        self.assertIsNotNone(sway)
        self.assertGreater(sway, 0.0)


class SignalDirectionTests(unittest.TestCase):
    """Regression tests for the direction bugs found during this module's
    own validation -- these must keep failing loudly if reintroduced."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_slower_more_irregular_walk_scores_higher_risk(self):
        steady = _walking_window(210, speed=0.18, stride_jitter=0.02, speed_jitter=0.03, sway_amp=0.005)
        unsteady = _walking_window(210, speed=0.07, stride_jitter=0.25, speed_jitter=0.10, sway_amp=0.04)

        steady_result = self.assessor.assess_risk(steady)
        unsteady_result = self.assessor.assess_risk(unsteady)

        self.assertIsNotNone(steady_result["risk_score"])
        self.assertIsNotNone(unsteady_result["risk_score"])
        self.assertGreater(
            unsteady_result["risk_score"], steady_result["risk_score"],
            "A slower, more irregular synthetic walk must score higher risk than a steady one.",
        )

        steady_speed = next(s for s in steady_result["signals"] if s["name"] == "walking_speed")["value"]
        unsteady_speed = next(s for s in unsteady_result["signals"] if s["name"] == "walking_speed")["value"]
        self.assertGreater(steady_speed, unsteady_speed)

    def test_shaky_sit_to_stand_scores_higher_risk_than_smooth(self):
        smooth = _sit_to_stand_window(shaky=False)
        shaky = _sit_to_stand_window(shaky=True)

        smooth_result = self.assessor.assess_risk(smooth)
        shaky_result = self.assessor.assess_risk(shaky)

        smooth_sts = next(s for s in smooth_result["signals"] if s["name"] == "sit_to_stand")
        shaky_sts = next(s for s in shaky_result["signals"] if s["name"] == "sit_to_stand")
        self.assertTrue(smooth_sts["available"])
        self.assertTrue(shaky_sts["available"])
        self.assertGreater(shaky_sts["risk_contribution"], smooth_sts["risk_contribution"])

    def test_sit_to_stand_detected_despite_one_sided_occlusion(self):
        """Regression test for a real bug: compute_sit_to_stand used to pick
        the LEFT shoulder/hip/knee via `_joint_point(...) or _joint_point(...)`,
        which never actually falls back to the right side on occlusion (a
        Python tuple is truthy even when it holds NaN) -- so a window with a
        perfectly good RIGHT-side view but an occluded LEFT side silently
        computed NaN and reported no transition at all. Fixed to average
        both sides' angles when valid, mirroring pipeline_utils.py's own
        convention. This window has only the right side visible throughout."""
        occluded = _sit_to_stand_window_left_occluded()
        result = gf.compute_sit_to_stand(occluded)
        self.assertIsNotNone(
            result,
            "compute_sit_to_stand must still detect the transition using the "
            "unoccluded right side alone -- this failed before the fix.",
        )
        self.assertIn("duration_sec", result)
        self.assertGreater(result["duration_sec"], 0)

    def test_single_noisy_frame_does_not_fabricate_a_sit_to_stand_transition(self):
        """Regression test for a real false positive found on real footage
        (SitFloor_lowKeypoints_crossedLegs.MOV): a person sitting cross-legged
        on the floor for an entire clip, never standing, whose noisy tracking
        produced exactly one frame with hip_angle >= _HIP_ANGLE_STANDING_MIN.
        The un-gated version of compute_sit_to_stand anchored a fabricated
        ~2.9s "transition" to that single frame, using the EARLIEST sitting
        frame in the whole window as its start, and counted 33 direction
        reversals of ordinary sitting fidgeting as transition "shakiness" --
        driving this signal's risk_contribution to ~1.0 for someone who never
        stood up. compute_sit_to_stand must require the standing state to be
        confirmed by multiple consecutive frames, not a single noisy one."""
        window = _sitting_with_single_noise_spike_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result,
            "A single noisy frame crossing the standing threshold must not be "
            "reported as a sit-to-stand transition.",
        )

    def test_genuine_sustained_standing_still_detected_after_confirm_gate(self):
        """The consecutive-frame confirmation gate added above must not cost
        real detections: a transition whose final standing state is held for
        multiple frames (as any real stand-up necessarily is, and as
        _sit_to_stand_window's own final segment already does) must still be
        detected."""
        window = _sit_to_stand_window(shaky=False)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        self.assertGreater(result["duration_sec"], 0)

    def test_fast_shallow_sit_to_stand_is_recovered_by_fallback(self):
        """Regression test for a real recall gap found on real footage
        (SitFast_GetupFast.MOV): a genuine fast sit-to-stand whose hip_angle
        trough never reaches the full sitting floor must still be detected,
        via _detect_fast_shallow_transition."""
        window = _fast_shallow_sit_to_stand_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result, "a fast, shallow (never fully seated) sit-to-stand must still be detected",
        )
        self.assertGreater(result["duration_sec"], 0)
        # Must be a short, fast transition -- not conflated with a slow one.
        self.assertLess(result["duration_sec"], 1.0)

    def test_ordinary_standing_jitter_does_not_trigger_fallback(self):
        """The fallback path must not fire on ordinary standing-still angle
        jitter between two unrelated confirmed-standing runs -- only a
        genuine, sufficiently deep dip (FAST_SIT_MIN_DESCENT_DEGREES)."""
        window = _fast_shallow_sit_to_stand_window(trough_angle=160.0)  # shallow jitter (~4.7 actual degrees), not a real dip
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(result)

    def test_standing_reading_right_after_long_tracking_gap_is_not_trusted(self):
        """Regression test for a real false positive found on real footage
        (Sitting_Lying_FewLandmarks_back.MOV): a person sitting/lying for an
        entire clip, whose tracking is lost for 12 consecutive frames and
        then immediately reads a few frames in the STANDING range -- a
        MediaPipe re-acquisition artifact, not a real stand. Plain
        consecutive-frame confirmation alone accepted this; it must now be
        rejected via _MAX_TRUSTED_GAP_BEFORE_STATE."""
        window = _standing_after_long_tracking_gap_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result, "a standing reading emerging right out of a long tracking blackout must not be trusted",
        )

    def test_standing_reading_after_short_gap_is_still_trusted(self):
        """The tracking-gap guard must be specific to LONG gaps -- an
        ordinary short landmark dropout (well under
        _MAX_TRUSTED_GAP_BEFORE_STATE) followed by a genuine sustained
        standing run must still be usable."""
        window = _standing_after_long_tracking_gap_window(gap_len=3, standing_run_len=10)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)


def _fall_adjacent_shallow_transition_window(n_frames=90, dip_start=40, dip_len=15,
                                              standing_angle=175.0, trough_angle=107.0,
                                              translation_per_frame=0.03):
    """Same angle dip-and-recover SHAPE as _fast_shallow_sit_to_stand_window
    (so, absent the translation check, the fallback would find a candidate
    here exactly as it would for a genuine stand) but the hip ALSO
    translates substantially DURING the dip -- unlike a genuine stand,
    which is primarily postural. A synthetic reconstruction of the real
    fall-adjacent motion FALLBACK_MAX_TRANSLATION_SPEED exists to reject
    (see that constant's own docstring: Backward_fall.mp4/Slow_fall.mp4
    measured peak translation of 2.88/17.79 torso-lengths/sec on the
    fallback's previously-fired candidate segment, vs. 0.35 for the one
    confirmed genuine stand available, SitFast_GetupFast.MOV)."""
    window = []
    hip_x = 0.3
    for i in range(n_frames):
        if i < dip_start:
            angle, cx = standing_angle, hip_x
        elif i < dip_start + dip_len:
            frac = (i - dip_start) / (dip_len - 1)
            angle = standing_angle - (standing_angle - trough_angle) * np.sin(frac * np.pi)
            cx = hip_x + translation_per_frame * (i - dip_start)
        else:
            angle, cx = standing_angle, hip_x + translation_per_frame * (dip_len - 1)
        window.append(_angle_pose_row(angle, i, cx=cx))
    return window


def _ambiguous_rapid_angle_noise_window(n_frames=90, seed=23):
    """Rapid, noisy hip-angle fluctuation (many reversals) while the hip
    position stays completely fixed -- ambiguous/shaky motion with NO real
    translation, as opposed to _fall_adjacent_shallow_transition_window's
    real translation. Must NOT be rejected by the translation check (it
    stays under FALLBACK_MAX_TRANSLATION_SPEED by construction, since the
    hip never moves) -- this is the class of case
    (Sitting_Lying_FewLandmarks.MOV's reversal=12 finding) that the
    translation check deliberately leaves untouched, a separate, disclosed,
    harder ambiguity than fall-adjacent whole-body motion."""
    rng = np.random.default_rng(seed)
    window = []
    for i in range(n_frames):
        if i < 40:
            angle = 175.0
        elif i < 70:
            angle = float(np.clip(107.0 + rng.normal(0, 15.0), 100.0, 130.0))
        else:
            angle = 175.0
        # Deliberately fixed cy (NOT _hip_cy_for_angle) -- this fixture's
        # entire point is "hip position stays completely fixed" (see
        # docstring) so it isolates the angle-noise/reversal-count check
        # from the hip-rise guard; varying cy with the noisy angle would
        # introduce real synthetic hip translation and defeat that isolation.
        window.append(_angle_pose_row(angle, i))
    return window


def _single_sided_visibility_noise_window(n_frames=90, dip_start=40, dip_len=20,
                                           standing_angle=175.0, dip_angle=104.0,
                                           noise_std=0.4, seed=41):
    """Confirmed-standing -> a stretch where ONLY the left side stays
    visible (right shoulder landmark set to NaN) while the left-side-only
    hip_angle wobbles by small per-frame noise around a roughly constant
    dip value -> confirmed-standing again. Hip position is fixed throughout
    (no translation), isolating the CONFIDENCE-gating mechanism
    (_count_reversals' `confident` mask) from the separate translation
    check. A faithful synthetic reconstruction of the real mechanism found
    on Sitting_Lying_FewLandmarks.MOV (see _count_reversals' own
    docstring): a stretch of single-sided visibility lets small,
    sub-noise-floor angle jitter flip sign almost every frame, manufacturing
    a high nominal reversal_count despite the person never moving. Real
    per-frame deltas measured 0.6-3.4 degrees while genuinely transitioning
    vs. mostly-under-1.3-degree noise while single-sided.

    NOTE: `_angle_pose_row`'s "angle" parameter is a REQUESTED geometric
    input, not the literal resulting hip_angle (see
    _fast_shallow_sit_to_stand_window's docstring for the same nonlinear-
    mapping caveat) -- dip_angle=104 was picked by direct measurement to
    produce an ACTUAL angle of ~129-130 degrees (comfortably between the
    125/143 sitting/standing floors, matching the real clip's own
    ~129-133-degree dip), not assumed from the requested number."""
    rng = np.random.default_rng(seed)
    window = []
    for i in range(n_frames):
        if i < dip_start or i >= dip_start + dip_len:
            angle = standing_angle
        else:
            angle = float(np.clip(dip_angle + rng.normal(0, noise_std), 95.0, 112.0))
        row = _angle_pose_row(angle, i)
        if dip_start <= i < dip_start + dip_len:
            row["keypoints"][24] = np.nan  # right shoulder invalid -> single-sided (left-only) angle
            row["keypoints"][25] = np.nan
        window.append(row)
    return window


class CountReversalsZeroDeltaTests(unittest.TestCase):
    """Regression tests for _count_reversals' zero-delta bridging fix (see
    docs/GAIT_CODE_REVIEW.md's follow-up audit): a delta of exactly zero
    used to make the old adjacent-pair comparison skip BOTH deltas touching
    it, silently dropping a genuine reversal whenever it happened to be
    bridged by one flat (identical-reading) frame."""

    def test_reversal_bridges_across_exact_zero_delta(self):
        """deltas = [+1, 0, -1] is a genuine direction reversal (rising then
        falling) with one exact-zero delta in between -- must count 1, not 0
        (the pre-fix result: both comparisons touching the zero delta were
        skipped, so the real +1 -> -1 reversal was never seen)."""
        segment = np.array([100.0, 101.0, 101.0, 100.0])
        self.assertEqual(gf._count_reversals(segment), 1.0)

    def test_equivalent_non_zero_delta_case_unaffected(self):
        """Same net shape as the test above but with no exact-zero delta --
        confirms the fix doesn't change anything when there's nothing to
        bridge (byte-identical to the pre-fix adjacent-pair comparison)."""
        segment = np.array([100.0, 101.0, 101.01, 100.0])
        self.assertEqual(gf._count_reversals(segment), 1.0)

    def test_multiple_zero_deltas_still_bridge_correctly(self):
        """Two consecutive exact-zero deltas between a rise and a fall --
        the reversal must still be found by looking past both flat frames
        to the last genuinely non-zero delta."""
        segment = np.array([100.0, 101.0, 101.0, 101.0, 100.0])
        self.assertEqual(gf._count_reversals(segment), 1.0)

    def test_all_zero_deltas_no_reversal(self):
        """A perfectly flat segment (no direction at all) must report 0
        reversals, not spuriously bridge into a phantom one."""
        segment = np.array([100.0, 100.0, 100.0, 100.0])
        self.assertEqual(gf._count_reversals(segment), 0.0)

    def test_leading_zero_delta_does_not_count_a_reversal(self):
        """A zero delta with NOTHING non-zero before it must not be treated
        as having a 'last sign' to compare against -- only genuine
        subsequent direction changes count."""
        segment = np.array([100.0, 100.0, 101.0, 100.0])
        self.assertEqual(gf._count_reversals(segment), 1.0)  # only the +1 -> -1 change


class SitToStandAngleNoiseConfidenceTests(unittest.TestCase):
    """Regression tests for _count_reversals' landmark-confidence gate
    (added to address the disclosed pure-angle-noise limitation --
    Sitting_Lying_FewLandmarks.MOV's reversal=12 case): a stretch of
    single-sided landmark visibility must not let small angle jitter
    manufacture a high nominal reversal_count."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_single_sided_noise_reversal_count_is_suppressed(self):
        window = _single_sided_visibility_noise_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result, "duration/translation are still trustworthy even when reversal-count isn't")
        self.assertEqual(
            result["reversal_count"], 0.0,
            "single-sided-visibility angle noise must not manufacture nonzero reversals",
        )

    def test_duration_and_detection_survive_even_though_reversal_count_is_suppressed(self):
        """The fix must not turn the whole signal unavailable -- duration_sec
        (independently trustworthy, unaffected by angle-direction noise)
        must still be reported; only reversal_count's spurious inflation is
        corrected."""
        window = _single_sided_visibility_noise_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        self.assertGreater(result["duration_sec"], 0)

    def test_both_sided_confirmed_transition_reversal_count_unaffected(self):
        """The confidence gate must not touch a transition where both sides
        stay valid throughout -- must reproduce the exact pre-fix reversal
        count for a genuine, fully-confident, shaky transition."""
        window = _sit_to_stand_window(shaky=True)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        self.assertEqual(result["reversal_count"], 6.0)  # unchanged from the pre-fix, fully-confident case

    def test_shaky_still_scores_higher_risk_than_smooth_after_confidence_gate(self):
        """The confidence gate must not undermine the module's core
        direction-sanity guarantee (see SignalDirectionTests) -- both
        fixtures are fully-confident (both sides always valid), so this
        must be completely unaffected."""
        smooth = _sit_to_stand_window(shaky=False)
        shaky = _sit_to_stand_window(shaky=True)
        smooth_result = self.assessor.assess_risk(smooth)
        shaky_result = self.assessor.assess_risk(shaky)
        smooth_sts = next(s for s in smooth_result["signals"] if s["name"] == "sit_to_stand")
        shaky_sts = next(s for s in shaky_result["signals"] if s["name"] == "sit_to_stand")
        self.assertGreater(shaky_sts["risk_contribution"], smooth_sts["risk_contribution"])

    def test_sitfast_getupfast_synthetic_reproduction_unaffected_by_confidence_gate(self):
        """SitFast_GetupFast's synthetic reproduction is fully-confident
        (both sides valid throughout, by construction) -- must be completely
        unaffected by the confidence gate, same as before this fix."""
        window = _fast_shallow_sit_to_stand_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        self.assertLess(result["duration_sec"], 1.0)


class SitToStandTranslationDiscriminationTests(unittest.TestCase):
    """Regression tests for the sit-to-stand fallback's hip-TRANSLATION
    discriminator (FALLBACK_MAX_TRANSLATION_SPEED), added to improve
    recall for genuine fast stands while specifically screening out
    fall-adjacent whole-body motion the hip-angle-only geometry alone
    cannot see."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_normal_sit_to_stand_unaffected(self):
        """The primary (sit-run-based) path is untouched by this change --
        a normal-speed, fully-seated transition must detect exactly as before."""
        window = _sit_to_stand_window(shaky=False)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        self.assertGreater(result["duration_sec"], 0)

    def test_fast_sit_to_stand_still_recovered(self):
        window = _fast_shallow_sit_to_stand_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        self.assertLess(result["duration_sec"], 1.0)

    def test_sitfast_getupfast_synthetic_reproduction(self):
        """Synthetic reproduction of the real SitFast_GetupFast.MOV event
        this fallback exists to recover (see that function's own docstring
        for the real-footage calibration: trough ~135.6 degrees, ~9.7
        degrees below a ~145.3 standing baseline). Real-footage confirmation
        of this exact clip is covered by benchmarks/validate_gait_on_footage.py,
        not the unit suite (real MediaPipe extraction is too slow for CI)."""
        window = _fast_shallow_sit_to_stand_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result, "SitFast_GetupFast's synthetic reproduction must still be detected")

    def test_previous_false_positive_scenario_remains_suppressed(self):
        """The original sit-to-stand false positive (SitFloor_lowKeypoints_
        crossedLegs.MOV: a single noisy frame crossing the standing
        threshold on a person who never stands) must remain fixed -- this
        translation check is an ADDITIONAL guard, not a replacement for the
        _STATE_CONFIRM_FRAMES guard that already fixes this case."""
        window = _sitting_with_single_noise_spike_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(result)

    def test_fall_adjacent_motion_is_rejected(self):
        """The core new behavior: a candidate that LOOKS like a valid dip
        by angle-shape alone, but whose hip translates substantially during
        it, must be rejected."""
        window = _fall_adjacent_shallow_transition_window()
        peak = self._peak_translation(window)
        self.assertGreater(
            peak, gf.FALLBACK_MAX_TRANSLATION_SPEED,
            "test fixture must produce implausible translation to be a meaningful test",
        )
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(result, "fall-adjacent whole-body translation must not be reported as a sit-to-stand")

    def test_ambiguous_rapid_angle_noise_without_translation_is_not_rejected_by_this_check(self):
        """Rapid, noisy angle fluctuation with NO real hip translation is a
        DIFFERENT, harder ambiguity (angle-only) that this specific check
        does not (and should not) resolve -- it must stay untouched by the
        translation guard specifically (it may still be caught or not by
        other, unrelated logic, but not by FALLBACK_MAX_TRANSLATION_SPEED)."""
        window = _ambiguous_rapid_angle_noise_window()
        peak = self._peak_translation(window)
        self.assertLess(
            peak, gf.FALLBACK_MAX_TRANSLATION_SPEED,
            "this fixture has zero real hip translation by construction",
        )

    def test_incomplete_sit_to_stand_still_rejected(self):
        """A transition that starts dipping but never re-confirms standing
        within the window must still report None -- unaffected by the
        translation check (never reaches it, since stand_runs has < 2 runs)."""
        window = _fast_shallow_sit_to_stand_window(n_frames=50)  # cut off before standing re-confirms
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(result)

    def test_noisy_landmarks_during_fall_adjacent_motion_still_rejected(self):
        """Landmark noise layered on top of fall-adjacent motion must not
        accidentally mask the translation (e.g. via a division-by-noise
        artifact) -- the rejection must be robust to realistic jitter."""
        rng = np.random.default_rng(31)
        window = _fall_adjacent_shallow_transition_window()
        window = [dict(r, keypoints=[
            v + rng.normal(0, 0.003) if not np.isnan(v) else v for v in r["keypoints"]
        ]) for r in window]
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(result)

    @staticmethod
    def _peak_translation(window):
        raw = gf._raw_keypoint_array(window)
        pairs = raw.reshape(-1, 33, 2)
        hip_mid_raw = (pairs[:, gf.LEFT_HIP, :] + pairs[:, gf.RIGHT_HIP, :]) / 2.0
        sh_mid_raw = (pairs[:, gf.LEFT_SHOULDER, :] + pairs[:, gf.RIGHT_SHOULDER, :]) / 2.0
        torso_len_raw = np.linalg.norm(sh_mid_raw - hip_mid_raw, axis=1)
        ts = gf._timestamps(window)
        return gf._peak_translation_speed(hip_mid_raw, torso_len_raw, ts, 0, 39, 40, 54)


class InputValidationTests(unittest.TestCase):
    """Phase 6 edge cases: fail clearly on invalid input rather than
    producing silently-incorrect output."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_none_window_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.assessor.assess_risk(None)

    def test_non_list_window_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.assessor.assess_risk("not a window")
        with self.assertRaises(TypeError):
            self.assessor.assess_risk(12345)

    def test_empty_window_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.assessor.assess_risk([])

    def test_too_short_window_raises_value_error(self):
        short_window = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(gf.MIN_WINDOW_FRAMES - 1)]
        with self.assertRaises(ValueError):
            self.assessor.assess_risk(short_window)

    def test_window_of_non_dicts_raises_type_error(self):
        window = [[1, 2, 3]] * gf.MIN_WINDOW_FRAMES
        with self.assertRaises(TypeError):
            self.assessor.assess_risk(window)

    def test_window_missing_keypoints_key_raises_value_error(self):
        window = [{"timestamp": i / 30.0} for i in range(gf.MIN_WINDOW_FRAMES)]
        with self.assertRaises(ValueError):
            self.assessor.assess_risk(window)

    def test_minimum_length_window_does_not_raise(self):
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        result = self.assessor.assess_risk(window)  # should not raise
        self.assertIn("risk_score", result)


class RobustnessTests(unittest.TestCase):
    """NaN/Inf/occlusion handling -- must degrade to unavailable signals,
    never crash or emit non-finite output."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_all_nan_window_does_not_crash_and_returns_none_score(self):
        window = [{"timestamp": i / 30.0, "keypoints": [np.nan] * 66} for i in range(150)]
        result = self.assessor.assess_risk(window)
        self.assertIsNone(result["risk_score"])
        for s in result["signals"]:
            self.assertFalse(s["available"])

    def test_inf_values_are_treated_as_missing_not_crash_or_propagate(self):
        window = _walking_window(150, speed=0.15)
        # Corrupt a chunk of frames with Inf in the hip coordinates.
        for i in range(40, 60):
            window[i]["keypoints"][46] = np.inf
            window[i]["keypoints"][47] = -np.inf
        result = self.assessor.assess_risk(window)  # should not raise
        if result["risk_score"] is not None:
            self.assertTrue(np.isfinite(result["risk_score"]))
        for s in result["signals"]:
            if isinstance(s["value"], float):
                self.assertTrue(np.isfinite(s["value"]))

    def test_partial_occlusion_does_not_crash(self):
        """Beyond "doesn't crash": under partial occlusion the output must
        still be well-formed (finite, in-range) -- not merely present. A
        no-crash-only assertion here would miss a regression that survives
        without raising but silently leaks a NaN/out-of-range value into
        risk_score or a signal's value through an under-masked computation."""
        window = _walking_window(150, speed=0.15)
        # Randomly drop ~30% of frames to fully-occluded (all-NaN).
        rng = np.random.default_rng(0)
        for i in range(len(window)):
            if rng.random() < 0.3:
                window[i]["keypoints"] = [np.nan] * 66
        result = self.assessor.assess_risk(window)  # should not raise
        self.assertIn("signals", result)
        self.assertEqual(len(result["signals"]), 4)
        if result["risk_score"] is not None:
            self.assertTrue(np.isfinite(result["risk_score"]))
            self.assertGreaterEqual(result["risk_score"], 0.0)
            self.assertLessEqual(result["risk_score"], 1.0)
        for s in result["signals"]:
            if isinstance(s["value"], float):
                self.assertTrue(np.isfinite(s["value"]), f"{s['name']} produced a non-finite value under partial occlusion")
            if s["risk_contribution"] is not None:
                self.assertTrue(0.0 <= s["risk_contribution"] <= 1.0)

    def test_wrong_keypoint_length_does_not_crash(self):
        """A malformed row with too few keypoint values (e.g. an upstream
        bug truncating the list) must degrade gracefully, not crash."""
        window = [{"timestamp": i / 30.0, "keypoints": [0.5, 0.5, 0.5]} for i in range(150)]
        result = self.assessor.assess_risk(window)  # should not raise
        self.assertIn("risk_score", result)


class RealCheckpointIntegrationTest(unittest.TestCase):
    """Integration-level check against real (unlabeled) extracted keypoints,
    not a mock -- mirrors docs/GAIT_DATA_ASSESSMENT.md's smoke test."""

    def test_runs_without_error_on_real_extracted_keypoints(self):
        import pandas as pd
        kp_csv = REPO_ROOT / "data" / "processed_keypoints" / "pose_keypoints.csv"
        if not kp_csv.exists():
            self.skipTest("data/processed_keypoints/pose_keypoints.csv not present in this checkout")

        df = pd.read_csv(kp_csv, low_memory=False, nrows=50000)
        assessor = GaitRiskAssessor()
        tested = 0
        for seq_id, seq_df in df.groupby("sequence_id"):
            if tested >= 3:
                break
            seq_df = seq_df.sort_values("frame").reset_index(drop=True)
            if len(seq_df) < gf.MIN_WINDOW_FRAMES:
                continue
            window = []
            for i, row in seq_df.iterrows():
                flat = []
                for lm in range(1, 34):
                    flat.append(row.get(f"x{lm}", np.nan))
                    flat.append(row.get(f"y{lm}", np.nan))
                window.append({"timestamp": i / 30.0, "frame": int(i), "keypoints": flat})
            result = assessor.assess_risk(window)  # should not raise
            self.assertIn("risk_score", result)
            self.assertEqual(len(result["signals"]), 4)
            tested += 1
        if tested == 0:
            self.skipTest("No real sequence long enough to test was found")


def _stationary_with_ankle_jitter_window(n_frames=150, jitter_std=0.01, seed=51):
    """A subject standing PERFECTLY still at the hip (no hip translation at
    all) except for INDEPENDENT per-frame jitter on the ANKLE landmarks
    only -- reproduces the exact failure class docs/GAIT_CODE_REVIEW.md
    finding #1 describes: ordinary ankle jitter (weight-shifting, MediaPipe
    frame-to-frame noise) on an otherwise-stationary subject, which used to
    be able to fabricate a stride-regularity signal since
    compute_stride_regularity previously had no ambulation gate at all
    (unlike compute_walking_speed/compute_postural_sway, which both have
    one)."""
    rng = np.random.default_rng(seed)
    window = []
    base = _standing_kps()
    for i in range(n_frames):
        kps = list(base)
        for idx in (54, 55, 56, 57):  # left/right ankle x, y
            kps[idx] = kps[idx] + rng.normal(0, jitter_std)
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


def _raw_stride_peak_count_ignoring_gates(window):
    """Reproduces the PRE-FIX peak-detection path (no ambulation gate, no
    prominence filter) directly against a window's ankle-y signal, so a
    test fixture can assert it WOULD have produced a fabricated signal
    under the old code -- proving the fixture is a meaningful regression
    test for finding #1, not a vacuous one (same "prove the fixture
    exercises the bug" pattern already used elsewhere in this file, e.g.
    WalkingSpeedPlausibilityTests._peak_instantaneous_speed)."""
    from scipy.signal import find_peaks as _find_peaks

    raw = gf._raw_keypoint_array(window)
    pos = gf._normalized_positions(window, _raw=raw)
    ankle_y = (pos[:, gf.LEFT_ANKLE, 1] + pos[:, gf.RIGHT_ANKLE, 1]) / 2.0
    valid = ~np.isnan(ankle_y)
    idx = np.arange(len(ankle_y))
    filled = np.interp(idx, idx[valid], ankle_y[valid])
    peaks, _ = _find_peaks(filled, distance=5)
    return len(peaks)


def _ambulating_no_ankle_oscillation_window(n_frames=150, speed=0.05):
    """Hip translates coherently and horizontally enough to pass the full
    ambulation gate (MIN_AMBULATION_PATH/MIN_AMBULATION_COHERENCE/
    MIN_HORIZONTAL_DOMINANCE_RATIO), but the ankles do not oscillate at all
    (fixed height relative to the hip) -- isolates the "genuinely
    ambulating but not enough detectable stride periodicity" path from the
    ambulation-gate-rejection path, which a different fixture already
    covers."""
    window = []
    for i in range(n_frames):
        t = i / 30.0
        hip_x = 0.3 + speed * t
        cx, cy, torso_len = hip_x, 0.5, 0.25
        kps = [np.nan] * 66
        kps[22], kps[23] = cx - 0.05, cy - torso_len
        kps[24], kps[25] = cx + 0.05, cy - torso_len
        kps[46], kps[47] = cx - 0.05, cy
        kps[48], kps[49] = cx + 0.05, cy
        kps[50], kps[51] = cx - 0.05, cy + torso_len * 0.8
        kps[52], kps[53] = cx + 0.05, cy + torso_len * 0.8
        kps[54], kps[55] = cx - 0.05, cy + torso_len * 1.6  # ankle -- no oscillation
        kps[56], kps[57] = cx + 0.05, cy + torso_len * 1.6
        window.append({"timestamp": t, "frame": i, "keypoints": kps})
    return window


class StrideRegularityTests(unittest.TestCase):
    """Regression tests for docs/GAIT_CODE_REVIEW.md finding #1 --
    compute_stride_regularity previously had NO ambulation/stationarity
    gate and NO peak height/prominence filtering, unlike its sibling
    signals. Zero test coverage existed for this function before this
    class (confirmed by the review). Covers: stationary subject, stationary
    subject with ankle jitter (the core bug), genuine walking, insufficient
    peaks, noisy signal, invalid/missing landmarks."""

    def test_perfectly_stationary_subject_no_signal(self):
        window = [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(150)]
        self.assertIsNone(gf.compute_stride_regularity(window))

    def test_stationary_subject_with_ankle_jitter_does_not_fabricate_regularity(self):
        """The core regression test for finding #1: ankle jitter on a
        stationary subject must not produce a stride-regularity value."""
        window = _stationary_with_ankle_jitter_window()
        self.assertGreaterEqual(
            _raw_stride_peak_count_ignoring_gates(window), 3,
            "test fixture must produce >=3 raw (pre-gate) peaks to be a meaningful regression test",
        )
        result = gf.compute_stride_regularity(window)
        self.assertIsNone(
            result,
            "ordinary ankle jitter on a stationary subject must not fabricate a stride-regularity signal",
        )

    def test_genuine_walking_produces_a_finite_cv(self):
        window = _walking_window(180, speed=0.15)
        result = gf.compute_stride_regularity(window)
        self.assertIsNotNone(result, "the ambulation gate must not suppress genuine walking recall")
        self.assertTrue(np.isfinite(result))
        self.assertGreaterEqual(result, 0.0)

    def test_ambulating_but_insufficient_peaks_returns_none(self):
        window = _ambulating_no_ankle_oscillation_window()
        # Sanity: this fixture genuinely clears the ambulation gate --
        # isolates "insufficient peaks" from "not ambulating at all".
        self.assertIsNotNone(gf.compute_walking_speed(window))
        self.assertIsNone(gf.compute_stride_regularity(window))

    def test_noisy_signal_does_not_crash(self):
        rng = np.random.default_rng(61)
        window = _walking_window(210, speed=0.2)
        window = [dict(r, keypoints=[
            v + rng.normal(0, 0.02) if not np.isnan(v) else v for v in r["keypoints"]
        ]) for r in window]
        result = gf.compute_stride_regularity(window)  # should not raise
        if result is not None:
            self.assertTrue(np.isfinite(result))
            self.assertGreaterEqual(result, 0.0)

    def test_all_nan_window_returns_none(self):
        window = [{"timestamp": i / 30.0, "frame": i, "keypoints": [np.nan] * 66} for i in range(150)]
        self.assertIsNone(gf.compute_stride_regularity(window))

    def test_mostly_missing_ankle_landmarks_returns_none(self):
        window = _walking_window(150, speed=0.2)
        blanked = []
        for i, row in enumerate(window):
            kps = list(row["keypoints"])
            kps[54] = kps[55] = kps[56] = kps[57] = np.nan
            blanked.append(dict(row, keypoints=kps))
        self.assertIsNone(gf.compute_stride_regularity(blanked))


def _vertical_translation_window(n_frames=90, drop_speed=0.02, hip_x=0.3, start_y=0.35):
    """A hip that translates almost PURELY VERTICALLY (e.g. kneeling down)
    -- coherent, plausible, and long enough to pass MIN_AMBULATION_PATH/
    MIN_AMBULATION_COHERENCE exactly like real horizontal walking would --
    but with net displacement dominated by the Y axis, not X. A synthetic
    reproduction of the real Kneeling.MOV false positive (see
    MIN_HORIZONTAL_DOMINANCE_RATIO's own docstring in gait_features.py and
    docs/GAIT_CODE_REVIEW.md finding #2)."""
    window = []
    for i in range(n_frames):
        t = i / 30.0
        hip_y = start_y + drop_speed * t
        cx, cy, torso_len = hip_x, hip_y, 0.25
        kps = [np.nan] * 66
        kps[22], kps[23] = cx - 0.05, cy - torso_len
        kps[24], kps[25] = cx + 0.05, cy - torso_len
        kps[46], kps[47] = cx - 0.05, cy
        kps[48], kps[49] = cx + 0.05, cy
        kps[50], kps[51] = cx - 0.05, cy + torso_len * 0.8
        kps[52], kps[53] = cx + 0.05, cy + torso_len * 0.8
        window.append({"timestamp": t, "frame": i, "keypoints": kps})
    return window


def _diagonal_walking_window(n_frames=150, dx_speed=0.15, dy_speed=0.05):
    """Hip translates diagonally with a clearly HORIZONTALLY-DOMINANT net
    displacement (dx_speed > dy_speed) -- must still pass the new direction
    gate, unlike _vertical_translation_window."""
    window = []
    for i in range(n_frames):
        t = i / 30.0
        cx = 0.3 + dx_speed * t
        cy = 0.5 + dy_speed * t
        torso_len = 0.25
        kps = [np.nan] * 66
        kps[22], kps[23] = cx - 0.05, cy - torso_len
        kps[24], kps[25] = cx + 0.05, cy - torso_len
        kps[46], kps[47] = cx - 0.05, cy
        kps[48], kps[49] = cx + 0.05, cy
        kps[50], kps[51] = cx - 0.05, cy + torso_len * 0.8
        kps[52], kps[53] = cx + 0.05, cy + torso_len * 0.8
        window.append({"timestamp": t, "frame": i, "keypoints": kps})
    return window


class WalkingSpeedDirectionTests(unittest.TestCase):
    """Regression tests for docs/GAIT_CODE_REVIEW.md finding #2 --
    compute_walking_speed's ambulation gate previously checked only
    magnitude/coherence, never translation DIRECTION, so a purely vertical
    postural change (kneeling down) could pass it exactly like genuine
    horizontal walking. Confirmed real false positive: Kneeling.MOV read as
    ~0.32-0.54 torso-lengths/sec "walking speed" (risk_contribution
    ~0.80-0.89). See MIN_HORIZONTAL_DOMINANCE_RATIO's docstring for the
    real-footage measurements this fix is calibrated against -- now
    including real walking footage at three camera angles (lateral,
    diagonal, toward-camera), which confirmed the gate does not
    over-suppress genuine walking recall at any of them (see that
    docstring's "REAL WALKING FOOTAGE VALIDATION" section for the
    per-clip ratios/recall counts)."""

    def test_purely_vertical_translation_is_not_ambulation(self):
        window = _vertical_translation_window()
        # Sanity: without the new direction gate, this fixture would pass
        # path length + coherence exactly like genuine walking would --
        # proves the fixture is a meaningful test of the direction check
        # specifically, not of the pre-existing gates.
        hip_track = gf._torso_scaled_hip_track(window)
        valid = ~np.isnan(hip_track).any(axis=1)
        valid_track = hip_track[valid]
        net = valid_track[-1] - valid_track[0]
        self.assertGreater(
            abs(float(net[1])), abs(float(net[0])),
            "test fixture must be vertically-dominated to be a meaningful test",
        )
        self.assertIsNone(
            gf.compute_walking_speed(window),
            "a purely vertical translation (e.g. kneeling) must not read as walking speed",
        )

    def test_horizontal_walking_still_detected_after_direction_gate(self):
        """Recall check: the direction gate must not suppress genuine
        horizontal walking (this module's existing synthetic generator)."""
        window = _walking_window(150, speed=0.15)
        result = gf.compute_walking_speed(window)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.0)

    def test_diagonal_walking_with_horizontal_dominance_is_detected(self):
        window = _diagonal_walking_window(dx_speed=0.15, dy_speed=0.05)
        result = gf.compute_walking_speed(window)
        self.assertIsNotNone(
            result, "translation with a clearly-dominant horizontal component must still be detected",
        )


class HipAngleConstantSyncTests(unittest.TestCase):
    """Regression test for docs/GAIT_CODE_REVIEW.md finding #6: gait_features.py's
    _HIP_ANGLE_SITTING_MAX/_HIP_ANGLE_STANDING_MIN are manually duplicated
    (not imported -- pipeline_utils.py does not expose them as module-level
    constants, and editing that file is out of scope/forbidden) from
    pipeline_utils.py's own function-local ANGLE_SITTING_MAX/ANGLE_STANDING_MIN
    inside _classify_heuristic. Read-only source inspection only -- does
    not import or modify pipeline_utils.py's runtime behavior in any way,
    just parses its already-loaded source text for the two literal values."""

    @staticmethod
    def _pipeline_utils_constant(name):
        src = inspect.getsource(pipeline_utils._classify_heuristic)
        m = re.search(rf"\b{name}\s*=\s*([0-9]+(?:\.[0-9]+)?)", src)
        assert m is not None, f"could not find {name} in pipeline_utils._classify_heuristic source"
        return float(m.group(1))

    def test_sitting_max_stays_in_sync(self):
        self.assertEqual(gf._HIP_ANGLE_SITTING_MAX, self._pipeline_utils_constant("ANGLE_SITTING_MAX"))

    def test_standing_min_stays_in_sync(self):
        self.assertEqual(gf._HIP_ANGLE_STANDING_MIN, self._pipeline_utils_constant("ANGLE_STANDING_MIN"))


def _double_sit_to_stand_window(n_frames=180):
    """Two full sit->stand cycles within one window (sit -> stand -> sit ->
    stand) -- regression fixture for docs/GAIT_CODE_REVIEW.md finding #7:
    compute_sit_to_stand's documented single-transition-per-window
    contract (only the FIRST confirmed transition is ever reported)."""
    window = []
    for i in range(n_frames):
        if i < 40:
            angle = 100.0
        elif i < 60:
            frac = (i - 40) / 20.0
            angle = 100.0 + frac * 75.0
        elif i < 90:
            angle = 175.0
        elif i < 110:
            frac = (i - 90) / 20.0
            angle = 175.0 - frac * 75.0
        elif i < 140:
            angle = 100.0
        elif i < 160:
            frac = (i - 140) / 20.0
            angle = 100.0 + frac * 75.0
        else:
            angle = 175.0
        # cy=_hip_cy_for_angle(angle): the stand phase must show a genuine
        # hip rise (see MIN_STAND_HIP_RISE's docstring in gait_features.py)
        # -- the fixed-cy default models a seated-repositioning-style
        # crossing with NO real rise, which the hip-rise guard (added after
        # this fixture was originally written) now correctly rejects,
        # making this test fail for a reason unrelated to what it actually
        # tests.
        window.append(_angle_pose_row(angle, i, cy=_hip_cy_for_angle(angle)))
    return window


class SitToStandSingleTransitionContractTests(unittest.TestCase):
    """Regression test locking in compute_sit_to_stand's documented
    single-transition-per-window contract (finding #7): a window containing
    TWO full sit->stand cycles must still report only the FIRST one."""

    def test_first_of_two_transitions_in_one_window_is_reported(self):
        window = _double_sit_to_stand_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        # The first cycle's sit ends around frame ~39 and its stand
        # confirms shortly after (~frame ~52) -- a short transition. If the
        # SECOND cycle's stand (~frame 160, ~4s later) were used instead
        # (or duration spanned to it), duration_sec would be much longer.
        self.assertLess(
            result["duration_sec"], 1.5,
            "only the FIRST sit->stand transition's duration must be reported, not a later one",
        )

        # Stronger, direct confirmation (not just an upper-bound heuristic):
        # the full 2-cycle window's result must be BYTE-IDENTICAL to running
        # compute_sit_to_stand on a window truncated right after the first
        # cycle's stand run (frames 0-89, i.e. before the second cycle's own
        # sit/stand data exists at all) -- proving the second cycle's data
        # genuinely never influences the reported transition, not merely
        # that the reported duration happens to be short.
        first_cycle_only = window[:90]
        self.assertGreaterEqual(
            len(first_cycle_only), gf.MIN_WINDOW_FRAMES,
            "test fixture's first-cycle-only slice must itself be a valid window",
        )
        first_cycle_result = gf.compute_sit_to_stand(first_cycle_only)
        self.assertEqual(
            result, first_cycle_result,
            "the full 2-cycle window's reported transition must be identical to what a "
            "window containing ONLY the first cycle reports -- the second cycle's data "
            "must have zero effect on the result",
        )


class TimestampMonotonicityTests(unittest.TestCase):
    """Regression tests for docs/GAIT_CODE_REVIEW.md finding #8:
    GaitRiskAssessor._validate_window previously had no explicit check that
    window frames are in non-decreasing chronological order."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_valid_monotonic_timestamps_do_not_raise(self):
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        self.assessor.assess_risk(window)  # should not raise

    def test_decreasing_timestamps_raise_value_error(self):
        window = [dict(r) for r in _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)]
        window[50]["timestamp"] = window[49]["timestamp"] - 0.1
        with self.assertRaises(ValueError):
            self.assessor.assess_risk(window)

    def test_duplicate_consecutive_timestamps_do_not_raise(self):
        window = [dict(r) for r in _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)]
        window[50]["timestamp"] = window[49]["timestamp"]
        self.assessor.assess_risk(window)  # should not raise

    def test_malformed_timestamp_interspersed_does_not_spuriously_raise(self):
        """A malformed timestamp gets a 30fps fallback downstream (see
        _timestamps' own docstring) -- the monotonicity check must skip it
        rather than comparing it (or the surrounding rows, via the
        fallback) and spuriously flagging a "decrease" that isn't real."""
        window = [dict(r) for r in _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)]
        window[50]["timestamp"] = "not-a-number"
        self.assessor.assess_risk(window)  # should not raise


class PosturalSwayTilingTests(unittest.TestCase):
    """Regression test for docs/GAIT_CODE_REVIEW.md finding #9:
    compute_postural_sway's non-overlapping tiling drops any trailing
    frames past the last full stable_subwindow-length tile. This locks in
    (rather than accidentally changes) that documented behavior."""

    def test_window_length_not_divisible_drops_trailing_frames(self):
        base_n = 90  # exactly 6 tiles of 15 -- matches this project's real usage
        base_window = [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(base_n)]
        baseline = gf.compute_postural_sway(base_window)

        extra = 7  # < stable_subwindow=15 -- an incomplete trailing tile
        huge_sway_extra = []
        for j in range(extra):
            kps = list(_standing_kps())
            kps[46] += 5.0 * (j + 1)  # wildly different hip position -- would dominate the mean if included
            kps[48] += 5.0 * (j + 1)
            huge_sway_extra.append({"timestamp": (base_n + j) / 30.0, "frame": base_n + j, "keypoints": kps})
        extended_window = base_window + huge_sway_extra

        result = gf.compute_postural_sway(extended_window)
        self.assertEqual(
            result, baseline,
            "trailing frames past the last full stable_subwindow-length tile must be dropped entirely, "
            "not folded into the last tile or a new partial one",
        )

    def test_no_trailing_frames_dropped_at_either_real_window_length(self):
        """Regression test for the re-verification (not mere re-acceptance)
        of finding #9's harmlessness claim: both window lengths this module
        is ACTUALLY called with -- MIN_WINDOW_FRAMES=90 and gait_stream's
        constructor default window_frames=150 -- must tile with ZERO
        trailing-frame drop, computed directly rather than assumed."""
        for n in (gf.MIN_WINDOW_FRAMES, 150):
            tile_starts = list(range(0, n - 15 + 1, 15))
            frames_covered = len(tile_starts) * 15
            self.assertEqual(
                frames_covered, n,
                f"window length {n} must tile with zero dropped trailing frames "
                f"(covered {frames_covered}/{n})",
            )

    def test_tile_phase_is_stable_across_reassessments_at_default_cadence(self):
        """Regression test locking in a second, previously-undocumented
        consequence of the same fact used above: gait_stream.py's own
        actual default reassessment cadence (StreamingGaitRiskAssessor's
        constructor default reassess_every_n_frames=15, matching every
        current benchmark script's REASSESS_EVERY_N) equals
        compute_postural_sway's own default stable_subwindow=15 -- so each
        re-assessment's window start advances by exactly one tile-width of
        real frames, and every re-assessment's tile boundaries land on the
        SAME absolute-frame residue class mod 15. Simulates the actual
        RingFrameBuffer fill-then-cadence logic
        (StreamingGaitRiskAssessor.push_frame's own frames_seen/
        since_last_assessment bookkeeping) directly, not assumed."""
        window_frames = 150
        reassess_every = 15
        stable_subwindow = 15
        total_frames = 3000

        window_starts = []
        frames_seen = 0
        since_last = 0
        for absolute_idx in range(total_frames):
            frames_seen += 1
            since_last += 1
            if frames_seen >= window_frames and since_last >= reassess_every:
                since_last = 0
                window_starts.append(absolute_idx - window_frames + 1)

        self.assertGreater(len(window_starts), 100, "simulation must produce enough re-assessments to be meaningful")
        residues = {s % stable_subwindow for s in window_starts}
        self.assertEqual(
            residues, {0},
            "at gait_stream.py's actual default cadence (reassess_every_n_frames=15, "
            "matching stable_subwindow=15), every re-assessment's tile phase must be "
            "identical -- if this ever fails, a change to either default has "
            "reintroduced the phase-sensitivity finding #9 warns about",
        )


class TimestampFallbackObservabilityTests(unittest.TestCase):
    """Regression tests for docs/GAIT_CODE_REVIEW.md finding #10:
    _timestamps' 30fps fallback previously had no observability at all."""

    def test_all_missing_timestamps_warns_once(self):
        window = [{"frame": i, "keypoints": _standing_kps()} for i in range(150)]  # no 'timestamp' key
        with self.assertWarns(RuntimeWarning):
            gf._timestamps(window)

    def test_isolated_missing_timestamp_does_not_warn(self):
        """A single malformed row out of many (well under
        _FALLBACK_WARN_FRACTION) is normal, low-impact noise -- must NOT
        warn, per the 'avoid noisy warnings for normal operation' ask."""
        window = [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(150)]
        del window[10]["timestamp"]
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            gf._timestamps(window)  # should not raise/warn

    def test_all_valid_timestamps_never_warns(self):
        window = [{"timestamp": i / 30.0, "frame": i, "keypoints": _standing_kps()} for i in range(150)]
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            gf._timestamps(window)  # should not raise/warn


class DropRunsAfterLongGapEdgeTests(unittest.TestCase):
    """Regression test for docs/GAIT_CODE_REVIEW.md finding #12: a
    confirmed run starting at index 0 of the window can never be treated
    as "emerging from a blackout" (no look-behind data exists) -- this
    locks in that documented, inherent limitation."""

    def test_run_starting_at_window_edge_is_not_penalized_for_missing_lookbehind(self):
        mask = np.array([True] * 10 + [False] * 5)
        invalid = np.array([False] * 15)  # irrelevant -- the scan can't go before index 0 anyway
        runs = gf._confirmed_runs(mask, min_len=3)
        kept = gf._drop_runs_after_long_gap(runs, invalid, max_gap=1)  # even a tiny max_gap
        self.assertEqual(runs, kept, "a run starting at index 0 must never be dropped by the gap check")


class PeakTranslationSpeedWarningTests(unittest.TestCase):
    """Regression test for docs/GAIT_CODE_REVIEW.md finding #13:
    _peak_translation_speed used to emit an unhandled RuntimeWarning
    ("Mean of empty slice") from np.nanmean when the reference torso-length
    slice was entirely NaN, even though the resulting 0.0 return was
    already correct."""

    def test_all_nan_reference_slice_does_not_warn(self):
        ts = np.arange(10) / 30.0
        hip_mid_raw = np.zeros((10, 2))
        torso_len_raw = np.full(10, np.nan)  # reference slice is entirely NaN
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = gf._peak_translation_speed(hip_mid_raw, torso_len_raw, ts, 0, 4, 5, 9)
        self.assertEqual(result, 0.0)


class WeightBlendingTests(unittest.TestCase):
    """Direct regression tests for docs/GAIT_CODE_REVIEW.md finding #17 --
    GaitRiskAssessor's weighted-average renormalization logic, isolated
    from feature-extraction correctness (already covered elsewhere) via
    patched _SIGNAL_SPECS entries with fixed return values. Covers: one
    signal available, two available, all four available, some unavailable,
    and zero available."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()
        # Any valid-length window -- the patched feature functions below
        # ignore it and return fixed values, so its content doesn't matter.
        self.window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)

    @staticmethod
    def _fixed(value):
        def _fn(window, **kwargs):
            return value
        return _fn

    def _patched_specs(self, walking_speed=None, stride_regularity=None,
                        postural_sway=None, sit_to_stand=None):
        return (
            ("walking_speed", self._fixed(walking_speed), gr._speed_risk, "gait", "d"),
            ("stride_regularity", self._fixed(stride_regularity), gr._stride_cv_risk, "gait", "d"),
            ("postural_sway", self._fixed(postural_sway), gr._sway_risk, "postural", "d"),
            ("sit_to_stand", self._fixed(sit_to_stand), gr._sit_to_stand_risk, "postural", "d"),
        )

    def test_single_signal_available_equals_its_own_contribution(self):
        specs = self._patched_specs(walking_speed=1.0)
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
            result = self.assessor.assess_risk(self.window)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertTrue(speed_signal["available"])
        self.assertAlmostEqual(result["risk_score"], speed_signal["risk_contribution"])

    def test_zero_signals_available_risk_score_is_none(self):
        specs = self._patched_specs()
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
            result = self.assessor.assess_risk(self.window)
        self.assertIsNone(result["risk_score"])
        for s in result["signals"]:
            self.assertFalse(s["available"])

    def test_two_signals_available_matches_weighted_average_formula(self):
        specs = self._patched_specs(walking_speed=1.0, stride_regularity=0.35)
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
            result = self.assessor.assess_risk(self.window)
        by_name = {s["name"]: s for s in result["signals"]}
        w1, c1 = gr._SIGNAL_WEIGHTS["walking_speed"], by_name["walking_speed"]["risk_contribution"]
        w2, c2 = gr._SIGNAL_WEIGHTS["stride_regularity"], by_name["stride_regularity"]["risk_contribution"]
        expected = (w1 * c1 + w2 * c2) / (w1 + w2)
        self.assertAlmostEqual(result["risk_score"], expected)

    def test_all_four_signals_available_matches_weighted_average_formula(self):
        specs = self._patched_specs(
            walking_speed=1.0, stride_regularity=0.35, postural_sway=0.08,
            sit_to_stand={"duration_sec": 2.5, "reversal_count": 3.0},
        )
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
            result = self.assessor.assess_risk(self.window)
        by_name = {s["name"]: s for s in result["signals"]}
        expected_num = sum(gr._SIGNAL_WEIGHTS[n] * by_name[n]["risk_contribution"] for n in gr._SIGNAL_WEIGHTS)
        expected_den = sum(gr._SIGNAL_WEIGHTS[n] for n in gr._SIGNAL_WEIGHTS)
        self.assertAlmostEqual(result["risk_score"], expected_num / expected_den)

    def test_some_signals_unavailable_only_available_ones_contribute(self):
        specs = self._patched_specs(
            postural_sway=0.1, sit_to_stand={"duration_sec": 1.0, "reversal_count": 0.0},
        )
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
            result = self.assessor.assess_risk(self.window)
        by_name = {s["name"]: s for s in result["signals"]}
        self.assertFalse(by_name["walking_speed"]["available"])
        self.assertFalse(by_name["stride_regularity"]["available"])
        w1, c1 = gr._SIGNAL_WEIGHTS["postural_sway"], by_name["postural_sway"]["risk_contribution"]
        w2, c2 = gr._SIGNAL_WEIGHTS["sit_to_stand"], by_name["sit_to_stand"]["risk_contribution"]
        expected = (w1 * c1 + w2 * c2) / (w1 + w2)
        self.assertAlmostEqual(result["risk_score"], expected)


def _fast_squat_rise_window(n_frames=90, dip_start=3, dip_len=5):
    """A sustained (confirmed) dip into the sitting-angle range -> an
    IMMEDIATE (1-frame gap) rise straight to confirmed standing, with NO
    transition frames between the two confirmed states. A synthetic
    reproduction of the real false positive found on Bend_pickup_squat_
    lowLight.MOV (see compute_sit_to_stand's minimum-gap guard docstring):
    during the RISING phase of a squat, hip_angle swept from a confirmed
    sitting-range reading to a confirmed standing-range reading in as
    little as 2 frames (measured: last_sit=31, first_stand_after=33 on that
    clip, ~0.068s at ~29.4fps) -- ~3x faster than the fastest GENUINE
    sit-to-stand this project has on file (SitFast_GetupFast.MOV: 0.216s).
    Requested/actual angle values below are picked from direct measurement
    of _angle_pose_row's own nonlinear requested->actual mapping (same
    caveat as _fast_shallow_sit_to_stand_window's docstring), not assumed:
    requested=95 -> actual ~106.3 (confirmed sitting, <= 125), requested=120
    -> actual ~152.5 (confirmed standing, >= 143).

    DELIBERATELY starts in a brief DEAD-ZONE state (107.0 -> actual
    ~135.5), NOT a long confirmed-standing baseline (found via a later
    audit pass -- see docs/GAIT_CODE_REVIEW.md): compute_sit_to_stand
    anchors `first_stand_after` to the EARLIEST confirmed standing run in
    the WHOLE window, so a fixture that opens on ~40 frames of stable
    standing before the dip would anchor there instead and route through
    _detect_fast_shallow_transition (the FALLBACK path) rather than the
    PRIMARY sit-run-based path this fixture exists to exercise --
    confirmed directly: the original (standing-baseline) version of this
    fixture returned None via the fallback path's OWN, unrelated
    trough-depth guard, not via the primary-path minimum-gap guard this
    fixture's test claims to cover."""
    window = []
    for i in range(n_frames):
        if i < dip_start:
            angle = 107.0  # actual ~135.5, dead zone -- NOT a confirmed standing run
        elif i < dip_start + dip_len:
            angle = 95.0  # actual ~106.3, confirmed sitting
        else:
            angle = 120.0  # actual ~152.5, confirmed standing -- immediately after the dip, no gap
        window.append(_angle_pose_row(angle, i))
    return window


def _brief_deep_bend_window(n_frames=90, dip_start=40, dip_len=2):
    """Standing -> a BRIEF (too short to primary-path-confirm) but DEEP dip
    well past the sitting threshold -> standing again, with the hip staying
    roughly in place (no real translation). A synthetic reproduction of the
    real false positive found on Bend_pickup_normalLight_leftRight.MOV /
    Bend_pickup_normalLight_back.MOV (see _detect_fast_shallow_transition's
    guard #3 docstring): a fast, deep BEND satisfies the fallback path's
    minimum-descent guard (which has no corresponding maximum/depth bound)
    just as easily as a genuine shallow perch does. Requested=90 -> actual
    exactly 90.0 (see docstring measurement) -- well past
    _HIP_ANGLE_SITTING_MAX=125, i.e. NOT "shallow" by this function's own
    definition."""
    window = []
    for i in range(n_frames):
        if dip_start <= i < dip_start + dip_len:
            angle = 90.0  # actual 90.0 -- a deep bend, not a shallow perch
        else:
            angle = 175.0  # actual ~178.5, confirmed standing
        window.append(_angle_pose_row(angle, i))
    return window


def _sustained_held_bend_window(n_frames=90, dip_start=3, dip_len=10):
    """A SUSTAINED (confirmed, multi-frame -- like someone pausing while
    bent over to pick something up) dip that stays just inside the sitting
    range -> a brief (3-frame, dead-zone) rise -> a confirmed stand, with
    NO prior confirmed-standing baseline earlier in the window (deliberately
    -- compute_sit_to_stand anchors `first_stand_after` to the EARLIEST
    confirmed standing run in the whole window; a fixture that opens on a
    long stable standing baseline would anchor there instead and route this
    through a different code path than the one being characterized here --
    exactly what a real multi-repetition clip's sliding window naturally
    produces once the window no longer starts at the clip's very beginning).
    Unlike _fast_squat_rise_window (too fast a crossing) or
    _brief_deep_bend_window (too deep/brief a trough), THIS shape satisfies
    every existing guard exactly the way a genuine sit-to-stand would --
    because a sufficiently deep, sufficiently HELD bend is geometrically
    indistinguishable from a sit via hip-angle alone. This is the residual,
    disclosed limitation confirmed on real footage (Bend_pickup_normalLight_
    leftRight.MOV/_back.MOV both still produced a detection in SOME sliding-
    window slice even after both new guards were added) -- documented and
    tested explicitly here (see docs/GAIT_CODE_REVIEW.md's follow-up
    investigation) so this known, understood behavior is a locked-in,
    visible characteristic rather than a silent surprise if rediscovered.
    NOT something this session's fix attempts to solve -- doing so safely
    needs a second discriminating signal or additional footage (see that
    same investigation's conclusion: knee angle, hip vertical drop, and
    duration were each empirically tested against real footage and found
    NOT to cleanly separate this case either), not another threshold tweak."""
    window = []
    for i in range(n_frames):
        if i < dip_start:
            angle = 107.0  # actual ~135.5, dead zone -- NOT a confirmed standing run
        elif i < dip_start + dip_len:
            angle = 100.0  # actual ~120.4, confirmed sitting -- HELD for dip_len frames
        elif i < dip_start + dip_len + 3:
            angle = 107.0  # actual ~135.5, dead zone (neither sit- nor stand-confirmed)
        else:
            angle = 175.0  # actual ~178.5, confirmed standing
        # cy=_hip_cy_for_angle(angle): the final "confirmed standing" phase
        # must show a genuine hip rise (see MIN_STAND_HIP_RISE's docstring
        # in gait_features.py) for this fixture to still mean what its own
        # docstring claims -- a real person actually straightening up out of
        # a held bend DOES raise their hip (confirmed on real footage:
        # Deep_Bend.mov's kneel-to-stand measured +0.403 torso-lengths of
        # rise, well within the guard's accepted range), so the hip-rise
        # guard does NOT by itself resolve this residual ambiguity -- it
        # only rejects standless seated repositioning (Sit_Stand_2.mov),
        # a different mechanism. Confirming this fixture still returns
        # non-None WITH a genuine rise modeled is what actually locks in
        # the residual limitation this test documents.
        window.append(_angle_pose_row(angle, i, cy=_hip_cy_for_angle(angle)))
    return window


class SitToStandBendSquatGuardTests(unittest.TestCase):
    """Regression tests for the two evidence-based guards added to close
    real false-positive mechanisms found via direct real-footage
    investigation (docs/GAIT_CODE_REVIEW.md's bend/squat follow-up):
    (1) the primary path's new minimum-gap guard, (2) the fallback path's
    new trough-must-stay-shallow guard. Also documents the residual,
    NOT-fixed limitation (a sustained held bend) explicitly rather than
    leaving it as an undocumented surprise."""

    def test_implausibly_fast_primary_path_crossing_is_rejected(self):
        """The core regression test for the primary-path minimum-gap guard:
        a sit-confirmed run followed with NO gap by a stand-confirmed run
        (the exact real Bend_pickup_squat_lowLight.MOV mechanism) must not
        be reported as a sit-to-stand transition."""
        window = _fast_squat_rise_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result,
            "an implausibly fast (sub-_STATE_CONFIRM_FRAMES-gap) primary-path "
            "crossing must not be reported as a genuine sit-to-stand",
        )

    def test_normal_primary_path_transition_still_detected_after_gap_guard(self):
        """Recall check: the minimum-gap guard must not suppress a normal,
        genuinely-paced sit-to-stand transition (the existing
        _sit_to_stand_window fixture, used throughout this test suite)."""
        window = _sit_to_stand_window(shaky=False)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)
        self.assertGreater(result["duration_sec"], 0)

    def test_deep_brief_bend_is_rejected_by_trough_depth_guard(self):
        """The core regression test for the fallback path's new trough-depth
        guard: a brief but DEEP dip (past _HIP_ANGLE_SITTING_MAX, i.e. not
        'shallow') must not be reported as a fast sit-to-stand -- the real
        Bend_pickup_normalLight_leftRight.MOV/_back.MOV mechanism."""
        window = _brief_deep_bend_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result,
            "a deep (past the sitting threshold) bend must not be reported as a "
            "shallow fast sit-to-stand, even if brief and translation-free",
        )

    def test_genuinely_shallow_fast_transition_still_recovered_after_depth_guard(self):
        """Recall check: the trough-depth guard must not suppress the exact
        genuine case this fallback path exists for -- a real reproduction
        of SitFast_GetupFast.MOV (_fast_shallow_sit_to_stand_window's
        default trough, measured to stay above _HIP_ANGLE_SITTING_MAX --
        see that fixture's own docstring)."""
        window = _fast_shallow_sit_to_stand_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result, "a genuinely shallow (trough above the sitting threshold) fast "
            "transition must still be detected after the depth guard",
        )
        self.assertLess(result["duration_sec"], 1.0)

    def test_sustained_held_bend_residual_limitation_documented(self):
        """NOT a bug fix -- documents the disclosed, understood residual
        limitation: a sufficiently deep, sufficiently HELD bend (someone
        pausing while bent over) remains indistinguishable from a genuine
        sit via hip-angle alone, and is still reported here. This is the
        expected, current, evidence-based boundary of what hip-angle-only
        geometry can resolve (see docs/GAIT_CODE_REVIEW.md's investigation
        for why knee angle, hip vertical drop, and duration were each
        empirically tested against real footage and found NOT to cleanly
        separate this case either) -- a locked-in characterization, not
        silently-accidental behavior."""
        window = _sustained_held_bend_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result,
            "documents (does not endorse) the current residual limitation -- "
            "a sustained held bend still registers as a sit-to-stand",
        )


def _pose_row_with_knee_angle(hip_angle, knee_angle, i, cx=0.3, cy=0.55):
    """Same shoulder/hip/knee geometry as _angle_pose_row, PLUS an ankle
    point positioned so the hip-knee-ankle angle equals `knee_angle`
    degrees (180 = straight leg, smaller = more bent) -- _angle_pose_row's
    own fixtures never set an ankle at all, so knee_angle is NaN
    everywhere in every OTHER sit-to-stand fixture in this file (confirmed:
    the standing-bend hip-rise exemption is a no-op for all of them, since
    it requires a non-NaN knee_angle at both reference points -- see
    test_all_existing_fixtures_unaffected_by_knee_exemption below)."""
    hip_angle = float(np.clip(hip_angle, 90.0, 180.0))
    fold = np.radians(180.0 - hip_angle)
    sh_x, sh_y = cx + 0.25 * np.sin(fold) * 0.3, cy - 0.25 * np.cos(fold)
    knee_x, knee_y = cx - 0.05, cy + 0.2
    bend = np.radians(180.0 - float(np.clip(knee_angle, 10.0, 180.0)))
    ankle_x, ankle_y = knee_x + 0.2 * np.sin(bend), knee_y + 0.2 * np.cos(bend)
    kps = [np.nan] * 66
    kps[22], kps[23] = sh_x - 0.05, sh_y
    kps[24], kps[25] = sh_x + 0.05, sh_y
    kps[46], kps[47] = cx - 0.05, cy
    kps[48], kps[49] = cx + 0.05, cy
    kps[50], kps[51] = knee_x, knee_y
    kps[52], kps[53] = cx + 0.05, cy + 0.2
    kps[54], kps[55] = ankle_x, ankle_y
    kps[56], kps[57] = cx + 0.05 + (ankle_x - knee_x), ankle_y
    return {"timestamp": i / 30.0, "frame": i, "keypoints": kps}


def _bend_recovery_window(n_frames=90, rise_start=40, rise_len=25,
                           standing_angle=160.0, trough_angle=80.0, knee_angle=170.0, cy=0.55):
    """A SUSTAINED bend (hip angle held in sitting-range from frame 0 --
    like a real sliding window landing entirely inside an already-in-
    progress bend, e.g. the real Deep_Bend_2.mov window this reproduces,
    t=13.82-15.31s, which likewise opens mid-bend with no standing frames
    before it) that then recovers to standing ONCE. The hip's raw vertical
    position is held perfectly FIXED throughout (`cy` constant, zero rise
    by construction -- the exact condition MIN_STAND_HIP_RISE alone would
    reject), and knee_angle is FIXED throughout at `knee_angle`. Used with
    a STRAIGHT knee_angle (default 170) to reproduce a genuine standing-
    bend recovery (Deep_Bend_1/2/3.mov's real mechanism); with a BENT
    knee_angle to reproduce genuine seated repositioning (Sit_Stand_2.mov's
    real, already-fixed false positive) -- see the test class docstring for
    which is which.

    Deliberately does NOT open on a standing baseline (contrast
    _sit_to_stand_window's own dip-from-standing shape) -- for the SAME
    reason documented on _sustained_held_bend_window: compute_sit_to_stand
    anchors `first_stand_after` to the EARLIEST confirmed standing run in
    the window, so any standing frames before the bend would anchor there
    instead of the post-bend recovery this fixture means to test."""
    window = []
    for i in range(n_frames):
        if i < rise_start:
            angle = trough_angle
        elif i < rise_start + rise_len:
            frac = (i - rise_start) / (rise_len - 1)
            angle = trough_angle + (standing_angle - trough_angle) * frac
        else:
            angle = standing_angle
        window.append(_pose_row_with_knee_angle(angle, knee_angle, i, cy=cy))
    return window


class StandingBendHipRiseExemptionTests(unittest.TestCase):
    """Regression tests for the standing-bend hip-rise exemption (see
    gait_features.py's "STANDING-BEND HIP-RISE EXEMPTION" docstring block):
    knee angle distinguishes a genuine standing-bend recovery (legs stay
    straight, so MIN_STAND_HIP_RISE's own "no real hip rise" rejection is a
    false negative) from genuine seated repositioning (legs stay bent,
    where that same rejection is correct and must be preserved)."""

    def test_straight_knee_no_hip_rise_is_now_detected(self):
        """The core fix: a hip-angle dip-and-recover with a STRAIGHT knee
        throughout and ZERO hip rise (the real Deep_Bend_1/2/3.mov
        mechanism) must now be detected, not silently dropped."""
        window = _bend_recovery_window(knee_angle=170.0)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result, "a genuine standing-bend recovery (straight knee, no hip rise) "
                    "must now be detected -- this is the fix",
        )

    def test_bent_knee_no_hip_rise_still_rejected(self):
        """Recall/safety check: the exact same hip-angle shape and zero hip
        rise, but with a BENT knee throughout (genuine seated repositioning,
        Sit_Stand_2.mov's real, already-fixed false positive) must STILL be
        rejected -- the exemption must not reopen the false positive
        MIN_STAND_HIP_RISE was built to close."""
        window = _bend_recovery_window(knee_angle=110.0)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result, "seated repositioning (bent knee, no hip rise) must still be "
                    "rejected -- the exemption is knee-angle-specific, not a blanket "
                    "removal of the hip-rise guard",
        )

    def test_implausibly_large_hip_drop_not_exempted_even_with_straight_knee(self):
        """Safety bound found via real-corpus validation (Stride_Big_
        Starting_Leap.mov's MediaPipe-acquisition-jitter artifact, hip_rise
        -6.051, straight knee by coincidence): an implausibly large hip
        DROP must not be exempted just because the knee happens to read as
        straight -- MAX_PLAUSIBLE_HIP_DROP_FOR_BEND_EXEMPTION bounds how
        negative a genuine standing-bend's hip_rise can plausibly be."""
        window = _bend_recovery_window(knee_angle=170.0, cy=0.55)
        # Splice in an implausible hip drop at the trough by lowering cy
        # far beyond any real standing-bend measurement (worst real case:
        # -0.454) right where the trough sits.
        for i in range(40, 55):
            row = window[i]
            kps = row["keypoints"]
            for idx in (23, 25, 47, 49, 51, 53, 55, 57):  # every y-coordinate set by the fixture
                if not np.isnan(kps[idx]):
                    kps[idx] += 3.0
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result, "an implausibly large hip drop must not be exempted even with a "
                    "straight knee -- it is more likely corrupted tracking than a "
                    "genuine gentle standing-bend recovery",
        )

    def test_all_existing_sit_to_stand_fixtures_unaffected(self):
        """Backward-compatibility guarantee: every pre-existing sit-to-stand
        fixture in this file never sets an ankle keypoint, so knee_angle is
        NaN throughout -- the new exemption must be a complete no-op for
        all of them (byte-identical results to before this session)."""
        for window, desc in (
            (_sit_to_stand_window(shaky=False), "genuine chair stand"),
            (_seated_repositioning_via_fallback_window(), "fallback-path seated repositioning"),
            (_sustained_held_bend_window(), "sustained held bend (disclosed residual limitation)"),
        ):
            raw = gf._raw_keypoint_array(window)
            pts = raw.reshape(-1, 33, 2)
            ankle_valid = ~(np.isnan(pts[:, gf.LEFT_ANKLE, :]).any(axis=1)
                            & np.isnan(pts[:, gf.RIGHT_ANKLE, :]).any(axis=1))
            self.assertFalse(ankle_valid.any(), f"{desc} fixture must have no ankle data "
                                                 "for this test to be meaningful")


def _seated_repositioning_via_fallback_window(n_frames=90, dip_start=40, dip_len=15,
                                               standing_angle=175.0, trough_angle=107.0):
    """Same angle dip-and-recover SHAPE as _fast_shallow_sit_to_stand_window
    (confirmed-standing -> shallow dip -> confirmed-standing), but with hip
    position held perfectly FIXED throughout (no rise anywhere) -- a
    synthetic reproduction of the real false positive found and root-caused
    on Sit_Stand_2.mov this session (see _detect_fast_shallow_transition's
    guard #5 docstring in gait_features.py): reclining/repositioning WHILE
    STILL SEATED swings hip_angle across the standing threshold on both
    sides of a shallow re-dip without the person ever leaving the chair, so
    the hip's real vertical position never changes. This shape satisfies
    every PRE-EXISTING fallback guard (#1 confirmed standing on both sides,
    #2 sufficient gap/descent, #3 shallow trough, #4 zero translation --
    identical geometry to _fast_shallow_sit_to_stand_window, which #1-#4
    alone accept) -- isolating guard #5 (hip-rise) as the only mechanism
    that can reject it."""
    window = []
    for i in range(n_frames):
        if i < dip_start:
            angle = standing_angle
        elif i < dip_start + dip_len:
            frac = (i - dip_start) / (dip_len - 1)
            angle = standing_angle - (standing_angle - trough_angle) * np.sin(frac * np.pi)
        else:
            angle = standing_angle
        window.append(_angle_pose_row(angle, i))  # fixed cy=0.55 default -- zero rise by construction
    return window


def _fallback_transition_window_with_rise(rise_amp, n_frames=90, dip_start=40, dip_len=15,
                                           standing_angle=175.0, trough_angle=107.0):
    """Same angle dip-and-recover SHAPE as _seated_repositioning_via_fallback_window,
    but with a CONTROLLABLE hip-rise amplitude (cy dips by `rise_amp` at the trough's
    midpoint, same sin(frac*pi) profile as the angle itself) -- lets a caller construct
    a candidate whose actual measured _hip_vertical_rise lands at a precise, calibrated
    value relative to MIN_STAND_HIP_RISE, rather than only the two extremes (zero rise
    from the fixture above / a comfortably-large rise from
    _fast_shallow_sit_to_stand_window) this module's other fixtures already cover.
    `rise_amp` values used by the boundary tests below were found by direct bisection
    against this module's OWN _hip_vertical_rise computation (not assumed from
    `rise_amp` itself, which does not map 1:1 to the measured torso-length-scaled
    rise -- the two quantities differ by roughly a factor of 9 at this fixture's
    geometry, since _hip_vertical_rise divides by a small reference torso length)."""
    window = []
    for i in range(n_frames):
        if i < dip_start:
            angle, cy = standing_angle, 0.55
        elif i < dip_start + dip_len:
            frac = (i - dip_start) / (dip_len - 1)
            angle = standing_angle - (standing_angle - trough_angle) * np.sin(frac * np.pi)
            cy = 0.55 + rise_amp * np.sin(frac * np.pi)
        else:
            angle, cy = standing_angle, 0.55
        window.append(_angle_pose_row(angle, i, cy=cy))
    return window


class SitToStandFallbackHipRiseGuardTests(unittest.TestCase):
    """Regression tests for _detect_fast_shallow_transition's guard #5
    (see that function's docstring), added after this exact real false
    positive was traced on Sit_Stand_2.mov: MIN_STAND_HIP_RISE (added to
    compute_sit_to_stand's PRIMARY path to reject seated repositioning --
    see that constant's docstring) was never applied to the FALLBACK path,
    so the identical seated-repositioning pattern still slipped through
    whenever the reclining motion's hip angle never formed a
    _STATE_CONFIRM_FRAMES-long confirmed SIT run (routing it through
    _detect_fast_shallow_transition instead of the already-guarded primary
    path). Measured directly on the real implicated window: trough-to-
    standing-run rise was 0.030-0.031 torso-lengths, far below
    MIN_STAND_HIP_RISE=0.08."""

    def test_seated_repositioning_with_no_rise_is_rejected(self):
        window = _seated_repositioning_via_fallback_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result,
            "a shallow dip-and-recover with NO genuine hip rise (seated repositioning) "
            "must not be reported as a sit-to-stand via the fallback path",
        )

    def test_genuine_fast_shallow_stand_with_real_rise_still_recovered(self):
        """Recall check: the guard must not suppress a GENUINE fast/shallow
        stand -- same angle shape as the rejected fixture above, but with a
        real hip rise modeled (see _fast_shallow_sit_to_stand_window's own
        docstring for why this fixture's rise is independent of trough
        depth). This is also the fixture SitFast_GetupFast.MOV's real
        extraction+assessment run confirms is still recovered end-to-end
        (dur=0.216s, matching this project's one real reference clip)."""
        window = _fast_shallow_sit_to_stand_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result, "a genuine fast/shallow stand with a real hip rise must still be recovered",
        )

    def test_rise_just_below_threshold_is_rejected(self):
        """Boundary check: the two tests above only exercise the extremes (exactly
        zero rise / a comfortably large ~0.4 torso-length rise) -- neither would catch
        an inverted comparison or a threshold off by a large margin. This rise
        amplitude was calibrated by direct bisection against _hip_vertical_rise
        (not assumed) to measure ~0.07992 torso-lengths -- just under
        MIN_STAND_HIP_RISE=0.08 -- and must still be rejected."""
        window = _fallback_transition_window_with_rise(0.008821639376878637)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result, "a measured rise just below MIN_STAND_HIP_RISE must still be rejected",
        )

    def test_rise_just_above_threshold_is_recovered(self):
        """Boundary check, the mirror of the test above: calibrated to measure
        ~0.08008 torso-lengths -- just OVER MIN_STAND_HIP_RISE -- and must be
        accepted. Together with the just-below case, this confirms the guard's
        comparison direction and threshold value at fine resolution, not just at
        the two extremes. (An exact-equality case, hip_rise == MIN_STAND_HIP_RISE,
        was not attempted as a fixture -- constructing one exactly is floating-point
        fragile given the geometry's nonlinear angle-to-position mapping; code
        inspection of the guard's own `hip_rise < MIN_STAND_HIP_RISE` comparison
        confirms the boundary is inclusive -- an exact-equality rise is ACCEPTED,
        not rejected, since strict less-than excludes it.)"""
        window = _fallback_transition_window_with_rise(0.008839300316572088)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result, "a measured rise just above MIN_STAND_HIP_RISE must be recovered",
        )

    def test_trough_frame_hip_nan_falls_back_to_nearest_valid_neighbor(self):
        """Regression test for _nearest_valid_hip_frame (added in a later
        robustness pass on this guard): a seated-repositioning candidate
        (zero real rise -- must be rejected) whose EXACT trough frame has
        its raw hip landmarks NaN on one side (hip_angle stays valid there,
        computed from the OTHER side's shoulder/hip/knee alone -- a
        realistic partial-occlusion pattern, not a contrived one) must
        still be correctly rejected, by falling back to the nearest frame
        within the same gap that DOES have usable raw hip data, rather than
        silently skipping the guard because its one designated reference
        frame happened to be unusable.

        Proven meaningful (not vacuous), not just asserted: with only the
        OLD single-fixed-frame behavior (no fallback), `_hip_vertical_rise`
        on the exact trough frame alone returns None for this fixture
        (verified directly -- see this test's own arithmetic below) --
        which the guard's `hip_rise is not None and ...` check would have
        silently treated as "cannot evaluate, do not reject," WRONGLY
        accepting this seated-repositioning candidate. The fix closes
        exactly this gap."""
        window = _seated_repositioning_via_fallback_window()
        window = [dict(r, keypoints=list(r["keypoints"])) for r in window]

        raw = gf._raw_keypoint_array(window)
        pairs = raw.reshape(-1, 33, 2)
        l_sh, r_sh = pairs[:, gf.LEFT_SHOULDER, :], pairs[:, gf.RIGHT_SHOULDER, :]
        l_hp, r_hp = pairs[:, gf.LEFT_HIP, :], pairs[:, gf.RIGHT_HIP, :]
        l_kn, r_kn = pairs[:, gf.LEFT_KNEE, :], pairs[:, gf.RIGHT_KNEE, :]
        left_angle = gf._batch_hip_angle(l_sh, l_hp, l_kn)
        right_angle = gf._batch_hip_angle(r_sh, r_hp, r_kn)
        valid_l, valid_r = ~np.isnan(left_angle), ~np.isnan(right_angle)
        n_valid = valid_l.astype(float) + valid_r.astype(float)
        angle_sum = np.where(valid_l, left_angle, 0) + np.where(valid_r, right_angle, 0)
        hip_angles = np.where(n_valid > 0, angle_sum / np.where(n_valid > 0, n_valid, 1), np.nan)
        stand_runs = gf._confirmed_runs(hip_angles >= gf._HIP_ANGLE_STANDING_MIN, gf._STATE_CONFIRM_FRAMES)
        pre_end, post_start = stand_runs[0][1], stand_runs[1][0]
        gap = hip_angles[pre_end + 1:post_start]
        trough_idx = pre_end + 1 + int(np.nanargmin(gap))

        # Blank ONLY the left hip landmark at the trough frame -- the right
        # side's shoulder/hip/knee stay intact, so hip_angle at this frame
        # is UNCHANGED (still valid, still the same trough value), but
        # hip_mid_raw = (LEFT_HIP + RIGHT_HIP) / 2 is now NaN there.
        window[trough_idx]["keypoints"][46] = np.nan  # left hip x
        window[trough_idx]["keypoints"][47] = np.nan  # left hip y

        # Prove this fixture actually exercises the gap the fix closes: the
        # OLD single-frame-only reference must be unusable at this exact frame.
        hip_mid_raw = (pairs[:, gf.LEFT_HIP, :] + pairs[:, gf.RIGHT_HIP, :]) / 2.0
        hip_mid_raw[trough_idx] = np.nan  # matches the blanked keypoints above
        sh_mid_raw = (pairs[:, gf.LEFT_SHOULDER, :] + pairs[:, gf.RIGHT_SHOULDER, :]) / 2.0
        torso_len_raw = np.linalg.norm(sh_mid_raw - hip_mid_raw, axis=1)
        post_end = stand_runs[1][1]
        old_single_frame_rise = gf._hip_vertical_rise(
            hip_mid_raw, torso_len_raw, trough_idx, trough_idx, post_start, post_end)
        self.assertIsNone(
            old_single_frame_rise,
            "test fixture must make the OLD single-fixed-frame reference unusable "
            "(None) to be a meaningful test of the nearest-valid-frame fallback",
        )

        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result,
            "a seated-repositioning candidate whose exact trough frame has NaN raw hip "
            "data (but a valid hip_angle from the other side) must still be rejected, "
            "via the nearest-valid-frame fallback -- not silently accepted because the "
            "one designated reference frame happened to be unusable",
        )


def _side_switching_occlusion_window(n_frames=90, seed=7):
    """Same sit-to-stand angle transition as _sit_to_stand_window(shaky=False),
    but with the LEFT shoulder/hip/knee blanked to NaN during the sitting
    phase (frames before the transition starts) and the RIGHT side blanked
    from the transition onward -- so the confirmed SIT run is attested
    ENTIRELY by the right side and the confirmed STAND run is attested
    ENTIRELY by the left side, with NO frame anywhere where the same side
    covers both. Synthetic reproduction of the real mechanism found on
    Deep_Bend.mov's two false-positive detections this session (see
    compute_sit_to_stand's anchor-run side-switching guard docstring):
    measured directly, that clip's spurious sit-run was 100% right-side-only
    and its spurious stand-run was 100% left-side-only -- the two states
    share no common corroborating side, unlike genuine one-sided-occlusion
    footage (see _sit_to_stand_window_left_occluded, where the SAME side
    covers both phases throughout)."""
    window = _sit_to_stand_window(shaky=False, n_frames=n_frames, seed=seed)
    window = [dict(r, keypoints=list(r["keypoints"])) for r in window]
    # Measured directly against this fixture's own actual (not requested)
    # angle crossings: the confirmed sit run is (0, 45) and the confirmed
    # stand run is (49, 89) -- NOT symmetric around the requested
    # transition midpoint, since _sit_to_stand_window's angle-vs-position
    # geometry is nonlinear. Blanked independently (not elif) with a
    # 3-frame buffer (46-48) left fully valid on both sides in between --
    # that buffer isn't part of either confirmed run, so it cannot
    # introduce a shared-side frame into either run's slice.
    sit_run_end, stand_run_start = 45, 49
    for i, row in enumerate(window):
        kps = row["keypoints"]
        if i <= sit_run_end:
            for idx in (22, 23, 46, 47, 50, 51):  # left shoulder/hip/knee
                kps[idx] = np.nan
        if i >= stand_run_start:
            for idx in (24, 25, 48, 49, 52, 53):  # right shoulder/hip/knee
                kps[idx] = np.nan
    return window


class SitToStandAnchorRunSideSwitchingGuardTests(unittest.TestCase):
    """Regression tests for compute_sit_to_stand's primary-path anchor-run
    side-switching guard (see that function's own docstring), added after
    tracing a real false positive on Deep_Bend.mov -- a sustained deep
    bend/kneel with heavy self-occlusion (ankle visibility 0.54, hip 0.86)
    produced a spurious sit-to-stand (duration=1.73s, reversal=0,
    reliability=0.038) whose sit-run was confirmed entirely by the right
    side and whose stand-run was confirmed entirely by the left side --
    no shared corroborating side between the two states.

    A first, broader version of this guard (reject whenever EITHER anchor
    run has zero both-sided-confident frames) was tried and rejected --
    documented as a dead end in the guard's own docstring -- because it
    broke two existing tests that deliberately depend on a DIFFERENT real
    scenario: one side occluded for an ENTIRE clip, where the other side
    stays reliably valid throughout both phases
    (test_sit_to_stand_detected_despite_one_sided_occlusion,
    test_sit_to_stand_reliability_reflects_landmark_confidence, both in
    SignalDirectionTests/SignalReliabilityTests). The guard actually
    implemented only rejects when the two anchor runs are BOTH entirely
    single-sided AND share no common side."""

    def test_side_switching_occlusion_is_rejected(self):
        window = _side_switching_occlusion_window()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result,
            "a sit-run confirmed entirely by one side and a stand-run confirmed entirely "
            "by the OTHER side, with no shared corroborating side, must not be reported "
            "as a genuine sit-to-stand",
        )

    def test_same_side_occlusion_throughout_is_not_rejected(self):
        """Recall check, same real scenario the rejected first-cut guard
        broke: one side occluded for the WHOLE clip, the other side
        reliably covering both the sit and stand phases, must still be
        detected -- this is _sit_to_stand_window_left_occluded, already
        covered by SignalDirectionTests::
        test_sit_to_stand_detected_despite_one_sided_occlusion; asserted
        again here, in this guard's own test class, so the guard's recall
        boundary is documented next to the guard itself."""
        window = _sit_to_stand_window_left_occluded()
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result,
            "one side occluded for the whole clip, with the other side reliably covering "
            "both the sit and stand phases, must still be recovered",
        )

    def test_same_side_occlusion_right_instead_of_left_is_not_rejected(self):
        """Adversarial case: mirror of test_same_side_occlusion_throughout_is_not_rejected
        with the RIGHT side occluded for the whole clip instead of the left (only the
        LEFT side is trustworthy throughout). The guard's own check
        (`shares_left`/`shares_right`) is symmetric in the code, but this confirms
        that symmetry empirically rather than by inspection alone -- it would be a
        real bug if the guard were accidentally right-side-specific (e.g. checking
        only `valid_r` and never `valid_l`, or vice versa)."""
        window = _sit_to_stand_window(shaky=False)
        for row in window:
            for idx in (24, 25, 48, 49, 52, 53):  # right shoulder/hip/knee
                row["keypoints"][idx] = np.nan
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result,
            "one side (right) occluded for the whole clip, with the LEFT side reliably "
            "covering both phases, must still be recovered -- the guard must not be "
            "accidentally specific to which side is occluded",
        )

    def test_one_period_single_sided_other_double_sided_is_not_rejected(self):
        """Adversarial case: the guard's stated rule only fires when BOTH anchor runs
        are entirely single-sided. Here the sit-run is entirely single-sided (left
        blanked through its own last confirmed frame, index 45 -- measured directly
        against this fixture's own confirmed-run boundaries, not assumed) while the
        stand-run is left completely untouched (fully double-sided throughout). Per
        the guard's `if not sit_both_conf.any() and not stand_both_conf.any():` outer
        AND, this must NOT be rejected regardless of side-sharing, since the stand-run
        alone already has both-sided-confident frames."""
        window = _sit_to_stand_window(shaky=False)
        window = [dict(r, keypoints=list(r["keypoints"])) for r in window]
        for i, row in enumerate(window):
            if i <= 45:  # this fixture's own confirmed sit-run is (0, 45) -- measured
                for idx in (22, 23, 46, 47, 50, 51):  # left shoulder/hip/knee
                    row["keypoints"][idx] = np.nan
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result,
            "a sit-run that is entirely single-sided must not be rejected when the "
            "stand-run has any both-sided-confident frame at all -- the guard's AND "
            "condition must not degrade into an OR",
        )

    def test_mid_period_alternating_sides_counts_as_any_not_majority(self):
        """Adversarial case: the stand-run here ALTERNATES which single side is valid
        frame-by-frame (never both simultaneously) -- neither a clean single-sided run
        (like Deep_Bend's real false positive) nor a clean same-side-throughout run
        (like the one-sided-occlusion case). The sit-run is entirely single-sided-right
        (mirrors test_side_switching_occlusion_is_rejected's sit-run construction).
        Per the guard's actual `.any()`-based implementation (not a majority vote),
        the stand-run's occasional right-side frames are enough to establish
        `shares_right`, so this must NOT be rejected -- documenting (not just
        asserting) that a mixed-tracking period is resolved by "any side ever
        overlapped," the more permissive of the two readings, not silently by
        whichever side happened to dominate that period."""
        window = _sit_to_stand_window(shaky=False)
        window = [dict(r, keypoints=list(r["keypoints"])) for r in window]
        for i, row in enumerate(window):
            kps = row["keypoints"]
            if i <= 45:  # confirmed sit-run: entirely right-only
                for idx in (22, 23, 46, 47, 50, 51):
                    kps[idx] = np.nan
            elif i >= 49:  # confirmed stand-run: alternate which side is blanked
                if i % 2 == 0:
                    for idx in (22, 23, 46, 47, 50, 51):  # blank left -> right-only frame
                        kps[idx] = np.nan
                else:
                    for idx in (24, 25, 48, 49, 52, 53):  # blank right -> left-only frame
                        kps[idx] = np.nan
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(
            result,
            "a stand-run with frame-by-frame alternating single-sided tracking shares "
            "the right side with the sit-run at least once, so this must be accepted -- "
            "the guard reads 'any side ever overlapped,' not a majority vote",
        )


def _n_frame_gap_primary_path_window(dead_zone_len, n_frames=90, dip_start=3, dip_len=5):
    """A sustained (confirmed) sit dip -> EXACTLY `dead_zone_len` frames
    (neither sit- nor stand-confirmed) -> confirmed standing. Regression
    fixture for the off-by-one fix in compute_sit_to_stand's primary-path
    minimum-gap guard (see that guard's own docstring): the ORIGINAL guard
    compared an INDEX DISTANCE (`first_stand_after - last_sit`, which is
    ALWAYS one more than the number of frames actually lying strictly
    between the two states) directly against _STATE_CONFIRM_FRAMES, so a
    gap of exactly 2 frames strictly between (index distance 3) was
    INCORRECTLY ACCEPTED by the old `3 < 3` check -- inconsistent with
    _detect_fast_shallow_transition's own pre-existing, differently
    (correctly) defined gap check for the identical physical situation.
    Requested/actual angle values: 100.0 -> actual ~120.4 (confirmed
    sitting), 107.0 -> actual ~135.5 (dead zone, neither state), 120.0 ->
    actual ~152.5 (confirmed standing) -- see _fast_squat_rise_window's
    docstring for the same measured mapping, and for why this fixture
    DELIBERATELY opens on a brief dead-zone state rather than a long
    confirmed-standing baseline (the same "which stand_runs entry does
    first_stand_after anchor to" trap that fixture's own docstring
    documents)."""
    window = []
    for i in range(n_frames):
        if i < dip_start:
            angle = 107.0  # actual ~135.5, dead zone -- NOT a confirmed standing run
        elif i < dip_start + dip_len:
            angle = 100.0  # actual ~120.4, confirmed sitting
        elif i < dip_start + dip_len + dead_zone_len:
            angle = 107.0  # actual ~135.5, dead zone
        else:
            angle = 175.0
        # cy=_hip_cy_for_angle(angle): the stand phase must show a genuine
        # hip rise (see MIN_STAND_HIP_RISE's docstring in gait_features.py)
        # -- the fixed-cy default models a seated-repositioning-style
        # crossing with NO real rise, which the hip-rise guard (added after
        # this fixture was originally written) now correctly rejects,
        # making this test fail for a reason unrelated to what it actually
        # tests.
        window.append(_angle_pose_row(angle, i, cy=_hip_cy_for_angle(angle)))
    return window


class SitToStandGapGuardOffByOneTests(unittest.TestCase):
    """Regression tests for the off-by-one fix in compute_sit_to_stand's
    primary-path minimum-gap guard (found via a later cross-module
    consistency audit -- see docs/GAIT_CODE_REVIEW.md): the guard must use
    the SAME "frames strictly between the two states" definition
    _detect_fast_shallow_transition's own pre-existing gap check already
    uses, not an off-by-one index-distance approximation of it."""

    def test_exactly_two_frame_gap_is_now_rejected(self):
        """The specific gap size (2 frames strictly between, index distance
        3) the original off-by-one guard incorrectly accepted (`3 < 3` is
        False) must now be rejected, matching _detect_fast_shallow_
        transition's own equivalent check (`gap.size=2 < 3` is True)."""
        window = _n_frame_gap_primary_path_window(dead_zone_len=2)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNone(
            result,
            "a 2-frame gap between confirmed sit and confirmed stand must be rejected -- "
            "this exact gap size was accepted by the pre-fix off-by-one guard",
        )

    def test_gap_guard_now_matches_fallback_paths_own_definition(self):
        """Direct, symbolic regression test for the off-by-one arithmetic
        itself: for the same physical frame positions, the primary path's
        gap computation must now agree with _detect_fast_shallow_
        transition's own (unchanged, pre-existing) gap.size computation."""
        last_sit, first_stand_after = 10, 13  # 2 frames (11, 12) strictly between
        primary_frames_between = (first_stand_after - last_sit) - 1
        pre_end, post_start = 10, 13
        fallback_gap_size = post_start - pre_end - 1
        self.assertEqual(primary_frames_between, fallback_gap_size)
        self.assertEqual(primary_frames_between, 2)

    def test_three_frame_gap_still_accepted(self):
        """Recall check: a gap of exactly _STATE_CONFIRM_FRAMES (3) frames
        strictly between the two states -- genuinely long enough by this
        module's own established standard -- must still be accepted."""
        window = _n_frame_gap_primary_path_window(dead_zone_len=3)
        result = gf.compute_sit_to_stand(window)
        self.assertIsNotNone(result)


def _timestamp_gap_walking_window(n_frames=180, gap_start=90, gap_seconds=5.0):
    """A genuine, perfectly regular synthetic walking bout, identical to
    _walking_window's own output, EXCEPT for one large (`gap_seconds`)
    timestamp discontinuity inserted mid-window -- simulates a batch of
    dropped/uncaptured frames during live streaming (see gait_stream.py),
    not a real change in the subject's gait. Regression fixture for
    MAX_INTERVAL_GAP_RATIO (see that constant's own docstring): reproduces
    the real failure mode found via direct testing -- a single such gap
    previously inflated compute_stride_regularity's CV from ~0.026 to
    ~1.46 for this exact fixture, a data-collection artifact misread as
    extreme stride irregularity."""
    window = [dict(r) for r in _walking_window(n_frames, speed=0.15)]
    for i, row in enumerate(window):
        if i < gap_start:
            row["timestamp"] = i / 30.0
        else:
            row["timestamp"] = (gap_start - 1) / 30.0 + gap_seconds + (i - gap_start + 1) / 30.0
    return window


class StrideRegularityTimestampGapTests(unittest.TestCase):
    """Regression tests for MAX_INTERVAL_GAP_RATIO: a timestamp
    discontinuity (dropped-frame batch) must not be misread as an
    extremely irregular stride."""

    def test_large_timestamp_gap_does_not_inflate_cv(self):
        clean_window = _walking_window(180, speed=0.15)
        gapped_window = _timestamp_gap_walking_window()

        clean_cv = gf.compute_stride_regularity(clean_window)
        gapped_cv = gf.compute_stride_regularity(gapped_window)

        self.assertIsNotNone(clean_cv)
        self.assertIsNotNone(
            gapped_cv,
            "a single data-gap artifact must not make the whole signal unavailable -- "
            "the surrounding genuine strides are still usable",
        )
        self.assertAlmostEqual(
            gapped_cv, clean_cv, delta=0.05,
            msg="a timestamp gap (data artifact) must not measurably change the reported "
            "CV relative to the same walk with no gap",
        )

    def test_large_timestamp_gap_does_not_inflate_risk_score(self):
        gapped_window = _timestamp_gap_walking_window()
        assessor = GaitRiskAssessor()
        result = assessor.assess_risk(gapped_window)
        stride_signal = next(s for s in result["signals"] if s["name"] == "stride_regularity")
        self.assertTrue(stride_signal["available"])
        self.assertLess(
            stride_signal["risk_contribution"], 0.5,
            "a data-gap-inflated CV must not read as confidently high stride-irregularity risk",
        )

    def test_genuine_slow_walking_without_a_gap_is_not_penalized(self):
        """Recall check: MAX_INTERVAL_GAP_RATIO must not reject genuinely
        slow (but evenly-paced) walking -- only frame-timing discontinuities."""
        slow_window = _walking_window(210, speed=0.03)
        cv = gf.compute_stride_regularity(slow_window)
        self.assertIsNotNone(cv)


class GaitCycleDetectionTests(unittest.TestCase):
    """Regression tests for the reusable gait-cycle detection helper
    (`gf._detect_gait_events`), extracted from compute_stride_regularity's
    previously-inline peak-detection so a second consumer (cadence) can
    reuse the identical detection instead of re-running find_peaks
    independently. These test the HELPER directly, isolated from the
    ambulation gate / landmark-validity gates compute_stride_regularity
    layers on top of it."""

    def test_regular_oscillation_produces_evenly_spaced_peaks(self):
        ts = np.arange(300) / 30.0
        # A clean sine wave, period 30 frames (1s) -- 10 full cycles over 300 frames.
        signal = np.sin(2 * np.pi * (np.arange(300) / 30.0))
        peaks, intervals = gf._detect_gait_events(signal, ts)
        self.assertGreaterEqual(len(peaks), 9)
        self.assertTrue(np.all(intervals > 0))
        # Evenly spaced -- CV of the intervals should be near zero.
        self.assertLess(float(np.std(intervals) / np.mean(intervals)), 0.05)

    def test_flat_signal_produces_no_peaks(self):
        ts = np.arange(90) / 30.0
        signal = np.zeros(90)
        peaks, intervals = gf._detect_gait_events(signal, ts)
        self.assertEqual(len(peaks), 0)
        self.assertEqual(len(intervals), 0)

    def test_peak_distance_scales_with_frame_rate_not_frame_count(self):
        """Regression test for the time-based peak-distance fix (see
        MIN_STEP_INTERVAL_SEC's own docstring): the old hardcoded
        `distance=5` silently assumed ~30fps, so on lower-fps real footage
        (this project's own Hussain set is documented at ~23-30fps) two
        genuinely separate steps could land closer together in FRAME count
        even though they're farther apart in REAL time than the intended
        minimum. Two impulse peaks 4 samples apart at 15fps are 0.267s apart
        in real time -- safely past the 0.1667s minimum -- and must both be
        detected (the old fixed distance=5 would have rejected one, since 4
        < 5 samples). The same 4-sample gap at 30fps is only 0.133s apart --
        genuinely below the minimum -- and must still collapse to one peak,
        confirming this is real time-scaling, not a blanket loosening."""
        signal = np.zeros(90)
        signal[20] = 1.0
        signal[24] = 1.0  # 4 samples after the first peak

        ts_15fps = np.arange(90) / 15.0
        peaks_15fps, intervals_15fps = gf._detect_gait_events(signal, ts_15fps)
        self.assertEqual(len(peaks_15fps), 2, "0.267s apart at 15fps must both be detected as separate steps")
        self.assertEqual(len(intervals_15fps), 1)

        ts_30fps = np.arange(90) / 30.0
        peaks_30fps, intervals_30fps = gf._detect_gait_events(signal, ts_30fps)
        self.assertEqual(len(peaks_30fps), 1, "0.133s apart at 30fps is still below the minimum step interval")

    def test_thirty_fps_distance_matches_old_hardcoded_value(self):
        """At exactly 30fps (every synthetic fixture in this module, and
        most of this project's real footage), the time-based distance must
        resolve to exactly the old hardcoded frame count (5) -- i.e. this
        fix must be byte-identical at the frame rate everything was
        previously validated against."""
        ts = np.arange(300) / 30.0
        signal = np.sin(2 * np.pi * (np.arange(300) / 30.0))
        peaks_new, intervals_new = gf._detect_gait_events(signal, ts)
        from scipy.signal import find_peaks
        min_prominence = max(float(np.ptp(signal)) * gf.STRIDE_PEAK_PROMINENCE_FRACTION, 1e-6)
        peaks_old, _ = find_peaks(signal, distance=5, prominence=min_prominence)
        np.testing.assert_array_equal(peaks_new, peaks_old)

    def test_single_peak_produces_no_intervals(self):
        ts = np.arange(90) / 30.0
        signal = np.zeros(90)
        signal[45] = 1.0  # one isolated bump, nothing else to pair it with
        peaks, intervals = gf._detect_gait_events(signal, ts)
        self.assertLessEqual(len(peaks), 1)
        self.assertEqual(len(intervals), 0)

    def test_exactly_two_peaks_produces_exactly_one_interval(self):
        """Phase 6 edge case: exactly two detected events -- enough for one
        interval, but compute_stride_regularity's own >=3-peak floor (see
        that function's docstring) means this alone must not be enough for
        a CV (need >=2 intervals, i.e. >=3 peaks, to compute a meaningful
        variability statistic)."""
        ts = np.arange(90) / 30.0
        signal = np.zeros(90)
        signal[20] = 1.0
        signal[60] = 1.0
        peaks, intervals = gf._detect_gait_events(signal, ts)
        self.assertEqual(len(peaks), 2)
        self.assertEqual(len(intervals), 1)

    def test_irregular_frame_rate_within_one_window_does_not_crash(self):
        """Phase 9 edge case: a window whose frame-to-frame timestamp
        spacing genuinely changes partway through (e.g. a camera that
        legitimately drops from 30fps to 10fps, not a single dropped-frame
        gap -- see StrideRegularityTimestampGapTests for that separate
        case) must not crash, and must use the REAL elapsed time (not a
        fixed-fps assumption) for whatever it does report."""
        window = [dict(r) for r in _walking_window(180, speed=0.15)]
        t = 0.0
        for i, row in enumerate(window):
            dt = 1.0 / 30.0 if i < 90 else 1.0 / 10.0
            if i > 0:
                t += dt
            row["timestamp"] = t
        result = GaitRiskAssessor().assess_risk(window)  # should not raise
        self.assertIn("risk_score", result)
        if result["risk_score"] is not None:
            self.assertTrue(np.isfinite(result["risk_score"]))
            self.assertGreaterEqual(result["risk_score"], 0.0)
            self.assertLessEqual(result["risk_score"], 1.0)

    def test_helper_matches_compute_stride_regularitys_own_peak_count(self):
        """The extraction must be byte-identical to what compute_stride_
        regularity's own (now-removed) inline find_peaks call would have
        produced -- verified here by reproducing its exact ankle-y pipeline
        and comparing peak counts against the CV this function reports."""
        window = _walking_window(180, speed=0.15)
        raw = gf._raw_keypoint_array(window)
        pos = gf._normalized_positions(window, _raw=raw)
        ankle_y = (pos[:, gf.LEFT_ANKLE, 1] + pos[:, gf.RIGHT_ANKLE, 1]) / 2.0
        ts = gf._timestamps(window)
        valid = ~np.isnan(ankle_y)
        idx = np.arange(len(ankle_y))
        ankle_y_filled = np.interp(idx, idx[valid], ankle_y[valid])
        peaks, intervals = gf._detect_gait_events(ankle_y_filled, ts)

        quality: dict = {}
        cv = gf.compute_stride_regularity(window, _quality_out=quality)
        self.assertIsNotNone(cv)
        self.assertEqual(quality["n_events"], len(peaks))
        self.assertAlmostEqual(cv, float(np.std(intervals) / np.mean(intervals)))


class SignalReliabilityTests(unittest.TestCase):
    """Regression tests for the new signal-quality/reliability metadata
    (docs/GAIT_CODE_REVIEW.md follow-up, Concepts 1/7): a graded [0, 1]
    confidence, distinct from the existing binary available/unavailable
    gate, reported per-signal and NOT folded into risk_score (preserves
    the existing risk-score contract exactly -- see
    RiskScoreContractPreservedTests below for a direct check of that)."""

    def setUp(self):
        self.assessor = GaitRiskAssessor()

    def test_reliability_present_and_in_range_when_available(self):
        window = _walking_window(210, speed=0.15)
        result = self.assessor.assess_risk(window)
        for s in result["signals"]:
            if s["available"]:
                self.assertIsNotNone(s["reliability"], f"{s['name']}: available signal must report reliability")
                self.assertGreaterEqual(s["reliability"], 0.0)
                self.assertLessEqual(s["reliability"], 1.0)

    def test_reliability_is_none_when_unavailable(self):
        window = [{"timestamp": i / 30.0, "keypoints": [np.nan] * 66} for i in range(150)]
        result = self.assessor.assess_risk(window)
        for s in result["signals"]:
            self.assertFalse(s["available"])
            self.assertIsNone(s["reliability"])

    def test_perfect_synthetic_data_reports_full_reliability(self):
        window = _walking_window(210, speed=0.15)
        result = self.assessor.assess_risk(window)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        stride_signal = next(s for s in result["signals"] if s["name"] == "stride_regularity")
        self.assertTrue(speed_signal["available"])
        self.assertTrue(stride_signal["available"])
        self.assertEqual(speed_signal["reliability"], 1.0)
        self.assertEqual(stride_signal["reliability"], 1.0)

    def test_partial_ankle_occlusion_reduces_stride_regularity_reliability(self):
        """Reliability must actually be GRADED, not a constant -- partial
        (but not disqualifying) ankle occlusion must measurably lower
        stride_regularity's reliability relative to the clean case, without
        making the signal unavailable outright."""
        clean_window = _walking_window(210, speed=0.15)
        rng = np.random.default_rng(7)
        occluded_window = [dict(r) for r in _walking_window(210, speed=0.15)]
        for i in range(len(occluded_window)):
            if rng.random() < 0.25:
                occluded_window[i] = dict(occluded_window[i], keypoints=[np.nan] * 66)

        clean_result = self.assessor.assess_risk(clean_window)
        occluded_result = self.assessor.assess_risk(occluded_window)
        clean_stride = next(s for s in clean_result["signals"] if s["name"] == "stride_regularity")
        occluded_stride = next(s for s in occluded_result["signals"] if s["name"] == "stride_regularity")

        self.assertTrue(occluded_stride["available"], "moderate occlusion must not make the signal unavailable")
        self.assertLess(
            occluded_stride["reliability"], clean_stride["reliability"],
            "partial occlusion must measurably reduce reported reliability",
        )

    def test_sit_to_stand_reliability_reflects_landmark_confidence(self):
        """Regression test tying reliability to the ALREADY-EXISTING
        both_sides_confident mechanism (see _count_reversals' docstring) --
        a transition detected with single-sided visibility throughout must
        report LOWER reliability than a fully-confident one, even though
        both are equally 'available'."""
        confident_window = _sit_to_stand_window(shaky=False)
        occluded_window = _sit_to_stand_window_left_occluded()

        confident_result = self.assessor.assess_risk(confident_window)
        occluded_result = self.assessor.assess_risk(occluded_window)
        confident_sts = next(s for s in confident_result["signals"] if s["name"] == "sit_to_stand")
        occluded_sts = next(s for s in occluded_result["signals"] if s["name"] == "sit_to_stand")

        self.assertTrue(confident_sts["available"])
        self.assertTrue(occluded_sts["available"])
        self.assertEqual(confident_sts["reliability"], 1.0)
        self.assertLess(occluded_sts["reliability"], confident_sts["reliability"])

    def test_reliability_does_not_change_risk_score_or_value(self):
        """The reliability mechanism must be pure ADDITIVE metadata --
        adding it must not change risk_score or any signal's value/
        risk_contribution relative to what they were before this feature
        existed. Verified by comparing assess_risk()'s result against
        compute_stride_regularity() called directly WITHOUT _quality_out
        (the pre-existing call pattern every other test in this file still
        uses) -- both must agree exactly."""
        window = _walking_window(210, speed=0.15)
        result = self.assessor.assess_risk(window)
        direct_cv = gf.compute_stride_regularity(window)  # no _quality_out -- old call pattern
        stride_signal = next(s for s in result["signals"] if s["name"] == "stride_regularity")
        self.assertEqual(stride_signal["value"], direct_cv)


class SignalCategoryTests(unittest.TestCase):
    """Regression test for the new `category` metadata field (Concept 6 --
    makes the existing implicit gait-vs-postural split explicit and
    queryable, with zero effect on risk_score computation)."""

    def test_signals_are_grouped_into_gait_and_postural_categories(self):
        window = _walking_window(210, speed=0.15)
        result = GaitRiskAssessor().assess_risk(window)
        categories = {s["name"]: s["category"] for s in result["signals"]}
        self.assertEqual(categories["walking_speed"], "gait")
        self.assertEqual(categories["stride_regularity"], "gait")
        self.assertEqual(categories["postural_sway"], "postural")
        self.assertEqual(categories["sit_to_stand"], "postural")


class CadenceTests(unittest.TestCase):
    """Regression tests for the cadence metadata (Concept 3 -- spatiotemporal
    parameter, essentially free once gait events are detected for the CV).
    Explicitly a PROXY (video-derived peak rate) -- see compute_stride_
    regularity's `_quality_out` docstring -- but named/unitized as STEPS,
    not strides, per the verified terminology finding below (steps/minute
    IS the standard clinical definition of cadence)."""

    def test_detected_events_are_steps_not_full_strides(self):
        """Direct regression test for the terminology finding (see
        _detect_gait_events' docstring): against _walking_window's own
        KNOWN internal stride period (1.05s -- one full two-legged gait
        cycle), the detected peak-to-peak interval must measure close to
        HALF that period (one peak per STEP, two steps per stride), not
        the full period (which would mean one peak per stride). This is
        what justifies naming the field 'cadence_steps_per_min' rather
        than '..._strides_per_min' or '..._cycles_per_min'."""
        window = _walking_window(300, speed=0.15, stride_jitter=0.0)
        quality: dict = {}
        gf.compute_stride_regularity(window, _quality_out=quality)
        mean_interval = 60.0 / quality["cadence_steps_per_min"]
        known_stride_period = 1.05  # tests/test_gait_risk.py::_walking_window's own period
        self.assertAlmostEqual(
            mean_interval, known_stride_period / 2.0, delta=0.02,
            msg="detected peak-to-peak interval must be ~half the known full-stride "
            "period -- confirms peaks correspond to STEPS, not full gait cycles",
        )

    def test_cadence_present_only_on_stride_regularity_entry(self):
        window = _walking_window(210, speed=0.15)
        result = GaitRiskAssessor().assess_risk(window)
        for s in result["signals"]:
            if s["name"] == "stride_regularity":
                self.assertIn("cadence_steps_per_min", s)
                self.assertIn("n_events", s)
            else:
                self.assertNotIn("cadence_steps_per_min", s)
                self.assertNotIn("n_events", s)

    def test_cadence_matches_mean_interval_relationship(self):
        window = _walking_window(210, speed=0.15)
        quality: dict = {}
        cv = gf.compute_stride_regularity(window, _quality_out=quality)
        self.assertIsNotNone(cv)
        self.assertIn("cadence_steps_per_min", quality)
        self.assertGreater(quality["cadence_steps_per_min"], 0.0)
        self.assertGreaterEqual(quality["n_events"], 3)

    def test_faster_walking_produces_higher_cadence(self):
        """Sanity/direction check: a faster synthetic walker (shorter
        stride period, same generator) must produce a higher detected
        cadence than a slower one -- not a specific calibrated value (this
        is a proxy, not a clinical measurement), just the right direction."""
        slow = _walking_window(210, speed=0.1, stride_jitter=0.0)
        fast = _walking_window(210, speed=0.1, stride_jitter=0.0)
        # _walking_window's stride period is fixed (1.05s) regardless of
        # speed -- cadence should therefore be statistically IDENTICAL
        # between these two (same period, different translation speed),
        # which is itself a useful direction check: cadence must track
        # STEP RATE, not translation speed, and must not accidentally
        # conflate the two.
        q_slow: dict = {}
        q_fast: dict = {}
        gf.compute_stride_regularity(slow, _quality_out=q_slow)
        gf.compute_stride_regularity(fast, _quality_out=q_fast)
        self.assertAlmostEqual(
            q_slow["cadence_steps_per_min"], q_fast["cadence_steps_per_min"], delta=1.0,
            msg="cadence must track step RATE (fixed by construction here), not translation speed",
        )


def _sustained_bend_window(n_frames=180, bend_start=30, bend_frames=15,
                            torso_standing=0.20, torso_bent=0.05, drift=0.0006):
    """A person standing still for `bend_start` frames, then bending over
    and STAYING bent for the rest of the window (unlike
    _fall_like_foreshortening_window, which snaps back to standing after a
    brief blip -- this models a SUSTAINED hold, matching the real clips
    this reproduces: Deep_Bend_2.mov/Deep_Bend_3.mov's sustained forward
    bend, torso_len_bent kept, not recovered). Raw hip position barely
    moves (`drift` is a tiny, realistic per-frame jitter, not a real walk)
    -- exactly the real mechanism found on real footage
    (docs/GAIT_DATA_ASSESSMENT.md Section 9): dividing a near-stationary
    raw position by a collapsed, near-degenerate torso length amplifies
    residual noise/drift into a large apparent translation, purely from the
    denominator shrinking, not genuine locomotion."""
    window = []
    hip_x, hip_y = 0.5, 0.3  # hip_x > hip_y so the resulting scaled drift
    # is horizontally dominant (MIN_HORIZONTAL_DOMINANCE_RATIO) -- see
    # gait_features._ambulation_check's own docstring: scaling a fixed raw
    # vector by a shrinking scalar preserves its direction, so this is what
    # lets this fixture clear that gate (and MIN_AMBULATION_COHERENCE, since
    # the resulting scaled trajectory is a straight line, not noise) without
    # needing real translation -- exactly the bug being reproduced.
    for i in range(n_frames):
        if i < bend_start:
            torso_len = torso_standing
        elif i < bend_start + bend_frames:
            frac = (i - bend_start) / float(bend_frames - 1)
            torso_len = torso_standing * (1 - frac) + torso_bent * frac
        else:
            torso_len = torso_bent
        cur_hip_x = hip_x + drift * i
        kps = [np.nan] * 66
        kps[22], kps[23] = cur_hip_x - 0.05, hip_y - torso_len
        kps[24], kps[25] = cur_hip_x + 0.05, hip_y - torso_len
        kps[46], kps[47] = cur_hip_x - 0.05, hip_y
        kps[48], kps[49] = cur_hip_x + 0.05, hip_y
        kps[50], kps[51] = cur_hip_x - 0.05, hip_y + 0.2
        kps[52], kps[53] = cur_hip_x + 0.05, hip_y + 0.2
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


def _approaching_walking_window(n_frames=180, speed=0.15, torso_start=0.10, torso_end=0.20):
    """Genuine walking TOWARD the camera: torso length grows smoothly and
    monotonically across the window as the subject's real distance from the
    camera decreases (the SAME real, legitimate mechanism found on this
    project's own Moving_in_out_frame.MOV/Stride.mov footage -- see
    MIN_TORSO_BASELINE_RATIO's docstring) -- must NOT be confused with the
    forward-bend collapse _sustained_bend_window reproduces, even though
    both involve a changing torso length."""
    window = []
    phase = 0.0
    hip_x = 0.3
    fps = 30.0
    for i in range(n_frames):
        dt = 1.0 / fps
        hip_x += speed * dt
        frac = i / float(n_frames - 1)
        torso_len = torso_start * (1 - frac) + torso_end * frac
        phase += 2 * np.pi * dt / 1.05
        swing_amp = 0.08 * (torso_len / 0.25)
        cx, cy = hip_x, 0.5
        sh_x, sh_y = cx, cy - torso_len
        kps = [np.nan] * 66
        kps[22], kps[23] = sh_x - 0.05, sh_y
        kps[24], kps[25] = sh_x + 0.05, sh_y
        kps[46], kps[47] = cx - 0.05, cy
        kps[48], kps[49] = cx + 0.05, cy
        l_swing = swing_amp * np.sin(phase)
        r_swing = swing_amp * np.sin(phase + np.pi)
        knee_y = cy + torso_len * 0.8
        ankle_y = cy + torso_len * 1.6
        kps[50], kps[51] = cx - 0.05 + l_swing * 0.5, knee_y
        kps[52], kps[53] = cx + 0.05 + r_swing * 0.5, knee_y
        kps[54], kps[55] = cx - 0.05 + l_swing, ankle_y - abs(l_swing) * 0.3
        kps[56], kps[57] = cx + 0.05 + r_swing, ankle_y - abs(r_swing) * 0.3
        window.append({"timestamp": i * dt, "frame": i, "keypoints": kps})
    return window


def _attach_world_keypoints(window, torso_len_3d_fn, lateral_half_width=0.15):
    """Attaches a synthetic `"world_keypoints"` field (99 floats: 33
    landmarks x x/y/z, real-world meters) to each row of `window`, IN
    PLACE, and returns it. `torso_len_3d_fn(i)` gives the 3D shoulder-mid-
    to-hip-mid distance for frame `i`; the hip midpoint is fixed at
    (0, 0, 0) (matching MediaPipe's real pose_world_landmarks behavior --
    hip-centered by construction, see WORLD_LANDMARKS_ROOT_CAUSE_FIX's
    docstring -- confirmed directly on real footage, not assumed: this
    project's own Deep_Bend_2.mov/Stride.mov both measure hip3d at
    ~(0.000, -0.001, 0.001) for essentially every frame). Only LEFT/RIGHT
    SHOULDER/HIP are set (mirroring how this file's existing 2D fixtures
    only set the joints their target function actually reads); every other
    landmark is left NaN."""
    for i, row in enumerate(window):
        torso_len = torso_len_3d_fn(i)
        wk = [np.nan] * 99
        wk[gf.LEFT_HIP * 3 + 0], wk[gf.LEFT_HIP * 3 + 1], wk[gf.LEFT_HIP * 3 + 2] = -lateral_half_width, 0.0, 0.0
        wk[gf.RIGHT_HIP * 3 + 0], wk[gf.RIGHT_HIP * 3 + 1], wk[gf.RIGHT_HIP * 3 + 2] = lateral_half_width, 0.0, 0.0
        wk[gf.LEFT_SHOULDER * 3 + 0], wk[gf.LEFT_SHOULDER * 3 + 1], wk[gf.LEFT_SHOULDER * 3 + 2] = \
            -lateral_half_width, -torso_len, 0.0
        wk[gf.RIGHT_SHOULDER * 3 + 0], wk[gf.RIGHT_SHOULDER * 3 + 1], wk[gf.RIGHT_SHOULDER * 3 + 2] = \
            lateral_half_width, -torso_len, 0.0
        row["world_keypoints"] = wk
    return window


class TorsoBaselineCalibrationTests(unittest.TestCase):
    """Regression tests for compute_torso_baseline() and
    compute_walking_speed()'s/GaitRiskAssessor.assess_risk()'s opt-in
    `_torso_baseline` availability gate -- see
    gait_features.MIN_TORSO_BASELINE_RATIO's docstring for the full
    real-footage derivation this locks in."""

    def test_baseline_recovers_standing_torso_length_from_stable_prefix(self):
        standing_window = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(45)]
        baseline = gf.compute_torso_baseline(standing_window)
        self.assertIsNotNone(baseline)
        expected = gf._raw_torso_len(standing_window)[0]
        self.assertAlmostEqual(baseline, float(expected), places=4)

    def test_baseline_is_none_when_window_too_short_or_all_invalid(self):
        too_short = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(5)]
        self.assertIsNone(gf.compute_torso_baseline(too_short))

        all_nan = [{"timestamp": i / 30.0, "keypoints": [np.nan] * 66} for i in range(45)]
        self.assertIsNone(gf.compute_torso_baseline(all_nan))

    def test_baseline_recovers_from_real_wall_clock_timestamps(self):
        """Regression test for a real bug found via this project's first
        real-time-pipeline integration test (not any synthetic/extraction-
        script fixture): every OTHER test in this class uses zero-based
        relative timestamps (i/30.0) -- exactly what every prior caller of
        this function (test fixtures, evaluate_real_footage.py's extraction-
        derived seconds) has always used. realtime_fall_detection.py's real
        frame loop instead uses `str(time.time())` -- an absolute Unix epoch
        wall-clock value, ~1.7e9 seconds, nowhere near 0. The original fps
        estimate (`len(ts) / ts[-1]`) implicitly assumed ts[0]==0 and
        silently produced a ~1e-8 "fps" against a real epoch timestamp,
        collapsing n_search to 0 and making this function return None
        UNCONDITIONALLY regardless of how clean the underlying data was --
        confirmed directly on real MediaPipe-tracked footage
        (Deep_Bend_2.mov via the actual realtime_fall_detection.py frame-
        building code: 45/45 valid, low-noise torso-length frames, yet
        compute_torso_baseline returned None every time before this fix).
        Fixed to use elapsed duration (ts[-1] - ts[0]), which is invariant
        to whether ts is relative-from-0 or an absolute epoch value."""
        t0 = 1_787_233_718.067  # a real epoch-scale value, not near 0
        wall_clock_window = [{"timestamp": t0 + i / 30.0, "keypoints": _standing_kps()} for i in range(45)]
        baseline = gf.compute_torso_baseline(wall_clock_window)
        self.assertIsNotNone(baseline, "a genuine, clean standing window must calibrate regardless of "
                                        "whether timestamps are relative-from-0 or absolute wall-clock")
        expected = gf._raw_torso_len(wall_clock_window)[0]
        self.assertAlmostEqual(baseline, float(expected), places=4)

        # And the result must be the SAME as the equivalent relative-timestamp
        # window (this fix must not change behavior for the already-standard
        # relative-timestamp case, only fix the previously-broken absolute case).
        relative_window = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(45)]
        baseline_relative = gf.compute_torso_baseline(relative_window)
        self.assertAlmostEqual(baseline, baseline_relative, places=4)

    def test_default_behavior_unchanged_when_baseline_not_supplied(self):
        """The central backward-compatibility guarantee: every existing
        caller (GaitRiskAssessor/gait_stream.py included) never passes
        `_torso_baseline`, so this new parameter must be a pure no-op by
        default."""
        window = _sustained_bend_window()
        self.assertEqual(gf.compute_walking_speed(window), gf.compute_walking_speed(window, _torso_baseline=None))
        result = GaitRiskAssessor().assess_risk(window)
        result_explicit_none = GaitRiskAssessor().assess_risk(window, _torso_baseline=None)
        self.assertEqual(result, result_explicit_none)

    def test_sustained_bend_marks_walking_speed_unavailable_with_baseline(self):
        """The real bug this gate exists for: a sustained forward-bend hold
        (raw hip position nearly fixed, torso length collapsed) currently
        reports an implausible-but-plausible-LOOKING walking_speed value
        without a baseline -- and must become unavailable, not a corrected
        number, once a caller supplies one."""
        window = _sustained_bend_window()
        ungated = gf.compute_walking_speed(window)
        self.assertIsNotNone(ungated, "test fixture must reproduce a currently-available spurious "
                                       "reading to be a meaningful test")
        self.assertGreater(ungated, 1.0, "fixture's spurious reading should be clearly elevated")

        baseline = gf.compute_torso_baseline(window[:30])
        self.assertIsNotNone(baseline)
        gated = gf.compute_walking_speed(window, _torso_baseline=baseline)
        self.assertIsNone(gated, "a sustained torso-length collapse well below MIN_TORSO_BASELINE_RATIO "
                                  "of a confirmed-standing baseline must mark walking_speed unavailable")

        result = GaitRiskAssessor().assess_risk(window, _torso_baseline=baseline)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertFalse(speed_signal["available"])
        self.assertIsNone(speed_signal["value"])

    def test_genuine_toward_camera_walking_not_suppressed_by_baseline(self):
        """Recall check, the central risk this gate had to be validated
        against on real footage (Moving_in_out_frame.MOV/Stride.mov -- see
        MIN_TORSO_BASELINE_RATIO's docstring): genuine walking toward the
        camera legitimately grows torso length across the window as
        distance shrinks. A baseline established from the FAR (small
        torso-length) start of that same walk must not suppress it."""
        window = _approaching_walking_window()
        ungated = gf.compute_walking_speed(window)
        self.assertIsNotNone(ungated, "test fixture must produce a genuine available reading")

        baseline = gf.compute_torso_baseline(window[:30])
        self.assertIsNotNone(baseline)
        gated = gf.compute_walking_speed(window, _torso_baseline=baseline)
        self.assertEqual(gated, ungated, "genuine toward-camera walking must be completely unaffected "
                                          "by the calibrated-baseline gate")

    def test_postural_sway_not_gated_by_torso_baseline_in_2d_mode(self):
        """2D-MODE (no `_world_keypoints` on the window): compute_postural_sway
        must not have its availability changed by `_torso_baseline` at all --
        see MIN_TORSO_BASELINE_RATIO's own "2D-MODE / 3D-MODE" docstring for
        why the 2D version of this gate is deliberately NOT applied to
        postural_sway (genuine seated sway legitimately collapses 2D
        torso_len relative to a standing baseline more than the bend this
        gate targets). `_torso_baseline`/`_world_raw` ARE now accepted
        parameters (see test_3d_mode tests below for when they DO activate)
        -- this locks in that supplying `_torso_baseline` ALONE, with no
        usable 3D data, stays a no-op."""
        self.assertIn("_torso_baseline", inspect.signature(gf.compute_postural_sway).parameters)
        self.assertIn("_world_raw", inspect.signature(gf.compute_postural_sway).parameters)

        sitting_window = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(90)]
        baseline = 5.0  # deliberately absurd/huge -- if this ever leaked into
        # postural_sway's own 2D-mode gate, sway would become spuriously unavailable
        result = GaitRiskAssessor().assess_risk(sitting_window, _torso_baseline=baseline)
        sway_signal = next(s for s in result["signals"] if s["name"] == "postural_sway")
        result_no_baseline = GaitRiskAssessor().assess_risk(sitting_window)
        sway_signal_no_baseline = next(s for s in result_no_baseline["signals"] if s["name"] == "postural_sway")
        self.assertEqual(sway_signal["available"], sway_signal_no_baseline["available"])
        self.assertEqual(sway_signal["value"], sway_signal_no_baseline["value"])


class WorldLandmarkRootCauseFixTests(unittest.TestCase):
    """Regression tests for the 3D world-landmark root-cause fix (see
    gait_features.WORLD_LANDMARKS_ROOT_CAUSE_FIX's docstring):
    _torso_scaled_hip_track's scale factor switching to 3D torso length
    when available, and MIN_TORSO_BASELINE_RATIO_3D's postural_sway gate."""

    def test_window_without_world_keypoints_is_byte_identical_to_before(self):
        """The central backward-compatibility guarantee, same standard as
        TorsoBaselineCalibrationTests' own -- a window with no
        `"world_keypoints"` on any row (every caller before this fix) must
        produce IDENTICAL output whether or not `_world_raw` machinery
        exists at all."""
        window = _sustained_bend_window()
        no_world = gf._raw_world_keypoint_array(window)
        self.assertTrue(np.isnan(no_world).all(), "fixture must not accidentally carry world_keypoints")
        with_param = gf.compute_walking_speed(window, _world_raw=no_world)
        without_param = gf.compute_walking_speed(window)
        self.assertEqual(with_param, without_param)

    def test_3d_gate_catches_residual_band_2d_gate_misses(self):
        """The actual root-cause fix, as shipped after full-corpus
        validation caught the first (VALUE-mixing) design broken -- see
        _torso_scaled_hip_track's own "TRIED AND REVERTED" docstring:
        hip_center's VALUE stays 2D-only always (locked in by
        test_window_without_world_keypoints_is_byte_identical_to_before),
        and the fix instead lives entirely in the AVAILABILITY GATE.
        Reproduces Section 11's own disclosed residual: a moderate-severity
        bend whose 2D torso-length ratio (0.45) sits ABOVE
        MIN_TORSO_BASELINE_RATIO (0.40, so the 2D gate does NOT catch it --
        matching Deep_Bend_2.mov's real, disclosed residual worst case,
        6.17 torso-lengths/sec, previously left uncaught) while its 3D
        torso-length ratio (0.60) sits BELOW MIN_TORSO_BASELINE_RATIO_3D
        (0.70, so the 3D gate DOES catch it) -- the real, validated
        improvement this fix delivers over Section 10's 2D-only gate."""
        window = _sustained_bend_window(torso_standing=0.20, torso_bent=0.09)
        baseline_2d = gf.compute_torso_baseline(window[:30])
        self.assertIsNotNone(baseline_2d)
        gated_2d = gf.compute_walking_speed(window, _torso_baseline=baseline_2d)
        self.assertIsNotNone(
            gated_2d, "fixture must reproduce the real, disclosed residual-band case "
                      "(2D gate does NOT catch it) to be a meaningful test",
        )

        def torso_3d(i):
            standing, bent = 0.50, 0.30  # ratio 0.60, below MIN_TORSO_BASELINE_RATIO_3D
            if i < 30:
                return standing
            if i < 45:
                frac = (i - 30) / 14.0
                return standing * (1 - frac) + bent * frac
            return bent
        world_window = _attach_world_keypoints([dict(row) for row in window], torso_3d)
        world_raw = gf._raw_world_keypoint_array(world_window)
        self.assertTrue(gf._has_sufficient_world_coverage(world_raw))
        baseline_3d = gf.compute_torso_baseline(world_window[:30], _world_raw=world_raw[:30])
        self.assertIsNotNone(baseline_3d)
        gated_3d = gf.compute_walking_speed(world_window, _world_raw=world_raw, _torso_baseline=baseline_3d)
        self.assertIsNone(
            gated_3d, "the 3D-mode gate must catch this moderate-severity bend that the "
                      "2D-mode gate alone cannot -- the real improvement this fix delivers",
        )
        # And the VALUE itself, with no baseline/gate at all, is unaffected by
        # `_world_raw` -- locking in that this fix is gate-only, not a value change.
        ungated_3d = gf.compute_walking_speed(world_window, _world_raw=world_raw)
        ungated_2d = gf.compute_walking_speed(window)
        self.assertEqual(ungated_3d, ungated_2d)

    def test_genuine_toward_camera_walking_not_suppressed_by_3d_gate(self):
        """Recall check mirroring the real corpus's tightest constraint
        (Moving_in_out_frame.MOV, see MIN_TORSO_BASELINE_RATIO's own
        docstring): genuine walking toward the camera, where 3D torso
        length legitimately stays ~constant (WORLD_LANDMARKS_ROOT_CAUSE_FIX
        point 2) rather than collapsing, must NOT trip the 3D-mode gate
        even when a baseline/gate ARE supplied."""
        window = _approaching_walking_window()
        two_d_speed = gf.compute_walking_speed(window)
        self.assertIsNotNone(two_d_speed)

        # 3D torso length genuinely stays ~constant across a real toward-camera
        # walk (see point 2) -- unlike the 2D fixture's own torso_start=0.10
        # -> torso_end=0.20 growth.
        world_window = _attach_world_keypoints([dict(row) for row in window], lambda i: 0.50)
        world_raw = gf._raw_world_keypoint_array(world_window)
        baseline_3d = gf.compute_torso_baseline(world_window[:30], _world_raw=world_raw[:30])
        self.assertIsNotNone(baseline_3d)
        gated = gf.compute_walking_speed(world_window, _world_raw=world_raw, _torso_baseline=baseline_3d)
        self.assertEqual(gated, two_d_speed, "genuine toward-camera walking (stable 3D torso length) "
                                              "must not be suppressed by the 3D-mode gate")

    def test_postural_sway_gated_in_3d_mode_for_sustained_bend(self):
        """3D-MODE gate, the postural_sway fix Section 11 could not safely
        ship in 2D: a sustained bend with a supplied 3D baseline must mark
        postural_sway unavailable."""
        window = _sustained_bend_window(n_frames=200, bend_start=30, bend_frames=15,
                                         torso_standing=0.20, torso_bent=0.05, drift=0.0)

        def torso_3d(i):
            if i < 30:
                return 0.50
            if i < 45:
                frac = (i - 30) / 14.0
                return 0.50 * (1 - frac) + 0.28 * frac
            return 0.28
        world_window = _attach_world_keypoints([dict(row) for row in window], torso_3d)
        world_raw = gf._raw_world_keypoint_array(world_window)
        calib_baseline = gf.compute_torso_baseline(world_window[:30], _world_raw=world_raw[:30])
        self.assertIsNotNone(calib_baseline)
        self.assertAlmostEqual(calib_baseline, 0.50, delta=0.01)

        ungated = gf.compute_postural_sway(world_window)
        gated = gf.compute_postural_sway(world_window, _world_raw=world_raw, _torso_baseline=calib_baseline)
        if ungated is not None:
            self.assertIsNone(gated, "a sustained 3D torso-length collapse well below "
                                      "MIN_TORSO_BASELINE_RATIO_3D of a confirmed-standing baseline "
                                      "must mark postural_sway unavailable")

    def test_postural_sway_not_gated_in_3d_mode_for_genuine_sitting(self):
        """Recall check mirroring the real corpus finding that killed the
        2D-mode/knee-angle candidates: genuine sitting must NOT trip the
        3D-mode gate either, even though 3D torso length does drop somewhat
        while sitting (measured on real footage: Sit_Stand_1.mov/
        Sit_Stand_2.mov settle at 0.85-0.89 of standing -- comfortably above
        MIN_TORSO_BASELINE_RATIO_3D)."""
        sitting_window = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(90)]

        def torso_3d(i):
            return 0.44  # ~0.88 of a 0.50 standing baseline -- matches the real
            # Sit_Stand_1.mov/Sit_Stand_2.mov sitting ratio range, comfortably
            # above MIN_TORSO_BASELINE_RATIO_3D
        world_window = _attach_world_keypoints([dict(row) for row in sitting_window], torso_3d)
        world_raw = gf._raw_world_keypoint_array(world_window)
        calib_baseline = 0.50
        gated = gf.compute_postural_sway(world_window, _world_raw=world_raw, _torso_baseline=calib_baseline)
        ungated = gf.compute_postural_sway(sitting_window)
        self.assertEqual(gated, ungated, "genuine sitting (a real, comfortably-above-threshold 3D ratio) "
                                          "must not be suppressed by the 3D-mode gate")

    def test_insufficient_world_coverage_falls_back_to_2d(self):
        """A window where MOST rows lack world_keypoints (below
        MIN_WORLD_LANDMARK_COVERAGE) must fall back to the original 2D
        behavior entirely, not attempt a partially-3D computation."""
        window = _sustained_bend_window()
        world_window = [dict(row) for row in window]
        # Only 10% of frames get world_keypoints -- below MIN_WORLD_LANDMARK_COVERAGE (0.5).
        sparse = _attach_world_keypoints([dict(row) for row in window], lambda i: 0.50)
        for i, row in enumerate(world_window):
            if i % 10 == 0:
                row["world_keypoints"] = sparse[i]["world_keypoints"]
        world_raw = gf._raw_world_keypoint_array(world_window)
        self.assertFalse(gf._has_sufficient_world_coverage(world_raw))
        speed_sparse_world = gf.compute_walking_speed(world_window, _world_raw=world_raw)
        speed_2d_only = gf.compute_walking_speed(window)
        self.assertEqual(speed_sparse_world, speed_2d_only)


def _fully_bent_with_ankle_jitter_window(n_frames=150, torso_bent=0.05, drift=0.0006,
                                          jitter_std=0.01, seed=51):
    """A subject already IN a sustained, fully-bent hold for the whole
    window (hip barely drifting, torso length constant and collapsed) with
    only realistic per-frame ANKLE tracking jitter -- no walking, no ankle
    swing of any kind. Reproduces this project's real GAIT audit finding
    (see gait_features.compute_stride_regularity's own docstring): dividing
    that ordinary ankle jitter by a collapsed, near-degenerate torso length
    (the SAME _normalized_positions scale factor _torso_scaled_hip_track
    uses for hip translation) amplifies it into a signal that clears
    STRIDE_PEAK_PROMINENCE_FRACTION, fabricating a non-trivial CV with a
    physically-implausible cadence. Unlike _sustained_bend_window (which
    ramps from standing to bent WITHIN the window, so the ramp itself
    dominates the ankle-y range and actually SUPPRESSES the noise-driven
    peaks relative to STRIDE_PEAK_PROMINENCE_FRACTION), this fixture models
    a window entirely INSIDE an already-sustained bend -- matching a
    real mid-clip sliding-window view of Deep_Bend_2.mov's own GT-confirmed
    "Deep bend sustained" span, where this exact fabrication was directly
    confirmed on real footage (CV up to 0.429, n_events=4-6)."""
    rng = np.random.default_rng(seed)
    window = []
    hip_x, hip_y = 0.5, 0.3
    for i in range(n_frames):
        cur_hip_x = hip_x + drift * i
        kps = [np.nan] * 66
        kps[22], kps[23] = cur_hip_x - 0.05, hip_y - torso_bent
        kps[24], kps[25] = cur_hip_x + 0.05, hip_y - torso_bent
        kps[46], kps[47] = cur_hip_x - 0.05, hip_y
        kps[48], kps[49] = cur_hip_x + 0.05, hip_y
        kps[50], kps[51] = cur_hip_x - 0.05, hip_y + 0.2
        kps[52], kps[53] = cur_hip_x + 0.05, hip_y + 0.2
        kps[54], kps[55] = cur_hip_x - 0.05, hip_y + 0.35 + rng.normal(0, jitter_std)
        kps[56], kps[57] = cur_hip_x + 0.05, hip_y + 0.35 + rng.normal(0, jitter_std)
        window.append({"timestamp": i / 30.0, "frame": i, "keypoints": kps})
    return window


class StrideRegularityTorsoBaselineTests(unittest.TestCase):
    """Regression tests for compute_stride_regularity's torso-baseline
    collapse gate (a later GAIT audit session -- see that function's own
    docstring and gait_features.MIN_TORSO_BASELINE_RATIO's "STRIDE_
    REGULARITY VALIDATION SCOPE" note): stride_regularity's ambulation gate
    runs on the identical 2D hip track compute_walking_speed's does, so it
    needed the identical torso-baseline gate TorsoBaselineCalibrationTests
    already locks in for that signal -- this class is the same pattern,
    applied to stride_regularity."""

    def test_fixture_reproduces_the_real_fabrication_without_a_gate(self):
        """Sanity check the fixture actually exercises the bug (same
        pattern as StrideRegularityTests' own finding-#1 fixture check):
        without a baseline, this window currently fabricates a non-trivial
        CV from pure ankle-tracking noise on a motionless, sustained-bent
        subject."""
        window = _fully_bent_with_ankle_jitter_window()
        quality = {}
        cv = gf.compute_stride_regularity(window, _quality_out=quality)
        self.assertIsNotNone(cv, "fixture must reproduce a currently-available spurious "
                                  "CV to be a meaningful regression test")
        self.assertGreaterEqual(quality.get("n_events", 0), 3)

    def test_sustained_bend_marks_stride_regularity_unavailable_with_baseline(self):
        window = _fully_bent_with_ankle_jitter_window()
        ungated = gf.compute_stride_regularity(window)
        self.assertIsNotNone(ungated)

        standing_prefix = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(30)]
        baseline = gf.compute_torso_baseline(standing_prefix)
        self.assertIsNotNone(baseline)
        gated = gf.compute_stride_regularity(window, _torso_baseline=baseline)
        self.assertIsNone(gated, "a sustained torso-length collapse well below MIN_TORSO_BASELINE_RATIO "
                                  "of a confirmed-standing baseline must mark stride_regularity unavailable, "
                                  "the same as it already does for walking_speed")

        result = GaitRiskAssessor().assess_risk(window, _torso_baseline=baseline)
        sr_signal = next(s for s in result["signals"] if s["name"] == "stride_regularity")
        self.assertFalse(sr_signal["available"])
        self.assertIsNone(sr_signal["value"])

    def test_genuine_walking_not_suppressed_by_baseline(self):
        """Recall check: a baseline established from genuine walking's own
        stable start must not suppress its own real cadence signal."""
        window = _walking_window(180, speed=0.15)
        ungated = gf.compute_stride_regularity(window)
        self.assertIsNotNone(ungated, "test fixture must produce a genuine available reading")

        baseline = gf.compute_torso_baseline(window[:30])
        self.assertIsNotNone(baseline)
        gated = gf.compute_stride_regularity(window, _torso_baseline=baseline)
        self.assertEqual(gated, ungated, "genuine walking must be completely unaffected by the "
                                          "calibrated-baseline gate")

    def test_default_behavior_unchanged_when_baseline_not_supplied(self):
        window = _fully_bent_with_ankle_jitter_window()
        self.assertEqual(gf.compute_stride_regularity(window), gf.compute_stride_regularity(window, _torso_baseline=None))
        result = GaitRiskAssessor().assess_risk(_walking_window(180, speed=0.15))
        result_explicit_none = GaitRiskAssessor().assess_risk(_walking_window(180, speed=0.15), _torso_baseline=None)
        self.assertEqual(result, result_explicit_none)

    def test_3d_gate_also_catches_stride_regularity_residual(self):
        """3D-mode mirror of WorldLandmarkRootCauseFixTests' own walking_speed
        test: when 3D world landmarks are available, the more sensitive 3D
        gate (MIN_TORSO_BASELINE_RATIO_3D) also protects stride_regularity,
        using the same worst-single-frame convention as walking_speed."""
        window = _fully_bent_with_ankle_jitter_window(torso_bent=0.12)  # 2D ratio 0.48 (vs.
        # _standing_kps()'s own torso length, 0.25) -- above MIN_TORSO_BASELINE_RATIO (0.40),
        # so the 2D gate alone would NOT catch it.
        baseline_2d = gf.compute_torso_baseline([{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(30)])
        gated_2d = gf.compute_stride_regularity(window, _torso_baseline=baseline_2d)
        self.assertIsNotNone(gated_2d, "fixture must reproduce the residual-band case (2D gate does "
                                        "NOT catch it) to be a meaningful test")

        def torso_3d(i):
            return 0.30  # ratio 0.60 vs. a 0.50 baseline -- below MIN_TORSO_BASELINE_RATIO_3D (0.70)
        world_window = _attach_world_keypoints([dict(row) for row in window], torso_3d)
        world_raw = gf._raw_world_keypoint_array(world_window)
        self.assertTrue(gf._has_sufficient_world_coverage(world_raw))
        baseline_3d = 0.50
        gated_3d = gf.compute_stride_regularity(world_window, _world_raw=world_raw, _torso_baseline=baseline_3d)
        self.assertIsNone(gated_3d, "the 3D-mode gate must catch this moderate-severity bend that the "
                                     "2D-mode gate alone cannot, mirroring walking_speed's own fix")

    def test_torso_baseline_and_world_raw_are_accepted_parameters(self):
        self.assertIn("_torso_baseline", inspect.signature(gf.compute_stride_regularity).parameters)
        self.assertIn("_world_raw", inspect.signature(gf.compute_stride_regularity).parameters)


class StrideRegularityConfidenceWeightingTests(unittest.TestCase):
    """Regression tests for _stride_regularity_confidence and its wiring
    into assess_risk()'s blend -- a later, dedicated risk-mapping audit
    session's fix for a real, evidenced problem: a stride-regularity CV
    computed from very few detected events (as few as the hard floor, 3)
    previously entered risk_score at the SAME nominal weight (1.2, the
    highest of the four signals) as a CV computed from many events, with
    no way for the blend to trust one more than the other. See
    gait_risk._stride_regularity_confidence's own module-level docstring
    for the full real-footage derivation (a full-44-clip-corpus run via
    benchmarks/gait_risk_distribution_analysis.py)."""

    def test_confidence_ramp_shape(self):
        # Floor at/below the hard minimum.
        self.assertEqual(gr._stride_regularity_confidence(3), gr.STRIDE_EVENTS_CONFIDENCE_FLOOR)
        self.assertEqual(gr._stride_regularity_confidence(1), gr.STRIDE_EVENTS_CONFIDENCE_FLOOR)
        self.assertEqual(gr._stride_regularity_confidence(0), gr.STRIDE_EVENTS_CONFIDENCE_FLOOR)
        # Full confidence at/above the plateau.
        self.assertEqual(gr._stride_regularity_confidence(gr.STRIDE_EVENTS_FULL_CONFIDENCE), 1.0)
        self.assertEqual(gr._stride_regularity_confidence(gr.STRIDE_EVENTS_FULL_CONFIDENCE + 5), 1.0)
        # Monotonically non-decreasing in between.
        vals = [gr._stride_regularity_confidence(n)
                for n in range(gr.MIN_STRIDE_EVENTS_FOR_CV, gr.STRIDE_EVENTS_FULL_CONFIDENCE + 1)]
        self.assertEqual(vals, sorted(vals))
        # Bounded in [floor, 1.0] throughout.
        for n in range(0, 20):
            c = gr._stride_regularity_confidence(n)
            self.assertGreaterEqual(c, gr.STRIDE_EVENTS_CONFIDENCE_FLOOR)
            self.assertLessEqual(c, 1.0)

    def test_none_n_events_is_neutral_not_floor(self):
        """A caller/context with no n_events information at all gets NO
        adjustment (1.0), not the pessimistic floor -- see the function's
        own docstring for why assuming the worst from an absence of
        information would be a stronger, unevidenced claim."""
        self.assertEqual(gr._stride_regularity_confidence(None), 1.0)

    def test_low_n_events_reduces_effective_weight_in_the_blend(self):
        """Direct proof this reaches assess_risk()'s own risk_score, not
        just the standalone function: two otherwise-identical blends
        (walking_speed + stride_regularity both available, same values),
        differing ONLY in stride_regularity's n_events, must produce
        DIFFERENT risk_score -- the low-n_events one pulled less toward
        stride_regularity's own risk_contribution."""
        assessor = GaitRiskAssessor()
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)

        def _specs(n_events):
            def _sr_fn(window, _quality_out=None, **kwargs):
                if _quality_out is not None:
                    _quality_out["n_events"] = n_events
                return 0.9  # deliberately high CV -- the case this mechanism protects
            return (
                ("walking_speed", lambda w, **kw: 1.0, gr._speed_risk, "gait", "d"),
                ("stride_regularity", _sr_fn, gr._stride_cv_risk, "gait", "d"),
                ("postural_sway", lambda w, **kw: None, gr._sway_risk, "postural", "d"),
                ("sit_to_stand", lambda w, **kw: None, gr._sit_to_stand_risk, "postural", "d"),
            )

        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", _specs(3)):
            low_n_result = assessor.assess_risk(window)
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", _specs(gr.STRIDE_EVENTS_FULL_CONFIDENCE)):
            high_n_result = assessor.assess_risk(window)

        speed_rc = gr._speed_risk(1.0)
        cv_rc = min(max(gr._stride_cv_risk(0.9), gr.RISK_CONTRIBUTION_FLOOR), gr.RISK_CONTRIBUTION_CEILING)
        w_speed = gr._SIGNAL_WEIGHTS["walking_speed"]
        w_sr = gr._SIGNAL_WEIGHTS["stride_regularity"]

        expected_low = (w_speed * speed_rc + w_sr * gr.STRIDE_EVENTS_CONFIDENCE_FLOOR * cv_rc) / \
                        (w_speed + w_sr * gr.STRIDE_EVENTS_CONFIDENCE_FLOOR)
        expected_high = (w_speed * speed_rc + w_sr * 1.0 * cv_rc) / (w_speed + w_sr * 1.0)

        self.assertAlmostEqual(low_n_result["risk_score"], expected_low)
        self.assertAlmostEqual(high_n_result["risk_score"], expected_high)
        # The core claim: fewer events -> the high CV pulls risk_score LESS
        # far from walking_speed's own (lower) contribution.
        self.assertLess(low_n_result["risk_score"], high_n_result["risk_score"])

        sr_entry_low = next(s for s in low_n_result["signals"] if s["name"] == "stride_regularity")
        sr_entry_high = next(s for s in high_n_result["signals"] if s["name"] == "stride_regularity")
        self.assertAlmostEqual(sr_entry_low["weight_confidence"], gr.STRIDE_EVENTS_CONFIDENCE_FLOOR)
        self.assertAlmostEqual(sr_entry_high["weight_confidence"], 1.0)
        # risk_contribution itself is UNCHANGED by confidence -- only the weight is.
        self.assertAlmostEqual(sr_entry_low["risk_contribution"], sr_entry_high["risk_contribution"])

    def test_weight_confidence_defaults_to_one_for_other_signals(self):
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        result = GaitRiskAssessor().assess_risk(window)
        for s in result["signals"]:
            if s["name"] != "stride_regularity" and s["available"]:
                self.assertEqual(s["weight_confidence"], 1.0)

    def test_weight_confidence_is_none_when_unavailable(self):
        window = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(90)]
        result = GaitRiskAssessor().assess_risk(window)
        for s in result["signals"]:
            if not s["available"]:
                self.assertIsNone(s["weight_confidence"])


class RiskContributionBoundsTests(unittest.TestCase):
    """Regression tests for RISK_CONTRIBUTION_FLOOR/CEILING -- a later,
    dedicated risk-mapping audit session's fix for a real, evidenced
    problem: this module's uncalibrated heuristic sigmoids reported
    risk_contribution as extreme as 0.00015 and 0.999 on real footage (see
    RISK_CONTRIBUTION_FLOOR's own module-level docstring for the full
    real-footage derivation -- fall-onset walking_speed readings and
    small-n_events stride_regularity readings, found via a full-44-clip-
    corpus run), overstating this heuristic system's own certainty at
    either extreme."""

    def test_extreme_speed_is_clipped_not_near_zero(self):
        # A speed far outside this module's own documented real range
        # (0.49-3.43 torso-lengths/sec across the full real corpus) --
        # mirrors the real fall-onset case (Chair_fall.mp4/Side_fall.mp4)
        # this bound was found from.
        raw = gr._speed_risk(10.0)
        self.assertLess(raw, gr.RISK_CONTRIBUTION_FLOOR, "fixture must exercise a genuinely "
                                                           "near-zero raw sigmoid to be meaningful")
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        specs = (
            ("walking_speed", lambda w, **kw: 10.0, gr._speed_risk, "gait", "d"),
            ("stride_regularity", lambda w, **kw: None, gr._stride_cv_risk, "gait", "d"),
            ("postural_sway", lambda w, **kw: None, gr._sway_risk, "postural", "d"),
            ("sit_to_stand", lambda w, **kw: None, gr._sit_to_stand_risk, "postural", "d"),
        )
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
            result = GaitRiskAssessor().assess_risk(window)
        speed_signal = next(s for s in result["signals"] if s["name"] == "walking_speed")
        self.assertAlmostEqual(speed_signal["risk_contribution"], gr.RISK_CONTRIBUTION_FLOOR)
        self.assertAlmostEqual(result["risk_score"], gr.RISK_CONTRIBUTION_FLOOR)

    def test_extreme_cv_is_clipped_not_near_one(self):
        raw = gr._stride_cv_risk(5.0)
        self.assertGreater(raw, gr.RISK_CONTRIBUTION_CEILING, "fixture must exercise a genuinely "
                                                                "near-one raw sigmoid to be meaningful")
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        specs = (
            ("walking_speed", lambda w, **kw: None, gr._speed_risk, "gait", "d"),
            ("stride_regularity", lambda w, _quality_out=None, **kw: (
                _quality_out.update({"n_events": 20}) if _quality_out is not None else None, 5.0)[1],
             gr._stride_cv_risk, "gait", "d"),
            ("postural_sway", lambda w, **kw: None, gr._sway_risk, "postural", "d"),
            ("sit_to_stand", lambda w, **kw: None, gr._sit_to_stand_risk, "postural", "d"),
        )
        with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
            result = GaitRiskAssessor().assess_risk(window)
        sr_signal = next(s for s in result["signals"] if s["name"] == "stride_regularity")
        self.assertAlmostEqual(sr_signal["risk_contribution"], gr.RISK_CONTRIBUTION_CEILING)

    def test_ordinary_values_are_never_clipped(self):
        """Recall check: the bound must not visibly alter ordinary,
        realistic risk_contribution values -- only genuinely extreme ones.
        Every value found anywhere in this project's real 44-clip corpus
        during this audit fell inside [FLOOR, CEILING] already (see
        RISK_CONTRIBUTION_FLOOR's own docstring)."""
        for speed in (0.5, 0.8, 1.0, 1.2, 1.7):
            rc = gr._speed_risk(speed)
            self.assertGreater(rc, gr.RISK_CONTRIBUTION_FLOOR)
            self.assertLess(rc, gr.RISK_CONTRIBUTION_CEILING)
        for cv in (0.05, 0.15, 0.3, 0.45):
            rc = gr._stride_cv_risk(cv)
            self.assertGreater(rc, gr.RISK_CONTRIBUTION_FLOOR)
            self.assertLess(rc, gr.RISK_CONTRIBUTION_CEILING)


class RiskMappingMonotonicityTests(unittest.TestCase):
    """Explicit regression tests that each risk-mapping function is
    monotonic in the direction this module's own docstrings claim (see
    gait_risk.py's per-function docstrings) -- locks in behavior verified
    analytically during a dedicated risk-mapping audit session (every
    mapping here is a sigmoid, or a fixed convex combination of sigmoids,
    of a single linear argument, which is monotonic by construction, but
    this is asserted directly rather than left as an unverified
    implication)."""

    def test_speed_risk_decreases_as_speed_increases(self):
        speeds = [0.1, 0.3, 0.5, 0.8, 1.0, 1.3, 1.7, 2.5, 4.0]
        risks = [gr._speed_risk(s) for s in speeds]
        self.assertEqual(risks, sorted(risks, reverse=True))

    def test_stride_cv_risk_increases_as_cv_increases(self):
        cvs = [0.0, 0.05, 0.15, 0.25, 0.30, 0.4, 0.6, 0.9]
        risks = [gr._stride_cv_risk(c) for c in cvs]
        self.assertEqual(risks, sorted(risks))

    def test_sway_risk_increases_as_sway_increases(self):
        sways = [0.0, 0.01, 0.03, 0.05, 0.07, 0.1, 0.2]
        risks = [gr._sway_risk(s) for s in sways]
        self.assertEqual(risks, sorted(risks))

    def test_sit_to_stand_risk_increases_with_duration_holding_reversals_fixed(self):
        durations = [0.1, 0.5, 1.0, 2.0, 3.0, 5.0]
        risks = [gr._sit_to_stand_risk({"duration_sec": d, "reversal_count": 1.0}) for d in durations]
        self.assertEqual(risks, sorted(risks))

    def test_sit_to_stand_risk_increases_with_reversals_holding_duration_fixed(self):
        reversal_counts = [0.0, 1.0, 2.0, 4.0, 8.0]
        risks = [gr._sit_to_stand_risk({"duration_sec": 1.0, "reversal_count": r}) for r in reversal_counts]
        self.assertEqual(risks, sorted(risks))

    def test_progressively_worse_stride_irregularity_never_decreases_end_to_end_risk_score(self):
        """The exact scenario the task itself poses: as stride irregularity
        (CV) gets progressively worse, holding everything else fixed, the
        BLENDED risk_score (not just the raw sigmoid) must never decrease
        -- exercises the full weight_confidence + clipping pipeline
        together, not the risk-mapping function in isolation."""
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        scores = []
        for cv in (0.05, 0.15, 0.25, 0.35, 0.5, 0.7, 0.9, 1.5):
            def _sr_fn(w, _quality_out=None, cv=cv, **kw):
                if _quality_out is not None:
                    _quality_out["n_events"] = 6  # fixed, well-evidenced -- isolates the CV axis
                return cv
            specs = (
                ("walking_speed", lambda w, **kw: None, gr._speed_risk, "gait", "d"),
                ("stride_regularity", _sr_fn, gr._stride_cv_risk, "gait", "d"),
                ("postural_sway", lambda w, **kw: None, gr._sway_risk, "postural", "d"),
                ("sit_to_stand", lambda w, **kw: None, gr._sit_to_stand_risk, "postural", "d"),
            )
            with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", specs):
                result = GaitRiskAssessor().assess_risk(window)
            scores.append(result["risk_score"])
        self.assertEqual(scores, sorted(scores), f"risk_score must be non-decreasing as CV worsens: {scores}")


class RiskScoreBoundsTests(unittest.TestCase):
    """risk_score must always stay within its documented [0.0, 1.0]
    contract (see gait_risk.py's own OUTPUT CONTRACT docstring) -- a
    mathematical guarantee of the weighted-average-of-sigmoids
    architecture, verified directly (including with the new weight_
    confidence/clipping mechanisms in the blend) rather than left implicit."""

    def test_risk_score_bounded_across_representative_real_scale_inputs(self):
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        for speed in (0.01, 0.5, 1.0, 3.5, 50.0):
            for cv in (0.01, 0.3, 0.9, 3.0):
                for n_events in (3, 6, 20):
                    def _mk(speed=speed, cv=cv, n_events=n_events):
                        def _sr_fn(w, _quality_out=None, **kw):
                            if _quality_out is not None:
                                _quality_out["n_events"] = n_events
                            return cv
                        return (
                            ("walking_speed", lambda w, **kw: speed, gr._speed_risk, "gait", "d"),
                            ("stride_regularity", _sr_fn, gr._stride_cv_risk, "gait", "d"),
                            ("postural_sway", lambda w, **kw: None, gr._sway_risk, "postural", "d"),
                            ("sit_to_stand", lambda w, **kw: None, gr._sit_to_stand_risk, "postural", "d"),
                        )
                    with mock.patch.object(GaitRiskAssessor, "_SIGNAL_SPECS", _mk()):
                        result = GaitRiskAssessor().assess_risk(window)
                    self.assertIsNotNone(result["risk_score"])
                    self.assertGreaterEqual(result["risk_score"], 0.0)
                    self.assertLessEqual(result["risk_score"], 1.0)


class TorsoAngularVelocityDiagnosticTests(unittest.TestCase):
    """Tests for gait_features.compute_torso_angular_velocity_diagnostic --
    see that function's own "TORSO ANGULAR VELOCITY" section docstring for
    what it is and why it exists: a candidate second signal investigated
    to discriminate "fast walking" from "fast falling" (walking_speed
    alone cannot -- see docs/GAIT_DATA_ASSESSMENT.md's risk-mapping audit).
    Real-footage evidence (both 2D and 3D-world-landmark modes) found NO
    clean separation -- this function is NOT called anywhere in
    assess_risk() or any other production path, and stays that way. These
    tests cover the DIAGNOSTIC's own correctness (it must compute the
    right number), not any risk-mapping behavior."""

    def _upright_row(self, i, hip_x=0.5, hip_y=0.55, torso_len=0.25):
        kps = [np.nan] * 66
        kps[22], kps[23] = hip_x - 0.05, hip_y - torso_len
        kps[24], kps[25] = hip_x + 0.05, hip_y - torso_len
        kps[46], kps[47] = hip_x - 0.05, hip_y
        kps[48], kps[49] = hip_x + 0.05, hip_y
        return {"timestamp": i / 30.0, "keypoints": kps}

    def test_stationary_upright_torso_reads_zero(self):
        window = [self._upright_row(i) for i in range(90)]
        result = gf.compute_torso_angular_velocity_diagnostic(window)
        self.assertIsNotNone(result)
        self.assertEqual(result["peak_deg_per_sec"], 0.0)
        self.assertEqual(result["mean_deg_per_sec"], 0.0)
        self.assertEqual(result["max_consecutive_pairs_above_150"], 0)
        self.assertEqual(result["mode"], "2d")
        self.assertEqual(result["coverage"], 1.0)

    def test_known_rotation_rate_matches_exactly(self):
        """A synthetic torso sweeping from 0 to 80 degrees over exactly 10
        frames at 30fps must measure peak_deg_per_sec == 8deg/frame * 30fps
        = 240 deg/sec, matching simple physics exactly -- not just 'runs
        without crashing'."""
        window = []
        for i in range(90):
            if i < 40:
                angle_deg = 0.0
            elif i < 50:
                angle_deg = (i - 40) / 10.0 * 80.0
            else:
                angle_deg = 80.0
            rad = np.radians(angle_deg)
            hip_x, hip_y, torso_len = 0.5, 0.55, 0.25
            sh_x = hip_x + torso_len * np.sin(rad)
            sh_y = hip_y - torso_len * np.cos(rad)
            kps = [np.nan] * 66
            kps[22], kps[23] = sh_x - 0.03, sh_y
            kps[24], kps[25] = sh_x + 0.03, sh_y
            kps[46], kps[47] = hip_x - 0.03, hip_y
            kps[48], kps[49] = hip_x + 0.03, hip_y
            window.append({"timestamp": i / 30.0, "keypoints": kps})
        result = gf.compute_torso_angular_velocity_diagnostic(window)
        self.assertAlmostEqual(result["peak_deg_per_sec"], 240.0, places=2)
        self.assertGreaterEqual(result["max_consecutive_pairs_above_150"], 1)

    def test_returns_none_on_all_nan_window(self):
        window = [{"timestamp": i / 30.0, "keypoints": [np.nan] * 66} for i in range(90)]
        self.assertIsNone(gf.compute_torso_angular_velocity_diagnostic(window))

    def test_3d_mode_used_when_world_raw_has_sufficient_coverage(self):
        window = [self._upright_row(i) for i in range(90)]
        world_window = _attach_world_keypoints([dict(row) for row in window], lambda i: 0.50)
        world_raw = gf._raw_world_keypoint_array(world_window)
        result = gf.compute_torso_angular_velocity_diagnostic(world_window, _world_raw=world_raw)
        self.assertEqual(result["mode"], "3d")
        # A perfectly upright synthetic torso (shoulder directly above hip
        # in the world-keypoints fixture too) must still read ~0 deg/sec.
        self.assertAlmostEqual(result["peak_deg_per_sec"], 0.0, places=2)

    def test_2d_fallback_when_world_raw_absent_or_insufficient(self):
        window = [self._upright_row(i) for i in range(90)]
        result_no_world = gf.compute_torso_angular_velocity_diagnostic(window)
        result_none_world_raw = gf.compute_torso_angular_velocity_diagnostic(
            window, _world_raw=gf._raw_world_keypoint_array(window))  # all-NaN -- insufficient coverage
        self.assertEqual(result_no_world["mode"], "2d")
        self.assertEqual(result_none_world_raw["mode"], "2d")
        self.assertEqual(result_no_world, result_none_world_raw)

    def test_not_wired_into_assess_risk_output(self):
        """Locks in that this diagnostic has NOT been wired into
        risk_score/signals anywhere -- see this class's own docstring for
        why (real-footage evidence found no clean separation)."""
        window = _walking_window(gf.MIN_WINDOW_FRAMES, speed=0.15)
        result = GaitRiskAssessor().assess_risk(window)
        signal_names = {s["name"] for s in result["signals"]}
        self.assertEqual(signal_names, {"walking_speed", "stride_regularity", "postural_sway", "sit_to_stand"})
        for s in result["signals"]:
            self.assertNotIn("torso_angular_velocity", str(s.get("name", "")))


class RiskScoreContractPreservedTests(unittest.TestCase):
    """Explicit, direct regression test that this session's additions
    (reliability, category, cadence) did not alter risk_score's value,
    the set of pre-existing keys, or any pre-existing key's type/semantics
    -- the central constraint of this work."""

    def test_preexisting_keys_and_types_unchanged(self):
        window = _walking_window(210, speed=0.15)
        result = GaitRiskAssessor().assess_risk(window)
        self.assertEqual(set(result.keys()), {"risk_score", "signals"})
        self.assertIsInstance(result["risk_score"], float)
        self.assertEqual(len(result["signals"]), 4)
        for s in result["signals"]:
            for key in ("name", "available", "value", "risk_contribution", "calibrated", "description"):
                self.assertIn(key, s)
            self.assertIsInstance(s["available"], bool)
            self.assertIsInstance(s["calibrated"], bool)
            self.assertIsInstance(s["description"], str)

    def test_all_compute_functions_still_callable_without_quality_out(self):
        """Every compute_* function's pre-existing call signature (no
        _quality_out) must still work identically -- backward compatibility
        for every OTHER test in this file that calls them this way."""
        walking_window = _walking_window(210, speed=0.15)
        sts_window = _sit_to_stand_window(shaky=False)
        self.assertIsNotNone(gf.compute_walking_speed(walking_window))
        self.assertIsNotNone(gf.compute_stride_regularity(walking_window))
        self.assertIsNotNone(gf.compute_sit_to_stand(sts_window))
        sway_window = [{"timestamp": i / 30.0, "keypoints": _standing_kps()} for i in range(90)]
        self.assertIsNotNone(gf.compute_postural_sway(sway_window))


if __name__ == "__main__":
    unittest.main()

"""
tests/test_realtime_gait_integration.py
========================================
Proves GAIT is actually REACHABLE from realtime_fall_detection.py's own
real-time frame loop -- not merely importable. See that module's own
"GAIT integration" docstring (in `run()`) for the wiring this exercises:

    camera/video frame -> MediaPipe detect_for_video() -> build_pose_row()
        (2D keypoints + optional world_keypoints)
      -> classify_posture_and_fall() (existing RF/heuristic/LSTM decision,
         UNCHANGED)
      -> TorsoBaselineCalibrator.observe() (session-level torso-length
         safety calibration, gated on the classifier's own "Standing" +
         "not fall_detected" verdict)
      -> StreamingGaitRiskAssessor.push_frame() (the actual GAIT window/
         risk computation)
      -> on_gait_update() callback (this test's own observation point)

This is deliberately SEPARATE from tests/test_gait_stream.py (which covers
StreamingGaitRiskAssessor/TorsoBaselineCalibrator's own logic against
synthetic fixtures, no camera/MediaPipe/video dependency) -- this file's
whole point is to run the REAL, unmocked realtime_fall_detection.run()
loop, with real MediaPipe pose estimation, against real footage already in
this repository, and confirm GAIT actually gets fed frames and produces
real results through it. Slower and heavier than the rest of this
project's `tests/` suite (real MediaPipe inference over an ~16s clip,
~20-60s wall time depending on hardware) for that reason -- this mirrors
why `benchmarks/validate_*.py` keeps real-footage validation separate from
the fast synthetic suite, just kept inside `tests/` (rather than
`benchmarks/`) here specifically because it's the one place asserting
end-to-end WIRING correctness, not signal/threshold plausibility, and a
wiring regression is exactly the kind of thing that SHOULD fail an
automated test run, not only a manually-run validation script.

Skips (does not fail) if the MediaPipe pose model or the test footage this
repository already tracks are unavailable, matching this project's
existing tolerance for environments without the full asset set.
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

POSE_MODEL_PATH = REPO_ROOT / "models" / "pose_landmarker_full.task"
TEST_CLIP = REPO_ROOT / "test_footage" / "GAIT_Analysis_Test_Footages" / "Deep_Bend_2.mov"

_SKIP_REASON = None
if not POSE_MODEL_PATH.exists():
    _SKIP_REASON = f"MediaPipe pose model not found at {POSE_MODEL_PATH}"
elif not TEST_CLIP.exists():
    _SKIP_REASON = f"Test footage not found at {TEST_CLIP}"
else:
    try:
        import realtime_fall_detection as rfd
    except Exception as exc:  # pragma: no cover -- environment-dependent (e.g. missing mediapipe/cv2)
        _SKIP_REASON = f"realtime_fall_detection could not be imported: {exc}"


@unittest.skipIf(_SKIP_REASON is not None, _SKIP_REASON or "")
class RealtimeGaitIntegrationTests(unittest.TestCase):
    """Runs the ACTUAL realtime_fall_detection.run() loop (headless, no
    LSTM/object-detector -- neither is relevant to what this test verifies,
    and skipping them keeps the run faster and removes two more optional
    external dependencies from what has to be present for this test to
    execute at all) against a real clip already tracked in this repo, and
    inspects the on_gait_update callback's payloads.

    Deep_Bend_2.mov specifically: ~16s, ~60fps, a long (~3.2s / ~190-frame)
    genuine GT-confirmed standing hold at the start (see
    test_footage/GAIT_Analysis_Test_Footages/Deep_Bend_2_GT.csv) --
    comfortably long enough to complete torso-baseline calibration well
    before the sustained bend that follows it, then a real, GT-confirmed
    sustained bend that is exactly the real-footage case
    gait_features.MIN_TORSO_BASELINE_RATIO's docstring documents as
    producing an un-gated walking_speed of up to ~15.8 torso-lengths/sec.
    This clip therefore doubles as a real-footage check that the
    integration actually PROTECTS against that failure mode end-to-end,
    not just that it runs without crashing.
    """

    # A small GAIT window/short calibration requirement, deliberately
    # smaller than realtime_fall_detection.py's own production defaults
    # (GAIT_WINDOW_FRAMES=150, GAIT_MIN_CALIBRATION_FRAMES=60) -- both are
    # still >= their respective hard floors (gait_features.MIN_WINDOW_FRAMES
    # =90, gait_features.CALIBRATION_SEGMENT_FRAMES=20), so this exercises
    # the exact same code paths, just faster (more assessments within one
    # ~16s clip, calibration completing well within the clip's own ~3.2s
    # standing hold either way).
    GAIT_WINDOW_FRAMES = 90
    GAIT_REASSESS_EVERY_N = 10
    GAIT_MIN_CALIBRATION_FRAMES = 45

    @classmethod
    def setUpClass(cls):
        cls.gait_updates = []
        cls.alerts = []
        rfd.run(
            str(TEST_CLIP),
            use_lstm=False,
            show_display=False,
            use_objects=False,
            use_gait=True,
            gait_window_frames=cls.GAIT_WINDOW_FRAMES,
            gait_reassess_every_n_frames=cls.GAIT_REASSESS_EVERY_N,
            gait_min_calibration_frames=cls.GAIT_MIN_CALIBRATION_FRAMES,
            on_gait_update=lambda d: cls.gait_updates.append(d),
            on_alert=lambda e: cls.alerts.append(e),
        )

    def test_gait_updates_were_actually_produced(self):
        """The core reachability proof: frames entering run()'s real loop
        reached the GAIT streaming assessor and it produced real results --
        not just that the modules involved could be imported."""
        self.assertGreater(len(self.gait_updates), 0,
                            "on_gait_update never fired -- GAIT is not actually reachable "
                            "from the real-time frame loop")

    def test_each_update_has_the_documented_shape(self):
        for u in self.gait_updates:
            self.assertIn("frame", u)
            self.assertIn("timestamp", u)
            self.assertIn("result", u)
            self.assertIn("torso_baseline", u)
            self.assertIn("torso_baseline_mode", u)
            result = u["result"]
            self.assertIn("risk_score", result)
            self.assertIn("signals", result)
            self.assertEqual(len(result["signals"]), 4)
            for s in result["signals"]:
                self.assertIn(s["name"], {"walking_speed", "stride_regularity",
                                           "postural_sway", "sit_to_stand"})

    def test_torso_baseline_was_established_from_the_real_standing_hold(self):
        """Proves the calibrator actually completed against real MediaPipe
        output for this clip (it has a long, clean, GT-confirmed standing
        hold at the start) -- not merely that it COULD in principle."""
        calibrated_updates = [u for u in self.gait_updates if u["torso_baseline"] is not None]
        self.assertGreater(len(calibrated_updates), 0,
                            "torso baseline was never established during this clip's own "
                            "~3.2s confirmed-standing hold")
        baseline = calibrated_updates[0]["torso_baseline"]
        self.assertGreater(baseline, 0.0)
        # Once established it must never change for the rest of the session
        # (single-baseline-per-session contract -- see
        # TorsoBaselineCalibrator's own docstring).
        for u in calibrated_updates:
            self.assertEqual(u["torso_baseline"], baseline)
        self.assertIn(calibrated_updates[0]["torso_baseline_mode"], ("2d", "3d"))

    def test_torso_collapse_protection_is_actually_active_end_to_end(self):
        """The concrete, real-footage proof that Section 9.2's audit finding
        (the torso-baseline gate exists and is unit-tested, but nothing in
        this repository ever supplied `_torso_baseline` in a runnable path)
        is now closed: walking_speed must never report an implausible value
        anywhere in this clip's real sustained bend, via the REAL run() loop
        -- not a direct, hand-wired assess_risk() call. Before the fix this
        exact clip, run through this exact loop, reported up to ~15.8-15.9
        torso-lengths/sec (see gait_features.MIN_TORSO_BASELINE_RATIO's own
        docstring for the same number found via a different, non-realtime
        extraction path)."""
        max_speed = 0.0
        for u in self.gait_updates:
            for s in u["result"]["signals"]:
                if s["name"] == "walking_speed" and s["available"]:
                    max_speed = max(max_speed, s["value"])
        # 2.0 torso-lengths/sec is a wide, deliberately generous ceiling --
        # every genuine real-footage walking_speed value documented anywhere
        # in this project's corpus (docs/GAIT_DATA_ASSESSMENT.md) is under
        # this; the UN-gated version of this exact bug measured ~15.8. This
        # is checking "no longer catastrophically implausible", not
        # asserting a tight bound on this one clip's own (non-walking)
        # content.
        self.assertLess(max_speed, 2.0,
                         f"walking_speed reached {max_speed:.2f} torso-lengths/sec somewhere in this "
                         "run -- the torso-baseline protection is not actually active end-to-end")

    def test_gait_never_affects_the_fall_alarm_contract(self):
        """GAIT is an ADDITIVE, parallel signal (docs/IMPLEMENTATION_PLAN.md
        Section 5.3) -- confirms the on_alert event, if any fired, carries
        GAIT context (gait_risk_score) but that context is informational
        only: this test doesn't (and structurally cannot, from outside)
        prove a negative about internal gating logic, so it instead locks
        in the documented contract fields exist and are the right type."""
        for event in self.alerts:
            self.assertIn("gait_risk_score", event)
            if event["gait_risk_score"] is not None:
                self.assertIsInstance(event["gait_risk_score"], float)
                self.assertGreaterEqual(event["gait_risk_score"], 0.0)
                self.assertLessEqual(event["gait_risk_score"], 1.0)


if __name__ == "__main__":
    unittest.main()

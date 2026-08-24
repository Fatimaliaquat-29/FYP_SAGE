"""
tests/test_gait_calibration_harness.py
=======================================
Tests for benchmarks/gait_calibration_harness.py -- the reusable Part-2
harness that turns a folder of purpose-tagged calibration clips into a
distribution/verdict report (see that module's own docstring).

These tests exercise the harness's OWN aggregation/discovery/rendering
logic with small, hand-constructed signal dicts -- they do not run
MediaPipe or claim anything about real calibration. That is deliberate:
this module must never be validated by feeding it synthetic footage (see
the module docstring's "no synthetic data" note) -- only its plumbing
(folder discovery, percentile math, verdict wording) is unit-testable
without real video.
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BENCH_DIR = REPO_ROOT / "benchmarks"
if str(BENCH_DIR) not in sys.path:
    sys.path.insert(0, str(BENCH_DIR))

import gait_calibration_harness as harness  # noqa: E402


class DiscoverIntakeTests(unittest.TestCase):
    def test_finds_only_subfolders_containing_video_files(self, ):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "quiet_stand").mkdir()
            (root / "quiet_stand" / "clip1.mp4").write_bytes(b"x")
            (root / "quiet_stand" / "notes.txt").write_bytes(b"x")
            (root / "empty_tag").mkdir()
            (root / "sway_wobble").mkdir()
            (root / "sway_wobble" / "clip2.mov").write_bytes(b"x")

            tags = harness.discover_intake(root)

            self.assertEqual(set(tags), {"quiet_stand", "sway_wobble"})
            self.assertEqual(len(tags["quiet_stand"]), 1)
            self.assertEqual(tags["quiet_stand"][0].name, "clip1.mp4")

    def test_empty_root_yields_no_tags(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(harness.discover_intake(Path(tmp)), {})


class StatsTests(unittest.TestCase):
    def test_empty_list_returns_none(self):
        self.assertIsNone(harness._stats([]))

    def test_known_distribution(self):
        s = harness._stats([1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertEqual(s["n"], 5)
        self.assertEqual(s["min"], 1.0)
        self.assertEqual(s["max"], 5.0)
        self.assertEqual(s["median"], 3.0)
        self.assertEqual(s["mean"], 3.0)


class VerdictTests(unittest.TestCase):
    def test_low_expectation_agrees_below_half(self):
        v = harness._verdict("low", {"median": 0.2})
        self.assertIn("AGREES", v)

    def test_low_expectation_disagrees_at_or_above_half(self):
        v = harness._verdict("low", {"median": 0.7})
        self.assertIn("DISAGREES", v)

    def test_high_expectation_agrees_at_or_above_half(self):
        v = harness._verdict("high", {"median": 0.5})
        self.assertIn("AGREES", v)

    def test_high_expectation_disagrees_below_half(self):
        v = harness._verdict("high", {"median": 0.49})
        self.assertIn("DISAGREES", v)

    def test_mid_expectation_never_pass_fails(self):
        v = harness._verdict("mid", {"median": 0.99})
        self.assertNotIn("AGREES", v)
        self.assertNotIn("DISAGREES", v)

    def test_no_data_is_explicit_not_a_silent_pass(self):
        v = harness._verdict("low", None)
        self.assertIn("no evidence", v)


class RenderReportTests(unittest.TestCase):
    def test_no_tags_produces_explanatory_message_not_a_crash(self):
        report = harness.render_report({})
        self.assertIn("No purpose-tag subfolders", report)

    def test_report_includes_verdict_line_for_known_tag_and_signal(self):
        tag_results = {
            "fast_walk": {
                "tag": "fast_walk", "n_clips": 1,
                "clips": [{"clip": "a.mp4", "n_frames": 100, "n_windows": 3,
                           "calibrated_at_frame": 30, "torso_baseline": 0.5}],
                "signal_values": {"walking_speed": harness._stats([1.5, 1.6, 1.7])},
                "signal_risk_contribution": {"walking_speed": harness._stats([0.1, 0.15, 0.12])},
            }
        }
        report = harness.render_report(tag_results)
        self.assertIn("fast_walk", report)
        self.assertIn("walking_speed", report)
        self.assertIn("AGREES", report)  # low risk_contribution matches fast_walk's "low" expectation

    def test_report_omits_verdict_for_unmapped_tag(self):
        tag_results = {
            "kneel": {
                "tag": "kneel", "n_clips": 1,
                "clips": [{"clip": "a.mp4", "n_frames": 50, "n_windows": 1,
                           "calibrated_at_frame": None, "torso_baseline": None}],
                "signal_values": {"postural_sway": harness._stats([0.03])},
                "signal_risk_contribution": {"postural_sway": harness._stats([0.4])},
            }
        }
        report = harness.render_report(tag_results)
        self.assertIn("kneel", report)
        self.assertNotIn("verdict vs. current threshold", report)

    def test_clip_level_error_is_surfaced_not_swallowed(self):
        tag_results = {
            "sts_fast": {
                "tag": "sts_fast", "n_clips": 1,
                "clips": [{"clip": "broken.mp4", "error": "RuntimeError: boom"}],
                "signal_values": {}, "signal_risk_contribution": {},
            }
        }
        report = harness.render_report(tag_results)
        self.assertIn("ERROR", report)
        self.assertIn("boom", report)


if __name__ == "__main__":
    unittest.main()

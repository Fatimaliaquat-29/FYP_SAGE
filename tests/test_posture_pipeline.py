import sys
import tempfile
import unittest
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import (
    build_pose_row,
    classify_posture_and_fall,
    write_pose_outputs,
    _compute_torso_angle,
    _compute_velocity,
    _extract_keypoint_pairs,
    reset_session_state,
)


class PosturePipelineTests(unittest.TestCase):
    def setUp(self):
        """Reset inter-frame pipeline state before every test."""
        reset_session_state()

    def test_classify_frame_handles_missing_keypoints(self):
        row = build_pose_row(timestamp="t", frame=1, landmarks=[])
        prediction = classify_posture_and_fall(row, previous_rows=[])
        self.assertEqual(prediction["posture_label"], "Unknown")
        self.assertFalse(prediction["fall_detected"])

    def test_write_pose_outputs_writes_consolidated_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)
            pose_path = temp_dir / "pose_keypoints.csv"
            posture_path = temp_dir / "posture_output.csv"
            rows = [
                build_pose_row(
                    timestamp="t1",
                    frame=1,
                    landmarks=[(0.50, 0.20)] * 33,
                ),
                build_pose_row(
                    timestamp="t2",
                    frame=2,
                    landmarks=[(0.49, 0.21)] * 33,
                ),
            ]
            for row in rows:
                row["body_height"] = 0.60
                row["torso_angle"] = 0.0
                row["hip_height"] = 0.50
                row["fall_detected"] = False
                row["confidence"] = 0.55
                row["other_labels"] = ""
                
            write_pose_outputs(rows, pose_path=pose_path, posture_path=posture_path)
            self.assertTrue(pose_path.exists())
            self.assertTrue(posture_path.exists())

            pose_df = pd.read_csv(pose_path)
            self.assertIn("timestamp", pose_df.columns)
            self.assertIn("frame", pose_df.columns)
            self.assertIn("x1", pose_df.columns)
            self.assertIn("y1", pose_df.columns)
            self.assertEqual(len(pose_df), 2)

    def test_posture_feature_script_runs_from_repo_root(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir)
            sample_input = temp_dir / "pose_keypoints.csv"
            sample_output = temp_dir / "posture_features.csv"
            
            # Build synthetic row in the new format
            row = {
                "timestamp": "t1",
                "frame": 1,
                "posture_label": "Unknown",
                "other_labels": ""
            }
            for i in range(1, 34):
                # Set shoulders, hips, ankles
                if i == 12:  # x12, y12 (lm 11 left shoulder)
                    row["x12"], row["y12"] = 0.48, 0.22
                elif i == 13:  # x13, y13 (lm 12 right shoulder)
                    row["x13"], row["y13"] = 0.52, 0.22
                elif i == 24:  # x24, y24 (lm 23 left hip)
                    row["x24"], row["y24"] = 0.49, 0.52
                elif i == 25:  # x25, y25 (lm 24 right hip)
                    row["x25"], row["y25"] = 0.51, 0.52
                elif i == 28:  # x28, y28 (lm 27 left ankle)
                    row["x28"], row["y28"] = 0.49, 0.80
                elif i == 29:  # x29, y29 (lm 28 right ankle)
                    row["x29"], row["y29"] = 0.51, 0.80
                else:
                    row[f"x{i}"] = np.nan
                    row[f"y{i}"] = np.nan

            pd.DataFrame([row]).to_csv(sample_input, index=False)

            result = subprocess.run(
                [
                    sys.executable, 
                    str(repo_root / "src" / "posture" / "posture_features.py"),
                    "--input", str(sample_input),
                    "--output", str(sample_output)
                ],
                cwd=repo_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(sample_output.exists())

    def test_torso_angle_calculation_standing(self):
        # Shoulder is above hip: dy < 0
        shoulder = (0.50, 0.20)
        hip = (0.50, 0.50)
        angle = _compute_torso_angle(shoulder, hip)
        self.assertAlmostEqual(angle, 0.0, places=2)

    def test_torso_angle_calculation_lying(self):
        # Shoulder and hip are horizontal: dy = 0
        shoulder = (0.20, 0.50)
        hip = (0.50, 0.50)
        angle = _compute_torso_angle(shoulder, hip)
        self.assertAlmostEqual(angle, 90.0, places=2)

    def test_velocity_calculation(self):
        # Hips at index 23 and 24
        kps1 = [np.nan] * 66
        kps1[46], kps1[47] = 0.50, 0.50
        kps1[48], kps1[49] = 0.50, 0.50

        kps2 = [np.nan] * 66
        kps2[46], kps2[47] = 0.50, 0.60
        kps2[48], kps2[49] = 0.50, 0.60

        row1 = {"keypoints": kps1}
        row2 = {"keypoints": kps2}
        velocity = _compute_velocity(row1, row2)
        self.assertAlmostEqual(velocity, 3.0, places=4)

    def test_fall_detection_trigger(self):
        reset_session_state()  # ensure angvel sustain counter starts at 0

        # ── Keypoint templates ───────────────────────────────────────────────
        kps_stand = [np.nan] * 66
        kps_stand[22], kps_stand[23] = 0.48, 0.20
        kps_stand[24], kps_stand[25] = 0.52, 0.20
        kps_stand[46], kps_stand[47] = 0.49, 0.50
        kps_stand[48], kps_stand[49] = 0.51, 0.50
        kps_stand[54], kps_stand[55] = 0.49, 0.80
        kps_stand[56], kps_stand[57] = 0.51, 0.80

        kps_lie = [np.nan] * 66
        kps_lie[22], kps_lie[23] = 0.18, 0.75
        kps_lie[24], kps_lie[25] = 0.22, 0.75
        kps_lie[46], kps_lie[47] = 0.49, 0.75
        kps_lie[48], kps_lie[49] = 0.51, 0.75
        kps_lie[54], kps_lie[55] = 0.79, 0.75
        kps_lie[56], kps_lie[57] = 0.81, 0.75

        prev_rows = []

        # ── Phase 1: 5 static standing frames to populate lookback buffer ────
        for i in range(5):
            row = build_pose_row(timestamp=str(i * 0.033), frame=i, keypoints=kps_stand)
            res = classify_posture_and_fall(row, previous_rows=prev_rows)
            row.update(res)
            prev_rows.append(row)

        # ── Phase 2: pre-seed the angvel counter with 3 mid-fall frames ────
        # Standing→mid-fall oscillation keeps smoothed_angvel > 200 deg/sec for
        # 3 frames, seeding _frames_angvel_above_floor so only 2 more high-angvel
        # frames are needed during the actual drop to arm angvel_sustained.
        kps_mid = [np.nan] * 66
        for j in range(len(kps_stand)):
            if not np.isnan(kps_stand[j]) and not np.isnan(kps_lie[j]):
                kps_mid[j] = kps_stand[j] + (kps_lie[j] - kps_stand[j]) * 0.5
        for i in range(3):
            row = build_pose_row(timestamp=str((5 + i) * 0.033), frame=5+i, keypoints=kps_mid)
            res = classify_posture_and_fall(row, previous_rows=prev_rows)
            row.update(res)
            prev_rows.append(row)

        # ── Phase 3: rapid fall — one large-displacement "impact" frame followed
        #    by 7 ramp frames.
        #
        # The impact frame (t=1.5) moves all keypoints 1.5× the stand→lie
        # displacement in a single 0.033 s step:
        #   hip Δy ≈ 0.375 normalised  →  velocity ≈ 0.375 / 0.60 / 0.033 ≈ 18.9 bh/sec
        # This clears FALL_PEAK_VELOCITY_FLOOR (15.0) with margin, matching the
        # spike a real fall produces.  The subsequent ramp frames (t = 1/6 … 7/6)
        # keep angvel_sustained=True and avg_recent_velocity > 1.5 as before.
        for phase_i, t in enumerate([1.5] + [i / 6.0 for i in range(1, 8)]):
            kps_fall = [np.nan] * 66
            for j in range(len(kps_stand)):
                if not np.isnan(kps_stand[j]) and not np.isnan(kps_lie[j]):
                    kps_fall[j] = kps_stand[j] + (kps_lie[j] - kps_stand[j]) * t

            frame_idx = 8 + phase_i
            row = build_pose_row(timestamp=str(frame_idx * 0.033), frame=frame_idx, keypoints=kps_fall)
            res2 = classify_posture_and_fall(row, previous_rows=prev_rows)
            row.update(res2)
            prev_rows.append(row)


        # ── Assertion: fall must have been detected somewhere in the fall sequence ──
        self.assertTrue(
            any(r.get("fall_detected", False) for r in prev_rows[5:]),
            msg=f"Fall never triggered. Labels: {[r.get('posture_label') for r in prev_rows[5:]]}, "
                f"Velocities: {[round(r.get('velocity', 0), 2) for r in prev_rows[5:]]}"
        )

    def test_fall_detection_no_trigger_on_slow_transition(self):
        prev_rows = []
        for i in range(10):
            t = i / 9.0
            sh_y = 0.20 + 0.55 * t
            hp_y = 0.50 + 0.25 * t
            ak_y = 0.80 - 0.05 * t
            sh_x = 0.50 - 0.30 * t
            hp_x = 0.50
            ak_x = 0.50 + 0.30 * t

            kps = [np.nan] * 66
            kps[22], kps[23] = sh_x - 0.02, sh_y
            kps[24], kps[25] = sh_x + 0.02, sh_y
            kps[46], kps[47] = hp_x - 0.01, hp_y
            kps[48], kps[49] = hp_x + 0.01, hp_y
            kps[54], kps[55] = ak_x - 0.01, ak_y
            kps[56], kps[57] = ak_x + 0.01, ak_y

            row = build_pose_row(timestamp=f"t{i}", frame=i+1, keypoints=kps)
            res = classify_posture_and_fall(row, previous_rows=prev_rows)
            row.update(res)
            prev_rows.append(row)

            if i == 9:
                self.assertEqual(res["posture_label"], "Lying")
                self.assertFalse(res["fall_detected"])

    def test_nan_handling(self):
        row = build_pose_row(timestamp="t", frame=1, keypoints=[np.nan] * 66)
        res = classify_posture_and_fall(row, previous_rows=[])
        self.assertEqual(res["posture_label"], "Unknown")
        self.assertFalse(res["fall_detected"])

    def _build_valid_kps(self, sh_y=0.20, hp_y=0.50, ak_y=0.80, kn_y=0.65):
        kps = [np.nan] * 66
        # shoulders (11/12)
        kps[22], kps[23] = 0.48, sh_y
        kps[24], kps[25] = 0.52, sh_y
        # hips (23/24)
        kps[46], kps[47] = 0.49, hp_y
        kps[48], kps[49] = 0.51, hp_y
        # knees (25/26)
        kps[50], kps[51] = 0.49, kn_y
        kps[52], kps[53] = 0.51, kn_y
        # ankles (27/28)
        kps[54], kps[55] = 0.49, ak_y
        kps[56], kps[57] = 0.51, ak_y
        return kps

    def test_sitting_hips_occluded(self):
        kps = self._build_valid_kps()
        kps[46] = kps[47] = kps[48] = kps[49] = np.nan
        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row)
        self.assertEqual(res["posture_label"], "Unknown")

    def test_sitting_only_upper_body(self):
        kps = self._build_valid_kps()
        kps[50] = kps[51] = kps[52] = kps[53] = np.nan  # knees missing
        kps[54] = kps[55] = kps[56] = kps[57] = np.nan  # ankles missing
        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row)
        self.assertEqual(res["posture_label"], "Standing")

    def test_missing_hip_landmarks(self):
        kps = self._build_valid_kps()
        kps[46] = kps[47] = kps[48] = kps[49] = np.nan
        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row)
        self.assertEqual(res["posture_label"], "Unknown")

    def test_missing_knee_landmarks(self):
        # Knees are NaN but ankles are present
        kps = self._build_valid_kps(sh_y=0.35, hp_y=0.50, ak_y=0.70)
        kps[50] = kps[51] = kps[52] = kps[53] = np.nan
        prev_rows = []

        # Buffer 5 frames of standing
        stand_kps = self._build_valid_kps(sh_y=0.20, hp_y=0.50, ak_y=0.80)
        for i in range(5):
            stand_row = build_pose_row(timestamp=str(i * 0.033), frame=i, keypoints=stand_kps)
            res_stand = classify_posture_and_fall(stand_row, previous_rows=prev_rows)
            stand_row.update(res_stand)
            prev_rows.append(stand_row)

        # Buffer 5 frames of sitting to satisfy the 5-frame smoothing filter
        for i in range(5):
            row = build_pose_row(timestamp=str((5 + i) * 0.033), frame=5+i, keypoints=kps)
            res = classify_posture_and_fall(row, previous_rows=prev_rows)
            row.update(res)
            prev_rows.append(row)

        self.assertEqual(res["posture_label"], "Sitting")

    def test_standing_partially_missing_lower_body(self):
        # Knees missing but ankles present
        kps = self._build_valid_kps(sh_y=0.20, hp_y=0.50, ak_y=0.80)
        kps[50] = kps[51] = kps[52] = kps[53] = np.nan
        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row)
        self.assertEqual(res["posture_label"], "Standing")

    def test_sitting_near_image_boundary(self):
        kps = self._build_valid_kps()
        # Simulate MediaPipe returning an out-of-frame y value (> 1.0) for extrapolated hips.
        # Values like 0.995 are perfectly valid for seated/lying people near the bottom edge.
        kps[47] = 1.05  # hip y genuinely outside frame
        kps[49] = 1.05
        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row)
        self.assertEqual(res["posture_label"], "Sitting")

    def test_missing_landmarks_return_unknown(self):
        kps = self._build_valid_kps()
        kps[22] = kps[23] = kps[24] = kps[25] = np.nan  # shoulders missing
        row = build_pose_row(keypoints=kps)
        res = classify_posture_and_fall(row)
        self.assertEqual(res["posture_label"], "Unknown")


if __name__ == "__main__":
    unittest.main()

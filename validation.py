import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.pipeline_utils import (
    DATA_DIR,
    POSE_KEYPOINTS_CSV,
    POSTURE_OUTPUT_CSV,
    build_pose_row,
    classify_posture_and_fall,
    write_pose_outputs,
)

INPUT_CSV = POSE_KEYPOINTS_CSV
FEATURES_CSV = DATA_DIR / "posture_features.csv"
OUTPUT_CSV = POSTURE_OUTPUT_CSV
VALIDATION_LOG = REPO_ROOT / "validation_log.csv"
SUMMARY_REPORT = REPO_ROOT / "summary_report.md"

FRAME_INTERVAL = 1.0 / 15.0  # simulate ~15 FPS capture


def _scale_coords(x, y, scale, cx=0.5, cy=0.5):
    return cx + (x - cx) * scale, cy + (y - cy) * scale


def build_synthetic_dataset(scenario_name, frame_count=12):
    """Create a lightweight synthetic pose dataset for each validation scenario."""
    rows = []
    base_time = time.time()

    for idx in range(frame_count):
        row = {
            "timestamp": base_time + idx * FRAME_INTERVAL,
            "frame": idx + 1,
        }
        for j in range(1, 34):
            row[f"x{j}"] = np.nan
            row[f"y{j}"] = np.nan
        row["posture_label"] = "Unknown"
        row["other_labels"] = ""

        if scenario_name == "Empty room":
            rows.append(row)
            continue

        # Base coordinate sets for each posture
        # In normalized image coords: y=0 is top, y=1 is bottom.
        # Standing: shoulder(top) -> hip(mid) -> knee(below hip) -> ankle(bottom)
        #   hip_angle ~ 180° (straight), knee_angle ~ 180° (straight)
        # Sitting: shoulder(top) -> hip(mid) -> knee(same y as hip, displaced forward) -> ankle(below knee)
        #   hip_angle ~ 90° (bent), knee_angle ~ 90° (bent)
        standing_coords = {
            "sh": (0.50, 0.22), "hp": (0.50, 0.52),
            "kn": (0.50, 0.66), "ak": (0.50, 0.85),
        }
        sitting_coords = {
            "sh": (0.50, 0.35), "hp": (0.50, 0.55),
            "kn": (0.65, 0.55), "ak": (0.65, 0.75),
        }

        # Determine scale factor for distance variants
        scale = 1.0
        if scenario_name.endswith("_near"):
            scale = 1.3
        elif scenario_name.endswith("_far"):
            scale = 0.5

        base_name = scenario_name.replace("_near", "").replace("_far", "")

        if base_name == "Standing":
            sh_x, sh_y = standing_coords["sh"]
            hp_x, hp_y = standing_coords["hp"]
            kn_x, kn_y = standing_coords["kn"]
            ak_x, ak_y = standing_coords["ak"]
        elif base_name == "Sitting":
            sh_x, sh_y = sitting_coords["sh"]
            hp_x, hp_y = sitting_coords["hp"]
            kn_x, kn_y = sitting_coords["kn"]
            ak_x, ak_y = sitting_coords["ak"]
        elif scenario_name == "Walking":
            sh_x, sh_y = standing_coords["sh"]
            hp_x, hp_y = standing_coords["hp"]
            kn_x, kn_y = standing_coords["kn"]
            ak_x, ak_y = standing_coords["ak"]
        elif scenario_name == "Slow lying":
            t = min(1.0, idx / 9.0)
            sh_x = 0.50 - 0.30 * t
            sh_y = 0.22 + 0.53 * t
            hp_x = 0.50
            hp_y = 0.52 + 0.23 * t
            kn_x = 0.50 + 0.15 * t
            kn_y = 0.66 + 0.09 * t
            ak_x = 0.50 + 0.30 * t
            ak_y = 0.85 - 0.10 * t
        elif scenario_name == "Fake fall":
            if idx in [2, 3]:
                sh_x, sh_y = sitting_coords["sh"]
                hp_x, hp_y = sitting_coords["hp"]
                kn_x, kn_y = sitting_coords["kn"]
                ak_x, ak_y = sitting_coords["ak"]
            else:
                sh_x, sh_y = standing_coords["sh"]
                hp_x, hp_y = standing_coords["hp"]
                kn_x, kn_y = standing_coords["kn"]
                ak_x, ak_y = standing_coords["ak"]
        elif scenario_name == "Standing_drift":
            if idx < 6:
                scale = 1.3
            else:
                scale = 0.5
            sh_x, sh_y = standing_coords["sh"]
            hp_x, hp_y = standing_coords["hp"]
            kn_x, kn_y = standing_coords["kn"]
            ak_x, ak_y = standing_coords["ak"]
        elif base_name == "Fall":
            if idx == 0:
                sh_x, sh_y = standing_coords["sh"]
                hp_x, hp_y = standing_coords["hp"]
                kn_x, kn_y = standing_coords["kn"]
                ak_x, ak_y = standing_coords["ak"]
            elif idx == 1:
                sh_x, sh_y = 0.35, 0.45
                hp_x, hp_y = 0.50, 0.62
                kn_x, kn_y = 0.58, 0.70
                ak_x, ak_y = 0.65, 0.78
            else:
                sh_x, sh_y = 0.20, 0.75
                hp_x, hp_y = 0.50, 0.75
                kn_x, kn_y = 0.65, 0.75
                ak_x, ak_y = 0.80, 0.75
        else:
            sh_x, sh_y = standing_coords["sh"]
            hp_x, hp_y = standing_coords["hp"]
            kn_x, kn_y = standing_coords["kn"]
            ak_x, ak_y = standing_coords["ak"]

        # Apply distance scale
        sh_x, sh_y = _scale_coords(sh_x, sh_y, scale)
        kn_x, kn_y = _scale_coords(kn_x, kn_y, scale)
        hp_x, hp_y = _scale_coords(hp_x, hp_y, scale)
        ak_x, ak_y = _scale_coords(ak_x, ak_y, scale)

        # Set landmarks: shoulders (11/12), knees (25/26), hips (23/24), ankles (27/28)
        row["x12"] = sh_x - 0.02 * scale
        row["x13"] = sh_x + 0.02 * scale
        row["y12"] = sh_y
        row["y13"] = sh_y

        row["x26"] = kn_x - 0.01 * scale
        row["x27"] = kn_x + 0.01 * scale
        row["y26"] = kn_y
        row["y27"] = kn_y

        row["x24"] = hp_x - 0.01 * scale
        row["x25"] = hp_x + 0.01 * scale
        row["y24"] = hp_y
        row["y25"] = hp_y

        row["x28"] = ak_x - 0.01 * scale
        row["x29"] = ak_x + 0.01 * scale
        row["y28"] = ak_y
        row["y29"] = ak_y

        rows.append(row)

    return pd.DataFrame(rows)


def run_realtime_pipeline_in_memory(dataset_df) -> list:
    """Simulate real-time stream processing frame-by-frame on the synthetic dataset."""
    previous_rows = []
    output_rows = []

    for _, df_row in dataset_df.iterrows():
        # Reconstruct keypoints array
        keypoints = []
        for j in range(1, 34):
            keypoints.append(df_row.get(f"x{j}", np.nan))
            keypoints.append(df_row.get(f"y{j}", np.nan))

        row = build_pose_row(
            timestamp=df_row.get("timestamp"),
            frame=int(df_row.get("frame", 0)),
            keypoints=keypoints,
        )

        result = classify_posture_and_fall(row, previous_rows=previous_rows)
        row.update(result)
        previous_rows.append(row)
        output_rows.append(row)

    # Write output to CSVs (handled with try/except in pipeline_utils)
    write_pose_outputs(output_rows, pose_path=INPUT_CSV, posture_path=OUTPUT_CSV)
    return output_rows


def evaluate_scenario(scenario_name, output_df, expected_fall=False, expected_posture=None):
    posture_col = "posture_label" if "posture_label" in output_df.columns else ("posture" if "posture" in output_df.columns else None)
    
    posture_counts = output_df[posture_col].value_counts().to_dict() if posture_col else {}
    posture_counts = {k: int(v) for k, v in posture_counts.items()}
    most_common_posture = max(posture_counts, key=posture_counts.get, default="Unknown") if posture_counts else "Unknown"
    lying_frames = posture_counts.get("Lying", 0)
    standing_frames = posture_counts.get("Standing", 0)
    sitting_frames = posture_counts.get("Sitting", 0)
    unknown_frames = posture_counts.get("Unknown", 0)

    body_height_series = output_df["body_height"].dropna()
    torso_angle_series = output_df["torso_angle"].dropna()
    hip_height_series = output_df["hip_height"].dropna()

    mean_body_height = round(float(body_height_series.mean()), 4) if not body_height_series.empty else None
    mean_torso_angle = round(float(torso_angle_series.mean()), 2) if not torso_angle_series.empty else None
    mean_hip_height = round(float(hip_height_series.mean()), 4) if not hip_height_series.empty else None

    # Find if there was any transition
    transition_count = 0
    if posture_col and len(output_df) > 1:
        prev_state = None
        for posture in output_df[posture_col].tolist():
            if prev_state is not None and posture != prev_state:
                transition_count += 1
            prev_state = posture

    # Retrieve fall detection result from pipeline directly
    fall_detected = False
    if "fall_detected" in output_df.columns:
        fall_detected = bool(output_df["fall_detected"].any())

    expected_result = "Fall" if expected_fall else "No fall"
    actual_result = "Fall" if fall_detected else "No fall"
    passed = (actual_result == expected_result)

    if "confidence" in output_df.columns:
        confidence = round(float(output_df["confidence"].mean()), 2)
    else:
        confidence = 0.50

    # Posture accuracy: fraction of non-Unknown frames matching expected_posture
    posture_accuracy = None
    if expected_posture and posture_col:
        non_unknown = output_df[output_df[posture_col] != "Unknown"]
        if len(non_unknown) > 0:
            matching = int((non_unknown[posture_col] == expected_posture).sum())
            posture_accuracy = round(matching / len(non_unknown), 3)

    notes = []
    notes.append(f"Predominant posture: {most_common_posture}")
    notes.append(f"Standing={standing_frames}, Sitting={sitting_frames}, Lying={lying_frames}, Unknown={unknown_frames}")
    if mean_body_height is not None:
        notes.append(f"Mean body height={mean_body_height:.3f}")
    if mean_torso_angle is not None:
        notes.append(f"Mean torso angle={mean_torso_angle:.2f}")
    if mean_hip_height is not None:
        notes.append(f"Mean hip height={mean_hip_height:.3f}")
    notes.append(f"Transitions={transition_count}")
    if posture_accuracy is not None:
        notes.append(f"Posture accuracy={posture_accuracy:.1%}")

    return {
        "scenario": scenario_name,
        "detection": actual_result,
        "confidence": confidence,
        "fall_detected": "Yes" if fall_detected else "No",
        "frames_processed": len(output_df),
        "processing_time_ms": None,
        "result": "PASS" if passed else "FAIL",
        "notes": " | ".join(notes),
        "predominant_posture": most_common_posture,
        "expected_posture": expected_posture or "",
        "posture_accuracy": posture_accuracy,
        "lying_frames": lying_frames,
        "transition_count": transition_count,
        "mean_body_height": mean_body_height,
        "mean_torso_angle": mean_torso_angle,
        "mean_hip_height": mean_hip_height,
    }


def write_validation_log(rows):
    fieldnames = [
        "timestamp",
        "scenario",
        "frames_processed",
        "detection",
        "confidence",
        "fall_detected",
        "processing_time_ms",
        "result",
        "notes",
        "predominant_posture",
        "expected_posture",
        "posture_accuracy",
        "lying_frames",
        "transition_count",
        "mean_body_height",
        "mean_torso_angle",
        "mean_hip_height",
    ]
    try:
        with VALIDATION_LOG.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"Warning: Could not write {VALIDATION_LOG}: {e}")


def write_summary_report(rows, generated_at):
    total = len(rows)
    passed = sum(1 for row in rows if row["result"] == "PASS")
    failed = total - passed
    success_rate = round((passed / total) * 100, 1) if total else 0.0
    avg_processing = round(sum(float(row["processing_time_ms"] or 0.0) for row in rows) / total, 2) if total else 0.0
    avg_confidence = round(sum(float(row["confidence"] or 0.0) for row in rows) / total, 2) if total else 0.0

    sections = [
        "# Validation Summary",
        "",
        f"- Date/time: {generated_at}",
        f"- Total scenarios tested: {total}",
        f"- Passed scenarios: {passed}",
        f"- Failed scenarios: {failed}",
        f"- Success rate: {success_rate:.1f}%",
        f"- Average processing time: {avg_processing:.2f} ms",
        f"- Average confidence: {avg_confidence:.2f}",
        "",
        "## Per Scenario Results",
        "",
    ]

    for row in rows:
        accuracy_str = f"{row['posture_accuracy']:.1%}" if row.get("posture_accuracy") is not None else "N/A"
        sections.extend(
            [
                f"### {row['scenario']}",
                f"- Outcome: {row['result']}",
                f"- Detection: {row['detection']}",
                f"- Expected posture: {row.get('expected_posture') or 'N/A'}",
                f"- Posture accuracy: {accuracy_str}",
                f"- Important observations: {row['notes']}",
                f"- Possible reasons for failure: {'None' if row['result'] == 'PASS' else 'Threshold mismatch or missing posture evidence'}",
                "",
            ]
        )

    # Distance-variant posture accuracy breakdown
    distance_rows = [r for r in rows if any(tag in r["scenario"] for tag in ["_near", "_far", "_drift"])]
    if distance_rows:
        sections.extend([
            "## Distance Variant Posture Accuracy",
            "",
            "| Scenario | Expected Posture | Posture Accuracy | Result |",
            "|---|---|---|---|",
        ])
        for r in distance_rows:
            acc = f"{r['posture_accuracy']:.1%}" if r.get("posture_accuracy") is not None else "N/A"
            sections.append(f"| {r['scenario']} | {r.get('expected_posture', 'N/A')} | {acc} | {r['result']} |")
        sections.append("")

    sections.extend(
        [
            "## Overall Analysis",
            "",
            "- Strengths: The pipeline uses scale-invariant joint angles as the primary classification signal and time/scale-normalized velocity for fall detection.",
            "- Weaknesses: Heuristics are tuned to temporal sequences and depend on consistent landmark availability.",
            f"- False positives: {sum(1 for row in rows if row['result'] == 'FAIL' and row['detection'] == 'Fall')}",
            f"- False negatives: {sum(1 for row in rows if row['result'] == 'FAIL' and row['detection'] == 'No fall')}",
            "- Recommended threshold adjustments: Tune ANGLE_STANDING_MIN, ANGLE_SITTING_MAX, FALL_AVG_VELOCITY_FLOOR, and FALL_ANGULAR_VELOCITY_FLOOR against recorded validation clips.",
        ]
    )

    try:
        SUMMARY_REPORT.write_text("\n".join(sections) + "\n", encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not write {SUMMARY_REPORT}: {e}")


def main():
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # (scenario_name, expected_fall, expected_posture)
    scenarios = [
        ("Standing", False, "Standing"),
        ("Standing_near", False, "Standing"),
        ("Standing_far", False, "Standing"),
        ("Standing_drift", False, "Standing"),
        ("Sitting", False, "Sitting"),
        ("Sitting_near", False, "Sitting"),
        ("Sitting_far", False, "Sitting"),
        ("Walking", False, "Standing"),
        ("Slow lying", False, None),
        ("Fake fall", False, None),
        ("Empty room", False, None),
        ("Fall", True, None),
        ("Fall_far", True, None),
    ]
    rows = []

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for scenario_name, expected_fall, expected_posture in scenarios:
        print(f"\n=== Validating scenario: {scenario_name} ===")
        
        # Clear existing output files to avoid appending scenario data together
        try:
            if INPUT_CSV.exists():
                INPUT_CSV.unlink()
        except Exception as e:
            print(f"Warning: {INPUT_CSV} is locked ({e}). Overwriting dynamically during run.")
            
        try:
            if OUTPUT_CSV.exists():
                OUTPUT_CSV.unlink()
        except Exception as e:
            print(f"Warning: {OUTPUT_CSV} is locked ({e}). Overwriting dynamically during run.")

        dataset = build_synthetic_dataset(scenario_name)

        start_time = time.perf_counter()
        # Run real-time classification pipeline in-memory
        output_rows = run_realtime_pipeline_in_memory(dataset)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Build output DataFrame from in-memory results if CSV is locked
        output_df = pd.DataFrame(output_rows)

        evaluation = evaluate_scenario(scenario_name, output_df, expected_fall=expected_fall, expected_posture=expected_posture)
        evaluation["timestamp"] = generated_at
        evaluation["processing_time_ms"] = elapsed_ms
        rows.append(evaluation)

        acc_str = f" | posture_acc={evaluation['posture_accuracy']:.1%}" if evaluation.get("posture_accuracy") is not None else ""
        print(f"Scenario {scenario_name}: {evaluation['result']} | detection={evaluation['detection']} | confidence={evaluation['confidence']}{acc_str}")

    write_validation_log(rows)
    write_summary_report(rows, generated_at)
    print(f"\nValidation log saved to: {VALIDATION_LOG}")
    print(f"Summary report saved to: {SUMMARY_REPORT}")


if __name__ == "__main__":
    main()

"""Re-run src/detection/score_v7_suite.py for A (v7) and A2 on original vs corrected round6_heldout labels.

Does NOT rewrite the scoring logic: it imports score_v7_suite and only swaps its
MODELS / EVAL_SETS tables and its output location. The output goes to
benchmarks/phase3_a2/roboflow/rescore_out/results/yolo_person_detection/v7_suite_iou<X>.md,
never over the tracked results/yolo_person_detection/ files.

Usage (with the .venv2 interpreter, which has ultralytics + CUDA):
    python rescore_suite.py 0.5
    python rescore_suite.py 0.3
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(r"D:\FYP\PROJECT FILES\main")
sys.path.insert(0, str(REPO))

import src.detection.score_v7_suite as suite  # noqa: E402

HERE = Path(__file__).resolve().parent
A2_WEIGHTS = REPO / "benchmarks" / "phase3_a2" / "runs" / "A2" / "weights" / "best.pt"

suite.MODELS = {
    "A_v7": REPO / "models" / "yolov8n_sage_merged_v7.pt",
    "A2": A2_WEIGHTS,
}
suite.EVAL_SETS = {
    "round6_heldout ORIGINAL labels": REPO / "handlabels" / "round6_heldout",
    "round6_heldout_v2 CORRECTED labels": REPO / "handlabels" / "round6_heldout_v2",
}
# score_v7_suite builds its output path from REPO_ROOT at the end of main();
# MODELS and EVAL_SETS above are already absolute, so this only moves the report.
suite.REPO_ROOT = HERE / "rescore_out"

if __name__ == "__main__":
    for name, path in suite.MODELS.items():
        if not path.exists():
            sys.exit(f"STOP: {name} weights not found at {path}")
    suite.main()

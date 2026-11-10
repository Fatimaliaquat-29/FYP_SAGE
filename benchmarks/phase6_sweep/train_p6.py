"""Phase 6: one-change-at-a-time runs against baseline C (phase 5).

Base args = phase 5 C's effective args (benchmarks/phase5_v8/train_C_effective_args.json), so the recipe is identical;
each run changes exactly one entry (see RUNS) plus project/name. Never trains on original datasets (sage_v8_* are
hardlink copies).

Usage: python -u train_p6.py <RUN> [--resume]   (cwd = phase6_sweep)
"""
import json
import sys
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase6_sweep"
BASE = ROOT / "benchmarks" / "phase5_v8" / "train_C_effective_args.json"
RUNS = {
    "LR2": {"lr0": 0.001176},
    "COS": {"cos_lr": True},
    "DCOS": {"cos_lr": True, "data": str(ROOT / "datasets" / "sage_v8_fixclips" / "data.yaml")},
    "B32": {"batch": 32},
    "B8": {"batch": 8},
    "LRH": {"lr0": 0.000294},
    "D": {"data": str(ROOT / "datasets" / "sage_v8_fixclips" / "data.yaml")},
}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name not in RUNS:
        sys.exit(f"usage: train_p6.py {'|'.join(RUNS)} [--resume]")
    if Path.cwd().resolve() != OUT.resolve():
        sys.exit(f"STOP: run from {OUT}")
    run_dir = OUT / "runs" / name
    print(f"ultralytics {ultralytics.__version__}  torch {torch.__version__}  cuda {torch.cuda.is_available()}", flush=True)
    if "--resume" in sys.argv:
        last = run_dir / "weights" / "last.pt"
        if not last.exists():
            sys.exit(f"STOP: cannot resume, {last} not found")
        YOLO(str(last)).train(resume=True)
        return
    if run_dir.exists():
        sys.exit(f"STOP: {run_dir} already exists")
    base = json.loads(BASE.read_text(encoding="utf-8"))
    args = dict(base["effective_args"])
    start = base["starting_weights"]
    change = RUNS[name]
    args.update(change)
    args.update({"project": str(OUT / "runs"), "name": name, "exist_ok": False})
    if not Path(args["data"]).exists():
        sys.exit(f"STOP: data not found {args['data']}")
    OUT.joinpath(f"train_{name}_effective_args.json").write_text(json.dumps(
        {"baseline": "phase5 C", "change_vs_C": change, "starting_weights": start, "effective_args": args},
        indent=2, default=str), encoding="utf-8")
    print("CHANGE vs C:", change, flush=True)
    YOLO(start).train(**args)


if __name__ == "__main__":
    main()

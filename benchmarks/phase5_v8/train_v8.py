"""Phase 5: train B or C = model A's RECORDED train_args with only the data/run-location changes.

Recorded args are read from models/yolov8n_sage_merged_v7.pt (ckpt["train_args"]) at run time.
Changes: data = sage_v8_clean (B) or sage_v8_full (C), project=OUT/runs, name=B|C, workers=0, device=0,
exist_ok=False, optimizer pinned to what A used (AdamW, lr0 0.000588, momentum 0.9). Epochs stay 30.
Starting weights = recorded `model` (models/yolov8n.pt), made absolute.

Usage: python -u train_v8.py B|C [--resume]   (run with cwd = OUT)
"""
import json
import sys
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase5_v8"
CKPT_A = ROOT / "models" / "yolov8n_sage_merged_v7.pt"
DATA = {"B": ROOT / "datasets" / "sage_v8_clean" / "data.yaml", "C": ROOT / "datasets" / "sage_v8_full" / "data.yaml"}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name not in DATA:
        sys.exit("usage: train_v8.py B|C [--resume]")
    run_dir = OUT / "runs" / name
    print(f"ultralytics {ultralytics.__version__}  torch {torch.__version__}  cuda {torch.cuda.is_available()}", flush=True)
    if Path.cwd().resolve() != OUT.resolve():
        sys.exit(f"STOP: run from {OUT} (cwd is {Path.cwd()})")
    if "--resume" in sys.argv:
        last = run_dir / "weights" / "last.pt"
        if not last.exists():
            sys.exit(f"STOP: cannot resume, {last} not found")
        print(f"RESUME from {last}", flush=True)
        YOLO(str(last)).train(resume=True)
        return
    if run_dir.exists():
        sys.exit(f"STOP: {run_dir} already exists (exist_ok=False); not overwriting")

    recorded = torch.load(CKPT_A, weights_only=False, map_location="cpu")["train_args"]
    start_weights = (ROOT / recorded["model"]).resolve()
    if not start_weights.exists():
        sys.exit(f"STOP: recorded starting weights not found: {start_weights}")
    # optimizer pinned to what optimizer=auto resolved to for A (AdamW, lr 0.000588 = 0.002*5/(4+13)). With 7
    # classes auto would pick lr 0.000909, which would make the learning rate a second difference besides data.
    overrides = {"data": str(DATA[name]), "project": str(OUT / "runs"), "name": name,
                 "workers": 0, "device": 0, "exist_ok": False,
                 "optimizer": "AdamW", "lr0": 0.000588, "momentum": 0.9}
    args = dict(recorded)
    args.update(overrides)
    args.pop("model")
    changed = {k: {"recorded": recorded.get(k), "used": args.get(k)}
               for k in set(recorded) | set(args) if recorded.get(k) != args.get(k)}
    OUT.joinpath(f"train_{name}_effective_args.json").write_text(json.dumps(
        {"ultralytics": ultralytics.__version__, "torch": torch.__version__, "starting_weights": str(start_weights),
         "changed_vs_recorded": changed, "effective_args": args}, indent=2, default=str), encoding="utf-8")
    print("CHANGED vs recorded:", json.dumps(changed, default=str), flush=True)
    YOLO(str(start_weights)).train(**args)


if __name__ == "__main__":
    main()

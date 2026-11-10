"""Phase 4: train A50 = model A's RECORDED train_args with epochs 30 -> 50 and only the run-location changes.

Recorded args are read from models/yolov8n_sage_merged_v7.pt (ckpt["train_args"]) at run time.
Changes: epochs=50, data=data_A50.yaml (hardlink copy), project=OUT/runs, name=A50, workers=0, device=0,
exist_ok=False. Starting weights = recorded `model` (models/yolov8n.pt), made absolute.

Usage: python -u train_A50.py [--resume]   (run with cwd = OUT)
"""
import json
import sys
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase4_a50"
CKPT_A = ROOT / "models" / "yolov8n_sage_merged_v7.pt"
DATA = ROOT / "datasets" / "sage_merged_v7_A50" / "data_A50.yaml"
RUN_DIR = OUT / "runs" / "A50"


def main():
    print(f"ultralytics {ultralytics.__version__}  torch {torch.__version__}  cuda {torch.cuda.is_available()}", flush=True)
    if Path.cwd().resolve() != OUT.resolve():
        sys.exit(f"STOP: run from {OUT} (cwd is {Path.cwd()})")
    if "--resume" in sys.argv:
        last = RUN_DIR / "weights" / "last.pt"
        if not last.exists():
            sys.exit(f"STOP: cannot resume, {last} not found")
        print(f"RESUME from {last}", flush=True)
        YOLO(str(last)).train(resume=True)
        return
    if RUN_DIR.exists():
        sys.exit(f"STOP: {RUN_DIR} already exists (exist_ok=False); not overwriting")

    recorded = torch.load(CKPT_A, weights_only=False, map_location="cpu")["train_args"]
    start_weights = (ROOT / recorded["model"]).resolve()
    if not start_weights.exists():
        sys.exit(f"STOP: recorded starting weights not found: {start_weights}")
    # optimizer pinned to what optimizer=auto resolved to for A (AdamW, lr 0.000588, momentum 0.9; see
    # phase3_a2/train_A2.log). With epochs=50, auto crosses Ultralytics' 10,000-iteration threshold and
    # switches to MuSGD lr 0.01, which would make optimizer a second difference besides epochs.
    overrides = {"epochs": 50, "data": str(DATA), "project": str(OUT / "runs"), "name": "A50",
                 "workers": 0, "device": 0, "exist_ok": False,
                 "optimizer": "AdamW", "lr0": 0.000588, "momentum": 0.9}
    args = dict(recorded)
    args.update(overrides)
    args.pop("model")
    if "sage_merged_v7_A50" not in args["data"] or not DATA.exists():
        sys.exit(f"STOP: data does not point at the A50 copy: {args['data']}")
    changed = {k: {"recorded": recorded.get(k), "used": args.get(k)}
               for k in set(recorded) | set(args) if recorded.get(k) != args.get(k)}
    OUT.joinpath("train_A50_effective_args.json").write_text(json.dumps(
        {"ultralytics": ultralytics.__version__, "torch": torch.__version__, "starting_weights": str(start_weights),
         "changed_vs_recorded": changed, "effective_args": args}, indent=2, default=str), encoding="utf-8")
    print("CHANGED vs recorded:", json.dumps(changed, default=str), flush=True)
    YOLO(str(start_weights)).train(**args)


if __name__ == "__main__":
    main()

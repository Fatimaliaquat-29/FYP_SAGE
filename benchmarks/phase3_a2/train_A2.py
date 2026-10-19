"""A4: train A2 with model A's RECORDED train_args and only the allowed changes.

Recorded args are read from models/yolov8n_sage_merged_v7.pt (ckpt["train_args"]) at
run time, so nothing is retyped by hand. Allowed changes (phase-3 prompt, A4):
  data=data_A2.yaml, project=OUT/runs, name=A2, workers=0, device=0, exist_ok=False
Starting weights = the recorded `model` value (models/yolov8n.pt), made absolute.

Usage:
  python -u train_A2.py            fresh run (refuses if OUT/runs/A2 exists)
  python -u train_A2.py --resume   resume from OUT/runs/A2/weights/last.pt (same settings)
Run with cwd = OUT so any Ultralytics asset download lands in OUT, not in the repo.
"""
import json
import sys
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase3_a2"
CKPT_A = ROOT / "models" / "yolov8n_sage_merged_v7.pt"
DATA_A2 = ROOT / "datasets" / "sage_merged_v7_A2" / "data_A2.yaml"
RUN_DIR = OUT / "runs" / "A2"


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

    overrides = {
        "data": str(DATA_A2),
        "project": str(OUT / "runs"),
        "name": "A2",
        "workers": 0,
        "device": 0,
        "exist_ok": False,
    }
    args = dict(recorded)
    args.update(overrides)
    args.pop("model")  # passed via YOLO(start_weights); same file as recorded, made absolute

    # Hard guard: Ultralytics must only ever see the A2 copy.
    if "sage_merged_v7_A2" not in args["data"] or not DATA_A2.exists():
        sys.exit(f"STOP: data does not point at the A2 copy: {args['data']}")

    changed = {k: {"recorded": recorded.get(k), "used": args.get(k)}
               for k in set(recorded) | set(args) if recorded.get(k) != args.get(k)}
    record = {"ultralytics": ultralytics.__version__, "torch": torch.__version__,
              "starting_weights": str(start_weights), "recorded_model_value": recorded["model"],
              "changed_vs_recorded": changed, "effective_args": args}
    OUT.joinpath("train_A2_effective_args.json").write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
    print("CHANGED vs recorded:", json.dumps(changed, default=str), flush=True)

    YOLO(str(start_weights)).train(**args)


if __name__ == "__main__":
    main()

"""A1: print the recorded train_args of model A (own checkpoint, trusted). Read-only."""
import json
import sys

import torch

ckpt = torch.load(r"D:\FYP\PROJECT FILES\main\models\yolov8n_sage_merged_v7.pt",
                  weights_only=False, map_location="cpu")
print("ckpt keys:", sorted(ckpt.keys()))
for k in ("version", "date", "epoch", "best_fitness", "license"):
    if k in ckpt:
        print(f"{k}: {ckpt[k]}")
args = ckpt.get("train_args")
print("TRAIN_ARGS_JSON " + json.dumps(args, default=str, sort_keys=True))
model = ckpt.get("model") or ckpt.get("ema")
names = getattr(model, "names", None)
print("model.names:", names)
sys.exit(0 if args else 1)

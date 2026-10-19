"""STAGE 5/6 -- train B or C with A's exact recipe (runs/detect/v7_1epoch_benchmark2/args.yaml), changing only
model / data / project / name / epochs / patience (and batch only on the documented crash fallback).
Usage:
  stage5_train.py --name B_yolo26n_30ep --epochs 30 --patience 10
  stage5_train.py --name B_yolo26n_30ep --resume <last.pt>
  stage5_train.py --name B_yolo26n_30ep_b8 --epochs 30 --patience 10 --batch 8
Writes raw/train_<key>.json (recipe, dropped keys, save_dir, best.pt) and raw/train_<key>_epochs.json."""
import argparse
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, OUT, RAW, RUNS, log, write_json, read_json

import yaml

CONTROL_ARGS = ROOT / "runs/detect/v7_1epoch_benchmark2/args.yaml"
NOT_COPIED = {"task", "mode", "model", "data", "epochs", "patience", "project", "name", "save_dir", "resume"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--key", default=None, help="logical model key (B_yolo26n_30ep / C_yolo26n_50ep)")
    ap.add_argument("--epochs", type=int)
    ap.add_argument("--patience", type=int)
    ap.add_argument("--batch", type=int, default=None)
    ap.add_argument("--resume", default=None)
    a = ap.parse_args()
    key = a.key or a.name
    from ultralytics import YOLO
    from ultralytics.cfg import DEFAULT_CFG_DICT

    meta_path = RAW / f"train_{key}.json"
    ep_path = RAW / f"train_{key}_epochs.json"
    meta = read_json(meta_path, {"key": key, "attempts": []})
    epochs_log = read_json(ep_path, [])
    attempt = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "name": a.name, "resume": a.resume, "batch_override": a.batch}

    state = {"t_epoch_start": None}

    def on_train_epoch_start(tr):
        state["t_epoch_start"] = time.time()

    def on_fit_epoch_end(tr):
        try:
            t = time.time()
            rec = {"epoch": int(tr.epoch) + 1, "t_start": state["t_epoch_start"], "t_end": t,
                   "duration_s": (t - state["t_epoch_start"]) if state["t_epoch_start"] else None,
                   "metrics": {k: float(v) for k, v in (tr.metrics or {}).items()},
                   "attempt_name": a.name}
            epochs_log.append(rec)
            write_json(ep_path, epochs_log)
        except Exception as ex:
            print(f"epoch bookkeeping failed: {ex!r}", flush=True)

    def on_train_start(tr):
        try:  # never let bookkeeping crash training
            attempt["save_dir"] = str(tr.save_dir)
            attempt["optimizer_arg"] = str(tr.args.optimizer)
            opt = getattr(tr, "optimizer", None)
            attempt["optimizer_used"] = type(opt).__name__ if opt is not None else None
            attempt["lr0_used"] = float(opt.param_groups[0].get("initial_lr", opt.param_groups[0]["lr"])) if opt is not None else None
            write_json(meta_path, meta)
        except Exception as ex:
            attempt["on_train_start_error"] = repr(ex)

    try:
        if a.resume:
            model = YOLO(a.resume)
            attempt["recipe"] = "resume=True from " + a.resume
            for cb, fn in (("on_train_epoch_start", on_train_epoch_start), ("on_fit_epoch_end", on_fit_epoch_end),
                           ("on_train_start", on_train_start)):
                model.add_callback(cb, fn)
            meta["attempts"].append(attempt)
            write_json(meta_path, meta)
            model.train(resume=True)
        else:
            control = yaml.safe_load(CONTROL_ARGS.read_text())
            overrides = {k: v for k, v in control.items() if k not in NOT_COPIED}
            dropped = sorted(k for k in overrides if k not in DEFAULT_CFG_DICT)
            for k in dropped:
                overrides.pop(k)
            overrides.update(data=str(OUT / "data_v7_fixed.yaml"), epochs=a.epochs, patience=a.patience,
                             project=str(RUNS), name=a.name)
            if a.batch:
                overrides["batch"] = a.batch
            attempt.update(recipe=overrides, dropped_keys_not_accepted=dropped,
                           model=str(ROOT / "yolo26n.pt"),
                           changed_vs_control={k: (control.get(k), overrides.get(k)) for k in
                                               ("model", "data", "epochs", "patience", "project", "name", "batch")
                                               if control.get(k) != overrides.get(k)})
            meta["attempts"].append(attempt)
            write_json(meta_path, meta)
            model = YOLO(str(ROOT / "yolo26n.pt"))
            for cb, fn in (("on_train_epoch_start", on_train_epoch_start), ("on_fit_epoch_end", on_fit_epoch_end),
                           ("on_train_start", on_train_start)):
                model.add_callback(cb, fn)
            model.train(**overrides)
        tr = model.trainer
        attempt["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        attempt["save_dir"] = str(tr.save_dir)
        attempt["best_pt"] = str(Path(tr.save_dir) / "weights" / "best.pt")
        attempt["epochs_completed"] = int(tr.epoch) + 1
        attempt["stopped_early"] = bool(getattr(tr, "stop", False)) and (int(tr.epoch) + 1) < int(tr.epochs)
        attempt["best_fitness"] = float(tr.best_fitness) if tr.best_fitness is not None else None
        attempt["status"] = "done"
        meta["best_pt"] = attempt["best_pt"]
        meta["save_dir"] = attempt["save_dir"]
        meta["status"] = "done"
        write_json(meta_path, meta)
        log(f"training {a.name} finished: {attempt['best_pt']}")
    except Exception as e:
        attempt["status"] = "crashed"
        attempt["error"] = repr(e)
        attempt["traceback_tail"] = traceback.format_exc()[-3000:]
        write_json(meta_path, meta)
        log(f"training {a.name} CRASHED: {e!r}")
        raise


if __name__ == "__main__":
    main()

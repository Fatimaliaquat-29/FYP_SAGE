"""Score models on every located person set (+ empty-room FP), optionally ultralytics val.
Usage: score_models.py --models stock_yolo26n stock_yolo26s --confs 0.4 0.25 [--val]
Writes raw/scores__<model>.json (one file per model, all confs)."""
import argparse
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RAW, MODELS, OUT, IMGSZ, log, write_json, read_json, decision, model_path
import score_lib as S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--confs", nargs="+", type=float, default=[0.4])
    ap.add_argument("--val", action="store_true")
    args = ap.parse_args()
    from ultralytics import YOLO
    any_ok = False
    for key in args.models:
        path = model_path(key)
        dst = RAW / f"scores__{key}.json"
        res = read_json(dst, {"model": key, "path": str(path), "scores": {}, "empty_fp": {}})
        if not path.exists():
            res["FAILED"] = f"weights not found: {path}"
            write_json(dst, res)
            log(f"SKIP {key}: {path} missing")
            continue
        m = YOLO(str(path))
        res["names0"] = m.names[0]
        res["n_classes"] = len(m.names)
        for conf in args.confs:
            for s in S.EVAL_SETS:
                k = f"{s}|c{conf}"
                if k in res["scores"]:
                    continue
                log(f"scoring {key} on {s} conf={conf}")
                try:
                    res["scores"][k] = S.score_model_on_set(m, key, s, conf=conf)
                except Exception as e:
                    res["scores"][k] = {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]}
                write_json(dst, res)
            if f"c{conf}" not in res["empty_fp"]:
                log(f"empty-room FP {key} conf={conf}")
                try:
                    res["empty_fp"][f"c{conf}"] = S.empty_room_fp(m, key, conf=conf)
                except Exception as e:
                    res["empty_fp"][f"c{conf}"] = {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]}
                write_json(dst, res)
        if args.val and "val" not in res:
            try:
                log(f"ultralytics val {key}")
                mv = m.val(data=str(OUT / "data_v7_fixed.yaml"), imgsz=IMGSZ, batch=16, workers=0, split="val",
                           project=str(OUT / "runs"), name=f"{key}_val", exist_ok=True, plots=False, verbose=False)
                res["val"] = {"mAP50": float(mv.box.map50), "mAP50_95": float(mv.box.map),
                              "precision": float(mv.box.mp), "recall": float(mv.box.mr)}
            except Exception as e:
                res["val"] = {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]}
            write_json(dst, res)
        any_ok = True
    if not any_ok:
        sys.exit(3)


if __name__ == "__main__":
    main()

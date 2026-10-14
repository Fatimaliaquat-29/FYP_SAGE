"""STAGE 3 / 6 -- dark-frame enhancement test. Variants applied to the input image before inference only.
Usage: stage3_enhance.py --models A_v7 stock_yolo26n [--grids]
Dark/bright subsets come from raw/luma_thresholds.json, which preflight wrote BEFORE any scoring."""
import argparse
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RAW, OUT, MODELS, STOCK, CONF, log, write_json, read_json, model_path
import score_lib as S

import cv2
import numpy as np

POOLED = ("reserved388_partial", "round6_heldout")   # disjoint, correctly oriented; used for the verdict


def subsets():
    lt = read_json(RAW / "luma_thresholds.json")
    out = {}
    for s, d in lt["sets"].items():
        lum = d["luma"]
        out[s] = {"dark": {n for n, v in lum.items() if v <= d["dark_max_luma"]},
                  "bright": {n for n, v in lum.items() if v >= d["bright_min_luma"]},
                  "all": set(lum)}
    return out


def run_model(key, subs):
    from ultralytics import YOLO
    dst = RAW / f"enhance__{key}.json"
    res = read_json(dst, {"model": key, "conf": CONF, "sets": {}})
    m = YOLO(str(model_path(key)))
    stock = key in STOCK
    for s in S.EVAL_SETS:
        gt, _ = S.load_set(s)
        for var in S.ENHANCEMENTS:
            k = f"{s}|{var}"
            if k in res["sets"]:
                continue
            log(f"S3 {key} {s} {var}")
            try:
                preds = S.predict_set(m, key, s, conf=CONF, enhancement=var)
                entry = {}
                for thr in (0.5, 0.3):
                    for sub in ("all", "dark", "bright"):
                        sc = S.score_preds(gt, preds, thr, stock, subset=subs[s][sub])
                        entry[f"{sub}|{thr}"] = S.summarise(*sc["person"])
                        entry[f"{sub}|{thr}"]["n_frames"] = len(subs[s][sub] & {Path(p).name for p in gt})
                res["sets"][k] = entry
            except Exception as e:
                res["sets"][k] = {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]}
            write_json(dst, res)
    # pooled over the disjoint sets
    pooled = {}
    for var in S.ENHANCEMENTS:
        e = {}
        for key2 in ("all|0.5", "dark|0.5", "bright|0.5", "all|0.3", "dark|0.3", "bright|0.3"):
            tp = fp = fn = nf = 0
            for s in POOLED:
                d = res["sets"].get(f"{s}|{var}", {}).get(key2)
                if not d:
                    continue
                tp += d["tp"]; fp += d["fp"]; fn += d["fn"]; nf += d["n_frames"]
            e[key2] = S.summarise(tp, fp, fn)
            e[key2]["n_frames"] = nf
        pooled[var] = e
    res["pooled"] = {"sets": list(POOLED), "variants": pooled}
    write_json(dst, res)
    return res


def grids(key="A_v7"):
    """6 darkest labelled frames that contain a person (pooled sets): original vs best variant for A,
    with hand-drawn person GT (green) and the model's person detections (red)."""
    res = read_json(RAW / f"enhance__{key}.json")
    pv = res["pooled"]["variants"]
    base = pv["none"]["dark|0.5"]["recall"] or 0
    gains = {v: (pv[v]["dark|0.5"]["recall"] or 0) - base for v in pv if v != "none"}
    best = max(gains, key=lambda v: gains[v])
    lt = read_json(RAW / "luma_thresholds.json")
    cands = []
    for s in POOLED:
        gt, _ = S.load_set(s)
        for p, boxes in gt.items():
            if any(b[0] == 0 for b in boxes):
                cands.append((lt["sets"][s]["luma"][Path(p).name], s, Path(p), boxes))
    cands.sort(key=lambda x: x[0])
    # spread across both sets: take the 3 darkest of each
    pick = []
    for s in POOLED:
        pick += [c for c in cands if c[1] == s][:3]
    gdir = OUT / "enhance_grids"
    gdir.mkdir(exist_ok=True)
    written = []
    for i, (lum, s, p, boxes) in enumerate(pick):
        im = cv2.imread(str(p))
        variants = {"none": im, best: S.ENHANCEMENTS[best](im)}
        panels = []
        for var, img in variants.items():
            img = img.copy()
            h, w = img.shape[:2]
            preds = read_json(S.PRED_DIR / f"{key}__{s}__c{CONF}__{var}.json", {}).get(p.name, [])
            for b in boxes:
                if b[0] == 0:
                    cv2.rectangle(img, (int(b[1] * w), int(b[2] * h)), (int(b[3] * w), int(b[4] * h)), (0, 255, 0), 4)
            for c, cls, bx in preds:
                if cls == 0:
                    cv2.rectangle(img, (int(bx[0] * w), int(bx[1] * h)), (int(bx[2] * w), int(bx[3] * h)), (0, 0, 255), 4)
                    cv2.putText(img, f"{c:.2f}", (int(bx[0] * w), max(30, int(bx[1] * h) - 8)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(img, f"{var} | luma {lum:.1f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 4)
            scale = 640 / w
            panels.append(cv2.resize(img, (640, int(h * scale))))
        hh = max(x.shape[0] for x in panels)
        panels = [cv2.copyMakeBorder(x, 0, hh - x.shape[0], 0, 0, cv2.BORDER_CONSTANT) for x in panels]
        f = gdir / f"grid_{i + 1}_{s}_{p.stem}.jpg"
        cv2.imwrite(str(f), np.hstack(panels))
        written.append(str(f))
    write_json(RAW / "enhance_grids.json", {"model": key, "best_variant_by_pooled_dark_recall_gain": best,
                                            "gains": gains, "files": written,
                                            "legend": "green = hand-drawn person GT, red = model person detections (conf>=0.4)"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--grids", action="store_true")
    args = ap.parse_args()
    subs = subsets()
    ok = 0
    for key in args.models:
        if not model_path(key).exists():
            log(f"SKIP {key}: weights missing")
            continue
        run_model(key, subs)
        ok += 1
    if args.grids:
        try:
            grids("A_v7")
        except Exception as e:
            write_json(RAW / "enhance_grids.json", {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]})
    if not ok:
        sys.exit(3)


if __name__ == "__main__":
    main()

"""Phase 5: score A (v7, 13 classes), B and C (7 classes) on the same sets in one session; apply DECISION_RULE.md.

Same harness as phase 4 (score_A50.py): conf 0.4, imgsz 640, score_v7_suite's greedy same-class matching
(instrumented copy). For model A the instrumented loop is first asserted equal to score_v7_suite.score_model in
the original 13-class space, then everything is compared in the 7-class space: held-out ground truth and A's
predictions are mapped (couch -> sofa, dining table -> table, ...; dropped classes removed). Person is id 0 in
both spaces, so A's person numbers are unchanged by the mapping and the control still applies.

Writes only under benchmarks/phase5_v8/: hits_<M>.csv, preds_<M>.json, v8_scores.json, RESULTS.md.
Usage: python -u score_v8.py
"""
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase5_v8"
sys.path.insert(0, str(ROOT))

import src.detection.score_v7_suite as suite  # noqa: E402  (unchanged scoring)
import src.detection.score_empty_false_positives as sef  # noqa: E402
from src.detection.footage_paths import RESERVED_EMPTY  # noqa: E402
from src.detection.score_heldout_objects import iou, load_ground_truth  # noqa: E402

CONF, IMGSZ = suite.CONF, suite.IMGSZ
IOUS = (0.5, 0.3)
NAMES = ["person", "bed", "chair", "sofa", "table", "bottle", "cup"]
V7_NAMES = ["person", "bottle", "cup", "wine glass", "bowl", "chair", "couch", "bed",
            "dining table", "toilet", "tv", "sink", "refrigerator"]
V7_MAP = {0: 0, 7: 1, 5: 2, 6: 3, 8: 4, 1: 5, 2: 6}
MODELS = {"A": ROOT / "models" / "yolov8n_sage_merged_v7.pt",
          "B": OUT / "runs" / "B" / "weights" / "best.pt",
          "C": OUT / "runs" / "C" / "weights" / "best.pt"}
NATIVE13 = {"A"}
SETS13 = {"heldout_objects": ROOT / "eval" / "heldout_objects",
          "reserved388_partial": ROOT / "benchmarks" / "overnight_yolo26" / "evalsets" / "held_out" / "reserved388_partial",
          "round6_heldout": ROOT / "handlabels" / "round6_heldout"}
SETS7 = {"cauca_s10": ROOT / "datasets" / "sage_v8_heldout_new" / "cauca_s10",
         "exdark_test": ROOT / "datasets" / "sage_v8_heldout_new" / "exdark_test"}
SETS = {**SETS13, **SETS7}
CONTROL = {"heldout_objects": (58, 93), "reserved388_partial": (107, 249), "round6_heldout": (50, 226)}
DECISION_SETS = ("round6_heldout", "reserved388_partial")
PROVISIONAL = ("**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no "
               "consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).")


def clip_of(name):
    stem = Path(name).stem
    c, _, f = stem.rpartition("_")
    return c if c and f.isdigit() else stem


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def load_set(d):
    image_paths = sorted(p for p in (d / "images").iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    return load_ground_truth(d / "labels", image_paths)


def predict(model, image_path):
    """Exactly score_v7_suite.score_model's prediction step."""
    preds = []
    for result in model.predict(str(image_path), conf=CONF, imgsz=IMGSZ, verbose=False):
        for box in result.boxes:
            x1, y1, x2, y2 = (float(v) for v in box.xyxyn[0])
            preds.append((float(box.conf.item()), int(box.cls.item()), (x1, y1, x2, y2)))
    preds.sort(key=lambda p: -p[0])
    return preds


def match_with_hits(gt_boxes, preds, iou_match):
    """score_v7_suite.score_model's matching loop, additionally recording which GT boxes were hit."""
    stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    hit = [False] * len(gt_boxes)
    unmatched = list(range(len(gt_boxes)))
    for _, cls, box in preds:
        best_iou, best_idx = 0.0, None
        for gi in unmatched:
            gt_cls, gt_box = gt_boxes[gi]
            if gt_cls != cls:
                continue
            overlap = iou(box, gt_box)
            if overlap > best_iou:
                best_iou, best_idx = overlap, gi
        if best_idx is not None and best_iou >= iou_match:
            stats[cls]["tp"] += 1
            unmatched.remove(best_idx)
            hit[best_idx] = True
        else:
            stats[cls]["fp"] += 1
    for gi in unmatched:
        stats[gt_boxes[gi][0]]["fn"] += 1
    return stats, hit


def to7_gt(boxes, is13):
    out = []
    for cls, *box in boxes:
        if is13:
            if cls in V7_MAP:
                out.append((V7_MAP[cls], tuple(box)))
        elif 0 <= cls < len(NAMES):
            out.append((cls, tuple(box)))
    return out


def to7_preds(preds, is13):
    return [(c, V7_MAP[k], b) for c, k, b in preds if k in V7_MAP] if is13 else preds


def score_model(name, model, gts):
    """Returns per-class stats (7-space), per-box rows, person FP per image, raw predictions (7-space)."""
    is13m = name in NATIVE13
    stats = {s: {thr: defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}) for thr in IOUS} for s in gts}
    fp_person = {s: {thr: {} for thr in IOUS} for s in gts}
    rows, raw = [], {}
    for s, gt in gts.items():
        is13s = s in SETS13
        if is13m and is13s:   # harness check against the official scorer, original 13-class space
            official = {thr: suite.score_model(model, gt, thr)[0] for thr in IOUS}
            mine = {thr: defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}) for thr in IOUS}
        raw[s] = {}
        for image_path, all_gt in gt.items():
            preds = predict(model, image_path)
            if is13m and is13s:
                g13 = [(c, tuple(b)) for c, *b in all_gt if c < len(V7_NAMES)]
                for thr in IOUS:
                    st, _ = match_with_hits(g13, preds, thr)
                    for c, v in st.items():
                        for k in ("tp", "fp", "fn"):
                            mine[thr][c][k] += v[k]
            g7, p7 = to7_gt(all_gt, is13s), to7_preds(preds, is13m)
            raw[s][image_path.name] = [[round(c, 4), k, *[round(v, 5) for v in b]] for c, k, b in p7]
            hits = {}
            for thr in IOUS:
                st, h = match_with_hits(g7, p7, thr)
                hits[thr] = h
                for c, v in st.items():
                    for k in ("tp", "fp", "fn"):
                        stats[s][thr][c][k] += v[k]
                fp_person[s][thr][image_path.name] = st[0]["fp"] if 0 in st else 0
            for i, (cls, box) in enumerate(g7):
                rows.append({"set": s, "image": image_path.name, "clip": clip_of(image_path.name) if is13s else s,
                             "box_idx": i, "cls": cls, "x1": f"{box[0]:.6f}", "y1": f"{box[1]:.6f}",
                             "x2": f"{box[2]:.6f}", "y2": f"{box[3]:.6f}",
                             "hit_iou0.5": int(hits[0.5][i]), "hit_iou0.3": int(hits[0.3][i])})
        if is13m and is13s:
            for thr in IOUS:
                for c in set(official[thr]) | set(mine[thr]):
                    a = dict(official[thr].get(c, {"tp": 0, "fp": 0, "fn": 0}))
                    b = dict(mine[thr].get(c, {"tp": 0, "fp": 0, "fn": 0}))
                    if a != b:
                        raise SystemExit(f"STOP: harness mismatch {name}/{s}/IoU{thr}/cls{c}: suite {a} vs instrumented {b}")
        print(f"  {name} {s}: done", flush=True)
    return stats, rows, fp_person, raw


def empty_room(model):
    clips = sorted(p for p in RESERVED_EMPTY.rglob("*") if p.suffix.lower() in sef.VIDEO_EXTENSIONS | sef.IMAGE_EXTENSIONS)
    out = {"frames": 0, "fp_frames": 0, "person_boxes": 0, "clips": {}}
    for c in clips:
        n, fpf, boxes, other, worst = sef.score_clip(model, c, 1, CONF, IMGSZ)
        out["clips"][c.name] = {"frames": n, "fp_frames": fpf, "person_boxes": boxes}
        out["frames"] += n
        out["fp_frames"] += fpf
        out["person_boxes"] += boxes
    return out


def val_metrics(name):
    rc = OUT / "runs" / name / "results.csv"
    if not rc.exists():
        return None
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(open(rc, encoding="utf-8"))]
    best = max(rows, key=lambda r: float(r["metrics/mAP50-95(B)"]))
    pick = lambda r: {"epoch": r["epoch"], "mAP50": r["metrics/mAP50(B)"], "mAP50-95": r["metrics/mAP50-95(B)"]}
    return {"epochs_logged": len(rows), "best_by_mAP50-95": pick(best), "last": pick(rows[-1])}


def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({k / n:.3f}) [{lo:.3f}, {hi:.3f}]" if n else "--"


def main():
    started = datetime.now().isoformat(timespec="seconds")
    gts = {}
    for s, d in SETS.items():
        gt, unl = load_set(d)
        gts[s] = gt
        print(f"{s}: {len(gt)} frames, {sum(1 for v in gt.values() for b in v if b[0] == 0)} person boxes, "
              f"{len(unl)} unlabelled excluded", flush=True)
    from ultralytics import YOLO
    models = {m: p for m, p in MODELS.items() if p.exists()}
    missing = [m for m in MODELS if m not in models]
    res = {"started": started, "conf": CONF, "imgsz": IMGSZ, "models": {k: str(v) for k, v in models.items()},
           "missing_models": missing, "stats": {}, "fp_person": {}, "empty_room": {}, "val": {}}
    rows_by = {}
    for m, p in models.items():
        print(f"scoring {m} ...", flush=True)
        model = YOLO(str(p))
        st, rows, fpp, raw = score_model(m, model, gts)
        rows_by[m] = rows
        res["stats"][m] = {s: {str(t): {NAMES[c]: v for c, v in st[s][t].items()} for t in IOUS} for s in st}
        res["fp_person"][m] = {s: {str(t): fpp[s][t] for t in IOUS} for s in fpp}
        with open(OUT / f"hits_{m}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        (OUT / f"preds_{m}.json").write_text(json.dumps(raw), encoding="utf-8")
        print(f"empty-room {m} ...", flush=True)
        res["empty_room"][m] = empty_room(model)
        res["val"][m] = val_metrics(m) if m != "A" else None
        if m == "A":
            control = {}
            for s, (kr, nr) in CONTROL.items():
                sel = [r for r in rows if r["set"] == s and r["cls"] == 0]
                k, n = sum(r["hit_iou0.5"] for r in sel), len(sel)
                control[s] = {"measured": [k, n], "recorded": [kr, nr], "reproduced": (k, n) == (kr, nr)}
            res["control"] = control
            if not all(v["reproduced"] for v in control.values()):
                res["verdict"] = {"_": "CONTROL FAILED: no comparison reported"}
                (OUT / "v8_scores.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
                write_md(res, {}, {})
                print("CONTROL FAILED", json.dumps(control), flush=True)
                return 1

    # paired person comparisons
    key = lambda r: (r["set"], r["image"], r["box_idx"])
    idx = {m: {key(r): r for r in rows if r["cls"] == 0} for m, rows in rows_by.items()}
    paired = {}
    for a, b in (("A", "B"), ("A", "C"), ("B", "C")):
        if a not in idx or b not in idx:
            continue
        assert set(idx[a]) == set(idx[b]), f"per-box keys differ between {a} and {b}"
        for thr in IOUS:
            for s in SETS:
                groups = {"ALL": [k for k in idx[a] if k[0] == s]}
                if s in SETS13:
                    for k in groups["ALL"]:
                        groups.setdefault(idx[a][k]["clip"], []).append(k)
                for g, ks in groups.items():
                    ha = sum(idx[a][k][f"hit_iou{thr}"] for k in ks)
                    hb = sum(idx[b][k][f"hit_iou{thr}"] for k in ks)
                    ob = sum(1 for k in ks if idx[b][k][f"hit_iou{thr}"] and not idx[a][k][f"hit_iou{thr}"])
                    oa = sum(1 for k in ks if idx[a][k][f"hit_iou{thr}"] and not idx[b][k][f"hit_iou{thr}"])
                    imgs = {k[1] for k in ks}
                    fpa = sum(res["fp_person"][a][s][str(thr)].get(i, 0) for i in imgs)
                    fpb = sum(res["fp_person"][b][s][str(thr)].get(i, 0) for i in imgs)
                    paired[f"{a}|{b}|{thr}|{s}|{g}"] = {"n": len(ks), "a_hits": ha, "b_hits": hb, "b_only": ob, "a_only": oa,
                                                        "mcnemar_p": mcnemar_exact(ob, oa), "a_fp": fpa, "b_fp": fpb}
    res["paired"] = paired
    verdict = {}
    for m in ("B", "C"):
        if m not in idx:
            verdict[m] = "not scored (no weights)"
            continue
        ch = {s: paired[f"A|{m}|0.5|{s}|ALL"] for s in DECISION_SETS}
        if all(c["mcnemar_p"] < 0.05 and c["b_only"] > c["a_only"] for c in ch.values()):
            verdict[m] = f"{m} is clearly better than A"
        elif all(c["mcnemar_p"] < 0.05 and c["a_only"] > c["b_only"] for c in ch.values()):
            verdict[m] = f"{m} is clearly worse than A"
        else:
            verdict[m] = "no clear difference"
    res["verdict"] = verdict
    res["finished"] = datetime.now().isoformat(timespec="seconds")
    (OUT / "v8_scores.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    write_md(res, paired, verdict)
    print("VERDICT:", json.dumps(verdict), flush=True)
    return 0


def write_md(res, paired, verdict):
    ms = list(res["stats"])
    L = ["# RESULTS: A (v7) vs B (cleaned, 7 classes) vs C (cleaned + CAUCAFall + ExDark)", "", PROVISIONAL, "",
         f"Scored {res['started']} to {res.get('finished', '?')}. conf {res['conf']}, imgsz {res['imgsz']}, same-class greedy "
         "matching (score_v7_suite logic), all classes compared in the 7-class space. Decision rule: DECISION_RULE.md "
         "(written before training).", ""]
    if res.get("missing_models"):
        L += [f"**Not scored (weights missing): {', '.join(res['missing_models'])}.**", ""]
    L += ["## Control: does A reproduce its recorded numbers? (person, IoU 0.5)", "",
          "| set | recorded | measured | reproduced |", "|---|---|---|---|"]
    for s, v in res.get("control", {}).items():
        L.append(f"| {s} | {v['recorded'][0]}/{v['recorded'][1]} | {v['measured'][0]}/{v['measured'][1]} | "
                 f"{'yes' if v['reproduced'] else '**NO**'} |")
    L.append("")
    if not paired:
        L += ["**No comparison reported.**", ""]
        (OUT / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        return
    L += ["## Verdict (DECISION_RULE.md applied literally)", ""]
    for m, v in verdict.items():
        L.append(f"- **{m} vs A: {v}.**")
        for s in DECISION_SETS:
            c = paired.get(f"A|{m}|0.5|{s}|ALL")
            if c:
                L.append(f"  - {s}, IoU 0.5: {m}-only {c['b_only']} vs A-only {c['a_only']}, exact McNemar p = {c['mcnemar_p']:.4g}")
    e = res["empty_room"]
    L += ["- Empty-room frames with a person box: " + ", ".join(f"{m} {e[m]['fp_frames']}/{e[m]['frames']}" for m in ms), ""]
    for thr in IOUS:
        L += [f"## Person recall per set, IoU {thr}" + ("  (decision threshold)" if thr == 0.5 else "  (supplementary)"), "",
              "hits/N (recall) [Wilson 95% CI]; FP = person false positives on those frames.", "",
              "| set | N | " + " | ".join(ms) + " | " + " | ".join(f"FP {m}" for m in ms) + " |",
              "|---|---|" + "---|" * (2 * len(ms))]
        for s in SETS:
            cells, fps, n = [], [], 0
            for m in ms:
                st = res["stats"][m][s][str(thr)].get("person", {"tp": 0, "fp": 0, "fn": 0})
                n = st["tp"] + st["fn"]
                cells.append(fmt(st["tp"], n))
                fps.append(str(st["fp"]))
            note = " (new; C trained on this domain)" if s in SETS7 else ""
            L.append(f"| {s}{note} | {n} | " + " | ".join(cells) + " | " + " | ".join(fps) + " |")
        L.append("")
        L += [f"### Paired person comparisons, IoU {thr}", "",
              "| pair | set | clip | N | hits (first) | hits (second) | second-only | first-only | McNemar p |",
              "|---|---|---|---|---|---|---|---|---|"]
        for k in sorted((k for k in paired if f"|{thr}|" in k), key=lambda k: (k.split("|")[0], k.split("|")[1],
                                                                                 list(SETS).index(k.split("|")[3]),
                                                                                 k.split("|")[4] != "ALL", k)):
            a, b, _, s, g = k.split("|")
            v = paired[k]
            L.append(f"| {a} vs {b} | {s} | {'**all**' if g == 'ALL' else g} | {v['n']} | {v['a_hits']} | {v['b_hits']} | "
                     f"{v['b_only']} | {v['a_only']} | {v['mcnemar_p']:.4g} |")
        L.append("")
    L += ["## Empty-room false positives (yolo_testing/Reserved/Empty, every frame)", "",
          "| model | frames | frames with a person box | person boxes |", "|---|---|---|---|"]
    for m in ms:
        L.append(f"| {m} | {e[m]['frames']} | {e[m]['fp_frames']} | {e[m]['person_boxes']} |")
    L += ["", "## Other classes, IoU 0.5: recall tp/(tp+fn) and false positives (7-class space)", "",
          "| set | class | " + " | ".join(ms) + " |", "|---|---|" + "---|" * len(ms)]
    for s in SETS:
        if s == "cauca_s10":
            continue      # person-only ground truth
        for c in NAMES[1:]:
            cells, any_gt = [], False
            for m in ms:
                st = res["stats"][m][s]["0.5"].get(c, {"tp": 0, "fp": 0, "fn": 0})
                n = st["tp"] + st["fn"]
                any_gt |= n > 0
                cells.append(f"{st['tp']}/{n} (fp {st['fp']})")
            if any_gt:
                L.append(f"| {s} | {c} | " + " | ".join(cells) + " |")
    L += ["", "## Val metrics (not used for the decision; B and C have different val sets and classes from A)", ""]
    for m in ms:
        v = res["val"].get(m)
        if v:
            L.append(f"- {m}: best epoch {v['best_by_mAP50-95']['epoch']} (mAP50 {v['best_by_mAP50-95']['mAP50']}, "
                     f"mAP50-95 {v['best_by_mAP50-95']['mAP50-95']}); last epoch {v['last']['epoch']} of {v['epochs_logged']} logged")
    L.append("")
    (OUT / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

"""A5: score model A (v7) and A2 on the same sets in one session, apply DECISION_RULE.md literally.

Scoring logic is NOT rewritten:
  * official per-class tp/fp/fn come from src/detection/score_v7_suite.score_model (unchanged,
    imported), with its own settings CONF=0.4, IMGSZ=640;
  * per-box hit vectors (needed for McNemar) come from an instrumented copy of the SAME greedy
    loop; its tp/fp/fn are asserted equal to score_model's for every (model, set, IoU) or the
    run stops;
  * empty-room false positives come from src/detection/score_empty_false_positives.score_clip
    (unchanged, imported) over yolo_testing/Reserved/Empty, stride 1, same conf/imgsz.

Writes only under benchmarks/phase3_a2/: hits_A.csv, hits_A2.csv, a5_scores.json, RESULTS.md.
Never writes to results/, overnight_yolo26/, handlabels/, eval/ or any dataset.

Usage:  python score_A5.py            full run (needs runs/A2/weights/best.pt)
        python score_A5.py --dry-run  load ground truth + list sets/clips only (no model, no GPU)
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
OUT = ROOT / "benchmarks" / "phase3_a2"
sys.path.insert(0, str(ROOT))

import src.detection.score_v7_suite as suite  # noqa: E402  (unchanged scoring)
import src.detection.score_empty_false_positives as sef  # noqa: E402
from src.detection.footage_paths import RESERVED_EMPTY  # noqa: E402
from src.detection.score_heldout_objects import iou, load_ground_truth  # noqa: E402
from src.detection.sage_classes import SAGE_CLASSES  # noqa: E402

CONF, IMGSZ = suite.CONF, suite.IMGSZ
IOUS = (0.5, 0.3)
MODELS = {
    "A": ROOT / "models" / "yolov8n_sage_merged_v7.pt",
    "A2": OUT / "runs" / "A2" / "weights" / "best.pt",
}
SETS = {
    "heldout_objects": ROOT / "eval" / "heldout_objects",
    "reserved388_partial": ROOT / "benchmarks" / "overnight_yolo26" / "evalsets" / "held_out" / "reserved388_partial",
    "round6_heldout": ROOT / "handlabels" / "round6_heldout",
}
CONTROL = {"heldout_objects": (58, 93), "reserved388_partial": (107, 249), "round6_heldout": (50, 226)}
DECISION_SETS = ("round6_heldout", "reserved388_partial")
PROVISIONAL = ("**PROVISIONAL:** every score in this phase is provisional. The held-out labels follow no "
               "consistent written convention (spec: docs/LABELLING_SPEC.md, v0.1 draft).")


# ---------------------------------------------------------------- helpers
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
    """Two-sided exact McNemar: binomial(b+c, 0.5) on the discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def load_set(d):
    image_paths = sorted(p for p in (d / "images").iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    gt, unlabelled = load_ground_truth(d / "labels", image_paths)
    return gt, unlabelled


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


def gt_list(all_gt):
    return [(cls, tuple(box)) for cls, *box in all_gt if cls < len(SAGE_CLASSES)]


# ---------------------------------------------------------------- scoring
def score_one(model, name, set_name, gt):
    """Returns (official per-class stats by IoU, per-box rows, person FP per image by IoU)."""
    official = {thr: suite.score_model(model, gt, thr)[0] for thr in IOUS}
    rows, mine = [], {thr: defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}) for thr in IOUS}
    fp_person = {thr: defaultdict(int) for thr in IOUS}
    for image_path, all_gt in gt.items():
        boxes = gt_list(all_gt)
        preds = predict(model, image_path)
        hits = {}
        for thr in IOUS:
            st, h = match_with_hits(boxes, preds, thr)
            hits[thr] = h
            for c, v in st.items():
                for k in ("tp", "fp", "fn"):
                    mine[thr][c][k] += v[k]
            fp_person[thr][image_path.name] = st[0]["fp"] if 0 in st else 0
        for i, (cls, box) in enumerate(boxes):
            rows.append({"set": set_name, "image": image_path.name, "clip": clip_of(image_path.name),
                         "box_idx": i, "cls": cls, "x1": f"{box[0]:.6f}", "y1": f"{box[1]:.6f}",
                         "x2": f"{box[2]:.6f}", "y2": f"{box[3]:.6f}",
                         "hit_iou0.5": int(hits[0.5][i]), "hit_iou0.3": int(hits[0.3][i])})
    for thr in IOUS:
        for c in set(official[thr]) | set(mine[thr]):
            a = dict(official[thr].get(c, {"tp": 0, "fp": 0, "fn": 0}))
            b = dict(mine[thr].get(c, {"tp": 0, "fp": 0, "fn": 0}))
            if a != b:
                raise SystemExit(f"STOP: harness mismatch {name}/{set_name}/IoU{thr}/cls{c}: suite {a} vs instrumented {b}")
    return official, rows, fp_person


def empty_room(model):
    clips = sorted(p for p in RESERVED_EMPTY.rglob("*")
                   if p.suffix.lower() in sef.VIDEO_EXTENSIONS | sef.IMAGE_EXTENSIONS)
    out = {"dir": str(RESERVED_EMPTY), "conf": CONF, "imgsz": IMGSZ, "stride": 1, "clips": {}}
    tf = tfp = tb = 0
    for c in clips:
        n, fpf, boxes, other, worst = sef.score_clip(model, c, 1, CONF, IMGSZ)
        out["clips"][c.name] = {"frames": n, "fp_frames": fpf, "person_boxes": boxes}
        tf, tfp, tb = tf + n, tfp + fpf, tb + boxes
    out.update(frames=tf, fp_frames=tfp, person_boxes=tb)
    return out


def person_summary(rows, thr, subset=None):
    sel = [r for r in rows if r["cls"] == 0 and (subset is None or subset(r))]
    k = sum(r[f"hit_iou{thr}"] for r in sel)
    return k, len(sel)


def write_hits(name, rows):
    path = OUT / f"hits_{name}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def val_metrics():
    rc = OUT / "runs" / "A2" / "results.csv"
    if not rc.exists():
        return None
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(open(rc, encoding="utf-8"))]
    best = max(rows, key=lambda r: float(r["metrics/mAP50-95(B)"]))
    last = rows[-1]
    pick = lambda r: {"epoch": r["epoch"], "mAP50": r["metrics/mAP50(B)"], "mAP50-95": r["metrics/mAP50-95(B)"]}
    return {"epochs_logged": len(rows), "best_by_mAP50-95": pick(best), "last": pick(last)}


def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({k / n:.3f}) [{lo:.3f}, {hi:.3f}]" if n else "--"


# ---------------------------------------------------------------- main
def main():
    started = datetime.now().isoformat(timespec="seconds")
    gts = {}
    for s, d in SETS.items():
        gt, unl = load_set(d)
        gts[s] = gt
        n_person = sum(1 for v in gt.values() for b in v if b[0] == 0)
        print(f"{s}: {len(gt)} frames, {n_person} person boxes, {len(unl)} unlabelled excluded", flush=True)
    clips = sorted(p.name for p in RESERVED_EMPTY.rglob("*") if p.suffix.lower() in sef.VIDEO_EXTENSIONS | sef.IMAGE_EXTENSIONS)
    print(f"empty-room clips ({RESERVED_EMPTY}): {clips}", flush=True)
    if "--dry-run" in sys.argv:
        return 0

    from ultralytics import YOLO
    for name, p in MODELS.items():
        if not p.exists():
            raise SystemExit(f"STOP: {name} weights not found: {p}")

    results = {"started": started, "conf": CONF, "imgsz": IMGSZ, "models": {k: str(v) for k, v in MODELS.items()},
               "sets": {s: str(d) for s, d in SETS.items()}, "official": {}, "fp_person": {}, "empty_room": {}}
    rows_by_model = {}

    # Model A first: control gate.
    model_a = YOLO(str(MODELS["A"]))
    rows_by_model["A"] = []
    for s in SETS:
        off, rows, fpp = score_one(model_a, "A", s, gts[s])
        rows_by_model["A"] += rows
        results["official"].setdefault("A", {})[s] = {str(t): {int(c): v for c, v in off[t].items()} for t in IOUS}
        results["fp_person"].setdefault("A", {})[s] = {str(t): dict(fpp[t]) for t in IOUS}
    control = {}
    for s, (k_ref, n_ref) in CONTROL.items():
        k, n = person_summary([r for r in rows_by_model["A"] if r["set"] == s], 0.5)
        control[s] = {"measured": [k, n], "recorded": [k_ref, n_ref], "reproduced": (k, n) == (k_ref, n_ref)}
    results["control"] = control
    write_hits("A", rows_by_model["A"])
    if not all(v["reproduced"] for v in control.values()):
        results["verdict"] = "CONTROL FAILED: no A2 comparison reported"
        (OUT / "a5_scores.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        write_results_md(results, None, None)
        print("CONTROL FAILED", json.dumps(control), flush=True)
        return 1

    model_a2 = YOLO(str(MODELS["A2"]))
    rows_by_model["A2"] = []
    for s in SETS:
        off, rows, fpp = score_one(model_a2, "A2", s, gts[s])
        rows_by_model["A2"] += rows
        results["official"].setdefault("A2", {})[s] = {str(t): {int(c): v for c, v in off[t].items()} for t in IOUS}
        results["fp_person"].setdefault("A2", {})[s] = {str(t): dict(fpp[t]) for t in IOUS}
    write_hits("A2", rows_by_model["A2"])

    for name, m in (("A", model_a), ("A2", model_a2)):
        print(f"empty-room {name} ...", flush=True)
        results["empty_room"][name] = empty_room(m)

    # paired comparison
    key = lambda r: (r["set"], r["image"], r["box_idx"])
    a_idx = {key(r): r for r in rows_by_model["A"] if r["cls"] == 0}
    b_idx = {key(r): r for r in rows_by_model["A2"] if r["cls"] == 0}
    assert set(a_idx) == set(b_idx), "per-box keys differ between A and A2"
    paired = {}
    for thr in IOUS:
        for s in SETS:
            groups = {"ALL": [k for k in a_idx if k[0] == s]}
            for k in groups["ALL"]:
                groups.setdefault(a_idx[k]["clip"], []).append(k)
            for g, ks in groups.items():
                ka = sum(a_idx[k][f"hit_iou{thr}"] for k in ks)
                kb = sum(b_idx[k][f"hit_iou{thr}"] for k in ks)
                only_a2 = sum(1 for k in ks if b_idx[k][f"hit_iou{thr}"] and not a_idx[k][f"hit_iou{thr}"])
                only_a = sum(1 for k in ks if a_idx[k][f"hit_iou{thr}"] and not b_idx[k][f"hit_iou{thr}"])
                imgs = {k[1] for k in ks}
                fpa = sum(results["fp_person"]["A"][s][str(thr)].get(i, 0) for i in imgs)
                fpb = sum(results["fp_person"]["A2"][s][str(thr)].get(i, 0) for i in imgs)
                paired[f"{thr}|{s}|{g}"] = {"n": len(ks), "A_hits": ka, "A2_hits": kb, "A2_only": only_a2,
                                            "A_only": only_a, "mcnemar_p": mcnemar_exact(only_a2, only_a),
                                            "A_fp_person": fpa, "A2_fp_person": fpb,
                                            "A_wilson": wilson(ka, len(ks)), "A2_wilson": wilson(kb, len(ks))}
    results["paired"] = paired
    results["val_A2"] = val_metrics()

    # verdict, applied literally
    checks = {s: paired[f"0.5|{s}|ALL"] for s in DECISION_SETS}
    better = all(c["mcnemar_p"] < 0.05 and c["A2_only"] > c["A_only"] for c in checks.values())
    results["verdict"] = "A2 is clearly better than A" if better else "no clear difference"
    results["finished"] = datetime.now().isoformat(timespec="seconds")
    (OUT / "a5_scores.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_results_md(results, paired, checks)
    print("VERDICT:", results["verdict"], flush=True)
    return 0


def write_results_md(res, paired, checks):
    L = ["# A5 RESULTS: A (v7) vs A2", "", PROVISIONAL, "",
         f"Scored {res['started']} to {res.get('finished', '?')}. conf {res['conf']}, imgsz {res['imgsz']}, "
         "person class, same-class greedy matching (src/detection/score_v7_suite.py, unchanged). "
         "Decision rule: DECISION_RULE.md (written before scoring).", "",
         "## Control: does A reproduce its recorded numbers? (person, IoU 0.5)", "",
         "| set | recorded | measured | reproduced |", "|---|---|---|---|"]
    for s, v in res["control"].items():
        L.append(f"| {s} | {v['recorded'][0]}/{v['recorded'][1]} | {v['measured'][0]}/{v['measured'][1]} | "
                 f"{'yes' if v['reproduced'] else '**NO**'} |")
    L.append("")
    if paired is None:
        L += ["**Control failed. Per the phase-3 prompt, no A2 comparison is reported.**", ""]
        (OUT / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        return
    for thr in IOUS:
        L += [f"## Person hits per set and clip, IoU {thr}" + ("  (decision threshold)" if thr == 0.5 else "  (supplementary)"),
              "", "hits/N (recall) [Wilson 95% CI]. McNemar = exact two-sided test on boxes hit by only one model. "
              "FP = person false positives on those frames.", "",
              "| set | clip | N | A | A2 | A2-only | A-only | McNemar p | FP A | FP A2 |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for s in SETS:
            ks = sorted((k for k in paired if k.startswith(f"{thr}|{s}|")), key=lambda k: (k.split("|")[2] != "ALL", k))
            for k in ks:
                v = paired[k]
                g = k.split("|")[2]
                L.append(f"| {s} | {'**all**' if g == 'ALL' else g} | {v['n']} | {fmt(v['A_hits'], v['n'])} | "
                         f"{fmt(v['A2_hits'], v['n'])} | {v['A2_only']} | {v['A_only']} | {v['mcnemar_p']:.4g} | "
                         f"{v['A_fp_person']} | {v['A2_fp_person']} |")
        L.append("")
    L += ["## Empty-room false positives (yolo_testing/Reserved/Empty, every frame)", "",
          "| model | frames | frames with a person box | person boxes |", "|---|---|---|---|"]
    for m, e in res["empty_room"].items():
        L.append(f"| {m} | {e['frames']} | {e['fp_frames']} | {e['person_boxes']} |")
    L.append("")
    L += ["## Other classes (official score_v7_suite output, IoU 0.5): recall tp/(tp+fn)", "",
          "| set | class | A | A2 |", "|---|---|---|---|"]
    for s in SETS:
        oa, ob = res["official"]["A"][s]["0.5"], res["official"]["A2"][s]["0.5"]
        for c in sorted(set(oa) | set(ob), key=int):
            if int(c) == 0:
                continue
            ga, gb = oa.get(c, {"tp": 0, "fp": 0, "fn": 0}), ob.get(c, {"tp": 0, "fp": 0, "fn": 0})
            na, nb = ga["tp"] + ga["fn"], gb["tp"] + gb["fn"]
            L.append(f"| {s} | {SAGE_CLASSES[int(c)]} | {ga['tp']}/{na} (fp {ga['fp']}) | {gb['tp']}/{nb} (fp {gb['fp']}) |")
    L.append("")
    v = res.get("val_A2")
    L += ["## A2 val metrics (not used for the decision)", ""]
    if v:
        L += [f"- best epoch by mAP50-95: epoch {v['best_by_mAP50-95']['epoch']}: mAP50 {v['best_by_mAP50-95']['mAP50']}, "
              f"mAP50-95 {v['best_by_mAP50-95']['mAP50-95']}",
              f"- last epoch ({v['epochs_logged']} logged): epoch {v['last']['epoch']}: mAP50 {v['last']['mAP50']}, "
              f"mAP50-95 {v['last']['mAP50-95']}", ""]
    else:
        L += ["UNKNOWN: runs/A2/results.csv not found.", ""]
    L += ["## Verdict (DECISION_RULE.md applied literally)", ""]
    for s, c in checks.items():
        L.append(f"- {s}, IoU 0.5: A2-only {c['A2_only']} vs A-only {c['A_only']}, exact McNemar p = {c['mcnemar_p']:.4g} "
                 f"-> {'meets' if (c['mcnemar_p'] < 0.05 and c['A2_only'] > c['A_only']) else 'does not meet'} the bar")
    e = res["empty_room"]
    L += [f"- empty-room FP frames: A {e['A']['fp_frames']}/{e['A']['frames']}, A2 {e['A2']['fp_frames']}/{e['A2']['frames']}",
          "", f"**Verdict: {res['verdict']}.**", ""]
    (OUT / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

"""Phase 6 scoring: A (control), C (baseline) and every finished phase-6 run, same harness as phase 5.

Reuses benchmarks/phase5_v8/score_v8.py unchanged (prediction, matching, McNemar, empty room). Each model is scored
once and cached (cache/<M>.json, hits_<M>.csv, preds_<M>.json); a run counts as finished only when the supervisor
wrote DONE_<M>. Applies DECISION_RULE.md: each run vs C (person, round6_heldout + reserved388_partial), the D bed
question, and secondary comparisons. Writes p6_scores.json and RESULTS.md. Run with cwd = phase6_sweep.
"""
import csv
import json
import statistics as stt
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase6_sweep"
P5 = ROOT / "benchmarks" / "phase5_v8"
sys.path.insert(0, str(P5))
sys.dont_write_bytecode = True
import score_v8 as sv  # noqa: E402

ORDER = ["A", "C", "D", "LR2", "B8", "COS", "DCOS", "B32", "LRH"]
DESC = {"A": "v7 (13 classes, old data)", "C": "baseline: lr 0.000588, linear, batch 16",
        "LR2": "learning rate x2 (0.001176)", "LRH": "learning rate x0.5 (0.000294)",
        "COS": "cosine LR schedule", "B32": "batch 32", "B8": "batch 8", "D": "C + 4 clips re-added (filtered)",
        "DCOS": "D data + cosine schedule (exploratory, chosen after results)"}
CACHE = OUT / "cache"


def weights(m):
    if m == "A":
        return sv.MODELS["A"]
    if m == "C":
        return P5 / "runs" / "C" / "weights" / "best.pt"
    p = OUT / "runs" / m / "weights" / "best.pt"
    return p if (OUT / f"DONE_{m}").exists() and p.exists() else None


def results_csv(m):
    return (P5 if m == "C" else OUT) / "runs" / m / "results.csv"


def val_metrics(m):
    rc = results_csv(m)
    if m == "A" or not rc.exists():
        return None
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(open(rc, encoding="utf-8"))]
    fit = lambda r: 0.1 * float(r["metrics/mAP50(B)"]) + 0.9 * float(r["metrics/mAP50-95(B)"])  # ultralytics best.pt
    best = max(rows, key=fit)
    return {"epochs_logged": len(rows), "best_epoch": int(float(best["epoch"])), "mAP50": float(best["metrics/mAP50(B)"]),
            "mAP50-95": float(best["metrics/mAP50-95(B)"])}


def score_one(m, gts):
    from ultralytics import YOLO
    model = YOLO(str(weights(m)))
    st, rows, fpp, raw = sv.score_model(m, model, gts)
    with open(OUT / f"hits_{m}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (OUT / f"preds_{m}.json").write_text(json.dumps(raw), encoding="utf-8")
    print(f"empty-room {m} ...", flush=True)
    er = sv.empty_room(model)
    c = {"weights": str(weights(m)), "scored": datetime.now().isoformat(timespec="seconds"),
         "stats": {s: {str(t): {sv.NAMES[k]: v for k, v in st[s][t].items()} for t in sv.IOUS} for s in st},
         "fp_person": {s: {str(t): fpp[s][t] for t in sv.IOUS} for s in fpp},
         "empty_room": {k: er[k] for k in ("frames", "fp_frames", "person_boxes")}}
    (CACHE / f"{m}.json").write_text(json.dumps(c), encoding="utf-8")


def load_hits(m):
    rows = list(csv.DictReader(open(OUT / f"hits_{m}.csv", encoding="utf-8")))
    for r in rows:
        r["cls"] = int(r["cls"])
        r["hit_iou0.5"], r["hit_iou0.3"] = int(r["hit_iou0.5"]), int(r["hit_iou0.3"])
    return rows


def paired(ia, ib, s, thr, cls=0):
    ks = [k for k, r in ia.items() if k[0] == s and r["cls"] == cls]
    h = f"hit_iou{thr}"
    ob = sum(1 for k in ks if ib[k][h] and not ia[k][h])
    oa = sum(1 for k in ks if ia[k][h] and not ib[k][h])
    return {"n": len(ks), "a_hits": sum(ia[k][h] for k in ks), "b_hits": sum(ib[k][h] for k in ks),
            "b_only": ob, "a_only": oa, "mcnemar_p": sv.mcnemar_exact(ob, oa)}


def verdict(pp, ref, m):
    ch = [pp[s] for s in sv.DECISION_SETS]
    if all(c["mcnemar_p"] < 0.05 and c["b_only"] > c["a_only"] for c in ch):
        return f"{m} is clearly better than {ref}"
    if all(c["mcnemar_p"] < 0.05 and c["a_only"] > c["b_only"] for c in ch):
        return f"{m} is clearly worse than {ref}"
    return "no clear difference"


def box_fit(m, gt7):
    """Phase-5 box_fit method on own footage (reserved388_partial + round6_heldout, de-duplicated)."""
    preds = json.loads((OUT / f"preds_{m}.json").read_text(encoding="utf-8"))
    seen, cov, ext, n_gt = set(), [], [], 0
    for s in ("reserved388_partial", "round6_heldout"):
        for image, pl in sorted(preds[s].items()):
            if image in seen:
                continue
            seen.add(image)
            pp = [p[2:] for p in pl if p[1] == 0 and p[0] >= 0.4]
            for g in gt7[s].get(image, []):
                n_gt += 1
                best = None
                for p in pp:
                    ix = max(0, min(g[2], p[2]) - max(g[0], p[0]))
                    iy = max(0, min(g[3], p[3]) - max(g[1], p[1]))
                    inter = ix * iy
                    ag, ap = (g[2] - g[0]) * (g[3] - g[1]), (p[2] - p[0]) * (p[3] - p[1])
                    i = inter / (ag + ap - inter + 1e-12)
                    if best is None or i > best[0]:
                        best = (i, inter / ag, (ap - inter) / ag)
                if best and best[0] >= 0.3:
                    cov.append(best[1])
                    ext.append(best[2])
    if not cov:
        return None
    return {"people": n_gt, "matched": len(cov), "median_cov": stt.median(cov),
            "good": sum(c >= 0.9 and e <= 0.25 for c, e in zip(cov, ext)),
            "tight": sum(c < 0.9 for c in cov), "loose": sum(e > 0.25 for e in ext),
            "very_loose": sum(e > 1.0 for e in ext)}


def main():
    CACHE.mkdir(exist_ok=True)
    gts, gt7 = {}, {}
    for s, d in sv.SETS.items():
        gts[s], _ = sv.load_set(d)
        gt7[s] = {p.name: [tuple(b) for c, b in sv.to7_gt(v, s in sv.SETS13) if c == 0] for p, v in gts[s].items()}
    ms = [m for m in ORDER if weights(m) is not None]
    for m in ms:
        if not (CACHE / f"{m}.json").exists() or json.loads((CACHE / f"{m}.json").read_text())["weights"] != str(weights(m)):
            print(f"scoring {m} ...", flush=True)
            score_one(m, gts)
    cache = {m: json.loads((CACHE / f"{m}.json").read_text(encoding="utf-8")) for m in ms}
    hits = {m: {(r["set"], r["image"], r["box_idx"]): r for r in load_hits(m)} for m in ms}

    control = {}
    for s, (kr, nr) in sv.CONTROL.items():
        sel = [r for r in hits["A"].values() if r["set"] == s and r["cls"] == 0]
        k = sum(r["hit_iou0.5"] for r in sel)
        control[s] = {"measured": [k, len(sel)], "recorded": [kr, nr], "reproduced": (k, len(sel)) == (kr, nr)}
    res = {"generated": datetime.now().isoformat(timespec="seconds"), "models": ms, "desc": DESC, "control": control,
           "cache": cache, "val": {m: val_metrics(m) for m in ms}, "paired": {}, "verdict_vs_C": {}, "verdict_vs_A": {},
           "box_fit": {m: box_fit(m, gt7) for m in ms}}
    ok = all(v["reproduced"] for v in control.values())
    if ok:
        for m in ms:
            for ref in ("A", "C"):
                if m == ref or (ref == "C" and m == "A"):
                    continue
                pp = {f"{s}|{t}": paired(hits[ref], hits[m], s, t) for s in sv.SETS for t in sv.IOUS}
                res["paired"][f"{ref}|{m}"] = pp
                (res["verdict_vs_C"] if ref == "C" else res["verdict_vs_A"])[m] = verdict(
                    {s: pp[f"{s}|0.5"] for s in sv.SETS}, ref, m)
        if "D" in ms:
            res["D_bed"] = {s: paired(hits["C"], hits["D"], s, 0.5, cls=1)
                            for s in ("reserved388_partial", "heldout_objects", "round6_heldout")}
            b = res["D_bed"]["reserved388_partial"]
            res["D_bed_answer"] = ("fixed" if b["mcnemar_p"] < 0.05 and b["b_only"] > b["a_only"] else "not shown fixed")
    (OUT / "p6_scores.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    write_md(res, ok)
    print("vs C:", res["verdict_vs_C"], "| D bed:", res.get("D_bed_answer"), flush=True)
    return 0 if ok else 1


def write_md(res, ok):
    ms, cache = res["models"], res["cache"]
    L = ["# Phase 6 RESULTS (updated after every finished run)", "", sv.PROVISIONAL, "",
         f"Generated {res['generated']}. Same harness as phase 5 (conf 0.4, imgsz 640, greedy same-class matching, "
         "exact McNemar). Rule: DECISION_RULE.md (written before training). Baseline = C.", "",
         "| model | what changed |", "|---|---|"] + [f"| {m} | {res['desc'][m]} |" for m in ms]
    L += ["", "## Control (A, person, IoU 0.5)", "", "| set | recorded | measured | ok |", "|---|---|---|---|"]
    for s, v in res["control"].items():
        L.append(f"| {s} | {v['recorded'][0]}/{v['recorded'][1]} | {v['measured'][0]}/{v['measured'][1]} | "
                 f"{'yes' if v['reproduced'] else '**NO**'} |")
    if not ok:
        L += ["", "**CONTROL FAILED: no comparison reported.**"]
        (OUT / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        return
    L += ["", "## Verdicts (person, IoU 0.5, round6_heldout + reserved388_partial)", ""]
    for m in ms:
        if m in ("A", "C"):
            continue
        pc = res["paired"][f"C|{m}"]
        L.append(f"- **{m} ({res['desc'][m]}) vs C: {res['verdict_vs_C'][m]}.** " + "; ".join(
            f"{s}: {m}-only {pc[s + '|0.5']['b_only']} vs C-only {pc[s + '|0.5']['a_only']}, p = {pc[s + '|0.5']['mcnemar_p']:.3g}"
            for s in sv.DECISION_SETS) + f". vs A: {res['verdict_vs_A'][m]}.")
    if "D_bed" in res:
        b = res["D_bed"]
        L += ["", f"**D bed question: {res['D_bed_answer']}.** Per-box bed hits C vs D (IoU 0.5): " + "; ".join(
            f"{s}: C {v['a_hits']}/{v['n']}, D {v['b_hits']}/{v['n']}, D-only {v['b_only']} vs C-only {v['a_only']}, "
            f"p = {v['mcnemar_p']:.3g}" for s, v in b.items())]
    for thr in sv.IOUS:
        L += ["", f"## Person recall, IoU {thr}" + (" (decision threshold)" if thr == 0.5 else " (supplementary)"), "",
              "| set | N | " + " | ".join(ms) + " |", "|---|---|" + "---|" * len(ms)]
        for s in sv.SETS:
            cells, n = [], 0
            for m in ms:
                st = cache[m]["stats"][s][str(thr)].get("person", {"tp": 0, "fn": 0, "fp": 0})
                n = st["tp"] + st["fn"]
                cells.append(f"{st['tp']} (fp {st['fp']})")
            L.append(f"| {s} | {n} | " + " | ".join(cells) + " |")
        L += ["", f"Paired vs C, IoU {thr} (run-only / C-only, exact McNemar p):", "",
              "| set | " + " | ".join(m for m in ms if m not in ("A", "C")) + " | A |", "|---|" + "---|" * (len(ms) - 1)]
        for s in sv.SETS:
            row = []
            for m in [m for m in ms if m not in ("A", "C")] + ["A"]:
                v = res["paired"][f"C|{m}"][f"{s}|{thr}"] if m != "A" else None
                if m == "A":
                    v = res["paired"]["A|C"][f"{s}|{thr}"] if "A|C" in res["paired"] else None
                    row.append(f"C-only {v['b_only']} / A-only {v['a_only']}, p {v['mcnemar_p']:.3g}" if v else "--")
                else:
                    row.append(f"{v['b_only']} / {v['a_only']}, p {v['mcnemar_p']:.3g}")
            L.append(f"| {s} | " + " | ".join(row) + " |")
    L += ["", "## Empty-room person false positives (4,101 frames)", "", "| model | frames with a person box | boxes |",
          "|---|---|---|"] + [f"| {m} | {cache[m]['empty_room']['fp_frames']}/{cache[m]['empty_room']['frames']} | "
                              f"{cache[m]['empty_room']['person_boxes']} |" for m in ms]
    L += ["", "## Other classes, IoU 0.5 (tp/N, fp)", "", "| set | class | " + " | ".join(ms) + " |",
          "|---|---|" + "---|" * len(ms)]
    for s in sv.SETS:
        if s == "cauca_s10":
            continue
        for c in sv.NAMES[1:]:
            cells, any_gt = [], False
            for m in ms:
                st = cache[m]["stats"][s]["0.5"].get(c, {"tp": 0, "fp": 0, "fn": 0})
                n = st["tp"] + st["fn"]
                any_gt |= n > 0
                cells.append(f"{st['tp']}/{n} (fp {st['fp']})")
            if any_gt:
                L.append(f"| {s} | {c} | " + " | ".join(cells) + " |")
    L += ["", "## Person box fit on own footage (phase-5 box_fit method; 475 labelled people)", "",
          "| model | matched | median coverage | good | tight (<90% covered) | loose (>25% extra) | very loose (>2x) |",
          "|---|---|---|---|---|---|---|"]
    for m in ms:
        b = res["box_fit"][m]
        if b:
            L.append(f"| {m} | {b['matched']} | {b['median_cov']:.0%} | {b['good']} | {b['tight']} | {b['loose']} | {b['very_loose']} |")
    L += ["", "## Val metrics (same val set for C and every phase-6 run; best.pt epoch)", "",
          "| model | best epoch | epochs run | mAP50 | mAP50-95 |", "|---|---|---|---|---|"]
    for m in ms:
        v = res["val"][m]
        if v:
            L.append(f"| {m} | {v['best_epoch']} | {v['epochs_logged']} | {v['mAP50']:.3f} | {v['mAP50-95']:.3f} |")
    (OUT / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

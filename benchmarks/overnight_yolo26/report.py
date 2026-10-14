"""Builds RESULTS.md purely from files the stage scripts wrote (raw/, state.json, runs/). Tolerates missing
inputs: anything absent is reported as MISSING/FAILED/SKIPPED, never filled in."""
import csv
import datetime as dt
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, RAW, RUNS, ROOT, read_json, write_json, wilson, run_start, now, STOCK

SETS = ["heldout_objects", "heldout_objects_rotfix", "reserved388_partial", "round6_heldout"]
SET_NOTE = {
    "heldout_objects": "eval/heldout_objects as stored (Bedroom_Fall frames sideways)",
    "heldout_objects_rotfix": "same frames, Bedroom_Fall rotated upright (OUT copy)",
    "reserved388_partial": "388-box labels, 7/11 clips with obtainable images",
    "round6_heldout": "handlabels/round6_heldout (Laying_Dim_HM + Behind_Bed_HM)",
}
L = []          # report lines
SUMMARY = []    # lead summary lines (<=12)
CHECK = []      # things to double-check by hand


def P(*a):
    L.append(" ".join(str(x) for x in a))


def pct(x, nd=3):
    return "--" if x is None else f"{x:.{nd}f}"


def ci(tp, n):
    lo, hi = wilson(tp, n)
    return "--" if lo is None else f"[{lo:.2f}, {hi:.2f}]"


# ------------------------------------------------------------------------------------------
def load_scores():
    """-> {(model, conf): {set: score_entry}}, empty FP {(model, conf): entry}"""
    sc, efp = {}, {}
    s1 = read_json(RAW / "stage1_control.json", {})
    for k, v in s1.get("scores", {}).items():
        m, s = k.split("|")
        sc.setdefault((m, 0.4), {})[s] = v
    for m in ("A_v7", "v6"):
        if f"empty_fp|{m}" in s1:
            efp[(m, 0.4)] = s1[f"empty_fp|{m}"]
    for f in RAW.glob("scores__*.json"):
        d = read_json(f, {})
        m = d.get("model")
        for k, v in d.get("scores", {}).items():
            s, c = k.split("|c")
            sc.setdefault((m, float(c)), {})[s] = v
        for k, v in d.get("empty_fp", {}).items():
            efp[(m, float(k[1:]))] = v
    return sc, efp


def person(entry, thr):
    try:
        return entry["by_iou"][thr]["person"]
    except Exception:
        return None


# ------------------------------------------------------------------------------------------
def sec_status(state):
    P("## 1. What finished / failed / skipped")
    P("")
    P("| stage | status | start | end | wall min | note |")
    P("|---|---|---|---|---|---|")
    for k, v in state.get("stages", {}).items():
        s, e = v.get("start"), v.get("end")
        mins = ""
        if s and e:
            mins = f"{(dt.datetime.fromisoformat(e) - dt.datetime.fromisoformat(s)).total_seconds() / 60:.1f}"
        P(f"| {k} | {v.get('status')} | {(s or '')[11:19]} | {(e or '')[11:19]} | {mins} | {v.get('note', '')} |")
    P("")
    if state.get("driver_error"):
        P("**Driver error (traceback tail):**")
        P("```")
        P(state["driver_error"])
        P("```")
    for k, v in state.get("stages", {}).items():
        if v.get("status") in ("failed", "timeout") and v.get("log_tail"):
            P(f"**{k} {v['status'].upper()}** -- log tail:")
            P("```")
            P("\n".join(v["log_tail"][-15:]))
            P("```")
    P(f"Driver launches: {', '.join(state.get('driver_launches', []))}. Run start {run_start():%Y-%m-%d %H:%M}; "
      f"report generated {now():%Y-%m-%d %H:%M} ({(now() - run_start()).total_seconds() / 3600:.2f} h after start).")
    P("")


def sec_control(s1):
    P("## 2. Control reproduction (A = models/yolov8n_sage_merged_v7.pt, conf 0.4, imgsz 640)")
    P("")
    if not s1:
        P("**FAILED/MISSING: raw/stage1_control.json not found.**")
        SUMMARY.append("Control reproduction: MISSING (stage 1 produced no output).")
        return
    rep = s1.get("control_reproduced")
    if rep is False:
        P("### **CONTROL NOT REPRODUCED** -- see the failing rows below; both values are shown and neither is treated as truth.")
    elif rep:
        P("**Control reproduced**: every reference value for A matched within 1 person box and 0.02 recall.")
    P("")
    P("| check | measured | reference | ok |")
    P("|---|---|---|---|")
    for c in s1.get("checks", []):
        P(f"| {c['check']} | {c.get('measured')}{' (' + c['measured_counts'] + ')' if c.get('measured_counts') else ''}"
          f"{' FP ' + str(c['measured_fp']) if 'measured_fp' in c else ''} | {c.get('reference')} | "
          f"{'n/a' if c.get('ok') is None else ('yes' if c['ok'] else '**NO**')} |")
    P("")
    he = s1.get("harness_equality", {})
    if "identical" in he:
        P(f"Harness equality check (A, eval/heldout_objects, person, IoU 0.5): original `score_loaded_model` "
          f"{he['original_score_loaded_model']} vs this harness {he['this_harness']} -> "
          f"{'IDENTICAL' if he['identical'] else '**DIFFERENT**'}.")
    elif he:
        P(f"Harness equality check: FAILED {he.get('FAILED')}")
    else:
        P("Harness equality check: not run (stage 1 incomplete).")
    P("")
    pf = read_json(RAW / "preflight.json", {})
    ev = pf.get("evalsets", {})
    if ev.get("clips_saved_unrotated"):
        P(f"**Measurement artifact found in eval/heldout_objects:** clip(s) {ev['clips_saved_unrotated']} are stored as the raw, "
          "unrotated (sideways) frame while their hand-drawn labels fit the upright frame (registered rotation in "
          "src/detection/footage_rotation.py). The long-standing reference 'Bedroom_Fall 0/20 for v5, v6, v7' therefore "
          "measures a sideways image against upright boxes, not the model. The `heldout_objects_rotfix` set below is the "
          "same 200 frames with only those images rotated; the as-stored set is kept so the reference can be reproduced.")
        CHECK.append("Eyeball OUT/evalsets/held_out/heldout_objects_rotfix/images/With_people_Bedroom_Fall_*.jpg against their labels "
                     "(the rotation fix rests on one rendered frame + the registered rotation).")
        P("")
    r = ev.get("reserved388_partial", {})
    if r:
        P(f"**388-box reserved set**: labels found (eval/heldout_objects/labels, 569 files, 388 person boxes), images for only "
          f"{r.get('frames')} frames / {r.get('person_boxes')} person boxes obtainable. Missing source clips: "
          f"{', '.join(c for c in r.get('clips_missing_source', []) if c.startswith('With'))}. Re-extraction check vs the "
          f"existing images: n={r['reextraction_check_vs_existing_images']['n']}, max mean |diff| = "
          f"{pct(r['reextraction_check_vs_existing_images']['max_mean_abs_diff'], 2)} grey levels. "
          f"v6 per-clip reproduction on the partial set: {({True: 'OK', False: '**NOT REPRODUCED**'}).get(s1.get('partial388_v6_reproduced'), 'not evaluated (stage 1 incomplete)')} "
          "(rows 'v6 reserved388 ...' above). The full-set reference (v6 0.577 @0.5 / 0.585 @0.3 on 388 boxes) cannot be checked.")
        P("")
    av = s1.get("A_val", {})
    if "mAP50" in av:
        P(f"A re-validated now on OUT/data_v7_fixed.yaml (2,610 val images): mAP50 {av['mAP50']:.4f}, mAP50-95 {av['mAP50_95']:.4f}.")
    for n in s1.get("notes", []):
        P(f"- {n}")
    P("")
    bad = [c for c in s1.get("checks", []) if c.get("ok") is False]
    if rep is None:
        SUMMARY.append("Control A: reproduction check not evaluated (stage 1 incomplete).")
    else:
        SUMMARY.append(("Control A: **CONTROL NOT REPRODUCED** on " + "; ".join(f"{c['check']} (measured {c['measured']} vs ref {c['reference']})" for c in bad if c['check'].startswith('A ')))
                       if rep is False else "Control A reproduced on every reference value (eval/heldout_objects 58/93 1 FP; round6_heldout chair/bed/person; empty-room 0/4101).")


def person_table(sc, efp):
    P("## 3. Person detection (conf 0.4 unless stated, imgsz 640; TP/FP/FN, recall with 95% Wilson CI)")
    P("")
    P("Every number below is tied to its eval set; do not compare across sets. Frames within a clip are correlated, so "
      "the Wilson intervals (which assume independent boxes) are if anything too narrow. With 93-249 boxes per set, "
      "recall differences under roughly 0.08-0.10 are not distinguishable from noise.")
    P("")
    order = [("A_v7", 0.4), ("v6", 0.4), ("B_yolo26n_30ep", 0.4), ("C_yolo26n_50ep", 0.4),
             ("stock_yolo26n", 0.4), ("stock_yolo26s", 0.4), ("stock_yolov8n", 0.4),
             ("stock_yolo26n", 0.25), ("stock_yolo26s", 0.25), ("stock_yolov8n", 0.25)]
    rows_csv = []
    for s in SETS:
        P(f"### {s} -- {SET_NOTE[s]}")
        P("")
        P("| model | conf | IoU | TP | FP | FN | recall | 95% CI | precision | Δrecall vs A |")
        P("|---|---|---|---|---|---|---|---|---|---|")
        for thr in ("0.5", "0.3"):
            a = person(sc.get(("A_v7", 0.4), {}).get(s, {}), thr)
            for m, c in order:
                e = sc.get((m, c), {}).get(s)
                if e is None:
                    continue
                if "FAILED" in e:
                    P(f"| {m} | {c} | {thr} | FAILED | | | | | | |")
                    continue
                p = person(e, thr)
                d = "" if (a is None or m == "A_v7") else f"{p['recall'] - a['recall']:+.3f}"
                P(f"| {m} | {c} | {thr} | {p['tp']} | {p['fp']} | {p['fn']} | {pct(p['recall'])} | {ci(p['tp'], p['n_gt'])} | {pct(p['precision'])} | {d} |")
                rows_csv.append({"set": s, "model": m, "conf": c, "iou": thr, **{k: p[k] for k in ("tp", "fp", "fn", "n_gt", "recall", "precision")}})
        P("")
    # empty-room
    P("### Empty-room person false positives (yolo_testing/Reserved/Empty, every frame, stride 1)")
    P("")
    P("| model | conf | frames | FP frames | FP rate | person boxes |")
    P("|---|---|---|---|---|---|")
    for m, c in order:
        e = efp.get((m, c))
        if e is None:
            continue
        if "FAILED" in e:
            P(f"| {m} | {c} | FAILED | | | |")
            continue
        P(f"| {m} | {c} | {e['frames']} | {e['fp_frames']} | {e['fp_rate_pct']:.2f}% | {e['person_boxes']} |")
        rows_csv.append({"set": "reserved_empty", "model": m, "conf": c, "iou": "", "tp": "", "fp": e["fp_frames"], "fn": "",
                         "n_gt": e["frames"], "recall": "", "precision": ""})
    P("")
    with open(RAW / "person_detection_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["set", "model", "conf", "iou", "tp", "fp", "fn", "n_gt", "recall", "precision"])
        w.writeheader()
        w.writerows(rows_csv)
    # per-clip
    P("### Per-clip person recall, IoU 0.5, conf 0.4 (TP/boxes, FP)")
    P("")
    models = [m for m in ("A_v7", "v6", "B_yolo26n_30ep", "C_yolo26n_50ep", "stock_yolo26n") if sc.get((m, 0.4))]
    for s in ("heldout_objects_rotfix", "reserved388_partial", "round6_heldout", "heldout_objects"):
        clips = set()
        for m in models:
            e = sc[(m, 0.4)].get(s)
            if e and "by_iou" in e:
                clips |= {c for c, v in e["by_iou"]["0.5"]["per_clip_person"].items() if v["n_gt"] or v["fp"]}
        if not clips:
            continue
        P(f"**{s}**")
        P("")
        P("| clip | " + " | ".join(models) + " |")
        P("|---|" + "---|" * len(models))
        for clip in sorted(clips):
            cells = []
            for m in models:
                e = sc[(m, 0.4)].get(s)
                v = e["by_iou"]["0.5"]["per_clip_person"].get(clip) if e and "by_iou" in e else None
                cells.append("--" if v is None else f"{v['tp']}/{v['n_gt']}, {v['fp']}FP")
            P(f"| {clip} | " + " | ".join(cells) + " |")
        P("")
    # other classes on round6_heldout
    P("### Other classes on round6_heldout (SAGE models only; stock COCO models are scored on person only)")
    P("")
    P("| model | IoU | class | TP | FP | FN | recall | precision |")
    P("|---|---|---|---|---|---|---|---|")
    for m in ("A_v7", "v6", "B_yolo26n_30ep", "C_yolo26n_50ep"):
        e = sc.get((m, 0.4), {}).get("round6_heldout")
        if not e or "by_iou" not in e:
            continue
        for thr in ("0.5", "0.3"):
            for cls, v in e["by_iou"][thr]["per_class"].items():
                if cls == "person" or v["n_gt"] == 0 and v["fp"] == 0:
                    continue
                P(f"| {m} | {thr} | {cls} | {v['tp']} | {v['fp']} | {v['fn']} | {pct(v['recall'])} | {pct(v['precision'])} |")
    P("")


def per_box_overlap(sc):
    """Which person boxes does each model miss? Uses the cached predictions + the same matching."""
    import score_lib as S
    out = {}
    for s in ("reserved388_partial", "round6_heldout", "heldout_objects_rotfix"):
        gt, _ = S.load_set(s)
        lt = read_json(RAW / "luma_thresholds.json", {}).get("sets", {}).get(s, {})
        missed = {}
        for m in ("A_v7", "B_yolo26n_30ep", "C_yolo26n_50ep", "stock_yolo26n"):
            f = S.PRED_DIR / f"{m}__{s}__c0.4__none.json"
            if not f.exists():
                continue
            preds = read_json(f)
            ms = set()
            for path, boxes in gt.items():
                name = Path(path).name
                gts = [b for b in boxes if b[0] == 0]
                un = list(range(len(gts)))
                for _, cls, box in preds.get(name, []):
                    if cls != 0:
                        continue
                    best, bi = 0.0, None
                    for gi in un:
                        o = S.iou(tuple(box), tuple(gts[gi][1:]))
                        if o > best:
                            best, bi = o, gi
                    if bi is not None and best >= 0.5:
                        un.remove(bi)
                for gi in un:
                    ms.add((name, gi))
            missed[m] = ms
        n_total = sum(1 for b in gt.values() for x in b if x[0] == 0)
        res = {"n_person_boxes": n_total, "missed": {m: len(v) for m, v in missed.items()}}
        if "A_v7" in missed:
            A = missed["A_v7"]
            for m, v in missed.items():
                if m == "A_v7":
                    continue
                res[f"{m}_vs_A"] = {"both_miss": len(A & v), "only_A_misses": len(A - v), "only_other_misses": len(v - A),
                                    "frac_of_A_misses_also_missed": (len(A & v) / len(A)) if A else None}
            if lt:
                dark = {n for n, l in lt["luma"].items() if l <= lt["dark_max_luma"]}
                res["A_misses_in_dark_tercile"] = sum(1 for n, _ in A if n in dark)
                res["person_boxes_in_dark_tercile"] = sum(1 for p, b in gt.items() if Path(p).name in dark for x in b if x[0] == 0)
            byclip = defaultdict(lambda: defaultdict(int))
            for m, v in missed.items():
                for n, _ in v:
                    byclip[S.clip_of(n)][m] += 1
            res["missed_by_clip"] = {c: dict(v) for c, v in byclip.items()}
        out[s] = res
    write_json(RAW / "miss_overlap.json", out)
    return out


def sec_training(sc):
    P("## 4. Training comparison (13-class val split of sage_merged_v7, 2,610 images)")
    P("")
    pf = read_json(RAW / "preflight.json", {})
    a = pf.get("recipe", {}).get("A_full_train", {})
    s1 = read_json(RAW / "stage1_control.json", {})
    P("| model | base | epochs run / set | patience | early-stopped | best epoch (mAP50-95) | best mAP50-95 (training log) | mAP50 at best | mean s/epoch | median s/epoch | re-val mAP50 | re-val mAP50-95 |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    if a:
        av = s1.get("A_val", {})
        P(f"| A (v7) | yolov8n.pt | {a['epochs_run']}/{a['epochs_configured']} | {a['patience']} | {a['early_stopped']} | {a['best_epoch_by_mAP50_95']} | "
          f"{a['best_mAP50_95']:.4f} | {a['mAP50_at_that_epoch']:.4f} | {a['mean_s_per_epoch']:.0f} | {a['median_s_per_epoch']:.0f} | "
          f"{pct(av.get('mAP50'), 4)} | {pct(av.get('mAP50_95'), 4)} |")
    tinfo = {}
    for key, cfg in (("B_yolo26n_30ep", "30/10"), ("C_yolo26n_50ep", "50/50")):
        meta = read_json(RAW / f"train_{key}.json")
        eps = read_json(RAW / f"train_{key}_epochs.json", [])
        if not meta:
            P(f"| {key} | yolo26n.pt | not run | | | | | | | | | |")
            continue
        save_dir = meta.get("save_dir") or (meta["attempts"][-1].get("save_dir") if meta.get("attempts") else None)
        rows = []
        if save_dir and (Path(save_dir) / "results.csv").exists():
            rows = [{k.strip(): v for k, v in r.items()} for r in csv.DictReader(open(Path(save_dir) / "results.csv", encoding="utf-8"))]
        m5095 = [float(r["metrics/mAP50-95(B)"]) for r in rows]
        m50 = [float(r["metrics/mAP50(B)"]) for r in rows]
        bi = max(range(len(m5095)), key=lambda i: m5095[i]) if m5095 else None
        seen = set()
        eps = [e for e in eps if not (e.get("t_start") in seen or seen.add(e.get("t_start")))]  # final-val callback repeats the last epoch
        durs = [e["duration_s"] for e in eps if e.get("duration_s")]
        import statistics
        att = meta.get("attempts", [])
        last = att[-1] if att else {}
        val = read_json(RAW / f"scores__{key}.json", {}).get("val", {})
        set_epochs = cfg.split("/")[0]
        P(f"| {key} | yolo26n.pt | {len(rows)}/{set_epochs} | {cfg.split('/')[1]} | {last.get('stopped_early')} | "
          f"{(int(float(rows[bi]['epoch'])) if bi is not None else '--')} | {pct(m5095[bi] if bi is not None else None, 4)} | "
          f"{pct(m50[bi] if bi is not None else None, 4)} | {(statistics.mean(durs) if durs else float('nan')):.0f} | "
          f"{(statistics.median(durs) if durs else float('nan')):.0f} | {pct(val.get('mAP50'), 4)} | {pct(val.get('mAP50_95'), 4)} |")
        tinfo[key] = {"attempts": [{k: x.get(k) for k in ("name", "status", "resume", "batch_override", "optimizer_used", "lr0_used",
                                                          "dropped_keys_not_accepted", "changed_vs_control", "error")} for x in att]}
    P("")
    P("s/epoch for A comes from its results.csv (cumulative `time` column, includes validation); for B/C from "
      "epoch-start -> fit-epoch-end callbacks (also includes validation). Same machine, same dataset, workers 0, batch 16 "
      "unless an attempt below says otherwise.")
    P("")
    for k, v in tinfo.items():
        P(f"- {k} attempts: `{json.dumps(v['attempts'], default=str)}`")
    P("")
    if not tinfo:
        P("No B/C training records found.")
        P("")


def enhancement_verdict(sc):
    P("## 5. Dark-frame enhancement (pre-registered rule)")
    P("")
    lt = read_json(RAW / "luma_thresholds.json", {})
    P("Dark = bottom third of mean-luma (Y of YCrCb) per eval set, bright = top third, fixed in preflight before any "
      "enhancement result. Rule: a variant *helps* a model iff pooled dark-subset person recall @IoU0.5 rises >= 0.05 "
      "absolute vs no enhancement, while pooled bright-subset recall drops <= 0.02 and overall precision drops <= 0.03. "
      "'Enhancement is worthwhile' iff one variant helps >= 2 of the 3 models (A, B, and C -- or stock yolo26n if C does "
      "not exist). Pooled = reserved388_partial + round6_heldout (disjoint, correctly oriented).")
    P("")
    if lt:
        P("| set | dark luma <= | bright luma >= | frames | dark frames | bright frames |")
        P("|---|---|---|---|---|---|")
        for s, d in lt["sets"].items():
            P(f"| {s} | {d['dark_max_luma']:.1f} | {d['bright_min_luma']:.1f} | {d['n_frames']} | {d['n_dark']} | {d['n_bright']} |")
        P("")
    third = "C_yolo26n_50ep" if (RAW / "enhance__C_yolo26n_50ep.json").exists() else "stock_yolo26n"
    models = ["A_v7", "B_yolo26n_30ep", third]
    helps = defaultdict(list)
    verdict_rows = []
    P("| model | variant | dark recall (TP/n) | Δdark | bright recall (TP/n) | Δbright | precision (all) | Δprec | helps? | dark underpowered (<30 boxes)? |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    missing = []
    for m in models:
        e = read_json(RAW / f"enhance__{m}.json")
        if not e or "pooled" not in e:
            missing.append(m)
            P(f"| {m} | MISSING | | | | | | | | |")
            continue
        pv = e["pooled"]["variants"]
        b = pv["none"]
        for var, d in pv.items():
            dd = (d["dark|0.5"]["recall"] or 0) - (b["dark|0.5"]["recall"] or 0)
            db = (d["bright|0.5"]["recall"] or 0) - (b["bright|0.5"]["recall"] or 0)
            dp = (d["all|0.5"]["precision"] or 0) - (b["all|0.5"]["precision"] or 0)
            h = var != "none" and dd >= 0.05 - 1e-12 and db >= -0.02 - 1e-12 and dp >= -0.03 - 1e-12
            if h:
                helps[var].append(m)
            under = d["dark|0.5"]["n_gt"] < 30
            P(f"| {m} | {var} | {pct(d['dark|0.5']['recall'])} ({d['dark|0.5']['tp']}/{d['dark|0.5']['n_gt']}) | {dd:+.3f} | "
              f"{pct(d['bright|0.5']['recall'])} ({d['bright|0.5']['tp']}/{d['bright|0.5']['n_gt']}) | {db:+.3f} | "
              f"{pct(d['all|0.5']['precision'])} | {dp:+.3f} | {'YES' if h else 'no'} | {'YES' if under else 'no'} |")
            verdict_rows.append({"model": m, "variant": var, "d_dark": dd, "d_bright": db, "d_prec": dp, "helps": h})
    P("")
    worth = [v for v, ms in helps.items() if len(ms) >= 2]
    if missing:
        verdict = (f"VERDICT INCOMPLETE: enhancement results missing for {missing}; with the available models, "
                   + ("enhancement is worthwhile" if worth else "no variant helps 2 of the 3 models") + ".")
    else:
        verdict = (f"VERDICT: enhancement is worthwhile (variant(s) {worth} help >= 2 of {models})." if worth
                   else f"VERDICT: enhancement is NOT worthwhile -- no single variant helps >= 2 of {models} under the pre-registered rule.")
    P(f"**{verdict}**")
    P("")
    P("Per-set (not pooled) dark-subset recall @IoU0.5, for transparency:")
    P("")
    P("| model | set | variant | dark TP/n | bright TP/n |")
    P("|---|---|---|---|---|")
    for m in models:
        e = read_json(RAW / f"enhance__{m}.json")
        if not e:
            continue
        for k, v in e.get("sets", {}).items():
            if "dark|0.5" not in v:
                continue
            s, var = k.split("|")
            P(f"| {m} | {s} | {var} | {v['dark|0.5']['tp']}/{v['dark|0.5']['n_gt']} | {v['bright|0.5']['tp']}/{v['bright|0.5']['n_gt']} |")
    P("")
    g = read_json(RAW / "enhance_grids.json", {})
    if g.get("files"):
        P(f"Example grids (original | {g['best_variant_by_pooled_dark_recall_gain']}, model A; {g['legend']}): " +
          ", ".join(Path(f).name for f in g["files"]) + " in OUT/enhance_grids/.")
        CHECK.append("Look at OUT/enhance_grids/*.jpg -- the 6 darkest labelled person frames, original vs best variant.")
    P("")
    write_json(RAW / "enhancement_verdict.json", {"models": models, "rows": verdict_rows, "helps": helps, "verdict": verdict})
    SUMMARY.append(verdict)


def sec_pose():
    P("## 6. Pose benchmark v2 (benchmarks/pose_yolo26 cache, corrected scoring)")
    P("")
    ps = read_json(RAW / "pose_v2_scores.json")
    sp = read_json(RAW / "pose_v2_speed.json")
    if not ps or "aggregates" not in ps:
        P("**FAILED/MISSING: raw/pose_v2_scores.json has no aggregates.**")
        SUMMARY.append("Pose v2: FAILED/MISSING.")
    else:
        ag = ps["aggregates"]
        mm = ps.get("reproduction_mismatches", [])
        P(f"Re-scoring the cached keypoints with the ORIGINAL rule reproduces metrics_full.json on "
          f"{'every clip x backend' if not mm else f'all but {len(mm)} clip x backend pairs (listed in raw/pose_v2_scores.json)'}.")
        P("")
        P("**Defect 1 (get_fall_window -> None when the GT has no upright segment): CONFIRMED in code** "
          "(evaluate_real_footage.get_fall_window requires a non-ignored, non-lying segment) and in data. Corrected rule, applied "
          "only when the original returns None: if the GT has a transition (ignored) segment and a lying/fall segment but no "
          "upright segment, the expected window is [start of first transition segment, end of last transition/lying segment]. "
          "Clips whose window this creates:")
        P("")
        P("| clip | GT rows (start, end, label, ignore) | corrected window (frames) |")
        P("|---|---|---|")
        for c in ag.get("_clips_with_corrected_window", []):
            rows_txt = "; ".join("%g-%gs %s%s" % (r[0], r[1], r[2], " (ign)" if r[3] else "") for r in c["gt_rows"])
            P(f"| {c['clip']} | {rows_txt} | {c['window_corrected_frames']} |")
        P("")
        backends = [b for b in ag if not b.startswith("_")]
        P("**ORIGINAL vs CORRECTED** (fall recall = TP / fall clips; a fall clip whose only alarms are outside the window is a miss; "
          "ADL false-alarm rate = ADL clips with any alarm / ADL clips):")
        P("")
        P("| backend | ORIG fall TP/clips | ORIG old-style % (TP/(TP+silent FN)) | ORIG ADL FA/clips | CORR fall TP/clips | CORR misses (silent / alarm outside) | CORR ADL FA/clips | posture acc (frame-weighted, n) |")
        P("|---|---|---|---|---|---|---|---|")
        for b in backends:
            o, c = ag[b]["original"], ag[b]["corrected"]
            P(f"| {b} | {o['tp']}/{o['fall_clips']} = {pct(o['fall_recall'], 3)} | {pct(o['old_style_recall_tp_over_tp_plus_silent_fn'], 3)} | "
              f"{o['adl_false_alarm_clips']}/{o['adl_clips']} | {c['tp']}/{c['fall_clips']} = {pct(c['fall_recall'], 3)} | "
              f"{c['fn_silent']} / {c['fn_alarm_outside_window']} | {c['adl_false_alarm_clips']}/{c['adl_clips']} = {pct(c['adl_false_alarm_rate'], 3)} | "
              f"{pct(ag[b]['posture_acc_frame_weighted'], 3)} (n={ag[b]['n_frames_scored']}) |")
        P("")
        mp = ag.get("mediapipe", {}).get("original", {})
        P(f"**Defect 2 (inconsistent denominators): CONFIRMED.** The old summary printed e.g. MediaPipe '60.0% (18/32)': the "
          f"percentage was TP/(TP+silent FN) = {pct(mp.get('old_style_recall_tp_over_tp_plus_silent_fn'), 3)}, while the "
          f"parenthesis used all {mp.get('fall_clips')} fall clips (18/32 = {18 / 32:.3f}). Fall clips whose alarm landed outside the "
          "window were dropped from the percentage's denominator but kept in the printed one. v2 uses one definition everywhere "
          "and prints the denominator with every rate.")
        P("")
        P("**Defect 3 (clips at 0% for every backend):** rules fixed before looking -- GT problem (no scored frames / GT longer than "
          "video by >1 s / GT covers <50% of video / window past the end), no person detected (best backend finds a person in "
          "<50% of the relevant frames), else genuine heuristic miss.")
        P("")
        P("| clip | kind | cause | evidence |")
        P("|---|---|---|---|")
        for z in ps.get("zero_clips", []):
            pf = z["person_found_frac"]
            best_pf = max((v for v in pf.values() if v is not None), default=None)
            ev = []
            if z["gt_reasons"]:
                ev.append("; ".join(z["gt_reasons"]))
            ev.append(f"best person-found {pct(best_pf, 2)}")
            if z["kind"].startswith("posture"):
                mpc = z["pred_label_counts_scored"].get("mediapipe", {})
                ev.append(f"GT {', '.join(sorted({r[2] for r in z['gt_rows'] if not r[3]}))}; MediaPipe predicted {mpc}")
            else:
                ev.append(f"window {z['window']}; results {sorted(set(z['fall_results'].values()))}; first alarms {z['first_alarm']}")
            P(f"| {z['clip']} | {z['kind']} | {z['cause']} | {' / '.join(ev)} |")
        P("")
    if sp and sp.get("summary"):
        P("**Defect 4 (speed not like-for-like): CONFIRMED** -- the old table compared YOLO-GPU over all 64 clips with MediaPipe-CPU "
          "over an 8-clip subset, single run. v2: same 8 clips, same decoded frames, same machine with no other job running, "
          f"warm-up ({sp['warmup_frames_excluded_per_clip']} frames/clip excluded + 20-frame global warm-up), median of "
          f"{sp['repeats']} repeated runs. MediaPipe ran with delegate `{sp['mediapipe_delegate']}` (CPU; the Python Tasks API "
          "on Windows has no GPU delegate here). Input: " + sp["input"] + ".")
        P("")
        P("| backend | device | pose ms/frame (median of rep medians) | rep medians | p95 | remap ms | heuristic ms/frame | frames/rep |")
        P("|---|---|---|---|---|---|---|---|")
        for k, v in sp["summary"].items():
            b, d = k.split("|")
            P(f"| {b} | {d} | {v['pose_median_of_rep_medians_ms']:.2f} | {', '.join(f'{x:.2f}' for x in v['rep_medians_ms'])} | "
              f"{v['pose_p95_median_ms']:.2f} | {pct(v['remap_ms_per_frame'], 3)} | {v['heuristic_ms_per_frame']:.3f} | {v['n_frames_timed_per_rep']} |")
        P("")
    elif sp:
        P("Speed run incomplete; partial runs in raw/pose_v2_speed.json.")
    else:
        P("**Speed: FAILED/MISSING** (raw/pose_v2_speed.json absent).")
    P("")
    if ps and "aggregates" in ps:
        ag = ps["aggregates"]
        P("### Bottom line (corrected scoring)")
        P("")
        P("| backend | fall TP / fall clips | fall recall 95% CI | ADL false alarms / ADL clips | ADL FA 95% CI | pose median ms (GPU) | pose median ms (CPU) |")
        P("|---|---|---|---|---|---|---|")
        summ = (sp or {}).get("summary", {})
        best = None
        for b in [x for x in ag if not x.startswith("_")]:
            c = ag[b]["corrected"]
            base = b.split("@")[0]
            g = summ.get(f"{base}|cuda:0", {}).get("pose_median_of_rep_medians_ms")
            cpu = summ.get(f"{base}|cpu", {}).get("pose_median_of_rep_medians_ms")
            P(f"| {b} | {c['tp']}/{c['fall_clips']} | {ci(c['tp'], c['fall_clips'])} | {c['adl_false_alarm_clips']}/{c['adl_clips']} | {ci(c['adl_false_alarm_clips'], c['adl_clips'])} | {pct(g, 2) if g else 'n/a'} | {pct(cpu, 2) if cpu else 'n/a'} |")
            if best is None or c["tp"] > ag[best]["corrected"]["tp"]:
                best = b
        P("")
        mpc = ag.get("mediapipe", {}).get("corrected", {})
        bc = ag[best]["corrected"]
        SUMMARY.append(f"Pose v2 (corrected): MediaPipe falls {mpc.get('tp')}/{mpc.get('fall_clips')}, ADL false alarms "
                       f"{mpc.get('adl_false_alarm_clips')}/{mpc.get('adl_clips')}; most fall TPs: {best} {bc['tp']}/{bc['fall_clips']}, "
                       f"ADL FA {bc['adl_false_alarm_clips']}/{bc['adl_clips']}. With ~{mpc.get('fall_clips')} fall clips, a few clips' difference is noise.")


def sec_recommendations(sc, efp, ov):
    P("## 7. Recommendations (derived from the tables above)")
    P("")
    lines = []
    have_b = bool(sc.get(("B_yolo26n_30ep", 0.4)))
    for s in SETS:
        a = person(sc.get(("A_v7", 0.4), {}).get(s, {}), "0.5")
        b = person(sc.get(("B_yolo26n_30ep", 0.4), {}).get(s, {}), "0.5")
        if a and b:
            d = b["recall"] - a["recall"]
            loA, hiA = wilson(a["tp"], a["n_gt"])
            loB, hiB = wilson(b["tp"], b["n_gt"])
            overlap = not (hiA < loB or hiB < loA)
            lines.append(f"- {s}: B {b['tp']}/{b['n_gt']} vs A {a['tp']}/{a['n_gt']} (Δ {d:+.3f}; FP B {b['fp']} vs A {a['fp']}); "
                         f"95% CIs {'overlap -> not distinguishable' if overlap else 'do NOT overlap'}.")
    if lines:
        P("Detector, B (YOLO26n, A's recipe) vs A, person @IoU0.5 conf 0.4:")
        P("")
        L.extend(lines)
        P("")
    elif not have_b:
        P("- B was not scored, so no detector change can be recommended from this run; keep A (v7) as the reference.")
    ea, eb = efp.get(("A_v7", 0.4)), efp.get(("B_yolo26n_30ep", 0.4))
    if ea and eb and "fp_rate_pct" in ea and "fp_rate_pct" in eb:
        P(f"- Empty-room FP: A {ea['fp_rate_pct']:.2f}% vs B {eb['fp_rate_pct']:.2f}% of {ea['frames']} frames.")
    if ov:
        P("")
        P("Model vs labels -- do B's misses fall on the same boxes as A's? (person, IoU 0.5, conf 0.4)")
        P("")
        P("| set | person boxes | A misses | other model | its misses | both miss | share of A's misses also missed |")
        P("|---|---|---|---|---|---|---|")
        for s, r in ov.items():
            for k, v in r.items():
                if k.endswith("_vs_A"):
                    m = k[:-5]
                    P(f"| {s} | {r['n_person_boxes']} | {r['missed'].get('A_v7')} | {m} | {r['missed'].get(m)} | {v['both_miss']} | {pct(v['frac_of_A_misses_also_missed'], 2)} |")
        P("")
        P("Reading rule: if B (a different architecture trained on the same labels) misses mostly the same boxes A misses, the "
          "ceiling is more likely in the data/labels (or the frames themselves) than in the architecture. A high share is "
          "evidence for that only together with the per-clip table in section 3 showing the misses concentrate in the same clips.")
    P("")


def sec_decisions():
    P("## 8. Decisions log and things to double-check by hand")
    P("")
    d = (OUT / "DECISIONS.md").read_text(encoding="utf-8") if (OUT / "DECISIONS.md").exists() else "(none)"
    P("Full log: DECISIONS.md. Entries:")
    P("")
    L.extend(d.strip().splitlines())
    P("")
    CHECK.extend([
        "The 4 missing source clips (TV_Lounge_1_Fall2, TV_Lounge_2_Fall2, people, people_(2)): if they exist elsewhere, "
        "the full 388-box set can be rebuilt with stage0_preflight.build_eval_sets().",
        "The corrected fall-window rule (section 6) for each clip it changed -- confirm against the videos that the alarm frames "
        "really are during the fall.",
        "Any 'CONTROL NOT REPRODUCED' / 'NOT REPRODUCED' row in section 2.",
    ])
    P("**Double-check by hand:**")
    P("")
    for c in CHECK:
        P(f"- {c}")
    P("")


def main():
    state = read_json(OUT / "state.json", {})
    sc, efp = load_scores()
    s1 = read_json(RAW / "stage1_control.json", {})
    body_sections = []
    try:
        sec_status(state)
    except Exception as e:
        P(f"(status section failed: {e!r})")
    for fn, args in ((sec_control, (s1,)), (person_table, (sc, efp)), (sec_training, (sc,)), (enhancement_verdict, (sc,)), (sec_pose, ())):
        try:
            fn(*args)
        except Exception as e:
            import traceback
            P(f"**Section {fn.__name__} FAILED while building the report:** `{e!r}`")
            P("```")
            P(traceback.format_exc()[-1500:])
            P("```")
    ov = None
    try:
        ov = per_box_overlap(sc)
    except Exception as e:
        P(f"(miss-overlap analysis failed: {e!r})")
    try:
        sec_recommendations(sc, efp, ov)
    except Exception as e:
        P(f"**Recommendations section failed:** `{e!r}`")
    notes = OUT / "ANALYST_NOTES.md"
    if notes.exists():
        L.extend(notes.read_text(encoding="utf-8").strip().splitlines())
        P("")
    sec_decisions()
    # lead summary
    gate = read_json(RAW / "gate.json")
    st = state.get("stages", {})
    cst = st.get("S6_train_C", {})
    head = ["# Overnight YOLO26 experiments -- RESULTS", "",
            f"Generated {now():%Y-%m-%d %H:%M} from files in benchmarks/overnight_yolo26/ only. Eval set named on every number.", "",
            "## Summary", ""]
    a, b = person(sc.get(("A_v7", 0.4), {}).get("reserved388_partial", {}), "0.5"), person(sc.get(("B_yolo26n_30ep", 0.4), {}).get("reserved388_partial", {}), "0.5")
    a6, b6 = person(sc.get(("A_v7", 0.4), {}).get("round6_heldout", {}), "0.5"), person(sc.get(("B_yolo26n_30ep", 0.4), {}).get("round6_heldout", {}), "0.5")
    summ = []
    done = [k for k, v in st.items() if v.get("status") == "done" and "__attempt" not in k]
    bad = [f"{k} ({v.get('status')})" for k, v in st.items() if v.get("status") not in ("done", "pending", "running") and "__attempt" not in k]
    summ.append(f"- Stages done: {len(done)}; not done: {', '.join(bad) or 'none'}.")
    caches = []
    for c in ("train.cache", "val.cache"):
        f = ROOT / "datasets/sage_merged_v7/labels" / c
        if f.exists():
            caches.append(f"{c} {f.stat().st_size} B, mtime {dt.datetime.fromtimestamp(f.stat().st_mtime):%Y-%m-%d %H:%M}")
    summ.append("- **READ-ONLY RULE BROKEN (my error):** Ultralytics overwrote datasets/sage_merged_v7/labels/train.cache and "
                "val.cache (derived label-scan caches, not labels/images); the junction workaround did not prevent it. Now: "
                + "; ".join(caches) + ". See DECISIONS.md.")
    CHECK.insert(0, "datasets/sage_merged_v7/labels/{train,val}.cache were rewritten by Ultralytics during this run (see DECISIONS.md). "
                    "Confirm nothing else depends on the old (Aug 22) cache files.")
    summ += [f"- {x}" for x in SUMMARY[:1]]
    if a and b:
        summ.append(f"- Person @IoU0.5, reserved388_partial: A {a['tp']}/{a['n_gt']} ({a['recall']:.3f}) vs B {b['tp']}/{b['n_gt']} ({b['recall']:.3f}).")
    if a6 and b6:
        summ.append(f"- Person @IoU0.5, round6_heldout: A {a6['tp']}/{a6['n_gt']} ({a6['recall']:.3f}) vs B {b6['tp']}/{b6['n_gt']} ({b6['recall']:.3f}).")
    sep = []
    for s in ("heldout_objects_rotfix", "reserved388_partial", "round6_heldout"):
        aa = person(sc.get(("A_v7", 0.4), {}).get(s, {}), "0.5")
        if not aa:
            continue
        loA, hiA = wilson(aa["tp"], aa["n_gt"])
        for m in ("v6", "B_yolo26n_30ep", "C_yolo26n_50ep", "stock_yolo26n", "stock_yolo26s", "stock_yolov8n"):
            pp = person(sc.get((m, 0.4), {}).get(s, {}), "0.5")
            if not pp:
                continue
            lo, hi = wilson(pp["tp"], pp["n_gt"])
            if hi < loA or lo > hiA:
                sep.append(f"{s}: {m} {pp['tp']}/{pp['n_gt']} vs A {aa['tp']}/{aa['n_gt']}")
    if sep:
        summ.append("- **Non-overlapping 95% CIs vs A (person @IoU0.5, conf 0.4):** " + "; ".join(sep) +
                    ". Where v6 beats A this CONTRADICTS v7_results.md ('v7 detects exactly the same fall frames v5 and v6 did'), "
                    "which was measured on the as-stored set with sideways Bedroom_Fall frames.")
    if gate:
        summ.append("- C: " + ("trained (gate passed)." if gate.get("run_C") else f"C SKIPPED: {', '.join(gate.get('failed_conditions', []))} (raw/gate.json)."))
    elif cst.get("status") == "skipped":
        summ.append(f"- {cst.get('note')}")
    summ += [f"- {x}" for x in SUMMARY[1:]]
    summ = summ[:12]
    text = "\n".join(head + summ + ["", "Full detail follows; raw JSON/CSV in raw/.", ""] + L) + "\n"
    (OUT / "RESULTS.md").write_text(text, encoding="utf-8")
    print(str(OUT / "RESULTS.md"))


if __name__ == "__main__":
    main()

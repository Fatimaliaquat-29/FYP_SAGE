"""Phase 6 figures (same style as phase 5). Writes under benchmarks/phase6_sweep/:
  training_curves.png        C + every phase-6 run (incl. ones still training): LR schedule, losses, val mAP
  person_recall_by_set.png   person recall at IoU 0.5 per held-out set, Wilson 95% CI, all scored models
  examples_sheet.jpg (+ examples/)   frames where a run and C disagree on a person; columns = C + each run
  bed_sheet.jpg              D vs C on held-out frames with beds (beds drawn)
  lying_on_bed_sheet.jpg     D vs C on the lying-on-bed frames where C drew very loose person boxes
Needs p6_scores.json, hits_<M>.csv, preds_<M>.json from score_p6.py (curves need only results.csv).
"""
import csv
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase6_sweep"
P5 = ROOT / "benchmarks" / "phase5_v8"
sys.path.insert(0, str(P5))
import plot_v8 as pv  # noqa: E402  (style, wilson, gt7, SET_DIRS, font)

ORDER = ["A", "C", "D", "LR2", "B8", "COS", "DCOS", "B32", "LRH"]
COLORS = {"A": "#2a78d6", "C": "#1baf7a", "D": "#eb6834", "LR2": "#6250d6", "B8": "#eda100", "LRH": "#7a7a7a", "COS": "#e87ba4",
          "B32": "#008300", "DCOS": "#008300"}   # DCOS takes the unused B32 slot (B32 not run)   # validated order (dataviz validate_palette.js, light): A,C,D,LR2,LRH,COS,B32
LABEL = {"A": "A: v7", "C": "C: baseline (phase 5)", "D": "D: C + 4 clips re-added", "LR2": "LR2: learning rate x2",
         "LRH": "LRH: learning rate x0.5", "B8": "B8: batch 8", "COS": "COS: cosine schedule", "B32": "B32: batch 32",
         "DCOS": "DCOS: D data + cosine"}
SURFACE, INK, INK2, GRID = pv.SURFACE, pv.INK, pv.INK2, pv.GRID
SETS = pv.SETS


def results(m):
    p = (P5 if m == "C" else OUT) / "runs" / m / "results.csv"
    if not p.exists():
        return None
    rows = [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(open(p, encoding="utf-8"))]
    return rows or None


def curves():
    data = {m: results(m) for m in ORDER if m != "A"}
    data = {m: r for m, r in data.items() if r}
    panels = [("lr/pg0", "Learning rate (schedule)"), ("train/box_loss", "Train box loss"),
              ("metrics/mAP50-95(B)", "Val mAP50-95"), ("val/box_loss", "Val box loss"),
              ("val/cls_loss", "Val class loss"), ("metrics/mAP50(B)", "Val mAP50")]
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.2), facecolor=SURFACE)
    for ax, (col, title) in zip(axes.flat, panels):
        pv.style(ax)
        ends = []
        for m, rows in data.items():
            ep, ys = [r["epoch"] for r in rows], [r[col] for r in rows]
            ax.plot(ep, ys, color=COLORS[m], lw=2 if m in ("C", "D") else 1.6, solid_capstyle="round",
                    label=LABEL[m] + ("" if len(rows) >= 30 or (OUT / f"DONE_{m}").exists() or m == "C" else
                                      f" (running, {len(rows)} ep)"))
            ends.append([ys[-1], m, ep[-1]])
        ax.axvline(20.5, color=INK2, lw=0.8, ls=(0, (3, 3)), alpha=0.5)
        lo, hi = ax.get_ylim()
        gap = 0.075 * (hi - lo)
        grp = sorted(ends)
        pos = [g[0] for g in grp]
        for i in range(1, len(pos)):
            if pos[i] - pos[i - 1] < gap:
                pos[i] = pos[i - 1] + gap
        over = pos[-1] - (hi - 0.6 * gap) if pos else 0
        pos = [p - over for p in pos] if over > 0 else pos
        for g, ly in zip(grp, pos):
            fmt = f"{g[0]:.2e}" if col.startswith("lr") else f"{g[0]:.3f}"
            ax.annotate(f"{g[1]} {fmt}", (g[2], g[0]), xytext=(31.0, ly), textcoords="data", va="center",
                        fontsize=7.5, color=INK2)
        ax.set_title(title, loc="left", fontsize=10, color=INK, pad=6)
        ax.set_xlim(0.5, 36)
        ax.set_xlabel("epoch")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", ncol=3, frameon=False, bbox_to_anchor=(0.99, 0.99), fontsize=8.5)
    fig.suptitle("Training curves: C vs phase-6 runs", x=0.012, ha="left", fontsize=13, fontweight="bold", y=0.985)
    fig.text(0.012, 0.925, "Each run changes ONE thing vs C (YOLOv8n, AdamW lr 0.000588, linear decay, batch 16, 30 epochs, "
             "seed 0). All share C's val set, so val curves ARE comparable here (unlike phase 5).", fontsize=9, color=INK2)
    fig.text(0.012, 0.012, "Dashed line: mosaic off for the last 10 epochs. Early stopping (patience 10) can end a run before "
             "30 epochs; best.pt is the epoch with the best val fitness.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.91))
    fig.savefig(OUT / "training_curves.png", dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print("wrote training_curves.png")


def recall_chart(res):
    ms = res["models"]
    cache = res["cache"]
    sets = list(SETS)
    fig, ax = plt.subplots(figsize=(11, 1.6 + 0.42 * len(ms) * len(sets)), facecolor=SURFACE)
    pv.style(ax)
    ax.grid(False, axis="y")
    bh = 0.84 / len(ms)
    labelled = set()
    for j, m in enumerate(ms):
        for i, s in enumerate(sets):
            st = cache[m]["stats"][s]["0.5"].get("person", {"tp": 0, "fn": 0})
            n = st["tp"] + st["fn"]
            if not n:
                continue
            lo, hi = pv.wilson(st["tp"], n)
            y = i + (j - (len(ms) - 1) / 2) * bh
            ax.barh(y, st["tp"] / n, height=bh - 0.03, color=COLORS[m], label=None if m in labelled else LABEL[m])
            labelled.add(m)
            ax.plot([lo, hi], [y, y], color=INK2, lw=0.9)
            ax.text(min(hi, 1.0) + 0.01, y, f"{m} {st['tp']}/{n}", va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(range(len(sets)))
    ax.set_yticklabels([SETS[s] for s in sets])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.2)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("person recall at IoU 0.5 (conf 0.4); whiskers = Wilson 95% CI")
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    fig.suptitle("Person recall per held-out set: C vs phase-6 runs", x=0.012, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.012, 0.008, "* CAUCAFall/ExDark: C and every phase-6 run trained on other images of these datasets; A did not. "
             "PROVISIONAL: held-out labels follow no consistent written convention.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(OUT / "person_recall_by_set.png", dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print("wrote person_recall_by_set.png")


def load_hits(m):
    return {(r["set"], r["image"], r["box_idx"]): r for r in csv.DictReader(open(OUT / f"hits_{m}.csv", encoding="utf-8"))}


def panel(s, image, m, preds, classes, title, box=None):
    im = Image.open(pv.SET_DIRS[s] / "images" / image).convert("RGB")
    W0, H0 = im.size
    if box:                       # crop (normalised x1,y1,x2,y2)
        im = im.crop((int(box[0] * W0), int(box[1] * H0), int(box[2] * W0), int(box[3] * H0)))
    im.thumbnail((420, 320))
    W, H = im.size
    d = ImageDraw.Draw(im)

    def xy(b):
        if not box:
            return [b[0] * W, b[1] * H, b[2] * W, b[3] * H]
        bw, bhh = box[2] - box[0], box[3] - box[1]
        return [(b[0] - box[0]) / bw * W, (b[1] - box[1]) / bhh * H, (b[2] - box[0]) / bw * W, (b[3] - box[1]) / bhh * H]
    for c, *b in pv.gt7(s, image):
        if c in classes:
            d.rectangle(xy(b), outline="white", width=2)
    for conf, c, *b in preds:
        if c in classes and conf >= 0.4:
            d.rectangle(xy(b), outline=COLORS[m], width=4)
            d.text((xy(b)[0] + 3, max(0, xy(b)[1] - 14)), f"{pv.NAMES[c]} {conf:.2f}", fill=COLORS[m], font=pv.font(12))
    bar = Image.new("RGB", (W, 26), "#202020")
    ImageDraw.Draw(bar).text((6, 5), title, fill="white", font=pv.font(14))
    c = Image.new("RGB", (W, H + 26), "black")
    c.paste(bar, (0, 0))
    c.paste(im, (0, 26))
    return c


def grid_sheet(rows, title, path):
    """rows: list of (caption, [panel images])"""
    if not rows:
        return
    pw = max(p.width for _, ps in rows for p in ps)
    ph = max(p.height for _, ps in rows for p in ps)
    ncol = max(len(ps) for _, ps in rows)
    sheet = Image.new("RGB", (pw * ncol, 50 + len(rows) * (ph + 24)), "#111111")
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), title, fill="white", font=pv.font(20))
    y = 50
    for cap, ps in rows:
        d.rectangle([0, y, pw * ncol, y + 24], fill="#f2f2f2")
        d.text((8, y + 4), cap, fill="black", font=pv.font(14))
        for i, p in enumerate(ps):
            sheet.paste(p, (i * pw, y + 24))
        y += ph + 24
    sheet.save(path, quality=88)
    print(f"wrote {path.name}")


def examples(res):
    ms = [m for m in res["models"] if m != "A"]
    runs = [m for m in ms if m != "C"]
    if not runs:
        print("examples skipped: no phase-6 run scored yet")
        return
    preds = {m: json.loads((OUT / f"preds_{m}.json").read_text(encoding="utf-8")) for m in ms}
    hits = {m: load_hits(m) for m in ms}
    picks, seen = [], set()
    for m in runs:
        for want in ("gain", "loss"):
            cands = []
            for k, rc in hits["C"].items():
                if rc["cls"] != "0" or k[0] not in ("reserved388_partial", "round6_heldout", "heldout_objects"):
                    continue
                a, b = int(rc["hit_iou0.5"]), int(hits[m][k]["hit_iou0.5"])
                if (want == "gain" and b and not a) or (want == "loss" and a and not b):
                    cands.append((k[0], k[1]))
            cands = sorted(set(cands) - seen)
            if cands:
                f = cands[len(cands) // 2]
                seen.add(f)
                picks.append((f, f"{m} finds a person C misses" if want == "gain" else f"C finds a person {m} misses"))
    (OUT / "examples").mkdir(exist_ok=True)
    rows = []
    for (s, image), why in picks[:12]:
        g = [x for x in pv.gt7(s, image) if x[0] == 0]
        ps = []
        for m in ms:
            k = sum(int(hits[m][(s, image, str(i))]["hit_iou0.5"]) for i, x in enumerate(pv.gt7(s, image)) if x[0] == 0
                    and (s, image, str(i)) in hits[m])
            ps.append(panel(s, image, m, preds[m][s].get(image, []), {0}, f"{m}: {k}/{len(g)} people found"))
        rows.append((f"{s} / {image}  -  {why}   (white = labelled person)", ps))
        w = sum(p.width for p in ps)
        one = Image.new("RGB", (w, max(p.height for p in ps)), "black")
        x = 0
        for p in ps:
            one.paste(p, (x, 0))
            x += p.width
        one.save(OUT / "examples" / f"{s}__{Path(image).stem}.jpg", quality=88)
    grid_sheet(rows, "Person detections: C vs each phase-6 run (same frames)", OUT / "examples_sheet.jpg")


def bed_and_lying(res):
    if "D" not in res["models"]:
        return
    bm = [m for m in ("A", "C", "D", "LR2", "COS", "DCOS") if m in res["models"]]   # LR2/COS = same data as C
    preds = {m: json.loads((OUT / f"preds_{m}.json").read_text(encoding="utf-8")) for m in bm}
    hits = {m: load_hits(m) for m in bm}
    # bed frames: held-out frames where D hits a bed C misses (and the reverse), own footage
    gains, losses = [], []
    for k, rc in hits["C"].items():
        if rc["cls"] != "1" or k[0] not in ("reserved388_partial", "round6_heldout"):
            continue
        a, b = int(rc["hit_iou0.5"]), int(hits["D"][k]["hit_iou0.5"])
        (gains if b and not a else losses if a and not b else []).append((k[0], k[1]))
    # prefer rooms D never trained on; Laying_Dim_HM (round6_heldout) is the same room as the re-added Dim clips
    other = sorted({g for g in gains if g[0] == "reserved388_partial"})
    same = sorted({g for g in gains if g[0] == "round6_heldout" and g[1].startswith("Laying_Dim")})
    pick = other[:: max(1, len(other) // 4)][:4] + same[len(same) // 2:][:1] + sorted(set(losses))[:2]
    rows = []
    for s, image in pick:
        tag = "  [SAME ROOM as re-added clips]" if image.startswith("Laying_Dim") else ""
        rows.append((f"{s} / {image}  -  {'D finds a bed C misses' if (s, image) in gains else 'C finds a bed D misses'}"
                     f"{tag}   (white = labelled bed)",
                     [panel(s, image, m, preds[m][s].get(image, []), {1}, f"{m}: bed boxes") for m in bm]))
    grid_sheet(rows, "Beds: " + " vs ".join(bm) + " (D = C + 4 clips re-added; LR2, COS = C's data)", OUT / "bed_sheet.jpg")
    # lying on bed: the frames where C drew very loose person boxes in phase 5
    frames = ["With_people_Bedroom_Fall_000290.jpg", "With_people_Bedroom_Fall_000420.jpg",
              "With_people_Bedroom_Fall_000480.jpg", "With_people_Bedroom_Fall_000580.jpg"]
    rows = [(f"reserved388_partial / {f}  -  person lying on the bed (white = labelled person)",
             [panel("reserved388_partial", f, m, preds[m]["reserved388_partial"].get(f, []), {0}, f"{m}: person boxes",
                   box=(0.2, 0.45, 0.8, 1.0))      # zoom on the bed area
              for m in bm]) for f in frames if f in preds["C"]["reserved388_partial"]]
    grid_sheet(rows, "Lying on the bed: C drew bed-sized person boxes here. What do the others draw?", OUT / "lying_on_bed_sheet.jpg")


def main():
    curves()
    sp = OUT / "p6_scores.json"
    if not sp.exists():
        print("no p6_scores.json yet")
        return 0
    res = json.loads(sp.read_text(encoding="utf-8"))
    if not all(v["reproduced"] for v in res["control"].values()):
        print("control failed: only curves drawn")
        return 0
    recall_chart(res)
    examples(res)
    bed_and_lying(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())

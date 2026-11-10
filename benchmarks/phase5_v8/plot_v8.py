"""Phase 5 figures (read-only on inputs; writes PNG/JPG under benchmarks/phase5_v8/):
  A_B_C_training_curves.png   overlay of the three results.csv files (same layout as phase 4)
  person_recall_by_set.png    person recall at IoU 0.5 per held-out set, Wilson 95% CI whiskers
  examples/*.jpg + examples_sheet.jpg   the same frames side by side: ground truth + each model's detections
Needs v8_scores.json, hits_<M>.csv and preds_<M>.json from score_v8.py for the last two.
"""
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase5_v8"
NAMES = ["person", "bed", "chair", "sofa", "table", "bottle", "cup"]
RUNS = {"A": ROOT / "runs" / "detect" / "runs" / "detect" / "v7_full_train" / "results.csv",
        "B": OUT / "runs" / "B" / "results.csv", "C": OUT / "runs" / "C" / "results.csv"}
LABEL = {"A": "A: v7 (13 classes)", "B": "B: cleaned (7 classes)", "C": "C: cleaned + CAUCAFall + ExDark"}
COLORS = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SETS = {"heldout_objects": "heldout_objects", "reserved388_partial": "reserved388_partial",
        "round6_heldout": "round6_heldout", "cauca_s10": "CAUCAFall subject 10*", "exdark_test": "ExDark test half*"}
SET_DIRS = {"heldout_objects": ROOT / "eval" / "heldout_objects",
            "reserved388_partial": ROOT / "benchmarks" / "overnight_yolo26" / "evalsets" / "held_out" / "reserved388_partial",
            "round6_heldout": ROOT / "handlabels" / "round6_heldout",
            "cauca_s10": ROOT / "datasets" / "sage_v8_heldout_new" / "cauca_s10",
            "exdark_test": ROOT / "datasets" / "sage_v8_heldout_new" / "exdark_test"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- 1. training curves
def curves():
    data = {k: [{kk.strip(): float(v) for kk, v in r.items()} for r in csv.DictReader(open(p, encoding="utf-8"))]
            for k, p in RUNS.items() if p.exists()}
    panels = [("train/box_loss", "Train box loss"), ("train/cls_loss", "Train class loss"),
              ("metrics/mAP50(B)", "Val mAP50"), ("val/box_loss", "Val box loss"),
              ("val/cls_loss", "Val class loss"), ("metrics/mAP50-95(B)", "Val mAP50-95")]
    fig, axes = plt.subplots(2, 3, figsize=(13, 6.8), facecolor=SURFACE)
    for ax, (col, title) in zip(axes.flat, panels):
        style(ax)
        ends = []
        for name, rows in data.items():
            ep, ys = [r["epoch"] for r in rows], [r[col] for r in rows]
            ax.plot(ep, ys, color=COLORS[name], lw=2, solid_capstyle="round", label=LABEL[name])
            ends.append([ys[-1], name, ep[-1]])
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
            ax.annotate(f"{g[1]} {g[0]:.3f}", (g[2], g[0]), xytext=(g[2] + 0.6, ly), textcoords="data",
                        va="center", fontsize=8, color=INK2)
        ax.set_title(title, loc="left", fontsize=10, color=INK, pad=6)
        ax.set_xlim(0.5, 35)
        ax.set_xlabel("epoch")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", ncol=3, frameon=False, bbox_to_anchor=(0.99, 0.985))
    fig.suptitle("Training curves: A vs B vs C", x=0.012, ha="left", fontsize=13, fontweight="bold", y=0.985)
    fig.text(0.012, 0.935, "Same recipe, seed, optimizer (AdamW, lr 0.000588), 30 epochs. B = v7 minus the 4 problem clips, "
             "relabelled to 7 classes; C = B + CAUCAFall + ExDark (indoor).", fontsize=9, color=INK2)
    fig.text(0.012, 0.012, "Dashed line: mosaic augmentation switched off for the last 10 epochs. Val curves are NOT directly "
             "comparable across models: A is validated on 13 classes, B on 7, C on 7 with extra CAUCAFall/ExDark val images.",
             fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.92))
    fig.savefig(OUT / "A_B_C_training_curves.png", dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print("wrote A_B_C_training_curves.png")


# ---------------------------------------------------------------- 2. person recall per set
def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def recall_chart(res):
    ms = list(res["stats"])
    fig, ax = plt.subplots(figsize=(10, 6.2), facecolor=SURFACE)
    style(ax)
    ax.grid(True, axis="x", color=GRID, lw=0.6)
    ax.grid(False, axis="y")
    sets = list(SETS)
    bh = 0.8 / len(ms)
    labelled = set()
    for j, m in enumerate(ms):
        for i, s in enumerate(sets):
            st = res["stats"][m][s]["0.5"].get("person", {"tp": 0, "fn": 0})
            n = st["tp"] + st["fn"]
            if not n:
                continue
            r = st["tp"] / n
            lo, hi = wilson(st["tp"], n)
            y = i + (j - (len(ms) - 1) / 2) * bh
            ax.barh(y, r, height=bh - 0.04, color=COLORS[m], label=None if m in labelled else LABEL[m])
            labelled.add(m)
            ax.plot([lo, hi], [y, y], color=INK2, lw=1)
            ax.text(min(hi, 1.0) + 0.012, y, f"{m} {st['tp']}/{n}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(sets)))
    ax.set_yticklabels([SETS[s] for s in sets])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.18)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel("person recall at IoU 0.5 (conf 0.4); whiskers = Wilson 95% CI")
    ax.legend(loc="lower right", frameon=False)
    fig.suptitle("Person recall per held-out set", x=0.012, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.012, 0.012, "* New held-out sets from the downloaded data: C trained on other images of the same domain, "
             "A and B did not. PROVISIONAL: held-out labels follow no consistent written convention.", fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(OUT / "person_recall_by_set.png", dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print("wrote person_recall_by_set.png")


# ---------------------------------------------------------------- 3. side-by-side examples
def load_hits(m):
    p = OUT / f"hits_{m}.csv"
    return {(r["set"], r["image"], r["box_idx"]): r for r in csv.DictReader(open(p, encoding="utf-8"))} if p.exists() else {}


def pick_frames(hits):
    """Frames where A and C disagree on person boxes (both directions), plus a dim-room frame; deterministic."""
    a, c = hits["A"], hits["C"]
    per = {}
    for k, ra in a.items():
        if ra["cls"] != "0" or k not in c:
            continue
        d = per.setdefault((k[0], k[1]), [0, 0, 0])
        d[0] += int(c[k]["hit_iou0.5"]) and not int(ra["hit_iou0.5"])
        d[1] += int(ra["hit_iou0.5"]) and not int(c[k]["hit_iou0.5"])
        d[2] += 1
    out = []
    for s in SETS:
        frames = sorted((f for f in per if f[0] == s), key=lambda f: f[1])
        c_only = [f for f in frames if per[f][0] > 0]
        a_only = [f for f in frames if per[f][1] > 0]
        out += [(f, "C finds a person A misses") for f in c_only[:: max(1, len(c_only) // 2)][:2]]
        out += [(f, "A finds a person C misses") for f in a_only[:: max(1, len(a_only) // 2)][:1]]
        if s == "round6_heldout":
            dim = [f for f in frames if "Laying_Dim" in f[1]]
            if dim:
                out.append((dim[len(dim) // 2], "dim room, person lying"))
    seen, uniq = set(), []
    for f, why in out:
        if f not in seen:
            seen.add(f)
            uniq.append((f, why))
    return uniq[:12]


def font(sz):
    try:
        return ImageFont.truetype("arial.ttf", sz)
    except OSError:
        return ImageFont.load_default()


def draw_panel(img_path, gt_lines, preds, m, title):
    im = Image.open(img_path).convert("RGB")
    im.thumbnail((640, 480))
    W, H = im.size
    d = ImageDraw.Draw(im)
    for c, x1, y1, x2, y2 in gt_lines:
        if c == 0:
            d.rectangle([x1 * W, y1 * H, x2 * W, y2 * H], outline="white", width=2)
    for conf, c, x1, y1, x2, y2 in preds:
        col = COLORS[m] if c == 0 else "#b0b0b0"
        d.rectangle([x1 * W, y1 * H, x2 * W, y2 * H], outline=col, width=4 if c == 0 else 1)
        d.text((x1 * W + 3, max(0, y1 * H - 15)), f"{NAMES[c]} {conf:.2f}", fill=col, font=font(13))
    bar = Image.new("RGB", (W, 30), "#202020")
    ImageDraw.Draw(bar).text((8, 6), title, fill="white", font=font(16))
    canvas = Image.new("RGB", (W, H + 30), "black")
    canvas.paste(bar, (0, 0))
    canvas.paste(im, (0, 30))
    return canvas


def gt7(s, image):
    lbl = SET_DIRS[s] / "labels" / f"{Path(image).stem}.txt"
    m13 = {0: 0, 7: 1, 5: 2, 6: 3, 8: 4, 1: 5, 2: 6}
    out = []
    for l in lbl.read_text(encoding="utf-8").splitlines():
        p = l.split()
        if len(p) < 5:
            continue
        c = int(float(p[0]))
        if s in ("cauca_s10", "exdark_test"):
            pass
        elif c in m13:
            c = m13[c]
        else:
            continue
        cx, cy, w, h = (float(v) for v in p[1:5])
        out.append((c, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    return out


def examples(res):
    ms = [m for m in ("A", "B", "C") if (OUT / f"preds_{m}.json").exists()]
    if "A" not in ms or "C" not in ms:
        print("examples skipped: need preds_A.json and preds_C.json")
        return
    preds = {m: json.loads((OUT / f"preds_{m}.json").read_text(encoding="utf-8")) for m in ms}
    hits = {m: load_hits(m) for m in ms}
    (OUT / "examples").mkdir(exist_ok=True)
    rows = []
    for (s, image), why in pick_frames(hits):
        img_path = SET_DIRS[s] / "images" / image
        g = gt7(s, image)
        n_person = sum(1 for x in g if x[0] == 0)
        panels = []
        for m in ms:
            k = sum(int(hits[m][(s, image, str(i))]["hit_iou0.5"]) for i, x in enumerate(g) if x[0] == 0
                    and (s, image, str(i)) in hits[m])
            panels.append(draw_panel(img_path, g, preds[m][s].get(image, []), m, f"{m}: {k}/{n_person} people found"))
        Wt, Ht = sum(p.width for p in panels), max(p.height for p in panels)
        head = Image.new("RGB", (Wt, 34), "#fcfcfb")
        ImageDraw.Draw(head).text((8, 7), f"{s} / {image}  -  {why}   (white = ground-truth person)", fill="#0b0b0b", font=font(17))
        row = Image.new("RGB", (Wt, Ht + 34), "black")
        row.paste(head, (0, 0))
        x = 0
        for p in panels:
            row.paste(p, (x, 34))
            x += p.width
        row.save(OUT / "examples" / f"{s}__{Path(image).stem}.jpg", quality=88)
        rows.append(row)
    if rows:
        Wm = max(r.width for r in rows)
        sheet = Image.new("RGB", (Wm, sum(r.height for r in rows)), "black")
        y = 0
        for r in rows:
            sheet.paste(r, (0, y))
            y += r.height
        sheet.thumbnail((2400, 100000))
        sheet.save(OUT / "examples_sheet.jpg", quality=85)
        print(f"wrote examples_sheet.jpg ({len(rows)} frames)")


if __name__ == "__main__":
    curves()
    sp = OUT / "v8_scores.json"
    if sp.exists():
        r = json.loads(sp.read_text(encoding="utf-8"))
        if r.get("paired"):
            recall_chart(r)
            examples(r)

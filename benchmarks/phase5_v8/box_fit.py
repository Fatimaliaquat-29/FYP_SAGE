"""How well do predicted person boxes fit the hand-labelled boxes? (our own test footage only)

For every ground-truth person box in reserved388_partial + round6_heldout (images de-duplicated), take the
model's best-overlapping person prediction (conf >= 0.4, the scoring threshold) and measure:
  IoU, coverage = share of the labelled box the prediction covers (low = too tight / cuts the person),
  area ratio = predicted area / labelled area (>1 = looser than the label, <1 = tighter).
Writes box_fit/box_fit_stats.md, box_fit/box_fit_sheet_<M>.jpg (close-up crops, tight -> loose).
Read-only on the test sets; uses preds_<M>.json written by score_v8.py.
"""
import json
import statistics as st
from pathlib import Path

from PIL import Image, ImageDraw

import plot_v8 as pv

OUT = pv.OUT / "box_fit"
SETS = ["reserved388_partial", "round6_heldout"]   # own footage; heldout_objects frames are also in reserved388
MATCH_IOU = 0.3


def iou_cov(g, p):
    ix = max(0, min(g[2], p[2]) - max(g[0], p[0]))
    iy = max(0, min(g[3], p[3]) - max(g[1], p[1]))
    inter = ix * iy
    ag = (g[2] - g[0]) * (g[3] - g[1])
    ap = (p[2] - p[0]) * (p[3] - p[1])
    return inter / (ag + ap - inter + 1e-12), inter / (ag + 1e-12), ap / (ag + 1e-12)


def pairs(model):
    preds = json.loads((pv.OUT / f"preds_{model}.json").read_text(encoding="utf-8"))
    seen, out, n_gt = set(), [], 0
    for s in SETS:
        for image, pl in sorted(preds[s].items()):
            if image in seen:
                continue
            seen.add(image)
            gts = [g[1:] for g in pv.gt7(s, image) if g[0] == 0]
            pp = [p[2:] for p in pl if p[1] == 0 and p[0] >= 0.4]
            for g in gts:
                n_gt += 1
                best = max(((iou_cov(g, p), p) for p in pp), key=lambda t: t[0][0], default=None)
                if best and best[0][0] >= MATCH_IOU:
                    (iou, cov, ar), p = best
                    out.append({"set": s, "image": image, "g": g, "p": p, "iou": iou, "cov": cov, "ar": ar})
    return out, n_gt


def crop_panel(r, model):
    im = Image.open(pv.SET_DIRS[r["set"]] / "images" / r["image"]).convert("RGB")
    W, H = im.size
    g, p = r["g"], r["p"]
    x1, y1 = min(g[0], p[0]) * W, min(g[1], p[1]) * H
    x2, y2 = max(g[2], p[2]) * W, max(g[3], p[3]) * H
    m = 0.35 * max(x2 - x1, y2 - y1)
    box = (max(0, x1 - m), max(0, y1 - m), min(W, x2 + m), min(H, y2 + m))
    c = im.crop(box)
    s = 300 / c.height
    c = c.resize((max(1, int(c.width * s)), 300))
    d = ImageDraw.Draw(c)
    def sc(b):
        return [(b[0] * W - box[0]) * s, (b[1] * H - box[1]) * s, (b[2] * W - box[0]) * s, (b[3] * H - box[1]) * s]
    d.rectangle(sc(g), outline="white", width=3)
    d.rectangle(sc(p), outline=pv.COLORS[model], width=3)
    cap = Image.new("RGB", (max(c.width, 260), 58), "#202020")
    dc = ImageDraw.Draw(cap)
    dc.text((6, 4), f"covers {r['cov']:.0%} of label | IoU {r['iou']:.2f}", fill="white", font=pv.font(14))
    dc.text((6, 22), f"box size vs label: {r['ar']:.2f}x", fill="white", font=pv.font(14))
    dc.text((6, 40), f"{Path(r['image']).stem}"[:38], fill="#b0b0b0", font=pv.font(11))
    canvas = Image.new("RGB", (cap.width, 358), "black")
    canvas.paste(c, (0, 0))
    canvas.paste(cap, (0, 300))
    return canvas


def sheet(rows, model):
    rows = sorted(rows, key=lambda r: r["ar"])
    n = 10
    pick = [rows[round(i * (len(rows) - 1) / (n - 1))] for i in range(n)]   # evenly spaced from tightest to loosest
    panels = [crop_panel(r, model) for r in pick]
    cols, pw = 5, max(p.width for p in panels)
    head = 70
    out = Image.new("RGB", (cols * pw, head + 2 * 358), "#111111")
    d = ImageDraw.Draw(out)
    d.text((10, 8), f"Model {model}: person box fit on our test footage (reserved388_partial + round6_heldout)",
           fill="white", font=pv.font(20))
    d.text((10, 38), f"White = hand-labelled box, colour = model box. 10 matched people, evenly spaced from the "
           f"tightest (top left) to the loosest (bottom right) of {len(rows)}.", fill="#cccccc", font=pv.font(15))
    for i, p in enumerate(panels):
        out.paste(p, ((i % cols) * pw, head + (i // cols) * 358))
    out.save(OUT / f"box_fit_sheet_{model}.jpg", quality=90)


def q(v, f):
    v = sorted(v)
    return v[min(len(v) - 1, int(f * len(v)))]


def main():
    OUT.mkdir(exist_ok=True)
    lines = ["# Person box fit on our own test footage (PROVISIONAL labels)", "",
             f"Sets: {', '.join(SETS)} (images de-duplicated). Each hand-labelled person box is paired with the model's "
             f"best-overlapping person box (conf >= 0.4); pairs with IoU < {MATCH_IOU} count as missed.", "",
             "- **coverage** = share of the labelled box the model's box covers (below ~90% = the box cuts off part of the person)",
             "- **size ratio** = model box area / labelled box area (above 1 = looser than the label, below 1 = tighter)", "",
             "| model | labelled people | matched | median IoU | median coverage | matched boxes covering >= 90% | "
             "median size ratio | size ratio 10th-90th pct |",
             "|---|---|---|---|---|---|---|---|"]
    for m in ("A", "B", "C"):
        rows, n_gt = pairs(m)
        cov = [r["cov"] for r in rows]
        ar = [r["ar"] for r in rows]
        lines.append(f"| {m} | {n_gt} | {len(rows)} | {st.median(r['iou'] for r in rows):.2f} | {st.median(cov):.0%} | "
                     f"{sum(c >= 0.9 for c in cov)}/{len(rows)} | {st.median(ar):.2f} | {q(ar, 0.1):.2f}-{q(ar, 0.9):.2f} |")
        sheet(rows, m)
    lines += ["", "Close-up sheets: box_fit_sheet_A.jpg, box_fit_sheet_B.jpg, box_fit_sheet_C.jpg."]
    (OUT / "box_fit_stats.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

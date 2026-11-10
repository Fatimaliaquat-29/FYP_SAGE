"""Draw labels on a fixed random sample of new-source training images (CAUCAFall + ExDark) into contact sheets.
Own labels green, pseudo-labels (from pseudo_labels_new_sources.csv) orange. Writes spotcheck_*.jpg here."""
import csv
import random
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase5_v8"
FULL = ROOT / "datasets" / "sage_v8_full"
NAMES = ["person", "bed", "chair", "sofa", "table", "bottle", "cup"]

pseudo = defaultdict(set)
for r in csv.DictReader(open(OUT / "pseudo_labels_new_sources.csv", encoding="utf-8")):
    pseudo[r["image"]].add((r["xc"], r["yc"]))


def sheet(prefix, n, out, prefer=None):
    imgs = sorted(p for p in (FULL / "images" / "train").iterdir() if p.name.startswith(prefix))
    rnd = random.Random(7)
    pick = rnd.sample(imgs, n // 2) + rnd.sample([p for p in imgs if prefer and p.name in prefer] or imgs, n - n // 2)
    tiles = []
    for p in pick:
        im = Image.open(p).convert("RGB")
        W, H = im.size
        d = ImageDraw.Draw(im)
        for l in (FULL / "labels" / "train" / f"{p.stem}.txt").read_text().splitlines():
            c, xc, yc, w, h = l.split()
            col = "orange" if (xc, yc) in pseudo.get(p.name, ()) else "lime"
            x1, y1 = (float(xc) - float(w) / 2) * W, (float(yc) - float(h) / 2) * H
            x2, y2 = (float(xc) + float(w) / 2) * W, (float(yc) + float(h) / 2) * H
            d.rectangle([x1, y1, x2, y2], outline=col, width=max(2, W // 200))
            d.text((x1 + 3, y1 + 2), NAMES[int(c)], fill=col)
        im.thumbnail((480, 360))
        tiles.append(im)
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new("RGB", (cols * 480, rows * 360), "black")
    for i, t in enumerate(tiles):
        S.paste(t, ((i % cols) * 480, (i // cols) * 360))
    S.save(OUT / out, quality=88)
    print("wrote", out, [p.name for p in pick])


sheet("cauca_", 12, "spotcheck_caucafall.jpg", prefer={k for k in pseudo if k.startswith("cauca_")})
sheet("exdark_", 12, "spotcheck_exdark.jpg", prefer={k for k in pseudo if k.startswith("exdark_")})

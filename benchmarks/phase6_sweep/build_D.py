"""Build datasets/sage_v8_fixclips (run D) = sage_v8_full (C's data) + the 4 problem clips re-added after filtering.

Why: dropping the 4 clips whole (phase 5) also removed 1,260 good bed boxes; C's bed recall on the
With_people_Bedroom held-out clips fell from 19/128 (A) to 1/128.

Filter, per frame (an _r1 repeat copy always follows its base frame), labels mapped to the 7 classes as in phase 5:
  1. Blanket_Cover_HM frames 710-1420 -> DROP (teammate: the box is on a blanket, not a person).
  2. Hand-labelled frames of Sitting_Dim_HM / Standing_Walking_Dim_HM (round6_patch) and Blanket_Cover_HM outside
     710-1420 -> KEEP (human-drawn; the teammates' complaints are about MediaPipe boxes / the blanket span).
  3. Everything else (MediaPipe frames of the two Dim clips, all of Bedroom_Falll) -> VET with model C, which never
     saw these clips: KEEP only if every labelled person box matches a C person prediction (conf >= 0.25, IoU >= 0.5)
     and C has no unmatched person prediction at conf >= 0.5. Otherwise DROP the whole frame (no half-labelled frames).
Reads originals only; images are hardlinks (real copy for JPEGs lacking the FFD9 end marker), labels are new files.
Writes OUT/build_D_report.json, OUT/build_D_decisions.csv, OUT/spotcheck_D.jpg, and the BUILD_OK flag last.
"""
import csv
import re
import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase6_sweep"
P5 = ROOT / "benchmarks" / "phase5_v8"
sys.path.insert(0, str(P5))
import build_v8 as bv  # noqa: E402  (helpers only: link, write_label, V7_MAP, NAMES)

FULL = ROOT / "datasets" / "sage_v8_full"
DST = ROOT / "datasets" / "sage_v8_fixclips"
V7 = ROOT / "datasets" / "sage_merged_v7"
MODEL_C = P5 / "runs" / "C" / "weights" / "best.pt"
PROV = ROOT / "benchmarks" / "phase3_a2" / "a1_provenance.csv"
BLANKET_SPAN = (710, 1420)


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy
    return i / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i + 1e-12)


def xyxy(p):
    cx, cy, w, h = (float(v) for v in p[1:5])
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]


def main():
    if DST.exists():
        sys.exit(f"STOP: {DST} exists")
    copies, report = [], {"base_copy": Counter(), "decisions": Counter(), "decisions_by_clip": defaultdict(Counter),
                          "added_images": 0, "added_boxes": Counter()}
    # 1. copy C's data
    for split in ("train", "val"):
        for img in (FULL / "images" / split).iterdir():
            bv.link(img, DST / "images" / split / img.name, copies)
            lbl = FULL / "labels" / split / f"{img.stem}.txt"
            bv.write_label(DST / "labels" / split / f"{img.stem}.txt",
                           lbl.read_text(encoding="utf-8").splitlines() if lbl.exists() else [])
            report["base_copy"][split] += 1
    print("base copy", dict(report["base_copy"]), flush=True)

    # 2. candidate frames of the 4 clips
    prov = [r for r in csv.DictReader(open(PROV, encoding="utf-8"))
            if r["prefix"] == "own" and r["clip"] in bv.DROP_CLIPS]
    by_base = defaultdict(list)
    for r in prov:
        by_base[re.sub(r"_r\d+$", "", r["stem"])].append(r)   # base = own_<clip>_<frame> (base_stem column lacks "own_")
    bases = sorted(by_base)

    def img_of(stem):
        hits = list((V7 / "images" / "train").glob(f"{stem}.*"))
        return hits[0] if hits else None

    def labels7(stem):
        lbl = V7 / "labels" / "train" / f"{stem}.txt"
        out = []
        for l in (lbl.read_text(encoding="utf-8").splitlines() if lbl.exists() else []):
            p = l.split()
            if len(p) >= 5 and int(float(p[0])) in bv.V7_MAP:
                out.append(" ".join([str(bv.V7_MAP[int(float(p[0]))])] + p[1:5]))
        return out

    # 3. model C predictions on the frames that need vetting
    from ultralytics import YOLO
    need, decision = [], {}
    for b in bases:
        r0 = next((r for r in by_base[b] if r["repeat_copy"] == "0"), by_base[b][0])
        clip, hand = r0["clip"], r0["provenance"].startswith("hand")
        frame = int(b.rsplit("_", 1)[-1])
        if clip == "Blanket_Cover_HM" and BLANKET_SPAN[0] <= frame <= BLANKET_SPAN[1]:
            decision[b] = ("drop", "blanket span 710-1420 (teammate)")
        elif hand and clip != "Bedroom_Falll":
            decision[b] = ("keep", "hand-labelled")
        else:
            need.append(b)
    m = YOLO(str(MODEL_C))
    preds = {}
    for i in range(0, len(need), 32):
        chunk = need[i:i + 32]
        res = m.predict([str(img_of(b)) for b in chunk], conf=0.25, imgsz=640, device=0, verbose=False)
        for b, r in zip(chunk, res):
            preds[b] = [(float(c), [float(v) for v in xy]) for c, k, xy in
                        zip(r.boxes.conf.tolist(), r.boxes.cls.tolist(), r.boxes.xyxyn.tolist()) if int(k) == 0]
    for b in need:
        gts = [xyxy(l.split()) for l in labels7(b) if l.split()[0] == "0"]
        pp = preds[b]
        matched = set()
        ok = True
        for g in gts:
            best = max(range(len(pp)), key=lambda j: iou(g, pp[j][1]), default=None)
            if best is None or iou(g, pp[best][1]) < 0.5:
                ok = False
                break
            matched.add(best)
        extra = [j for j, (c, _) in enumerate(pp) if j not in matched and c >= 0.5]
        if ok and not extra:
            decision[b] = ("keep", "vetted: model C agrees")
        elif not ok:
            decision[b] = ("drop", "vetted: a labelled person box not confirmed by C")
        else:
            decision[b] = ("drop", "vetted: C sees an unlabelled person")

    # 4. write kept frames (base + repeat copies)
    rows = []
    for b in bases:
        act, why = decision[b]
        clip = by_base[b][0]["clip"]
        report["decisions"][f"{act}: {why}"] += 1
        report["decisions_by_clip"][clip][act] += 1
        for r in by_base[b]:
            rows.append({"stem": r["stem"], "base_stem": b, "clip": clip, "provenance": r["provenance"],
                         "decision": act, "reason": why})
            if act != "keep":
                continue
            src = img_of(r["stem"])
            lines = labels7(r["stem"])
            bv.link(src, DST / "images" / "train" / src.name, copies)
            bv.write_label(DST / "labels" / "train" / f"{r['stem']}.txt", lines)
            report["added_images"] += 1
            for l in lines:
                report["added_boxes"][bv.NAMES[int(l.split()[0])]] += 1
    with open(OUT / "build_D_decisions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    bv.write_yaml(DST, "D: C's data + the 4 problem clips re-added after filtering (benchmarks/phase6_sweep).")

    # 5. spot-check sheet: 8 kept-by-vetting, 8 dropped-by-vetting, 4 hand-kept
    def thumb(b, tag):
        im = Image.open(img_of(b)).convert("RGB")
        im.thumbnail((400, 300))
        W, H = im.size
        d = ImageDraw.Draw(im)
        for l in labels7(b):
            p = l.split()
            x = xyxy(p)
            d.rectangle([x[0] * W, x[1] * H, x[2] * W, x[3] * H], outline="white" if p[0] == "0" else "#888888",
                        width=3 if p[0] == "0" else 1)
        for c, x in preds.get(b, []):
            d.rectangle([x[0] * W, x[1] * H, x[2] * W, x[3] * H], outline="#1baf7a", width=2)
        d.rectangle([0, 0, W, 20], fill="#202020")
        d.text((4, 3), f"{tag}: {b[4:]}"[:60], fill="white")
        return im
    pick = []
    for want, n in (("vetted: model C agrees", 8), ("vetted: a labelled person box not confirmed by C", 6),
                    ("vetted: C sees an unlabelled person", 2), ("hand-labelled", 4)):
        cands = [b for b in bases if decision[b][1] == want]
        pick += [(b, ("KEEP " if decision[b][0] == "keep" else "DROP ") + want.split(":")[-1].strip()[:28])
                 for b in cands[:: max(1, len(cands) // n)][:n]]
    if pick:
        th = [thumb(b, t) for b, t in pick]
        cols = 4
        sheet = Image.new("RGB", (cols * 400, ((len(th) + cols - 1) // cols) * 300), "black")
        for i, t in enumerate(th):
            sheet.paste(t, ((i % cols) * 400, (i // cols) * 300))
        sheet.save(OUT / "spotcheck_D.jpg", quality=88)

    # 6. verify and flag
    ver = {}
    for split in ("train", "val"):
        ni = sum(1 for _ in (DST / "images" / split).iterdir())
        nl = sum(1 for p in (DST / "labels" / split).iterdir() if p.suffix == ".txt")
        ver[split] = {"images": ni, "labels": nl}
    ok = all(v["images"] == v["labels"] for v in ver.values()) and \
        ver["train"]["images"] == report["base_copy"]["train"] + report["added_images"]
    report.update({"verify": ver, "ALL_OK": ok, "real_copies": copies})
    (OUT / "build_D_report.json").write_text(json.dumps(report, indent=2, default=dict), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("decisions", "decisions_by_clip", "added_images", "added_boxes", "verify",
                                             "ALL_OK")}, indent=1, default=dict))
    if ok:
        (DST / "BUILD_OK").write_text("ok", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

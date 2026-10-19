"""Label-quality audit of datasets/sage_merged_v7 TRAIN split. Read-only on ROOT; writes only to OUT.
Never loads the dataset through data.yaml / ultralytics train/val (that rewrites labels/*.cache): images and
label .txt files are read with plain Python, and the detector is called with model.predict(<image paths>).

Steps: inventory, leakage, darkness, automatic flags, audit-sheet sample + contact sheets.
"""
import csv
import datetime as dt
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
import cv2
import numpy as np
import yaml

ROOT = Path(r"D:\FYP\PROJECT FILES\fatima")
OUT = ROOT / "benchmarks" / "label_audit"
DS = ROOT / "datasets" / "sage_merged_v7"
IMG = DS / "images" / "train"
LAB = DS / "labels" / "train"
EVAL_DIRS = {"eval/heldout_objects": ROOT / "eval" / "heldout_objects" / "images",
             "handlabels/round6_heldout": ROOT / "handlabels" / "round6_heldout" / "images"}
HAND_DIRS = {"round5": ROOT / "handlabels/round5/labels", "round6": ROOT / "handlabels/round6/labels",
             "round6_patch": ROOT / "handlabels/round6_patch/labels"}
DET_WEIGHTS = [ROOT / "benchmarks/overnight_yolo26/weights/yolo26s.pt", ROOT / "yolo26n.pt"]
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}
SEED = 0
CONF_HI, CONF_LO, IOU_T, IMGSZ = 0.5, 0.25, 0.3, 640
RAW = OUT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
(OUT / "sheets").mkdir(exist_ok=True)


def log(m):
    print(f"[{dt.datetime.now():%H:%M:%S}] {m}", flush=True)


def decision(t):
    with open(OUT / "DECISIONS.md", "a", encoding="utf-8") as f:
        f.write(f"- [{dt.datetime.now():%Y-%m-%d %H:%M}] {t}\n")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read_labels(p):
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.split()
        if len(s) >= 5:
            c = int(float(s[0]))
            cx, cy, w, h = map(float, s[1:5])
            out.append((c, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    return out


def iou(a, b):
    ix1, iy1, ix2, iy2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / u if u > 0 else 0.0


def parse_name(name):
    stem = Path(name).stem
    top = stem.split("_", 1)[0]
    rep = re.search(r"_r(\d+)$", stem)
    base = stem[: rep.start()] if rep else stem
    inner = base[len(top) + 1:]
    clip = re.sub(r"_\d+$", "", inner) if top != "coco" else "coco"
    return top, clip, inner, (int(rep.group(1)) if rep else 0)


def main():
    R = {"generated": dt.datetime.now().isoformat(timespec="seconds")}
    # ---- class order check (plain yaml read, no ultralytics) ----
    sc = {}
    exec((ROOT / "src/detection/sage_classes.py").read_text(encoding="utf-8"), sc)
    names = yaml.safe_load((DS / "data.yaml").read_text(encoding="utf-8"))["names"]
    names = [names[i] for i in sorted(names)] if isinstance(names, dict) else list(names)
    R["class_check"] = {"sage_classes": sc["SAGE_CLASSES"], "data_yaml_names": names, "match": sc["SAGE_CLASSES"] == names}

    # ---- 1. inventory ----
    log("inventory")
    imgs = sorted(p for p in IMG.iterdir() if p.suffix.lower() in IMG_EXT)
    labs = {p.stem: p for p in LAB.glob("*.txt")}
    hand = {}
    for k, d in HAND_DIRS.items():
        for f in d.glob("*.txt"):
            if f.name != "classes.txt":
                hand[f.stem] = k
    rows = []
    bad_cls = Counter()
    for p in imgs:
        top, clip, inner, rep = parse_name(p.name)
        lp = labs.get(p.stem)
        boxes = read_labels(lp) if lp else None
        if boxes:
            for b in boxes:
                if not 0 <= b[0] < len(names):
                    bad_cls[b[0]] += 1
        prov = {"coco": "coco (external, human-drawn)", "empty": "empty-room (no person by construction)"}.get(top)
        if top == "own":
            prov = f"hand-drawn ({hand[inner]})" if inner in hand else "MediaPipe-derived"
        rows.append({"filename": p.name, "top": top, "clip": clip, "inner": inner, "repeat": rep, "provenance": prov,
                     "has_label": lp is not None, "label_empty": (lp is not None and not boxes),
                     "n_person": sum(1 for b in boxes if b[0] == 0) if boxes else 0,
                     "n_other": sum(1 for b in boxes if b[0] != 0) if boxes else 0})
    img_stems = {p.stem for p in imgs}
    R["inventory"] = {"images": len(imgs), "label_files": len(labs), "images_without_label_file": sum(not r["has_label"] for r in rows),
                      "images_with_empty_label_file": sum(r["label_empty"] for r in rows),
                      "label_files_without_image": len(set(labs) - img_stems),
                      "out_of_schema_class_boxes": dict(bad_cls)}

    def agg(key):
        g = defaultdict(lambda: {"images": 0, "person_boxes": 0, "zero_person": 0, "repeat_copies": 0})
        for r in rows:
            e = g[r[key]]
            e["images"] += 1
            e["person_boxes"] += r["n_person"]
            e["zero_person"] += r["n_person"] == 0
            e["repeat_copies"] += r["repeat"] > 0
        for e in g.values():
            e["mean_person_per_image"] = e["person_boxes"] / e["images"]
            e["pct_zero_person"] = 100 * e["zero_person"] / e["images"]
        return dict(sorted(g.items()))
    R["by_top"] = agg("top")
    R["by_clip"] = agg("clip")
    R["by_provenance"] = agg("provenance")

    # ---- md5 (duplicates + leakage) ----
    log("md5 of train images")
    for r, p in zip(rows, imgs):
        r["md5"] = md5(p)
    by_md5 = defaultdict(list)
    for r in rows:
        by_md5[r["md5"]].append(r["filename"])
    rep_rows = [r for r in rows if r["repeat"] > 0]
    orig = {(r["top"], r["inner"]): r for r in rows if r["repeat"] == 0}
    rep_identical = sum(1 for r in rep_rows if (r["top"], r["inner"]) in orig and orig[(r["top"], r["inner"])]["md5"] == r["md5"])
    R["duplicates"] = {"repeat_copies": len(rep_rows), "repeat_copies_md5_identical_to_original": rep_identical,
                       "md5_groups_with_more_than_1_file": sum(1 for v in by_md5.values() if len(v) > 1),
                       "files_in_duplicate_groups_that_are_not_rN_copies": sum(len(v) - 1 for v in by_md5.values() if len(v) > 1) - rep_identical}
    log("leakage")
    leak = {}
    train_md5 = set(by_md5)
    train_names = {r["filename"] for r in rows}
    train_inner = {r["inner"] for r in rows}
    for k, d in EVAL_DIRS.items():
        ev = [p for p in d.iterdir() if p.suffix.lower() in IMG_EXT]
        hashes = {p.name: md5(p) for p in ev}
        leak[k] = {"eval_images": len(ev), "filename_overlap": sum(p.name in train_names for p in ev),
                   "filename_overlap_after_stripping_source_prefix": sum(p.stem in train_inner for p in ev),
                   "md5_overlap": sum(h in train_md5 for h in hashes.values()),
                   "examples": [p.name for p in ev if p.stem in train_inner or hashes[p.name] in train_md5][:10]}
    R["leakage"] = leak

    # ---- 3. darkness ----
    log("luma")
    for r, p in zip(rows, imgs):
        im = cv2.imread(str(p))
        r["luma"] = float(cv2.cvtColor(im, cv2.COLOR_BGR2YCrCb)[:, :, 0].mean()) if im is not None else None
        r["h"], r["w"] = (im.shape[:2] if im is not None else (None, None))
    lv = np.array([r["luma"] for r in rows if r["luma"] is not None])
    t1, t2 = float(np.percentile(lv, 100 / 3)), float(np.percentile(lv, 200 / 3))
    for r in rows:
        r["dark_bucket"] = "dark" if r["luma"] <= t1 else ("bright" if r["luma"] >= t2 else "mid")
    R["darkness"] = {"definition": "mean Y (YCrCb) per image; dark = <= 33.33rd percentile over ALL train images, bright = >= 66.67th",
                     "dark_max_luma": t1, "bright_min_luma": t2,
                     "by_top_bucket": {t: dict(Counter(r["dark_bucket"] for r in rows if r["top"] == t)) for t in R["by_top"]}}

    # ---- 4. automatic flags ----
    pop = [r for r in rows if r["top"] in ("own", "empty") and r["repeat"] == 0]
    stride = 2 if len(pop) > 6000 else 1
    pop = pop[::stride]
    assert len(pop) > 0
    R["auto_flags_setup"] = {"population": "own_ + empty_ images (own footage; empty_ names match yolo_testing/Training/Empty clips), "
                                          "excluding _rN repeat copies (md5-identical duplicates)",
                             "n_checked": len(pop), "stride": stride, "conf_detect": CONF_HI, "conf_phantom_support": CONF_LO,
                             "iou_threshold": IOU_T, "imgsz": IMGSZ}
    from ultralytics import YOLO
    w = next((p for p in DET_WEIGHTS if p.exists()), None)
    R["auto_flags_setup"]["detector"] = str(w)
    R["auto_flags_setup"]["detector_md5"] = md5(w)
    model = YOLO(str(w))
    assert model.names[0] == "person"
    log(f"detector {w.name} on {len(pop)} images")
    paths = [str(IMG / r["filename"]) for r in pop]
    dets = {}
    for i in range(0, len(paths), 32):
        batch = paths[i:i + 32]
        # res.path is 'imageN.jpg' for list input, so pair results with the inputs by order
        for pth, res in zip(batch, model.predict(batch, conf=CONF_LO, imgsz=IMGSZ, classes=[0], verbose=False, save=False)):
            dets[Path(pth).name] = [(float(b.conf.item()), tuple(float(v) for v in b.xyxyn[0])) for b in res.boxes if int(b.cls.item()) == 0]
        if i % 640 == 0:
            log(f"  {i}/{len(paths)}")
    for r in pop:
        gt = [b[1:] for b in read_labels(LAB / f"{Path(r['filename']).stem}.txt") if b[0] == 0] if r["has_label"] else []
        d = dets.get(r["filename"], [])
        hi = [x for x in d if x[0] >= CONF_HI]
        miss = [x for x in hi if max((iou(x[1], g) for g in gt), default=0.0) < IOU_T]
        phantom = [g for g in gt if max((iou(x[1], g) for x in d), default=0.0) < IOU_T]
        r.update(checked=True, n_det50=len(hi), n_missing=len(miss), n_phantom=len(phantom),
                 missing_max_conf=max((x[0] for x in miss), default=None),
                 gt_horizontal=any((g[2] - g[0]) * r["w"] > (g[3] - g[1]) * r["h"] for g in gt) if gt and r["w"] else False)
        dets[r["filename"]] = d
    assert sum(1 for r in pop if r["n_det50"]) > 0.3 * sum(1 for r in pop if r["n_person"]), "detector output looks empty"
    json.dump({k: v for k, v in dets.items() if k in {r["filename"] for r in pop}}, open(RAW / "detections.json", "w"))

    def flag_table(key):
        g = defaultdict(lambda: {"checked": 0, "with_missing": 0, "with_phantom": 0, "gt_person_boxes": 0, "phantom_boxes": 0})
        for r in pop:
            for k in (r[key], "ALL"):
                e = g[k]
                e["checked"] += 1
                e["with_missing"] += r["n_missing"] > 0
                e["with_phantom"] += r["n_phantom"] > 0
                e["gt_person_boxes"] += r["n_person"]
                e["phantom_boxes"] += r["n_phantom"]
        for e in g.values():
            e["pct_missing"] = 100 * e["with_missing"] / e["checked"]
            e["pct_phantom"] = 100 * e["with_phantom"] / e["checked"]
        return dict(sorted(g.items()))
    for r in pop:
        r["lying_proxy"] = "GT person box wider than tall" if r["gt_horizontal"] else ("no GT person" if r["n_person"] == 0 else "GT person box taller than wide")
    R["flags_by_top"] = flag_table("top")
    R["flags_by_clip"] = flag_table("clip")
    R["flags_by_provenance"] = flag_table("provenance")
    R["flags_by_dark_bucket"] = flag_table("dark_bucket")
    R["flags_by_lying_proxy"] = flag_table("lying_proxy")
    for r in pop:
        r["prov_x_dark"] = f"{r['provenance']} | {r['dark_bucket']}"
    R["flags_by_provenance_x_dark"] = flag_table("prov_x_dark")

    with open(OUT / "train_images.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["filename", "top", "clip", "provenance", "repeat", "has_label", "label_empty", "n_person", "n_other", "md5",
                "luma", "dark_bucket", "w", "h", "checked", "n_det50", "n_missing", "n_phantom", "missing_max_conf", "gt_horizontal"]
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)

    # ---- 5. audit sample ----
    rng = random.Random(SEED)
    sel, reason = [], {}

    def take(cands, n, why):
        cands = [c for c in cands if c["filename"] not in reason]
        rng.shuffle(cands)
        got = 0
        for c in cands:
            if got >= n:
                break
            reason[c["filename"]] = why
            sel.append(c)
            got += 1
        return got
    short = {}
    short["random"] = 40 - take(list(pop), 40, "random")
    short["suspected_missing"] = 40 - take([r for r in pop if r["n_missing"] > 0], 40, "suspected_missing")
    short["suspected_phantom"] = 20 - take([r for r in pop if r["n_phantom"] > 0], 20, "suspected_phantom")
    own = [r for r in pop if r["top"] == "own"]
    cut = float(np.percentile([r["luma"] for r in own], 10))
    short["darkest_10pct_own"] = 20 - take([r for r in own if r["luma"] <= cut], 20, "darkest_10pct_own")
    fill = sum(short.values())
    if fill:
        take(list(pop), fill, "random_fill")
        decision(f"Audit sample: {short} short after dedupe; filled {fill} from uniform random ('random_fill').")
    R["sample"] = {"n": len(sel), "short_filled": short, "darkest_10pct_own_luma_cut": cut, "seed": SEED}
    render_sheets(sel, reason, dets, cut)
    json.dump(R, open(RAW / "audit_stats.json", "w"), indent=2, default=str)
    log("done")


def render_sheets(sel, reason, dets, dark_cut):
    TILE = 720
    tiles, recs = [], []
    for i, r in enumerate(sel, 1):
        p = IMG / r["filename"]
        im = cv2.imread(str(p))
        h, w = im.shape[:2]
        disp_bright = r["luma"] <= dark_cut
        if disp_bright:   # display only: CLAHE on L so a human can see anything at all
            lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(lab[:, :, 0])
            im = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        th = max(2, int(round(max(h, w) / 300)))
        gt = read_labels(LAB / f"{Path(r['filename']).stem}.txt") if r["has_label"] else []
        for b in gt:
            pt1, pt2 = (int(b[1] * w), int(b[2] * h)), (int(b[3] * w), int(b[4] * h))
            if b[0] == 0:
                cv2.rectangle(im, pt1, pt2, (0, 255, 0), th * 2)
            else:
                cv2.rectangle(im, pt1, pt2, (170, 170, 170), max(1, th // 2))
        gtp = [b[1:] for b in gt if b[0] == 0]
        for c, bx in dets.get(r["filename"], []):
            if c >= CONF_HI and max((iou(bx, g) for g in gtp), default=0.0) < IOU_T:
                cv2.rectangle(im, (int(bx[0] * w), int(bx[1] * h)), (int(bx[2] * w), int(bx[3] * h)), (0, 0, 255), th * 2)
                cv2.putText(im, f"{c:.2f}", (int(bx[0] * w) + 4, int(bx[1] * h) + 14 * th), cv2.FONT_HERSHEY_SIMPLEX, th * 0.6, (0, 0, 255), th)
        s = TILE / max(h, w)
        im = cv2.resize(im, (int(w * s), int(h * s)))
        tile = np.zeros((TILE, TILE, 3), np.uint8)
        y0, x0 = (TILE - im.shape[0]) // 2, (TILE - im.shape[1]) // 2
        tile[y0:y0 + im.shape[0], x0:x0 + im.shape[1]] = im
        cv2.rectangle(tile, (0, 0), (TILE, 92), (0, 0, 0), -1)
        cv2.putText(tile, f"#{i}", (8, 62), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 255), 4)
        cv2.putText(tile, r["clip"][:34], (150, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        flag = "+".join(x for x, k in (("MISS", "n_missing"), ("PHANTOM", "n_phantom")) if r[k] > 0) or "-"
        cv2.putText(tile, f"{reason[r['filename']]} | flag {flag} | luma {r['luma']:.0f}{' | DISPLAY BRIGHTENED' if disp_bright else ''}",
                    (150, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        tiles.append(tile)
        recs.append({"idx": i, "filename": r["filename"], "source": r["clip"], "luma": round(r["luma"], 1),
                     "sampling_reason": reason[r["filename"]], "auto_flag": flag, "verdict_human": "", "notes_human": "",
                     "verdict_ai": "", "notes_ai": ""})
    for s in range(0, len(tiles), 9):
        grid = tiles[s:s + 9] + [np.zeros((TILE, TILE, 3), np.uint8)] * (9 - len(tiles[s:s + 9]))
        rows_ = [np.hstack(grid[k:k + 3]) for k in (0, 3, 6)]
        cv2.imwrite(str(OUT / "sheets" / f"sheet_{s // 9 + 1:02d}.jpg"), np.vstack(rows_), [cv2.IMWRITE_JPEG_QUALITY, 88])
    with open(OUT / "audit_sheet.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(recs[0]))
        wr.writeheader()
        wr.writerows(recs)
    with open(RAW / "sample_meta.json", "w") as f:
        json.dump({r["filename"]: {"provenance": r["provenance"], "top": r["top"], "dark_bucket": r["dark_bucket"],
                                   "lying_proxy": r["lying_proxy"]} for r in sel}, f, indent=1)


if __name__ == "__main__":
    main()

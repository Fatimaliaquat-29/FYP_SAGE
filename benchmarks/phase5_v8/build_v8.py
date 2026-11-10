"""Phase 5: build the two training sets and the two new held-out tests (see PLAN.md).

  datasets/sage_v8_clean        (B)  v7 minus the 4 problem clips, labels rewritten to the 7-class IDs
  datasets/sage_v8_full         (C)  B + CAUCAFall (subjects 1-8 train, 9 val) + ExDark indoor (train, val half)
  datasets/sage_v8_heldout_new       cauca_s10/ and exdark_test/: never trained on, own labels only (no pseudo)

Reads the originals, never writes to them. Images are hardlinks (same volume), except a JPEG not ending in FFD9,
which gets a real copy (Ultralytics re-saves such files in place, which through a hardlink would rewrite the
original). Labels are newly written files. Missing classes in the new sources are pseudo-labelled the way v7's own
footage was (stock models/yolov8n.pt, conf 0.35, its person boxes discarded).

Usage: python -u build_v8.py   (cwd = benchmarks/phase5_v8)
"""
import csv
import json
import os
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase5_v8"
V7 = ROOT / "datasets" / "sage_merged_v7"
CLEAN = ROOT / "datasets" / "sage_v8_clean"
FULL = ROOT / "datasets" / "sage_v8_full"
HELD = ROOT / "datasets" / "sage_v8_heldout_new"
NEW = ROOT / "new datasets"
CA = NEW / "CAUCAFall" / "extracted" / "Dataset CAUCAFall" / "CAUCAFall"
EX_IMG = NEW / "ExDark" / "extracted" / "ExDark"
EX_ANN = NEW / "ExDark" / "annotations_download" / "extracted" / "ExDark_Annno"
EX_LIST = NEW / "ExDark" / "annotations_download" / "imageclasslist.txt"
STOCK = ROOT / "models" / "yolov8n.pt"

NAMES = ["person", "bed", "chair", "sofa", "table", "bottle", "cup"]
V7_NAMES = ["person", "bottle", "cup", "wine glass", "bowl", "chair", "couch", "bed",
            "dining table", "toilet", "tv", "sink", "refrigerator"]
V7_MAP = {0: 0, 7: 1, 5: 2, 6: 3, 8: 4, 1: 5, 2: 6}          # v7 id -> new id; others dropped
DROP_CLIPS = {"Sitting_Dim_HM", "Standing_Walking_Dim_HM", "Blanket_Cover_HM", "Bedroom_Falll"}
EX_MAP = {"People": 0, "Chair": 2, "Table": 4, "Bottle": 5, "Cup": 6}
STOCK_TO_NEW = {"bed": 1, "chair": 2, "couch": 3, "dining table": 4, "bottle": 5, "cup": 6}
PSEUDO_FOR = {"cauca": {"bed", "chair", "couch", "dining table", "bottle", "cup"}, "exdark": {"bed", "couch"}}
PSEUDO_CONF = 0.35
CAUCA_STRIDE = 6
CAUCA_SPLIT = {**{f"Subject.{i}": "train" for i in range(1, 9)}, "Subject.9": "val", "Subject.10": "test"}


def ends_ok(p):
    with open(p, "rb") as f:
        f.seek(-2, 2)
        return f.read() == b"\xff\xd9"


def link(src, dst, copies):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in (".jpg", ".jpeg") and not ends_ok(src):
        shutil.copyfile(src, dst)
        copies.append(str(src))
    else:
        os.link(src, dst)


def write_label(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(l + "\n" for l in lines), encoding="utf-8")


def v7_clip(stem):
    """own_<clip>_<frame>[_r1] -> clip; other prefixes -> None."""
    if not stem.startswith("own_"):
        return None
    parts = stem[4:].split("_")
    if parts[-1].startswith("r") and parts[-1][1:].isdigit():
        parts = parts[:-1]
    return "_".join(parts[:-1]) if parts[-1].isdigit() else "_".join(parts)


# ---------------------------------------------------------------- v7 -> 7 classes, problem clips removed
def build_v7_part(dsts, report, copies):
    prov = {r["stem"]: r["clip"] for r in csv.DictReader(open(OUT.parent / "phase3_a2" / "a1_provenance.csv", encoding="utf-8"))
            if r["prefix"] == "own"}
    dropped, dropped_boxes = [], Counter()
    for split in ("train", "val"):
        for img in sorted((V7 / "images" / split).iterdir()):
            if not img.is_file():
                continue
            clip = prov.get(img.stem) if split == "train" else None
            clip = clip or v7_clip(img.stem)
            lbl = V7 / "labels" / split / f"{img.stem}.txt"
            text = lbl.read_text(encoding="utf-8") if lbl.exists() else ""
            if clip in DROP_CLIPS:
                dropped.append({"split": split, "image": img.name, "clip": clip})
                for l in text.splitlines():
                    if l.split():
                        dropped_boxes[V7_NAMES[int(float(l.split()[0]))]] += 1
                continue
            lines, removed = [], 0
            for l in text.splitlines():
                p = l.split()
                if len(p) < 5:
                    continue
                c = int(float(p[0]))
                if c in V7_MAP:
                    lines.append(" ".join([str(V7_MAP[c])] + p[1:5]))
                else:
                    removed += 1
            src_tag = img.stem.split("_")[0]
            report["v7_removed_boxes_dropped_classes"][src_tag] += removed
            if not lines and text.strip():
                report["v7_images_now_empty"][f"{split}/{src_tag}"] += 1
            for d in dsts:
                link(img, d / "images" / split / img.name, copies if d is dsts[0] else [])
                write_label(d / "labels" / split / f"{img.stem}.txt", lines)
            report["images"][f"{split}/v7_{src_tag}"] += 1
            for l in lines:
                report["boxes"][f"{split}/v7_{src_tag}"][NAMES[int(l.split()[0])]] += 1
    with open(OUT / "dropped_problem_clips.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["split", "image", "clip"])
        w.writeheader()
        w.writerows(dropped)
    report["dropped_problem_clip_images"] = dict(Counter(d["clip"] for d in dropped))
    report["dropped_problem_clip_images_by_split"] = dict(Counter(d["split"] for d in dropped))
    report["dropped_problem_clip_boxes_v7names"] = dict(dropped_boxes)


# ---------------------------------------------------------------- new sources
def select_cauca(report):
    items = []
    for subj in sorted(CA.iterdir(), key=lambda p: int(p.name.split(".")[1])):
        for act in sorted(p for p in subj.iterdir() if p.is_dir()):
            labelled = [p for p in sorted(act.glob("*.png")) if p.with_suffix(".txt").exists()]
            report["cauca_unlabelled_skipped"] += len(list(act.glob("*.png"))) - len(labelled)
            for i, p in enumerate(labelled):
                if i % CAUCA_STRIDE:
                    continue
                boxes = []
                for l in p.with_suffix(".txt").read_text(encoding="utf-8").splitlines():
                    q = l.split()
                    if len(q) == 5:
                        boxes.append(" ".join(["0"] + q[1:5]))          # fall / nofall -> person
                name = f"cauca_S{int(subj.name.split('.')[1]):02d}_{act.name.replace(' ', '')}_{p.stem}{p.suffix.lower()}"
                items.append({"src": p, "name": name, "split": CAUCA_SPLIT[subj.name], "own": boxes, "kind": "cauca"})
    return items


def select_exdark(report):
    meta = {}
    for line in EX_LIST.read_text().splitlines()[1:]:
        f = line.split()
        if len(f) == 5:
            meta[f[0]] = {"indoor": f[3] == "1", "split": f[4]}
    items = []
    for cls_dir in sorted(p for p in EX_IMG.iterdir() if p.is_dir()):
        for img in sorted(p for p in cls_dir.iterdir() if p.is_file()):
            m = meta.get(img.name)
            if not m or not m["indoor"]:
                report["exdark_skipped"]["outdoor_or_unlisted"] += 1
                continue
            ann = EX_ANN / cls_dir.name / f"{img.name}.txt"
            raw = [l.split() for l in ann.read_text(errors="replace").splitlines()[1:] if l.strip()] if ann.exists() else []
            kept = [r for r in raw if r[0] in EX_MAP]
            if not kept:
                report["exdark_skipped"]["no_kept_class"] += 1
                continue
            try:
                with Image.open(img) as im:
                    W, H = im.size
                    orient = im.getexif().get(274, 1)
            except Exception:
                report["exdark_skipped"]["unreadable"] += 1
                continue
            if orient not in (0, 1):
                report["exdark_skipped"]["exif_rotated"] += 1
                continue
            boxes = []
            for r in kept:
                l, t, w, h = (float(v) for v in r[1:5])
                x1, y1, x2, y2 = max(0, l), max(0, t), min(W, l + w), min(H, t + h)
                if x2 - x1 < 2 or y2 - y1 < 2:
                    report["exdark_skipped_boxes_degenerate"] += 1
                    continue
                boxes.append(f"{EX_MAP[r[0]]} {(x1 + x2) / 2 / W:.6f} {(y1 + y2) / 2 / H:.6f} {(x2 - x1) / W:.6f} {(y2 - y1) / H:.6f}")
            if not boxes:
                report["exdark_skipped"]["no_valid_box"] += 1
                continue
            num = int("".join(ch for ch in img.stem if ch.isdigit()) or 0)
            split = "train" if m["split"] in ("1", "3") else ("val" if num % 2 == 0 else "test")
            items.append({"src": img, "name": f"exdark_{img.stem}{img.suffix.lower()}", "split": split, "own": boxes,
                          "kind": "exdark"})
    return items


def pseudo_label(items, report):
    """Stock yolov8n at conf 0.35 on train/val items only; adds only the classes the source lacks."""
    from ultralytics import YOLO
    model = YOLO(str(STOCK))
    rows = []
    todo = [it for it in items if it["split"] in ("train", "val")]
    for k in range(0, len(todo), 64):
        chunk = todo[k:k + 64]
        for it, res in zip(chunk, model.predict([str(it["src"]) for it in chunk], conf=PSEUDO_CONF, verbose=False)):
            it["pseudo"] = []
            for b in res.boxes:
                name = res.names[int(b.cls[0])].strip().lower()
                if name not in PSEUDO_FOR[it["kind"]]:
                    continue
                xc, yc, w, h = (float(v) for v in b.xywhn[0])
                if w <= 0 or h <= 0:
                    continue
                it["pseudo"].append(f"{STOCK_TO_NEW[name]} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
                rows.append({"image": it["name"], "split": it["split"], "class": NAMES[STOCK_TO_NEW[name]],
                             "conf": f"{float(b.conf[0]):.3f}", "xc": f"{xc:.6f}", "yc": f"{yc:.6f}", "w": f"{w:.6f}", "h": f"{h:.6f}"})
        print(f"  pseudo-labelled {min(k + 64, len(todo))}/{len(todo)}", flush=True)
    with open(OUT / "pseudo_labels_new_sources.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image", "split", "class", "conf", "xc", "yc", "w", "h"])
        w.writeheader()
        w.writerows(rows)
    report["pseudo_boxes"] = {k: dict(v) for k, v in _count(rows).items()}


def _count(rows):
    c = defaultdict(Counter)
    for r in rows:
        c[r["image"].split("_")[0]][r["class"]] += 1
    return c


def iou_xywh(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw / 2, bx + bw / 2) - max(ax - aw / 2, bx - bw / 2))
    iy = max(0.0, min(ay + ah / 2, by + bh / 2) - max(ay - ah / 2, by - bh / 2))
    inter = ix * iy
    return inter / (aw * ah + bw * bh - inter) if inter else 0.0


def drop_conflicting_pseudo(items, report):
    """ExDark labels sofas as Chair, so a pseudo sofa/bed on the same object would give it two classes
    (spotcheck_exdark_first_build.jpg). For a pseudo box with IoU >= 0.5 against one of the image's own boxes:
    if it is sofa and the own box is Chair, the own box becomes sofa (v7's own footage and COCO call these
    couch -> sofa); in every other case the pseudo box is dropped (e.g. stock 'bed' on an armchair)."""
    for it in items:
        if it["kind"] != "exdark" or not it.get("pseudo"):
            continue
        own = [l.split() for l in it["own"]]
        keep = []
        for l in it["pseudo"]:
            p = l.split()
            box = tuple(float(v) for v in p[1:])
            hits = [o for o in own if iou_xywh(box, tuple(float(v) for v in o[1:])) >= 0.5]
            if not hits:
                keep.append(l)
                continue
            if p[0] == "3":
                for o in hits:
                    if o[0] == "2":
                        o[0] = "3"
                        report["exdark_chair_relabelled_sofa"] += 1
            report["exdark_pseudo_dropped_overlap"][NAMES[int(p[0])]] += 1
        it["own"] = [" ".join(o) for o in own]
        it["pseudo"] = keep


def place_new(items, report, copies):
    for it in items:
        if it["split"] == "test":
            sub = HELD / ("cauca_s10" if it["kind"] == "cauca" else "exdark_test")
            link(it["src"], sub / "images" / it["name"], copies)
            write_label(sub / "labels" / f"{Path(it['name']).stem}.txt", it["own"])
            report["images"][f"heldout/{it['kind']}"] += 1
            for l in it["own"]:
                report["boxes"][f"heldout/{it['kind']}"][NAMES[int(l.split()[0])]] += 1
            continue
        lines = it["own"] + it.get("pseudo", [])
        link(it["src"], FULL / "images" / it["split"] / it["name"], copies)
        write_label(FULL / "labels" / it["split"] / f"{Path(it['name']).stem}.txt", lines)
        report["images"][f"{it['split']}/{it['kind']}"] += 1
        for l in lines:
            report["boxes"][f"{it['split']}/{it['kind']}"][NAMES[int(l.split()[0])]] += 1


def write_yaml(d, note):
    y = (f"# {note} See benchmarks/phase5_v8/PLAN.md.\npath: {d.as_posix()}\ntrain: images/train\nval: images/val\n"
         f"names:\n" + "".join(f"  {i}: {n}\n" for i, n in enumerate(NAMES)))
    (d / "data.yaml").write_text(y, encoding="utf-8")


def main():
    for d in (CLEAN, FULL, HELD):
        if d.exists():
            sys.exit(f"STOP: {d} already exists")
    report = {"images": Counter(), "boxes": defaultdict(Counter), "v7_removed_boxes_dropped_classes": Counter(),
              "v7_images_now_empty": Counter(), "cauca_unlabelled_skipped": 0, "exdark_skipped": Counter(),
              "exdark_skipped_boxes_degenerate": 0, "exdark_pseudo_dropped_overlap": Counter(),
              "exdark_chair_relabelled_sofa": 0}
    copies = []
    print("v7 part ...", flush=True)
    build_v7_part([CLEAN, FULL], report, copies)
    print("selecting CAUCAFall / ExDark ...", flush=True)
    items = select_cauca(report) + select_exdark(report)
    print(f"  {len(items)} new-source images selected", flush=True)
    pseudo_label(items, report)
    drop_conflicting_pseudo(items, report)
    place_new(items, report, copies)
    write_yaml(CLEAN, "B: v7 minus the 4 problem clips, 7 classes.")
    write_yaml(FULL, "C: B + CAUCAFall + ExDark (indoor), 7 classes.")

    # verification
    v = {}
    for d in (CLEAN, FULL):
        for split in ("train", "val"):
            imgs = sorted(p.stem for p in (d / "images" / split).iterdir())
            lbls = sorted(p.stem for p in (d / "labels" / split).glob("*.txt"))
            v[f"{d.name}/{split}"] = {"images": len(imgs), "labels": len(lbls), "names_match": imgs == lbls}
    for sub in ("cauca_s10", "exdark_test"):
        imgs = sorted(p.stem for p in (HELD / sub / "images").iterdir())
        lbls = sorted(p.stem for p in (HELD / sub / "labels").glob("*.txt"))
        v[f"heldout/{sub}"] = {"images": len(imgs), "labels": len(lbls), "names_match": imgs == lbls}
    bad_ids = 0
    for d in (CLEAN, FULL, HELD):
        for t in d.rglob("*.txt"):
            for l in t.read_text(encoding="utf-8").splitlines():
                p = l.split()
                if len(p) != 5 or not (0 <= int(p[0]) < len(NAMES)) or not all(0 <= float(x) <= 1.000001 for x in p[1:]):
                    bad_ids += 1
    v["invalid_label_lines"] = bad_ids
    v["drop_clip_frames_left"] = sum(1 for d in (CLEAN, FULL) for p in d.rglob("*.jpg") if v7_clip(p.stem) in DROP_CLIPS)
    v["real_copies_bad_eoi"] = copies
    v["cache_files"] = [str(p) for p in ROOT.joinpath("datasets").glob("sage_v8_*/**/*.cache")]
    v["ALL_OK"] = all(x["names_match"] for k, x in v.items() if isinstance(x, dict)) and bad_ids == 0 \
        and v["drop_clip_frames_left"] == 0 and not v["cache_files"]
    report["verify"] = v
    out = json.loads(json.dumps(report, default=lambda o: dict(o) if isinstance(o, Counter) else str(o)))
    (OUT / "build_report.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2), flush=True)
    return 0 if v["ALL_OK"] else 1


if __name__ == "__main__":
    sys.exit(main())

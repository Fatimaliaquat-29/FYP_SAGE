"""A3: build datasets/sage_merged_v7_A2 from sage_merged_v7 minus the A2 drop set.

Reads the original dataset (never writes to it). Creates only:
  datasets/sage_merged_v7_A2/{images,labels}/{train,val}/, data_A2.yaml
  benchmarks/phase3_a2/{dropped_manifest.csv, kept_summary.csv, a3_verify.json}

Images: hardlinks (same volume, no extra space) EXCEPT any JPEG not ending in
FFD9. Ultralytics' label check re-saves such files in place, which through a
hardlink would rewrite the ORIGINAL image; those get real copies instead.
Labels: real byte copies. No .cache files are copied.
"""
import csv
import hashlib
import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
SRC = ROOT / "datasets" / "sage_merged_v7"
DST = ROOT / "datasets" / "sage_merged_v7_A2"
OUT = ROOT / "benchmarks" / "phase3_a2"
CLASSES = ["person", "bottle", "cup", "wine glass", "bowl", "chair", "couch", "bed",
           "dining table", "toilet", "tv", "sink", "refrigerator"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jpeg_ends_ok(p):
    with open(p, "rb") as f:
        f.seek(-2, 2)
        return f.read() == b"\xff\xd9"


def main():
    if DST.exists():
        print(f"STOP: {DST} already exists")
        return 1
    prov = list(csv.DictReader(open(OUT / "a1_provenance.csv", encoding="utf-8")))
    by_stem = {r["stem"]: r for r in prov}
    drop = {r["stem"] for r in prov if r["target_clip"] == "1" and r["provenance"] == "no_hand"}
    bad_hand = [s for s in drop if by_stem[s]["provenance"].startswith("hand")]
    if bad_hand:
        print("STOP: hand-drawn frame in drop set", bad_hand[:5])
        return 1

    for split in ("train", "val"):
        (DST / "images" / split).mkdir(parents=True)
        (DST / "labels" / split).mkdir(parents=True)

    stats = Counter()
    real_copies = []
    for split in ("train", "val"):
        for img in sorted((SRC / "images" / split).iterdir()):
            if not img.is_file():
                continue
            if split == "train" and img.stem in drop:
                stats[f"{split}_dropped"] += 1
                continue
            dst_img = DST / "images" / split / img.name
            if img.suffix.lower() in (".jpg", ".jpeg") and not jpeg_ends_ok(img):
                shutil.copyfile(img, dst_img)
                real_copies.append(str(img.relative_to(SRC)))
            else:
                os.link(img, dst_img)
            lbl = SRC / "labels" / split / f"{img.stem}.txt"
            if lbl.exists():
                shutil.copyfile(lbl, DST / "labels" / split / lbl.name)
                stats[f"{split}_labels"] += 1
            stats[f"{split}_images"] += 1

    yaml = (f"# A2 copy of sage_merged_v7: train minus non-hand-drawn frames of Sitting_Dim_HM and\n"
            f"# Standing_Walking_Dim_HM (see benchmarks/phase3_a2/A2_DROP_DECISION.md). Val unchanged.\n"
            f"path: {DST.as_posix()}\ntrain: images/train\nval: images/val\nnames:\n"
            + "".join(f"  {i}: {n}\n" for i, n in enumerate(CLASSES)))
    (DST / "data_A2.yaml").write_text(yaml, encoding="utf-8")

    with open(OUT / "dropped_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "clip", "repeat_copy", "reason"])
        for s in sorted(drop):
            r = by_stem[s]
            w.writerow([f"datasets/sage_merged_v7/images/train/{s}.jpg", r["clip"], r["repeat_copy"],
                        "target clip, not hand-drawn (no hand label in round5/round6/round6_patch; MediaPipe box)"])

    kept = Counter()
    for r in prov:
        if r["stem"] in drop:
            continue
        kept[(r["prefix"], r["clip"] if r["prefix"] == "own" else "*",
              r["provenance"], "repeat" if r["repeat_copy"] != "0" else "base")] += 1
    with open(OUT / "kept_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["prefix", "clip", "provenance", "copy", "kept_images"])
        for k, n in sorted(kept.items()):
            w.writerow([*k, n])

    # ---- verification ----
    v = {}
    orig_train = len([p for p in (SRC / "images" / "train").iterdir() if p.is_file()])
    new_train = len(list((DST / "images" / "train").iterdir()))
    v["original_train"], v["dropped"], v["new_train"] = orig_train, len(drop), new_train
    v["train_count_ok"] = new_train == orig_train - len(drop)
    v["dropped_present_in_copy"] = sum((DST / "images" / "train" / f"{s}.jpg").exists() for s in drop)
    v["dropped_hand_drawn"] = sum(by_stem[s]["provenance"].startswith("hand") for s in drop)
    hand_stems = {r["stem"] for r in prov if r["provenance"].startswith("hand")}
    v["hand_frames_total"] = len(hand_stems)
    v["hand_frames_in_copy"] = sum((DST / "images" / "train" / f"{s}.jpg").exists() for s in hand_stems)
    ov = sorted(p.name for p in (SRC / "labels" / "val").glob("*.txt"))
    nv = sorted(p.name for p in (DST / "labels" / "val").glob("*.txt"))
    v["val_label_files_orig_new"] = [len(ov), len(nv)]
    v["val_images_orig_new"] = [len(list((SRC / "images" / "val").iterdir())),
                                len(list((DST / "images" / "val").iterdir()))]
    v["val_label_sha_mismatch"] = sum(sha(SRC / "labels" / "val" / n) != sha(DST / "labels" / "val" / n)
                                      for n in ov) if ov == nv else "NAME LISTS DIFFER"
    tl = [p.name for p in (DST / "labels" / "train").glob("*.txt")]
    v["train_label_sha_mismatch_vs_original"] = sum(sha(SRC / "labels" / "train" / n) != sha(DST / "labels" / "train" / n) for n in tl)
    v["train_images_without_label"] = sum(not (DST / "labels" / "train" / f"{p.stem}.txt").exists()
                                          for p in (DST / "images" / "train").iterdir())
    v["images_hardlinked"] = sum(os.path.samefile(p, SRC / "images" / sp / p.name)
                                 for sp in ("train", "val") for p in (DST / "images" / sp).iterdir())
    v["images_real_copies_bad_eoi"] = real_copies
    v["cache_files_in_copy"] = [str(p) for p in DST.rglob("*.cache")]
    v["class_names_ok"] = CLASSES == [l.split(": ", 1)[1] for l in yaml.splitlines() if l.startswith("  ")]
    v["stats"] = dict(stats)
    ok = (v["train_count_ok"] and v["dropped_present_in_copy"] == 0 and v["dropped_hand_drawn"] == 0
          and v["hand_frames_in_copy"] == v["hand_frames_total"] and v["val_label_sha_mismatch"] == 0
          and v["val_label_files_orig_new"][0] == v["val_label_files_orig_new"][1]
          and v["val_images_orig_new"][0] == v["val_images_orig_new"][1]
          and v["train_label_sha_mismatch_vs_original"] == 0 and not v["cache_files_in_copy"]
          and v["class_names_ok"])
    v["ALL_OK"] = bool(ok)
    (OUT / "a3_verify.json").write_text(json.dumps(v, indent=2), encoding="utf-8")
    print(json.dumps(v, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

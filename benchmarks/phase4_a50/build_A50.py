"""Phase 4: build datasets/sage_merged_v7_A50, a full copy of sage_merged_v7 (nothing dropped) for the
50-epoch run, and record a hash baseline of the original's labels.

Why a copy: Ultralytics rewrites labels/*.cache next to the data it trains on, and the original's cache
was built from different (C:/University) paths, so training on the original would rewrite it.

Images: hardlinks (same volume, no extra space), except any JPEG not ending in FFD9, which gets a real
copy (Ultralytics re-saves such files in place, which through a hardlink would rewrite the original).
Labels: real byte copies. No .cache files copied. Reads the original, never writes to it.
"""
import csv
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
SRC = ROOT / "datasets" / "sage_merged_v7"
DST = ROOT / "datasets" / "sage_merged_v7_A50"
OUT = ROOT / "benchmarks" / "phase4_a50"
CLASSES = ["person", "bottle", "cup", "wine glass", "bowl", "chair", "couch", "bed",
           "dining table", "toilet", "tv", "sink", "refrigerator"]
TICKS_EPOCH_OFFSET = 621355968000000000


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()


def ends_ok(p):
    with open(p, "rb") as f:
        f.seek(-2, 2)
        return f.read() == b"\xff\xd9"


def main():
    if DST.exists():
        print(f"STOP: {DST} already exists")
        return 1
    # baseline of the ORIGINAL labels (all splits + .cache)
    with open(OUT / "baseline_hashes_original.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "bytes", "mtime_utc_ticks", "sha256"])
        n_base = 0
        for p in sorted((SRC / "labels").rglob("*")):
            if p.is_file():
                st = p.stat()
                w.writerow([str(p.relative_to(SRC)), st.st_size, TICKS_EPOCH_OFFSET + st.st_mtime_ns // 100, sha(p)])
                n_base += 1

    real = []
    for split in ("train", "val"):
        (DST / "images" / split).mkdir(parents=True)
        (DST / "labels" / split).mkdir(parents=True)
        for img in sorted((SRC / "images" / split).iterdir()):
            if not img.is_file():
                continue
            d = DST / "images" / split / img.name
            if img.suffix.lower() in (".jpg", ".jpeg") and not ends_ok(img):
                shutil.copyfile(img, d)
                real.append(str(img.relative_to(SRC)))
            else:
                os.link(img, d)
            lbl = SRC / "labels" / split / f"{img.stem}.txt"
            if lbl.exists():
                shutil.copyfile(lbl, DST / "labels" / split / lbl.name)
    yaml = (f"# A50: full copy of sage_merged_v7 (nothing dropped) for the 50-epoch run. See benchmarks/phase4_a50.\n"
            f"path: {DST.as_posix()}\ntrain: images/train\nval: images/val\nnames:\n"
            + "".join(f"  {i}: {n}\n" for i, n in enumerate(CLASSES)))
    (DST / "data_A50.yaml").write_text(yaml, encoding="utf-8")

    v = {"baseline_label_files": n_base}
    for split in ("train", "val"):
        si = sorted(p.name for p in (SRC / "images" / split).iterdir() if p.is_file())
        di = sorted(p.name for p in (DST / "images" / split).iterdir())
        sl = sorted(p.name for p in (SRC / "labels" / split).glob("*.txt"))
        dl = sorted(p.name for p in (DST / "labels" / split).glob("*.txt"))
        v[f"{split}_images_src_dst"] = [len(si), len(di)]
        v[f"{split}_labels_src_dst"] = [len(sl), len(dl)]
        v[f"{split}_names_identical"] = si == di and sl == dl
        v[f"{split}_label_sha_mismatch"] = sum(sha(SRC / "labels" / split / n) != sha(DST / "labels" / split / n) for n in sl) if sl == dl else "NAMES DIFFER"
    v["images_hardlinked"] = sum(os.path.samefile(p, SRC / "images" / sp / p.name) for sp in ("train", "val") for p in (DST / "images" / sp).iterdir())
    v["images_real_copies_bad_eoi"] = real
    v["cache_files_in_copy"] = [str(p) for p in DST.rglob("*.cache")]
    v["ALL_OK"] = bool(v["train_names_identical"] and v["val_names_identical"] and v["train_label_sha_mismatch"] == 0
                       and v["val_label_sha_mismatch"] == 0 and not v["cache_files_in_copy"])
    (OUT / "build_verify.json").write_text(json.dumps(v, indent=2), encoding="utf-8")
    print(json.dumps(v, indent=2))
    return 0 if v["ALL_OK"] else 1


if __name__ == "__main__":
    sys.exit(main())

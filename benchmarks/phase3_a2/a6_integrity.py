"""A6: integrity check of the ORIGINAL dataset after training/scoring. Read-only. Standard library only.

1. Recompute SHA256 + size + mtime of every file under datasets/sage_merged_v7/labels and compare
   with baseline_hashes_original.csv (written in A0). Any difference, missing or new file = violation.
2. Extra: every image under datasets/sage_merged_v7/images is hardlinked into the A2 copy, so a
   write through the copy would change the original. Flag any original image whose mtime is after
   training started (first line of supervisor_events.log).
Writes OUT/a6_integrity.json and prints a summary. Exit 0 only if clean.
"""
import csv
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
DS = ROOT / "datasets" / "sage_merged_v7"
OUT = ROOT / "benchmarks" / "phase3_a2"
TICKS_EPOCH_OFFSET = 621355968000000000  # .NET ticks at 1970-01-01


def main():
    base = {r["path"]: r for r in csv.DictReader(open(OUT / "baseline_hashes_original.csv", encoding="utf-8-sig"))}
    now = {str(p.relative_to(DS)): p for p in (DS / "labels").rglob("*") if p.is_file()}
    changed, missing = [], []
    for rel, b in base.items():
        p = now.get(rel)
        if p is None:
            missing.append(rel)
            continue
        st = p.stat()
        ticks = TICKS_EPOCH_OFFSET + st.st_mtime_ns // 100
        sha = hashlib.sha256(p.read_bytes()).hexdigest().upper()
        if sha != b["sha256"].upper() or st.st_size != int(b["bytes"]) or ticks != int(b["mtime_utc_ticks"]):
            changed.append({"path": rel, "sha_ok": sha == b["sha256"].upper(), "size_ok": st.st_size == int(b["bytes"]),
                            "mtime_ok": ticks == int(b["mtime_utc_ticks"])})
    new = sorted(set(now) - set(base))

    first = (OUT / "supervisor_events.log").read_text(encoding="utf-8").splitlines()[0]
    train_start = datetime.strptime(first[:19], "%Y-%m-%d %H:%M:%S").timestamp()
    touched_images = [str(p.relative_to(DS)) for p in (DS / "images").rglob("*")
                      if p.is_file() and p.stat().st_mtime > train_start]

    res = {"checked_at": datetime.now().isoformat(timespec="seconds"), "baseline_files": len(base),
           "current_files": len(now), "changed": changed, "missing": missing, "new_files": new,
           "training_started": first[:19], "original_images_modified_after_training_start": touched_images[:50],
           "n_original_images_modified_after_training_start": len(touched_images)}
    res["CLEAN"] = not (changed or missing or new or touched_images)
    (OUT / "a6_integrity.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in res.items()}, indent=2))
    return 0 if res["CLEAN"] else 1


if __name__ == "__main__":
    sys.exit(main())

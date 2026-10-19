"""Turn a CHECKED Roboflow export into handlabels/round6_heldout_v2/ (run after check_export.py says ALL PASS).

Pure standard library, no network. Never touches handlabels/round6_heldout/ (the
original labels stay as the record of what v7 was scored on).

Creates:
  handlabels/round6_heldout_v2/classes.txt     copy of round6_heldout/classes.txt
  handlabels/round6_heldout_v2/labels/<stem>.txt   export labels renamed back to original stems
  handlabels/round6_heldout_v2/images/<stem>.jpg   copies of the ORIGINAL frames (not the export's)

Usage:
    python import_corrected_labels.py <export_folder>
"""
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_export as ce  # noqa: E402  (same folder; reuses its name mapping and checks)

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
SRC = ROOT / "handlabels" / "round6_heldout"
DST = ROOT / "handlabels" / "round6_heldout_v2"


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    export = Path(argv[1])
    if ce.main(["check_export.py", str(export)]) != 0:
        print("STOP: check_export.py did not pass; nothing written.")
        return 1
    if DST.exists():
        print(f"STOP: {DST} already exists; nothing written. Remove or rename it yourself first.")
        return 1
    images = [p for p in export.rglob("*") if p.suffix.lower() in ce.IMG_EXT and p.parent.name == "images"]
    (DST / "labels").mkdir(parents=True)
    (DST / "images").mkdir()
    shutil.copyfile(SRC / "classes.txt", DST / "classes.txt")
    for p in images:
        stem = ce.original_stem(p.stem)
        shutil.copyfile(p.parent.parent / "labels" / f"{p.stem}.txt", DST / "labels" / f"{stem}.txt")
        shutil.copyfile(SRC / "images" / f"{stem}.jpg", DST / "images" / f"{stem}.jpg")
    n_l = len(list((DST / "labels").glob("*.txt")))
    n_i = len(list((DST / "images").glob("*.jpg")))
    print(f"Wrote {DST}: {n_i} images, {n_l} label files")
    return 0 if n_l == n_i == ce.EXPECTED_COUNT else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

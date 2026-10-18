"""Check a Roboflow YOLOv8 export of the round6_heldout retag before using it.

Pure standard library, no network. Prints PASS/FAIL per check; exit code 0 only
if every check passes.

Usage:
    python check_export.py <export_folder>
    (the unzipped export folder, i.e. the one containing data.yaml)

Checks:
  1. class names: same 13 names in the same ORDER as src/detection/sage_classes.py
  2. image count: 298 images across all splits
  3. filenames: every export image maps back to one original frame stem
  4. image sizes: each export image has the same width x height as the original
  5. labels: every image has a label file and every class id is in 0..12
"""
import re
import sys
from pathlib import Path

ORIGINAL_IMAGES = Path(r"D:\FYP\PROJECT FILES\main\handlabels\round6_heldout\images")
EXPECTED_CLASSES = ["person", "bottle", "cup", "wine glass", "bowl", "chair", "couch", "bed",
                    "dining table", "toilet", "tv", "sink", "refrigerator"]
EXPECTED_COUNT = 298
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}
# Roboflow renames "Foo_000010.jpg" to "Foo_000010_jpg.rf.<hash>.jpg"
RF_SUFFIX = re.compile(r"_(jpg|jpeg|png|bmp)\.rf\.[0-9a-fA-F]+$")


def parse_names(yaml_text):
    """Read `names:` from data.yaml in inline-list, block-list or index-map form."""
    lines = yaml_text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^names\s*:\s*(.*)$", line)
        if not m:
            continue
        rest = m.group(1).strip()
        if rest.startswith("["):
            body = rest
            j = i
            while not body.rstrip().endswith("]") and j + 1 < len(lines):
                j += 1
                body += lines[j].strip()
            # class names contain no commas, so a plain split is enough
            inner = body.strip()[1:-1]
            return [t.strip().strip("'\"") for t in inner.split(",") if t.strip()]
        names, mapping = [], {}
        for nxt in lines[i + 1:]:
            if not nxt.strip() or nxt.lstrip().startswith("#"):
                continue
            # block items may be indented or start at column 0 ("- person")
            if not nxt.startswith((" ", "\t", "- ")):
                break
            s = nxt.strip()
            if s.startswith("- "):
                names.append(s[2:].strip().strip("'\""))
            else:
                km = re.match(r"^(\d+)\s*:\s*(.+)$", s)
                if km:
                    mapping[int(km.group(1))] = km.group(2).strip().strip("'\"")
        if mapping:
            return [mapping[k] for k in sorted(mapping)]
        return names
    return None


def image_size(path):
    """(width, height) for JPEG/PNG/BMP using only the standard library."""
    with open(path, "rb") as f:
        head = f.read(26)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
        if head[:2] == b"BM":
            return int.from_bytes(head[18:22], "little"), abs(int.from_bytes(head[22:26], "little", signed=True))
        if head[:2] != b"\xff\xd8":
            return None
        f.seek(2)
        while True:
            b = f.read(1)
            while b and b != b"\xff":
                b = f.read(1)
            while b == b"\xff":
                b = f.read(1)
            if not b:
                return None
            marker = b[0]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                continue
            seglen = int.from_bytes(f.read(2), "big")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                seg = f.read(5)
                return int.from_bytes(seg[3:5], "big"), int.from_bytes(seg[1:3], "big")
            f.seek(seglen - 2, 1)


def original_stem(export_stem):
    return RF_SUFFIX.sub("", export_stem)


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = Path(argv[1])
    results = []

    def report(name, ok, detail):
        results.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")

    yamls = list(root.glob("data.yaml")) or list(root.rglob("data.yaml"))
    if not yamls:
        report("data.yaml present", False, f"no data.yaml under {root}")
        return 1
    names = parse_names(yamls[0].read_text(encoding="utf-8"))
    if names == EXPECTED_CLASSES:
        report("class order", True, "13 names, same order")
    else:
        detail = f"export has {names}"
        if names and sorted(names) == sorted(EXPECTED_CLASSES):
            remap = {i: EXPECTED_CLASSES.index(n) for i, n in enumerate(names) if EXPECTED_CLASSES.index(n) != i}
            detail += f"\n       same names, DIFFERENT ORDER. export id -> original id: {remap}"
        elif names:
            detail += (f"\n       missing: {[n for n in EXPECTED_CLASSES if n not in names]}"
                       f"  extra: {[n for n in names if n not in EXPECTED_CLASSES]}")
        report("class order", False, detail)

    images = sorted(p for p in root.rglob("*") if p.suffix.lower() in IMG_EXT and p.parent.name == "images")
    report("image count", len(images) == EXPECTED_COUNT, f"{len(images)} images (expected {EXPECTED_COUNT})")

    orig = {p.stem: p for p in ORIGINAL_IMAGES.glob("*.jpg")}
    mapped, unmapped, dupes = {}, [], []
    for p in images:
        s = original_stem(p.stem)
        if s not in orig:
            unmapped.append(p.name)
        elif s in mapped:
            dupes.append(p.name)
        else:
            mapped[s] = p
    missing = sorted(set(orig) - set(mapped))
    report("filenames map to originals", not unmapped and not dupes and not missing,
           f"mapped {len(mapped)}/{len(orig)}; unmapped {len(unmapped)} {unmapped[:5]}; "
           f"duplicates {len(dupes)} {dupes[:5]}; originals missing {len(missing)} {missing[:5]}")

    bad_size = []
    for s, p in mapped.items():
        a, b = image_size(p), image_size(orig[s])
        if a is None or a != b:
            bad_size.append(f"{p.name}: export {a} vs original {b}")
    report("image sizes unchanged", not bad_size, f"{len(mapped) - len(bad_size)}/{len(mapped)} match" +
           ("".join(f"\n       {x}" for x in bad_size[:10])))

    no_label, bad_ids = [], []
    for p in images:
        lbl = p.parent.parent / "labels" / f"{p.stem}.txt"
        if not lbl.exists():
            no_label.append(p.name)
            continue
        for ln, line in enumerate(lbl.read_text(encoding="utf-8").splitlines(), 1):
            parts = line.split()
            if not parts:
                continue
            try:
                cid = int(parts[0])
            except ValueError:
                bad_ids.append(f"{lbl.name}:{ln} '{parts[0]}'")
                continue
            if not 0 <= cid <= 12 or len(parts) != 5:
                bad_ids.append(f"{lbl.name}:{ln} id={parts[0]} fields={len(parts)}")
    report("labels present, ids 0..12, 5 fields", not no_label and not bad_ids,
           f"missing label files {len(no_label)} {no_label[:5]}; bad lines {len(bad_ids)} {bad_ids[:5]}")

    print("ALL PASS" if all(results) else "SOME CHECKS FAILED")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""Reports where each box label CAME FROM, per class. Read-only.

Why this exists
---------------
Not every label in this project is ground truth, and the mix was invisible.

  * `person` boxes in our own footage are MediaPipe-derived -- reliable.
  * COCO boxes are human-drawn -- reliable.
  * But when generate_bbox_dataset.py runs with --pseudo_objects, the SAME own
    label files also carry FURNITURE boxes guessed by a stock COCO YOLOv8n.
    Those are pseudo-labels.

Training on pseudo-labels is a deliberate trade. MEASURING against them is
circular -- it scores the student on how well it reproduces the teacher it was
trained to imitate. Measured Aug 2026, 73.9% of `chair` and 81.1% of `bed`
boxes in the merged VAL split were pseudo-labels, which means the standing
"chair/bed strong" result was largely self-referential.

Two targets
-----------
  --target sources     the source datasets, i.e. what feeds training
  --target merged-val  the built merged val split, i.e. what scores the model

`merged-val` recovers the source of each label from its filename, because
build_merged_dataset.copy_split() stamps an `own_` / `coco_` / `empty_` prefix
onto every file it writes.

Run both after any dataset rebuild. If a furniture class shows a high pseudo
share under `merged-val`, its score from that split is not evidence.
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.sage_classes import CLASS_TO_INDEX, SAGE_CLASSES

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# Which prefixes carry hand/algorithmically-trustworthy labels for OBJECT classes.
# `own` is trustworthy for person (MediaPipe) but NOT for furniture (pseudo).
HUMAN_OBJECT_SOURCES = {"coco"}


def load_source_class_names(dataset_dir: Path):
    """Read a YOLO dataset's class names from its yaml sidecar.

    Same list/dict handling as build_merged_dataset.load_source_class_names.
    Duplicated rather than imported so this diagnostic still runs if the merge
    script is mid-edit.
    """
    for candidate in list(dataset_dir.glob("*.yaml")) + list(dataset_dir.glob("*.yml")):
        with candidate.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        names = data.get("names")
        if names is None:
            continue
        if isinstance(names, dict):
            return {int(k): str(v) for k, v in names.items()}
        if isinstance(names, list):
            return {i: str(v) for i, v in enumerate(names)}
    raise SystemExit(f"No yaml with a usable `names:` entry in {dataset_dir}")


def count_source_dataset(dataset_dir: Path):
    """Count boxes per SAGE class in one SOURCE dataset, remapping by name."""
    names = load_source_class_names(dataset_dir)
    remap = {i: CLASS_TO_INDEX.get(n.strip().lower()) for i, n in names.items()}

    counts = defaultdict(int)
    dropped = 0
    n_images = 0
    n_empty = 0
    for split in ("train", "val"):
        images_dir = dataset_dir / "images" / split
        labels_dir = dataset_dir / "labels" / split
        if not images_dir.is_dir():
            continue
        images = [p for p in images_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS]
        n_images += len(images)
        for image_path in images:
            label_path = labels_dir / f"{image_path.stem}.txt"
            if not label_path.exists():
                n_empty += 1
                continue
            lines = [l for l in label_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            if not lines:
                n_empty += 1
            for line in lines:
                dst = remap.get(int(float(line.split()[0])))
                if dst is None:
                    dropped += 1
                else:
                    counts[dst] += 1
    return counts, n_images, n_empty, dropped


def count_merged_split(merged_dir: Path, split: str):
    """Count boxes per class per source-prefix in a BUILT merged split.

    Labels are already remapped to SAGE indices by the merge step, so no name
    resolution is needed here -- only the prefix, which identifies provenance.
    """
    labels_dir = merged_dir / "labels" / split
    if not labels_dir.is_dir():
        raise SystemExit(f"{labels_dir} not found -- build the merged dataset first.")

    counts = defaultdict(lambda: defaultdict(int))
    files_per_source = defaultdict(int)
    for label_file in labels_dir.glob("*.txt"):
        source = label_file.name.split("_")[0]
        files_per_source[source] += 1
        for line in label_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                counts[int(line.split()[0])][source] += 1
    return counts, files_per_source


def _print_table(rows, header):
    print(header)
    print("-" * len(header))
    for row in rows:
        print(row)


def report_sources(own_dir: Path, coco_dir: Path, own_repeat: int):
    for d in (own_dir, coco_dir):
        if not d.is_dir():
            raise SystemExit(f"{d} not found.")

    own, own_imgs, own_empty, own_drop = count_source_dataset(own_dir)
    coco, coco_imgs, coco_empty, coco_drop = count_source_dataset(coco_dir)
    r = max(1, own_repeat)

    print(f"own  ({own_dir.name}):  {own_imgs} images, {own_empty} empty, "
          f"{sum(own.values())} boxes, {own_drop} dropped")
    print(f"coco ({coco_dir.name}): {coco_imgs} images, {coco_empty} empty, "
          f"{sum(coco.values())} boxes, {coco_drop} dropped")
    if r > 1:
        print(f"(own counts shown multiplied by --own_repeat {r})")
    print()

    header = f"{'idx':>3}  {'class':<14} {'own':>9} {'coco':>9} {'own share':>10}  {'label quality':<26}"
    rows = []
    for idx, name in enumerate(SAGE_CLASSES):
        o, c = own.get(idx, 0) * r, coco.get(idx, 0)
        total = o + c
        share = f"{100 * o / total:.1f}%" if total else "-"
        if idx == 0:
            quality = "own = MediaPipe (reliable)"
        elif o == 0:
            quality = "COCO only (human)"
        else:
            quality = f"{100 * o / total:.0f}% PSEUDO-labeled"
        rows.append(f"{idx:>3}  {name:<14} {o:>9} {c:>9} {share:>10}  {quality:<26}")
    _print_table(rows, header)

    obj_own = sum(v for k, v in own.items() if k != 0) * r
    obj_coco = sum(v for k, v in coco.items() if k != 0)
    print()
    print(f"person   own={own.get(0, 0) * r}  coco={coco.get(0, 0)}")
    if obj_own + obj_coco:
        print(f"objects  own={obj_own}  coco={obj_coco}   "
              f"-> own is {100 * obj_own / (obj_own + obj_coco):.1f}% of all object boxes")
    print()
    print("NOTE: --own_repeat is a WHOLESALE lever. It repeats the own source's person and")
    print("      furniture boxes together, so it cannot dilute pseudo-labeled furniture while")
    print("      keeping person boxes dominant -- they are the same files. Deleting the")
    print("      furniture boxes instead would train those visibly-present objects as")
    print("      BACKGROUND (the same trap copy_split() documents for COCO's person boxes).")
    print("      Improve the pseudo-labels with a stronger teacher rather than reweighting")
    print("      them -- see docs/data_quality_improvement_plan.md Phase 1b.")


def report_merged_val(merged_dir: Path, split: str):
    counts, files_per_source = count_merged_split(merged_dir, split)
    print(f"{merged_dir.name}/{split}: "
          + ", ".join(f"{k}={v} files" for k, v in sorted(files_per_source.items())))
    print()

    sources = sorted({s for per_source in counts.values() for s in per_source})
    header = (f"{'idx':>3}  {'class':<14} "
              + " ".join(f"{s:>9}" for s in sources)
              + f"  {'pseudo share':>13}  verdict")
    rows = []
    contaminated = []
    for idx, name in enumerate(SAGE_CLASSES):
        per_source = counts.get(idx, {})
        total = sum(per_source.values())
        cells = " ".join(f"{per_source.get(s, 0):>9}" for s in sources)

        if idx == 0 or total == 0:
            # person: `own` labels are MediaPipe, which we do trust.
            share_text, verdict = ("-", "n/a" if total == 0 else "person: own=MediaPipe, OK")
        else:
            pseudo = sum(v for s, v in per_source.items() if s not in HUMAN_OBJECT_SOURCES)
            pct = 100 * pseudo / total
            share_text = f"{pct:.1f}%"
            if pct >= 50:
                verdict = "CONTAMINATED - do not quote"
                contaminated.append((name, pct))
            elif pct > 0:
                verdict = "partly pseudo - caveat it"
            else:
                verdict = "clean (human labels)"
        rows.append(f"{idx:>3}  {name:<14} {cells}  {share_text:>13}  {verdict}")
    _print_table(rows, header)

    print()
    if contaminated:
        print("These classes are scored mostly against a stock detector's own guesses, on the")
        print("same rooms it guessed them in. Their numbers measure agreement with the teacher,")
        print("not accuracy:")
        for name, pct in contaminated:
            print(f"    {name:<14} {pct:.1f}% pseudo-labeled")
        print()
        print("Report furniture accuracy from a HAND-LABELLED held-out room instead --")
        print("see sample_heldout_frames.py / score_heldout_objects.py. A held-out room does")
        print("NOT fix this on its own: if its furniture is also pseudo-labeled, the same")
        print("circularity is reproduced intact.")
    else:
        print("No object class is majority pseudo-labeled in this split.")


def main():
    parser = argparse.ArgumentParser(
        description="Report label provenance per class (pseudo-labeled vs human-labeled)")
    parser.add_argument("--target", choices=("sources", "merged-val"), default="sources",
                        help="`sources` = what feeds training; `merged-val` = what scores the model")
    parser.add_argument("--own_dir", type=str,
                        default=str(REPO_ROOT / "datasets" / "sage_person_finetune"))
    parser.add_argument("--coco_dir", type=str,
                        default=str(REPO_ROOT / "datasets" / "coco_subset"))
    parser.add_argument("--merged_dir", type=str,
                        default=str(REPO_ROOT / "datasets" / "sage_merged"))
    parser.add_argument("--split", type=str, default="val",
                        help="Which merged split to inspect with --target merged-val")
    parser.add_argument("--own_repeat", type=int, default=1,
                        help="Preview the source balance at this --own_repeat (default 1)")
    args = parser.parse_args()

    if args.target == "sources":
        report_sources(Path(args.own_dir), Path(args.coco_dir), args.own_repeat)
    else:
        report_merged_val(Path(args.merged_dir), args.split)


if __name__ == "__main__":
    main()

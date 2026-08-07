"""Merges three sources into one YOLO dataset over the SAGE class list:

  1. Our own room frames (generate_bbox_dataset.py). NOTE: the person boxes here
     are MediaPipe-derived and reliable, but when that script is run with
     --pseudo_objects the SAME files also carry furniture boxes guessed by a
     stock COCO model. Those object labels are pseudo-labels, not ground truth,
     and they currently cover only chair/bed/dining table/tv/refrigerator.
     Anything measured against them is measuring agreement with that guesser --
     see report_label_sources.py.
  2. A COCO subset exported in YOLO format (fetch_coco_subset.py)
  3. Optional empty-room "background" frames carrying no objects

Why this exists: fine-tuning on the person-only dataset passed nc=1, which
structurally REPLACED YOLOv8's 80-class detection head -- the resulting model
cannot emit `chair` or `bottle` at all, because those output neurons no longer
exist. Keeping a multi-class label space is the fix; no forgetting-mitigation
trick (lower LR, frozen backbone) can substitute for it.

THE FAILURE MODE THIS GUARDS AGAINST
Every YOLO label file stores an integer class index, and those integers mean
different things in different datasets. A COCO export where `chair` happens to
be index 3 would, if copied naively, train `chair` boxes as SAGE class 3
(`wine glass`). Loss curves still look healthy, so it fails silently. This
script therefore remaps STRICTLY BY CLASS NAME, read from each source's own
metadata, and aborts on any name it cannot resolve rather than guessing.

Our own person labels need no remapping (person is index 0 in both), but they
are validated and rewritten through the same path anyway, so no source gets a
trusted-by-default shortcut.
"""

import argparse
import shutil
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.footage_paths import TRAINING_EMPTY, assert_not_reserved
from src.detection.sage_classes import CLASS_TO_INDEX, SAGE_CLASSES

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
SPLITS = ("train", "val")


def load_source_class_names(dataset_dir: Path):
    """Read a YOLO dataset's class names from its yaml sidecar.

    Handles both the list form (`names: [a, b]`) and the dict form
    (`names: {0: a, 1: b}`), which differ across Ultralytics/FiftyOne versions.
    """
    candidates = list(dataset_dir.glob("*.yaml")) + list(dataset_dir.glob("*.yml"))
    if not candidates:
        raise SystemExit(f"No dataset yaml found in {dataset_dir}; cannot resolve class names.")

    for candidate in candidates:
        with candidate.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        names = data.get("names")
        if names is None:
            continue
        if isinstance(names, dict):
            return {int(k): str(v) for k, v in names.items()}
        if isinstance(names, list):
            return {i: str(v) for i, v in enumerate(names)}

    raise SystemExit(f"None of the yaml files in {dataset_dir} contain a usable `names:` entry.")


def build_index_remap(source_names, source_label: str, strict: bool):
    """Map source class index -> SAGE class index, by NAME.

    Returns (remap, dropped_names). Classes absent from SAGE_CLASSES map to
    None, meaning their boxes are discarded (the pixels then act as background,
    which is intended -- SAGE has no use for `giraffe`).
    """
    remap = {}
    dropped = []
    for src_idx, raw_name in source_names.items():
        name = raw_name.strip().lower()
        if name in CLASS_TO_INDEX:
            remap[src_idx] = CLASS_TO_INDEX[name]
        else:
            remap[src_idx] = None
            dropped.append(raw_name)

    resolved = sum(1 for v in remap.values() if v is not None)
    if resolved == 0:
        raise SystemExit(
            f"[{source_label}] None of its {len(source_names)} class names matched SAGE_CLASSES.\n"
            f"  source names: {sorted(source_names.values())}\n"
            f"  SAGE classes: {SAGE_CLASSES}\n"
            "Refusing to continue -- this would train on meaningless labels."
        )
    if strict and dropped:
        raise SystemExit(
            f"[{source_label}] --strict is set and these classes are not in SAGE_CLASSES: {sorted(set(dropped))}"
        )

    print(f"[{source_label}] class mapping resolved by name: {resolved}/{len(source_names)} kept")
    for src_idx, dst_idx in sorted(remap.items()):
        if dst_idx is not None:
            print(f"    {src_idx:>3} {source_names[src_idx]!r} -> {dst_idx} {SAGE_CLASSES[dst_idx]!r}")
    if dropped:
        print(f"    dropped (not a SAGE class): {sorted(set(dropped))}")
    return remap


def remap_label_file(label_path: Path, remap):
    """Rewrite one YOLO label file's class indices. Returns (lines, n_dropped)."""
    out_lines = []
    dropped = 0
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts:
            continue
        src_idx = int(float(parts[0]))
        dst_idx = remap.get(src_idx, None)
        if dst_idx is None:
            dropped += 1
            continue
        out_lines.append(" ".join([str(dst_idx)] + parts[1:]))
    return out_lines, dropped


def copy_split(source_dir: Path, split: str, remap, out_dir: Path, prefix: str, stats,
               reassign_val_every: int = 0, repeat: int = 1):
    """Copy one split of a YOLO dataset into the merged tree, remapping labels.

    reassign_val_every: if set, every Nth image of an incoming *train* split is
        diverted to val instead. FiftyOne exports everything as one split, which
        would otherwise leave val with no examples of the object classes -- so
        object mAP would be silently unmeasurable.
    repeat: writes each *train* image N times. This is the lever for the person
        class-imbalance problem: COCO contributes far more (upright) person
        boxes than our own footage contributes lying ones, so our lying-pose
        examples can get drowned out. Oversampling is the safe correction --
        deleting COCO's person boxes is NOT, because unlabeled people in an
        image actively teach the model that a person is background.
    """
    images_dir = source_dir / "images" / split
    labels_dir = source_dir / "labels" / split
    if not images_dir.is_dir():
        return

    for dest_split in ("train", "val"):
        (out_dir / "images" / dest_split).mkdir(parents=True, exist_ok=True)
        (out_dir / "labels" / dest_split).mkdir(parents=True, exist_ok=True)

    images = [p for p in sorted(images_dir.iterdir()) if p.suffix.lower() in IMAGE_EXTENSIONS]
    for i, image_path in enumerate(images):
        label_path = labels_dir / f"{image_path.stem}.txt"

        if label_path.exists():
            lines, dropped = remap_label_file(label_path, remap)
            stats["boxes_dropped"] += dropped
        else:
            # No label file: YOLO treats this as a background image.
            lines = []

        dest_split = split
        if split == "train" and reassign_val_every and (i % reassign_val_every == reassign_val_every - 1):
            dest_split = "val"

        # Only oversample training data; duplicating val would corrupt the metric.
        copies = repeat if (dest_split == "train" and repeat > 1) else 1
        for copy_idx in range(copies):
            suffix = "" if copy_idx == 0 else f"_r{copy_idx}"
            dest_stem = f"{prefix}_{image_path.stem}{suffix}"
            shutil.copy2(image_path, out_dir / "images" / dest_split / f"{dest_stem}{image_path.suffix}")
            (out_dir / "labels" / dest_split / f"{dest_stem}.txt").write_text(
                ("\n".join(lines) + "\n") if lines else "", encoding="utf-8"
            )
            stats["images"] += 1
            stats["boxes"] += len(lines)
            if not lines:
                stats["backgrounds"] += 1


def collect_empty_frames(empty_dir: Path, out_dir: Path, val_every: int, stride: int, stats):
    """Add person-free frames as explicit background examples.

    Accepts loose images and/or video files. Background images are the standard
    YOLO way to teach precision: an image with an empty label file contributes
    only false-positive suppression. Our person-only training set contained
    zero of these, which is why precision was never systematically measurable.

    IMPORTANT: use yolo_testing/Training/Empty. Anything under yolo_testing/Reserved/ is
    refused by assert_not_reserved() in main(), because folding held-out
    footage into training destroys it permanently. Note also that the clip
    discovery in generate_bbox_dataset.py and benchmark_footage.py assigns
    train/val BY POSITION in the sorted listing, so which directory you point
    at changes which clips are held out.
    """
    if not empty_dir or not empty_dir.is_dir():
        return

    import cv2

    frames = []
    for path in sorted(empty_dir.rglob("*")):
        # Key on the path relative to empty_dir, not the bare stem: two rooms
        # filed as bedroom/room.mp4 and kitchen/room.mp4 would otherwise
        # overwrite each other's frames (the same collision that silently cost
        # 499 frames in the person dataset).
        try:
            relative = path.relative_to(empty_dir)
        except ValueError:
            relative = Path(path.name)
        key = "_".join(list(relative.parts[:-1]) + [relative.stem]).replace(" ", "_").replace("-", "_")

        if path.suffix.lower() in IMAGE_EXTENSIONS:
            image = cv2.imread(str(path))
            if image is not None:
                frames.append((key, image))
        elif path.suffix.lower() in VIDEO_EXTENSIONS:
            cap = cv2.VideoCapture(str(path))
            idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                idx += 1
                if idx % stride == 0:  # thin out near-duplicate frames
                    frames.append((f"{key}_{idx:06d}", frame))
            cap.release()

    keys = [k for k, _ in frames]
    if len(set(keys)) != len(keys):
        raise SystemExit("Empty-room frame keys collided; this would silently drop frames.")

    for i, (stem, image) in enumerate(frames):
        split = "val" if (i % val_every == val_every - 1) else "train"
        out_images = out_dir / "images" / split
        out_labels = out_dir / "labels" / split
        out_images.mkdir(parents=True, exist_ok=True)
        out_labels.mkdir(parents=True, exist_ok=True)

        cv2.imwrite(str(out_images / f"empty_{stem}.jpg"), image)
        (out_labels / f"empty_{stem}.txt").write_text("", encoding="utf-8")
        stats["images"] += 1
        stats["backgrounds"] += 1


def main():
    parser = argparse.ArgumentParser(description="Merge SAGE person frames + COCO subset + empty-room negatives")
    parser.add_argument("--own_dir", type=str, default=str(REPO_ROOT / "datasets" / "sage_person_finetune"),
                        help="Our own room frames: MediaPipe person boxes, plus pseudo-labeled "
                             "furniture boxes if generate_bbox_dataset.py was run with --pseudo_objects")
    parser.add_argument("--coco_dir", type=str, default=str(REPO_ROOT / "datasets" / "coco_subset"),
                        help="COCO subset exported in YOLO format")
    parser.add_argument("--empty_dir", type=str, default=None,
                        help=f"Dir of empty-room images/videos used as background negatives. "
                             f"Use {TRAINING_EMPTY}; anything under yolo_testing/Reserved/ is refused.")
    parser.add_argument("--empty_stride", type=int, default=15,
                        help="Keep every Nth frame of empty-room video (default 15; raise it if "
                             "backgrounds end up over ~15%% of the dataset)")
    parser.add_argument("--out_dir", type=str, default=str(REPO_ROOT / "datasets" / "sage_merged"))
    parser.add_argument("--val_every", type=int, default=5, help="Every Nth empty-room frame goes to val")
    parser.add_argument("--strict", action="store_true",
                        help="Abort if a source contains any class not in SAGE_CLASSES")
    parser.add_argument("--coco_val_every", type=int, default=10,
                        help="Divert every Nth COCO train image to val (default 10). FiftyOne exports "
                             "a single split, so without this val has no object-class examples and "
                             "object mAP cannot be measured.")
    parser.add_argument("--own_repeat", type=int, default=1,
                        help="Repeat our own person frames N times in train, to stop COCO's much larger "
                             "count of upright person boxes from drowning out our lying-pose examples. "
                             "Raise this if lying recall regresses after training.")
    args = parser.parse_args()

    own_dir = Path(args.own_dir)
    coco_dir = Path(args.coco_dir)
    out_dir = Path(args.out_dir)

    # Validate BEFORE any copying. Checked at the point of use instead, this
    # would abort only after thousands of frames had already been written --
    # leaving a half-built dataset behind and burning minutes to report an
    # error that was knowable from the arguments alone.
    if args.empty_dir:
        assert_not_reserved(Path(args.empty_dir), "background negatives")

    if out_dir.exists():
        raise SystemExit(f"{out_dir} already exists -- remove it first so a stale merge can't be trained on.")

    sources = []
    if own_dir.is_dir():
        sources.append(("own", own_dir))
    else:
        print(f"WARNING: {own_dir} not found -- the merged set will have no lying-pose person frames.")
    if coco_dir.is_dir():
        sources.append(("coco", coco_dir))
    else:
        print(f"WARNING: {coco_dir} not found -- run fetch_coco_subset.py first, or objects stay undetectable.")

    if not sources:
        raise SystemExit("Neither source dataset exists; nothing to merge.")

    totals = {"images": 0, "boxes": 0, "boxes_dropped": 0, "backgrounds": 0}
    for prefix, source_dir in sources:
        names = load_source_class_names(source_dir)
        remap = build_index_remap(names, prefix, args.strict)
        stats = {"images": 0, "boxes": 0, "boxes_dropped": 0, "backgrounds": 0}
        for split in SPLITS:
            copy_split(
                source_dir, split, remap, out_dir, prefix, stats,
                # Our own dataset already has an honest clip-level split; only the
                # single-split COCO export needs val carved out of it.
                reassign_val_every=args.coco_val_every if prefix == "coco" else 0,
                repeat=args.own_repeat if prefix == "own" else 1,
            )
        print(f"[{prefix}] {stats['images']} images, {stats['boxes']} boxes, "
              f"{stats['boxes_dropped']} boxes dropped, {stats['backgrounds']} backgrounds\n")
        for key in totals:
            totals[key] += stats[key]

    if args.empty_dir:
        stats = {"images": 0, "boxes": 0, "boxes_dropped": 0, "backgrounds": 0}
        collect_empty_frames(Path(args.empty_dir), out_dir, args.val_every, args.empty_stride, stats)
        print(f"[empty] {stats['images']} background frames added\n")
        for key in totals:
            totals[key] += stats[key]

    data_yaml = out_dir / "data.yaml"
    data_yaml.write_text(
        "path: {}\ntrain: images/train\nval: images/val\nnames:\n{}\n".format(
            out_dir.resolve().as_posix(),
            "\n".join(f"  {i}: {name}" for i, name in enumerate(SAGE_CLASSES)),
        ),
        encoding="utf-8",
    )

    # Per-class box counts, so imbalance is visible now rather than inferred
    # from a disappointing training run later.
    class_counts = {i: 0 for i in range(len(SAGE_CLASSES))}
    split_images = {}
    for split in SPLITS:
        labels_dir = out_dir / "labels" / split
        if not labels_dir.is_dir():
            continue
        split_images[split] = len(list((out_dir / "images" / split).glob("*")))
        for label_file in labels_dir.glob("*.txt"):
            for line in label_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    class_counts[int(line.split()[0])] += 1

    background_pct = 100 * totals["backgrounds"] / totals["images"] if totals["images"] else 0
    print("=== merged dataset ===")
    for split, count in split_images.items():
        print(f"  {split}: {count} images")
    print("  boxes per class:")
    for idx, name in enumerate(SAGE_CLASSES):
        print(f"    {idx:>2} {name:<14} {class_counts[idx]}")
    print(f"  images:       {totals['images']}")
    print(f"  boxes:        {totals['boxes']}")
    print(f"  backgrounds:  {totals['backgrounds']} ({background_pct:.1f}% of images)")
    if background_pct > 15:
        print("  WARNING: backgrounds are over ~15% of the dataset. Too many negatives bias the")
        print("           model toward predicting nothing, which costs recall on real falls.")
        print("           Raise --empty_stride and rebuild.")
    print(f"  boxes dropped (non-SAGE classes): {totals['boxes_dropped']}")
    print(f"  classes:      {len(SAGE_CLASSES)}")
    print(f"  data.yaml:    {data_yaml}")
    print("\nTrain with:")
    print(f"  python src/detection/finetune_person.py --data {data_yaml} --weights models/yolov8n.pt")
    print("NOTE: fine-tune from the STOCK weights, not the person-only checkpoint --")
    print("      that checkpoint's head only has one class and cannot regrow the others.")


if __name__ == "__main__":
    main()

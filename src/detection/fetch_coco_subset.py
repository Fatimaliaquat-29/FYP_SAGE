"""Downloads a small, class-filtered COCO subset and exports it in YOLO format.

Uses FiftyOne, which fetches ONLY images containing the requested classes --
roughly 800 MB for ~5k images, versus the ~19 GB / 118k images that
Ultralytics' stock coco.yaml auto-download would pull.

Requires: pip install fiftyone   (not in requirements.txt -- this is a one-off
dataset-preparation tool, not a runtime dependency of the detector.)

The export is written with an explicit `classes=SAGE_CLASSES` ordering so the
indices already line up with SAGE. build_merged_dataset.py still re-verifies
every class by name, so a FiftyOne version that ignores that argument gets
caught rather than silently producing scrambled labels.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.sage_classes import SAGE_CLASSES

# We already have 2,331 person frames from our own footage, including the lying
# poses that stock COCO lacks. Pulling COCO's ~64k person images would drown
# those out, so person is capped hard and the budget goes to object classes.
PERSON_CAP = 500


def main():
    parser = argparse.ArgumentParser(description="Download a class-filtered COCO subset in YOLO format")
    parser.add_argument("--out_dir", type=str, default=str(REPO_ROOT / "datasets" / "coco_subset"))
    parser.add_argument("--per_class", type=int, default=500, help="Target images per non-person class")
    parser.add_argument("--split", type=str, default="train", choices=["train", "validation"])
    args = parser.parse_args()

    try:
        import fiftyone as fo
        import fiftyone.zoo as foz
    except ImportError:
        raise SystemExit(
            "FiftyOne is not installed. Install it with:\n"
            "    pip install fiftyone\n"
            "It is only needed to build the dataset, not to run the detector."
        )

    out_dir = Path(args.out_dir)
    if out_dir.exists():
        raise SystemExit(f"{out_dir} already exists -- remove it first to avoid mixing two downloads.")

    # This download is large enough that transient network failures are likely.
    # FiftyOne keeps named datasets in a persistent database, so a half-finished
    # run leaves a name behind that makes the retry fail with "already exists".
    for stale in ("sage_coco_objects", "sage_coco_person"):
        if stale in fo.list_datasets():
            print(f"Removing stale dataset from a previous run: {stale}")
            fo.delete_dataset(stale)

    object_classes = [c for c in SAGE_CLASSES if c != "person"]
    # Images overlap heavily (one kitchen photo holds several classes), so the
    # unique image count lands well below per_class * len(object_classes).
    max_samples = args.per_class * len(object_classes)

    print(f"Requesting up to {max_samples} images across {len(object_classes)} object classes...")
    dataset = foz.load_zoo_dataset(
        "coco-2017",
        split=args.split,
        label_types=["detections"],
        classes=object_classes,
        max_samples=max_samples,
        dataset_name="sage_coco_objects",
    )

    print(f"Requesting up to {PERSON_CAP} additional person images...")
    person_dataset = foz.load_zoo_dataset(
        "coco-2017",
        split=args.split,
        label_types=["detections"],
        classes=["person"],
        max_samples=PERSON_CAP,
        dataset_name="sage_coco_person",
    )
    dataset.merge_samples(person_dataset)

    print(f"Exporting {len(dataset)} samples to {out_dir} ...")
    dataset.export(
        export_dir=str(out_dir),
        dataset_type=fo.types.YOLOv5Dataset,
        label_field="ground_truth",
        classes=SAGE_CLASSES,
        split="train",
    )

    print(f"\nDone. Next:\n  python src/detection/build_merged_dataset.py --coco_dir {out_dir}")
    print("Verify the printed class mapping before training -- it is the one step that fails silently.")


if __name__ == "__main__":
    main()

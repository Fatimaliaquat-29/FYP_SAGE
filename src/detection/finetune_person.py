"""Fine-tunes YOLOv8n on the auto-labeled person dataset built by
generate_bbox_dataset.py, to address the real-footage benchmark finding that
the stock COCO-pretrained model frequently fails to detect a fallen/lying
person.

This produces a single-class ("person") detector -- it trades away the
stock model's other 79 COCO classes for better recall on the pose that
matters most here. See docs/YOLO_Phase_Summary.md for the tradeoff discussion.
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_YAML = REPO_ROOT / "datasets" / "sage_person_finetune" / "data.yaml"
DEFAULT_BASE_WEIGHTS = REPO_ROOT / "models" / "yolov8n.pt"


def main():
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8n for person detection on fallen/lying poses")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_YAML))
    parser.add_argument("--weights", type=str, default=str(DEFAULT_BASE_WEIGHTS))
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--project", type=str, default=str(REPO_ROOT / "runs" / "detect"))
    parser.add_argument("--name", type=str, default="sage_person_finetune")
    args = parser.parse_args()

    model = YOLO(args.weights)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name,
        device="cpu",
        patience=10,
    )


if __name__ == "__main__":
    main()

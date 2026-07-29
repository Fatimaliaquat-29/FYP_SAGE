from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = REPO_ROOT / "models" / "yolov8n.pt"


class YOLOObjectDetector:
    """Thin wrapper around a YOLOv8 model exposing a single detect() call.

    Runs standalone, alongside MediaPipe rather than replacing it. Kept
    deliberately minimal (one method, one dict shape) so wiring this into
    the live pipeline later is mechanical.
    """

    def __init__(
        self,
        model_path: Path = DEFAULT_MODEL_PATH,
        confidence_threshold: float = 0.4,
        device: Optional[str] = None,
        imgsz: int = 640,
    ):
        self.model = YOLO(str(model_path))
        self.confidence_threshold = confidence_threshold
        self.device = device
        # Should match the size a fine-tuned model was trained at; also the main
        # speed/accuracy dial (smaller = faster), which matters for the Jetson target.
        self.imgsz = imgsz
        self.class_names = self.model.names

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Run detection on a single BGR frame (as read by cv2.VideoCapture).

        Returns a list of {"class": str, "confidence": float, "bbox": [x1, y1, x2, y2]}.
        """
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            device=self.device,
            imgsz=self.imgsz,
            verbose=False,
        )

        detections: List[Dict[str, Any]] = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                detections.append(
                    {
                        "class": result.names[cls_id],
                        "confidence": float(box.conf[0]),
                        "bbox": [float(v) for v in box.xyxy[0]],
                    }
                )
        return detections

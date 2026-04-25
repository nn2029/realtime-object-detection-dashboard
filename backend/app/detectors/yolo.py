"""Optional Ultralytics YOLO detector implementation.

The imports are intentionally delayed until initialization so the backend can
start in mock mode on machines that do not have ultralytics, OpenCV, or NumPy.
"""

from __future__ import annotations

import base64

from ..models import Detection, FramePayload
from .base import DetectorError


class UltralyticsYoloDetector:
    """YOLOv8 adapter matching the same normalized Detection contract."""

    name = "ultralytics-yolov8"

    def __init__(self, weights_path: str = "yolov8n.pt") -> None:
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise DetectorError(
                "ultralytics is not installed. Install optional YOLO dependencies "
                "or run with DETECTOR_MODE=mock."
            ) from exc

        self.model = YOLO(weights_path)

    def detect(self, frame: FramePayload) -> list[Detection]:
        image = self._decode_frame(frame)
        if image is None:
            return []

        results = self.model.predict(image, verbose=False)
        detections: list[Detection] = []

        for result in results:
            names = getattr(result, "names", {}) or {}
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue

            for box in boxes:
                x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                width = max(frame.width, 1)
                height = max(frame.height, 1)
                detections.append(
                    Detection(
                        label=str(names.get(class_id, class_id)),
                        confidence=confidence,
                        bbox=(x1 / width, y1 / height, (x2 - x1) / width, (y2 - y1) / height),
                        track_id=None,
                    ).normalized()
                )

        return detections

    @staticmethod
    def _decode_frame(frame: FramePayload):
        if not frame.image:
            return None

        try:
            import cv2
            import numpy as np
        except ImportError as exc:
            raise DetectorError(
                "opencv-python and numpy are required for YOLO frame decoding."
            ) from exc

        _, _, payload = frame.image.partition(",")
        raw_bytes = base64.b64decode(payload or frame.image)
        buffer = np.frombuffer(raw_bytes, dtype=np.uint8)
        return cv2.imdecode(buffer, cv2.IMREAD_COLOR)

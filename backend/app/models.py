"""Shared data models used by detectors, processing, and API adapters.

These dataclasses stay independent from FastAPI/Pydantic so the core object
detection pipeline can be tested without web framework dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


Box = tuple[float, float, float, float]


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


@dataclass(frozen=True)
class Detection:
    """A normalized object detection returned by any detector implementation.

    The bounding box uses relative coordinates `(x, y, width, height)` in the
    range 0..1, which lets the frontend draw detections over webcam video,
    uploaded video, or generated frames without knowing source pixels.
    """

    label: str
    confidence: float
    bbox: Box
    track_id: str | None = None
    color: str = "#2dd4bf"

    def normalized(self) -> "Detection":
        x, y, width, height = self.bbox
        width = _clamp(width)
        height = _clamp(height)
        x = _clamp(x, 0.0, 1.0 - width)
        y = _clamp(y, 0.0, 1.0 - height)

        return Detection(
            label=self.label,
            confidence=_clamp(self.confidence),
            bbox=(x, y, width, height),
            track_id=self.track_id,
            color=self.color,
        )

    def to_dict(self) -> dict[str, Any]:
        detection = self.normalized()
        x, y, width, height = detection.bbox
        return {
            "label": detection.label,
            "confidence": round(detection.confidence, 4),
            "bbox": {
                "x": round(x, 5),
                "y": round(y, 5),
                "width": round(width, 5),
                "height": round(height, 5),
            },
            "trackId": detection.track_id,
            "color": detection.color,
        }


@dataclass(frozen=True)
class FramePayload:
    """A single frame message received from a dashboard client."""

    frame_id: int
    timestamp: float
    width: int
    height: int
    image: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_client_message(cls, message: dict[str, Any]) -> "FramePayload":
        metadata = message.get("metadata") or {}
        return cls(
            frame_id=int(message.get("frameId", 0)),
            timestamp=float(message.get("timestamp", 0.0)),
            width=int(message.get("width", 640)),
            height=int(message.get("height", 480)),
            image=message.get("image"),
            metadata=metadata if isinstance(metadata, dict) else {},
        )


@dataclass(frozen=True)
class FrameResult:
    """Detection output and aggregated stream metrics for a processed frame."""

    frame_id: int
    timestamp: float
    detector: str
    detections: list[Detection]
    latency_ms: float
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "frameId": self.frame_id,
            "timestamp": self.timestamp,
            "detector": self.detector,
            "latencyMs": round(self.latency_ms, 2),
            "detections": [detection.to_dict() for detection in self.detections],
            "metrics": self.metrics,
        }

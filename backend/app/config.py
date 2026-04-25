"""Runtime configuration for the backend service."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _as_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _as_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class AppSettings:
    """Configuration values loaded from environment variables."""

    detector_mode: str = "mock"
    yolo_weights: str = "yolov8n.pt"
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)
    max_history: int = 120
    mock_max_objects: int = 4
    target_fps: float = 8.0
    max_connections: int = 12
    max_frame_pixels: int = 1280 * 720

    @classmethod
    def from_env(cls) -> "AppSettings":
        origins = tuple(
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        )

        return cls(
            detector_mode=os.getenv("DETECTOR_MODE", "mock").lower(),
            yolo_weights=os.getenv("YOLO_WEIGHTS", "yolov8n.pt"),
            cors_origins=origins or ("http://localhost:5173",),
            max_history=_as_int("METRICS_HISTORY", 120),
            mock_max_objects=_as_int("MOCK_MAX_OBJECTS", 4),
            target_fps=_as_float("TARGET_FPS", 8.0),
            max_connections=_as_int("MAX_CONNECTIONS", 12),
            max_frame_pixels=_as_int("MAX_FRAME_PIXELS", 1280 * 720),
        )

    def public_dict(self) -> dict[str, object]:
        return {
            "detectorMode": self.detector_mode,
            "targetFps": self.target_fps,
            "maxHistory": self.max_history,
            "maxConnections": self.max_connections,
            "maxFramePixels": self.max_frame_pixels,
            "corsOrigins": list(self.cors_origins),
        }

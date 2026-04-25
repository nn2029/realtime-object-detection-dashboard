"""Detector creation helpers."""

from __future__ import annotations

from pathlib import Path

from ..config import AppSettings
from .base import Detector, DetectorError
from .mock import MockDetector


def create_detector(settings: AppSettings) -> Detector:
    """Create the configured detector, falling back to mock for auto mode."""

    mode = settings.detector_mode.lower()
    if mode == "mock":
        return MockDetector(max_objects=settings.mock_max_objects)

    if mode in {"yolo", "auto"}:
        if mode == "auto" and not Path(settings.yolo_weights).exists():
            return MockDetector(max_objects=settings.mock_max_objects)

        try:
            from .yolo import UltralyticsYoloDetector

            return UltralyticsYoloDetector(settings.yolo_weights)
        except Exception as exc:
            if mode == "auto":
                return MockDetector(max_objects=settings.mock_max_objects)
            if isinstance(exc, DetectorError):
                raise
            raise DetectorError(f"Failed to initialize YOLO detector: {exc}") from exc

    raise DetectorError(f"Unknown detector mode: {settings.detector_mode}")

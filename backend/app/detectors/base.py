"""Detector abstraction shared by mock and YOLO implementations."""

from __future__ import annotations

from typing import Protocol

from ..models import Detection, FramePayload


class DetectorError(RuntimeError):
    """Raised when a detector cannot be initialized or run."""


class Detector(Protocol):
    """Minimal interface needed by the streaming frame processor."""

    name: str

    def detect(self, frame: FramePayload) -> list[Detection]:
        """Return detections for a frame.

        Implementations should return normalized boxes and avoid mutating the
        input payload. The processor treats detectors as synchronous because
        most model runtimes already manage their own optimized execution.
        """
        ...

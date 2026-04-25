"""Deterministic detector used for demos, tests, and offline development."""

from __future__ import annotations

import math

from ..models import Detection, FramePayload


class MockDetector:
    """Generate YOLO-shaped detections without model weights.

    Portfolio projects often need to run on review machines where GPU drivers,
    OpenCV wheels, or YOLO weights are unavailable. This detector keeps the
    WebSocket stream, overlay rendering, metrics, and event UI fully demoable
    while preserving the same contract used by a real YOLO implementation.
    """

    name = "mock-yolo"

    def __init__(self, max_objects: int = 4, empty_every: int = 11) -> None:
        self.max_objects = max(1, max_objects)
        self.empty_every = max(2, empty_every)
        self.labels = ("person", "robot", "bottle", "laptop", "chair", "wrench")
        self.colors = ("#22c55e", "#38bdf8", "#f97316", "#e879f9", "#f43f5e", "#a3e635")

    def detect(self, frame: FramePayload) -> list[Detection]:
        if frame.frame_id % self.empty_every == 0:
            return []

        count = (frame.frame_id % self.max_objects) + 1
        detections: list[Detection] = []

        for index in range(count):
            phase = frame.frame_id * 0.13 + index * 1.71
            width = 0.14 + 0.03 * ((frame.frame_id + index) % 3)
            height = 0.13 + 0.025 * ((frame.frame_id + index * 2) % 4)
            x = 0.04 + ((math.sin(phase) + 1.0) / 2.0) * (0.92 - width)
            y = 0.05 + ((math.cos(phase * 0.78) + 1.0) / 2.0) * (0.9 - height)
            confidence = 0.58 + ((math.sin(phase * 1.37) + 1.0) / 2.0) * 0.38

            detections.append(
                Detection(
                    label=self.labels[(frame.frame_id + index) % len(self.labels)],
                    confidence=confidence,
                    bbox=(x, y, width, height),
                    track_id=f"mock-{index}",
                    color=self.colors[index % len(self.colors)],
                ).normalized()
            )

        return detections

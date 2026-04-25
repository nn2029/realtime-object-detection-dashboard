"""Frame processing pipeline for WebSocket inference requests."""

from __future__ import annotations

import time
from typing import Any

from ..detectors.base import Detector
from ..models import FramePayload, FrameResult
from .metrics import StreamingMetrics


class FrameProcessor:
    """Convert client frame messages into detection responses.

    Streaming architecture note:
    The dashboard sends a frame, waits for the detection response, then sends
    the next eligible frame. That simple acknowledgement loop is deliberate
    backpressure: the server does not build an unbounded frame queue, and stale
    frames are skipped in favor of the latest view of the camera feed.
    """

    def __init__(self, detector: Detector, metrics: StreamingMetrics | None = None) -> None:
        self.detector = detector
        self.metrics = metrics or StreamingMetrics()

    def process_client_frame(self, message: dict[str, Any]) -> FrameResult:
        frame = FramePayload.from_client_message(message)
        timestamp = frame.timestamp or time.time()
        started_at = time.perf_counter()
        detections = self.detector.detect(frame)
        latency_ms = (time.perf_counter() - started_at) * 1000
        snapshot = self.metrics.record_frame(
            frame_id=frame.frame_id,
            timestamp=timestamp,
            detections=detections,
            latency_ms=latency_ms,
        )

        return FrameResult(
            frame_id=frame.frame_id,
            timestamp=timestamp,
            detector=self.detector.name,
            detections=detections,
            latency_ms=latency_ms,
            metrics=snapshot,
        )

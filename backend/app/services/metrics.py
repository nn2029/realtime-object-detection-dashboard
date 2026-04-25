"""Rolling metrics for a real-time detection stream."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from statistics import mean
from typing import Any, Deque

from ..models import Detection


@dataclass(frozen=True)
class MetricPoint:
    """A compact point used by the frontend timeline chart."""

    frame_id: int
    timestamp: float
    detections: int
    avg_confidence: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "frameId": self.frame_id,
            "timestamp": self.timestamp,
            "detections": self.detections,
            "avgConfidence": round(self.avg_confidence, 4),
        }


class StreamingMetrics:
    """Aggregate low-cost counters for each processed frame."""

    def __init__(self, max_history: int = 120) -> None:
        self.max_history = max(2, max_history)
        self.frames_seen = 0
        self.detections_seen = 0
        self.class_counts: Counter[str] = Counter()
        self._confidence_values: Deque[float] = deque(maxlen=self.max_history)
        self._latencies: Deque[float] = deque(maxlen=self.max_history)
        self._frame_times: Deque[float] = deque(maxlen=self.max_history)
        self._timeline: Deque[MetricPoint] = deque(maxlen=self.max_history)

    def record_frame(
        self,
        frame_id: int,
        timestamp: float,
        detections: list[Detection],
        latency_ms: float,
    ) -> dict[str, Any]:
        self.frames_seen += 1
        self.detections_seen += len(detections)
        self._latencies.append(latency_ms)
        self._frame_times.append(timestamp)

        confidence_values = [detection.confidence for detection in detections]
        self._confidence_values.extend(confidence_values)

        for detection in detections:
            self.class_counts[detection.label] += 1

        avg_frame_confidence = mean(confidence_values) if confidence_values else 0.0
        self._timeline.append(
            MetricPoint(
                frame_id=frame_id,
                timestamp=timestamp,
                detections=len(detections),
                avg_confidence=avg_frame_confidence,
            )
        )

        return self.snapshot(active_detections=len(detections))

    def snapshot(self, active_detections: int = 0) -> dict[str, Any]:
        average_confidence = mean(self._confidence_values) if self._confidence_values else 0.0
        average_latency = mean(self._latencies) if self._latencies else 0.0
        fps = self._fps()

        return {
            "framesSeen": self.frames_seen,
            "detectionsSeen": self.detections_seen,
            "activeDetections": active_detections,
            "avgConfidence": round(average_confidence, 4),
            "avgLatencyMs": round(average_latency, 2),
            "fps": round(fps, 2),
            "classCounts": dict(self.class_counts),
            "topLabels": self.class_counts.most_common(5),
            "timeline": [point.to_dict() for point in self._timeline],
        }

    def reset(self) -> None:
        self.frames_seen = 0
        self.detections_seen = 0
        self.class_counts.clear()
        self._confidence_values.clear()
        self._latencies.clear()
        self._frame_times.clear()
        self._timeline.clear()

    def _fps(self) -> float:
        if len(self._frame_times) < 2:
            return 0.0

        elapsed = self._frame_times[-1] - self._frame_times[0]
        if elapsed <= 0:
            return 0.0

        return (len(self._frame_times) - 1) / elapsed

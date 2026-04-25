from __future__ import annotations

import unittest

from app.models import Detection
from app.services.metrics import StreamingMetrics


class StreamingMetricsTest(unittest.TestCase):
    def test_records_counts_confidence_latency_and_fps(self) -> None:
        metrics = StreamingMetrics(max_history=5)
        first = [
            Detection("person", 0.9, (0.1, 0.1, 0.2, 0.2)),
            Detection("robot", 0.7, (0.4, 0.1, 0.2, 0.2)),
        ]
        second = [Detection("person", 0.8, (0.2, 0.3, 0.2, 0.2))]

        metrics.record_frame(frame_id=1, timestamp=10.0, detections=first, latency_ms=20.0)
        snapshot = metrics.record_frame(
            frame_id=2,
            timestamp=11.0,
            detections=second,
            latency_ms=40.0,
        )

        self.assertEqual(snapshot["framesSeen"], 2)
        self.assertEqual(snapshot["detectionsSeen"], 3)
        self.assertEqual(snapshot["activeDetections"], 1)
        self.assertEqual(snapshot["classCounts"], {"person": 2, "robot": 1})
        self.assertEqual(snapshot["topLabels"][0], ("person", 2))
        self.assertAlmostEqual(snapshot["avgConfidence"], 0.8)
        self.assertAlmostEqual(snapshot["avgLatencyMs"], 30.0)
        self.assertAlmostEqual(snapshot["fps"], 1.0)

    def test_history_is_bounded_while_totals_remain_cumulative(self) -> None:
        metrics = StreamingMetrics(max_history=2)

        for frame_id in range(1, 5):
            metrics.record_frame(
                frame_id=frame_id,
                timestamp=float(frame_id),
                detections=[Detection("person", 0.5, (0.1, 0.1, 0.2, 0.2))],
                latency_ms=10.0,
            )

        snapshot = metrics.snapshot()

        self.assertEqual(snapshot["framesSeen"], 4)
        self.assertEqual(snapshot["detectionsSeen"], 4)
        self.assertEqual(len(snapshot["timeline"]), 2)
        self.assertEqual(snapshot["timeline"][0]["frameId"], 3)

    def test_reset_clears_metrics(self) -> None:
        metrics = StreamingMetrics()
        metrics.record_frame(
            frame_id=1,
            timestamp=1.0,
            detections=[Detection("person", 0.9, (0.1, 0.1, 0.2, 0.2))],
            latency_ms=5.0,
        )

        metrics.reset()
        snapshot = metrics.snapshot()

        self.assertEqual(snapshot["framesSeen"], 0)
        self.assertEqual(snapshot["detectionsSeen"], 0)
        self.assertEqual(snapshot["classCounts"], {})
        self.assertEqual(snapshot["timeline"], [])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from app.detectors.mock import MockDetector
from app.models import FramePayload


class MockDetectorTest(unittest.TestCase):
    def test_mock_detector_is_deterministic(self) -> None:
        detector = MockDetector(max_objects=4)
        frame = FramePayload(frame_id=42, timestamp=1.0, width=640, height=480)

        first = [detection.to_dict() for detection in detector.detect(frame)]
        second = [detection.to_dict() for detection in detector.detect(frame)]

        self.assertEqual(first, second)

    def test_mock_detector_outputs_normalized_valid_detections(self) -> None:
        detector = MockDetector(max_objects=4)
        frame = FramePayload(frame_id=5, timestamp=1.0, width=640, height=480)

        detections = detector.detect(frame)

        self.assertGreater(len(detections), 0)
        for detection in detections:
            x, y, width, height = detection.bbox
            self.assertGreaterEqual(x, 0.0)
            self.assertGreaterEqual(y, 0.0)
            self.assertGreater(width, 0.0)
            self.assertGreater(height, 0.0)
            self.assertLessEqual(x + width, 1.0)
            self.assertLessEqual(y + height, 1.0)
            self.assertGreaterEqual(detection.confidence, 0.0)
            self.assertLessEqual(detection.confidence, 1.0)

    def test_mock_detector_can_emit_empty_frames(self) -> None:
        detector = MockDetector(max_objects=4, empty_every=3)
        frame = FramePayload(frame_id=6, timestamp=1.0, width=640, height=480)

        self.assertEqual(detector.detect(frame), [])


if __name__ == "__main__":
    unittest.main()

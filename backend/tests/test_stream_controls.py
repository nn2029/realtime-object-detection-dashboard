from __future__ import annotations

import unittest

from app.detectors.mock import MockDetector
from app.services.connection_limiter import StreamLimiter
from app.services.frame_processor import FrameProcessor


class StreamLimiterTest(unittest.TestCase):
    def test_limiter_rejects_connections_over_capacity(self) -> None:
        limiter = StreamLimiter(max_connections=1)

        self.assertTrue(limiter.try_acquire())
        self.assertFalse(limiter.try_acquire())

        limiter.release()
        self.assertTrue(limiter.try_acquire())


class FrameProcessorGuardTest(unittest.TestCase):
    def test_rejects_frames_above_pixel_budget(self) -> None:
        processor = FrameProcessor(
            detector=MockDetector(),
            max_frame_pixels=10_000,
        )

        with self.assertRaisesRegex(ValueError, "above the 10000 pixel limit"):
            processor.process_client_frame(
                {
                    "type": "frame",
                    "frameId": 1,
                    "timestamp": 1.0,
                    "width": 500,
                    "height": 500,
                }
            )


if __name__ == "__main__":
    unittest.main()

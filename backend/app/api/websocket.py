"""WebSocket stream endpoint for real-time detection."""

from __future__ import annotations

import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.frame_processor import FrameProcessor
from ..services.connection_limiter import StreamLimiter


def create_stream_router(
    processor: FrameProcessor,
    *,
    max_connections: int,
    target_fps: float,
) -> APIRouter:
    router = APIRouter()
    limiter = StreamLimiter(max_connections=max_connections)
    min_frame_interval = 1 / max(target_fps, 1.0)

    @router.websocket("/ws/detect")
    async def detect_stream(websocket: WebSocket) -> None:
        if not limiter.try_acquire():
            await websocket.accept()
            await websocket.send_json(
                {
                    "type": "error",
                    "payload": {"message": "Stream capacity reached. Try again shortly."},
                }
            )
            await websocket.close(code=1013)
            return

        await websocket.accept()
        await websocket.send_json(
            {
                "type": "ready",
                "payload": {
                    "detector": processor.detector.name,
                    "metrics": processor.metrics.snapshot(),
                    "stream": {
                        "activeConnections": limiter.active_connections,
                        "maxConnections": limiter.max_connections,
                        "targetFps": target_fps,
                    },
                },
            }
        )

        last_processed_at = 0.0
        try:
            while True:
                message = await websocket.receive_json()
                message_type = message.get("type", "frame")

                if message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue

                if message_type == "reset":
                    processor.metrics.reset()
                    await websocket.send_json(
                        {"type": "metrics", "payload": processor.metrics.snapshot()}
                    )
                    continue

                if message_type != "frame":
                    await websocket.send_json(
                        {"type": "error", "payload": {"message": "Unsupported message type"}}
                    )
                    continue

                now = time.monotonic()
                if now - last_processed_at < min_frame_interval:
                    retry_after = max(0.0, min_frame_interval - (now - last_processed_at))
                    await websocket.send_json(
                        {
                            "type": "throttled",
                            "payload": {
                                "retryAfterMs": round(retry_after * 1000, 1),
                                "metrics": processor.metrics.snapshot(),
                            },
                        }
                    )
                    continue

                try:
                    result = processor.process_client_frame(message)
                except ValueError as exc:
                    await websocket.send_json(
                        {"type": "error", "payload": {"message": str(exc)}}
                    )
                    continue

                last_processed_at = now
                await websocket.send_json({"type": "detections", "payload": result.to_dict()})
        except WebSocketDisconnect:
            return
        finally:
            limiter.release()

    return router

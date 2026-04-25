"""WebSocket stream endpoint for real-time detection."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.frame_processor import FrameProcessor


def create_stream_router(processor: FrameProcessor) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/detect")
    async def detect_stream(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json(
            {
                "type": "ready",
                "payload": {
                    "detector": processor.detector.name,
                    "metrics": processor.metrics.snapshot(),
                },
            }
        )

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

                # Processing is sequential per socket by design. This keeps the
                # freshest frame moving through the pipeline and avoids a memory
                # spike if a browser captures frames faster than inference runs.
                result = processor.process_client_frame(message)
                await websocket.send_json({"type": "detections", "payload": result.to_dict()})
        except WebSocketDisconnect:
            return

    return router

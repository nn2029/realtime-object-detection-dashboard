"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import create_api_router
from .api.websocket import create_stream_router
from .config import AppSettings
from .detectors import create_detector
from .services.frame_processor import FrameProcessor
from .services.metrics import StreamingMetrics


def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or AppSettings.from_env()
    detector = create_detector(settings)
    metrics = StreamingMetrics(max_history=settings.max_history)
    processor = FrameProcessor(
        detector=detector,
        metrics=metrics,
        max_frame_pixels=settings.max_frame_pixels,
    )

    app = FastAPI(
        title="Real-Time Object Detection Dashboard API",
        version="0.1.0",
        description="WebSocket inference API for webcam object detection dashboards.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(create_api_router(settings=settings, processor=processor), prefix="/api")
    app.include_router(
        create_stream_router(
            processor=processor,
            max_connections=settings.max_connections,
            target_fps=settings.target_fps,
        )
    )
    app.state.processor = processor
    app.state.settings = settings
    return app


app = create_app()

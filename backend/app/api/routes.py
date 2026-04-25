"""HTTP API routes for service status and current metrics."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import AppSettings
from ..services.frame_processor import FrameProcessor


def create_api_router(settings: AppSettings, processor: FrameProcessor) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "detector": processor.detector.name,
            "config": settings.public_dict(),
        }

    @router.get("/metrics")
    async def metrics() -> dict[str, object]:
        return processor.metrics.snapshot()

    @router.get("/config")
    async def config() -> dict[str, object]:
        return settings.public_dict()

    @router.post("/metrics/reset")
    async def reset_metrics() -> dict[str, object]:
        processor.metrics.reset()
        return processor.metrics.snapshot()

    return router

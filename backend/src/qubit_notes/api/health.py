from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    # platform service name to its status
    services: dict[str, str]
    error: str | None = None


@router.get("/config")
async def config(request: Request) -> dict:
    """what the browser needs before anyone signs in: how students sign in"""
    return request.app.state.authenticator.config()


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    platform_health = await run_in_threadpool(request.app.state.platform.health)
    return HealthResponse(
        status="ok" if platform_health.serving else "degraded",
        services=platform_health.services,
        error=platform_health.error,
    )

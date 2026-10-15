from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    providers: list[str]
    error: str | None = None


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    platform_health = await run_in_threadpool(request.app.state.platform.health)
    return HealthResponse(
        status="ok" if platform_health.reachable else "degraded",
        providers=platform_health.providers,
        error=platform_health.error,
    )

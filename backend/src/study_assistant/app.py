from fastapi import FastAPI

from study_assistant.api import health
from study_assistant.platform.port import StudyPlatform
from study_assistant.settings import Settings


def create_app(platform: StudyPlatform | None = None, settings: Settings | None = None) -> FastAPI:
    """Build the app. Tests pass their own ``platform``; otherwise it talks to gogi."""
    settings = settings or Settings()
    if platform is None:
        from study_assistant.platform.gogi_adapter import GogiPlatform

        platform = GogiPlatform(gateway_url=settings.gateway_url)

    app = FastAPI(title="Study Assistant")
    app.state.platform = platform
    app.state.settings = settings
    app.include_router(health.router, prefix="/api")
    return app

from fastapi import FastAPI

from study_assistant.api import courses, health, materials
from study_assistant.api.errors import add_error_handlers
from study_assistant.domain.courses import Courses
from study_assistant.domain.materials import Materials
from study_assistant.domain.memory import StudentMemory
from study_assistant.platform.port import StudyPlatform
from study_assistant.settings import Settings


def create_app(platform: StudyPlatform | None = None, settings: Settings | None = None) -> FastAPI:
    """Build the app. Tests pass their own ``platform``; otherwise it talks to gogi."""
    settings = settings or Settings()
    if platform is None:
        from study_assistant.platform.gogi_adapter import GogiPlatform

        platform = GogiPlatform(settings)

    app = FastAPI(title="Study Assistant")
    app.state.platform = platform
    app.state.settings = settings
    app.state.memory = StudentMemory(platform)
    app.state.courses = Courses(platform)
    app.state.materials = Materials(platform, app.state.courses, app.state.memory)

    add_error_handlers(app)
    for router in (health.router, courses.router, materials.router):
        app.include_router(router, prefix="/api")
    return app

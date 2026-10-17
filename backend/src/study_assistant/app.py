from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from study_assistant import storage
from study_assistant.api import courses, health, materials, notes, reading, study
from study_assistant.api.errors import add_error_handlers
from study_assistant.domain.courses import Courses
from study_assistant.domain.materials import Materials
from study_assistant.domain.memory import StudentMemory
from study_assistant.domain.notes import Notes
from study_assistant.domain.quizzes import Quizzes
from study_assistant.domain.reading import Reading
from study_assistant.domain.sources import Sources
from study_assistant.domain.summaries import Summaries
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
    app.state.materials = Materials(platform, app.state.courses, app.state.memory, settings.max_upload_mb)
    app.state.reading = Reading(platform, app.state.courses)
    app.state.database = storage.connect(settings.database_url)
    app.state.notes = Notes(app.state.database, app.state.reading)
    sources = Sources(platform, app.state.courses, app.state.reading)
    app.state.summaries = Summaries(app.state.database, platform, sources)
    app.state.quizzes = Quizzes(app.state.database, platform, sources)
    # deleting a material deletes everyone's notes, summaries and quizzes on it
    for service in (app.state.notes, app.state.summaries, app.state.quizzes):
        app.state.materials.on_delete(service.forget_material)

    add_error_handlers(app)
    for router in (health.router, courses.router, materials.router, reading.router, notes.router, study.router):
        app.include_router(router, prefix="/api")
    if settings.frontend_dir:
        app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
    return app

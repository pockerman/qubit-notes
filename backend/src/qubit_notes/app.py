from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from qubit_notes import storage
from qubit_notes.api import assistant, courses, health, images, materials, notes, reading, references, study
from qubit_notes.api.auth import authenticator
from qubit_notes.api.errors import add_error_handlers
from qubit_notes.domain.assistant import Assistant
from qubit_notes.domain.conversions import Conversions
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.images import Images
from qubit_notes.domain.materials import Materials
from qubit_notes.domain.memory import StudentMemory
from qubit_notes.domain.notes import Notes
from qubit_notes.domain.quizzes import Quizzes
from qubit_notes.domain.reading import Reading
from qubit_notes.domain.references import References
from qubit_notes.domain.sources import Sources
from qubit_notes.domain.summaries import Summaries
from qubit_notes.domain.topics import Topics
from qubit_notes.platform import platform_from
from qubit_notes.platform.named import NamedDocuments
from qubit_notes.platform.port import StudyPlatform
from qubit_notes.settings import Settings


@asynccontextmanager
async def _lifespan(app: FastAPI):
    yield
    # conversions and the app's own platform's ingestions stop; what they haven't finished is done when the app
    # starts again
    app.state.conversions.stop()
    if stop := getattr(app.state.platform, "stop", None):
        stop()


def create_app(platform: StudyPlatform | None = None, settings: Settings | None = None) -> FastAPI:
    """Build the app. Tests pass their own ``platform``; otherwise it's the one the settings name: the app's own, or
    gogi."""
    settings = settings or Settings()
    database = storage.connect(settings.database_url)
    if platform is None:
        platform = platform_from(settings, database)

    # a converted PDF's Markdown keeps the PDF's name, but platforms read it as Markdown by a name ending in .md
    platform = NamedDocuments(platform)

    app = FastAPI(title="Qubit Notes", lifespan=_lifespan)
    app.state.platform = platform
    app.state.settings = settings
    app.state.authenticator = authenticator(settings)
    app.state.memory = StudentMemory(platform)
    app.state.courses = Courses(platform)
    app.state.images = Images(platform, app.state.courses)
    app.state.conversions = Conversions(database, platform, app.state.courses, app.state.images)
    app.state.topics = Topics(database, platform, app.state.courses)
    app.state.references = References(platform, app.state.courses, app.state.topics)
    app.state.materials = Materials(
        platform,
        app.state.courses,
        app.state.memory,
        settings.max_upload_mb,
        app.state.conversions,
        app.state.references,
    )
    app.state.reading = Reading(platform, app.state.courses, app.state.conversions)
    # a deleted material's images go with it, as does a converted one's original
    app.state.materials.on_delete_in_course(app.state.images.forget)
    app.state.materials.on_delete_in_course(app.state.conversions.forget)
    app.state.conversions.resume()
    app.state.database = database
    app.state.notes = Notes(app.state.database, app.state.reading)
    app.state.materials.on_upload(app.state.topics.ensure)
    sources = Sources(platform, app.state.courses, app.state.reading)
    app.state.summaries = Summaries(app.state.database, platform, sources)
    app.state.quizzes = Quizzes(app.state.database, platform, sources)
    app.state.assistant = Assistant(
        app.state.database, platform, app.state.courses, app.state.reading, app.state.summaries, app.state.quizzes
    )
    # deleting a material deletes everyone's notes, summaries, quizzes and conversations on it
    for service in (app.state.notes, app.state.summaries, app.state.quizzes, app.state.assistant):
        app.state.materials.on_delete(service.forget_material)
    # deleting a course deletes all of that, its topics, and what the assistant learned from its material
    app.state.courses.on_delete(app.state.materials.forget_course)
    for service in (app.state.notes, app.state.summaries, app.state.quizzes, app.state.assistant, app.state.topics):
        app.state.courses.on_delete(lambda course, forget=service.forget_course: forget(course.id))

    add_error_handlers(app)
    for router in (
        health.router,
        courses.router,
        materials.router,
        images.router,
        reading.router,
        references.router,
        notes.router,
        study.router,
        assistant.router,
    ):
        app.include_router(router, prefix="/api")
    if settings.frontend_dir:
        app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
    return app

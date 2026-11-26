from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from qubit_notes import storage
from qubit_notes.api import (
    account,
    ai_model,
    app_keys,
    assistant,
    audio,
    comprehension,
    courses,
    generating,
    health,
    images,
    lessons,
    materials,
    notes,
    papers,
    programs,
    prompts,
    reading,
    references,
    repositories,
    study,
    usage,
    writing_assistant,
)
from qubit_notes.api.auth import authenticator
from qubit_notes.api.errors import add_error_handlers
from qubit_notes.domain.account import Account
from qubit_notes.domain.ai_model import AIModel
from qubit_notes.domain.app_keys import AppKeys
from qubit_notes.domain.assistant import Assistant
from qubit_notes.domain.audio import Audios
from qubit_notes.domain.comprehension import ComprehensionAssistantAgent
from qubit_notes.domain.conversions import Conversions
from qubit_notes.domain.course_titles import CourseTitles
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.flashcards import Flashcards
from qubit_notes.domain.generating import Generator
from qubit_notes.domain.images import Images
from qubit_notes.domain.lessons import Lessons
from qubit_notes.domain.material_order import MaterialOrder
from qubit_notes.domain.materials import Materials
from qubit_notes.domain.memory import StudentMemory
from qubit_notes.domain.notes import Notes
from qubit_notes.domain.papers import PaperRecords, Papers
from qubit_notes.domain.programs import programs as programs_from
from qubit_notes.domain.prompt_versions import PromptVersions
from qubit_notes.domain.quizzes import Quizzes
from qubit_notes.domain.reading import Reading
from qubit_notes.domain.reading_order import ReadingOrder
from qubit_notes.domain.reading_progress import ReadingProgress
from qubit_notes.domain.references import References
from qubit_notes.domain.reviews import Reviews
from qubit_notes.domain.sources import Sources
from qubit_notes.domain.subject_download import SubjectDownload
from qubit_notes.domain.subject_repositories import GitHost, SubjectRepositories
from qubit_notes.domain.summaries import Summaries
from qubit_notes.domain.topics import Topics
from qubit_notes.domain.tracing import Tracer, Traces
from qubit_notes.domain.transcription import Transcription
from qubit_notes.domain.usage import AIUsage
from qubit_notes.domain.writing_assistant import WriteMaterialAssistantAgent
from qubit_notes.github import GitHub
from qubit_notes.platform import platform_from
from qubit_notes.platform.named import NamedDocuments
from qubit_notes.platform.port import StudyPlatform
from qubit_notes.platform.standalone.files import files_from
from qubit_notes.prompts import DIRECTORY, Prompts
from qubit_notes.prompts import use as use_prompts
from qubit_notes.settings import Settings
from qubit_notes.tracers import tracer_from


@asynccontextmanager
async def _lifespan(app: FastAPI):
    yield
    # conversions and the app's own platform's ingestions stop; what they haven't finished is done when the app
    # starts again
    app.state.conversions.stop()
    app.state.lessons.stop()
    # the traces still to be sent are sent
    app.state.traces.stop()
    if stop := getattr(app.state.platform, "stop", None):
        stop()


def create_app(
    platform: StudyPlatform | None = None,
    settings: Settings | None = None,
    tracer: Tracer | None = None,
    git_host: GitHost | None = None,
) -> FastAPI:
    """Build the app. Tests pass their own ``platform``; otherwise it's the one the settings name: the app's own, or
    gogi. Likewise the ``tracer`` the AI is traced to: Langfuse where the settings have its keys, and the
    ``git_host`` students push their subjects to: GitHub."""
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
    app.state.account = Account(settings)
    # the keys the admins gave the app, given to its platform again
    # the prompts the AI is given, at the version in use: prompt.toml's, or the one the admins chose
    app.state.prompt_versions = PromptVersions(database)
    app.state.prompt_versions.prompts = Prompts(
        Path(settings.prompts_dir) if settings.prompts_dir else DIRECTORY, chosen=app.state.prompt_versions.chosen
    )
    # a prompt.toml naming a version that doesn't exist is refused now, rather than when the AI is asked
    app.state.prompt_versions.prompts.validate()
    use_prompts(app.state.prompt_versions.prompts)
    app.state.app_keys = AppKeys(database, settings, platform)
    app.state.app_keys.restore()
    # the AI's model, as the admins chose it or the settings name it
    app.state.ai_model = AIModel(database, settings, platform)
    app.state.ai_model.restore()
    app.state.memory = StudentMemory(platform)
    app.state.courses = Courses(platform)
    # which courses are collections of papers, and the papers' details
    app.state.paper_records = PaperRecords(database)
    app.state.images = Images(platform, app.state.courses)
    app.state.conversions = Conversions(database, platform, app.state.courses, app.state.images)
    app.state.topics = Topics(database, platform, app.state.courses)
    app.state.references = References(platform, app.state.courses, app.state.topics)
    app.state.material_order = MaterialOrder(database)
    app.state.materials = Materials(
        platform,
        app.state.courses,
        app.state.memory,
        settings.max_upload_mb,
        app.state.conversions,
        app.state.references,
        app.state.material_order,
    )
    app.state.programs = programs_from(settings)
    app.state.reading = Reading(platform, app.state.courses, app.state.conversions)
    # a deleted material's images go with it, as does a converted one's original
    app.state.materials.on_delete_in_course(app.state.images.forget)
    app.state.materials.on_delete_in_course(app.state.conversions.forget)
    app.state.materials.on_delete_in_course(app.state.material_order.forget)
    app.state.conversions.resume()
    app.state.database = database
    app.state.notes = Notes(app.state.database, app.state.reading)
    app.state.reading_progress = ReadingProgress(app.state.database, app.state.reading)
    app.state.materials.on_upload(app.state.topics.ensure)
    app.state.lessons = Lessons(
        database, platform, app.state.courses, app.state.topics, app.state.materials, app.state.images
    )
    # the original of lessons goes with the last of their materials
    app.state.materials.on_delete_in_course(app.state.lessons.forget)
    app.state.lessons.resume()
    # a deleted topic's material goes with it
    app.state.topics.on_delete(app.state.materials.delete_topic)
    app.state.reading_order = ReadingOrder(app.state.courses, app.state.topics, app.state.materials)
    # every call to the AI goes through it, so that it is counted and traced; the traces go with the material they
    # hold, and those Langfuse couldn't delete before are tried again
    app.state.traces = Traces(database, tracer or tracer_from(settings))
    app.state.traces.retry_deletions_in_background()
    app.state.ai_usage = AIUsage(database, platform, app.state.traces)
    app.state.generator = Generator(platform, app.state.ai_usage, app.state.courses, app.state.reading)
    sources = Sources(platform, app.state.courses, app.state.reading)
    app.state.summaries = Summaries(app.state.database, app.state.ai_usage, sources)
    app.state.quizzes = Quizzes(app.state.database, app.state.ai_usage, sources)
    app.state.reviews = Reviews(
        app.state.database, app.state.courses, platform, app.state.topics, app.state.paper_records
    )
    app.state.flashcards = Flashcards(app.state.database, app.state.ai_usage, sources, app.state.reviews)
    app.state.subject_download = SubjectDownload(
        platform,
        app.state.courses,
        app.state.topics,
        app.state.materials,
        app.state.conversions,
        app.state.images,
        app.state.reviews,
    )
    # the repositories students push their subjects to
    app.state.subject_repositories = SubjectRepositories(
        database,
        settings.secret_key,
        git_host or GitHub(),
        app.state.courses,
        app.state.topics,
        app.state.materials,
        app.state.notes,
        app.state.summaries,
        app.state.quizzes,
        app.state.flashcards,
        app.state.reviews,
        platform,
        app.state.images,
    )
    app.state.assistant = Assistant(
        app.state.database,
        platform,
        app.state.courses,
        app.state.reading,
        app.state.summaries,
        app.state.quizzes,
        app.state.flashcards,
        app.state.ai_usage,
        app.state.paper_records,
    )
    # each student's audio of a material, its MP3s with the app's files
    app.state.audios = Audios(
        app.state.database,
        platform,
        app.state.courses,
        sources,
        app.state.ai_usage,
        files_from(settings),
        settings.speech_model,
    )
    # checks of a student's understanding, and what they say, heard, to answer by voice
    app.state.comprehension = ComprehensionAssistantAgent(
        app.state.database, platform, app.state.courses, sources, app.state.ai_usage
    )
    app.state.transcription = Transcription(platform, app.state.ai_usage, settings.transcription_model)
    # what is written about the material: everyone's notes, summaries, quizzes, flashcards and conversations on it
    written = (
        app.state.notes,
        app.state.reading_progress,
        app.state.summaries,
        app.state.quizzes,
        app.state.flashcards,
        app.state.assistant,
        app.state.audios,
        app.state.comprehension,
    )
    # deleting a material deletes all of that
    for service in (*written, app.state.traces):
        app.state.materials.on_delete(service.forget_material)
    # deleting a course deletes all of that, its topics, and what the assistant learned from its material
    app.state.courses.on_delete(app.state.materials.forget_course)
    app.state.courses.on_delete(lambda course: app.state.material_order.forget_course(course.id))
    app.state.course_titles = CourseTitles(database, app.state.courses, app.state.paper_records.collections)
    app.state.courses.on_delete(app.state.course_titles.forget)
    # collections of papers: courses of their own, apart from the student's courses
    # the writing assistant: help writing material, from the web
    app.state.writing_assistant = WriteMaterialAssistantAgent(
        database, platform, app.state.courses, app.state.course_titles, app.state.topics, app.state.ai_usage
    )
    app.state.courses.on_delete(lambda course: app.state.writing_assistant.forget_course(course.id))
    app.state.papers = Papers(app.state.paper_records, app.state.courses, app.state.course_titles, app.state.materials)
    app.state.materials.on_delete(app.state.paper_records.forget_material)
    app.state.courses.on_delete(lambda course: app.state.paper_records.forget_course(course.id))
    for service in (*written, app.state.topics, app.state.traces, app.state.subject_repositories):
        app.state.courses.on_delete(lambda course, forget=service.forget_course: forget(course.id))

    add_error_handlers(app)
    # a student's AI requests answered by the provider they chose
    app.add_middleware(ai_model.ChosenProvider)
    for router in (
        health.router,
        app_keys.router,
        ai_model.router,
        account.router,
        courses.router,
        materials.router,
        lessons.router,
        papers.router,
        images.router,
        reading.router,
        references.router,
        generating.router,
        notes.router,
        study.router,
        programs.router,
        assistant.router,
        audio.router,
        audio.models_router,
        writing_assistant.router,
        comprehension.router,
        comprehension.transcription_router,
        usage.router,
        prompts.router,
        repositories.router,
    ):
        app.include_router(router, prefix="/api")
    if settings.frontend_dir:
        app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
    return app

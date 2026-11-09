"""The audio of a material (features/material_audio.feature): a narration of it the AI writes to be listened to,
following the student's instructions, read aloud by OpenAI's speech model.

Each student has at most one audio of a material, their own. Making it takes a while, so it is made in the
background: it is "generating" until it is "ready", or has "failed", saying why. Its file is kept with the app's
files, under audio/; the rest in the app's database.
"""

import contextvars
import json
import re
import uuid
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import datetime
from typing import Literal

from loguru import logger
from pydantic import BaseModel, ValidationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import Conflict, InvalidRequest, NotFound, Unavailable
from qubit_notes.domain.materials import is_video
from qubit_notes.domain.sources import Scope, Sources, SourceText
from qubit_notes.domain.usage import AIUsage
from qubit_notes.domain.written import now
from qubit_notes.platform.port import PlatformError, StudyPlatform
from qubit_notes.platform.standalone.files import Files

Status = Literal["generating", "ready", "failed"]
CONTENT_TYPE = "audio/mpeg"
# what the AI narrates at once, as for summaries; a longer material is narrated in parts, one after the other
MAX_CHARACTERS = 60_000
# what OpenAI's speech model reads aloud at once; a longer narration is read in parts, its MP3s one after the other
MAX_SPEECH_CHARACTERS = 3_000
# of an earlier narration, what the AI is given to improve on
MAX_EARLIER_CHARACTERS = 30_000
MAX_INSTRUCTIONS = 2_000
VOICE = "Clear, warm and unhurried, like a good teacher explaining to one student."


class SpeechModel(BaseModel):
    """one of OpenAI's speech models, as the student chooses it"""

    id: str
    name: str
    # whether it is told how to speak the narration; the others read it as they do
    follows_instructions: bool


SPEECH_MODELS = [
    SpeechModel(id="gpt-4o-mini-tts", name="GPT-4o mini TTS", follows_instructions=True),
    SpeechModel(id="tts-1", name="TTS-1 (fast)", follows_instructions=False),
    SpeechModel(id="tts-1-hd", name="TTS-1 HD (best sound)", follows_instructions=False),
]
_SPEECH_MODELS = {model.id: model for model in SPEECH_MODELS}


class SpeechModels(BaseModel):
    """the speech models to choose from, the app's own, which reads it if none is chosen, and whether it can speak"""

    models: list[SpeechModel]
    default: str
    available: bool


SYSTEM = (
    "You write narrations of a student's study material, to be listened to rather than read, e.g. on a walk. "
    "Write plain spoken English with no Markdown, headings, lists, links or symbols: say formulas and equations in "
    "words, describe code, tables and figures rather than read them out, and say where one part ends and the next "
    "begins. Keep to what the material says, in its order, unless the student's instructions say otherwise; follow "
    "them. Also say, in a sentence or two, how the narration is to be spoken (voice, tone, pace), from the "
    "instructions if they say."
)


class Narration(BaseModel):
    """what the AI writes: the narration, and how it is to be spoken"""

    narration: str
    voice: str = ""


class Audio(BaseModel):
    """A student's audio of a material."""

    id: str
    course_id: str
    document_id: str
    status: Status
    # what the student asked it to be, and what they last suggested to improve it, if they did
    instructions: str = ""
    suggestions: str = ""
    # what the AI wrote, read aloud; empty until it is ready
    narration: str = ""
    # the speech model it is read by
    model: str
    # why it failed
    error: str | None = None
    size: int = 0
    created_at: datetime
    updated_at: datetime


class AudioFile(BaseModel):
    filename: str
    content_type: str
    content: bytes


def _text(sources: list[SourceText]) -> str:
    return "\n\n".join(f"## {s.title}\n\n{s.content}" for s in sources)


def _batches(sources: list[SourceText]) -> list[list[SourceText]]:
    batches, batch, size = [], [], 0
    for source in sources:
        length = len(source.content) + len(source.title)
        if batch and size + length > MAX_CHARACTERS:
            batches.append(batch)
            batch, size = [], 0
        batch.append(source)
        size += length
    return batches + [batch] if batch else batches


def parts(narration: str, limit: int = MAX_SPEECH_CHARACTERS) -> list[str]:
    """the narration in parts of at most ``limit`` characters, split between paragraphs, else sentences, else words"""
    pieces: list[str] = []
    for paragraph in (p.strip() for p in re.split(r"\n\s*\n", narration)):
        if not paragraph:
            continue
        if len(paragraph) <= limit:
            pieces.append(paragraph)
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
            while len(sentence) > limit:
                cut = sentence.rfind(" ", 0, limit)
                cut = cut if cut > 0 else limit
                pieces.append(sentence[:cut])
                sentence = sentence[cut:].strip()
            if sentence:
                pieces.append(sentence)
    joined: list[str] = []
    for piece in pieces:
        if joined and len(joined[-1]) + 2 + len(piece) <= limit:
            joined[-1] = f"{joined[-1]}\n\n{piece}"
        else:
            joined.append(piece)
    return joined


class Audios:
    def __init__(
        self,
        engine: Engine,
        platform: StudyPlatform,
        courses: Courses,
        sources: Sources,
        ai: AIUsage,
        files: Files,
        speech_model: str = "gpt-4o-mini-tts",
        executor: Executor | None = None,
    ):
        self._engine = engine
        self._platform = platform
        self._courses = courses
        self._sources = sources
        self._ai = ai
        self._files = files
        # the app's own speech model, which reads it if the student chooses none
        self._speech_model = speech_model if speech_model in _SPEECH_MODELS else SPEECH_MODELS[0].id
        self._executor = executor or ThreadPoolExecutor(max_workers=2, thread_name_prefix="audio")
        self._interrupted()

    # what the student sees and does

    def speech_models(self) -> SpeechModels:
        return SpeechModels(models=SPEECH_MODELS, default=self._speech_model, available=self._platform.can_speak())

    def get(self, student: str, course_id: str, document_id: str) -> Audio | None:
        self._material(student, course_id, document_id)
        row = self._row(student, document_id)
        return _audio(row) if row else None

    def request(
        self, student: str, course_id: str, document_id: str, instructions: str = "", model: str | None = None
    ) -> Audio:
        """starts making the student's audio of the material, following their instructions, read by the model"""
        instructions = _checked(instructions)
        model = self._model(model)
        self._ready_to_make(student, course_id, document_id)
        if (row := self._row(student, document_id)) is not None:
            if row.status == "generating":
                raise Conflict("its audio is being made; wait until it is ready")
            raise Conflict("it has audio already: delete it, or improve it, first")
        at = now()
        values = {
            "id": uuid.uuid4().hex,
            "student": student,
            "course_id": course_id,
            "document_id": document_id,
            "status": "generating",
            "instructions": instructions,
            "suggestions": "",
            "narration": "",
            "voice": "",
            "model": model,
            "created_at": at,
            "updated_at": at,
        }
        with self._engine.begin() as connection:
            connection.execute(insert(storage.material_audio).values(**values))
        made = _audio(self._row(student, document_id))
        self._start(student, values["id"], course_id, document_id, instructions, None, model)
        return made

    def improve(
        self, student: str, course_id: str, document_id: str, suggestions: str, model: str | None = None
    ) -> Audio:
        """starts making the audio anew, from the material, its earlier narration and the student's suggestions, read
        by the model chosen now"""
        suggestions = _checked(suggestions)
        model = self._model(model)
        if not suggestions:
            raise InvalidRequest("say what to change")
        self._ready_to_make(student, course_id, document_id)
        row = self._row(student, document_id)
        if row is None or (row.status == "failed" and not row.narration):
            raise NotFound("it has no audio to improve; ask for one")
        if row.status == "generating":
            raise Conflict("its audio is being made; wait until it is ready")
        with self._engine.begin() as connection:
            connection.execute(
                update(storage.material_audio)
                .where(storage.material_audio.c.id == row.id)
                .values(status="generating", suggestions=suggestions, model=model, error=None, updated_at=now())
            )
        earlier = (row.narration, suggestions)
        made = _audio(self._row(student, document_id))
        self._start(student, row.id, course_id, document_id, row.instructions, earlier, model)
        return made

    def delete(self, student: str, course_id: str, document_id: str) -> None:
        self._material(student, course_id, document_id)
        row = self._row(student, document_id)
        if row is None:
            raise NotFound("it has no audio of yours")
        if row.status == "generating":
            raise Conflict("its audio is being made; delete it once it is ready")
        self._forget([row])

    def file(self, student: str, course_id: str, document_id: str) -> AudioFile:
        material = self._material(student, course_id, document_id)
        row = self._row(student, document_id)
        content = self._files.get(_key(row.id)) if row and row.status == "ready" else None
        if content is None:
            raise NotFound("it has no audio of yours to listen to")
        stem = material.filename.rsplit(".", 1)[0]
        return AudioFile(filename=f"{stem}.mp3", content_type=CONTENT_TYPE, content=content)

    # what is deleted with what it is of

    def forget_material(self, document_id: str) -> None:
        self._forget(self._rows(storage.material_audio.c.document_id == document_id))

    def forget_course(self, course_id: str) -> None:
        self._forget(self._rows(storage.material_audio.c.course_id == course_id))

    # making it

    def _ready_to_make(self, student: str, course_id: str, document_id: str) -> None:
        material = self._material(student, course_id, document_id)
        if is_video(material.content_type) or not material.content_type.startswith("text/"):
            raise InvalidRequest("only text has audio: a video or an image has nothing to narrate")
        if not self._platform.can_speak():
            raise Unavailable("audio needs the app's OpenAI key, to read the narration aloud")

    def _start(
        self,
        student: str,
        audio_id: str,
        course_id: str,
        document_id: str,
        instructions: str,
        earlier: tuple[str, str] | None,
        model: str,
    ) -> None:
        # the AI the student chose, which the request names, also writes the narration in the background
        context = contextvars.copy_context()
        self._executor.submit(
            context.run, self._make, student, audio_id, course_id, document_id, instructions, earlier, model
        )

    def _make(
        self,
        student: str,
        audio_id: str,
        course_id: str,
        document_id: str,
        instructions: str,
        earlier: tuple[str, str] | None,
        model: str,
    ) -> None:
        try:
            sources = self._sources.gather(student, Scope(course_id=course_id, document_id=document_id)).sources
            if not sources:
                raise InvalidRequest("the material has no text to narrate yet")
            batches = _batches(sources)
            narrated = [
                self._narrate(student, batch, instructions, earlier, i, len(batches))
                for i, batch in enumerate(batches, start=1)
            ]
            narration = "\n\n".join(n.narration.strip() for n in narrated)
            voice = next((n.voice.strip() for n in narrated if n.voice.strip()), VOICE)
            # only a model that follows how to speak it is told
            how = voice if _SPEECH_MODELS[model].follows_instructions else ""
            audio = b"".join(self._ai.speak(student, "audio", part, how, model).audio for part in parts(narration))
            self._files.put(_key(audio_id), audio, CONTENT_TYPE)
            self._update(audio_id, status="ready", narration=narration, voice=voice, size=len(audio), error=None)
        except Exception as e:  # noqa: BLE001 - whatever went wrong, the student is told, not left waiting
            logger.error(f"the audio {audio_id} could not be made: {e}")
            self._update(audio_id, status="failed", error=_why(e))

    def _narrate(
        self,
        student: str,
        batch: list[SourceText],
        instructions: str,
        earlier: tuple[str, str] | None,
        part: int,
        of: int,
    ) -> Narration:
        prompt = [f"The student's instructions: {instructions or '(none)'}"]
        if earlier:
            narration, suggestions = earlier
            prompt += [
                f"An earlier narration of the material:\n\n{narration[:MAX_EARLIER_CHARACTERS]}",
                f"The student's suggestions to improve it: {suggestions}\n\nWrite a new narration that follows them.",
            ]
        what = f"part {part} of {of} of the material" if of > 1 else "the material"
        prompt.append(f"Narrate {what}:\n\n{_text(batch)}")
        reply = ""
        for _ in range(2):
            reply = self._ai.complete(
                student, "audio", SYSTEM, "\n\n".join(prompt), json_schema=Narration.model_json_schema()
            )
            try:
                narrated = Narration.model_validate(json.loads(reply))
                if narrated.narration.strip():
                    return narrated
            except (ValueError, ValidationError) as e:
                logger.warning(f"the AI's narration is not valid: {e}")
        raise InvalidRequest("the AI could not write a narration of it; try again")

    # the database and the files

    def _model(self, model: str | None) -> str:
        if not model:
            return self._speech_model
        if model not in _SPEECH_MODELS:
            raise InvalidRequest(f"choose one of the speech models: {', '.join(_SPEECH_MODELS)}")
        return model

    def _material(self, student: str, course_id: str, document_id: str):
        course = self._courses.get_by_id(student, course_id)
        material = self._platform.get_document(course.id, document_id)
        if material is None:
            raise NotFound(f"no material {document_id!r} in the course")
        return material

    def _row(self, student: str, document_id: str):
        table = storage.material_audio
        with self._engine.connect() as connection:
            return connection.execute(
                select(table).where(table.c.student == student, table.c.document_id == document_id)
            ).first()

    def _rows(self, condition) -> list:
        with self._engine.connect() as connection:
            return connection.execute(select(storage.material_audio).where(condition)).all()

    def _update(self, audio_id: str, **values) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                update(storage.material_audio)
                .where(storage.material_audio.c.id == audio_id)
                .values(**values, updated_at=now())
            )

    def _forget(self, rows: list) -> None:
        for row in rows:
            self._files.delete(_key(row.id))
        with self._engine.begin() as connection:
            connection.execute(
                delete(storage.material_audio).where(storage.material_audio.c.id.in_([row.id for row in rows]))
            )

    def _interrupted(self) -> None:
        """audio left being made when the app last stopped won't be"""
        with self._engine.begin() as connection:
            connection.execute(
                update(storage.material_audio)
                .where(storage.material_audio.c.status == "generating")
                .values(status="failed", error="the app stopped while it was being made; delete it and ask again")
            )


def _key(audio_id: str) -> str:
    return f"audio/{audio_id}.mp3"


def _checked(text: str) -> str:
    text = text.strip()
    if len(text) > MAX_INSTRUCTIONS:
        raise InvalidRequest(f"instructions and suggestions can be at most {MAX_INSTRUCTIONS} characters")
    return text


def _why(error: Exception) -> str:
    if isinstance(error, PlatformError):
        return f"OpenAI couldn't read it aloud: {error.details}"
    if isinstance(error, InvalidRequest):
        return str(error)
    return "something went wrong while making it; delete it and try again"


def _audio(row) -> Audio:
    return Audio(
        id=row.id,
        course_id=row.course_id,
        document_id=row.document_id,
        status=row.status,
        instructions=row.instructions,
        suggestions=row.suggestions,
        narration=row.narration if row.status != "generating" else "",
        model=row.model,
        error=row.error,
        size=row.size or 0,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )

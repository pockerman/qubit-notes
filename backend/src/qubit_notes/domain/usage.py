"""How many tokens the AI uses, on what and for whom (features/ai_usage.feature), and the traces of its calls
(features/tracing.feature).

Every call to the AI goes through ``AIUsage``, which records what it took and traces it. A call that fails at the
provider took nothing we can know of, and isn't recorded, but is traced; a reply the app can't use took tokens all the
same, and is recorded, and traced as unusable.

A call is a step of the trace open around it (``AIUsage.traced``), or else of a trace of its own.
"""

import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from qubit_notes import storage
from qubit_notes.domain.errors import NotAllowed
from qubit_notes.domain.tracing import Step, Traces
from qubit_notes.domain.written import now
from qubit_notes.platform.port import Completion, Message, Researched, Speech, StudyPlatform, Transcript

DAYS = 30


class Spent(BaseModel):
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class SpentOn(Spent):
    purpose: str


class SpentWith(Spent):
    provider: str
    model: str


class Usage(Spent):
    """a student's usage over the last ``days`` days, in all, by purpose and by model; most tokens first"""

    days: int
    purposes: list[SpentOn] = []
    models: list[SpentWith] = []


class StudentUsage(Spent):
    student: str


def _spent():
    table = storage.ai_usage
    total = func.sum(table.c.input_tokens + table.c.output_tokens)
    columns = (
        func.count().label("requests"),
        func.coalesce(func.sum(table.c.input_tokens), 0).label("input_tokens"),
        func.coalesce(func.sum(table.c.output_tokens), 0).label("output_tokens"),
    )
    return columns, total


class AIUsage:
    """Calls the AI for a student, for a purpose, traces those calls, and tells what they took. ``now`` is the clock it
    goes by."""

    def __init__(
        self,
        engine: Engine,
        platform: StudyPlatform,
        traces: Traces | None = None,
        clock: Callable[[], datetime] = now,
    ):
        self._engine = engine
        self._platform = platform
        if traces is None:
            from qubit_notes.tracers import NoTracer

            traces = Traces(engine, NoTracer())
        self.traces = traces
        self.now = clock

    def traced(self, student: str, purpose: str, session_id: str | None = None):
        """the trace of the calls to the AI made inside it, as one thing the student asked for"""
        return self.traces.trace(student, purpose, session_id)

    def complete(
        self,
        student: str,
        purpose: str,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
        usable: Callable[[str], object] | None = None,
    ) -> str:
        """what the AI answers, recorded as used by the student for the purpose; ``usable`` tells whether the app can
        use it, returning something or raising ValueError, so its trace says"""
        with self.traced(student, purpose):
            step = _step("generation", purpose, system, {"prompt": prompt, "history": len(history or [])})
            with self.traces.step(step):
                completion = _called(
                    step, lambda: self._platform.complete(system, prompt, json_schema=json_schema, history=history)
                )
                step.output = completion.text
                if usable is not None:
                    _check(step, usable, completion.text)
            self._record(student, purpose, completion)
        return completion.text

    def speak(self, student: str, purpose: str, text: str, instructions: str, model: str) -> Speech:
        """the text read aloud by the speech model, recorded as used by the student for the purpose"""
        with self.traced(student, purpose):
            step = _step("speech", purpose, None, {"text": text, "instructions": instructions})
            with self.traces.step(step):
                speech = _called(step, lambda: self._platform.speak(text, instructions, model))
                # the sound is not traced
                step.output = f"{len(speech.audio)} bytes of audio"
            self._record(student, purpose, speech)
        return speech

    def transcribe(self, student: str, purpose: str, audio: bytes, content_type: str, model: str) -> Transcript:
        """what the recording says, heard by the transcription model, recorded as used by the student for the purpose"""
        with self.traced(student, purpose):
            step = _step("transcription", purpose, None, f"{len(audio)} bytes of {content_type}")
            with self.traces.step(step):
                transcript = _called(step, lambda: self._platform.transcribe(audio, content_type, model))
                step.output = transcript.text
            self._record(student, purpose, transcript)
        return transcript

    def research(
        self, student: str, purpose: str, system: str, prompt: str, history: list[Message], search_web: bool
    ) -> Researched:
        """what the AI writes, searching the web, unless told not to; recorded as used by the student for the purpose"""
        with self.traced(student, purpose):
            given = {"prompt": prompt, "history": len(history), "search_web": search_web}
            step = _step("generation", purpose, system, given)
            with self.traces.step(step):
                researched = _called(step, lambda: self._platform.research(system, prompt, history, search_web))
                step.output = {
                    "text": researched.text,
                    "searched": researched.searched,
                    "sources": [source.model_dump() for source in researched.sources],
                }
            self._record(student, purpose, researched)
        return researched

    def _record(self, student: str, purpose: str, completion: Completion | Speech | Researched | Transcript) -> None:
        row = {
            "id": uuid.uuid4().hex,
            "student": student,
            "purpose": purpose,
            "provider": completion.provider,
            "model": completion.model,
            "input_tokens": completion.input_tokens,
            "output_tokens": completion.output_tokens,
            "created_at": self.now(),
        }
        try:
            with self._engine.begin() as connection:
                connection.execute(insert(storage.ai_usage).values(**row))
        except SQLAlchemyError as e:
            # the student has their answer, and has paid for it in tokens: not counting it is the lesser evil
            logger.error(f"the AI's usage was not recorded: {row}: {e}")

    def of(self, student: str, days: int = DAYS) -> Usage:
        """the student's usage over the last ``days`` days"""
        table = storage.ai_usage
        columns, total = _spent()
        since = (table.c.student == student, table.c.created_at >= self.now() - timedelta(days=days))
        with self._engine.connect() as connection:
            all_of_it = connection.execute(select(*columns).where(*since)).one()
            purposes = connection.execute(
                select(table.c.purpose, *columns)
                .where(*since)
                .group_by(table.c.purpose)
                .order_by(total.desc(), table.c.purpose)
            ).all()
            models = connection.execute(
                select(table.c.provider, table.c.model, *columns)
                .where(*since)
                .group_by(table.c.provider, table.c.model)
                .order_by(total.desc(), table.c.provider, table.c.model)
            ).all()
        return Usage(
            days=days,
            **all_of_it._mapping,
            purposes=[SpentOn(**row._mapping) for row in purposes],
            models=[SpentWith(**row._mapping) for row in models],
        )

    def of_students(self, admin: bool, days: int = DAYS) -> list[StudentUsage]:
        """every student's usage over the last ``days`` days, most tokens first; only the app's admins see it"""
        if not admin:
            raise NotAllowed("only the app's admins can see everyone's usage")
        table = storage.ai_usage
        columns, total = _spent()
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(table.c.student, *columns)
                .where(table.c.created_at >= self.now() - timedelta(days=days))
                .group_by(table.c.student)
                .order_by(total.desc(), table.c.student)
            ).all()
        return [StudentUsage(**row._mapping) for row in rows]


def _step(kind, purpose: str, system: str | None, given: Any) -> Step:
    """a step of a call to the AI, about to be made with the system prompt and what it is given"""
    return Step(
        kind=kind,
        name=purpose,
        prompt=getattr(system, "name", None),
        prompt_version=getattr(system, "version", None),
        prompt_sha256=getattr(system, "sha256", None),
        input=given,
        started_at=now(),
    )


def _called[T: Completion | Speech | Researched | Transcript](step: Step, call: Callable[[], T]) -> T:
    """what the AI answered the call, which the step records; or the provider's failure, which it records too"""
    try:
        answered = call()
    except Exception as e:
        step.outcome = "failed at the provider"
        step.error = str(e)
        raise
    step.provider = answered.provider
    step.model = answered.model
    step.input_tokens = answered.input_tokens
    step.output_tokens = answered.output_tokens
    return answered


def _check(step: Step, usable: Callable[[str], object], text: str) -> None:
    """whether the app can use the AI's reply, which the step records"""
    try:
        if usable(text):
            return
        why = "the app can't use the reply"
    except ValueError as e:
        why = str(e)
    step.outcome = "unusable reply"
    step.error = why

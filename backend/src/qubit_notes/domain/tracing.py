"""Tracing the AI (features/tracing.feature).

A trace is of one thing a student asked for, e.g. an answer or a quiz, named by its purpose. Its steps are the calls
to the AI made for it, and the searches of the material that found what the AI was given. ``Traces`` opens and closes
traces around the app's own work and sends them to a ``Tracer``, Langfuse where the app is given its keys
(``qubit_notes.tracers``).

Traces hold the students' material, so the app keeps, for each one, the course and the materials it holds; they are
deleted with them. A deletion the tracer can't take now is kept, and tried again later: when the app starts, and with
the next deletion.

Tracing never stands in the way of the student: whatever the tracer does wrong is logged, and the student gets their
reply all the same.
"""

import threading
import uuid
from collections.abc import Callable, Iterable, Iterator
from contextlib import AbstractContextManager, contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any, Literal, Protocol

from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from qubit_notes import storage


def now() -> datetime:
    return datetime.now(UTC)


Outcome = Literal["ok", "unusable reply", "failed at the provider"]
# the score a rating of a reply is sent as, and its values (features/rating_answers.feature)
RATING = "rating"
RATING_SCORES = {"up": 1, "down": 0}


class Passage(BaseModel):
    """a passage of the material that a search found, as the AI was given it"""

    reference: str
    document_id: str
    filename: str
    section: int
    title: str
    text: str


class Step(BaseModel):
    """a call to the AI, or a search of the material, made for a trace"""

    kind: Literal["generation", "speech", "transcription", "search"]
    # the purpose it was made for, as in the AI's usage
    name: str
    # the system prompt and its version (qubit_notes.prompts)
    prompt: str | None = None
    prompt_version: str | None = None
    provider: str = ""
    model: str = ""
    input: Any = None
    output: Any = None
    input_tokens: int = 0
    output_tokens: int = 0
    started_at: datetime
    ended_at: datetime | None = None
    outcome: Outcome = "ok"
    # what went wrong, if it did
    error: str | None = None
    # what a search found
    passages: list[Passage] = Field(default_factory=list)


class TraceInfo(BaseModel):
    """what a trace is of: its id, its purpose, the student it is for and the conversation it is part of"""

    id: str
    purpose: str
    student: str
    session_id: str | None = None


class Tracer(Protocol):
    """Where traces are sent: Langfuse, or nowhere. ``trace`` and ``step`` are open while what they trace is done, so
    that their times are its own; a step is filled in before it closes."""

    def trace(self, trace: TraceInfo) -> AbstractContextManager[None]: ...

    def step(self, step: Step) -> AbstractContextManager[None]: ...

    def score(self, trace_id: str, name: str, value: float) -> None: ...

    def unscore(self, trace_id: str, name: str) -> None: ...

    def delete(self, trace_ids: list[str]) -> None:
        """deletes the traces; raises if they can't be deleted now"""
        ...

    def stop(self) -> None:
        """sends what is still to be sent"""
        ...


class _Open:
    """a trace being made: what it is, and the course and the materials it holds"""

    def __init__(self, info: TraceInfo):
        self.info = info
        self.course_id: str | None = None
        self.document_ids: set[str] = set()

    def hold(self, course_id: str | None, document_ids: Iterable[str]) -> None:
        self.course_id = self.course_id or course_id
        self.document_ids.update(d for d in document_ids if d)


# the trace being made in this context, if any
_current: ContextVar[_Open | None] = ContextVar("current_trace", default=None)
# the material drawn on before a trace was opened, e.g. gathered for a quiz before the AI is asked to write it
_held: ContextVar[_Open | None] = ContextVar("held_material", default=None)


def holds(course_id: str | None, document_ids: Iterable[str] = ()) -> None:
    """the trace being made, or the next one made here, holds the material of the course's documents"""
    trace = _current.get()
    if trace is None:
        trace = _held.get()
        if trace is None:
            trace = _Open(TraceInfo(id="", purpose="", student=""))
            _held.set(trace)
    trace.hold(course_id, document_ids)


class Trace:
    """the trace being made, as those who make it see it"""

    def __init__(self, traces: "Traces", open_trace: _Open):
        self._traces = traces
        self._open = open_trace

    @property
    def id(self) -> str:
        return self._open.info.id

    def search(self, question: str, passages: list[Passage], course_id: str | None = None) -> None:
        """the search of the material for the question, and the passages it found"""
        self._open.hold(course_id, (passage.document_id for passage in passages))
        at = now()
        step = Step(kind="search", name="search", input=question, started_at=at, ended_at=at, passages=passages)
        step.output = [passage.reference for passage in passages]
        with self._traces.step(step):
            pass


class Traces:
    """Opens traces around the app's work, sends them to the tracer, and deletes them with the material they hold."""

    def __init__(self, engine: Engine, tracer: Tracer, clock: Callable[[], datetime] = now):
        self._engine = engine
        self.tracer = tracer
        self.now = clock

    # tracing

    @contextmanager
    def trace(self, student: str, purpose: str, session_id: str | None = None) -> Iterator[Trace]:
        """the trace of what is done inside it; inside another trace, that one"""
        current = _current.get()
        if current is not None:
            yield Trace(self, current)
            return
        opened = _Open(TraceInfo(id=uuid.uuid4().hex, purpose=purpose, student=student, session_id=session_id))
        held = _held.get()
        if held is not None:
            opened.hold(held.course_id, held.document_ids)
            _held.set(None)
        token = _current.set(opened)
        try:
            with _guarded(lambda: self.tracer.trace(opened.info)):
                yield Trace(self, opened)
        finally:
            _current.reset(token)
            self._keep(opened)

    @contextmanager
    def step(self, step: Step) -> Iterator[Step]:
        """the step, traced once what it traces is done; the caller fills it in"""
        with _guarded(lambda: self.tracer.step(step)):
            try:
                yield step
            finally:
                step.ended_at = step.ended_at or self.now()

    def _keep(self, opened: _Open) -> None:
        """what the trace holds, so it can be deleted with it"""
        info = opened.info
        try:
            with self._engine.begin() as connection:
                connection.execute(
                    insert(storage.ai_traces).values(
                        id=info.id, student=info.student, course_id=opened.course_id, created_at=self.now()
                    )
                )
                if opened.document_ids:
                    connection.execute(
                        insert(storage.ai_trace_documents),
                        [{"trace_id": info.id, "document_id": d} for d in sorted(opened.document_ids)],
                    )
        except SQLAlchemyError as e:
            logger.error(f"what the trace {info.id} holds was not kept: {e}")

    # scores

    def score(self, trace_id: str | None, name: str, value: float | None) -> None:
        """the trace's score, or none if ``value`` is None"""
        if not trace_id:
            return
        try:
            # a score is replaced by deleting it first: Langfuse keeps a score sent again on another day as another
            self.tracer.unscore(trace_id, name)
            if value is not None:
                self.tracer.score(trace_id, name, value)
        except Exception as e:  # noqa: BLE001 - tracing never stands in the way of the student
            logger.error(f"the score {name} of the trace {trace_id} was not sent: {e}")

    # deleting

    def forget_material(self, document_id: str) -> None:
        documents = storage.ai_trace_documents
        self._forget(select(documents.c.trace_id).where(documents.c.document_id == document_id))

    def forget_course(self, course_id: str) -> None:
        self._forget(select(storage.ai_traces.c.id).where(storage.ai_traces.c.course_id == course_id))

    def forget_student(self, student: str) -> None:
        self._forget(select(storage.ai_traces.c.id).where(storage.ai_traces.c.student == student))

    def _forget(self, which) -> None:
        traces, documents, pending = storage.ai_traces, storage.ai_trace_documents, storage.ai_trace_deletions
        with self._engine.begin() as connection:
            ids = sorted({row[0] for row in connection.execute(which)})
            if not ids:
                return
            connection.execute(delete(documents).where(documents.c.trace_id.in_(ids)))
            connection.execute(delete(traces).where(traces.c.id.in_(ids)))
            # deleted from the tracer next, and until then kept to be tried again
            connection.execute(insert(pending), [{"trace_id": i, "created_at": self.now()} for i in ids])
        self.retry_deletions()

    def retry_deletions(self) -> None:
        """deletes from the tracer the traces it couldn't delete before"""
        pending = storage.ai_trace_deletions
        with self._engine.connect() as connection:
            ids = [row.trace_id for row in connection.execute(select(pending.c.trace_id))]
        if not ids:
            return
        try:
            self.tracer.delete(ids)
        except Exception as e:  # noqa: BLE001 - tried again later
            logger.warning(f"{len(ids)} traces could not be deleted now, and will be tried again: {e}")
            return
        with self._engine.begin() as connection:
            connection.execute(delete(pending).where(pending.c.trace_id.in_(ids)))

    def retry_deletions_in_background(self) -> None:
        threading.Thread(target=self.retry_deletions, name="trace-deletions", daemon=True).start()

    def stop(self) -> None:
        try:
            self.tracer.stop()
        except Exception as e:  # noqa: BLE001
            logger.error(f"the last traces were not sent: {e}")


@contextmanager
def _guarded(open_context: Callable[[], AbstractContextManager[Any]]) -> Iterator[None]:
    """the tracer's context, around what is traced; whatever goes wrong in the tracer is logged, never raised, and
    whatever goes wrong in what is traced is raised as it is"""
    try:
        context = open_context()
        context.__enter__()
    except Exception as e:  # noqa: BLE001 - tracing never stands in the way of the student
        logger.error(f"the AI is not traced: {e}")
        yield
        return
    try:
        yield
    except BaseException as e:
        try:
            context.__exit__(type(e), e, e.__traceback__)
        except Exception as error:  # noqa: BLE001
            logger.error(f"the AI's trace was not sent: {error}")
        raise
    else:
        try:
            context.__exit__(None, None, None)
        except Exception as e:  # noqa: BLE001
            logger.error(f"the AI's trace was not sent: {e}")

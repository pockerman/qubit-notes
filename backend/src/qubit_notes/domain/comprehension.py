"""Checking a student's understanding (features/comprehension.feature): ComprehensionAssistantAgent asks a student open
questions on a section, a document, a topic or a whole subject, one at a time, assesses each answer, typed or spoken,
and, when the student ends the check, gives its verdict: how well they understood it, and what to study again.

Each check is kept with the material it was written from, so it can be taken up again; the AI is given the material
and the whole check so far each time it asks, assesses or gives its verdict.
"""

import json
import uuid
from datetime import datetime
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import Conflict, InvalidRequest, NotFound, StudyAssistantError
from qubit_notes.domain.materials import is_video
from qubit_notes.domain.sources import OutOfDate, Scope, Source, Sources, SourceText
from qubit_notes.domain.usage import AIUsage
from qubit_notes.domain.written import (
    forget_course_rows,
    forget_document,
    material,
    now,
    of_scope,
    scope_of,
    scope_values,
)
from qubit_notes.platform.port import StudyPlatform

MAX_QUESTIONS = 20
MAX_ANSWER_CHARACTERS = 4_000
# the most text the AI is given of the material; each section gets an equal share of it
MAX_CHARACTERS = 60_000
PURPOSE = "comprehension"

Understood = Literal["yes", "partly", "no"]

SYSTEM = """You check a student's understanding of their study material, as a good tutor would in conversation. You
ask one open question at a time, from the material, that a student who understood it can answer in a few sentences in
their own words: ask why and how, to explain, compare, apply to an example or predict, rather than to recall wording.
Cover the material evenly, and follow up on what the student got wrong or left out before moving on. You assess each
answer fairly: "yes" if it shows they understood, "partly" if it is right but incomplete or imprecise, "no" if it is
wrong or they don't know; say why, briefly and kindly, correcting what was wrong from the material. Spoken answers were
transcribed, so don't mark them down for wording or punctuation. Use only the material you are given, and name the
sections you draw on by their references, e.g. S3."""


class AIFailed(StudyAssistantError):
    """The AI didn't write what was asked for."""


class WrittenQuestion(BaseModel):
    question: str
    # the reference of the section it is from, e.g. "S3"
    source: str


class WrittenAssessment(BaseModel):
    understood: Understood
    feedback: str
    # the references of the sections that say so
    cited: list[str]
    # the next question, and its section; empty where told to ask no further question
    question: str
    source: str


class WrittenVerdict(BaseModel):
    summary: str
    # what the student understood, in a few words each
    understood: list[str]
    # the references of the sections to study again
    to_study: list[str]


class Exchange(BaseModel):
    """a question of the check, and, once the student answered it, their answer and how well they understood it"""

    question: str
    source: Source
    answer: str | None = None
    # whether the student said it, rather than typed it
    spoken: bool = False
    understood: Understood | None = None
    feedback: str | None = None
    cited: list[Source] = Field(default_factory=list)


class Verdict(BaseModel):
    summary: str
    understood: list[str]
    to_study: list[Source]


class Check(BaseModel):
    id: str
    scope: Scope
    exchanges: list[Exchange]
    # the sections it is written from
    sources: list[Source]
    verdict: Verdict | None = None
    created_at: datetime
    updated_at: datetime
    ended_at: datetime | None = None
    out_of_date: OutOfDate | None = None

    @property
    def question(self) -> Exchange | None:
        """the question waiting for an answer, if one is"""
        last = self.exchanges[-1] if self.exchanges else None
        return last if last is not None and last.answer is None else None


class ComprehensionAssistantAgent:
    def __init__(self, engine: Engine, platform: StudyPlatform, courses: Courses, sources: Sources, ai: AIUsage):
        self._engine = engine
        self._platform = platform
        self._courses = courses
        self._sources = sources
        self._ai = ai

    def start(self, student: str, scope: Scope) -> Check:
        """a new check of the student's understanding of the scope, with its first question"""
        course = self._courses.get_by_id(student, scope.course_id)
        if scope.of_material:
            document = self._platform.get_document(course.id, scope.document_id)
            if document is not None and is_video(document.content_type):
                raise InvalidRequest(f"{document.filename!r} is a video, with no text to question you on")
        gathered = self._sources.gather(student, scope)
        cited = _labelled(gathered.sources)
        prompt = _prompt(gathered.sources, [], "Ask the first question.")
        written = self._written(student, prompt, WrittenQuestion, lambda q: q.question.strip() and q.source in cited)
        at = now()
        row = {
            "id": uuid.uuid4().hex,
            **scope_values(student, scope),
            "sources": [_bare(source).model_dump() for source in gathered.sources],
            "documents": {d: ref.model_dump() for d, ref in gathered.documents.items()},
            "exchanges": [Exchange(question=written.question, source=_bare(cited[written.source])).model_dump()],
            "verdict": None,
            "created_at": at,
            "updated_at": at,
            "ended_at": None,
        }
        with self._engine.begin() as connection:
            connection.execute(insert(storage.comprehension_checks).values(**row))
        return self.get(student, row["id"])

    def answer(self, student: str, check_id: str, answer: str, spoken: bool = False) -> Check:
        """the student's answer to the question waiting, assessed, with the next question, unless it was the last"""
        answer = answer.strip()
        if not answer:
            raise InvalidRequest("answer the question")
        if len(answer) > MAX_ANSWER_CHARACTERS:
            raise InvalidRequest(f"answer in at most {MAX_ANSWER_CHARACTERS} characters")
        check, texts = self._check_with_material(student, check_id)
        if check.ended_at is not None:
            raise Conflict("the check is ended: start another")
        waiting = check.question
        if waiting is None:
            raise Conflict(f"the check has asked its {MAX_QUESTIONS} questions: end it for its verdict")

        cited = _labelled(texts)
        references = {(s.document_id, s.section): label for label, s in cited.items()}
        on = references.get((waiting.source.document_id, waiting.source.section), "S1")
        last = len(check.exchanges) >= MAX_QUESTIONS
        task = [
            f"The last question is from {on}.",
            f"The student's answer{' (spoken, transcribed)' if spoken else ''}: {answer}",
            "Assess the answer, citing the sections that say so. "
            + (
                "Ask no further question: leave the question and its source empty."
                if last
                else "Then ask the next question, following up on what they got wrong or left out, if anything."
            ),
        ]
        prompt = _prompt(texts, check.exchanges[:-1], "\n".join(task), asking=waiting)

        def valid(assessed: WrittenAssessment) -> bool:
            return bool(last or (assessed.question.strip() and assessed.source in cited))

        assessed = self._written(student, prompt, WrittenAssessment, valid)
        exchanges = [*check.exchanges[:-1]]
        exchanges.append(
            waiting.model_copy(
                update={
                    "answer": answer,
                    "spoken": spoken,
                    "understood": assessed.understood,
                    "feedback": assessed.feedback,
                    "cited": [_bare(cited[c]) for c in dict.fromkeys(assessed.cited) if c in cited],
                }
            )
        )
        if not last:
            exchanges.append(Exchange(question=assessed.question, source=_bare(cited[assessed.source])))
        self._save(check.id, exchanges=[e.model_dump() for e in exchanges])
        return self.get(student, check.id)

    def end(self, student: str, check_id: str) -> Check:
        """the check ended, with its verdict"""
        check, texts = self._check_with_material(student, check_id)
        if check.ended_at is not None:
            return check
        answered = [e for e in check.exchanges if e.answer is not None]
        if not answered:
            raise InvalidRequest("answer at least one question first")
        cited = _labelled(texts)
        prompt = _prompt(
            texts,
            answered,
            "The student ends the check. Give its verdict: a summary of how well they understood the material, what "
            "they understood, and the references of the sections they should study again.",
        )
        written = self._written(student, prompt, WrittenVerdict, lambda _: True)
        verdict = Verdict(
            summary=written.summary,
            understood=written.understood,
            to_study=[_bare(cited[c]) for c in dict.fromkeys(written.to_study) if c in cited],
        )
        # a question asked and not answered isn't part of it
        self._save(
            check.id,
            exchanges=[e.model_dump() for e in answered],
            verdict=verdict.model_dump(),
            ended_at=now(),
        )
        return self.get(student, check.id)

    def get(self, student: str, check_id: str) -> Check:
        return self._check(student, self._row(student, check_id))

    def history(self, student: str, scope: Scope) -> list[Check]:
        """the student's checks of exactly the scope, newest first"""
        self._courses.get_by_id(student, scope.course_id)
        with self._engine.connect() as connection:
            rows = connection.execute(of_scope(storage.comprehension_checks, student, scope)).all()
        return [self._check(student, row) for row in rows]

    def delete(self, student: str, check_id: str) -> None:
        self._row(student, check_id)
        table = storage.comprehension_checks
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.id == check_id))

    def forget_material(self, document_id: str) -> None:
        with self._engine.begin() as connection:
            forget_document(connection, storage.comprehension_checks, document_id)

    def forget_course(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            forget_course_rows(connection, storage.comprehension_checks, course_id)

    def _written[T: BaseModel](self, student: str, prompt: str, shape: type[T], valid) -> T:
        """what the AI writes in the shape, if valid; it is asked twice before the student is told it failed"""
        for _ in range(2):
            answer = self._ai.complete(student, PURPOSE, SYSTEM, prompt, json_schema=shape.model_json_schema())
            try:
                written = shape.model_validate(json.loads(answer))
            except (ValueError, ValidationError) as e:
                logger.warning(f"the AI's {shape.__name__} is not valid: {e}")
                continue
            if valid(written):
                return written
            logger.warning(f"the AI's {shape.__name__} cites no section it was given: {written}")
        raise AIFailed("the assistant could not check your understanding just now; try again")

    def _check_with_material(self, student: str, check_id: str) -> tuple[Check, list[SourceText]]:
        """the check, and the text of the sections it was written from, as they are now"""
        check = self.get(student, check_id)
        try:
            texts = self._sources.gather(student, check.scope).sources
        except NotFound:
            texts = []
        # the sections it was started from, which its questions cite, as they are now; any added since, after them
        by_key = {(t.document_id, t.section): t for t in texts}
        kept = [by_key.pop((s.document_id, s.section)) for s in check.sources if (s.document_id, s.section) in by_key]
        texts = kept + list(by_key.values())
        if not texts:
            raise NotFound("the material of the check is gone")
        return check, texts

    def _save(self, check_id: str, **values) -> None:
        table = storage.comprehension_checks
        with self._engine.begin() as connection:
            connection.execute(update(table).where(table.c.id == check_id).values(**values, updated_at=now()))

    def _row(self, student: str, check_id: str):
        table = storage.comprehension_checks
        with self._engine.connect() as connection:
            row = connection.execute(select(table).where(table.c.id == check_id, table.c.student == student)).first()
        if row is None:
            raise NotFound(f"no check {check_id!r}")
        return row

    def _check(self, student: str, row) -> Check:
        scope = scope_of(row)
        try:
            out_of_date = self._sources.out_of_date(student, scope, row.documents)
        except NotFound:
            out_of_date = None
        return Check(
            id=row.id,
            scope=scope,
            exchanges=[Exchange(**e) for e in row.exchanges],
            sources=[Source(**s) for s in row.sources],
            verdict=Verdict(**row.verdict) if row.verdict else None,
            created_at=row.created_at,
            updated_at=row.updated_at,
            ended_at=row.ended_at,
            out_of_date=out_of_date,
        )


def _bare(source: SourceText | Source) -> Source:
    return Source(**source.model_dump(include=set(Source.model_fields)))


def _labelled(texts: list[SourceText]) -> dict[str, SourceText]:
    return {f"S{i}": text for i, text in enumerate(texts, start=1)}


def _prompt(texts: list[SourceText], exchanges: list[Exchange], task: str, asking: Exchange | None = None) -> str:
    """the material, labelled, the check so far, and what the AI is to do now"""
    references = {(t.document_id, t.section): f"S{i}" for i, t in enumerate(texts, start=1)}

    def ref(source: Source) -> str:
        return references.get((source.document_id, source.section), "S1")

    so_far = []
    for i, exchange in enumerate(exchanges, start=1):
        so_far.append(f"Question {i} (from {ref(exchange.source)}): {exchange.question}")
        if exchange.answer is not None:
            spoken = " (spoken, transcribed)" if exchange.spoken else ""
            so_far.append(f"The student answered{spoken}: {exchange.answer}")
            so_far.append(f"Understood: {exchange.understood}. {exchange.feedback}")
    if asking is not None:
        so_far.append(f"Question {len(exchanges) + 1} (from {ref(asking.source)}): {asking.question}")
    parts = [
        "The material, each section labelled by its reference:",
        material(texts, MAX_CHARACTERS),
        "The check so far:\n" + ("\n".join(so_far) if so_far else "(nothing yet)"),
        task,
    ]
    return "\n\n".join(parts)

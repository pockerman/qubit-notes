import json
import uuid
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine

from study_assistant import storage
from study_assistant.domain.errors import InvalidRequest, NotFound, StudyAssistantError
from study_assistant.domain.sources import OutOfDate, Scope, Source, Sources, SourceText
from study_assistant.domain.written import forget_document, now, of_scope, scope_of, scope_values
from study_assistant.platform.port import StudyPlatform

MIN_QUESTIONS, MAX_QUESTIONS = 1, 20
CHOICES = 4
# the most text a quiz is written from; each section gets an equal share of it
MAX_CHARACTERS = 60_000

SYSTEM = f"""You write multiple-choice quizzes that test a student's understanding of their study material.
Each question has exactly {CHOICES} choices, one of them correct, and the wrong ones plausible. Test understanding
rather than recall of wording, cover the material evenly, and use only the material you are given. Every question
names the section it comes from by its reference, e.g. S3."""


class AIFailed(StudyAssistantError):
    """The AI didn't write what was asked for."""


class WrittenQuestion(BaseModel):
    question: str
    choices: list[str]
    # the index of the correct choice
    answer: int
    # the reference of the section the question is from, e.g. "S3"
    source: str


class WrittenQuiz(BaseModel):
    questions: list[WrittenQuestion]


class Question(BaseModel):
    question: str
    choices: list[str]
    source: Source


class Quiz(BaseModel):
    """A quiz as the student sees it: without its answers, which taking it reveals."""

    id: str
    scope: Scope
    questions: list[Question]
    sources: list[Source]
    created_at: datetime
    out_of_date: OutOfDate | None = None


class QuestionResult(BaseModel):
    question: str
    chosen: int | None
    correct: bool
    correct_choice: int
    # what to study again
    source: Source


class Attempt(BaseModel):
    id: str
    quiz_id: str
    score: int
    total: int
    results: list[QuestionResult] = Field(default_factory=list)
    created_at: datetime


def _material(sources: list[SourceText]) -> str:
    share = max(500, MAX_CHARACTERS // max(1, len(sources)))
    return "\n\n".join(f"[S{i}] {s.filename} › {s.title}\n{s.content[:share]}" for i, s in enumerate(sources, start=1))


class Quizzes:
    """Multiple-choice quizzes on a section, a document or a topic, written by the AI from the material, and the
    student's attempts at them. Each student's quizzes are their own; the newest of a scope and size is shown until
    they ask for a new one."""

    def __init__(self, engine: Engine, platform: StudyPlatform, sources: Sources):
        self._engine = engine
        self._platform = platform
        self._sources = sources

    def get(self, student: str, scope: Scope, count: int, new: bool = False) -> Quiz:
        if not MIN_QUESTIONS <= count <= MAX_QUESTIONS:
            raise InvalidRequest(f"a quiz has between {MIN_QUESTIONS} and {MAX_QUESTIONS} questions")
        if not new:
            saved = [quiz for quiz in self._rows(student, scope) if quiz.count == count]
            if saved:
                return self._quiz(student, saved[0])
        return self._write(student, scope, count)

    def history(self, student: str, scope: Scope) -> list[Quiz]:
        return [self._quiz(student, row) for row in self._rows(student, scope)]

    def answers(self, student: str, quiz_id: str) -> list[int]:
        """the index of each question's correct choice"""
        return [question["answer"] for question in self._row(student, quiz_id).questions]

    def take(self, student: str, quiz_id: str, answers: list[int | None]) -> Attempt:
        """scores the answers, the index of the choice for each question, None for one not answered"""
        row = self._row(student, quiz_id)
        if len(answers) != len(row.questions):
            raise InvalidRequest(f"the quiz has {len(row.questions)} questions; got {len(answers)} answers")
        results = [
            QuestionResult(
                question=question["question"],
                chosen=chosen,
                correct=chosen == question["answer"],
                correct_choice=question["answer"],
                source=Source(**question["source"]),
            )
            for question, chosen in zip(row.questions, answers)
        ]
        attempt = {
            "id": uuid.uuid4().hex,
            "quiz_id": quiz_id,
            "student": student,
            "answers": answers,
            "score": sum(result.correct for result in results),
            "total": len(results),
            "created_at": now(),
        }
        with self._engine.begin() as connection:
            connection.execute(insert(storage.quiz_attempts).values(**attempt))
        return Attempt(**attempt, results=results)

    def attempts(self, student: str, quiz_id: str) -> list[Attempt]:
        """the student's attempts at the quiz, newest first"""
        self._row(student, quiz_id)
        attempts = storage.quiz_attempts
        query = (
            select(attempts)
            .where(attempts.c.quiz_id == quiz_id, attempts.c.student == student)
            .order_by(attempts.c.created_at.desc())
        )
        with self._engine.connect() as connection:
            return [Attempt(**row._mapping) for row in connection.execute(query)]

    def forget_material(self, document_id: str) -> None:
        with self._engine.begin() as connection:
            ids = forget_document(connection, storage.quizzes, document_id)
            if ids:
                connection.execute(delete(storage.quiz_attempts).where(storage.quiz_attempts.c.quiz_id.in_(ids)))

    def _write(self, student: str, scope: Scope, count: int) -> Quiz:
        gathered = self._sources.gather(student, scope)
        cited = {f"S{i}": source for i, source in enumerate(gathered.sources, start=1)}
        prompt = f"Write a quiz of {count} questions on this material.\n\n{_material(gathered.sources)}"

        questions = None
        for _ in range(2):
            questions = self._questions(prompt, cited, count)
            if questions:
                break
        if not questions:
            raise AIFailed("the assistant could not write the quiz; try again")

        sources = [Source(**source.model_dump(exclude={"content"})) for source in gathered.sources]
        row = {
            "id": uuid.uuid4().hex,
            **scope_values(student, scope),
            "sources": [source.model_dump() for source in sources],
            "documents": {d: ref.model_dump() for d, ref in gathered.documents.items()},
            "count": count,
            "questions": questions,
            "created_at": now(),
        }
        with self._engine.begin() as connection:
            connection.execute(insert(storage.quizzes).values(**row))
        return self._quiz(student, _Row(row))

    def _questions(self, prompt: str, cited: dict[str, SourceText], count: int) -> list[dict] | None:
        """the questions the AI writes, if there are at least ``count`` well-formed ones"""
        answer = self._platform.complete(SYSTEM, prompt, json_schema=WrittenQuiz.model_json_schema())
        try:
            written = WrittenQuiz.model_validate(json.loads(answer))
        except (ValueError, ValidationError) as e:
            logger.warning(f"the AI's quiz is not valid: {e}")
            return None
        valid = [
            {
                "question": q.question,
                "choices": q.choices,
                "answer": q.answer,
                "source": cited[q.source].model_dump(exclude={"content"}),
            }
            for q in written.questions
            if len(q.choices) == CHOICES and 0 <= q.answer < CHOICES and q.source in cited
        ]
        return valid[:count] if len(valid) >= count else None

    def _rows(self, student: str, scope: Scope) -> list:
        with self._engine.connect() as connection:
            return connection.execute(of_scope(storage.quizzes, student, scope)).all()

    def _row(self, student: str, quiz_id: str):
        quizzes = storage.quizzes
        with self._engine.connect() as connection:
            row = connection.execute(
                select(quizzes).where(quizzes.c.id == quiz_id, quizzes.c.student == student)
            ).first()
        if row is None:
            raise NotFound(f"no quiz {quiz_id!r}")
        return row

    def _quiz(self, student: str, row) -> Quiz:
        scope = scope_of(row)
        return Quiz(
            id=row.id,
            scope=scope,
            questions=[
                Question(question=q["question"], choices=q["choices"], source=Source(**q["source"]))
                for q in row.questions
            ],
            sources=[Source(**source) for source in row.sources],
            created_at=row.created_at,
            out_of_date=self._sources.out_of_date(student, scope, row.documents),
        )


class _Row:
    """a row just written, with its columns as attributes like a selected one"""

    def __init__(self, values: dict):
        self.__dict__.update(values)

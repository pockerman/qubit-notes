"""How many tokens the AI uses, on what and for whom (features/ai_usage.feature).

Every call to the AI goes through ``AIUsage.complete``, which records what it took. A call that fails at the provider
took nothing we can know of, and isn't recorded; a reply the app can't use took tokens all the same, and is.
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
from qubit_notes.domain.written import now
from qubit_notes.platform.port import Completion, Message, Speech, StudyPlatform

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
    """Calls the AI for a student, for a purpose, and tells what those calls took. ``now`` is the clock it goes by."""

    def __init__(self, engine: Engine, platform: StudyPlatform, clock: Callable[[], datetime] = now):
        self._engine = engine
        self._platform = platform
        self.now = clock

    def complete(
        self,
        student: str,
        purpose: str,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str:
        """what the AI answers, recorded as used by the student for the purpose"""
        completion = self._platform.complete(system, prompt, json_schema=json_schema, history=history)
        self._record(student, purpose, completion)
        return completion.text

    def speak(self, student: str, purpose: str, text: str, instructions: str, model: str) -> Speech:
        """the text read aloud by the speech model, recorded as used by the student for the purpose"""
        speech = self._platform.speak(text, instructions, model)
        self._record(student, purpose, speech)
        return speech

    def _record(self, student: str, purpose: str, completion: Completion | Speech) -> None:
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

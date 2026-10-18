from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

from study_assistant import storage
from study_assistant.domain.courses import SLUG, Course, Courses
from study_assistant.domain.errors import InvalidRequest
from study_assistant.platform.port import StudyPlatform


class Topic(BaseModel):
    subject: str
    topic: str
    # how many materials it has
    materials: int


class Topics:
    """A course's subjects and topics. A topic is created explicitly or by uploading to it, and stays when all of
    its material is deleted."""

    def __init__(self, engine: Engine, platform: StudyPlatform, courses: Courses):
        self._engine = engine
        self._platform = platform
        self._courses = courses

    def create(self, student: str, course_name: str, subject: str, topic: str) -> Topic:
        for name in (subject, topic):
            if not SLUG.match(name):
                raise InvalidRequest(f"invalid name {name!r}: use lowercase words joined by hyphens")
        course = self._courses.get(student, course_name)
        self._courses.require_owner(student, course)
        self.ensure(course.id, subject, topic)
        return next(t for t in self.list(student, course_name) if (t.subject, t.topic) == (subject, topic))

    def ensure(self, course_id: str, subject: str, topic: str) -> None:
        """the topic exists, e.g. when material is uploaded to it"""
        row = {"course_id": course_id, "subject": subject, "topic": topic, "created_at": datetime.now(UTC)}
        with self._engine.begin() as connection:
            if connection.dialect.name == "sqlite":
                connection.execute(sqlite_insert(storage.topics).values(**row).on_conflict_do_nothing())
            else:
                connection.execute(postgres_insert(storage.topics).values(**row).on_conflict_do_nothing())

    def list(self, student: str, course_name: str) -> list[Topic]:
        return self.of_course(self._courses.get(student, course_name))

    def forget_course(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(storage.topics).where(storage.topics.c.course_id == course_id))

    def of_course(self, course: Course) -> list[Topic]:
        counts: dict[tuple[str, str], int] = {}
        with self._engine.connect() as connection:
            for row in connection.execute(select(storage.topics).where(storage.topics.c.course_id == course.id)):
                counts[(row.subject, row.topic)] = 0
        # material uploaded before topics were kept has a topic all the same
        for document in self._platform.list_documents(course.id):
            key = (document.metadata.get("subject", ""), document.metadata.get("topic", ""))
            counts[key] = counts.get(key, 0) + 1
        return [Topic(subject=s, topic=t, materials=n) for (s, t), n in sorted(counts.items())]

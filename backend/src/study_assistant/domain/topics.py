from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

from study_assistant import storage
from study_assistant.domain.courses import SLUG, Course, Courses
from study_assistant.domain.errors import InvalidRequest, NotFound
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

    def order(self, student: str, course_name: str, subject: str, topics: list[str]) -> list[Topic]:
        """puts the subject's topics in the order they're meant to be read; returns the course's topics"""
        course = self._courses.get(student, course_name)
        self._courses.require_owner(student, course)
        of_subject = [t.topic for t in self.of_course(course) if t.subject == subject]
        if not of_subject:
            raise NotFound(f"no subject {subject!r} in {course.name!r}")
        if len(topics) != len(of_subject) or set(topics) != set(of_subject):
            raise InvalidRequest(f"the order must have each of the topics of {subject!r} once: {', '.join(of_subject)}")
        table = storage.topic_order
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.course_id == course.id, table.c.subject == subject))
            connection.execute(
                insert(table),
                [
                    {"course_id": course.id, "subject": subject, "topic": topic, "position": position}
                    for position, topic in enumerate(topics)
                ],
            )
        return self.of_course(course)

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
            for table in (storage.topics, storage.topic_order):
                connection.execute(delete(table).where(table.c.course_id == course_id))

    def of_course(self, course: Course) -> list[Topic]:
        """the course's topics: by subject, and in each subject in the order the owners set, the newest last"""
        counts: dict[tuple[str, str], int] = {}
        created: dict[tuple[str, str], datetime] = {}
        positions: dict[tuple[str, str], int] = {}
        with self._engine.connect() as connection:
            for row in connection.execute(select(storage.topics).where(storage.topics.c.course_id == course.id)):
                counts[(row.subject, row.topic)] = 0
                created[(row.subject, row.topic)] = _aware(row.created_at)
            order = storage.topic_order
            for row in connection.execute(select(order).where(order.c.course_id == course.id)):
                positions[(row.subject, row.topic)] = row.position
        # material uploaded before topics were kept has a topic all the same
        for document in self._platform.list_documents(course.id):
            key = (document.metadata.get("subject", ""), document.metadata.get("topic", ""))
            counts[key] = counts.get(key, 0) + 1

        def place(key: tuple[str, str]):
            subject, topic = key
            if key in positions:
                return (subject, 0, positions[key], _EARLIEST, topic)
            return (subject, 1, 0, created.get(key, _LATEST), topic)

        return [Topic(subject=s, topic=t, materials=counts[(s, t)]) for s, t in sorted(counts, key=place)]


_EARLIEST = datetime.min.replace(tzinfo=UTC)
_LATEST = datetime.max.replace(tzinfo=UTC)


def _aware(moment: datetime) -> datetime:
    # SQLite gives back the time without its zone, which was UTC
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)

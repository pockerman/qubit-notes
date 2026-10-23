from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.conversions import is_original
from qubit_notes.domain.courses import SLUG, Course, Courses
from qubit_notes.domain.errors import InvalidRequest, NotFound
from qubit_notes.domain.images import is_image
from qubit_notes.platform.port import StudyPlatform


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
        # what goes with a deleted topic, e.g. its material; each is called with the course, subject and topic
        self._on_delete = []

    def on_delete(self, forget) -> None:
        self._on_delete.append(forget)

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

    def delete(self, student: str, course_name: str, subject: str, topic: str) -> None:
        """deletes the topic with all of its material; the subject's other topics keep their order"""
        course = self._courses.get(student, course_name)
        self._courses.require_owner(student, course)
        if (subject, topic) not in {(t.subject, t.topic) for t in self.of_course(course)}:
            raise NotFound(f"{course.name!r} has no topic {f'{subject}/{topic}'!r}")
        for forget in self._on_delete:
            forget(course, subject, topic)
        with self._engine.begin() as connection:
            for table in (storage.topics, storage.topic_order):
                connection.execute(
                    delete(table).where(
                        table.c.course_id == course.id, table.c.subject == subject, table.c.topic == topic
                    )
                )

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
            # a material's images, and a converted one's original, are not materials of their own
            if is_image(document) or is_original(document):
                continue
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

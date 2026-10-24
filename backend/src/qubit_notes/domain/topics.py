from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
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
    # the ids of the subject and topic: lowercase words joined by hyphens, in links and references
    subject: str
    topic: str
    # how many materials it has
    materials: int
    # what they are called, as the student typed them, or named after their ids
    subject_name: str = ""
    name: str = ""


def named(slug: str) -> str:
    """the name of a subject or topic that wasn't given one: its id, with spaces for hyphens and a capital first
    letter, e.g. "Finite elements" for finite-elements"""
    words = slug.replace("-", " ")
    return words[:1].upper() + words[1:]


class Topics:
    """A course's subjects and topics. A topic is created explicitly or by uploading to it, and stays when all of
    its material is deleted. Subjects and topics are known by their ids, and shown by their names
    (features/topic_names.feature)."""

    def __init__(self, engine: Engine, platform: StudyPlatform, courses: Courses):
        self._engine = engine
        self._platform = platform
        self._courses = courses
        # what goes with a deleted topic, e.g. its material; each is called with the course, subject and topic
        self._on_delete = []

    def on_delete(self, forget) -> None:
        self._on_delete.append(forget)

    def create(
        self,
        student: str,
        course_name: str,
        subject: str,
        topic: str,
        subject_name: str | None = None,
        topic_name: str | None = None,
    ) -> Topic:
        """the topic, with the names given, if any; a subject's or topic's name, once it has one, is kept"""
        for name in (subject, topic):
            if not SLUG.match(name):
                raise InvalidRequest(f"invalid name {name!r}: use lowercase words joined by hyphens")
        course = self._courses.get(student, course_name)
        self._courses.require_owner(student, course)
        self.ensure(course.id, subject, topic)
        with self._engine.begin() as connection:
            if topic_name and topic_name.strip():
                connection.execute(
                    update(storage.topics)
                    .where(*self._is_topic(course.id, subject, topic), storage.topics.c.name.is_(None))
                    .values(name=topic_name.strip())
                )
            names = storage.subject_names
            has_name = connection.execute(
                select(names.c.name).where(names.c.course_id == course.id, names.c.subject == subject)
            ).first()
            if subject_name and subject_name.strip() and not has_name:
                connection.execute(
                    insert(names).values(course_id=course.id, subject=subject, name=subject_name.strip())
                )
        return next(t for t in self.list(student, course_name) if (t.subject, t.topic) == (subject, topic))

    def rename(self, student: str, course_name: str, subject: str, topic: str, name: str) -> Topic:
        """gives the topic another name; its id stays"""
        course = self._courses.get(student, course_name)
        self._courses.require_owner(student, course)
        name = _name(name)
        topics = [t for t in self.of_course(course) if t.subject == subject]
        if topic not in {t.topic for t in topics}:
            raise NotFound(f"{course.name!r} has no topic {f'{subject}/{topic}'!r}")
        taken = next((t.name for t in topics if t.topic != topic and t.name.casefold() == name.casefold()), None)
        if taken:
            raise InvalidRequest(f"the subject already has a topic named {taken!r}")
        # a topic of material uploaded before topics were kept has no row yet
        self.ensure(course.id, subject, topic)
        with self._engine.begin() as connection:
            connection.execute(
                update(storage.topics).where(*self._is_topic(course.id, subject, topic)).values(name=name)
            )
        return next(t for t in self.of_course(course) if (t.subject, t.topic) == (subject, topic))

    def rename_subject(self, student: str, course_name: str, subject: str, name: str) -> list[Topic]:
        """gives the subject another name; its id stays. Returns the course's topics"""
        course = self._courses.get(student, course_name)
        self._courses.require_owner(student, course)
        name = _name(name)
        if subject not in {t.subject for t in self.of_course(course)}:
            raise NotFound(f"no subject {subject!r} in {course.name!r}")
        names = storage.subject_names
        with self._engine.begin() as connection:
            connection.execute(delete(names).where(names.c.course_id == course.id, names.c.subject == subject))
            connection.execute(insert(names).values(course_id=course.id, subject=subject, name=name))
        return self.of_course(course)

    @staticmethod
    def _is_topic(course_id: str, subject: str, topic: str):
        table = storage.topics
        return table.c.course_id == course_id, table.c.subject == subject, table.c.topic == topic

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
            for table in (storage.topics, storage.topic_order, storage.subject_names):
                connection.execute(delete(table).where(table.c.course_id == course_id))

    def of_course(self, course: Course) -> list[Topic]:
        """the course's topics: by subject, and in each subject in the order the owners set, the newest last"""
        counts: dict[tuple[str, str], int] = {}
        created: dict[tuple[str, str], datetime] = {}
        positions: dict[tuple[str, str], int] = {}
        topic_names: dict[tuple[str, str], str] = {}
        with self._engine.connect() as connection:
            for row in connection.execute(select(storage.topics).where(storage.topics.c.course_id == course.id)):
                counts[(row.subject, row.topic)] = 0
                created[(row.subject, row.topic)] = _aware(row.created_at)
                if row.name:
                    topic_names[(row.subject, row.topic)] = row.name
            names = storage.subject_names
            subject_names = dict(
                connection.execute(select(names.c.subject, names.c.name).where(names.c.course_id == course.id)).all()
            )
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

        return [
            Topic(
                subject=s,
                topic=t,
                materials=counts[(s, t)],
                subject_name=subject_names.get(s) or named(s),
                name=topic_names.get((s, t)) or named(t),
            )
            for s, t in sorted(counts, key=place)
        ]


def _name(name: str) -> str:
    name = " ".join(name.split())
    if not name:
        raise InvalidRequest("a name can't be blank")
    return name


_EARLIEST = datetime.min.replace(tzinfo=UTC)
_LATEST = datetime.max.replace(tzinfo=UTC)


def _aware(moment: datetime) -> datetime:
    # SQLite gives back the time without its zone, which was UTC
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)

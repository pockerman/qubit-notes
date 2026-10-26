"""A subject's lessons made from a document: a topic of each of its headings at its top level, with the text of the
heading's part as its material (features/lessons.feature, conversion/lessons.py).

A PDF or an EPUB is converted to Markdown first, as an uploaded one is, and each lesson keeps the pictures its text
refers to. The lessons are made in the background, as a job of the app's own that the student follows; the document
isn't kept, so a job the app stopped in the middle of fails, and the student makes the lessons again.
"""

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import PurePosixPath

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.conversion import CONVERTIBLE, Converted, NotConvertible, to_markdown
from qubit_notes.conversion.lessons import lessons
from qubit_notes.domain.courses import SLUG, Course, Courses
from qubit_notes.domain.errors import InvalidRequest, NotFound, TooLarge
from qubit_notes.domain.images import Images
from qubit_notes.domain.materials import MB, Materials
from qubit_notes.domain.topics import Topics, named, slug
from qubit_notes.platform.port import IngestStatus

DOCUMENT_TYPES = {".pdf": "application/pdf", ".epub": "application/epub+zip", ".md": "text/markdown"}

table = storage.lesson_imports


class LessonImport(BaseModel):
    id: str
    course_id: str
    subject: str
    filename: str
    status: IngestStatus
    # why the lessons could not be made, e.g. a PDF without text
    error: str | None = None
    # the ids of the topics made, in the order of the document
    topics: list[str] = []


class Lessons:
    def __init__(
        self,
        database: Engine,
        courses: Courses,
        topics: Topics,
        materials: Materials,
        images: Images,
        workers: int = 1,
    ):
        self._engine = database
        self._courses = courses
        self._topics = topics
        self._materials = materials
        self._images = images
        # inline where the database is in memory, as in tests: its one connection can't be shared by threads
        in_memory = database.dialect.name == "sqlite" and database.url.database in (None, "", ":memory:")
        self._executor = None if in_memory else ThreadPoolExecutor(workers, thread_name_prefix="lessons")

    def start(self, student: str, course_name: str, subject: str, filename: str, content: bytes) -> LessonImport:
        """makes lessons in the subject from the document, in the background"""
        content_type = DOCUMENT_TYPES.get(PurePosixPath(filename).suffix.lower())
        if content_type is None:
            raise InvalidRequest(f"make lessons from a PDF, an EPUB or a Markdown file, not {filename!r}")
        if not content:
            raise InvalidRequest(f"{filename!r} is empty")
        limit = self._materials.max_upload_mb
        if len(content) > limit * MB:
            raise TooLarge(f"{filename!r} is {len(content) / MB:.1f} MB; the limit is {limit:g} MB")
        if not SLUG.match(subject):
            raise InvalidRequest(f"invalid subject {subject!r}: use lowercase words joined by hyphens")
        course = self._courses.get(student, course_name)
        self._courses.require_owner(student, course)

        now = datetime.now(UTC)
        row = {
            "id": f"lessons-{uuid.uuid4().hex}",
            "student": student,
            "course_id": course.id,
            "subject": subject,
            "filename": filename,
            "status": IngestStatus.PENDING.value,
            "topics": [],
            "created_at": now,
            "updated_at": now,
        }
        with self._engine.begin() as connection:
            connection.execute(insert(table).values(**row))
        args = (row["id"], student, course, subject, filename, content_type, content)
        if self._executor is None:
            self._make(*args)
        else:
            self._executor.submit(self._make, *args)
        return self.get(student, row["id"])

    def get(self, student: str, import_id: str) -> LessonImport:
        with self._engine.connect() as connection:
            row = connection.execute(select(table).where(table.c.id == import_id, table.c.student == student)).first()
        if row is None:
            raise NotFound(f"no lessons being made {import_id!r}")
        return LessonImport(
            id=row.id,
            course_id=row.course_id,
            subject=row.subject,
            filename=row.filename,
            status=IngestStatus(row.status),
            error=row.error,
            topics=row.topics,
        )

    def abandon(self) -> None:
        """fails the lessons the app stopped making: the document wasn't kept, so they are made again"""
        unfinished = table.c.status.in_([IngestStatus.PENDING.value, IngestStatus.RUNNING.value])
        with self._engine.begin() as connection:
            connection.execute(
                update(table)
                .where(unfinished)
                .values(
                    status=IngestStatus.FAILED.value,
                    error="the app stopped while making the lessons; make them again",
                    updated_at=datetime.now(UTC),
                )
            )

    def stop(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=True)

    def _set(self, import_id: str, **values) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                update(table).where(table.c.id == import_id).values(updated_at=datetime.now(UTC), **values)
            )

    def _make(
        self,
        import_id: str,
        student: str,
        course: Course,
        subject: str,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> None:
        try:
            self._set(import_id, status=IngestStatus.RUNNING.value)
            if content_type in CONVERTIBLE:
                converted = to_markdown(filename, content_type, content)
            else:
                converted = Converted(markdown=content.decode("utf-8", errors="replace"))
            parts = lessons(converted.markdown, untitled=named(slug(PurePosixPath(filename).stem)) or filename)
            if not parts:
                raise NotConvertible(f"{filename!r} has no text to make lessons of")

            of_subject = [t.topic for t in self._topics.of_course(course) if t.subject == subject]
            made = []
            for n, part in enumerate(parts, start=1):
                topic = _unused(slug(part.title) or f"lesson-{n}", set(of_subject) | set(made))
                self._topics.create(student, course.name, subject, topic, topic_name=part.title)
                upload = self._materials.upload(
                    student, f"{course.name}/{subject}/{topic}", f"{topic}.md", part.markdown.encode()
                )
                for path, image in converted.images.items():
                    if path in part.markdown:
                        self._images.keep(course.id, upload.document_id, path, image)
                made.append(topic)
                self._set(import_id, topics=list(made))
            # after the subject's other topics, in the order of the document
            self._topics.order(student, course.name, subject, of_subject + made)
            self._set(import_id, status=IngestStatus.COMPLETED.value)
        except NotConvertible as e:
            self._set(import_id, status=IngestStatus.FAILED.value, error=str(e))
        except Exception as e:
            logger.exception(f"making the lessons {import_id} failed")
            self._set(import_id, status=IngestStatus.FAILED.value, error=f"making the lessons failed: {e}")


def _unused(topic: str, taken: set[str]) -> str:
    """the topic's id, with a number after it if the subject has it already, e.g. 1-introduction-2"""
    candidate, n = topic, 1
    while candidate in taken:
        n += 1
        candidate = f"{topic}-{n}"
    return candidate

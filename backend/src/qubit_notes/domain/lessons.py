"""A subject's lessons made from a document: a topic of each of its headings at its top level, with the text of the
heading's part as its material (features/lessons.feature, conversion/lessons.py).

The document is kept by the platform as an original, as an uploaded PDF's is (domain/conversions.py), while its
lessons are made. A PDF's or an EPUB's lessons keep it: each lesson's material is converted from it, so it downloads
the original and is exported as it is now, and the original is deleted with the last of them. A Markdown document's
lessons are their own text, so it is deleted once they're made.

A PDF or an EPUB is converted to Markdown first, as an uploaded one is, and each lesson keeps the pictures its text
refers to. The lessons are made in the background, as a job of the app's own that the student follows; those the app
stopped making are made again, from the start, when it starts.
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
from qubit_notes.domain.conversions import CONVERTED_FROM, ORIGINAL, ORIGINAL_KIND
from qubit_notes.domain.courses import SLUG, Courses
from qubit_notes.domain.errors import InvalidRequest, NotFound, TooLarge
from qubit_notes.domain.images import KIND, Images
from qubit_notes.domain.materials import MB, Materials
from qubit_notes.domain.topics import Topics, named, slug
from qubit_notes.platform.port import IngestStatus, StudyPlatform

DOCUMENT_TYPES = {".pdf": "application/pdf", ".epub": "application/epub+zip", ".md": "text/markdown"}
# metadata of an original that lessons are made from: the job making them
LESSONS = "lessons"

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
        platform: StudyPlatform,
        courses: Courses,
        topics: Topics,
        materials: Materials,
        images: Images,
        workers: int = 1,
    ):
        self._engine = database
        self._platform = platform
        self._courses = courses
        self._topics = topics
        self._materials = materials
        self._images = images
        # inline where the database is in memory, as in tests: its one connection can't be shared by threads
        in_memory = database.dialect.name == "sqlite" and database.url.database in (None, "", ":memory:")
        self._executor = None if in_memory else ThreadPoolExecutor(workers, thread_name_prefix="lessons")

    def start(self, student: str, course_name: str, subject: str, filename: str, content: bytes) -> LessonImport:
        """keeps the document as an original, and makes lessons in the subject from it in the background"""
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

        import_id = f"lessons-{uuid.uuid4().hex}"
        original = self._platform.ingest_document(
            course.id,
            filename,
            content,
            content_type,
            metadata={KIND: ORIGINAL_KIND, LESSONS: import_id, "subject": subject},
            store_only=True,
        )
        now = datetime.now(UTC)
        with self._engine.begin() as connection:
            connection.execute(
                insert(table).values(
                    id=import_id,
                    student=student,
                    course_id=course.id,
                    subject=subject,
                    filename=filename,
                    original_id=original.document_id,
                    status=IngestStatus.PENDING.value,
                    topics=[],
                    created_at=now,
                    updated_at=now,
                )
            )
        self._submit(import_id)
        return self.get(student, import_id)

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

    def resume(self) -> None:
        """makes again the lessons the app stopped making"""
        unfinished = table.c.status.in_([IngestStatus.PENDING.value, IngestStatus.RUNNING.value])
        with self._engine.connect() as connection:
            ids = connection.execute(select(table.c.id).where(unfinished)).scalars().all()
        for import_id in ids:
            self._submit(import_id)

    def stop(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=True)

    def forget(self, course_id: str, document_id: str) -> None:
        """deletes the original of lessons once the last of their materials is deleted"""
        for original in self._platform.list_documents(course_id, {KIND: ORIGINAL_KIND}):
            import_id = original.metadata.get(LESSONS)
            if not import_id or self._status(import_id) != IngestStatus.COMPLETED.value:
                # another kind of original, or lessons still being made from it
                continue
            if not self._platform.list_documents(course_id, {ORIGINAL: original.document_id}):
                self._platform.delete_document(course_id, original.document_id)

    def _status(self, import_id: str) -> str | None:
        with self._engine.connect() as connection:
            return connection.execute(select(table.c.status).where(table.c.id == import_id)).scalar()

    def _submit(self, import_id: str) -> None:
        if self._executor is None:
            self._make(import_id)
        else:
            self._executor.submit(self._make, import_id)

    def _set(self, import_id: str, **values) -> None:
        with self._engine.begin() as connection:
            connection.execute(
                update(table).where(table.c.id == import_id).values(updated_at=datetime.now(UTC), **values)
            )

    def _make(self, import_id: str) -> None:
        with self._engine.connect() as connection:
            row = connection.execute(select(table).where(table.c.id == import_id)).first()
        if row is None:
            return
        try:
            self._set(import_id, status=IngestStatus.RUNNING.value)
            course = self._courses.get_by_id(row.student, row.course_id)
            original = self._platform.get_document(course.id, row.original_id)
            downloaded = self._platform.download_document(course.id, row.original_id) if original else None
            if downloaded is None:
                raise NotConvertible(f"{row.filename!r} was deleted before its lessons were made")
            # what was made before the app stopped is made again
            for topic in row.topics:
                self._topics.delete(row.student, course.name, row.subject, topic)
            self._set(import_id, topics=[])

            content_type = original.content_type
            if content_type in CONVERTIBLE:
                converted = to_markdown(row.filename, content_type, downloaded.content)
                # each lesson is converted from the document, which stays as their original
                metadata = {CONVERTED_FROM: content_type, ORIGINAL: row.original_id}
            else:
                converted = Converted(markdown=downloaded.content.decode("utf-8", errors="replace"))
                metadata = {}
            untitled = named(slug(PurePosixPath(row.filename).stem)) or row.filename
            parts = lessons(converted.markdown, untitled=untitled)
            if not parts:
                raise NotConvertible(f"{row.filename!r} has no text to make lessons of")

            of_subject = [t.topic for t in self._topics.of_course(course) if t.subject == row.subject]
            made = []
            for n, part in enumerate(parts, start=1):
                topic = _unused(slug(part.title) or f"lesson-{n}", set(of_subject) | set(made))
                self._topics.create(row.student, course.name, row.subject, topic, topic_name=part.title)
                made.append(topic)
                self._set(import_id, topics=list(made))
                upload = self._materials.upload(
                    row.student,
                    f"{course.name}/{row.subject}/{topic}",
                    f"{topic}.md",
                    part.markdown.encode(),
                    metadata=metadata,
                )
                for path, image in converted.images.items():
                    if path in part.markdown:
                        self._images.keep(course.id, upload.document_id, path, image)
            # after the subject's other topics, in the order of the document
            self._topics.order(row.student, course.name, row.subject, of_subject + made)
            if not metadata:
                self._platform.delete_document(course.id, row.original_id)
            self._set(import_id, status=IngestStatus.COMPLETED.value)
        except NotConvertible as e:
            self._failed(import_id, row, str(e))
        except Exception as e:
            logger.exception(f"making the lessons {import_id} failed")
            self._failed(import_id, row, f"making the lessons failed: {e}")

    def _failed(self, import_id: str, row, error: str) -> None:
        self._set(import_id, status=IngestStatus.FAILED.value, error=error)
        # an original no lesson was made from is not kept
        made = self.get(row.student, import_id).topics
        if not made:
            self._platform.delete_document(row.course_id, row.original_id)


def _unused(topic: str, taken: set[str]) -> str:
    """the topic's id, with a number after it if the subject has it already, e.g. 1-introduction-2"""
    candidate, n = topic, 1
    while candidate in taken:
        n += 1
        candidate = f"{topic}-{n}"
    return candidate

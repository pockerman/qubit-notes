from __future__ import annotations

import re
import unicodedata
from pathlib import PurePosixPath

from pydantic import BaseModel

from qubit_notes.domain.conversions import JOB_PREFIX, Conversions, converted_from, is_original
from qubit_notes.domain.courses import Course, Courses, Location
from qubit_notes.domain.errors import Conflict, InvalidRequest, NotFound, TooLarge
from qubit_notes.domain.images import is_image
from qubit_notes.domain.material_order import MaterialOrder
from qubit_notes.domain.memory import StudentMemory
from qubit_notes.domain.references import References
from qubit_notes.domain.videos import VIDEO_TYPES, duration_seconds
from qubit_notes.platform.port import IngestJob, IngestStatus, StudyPlatform

MB = 1024 * 1024
TEXT_TYPES = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    # converted to Markdown when uploaded (domain/conversions.py)
    ".pdf": "application/pdf",
    ".epub": "application/epub+zip",
}
# the material whose text can be edited: a converted PDF's or EPUB's is Markdown
EDITABLE_TYPES = {"text/plain", "text/markdown"}
CONTENT_TYPES = {**TEXT_TYPES, **VIDEO_TYPES}


def is_video(content_type: str) -> bool:
    return content_type.startswith("video/")


class Material(BaseModel):
    document_id: str
    course: str
    course_id: str
    subject: str
    topic: str
    filename: str
    status: IngestStatus
    # "text" (read by section, summarised and quizzed) or "video" (watched, with notes at moments)
    kind: str = "text"
    duration_seconds: float | None = None
    # "pdf" or "epub" for a material converted from one, whose original can be downloaded too
    converted_from: str | None = None
    # why it could not be processed, e.g. a PDF without text
    error: str | None = None


class Upload(BaseModel):
    job_id: str
    document_id: str
    course_id: str
    status: str
    # the references of a Markdown material to what its course doesn't have, as written
    broken_references: list[str] = []


class Materials:
    """Uploading, listing and deleting study material. Material is a document in its course's index, with its
    subject and topic as metadata."""

    def __init__(
        self,
        platform: StudyPlatform,
        courses: Courses,
        memory: StudentMemory,
        max_upload_mb: float,
        conversions: Conversions,
        references: References,
        order: MaterialOrder,
    ):
        self._platform = platform
        self._courses = courses
        self._conversions = conversions
        self._references = references
        self._order = order
        self._memory = memory
        self.max_upload_mb = max_upload_mb
        # what else is forgotten with a material, e.g. its notes; each is called with its document id
        self._on_delete = []
        self._on_delete_in_course = []
        # called with the course id, subject and topic of every upload, so the topic is kept
        self._on_upload = []

    def on_upload(self, keep) -> None:
        self._on_upload.append(keep)

    def on_delete(self, forget) -> None:
        self._on_delete.append(forget)

    def on_delete_in_course(self, forget) -> None:
        """``forget`` is called with the course id and the document id of every deleted material"""
        self._on_delete_in_course.append(forget)

    def upload(
        self, student: str, location: str, filename: str, content: bytes, metadata: dict[str, str] | None = None
    ) -> Upload:
        """``metadata`` is more for the material's own, e.g. the original of a lesson made from a document"""
        where = Location.parse(location)
        content_type = CONTENT_TYPES.get(PurePosixPath(filename).suffix.lower())
        if content_type is None:
            raise InvalidRequest(f"unsupported file type {filename!r}: upload {', '.join(CONTENT_TYPES)} files")
        if not content:
            raise InvalidRequest(f"{filename!r} is empty")
        if len(content) > self.max_upload_mb * MB:
            raise TooLarge(f"{filename!r} is {len(content) / MB:.1f} MB; the limit is {self.max_upload_mb:g} MB")

        course = self._courses.get_or_create(student, where.course)
        self._courses.require_owner(student, course)
        metadata = {
            **(metadata or {}),
            "subject": where.subject,
            "topic": where.topic,
            "filename": filename,
            "uploaded_by": student,
        }
        video = is_video(content_type)
        if video and (duration := duration_seconds(content)) is not None:
            metadata["duration_seconds"] = f"{duration:.3f}"
        if self._conversions.convertible(content_type):
            # a PDF or an EPUB is converted to Markdown, which is processed then
            job = self._conversions.start(course.id, filename, content, content_type, metadata)
        else:
            # a video has no text to process: the platform keeps it as it is
            job = self._platform.ingest_document(
                course.id, filename, content, content_type, metadata=metadata, store_only=video
            )
        for keep in self._on_upload:
            keep(course.id, where.subject, where.topic)
        # new material goes after the topic's other material
        self._order.append(course.id, where.subject, where.topic, job.document_id)
        return Upload(
            job_id=job.job_id,
            document_id=job.document_id,
            course_id=course.id,
            status=job.status,
            broken_references=self._broken(course, content_type, content),
        )

    def write(self, student: str, location: str, name: str, text: str) -> Upload:
        """a Markdown material the student wrote, saved under a filename made from its name"""
        where = Location.parse(location)
        filename = markdown_filename(name)
        if filename is None:
            raise InvalidRequest("the material needs a name with at least one letter or digit")
        if not text.strip():
            raise InvalidRequest("the material needs some text")
        course = self._courses.get(student, where.course)
        self._courses.require_owner(student, course)
        if any(m.filename == filename for m in self.list(student, where.course, where.subject, where.topic)):
            raise Conflict(f"the topic already has {filename!r}; edit it, or give this one another name")
        return self.upload(student, location, filename, text.encode())

    def ingestion(self, job_id: str) -> IngestJob:
        if job_id.startswith(JOB_PREFIX):
            job = self._conversions.job(job_id)
        else:
            job = self._platform.get_ingest_job(job_id)
        if job is None:
            raise NotFound(f"no upload {job_id!r}")
        return job

    def list(self, student: str, course: str, subject: str | None = None, topic: str | None = None) -> list[Material]:
        found = self._courses.get(student, course)
        metadata_filter = {key: value for key, value in (("subject", subject), ("topic", topic)) if value}
        materials = [
            Material(
                document_id=document.document_id,
                course=found.name,
                course_id=found.id,
                subject=document.metadata.get("subject", ""),
                topic=document.metadata.get("topic", ""),
                filename=document.filename,
                status=document.status,
                kind="video" if is_video(document.content_type) else "text",
                duration_seconds=duration_of(document.metadata),
                converted_from=converted_from(document),
                error=self._conversions.error(document) if document.status == IngestStatus.FAILED else None,
            )
            for document in map(
                self._conversions.as_it_is, self._platform.list_documents(found.id, metadata_filter or None)
            )
            # a Markdown material's images, and a converted material's original, are kept beside it, but are not
            # materials of their own
            if not is_image(document) and not is_original(document)
        ]
        # each topic's material in the order it's meant to be read; material without a place in it after, by name
        positions = self._order.positions(found.id)

        def place(m: Material):
            position = positions.get(m.document_id)
            return (m.subject, m.topic, position is None, position or 0, m.filename)

        return sorted(materials, key=place)

    def order(self, student: str, location: str, filenames: list[str]) -> list[Material]:
        """puts the topic's material in the order it's meant to be read; returns it in that order"""
        where = Location.parse(location)
        course = self._courses.get(student, where.course)
        self._courses.require_owner(student, course)
        current = self.list(student, where.course, where.subject, where.topic)
        if len(filenames) != len(current) or set(filenames) != {m.filename for m in current}:
            topic = f"{where.subject}/{where.topic}"
            raise InvalidRequest(
                f"the order must have each of the materials of {topic!r} once: {', '.join(m.filename for m in current)}"
            )
        by_name = {m.filename: m.document_id for m in current}
        self._order.set(course.id, where.subject, where.topic, [by_name[filename] for filename in filenames])
        return self.list(student, where.course, where.subject, where.topic)

    def text(self, student: str, course_id: str, document_id: str) -> str:
        """the text of a Markdown or text material, to edit"""
        course, document = self._editable(student, course_id, document_id)
        downloaded = self._platform.download_document(course.id, document.document_id)
        if downloaded is None:
            raise NotFound(f"no material {document_id!r}")
        return downloaded.content.decode("utf-8", errors="replace")

    def edit(self, student: str, course_id: str, document_id: str, text: str) -> Upload:
        """gives a Markdown or text material new text, which is processed again"""
        course, document = self._editable(student, course_id, document_id)
        if not text.strip():
            raise InvalidRequest("the material cannot be empty")
        content = text.encode()
        if len(content) > self.max_upload_mb * MB:
            raise TooLarge(
                f"{document.filename!r} is {len(content) / MB:.1f} MB; the limit is {self.max_upload_mb:g} MB"
            )
        job = self._platform.replace_document(
            course.id,
            document.document_id,
            document.filename,
            content,
            document.content_type,
            metadata={**document.metadata, "edited_by": student},
        )
        return Upload(
            job_id=job.job_id,
            document_id=job.document_id,
            course_id=course.id,
            status=job.status,
            broken_references=self._broken(course, document.content_type, content),
        )

    def _broken(self, course: Course, content_type: str, content: bytes) -> list[str]:
        if content_type != "text/markdown":
            return []
        return self._references.broken(course, content.decode("utf-8", errors="replace"))

    def _editable(self, student: str, course_id: str, document_id: str):
        course = self._courses.get_by_id(student, course_id)
        self._courses.require_owner(student, course)
        document = self._platform.get_document(course.id, document_id)
        if document is None:
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        if document.content_type not in EDITABLE_TYPES:
            raise InvalidRequest(f"{document.filename!r} cannot be edited: only text material can be edited")
        return course, document

    def delete(self, student: str, location: str, filename: str) -> Material:
        where = Location.parse(location)
        course = self._courses.get(student, where.course)
        self._courses.require_owner(student, course)

        material = next(
            (m for m in self.list(student, where.course, where.subject, where.topic) if m.filename == filename), None
        )
        if material is None:
            raise NotFound(f"no material {filename!r} in {where}")

        self._platform.delete_document(course.id, material.document_id)
        self._forget(course, material.document_id)
        return material

    def delete_topic(self, course: Course, subject: str, topic: str) -> None:
        """deletes the material of a deleted topic, and everything made from it"""
        for document in self._platform.list_documents(course.id, {"subject": subject, "topic": topic}):
            if is_image(document) or is_original(document):
                # they go with their material
                continue
            self._platform.delete_document(course.id, document.document_id)
            self._forget(course, document.document_id)

    def forget_course(self, course: Course) -> None:
        """what the assistant learned from a deleted course's material, for anyone who studied it"""
        document_ids = {document.document_id for document in self._platform.list_documents(course.id)}
        if document_ids:
            for member in course.members:
                self._memory.forget_sources(member, document_ids)

    def _forget(self, course: Course, document_id: str) -> None:
        for forget in self._on_delete:
            forget(document_id)
        for forget in self._on_delete_in_course:
            forget(course.id, document_id)
        # anyone who studied the course may have notes learned from the material
        for member in course.members:
            self._memory.forget_source(member, document_id)


def markdown_filename(name: str) -> str | None:
    """the filename of a written material: "Shape functions" is "shape-functions.md"; None if it has no letters or
    digits"""
    stem = name.strip()
    if stem.lower().endswith(".md"):
        stem = stem[:-3]
    stem = "".join(c for c in unicodedata.normalize("NFKD", stem) if not unicodedata.combining(c)).lower()
    stem = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return f"{stem}.md" if stem else None


def duration_of(metadata: dict[str, str]) -> float | None:
    value = metadata.get("duration_seconds")
    return float(value) if value else None

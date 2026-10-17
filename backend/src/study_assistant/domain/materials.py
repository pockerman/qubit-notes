from pathlib import PurePosixPath

from pydantic import BaseModel

from study_assistant.domain.courses import Course, Courses, Location
from study_assistant.domain.errors import InvalidRequest, NotFound, TooLarge
from study_assistant.domain.memory import StudentMemory
from study_assistant.domain.videos import VIDEO_TYPES, duration_seconds
from study_assistant.platform.port import IngestJob, IngestStatus, StudyPlatform

MB = 1024 * 1024
TEXT_TYPES = {".txt": "text/plain", ".md": "text/markdown", ".pdf": "application/pdf"}
# the material whose text can be edited
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


class Upload(BaseModel):
    job_id: str
    document_id: str
    course_id: str
    status: str


class Materials:
    """Uploading, listing and deleting study material. Material is a document in its course's index, with its
    subject and topic as metadata."""

    def __init__(self, platform: StudyPlatform, courses: Courses, memory: StudentMemory, max_upload_mb: float):
        self._platform = platform
        self._courses = courses
        self._memory = memory
        self.max_upload_mb = max_upload_mb
        # what else is forgotten with a material, e.g. its notes; each is called with its document id
        self._on_delete = []
        # called with the course id, subject and topic of every upload, so the topic is kept
        self._on_upload = []

    def on_upload(self, keep) -> None:
        self._on_upload.append(keep)

    def on_delete(self, forget) -> None:
        self._on_delete.append(forget)

    def upload(self, student: str, location: str, filename: str, content: bytes) -> Upload:
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
        metadata = {"subject": where.subject, "topic": where.topic, "filename": filename, "uploaded_by": student}
        video = is_video(content_type)
        if video and (duration := duration_seconds(content)) is not None:
            metadata["duration_seconds"] = f"{duration:.3f}"
        # a video has no text to process: gogi keeps it as it is
        job = self._platform.ingest_document(
            course.id, filename, content, content_type, metadata=metadata, store_only=video
        )
        for keep in self._on_upload:
            keep(course.id, where.subject, where.topic)
        return Upload(job_id=job.job_id, document_id=job.document_id, course_id=course.id, status=job.status)

    def ingestion(self, job_id: str) -> IngestJob:
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
            )
            for document in self._platform.list_documents(found.id, metadata_filter or None)
        ]
        return sorted(materials, key=lambda m: (m.subject, m.topic, m.filename))

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
        return Upload(job_id=job.job_id, document_id=job.document_id, course_id=course.id, status=job.status)

    def _editable(self, student: str, course_id: str, document_id: str):
        course = self._courses.get_by_id(student, course_id)
        self._courses.require_owner(student, course)
        document = self._platform.get_document(course.id, document_id)
        if document is None:
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        if document.content_type not in EDITABLE_TYPES:
            raise InvalidRequest(
                f"{document.filename!r} cannot be edited: only Markdown and text material can be edited"
            )
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

    def _forget(self, course: Course, document_id: str) -> None:
        for forget in self._on_delete:
            forget(document_id)
        # anyone who studied the course may have notes learned from the material
        for member in course.members:
            self._memory.forget_source(member, document_id)


def duration_of(metadata: dict[str, str]) -> float | None:
    value = metadata.get("duration_seconds")
    return float(value) if value else None

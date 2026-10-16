from pathlib import PurePosixPath

from pydantic import BaseModel

from study_assistant.domain.courses import Course, Courses, Location
from study_assistant.domain.errors import InvalidRequest, NotFound
from study_assistant.domain.memory import StudentMemory
from study_assistant.platform.port import IngestJob, StudyPlatform

CONTENT_TYPES = {".txt": "text/plain", ".md": "text/markdown", ".pdf": "application/pdf"}


class Material(BaseModel):
    document_id: str
    course: str
    subject: str
    topic: str
    filename: str


class Upload(BaseModel):
    job_id: str
    document_id: str
    course_id: str
    status: str


class Materials:
    """Uploading, listing and deleting study material. Material is a document in its course's index, with its
    subject and topic as metadata."""

    def __init__(self, platform: StudyPlatform, courses: Courses, memory: StudentMemory):
        self._platform = platform
        self._courses = courses
        self._memory = memory

    def upload(self, student: str, location: str, filename: str, content: bytes) -> Upload:
        where = Location.parse(location)
        content_type = CONTENT_TYPES.get(PurePosixPath(filename).suffix.lower())
        if content_type is None:
            raise InvalidRequest(f"unsupported file type {filename!r}: upload {', '.join(CONTENT_TYPES)} files")
        if not content:
            raise InvalidRequest(f"{filename!r} is empty")

        course = self._courses.get_or_create(student, where.course)
        self._courses.require_owner(student, course)
        job = self._platform.ingest_document(
            course.id,
            filename,
            content,
            content_type,
            metadata={"subject": where.subject, "topic": where.topic, "filename": filename, "uploaded_by": student},
        )
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
                subject=document.metadata.get("subject", ""),
                topic=document.metadata.get("topic", ""),
                filename=document.filename,
            )
            for document in self._platform.list_documents(found.id, metadata_filter or None)
        ]
        return sorted(materials, key=lambda m: (m.subject, m.topic, m.filename))

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
        # anyone who studied the course may have notes learned from the material
        for member in course.members:
            self._memory.forget_source(member, document_id)

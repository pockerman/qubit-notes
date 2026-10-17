from pydantic import BaseModel

from study_assistant.domain.courses import Course, Courses
from study_assistant.domain.errors import Conflict, NotFound
from study_assistant.platform.port import (
    DocumentInfo,
    DownloadedFile,
    IngestStatus,
    Section,
    SectionText,
    StudyPlatform,
)


class OpenedMaterial(BaseModel):
    course_id: str
    document_id: str
    filename: str
    subject: str
    topic: str
    sections: list[Section]


class Reading:
    """Reading material section by section, and downloading it. Every member of a course may read its material."""

    def __init__(self, platform: StudyPlatform, courses: Courses):
        self._platform = platform
        self._courses = courses

    def open(self, student: str, course_id: str, document_id: str) -> OpenedMaterial:
        course, document = self._readable(student, course_id, document_id)
        return OpenedMaterial(
            course_id=course.id,
            document_id=document.document_id,
            filename=document.filename,
            subject=document.metadata.get("subject", ""),
            topic=document.metadata.get("topic", ""),
            sections=self._platform.list_sections(course.id, document.document_id),
        )

    def read(self, student: str, course_id: str, document_id: str, position: int) -> list[SectionText]:
        """the section at the position, followed by its subsections"""
        course, document = self._readable(student, course_id, document_id)
        parts = self._platform.read_section(course.id, document.document_id, position)
        if parts is None:
            raise NotFound(f"{document.filename!r} has no section {position}")
        return parts

    def download(self, student: str, course_id: str, document_id: str) -> DownloadedFile:
        course, document = self._material(student, course_id, document_id)
        downloaded = self._platform.download_document(course.id, document.document_id)
        if downloaded is None:
            raise NotFound(f"no material {document_id!r}")
        return downloaded

    def _material(self, student: str, course_id: str, document_id: str) -> tuple[Course, DocumentInfo]:
        course = self._courses.get_by_id(student, course_id)
        document = self._platform.get_document(course.id, document_id)
        if document is None:
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        return course, document

    def _readable(self, student: str, course_id: str, document_id: str) -> tuple[Course, DocumentInfo]:
        course, document = self._material(student, course_id, document_id)
        if document.status == IngestStatus.FAILED:
            raise Conflict(f"{document.filename!r} could not be processed, so it cannot be read")
        if document.status != IngestStatus.COMPLETED:
            raise Conflict(f"{document.filename!r} is still being processed; try again in a moment")
        return course, document

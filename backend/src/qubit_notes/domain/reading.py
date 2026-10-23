from pydantic import BaseModel

from qubit_notes.domain.conversions import Conversions, converted_from, is_original
from qubit_notes.domain.courses import Course, Courses
from qubit_notes.domain.errors import Conflict, NotFound, OutOfRange
from qubit_notes.domain.materials import duration_of, is_video
from qubit_notes.platform.port import (
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
    # "text", read by section, or "video", which has no sections
    kind: str
    content_type: str
    duration_seconds: float | None = None
    # "pdf" or "epub" for a material converted from one, whose original can be downloaded too
    converted_from: str | None = None
    sections: list[Section]


class Reading:
    """Reading material section by section, and downloading it. Every member of a course may read its material."""

    def __init__(self, platform: StudyPlatform, courses: Courses, conversions: Conversions):
        self._platform = platform
        self._courses = courses
        self._conversions = conversions

    def open(self, student: str, course_id: str, document_id: str) -> OpenedMaterial:
        course, document = self._readable(student, course_id, document_id)
        return OpenedMaterial(
            course_id=course.id,
            document_id=document.document_id,
            filename=document.filename,
            subject=document.metadata.get("subject", ""),
            topic=document.metadata.get("topic", ""),
            kind="video" if is_video(document.content_type) else "text",
            content_type=document.content_type,
            duration_seconds=duration_of(document.metadata),
            converted_from=converted_from(document),
            sections=[] if is_video(document.content_type) else self._platform.list_sections(course.id, document_id),
        )

    def read(self, student: str, course_id: str, document_id: str, position: int) -> list[SectionText]:
        """the section at the position, followed by its subsections"""
        course, document = self._readable(student, course_id, document_id)
        parts = self._platform.read_section(course.id, document.document_id, position)
        if parts is None:
            raise NotFound(f"{document.filename!r} has no section {position}")
        return parts

    def download(
        self, student: str, course_id: str, document_id: str, offset: int = 0, length: int = 0
    ) -> DownloadedFile:
        """the uploaded file, or length bytes of it from offset (to its end if length is 0): a converted material's
        original"""
        course, document = self._material(student, course_id, document_id)
        document = self._conversions.original(course.id, document)
        if offset and offset >= document.size_bytes:
            raise OutOfRange(f"{document.filename!r} is {document.size_bytes} bytes")
        downloaded = self._platform.download_document(course.id, document.document_id, offset, length)
        if downloaded is None:
            raise NotFound(f"no material {document_id!r}")
        return downloaded

    def contents(self, student: str, course_id: str, document_id: str) -> list[SectionText]:
        """every section of the document with its own text, reading each top section with its subsections"""
        course, document = self._readable(student, course_id, document_id)
        parts, read = [], set()
        for section in self._platform.list_sections(course.id, document.document_id):
            if section.position in read:
                continue
            for part in self._platform.read_section(course.id, document.document_id, section.position) or []:
                read.add(part.section.position)
                parts.append(part)
        return parts

    def section_content(self, student: str, course_id: str, document_id: str, position: int) -> str:
        """the section's own text, without its subsections'"""
        return self.read(student, course_id, document_id, position)[0].content

    def _material(self, student: str, course_id: str, document_id: str) -> tuple[Course, DocumentInfo]:
        course = self._courses.get_by_id(student, course_id)
        document = self._platform.get_document(course.id, document_id)
        if document is None or is_original(document):
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        return course, self._conversions.as_it_is(document)

    def _readable(self, student: str, course_id: str, document_id: str) -> tuple[Course, DocumentInfo]:
        course, document = self._material(student, course_id, document_id)
        if document.status == IngestStatus.FAILED:
            why = self._conversions.error(document)
            because = f": {why}" if why else ""
            raise Conflict(f"{document.filename!r} could not be processed, so it cannot be read{because}")
        if document.status != IngestStatus.COMPLETED:
            raise Conflict(f"{document.filename!r} is still being processed; try again in a moment")
        return course, document

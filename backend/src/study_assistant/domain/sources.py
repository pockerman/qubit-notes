"""What a summary or a quiz is about, and the material it is written from."""

from pydantic import BaseModel, model_validator

from study_assistant.domain.courses import Courses
from study_assistant.domain.errors import InvalidRequest, NotFound
from study_assistant.domain.materials import is_video
from study_assistant.domain.reading import Reading
from study_assistant.platform.port import IngestStatus, StudyPlatform


class Scope(BaseModel):
    """A section of a document (with its subsections), a whole document, or a topic: every text of the topic."""

    course_id: str
    document_id: str | None = None
    section: int | None = None
    subject: str | None = None
    topic: str | None = None

    @model_validator(mode="after")
    def _one_kind(self) -> "Scope":
        if self.document_id is None and not (self.subject and self.topic):
            raise ValueError("a scope is a document, a section of one, or a subject and topic")
        if self.document_id is not None and (self.subject or self.topic):
            raise ValueError("a scope is either a document or a topic")
        if self.section is not None and self.document_id is None:
            raise ValueError("a section is of a document")
        return self

    @property
    def kind(self) -> str:
        if self.section is not None:
            return "section"
        return "document" if self.document_id else "topic"


class Source(BaseModel):
    """A section of a material, as cited by a summary or a quiz"""

    document_id: str
    filename: str
    section: int
    title: str


class SourceText(Source):
    content: str


class DocumentRef(BaseModel):
    filename: str
    # changes when the material is edited
    version: str = ""


class Gathered(BaseModel):
    sources: list[SourceText]
    # every material drawn on, by document id: it can be edited after, and a topic's can be added to or removed
    documents: dict[str, DocumentRef]


class OutOfDate(BaseModel):
    """how the material changed since a summary or quiz was written from it"""

    added: list[str] = []
    removed: list[str] = []
    edited: list[str] = []


class Sources:
    """Gathers the text a summary or a quiz is written from. Videos have no text, so a topic's are left out."""

    def __init__(self, platform: StudyPlatform, courses: Courses, reading: Reading):
        self._platform = platform
        self._courses = courses
        self._reading = reading

    def gather(self, student: str, scope: Scope) -> Gathered:
        course = self._courses.get_by_id(student, scope.course_id)
        if scope.kind == "topic":
            documents = self._topic_documents(course.id, scope)
            if not documents:
                raise NotFound(f"there is no material to work from in {scope.subject}/{scope.topic}")
        else:
            opened = self._reading.open(student, scope.course_id, scope.document_id)
            if opened.kind == "video":
                raise InvalidRequest(f"{opened.filename!r} is a video: only texts are summarised and quizzed")
            documents = self._current(course.id, scope)

        sources = []
        for document_id, ref in documents.items():
            filename = ref.filename
            if scope.kind == "section":
                parts = self._reading.read(student, scope.course_id, document_id, scope.section)
                sources += [_source(document_id, filename, part) for part in parts]
            else:
                sources += self._whole(student, scope.course_id, document_id, filename)
        return Gathered(sources=sources, documents=documents)

    def out_of_date(self, student: str, scope: Scope, documents: dict) -> OutOfDate | None:
        """how the material changed since it was ``documents``: edited, or, for a topic, added or removed;
        None if it hasn't"""
        written = {d: ref if isinstance(ref, dict) else {"filename": ref} for d, ref in documents.items()}
        course = self._courses.get_by_id(student, scope.course_id)
        current = self._current(course.id, scope, completed_only=False)
        added = sorted(current[d].filename for d in current.keys() - written.keys()) if scope.kind == "topic" else []
        removed = (
            sorted(written[d]["filename"] for d in written.keys() - current.keys()) if scope.kind == "topic" else []
        )
        edited = sorted(
            current[d].filename
            for d in current.keys() & written.keys()
            if written[d].get("version") and current[d].version != written[d]["version"]
        )
        return OutOfDate(added=added, removed=removed, edited=edited) if added or removed or edited else None

    def _current(self, course_id: str, scope: Scope, completed_only: bool = True) -> dict[str, DocumentRef]:
        if scope.kind == "topic":
            return self._topic_documents(course_id, scope, completed_only)
        document = self._platform.get_document(course_id, scope.document_id)
        return (
            {document.document_id: DocumentRef(filename=document.filename, version=document.version)}
            if document
            else {}
        )

    def _topic_documents(self, course_id: str, scope: Scope, completed_only: bool = True) -> dict[str, DocumentRef]:
        found = self._platform.list_documents(course_id, {"subject": scope.subject, "topic": scope.topic})
        texts = [
            d
            for d in found
            if not is_video(d.content_type) and (d.status == IngestStatus.COMPLETED or not completed_only)
        ]
        return {
            d.document_id: DocumentRef(filename=d.filename, version=d.version)
            for d in sorted(texts, key=lambda d: d.filename)
        }

    def _whole(self, student: str, course_id: str, document_id: str, filename: str) -> list[SourceText]:
        """every section of the document, reading each top section with its subsections"""
        sections = self._platform.list_sections(course_id, document_id)
        sources, read = [], set()
        for section in sections:
            if section.position in read:
                continue
            for part in self._reading.read(student, course_id, document_id, section.position):
                read.add(part.section.position)
                sources.append(_source(document_id, filename, part))
        return sources


def _source(document_id: str, filename: str, part) -> SourceText:
    return SourceText(
        document_id=document_id,
        filename=filename,
        section=part.section.position,
        title=part.section.title or filename,
        content=part.content,
    )

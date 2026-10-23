"""References between the topics of a course (features/references.feature): what a Markdown material's references
refer to, and the materials each topic is mentioned in. Both are worked out from the material as it is now, so a
reference breaks as soon as what it refers to is deleted, and a mention goes as soon as its reference does."""

from typing import Literal

from pydantic import BaseModel

from qubit_notes.domain.conversions import is_original
from qubit_notes.domain.courses import Course, Courses
from qubit_notes.domain.errors import NotFound
from qubit_notes.domain.images import is_image
from qubit_notes.domain.reference_text import Written, written_in
from qubit_notes.domain.topics import Topics
from qubit_notes.platform.port import DocumentInfo, Section, StudyPlatform

MARKDOWN = "text/markdown"


class Reference(BaseModel):
    # as written, e.g. "[[numerical-methods/finite-elements|the FEM topic]]"
    written: str
    shown_as: str
    # what it refers to; "nothing" if the course doesn't have it
    refers_to: Literal["topic", "material", "section", "nothing"]
    subject: str | None = None
    topic: str | None = None
    material: str | None = None
    document_id: str | None = None
    section: str | None = None
    # the section's position in its material, to open it there
    position: int | None = None


class Mention(BaseModel):
    """a material that refers to a topic"""

    subject: str
    topic: str
    material: str
    document_id: str


class TopicMentions(BaseModel):
    subject: str
    topic: str
    mentioned_in: list[Mention]


class _Course:
    """what a course has to refer to, looked up once for all the references being resolved"""

    def __init__(self, platform: StudyPlatform, topics: Topics, course: Course):
        self._platform = platform
        self.course = course
        self.topics = [(t.subject, t.topic) for t in topics.of_course(course)]
        self.materials = [d for d in platform.list_documents(course.id) if not is_image(d) and not is_original(d)]
        self._by_name = {
            (d.metadata.get("subject", ""), d.metadata.get("topic", ""), d.filename): d for d in self.materials
        }
        self._sections: dict[str, list[Section]] = {}

    def material(self, subject: str, topic: str, filename: str) -> DocumentInfo | None:
        return self._by_name.get((subject, topic, filename))

    def section(self, document: DocumentInfo, title: str) -> Section | None:
        if document.document_id not in self._sections:
            self._sections[document.document_id] = self._platform.list_sections(self.course.id, document.document_id)
        return next((s for s in self._sections[document.document_id] if s.title.strip() == title), None)

    def resolve(self, written: Written) -> Reference:
        nothing = Reference(written=written.text, shown_as=written.shown_as, refers_to="nothing")
        if not written.well_formed:
            return nothing
        subject, topic, *filename = written.parts
        if (subject, topic) not in self.topics:
            return nothing
        if not filename:
            return nothing.model_copy(update={"refers_to": "topic", "subject": subject, "topic": topic})
        document = self.material(subject, topic, filename[0])
        if document is None:
            return nothing
        material = nothing.model_copy(
            update={
                "refers_to": "material",
                "subject": subject,
                "topic": topic,
                "material": document.filename,
                "document_id": document.document_id,
            }
        )
        if written.section is None:
            return material
        section = self.section(document, written.section)
        if section is None:
            return nothing
        return material.model_copy(
            update={"refers_to": "section", "section": section.title.strip(), "position": section.position}
        )


class References:
    def __init__(self, platform: StudyPlatform, courses: Courses, topics: Topics):
        self._platform = platform
        self._courses = courses
        self._topics = topics

    def of(self, student: str, course_id: str, document_id: str) -> list[Reference]:
        """the references of a material, and what each refers to"""
        course = self._courses.get_by_id(student, course_id)
        document = self._platform.get_document(course.id, document_id)
        if document is None or is_image(document) or is_original(document):
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        return self._resolve(_Course(self._platform, self._topics, course), self._text(course, document))

    def in_text(self, student: str, course_id: str, text: str) -> list[Reference]:
        """the references of text not saved yet, e.g. one being written"""
        course = self._courses.get_by_id(student, course_id)
        return self._resolve(_Course(self._platform, self._topics, course), text)

    def broken(self, course: Course, text: str) -> list[str]:
        """the references of the text to what the course doesn't have, as written, once each"""
        found = self._resolve(_Course(self._platform, self._topics, course), text)
        return list(dict.fromkeys(r.written for r in found if r.refers_to == "nothing"))

    def mentions(self, student: str, course_name: str) -> list[TopicMentions]:
        """each topic of the course, in order, with the materials it is mentioned in"""
        course = self._courses.get(student, course_name)
        known = _Course(self._platform, self._topics, course)
        mentioned: dict[tuple[str, str], dict[str, Mention]] = {key: {} for key in known.topics}
        for document in known.materials:
            if document.content_type != MARKDOWN:
                continue
            mention = Mention(
                subject=document.metadata.get("subject", ""),
                topic=document.metadata.get("topic", ""),
                material=document.filename,
                document_id=document.document_id,
            )
            for reference in self._resolve(known, self._text(course, document)):
                if reference.refers_to != "nothing":
                    mentioned[(reference.subject, reference.topic)][document.document_id] = mention
        return [
            TopicMentions(
                subject=subject,
                topic=topic,
                mentioned_in=sorted(by.values(), key=lambda m: (m.subject, m.topic, m.material)),
            )
            for (subject, topic), by in mentioned.items()
        ]

    @staticmethod
    def _resolve(known: _Course, text: str) -> list[Reference]:
        return [known.resolve(written) for written in written_in(text)]

    def _text(self, course: Course, document: DocumentInfo) -> str:
        if document.content_type != MARKDOWN:
            return ""
        downloaded = self._platform.download_document(course.id, document.document_id)
        return downloaded.content.decode("utf-8", errors="replace") if downloaded else ""

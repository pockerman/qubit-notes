"""Going on from a material to the next one, or back to the previous one (features/reading_order.feature): through a
subject's topics in their order, and each topic's material in its order, passing over material not ready to read."""

from pydantic import BaseModel

from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import NotFound
from qubit_notes.domain.materials import Material, Materials
from qubit_notes.domain.topics import Topics
from qubit_notes.platform.port import IngestStatus


class Neighbours(BaseModel):
    previous: Material | None = None
    next: Material | None = None


class ReadingOrder:
    def __init__(self, courses: Courses, topics: Topics, materials: Materials):
        self._courses = courses
        self._topics = topics
        self._materials = materials

    def neighbours(self, student: str, course_id: str, document_id: str) -> Neighbours:
        """the materials before and after this one in its subject"""
        course = self._courses.get_by_id(student, course_id)
        materials = self._materials.list(student, course.name)
        material = next((m for m in materials if m.document_id == document_id), None)
        if material is None:
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        topics = [t.topic for t in self._topics.of_course(course) if t.subject == material.subject]
        in_order = [
            m
            for topic in topics
            for m in materials
            if m.subject == material.subject and m.topic == topic and m.status == IngestStatus.COMPLETED
        ]
        at = next((i for i, m in enumerate(in_order) if m.document_id == document_id), None)
        if at is None:
            return Neighbours()
        return Neighbours(
            previous=in_order[at - 1] if at > 0 else None,
            next=in_order[at + 1] if at + 1 < len(in_order) else None,
        )

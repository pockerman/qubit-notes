"""Going on from a material to the next topic of its subject, or back to the previous one
(features/reading_order.feature): through the subject's topics in their order, each opening at its first material
ready to read, passing over topics with none."""

from pydantic import BaseModel

from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import NotFound
from qubit_notes.domain.materials import Material, Materials
from qubit_notes.domain.topics import Topics
from qubit_notes.platform.port import IngestStatus


class TopicToRead(BaseModel):
    subject: str
    topic: str
    # what it is called
    name: str
    # its first material ready to read, where it opens
    material: Material


class Neighbours(BaseModel):
    previous: TopicToRead | None = None
    next: TopicToRead | None = None


class ReadingOrder:
    def __init__(self, courses: Courses, topics: Topics, materials: Materials):
        self._courses = courses
        self._topics = topics
        self._materials = materials

    def neighbours(self, student: str, course_id: str, document_id: str) -> Neighbours:
        """the topics before and after this material's in its subject"""
        course = self._courses.get_by_id(student, course_id)
        materials = self._materials.list(student, course.name)
        material = next((m for m in materials if m.document_id == document_id), None)
        if material is None:
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        topics = [t for t in self._topics.of_course(course) if t.subject == material.subject]
        at = next((i for i, t in enumerate(topics) if t.topic == material.topic), None)
        if at is None:
            return Neighbours()

        def to_read(index: int) -> TopicToRead | None:
            topic = topics[index]
            # the material is listed in its order
            first = next(
                (
                    m
                    for m in materials
                    if (m.subject, m.topic) == (topic.subject, topic.topic) and m.status == IngestStatus.COMPLETED
                ),
                None,
            )
            if first is None:
                return None
            return TopicToRead(subject=topic.subject, topic=topic.topic, name=topic.name, material=first)

        before = (to_read(i) for i in range(at - 1, -1, -1))
        after = (to_read(i) for i in range(at + 1, len(topics)))
        return Neighbours(
            previous=next((t for t in before if t), None),
            next=next((t for t in after if t), None),
        )

"""The sections of a material each student has opened (features/reading_progress.feature).

Every time a section is shown is kept, so that when and how often can be told later as well as whether. Opening a
section isn't reading it, so it's called what it is. A section is shown with its subsections, so they count as opened.
"""

import uuid
from collections.abc import Callable
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.reading import Reading
from qubit_notes.domain.written import now


class Progress(BaseModel):
    """how many sections a material has, and the positions of those opened, in order"""

    sections: int
    opened: list[int]


class ReadingProgress:
    def __init__(self, engine: Engine, reading: Reading, clock: Callable[[], datetime] = now):
        self._engine = engine
        self._reading = reading
        self.now = clock

    def opened(self, student: str, course_id: str, document_id: str, position: int) -> Progress:
        """the student was shown the section at the position, and its subsections with it"""
        shown = self._reading.read(student, course_id, document_id, position)
        at = self.now()
        rows = [
            {
                "id": uuid.uuid4().hex,
                "student": student,
                "course_id": course_id,
                "document_id": document_id,
                "section": part.section.position,
                "opened_at": at,
            }
            for part in shown
        ]
        with self._engine.begin() as connection:
            connection.execute(insert(storage.section_opens), rows)
        return self.progress(student, course_id, document_id)

    def progress(self, student: str, course_id: str, document_id: str) -> Progress:
        """what the student has opened of the material; sections it no longer has aren't counted"""
        sections = {section.position for section in self._reading.open(student, course_id, document_id).sections}
        table = storage.section_opens
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(table.c.section).where(table.c.student == student, table.c.document_id == document_id).distinct()
            ).all()
        return Progress(sections=len(sections), opened=sorted(sections & {row.section for row in rows}))

    def forget_material(self, document_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(storage.section_opens).where(storage.section_opens.c.document_id == document_id))

    def forget_course(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(storage.section_opens).where(storage.section_opens.c.course_id == course_id))

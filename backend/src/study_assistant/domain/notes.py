import uuid
from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from study_assistant import storage
from study_assistant.domain.errors import InvalidRequest, NotFound
from study_assistant.domain.reading import Reading


class Note(BaseModel):
    id: str
    course_id: str
    document_id: str
    # a note on a text: the section and the passage of it the note is on
    section: int | None = None
    section_title: str | None = None
    passage: str | None = None
    # a note on a video: the moment it's at
    at_seconds: float | None = None
    text: str
    created_at: datetime
    updated_at: datetime


def format_moment(seconds: float) -> str:
    """e.g. 750 as "12:30", 3725 as "1:02:05\""""
    total = int(seconds)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


class Notes:
    """A student's notes on material: on a passage of a text, or at a moment of a video. Notes are private: only
    the student who took one sees it. Any member of a course may take notes on its material."""

    def __init__(self, engine: Engine, reading: Reading):
        self._engine = engine
        self._reading = reading

    def add(
        self,
        student: str,
        course_id: str,
        document_id: str,
        text: str,
        *,
        section: int | None = None,
        passage: str | None = None,
        at_seconds: float | None = None,
    ) -> Note:
        text = text.strip()
        if not text:
            raise InvalidRequest("a note needs some text")
        opened = self._reading.open(student, course_id, document_id)
        values = {}
        if opened.kind == "video":
            if at_seconds is None or at_seconds < 0:
                raise InvalidRequest("a note on a video needs the moment it's at")
            if opened.duration_seconds is not None and at_seconds > opened.duration_seconds:
                raise InvalidRequest(f"the video is only {format_moment(opened.duration_seconds)} long")
            values = {"at_seconds": at_seconds}
        else:
            if section is None or not passage:
                raise InvalidRequest("a note on a text needs the section and the passage it's on")
            titles = {s.position: s.title for s in opened.sections}
            if section not in titles:
                raise NotFound(f"{opened.filename!r} has no section {section}")
            start = self._reading.section_content(student, course_id, document_id, section).find(passage)
            if start < 0:
                raise InvalidRequest(f"the passage {passage!r} is not in that section")
            values = {"section": section, "section_title": titles[section], "passage": passage, "passage_start": start}

        now = datetime.now(UTC)
        note = {
            "id": uuid.uuid4().hex,
            "student": student,
            "course_id": course_id,
            "document_id": document_id,
            "text": text,
            "created_at": now,
            "updated_at": now,
            **values,
        }
        with self._engine.begin() as connection:
            connection.execute(insert(storage.notes).values(**note))
        return Note(**note)

    def of_material(self, student: str, course_id: str, document_id: str) -> list[Note]:
        """the student's notes on the material, in the order of the material"""
        self._reading.open(student, course_id, document_id)
        notes = storage.notes
        query = (
            select(notes)
            .where(notes.c.student == student, notes.c.document_id == document_id)
            .order_by(notes.c.section, notes.c.passage_start, notes.c.at_seconds, notes.c.created_at)
        )
        return self._select(query)

    def all(self, student: str) -> list[Note]:
        notes = storage.notes
        return self._select(select(notes).where(notes.c.student == student).order_by(notes.c.created_at))

    def change(self, student: str, note_id: str, text: str) -> Note:
        text = text.strip()
        if not text:
            raise InvalidRequest("a note needs some text")
        notes = storage.notes
        with self._engine.begin() as connection:
            changed = connection.execute(
                update(notes)
                .where(notes.c.id == note_id, notes.c.student == student)
                .values(text=text, updated_at=datetime.now(UTC))
            ).rowcount
        if not changed:
            raise NotFound(f"no note {note_id!r}")
        return self._select(select(notes).where(notes.c.id == note_id))[0]

    def delete(self, student: str, note_id: str) -> None:
        notes = storage.notes
        with self._engine.begin() as connection:
            deleted = connection.execute(delete(notes).where(notes.c.id == note_id, notes.c.student == student))
        if not deleted.rowcount:
            raise NotFound(f"no note {note_id!r}")

    def forget_material(self, document_id: str) -> None:
        """every student's notes on a deleted material"""
        with self._engine.begin() as connection:
            connection.execute(delete(storage.notes).where(storage.notes.c.document_id == document_id))

    def _select(self, query) -> list[Note]:
        with self._engine.connect() as connection:
            return [Note(**row._mapping) for row in connection.execute(query)]

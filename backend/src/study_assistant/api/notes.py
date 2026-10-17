from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from study_assistant.api.deps import Student, notes
from study_assistant.domain.notes import Note, Notes

router = APIRouter(tags=["notes"])
NotesDep = Annotated[Notes, Depends(notes)]


class NewNote(BaseModel):
    text: str
    # on a text: the section and the passage of it
    section: int | None = None
    passage: str | None = None
    # on a video: the moment
    at_seconds: float | None = None


class ChangedNote(BaseModel):
    text: str


@router.get("/courses/{course_id}/materials/{document_id}/notes", response_model=list[Note])
async def notes_of_material(course_id: str, document_id: str, student: Student, service: NotesDep) -> list[Note]:
    return await run_in_threadpool(service.of_material, student, course_id, document_id)


@router.post("/courses/{course_id}/materials/{document_id}/notes", response_model=Note, status_code=201)
async def add_note(course_id: str, document_id: str, note: NewNote, student: Student, service: NotesDep) -> Note:
    return await run_in_threadpool(
        lambda: service.add(
            student,
            course_id,
            document_id,
            note.text,
            section=note.section,
            passage=note.passage,
            at_seconds=note.at_seconds,
        )
    )


@router.get("/notes", response_model=list[Note])
async def my_notes(student: Student, service: NotesDep) -> list[Note]:
    return await run_in_threadpool(service.all, student)


@router.patch("/notes/{note_id}", response_model=Note)
async def change_note(note_id: str, note: ChangedNote, student: Student, service: NotesDep) -> Note:
    return await run_in_threadpool(service.change, student, note_id, note.text)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: str, student: Student, service: NotesDep) -> Response:
    await run_in_threadpool(service.delete, student, note_id)
    return Response(status_code=204)

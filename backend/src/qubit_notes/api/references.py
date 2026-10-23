from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, references
from qubit_notes.domain.references import Reference, References, TopicMentions

router = APIRouter(tags=["references"])
ReferencesDep = Annotated[References, Depends(references)]


class Text(BaseModel):
    text: str


@router.get("/courses/{course_id}/materials/{document_id}/references", response_model=list[Reference])
async def material_references(
    course_id: str, document_id: str, student: Student, service: ReferencesDep
) -> list[Reference]:
    """the references of a Markdown material, and what each refers to"""
    return await run_in_threadpool(service.of, student, course_id, document_id)


@router.post("/courses/{course_id}/references", response_model=list[Reference])
async def text_references(course_id: str, body: Text, student: Student, service: ReferencesDep) -> list[Reference]:
    """the references of text not saved yet, e.g. one being written, and what each refers to"""
    return await run_in_threadpool(service.in_text, student, course_id, body.text)


@router.get("/courses/{course}/mentions", response_model=list[TopicMentions])
async def mentions(course: str, student: Student, service: ReferencesDep) -> list[TopicMentions]:
    """each topic of the course with the materials it is mentioned in"""
    return await run_in_threadpool(service.mentions, student, course)

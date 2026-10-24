from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, generator
from qubit_notes.domain.generating import Generated, Generator, Kind

router = APIRouter(tags=["generating"])
GeneratorDep = Annotated[Generator, Depends(generator)]


class GenerateRequest(BaseModel):
    # the materials to generate from, by document id
    documents: list[str]
    kind: Kind | None = None
    instructions: str = ""


@router.post("/courses/{course_id}/generated", response_model=Generated)
async def generate(course_id: str, body: GenerateRequest, student: Student, service: GeneratorDep) -> Generated:
    """new material the AI writes from the materials; it is not saved until the student saves it"""
    return await run_in_threadpool(service.generate, student, course_id, body.documents, body.kind, body.instructions)

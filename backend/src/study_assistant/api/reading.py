from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, Response
from fastapi.concurrency import run_in_threadpool

from study_assistant.api.deps import Student, reading
from study_assistant.domain.reading import OpenedMaterial, Reading
from study_assistant.platform.port import SectionText

# a course is addressed by its id here, e.g. "maria--aeronautics": a student who isn't one of its
# members is refused, rather than told there's no such course
router = APIRouter(prefix="/courses/{course_id}/materials/{document_id}", tags=["reading"])
ReadingDep = Annotated[Reading, Depends(reading)]


@router.get("", response_model=OpenedMaterial)
async def open_material(course_id: str, document_id: str, student: Student, service: ReadingDep) -> OpenedMaterial:
    return await run_in_threadpool(service.open, student, course_id, document_id)


@router.get("/sections/{position}", response_model=list[SectionText])
async def read_section(
    course_id: str, document_id: str, position: int, student: Student, service: ReadingDep
) -> list[SectionText]:
    return await run_in_threadpool(service.read, student, course_id, document_id, position)


@router.get("/file")
async def download(course_id: str, document_id: str, student: Student, service: ReadingDep) -> Response:
    downloaded = await run_in_threadpool(service.download, student, course_id, document_id)
    return Response(
        content=downloaded.content,
        media_type=downloaded.content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(downloaded.filename)}"},
    )

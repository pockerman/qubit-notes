from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, Header, Response
from fastapi.concurrency import run_in_threadpool

from qubit_notes.api.deps import Student, StudentInLink, conversions, reading
from qubit_notes.domain.conversions import Conversions
from qubit_notes.domain.reading import OpenedMaterial, Reading
from qubit_notes.platform.port import SectionText

# a course is addressed by its id here, e.g. "maria--aeronautics": a student who isn't one of its
# members is refused, rather than told there's no such course
router = APIRouter(prefix="/courses/{course_id}/materials/{document_id}", tags=["reading"])
ReadingDep = Annotated[Reading, Depends(reading)]
ConversionsDep = Annotated[Conversions, Depends(conversions)]


@router.get("", response_model=OpenedMaterial)
async def open_material(course_id: str, document_id: str, student: Student, service: ReadingDep) -> OpenedMaterial:
    return await run_in_threadpool(service.open, student, course_id, document_id)


@router.get("/sections/{position}", response_model=list[SectionText])
async def read_section(
    course_id: str, document_id: str, position: int, student: Student, service: ReadingDep
) -> list[SectionText]:
    return await run_in_threadpool(service.read, student, course_id, document_id, position)


def _byte_range(header: str | None) -> tuple[int, int] | None:
    """the (offset, length) of a "bytes=start-[end]" Range header; length 0 means to the end"""
    if not header or not header.startswith("bytes=") or "," in header:
        return None
    start, _, end = header.removeprefix("bytes=").partition("-")
    if not start.isdigit() or (end and not end.isdigit()):
        return None
    offset = int(start)
    return offset, (int(end) - offset + 1 if end else 0)


@router.get("/file")
async def download(
    course_id: str,
    document_id: str,
    service: ReadingDep,
    who: StudentInLink,
    range: Annotated[str | None, Header()] = None,
    inline: bool = False,
) -> Response:
    """The uploaded file. A <video> element can't send headers, so who the student is may come in the link instead:
    ?student= by name, or ?access_token= with Cognito. It asks for parts of the file with a Range header to seek."""
    byte_range = _byte_range(range)
    offset, length = byte_range or (0, 0)
    downloaded = await run_in_threadpool(service.download, who, course_id, document_id, offset, length)
    disposition = "inline" if inline else "attachment"
    headers = {
        "Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(downloaded.filename)}",
        "Accept-Ranges": "bytes",
    }
    if byte_range is None:
        return Response(content=downloaded.content, media_type=downloaded.content_type, headers=headers)
    end = offset + len(downloaded.content) - 1
    headers["Content-Range"] = f"bytes {offset}-{end}/{downloaded.size}"
    return Response(content=downloaded.content, status_code=206, media_type=downloaded.content_type, headers=headers)


@router.get("/export")
async def export(course_id: str, document_id: str, student: Student, service: ConversionsDep) -> Response:
    """a material converted from a PDF or an EPUB as it is now, as a PDF or an EPUB laid out anew from its Markdown"""
    exported = await run_in_threadpool(service.export, student, course_id, document_id)
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(exported.filename)}"}
    return Response(content=exported.content, media_type=exported.content_type, headers=headers)

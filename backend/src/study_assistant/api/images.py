from typing import Annotated

from fastapi import APIRouter, Depends, Form, Response, UploadFile
from fastapi.concurrency import run_in_threadpool

from study_assistant.api.deps import Student, images
from study_assistant.domain.images import Images, MaterialImages

router = APIRouter(prefix="/courses/{course_id}/materials/{document_id}/images", tags=["images"])
ImagesDep = Annotated[Images, Depends(images)]


@router.get("", response_model=MaterialImages)
async def images_of(course_id: str, document_id: str, student: Student, service: ImagesDep) -> MaterialImages:
    """the images the material refers to: those it has and those missing"""
    return await run_in_threadpool(service.of, student, course_id, document_id)


@router.post("", response_model=MaterialImages)
async def add_image(
    course_id: str,
    document_id: str,
    student: Student,
    service: ImagesDep,
    file: UploadFile,
    path: Annotated[str | None, Form()] = None,
) -> MaterialImages:
    """keeps the image under ``path``, or under the path the material refers to by the image's file name"""
    content = await file.read()
    return await run_in_threadpool(service.add, student, course_id, document_id, file.filename or "", content, path)


@router.get("/{path:path}")
async def image(course_id: str, document_id: str, path: str, student: Student, service: ImagesDep) -> Response:
    found = await run_in_threadpool(service.get, student, course_id, document_id, path)
    # served as the image it was checked to be, and nothing else
    headers = {
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'none'",
        "Cache-Control": "private, max-age=300",
    }
    return Response(content=found.content, media_type=found.content_type, headers=headers)

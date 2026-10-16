from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile
from fastapi.concurrency import run_in_threadpool

from study_assistant.api.deps import Student, materials
from study_assistant.domain.materials import Material, Materials, Upload
from study_assistant.platform.port import IngestJob

router = APIRouter(tags=["materials"])
MaterialsDep = Annotated[Materials, Depends(materials)]


@router.post("/materials", response_model=Upload, status_code=202)
async def upload(student: Student, service: MaterialsDep, file: UploadFile, location: Annotated[str, Form()]) -> Upload:
    content = await file.read()
    return await run_in_threadpool(service.upload, student, location, file.filename or "", content)


@router.get("/uploads/{job_id}", response_model=IngestJob)
async def upload_status(job_id: str, student: Student, service: MaterialsDep) -> IngestJob:
    return await run_in_threadpool(service.ingestion, job_id)


@router.get("/courses/{course}/materials", response_model=list[Material])
async def list_materials(
    course: str, student: Student, service: MaterialsDep, subject: str | None = None, topic: str | None = None
) -> list[Material]:
    return await run_in_threadpool(service.list, student, course, subject, topic)


@router.delete("/courses/{course}/materials/{subject}/{topic}/{filename}", response_model=Material)
async def delete_material(
    course: str, subject: str, topic: str, filename: str, student: Student, service: MaterialsDep
) -> Material:
    return await run_in_threadpool(service.delete, student, f"{course}/{subject}/{topic}", filename)

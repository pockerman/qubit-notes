from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from study_assistant.api.deps import Student, materials, topics
from study_assistant.domain.materials import Material, Materials, Upload
from study_assistant.domain.topics import Topic, Topics
from study_assistant.platform.port import IngestJob

router = APIRouter(tags=["materials"])
MaterialsDep = Annotated[Materials, Depends(materials)]
TopicsDep = Annotated[Topics, Depends(topics)]


class NewTopic(BaseModel):
    subject: str
    topic: str


class Text(BaseModel):
    text: str


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


@router.get("/courses/{course}/topics", response_model=list[Topic])
async def list_topics(course: str, student: Student, service: TopicsDep) -> list[Topic]:
    return await run_in_threadpool(service.list, student, course)


@router.post("/courses/{course}/topics", response_model=Topic, status_code=201)
async def create_topic(course: str, body: NewTopic, student: Student, service: TopicsDep) -> Topic:
    return await run_in_threadpool(service.create, student, course, body.subject, body.topic)


@router.get("/courses/{course_id}/materials/{document_id}/text", response_model=Text)
async def material_text(course_id: str, document_id: str, student: Student, service: MaterialsDep) -> Text:
    """the text of a Markdown or text material, to edit"""
    return Text(text=await run_in_threadpool(service.text, student, course_id, document_id))


@router.put("/courses/{course_id}/materials/{document_id}/text", response_model=Upload, status_code=202)
async def edit_material(
    course_id: str, document_id: str, body: Text, student: Student, service: MaterialsDep
) -> Upload:
    """gives the material new text, which is processed again"""
    return await run_in_threadpool(service.edit, student, course_id, document_id, body.text)

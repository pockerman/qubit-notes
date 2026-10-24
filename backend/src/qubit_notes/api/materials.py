from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, materials, reading_order, topics
from qubit_notes.domain.materials import Material, Materials, Upload
from qubit_notes.domain.reading_order import Neighbours, ReadingOrder
from qubit_notes.domain.topics import Subject, Topic, Topics
from qubit_notes.platform.port import IngestJob

router = APIRouter(tags=["materials"])
MaterialsDep = Annotated[Materials, Depends(materials)]
TopicsDep = Annotated[Topics, Depends(topics)]
ReadingOrderDep = Annotated[ReadingOrder, Depends(reading_order)]


class NewTopic(BaseModel):
    # their ids
    subject: str
    topic: str
    # what they are called, as the student typed them; named after their ids if not given
    subject_name: str | None = None
    topic_name: str | None = None


class NewName(BaseModel):
    name: str


class TopicOrder(BaseModel):
    topics: list[str]


class MaterialOrder(BaseModel):
    # the topic's materials by filename
    materials: list[str]


class Text(BaseModel):
    text: str


class WrittenMaterial(BaseModel):
    # what the student calls it; it is saved as a Markdown filename made from it
    name: str
    text: str


@router.post("/materials", response_model=Upload, status_code=202)
async def upload(student: Student, service: MaterialsDep, file: UploadFile, location: Annotated[str, Form()]) -> Upload:
    content = await file.read()
    return await run_in_threadpool(service.upload, student, location, file.filename or "", content)


@router.post("/courses/{course}/subjects/{subject}/topics/{topic}/materials", response_model=Upload, status_code=202)
async def write_material(
    course: str, subject: str, topic: str, body: WrittenMaterial, student: Student, service: MaterialsDep
) -> Upload:
    """a Markdown material the student wrote in the topic; processed like an upload"""
    return await run_in_threadpool(service.write, student, f"{course}/{subject}/{topic}", body.name, body.text)


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
    return await run_in_threadpool(
        service.create, student, course, body.subject, body.topic, body.subject_name, body.topic_name
    )


@router.get("/courses/{course}/subjects", response_model=list[Subject])
async def list_subjects(course: str, student: Student, service: TopicsDep) -> list[Subject]:
    """the course's subjects, also those without topics"""
    return await run_in_threadpool(service.subjects, student, course)


@router.post("/courses/{course}/subjects", response_model=Subject, status_code=201)
async def create_subject(course: str, body: NewName, student: Student, service: TopicsDep) -> Subject:
    """a subject, before any of its topics; its id is made from its name"""
    return await run_in_threadpool(service.create_subject, student, course, body.name)


@router.delete("/courses/{course}/subjects/{subject}", status_code=204)
async def delete_subject(course: str, subject: str, student: Student, service: TopicsDep) -> None:
    """deletes a subject that has no topics"""
    await run_in_threadpool(service.delete_subject, student, course, subject)


@router.put("/courses/{course}/subjects/{subject}/topics/{topic}/name", response_model=Topic)
async def rename_topic(
    course: str, subject: str, topic: str, body: NewName, student: Student, service: TopicsDep
) -> Topic:
    """gives the topic another name; its id, in links and references, stays"""
    return await run_in_threadpool(service.rename, student, course, subject, topic, body.name)


@router.put("/courses/{course}/subjects/{subject}/name", response_model=list[Topic])
async def rename_subject(course: str, subject: str, body: NewName, student: Student, service: TopicsDep) -> list[Topic]:
    """gives the subject another name; its id stays"""
    return await run_in_threadpool(service.rename_subject, student, course, subject, body.name)


@router.delete("/courses/{course}/subjects/{subject}/topics/{topic}", status_code=204)
async def delete_topic(course: str, subject: str, topic: str, student: Student, service: TopicsDep) -> None:
    """deletes the topic with all of its material"""
    await run_in_threadpool(service.delete, student, course, subject, topic)


@router.put("/courses/{course}/subjects/{subject}/topics/{topic}/material-order", response_model=list[Material])
async def order_materials(
    course: str, subject: str, topic: str, body: MaterialOrder, student: Student, service: MaterialsDep
) -> list[Material]:
    """puts the topic's material in the order it's meant to be read"""
    return await run_in_threadpool(service.order, student, f"{course}/{subject}/{topic}", body.materials)


@router.get("/courses/{course_id}/materials/{document_id}/neighbours", response_model=Neighbours)
async def neighbours(course_id: str, document_id: str, student: Student, service: ReadingOrderDep) -> Neighbours:
    """the materials before and after this one in its subject, to read on"""
    return await run_in_threadpool(service.neighbours, student, course_id, document_id)


@router.put("/courses/{course}/subjects/{subject}/topic-order", response_model=list[Topic])
async def order_topics(
    course: str, subject: str, body: TopicOrder, student: Student, service: TopicsDep
) -> list[Topic]:
    """puts the subject's topics in the order they're meant to be read"""
    return await run_in_threadpool(service.order, student, course, subject, body.topics)


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

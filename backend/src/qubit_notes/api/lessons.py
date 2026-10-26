"""A subject's lessons made from a document: see domain/lessons.py."""

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.concurrency import run_in_threadpool

from qubit_notes.api.deps import Student, lessons
from qubit_notes.domain.lessons import LessonImport, Lessons, Original

router = APIRouter(tags=["lessons"])
LessonsDep = Annotated[Lessons, Depends(lessons)]


@router.post("/courses/{course}/subjects/{subject}/lessons", response_model=LessonImport, status_code=202)
async def make_lessons(
    course: str, subject: str, student: Student, service: LessonsDep, file: UploadFile
) -> LessonImport:
    """makes a topic of each heading of the document, in the background"""
    content = await file.read()
    return await run_in_threadpool(service.start, student, course, subject, file.filename or "", content)


@router.get("/courses/{course}/subjects/{subject}/originals", response_model=list[Original])
async def originals(course: str, subject: str, student: Student, service: LessonsDep) -> list[Original]:
    """the documents the subject's lessons were made from; each lesson's material downloads its original"""
    return await run_in_threadpool(service.originals, student, course, subject)


@router.get("/lesson-imports/{import_id}", response_model=LessonImport)
async def lesson_import(import_id: str, student: Student, service: LessonsDep) -> LessonImport:
    return await run_in_threadpool(service.get, student, import_id)

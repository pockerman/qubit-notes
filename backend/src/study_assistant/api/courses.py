from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from study_assistant.api.deps import Student, courses
from study_assistant.domain.courses import Course, Courses
from study_assistant.platform.port import MemberRole

router = APIRouter(prefix="/courses", tags=["courses"])
CoursesDep = Annotated[Courses, Depends(courses)]


class CourseResponse(BaseModel):
    id: str
    name: str
    owner: str
    role: MemberRole


class MemberResponse(BaseModel):
    student: str
    role: MemberRole


class NewCourse(BaseModel):
    name: str


class ShareRequest(BaseModel):
    student: str
    role: MemberRole


def _course(course: Course, student: str) -> CourseResponse:
    return CourseResponse(id=course.id, name=course.name, owner=course.owner, role=course.role_of(student))


def _members(course: Course) -> list[MemberResponse]:
    return [MemberResponse(student=name, role=role) for name, role in sorted(course.members.items())]


@router.get("", response_model=list[CourseResponse])
async def list_courses(student: Student, catalog: CoursesDep) -> list[CourseResponse]:
    return [_course(course, student) for course in await run_in_threadpool(catalog.list, student)]


@router.post("", response_model=CourseResponse, status_code=201)
async def create_course(body: NewCourse, student: Student, catalog: CoursesDep) -> CourseResponse:
    return _course(await run_in_threadpool(catalog.create, student, body.name), student)


@router.delete("/{course}", status_code=204)
async def delete_course(course: str, student: Student, catalog: CoursesDep) -> None:
    await run_in_threadpool(catalog.delete, student, course)


@router.get("/{course}/members", response_model=list[MemberResponse])
async def list_members(course: str, student: Student, catalog: CoursesDep) -> list[MemberResponse]:
    return _members(await run_in_threadpool(catalog.get, student, course))


@router.put("/{course}/members", response_model=list[MemberResponse])
async def share(course: str, body: ShareRequest, student: Student, catalog: CoursesDep) -> list[MemberResponse]:
    return _members(await run_in_threadpool(catalog.share, student, course, body.student, body.role))


@router.delete("/{course}/members/{member}", response_model=list[MemberResponse])
async def unshare(course: str, member: str, student: Student, catalog: CoursesDep) -> list[MemberResponse]:
    return _members(await run_in_threadpool(catalog.unshare, student, course, member))

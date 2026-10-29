from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, course_titles, courses, paper_records
from qubit_notes.domain.course_titles import CourseTitles
from qubit_notes.domain.courses import Course, Courses
from qubit_notes.domain.papers import PaperRecords
from qubit_notes.platform.port import MemberRole

router = APIRouter(prefix="/courses", tags=["courses"])
CoursesDep = Annotated[Courses, Depends(courses)]
TitlesDep = Annotated[CourseTitles, Depends(course_titles)]
RecordsDep = Annotated[PaperRecords, Depends(paper_records)]


class CourseResponse(BaseModel):
    id: str
    # in its links: lowercase words joined by hyphens
    name: str
    # what it is called
    title: str
    owner: str
    role: MemberRole


class MemberResponse(BaseModel):
    student: str
    role: MemberRole


class NewCourse(BaseModel):
    name: str
    # as the student typed it; titled after its name if not given
    title: str | None = None


class NewTitle(BaseModel):
    title: str


class ShareRequest(BaseModel):
    student: str
    role: MemberRole


def _courses(courses: list[Course], student: str, titles: CourseTitles) -> list[CourseResponse]:
    titled = titles.of(courses)
    return [
        CourseResponse(id=c.id, name=c.name, title=titled[c.id], owner=c.owner, role=c.role_of(student))
        for c in courses
    ]


def _members(course: Course) -> list[MemberResponse]:
    return [MemberResponse(student=name, role=role) for name, role in sorted(course.members.items())]


@router.get("", response_model=list[CourseResponse])
async def list_courses(
    student: Student, catalog: CoursesDep, titles: TitlesDep, records: RecordsDep
) -> list[CourseResponse]:
    """the student's courses, and those shared with them; their collections of papers are under /papers"""
    collections = await run_in_threadpool(records.collections)
    listed = await run_in_threadpool(catalog.list, student)
    return _courses([course for course in listed if course.id not in collections], student, titles)


@router.post("", response_model=CourseResponse, status_code=201)
async def create_course(body: NewCourse, student: Student, catalog: CoursesDep, titles: TitlesDep) -> CourseResponse:
    course = await run_in_threadpool(catalog.create, student, body.name)
    if body.title and body.title.strip():
        await run_in_threadpool(titles.title, student, course.name, body.title)
    return _courses([course], student, titles)[0]


@router.put("/{course}/title", response_model=CourseResponse)
async def change_title(course: str, body: NewTitle, student: Student, titles: TitlesDep) -> CourseResponse:
    """gives the course another title; its name, in its links, stays. Only its creator can"""
    return _courses([await run_in_threadpool(titles.title, student, course, body.title)], student, titles)[0]


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

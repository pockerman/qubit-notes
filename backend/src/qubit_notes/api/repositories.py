"""A subject's repository: connecting it, pushing to it, and disconnecting it (features/subject_repository.feature)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, computed_field

from qubit_notes.api.deps import Student
from qubit_notes.domain.subject_repositories import Connection, Pushed, SubjectRepositories

router = APIRouter()


def subject_repositories(request: Request) -> SubjectRepositories:
    return request.app.state.subject_repositories


Repositories = Annotated[SubjectRepositories, Depends(subject_repositories)]


class Connect(BaseModel):
    # e.g. maria/numerical-methods
    repository: str
    # a token GitHub gives that may write to the repository's contents; never shown back
    token: str


class ConnectionOut(Connection):
    @computed_field
    @property
    def connected(self) -> bool:
        return self.repository is not None


def _out(connection: Connection) -> ConnectionOut:
    return ConnectionOut(**connection.model_dump())


@router.get("/courses/{course}/subjects/{subject}/repository", response_model=ConnectionOut)
async def connection(course: str, subject: str, student: Student, service: Repositories) -> ConnectionOut:
    """the repository the student pushes the subject to, if any, and when they last pushed it"""
    return _out(await run_in_threadpool(service.connection, student, course, subject))


@router.put("/courses/{course}/subjects/{subject}/repository", response_model=ConnectionOut)
async def connect(course: str, subject: str, body: Connect, student: Student, service: Repositories) -> ConnectionOut:
    """connects the subject to a repository on GitHub, with a token that may write to it"""
    return _out(await run_in_threadpool(service.connect, student, course, subject, body.repository, body.token))


@router.delete("/courses/{course}/subjects/{subject}/repository", status_code=204)
async def disconnect(course: str, subject: str, student: Student, service: Repositories) -> None:
    """forgets the subject's repository and its token; the repository is left as it is"""
    await run_in_threadpool(service.disconnect, student, course, subject)


@router.post("/courses/{course}/subjects/{subject}/repository/push", response_model=Pushed)
async def push(course: str, subject: str, student: Student, service: Repositories) -> Pushed:
    """pushes everything of the subject that is the student's own, in one commit; none if nothing changed"""
    return await run_in_threadpool(service.push, student, course, subject)

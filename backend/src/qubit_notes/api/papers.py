from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, papers
from qubit_notes.conversion.details import Details
from qubit_notes.domain.courses import Course
from qubit_notes.domain.materials import Upload
from qubit_notes.domain.papers import Collection, Paper, Papers
from qubit_notes.platform.port import MemberRole

router = APIRouter(prefix="/papers", tags=["papers"])
PapersDep = Annotated[Papers, Depends(papers)]


class NewCollection(BaseModel):
    name: str
    # as the student typed it; titled after its name if not given
    title: str | None = None


class NewTitle(BaseModel):
    title: str


class MemberResponse(BaseModel):
    student: str
    role: MemberRole


class ShareRequest(BaseModel):
    student: str
    role: MemberRole


def _members(course: Course) -> list[MemberResponse]:
    return [MemberResponse(student=name, role=role) for name, role in sorted(course.members.items())]


@router.get("/collections", response_model=list[Collection])
async def list_collections(student: Student, service: PapersDep) -> list[Collection]:
    """the student's collections of papers, and those shared with them"""
    return await run_in_threadpool(service.collections, student)


@router.post("/collections", response_model=Collection, status_code=201)
async def create_collection(body: NewCollection, student: Student, service: PapersDep) -> Collection:
    return await run_in_threadpool(service.create, student, body.name, body.title)


@router.get("/collections/{collection_id}", response_model=Collection)
async def get_collection(collection_id: str, student: Student, service: PapersDep) -> Collection:
    return await run_in_threadpool(service.collection, student, collection_id)


@router.put("/collections/{collection_id}/title", response_model=Collection)
async def change_title(collection_id: str, body: NewTitle, student: Student, service: PapersDep) -> Collection:
    """gives the collection another title; its name, in its links, stays. Only its creator can"""
    return await run_in_threadpool(service.title, student, collection_id, body.title)


@router.delete("/collections/{collection_id}", status_code=204)
async def delete_collection(collection_id: str, student: Student, service: PapersDep) -> None:
    await run_in_threadpool(service.delete, student, collection_id)


@router.get("/collections/{collection_id}/members", response_model=list[MemberResponse])
async def list_members(collection_id: str, student: Student, service: PapersDep) -> list[MemberResponse]:
    return _members(await run_in_threadpool(service.get, student, collection_id))


@router.put("/collections/{collection_id}/members", response_model=list[MemberResponse])
async def share(collection_id: str, body: ShareRequest, student: Student, service: PapersDep) -> list[MemberResponse]:
    return _members(await run_in_threadpool(service.share, student, collection_id, body.student, body.role))


@router.delete("/collections/{collection_id}/members/{member}", response_model=list[MemberResponse])
async def unshare(collection_id: str, member: str, student: Student, service: PapersDep) -> list[MemberResponse]:
    return _members(await run_in_threadpool(service.unshare, student, collection_id, member))


@router.get("/collections/{collection_id}/papers", response_model=list[Paper])
async def list_papers(collection_id: str, student: Student, service: PapersDep) -> list[Paper]:
    """the collection's papers, by their titles"""
    return await run_in_threadpool(service.papers, student, collection_id)


@router.post("/collections/{collection_id}/papers", response_model=Upload, status_code=202)
async def upload_paper(collection_id: str, file: UploadFile, student: Student, service: PapersDep) -> Upload:
    """adds a paper, which is processed in the background as material is"""
    content = await file.read()
    return await run_in_threadpool(service.upload, student, collection_id, file.filename or "", content)


@router.get("/collections/{collection_id}/papers/{document_id}", response_model=Paper)
async def get_paper(collection_id: str, document_id: str, student: Student, service: PapersDep) -> Paper:
    return await run_in_threadpool(service.paper, student, collection_id, document_id)


@router.put("/collections/{collection_id}/papers/{document_id}/details", response_model=Paper)
async def describe_paper(
    collection_id: str, document_id: str, body: Details, student: Student, service: PapersDep
) -> Paper:
    """gives the paper other details; only the collection's owners can"""
    return await run_in_threadpool(service.describe, student, collection_id, document_id, body)


@router.delete("/collections/{collection_id}/papers/{document_id}", response_model=Paper)
async def delete_paper(collection_id: str, document_id: str, student: Student, service: PapersDep) -> Paper:
    return await run_in_threadpool(service.delete_paper, student, collection_id, document_id)

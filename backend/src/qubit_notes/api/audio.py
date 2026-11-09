"""A student's audio of a material (features/material_audio.feature)."""

from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, audios
from qubit_notes.domain.audio import Audio, Audios, SpeechModels

router = APIRouter(prefix="/courses/{course_id}/materials/{document_id}/audio", tags=["audio"])
# the speech models, apart from any material
models_router = APIRouter(tags=["audio"])
AudiosDep = Annotated[Audios, Depends(audios)]


@models_router.get("/speech-models", response_model=SpeechModels)
async def speech_models(student: Student, service: AudiosDep) -> SpeechModels:
    """the speech models a student chooses from, the app's own, and whether the app can speak"""
    return service.speech_models()


class Asked(BaseModel):
    # how it is to be written and spoken, if the student says
    instructions: str = ""
    # the speech model that reads it; the app's own if not given
    model: str | None = None


class Suggested(BaseModel):
    suggestions: str
    model: str | None = None


@router.get("", response_model=Audio | None)
async def get(course_id: str, document_id: str, student: Student, service: AudiosDep) -> Audio | None:
    """the student's audio of the material, or null if they have none"""
    return await run_in_threadpool(service.get, student, course_id, document_id)


@router.post("", response_model=Audio, status_code=202)
async def request(course_id: str, document_id: str, asked: Asked, student: Student, service: AudiosDep) -> Audio:
    """starts making the student's audio of the material; it is generating until it is ready, or has failed"""
    return await run_in_threadpool(service.request, student, course_id, document_id, asked.instructions, asked.model)


@router.post("/improvements", response_model=Audio, status_code=202)
async def improve(
    course_id: str, document_id: str, suggested: Suggested, student: Student, service: AudiosDep
) -> Audio:
    """starts making the audio anew, following the student's suggestions"""
    return await run_in_threadpool(
        service.improve, student, course_id, document_id, suggested.suggestions, suggested.model
    )


@router.delete("", status_code=204)
async def delete(course_id: str, document_id: str, student: Student, service: AudiosDep) -> None:
    await run_in_threadpool(service.delete, student, course_id, document_id)


@router.get("/file")
async def file(course_id: str, document_id: str, student: Student, service: AudiosDep) -> Response:
    """the audio as MP3"""
    made = await run_in_threadpool(service.file, student, course_id, document_id)
    headers = {"Content-Disposition": f"inline; filename*=UTF-8''{quote(made.filename)}"}
    return Response(content=made.content, media_type=made.content_type, headers=headers)

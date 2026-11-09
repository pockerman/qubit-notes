"""Checking a student's understanding (features/comprehension.feature), and answering by voice
(features/transcription.feature)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, comprehension, transcription
from qubit_notes.domain.comprehension import Check, ComprehensionAssistantAgent
from qubit_notes.domain.sources import Scope
from qubit_notes.domain.transcription import MAX_RECORDING_BYTES, Heard, Transcription, TranscriptionModels

router = APIRouter(prefix="/comprehension-checks", tags=["comprehension"])
transcription_router = APIRouter(tags=["comprehension"])
AgentDep = Annotated[ComprehensionAssistantAgent, Depends(comprehension)]
TranscriptionDep = Annotated[Transcription, Depends(transcription)]


class Answered(BaseModel):
    answer: str
    # whether the student said it, rather than typed it
    spoken: bool = False


@router.post("", response_model=Check, status_code=201)
async def start(scope: Scope, student: Student, agent: AgentDep) -> Check:
    """a new check of the student's understanding of the scope, with its first question"""
    return await run_in_threadpool(agent.start, student, scope)


@router.get("", response_model=list[Check])
async def checks_of(scope: Annotated[Scope, Query()], student: Student, agent: AgentDep) -> list[Check]:
    """the student's checks of the scope, newest first"""
    return await run_in_threadpool(agent.history, student, scope)


@router.get("/{check_id}", response_model=Check)
async def get(check_id: str, student: Student, agent: AgentDep) -> Check:
    return await run_in_threadpool(agent.get, student, check_id)


@router.post("/{check_id}/answers", response_model=Check)
async def answer(check_id: str, answered: Answered, student: Student, agent: AgentDep) -> Check:
    """the student's answer to the question waiting, assessed, with the next question"""
    return await run_in_threadpool(agent.answer, student, check_id, answered.answer, answered.spoken)


@router.post("/{check_id}/end", response_model=Check)
async def end(check_id: str, student: Student, agent: AgentDep) -> Check:
    """the check ended, with its verdict"""
    return await run_in_threadpool(agent.end, student, check_id)


@router.delete("/{check_id}", status_code=204)
async def delete(check_id: str, student: Student, agent: AgentDep) -> None:
    await run_in_threadpool(agent.delete, student, check_id)


@transcription_router.get("/transcription-models", response_model=TranscriptionModels)
async def transcription_models(student: Student, service: TranscriptionDep) -> TranscriptionModels:
    """the transcription models a student chooses from, the app's own, and whether the app can hear"""
    return service.models()


@transcription_router.post("/transcriptions", response_model=Heard)
async def transcribe(
    recording: UploadFile,
    student: Student,
    service: TranscriptionDep,
    model: Annotated[str | None, Form()] = None,
) -> Heard:
    """what the student said, recorded, as text; the recording isn't kept"""
    # one byte more than a recording can be is enough to refuse it
    audio = await recording.read(MAX_RECORDING_BYTES + 1)
    return await run_in_threadpool(service.transcribe, student, audio, recording.content_type or "", model)

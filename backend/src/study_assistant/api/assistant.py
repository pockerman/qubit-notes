"""The assistant: a student's requests, in their own words, while reading a material or studying a topic, and their
conversation with it there."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from study_assistant.api.deps import Student, assistant
from study_assistant.domain.assistant import Assistant, Conversation, Turn
from study_assistant.domain.sources import Scope

router = APIRouter(prefix="/assistant", tags=["assistant"])
AssistantDep = Annotated[Assistant, Depends(assistant)]


class Request(Scope):
    """what the student asks, and where they are: a section of a material (or the material), or a topic"""

    question: str


@router.post("/requests", response_model=Turn)
async def ask(request: Request, student: Student, service: AssistantDep) -> Turn:
    where = Scope(**request.model_dump(exclude={"question"}))
    return await run_in_threadpool(service.ask, student, where, request.question)


@router.get("/conversation", response_model=Conversation)
async def conversation(where: Annotated[Scope, Query()], student: Student, service: AssistantDep) -> Conversation:
    """the student's conversation on the material or the topic"""
    return await run_in_threadpool(service.conversation, student, where)


@router.delete("/conversation", response_model=Conversation)
async def start_again(where: Annotated[Scope, Query()], student: Student, service: AssistantDep) -> Conversation:
    """forgets the conversation, so the next request starts a new one"""
    return await run_in_threadpool(service.start_again, student, where)

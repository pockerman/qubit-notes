"""The writing assistant: help writing a Markdown material in a topic, from the web, citing it
(features/writing_assistant.feature)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, writing_assistant
from qubit_notes.domain.assistant import Rating
from qubit_notes.domain.writing_assistant import WriteMaterialAssistantAgent, WritingReply, WritingRequest

router = APIRouter(tags=["writing assistant"])
AgentDep = Annotated[WriteMaterialAssistantAgent, Depends(writing_assistant)]


@router.post("/courses/{course_id}/subjects/{subject}/topics/{topic}/writing-assistant", response_model=WritingReply)
async def ask(
    course_id: str, subject: str, topic: str, asked: WritingRequest, student: Student, agent: AgentDep
) -> WritingReply:
    """what the writing assistant writes for the student, for a material in the topic"""
    return await run_in_threadpool(agent.ask, student, course_id, subject, topic, asked)


class Rated(BaseModel):
    # None takes the rating back
    rating: Rating | None


@router.put("/writing-assistant/replies/{reply_id}/rating", response_model=WritingReply)
async def rate(reply_id: str, rated: Rated, student: Student, agent: AgentDep) -> WritingReply:
    """the student's thumbs up or down of a reply of the writing assistant to them"""
    return await run_in_threadpool(agent.rate, student, reply_id, rated.rating)

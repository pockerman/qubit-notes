"""How many tokens the AI has used: a student's own, and for the app's admins, everyone's."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from qubit_notes.api.deps import Student, ai_usage, app_keys
from qubit_notes.domain.app_keys import AppKeys
from qubit_notes.domain.usage import DAYS, AIUsage, StudentUsage, Usage

router = APIRouter(prefix="/usage", tags=["usage"])
AIUsageDep = Annotated[AIUsage, Depends(ai_usage)]
AppKeysDep = Annotated[AppKeys, Depends(app_keys)]
Days = Annotated[int, Query(ge=1, le=366)]


@router.get("", response_model=Usage)
async def mine(student: Student, service: AIUsageDep, days: Days = DAYS) -> Usage:
    """the tokens the student has used over the last days"""
    return await run_in_threadpool(service.of, student, days)


@router.get("/students", response_model=list[StudentUsage])
async def everyone(student: Student, service: AIUsageDep, keys: AppKeysDep, days: Days = DAYS) -> list[StudentUsage]:
    """the tokens each student has used over the last days, most first; only the app's admins see it"""
    return await run_in_threadpool(service.of_students, keys.is_admin(student), days)

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, ai_model, app_keys
from qubit_notes.domain.ai_model import AIModel, AIModelInUse
from qubit_notes.domain.app_keys import AppKeys

router = APIRouter(tags=["ai model"])
AIModelDep = Annotated[AIModel, Depends(ai_model)]
AppKeysDep = Annotated[AppKeys, Depends(app_keys)]


class ModelChoice(BaseModel):
    provider: str
    # the provider's own if not given
    model: str | None = None


@router.get("/ai-model", response_model=AIModelInUse)
async def in_use(student: Student, service: AIModelDep) -> AIModelInUse:
    """the provider and model the AI answers with, and whether the app has each provider's key"""
    return await run_in_threadpool(service.in_use)


@router.put("/ai-model", response_model=AIModelInUse)
async def choose(body: ModelChoice, student: Student, service: AIModelDep, keys: AppKeysDep) -> AIModelInUse:
    """the AI answers with this model from now on; only the app's admins choose"""
    return await run_in_threadpool(service.choose, keys.is_admin(student), body.provider, body.model)

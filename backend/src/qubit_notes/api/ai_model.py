from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from starlette.types import ASGIApp, Receive, Scope, Send

from qubit_notes.api.deps import Student, ai_model, app_keys
from qubit_notes.domain.ai_model import AIModel, AIModelInUse
from qubit_notes.domain.app_keys import AppKeys
from qubit_notes.platform.port import chosen_ai

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


class ChosenProvider:
    """Answers a request with the model provider the student chose, named in its X-AI-Provider header, rather than
    the app's, where the app has that provider's key; else with the app's."""

    def __init__(self, app: ASGIApp):
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        provider = dict(scope.get("headers", [])).get(b"x-ai-provider") if scope["type"] == "http" else None
        if not provider:
            await self._app(scope, receive, send)
            return
        models: AIModel = scope["app"].state.ai_model
        token = chosen_ai.set(await run_in_threadpool(models.chosen, provider.decode().strip().lower()))
        try:
            await self._app(scope, receive, send)
        finally:
            chosen_ai.reset(token)

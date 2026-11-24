"""The prompts' versions, for the app's admins (features/prompt_versions.feature)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, app_keys
from qubit_notes.domain.app_keys import AppKeys
from qubit_notes.domain.prompt_versions import Comparison, PromptInUse, PromptVersion, PromptVersions

router = APIRouter(prefix="/prompts", tags=["prompts"])
AppKeysDep = Annotated[AppKeys, Depends(app_keys)]


def prompt_versions(request: Request) -> PromptVersions:
    return request.app.state.prompt_versions


PromptVersionsDep = Annotated[PromptVersions, Depends(prompt_versions)]


class Choice(BaseModel):
    # None: the version prompt.toml names
    version: int | None = None


@router.get("", response_model=list[PromptInUse])
async def overview(student: Student, service: PromptVersionsDep, keys: AppKeysDep) -> list[PromptInUse]:
    """every prompt, its versions and the one in use"""
    return await run_in_threadpool(service.overview, keys.is_admin(student))


@router.get("/{name}/versions/{version}", response_model=PromptVersion)
async def read(name: str, version: int, student: Student, service: PromptVersionsDep, keys: AppKeysDep):
    return await run_in_threadpool(service.read, keys.is_admin(student), name, version)


@router.get("/{name}/comparison", response_model=Comparison)
async def compare(
    name: str,
    student: Student,
    service: PromptVersionsDep,
    keys: AppKeysDep,
    old: Annotated[int, Query()],
    new: Annotated[int, Query()],
) -> Comparison:
    """how the version ``new`` of the prompt differs from ``old``, line by line"""
    return await run_in_threadpool(service.compare, keys.is_admin(student), name, old, new)


@router.put("/{name}/choice", response_model=PromptInUse)
async def choose(name: str, body: Choice, student: Student, service: PromptVersionsDep, keys: AppKeysDep):
    """the version of the prompt used from now on, for everyone; none for prompt.toml's"""
    return await run_in_threadpool(service.choose, keys.is_admin(student), name, body.version)

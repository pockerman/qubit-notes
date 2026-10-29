from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, app_keys
from qubit_notes.domain.app_keys import AppKeys, KeyState

router = APIRouter(tags=["app keys"])
AppKeysDep = Annotated[AppKeys, Depends(app_keys)]


class Me(BaseModel):
    student: str
    # whether the student can give the app the keys it is missing
    admin: bool


class KeyRequest(BaseModel):
    key: str


@router.get("/me", response_model=Me)
async def me(student: Student, service: AppKeysDep) -> Me:
    """who is signed in"""
    return Me(student=student, admin=service.is_admin(student))


@router.put("/keys/{provider}", status_code=204)
async def give_key(provider: str, body: KeyRequest, student: Student, service: AppKeysDep) -> Response:
    """the app uses the key for the model provider from now on; it is never given back"""
    await run_in_threadpool(service.give, student, provider, body.key)
    return Response(status_code=204)


@router.get("/keys", response_model=list[KeyState])
async def key_states(student: Student, service: AppKeysDep) -> list[KeyState]:
    """whether the app has each model provider's key, never the keys"""
    return await run_in_threadpool(service.states)


@router.delete("/keys/{provider}", status_code=204)
async def take_back_key(provider: str, student: Student, service: AppKeysDep) -> Response:
    """the app has no key for the model provider from now on; one its settings give can't be removed"""
    await run_in_threadpool(service.take_back, student, provider)
    return Response(status_code=204)

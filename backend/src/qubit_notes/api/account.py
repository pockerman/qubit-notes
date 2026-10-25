from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from qubit_notes.api.deps import Student, account
from qubit_notes.domain.account import Account, AccountDetails

router = APIRouter(tags=["account"])
AccountDep = Annotated[Account, Depends(account)]


def access_token(request: Request) -> str | None:
    """the student's Cognito access token, which Cognito changes their account with"""
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    return token.strip() if scheme.lower() == "bearer" and token.strip() else None


Token = Annotated[str | None, Depends(access_token)]


class PasswordChange(BaseModel):
    current: str
    new: str


class EmailChange(BaseModel):
    email: str


class EmailCode(BaseModel):
    code: str


@router.get("/account", response_model=AccountDetails)
async def details(student: Student, token: Token, service: AccountDep) -> AccountDetails:
    """how the student signs in, and their email"""
    return await run_in_threadpool(service.details, token)


@router.put("/account/password", status_code=204)
async def change_password(body: PasswordChange, student: Student, token: Token, service: AccountDep) -> Response:
    """the student signs in with the new password from now on; it needs the current one"""
    await run_in_threadpool(service.change_password, token, body.current, body.new)
    return Response(status_code=204)


@router.put("/account/email", status_code=204)
async def change_email(body: EmailChange, student: Student, token: Token, service: AccountDep) -> Response:
    """Cognito emails a code to the new email, which is used once the student confirms it"""
    await run_in_threadpool(service.change_email, token, body.email)
    return Response(status_code=204)


@router.post("/account/email/confirm", status_code=204)
async def confirm_email(body: EmailCode, student: Student, token: Token, service: AccountDep) -> Response:
    """the new email is used from now on"""
    await run_in_threadpool(service.confirm_email, token, body.code)
    return Response(status_code=204)

"""A student's account (features/account.feature): signed in with Cognito, their email and password are their
Cognito account's, which the app changes through Cognito's API with the student's own access token, so it never
keeps either. A new email is used once the student confirms it with the code Cognito emails to it. Signed in by name,
a student has no email or password."""

import httpx
from loguru import logger
from pydantic import BaseModel

from qubit_notes.domain.errors import Conflict, InvalidRequest, NotAllowed
from qubit_notes.settings import Settings

# what Cognito answers with when it refuses, to what the student is told
REFUSED = {
    "NotAuthorizedException": "your current password is not right",
    "InvalidPasswordException": "the new password does not meet the rules for passwords",
    "InvalidParameterException": "that is not a valid email or password",
    "CodeMismatchException": "the code is not right",
    "ExpiredCodeException": "the code has expired: change your email again for a new one",
    "AliasExistsException": "another account has that email",
    "LimitExceededException": "too many tries: try again later",
    "TooManyRequestsException": "too many tries: try again later",
}


class AccountDetails(BaseModel):
    # how the student signs in: by name, or with Cognito
    signs_in_with: str
    email: str | None = None


class Account:
    def __init__(self, settings: Settings):
        self._cognito = settings.cognito_api if settings.auth == "cognito" else ""

    def details(self, token: str | None) -> AccountDetails:
        if not self._cognito:
            return AccountDetails(signs_in_with="name")
        user = self._call("GetUser", token, {})
        attributes = {a["Name"]: a["Value"] for a in user.get("UserAttributes", [])}
        return AccountDetails(signs_in_with="cognito", email=attributes.get("email"))

    def change_password(self, token: str | None, current: str, new: str) -> None:
        self._call("ChangePassword", token, {"PreviousPassword": current, "ProposedPassword": new})

    def change_email(self, token: str | None, email: str) -> None:
        """Cognito emails a code to the new email; the student keeps the one they had until they confirm it"""
        email = email.strip()
        if "@" not in email:
            raise InvalidRequest("that is not a valid email")
        self._call("UpdateUserAttributes", token, {"UserAttributes": [{"Name": "email", "Value": email}]})

    def confirm_email(self, token: str | None, code: str) -> None:
        self._call("VerifyUserAttribute", token, {"AttributeName": "email", "Code": code.strip()})

    def _call(self, action: str, token: str | None, body: dict) -> dict:
        if not self._cognito:
            raise Conflict("you sign in by name, so you have no email or password to change")
        if not token:
            raise NotAllowed("sign in with Cognito to change your account")
        response = httpx.post(
            self._cognito,
            json={"AccessToken": token, **body},
            headers={
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Target": f"AWSCognitoIdentityProviderService.{action}",
            },
            timeout=30,
        )
        if response.is_success:
            return response.json() if response.content else {}
        # Cognito names the kind of refusal in __type, e.g. "NotAuthorizedException"
        kind = response.json().get("__type", "").rpartition("#")[2] if response.content else ""
        if kind in REFUSED:
            raise InvalidRequest(REFUSED[kind])
        logger.error(f"Cognito refused {action}: {response.status_code} {response.text}")
        raise Conflict("Cognito could not change your account: try again later")

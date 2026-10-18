"""Who is making a request.

Run without Cognito, as in development, a student says who they are with the ``X-Student-Id`` header. Run with
Cognito (``QUBIT_NOTES_AUTH=cognito``), a student signs in with Amazon Cognito and every request carries their
access token, ``Authorization: Bearer ...``. The token must be signed by the app's user pool, issued to the app, an
access token and not expired; the student is the Cognito username in it.
"""

from typing import Protocol

import jwt
from fastapi import HTTPException, Request
from loguru import logger

from qubit_notes.settings import Settings

SIGN_IN = {"WWW-Authenticate": "Bearer"}


def _asked_to_sign_in(why: str) -> HTTPException:
    return HTTPException(status_code=401, detail=why, headers=SIGN_IN)


class Authenticator(Protocol):
    def student(self, request: Request, *, in_link: bool = False) -> str:
        """the student making the request; ``in_link`` for a link a ``<video>`` follows, which can't send headers"""
        ...

    def config(self) -> dict:
        """what the browser needs to sign students in"""
        ...


class NameAuthenticator:
    """The student says who they are."""

    def student(self, request: Request, *, in_link: bool = False) -> str:
        student = request.headers.get("X-Student-Id") or (request.query_params.get("student") if in_link else None)
        if not student:
            raise _asked_to_sign_in("say who you are with X-Student-Id")
        return student

    def config(self) -> dict:
        return {"auth": "name"}


class CognitoAuthenticator:
    """The student is who their Cognito access token says."""

    def __init__(self, settings: Settings):
        if not (settings.cognito_client_id and settings.cognito_domain and settings.issuer):
            raise ValueError(
                "signing in with Cognito needs QUBIT_NOTES_COGNITO_CLIENT_ID, QUBIT_NOTES_COGNITO_DOMAIN and "
                "the user pool: QUBIT_NOTES_COGNITO_REGION and QUBIT_NOTES_COGNITO_USER_POOL_ID"
            )
        self._issuer = settings.issuer
        self._client_id = settings.cognito_client_id
        self._domain = settings.cognito_domain.rstrip("/")
        # the user pool's public keys, fetched when a token names a key not seen yet
        self._keys = jwt.PyJWKClient(f"{self._issuer}/.well-known/jwks.json", cache_keys=True, lifespan=3600)

    def student(self, request: Request, *, in_link: bool = False) -> str:
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "bearer" or not token:
            token = request.query_params.get("access_token", "") if in_link else ""
        if not token:
            raise _asked_to_sign_in("sign in with Cognito")
        return self._username(token.strip())

    def _username(self, token: str) -> str:
        try:
            key = self._keys.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                key.key,
                algorithms=["RS256"],
                issuer=self._issuer,
                options={"require": ["exp", "iss", "token_use"], "verify_aud": False},
            )
        except jwt.PyJWTError as e:
            logger.info(f"a Cognito token was not accepted: {e}")
            raise _asked_to_sign_in("the sign-in is not valid or has expired; sign in again") from e
        # an access token says which app it was issued to with client_id; an ID token is not sent to the app
        if claims.get("token_use") != "access" or claims.get("client_id") != self._client_id:
            raise _asked_to_sign_in("the token is not an access token of this app; sign in again")
        username = claims.get("username")
        if not username:
            raise _asked_to_sign_in("the token has no username; sign in again")
        return username

    def config(self) -> dict:
        return {"auth": "cognito", "cognito": {"domain": self._domain, "client_id": self._client_id}}


def authenticator(settings: Settings) -> Authenticator:
    return CognitoAuthenticator(settings) if settings.auth == "cognito" else NameAuthenticator()

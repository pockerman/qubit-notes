"""A stand-in for Amazon Cognito: a user pool's signing keys and tokens, and the pages of its managed sign-in.

It serves what the app and the browser use of Cognito, as Cognito does:

- ``/.well-known/jwks.json``: the pool's public keys, under its issuer
- ``/oauth2/authorize``: the sign-in page; signing in sends the browser back to the app with a code
- ``/oauth2/token``: a code, with the PKCE verifier of its challenge, for tokens; and a refresh token for new ones
- ``/logout``: ends the sign-in and sends the browser back to the app
"""

import base64
import hashlib
import html
import secrets
import time
import uuid
from urllib.parse import urlencode

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

CLIENT_ID = "qubit-notes-test-client"


class SigningKey:
    def __init__(self):
        self.kid = uuid.uuid4().hex
        self.private = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def jwk(self) -> dict:
        jwk = jwt.algorithms.RSAAlgorithm.to_jwk(self.private.public_key(), as_dict=True)
        return {**jwk, "kid": self.kid, "use": "sig", "alg": "RS256"}


class FakeCognito:
    def __init__(self):
        self.base_url = ""
        self.key = SigningKey()
        self.users: set[str] = set()
        # code to (username, PKCE challenge, redirect uri)
        self._codes: dict[str, tuple[str, str, str]] = {}
        self._refresh: dict[str, str] = {}

    @property
    def issuer(self) -> str:
        return self.base_url

    def token(
        self,
        username: str,
        *,
        expired: bool = False,
        key: SigningKey | None = None,
        issuer: str | None = None,
        client_id: str = CLIENT_ID,
        token_use: str = "access",
    ) -> str:
        """a token of the pool, as Cognito issues them; the arguments make the kinds the app must not accept"""
        now = int(time.time())
        claims = {
            "sub": str(uuid.uuid5(uuid.NAMESPACE_DNS, username)),
            "iss": issuer or self.issuer,
            "token_use": token_use,
            "auth_time": now,
            "iat": now - 7200 if expired else now,
            "exp": now - 3600 if expired else now + 3600,
            "jti": uuid.uuid4().hex,
        }
        if token_use == "access":
            claims |= {"client_id": client_id, "username": username, "scope": "openid"}
        else:
            claims |= {"aud": client_id, "cognito:username": username}
        key = key or self.key
        return jwt.encode(claims, key.private, algorithm="RS256", headers={"kid": key.kid})

    def app(self) -> FastAPI:
        app = FastAPI()
        # the browser calls the token endpoint from the app's origin
        app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

        @app.get("/.well-known/jwks.json")
        def jwks():
            return {"keys": [self.key.jwk()]}

        @app.get("/oauth2/authorize", response_class=HTMLResponse)
        def authorize(request: Request):
            query = request.query_params
            if query.get("client_id") != CLIENT_ID or query.get("code_challenge_method") != "S256":
                raise HTTPException(400, "unknown client, or no PKCE challenge")
            hidden = "".join(
                f'<input type="hidden" name="{name}" value="{html.escape(query.get(name, ""))}">'
                for name in ("redirect_uri", "state", "code_challenge")
            )
            return f"""<!doctype html><title>Sign in</title>
                <h1>Sign in to Cognito (test)</h1>
                <form method="post" action="/login">{hidden}
                  <label>Username <input name="username"></label>
                  <button type="submit">Sign in</button>
                </form>"""

        @app.post("/login")
        def login(
            username: str = Form(), redirect_uri: str = Form(), state: str = Form(), code_challenge: str = Form()
        ):
            if username not in self.users:
                return HTMLResponse("<p>Incorrect username or password.</p>", status_code=401)
            code = secrets.token_urlsafe(16)
            self._codes[code] = (username, code_challenge, redirect_uri)
            return RedirectResponse(f"{redirect_uri}?{urlencode({'code': code, 'state': state})}", status_code=302)

        @app.post("/oauth2/token")
        def token(
            grant_type: str = Form(),
            client_id: str = Form(),
            code: str = Form(""),
            redirect_uri: str = Form(""),
            code_verifier: str = Form(""),
            refresh_token: str = Form(""),
        ):
            if client_id != CLIENT_ID:
                raise HTTPException(400, "invalid_client")
            if grant_type == "refresh_token":
                username = self._refresh.get(refresh_token)
                if not username:
                    raise HTTPException(400, "invalid_grant")
                return {
                    "access_token": self.token(username),
                    "id_token": self.token(username, token_use="id"),
                    "token_type": "Bearer",
                    "expires_in": 3600,
                }
            username, challenge, expected_redirect = self._codes.pop(code, ("", "", ""))
            verified = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b"=").decode()
            if not username or verified != challenge or redirect_uri != expected_redirect:
                raise HTTPException(400, "invalid_grant")
            refresh = secrets.token_urlsafe(24)
            self._refresh[refresh] = username
            return {
                "access_token": self.token(username),
                "id_token": self.token(username, token_use="id"),
                "refresh_token": refresh,
                "token_type": "Bearer",
                "expires_in": 3600,
            }

        @app.get("/logout")
        def logout(client_id: str, logout_uri: str):
            if client_id != CLIENT_ID:
                raise HTTPException(400, "invalid_client")
            return RedirectResponse(logout_uri, status_code=302)

        return app

"""Fixtures for the BDD scenarios: the platform the app runs against, the app client and the scenario's students."""

import os
import shlex
import socket
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient

from qubit_notes.app import create_app
from qubit_notes.settings import Settings
from tests.bdd.students import Students
from tests.fakes.fake_cognito import CLIENT_ID, FakeCognito
from tests.fakes.fake_platform import FakePlatform

FRONTEND = Path(__file__).resolve().parents[3] / "frontend"


@pytest.fixture
def on_gogi(request) -> bool:
    return request.config.getoption("--platform") == "gogi"


# the app's own database: in memory, or e.g. Postgres, as deployed, shared by the scenarios
TEST_DATABASE_URL = os.environ.get("QUBIT_NOTES_TEST_DATABASE_URL", "sqlite://")

# where gogi requires keys: the gateway that requires them, and gogi's tool for registering applications
KEYS_GATEWAY = os.environ.get("QUBIT_NOTES_TEST_KEYS_GATEWAY", "localhost:50050")
GOGI_ADMIN = os.environ.get("QUBIT_NOTES_TEST_GOGI_ADMIN", "docker exec gogi-gateway-applications /root/gogi-admin")


class GogiApplications:
    """The applications a scenario registers with gogi, as gogi's operator does; deleted after the scenario."""

    def __init__(self):
        self.suffix = uuid.uuid4().hex[:6]
        self.keys: dict[str, str] = {}

    def name(self, application: str) -> str:
        return f"{application}-{self.suffix}"

    def register(self, application: str) -> str:
        output = self._admin("register", self.name(application))
        self.keys[application] = output.strip().splitlines()[-1]
        return self.keys[application]

    def delete_all(self):
        for application in self.keys:
            self._admin("delete", self.name(application))

    @staticmethod
    def _admin(*args: str) -> str:
        done = subprocess.run([*shlex.split(GOGI_ADMIN), *args], check=True, capture_output=True, text=True)
        return done.stdout


@pytest.fixture
def gogi_applications():
    applications = GogiApplications()
    yield applications
    applications.delete_all()


@pytest.fixture
def platform(request, on_gogi):
    if not on_gogi:
        return FakePlatform()

    from qubit_notes.platform.gogi_adapter import GogiPlatform

    if "gogi_keys" in request.keywords:
        key = request.getfixturevalue("gogi_applications").register("qubit-notes")
        return GogiPlatform(Settings(gateway_url=KEYS_GATEWAY, gogi_api_key=key))
    if "gogi_wrong_key" in request.keywords:
        return GogiPlatform(Settings(gateway_url=KEYS_GATEWAY, gogi_api_key="gogi_" + uuid.uuid4().hex))
    return GogiPlatform(Settings())


@pytest.fixture(scope="session")
def frontend_dir() -> str:
    """The built frontend; built once per run so the UI scenarios test the current code."""
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND, check=True, capture_output=True)
    return str(FRONTEND / "dist")


@contextmanager
def _served(app):
    """the ASGI app served over HTTP on a free port, at its URL"""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.01)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture
def cognito():
    """a stand-in for the app's Cognito user pool and its sign-in pages, for the @cognito scenarios"""
    fake = FakeCognito()
    with _served(fake.app()) as url:
        fake.base_url = url
        yield fake


@pytest.fixture
def app(request, platform):
    # only the UI scenarios need the frontend, and building it takes a moment
    frontend = request.getfixturevalue("frontend_dir") if "ui" in request.keywords else None
    settings = Settings(frontend_dir=frontend, database_url=TEST_DATABASE_URL)
    if "cognito" in request.keywords:
        cognito = request.getfixturevalue("cognito")
        settings = settings.model_copy(
            update={
                "auth": "cognito",
                "cognito_issuer": cognito.issuer,
                "cognito_domain": cognito.base_url,
                "cognito_client_id": CLIENT_ID,
            }
        )
    return create_app(platform=platform, settings=settings)


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def live_url(app):
    """The app served over HTTP, for the browser."""
    with _served(app) as url:
        yield url


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser, live_url):
    context = browser.new_context(base_url=live_url)
    context.set_default_timeout(10_000)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def students(request, client, platform, on_gogi):
    # signed in with Cognito, a student's requests carry their token rather than their name
    token = request.getfixturevalue("cognito").token if "cognito" in request.keywords else None
    students = Students(client, ingest_timeout_seconds=180 if on_gogi else 1, token=token)
    yield students
    # the scenario's courses and conversations would otherwise stay on the gogi platform
    for student_id in students.seen:
        client.app.state.assistant.forget_student(student_id)
        for index in platform.list_member_indexes(student_id):
            if index.owner == student_id:
                platform.delete_index(index.name)


@pytest.fixture
def context() -> dict:
    """What a scenario's steps share, e.g. the last response."""
    return {}

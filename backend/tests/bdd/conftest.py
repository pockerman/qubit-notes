"""Fixtures for the BDD scenarios: the platform the app runs against, the app client and the scenario's students."""

import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient

from study_assistant.app import create_app
from study_assistant.settings import Settings
from tests.bdd.students import Students
from tests.fakes.fake_platform import FakePlatform

FRONTEND = Path(__file__).resolve().parents[3] / "frontend"


@pytest.fixture
def on_gogi(request) -> bool:
    return request.config.getoption("--platform") == "gogi"


@pytest.fixture
def platform(on_gogi):
    if on_gogi:
        from study_assistant.platform.gogi_adapter import GogiPlatform

        return GogiPlatform(Settings())
    return FakePlatform()


@pytest.fixture(scope="session")
def frontend_dir() -> str:
    """The built frontend; built once per run so the UI scenarios test the current code."""
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND, check=True, capture_output=True)
    return str(FRONTEND / "dist")


@pytest.fixture
def app(request, platform):
    # only the UI scenarios need the frontend, and building it takes a moment
    frontend = request.getfixturevalue("frontend_dir") if "ui" in request.keywords else None
    return create_app(platform=platform, settings=Settings(frontend_dir=frontend, database_url="sqlite://"))


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def live_url(app):
    """The app served over HTTP, for the browser."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.01)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


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
def students(client, platform, on_gogi):
    students = Students(client, ingest_timeout_seconds=180 if on_gogi else 1)
    yield students
    # the scenario's courses would otherwise stay on the gogi platform
    for student_id in students.seen:
        for index in platform.list_member_indexes(student_id):
            if index.owner == student_id:
                platform.delete_index(index.name)


@pytest.fixture
def context() -> dict:
    """What a scenario's steps share, e.g. the last response."""
    return {}

"""Fixtures for the BDD scenarios: the platform the app runs against, the app client and the scenario's students."""

import pytest
from fastapi.testclient import TestClient

from study_assistant.app import create_app
from study_assistant.settings import Settings
from tests.bdd.students import Students
from tests.fakes.fake_platform import FakePlatform


@pytest.fixture
def on_gogi(request) -> bool:
    return request.config.getoption("--platform") == "gogi"


@pytest.fixture
def platform(on_gogi):
    if on_gogi:
        from study_assistant.platform.gogi_adapter import GogiPlatform

        return GogiPlatform(Settings())
    return FakePlatform()


@pytest.fixture
def client(platform):
    with TestClient(create_app(platform=platform)) as client:
        yield client


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

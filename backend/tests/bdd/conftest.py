"""Fixtures for the BDD scenarios: the platform the app runs against, the app client and the shared context."""

import pytest
from fastapi.testclient import TestClient

from study_assistant.app import create_app
from study_assistant.settings import Settings
from tests.fakes.fake_platform import FakePlatform


@pytest.fixture
def platform(request):
    if request.config.getoption("--platform") == "gogi":
        from study_assistant.platform.gogi_adapter import GogiPlatform

        return GogiPlatform(gateway_url=Settings().gateway_url)
    return FakePlatform()


@pytest.fixture
def client(platform):
    with TestClient(create_app(platform=platform)) as client:
        yield client


@pytest.fixture
def context() -> dict:
    """What a scenario's steps share, e.g. the last response."""
    return {}

"""The app as an application of gogi: its key, and its own credentials in gogi."""

import io
import uuid

import pytest
from pytest_bdd import given, parsers, then, when

from qubit_notes import cli
from qubit_notes.domain.courses import index_name


@given(parsers.parse('gogi requires keys and the app runs with the key of the application "{application}"'))
def app_has_its_key(platform, gogi_applications, application):
    # the platform fixture registered the application and gave the app its key
    assert application in gogi_applications.keys
    assert platform.health().authenticated


@given("gogi requires keys and the app runs with a key gogi did not give")
def app_has_a_wrong_key():
    # the platform fixture gave the app a key gogi did not give
    pass


@given("the platform does not take the app's key")
def platform_does_not_take_the_key(platform):
    platform.takes_key = False


@then(parsers.parse('another application of gogi does not see the course "{course}" of "{student}"'))
def another_application_does_not_see(gogi_applications, students, course, student):
    from qubit_notes.platform.gogi_adapter import GogiPlatform
    from qubit_notes.settings import Settings
    from tests.bdd.conftest import KEYS_GATEWAY

    other = GogiPlatform(Settings(gateway_url=KEYS_GATEWAY, gogi_api_key=gogi_applications.register("xact-marine")))
    student_id = students.id(student)
    assert other.get_index(index_name(student_id, course)) is None
    assert other.list_member_indexes(student_id) == []


@pytest.fixture
def provider_key() -> str:
    return f"sk-ant-test-{uuid.uuid4().hex}"


@when("the app's Anthropic key is stored")
def store_anthropic_key(platform, provider_key, capsys, context):
    assert cli.main(["store-provider-key", "anthropic"], stdin=io.StringIO(provider_key + "\n"), platform=platform) == 0
    context["output"] = capsys.readouterr().out


@then(parsers.parse('gogi has the credential "{credential}" of "{application}", without showing its value'))
def has_credential(platform, provider_key, context, credential, application):
    assert credential in platform.list_credentials()
    assert provider_key not in context["output"]


@then("it reports that gogi does not take the app's key")
def reports_key_not_taken(context):
    body = context["response"].json()
    assert "does not take the app's key" in (body["error"] or ""), body

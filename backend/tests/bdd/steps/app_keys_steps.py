from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage
from qubit_notes.domain.app_keys import AppKeys
from qubit_notes.platform.named import NamedDocuments
from tests.fakes.fake_platform import FakePlatform

SECRET = "the app's secret, for the scenarios"


def _app_keys(app, platform, settings=None, admins=None) -> AppKeys:
    """the app's keys, as the app starts with them"""
    keys = AppKeys(app.state.database, settings or app.state.app_keys._settings, platform)
    keys.admins = admins if admins is not None else app.state.app_keys.admins
    return keys


@given(parsers.parse('qubit-notes is running without a key for "{provider}"'))
def running_without_key(app, platform, provider):
    platform.needs_keys.add(provider)
    app.state.app_keys = _app_keys(
        app, app.state.platform, app.state.settings.model_copy(update={"secret_key": SECRET})
    )


@given(parsers.parse('"{name}" is an admin of qubit-notes'))
def is_admin(app, students, name):
    app.state.app_keys.admins = {students.id(name)}


@given("qubit-notes has a secret to keep the keys it is given with")
def has_secret(app):
    settings = app.state.app_keys._settings.model_copy(update={"secret_key": SECRET})
    app.state.app_keys = _app_keys(app, app.state.platform, settings)


@given("qubit-notes has no secret")
def has_no_secret(app):
    settings = app.state.app_keys._settings.model_copy(update={"secret_key": None})
    app.state.app_keys = _app_keys(app, app.state.platform, settings)


@then(parsers.parse('it reports the key of "{provider}" as missing'))
def reports_key_missing(context, provider):
    assert provider in context["response"].json()["missing_keys"], context["response"].json()


@then(parsers.re(r"I am told I am (?P<answer>an admin|not an admin)$"))
def told_whether_admin(client, students, answer):
    response = client.get("/api/me", headers=students.headers())
    assert response.status_code == 200, response.text
    assert response.json()["admin"] == (answer == "an admin"), response.json()


@when(parsers.parse('I give the app the key "{key}" for "{provider}"'))
def give_key(client, students, context, key, provider):
    context["response"] = client.put(f"/api/keys/{provider}", headers=students.headers(), json={"key": key})


@given(parsers.parse('I have given the app the key "{key}" for "{provider}"'))
def have_given_key(client, students, key, provider):
    response = client.put(f"/api/keys/{provider}", headers=students.headers(), json={"key": key})
    assert response.status_code == 204, response.text


def _restart(app, platform, **settings):
    """the app starting again with its database: a new platform, needing the same keys, and the keys kept"""
    settings = app.state.app_keys._settings.model_copy(update=settings)
    restarted = FakePlatform()
    restarted.needs_keys = set(platform.needs_keys)
    # the platform takes the keys its settings give
    restarted.keys = {
        p: getattr(settings, f"{p}_api_key") for p in restarted.needs_keys if getattr(settings, f"{p}_api_key")
    }
    app.state.platform = NamedDocuments(restarted)
    app.state.app_keys = _app_keys(app, app.state.platform, settings)
    app.state.app_keys.restore()


@when("qubit-notes restarts")
def restarts(app, platform):
    _restart(app, platform)


@when(parsers.parse('qubit-notes restarts with the key "{key}" for "{provider}" in its settings'))
def restarts_with_key(app, platform, key, provider):
    _restart(app, platform, **{f"{provider}_api_key": key})


@then(parsers.parse('the app uses the key "{key}" for "{provider}"'))
def uses_key(app, key, provider):
    assert app.state.platform.keys.get(provider) == key


@then("when I check its health, no key is missing")
def no_key_missing(client):
    health = client.get("/api/health").json()
    assert health["missing_keys"] == [] and health["status"] == "ok", health


@then(parsers.parse('the key of "{provider}" is still missing'))
def still_missing(client, provider):
    assert provider in client.get("/api/health").json()["missing_keys"]


@then(parsers.parse('the database does not hold "{key}"'))
def database_does_not_hold(app, key):
    with app.state.database.connect() as connection:
        rows = connection.execute(select(storage.app_keys)).all()
    assert rows
    assert not any(key in str(value) for row in rows for value in row)


@then(parsers.parse('nothing the app answers holds "{key}"'))
def nothing_answered_holds(client, students, context, key):
    answers = [context["response"], client.get("/api/me", headers=students.headers()), client.get("/api/health")]
    for answer in answers:
        assert key not in answer.text, answer.text


@then("I am not allowed to do that")
def not_allowed_to_me(context):
    assert context["response"].status_code == 403, context["response"].text


@then("I am told to set QUBIT_NOTES_SECRET_KEY first")
def told_to_set_secret(context):
    response = context["response"]
    assert response.status_code == 409, response.text
    assert "QUBIT_NOTES_SECRET_KEY" in response.json()["detail"]


@then(parsers.parse('I am told the app has no provider "{provider}"'))
def told_no_provider(context, provider):
    response = context["response"]
    assert response.status_code == 404, response.text
    assert f"no provider {provider!r}" in response.json()["detail"]

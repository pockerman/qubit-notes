from pytest_bdd import given, parsers, then, when
from sqlalchemy import delete

from qubit_notes import storage
from qubit_notes.domain.ai_model import AIModel
from qubit_notes.platform.named import NamedDocuments
from tests.fakes.fake_platform import FakePlatform


def _fresh(app, platform):
    """the app as its admins found it, before they chose a model: the scenarios may share a database"""
    with app.state.database.begin() as connection:
        connection.execute(delete(storage.app_settings))
    # the provider it starts with, as the platform is started with the settings
    platform.ai_model = None


def _start(app, platform=None, **settings):
    """the app starting with these settings, and its database, so with the model the admins chose"""
    app.state.settings = app.state.settings.model_copy(update=settings)
    if platform is not None:
        app.state.platform = NamedDocuments(platform)
    app.state.ai_model = AIModel(app.state.database, app.state.settings, app.state.platform)
    app.state.ai_model.restore()


@given(parsers.re(r'qubit-notes is running with the model provider "(?P<provider>[^"]+)", and no model set$'))
def running_with_provider(app, platform, provider):
    _fresh(app, platform)
    _start(app, llm_provider=provider, llm_model=None)


@given(
    parsers.re(
        r'qubit-notes is running with the model provider "(?P<provider>[^"]+)", and the model "(?P<model>[^"]+)"$'
    )
)
def running_with_model(app, platform, provider, model):
    _fresh(app, platform)
    _start(app, llm_provider=provider, llm_model=model)


@given(parsers.re(r'qubit-notes has the key "(?P<key>[^"]+)" for "(?P<provider>[^"]+)" in its settings$'))
def has_key_in_settings(app, platform, key, provider):
    app.state.settings = app.state.settings.model_copy(update={f"{provider}_api_key": key})
    platform.keys[provider] = key
    app.state.ai_model = AIModel(app.state.database, app.state.settings, app.state.platform)


@when(parsers.re(r"I ask which model the AI uses$"))
def ask_model(client, students, context):
    context["response"] = client.get("/api/ai-model", headers=students.headers())
    assert context["response"].status_code == 200, context["response"].text


@then(parsers.re(r'I am told it is "(?P<model>[^"]+)" of "(?P<provider>[^"]+)"$'))
def told_model(context, model, provider):
    answer = context["response"].json()
    assert (answer["provider"], answer["model"]) == (provider, model), answer


@then("I am told the models suggested are:")
def told_suggested(context, datatable):
    _, *rows = datatable
    suggested = context["response"].json()["suggested"]
    assert suggested == {provider: [m.strip() for m in models.split(",")] for provider, models in rows}


def _choose(client, students, provider: str, model: str | None):
    return client.put("/api/ai-model", headers=students.headers(), json={"provider": provider, "model": model})


@when(parsers.re(r'I choose the model "(?P<model>[^"]+)" of "(?P<provider>[^"]+)"$'))
def choose_model(client, students, context, model, provider):
    context["response"] = _choose(client, students, provider, model)


@given(parsers.re(r'I have chosen the model "(?P<model>[^"]+)" of "(?P<provider>[^"]+)"$'))
def have_chosen_model(client, students, model, provider):
    response = _choose(client, students, provider, model)
    assert response.status_code == 200, response.text


@when(parsers.re(r'I choose "(?P<provider>[^"]+)", without a model$'))
def choose_provider(client, students, context, provider):
    context["response"] = _choose(client, students, provider, None)


@when(parsers.re(r'qubit-notes restarts with the model "(?P<model>[^"]+)" of "(?P<provider>[^"]+)" in its settings$'))
def restarts_with_model(app, model, provider):
    _start(app, FakePlatform(), llm_provider=provider, llm_model=model)


@then(parsers.re(r'the AI uses "(?P<model>[^"]+)" of "(?P<provider>[^"]+)"$'))
def ai_uses(app, client, students, model, provider):
    assert app.state.platform.ai_model == (provider, model), app.state.platform.ai_model
    answer = client.get("/api/ai-model", headers=students.headers()).json()
    assert (answer["provider"], answer["model"]) == (provider, model), answer


@then(parsers.re(r'when I check its health, it reports the key of "(?P<provider>[^"]+)" as missing$'))
def health_reports_missing(client, provider):
    health = client.get("/api/health").json()
    assert provider in health["missing_keys"], health


@then(parsers.re(r'I am told the app has the key of "(?P<has>[^"]+)", but not of "(?P<hasnt>[^"]+)"$'))
def told_keys(context, has, hasnt):
    keys = context["response"].json()["keys"]
    assert keys[has] is True and keys[hasnt] is False, keys


@then(
    parsers.re(r'I am told the app\'s settings give the key of "(?P<given>[^"]+)", but not of "(?P<not_given>[^"]+)"$')
)
def told_keys_in_settings(context, given, not_given):
    in_settings = context["response"].json()["in_settings"]
    assert in_settings[given] is True and in_settings[not_given] is False, in_settings


@then("I am told the app's AI is Anthropic's or OpenAI's")
def told_providers(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "Anthropic's or OpenAI's" in response.json()["detail"]

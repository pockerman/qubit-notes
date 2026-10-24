"""The app on its own: its platform's parts, its embedding models, and what a restart keeps."""

from pytest_bdd import given, parsers, then, when

from qubit_notes import cli
from qubit_notes.platform.standalone.ai import ProviderAI


@given("qubit-notes is running on its own")
def running_on_its_own(platform, client):
    assert platform.health().services.keys() == {"database", "files", "embeddings", "ai"}


@given("qubit-notes is running on its own, without a key for its model provider")
def running_without_a_key(platform, client):
    settings = platform.settings.model_copy(update={"llm_provider": "anthropic", "anthropic_api_key": None})
    platform.restart(ai=ProviderAI(settings))


@given(parsers.parse('qubit-notes is running on its own, embedding material with "{model}"'))
def running_with_model(platform, client, model):
    platform.restart(embedding_model=model)


@given("the app stops before it has processed what is uploaded")
def app_stops(platform):
    platform.current.stop()


@when("the app is restarted")
def restarted(platform):
    platform.restart()


@when(parsers.parse('the app is restarted, embedding material with "{model}"'))
def restarted_with_model(platform, model):
    platform.restart(embedding_model=model)


@when("the material is embedded again")
def embedded_again(platform, capsys):
    assert cli.main(["reembed"], platform=platform) == 0
    capsys.readouterr()


def _course_id(students, course: str) -> str:
    return next(c["id"] for c in students.courses() if c["name"] == course)


@when(parsers.parse('the course "{course}" is searched for "{query}"'))
def searched(platform, students, context, course, query):
    context["found"] = platform.search(_course_id(students, course), query, top_k=5)


@then(parsers.parse('the first passage found is from the section "{title}" of "{filename}"'))
def first_from_section(context, title, filename):
    first = context["found"][0]
    assert (first.metadata["filename"], first.metadata["section_title"]) == (filename, title), context["found"]


@then(parsers.parse('the first passage found is from "{filename}"'))
def first_from(context, filename):
    assert context["found"][0].metadata["filename"] == filename, context["found"]


@then("no passage is found")
def none_found(context):
    assert context["found"] == []


@then(parsers.parse('the course "{course}" is searched for "{query}" with "{filename}" first'))
def searched_first(platform, students, context, course, query, filename):
    found = platform.search(_course_id(students, course), query, top_k=5)
    assert found and found[0].metadata["filename"] == filename, found


@then(parsers.parse('I can download "{filename}" as it was uploaded'))
def download_as_uploaded(students, context, filename):
    response = students.download(students.find_material(filename))
    assert response.status_code == 200, response.text
    assert response.content == context["uploaded"][filename]


@then(parsers.re(r'it reports (?P<services>"[^"]+"(?:, "[^"]+")* and "[^"]+") as serving'))
def services_serving(context, services):
    names = [name.strip(' "') for name in services.replace(" and ", ", ").split(",")]
    reported = context["response"].json()["services"]
    assert all(reported[name] == "SERVING" for name in names), reported


@then("nothing it reports names a setting")
def names_no_setting(context):
    assert "QUBIT_NOTES_" not in context["response"].text, context["response"].text


@then("the app says to set QUBIT_NOTES_ANTHROPIC_API_KEY instead")
def says_set_key(context):
    assert context["code"] == 1
    assert "QUBIT_NOTES_ANTHROPIC_API_KEY" in context["error"]
    assert not context["output"]

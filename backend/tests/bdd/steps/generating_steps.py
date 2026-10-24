"""Steps of generating.feature: new material the AI writes from materials the student chooses."""

import re

from pytest_bdd import given, parsers, then, when


def _generate(
    students, context, filenames: str, kind: str | None = None, instructions: str = "", name: str | None = None
):
    documents = [students.find_material(f.strip())["document_id"] for f in filenames.split(",") if f.strip()]
    course_id = students.find_material("fem-notes.md")["course_id"]
    response = students.client.post(
        f"/api/courses/{course_id}/generated",
        headers=students.headers(name),
        json={"documents": documents, "kind": kind, "instructions": instructions},
    )
    context["response"] = response
    if response.status_code == 200:
        # what was generated before, to tell a new generation from it
        context["previous generated"] = context.get("generated")
        context["generated"] = response.json()
    return response


# regular expressions, as the names in quotes may be empty and are followed by more in quotes
@when(parsers.re(r'I generate "(?P<kind>[^"]+)" from "(?P<filenames>[^"]*)"$'))
def generate(students, context, kind, filenames):
    _generate(students, context, filenames, kind)


@given(parsers.re(r'I have generated "(?P<kind>[^"]+)" from "(?P<filenames>[^"]*)"$'))
def have_generated(students, context, kind, filenames):
    assert _generate(students, context, filenames, kind).status_code == 200


@when(parsers.re(r'I generate from "(?P<filenames>[^"]*)" with the instructions "(?P<instructions>[^"]*)"$'))
def generate_with_instructions(students, context, filenames, instructions):
    _generate(students, context, filenames, None, instructions)


@when(
    parsers.re(
        r'I generate "(?P<kind>[^"]+)" from "(?P<filenames>[^"]*)" with the instructions "(?P<instructions>[^"]*)"$'
    )
)
def generate_kind_with_instructions(students, context, kind, filenames, instructions):
    _generate(students, context, filenames, kind, instructions)


@when(parsers.re(r'the student "(?P<name>[^"]+)" generates "(?P<kind>[^"]+)" from "(?P<filenames>[^"]*)"$'))
def student_generates(students, context, name, kind, filenames):
    _generate(students, context, filenames, kind, name=name)


@then(parsers.parse('I am given Markdown named "{name}"'))
def given_markdown_named(context, name):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.json()["name"] == name


@then(parsers.parse('it is drawn from the sections "{titles}"'))
def drawn_from(context, titles):
    text = context["generated"]["text"]
    drawn = re.findall(r"^- From [^›]+› (.+?) \[\[", text, re.MULTILINE)
    assert drawn == [title.strip() for title in titles.split(",")], text


@then(parsers.parse('its text refers to "{reference}"'))
def text_refers_to(context, reference):
    assert reference in context["generated"]["text"], context["generated"]["text"]


@then(parsers.re(r'the AI was asked for (?P<asked>[^"].*)$'))
def asked_for_kind(platform, asked):
    assert f"Write {asked}." in platform.completions[-1]


@then(parsers.parse('the AI was asked for "{instructions}"'))
def asked_for_instructions(platform, instructions):
    assert f"The student asks: {instructions}" in platform.completions[-1]


@then("I am given Markdown unlike the last")
def unlike_the_last(context):
    assert context["previous generated"] is not None
    assert context["generated"]["text"] != context["previous generated"]["text"]


@when(parsers.parse('I write the material "{name}" in "{location}" with the generated text'))
def write_generated(students, context, name, location):
    from tests.bdd.steps.writing_steps import _write

    _write(students, context, name, location, context["generated"]["text"])


def _told(context, status: int, words: str) -> None:
    response = context["response"]
    assert response.status_code == status, response.text
    assert words in response.json()["detail"], response.json()["detail"]


@then("I am told to choose at least one material")
def told_choose_material(context):
    _told(context, 422, "choose at least one material")


@then("I am told to choose a kind or write instructions")
def told_choose_kind(context):
    _told(context, 422, "choose a kind of material, or write instructions")


@then(parsers.parse('I am told "{filename}" is a video, with no text to generate from'))
def told_video(context, filename):
    _told(context, 422, f"{filename!r} is a video, with no text to generate from")


@then(parsers.parse('I am told "{filename}" is not ready yet'))
def told_not_ready(context, filename):
    _told(context, 409, f"{filename!r} is not ready yet")


@given(parsers.parse("the most material generated from at once is {characters:d} characters"))
def generation_limit(client, characters):
    client.app.state.generator.max_characters = characters


@then("I am told the material chosen is too long, and to choose less")
def told_too_long(context):
    _told(context, 422, "too long to generate from at once: choose less")

"""Steps of material_audio.feature and ui_material_audio.feature: the audio of a material, read aloud by a stand-in
for OpenAI's speech model."""

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage
from qubit_notes.domain.audio import MAX_SPEECH_CHARACTERS

MP3 = b"\xff\xfb"


def _ai(platform):
    return platform.ai


def _url(students, filename: str, name=None) -> str:
    material = students.find_material(filename)
    return f"/api/courses/{material['course_id']}/materials/{material['document_id']}/audio"


def _ask(students, context, filename: str, instructions: str = "", name=None, model=None) -> None:
    asked = {"instructions": instructions, **({"model": model} if model else {})}
    context["response"] = students.client.post(_url(students, filename), json=asked, headers=students.headers(name))


def _get(students, filename: str, name=None):
    response = students.client.get(_url(students, filename), headers=students.headers(name))
    assert response.status_code == 200, response.text
    return response.json()


def _made(students, filename: str, name=None) -> dict:
    """the audio, once it is no longer generating"""
    deadline = time.monotonic() + 10
    while (audio := _get(students, filename, name)) and audio["status"] == "generating":
        assert time.monotonic() < deadline, "the audio is still generating"
        time.sleep(0.05)
    return audio


def _refused(context, status: int, words: str) -> None:
    assert context["response"].status_code == status, context["response"].text
    assert words in context["response"].json()["detail"], context["response"].json()


def _files(app) -> list[Path]:
    return sorted((Path(app.state.settings.files_dir) / "audio").glob("*.mp3"))


class Inline:
    """makes the audio there and then: one in-memory database, shared by threads, loses what another thread writes"""

    def submit(self, fn, *args) -> Future:
        future: Future = Future()
        future.set_result(fn(*args))
        return future


@given("the app can speak with OpenAI")
def can_speak(app, platform):
    _ai(platform).speaks = True
    if storage.in_memory(app.state.settings.database_url):
        app.state.audios._executor = Inline()


@given("the app can't speak, having no OpenAI key")
def cannot_speak(platform):
    _ai(platform).speaks = False


@given("OpenAI fails to speak")
def fails_to_speak(platform):
    _ai(platform).speaking_fails = True


@given("the app is slow to speak")
def slow_to_speak(request, app, platform):
    let = threading.Event()
    _ai(platform).slow_to_speak = let
    # in the background, as it is waited for
    app.state.audios._executor = ThreadPoolExecutor(max_workers=1)
    request.addfinalizer(let.set)


@given(parsers.parse('"{filename}" in "{location}" has {count:d} sections'))
def long_material(students, filename, location, count):
    text = "\n\n".join(
        f"# {n} Part {n}\n" + " ".join(f"Sentence {i} of part {n} says something to listen to." for i in range(5))
        for n in range(1, count + 1)
    )
    students.wait_until_ingested(students.upload(location, filename, text.encode()))


@when(parsers.parse('I ask for the audio of "{filename}" read by "{model}", with the instructions "{instructions}"'))
def ask_with_model_and_instructions(students, context, filename, model, instructions):
    _ask(students, context, filename, instructions, model=model)


@when(parsers.parse('I ask for the audio of "{filename}" read by "{model}"'))
def ask_with_model(students, context, filename, model):
    _ask(students, context, filename, model=model)


@when(parsers.parse('I ask for the audio of "{filename}" with the instructions "{instructions}"'))
def ask_with_instructions(students, context, filename, instructions):
    _ask(students, context, filename, instructions)


@when(parsers.parse('I ask for the audio of "{filename}"'))
@given(parsers.parse('I have asked for the audio of "{filename}"'))
def ask_for_audio(students, context, filename):
    _ask(students, context, filename)


@when(parsers.parse('the student "{name}" asks for the audio of "{filename}"'))
def they_ask(students, context, name, filename):
    _ask(students, context, filename, name=name)


@given(parsers.parse('I have the audio of "{filename}"'))
def have_audio(students, context, filename):
    _ask(students, context, filename)
    assert context["response"].status_code == 202, context["response"].text
    audio = _made(students, filename)
    assert audio["status"] == "ready", audio
    context["narration"] = audio["narration"]


@when(parsers.parse('I delete the audio of "{filename}"'))
def delete_audio(students, context, filename):
    context["response"] = students.client.delete(_url(students, filename), headers=students.headers())
    assert context["response"].status_code == 204, context["response"].text


@when(parsers.parse('I suggest "{suggestions}" for the audio of "{filename}"'))
def suggest(students, context, suggestions, filename):
    context["suggestions"] = suggestions
    context["response"] = students.client.post(
        f"{_url(students, filename)}/improvements", json={"suggestions": suggestions}, headers=students.headers()
    )


@when(parsers.parse('I suggest "{suggestions}" for the audio of "{filename}", read by "{model}"'))
def suggest_with_model(students, context, suggestions, filename, model):
    context["response"] = students.client.post(
        f"{_url(students, filename)}/improvements",
        json={"suggestions": suggestions, "model": model},
        headers=students.headers(),
    )


@when("I ask which speech models there are")
def ask_speech_models(students, context):
    context["response"] = students.client.get("/api/speech-models", headers=students.headers())


@then(parsers.parse('I am told the speech models are "{models}"'))
def told_speech_models(context, models):
    assert context["response"].status_code == 200, context["response"].text
    assert [m["id"] for m in context["response"].json()["models"]] == [m.strip() for m in models.split(",")]


@then(parsers.parse('I am told the app\'s own is "{model}"'))
def told_own_model(context, model):
    assert context["response"].json()["default"] == model


@then("I am told the app can speak")
def told_can_speak(context):
    assert context["response"].json()["available"] is True


@then(parsers.parse('it was read aloud by "{model}"'))
def read_by(platform, model):
    spoken = _ai(platform).spoken
    assert spoken and all(used == model for _, _, used in spoken), spoken


@then(parsers.parse('the audio of "{filename}" was read by "{model}"'))
def audio_read_by(students, filename, model):
    assert _get(students, filename)["model"] == model


@then("it was read aloud with no instructions on how to speak it")
def read_without_instructions(platform):
    spoken = _ai(platform).spoken
    assert spoken and all(how == "" for _, how, _ in spoken), spoken


@then("I am told to choose one of the speech models")
def told_choose_model(context):
    _refused(context, 422, "choose one of the speech models")


@then(parsers.parse('"{filename}" has no audio of mine'))
def no_audio_of_mine(students, filename):
    assert _get(students, filename) is None


@then(parsers.parse('"{filename}" has no audio of "{name}"'))
def no_audio_of_theirs(students, filename, name):
    assert _get(students, filename, name) is None


@then(parsers.parse('"{name}" can\'t listen to mine'))
def cannot_listen(students, context, name):
    response = students.client.get(f"{_url(students, 'fem-notes.md')}/file", headers=students.headers(name))
    assert response.status_code == 404, response.text


@then(parsers.parse('the audio of "{filename}" is generating'))
def is_generating(context, filename):
    assert context["response"].status_code == 202, context["response"].text
    assert context["response"].json()["status"] == "generating"


@then(parsers.parse('once it is made, the audio of "{filename}" is ready'))
def made_ready(students, context, filename):
    audio = _made(students, filename)
    assert audio["status"] == "ready", audio
    context["audio"], context["filename"] = audio, filename


@then(parsers.parse('once it is made, the audio of "{filename}" of "{name}" is ready'))
def their_made_ready(students, filename, name):
    assert _made(students, filename, name)["status"] == "ready"


@then(parsers.parse('once it is made, the audio of "{filename}" has failed, saying why'))
def made_failed(students, filename):
    audio = _made(students, filename)
    assert audio["status"] == "failed", audio
    assert "OpenAI couldn't read it aloud" in audio["error"], audio


@then(parsers.parse('its narration is of "{first}" and "{second}"'))
def narration_of(context, first, second):
    assert first in context["audio"]["narration"] and second in context["audio"]["narration"], context["audio"]


@then("I can listen to it as MP3")
def listen(students, context):
    response = students.client.get(f"{_url(students, context['filename'])}/file", headers=students.headers())
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content.startswith(MP3)
    context["mp3"] = response.content


@then("the narration was read aloud by OpenAI")
def read_aloud(platform, context):
    spoken = "\n\n".join(text for text, _, _ in _ai(platform).spoken)
    assert spoken == context["audio"]["narration"]


@then(parsers.parse('the AI was told to write it "{instructions}"'))
def told_to_write(platform, instructions):
    assert any(f"The student's instructions: {instructions}" in prompt for prompt in _ai(platform).completions)


@then("it was read aloud as the AI said to speak it")
def spoken_as_said(platform):
    spoken = _ai(platform).spoken
    assert spoken and all(how.startswith("Speak as told: ") for _, how, _ in spoken), spoken


@then(parsers.parse('the audio of "{filename}" has the instructions "{instructions}"'))
def has_instructions(students, filename, instructions):
    assert _get(students, filename)["instructions"] == instructions


@then("its narration was read aloud in more than one part, each short enough for OpenAI")
def in_parts(platform):
    spoken = _ai(platform).spoken
    assert len(spoken) > 1
    assert all(len(text) <= MAX_SPEECH_CHARACTERS for text, _, _ in spoken)


@then(parsers.parse('my AI usage has "{purpose}"'))
def usage_has(students, purpose):
    response = students.client.get("/api/usage", headers=students.headers())
    assert purpose in [spent["purpose"] for spent in response.json()["purposes"]], response.json()


@then("its file is deleted")
def file_deleted(app):
    assert _files(app) == []


@then(parsers.parse('I am told to delete or improve the audio of "{filename}" first'))
def told_delete_or_improve(context, filename):
    _refused(context, 409, "delete it, or improve it, first")


@then(parsers.parse('the AI was given its earlier narration and "{suggestions}"'))
def given_earlier(platform, context, suggestions):
    prompt = _ai(platform).completions[-1]
    assert context["narration"] in prompt
    assert f"The student's suggestions to improve it: {suggestions}" in prompt


@then("it is a new narration")
def new_narration(context):
    assert context["audio"]["narration"] != context["narration"]


@then("the earlier audio's file is deleted")
def earlier_deleted(app, context):
    files = _files(app)
    assert len(files) == 1
    assert files[0].read_bytes() == MP3 + b"\x90\x00" + context["audio"]["narration"].encode()


@then(parsers.parse('I am told there is no audio of "{filename}" to improve'))
def told_none_to_improve(context, filename):
    _refused(context, 404, "no audio to improve")


@then(parsers.parse('I am told the audio of "{filename}" is being made'))
def told_being_made(context, filename):
    _refused(context, 409, "being made")


@then("I am told audio needs the app's OpenAI key")
def told_needs_key(context):
    _refused(context, 503, "audio needs the app's OpenAI key")


@then("I am told only text has audio")
def told_only_text(context):
    _refused(context, 422, "only text has audio")


@then("the audio is refused, the course not being shared with them")
def refused_not_shared(context):
    _refused(context, 403, "is not shared with you")


@then("no audio is kept")
def none_kept(app):
    with app.state.database.connect() as connection:
        assert connection.execute(select(storage.material_audio)).all() == []
    assert _files(app) == []


# in the browser


def _panel(page):
    return page.get_by_role("complementary", name="Audio")


@when("I open the audio")
def open_audio(page):
    page.get_by_role("group", name="Material actions").get_by_role("button", name="Audio", exact=True).click()
    expect(_panel(page)).to_be_visible()


@then("I am offered to make the audio")
def offered_to_make(page):
    expect(_panel(page).get_by_role("button", name="Make audio")).to_be_visible()


@when("I make the audio")
def make_audio_as_it_comes(page):
    make_audio(page, "")


@when(parsers.parse('I make the audio with the instructions "{instructions}"'))
def make_audio(page, instructions):
    panel = _panel(page)
    panel.get_by_role("textbox", name="Instructions").fill(instructions)
    panel.get_by_role("button", name="Make audio").click()
    expect(panel.get_by_role("button", name="Delete audio")).to_be_visible()


@when(parsers.parse('I improve the audio with "{suggestions}"'))
def improve_audio(page, suggestions):
    panel = _panel(page)
    panel.get_by_role("button", name="Improve", exact=True).click()
    panel.get_by_role("textbox", name="Suggestions").fill(suggestions)
    panel.get_by_role("button", name="Make it again").click()
    expect(panel.get_by_role("button", name="Delete audio")).to_be_visible()


@when("I delete the audio")
def delete_in_browser(page):
    _panel(page).get_by_role("button", name="Delete audio").click()


@then("I see the audio is ready to play")
def ready_to_play(page):
    panel = _panel(page)
    expect(panel.get_by_label("Audio player")).to_be_visible()
    expect(panel.get_by_role("link", name="Download MP3")).to_be_visible()


@then(parsers.parse('I see its narration has "{text}"'))
def narration_has(page, text):
    panel = _panel(page)
    panel.get_by_text("Narration", exact=True).click()
    expect(panel.get_by_role("group", name="Narration")).to_contain_text(text)


@then(parsers.parse('I see the instructions "{instructions}"'))
def see_instructions(page, instructions):
    expect(_panel(page).get_by_label("Made with")).to_contain_text(instructions)


@then(parsers.parse('I see the suggestions "{suggestions}"'))
def see_suggestions(page, suggestions):
    expect(_panel(page).get_by_label("Made with")).to_contain_text(suggestions)


def _models(page):
    return _panel(page).get_by_role("radiogroup", name="Speech model")


@then(parsers.parse('I can choose the speech model from "{names}"'))
def can_choose_models(page, names):
    radios = _models(page).get_by_role("radio")
    wanted = [name.strip() for name in names.split(", ")]
    expect(radios).to_have_count(len(wanted))
    for name in wanted:
        expect(_models(page).get_by_role("radio", name=name, exact=True)).to_be_visible()


@then(parsers.parse('"{name}" is chosen'))
def model_chosen(page, name):
    expect(_models(page).get_by_role("radio", name=name, exact=True)).to_be_checked()


@when(parsers.parse('I choose the speech model "{name}"'))
def choose_model(page, name):
    _models(page).get_by_role("radio", name=name, exact=True).check()


@then(parsers.parse('I see it was read by "{name}"'))
def see_read_by(page, name):
    expect(_panel(page).get_by_label("Made with")).to_contain_text(name)

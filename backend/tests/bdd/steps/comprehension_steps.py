"""Steps of comprehension.feature, transcription.feature and ui_comprehension.feature: checking a student's
understanding, with a stand-in for the AI, and answering by voice, with a stand-in for OpenAI's transcription."""

import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage
from qubit_notes.domain.comprehension import MAX_QUESTIONS
from tests.bdd.steps.study_steps import _document_scope, _section_scope, _topic_scope
from tests.fakes.fake_ai import SAID

URL = "/api/comprehension-checks"


def _ai(platform):
    return platform.ai


def _subject_scope(students, location: str) -> dict:
    course, subject = location.split("/")
    course_id = next(c["id"] for c in students.courses() if c["name"] == course)
    return {"course_id": course_id, "subject": subject}


def _start(students, context, scope: dict, name=None) -> None:
    context["scope"] = scope
    context["response"] = students.client.post(URL, json=scope, headers=students.headers(name))
    if context["response"].status_code == 201:
        context["check"] = context["response"].json()


def _check(context) -> dict:
    assert context["response"].status_code in (200, 201), context["response"].text
    return context["response"].json()


def _refused(context, status: int, words: str) -> None:
    assert context["response"].status_code == status, context["response"].text
    assert words in context["response"].json()["detail"], context["response"].json()


def _waiting(check: dict) -> dict | None:
    last = check["exchanges"][-1] if check["exchanges"] else None
    return last if last and last["answer"] is None else None


def _answer(students, context, answer: str, spoken: bool = False) -> None:
    context["response"] = students.client.post(
        f"{URL}/{context['check']['id']}/answers", json={"answer": answer, "spoken": spoken}, headers=students.headers()
    )
    if context["response"].status_code == 200:
        context["check"] = context["response"].json()


def _end(students, context) -> None:
    context["response"] = students.client.post(f"{URL}/{context['check']['id']}/end", headers=students.headers())
    if context["response"].status_code == 200:
        context["check"] = context["response"].json()


def _list(students, scope: dict, name=None) -> list[dict]:
    response = students.client.get(URL, params=scope, headers=students.headers(name))
    assert response.status_code == 200, response.text
    return response.json()


def _prompt(platform) -> str:
    return _ai(platform).completions[-1]


def _given_material(platform) -> set[str]:
    """the materials the AI was given, by filename, in its last prompt"""
    return set(re.findall(r"^\[S\d+\] (.+?) › ", _prompt(platform), re.MULTILINE))


# starting a check


@when(parsers.parse('I check my understanding of the section "{title}" of "{filename}"'))
@given(parsers.parse('I am checking my understanding of the section "{title}" of "{filename}"'))
def check_section(students, context, title, filename):
    _start(students, context, _section_scope(students, title, filename))


@when(parsers.parse('I check my understanding of the topic "{location}"'))
def check_topic(students, context, location):
    _start(students, context, _topic_scope(students, location))


@when(parsers.parse('I check my understanding of the subject "{location}"'))
def check_subject(students, context, location):
    _start(students, context, _subject_scope(students, location))


@given(parsers.re(r'I have checked my understanding of "(?P<filename>[^"]+)"(?: again)?$'))
def have_checked(students, context, filename):
    _start(students, context, _document_scope(students, filename))
    _answer(students, context, "I don't know")
    context.setdefault("checks", []).append(context["check"]["id"])


@when(parsers.re(r'I check my understanding of "(?P<filename>[^"]+)"$'))
@given(parsers.re(r'I am checking my understanding of "(?P<filename>[^"]+)"$'))
def check_document(students, context, filename):
    _start(students, context, _document_scope(students, filename))


@when(parsers.parse('the student "{name}" checks their understanding of "{filename}"'))
def they_check(students, context, name, filename):
    _start(students, context, _document_scope(students, filename), name=name)


@then(parsers.re(r"the assistant asks (?:me|them) a question$"))
def asks_a_question(context):
    check = _check(context)
    assert len(check["exchanges"]) == 1, check
    question = _waiting(check)
    assert question and question["question"], check


@then(parsers.parse('the question cites one of the sections "{first}" or "{second}" of "{filename}"'))
def question_cites(context, first, second, filename):
    source = _waiting(_check(context))["source"]
    assert source["filename"] == filename and source["title"] in (first, second), source


@then(parsers.parse('the assistant was given the sections "{first}", "{second}" and "{third}"'))
def given_sections(platform, first, second, third):
    titles = re.findall(r"^\[S\d+\] .+? › (.+)$", _prompt(platform), re.MULTILINE)
    assert titles == [first, second, third], titles


@then(parsers.parse('the assistant was given "{first}" and "{second}"'))
def given_materials(platform, first, second):
    assert {first, second} <= _given_material(platform), _given_material(platform)


@then(parsers.parse('the assistant was not given "{filename}"'))
def not_given(platform, filename):
    assert filename not in _given_material(platform), _given_material(platform)


@then(parsers.parse('I am told "{filename}" is a video, with no text to question me on'))
def told_video(context, filename):
    _refused(context, 422, f"{filename!r} is a video, with no text to question you on")


@then("I am told there is no material to question me on")
def told_no_material(context):
    _refused(context, 404, "there is no material to work from")


# answering


@when(parsers.re(r'I answer "(?P<answer>[^"]+)"$'))
@given(parsers.re(r'I have answered "(?P<answer>[^"]+)"$'))
def answer(students, context, answer):
    _answer(students, context, answer)


@when(parsers.parse('I answer "{answer}", having said it'))
def answer_spoken(students, context, answer):
    _answer(students, context, answer, spoken=True)


@when("I answer nothing")
def answer_nothing(students, context):
    _answer(students, context, "   ")


@when(parsers.parse("I answer {count:d} questions"))
def answer_many(students, context, count):
    for i in range(count):
        _answer(students, context, f"Answer {i + 1}")
        assert context["response"].status_code == 200, context["response"].text


@then(parsers.parse('the assistant says I understood it "{understood}", citing the material'))
def assessed(context, understood):
    answered = [e for e in _check(context)["exchanges"] if e["answer"] is not None][-1]
    assert answered["understood"] == understood, answered
    assert answered["feedback"] and answered["cited"], answered
    assert answered["cited"][0]["filename"] == "fem-notes.md", answered


@then("the assistant asks me the next question")
def next_question(context):
    check = _check(context)
    assert len(check["exchanges"]) == 2, check
    assert _waiting(check)["question"], check


@then(parsers.parse('the assistant was given my earlier answer "{answer}"'))
def given_earlier(platform, answer):
    prompt = _prompt(platform)
    assert f"The student answered: {answer}" in prompt, prompt
    assert re.search(r"^Understood: (yes|partly|no)\. ", prompt, re.MULTILINE), prompt


@then("my answer is kept as spoken")
def kept_spoken(platform, context):
    answered = _check(context)["exchanges"][0]
    assert answered["spoken"] is True, answered
    assert "The student's answer (spoken, transcribed): " in _prompt(platform)


@then("I am told to answer the question")
def told_to_answer(context):
    _refused(context, 422, "answer the question")


@then("the assistant asks me no more questions")
def no_more_questions(context):
    check = _check(context)
    assert len(check["exchanges"]) == MAX_QUESTIONS, len(check["exchanges"])
    assert _waiting(check) is None, check["exchanges"][-1]


@then("I am told to end the check when I answer again")
def told_to_end(students, context):
    _answer(students, context, "One more")
    _refused(context, 409, "end it for its verdict")


# ending


@when("I end the check")
@given("I have ended the check")
def end(students, context):
    _end(students, context)


@then("I get a verdict with a summary, what I understood and the sections to study again")
def verdict(context):
    verdict = _check(context)["verdict"]
    assert verdict and verdict["summary"], verdict
    assert verdict["understood"], verdict
    assert verdict["to_study"] and verdict["to_study"][0]["filename"] == "fem-notes.md", verdict


@then("the check is ended")
def is_ended(context):
    check = _check(context)
    assert check["ended_at"], check
    # the question asked last, not answered, isn't part of it
    assert all(e["answer"] is not None for e in check["exchanges"]), check


@then("I am told the check is ended")
def told_ended(context):
    _refused(context, 409, "the check is ended")


@then("I am told to answer at least one question first")
def told_answer_first(context):
    _refused(context, 422, "answer at least one question first")


# kept


@when("I open the check again")
def open_again(students, context):
    context["response"] = students.client.get(f"{URL}/{context['check']['id']}", headers=students.headers())


@then(parsers.parse('it has my answer "{answer}" and the question after it'))
def has_answer(context, answer):
    check = _check(context)
    assert check["exchanges"][0]["answer"] == answer, check
    assert _waiting(check) is check["exchanges"][1] or _waiting(check) == check["exchanges"][1], check


@when(parsers.parse('I list my checks of "{filename}"'))
def list_checks(students, context, filename):
    context["listed"] = _list(students, _document_scope(students, filename))


@then(parsers.parse("I see {count:d} checks, the newest first"))
def see_checks(context, count):
    assert [c["id"] for c in context["listed"]] == list(reversed(context["checks"]))[:count]
    assert len(context["listed"]) == count


@when("I delete the check")
def delete_check(students, context):
    context["response"] = students.client.delete(f"{URL}/{context['check']['id']}", headers=students.headers())
    assert context["response"].status_code == 204, context["response"].text


@then(parsers.parse('I have no checks of "{filename}"'))
def no_checks(students, filename):
    assert _list(students, _document_scope(students, filename)) == []


@when(parsers.parse('the student "{name}" opens my check'))
def they_open(students, context, name):
    context["response"] = students.client.get(f"{URL}/{context['check']['id']}", headers=students.headers(name))


@then("the check is not found")
def not_found(context):
    assert context["response"].status_code == 404, context["response"].text


@then(parsers.parse('the student "{name}" has no checks of "{filename}"'))
def they_have_none(students, name, filename):
    assert _list(students, _document_scope(students, filename), name=name) == []


@then("the check is refused, the course not being shared with them")
def refused_not_shared(context):
    _refused(context, 403, "not shared with you")


@then("no check of mine is kept")
def none_kept(client):
    with client.app.state.database.connect() as connection:
        assert connection.execute(select(storage.comprehension_checks)).all() == []


# answering by voice


def _say(students, context, said: bytes, model=None) -> None:
    context["response"] = students.client.post(
        "/api/transcriptions",
        files={"recording": ("answer.webm", said, "audio/webm")},
        data={"model": model} if model else {},
        headers=students.headers(),
    )


@given("the app can hear with OpenAI")
def can_hear(platform):
    _ai(platform).hears = True


@given("the app can't hear, having no OpenAI key")
def cannot_hear(platform):
    _ai(platform).hears = False


@when("I ask which models can hear what I say")
def ask_models(students, context):
    context["response"] = students.client.get("/api/transcription-models", headers=students.headers())
    assert context["response"].status_code == 200, context["response"].text
    context["models"] = context["response"].json()


@then(parsers.parse('I am offered the transcription models "{models}"'))
def offered_models(context, models):
    assert [m["id"] for m in context["models"]["models"]] == models.split(",")
    assert all(m["name"] for m in context["models"]["models"])


@then(parsers.parse('the app\'s own is "{model}"'))
def own_model(context, model):
    assert context["models"]["default"] == model


@then("I am told the app can't hear what I say")
def told_cannot_hear(context):
    assert context["models"]["available"] is False


@when(parsers.re(r'I say "(?P<said>[^"]+)"$'))
def say(students, context, said):
    _say(students, context, SAID + said.encode())


@when(parsers.parse('I say "{said}" to "{model}"'))
def say_to(students, context, said, model):
    _say(students, context, SAID + said.encode(), model)


@when("I say nothing")
def say_nothing(students, context):
    _say(students, context, b"")


@then(parsers.parse('I get the text "{text}"'))
def get_text(context, text):
    assert context["response"].status_code == 200, context["response"].text
    assert context["response"].json()["text"] == text


@then(parsers.parse('it was heard by "{model}"'))
def heard_by(platform, context, model):
    assert context["response"].status_code == 200, context["response"].text
    assert context["response"].json()["model"] == model
    assert _ai(platform).heard[-1] == model


@then(parsers.parse('I am told there is no transcription model "{model}"'))
def no_such_model(context, model):
    _refused(context, 422, f"there is no transcription model {model!r}")


@then("the recording is refused, as the app has no OpenAI key")
def refused_no_key(context):
    _refused(context, 503, "needs the app's OpenAI key")


@then("I am told the recording is empty")
def told_empty(context):
    _refused(context, 422, "the recording is empty")


# in the browser


def _panel(page):
    return page.get_by_role("complementary", name="Comprehension check")


def _exchanges(page):
    return _panel(page).get_by_role("list", name="Questions and answers").get_by_role("listitem")


@when("I open the comprehension check")
def open_panel(page):
    page.get_by_role("button", name="Check understanding").click()
    expect(_panel(page)).to_be_visible()


@when("I close the comprehension check")
def close_panel(page):
    _panel(page).get_by_role("button", name="Close the comprehension check").click()
    expect(_panel(page)).to_have_count(0)


@when(parsers.parse('I start a check of "{what}"'))
def start_in_browser(page, what):
    panel = _panel(page)
    of = panel.get_by_label("Check", exact=True)
    if of.count():
        of.select_option(label=what)
    panel.get_by_role("button", name="Start a check").click()


@then("I see the assistant's question")
def see_question(page):
    expect(_exchanges(page).first.locator(".question")).to_contain_text("Question")
    expect(_exchanges(page).first.locator(".from")).to_contain_text("fem-notes.md")


def _send(page, answer: str | None = None) -> None:
    panel = _panel(page)
    before = panel.locator(".assessment").count()
    if answer is not None:
        panel.get_by_role("textbox", name="Your answer").fill(answer)
    panel.get_by_role("button", name="Send", exact=True).click()
    expect(panel.locator(".assessment")).to_have_count(before + 1)


@when(parsers.parse('I type the answer "{answer}"'))
def type_answer(page, answer):
    _send(page, answer)


@then("I see how well I understood it")
def see_assessment(page):
    expect(_panel(page).locator(".assessment").last).to_contain_text(re.compile(r"Understood|Partly|Not understood"))


@then("I see the assistant's next question")
def see_next(page):
    expect(_exchanges(page)).to_have_count(2)


@when("I end the check in the browser")
def end_in_browser(page):
    _panel(page).get_by_role("button", name="End the check").click()


@then("I see the verdict, with what to study again")
def see_verdict(page):
    verdict = _panel(page).get_by_role("region", name="Verdict")
    expect(verdict).to_contain_text("Verdict")
    expect(verdict.get_by_role("list", name="To study again")).to_contain_text("fem-notes.md")


@when("I record my answer and stop")
def record(page):
    page.context.grant_permissions(["microphone"])
    panel = _panel(page)
    panel.get_by_role("button", name="Record").click()
    stop = panel.get_by_role("button", name="Stop")
    expect(stop).to_be_visible()
    page.wait_for_timeout(500)
    stop.click()


@then(parsers.parse('my answer reads "{text}"'))
def answer_reads(page, text):
    expect(_panel(page).get_by_role("textbox", name="Your answer")).to_have_value(text)


@when("I send my answer")
def send(page):
    _send(page)


@then(parsers.parse("I see {count:d} earlier check"))
def see_earlier(page, count):
    expect(_panel(page).get_by_role("list", name="Earlier checks").get_by_role("listitem")).to_have_count(count)


@when("I take up the earlier check")
def take_up(page):
    _panel(page).get_by_role("list", name="Earlier checks").get_by_role("button", name="Take up").first.click()


@then(parsers.parse('I see my answer "{answer}"'))
def see_answer(page, answer):
    expect(_exchanges(page).first.locator(".answer")).to_have_text(answer)

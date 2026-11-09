"""Steps of rating_answers.feature, and of copying and rating the assistant's replies in the browser
(ui_assistant_replies.feature)."""

from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage
from tests.bdd.steps.assistant_steps import _conversation
from tests.bdd.steps.study_steps import _document_scope
from tests.bdd.steps.ui_steps import _assistant


def _rate(students, context, rating, name=None) -> None:
    response = students.client.put(
        f"/api/assistant/turns/{context['turn']['id']}/rating", headers=students.headers(name), json={"rating": rating}
    )
    context["response"] = response
    if response.status_code == 200:
        context["turn"] = response.json()


def _rated(context) -> dict:
    assert context["response"].status_code == 200, context["response"].text
    return context["response"].json()


def _in_conversation(context, filename: str) -> dict:
    return next(
        turn for turn in _conversation(context["students"], filename)["turns"] if turn["id"] == context["turn"]["id"]
    )


def _kept(client) -> list:
    with client.app.state.database.connect() as connection:
        return connection.execute(select(storage.answer_ratings)).all()


@then("the assistant's reply has no rating")
def no_rating(context):
    assert context["turn"]["rating"] is None


@when(parsers.parse('I rate the assistant\'s reply "{rating}"'))
@given(parsers.parse('I have rated the assistant\'s reply "{rating}"'))
def rate(students, context, rating):
    context["students"] = students
    _rate(students, context, rating)


@when("I take back my rating of the assistant's reply")
def take_back(students, context):
    _rate(students, context, None)


@when(parsers.parse('the student "{name}" rates my assistant\'s reply "{rating}"'))
def they_rate(students, context, name, rating):
    _rate(students, context, rating, name)


@then(parsers.parse('the assistant\'s reply is rated "{rating}"'))
def is_rated(context, rating):
    assert _rated(context)["rating"] == rating


@then(parsers.parse('my conversation with the assistant on "{filename}" shows the reply rated "{rating}"'))
def conversation_shows_rating(students, context, filename, rating):
    context["students"] = students
    assert _in_conversation(context, filename)["rating"] == rating


@then(parsers.parse('my conversation with the assistant on "{filename}" shows the reply with no rating'))
def conversation_shows_no_rating(students, context, filename):
    context["students"] = students
    assert _in_conversation(context, filename)["rating"] is None


@then("the rating is refused as invalid")
def refused_invalid(context):
    assert context["response"].status_code == 422, context["response"].text


@then("the rating is refused as not found")
def refused_not_found(context):
    assert context["response"].status_code == 404, context["response"].text


@then(parsers.parse('my rating "{rating}" of "{question}" is kept'))
def rating_kept(client, students, rating, question):
    kept = [row for row in _kept(client) if students.name(row.student) == students.me]
    assert [(row.rating, row.question) for row in kept] == [(rating, question)], kept


@then("no rating of mine is kept")
def nothing_kept(client):
    assert _kept(client) == []


# in the browser


def _last_turn(page):
    return _assistant(page).get_by_role("list", name="Conversation").locator("li.turn").last


def _thumb(page, which: str):
    return _last_turn(page).get_by_role("button", name=f"Thumbs {which}")


def _copied(page) -> str:
    return page.evaluate("navigator.clipboard.readText()")


def _last_reply(students) -> dict:
    where = _document_scope(students, "fem-notes.md")
    response = students.client.get("/api/assistant/conversation", headers=students.headers(), params=where)
    return response.json()["turns"][-1]


@when("I copy the assistant's reply")
def copy_reply(page):
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    _last_turn(page).get_by_role("button", name="Copy").click()


@then("I am told it was copied")
def told_copied(page):
    expect(_last_turn(page).get_by_role("button", name="Copied")).to_be_visible()


@then("what I copied is the assistant's answer")
def copied_answer(page, students):
    assert _copied(page) == _last_reply(students)["answer"]


@then("what I copied has the quiz's questions and their choices")
def copied_quiz(page, students):
    copied = _copied(page)
    questions = _last_reply(students)["quiz"]["questions"]
    assert questions
    for question in questions:
        assert question["question"] in copied
        for choice in question["choices"]:
            assert choice in copied


@when(parsers.re(r"I give the assistant's reply a thumbs (?P<which>up|down)$"))
def give_thumb(page, which):
    _thumb(page, which).click()


@then(parsers.re(r"the thumbs (?P<which>up|down) of the reply is pressed$"))
def thumb_pressed(page, which):
    expect(_thumb(page, which)).to_have_attribute("aria-pressed", "true")


@then(parsers.re(r"the thumbs (?P<which>up|down) of the reply is not pressed$"))
def thumb_not_pressed(page, which):
    expect(_thumb(page, which)).to_have_attribute("aria-pressed", "false")


@then("neither thumb of the reply is pressed")
def neither_pressed(page):
    thumb_not_pressed(page, "up")
    thumb_not_pressed(page, "down")


@when("I come back to the page later")
def come_back(page):
    page.reload()
    expect(page.get_by_role("heading", level=2)).to_be_visible()

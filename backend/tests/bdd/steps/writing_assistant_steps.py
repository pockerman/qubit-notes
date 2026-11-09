"""Steps of writing_assistant.feature and ui_writing_assistant.feature: the writing assistant, with a stand-in for an
AI that searches the web."""

import re

from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage

LOCATION = "aeronautics/numerical-methods/finite-elements"


def _ai(platform):
    return platform.ai


def _ask(students, context, request: str, location: str = LOCATION, name=None, **asked) -> None:
    course, subject, topic = location.split("/")
    course_id = next(c["id"] for c in students.courses(name=name) if c["name"] == course)
    body = {"request": request, "history": context.get("writing_history", []), **asked}
    context["response"] = students.client.post(
        f"/api/courses/{course_id}/subjects/{subject}/topics/{topic}/writing-assistant",
        json=body,
        headers=students.headers(name),
    )
    if context["response"].status_code == 200:
        context["writing_request"] = request
        context["writing_reply"] = context["response"].json()


def _reply(context) -> dict:
    assert context["response"].status_code == 200, context["response"].text
    return context["response"].json()


def _prompt(platform) -> str:
    return _ai(platform).completions[-1]


@given("the AI can't search the web")
def cannot_search(platform):
    _ai(platform).searches_web = False


@when(parsers.parse('I ask the writing assistant "{request}", not searching the web'))
def ask_without_web(students, context, request):
    _ask(students, context, request, search_web=False)


@when(parsers.parse('I ask the writing assistant "{request}" about the section "{section}" of:'))
def ask_about_section(students, context, request, section, docstring):
    context["draft"] = docstring
    _ask(students, context, request, draft=docstring, section=section)


@when(parsers.parse('I ask the writing assistant "{request}" after that'))
def ask_follow_up(students, context, request):
    context["writing_history"] = [{"request": context["writing_request"], "reply": context["writing_reply"]["reply"]}]
    _ask(students, context, request)


@when(parsers.parse('I ask the writing assistant "{request}" in "{location}"'))
def ask_in(students, context, request, location):
    _ask(students, context, request, location)


@when(parsers.parse('the student "{name}" asks the writing assistant "{request}" in "{location}"'))
def they_ask(students, context, name, request, location):
    _ask(students, context, request, location, name=name)


@when("I ask the writing assistant nothing")
def ask_nothing(students, context):
    _ask(students, context, "  ")


@when(parsers.parse('I ask the writing assistant "{request}"'))
@given(parsers.parse('I have asked the writing assistant "{request}"'))
def ask(students, context, request):
    _ask(students, context, request)


@then("the writing assistant replies in Markdown")
def replies(context):
    assert _reply(context)["reply"].startswith("## Writing ")


@then("it searched the web for it")
def searched(platform, context):
    assert _reply(context)["searched"] is True
    assert _ai(platform).searched[-1] is True


@then("it didn't search the web")
def did_not_search(platform, context):
    assert _reply(context)["searched"] is False
    assert _ai(platform).searched[-1] is False


@then("its reply cites its references by number, each with a title and an address")
def cites_by_number(context):
    reply = _reply(context)
    markers = sorted({int(n) for n in re.findall(r"\[(\d+)\]", reply["reply"])})
    assert markers == list(range(1, len(reply["sources"]) + 1)) and markers, reply
    assert all(source["title"] and source["url"].startswith("https://") for source in reply["sources"]), reply


@then("its reply cites nothing")
def cites_nothing(context):
    reply = _reply(context)
    assert reply["sources"] == [] and not re.search(r"\[\d+\]", reply["reply"]), reply


@then(parsers.parse('it was given the section "{section}" to help with'))
def given_section(platform, context, section):
    assert _reply(context)["section"] == section
    assert (
        f"The section they want help with, {section}:\n\nShape functions interpolate the solution inside each element."
        in _prompt(platform)
    )


@then("it was given what I have written so far")
def given_draft(platform, context):
    assert context["draft"].strip() in _prompt(platform)


@then(parsers.parse('it was told the material is for "{course}" › "{subject}" › "{topic}"'))
def told_where(platform, course, subject, topic):
    assert f"for the course {course}, the subject {subject}, the topic {topic}." in _prompt(platform)


@then("it was given my earlier request and its reply")
def given_earlier(platform, context):
    history = _ai(platform).histories[-1]
    assert [m.role for m in history] == ["user", "assistant"]
    assert history[0].content == "Write an introduction to the finite element method"
    assert history[1].content.startswith("## Writing 1")


@then("the writing assistant is refused, as only owners write material")
def refused_owners(context):
    assert context["response"].status_code == 403, context["response"].text
    assert "only the owners" in context["response"].json()["detail"]


@then("the writing assistant is refused as not found")
def refused_not_found(context):
    assert context["response"].status_code == 404, context["response"].text


@then("I am told to ask the writing assistant something")
def told_to_ask(context):
    assert context["response"].status_code == 422, context["response"].text
    assert context["response"].json()["detail"] == "ask the writing assistant something"


# rating its replies


def _rate(students, context, rating, name=None) -> None:
    context["response"] = students.client.put(
        f"/api/writing-assistant/replies/{context['writing_reply']['id']}/rating",
        json={"rating": rating},
        headers=students.headers(name),
    )


@then("the writing assistant's reply has no rating")
def reply_not_rated(context):
    assert _reply(context)["rating"] is None


@when(parsers.parse('I rate the writing assistant\'s reply "{rating}"'))
@given(parsers.parse('I have rated the writing assistant\'s reply "{rating}"'))
def rate_reply(students, context, rating):
    _rate(students, context, rating)


@when("I take back my rating of the writing assistant's reply")
def take_back_rating(students, context):
    _rate(students, context, None)


@when(parsers.parse('the student "{name}" rates my writing assistant\'s reply "{rating}"'))
def they_rate_reply(students, context, name, rating):
    _rate(students, context, rating, name)


@then(parsers.parse('the writing assistant\'s reply is rated "{rating}"'))
def reply_rated(context, rating):
    assert _reply(context)["rating"] == rating


@then(parsers.parse('my rating "{rating}" of the writing of "{request}" is kept'))
def writing_rating_kept(client, students, rating, request):
    with client.app.state.database.connect() as connection:
        rows = connection.execute(select(storage.answer_ratings)).all()
    kept = [(row.rating, row.kind, row.question) for row in rows if students.name(row.student) == students.me]
    assert kept == [(rating, "writing", request)], kept


@then("no reply of the writing assistant is kept")
def no_replies_kept(client):
    with client.app.state.database.connect() as connection:
        assert connection.execute(select(storage.writing_replies)).all() == []


# in the browser


def _panel(page):
    return page.get_by_role("complementary", name="Writing assistant")


def _text(page):
    return page.get_by_role("form", name=re.compile("^(Write|Edit) material$")).get_by_label("Text")


def _last_reply(page):
    return _panel(page).get_by_role("article").last


@when("I open the writing assistant")
def open_writing_assistant(page):
    page.get_by_role("button", name="Writing assistant").click()
    expect(_panel(page)).to_be_visible()


@when("I start editing the material")
def start_editing(page):
    page.get_by_role("button", name="Edit", exact=True).click()
    expect(_text(page)).not_to_have_value("")


@when(parsers.parse('I choose the section "{section}" for the writing assistant'))
def choose_section(page, section):
    _panel(page).get_by_label("Help with").select_option(label=section)


@when("I turn off searching the web")
def turn_off_web(page):
    _panel(page).get_by_role("checkbox", name="Search the web").uncheck()


@when(parsers.parse('I ask the writing assistant in the browser "{request}"'))
def ask_in_browser(page, request):
    panel = _panel(page)
    replies = panel.get_by_role("article")
    before = replies.count()
    panel.get_by_role("textbox", name="Ask the writing assistant").fill(request)
    panel.get_by_role("button", name="Ask", exact=True).click()
    expect(replies).to_have_count(before + 1, timeout=600_000)


@then("I see its reply with its references")
def see_reply_with_references(page):
    reply = _last_reply(page)
    expect(reply).to_contain_text("as one page says")
    references = reply.get_by_role("list", name="References").get_by_role("link")
    expect(references).to_have_count(2)
    expect(references.first).to_have_attribute("href", re.compile(r"^https://example\.org/"))


@then("I see its reply without references")
def see_reply_without_references(page):
    reply = _last_reply(page)
    expect(reply).to_contain_text("from what the AI knows")
    expect(reply.get_by_role("list", name="References")).to_have_count(0)


@when("I add the reply at the end of the material")
def add_at_end(page):
    _last_reply(page).get_by_role("button", name="Add at the end").click()


@when("I replace the section with the reply")
def replace_section(page):
    _last_reply(page).get_by_role("button", name="Replace the section").click()


@then(parsers.parse('the text has "{text}"'))
def text_has(page, text):
    expect(_text(page)).to_have_value(re.compile(re.escape(text)))


@then(parsers.parse('the text no longer has "{text}"'))
def text_lacks(page, text):
    expect(_text(page)).not_to_have_value(re.compile(re.escape(text)))


@then("the text has the reply, and its references as links")
def text_has_reply(page):
    value = _text(page)
    expect(value).to_have_value(re.compile(r"as one page says \[\[1\]\]\(https://example\.org/\d+/1\)"))
    expect(value).to_have_value(re.compile(r"\*\*References\*\*\n\n1\. \[Page \d+\.1\]\(https://example\.org/\d+/1\)"))


def _thumb(page, which: str):
    return _last_reply(page).get_by_role("button", name=f"Thumbs {which}")


@when(parsers.re(r"I give the writing assistant's reply a thumbs (?P<which>up|down)$"))
def give_writing_thumb(page, which):
    _thumb(page, which).click()


@then(parsers.re(r"the thumbs (?P<which>up|down) of the writing assistant's reply is pressed$"))
def writing_thumb_pressed(page, which):
    expect(_thumb(page, which)).to_have_attribute("aria-pressed", "true")


@then(parsers.re(r"the thumbs (?P<which>up|down) of the writing assistant's reply is not pressed$"))
def writing_thumb_not_pressed(page, which):
    expect(_thumb(page, which)).to_have_attribute("aria-pressed", "false")


@then("neither thumb of the writing assistant's reply is pressed")
def neither_writing_thumb(page):
    writing_thumb_not_pressed(page, "up")
    writing_thumb_not_pressed(page, "down")

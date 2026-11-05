"""Steps of ai_usage.feature and ui_ai_usage.feature: how many tokens the AI uses, on what and for whom."""

from datetime import timedelta

from pytest_bdd import given, parsers, then, when

from tests.bdd.steps.study_steps import _document_scope, _rows


def _used(students, name=None, **params) -> dict:
    response = students.client.get("/api/usage", headers=students.headers(name), params=params)
    assert response.status_code == 200, response.text
    return response.json()


def _ask_ai(students, what: str, name=None):
    """asks the AI for what the scenario names, about the material"""
    scope = _document_scope(students, "fem-notes.md")
    headers = students.headers(name)
    client = students.client
    if what == "a question answered":
        response = client.post("/api/assistant/requests", headers=headers, json={**scope, "question": "What is it?"})
    elif what == "a summary":
        response = client.post("/api/summaries", headers=headers, json=scope)
    elif what == "a quiz":
        response = client.post("/api/quizzes", headers=headers, json={**scope, "questions": 1})
    elif what == "flashcards":
        response = client.post("/api/flashcards", headers=headers, json={**scope, "cards": 1})
    else:
        assert what == "generated material"
        response = client.post(
            f"/api/courses/{scope['course_id']}/generated",
            headers=headers,
            json={"documents": [scope["document_id"]], "kind": "cheat sheet", "instructions": ""},
        )
    assert response.status_code == 200, response.text
    return response


@given(parsers.parse("the AI uses {tokens_in:d} input tokens and {tokens_out:d} output tokens each time"))
def ai_uses(app, tokens_in, tokens_out):
    app.state.platform.ai.tokens = (tokens_in, tokens_out)


@when(parsers.parse("I ask the AI for {what}"))
@given(parsers.parse("I have asked the AI for {what}"))
def ask_ai(students, what):
    _ask_ai(students, what)


@given(parsers.parse('the student "{name}" has asked the AI for {what}'))
def they_ask_ai(students, name, what):
    _ask_ai(students, what, name=name)


@given(parsers.parse("I asked the AI for {what} {days:d} days ago"))
def asked_ai_days_ago(app, students, what, days):
    usage = app.state.ai_usage
    clock = usage.now
    usage.now = lambda: clock() - timedelta(days=days)
    try:
        _ask_ai(students, what)
    finally:
        usage.now = clock


@then("I have used no tokens")
def used_nothing(students):
    assert _spent(_used(students)) == (0, 0, 0)


def _spent(row: dict) -> tuple[int, int, int]:
    return row["input_tokens"], row["output_tokens"], row["requests"]


@then(parsers.parse("I have used {tokens_in:d} input tokens and {tokens_out:d} output tokens in {count:d} request"))
@then(parsers.parse("I have used {tokens_in:d} input tokens and {tokens_out:d} output tokens in {count:d} requests"))
def used_in_requests(students, tokens_in, tokens_out, count):
    assert _spent(_used(students)) == (tokens_in, tokens_out, count)


@then(parsers.parse('I have used {tokens_in:d} input tokens and {tokens_out:d} output tokens on "{purpose}"'))
def used_on(students, tokens_in, tokens_out, purpose):
    row = next(row for row in _used(students)["purposes"] if row["purpose"] == purpose)
    assert _spent(row)[:2] == (tokens_in, tokens_out)


@then(
    parsers.parse(
        'I have used {tokens_in:d} input tokens and {tokens_out:d} output tokens with "{model}" of "{provider}"'
    )
)
def used_with(students, tokens_in, tokens_out, model, provider):
    row = next(r for r in _used(students)["models"] if (r["provider"], r["model"]) == (provider, model))
    assert _spent(row)[:2] == (tokens_in, tokens_out)


@then(
    parsers.parse("I have used {tokens_in:d} input tokens and {tokens_out:d} output tokens over the last {days:d} days")
)
def used_over(students, tokens_in, tokens_out, days):
    assert _spent(_used(students, days=days))[:2] == (tokens_in, tokens_out)


@when(parsers.parse("I ask for my usage over the last {days:d} days"))
def ask_for_days(students, context, days):
    context["response"] = students.client.get("/api/usage", headers=students.headers(), params={"days": days})


@then("I am told the number of days is invalid")
def told_days_invalid(context):
    assert context["response"].status_code == 422, context["response"].text


@then(parsers.parse('the student "{name}" has used no tokens'))
def they_used_nothing(students, name):
    assert _spent(_used(students, name=name)) == (0, 0, 0)


@then(parsers.parse('the admin "{name}" sees the usage:'))
def admin_sees(students, name, datatable):
    response = students.client.get("/api/usage/students", headers=students.headers(name))
    assert response.status_code == 200, response.text
    wanted = [
        (students.id(row["student"]), int(row["requests"]), int(row["input tokens"]), int(row["output tokens"]))
        for row in _rows(datatable)
    ]
    assert [(r["student"], r["requests"], r["input_tokens"], r["output_tokens"]) for r in response.json()] == wanted


@when("I ask for everyone's usage")
def ask_for_everyones(students, context):
    context["response"] = students.client.get("/api/usage/students", headers=students.headers())


@then("I am told only the app's admins can see it")
def told_only_admins(context):
    assert context["response"].status_code == 403, context["response"].text
    assert "only the app's admins" in context["response"].json()["detail"]


# in the browser


def _usage_row(page, name: str):
    return page.get_by_role("row").filter(has=page.get_by_role("rowheader", name=name, exact=True))


@then(parsers.parse('I see I have used "{tokens}" tokens'))
def see_used(page, tokens):
    from playwright.sync_api import expect

    expect(page.get_by_text(f"You have used {tokens} tokens")).to_be_visible()


@then(parsers.parse('I see "{purpose}" used "{tokens}" tokens'))
def see_purpose_used(page, purpose, tokens):
    from playwright.sync_api import expect

    expect(_usage_row(page, purpose).get_by_role("cell").last).to_have_text(tokens)


@then(parsers.parse('I see the student "{name}" used "{tokens}" tokens'))
def see_student_used(page, students, name, tokens):
    from playwright.sync_api import expect

    expect(_usage_row(page, students.id(name)).get_by_role("cell").last).to_have_text(tokens)


@then("I don't see the usage of each student")
def see_no_students(page):
    from playwright.sync_api import expect

    expect(page.get_by_role("heading", name="Usage")).to_be_visible()
    expect(page.get_by_role("heading", name="Students")).to_have_count(0)

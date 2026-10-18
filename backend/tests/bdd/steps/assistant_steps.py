"""Steps of ask.feature: asking the assistant while reading a material."""

from pytest_bdd import given, parsers, then, when

from tests.bdd.steps.study_steps import _document_scope, _section_scope, _topic_scope


def _first_section(students, filename: str) -> dict:
    material = students.find_material(filename)
    sections = students.open(material).json()["sections"]
    return {**_document_scope(students, filename), "section": sections[0]["position"]}


def _ask(students, context, question: str):
    response = students.client.post(
        "/api/assistant/requests", headers=students.headers(), json={**context["where"], "question": question}
    )
    assert response.status_code == 200, response.text
    context["turn"] = response.json()
    context.setdefault("turns", []).append(context["turn"])


def _conversation(students, filename: str, name: str | None = None) -> dict:
    where = _document_scope(students, filename) if name is None else _their_scope(students, filename, name)
    response = students.client.get("/api/assistant/conversation", headers=students.headers(name), params=where)
    assert response.status_code == 200, response.text
    return response.json()


def _their_scope(students, filename: str, name: str) -> dict:
    material = students.find_material(filename, name=name)
    return {"course_id": material["course_id"], "document_id": material["document_id"]}


def _cited(turn: dict) -> set[tuple[str, str]]:
    return {(source["filename"], source["title"]) for source in turn["sources"]}


# where the student is, and what they ask


@given(parsers.parse('I am reading the section "{title}" of "{filename}"'))
def reading_section(students, context, title, filename):
    context["where"] = _section_scope(students, title, filename)


@when(parsers.parse('I ask the assistant "{question}"'))
@given(parsers.parse('I have asked the assistant "{question}"'))
def ask_the_assistant(students, context, question):
    _ask(students, context, question)


@given(parsers.parse('I have asked the assistant "{question}" while reading "{filename}"'))
def asked_while_reading(students, context, question, filename):
    context["where"] = _first_section(students, filename)
    _ask(students, context, question)
    context["asked"] = question


# answers


@then("the assistant answers")
def answers(context):
    turn = context["turn"]
    assert turn["kind"] == "answer" and turn["covered"], turn
    assert turn["answer"].strip()


@then(parsers.parse('the answer cites the section "{title}" of "{filename}"'))
def cites_section(context, title, filename):
    assert (filename, title) in _cited(context["turn"]), context["turn"]


@then(parsers.parse('the answer cites "{filename}"'))
def cites_material(context, filename):
    assert filename in {cited for cited, _ in _cited(context["turn"])}, context["turn"]


@then("the assistant tells me my material does not cover it")
def not_covered(context):
    turn = context["turn"]
    assert turn["kind"] == "answer" and not turn["covered"], turn
    assert turn["answer"].strip()


@then("the answer cites nothing")
def cites_nothing(context):
    assert context["turn"]["sources"] == []


# summaries and quizzes


def _summary(context) -> dict:
    turn = context["turn"]
    assert turn["kind"] == "summary" and turn["summary"], turn
    return turn["summary"]


def _same_scope(scope: dict, expected: dict) -> bool:
    return all(scope.get(key) == value for key, value in expected.items()) and all(
        scope.get(key) is None for key in ("document_id", "section", "subject", "topic") if key not in expected
    )


@then(parsers.parse('the assistant gives me a summary of the section "{title}" of "{filename}"'))
def summary_of_section(students, context, title, filename):
    assert _same_scope(_summary(context)["scope"], _section_scope(students, title, filename))


@then(parsers.parse('the assistant gives me a summary of "{filename}"'))
def summary_of_document(students, context, filename):
    assert _same_scope(_summary(context)["scope"], _document_scope(students, filename))


@then(parsers.parse('the assistant gives me a summary of the topic "{location}"'))
def summary_of_topic(students, context, location):
    assert _same_scope(_summary(context)["scope"], _topic_scope(students, location))


@then("the assistant gives me the summary I got before")
def same_summary(context):
    first = next(turn["summary"] for turn in context["turns"] if turn["summary"])
    assert _summary(context)["id"] == first["id"]


@then("the assistant gives me a summary I have not seen before")
def new_summary(context):
    seen = {turn["summary"]["id"] for turn in context["turns"][:-1] if turn["summary"]}
    assert _summary(context)["id"] not in seen


@then(parsers.parse('the assistant gives me a quiz of {count:d} questions on "{filename}"'))
def quiz_on_document(students, context, count, filename):
    turn = context["turn"]
    assert turn["kind"] == "quiz" and turn["quiz"], turn
    assert len(turn["quiz"]["questions"]) == count
    assert _same_scope(turn["quiz"]["scope"], _document_scope(students, filename))


# the conversation


@then("the assistant is given my earlier question and its answer")
def given_earlier(platform, context):
    earlier = context["turns"][-2]
    history = [(message.role, message.content) for message in platform.histories[-1]]
    assert ("user", earlier["question"]) in history
    assert ("assistant", earlier["answer"]) in history


@when(parsers.parse('I open "{filename}" again'))
def open_again(students, context, filename):
    context["conversation"] = _conversation(students, filename)


@then(parsers.parse('my conversation with the assistant on "{filename}" shows "{question}" and its answer'))
def conversation_shows(context, filename, question):
    turns = context["conversation"]["turns"]
    assert [turn["question"] for turn in turns] == [question]
    assert turns[0]["answer"] == context["turns"][0]["answer"]


@when(parsers.parse('I start a new conversation on "{filename}"'))
def start_again(students, context, filename):
    context["ended"] = _conversation(students, filename)["id"]
    response = students.client.delete(
        "/api/assistant/conversation", headers=students.headers(), params=_document_scope(students, filename)
    )
    assert response.status_code == 200, response.text


@then(parsers.parse('my conversation with the assistant on "{filename}" is empty'))
def conversation_empty(students, filename):
    assert _conversation(students, filename)["turns"] == []


@then("the assistant is not given my earlier question")
def not_given_earlier(students, platform, context):
    assert platform.conversation_context(context["ended"]) == []
    _ask(students, context, "What is assembled into the global stiffness matrix?")
    assert context["asked"] not in [message.content for message in platform.histories[-1]]


@when(parsers.parse('the student "{name}" opens "{filename}"'))
def they_open(students, context, name, filename):
    context["their_conversation"] = _conversation(students, filename, name=name)


@then(parsers.parse('the conversation of "{name}" with the assistant on "{filename}" is empty'))
def their_conversation_empty(context, name, filename):
    assert context["their_conversation"]["turns"] == []

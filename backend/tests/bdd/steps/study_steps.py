"""Steps of summaries.feature and quizzes.feature, which ask for things the same way."""

from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from study_assistant import storage


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row)) for row in rows]


# scopes


def _section_scope(students, title: str, filename: str) -> dict:
    material = students.find_material(filename)
    opened = students.open(material).json()
    position = next(s["position"] for s in opened["sections"] if s["title"] == title)
    return {"course_id": material["course_id"], "document_id": material["document_id"], "section": position}


def _document_scope(students, filename: str) -> dict:
    material = students.find_material(filename)
    return {"course_id": material["course_id"], "document_id": material["document_id"]}


def _topic_scope(students, location: str) -> dict:
    course, subject, topic = location.split("/")
    course_id = next(c["id"] for c in students.courses() if c["name"] == course)
    return {"course_id": course_id, "subject": subject, "topic": topic}


def _ask(students, kind: str, scope: dict, *, new: bool = False, questions: int | None = None, name=None):
    body = {**scope, "new": new}
    if questions is not None:
        body["questions"] = questions
    return students.client.post(f"/api/{kind}", headers=students.headers(name), json=body)


def _history(students, kind: str, scope: dict, name=None) -> list[dict]:
    response = students.client.get(f"/api/{kind}", headers=students.headers(name), params=scope)
    assert response.status_code == 200, response.text
    return response.json()


def _asked(context, kind: str, scope: dict, response) -> None:
    """what was just asked for and got, for the steps that follow"""
    context["kind"], context["scope"], context["response"] = kind, scope, response
    if response.status_code == 200:
        context.setdefault("got", []).append(response.json())
        if scope.get("document_id"):
            context["document_id"] = scope["document_id"]


def _got(context) -> dict:
    response = context["response"]
    assert response.status_code == 200, response.text
    return response.json()


# asking for summaries

SUMMARY_OF_SECTION = 'a summary of the section "{title}" of "{filename}"'
SUMMARY_OF_DOCUMENT = 'a summary of "{filename}"'
SUMMARY_OF_TOPIC = 'a summary of the topic "{location}"'


@when(parsers.parse("I ask for " + SUMMARY_OF_SECTION))
@given(parsers.parse("I have asked for " + SUMMARY_OF_SECTION))
def summary_of_section(students, context, title, filename):
    scope = _section_scope(students, title, filename)
    _asked(context, "summaries", scope, _ask(students, "summaries", scope))


@when(parsers.parse('I ask for a new summary of the section "{title}" of "{filename}"'))
def new_summary_of_section(students, context, title, filename):
    scope = _section_scope(students, title, filename)
    _asked(context, "summaries", scope, _ask(students, "summaries", scope, new=True))


@when(parsers.parse("I ask for " + SUMMARY_OF_DOCUMENT))
@given(parsers.parse("I have asked for " + SUMMARY_OF_DOCUMENT))
def summary_of_document(students, context, filename):
    scope = _document_scope(students, filename)
    _asked(context, "summaries", scope, _ask(students, "summaries", scope))


@when(parsers.parse("I ask for " + SUMMARY_OF_TOPIC))
@given(parsers.parse("I have asked for " + SUMMARY_OF_TOPIC))
def summary_of_topic(students, context, location):
    scope = _topic_scope(students, location)
    _asked(context, "summaries", scope, _ask(students, "summaries", scope))


@when(parsers.parse('the student "{name}" asks for a summary of "{filename}"'))
def student_asks_for_summary(students, context, name, filename):
    scope = _document_scope(students, filename)
    context["their_response"] = _ask(students, "summaries", scope, name=name)
    context["their_name"] = name


# asking for quizzes

QUIZ_ON_SECTION = 'a quiz of {count:d} questions on the section "{title}" of "{filename}"'
QUIZ_ON_DOCUMENT = 'a quiz of {count:d} questions on "{filename}"'
QUIZ_ON_TOPIC = 'a quiz of {count:d} questions on the topic "{location}"'


@when(parsers.parse("I ask for " + QUIZ_ON_SECTION))
@given(parsers.parse("I have asked for " + QUIZ_ON_SECTION))
def quiz_on_section(students, context, count, title, filename):
    scope = _section_scope(students, title, filename)
    _asked(context, "quizzes", scope, _ask(students, "quizzes", scope, questions=count))


@when(parsers.parse('I ask for a new quiz of {count:d} questions on the section "{title}" of "{filename}"'))
def new_quiz_on_section(students, context, count, title, filename):
    scope = _section_scope(students, title, filename)
    _asked(context, "quizzes", scope, _ask(students, "quizzes", scope, questions=count, new=True))


@when(parsers.parse("I ask for " + QUIZ_ON_DOCUMENT))
@given(parsers.parse("I have asked for " + QUIZ_ON_DOCUMENT))
@given(parsers.parse("I have " + QUIZ_ON_DOCUMENT))
def quiz_on_document(students, context, count, filename):
    scope = _document_scope(students, filename)
    _asked(context, "quizzes", scope, _ask(students, "quizzes", scope, questions=count))


@when(parsers.parse("I ask for " + QUIZ_ON_TOPIC))
@given(parsers.parse("I have asked for " + QUIZ_ON_TOPIC))
def quiz_on_topic(students, context, count, location):
    scope = _topic_scope(students, location)
    _asked(context, "quizzes", scope, _ask(students, "quizzes", scope, questions=count))


# what was got


@then("I get a summary")
def got_a_summary(context):
    assert _got(context)["content"].strip()


@then(parsers.parse("I get a quiz of {count:d} questions"))
def got_a_quiz(context, count):
    assert len(_got(context)["questions"]) == count


@then("I get the summary I got before")
@then("I get the quiz I got before")
def got_the_same(context):
    assert _got(context)["id"] == context["got"][0]["id"]


@then("I get a summary I have not seen before")
@then("I get a quiz I have not seen before")
def got_a_new_one(context):
    latest, earlier = _got(context), context["got"][0]
    assert latest["id"] != earlier["id"]
    assert latest.get("content") != earlier.get("content") or latest.get("questions") != earlier.get("questions")


@then("no new summary was written")
@then("no new quiz was written")
def nothing_new(students, context):
    assert len(_history(students, context["kind"], context["scope"])) == 1


@then(parsers.parse('the summaries of the section "{title}" of "{filename}" are, newest first:'))
def summaries_newest_first(students, context, title, filename, datatable):
    history = _history(students, "summaries", _section_scope(students, title, filename))
    expected = {"new": context["got"][-1]["id"], "earlier": context["got"][0]["id"]}
    assert [s["id"] for s in history] == [expected[row["summary"]] for row in _rows(datatable)]


@then(parsers.parse('I have {count:d} quizzes on the section "{title}" of "{filename}", newest first'))
def quizzes_newest_first(students, context, count, title, filename):
    history = _history(students, "quizzes", _section_scope(students, title, filename))
    assert [q["id"] for q in history] == [q["id"] for q in reversed(context["got"])][:count]
    assert len(history) == count


@then(parsers.parse('But I am told it is out of date, as "{filename}" was added since'))
@then(parsers.parse('I am told it is out of date, as "{filename}" was added since'))
def out_of_date(context, filename):
    assert filename in (_got(context)["out_of_date"] or {}).get("added", [])


@then("I am told there is no material to summarise")
def nothing_to_summarise(context):
    response = context["response"]
    assert response.status_code == 404, response.text
    assert "no material" in response.json()["detail"]


@then(parsers.parse("I am told a quiz has between {low:d} and {high:d} questions"))
def quiz_size(context, low, high):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"between {low} and {high} questions" in response.json()["detail"]


@then(parsers.parse('the student "{name}" gets a summary written for them'))
def their_own_summary(students, context, name):
    response = context["their_response"]
    assert response.status_code == 200, response.text
    assert response.json()["id"] != context["got"][0]["id"]
    assert len(_history(students, "summaries", context["scope"], name=name)) == 1


# citations


def _cited(context) -> list[dict]:
    got = _got(context)
    if "questions" in got:
        return [question["source"] for question in got["questions"]]
    return got["sources"]


@then("the summary cites only:")
def cites_only(context, datatable):
    cited = {(s["filename"], s["title"]) for s in _cited(context)}
    assert cited == {(row["material"], row["section"]) for row in _rows(datatable)}


@then(parsers.parse('the summary cites every section of "{filename}"'))
def cites_every_section(students, context, filename):
    sections = students.open(students.find_material(filename)).json()["sections"]
    assert {s["title"] for s in _cited(context) if s["filename"] == filename} == {s["title"] for s in sections}


@then(parsers.parse('the summary cites "{first}" and "{second}"'))
@then(parsers.parse('the questions cite "{first}" and "{second}"'))
def cites_both(context, first, second):
    assert {first, second} <= {s["filename"] for s in _cited(context)}


@then(parsers.parse('the summary cites "{filename}"'))
def cites(context, filename):
    assert filename in {s["filename"] for s in _cited(context)}


@then(parsers.parse('the summary does not cite "{filename}"'))
@then(parsers.parse('no question cites "{filename}"'))
def does_not_cite(context, filename):
    assert filename not in {s["filename"] for s in _cited(context)}


@then(parsers.parse('every question cites one of the sections "{first}" or "{second}" of "{filename}"'))
def every_question_cites_one_of(context, first, second, filename):
    assert all(s["filename"] == filename and s["title"] in (first, second) for s in _cited(context))


@then(parsers.parse('every question cites a section of "{filename}"'))
def every_question_cites(context, filename):
    assert all(s["filename"] == filename for s in _cited(context))


@then(parsers.parse("every question has {count:d} choices, one of them correct"))
def every_question_has_choices(client, students, context, count):
    quiz = _got(context)
    answers = client.app.state.quizzes.answers(students.id(students.me), quiz["id"])
    assert all(len(question["choices"]) == count for question in quiz["questions"])
    assert all(0 <= answer < count for answer in answers)


# deleting


@then(parsers.parse('I have no summaries of "{filename}"'))
@then(parsers.parse('I have no quizzes on "{filename}"'))
def none_left(client, context, filename):
    table = storage.summaries if context["kind"] == "summaries" else storage.quizzes
    with client.app.state.database.connect() as connection:
        left = connection.execute(select(table).where(table.c.document_id == context["document_id"])).all()
    assert left == []


# taking quizzes


def _take(client, students, context, correct: int):
    quiz = _got(context)
    answers = client.app.state.quizzes.answers(students.id(students.me), quiz["id"])
    chosen = [answer if i < correct else (answer + 1) % 4 for i, answer in enumerate(answers)]
    response = client.post(f"/api/quizzes/{quiz['id']}/attempts", headers=students.headers(), json={"answers": chosen})
    assert response.status_code == 201, response.text
    context["attempt"] = response.json()


@when(parsers.parse("I answer {right:d} of its questions correctly and {wrong:d} wrongly"))
def answer(client, students, context, right, wrong):
    _take(client, students, context, right)


@given(
    parsers.parse('I have taken a quiz of {count:d} questions on "{filename}" and scored {score:d} out of {total:d}')
)
def have_taken(client, students, context, count, filename, score, total):
    quiz_on_document(students, context, count, filename)
    _take(client, students, context, score)


@when("I take it again and answer every question correctly")
def take_again(client, students, context):
    _take(client, students, context, len(_got(context)["questions"]))


@then(parsers.parse("my score is {score:d} out of {total:d}"))
def score_is(context, score, total):
    assert (context["attempt"]["score"], context["attempt"]["total"]) == (score, total)


@then("for the question I got wrong I see the correct answer and the section to study again")
def see_correct_answer(client, students, context):
    wrong = [result for result in context["attempt"]["results"] if not result["correct"]]
    answers = client.app.state.quizzes.answers(students.id(students.me), _got(context)["id"])
    assert len(wrong) == 1
    position = context["attempt"]["results"].index(wrong[0])
    assert wrong[0]["correct_choice"] == answers[position]
    assert wrong[0]["source"]["title"]


@then("my scores for the quiz are, newest first:")
def scores(client, students, context, datatable):
    response = client.get(f"/api/quizzes/{_got(context)['id']}/attempts", headers=students.headers())
    seen = [f"{a['score']} of {a['total']}" for a in response.json()]
    assert seen == [row["score"] for row in _rows(datatable)]

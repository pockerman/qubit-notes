from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row)) for row in rows]


def _create_course(students, name: str):
    return students.client.post("/api/courses", headers=students.headers(), json={"name": name})


def _create_topic(students, location: str, course: str, name: str | None = None):
    subject, topic = location.split("/")
    return students.client.post(
        f"/api/courses/{course}/topics", headers=students.headers(name), json={"subject": subject, "topic": topic}
    )


@when(parsers.parse('I create the course "{name}"'))
def create_course(request, students, context, name):
    if "ui" in request.keywords:
        # in the browser, which writes the name the way it's stored
        from tests.bdd.steps.ui_steps import create_course_in_browser

        create_course_in_browser(request.getfixturevalue("page"), name)
        return
    context["response"] = _create_course(students, name)


@given(parsers.parse('I have created the course "{name}"'))
def have_created_course(students, name):
    response = _create_course(students, name)
    assert response.status_code == 201, response.text


@then(parsers.parse('I am the owner of the course "{name}"'))
def owner_of(students, name):
    assert next(c for c in students.courses() if c["name"] == name)["role"] == "owner"


@then(parsers.parse('the course "{name}" has no material'))
def no_material(students, name):
    assert students.materials(name) == []


@then(parsers.parse('I am told I already have the course "{name}"'))
def already_have(context, name):
    response = context["response"]
    assert response.status_code == 409, response.text
    assert f"already have the course {name!r}" in response.json()["detail"]


@then("I am told the course name is invalid")
def invalid_name(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "invalid course name" in response.json()["detail"]


@when(parsers.parse('I create the topic "{location}" in "{course}"'))
@given(parsers.parse('I have created the topic "{location}" in "{course}"'))
def create_topic(students, context, location, course):
    context["response"] = _create_topic(students, location, course)
    assert context["response"].status_code == 201, context["response"].text


@when(parsers.parse('the student "{name}" creates the topic "{location}" in "{course}"'))
def student_creates_topic(students, context, name, location, course):
    context["response"] = _create_topic(students, location, course, name=name)


def _delete_topic(students, location: str, course: str, name: str | None = None):
    subject, topic = location.split("/")
    return students.client.delete(
        f"/api/courses/{course}/subjects/{subject}/topics/{topic}", headers=students.headers(name)
    )


@when(parsers.parse('I delete the topic "{location}" from "{course}"'))
def delete_topic(students, context, location, course):
    context["response"] = _delete_topic(students, location, course)


@when(parsers.parse('the student "{name}" deletes the topic "{location}" from "{course}"'))
def student_deletes_topic(students, context, name, location, course):
    context["response"] = _delete_topic(students, location, course, name)


@then(parsers.parse('I am told "{course}" has no topic "{location}"'))
def no_such_topic(context, course, location):
    response = context["response"]
    assert response.status_code == 404, response.text
    assert f"{course!r} has no topic {location!r}" in response.json()["detail"]


@then(parsers.parse('the topics of "{course}" are:'))
def topics_are(students, course, datatable):
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers())
    assert response.status_code == 200, response.text
    seen = [{"subject": t["subject"], "topic": t["topic"], "materials": str(t["materials"])} for t in response.json()]
    assert seen == _rows(datatable)


@then(parsers.parse('the topics of "{course}" are empty'))
def topics_empty(students, course):
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers())
    assert response.status_code == 200, response.text
    assert response.json() == []


# deleting


def _delete_course(students, course: str, name: str | None = None):
    return students.client.delete(f"/api/courses/{course}", headers=students.headers(name))


@when(parsers.parse('I delete the course "{course}"'))
def delete_course(students, context, course):
    context["response"] = _delete_course(students, course)


@when(parsers.parse('the student "{name}" deletes the course "{course}"'))
def student_deletes_course(students, context, name, course):
    context["response"] = _delete_course(students, course, name)


@then(parsers.parse('the course "{course}" is still there'))
def course_still_there(students, course):
    assert course in [c["name"] for c in students.courses()]


@then(parsers.parse('I am told I have no course "{course}"'))
def no_such_course(context, course):
    response = context["response"]
    assert response.status_code == 404, response.text
    assert f"no course {course!r}" in response.json()["detail"]


@given(parsers.parse('I have a summary and a quiz of "{filename}"'))
def have_summary_and_quiz(students, filename):
    material = students.find_material(filename)
    scope = {"course_id": material["course_id"], "document_id": material["document_id"]}
    for kind, extra in (("summaries", {}), ("quizzes", {"questions": 1})):
        response = students.client.post(f"/api/{kind}", headers=students.headers(), json={**scope, **extra})
        assert response.status_code == 200, response.text
    quiz = response.json()
    attempt = students.client.post(
        f"/api/quizzes/{quiz['id']}/attempts", headers=students.headers(), json={"answers": [0]}
    )
    assert attempt.status_code == 201, attempt.text


@then("I have no notes, summaries, quizzes or conversations")
def nothing_written(students):
    # what the student wrote is about material that's gone, so it can't be asked for by its scope any more
    me = students.id(students.me)
    database = students.client.app.state.database
    with database.connect() as connection:
        for table in (storage.notes, storage.summaries, storage.quizzes, storage.quiz_attempts, storage.conversations):
            assert connection.execute(select(table).where(table.c.student == me)).fetchall() == [], table.name
        turns = connection.execute(select(storage.conversation_turns)).fetchall()
        assert turns == []


# the order of topics


def _topics_of(students, subject: str, course: str, name: str | None = None) -> list[str]:
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers(name))
    assert response.status_code == 200, response.text
    return [t["topic"] for t in response.json() if t["subject"] == subject]


def _order(students, subject: str, course: str, datatable, name: str | None = None):
    topics = [row["topic"] for row in _rows(datatable)]
    return students.client.put(
        f"/api/courses/{course}/subjects/{subject}/topic-order", headers=students.headers(name), json={"topics": topics}
    )


@when(parsers.parse('I put the topics of "{subject}" in "{course}" in the order:'))
def put_in_order(students, context, subject, course, datatable):
    context["response"] = _order(students, subject, course, datatable)


@given(parsers.parse('I have put the topics of "{subject}" in "{course}" in the order:'))
def have_put_in_order(students, subject, course, datatable):
    response = _order(students, subject, course, datatable)
    assert response.status_code == 200, response.text


@when(parsers.parse('the student "{name}" puts the topics of "{subject}" in "{course}" in the order:'))
def student_puts_in_order(students, context, name, subject, course, datatable):
    context["response"] = _order(students, subject, course, datatable, name)


@then(parsers.parse('the topics of "{subject}" in "{course}" are, in order:'))
def topics_in_order(students, subject, course, datatable):
    assert _topics_of(students, subject, course) == [row["topic"] for row in _rows(datatable)]


@then(parsers.parse('the student "{name}" sees the topics of "{subject}" in "{course}" in the order:'))
def student_sees_topics_in_order(students, name, subject, course, datatable):
    assert _topics_of(students, subject, course, name) == [row["topic"] for row in _rows(datatable)]


@then(parsers.parse('I am told the order must have each of the topics of "{subject}" once'))
def order_invalid(context, subject):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"each of the topics of {subject!r} once" in response.json()["detail"]

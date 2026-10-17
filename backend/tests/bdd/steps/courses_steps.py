from pytest_bdd import given, parsers, then, when


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
def create_topic(students, context, location, course):
    context["response"] = _create_topic(students, location, course)
    assert context["response"].status_code == 201, context["response"].text


@when(parsers.parse('the student "{name}" creates the topic "{location}" in "{course}"'))
def student_creates_topic(students, context, name, location, course):
    context["response"] = _create_topic(students, location, course, name=name)


@then(parsers.parse('the topics of "{course}" are:'))
def topics_are(students, course, datatable):
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers())
    assert response.status_code == 200, response.text
    seen = [{"subject": t["subject"], "topic": t["topic"], "materials": str(t["materials"])} for t in response.json()]
    assert seen == _rows(datatable)

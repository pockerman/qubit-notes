from pytest_bdd import given, parsers, then, when


def _create_titled(students, name: str, title: str):
    return students.client.post("/api/courses", headers=students.headers(), json={"name": name, "title": title})


@when(parsers.re(r'I create the course "(?P<name>[^"]+)" titled "(?P<title>[^"]+)"$'))
def create_titled(students, context, name, title):
    context["response"] = _create_titled(students, name, title)
    assert context["response"].status_code == 201, context["response"].text


@given(parsers.re(r'I have created the course "(?P<name>[^"]+)" titled "(?P<title>[^"]+)"$'))
def have_created_titled(students, name, title):
    response = _create_titled(students, name, title)
    assert response.status_code == 201, response.text


def _change_title(students, course: str, title: str, student: str | None = None):
    return students.client.put(f"/api/courses/{course}/title", headers=students.headers(student), json={"title": title})


@when(parsers.re(r'I change the title of "(?P<course>[^"]+)" to "(?P<title>[^"]*)"$'))
def change_title(request, students, context, course, title):
    if "ui" in request.keywords:
        # in the browser, the course is the one titled so
        from tests.bdd.steps.ui_steps import change_title_in_browser

        change_title_in_browser(request.getfixturevalue("page"), course, title)
        return
    context["response"] = _change_title(students, course, title)


@when(parsers.re(r'the student "(?P<student>[^"]+)" changes the title of "(?P<course>[^"]+)" to "(?P<title>[^"]*)"$'))
def student_changes_title(students, context, student, course, title):
    context["response"] = _change_title(students, course, title, student)


@then(parsers.re(r'the student "(?P<student>[^"]+)" sees the course "(?P<course>[^"]+)" titled "(?P<title>[^"]+)"$'))
def student_sees_title(students, student, course, title):
    response = students.client.get("/api/courses", headers=students.headers(student))
    assert response.status_code == 200, response.text
    assert next(c for c in response.json() if c["name"] == course)["title"] == title


@then("I am told a title can't be blank")
def told_blank_title(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "a title can't be blank" in response.json()["detail"]


@then(parsers.parse('I am told I already have a course titled "{title}"'))
def told_title_taken(context, title):
    response = context["response"]
    assert response.status_code == 409, response.text
    assert f"already have a course titled {title!r}" in response.json()["detail"]

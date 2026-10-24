from pytest_bdd import given, parsers, then, when


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row, strict=True)) for row in rows]


def _create_subject(students, name: str, course: str, student: str | None = None):
    return students.client.post(
        f"/api/courses/{course}/subjects", headers=students.headers(student), json={"name": name}
    )


def _delete_subject(students, subject: str, course: str, student: str | None = None):
    return students.client.delete(f"/api/courses/{course}/subjects/{subject}", headers=students.headers(student))


@when(parsers.re(r'I create the subject "(?P<name>[^"]+)" in "(?P<course>[^"]+)"$'))
def create_subject(students, context, name, course):
    context["response"] = _create_subject(students, name, course)


@given(parsers.re(r'I have created the subject "(?P<name>[^"]+)" in "(?P<course>[^"]+)"$'))
def have_created_subject(students, name, course):
    response = _create_subject(students, name, course)
    assert response.status_code == 201, response.text


@when(parsers.re(r'the student "(?P<student>[^"]+)" creates the subject "(?P<name>[^"]+)" in "(?P<course>[^"]+)"$'))
def student_creates_subject(students, context, student, name, course):
    context["response"] = _create_subject(students, name, course, student)


@when(parsers.re(r'I delete the subject "(?P<subject>[^"]+)" from "(?P<course>[^"]+)"$'))
def delete_subject(students, context, subject, course):
    context["response"] = _delete_subject(students, subject, course)


@when(
    parsers.re(r'the student "(?P<student>[^"]+)" deletes the subject "(?P<subject>[^"]+)" from "(?P<course>[^"]+)"$')
)
def student_deletes_subject(students, context, student, subject, course):
    context["response"] = _delete_subject(students, subject, course, student)


@then(parsers.re(r'the subjects of "(?P<course>[^"]+)" are:$'))
def subjects_are(students, course, datatable):
    response = students.client.get(f"/api/courses/{course}/subjects", headers=students.headers())
    assert response.status_code == 200, response.text
    seen = [{"subject": s["subject"], "name": s["name"], "topics": str(s["topics"])} for s in response.json()]
    assert seen == _rows(datatable)


@then(parsers.re(r'I am told the course already has the subject "(?P<name>[^"]+)"$'))
def told_subject_taken(context, name):
    response = context["response"]
    assert response.status_code == 409, response.text
    assert f"the course already has the subject {name!r}" in response.json()["detail"]


@then("I am told a subject's name needs at least one letter or digit")
def told_subject_needs_letter(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "a subject's name needs at least one letter or digit" in response.json()["detail"]


@then(parsers.re(r'I am told to delete the topics of "(?P<name>[^"]+)" first$'))
def told_delete_topics_first(context, name):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"delete the topics of {name!r} first" in response.json()["detail"]

from pytest_bdd import given, parsers, then, when


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row, strict=True)) for row in rows]


def _create_named(students, topic: str, subject: str, course: str):
    """the topic, created as the browser creates it: ids made from the names, and the names"""

    def slug(name: str) -> str:
        return "-".join("".join(c if c.isalnum() else " " for c in name.lower()).split())

    return students.client.post(
        f"/api/courses/{course}/topics",
        headers=students.headers(),
        json={"subject": slug(subject), "topic": slug(topic), "subject_name": subject, "topic_name": topic},
    )


@when(parsers.re(r'I create the topic "(?P<topic>[^"]+)" in the subject "(?P<subject>[^"]+)" in "(?P<course>[^"]+)"$'))
@given(
    parsers.re(
        r'I have created the topic "(?P<topic>[^"]+)" in the subject "(?P<subject>[^"]+)" in "(?P<course>[^"]+)"$'
    )
)
def create_named_topic(students, context, topic, subject, course):
    context["response"] = _create_named(students, topic, subject, course)
    assert context["response"].status_code == 201, context["response"].text


@then(parsers.parse('the topics of "{course}" are named:'))
def topics_named(students, course, datatable):
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers())
    assert response.status_code == 200, response.text
    seen = [
        {"subject": t["subject"], "subject name": t["subject_name"], "topic": t["topic"], "topic name": t["name"]}
        for t in response.json()
    ]
    assert seen == _rows(datatable)


def _rename_topic(students, location: str, course: str, name: str, student: str | None = None):
    subject, topic = location.split("/")
    return students.client.put(
        f"/api/courses/{course}/subjects/{subject}/topics/{topic}/name",
        headers=students.headers(student),
        json={"name": name},
    )


@when(parsers.re(r'I rename the topic "(?P<location>[^"]+)" of "(?P<course>[^"]+)" to "(?P<name>[^"]*)"$'))
def rename_topic(students, context, location, course, name):
    context["response"] = _rename_topic(students, location, course, name)


@given(parsers.re(r'I have renamed the topic "(?P<location>[^"]+)" of "(?P<course>[^"]+)" to "(?P<name>[^"]*)"$'))
def have_renamed_topic(students, location, course, name):
    response = _rename_topic(students, location, course, name)
    assert response.status_code == 200, response.text


@when(
    parsers.re(
        r'the student "(?P<student>[^"]+)" renames the topic "(?P<location>[^"]+)" of "(?P<course>[^"]+)" '
        r'to "(?P<name>[^"]*)"$'
    )
)
def student_renames_topic(students, context, student, location, course, name):
    context["response"] = _rename_topic(students, location, course, name, student)


@when(parsers.re(r'I rename the subject "(?P<subject>[^"]+)" of "(?P<course>[^"]+)" to "(?P<name>[^"]*)"$'))
def rename_subject(students, context, subject, course, name):
    context["response"] = students.client.put(
        f"/api/courses/{course}/subjects/{subject}/name", headers=students.headers(), json={"name": name}
    )
    assert context["response"].status_code == 200, context["response"].text


@then("I am told a name can't be blank")
def told_blank(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "a name can't be blank" in response.json()["detail"]


@then(parsers.parse('I am told the subject already has a topic named "{name}"'))
def told_taken(context, name):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"already has a topic named {name!r}" in response.json()["detail"]

"""Steps of writing.feature: material a student writes rather than uploads."""

from pytest_bdd import given, parsers, then, when

from qubit_notes.domain.materials import markdown_filename


def _write(students, context, name: str, location: str, text: str, student: str | None = None):
    course, subject, topic = location.split("/")
    response = students.client.post(
        f"/api/courses/{course}/subjects/{subject}/topics/{topic}/materials",
        headers=students.headers(student),
        json={"name": name, "text": text},
    )
    context["response"] = response
    if response.status_code == 202:
        # what was written, by the filename it's saved under, to compare with what's read back
        context.setdefault("written", {})[markdown_filename(name)] = text
    return response


# the name may be empty, which parse's {name} doesn't match
@when(parsers.re(r'I write the material "(?P<name>[^"]*)" in "(?P<location>[^"]+)" with the text:'))
def write_material(students, context, name, location, docstring):
    _write(students, context, name, location, docstring)


@given(parsers.parse('I have written the material "{name}" in "{location}" with the text:'))
def have_written_material(students, context, name, location, docstring):
    students.wait_until_ingested(_write(students, context, name, location, docstring))


@when(parsers.parse('the student "{student}" writes the material "{name}" in "{location}" with the text:'))
def student_writes_material(students, context, student, name, location, docstring):
    _write(students, context, name, location, docstring, student)


@then(parsers.parse('the materials of "{location}" are:'))
def materials_are(students, location, datatable):
    course, subject, topic = location.split("/")
    header, *rows = datatable
    assert header == ["filename"]
    assert [m["filename"] for m in students.materials(course, subject=subject, topic=topic)] == [r[0] for r in rows]


@then("I am given its text exactly as I wrote it")
def given_text_as_written(context):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.json()["text"] == context["written"][context["filename"]]


@then(parsers.parse('I am told the topic already has "{filename}"'))
def topic_already_has(context, filename):
    response = context["response"]
    assert response.status_code == 409, response.text
    assert f"the topic already has {filename!r}" in response.json()["detail"]


@then(parsers.parse('the text of "{filename}" is still "{text}"'))
def text_still(students, filename, text):
    material = students.find_material(filename)
    response = students.client.get(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/text", headers=students.headers()
    )
    assert response.status_code == 200, response.text
    assert response.json()["text"].strip() == text


@then("I am told the material needs a name")
def needs_a_name(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "needs a name" in response.json()["detail"]


@then("I am told the material needs some text")
def needs_some_text(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "needs some text" in response.json()["detail"]

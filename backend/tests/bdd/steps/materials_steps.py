from pytest_bdd import given, parsers, then, when


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row)) for row in rows]


def _course_of(location: str) -> str:
    return location.split("/", 1)[0]


# uploading


@when(parsers.parse('I upload the file "{filename}" to "{location}" with the content:'))
def upload_with_content(students, context, filename, location, docstring):
    context["response"] = students.upload(location, filename, docstring.encode())
    context["filename"] = filename


@when(parsers.parse('I upload the file "{filename}" to "{location}" with no content'))
def upload_empty(students, context, filename, location):
    context["response"] = students.upload(location, filename, b"")


@when(parsers.parse('I upload the file "{filename}" to "{location}"'))
def upload(students, context, filename, location):
    context["response"] = students.upload(location, filename)


@when(parsers.parse('the student "{name}" uploads "{filename}" to "{location}"'))
def student_uploads(students, context, name, filename, location):
    context["response"] = students.upload(location, filename, name=name)


@given(parsers.parse('I have uploaded "{filename}" to "{location}"'))
def have_uploaded(students, filename, location):
    students.upload_and_wait(location, filename)


@given(parsers.parse('the student "{name}" has uploaded "{filename}" to "{location}"'))
def student_has_uploaded(students, name, filename, location):
    students.upload_and_wait(location, filename, name=name)


@given("I have uploaded these materials:")
def have_uploaded_these(students, datatable):
    uploads = [students.upload(row["location"], row["filename"]) for row in _rows(datatable)]
    for response in uploads:
        students.wait_until_ingested(response)


@then("the upload is accepted for processing")
def accepted(context):
    assert context["response"].status_code == 202, context["response"].text


@then(parsers.parse("the upload is rejected as {reason}"))
def rejected(context, reason):
    response = context["response"]
    assert response.status_code == 422, response.text
    expected = {"unsupported": "unsupported", "empty": "empty", "having an invalid location": "invalid location"}
    assert expected[reason] in response.json()["detail"], response.text


@then(parsers.parse('the material "{filename}" is eventually ready'))
def eventually_ready(students, context, filename):
    students.wait_until_ingested(context["response"])


# listing


@when("I list my courses")
def list_courses(students, context):
    context["courses"] = students.courses()


@then("I see the courses:")
def see_courses(context, datatable):
    assert [course["name"] for course in context["courses"]] == [row["course"] for row in _rows(datatable)]


@when(parsers.parse('I list the materials of the course "{course}"'))
def list_course_materials(students, context, course):
    context["materials"] = students.materials(course)


@when(parsers.parse('I list the materials of "{location}"'))
def list_topic_materials(students, context, location):
    course, subject, topic = location.split("/")
    context["materials"] = students.materials(course, subject=subject, topic=topic)


@then("I see the materials:")
def see_materials(context, datatable):
    seen = [{key: m[key] for key in ("subject", "topic", "filename")} for m in context["materials"]]
    assert seen == _rows(datatable)


@then(parsers.parse('the materials of "{location}" are empty'))
def materials_empty(students, location):
    course, subject, topic = location.split("/")
    assert students.materials(course, subject=subject, topic=topic) == []


@then(parsers.parse('the materials of the course "{course}" include "{filename}"'))
def materials_include(students, course, filename):
    assert filename in [m["filename"] for m in students.materials(course)]


@then(parsers.parse('the materials of the course "{course}" do not include "{filename}"'))
def materials_exclude(students, course, filename):
    assert filename not in [m["filename"] for m in students.materials(course)]


# deleting


@when(parsers.parse('I delete the material "{filename}" from "{location}"'))
def delete(students, context, filename, location):
    context["response"] = students.delete(location, filename)


@when(parsers.parse('the student "{name}" deletes the material "{filename}" from "{location}"'))
def student_deletes(students, context, name, filename, location):
    context["response"] = students.delete(location, filename, name=name)


@then("I am told the material was not found")
def not_found(context):
    assert context["response"].status_code == 404, context["response"].text


def _found_filenames(platform, students, course: str, query: str) -> list[str]:
    found = next(c for c in students.courses() if c["name"] == course)
    return [chunk.metadata.get("filename") for chunk in platform.search(found["id"], query, top_k=10)]


@given(parsers.parse('searching "{course}" for "{query}" finds "{filename}"'))
def search_finds(platform, students, course, query, filename):
    assert filename in _found_filenames(platform, students, course, query)


@then(parsers.parse('searching "{course}" for "{query}" finds nothing from "{filename}"'))
def search_finds_nothing(platform, students, course, query, filename):
    assert filename not in _found_filenames(platform, students, course, query)


# memories


@given(parsers.parse('the assistant remembers "{text}" from "{filename}"'))
def remembers(client, students, text, filename):
    document_id = next(
        m["document_id"]
        for course in students.courses()
        for m in students.materials(course["name"])
        if m["filename"] == filename
    )
    client.app.state.memory.remember(students.id(students.me), text, sources=[document_id])


def _remembered(client, students) -> list[str]:
    return [note.text for note in client.app.state.memory.notes(students.id(students.me))]


@then(parsers.parse('the assistant no longer remembers "{text}"'))
def no_longer_remembers(client, students, text):
    assert text not in _remembered(client, students)


@then(parsers.parse('the assistant still remembers "{text}"'))
def still_remembers(client, students, text):
    assert text in _remembered(client, students)

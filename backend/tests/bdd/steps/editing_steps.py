from pytest_bdd import parsers, then, when


def _text_path(material: dict) -> str:
    return f"/api/courses/{material['course_id']}/materials/{material['document_id']}/text"


def _change(students, context, filename: str, text: str, name: str | None = None) -> None:
    # the owner finds the material; the change is made as the student
    material = students.find_material(filename)
    context["response"] = students.client.put(_text_path(material), headers=students.headers(name), json={"text": text})
    context["edited"] = material


@when(parsers.parse('I change the text of "{filename}" to:'))
def change_text(students, context, filename, docstring):
    _change(students, context, filename, docstring)


# a regular expression, as the text may be empty
@when(parsers.re(r'I change the text of "(?P<filename>[^"]+)" to "(?P<text>[^"]*)"'))
def change_text_to(students, context, filename, text):
    _change(students, context, filename, text)


@when(parsers.parse('the student "{name}" changes the text of "{filename}" to "{text}"'))
def student_changes_text(students, context, name, filename, text):
    _change(students, context, filename, text, name=name)


@when(parsers.parse('"{filename}" is eventually ready'))
@then(parsers.parse('"{filename}" is eventually ready'))
def eventually_ready(students, context, filename):
    students.wait_until_ingested(context["response"])
    # what follows reads the material as it is now
    context["response"] = students.open(students.find_material(filename))


@then(parsers.parse('I read "{text}" in the section "{title}" of "{filename}"'))
def read_in_section(students, text, title, filename):
    material = students.find_material(filename)
    sections = students.open(material).json()["sections"]
    position = next(s["position"] for s in sections if s["title"] == title)
    response = students.read_section(material, position)
    assert response.status_code == 200, response.text
    assert text in "\n".join(part["content"] for part in response.json())


@when(parsers.parse('I open "{filename}" for editing'))
def open_for_editing(students, context, filename):
    context["response"] = students.client.get(_text_path(students.find_material(filename)), headers=students.headers())
    context["filename"] = filename


@then("I am given its text exactly as I uploaded it")
def given_its_text(context):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.json()["text"] == context["uploaded"][context["filename"]].decode()


@then("I am told only Markdown and text material can be edited")
def only_text(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "only Markdown and text material can be edited" in response.json()["detail"]


@then("I am told the material cannot be empty")
def cannot_be_empty(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "cannot be empty" in response.json()["detail"]


@then(parsers.parse('the note "{text}" is detached, as its passage "{passage}" is no longer there'))
def note_detached(students, text, passage):
    material = students.find_material("fem-notes.md")
    notes = students.client.get(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/notes", headers=students.headers()
    ).json()
    note = next(n for n in notes if n["text"] == text)
    assert note["detached"] and note["passage"] == passage

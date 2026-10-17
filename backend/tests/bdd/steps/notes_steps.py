from pytest_bdd import given, parsers, then, when

from tests.videos import make_mp4


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row)) for row in rows]


def _seconds(moment: str) -> float:
    """e.g. "12:30" as 750"""
    seconds = 0
    for part in moment.split(":"):
        seconds = seconds * 60 + int(part)
    return float(seconds)


def _moment(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def _notes_path(material: dict) -> str:
    return f"/api/courses/{material['course_id']}/materials/{material['document_id']}/notes"


def _section(students, material: dict, title: str) -> int:
    opened = students.open(material)
    assert opened.status_code == 200, opened.text
    return next(s["position"] for s in opened.json()["sections"] if s["title"] == title)


def _note_on_passage(client, students, text, passage, title, filename, name=None):
    # the material is found as the owner sees it; the note is taken as the student
    material = students.find_material(filename)
    body = {"text": text, "section": _section(students, material, title), "passage": passage}
    return client.post(_notes_path(material), headers=students.headers(name), json=body)


def _notes(client, students, filename, name=None) -> list[dict]:
    response = client.get(_notes_path(students.find_material(filename)), headers=students.headers(name))
    assert response.status_code == 200, response.text
    return response.json()


def _note_id(client, students, text) -> str:
    response = client.get("/api/notes", headers=students.headers())
    return next(note["id"] for note in response.json() if note["text"] == text)


# taking notes


@when(parsers.parse('I note "{text}" on "{passage}" in "{title}" of "{filename}"'))
def note_on_passage(client, students, context, text, passage, title, filename):
    context["response"] = _note_on_passage(client, students, text, passage, title, filename)


@given(parsers.parse('I have noted "{text}" on "{passage}" in "{title}" of "{filename}"'))
def have_noted(client, students, text, passage, title, filename):
    response = _note_on_passage(client, students, text, passage, title, filename)
    assert response.status_code == 201, response.text


@when(parsers.parse('the student "{name}" notes "{text}" on "{passage}" in "{title}" of "{filename}"'))
def student_notes(client, students, context, name, text, passage, title, filename):
    context["response"] = _note_on_passage(client, students, text, passage, title, filename, name=name)
    assert context["response"].status_code == 201, context["response"].text


@given(parsers.parse('I have uploaded the video "{filename}" to "{location}"'))
def have_uploaded_video(students, filename, location):
    students.wait_until_ingested(students.upload(location, filename, make_mp4(3600)))


@given(parsers.parse('I have uploaded the {minutes:d}-minute video "{filename}" to "{location}"'))
def have_uploaded_video_of(students, minutes, filename, location):
    students.wait_until_ingested(students.upload(location, filename, make_mp4(minutes * 60)))


@when(parsers.parse('I note "{text}" at {moment} of "{filename}"'))
def note_at_moment(client, students, context, text, moment, filename):
    material = students.find_material(filename)
    context["response"] = client.post(
        _notes_path(material), headers=students.headers(), json={"text": text, "at_seconds": _seconds(moment)}
    )


# listing


@when(parsers.parse('I list the notes of "{filename}"'))
def list_notes(client, students, context, filename):
    context["notes"] = _notes(client, students, filename)


@then(parsers.parse('the notes of "{filename}" are:'))
def notes_are(client, students, filename, datatable):
    rows = _rows(datatable)
    notes = _notes(client, students, filename)
    if "at" in rows[0]:
        seen = [{"at": _moment(n["at_seconds"]), "note": n["text"]} for n in notes]
    else:
        seen = [{"section": n["section_title"], "passage": n["passage"], "note": n["text"]} for n in notes]
    assert seen == rows


@then(parsers.parse('"{filename}" has no notes'))
def has_no_notes(client, students, filename):
    assert _notes(client, students, filename) == []


@then("I have no notes")
def i_have_no_notes(client, students):
    response = client.get("/api/notes", headers=students.headers())
    assert response.json() == []


@then(parsers.parse('the student "{name}" sees no notes on "{filename}"'))
def student_sees_no_notes(client, students, name, filename):
    assert _notes(client, students, filename, name=name) == []


@then(parsers.parse('the student "{name}" sees {count:d} note on "{filename}"'))
def student_sees_notes(client, students, name, count, filename):
    assert len(_notes(client, students, filename, name=name)) == count


# refusals


@then("I am told the passage is not in that section")
def passage_not_in_section(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "not in that section" in response.json()["detail"]


@then(parsers.parse("I am told the video is only {length} long"))
def video_is_only(context, length):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"only {length} long" in response.json()["detail"]


# changing


@when(parsers.parse('I change the note "{text}" to "{new_text}"'))
def change_note(client, students, text, new_text):
    response = client.patch(
        f"/api/notes/{_note_id(client, students, text)}", headers=students.headers(), json={"text": new_text}
    )
    assert response.status_code == 200, response.text


@when(parsers.parse('I delete the note "{text}"'))
def delete_note(client, students, text):
    response = client.delete(f"/api/notes/{_note_id(client, students, text)}", headers=students.headers())
    assert response.status_code == 204, response.text

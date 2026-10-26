"""Steps of lessons.feature: making a subject's lessons from a document."""

import time

from pytest_bdd import given, parsers, then, when

from qubit_notes.domain.conversions import ORIGINAL_KIND
from qubit_notes.domain.images import KIND
from tests.bdd.steps.converting_steps import PICTURED_TEXT
from tests.epubs import make_epub
from tests.pdfs import make_pdf, make_pdf_with_picture, make_scanned_pdf

TWO_LESSONS = b"# 1 Introduction\nSmall elements.\n\n# 2 Shape functions\nInterpolation.\n"


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row, strict=True)) for row in rows]


def _make(students, context, location: str, filename: str, content: bytes, name: str | None = None) -> None:
    context.setdefault("uploaded", {})[filename] = content
    context["lessons_from"] = filename
    course, subject = location.split("/")
    context["response"] = students.client.post(
        f"/api/courses/{course}/subjects/{subject}/lessons",
        headers=students.headers(name),
        files={"file": (filename, content)},
    )


def _made(students, context) -> dict:
    """the lessons once they're made, or it failed, and their material once it's processed"""
    response = context["response"]
    assert response.status_code == 202, response.text
    made = response.json()
    deadline = time.monotonic() + 60
    while made["status"] not in ("completed", "failed") and time.monotonic() < deadline:
        time.sleep(0.5)
        made = students.client.get(f"/api/lesson-imports/{made['id']}", headers=students.headers()).json()
    if made["status"] == "completed":
        course = next(c["name"] for c in students.courses() if c["id"] == made["course_id"])
        while time.monotonic() < deadline:
            materials = students.materials(course, subject=made["subject"])
            if all(m["status"] in ("completed", "failed") for m in materials):
                break
            time.sleep(0.5)
    return made


def _material(students, location: str, topic: str) -> dict:
    course, subject = location.split("/")
    (material,) = students.materials(course, subject=subject, topic=topic)
    return material


# making lessons


@when(parsers.parse('I make lessons in "{location}" from a PDF "{filename}" with the pages:'))
def from_pdf(students, context, location, filename, datatable):
    pages = _rows(datatable)
    outline = [(p["outline"], int(p["level"]), int(p["page"])) for p in pages if p["outline"]]
    _make(students, context, location, filename, make_pdf([p["text"] for p in pages], outline=outline))


@given(parsers.parse('I have made lessons in "{location}" from a PDF "{filename}" with the pages:'))
def have_made_from_pdf(students, context, location, filename, datatable):
    from_pdf(students, context, location, filename, datatable)
    made = _made(students, context)
    assert made["status"] == "completed", made


@when(parsers.parse('I make lessons in "{location}" from an EPUB "{filename}" with the chapters:'))
def from_epub(students, context, location, filename, datatable):
    _, *rows = datatable
    _make(students, context, location, filename, make_epub([(title, text) for title, text in rows]))


@when(parsers.parse('I make lessons in "{location}" from the Markdown "{filename}":'))
def from_markdown(students, context, location, filename, docstring):
    _make(students, context, location, filename, docstring.encode())


@when(parsers.parse('I make lessons in "{location}" from a PDF "{filename}" with a picture in its section "{title}"'))
def from_pdf_with_picture(students, context, location, filename, title):
    _make(students, context, location, filename, make_pdf_with_picture(title, PICTURED_TEXT))


@when(parsers.parse('I make lessons in "{location}" from the file "{filename}"'))
def from_file(students, context, location, filename):
    _make(students, context, location, filename, b"not a document")


@when(parsers.parse('I make lessons in "{location}" from a PDF of pictures only "{filename}"'))
def from_scan(students, context, location, filename):
    _make(students, context, location, filename, make_scanned_pdf())


@when(parsers.parse('the student "{name}" makes lessons in "{location}" from the Markdown "{filename}"'))
def they_make_lessons(students, context, name, location, filename):
    _make(students, context, location, filename, TWO_LESSONS, name=name)


@given(parsers.parse('the app stopped while making lessons in "{location}" from the Markdown "{filename}":'))
def stopped_while_making(client, students, context, location, filename, docstring, monkeypatch):
    # the lessons are started, but not made
    with monkeypatch.context() as patched:
        patched.setattr(client.app.state.lessons, "_submit", lambda import_id: None)
        _make(students, context, location, filename, docstring.encode())


@when("the app starts again")
def app_starts_again(client):
    client.app.state.lessons.resume()


# the lessons made


@then("the lessons are made")
def lessons_made(students, context):
    made = _made(students, context)
    assert made["status"] == "completed", made


@then(parsers.parse('the subject "{subject}" of "{course}" has the lessons:'))
def has_lessons(students, context, subject, course, datatable):
    made = _made(students, context)
    assert made["status"] == "completed", made
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers())
    topics = [t for t in response.json() if t["subject"] == subject]
    materials = students.materials(course, subject=subject)
    seen = [
        {
            "lesson": t["name"],
            "topic": t["topic"],
            "material": ", ".join(m["filename"] for m in materials if m["topic"] == t["topic"]),
        }
        for t in topics
    ]
    assert seen == _rows(datatable)
    assert made["topics"] == [row["topic"] for row in _rows(datatable)]
    assert all(m["status"] == "completed" for m in materials), materials


@then(parsers.parse('I read "{text}" in the lesson "{topic}" of "{location}"'))
def read_in_lesson(students, text, topic, location):
    material = _material(students, location, topic)
    sections = students.open(material).json()["sections"]
    read = [students.read_section(material, s["position"]).json() for s in sections]
    assert text in "\n".join(part["content"] for parts in read for part in parts)


@then(parsers.parse('the lesson "{topic}" of "{location}" has the sections:'))
def lesson_sections(students, context, topic, location, datatable):
    _made(students, context)
    response = students.open(_material(students, location, topic))
    assert response.status_code == 200, response.text
    seen = [{"section": s["title"], "level": str(s["level"])} for s in response.json()["sections"]]
    assert seen == _rows(datatable)


@then(parsers.parse('the lesson "{topic}" of "{location}" has that image, and is missing none'))
def lesson_image(students, context, topic, location):
    _made(students, context)
    material = _material(students, location, topic)
    response = students.client.get(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/images", headers=students.headers()
    )
    assert response.status_code == 200, response.text
    assert len(response.json()["images"]) == 1 and response.json()["missing"] == [], response.json()


@then("I am told to make lessons from a PDF, an EPUB or a Markdown file")
def told_which_files(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "make lessons from a PDF, an EPUB or a Markdown file" in response.json()["detail"]


@then(parsers.parse('making the lessons fails, as "{filename}" has no text to convert, as it may be scanned'))
def making_fails(students, context, filename):
    made = _made(students, context)
    assert made["status"] == "failed", made
    assert f"{filename!r} has no text to convert, as it may be scanned" in made["error"]


@then(parsers.parse('the subject "{subject}" of "{course}" has no topics'))
def no_topics(students, subject, course):
    response = students.client.get(f"/api/courses/{course}/topics", headers=students.headers())
    assert [t for t in response.json() if t["subject"] == subject] == []


# the original


@when(parsers.parse('I download the original of the lesson "{topic}" of "{location}"'))
def download_lesson_original(students, context, topic, location):
    context["response"] = students.download(_material(students, location, topic))
    context["filename"] = context["lessons_from"]


@when(parsers.parse('I download the lesson "{topic}" of "{location}" as it is now'))
def download_lesson_now(students, context, topic, location):
    context["response"] = students.export(_material(students, location, topic))


@when(parsers.parse('I download the lesson "{topic}" of "{location}"'))
def download_lesson(students, context, topic, location):
    _made(students, context)
    context["response"] = students.download(_material(students, location, topic))


@then(parsers.parse('I get its own text, which does not include "{text}"'))
def own_text(context, text):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.content.decode().startswith("# ")
    assert text not in response.content.decode()


def _originals(client, students, course: str, filename: str) -> list:
    course_id = next(c["id"] for c in students.courses() if c["name"] == course)
    found = client.app.state.platform.list_documents(course_id, {KIND: ORIGINAL_KIND})
    return [document for document in found if document.filename == filename]


@then(parsers.parse('the original "{filename}" is kept in "{course}"'))
def original_kept(client, students, filename, course):
    assert len(_originals(client, students, course, filename)) == 1


@then(parsers.parse('the original "{filename}" is no longer kept in "{course}"'))
def original_gone(client, students, filename, course):
    assert _originals(client, students, course, filename) == []


# the subject's originals


def _subject_originals(students, subject: str, course: str, name: str | None = None) -> list[dict]:
    response = students.client.get(
        f"/api/courses/{course}/subjects/{subject}/originals", headers=students.headers(name)
    )
    assert response.status_code == 200, response.text
    return response.json()


@then(parsers.parse('the subject "{subject}" of "{course}" has the originals:'))
def has_originals(students, subject, course, datatable):
    seen = [
        {"original": o["filename"], "lessons": ", ".join(lesson["topic"] for lesson in o["lessons"])}
        for o in _subject_originals(students, subject, course)
    ]
    expected = [{key: value.strip() for key, value in row.items()} for row in _rows(datatable)]
    assert seen == expected


@then(parsers.parse('the subject "{subject}" of "{course}" has no originals'))
def has_no_originals(students, subject, course):
    assert _subject_originals(students, subject, course) == []


@then(parsers.parse('the student "{name}" sees the originals of "{subject}" in "{course}": "{filenames}"'))
def they_see_originals(students, name, subject, course, filenames):
    assert [o["filename"] for o in _subject_originals(students, subject, course, name)] == filenames.split('", "')

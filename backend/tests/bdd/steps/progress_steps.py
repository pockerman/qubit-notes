"""Steps of reading_progress.feature and of the sections marked as opened in the reader."""

import re

from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage

OPENED = re.compile(r"\bopened\b")


def _paths(students, filename: str) -> tuple[dict, str]:
    material = students.find_material(filename)
    return material, f"/api/courses/{material['course_id']}/materials/{material['document_id']}"


def _position(students, title: str, filename: str) -> int:
    opened = students.open(students.find_material(filename)).json()
    return next(section["position"] for section in opened["sections"] if section["title"] == title)


def _open_section(students, position: int, filename: str, name=None):
    _, path = _paths(students, filename)
    return students.client.post(f"{path}/sections/{position}/opened", headers=students.headers(name))


def _progress(students, filename: str, name=None) -> dict:
    _, path = _paths(students, filename)
    response = students.client.get(f"{path}/progress", headers=students.headers(name))
    assert response.status_code == 200, response.text
    return response.json()


@when(parsers.parse('I open the section "{title}" of "{filename}"'))
@given(parsers.parse('I have opened the section "{title}" of "{filename}"'))
def open_section(students, context, title, filename):
    context["response"] = _open_section(students, _position(students, title, filename), filename)
    assert context["response"].status_code == 200, context["response"].text


@when(parsers.parse('I open section {position:d} of "{filename}"'))
def open_section_at(students, context, position, filename):
    context["response"] = _open_section(students, position, filename)


@when(parsers.parse('the student "{name}" opens the section "{title}" of "{filename}"'))
def they_open_section(students, context, name, title, filename):
    context["response"] = _open_section(students, _position(students, title, filename), filename, name=name)


@then("I am told there is no such section")
def told_no_section(context):
    assert context["response"].status_code == 404, context["response"].text


@then(parsers.parse('I have opened {count:d} of the {sections:d} sections of "{filename}"'))
def have_opened(students, count, sections, filename):
    progress = _progress(students, filename)
    assert (len(progress["opened"]), progress["sections"]) == (count, sections)


@then(parsers.parse('the student "{name}" has opened {count:d} of the {sections:d} sections of "{filename}"'))
def they_have_opened(students, name, count, sections, filename):
    progress = _progress(students, filename, name=name)
    assert (len(progress["opened"]), progress["sections"]) == (count, sections)


@then(parsers.parse('I have opened the sections "{titles}" of "{filename}"'))
def have_opened_titles(students, titles, filename):
    wanted = [_position(students, title.strip(), filename) for title in titles.split(",")]
    assert _progress(students, filename)["opened"] == wanted


@then(parsers.parse('every time I opened "{filename}" is kept: {count:d}'))
def every_time_kept(client, students, filename, count):
    table = storage.section_opens
    document_id = students.find_material(filename)["document_id"]
    with client.app.state.database.connect() as connection:
        assert len(connection.execute(select(table).where(table.c.document_id == document_id)).all()) == count


@then("nothing is kept of what I opened")
def nothing_kept(client, students):
    table = storage.section_opens
    with client.app.state.database.connect() as connection:
        rows = connection.execute(select(table).where(table.c.student == students.id(students.me))).all()
    assert rows == []


@then(parsers.parse('the sections "{titles}" are marked as opened'))
def sections_marked(page, titles):
    from playwright.sync_api import expect

    for title in titles.split(","):
        section = page.get_by_role("navigation", name="Sections").get_by_role("button", name=title.strip(), exact=True)
        expect(section).to_have_class(OPENED)


@then(parsers.parse('the section "{title}" is not marked as opened'))
def section_not_marked(page, title):
    from playwright.sync_api import expect

    section = page.get_by_role("navigation", name="Sections").get_by_role("button", name=title, exact=True)
    expect(section).not_to_have_class(OPENED)

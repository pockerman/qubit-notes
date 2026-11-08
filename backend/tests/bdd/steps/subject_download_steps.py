"""Steps of subject_download.feature: a subject as a zip."""

import csv
import io
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote

from pytest_bdd import given, parsers, then, when


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row)) for row in rows]


def _download(students, context, subject: str, course: str, name: str | None = None) -> None:
    context["response"] = students.client.get(
        f"/api/courses/{course}/subjects/{subject}/zip", headers=students.headers(name)
    )


def _zip(context) -> zipfile.ZipFile:
    response = context["response"]
    assert response.status_code == 200, response.text
    return zipfile.ZipFile(io.BytesIO(response.content))


def _cards(context) -> list[dict]:
    return list(csv.DictReader(io.StringIO(_zip(context).read("flashcards.csv").decode())))


@given(parsers.parse('I have put the topics of "{subject}" of "{course}" in the order "{topics}"'))
def topics_in_order(students, subject, course, topics):
    response = students.client.put(
        f"/api/courses/{course}/subjects/{subject}/topic-order",
        headers=students.headers(),
        json={"topics": [t.strip() for t in topics.split(",")]},
    )
    assert response.status_code == 200, response.text


@when(parsers.parse('I download the subject "{subject}" of "{course}"'))
def download(students, context, subject, course):
    _download(students, context, subject, course)


@when(parsers.parse('the student "{name}" downloads the subject "{subject}" of "{course}"'))
def student_downloads(students, context, name, subject, course):
    _download(students, context, subject, course, name)


@then(parsers.parse('I get "{filename}"'))
def get_file(context, filename):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/zip"
    disposition = response.headers["content-disposition"]
    assert unquote(disposition.split("filename*=UTF-8''")[1]) == filename
    assert _zip(context).testzip() is None


@then("it has the files:")
def has_files(context, datatable):
    files = sorted(info.filename for info in _zip(context).infolist() if not info.is_dir())
    assert files == sorted(row["file"] for row in _rows(datatable))


@then(parsers.parse('it has the file "{path}"'))
def has_file(context, path):
    assert path in _zip(context).namelist(), _zip(context).namelist()


@then(parsers.parse('"{path}" in it is the material "{filename}" as it is now'))
def is_material(students, context, path, filename):
    material = students.find_material(filename)
    response = students.client.get(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/text", headers=students.headers()
    )
    assert response.status_code == 200, response.text
    assert _zip(context).read(path).decode() == response.json()["text"]


@then(parsers.parse('"{path}" in it is the file I uploaded as "{filename}"'))
def is_uploaded(context, path, filename):
    assert _zip(context).read(path) == context["uploaded"][filename]


@then(parsers.parse('"{path}" in it is the image I added'))
def is_image(context, path):
    added = next(iter(context["added"].values()))
    assert _zip(context).read(path) == added


@then(parsers.parse('flashcards.csv in it has {count:d} cards from "{filename}"'))
def cards_from(context, count, filename):
    cards = _cards(context)
    assert len(cards) == count, cards
    assert {card["material"] for card in cards} == {filename}
    assert all(card["front"] and card["back"] and card["topic"] and card["section"] for card in cards)


@then("flashcards.csv in it has no cards")
def no_cards(context):
    assert _cards(context) == []


@then("flashcards.md in it has the cards of flashcards.csv")
def markdown_has_cards(context):
    markdown = _zip(context).read("flashcards.md").decode()
    for card in _cards(context):
        assert card["front"] in markdown
        assert card["back"] in markdown


@then("the download is refused as not found")
def refused(context):
    assert context["response"].status_code == 404, context["response"].text


@then("the zip isn't kept on the server once it is sent")
def not_kept(context):
    assert list(Path(tempfile.gettempdir()).glob("qubit-notes-*.zip")) == []


# in the browser


@when("I download the subject as a zip")
def download_in_browser(page, context):
    with page.expect_download() as download:
        page.get_by_role("button", name="Download as zip").click()
    context["download"] = download.value


@then(parsers.parse('I get the zip "{filename}" with "{path}"'))
def got_zip(context, filename, path):
    download = context["download"]
    assert download.suggested_filename == filename
    with zipfile.ZipFile(download.path()) as archive:
        assert path in archive.namelist(), archive.namelist()

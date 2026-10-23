"""PDF and EPUB material as Markdown: converting them, editing them, and downloading them as they were and are."""

import re
import time
import unicodedata
from io import BytesIO

import pymupdf
from ebooklib import ITEM_DOCUMENT, epub
from pytest_bdd import given, parsers, then, when

from tests.epubs import make_epub
from tests.pdfs import make_pdf, make_pdf_of_lines, make_pdf_with_picture, make_scanned_pdf, picture

PICTURED_TEXT = "The domain is divided into triangles."


def _upload(students, context, location: str, filename: str, content: bytes) -> None:
    context.setdefault("uploaded", {})[filename] = content
    students.wait_until_ingested(students.upload(location, filename, content))


@given(parsers.parse('I have uploaded a PDF "{filename}" to "{location}" with the pages:'))
def uploaded_pdf_pages(students, context, filename, location, datatable):
    header, *rows = datatable
    pages = [dict(zip(header, row, strict=True)) for row in rows]
    outline = [(p["outline"], int(p["level"]), int(p["page"])) for p in pages if p["outline"]]
    _upload(students, context, location, filename, make_pdf([p["text"] for p in pages], outline=outline))


@given(parsers.parse('I have uploaded a PDF "{filename}" to "{location}" with the lines:'))
def uploaded_pdf_lines(students, context, filename, location, datatable):
    _, *rows = datatable
    _upload(students, context, location, filename, make_pdf_of_lines([(text, float(size)) for text, size in rows]))


@given(parsers.parse('I have uploaded an EPUB "{filename}" to "{location}" with the chapters:'))
def uploaded_epub(students, context, filename, location, datatable):
    _, *rows = datatable
    _upload(students, context, location, filename, make_epub([(title, text) for title, text in rows]))


@given(
    parsers.re(
        r'I have uploaded (?P<kind>a PDF|an EPUB) "(?P<filename>[^"]+)" with a picture in its section '
        r'"(?P<title>[^"]+)" to "(?P<location>[^"]+)"'
    )
)
def uploaded_with_picture(students, context, kind, filename, title, location):
    if kind == "a PDF":
        content = make_pdf_with_picture(title, PICTURED_TEXT)
    else:
        content = make_epub([(title, PICTURED_TEXT)], picture_in=title, picture=picture())
    _upload(students, context, location, filename, content)


@when(parsers.parse('I upload a PDF "{filename}" of pictures only to "{location}"'))
def upload_scan(students, context, filename, location):
    context["response"] = students.upload(location, filename, make_scanned_pdf())


@given(parsers.parse('I have changed the text of "{filename}" to:'))
def changed_text(students, context, filename, docstring):
    material = students.find_material(filename)
    response = students.client.put(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/text",
        headers=students.headers(),
        json={"text": docstring},
    )
    students.wait_until_ingested(response)


# what was converted


def _sections_of(markdown: str) -> dict[str, str]:
    """each heading's text, up to the next heading"""
    found, title = {}, None
    for line in markdown.splitlines():
        match = re.match(r"^#{1,6}\s+(.*?)\s*$", line)
        if match:
            title = match.group(1)
            found[title] = ""
        elif title is not None:
            found[title] += line + "\n"
    return found


@then(parsers.parse('its text shows an image in the section "{title}"'))
def shows_image(context, title):
    response = context["response"]
    assert response.status_code == 200, response.text
    section = _sections_of(response.json()["text"])[title]
    assert PICTURED_TEXT in section
    assert re.search(r"!\[[^\]]*\]\([^)]+\)", section), section


@then(parsers.parse('"{filename}" has that image, and is missing none'))
def has_the_image(students, filename):
    material = students.find_material(filename)
    response = students.client.get(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/images", headers=students.headers()
    )
    assert response.status_code == 200, response.text
    assert len(response.json()["images"]) == 1 and response.json()["missing"] == [], response.json()


@then(parsers.parse('the material "{filename}" fails to be processed'))
def fails(students, context, filename):
    job_id = context["response"].json()["job_id"]
    deadline = time.monotonic() + 30
    while True:
        job = students.client.get(f"/api/uploads/{job_id}", headers=students.headers()).json()
        if job["status"] in ("completed", "failed") or time.monotonic() > deadline:
            break
        time.sleep(0.2)
    assert job["status"] == "failed", job
    context["job"] = job
    assert students.find_material(filename)["status"] == "failed"


@then(parsers.parse('I am told "{filename}" has no text to convert, as it may be scanned'))
def told_no_text(students, context, filename):
    assert "has no text to convert, as it may be scanned" in context["job"]["error"]
    assert "has no text to convert" in students.find_material(filename)["error"]


@then(parsers.parse('I am given Markdown with the headings "{first}" and "{second}"'))
def given_markdown(context, first, second):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert {first, second} <= set(_sections_of(response.json()["text"]))


# downloads


@when(parsers.parse('I download the original of "{filename}"'))
def download_original(students, context, filename):
    context["response"] = students.download(students.find_material(filename))
    context["filename"] = filename


@when(parsers.parse('I download "{filename}" as it is now'))
def download_now(students, context, filename):
    context["response"] = students.export(students.find_material(filename))


@when(parsers.parse('the student "{name}" downloads the original of "{filename}"'))
def they_download_original(students, context, name, filename):
    context["response"] = students.download(students.find_material(filename, name=name), name=name)
    context["filename"] = filename


@when(parsers.parse('the student "{name}" downloads "{filename}" as it is now'))
def they_download_now(students, context, name, filename):
    context["response"] = students.export(students.find_material(filename, name=name), name=name)


@then(parsers.parse('the student "{name}" gets the file exactly as I uploaded it'))
def they_get_the_file(context, name):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.content == context["uploaded"][context["filename"]]


def _text(response) -> str:
    if response.headers["content-type"].startswith("application/pdf"):
        document = pymupdf.open(stream=response.content, filetype="pdf")
        text = "".join(page.get_text() for page in document)
    else:
        book = epub.read_epub(BytesIO(response.content))
        text = "".join(item.get_content().decode() for item in book.get_items_of_type(ITEM_DOCUMENT))
    # ligatures, e.g. "ﬁ", as the letters they join
    return " ".join(unicodedata.normalize("NFKC", text).split())


@then(parsers.parse('I get a PDF called "{filename}"'))
@then(parsers.parse('the student "{name}" gets a PDF called "{filename}"'))
def got_pdf(context, filename, name=None):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/pdf")
    assert filename in response.headers["content-disposition"]
    assert pymupdf.open(stream=response.content, filetype="pdf").page_count >= 1


@then(parsers.parse('I get an EPUB called "{filename}" with the chapter "{chapter}"'))
def got_epub(context, filename, chapter):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/epub+zip")
    assert filename in response.headers["content-disposition"]
    book = epub.read_epub(BytesIO(response.content))
    assert chapter in [entry.title for entry in book.toc]


@then(parsers.parse('its text includes "{text}"'))
def text_includes(context, text):
    assert text in _text(context["response"])


@then(parsers.parse('its text does not include "{text}"'))
def text_excludes(context, text):
    assert text not in _text(context["response"])


@then(parsers.parse("I get a PDF with {count:d} picture"))
def pdf_with_pictures(context, count):
    response = context["response"]
    assert response.status_code == 200, response.text
    document = pymupdf.open(stream=response.content, filetype="pdf")
    assert sum(len(page.get_images()) for page in document) == count

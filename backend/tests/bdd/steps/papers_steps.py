"""Steps of papers.feature: collections of papers, apart from courses, and the papers in them."""

import re

import pymupdf
from playwright.sync_api import expect
from pytest_bdd import given, parsers, then, when

from tests.bdd.steps.sharing_steps import ROLE
from tests.bdd.steps.ui_steps import choose_from_menu
from tests.pdfs import make_pdf

DETAILS = ("title", "authors", "year", "venue", "doi")


def _create(students, name: str, title: str):
    return students.client.post(
        "/api/papers/collections", headers=students.headers(), json={"name": name, "title": title}
    )


def _upload(students, collection: str, filename: str, content: bytes | None = None, *, name: str | None = None):
    if content is None:
        content = f"# {filename}\n\nNotes on {collection}.\n".encode()
    collection_id = students.collection(collection, name=name)["id"]
    return students.client.post(
        f"/api/papers/collections/{collection_id}/papers",
        headers=students.headers(name),
        files={"file": (filename, content)},
    )


def _uploaded(students, collection: str, filename: str, content: bytes | None = None):
    response = _upload(students, collection, filename, content)
    assert response.status_code == 202, response.text
    students.wait_until_ingested(response)


def _paper(students, collection: str, filename: str, *, name: str | None = None) -> dict:
    collection_id = students.collection(collection, name=name)["id"]
    return next(p for p in students.papers(collection_id, name=name) if p["material"]["filename"] == filename)


def _describe(students, filename: str, details: dict, *, name: str | None = None):
    material = students.find_material(filename, name=name)
    return students.client.put(
        f"/api/papers/collections/{material['course_id']}/papers/{material['document_id']}/details",
        headers=students.headers(name),
        json=details,
    )


def _details(rows: list[list[str]]) -> dict:
    """the details of a two-column table, e.g. | year | 2017 |, as the API has them"""
    given = {key: value.strip() for key, value in rows}
    details = {"title": "", "authors": [], "year": None, "venue": "", "doi": "", **given}
    if "authors" in given:
        details["authors"] = [author.strip() for author in given["authors"].split(",") if author.strip()]
    if given.get("year"):
        details["year"] = int(given["year"])
    return details


# collections


@when(parsers.parse('I create the collection "{name}" titled "{title}"'))
def create(students, context, name, title):
    context["response"] = _create(students, name, title)


@given(parsers.parse('I have created the collection "{name}" titled "{title}"'))
def have_created(students, name, title):
    response = _create(students, name, title)
    assert response.status_code == 201, response.text


@then("my collections are:")
def my_collections(students, datatable):
    found = [[c["name"], c["title"]] for c in students.collections()]
    assert [["collection", "title"], *found] == datatable


@then("I have no collections")
def no_collections(students):
    assert students.collections() == []


@then("I have no courses")
def no_courses(students):
    assert students.courses() == []


@then(parsers.parse('I am told I already have a course or a collection called "{name}"'))
def told_name_taken(context, name):
    response = context["response"]
    assert response.status_code == 409, response.text
    assert f"already have a course or a collection called {name!r}" in response.json()["detail"]


@when(parsers.parse('I delete the collection "{name}"'))
def delete_collection(students, name):
    collection_id = students.collection(name)["id"]
    response = students.client.delete(f"/api/papers/collections/{collection_id}", headers=students.headers())
    assert response.status_code == 204, response.text


# papers


@when(parsers.parse('I upload the paper "{filename}" to "{collection}" with the content:'))
@given(parsers.parse('I have uploaded the paper "{filename}" to "{collection}" with the content:'))
def upload_with_content(students, filename, collection, docstring):
    _uploaded(students, collection, filename, docstring.encode())


@given(parsers.parse('I have uploaded the paper "{filename}" to "{collection}"'))
def have_uploaded(students, filename, collection):
    _uploaded(students, collection, filename)


@when(parsers.parse('I upload the paper "{filename}" to "{collection}", whose pages read:'))
def upload_pdf(students, filename, collection, datatable):
    pages = [text for text, _ in datatable[1:]]
    outline = [(title, 1, page) for page, (_, title) in enumerate(datatable[1:], start=1)]
    _uploaded(students, collection, filename, make_pdf(pages, outline))


@when(
    parsers.parse(
        'I upload the paper "{filename}" to "{collection}", a PDF titled "{title}" by "{authors}" whose first page '
        'reads "{text}"'
    )
)
def upload_described_pdf(students, filename, collection, title, authors, text):
    document = pymupdf.open()
    document.new_page().insert_text((72, 72), text, fontsize=11)
    document.set_metadata({"title": title, "author": authors})
    _uploaded(students, collection, filename, document.tobytes())


@when(parsers.parse('I upload the paper "{filename}" to "{collection}"'))
def upload(students, context, filename, collection):
    context["response"] = _upload(students, collection, filename, b"not a paper")


@when(parsers.parse('the student "{name}" uploads the paper "{filename}" to "{collection}"'))
def they_upload(students, context, name, filename, collection):
    context["response"] = _upload(students, collection, filename, name=name)


@then("I am told a paper must be a PDF, an EPUB, a Markdown or a text file")
def told_not_a_paper(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "a paper must be a PDF, an EPUB, a Markdown or a text file" in response.json()["detail"]


@then(parsers.parse('the papers of "{collection}" are:'))
def papers_are(students, collection, datatable):
    collection_id = students.collection(collection)["id"]
    found = [[p["material"]["filename"], p["details"]["title"]] for p in students.papers(collection_id)]
    assert [["paper", "title"], *found] == datatable


@then(parsers.parse('"{collection}" has no papers'))
def no_papers(students, collection):
    assert students.papers(students.collection(collection)["id"]) == []


@then(parsers.parse('"{filename}" is read by its sections "{titles}"'))
def read_by_sections(students, filename, titles):
    opened = students.open(students.find_material(filename))
    assert opened.status_code == 200, opened.text
    assert [s["title"] for s in opened.json()["sections"]] == [t.strip() for t in titles.split(",")]


@when(parsers.parse('I delete the paper "{filename}" from "{collection}"'))
def delete_paper(students, filename, collection):
    paper = _paper(students, collection, filename)
    response = students.client.delete(
        f"/api/papers/collections/{paper['material']['course_id']}/papers/{paper['material']['document_id']}",
        headers=students.headers(),
    )
    assert response.status_code == 200, response.text


# details


@when(parsers.parse('I change the details of "{filename}" to:'))
def change_details(students, context, filename, datatable):
    context["response"] = _describe(students, filename, _details(datatable))


@when(parsers.parse('the student "{name}" changes the title of the paper "{filename}" to "{title}"'))
def they_change_title(students, context, name, filename, title):
    context["response"] = _describe(students, filename, {"title": title}, name=name)


@then(parsers.parse('the details of "{filename}" are:'))
def details_are(students, filename, datatable):
    material = students.find_material(filename)
    response = students.client.get(
        f"/api/papers/collections/{material['course_id']}/papers/{material['document_id']}",
        headers=students.headers(),
    )
    assert response.status_code == 200, response.text
    assert response.json()["details"] == _details(datatable)


@then("I am told a paper needs a title")
def told_needs_title(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "a paper needs a title" in response.json()["detail"]


# the assistant


@given(parsers.parse('I am studying the collection "{collection}"'))
def studying_collection(students, context, collection):
    collection_id = students.collection(collection)["id"]
    context["where"] = {"course_id": collection_id, "subject": "papers", "topic": "papers"}


@then(parsers.parse('the answer does not cite "{filename}"'))
def does_not_cite(context, filename):
    assert filename not in {source["filename"] for source in context["turn"]["sources"]}, context["turn"]


# sharing


@when(parsers.parse('I share the collection "{collection}" with "{name}" as {role}'))
@given(parsers.parse('I have shared the collection "{collection}" with "{name}" as {role}'))
def share(students, collection, name, role):
    collection_id = students.collection(collection)["id"]
    response = students.client.put(
        f"/api/papers/collections/{collection_id}/members",
        headers=students.headers(),
        json={"student": students.id(name), "role": ROLE[role]},
    )
    assert response.status_code == 200, response.text


@then(parsers.parse('the student "{name}" sees the collections:'))
def they_see_collections(students, name, datatable):
    found = [[c["name"], students.name(c["owner"]), c["role"]] for c in students.collections(name=name)]
    assert [["collection", "owned by", "role"], *found] == datatable


@then(parsers.parse('the student "{name}" sees the papers "{filenames}" in "{collection}"'))
def they_see_papers(students, name, filenames, collection):
    collection_id = students.collection(collection, name=name)["id"]
    found = [p["material"]["filename"] for p in students.papers(collection_id, name=name)]
    assert found == [f.strip() for f in filenames.split(",")]


# in the browser


def _go_to_papers(page) -> None:
    # reloaded, as collections may have been created since the page was loaded
    page.goto("/#/papers")
    page.reload()
    expect(page.get_by_role("heading", name="My papers", level=2)).to_be_visible()


def _paper_item(page, title: str):
    titled = page.locator(".paper-title", has_text=re.compile(f"^{re.escape(title)}$"))
    return page.get_by_role("list", name="Papers").get_by_role("listitem").filter(has=titled)


@when("I go to my papers")
def go_to_papers(page):
    choose_from_menu(page, "My papers")
    expect(page.get_by_role("heading", name="My papers", level=2)).to_be_visible()


@when(parsers.re(r'I create the collection "(?P<title>[^"]+)"$'))
def create_in_browser(page, title):
    page.get_by_role("button", name="Create new collection").click()
    form = page.get_by_role("form", name="New collection")
    form.get_by_label("Collection name").fill(title)
    form.get_by_role("button", name="Create collection").click()


@then(parsers.parse('I am in the collection "{title}"'))
def in_collection(page, title):
    expect(page.get_by_role("heading", name=title, level=2)).to_be_visible()


@then("I see that it has no papers yet")
def no_papers_yet(page):
    expect(page.get_by_text("No papers yet")).to_be_visible()


@when(parsers.parse('I open the collection "{title}"'))
def open_collection(page, title):
    _go_to_papers(page)
    page.get_by_role("list", name="Collections").get_by_role("link", name=re.compile(f"^{re.escape(title)}\\b")).click()
    expect(page.get_by_role("heading", name=title, level=2)).to_be_visible()


@when(parsers.parse('I add the paper "{filename}" with the content:'))
def add_paper_in_browser(page, filename, docstring):
    form = page.get_by_role("form", name="Add a paper")
    form.get_by_label("Paper").set_input_files(
        {"name": filename, "mimeType": "text/markdown", "buffer": docstring.encode()}
    )
    form.get_by_role("button", name="Add paper").click()


@then(parsers.re(r'I see the paper "(?P<title>[^"]+)"$'))
def see_paper(page, title):
    # a link to read it once it's processed
    expect(_paper_item(page, title).get_by_role("link", name=title, exact=True)).to_be_visible(timeout=120_000)


@then(parsers.parse('I see the paper "{title}" by "{byline}"'))
def see_paper_by(page, title, byline):
    expect(_paper_item(page, title)).to_contain_text(byline)


@when(parsers.parse('I open the paper "{title}"'))
def open_paper(page, title):
    _paper_item(page, title).get_by_role("link", name=title, exact=True).click(timeout=120_000)
    expect(page.get_by_role("heading", name=title, level=2)).to_be_visible()


@then(parsers.parse('I am reading "{title}" of "{collection}"'))
def reading_paper(page, title, collection):
    header = page.locator(".reader-header")
    expect(header.get_by_role("heading", name=title, level=2)).to_be_visible()
    expect(header).to_contain_text(collection)


@when(
    parsers.parse(
        'I change the details of the paper "{title}" to the title "{new_title}", the authors "{authors}", the year '
        '"{year}" and the venue "{venue}"'
    )
)
def change_details_in_browser(page, title, new_title, authors, year, venue):
    page.get_by_role("button", name=f"Edit the details of {title}").click()
    form = page.get_by_role("form", name="Paper details")
    form.get_by_label("Title").fill(new_title)
    form.get_by_label("Authors").fill(authors)
    form.get_by_label("Year").fill(year)
    form.get_by_label("Venue").fill(venue)
    form.get_by_role("button", name="Save details").click()
    expect(form).to_have_count(0)

from pytest_bdd import given, parsers, then, when

from tests.pdfs import make_pdf


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row)) for row in rows]


def _position(students, material: dict, title: str) -> int:
    opened = students.open(material)
    assert opened.status_code == 200, opened.text
    return next(s["position"] for s in opened.json()["sections"] if s["title"] == title)


def _read(students, context, title: str, filename: str, name: str | None = None) -> None:
    # the owner finds the material and its section; the reader may not be allowed to
    material = students.find_material(filename)
    context["response"] = students.read_section(material, _position(students, material, title), name=name)


def _text(context) -> str:
    response = context["response"]
    assert response.status_code == 200, response.text
    return "\n".join(part["content"] for part in response.json())


@given(parsers.parse('I have uploaded "{filename}" to "{location}" with the content:'))
def have_uploaded_with_content(students, context, filename, location, docstring):
    context.setdefault("uploaded", {})[filename] = docstring.encode()
    students.wait_until_ingested(students.upload(location, filename, docstring.encode()))


@given(parsers.parse('I have uploaded a {pages:d}-page PDF "{filename}" without an outline to "{location}"'))
def have_uploaded_pdf(students, pages, filename, location):
    pdf = make_pdf([f"Text of page {n}." for n in range(1, pages + 1)])
    students.wait_until_ingested(students.upload(location, filename, pdf))


@given(parsers.parse('I have just uploaded "{filename}" to "{location}"'))
def have_just_uploaded(platform, students, filename, location):
    # the fake platform keeps it pending, as if it were still being processed
    platform.hold_ingestion = True
    assert students.upload(location, filename).status_code == 202


@when(parsers.parse('I open "{filename}"'))
@when(parsers.parse('I open "{filename}" before it is ready'))
def open_material(students, context, filename):
    context["response"] = students.open(students.find_material(filename))


@then("I see the sections:")
def see_sections(context, datatable):
    response = context["response"]
    assert response.status_code == 200, response.text
    seen = [{"section": s["title"], "level": str(s["level"])} for s in response.json()["sections"]]
    assert seen == _rows(datatable)


@when(parsers.parse('I read the section "{title}" of "{filename}"'))
def read_section(students, context, title, filename):
    _read(students, context, title, filename)


@when(parsers.parse('the student "{name}" reads the section "{title}" of "{filename}"'))
def student_reads_section(students, context, name, title, filename):
    _read(students, context, title, filename, name=name)


@then(parsers.parse('I read "{text}"'))
@then(parsers.parse('the student "{name}" reads "{text}"'))
def reads(context, text, name=None):
    assert text in _text(context)


@then("I am told the material is still being processed")
def still_processing(context):
    response = context["response"]
    assert response.status_code == 409, response.text
    assert "still being processed" in response.json()["detail"]


@when(parsers.parse('I download "{filename}"'))
def download(students, context, filename):
    context["response"] = students.download(students.find_material(filename))
    context["filename"] = filename


@then("I get the file exactly as I uploaded it")
def got_the_file(context):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.content == context["uploaded"][context["filename"]]
    assert context["filename"] in response.headers["content-disposition"]

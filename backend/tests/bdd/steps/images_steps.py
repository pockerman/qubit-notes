"""Steps of images.feature: the images of Markdown material."""

from pathlib import PurePosixPath

from pytest_bdd import given, parsers, then, when

from study_assistant.domain.images import MB
from tests.images import make_image, make_png


def _images_path(material: dict) -> str:
    return f"/api/courses/{material['course_id']}/materials/{material['document_id']}/images"


def _add(students, context, filename: str, name: str, content: bytes, path: str | None, student: str | None = None):
    material = students.find_material(filename)
    context.setdefault("materials", {})[filename] = material
    data = {"path": path} if path else {}
    response = students.client.post(
        _images_path(material), headers=students.headers(student), data=data, files={"file": (name, content)}
    )
    context["response"] = response
    if response.status_code == 200:
        context.setdefault("added", {})[path or name] = content
    return response


@when(parsers.parse('I add the image "{path}" to "{filename}"'))
@given(parsers.parse('I have added the image "{path}" to "{filename}"'))
def add_image(students, context, path, filename):
    _add(students, context, filename, PurePosixPath(path).name, make_png(), path)


@when(parsers.parse('the student "{student}" adds the image "{path}" to "{filename}"'))
def student_adds_image(students, context, student, path, filename):
    _add(students, context, filename, PurePosixPath(path).name, make_png(), path, student)


@when(parsers.parse('I add an image called "{name}" to "{filename}"'))
def add_image_called(students, context, name, filename):
    _add(students, context, filename, name, make_png(), None)


@when(parsers.parse('I add another image as "{path}" to "{filename}"'))
def add_another_image(students, context, path, filename):
    _add(students, context, filename, PurePosixPath(path).name, make_png(10, 120, 220), path)


@when(parsers.parse('I add the image "{path}" to "{filename}", which it refers to'))
def add_referred_image(students, context, path, filename):
    material = students.find_material(filename)
    text = f"# 1 Meshing\n![A mesh]({path})\n"
    changed = students.client.put(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/text",
        headers=students.headers(),
        json={"text": text},
    )
    students.wait_until_ingested(changed)
    extension = PurePosixPath(path).suffix.removeprefix(".")
    _add(students, context, filename, PurePosixPath(path).name, make_image(extension), path)


@when(parsers.parse('I add an image of {size:d} MB as "{path}" to "{filename}"'))
def add_large_image(students, context, size, path, filename):
    content = make_png() + b"\x00" * (size * MB)
    _add(students, context, filename, PurePosixPath(path).name, content, path)


def _images_of(students, filename: str) -> dict:
    response = students.client.get(_images_path(students.find_material(filename)), headers=students.headers())
    assert response.status_code == 200, response.text
    return response.json()


def _paths(paths: str) -> list[str]:
    return [path.strip() for path in paths.split(",")]


@then(parsers.parse('"{filename}" has the images "{paths}"'))
def has_images(students, filename, paths):
    assert _images_of(students, filename)["images"] == _paths(paths)


@then(parsers.parse('"{filename}" is missing the images "{paths}"'))
def missing_images(students, filename, paths):
    assert _images_of(students, filename)["missing"] == _paths(paths)


def _image(students, context, path: str, filename: str, student: str | None = None):
    # by the material it was added to, which may since have been deleted
    material = context["materials"][filename]
    return students.client.get(f"{_images_path(material)}/{path}", headers=students.headers(student))


@then(parsers.parse('the image "{path}" of "{filename}" is the one I added'))
@then(parsers.parse('the image "{path}" of "{filename}" is the one I added last'))
def image_is_added(students, context, path, filename):
    response = _image(students, context, path, filename)
    assert response.status_code == 200, response.text
    assert response.content == context["added"][path]
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-content-type-options"] == "nosniff"


@then(parsers.parse('the student "{student}" sees the image "{path}" of "{filename}"'))
def student_sees_image(students, context, student, path, filename):
    response = _image(students, context, path, filename, student)
    assert response.status_code == 200, response.text
    assert response.content == context["added"][path]


@then(parsers.parse('the image "{path}" of "{filename}" is gone'))
def image_gone(students, context, path, filename):
    assert _image(students, context, path, filename).status_code == 404


@then(parsers.parse('I am told "{filename}" does not refer to "{name}"'))
def does_not_refer(context, filename, name):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"{filename!r} does not refer to {name!r}" in response.json()["detail"]


@then(parsers.parse("the image is {outcome}"))
def image_outcome(context, outcome):
    response = context["response"]
    assert response.status_code == {"accepted": 200, "rejected": 422}[outcome], response.text


@then(parsers.parse("I am told the image is larger than {size:d} MB"))
def image_too_large(context, size):
    response = context["response"]
    assert response.status_code == 413, response.text
    assert f"up to {size} MB" in response.json()["detail"]


@then("I am told only Markdown material has images")
def only_markdown(context):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert "only Markdown material has images" in response.json()["detail"]

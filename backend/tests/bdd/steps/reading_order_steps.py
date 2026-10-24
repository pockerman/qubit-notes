"""Steps of reading_order.feature: the order of a topic's material, and reading on from one material to the next."""

from pytest_bdd import given, parsers, then, when


def _order(students, location: str, datatable, name: str | None = None):
    course, subject, topic = location.split("/")
    header, *rows = datatable
    assert header == ["filename"]
    return students.client.put(
        f"/api/courses/{course}/subjects/{subject}/topics/{topic}/material-order",
        headers=students.headers(name),
        json={"materials": [row[0] for row in rows]},
    )


@when(parsers.parse('I put the material of "{location}" in the order:'))
def put_material_in_order(students, context, location, datatable):
    context["response"] = _order(students, location, datatable)


@given(parsers.parse('I have put the material of "{location}" in the order:'))
def have_put_material_in_order(students, location, datatable):
    response = _order(students, location, datatable)
    assert response.status_code == 200, response.text


@when(parsers.parse('the student "{name}" puts the material of "{location}" in the order:'))
def student_puts_material_in_order(students, context, name, location, datatable):
    context["response"] = _order(students, location, datatable, name)


@then(parsers.parse('the student "{name}" sees the materials of "{location}" in the order:'))
def student_sees_materials_in_order(students, name, location, datatable):
    course, subject, topic = location.split("/")
    header, *rows = datatable
    found = students.materials(course, name=name, subject=subject, topic=topic)
    assert [m["filename"] for m in found] == [row[0] for row in rows]


@then(parsers.parse('I am told the order must have each of the materials of "{topic}" once'))
def material_order_invalid(context, topic):
    response = context["response"]
    assert response.status_code == 422, response.text
    assert f"the order must have each of the materials of {topic!r} once" in response.json()["detail"]


def _neighbours(students, context) -> dict:
    opened = context["response"].json()
    response = students.client.get(
        f"/api/courses/{opened['course_id']}/materials/{opened['document_id']}/neighbours", headers=students.headers()
    )
    assert response.status_code == 200, response.text
    return response.json()


@then(parsers.re(r'the (?P<which>next|previous) material is "(?P<filename>[^"]+)" in "(?P<location>[^"]+)"'))
def neighbour_is(students, context, which, filename, location):
    neighbour = _neighbours(students, context)[which]
    assert neighbour is not None, f"no {which} material"
    assert (neighbour["filename"], f"{neighbour['subject']}/{neighbour['topic']}") == (filename, location)


@then(parsers.re(r"there is no (?P<which>next|previous) material"))
def no_neighbour(students, context, which):
    assert _neighbours(students, context)[which] is None

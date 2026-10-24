"""Steps of references.feature: references between the topics of a course, and the topics' mentions."""

from pytest_bdd import parsers, then


def _references(students, filename: str, name: str | None = None) -> list[dict]:
    material = students.find_material(filename, name=name)
    response = students.client.get(
        f"/api/courses/{material['course_id']}/materials/{material['document_id']}/references",
        headers=students.headers(name),
    )
    assert response.status_code == 200, response.text
    return response.json()


def _mentions(students, location: str, course: str, name: str | None = None) -> list[dict]:
    subject, topic = location.split("/")
    response = students.client.get(f"/api/courses/{course}/mentions", headers=students.headers(name))
    assert response.status_code == 200, response.text
    found = next(t for t in response.json() if (t["subject"], t["topic"]) == (subject, topic))
    return [{key: m[key] for key in ("subject", "topic", "material")} for m in found["mentioned_in"]]


# the columns of a reference in a table, by its field
COLUMNS = {
    "shown as": "shown_as",
    "refers to": "refers_to",
    "subject": "subject",
    "topic": "topic",
    "material": "material",
    "section": "section",
}


@then(parsers.parse('the references of "{filename}" are:'))
def references_are(students, filename, datatable):
    header, *rows = datatable
    fields = [COLUMNS[column] for column in header]
    found = [[reference[field] or "" for field in fields] for reference in _references(students, filename)]
    assert found == rows


@then("none of its references is broken")
def none_broken(students, context):
    response = context["response"]
    if "generated" in context and response.status_code == 200:
        # generated, not saved: its references are resolved as the editor's preview resolves them
        course_id = students.find_material("fem-notes.md")["course_id"]
        text = context["generated"]["text"]
        resolved = students.client.post(
            f"/api/courses/{course_id}/references", headers=students.headers(), json={"text": text}
        ).json()
        assert resolved and all(r["refers_to"] != "nothing" for r in resolved), resolved
        return
    assert response.status_code == 202, response.text
    assert response.json()["broken_references"] == []


@then(parsers.parse('"{filename}" has no references'))
def no_references(students, filename):
    assert _references(students, filename) == []


@then("the material is saved")
def saved(students, context):
    students.wait_until_ingested(context["response"])


@then(parsers.parse('I am told "{filename}" has the broken reference "{reference}"'))
def told_broken(context, filename, reference):
    response = context["response"]
    assert response.status_code == 202, response.text
    assert response.json()["broken_references"] == [reference]


@then(parsers.parse('the topic "{location}" of "{course}" is mentioned in:'))
def mentioned_in(students, location, course, datatable):
    header, *rows = datatable
    assert _mentions(students, location, course) == [dict(zip(header, row)) for row in rows]


@then(parsers.parse('the topic "{location}" of "{course}" is mentioned in nothing'))
def mentioned_in_nothing(students, location, course):
    assert _mentions(students, location, course) == []


@then(parsers.parse('the student "{name}" sees that the topic "{location}" of "{course}" is mentioned in:'))
def student_sees_mentions(students, name, location, course, datatable):
    header, *rows = datatable
    assert _mentions(students, location, course, name) == [dict(zip(header, row)) for row in rows]


@then(parsers.parse('the student "{name}" sees {count:d} references in "{filename}"'))
def student_sees_references(students, name, count, filename):
    references = _references(students, filename, name)
    assert len(references) == count
    assert all(r["refers_to"] != "nothing" for r in references)

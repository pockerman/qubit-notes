from pytest_bdd import given, parsers, then, when

from tests.bdd.steps.materials_steps import _rows

ROLE = {"a reader": "reader", "an owner": "owner"}


@when(parsers.parse('I share the course "{course}" with "{name}" as {role}'))
@given(parsers.parse('I have shared the course "{course}" with "{name}" as {role}'))
def share(students, context, course, name, role):
    context["response"] = students.share(course, name, ROLE[role])
    assert context["response"].status_code == 200, context["response"].text


@when(parsers.parse('the student "{name}" shares the course "{course}" with "{other}" as {role}'))
def student_shares(students, context, name, course, other, role):
    context["response"] = students.share(course, other, ROLE[role], name=name)


@when(parsers.parse('I stop sharing the course "{course}" with "{name}"'))
def unshare(students, context, course, name):
    context["response"] = students.client.delete(
        f"/api/courses/{course}/members/{students.id(name)}", headers=students.headers()
    )


@when(parsers.parse('I list the members of the course "{course}"'))
def list_members(students, context, course):
    context["response"] = students.client.get(f"/api/courses/{course}/members", headers=students.headers())


@then("I see the members:")
def see_members(students, context, datatable):
    assert context["response"].status_code == 200, context["response"].text
    members = [{"student": students.name(m["student"]), "role": m["role"]} for m in context["response"].json()]
    assert members == _rows(datatable)


@then(parsers.parse('the student "{name}" sees the courses:'))
def student_sees_courses(students, name, datatable):
    seen = [
        {"course": c["name"], "owned by": students.name(c["owner"]), "role": c["role"]}
        for c in students.courses(name=name)
    ]
    assert seen == _rows(datatable)


@then(parsers.parse('the student "{name}" sees the materials of the course "{course}":'))
def student_sees_materials(students, name, course, datatable):
    seen = [{key: m[key] for key in ("subject", "topic", "filename")} for m in students.materials(course, name=name)]
    assert seen == _rows(datatable)


@then(parsers.parse('the student "{name}" has no courses'))
def student_has_no_courses(students, name):
    assert students.courses(name=name) == []


@then("I am told a course must keep at least one owner")
def must_keep_owner(context):
    assert context["response"].status_code == 409, context["response"].text
    assert "at least one owner" in context["response"].json()["detail"]

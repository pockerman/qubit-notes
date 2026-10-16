from pytest_bdd import given, parsers, then


@given("the study assistant is running")
def study_assistant_running(client):
    return client


@given(parsers.parse('I am the student "{name}"'))
def i_am(students, name):
    students.me = name


@then(parsers.parse('the student "{name}" is not allowed to do that'))
def not_allowed(context, name):
    assert context["response"].status_code == 403, context["response"].text

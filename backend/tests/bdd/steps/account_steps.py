"""A student's account: their email and password, changed through Cognito (tests/fakes/fake_cognito.py)."""

from pytest_bdd import given, parsers, then, when

from tests.fakes.fake_cognito import User


@given(
    parsers.re(
        r'Cognito has the user "(?P<name>[^"]+)" with the email "(?P<email>[^"]+)" '
        r'and the password "(?P<password>[^"]+)"$'
    )
)
def cognito_has_user_with(cognito, students, name, email, password):
    cognito.users[students.id(name)] = User(email=email, password=password)


@when("I look at my account")
def look_at_account(client, students, context):
    context["response"] = client.get("/api/account", headers=students.headers())


@then(parsers.re(r'I am told my email is "(?P<email>[^"]+)"$'))
def told_email(client, students, email):
    response = client.get("/api/account", headers=students.headers())
    assert response.status_code == 200, response.text
    assert response.json() == {"signs_in_with": "cognito", "email": email}


def _change_password(client, students, current, new):
    return client.put("/api/account/password", headers=students.headers(), json={"current": current, "new": new})


@when(parsers.re(r'I change my password from "(?P<current>[^"]+)" to "(?P<new>[^"]+)"$'))
def change_password(client, students, context, current, new):
    context["response"] = _change_password(client, students, current, new)


@then(parsers.re(r'Cognito takes "(?P<password>[^"]+)" as the password of "(?P<name>[^"]+)"$'))
def cognito_password(cognito, students, password, name):
    assert cognito.users[students.id(name)].password == password


def _told(context, status: int, text: str):
    response = context["response"]
    assert response.status_code == status, response.text
    assert text in response.json()["detail"], response.text


@then("I am told my current password is not right")
def told_current_password_wrong(context):
    _told(context, 422, "your current password is not right")


@then("I am told the new password does not meet the rules for passwords")
def told_password_rules(context):
    _told(context, 422, "the new password does not meet the rules for passwords")


def _change_email(client, students, email):
    return client.put("/api/account/email", headers=students.headers(), json={"email": email})


@when(parsers.re(r'I change my email to "(?P<email>[^"]+)"$'))
def change_email(client, students, context, email):
    context["response"] = _change_email(client, students, email)


@given(parsers.re(r'I have changed my email to "(?P<email>[^"]+)"$'))
def have_changed_email(client, students, email):
    response = _change_email(client, students, email)
    assert response.status_code == 204, response.text


@then(parsers.re(r'I am told to enter the code sent to "(?P<email>[^"]+)"$'))
def told_to_enter_code(cognito, students, context, email):
    assert context["response"].status_code == 204, context["response"].text
    user = cognito.users[students.id(students.me)]
    assert user.pending_email == email and user.code


def _confirm(client, students, context, code):
    context["response"] = client.post("/api/account/email/confirm", headers=students.headers(), json={"code": code})


@when("I confirm my email with the code Cognito sent")
def confirm_with_sent_code(cognito, client, students, context):
    _confirm(client, students, context, cognito.users[students.id(students.me)].code)
    assert context["response"].status_code == 204, context["response"].text


@when(parsers.re(r'I confirm my email with the code "(?P<code>[^"]+)"$'))
def confirm_with_code(client, students, context, code):
    _confirm(client, students, context, code)


@then("I am told the code is not right")
def told_code_wrong(context):
    _told(context, 422, "the code is not right")

"""Signing in with Amazon Cognito: the app checks the tokens of tests/fakes/fake_cognito.py as it does Cognito's."""

from pytest_bdd import given, parsers, then, when

from tests.fakes.fake_cognito import SigningKey, User


@given("the app signs students in with Cognito")
def app_signs_in_with_cognito(client):
    # the app fixture set the app up with Cognito for the scenarios tagged @cognito
    assert client.get("/api/config").json()["auth"] == "cognito"


@given(parsers.parse('I have signed in with Cognito as "{name}"'))
def signed_in_with_cognito(students, name):
    # the scenario's requests carry the student's Cognito token
    students.me = name


@then(parsers.parse('the course "{course}" is created by "{name}"'))
def course_created_by(students, context, course, name):
    response = context["response"]
    assert response.status_code == 201, response.text
    assert response.json()["owner"] == students.id(name)


@when(parsers.parse('I say I am "{name}" without a token'))
def say_who_i_am(students, context, name):
    context["response"] = students.client.get("/api/courses", headers={"X-Student-Id": students.id(name)})


@then("I am asked to sign in")
def asked_to_sign_in(context):
    response = context["response"]
    assert response.status_code == 401, response.text
    assert response.headers.get("WWW-Authenticate") == "Bearer"


TOKENS = {
    "expired": {"expired": True},
    "signed by another key": {"key": SigningKey()},
    "from another user pool": {"issuer": "https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_Another"},
    "issued to another app": {"client_id": "another-app"},
    "an ID token, not an access token": {"token_use": "id"},
}


@given(parsers.parse('I have a Cognito token for "{name}" that is {problem}'))
def token_with_problem(cognito, students, context, name, problem):
    context["token"] = cognito.token(students.id(name), **TOKENS[problem])


@when("I list my courses with it")
def list_courses_with_token(students, context):
    context["response"] = students.client.get("/api/courses", headers={"Authorization": f"Bearer {context['token']}"})


def _file_url(students, filename: str) -> str:
    material = next(m for m in students.materials("aeronautics") if m["filename"] == filename)
    return f"/api/courses/{material['course_id']}/materials/{material['document_id']}/file"


@when(parsers.parse('I play "{filename}" with my token in its link'))
def play_with_token(cognito, students, context, filename):
    token = cognito.token(students.id(students.me))
    # as a <video> does: no headers, who the student is is in the link
    context["response"] = students.client.get(
        _file_url(students, filename), params={"access_token": token, "inline": "true"}
    )


@when(parsers.parse('I play "{filename}" with only my name in its link'))
def play_with_name(students, context, filename):
    context["response"] = students.client.get(
        _file_url(students, filename), params={"student": students.id(students.me), "inline": "true"}
    )


@then("I get the video")
def get_the_video(context):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("video/mp4")


# in the browser


@given(parsers.parse('Cognito has the user "{name}"'))
def cognito_has_user(cognito, students, name):
    cognito.users[students.id(name)] = User()


@when("I open the app")
def open_the_app(page):
    page.goto("/")


@then("I am sent to sign in with Cognito")
def sent_to_cognito(page, cognito):
    from playwright.sync_api import expect

    expect(page.get_by_role("heading", name="Sign in to Cognito (test)")).to_be_visible()
    assert page.url.startswith(f"{cognito.base_url}/oauth2/authorize?"), page.url


@when(parsers.parse('I sign in to Cognito as "{name}"'))
def sign_in_to_cognito(page, students, name):
    students.me = name
    page.get_by_label("Username").fill(students.id(name))
    page.get_by_role("button", name="Sign in").click()


@then(parsers.parse('I am back in the app, signed in as "{name}"'))
def back_in_the_app(page, live_url, students, name):
    from playwright.sync_api import expect

    expect(page.get_by_text(f"Signed in as {students.id(name)}")).to_be_visible()
    assert page.url.startswith(live_url) and "code=" not in page.url, page.url
    # and the backend takes who the student is: their courses are listed, with none yet
    expect(page.get_by_text("You have no courses yet.")).to_be_visible()


@given(parsers.parse('I have signed in to the app with Cognito as "{name}"'))
def signed_in_to_the_app(page, cognito, live_url, students, name):
    open_the_app(page)
    sent_to_cognito(page, cognito)
    sign_in_to_cognito(page, students, name)
    back_in_the_app(page, live_url, students, name)


@when("I sign out")
def sign_out(page):
    page.get_by_role("button", name="Menu").click()
    page.get_by_role("menuitem", name="Sign out").click()

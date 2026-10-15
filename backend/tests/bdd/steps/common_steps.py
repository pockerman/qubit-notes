from pytest_bdd import given


@given("the study assistant is running")
def study_assistant_running(client):
    return client

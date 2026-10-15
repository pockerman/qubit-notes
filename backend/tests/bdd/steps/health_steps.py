from pytest_bdd import then, when


@when("I check its health")
def check_health(client, context):
    context["response"] = client.get("/api/health")


@then("it reports that it is healthy")
def reports_healthy(context):
    response = context["response"]
    assert response.status_code == 200
    assert response.json()["status"] == "ok", response.json()


@then("it lists at least one model provider")
def lists_providers(context):
    assert context["response"].json()["providers"]

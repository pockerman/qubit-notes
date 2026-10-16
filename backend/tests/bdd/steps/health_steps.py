from pytest_bdd import given, parsers, then, when


@given(parsers.parse('the platform service "{service}" is down'))
def service_down(platform, service):
    platform.down.add(service)


@given("the platform cannot be reached")
def platform_unreachable(platform):
    platform.reachable = False


@when("I check its health")
def check_health(client, context):
    context["response"] = client.get("/api/health")


@then("it reports that it is healthy")
def reports_healthy(context):
    response = context["response"]
    assert response.status_code == 200
    assert response.json()["status"] == "ok", response.json()


@then("it reports that it is degraded")
def reports_degraded(context):
    response = context["response"]
    assert response.status_code == 200
    assert response.json()["status"] == "degraded", response.json()


@then("it reports every platform service as serving")
def every_service_serving(context):
    services = context["response"].json()["services"]
    assert "gateway" in services
    assert all(status == "SERVING" for status in services.values()), services


@then(parsers.parse('it reports "{service}" as not serving'))
def service_not_serving(context, service):
    assert context["response"].json()["services"][service] == "NOT_SERVING"


@then("it reports why the platform cannot be reached")
def reports_error(context):
    assert context["response"].json()["error"]

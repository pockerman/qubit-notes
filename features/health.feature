Feature: Service health
  As someone running the study assistant
  I want to know whether the gogi platform behind it is healthy
  So that I can tell a broken deployment apart from a broken feature

  @gogi
  Scenario: The platform is healthy
    Given the study assistant is running
    When I check its health
    Then it reports that it is healthy
    And it reports every platform service as serving

  Scenario: A platform service is down
    Given the study assistant is running
    And the platform service "guardrails" is down
    When I check its health
    Then it reports that it is degraded
    And it reports "guardrails" as not serving

  Scenario: The platform cannot be reached
    Given the study assistant is running
    And the platform cannot be reached
    When I check its health
    Then it reports that it is degraded
    And it reports why the platform cannot be reached

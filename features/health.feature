Feature: Service health
  As someone running the study assistant
  I want to know whether it can reach the gogi platform
  So that I can tell a broken deployment apart from a broken feature

  @gogi
  Scenario: The study assistant reaches the platform
    Given the study assistant is running
    When I check its health
    Then it reports that it is healthy
    And it lists at least one model provider

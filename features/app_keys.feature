Feature: The app's keys, set by its admins
  As an admin of qubit-notes
  I want to give the app a key it is missing, such as its Anthropic key, from the app itself
  So that I don't have to change its settings and restart it

  The app's keys are its own, shared by everyone who uses it: the key of its AI's provider, and
  of its embedding model's where that is at Voyage AI or OpenAI (see The app's own platform).
  They come from its settings, e.g. QUBIT_NOTES_ANTHROPIC_API_KEY. A key the settings don't
  give is missing, and the health check reports it as missing, by its provider.

  The admins, named in QUBIT_NOTES_ADMINS (e.g. "alex,maria"), can give the app a missing key.
  It is kept in the app's database, encrypted with the app's secret (QUBIT_NOTES_SECRET_KEY), so
  the app has it again when it restarts, and it is never shown back to anyone. A key in the
  settings is used rather than one kept in the database. Where the platform is gogi, the key is
  stored in gogi as the app's credential, as `qubit-notes store-provider-key` does.

  Background:
    Given qubit-notes is running without a key for "anthropic"
    And "alex" is an admin of qubit-notes

  Scenario: The health check names the missing key
    When I check its health
    Then it reports that it is degraded
    And it reports the key of "anthropic" as missing

  Scenario: Students are told whether they are admins
    Given I am the student "alex"
    Then I am told I am an admin
    Given I am the student "maria"
    Then I am told I am not an admin

  Scenario: An admin gives the app its missing key
    Given I am the student "alex"
    When I give the app the key "sk-ant-test" for "anthropic"
    Then the app uses the key "sk-ant-test" for "anthropic"
    And when I check its health, no key is missing

  Scenario: The key is kept, encrypted, when the app restarts
    Given I am the student "alex"
    And I have given the app the key "sk-ant-test" for "anthropic"
    When qubit-notes restarts
    Then the app uses the key "sk-ant-test" for "anthropic"
    And the database does not hold "sk-ant-test"

  Scenario: The key is never shown back
    Given I am the student "alex"
    When I give the app the key "sk-ant-test" for "anthropic"
    And I check its health
    Then nothing the app answers holds "sk-ant-test"

  Scenario: A key in the settings is used rather than one kept
    Given I am the student "alex"
    And I have given the app the key "sk-ant-kept" for "anthropic"
    When qubit-notes restarts with the key "sk-ant-settings" for "anthropic" in its settings
    Then the app uses the key "sk-ant-settings" for "anthropic"

  Scenario: Only admins give the app keys
    Given I am the student "maria"
    When I give the app the key "sk-ant-test" for "anthropic"
    Then I am not allowed to do that
    And the key of "anthropic" is still missing

  Scenario: Keys are kept only with the app's secret
    Given qubit-notes has no secret
    And I am the student "alex"
    When I give the app the key "sk-ant-test" for "anthropic"
    Then I am told to set QUBIT_NOTES_SECRET_KEY first
    And the key of "anthropic" is still missing

  Scenario: Only the keys of the app's providers
    Given I am the student "alex"
    When I give the app the key "abc" for "acme"
    Then I am told the app has no provider "acme"

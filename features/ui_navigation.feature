@ui
Feature: The navigation bar
  As a student
  I want the app's bar to show whether the platform is working and to keep its links in a menu
  So that it stays tidy, and an admin can fix what the platform is missing from where it shows

  The bar has the app's name, with the platform's status next to it, and on the right "Signed in
  as …" beside a menu of My courses, Settings (see Settings in the browser) and Sign out. Where the platform
  is degraded, its status can be opened to see why, in plain words. A missing key is "The app is
  missing a key.", naming neither the provider nor the setting that holds it: an admin is told to
  head to Settings to give it, with a link there (see Settings in the browser); anyone else is told
  to ask an admin.

  Scenario: The bar
    Given I am signed in as "maria"
    Then I see the platform's status next to the app's name
    And I see "Signed in as maria" beside the menu
    When I open the menu
    Then it offers "My courses, Settings, Sign out"

  Scenario: My courses, from the menu
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    When I open the course "Aeronautics"
    And I choose "My courses" from the menu
    Then I see my courses

  Scenario: Sign out, from the menu
    Given I am signed in as "maria"
    When I choose "Sign out" from the menu
    Then I am asked who I am

  Scenario: An admin is sent to Settings to give the app its missing key
    Given qubit-notes is running without a key for "anthropic"
    And qubit-notes has a secret to keep the keys it is given with
    And "alex" is an admin of qubit-notes
    And I am signed in as "alex"
    Then the platform's status says "Platform degraded: ai"
    When I open the platform's status
    Then I am told the app is missing a key
    And I am not shown "Anthropic"
    And I am not shown the setting "QUBIT_NOTES_ANTHROPIC_API_KEY"
    And I am not offered to give it a key
    When I head to Settings from the platform's status
    And I give the provider's key "sk-ant-test" in the settings
    Then the platform's status says "Platform connected"

  Scenario: A student who is not an admin is told to ask one
    Given qubit-notes is running without a key for "anthropic"
    And "alex" is an admin of qubit-notes
    And I am signed in as "maria"
    When I open the platform's status
    Then I am told the app is missing a key
    And I am not shown "Anthropic"
    And I am told to ask an admin to give it
    And I am not offered to give it a key

@ui
Feature: Settings in the browser
  As an admin of qubit-notes
  I want a settings page where I choose the AI's provider and model
  So that changing the model is a few clicks, not a change to the app's settings and a restart

  "AI model", under "Settings" in the app's menu, opens the AI's settings. They show the provider
  and model the AI uses (see The AI's model). An admin chooses another there: the provider from
  a list, Anthropic or OpenAI, and the model by typing its name, with the provider's models
  suggested; choosing a provider fills in its own model. Below it is one "Provider key" field, for
  the key of the provider saved: Anthropic's or OpenAI's, whichever the AI uses, with nothing said
  about it but the field's name. An admin gives the key there, or replaces the one the app was
  given (see The app's keys, set by its admins). A key the app's settings give is used rather than
  one given, so the field is not offered then, only "The app's settings give this key.".
  Where the app is missing its embedding model's key, e.g. Voyage AI's, an "Embedding model"
  section offers a field for it too, to admins, until it is given. Anyone else sees the provider
  and model, but no key's field, and cannot change them.

  Background:
    Given qubit-notes is running with the model provider "anthropic", and no model set
    And qubit-notes has a secret to keep the keys it is given with
    And "alex" is an admin of qubit-notes

  Scenario: An admin chooses another model of the same provider
    Given I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    Then I see the AI uses "claude-sonnet-5-5" of "Anthropic"
    When I choose the model "claude-opus-5-5" in the settings, and save it
    Then I am told the AI uses "claude-opus-5-5" of "Anthropic" from now on
    And the AI uses "claude-opus-5-5" of "anthropic"

  Scenario: An admin changes to OpenAI and gives its key
    Given I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    And I choose the provider "OpenAI" in the settings
    Then the model is filled in as "gpt-5"
    When I choose the model "gpt-5-mini" in the settings, and save it
    Then I am offered the provider's key
    And I am not told "OpenAI's key, the AI's provider"
    When I give the provider's key "sk-openai-test" in the settings
    Then I am told the provider's key is saved
    And the app uses the key "sk-openai-test" for "openai"
    And the AI uses "gpt-5-mini" of "openai"

  Scenario: An admin replaces the provider's key the app was given
    Given qubit-notes is running without a key for "anthropic"
    And I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    Then I am offered the provider's key
    When I give the provider's key "sk-ant-first" in the settings
    And I give the provider's key "sk-ant-second" in the settings
    Then the app uses the key "sk-ant-second" for "anthropic"
    And I am offered no other key

  Scenario: The provider's key the app's settings give is not changed here
    Given qubit-notes has the key "sk-ant-test" for "anthropic" in its settings
    And I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    Then I am told the app's settings give the provider's key
    And I am not shown the setting "QUBIT_NOTES_ANTHROPIC_API_KEY"
    And I am not offered to change the provider's key

  Scenario: An admin gives the embedding model's missing key
    Given qubit-notes is running without a key for "voyage"
    And I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    Then I am told the app is missing its embedding model's key, of "Voyage AI"
    When I give the embedding model's key "pa-test" in the settings
    Then the app uses the key "pa-test" for "voyage"
    And I am offered no embedding model's key

  Scenario: A student who is not an admin sees the model, but cannot change it
    Given I am signed in as "maria"
    When I choose "Settings › AI model" from the menu
    Then I see the AI uses "claude-sonnet-5-5" of "Anthropic"
    But I am not offered to change it
    And I am offered no key

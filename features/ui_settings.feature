@ui
Feature: Settings in the browser
  As an admin of qubit-notes
  I want a settings page where I choose the AI's provider and model, and give the app its keys
  So that changing the model is a few clicks, not a change to the app's settings and a restart

  "AI model", under "Settings" in the app's menu, opens the AI's settings. They show the provider
  and model the AI uses (see The AI's model). An admin chooses another there: the provider from
  a list, Anthropic or OpenAI, and the model by typing its name, with the provider's models
  suggested; choosing a provider fills in its own model. If the app has no key for the AI's
  provider, they say so.

  Below, "Keys" lists the model providers, Anthropic and OpenAI, and Voyage AI once the app needs
  or has its key, each with whether the app has its key: "Saved", "No key", or "Given by the
  app's settings" (see The app's keys, set by its admins). An admin gives a missing key there, and
  is told once it is saved; a key saved can be replaced or removed, and is shown as saved when
  they come back, never the key itself. A key the app's settings give is used rather than one
  given, so it is neither replaced nor removed here. Anyone else sees the provider and model, but
  no keys, and cannot change them.

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
    Then I am told the app has no OpenAI key yet
    And I see the "OpenAI" key is "No key"
    When I give the "OpenAI" key "sk-openai-test" in the settings
    Then I am told "The OpenAI key is saved."
    And I see the "OpenAI" key is "Saved"
    And the app uses the key "sk-openai-test" for "openai"
    And the AI uses "gpt-5-mini" of "openai"

  Scenario: A key saved is shown as saved when the admin comes back, and can be replaced
    Given qubit-notes is running without a key for "anthropic"
    And I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    And I give the "Anthropic" key "sk-ant-first" in the settings
    And I come back to the settings
    Then I see the "Anthropic" key is "Saved"
    And I am not shown "sk-ant-first" in the settings
    When I replace the "Anthropic" key with "sk-ant-second" in the settings
    Then I am told "The Anthropic key is saved."
    And the app uses the key "sk-ant-second" for "anthropic"

  Scenario: An admin removes a key
    Given I am the student "alex"
    And I have given the app the key "sk-openai-test" for "openai"
    And I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    And I remove the "OpenAI" key in the settings
    Then I am told "The OpenAI key is removed."
    And I see the "OpenAI" key is "No key"
    And the key of "openai" is gone

  Scenario: The provider's key the app's settings give is not changed here
    Given qubit-notes has the key "sk-ant-test" for "anthropic" in its settings
    And I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    Then I see the "Anthropic" key is "Given by the app's settings"
    And I am not shown "QUBIT_NOTES_ANTHROPIC_API_KEY" in the settings
    And I am not offered to change the "Anthropic" key

  Scenario: An admin gives the embedding model's missing key
    Given qubit-notes is running without a key for "voyage"
    And I am signed in as "alex"
    When I choose "Settings › AI model" from the menu
    Then I see the "Voyage AI" key is "No key"
    When I give the "Voyage AI" key "pa-test" in the settings
    Then I see the "Voyage AI" key is "Saved"
    And the app uses the key "pa-test" for "voyage"

  Scenario: A student who is not an admin sees the model, but cannot change it
    Given I am signed in as "maria"
    When I choose "Settings › AI model" from the menu
    Then I see the AI uses "claude-sonnet-5-5" of "Anthropic"
    But I am not offered to change it
    And I am offered no key

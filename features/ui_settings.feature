@ui
Feature: Settings in the browser
  As an admin of qubit-notes
  I want a settings page where I choose the AI's provider and model
  So that changing the model is a few clicks, not a change to the app's settings and a restart

  "Settings" in the app's menu opens the settings. Their "AI model" section shows the provider
  and model the AI uses (see The AI's model). An admin chooses another there: the provider from
  a list, Anthropic or OpenAI, and the model by typing its name, with the provider's models
  suggested; choosing a provider fills in its own model. If the app is missing the key of the
  provider chosen, it says so there, and the admin can give it there too. Anyone else sees the
  provider and model, but cannot change them.

  Background:
    Given qubit-notes is running with the model provider "anthropic", and no model set
    And qubit-notes has the key "sk-ant-test" for "anthropic" in its settings
    And qubit-notes has a secret to keep the keys it is given with
    And "alex" is an admin of qubit-notes

  Scenario: An admin chooses another model of the same provider
    Given I am signed in as "alex"
    When I choose "Settings" from the menu
    Then I see the AI uses "claude-sonnet-5-5" of "Anthropic"
    When I choose the model "claude-opus-5-5" in the settings, and save it
    Then I am told the AI uses "claude-opus-5-5" of "Anthropic" from now on
    And the AI uses "claude-opus-5-5" of "anthropic"

  Scenario: An admin changes to OpenAI and gives its key
    Given I am signed in as "alex"
    When I choose "Settings" from the menu
    And I choose the provider "OpenAI" in the settings
    Then the model is filled in as "gpt-5"
    When I choose the model "gpt-5-mini" in the settings, and save it
    Then I am told the app is missing its "OpenAI" key
    When I give it the key "sk-openai-test"
    Then the app uses the key "sk-openai-test" for "openai"
    And the AI uses "gpt-5-mini" of "openai"

  Scenario: A student who is not an admin sees the model, but cannot change it
    Given I am signed in as "maria"
    When I choose "Settings" from the menu
    Then I see the AI uses "claude-sonnet-5-5" of "Anthropic"
    But I am not offered to change it

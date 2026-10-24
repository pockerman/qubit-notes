Feature: The AI's model
  As an admin of qubit-notes
  I want to choose the model that writes the app's answers, summaries, quizzes and material
  So that I can use Anthropic's or OpenAI's, and change to another model easily

  The app's AI is a model of one provider, Anthropic or OpenAI. The app's settings name them
  (QUBIT_NOTES_LLM_PROVIDER, QUBIT_NOTES_LLM_MODEL); a provider without a model set uses its own
  by default:
    | provider  | model             |
    | anthropic | claude-sonnet-5-5 |
    | openai    | gpt-5             |
  So QUBIT_NOTES_LLM_PROVIDER=openai and the OpenAI key are all the app needs to use OpenAI.

  The admins (see The app's keys, set by its admins) can choose another provider and model from
  the app. The choice is kept in the app's database and used from then on, for everyone, and
  again when the app restarts, rather than the settings'. A model is named as its provider names
  it, e.g. "claude-opus-5-5" or "gpt-5-mini": the app suggests some of each provider's, and takes
  any other. The AI needs its provider's key; the app tells whether it has each provider's key,
  never the key itself. Where the platform is gogi, the choice is given to gogi with each request
  to the AI. The model that embeds material is not chosen here (see The app on its own).

  Background:
    Given qubit-notes is running with the model provider "anthropic", and no model set
    And "alex" is an admin of qubit-notes

  Scenario: The AI uses the settings' provider, with its own model by default
    Given I am the student "maria"
    When I ask which model the AI uses
    Then I am told it is "claude-sonnet-5-5" of "anthropic"
    And I am told the models suggested are:
      | provider  | models                                               |
      | anthropic | claude-opus-5-5, claude-sonnet-5-5, claude-haiku-5-5 |
      | openai    | gpt-5, gpt-5-mini, gpt-5-nano                        |

  Scenario Outline: Each provider's own model
    Given qubit-notes is running with the model provider "<provider>", and no model set
    Then the AI uses "<model>" of "<provider>"

    Examples:
      | provider  | model             |
      | anthropic | claude-sonnet-5-5 |
      | openai    | gpt-5             |

  Scenario: The model the settings name
    Given qubit-notes is running with the model provider "openai", and the model "gpt-5-mini"
    Then the AI uses "gpt-5-mini" of "openai"

  Scenario: An admin chooses another model
    Given I am the student "alex"
    When I choose the model "claude-opus-5-5" of "anthropic"
    Then the AI uses "claude-opus-5-5" of "anthropic"

  Scenario: An admin chooses OpenAI, without its key
    Given I am the student "alex"
    When I choose the model "gpt-5-mini" of "openai"
    Then the AI uses "gpt-5-mini" of "openai"
    And when I check its health, it reports the key of "openai" as missing

  Scenario: A provider chosen without a model uses its own
    Given I am the student "alex"
    When I choose "openai", without a model
    Then the AI uses "gpt-5" of "openai"

  Scenario: The choice is kept when the app restarts, rather than the settings'
    Given I am the student "alex"
    And I have chosen the model "gpt-5-mini" of "openai"
    When qubit-notes restarts with the model "claude-haiku-5-5" of "anthropic" in its settings
    Then the AI uses "gpt-5-mini" of "openai"

  Scenario: The app tells whether it has each provider's key
    Given qubit-notes has the key "sk-ant-test" for "anthropic" in its settings
    And I am the student "alex"
    When I ask which model the AI uses
    Then I am told the app has the key of "anthropic", but not of "openai"
    And nothing the app answers holds "sk-ant-test"

  Scenario: Only admins choose the model
    Given I am the student "maria"
    When I choose the model "claude-opus-5-5" of "anthropic"
    Then I am not allowed to do that
    And the AI uses "claude-sonnet-5-5" of "anthropic"

  Scenario: Only the app's providers
    Given I am the student "alex"
    When I choose the model "acme-1" of "acme"
    Then I am told the app's AI is Anthropic's or OpenAI's

@ai
Feature: The AI's usage
  As a student of qubit-notes, or an admin paying for its AI
  I want to see how many tokens the AI uses, on what, and for whom
  So that its cost is known, and can be planned for and limited

  Every call to the AI is recorded with the tokens it used, what it was for, the student it was
  for, and the provider and model that answered. A call that the app has to make again, because
  the AI's reply was no good, used tokens all the same, so each is recorded; one the provider
  refused used none. What it is for is one of:

    | purpose    | asked for                                |
    | assistant  | whatever a student asks the assistant    |
    | summary    | a summary                                |
    | quiz       | a quiz                                   |
    | flashcards | a deck of flashcards                     |
    | generating | material generated from a topic's        |

  A student sees their own usage, by purpose and by model, over the last 30 days unless they ask
  for another number of days. The app's admins also see everyone's, largest first. Usage is kept
  when the material or course it was for is deleted: the tokens were used all the same.

  Background:
    Given I am the student "maria"
    And the AI uses 1000 input tokens and 200 output tokens each time
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Rule: Every call to the AI is recorded

    Scenario: Nothing is used before the AI is asked
      Then I have used no tokens

    Scenario Outline: What I ask the AI for is recorded by its purpose
      When I ask the AI for <what>
      Then I have used 1000 input tokens and 200 output tokens in 1 request
      And I have used 1000 input tokens and 200 output tokens on "<purpose>"

      Examples:
        | what                | purpose    |
        | a question answered | assistant  |
        | a summary           | summary    |
        | a quiz              | quiz       |
        | flashcards          | flashcards |
        | generated material  | generating |

    Scenario: A saved summary uses no more tokens
      When I ask the AI for a summary
      And I ask the AI for a summary
      Then I have used 1000 input tokens and 200 output tokens in 1 request

    Scenario: Requests add up
      When I ask the AI for a summary
      And I ask the AI for a quiz
      Then I have used 2000 input tokens and 400 output tokens in 2 requests

    Scenario: The provider and model that answered are recorded
      Given qubit-notes has a secret to keep the keys it is given with
      And "alex" is an admin of qubit-notes
      And I am the student "alex"
      And I have given the app the key "sk-openai-test" for "openai"
      And I am the student "maria"
      When I ask the assistant about "fem-notes.md", choosing "openai"
      Then I have used 1000 input tokens and 200 output tokens with "gpt-5" of "openai"

    Scenario: Usage is kept when the material is deleted
      Given I have asked the AI for a summary
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then I have used 1000 input tokens and 200 output tokens in 1 request

  Rule: I see my usage over the days I ask for

    Scenario: Usage older than the days asked for isn't counted
      Given I asked the AI for a summary 40 days ago
      And I have asked the AI for a quiz
      Then I have used 1000 input tokens and 200 output tokens in 1 request
      And I have used 2000 input tokens and 400 output tokens over the last 60 days

    Scenario Outline: The days must be sensible
      When I ask for my usage over the last <days> days
      Then I am told the number of days is invalid

      Examples:
        | days |
        | 0    |
        | 367  |

  Rule: A student sees their own usage, and the admins everyone's

    Scenario: Another student's usage is not mine
      Given I have asked the AI for a summary
      Then the student "tom" has used no tokens

    Scenario: An admin sees everyone's usage, largest first
      Given "alex" is an admin of qubit-notes
      And I have shared the course "aeronautics" with "tom" as a reader
      And I have asked the AI for a summary
      And the student "tom" has asked the AI for a quiz
      And the student "tom" has asked the AI for flashcards
      Then the admin "alex" sees the usage:
        | student | requests | input tokens | output tokens |
        | tom     | 2        | 2000         | 400           |
        | maria   | 1        | 1000         | 200           |

    Scenario: Only the app's admins see everyone's usage
      When I ask for everyone's usage
      Then I am told only the app's admins can see it

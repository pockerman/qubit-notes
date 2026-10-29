@ui
Feature: Asking the assistant in the browser
  As a student
  I want to ask the assistant from the page I am reading
  So that I can get answers, summaries and quizzes as I read

  An "AI" button next to "Edit" and "Download" opens the assistant beside the text. Summaries
  and quizzes are asked for there, in words: there are no separate buttons for them.

  Where the app has the keys of both Anthropic and OpenAI, the assistant offers to choose which
  answers, each with its model (see The AI's model). The choice is the student's, kept in their
  browser, for everything the AI does for them.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Scenario: Ask a question while reading
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "What does the finite element method divide a domain into?"
    Then I see an answer that cites "1 Introduction"
    And I see the text "The finite element method divides a domain into small elements."

  Scenario: Summarise the section being read
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "Summarise this section"
    Then I see a summary drawn from "1 Introduction"

  Scenario: Take a quiz on the whole document
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "Quiz me with 2 questions on the whole document"
    And I answer every question with its first choice
    Then I see that I scored 2 out of 2

  Scenario: Summarise a topic
    When I open the course "Aeronautics"
    And I open the topic "Finite elements"
    And I open the assistant
    And I ask "Summarise this topic"
    Then I see a summary drawn from "1 Introduction"

  Scenario: There are no separate summary and quiz buttons
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    Then I see the buttons "Edit", "Download" and "AI" together
    But I see no "Summarise" or "Quiz me" button

  Scenario: Choose which provider answers, where the app has the keys of both
    Given qubit-notes has the key "sk-ant-test" for "anthropic" in its settings
    And qubit-notes has the key "sk-openai-test" for "openai" in its settings
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    Then I can choose the AI from "Anthropic · claude-sonnet-5-5, OpenAI · gpt-5"
    When I choose the AI "OpenAI · gpt-5"
    And I ask "What does the finite element method divide a domain into?"
    Then I see an answer that cites "1 Introduction"
    And the AI answered with "gpt-5" of "openai"

  Scenario: No choice of provider where the app has the key of one
    Given qubit-notes has the key "sk-ant-test" for "anthropic" in its settings
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    Then I am not offered to choose the AI

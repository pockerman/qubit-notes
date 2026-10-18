@ui
Feature: Asking the assistant in the browser
  As a student
  I want to ask the assistant from the page I am reading
  So that I can get answers, summaries and quizzes as I read

  An "AI" button next to "Edit" and "Download" opens the assistant beside the text. Summaries
  and quizzes are asked for there, in words: there are no separate buttons for them.

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
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "What does the finite element method divide a domain into?"
    Then I see an answer that cites "1 Introduction"
    And I see the text "The finite element method divides a domain into small elements."

  Scenario: Summarise the section being read
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "Summarise this section"
    Then I see a summary drawn from "1 Introduction"

  Scenario: Take a quiz on the whole document
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "Quiz me with 2 questions on the whole document"
    And I answer every question with its first choice
    Then I see that I scored 2 out of 2

  Scenario: Summarise a topic
    When I open the course "aeronautics"
    And I study the topic "finite-elements"
    And I open the assistant
    And I ask "Summarise this topic"
    Then I see a summary drawn from "1 Introduction"

  Scenario: There are no separate summary and quiz buttons
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    Then I see the buttons "Edit", "Download" and "AI" together
    But I see no "Summarise" or "Quiz me" button

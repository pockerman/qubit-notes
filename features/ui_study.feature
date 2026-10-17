@ui
Feature: Summaries and quizzes in the browser
  As a student
  I want to ask for summaries and quizzes on screen
  So that I can revise as I read

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Scenario: Summarise the section being read
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    And I ask for a summary of this section
    Then I see a summary drawn from "1 Introduction"

  Scenario: Take a quiz on the whole document
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    And I ask for a quiz of 2 questions on the whole document
    And I answer every question with its first choice
    Then I see that I scored 2 out of 2

  Scenario: Summarise a topic
    When I open the course "aeronautics"
    And I study the topic "finite-elements"
    And I ask for a summary of this topic
    Then I see a summary drawn from "1 Introduction"

@ui
Feature: Reading material in the browser
  As a student
  I want to read my material section by section on screen
  So that I can study without leaving the assistant

  Scenario: Open a material and read a section
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.

      ## 2.1 Linear elements
      A linear element interpolates linearly between its two nodes.
      """
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    Then I see its sections "1 Introduction, 2 Shape functions, 2.1 Linear elements"
    And I see the text "The finite element method divides a domain into small elements."
    When I choose the section "2.1 Linear elements"
    Then I see the text "A linear element interpolates linearly between its two nodes."

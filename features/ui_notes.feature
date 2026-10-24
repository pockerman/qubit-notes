@ui
Feature: Notes in the browser
  As a student
  I want to take notes on what I read and watch, on screen
  So that my thoughts stay next to the material

  Scenario: Take a note on a passage of a text
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I select "divides a domain into small elements" and note "compare with Galerkin's method"
    Then I see my note "compare with Galerkin's method"
    And the passage "divides a domain into small elements" is highlighted

  Scenario: The note opens beside the passage
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
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I choose the section "2 Shape functions"
    And I select the passage "interpolates linearly between its two nodes"
    Then the new note opens to the left of the text, level with "interpolates linearly between its two nodes"

  Scenario: Take a note on a video
    Given I am signed in as "maria"
    And I have uploaded the video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I open "lecture-3.mp4" to read it
    And I note "worked example" at the current moment of the video
    Then I see my note "worked example" at 00:00

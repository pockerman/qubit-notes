@ui
Feature: Writing material in the browser
  As a student
  I want to write a topic's material in an editor on screen
  So that I can type or paste my notes and see them formatted before I save them

  The editor has a "Write" tab, where the Markdown is typed or pasted, and a "Preview" tab,
  which shows it formatted the way the reader will.

  Background:
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    And I have created the topic "numerical-methods/finite-elements" in "aeronautics"

  Scenario: Write a material in a topic
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I name it "Shape functions"
    And I type:
      """
      # 1 Shape functions
      Shape functions interpolate the solution inside each element.
      """
    And I save it
    Then I am on the topic "Numerical methods" › "Finite elements"
    And I see its materials "shape-functions.md"
    When I open "shape-functions.md" to read it
    Then I see the text "Shape functions interpolate the solution inside each element."

  Scenario: Preview the material before saving it
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I type:
      """
      The **main** idea, in a table:

      | Element | Nodes |
      |---------|-------|
      | Linear  | 2     |
      """
    And I preview it
    Then "main" is in bold
    And I see a table with the columns "Element, Nodes"
    When I go back to writing
    Then the text I typed is still there

  Scenario: Leaving without saving asks first
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I type:
      """
      Notes I have not saved yet.
      """
    And I cancel, but choose to keep writing
    Then the text I typed is still there

  Scenario: A reader of a shared course is not offered to write material
    Given the student "maria" has shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    And I open the topic "Finite elements"
    Then I am not offered to write material

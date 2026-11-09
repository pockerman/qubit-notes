@ui
Feature: The writing assistant in the browser
  As a student writing material of my own
  I want the writing assistant beside the text I am writing or editing
  So that I can ask it for help and take what it writes into my material

  "Writing assistant", next to "Write" and "Preview" when writing material and next to "Save" when
  editing it, opens the writing assistant beside the text, in the place of the code editors (see
  The writing assistant). The student asks it for material on a subject, or chooses a section of
  their text, by its heading, for it to help with. "Search the web" is on unless they turn it off.

  Each reply is shown formatted, with its references below, numbered, linking to their addresses.
  It goes into the material, as Markdown, with its references after it, as links: "Insert" puts it
  where the cursor is, "Add at the end" after the rest, and, for a reply about a section, "Replace
  the section" in the place of that section's text, its heading kept. The conversation lasts while
  the page is open; "New conversation" starts another. Below each reply are a thumbs up and a
  thumbs down, as below the assistant's: the thumb chosen stays pressed, and choosing it again
  takes the rating back.

  Background:
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    And I have created the topic "numerical-methods/finite-elements" in "aeronautics"

  Scenario: Write material with the writing assistant
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I open the writing assistant
    And I ask the writing assistant in the browser "Write an introduction to the finite element method"
    Then I see its reply with its references
    When I add the reply at the end of the material
    Then the text has the reply, and its references as links

  Scenario: Help with a section, and replace it
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I type:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """
    And I open the writing assistant
    And I choose the section "2 Shape functions" for the writing assistant
    And I ask the writing assistant in the browser "Add a worked example to this section"
    And I replace the section with the reply
    Then the text has "# 1 Introduction"
    And the text has "The finite element method divides a domain into small elements."
    And the text has "# 2 Shape functions"
    And the text no longer has "Shape functions interpolate the solution inside each element."
    And the text has the reply, and its references as links

  Scenario: The writing assistant beside the material being edited
    Given I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I start editing the material
    And I open the writing assistant
    And I ask the writing assistant in the browser "Write a section on meshing"
    And I add the reply at the end of the material
    Then the text has "The finite element method divides a domain into small elements."
    And the text has the reply, and its references as links

  Scenario: Without searching the web
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I open the writing assistant
    And I turn off searching the web
    And I ask the writing assistant in the browser "Write an introduction to the finite element method"
    Then I see its reply without references

  Scenario: Rate a reply
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I open the writing assistant
    And I ask the writing assistant in the browser "Write an introduction to the finite element method"
    And I give the writing assistant's reply a thumbs up
    Then the thumbs up of the writing assistant's reply is pressed
    When I give the writing assistant's reply a thumbs down
    Then the thumbs down of the writing assistant's reply is pressed
    And the thumbs up of the writing assistant's reply is not pressed
    When I give the writing assistant's reply a thumbs down
    Then neither thumb of the writing assistant's reply is pressed

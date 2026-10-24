@ui
Feature: Generating material with the AI in the browser
  As a student
  I want to tick materials of a topic and have the AI write new material from them
  So that I can make revision notes and the like without leaving the topic

  On a topic's page, its owners tick materials and choose "Generate material". They pick a
  kind, or write instructions, or both, and the AI's Markdown opens in the editor, named for its
  kind, as if they had written it: they edit it, preview it, choose the topic to save it in (the
  one they are in, unless they choose another), and save it. Nothing is saved until they do.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Assembly
      The element matrices are assembled into the global stiffness matrix.
      """
    And I have uploaded "fe-meshing.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Meshing
      The domain is divided into triangles.
      """
    And I have created the topic "numerical-methods/linear-solvers" in "aeronautics"

  Scenario: Generate revision notes, preview them and save them in the topic
    When I open the course "aeronautics"
    And I open the topic "finite-elements"
    And I tick "fem-notes.md" and "fe-meshing.md"
    And I generate "Revision notes" from them
    Then the editor has the name "Revision notes"
    When I preview it
    Then I see the reference "2 Assembly" as a link
    When I save it
    Then I am on the topic "numerical-methods" › "finite-elements"
    And I see its materials "fem-notes.md, fe-meshing.md, revision-notes.md"

  Scenario: Save generated material in another topic
    When I open the course "aeronautics"
    And I open the topic "finite-elements"
    And I tick "fem-notes.md"
    And I generate "Cheat sheet" from them, with the instructions "One page at most"
    And I choose to save it in "numerical-methods" › "linear-solvers"
    And I save it
    Then I am on the topic "numerical-methods" › "linear-solvers"
    And I see its materials "cheat-sheet.md"

  Scenario: Nothing is saved when I leave without saving
    When I open the course "aeronautics"
    And I open the topic "finite-elements"
    And I tick "fem-notes.md"
    And I generate "Revision notes" from them
    And I cancel, and choose to discard it
    Then I am on the topic "numerical-methods" › "finite-elements"
    And I see its materials "fem-notes.md, fe-meshing.md"

  Scenario: Generating needs a material ticked
    When I open the course "aeronautics"
    And I open the topic "finite-elements"
    Then I cannot generate material until I tick one

  Scenario: A video cannot be ticked
    Given I have uploaded "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "aeronautics"
    And I open the topic "finite-elements"
    Then I cannot tick "lecture-3.mp4"

  Scenario: A reader of a shared course is not offered to generate material
    Given I have shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "aeronautics"
    And I open the topic "finite-elements"
    Then I am not offered to generate material

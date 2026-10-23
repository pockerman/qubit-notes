@ui
Feature: References between topics in the browser
  As a student
  I want to follow the references in my material, and add them without typing paths
  So that I can move between the topics of my course as I study

  A reference is a link: to a topic, it opens the course at that topic; to a material, it opens
  the material; to a section, it opens the material at that section. A broken reference is
  shown struck through and is not a link. While writing or editing, "Add reference" picks a
  topic, a material or a section of the course and puts its reference in the text; "How
  references work" beside it shows how they are written (see docs/references.md). The course
  page shows under each topic the materials it is mentioned in.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Assembly
      The element matrices are assembled into the global stiffness matrix.
      """
    And I have written the material "Sparse matrices" in "aeronautics/numerical-methods/linear-solvers" with the text:
      """
      # 1 Sparse matrices
      The stiffness matrix of [[numerical-methods/finite-elements|the FEM topic]] is sparse.
      It is assembled as in [[numerical-methods/finite-elements/fem-notes.md#2 Assembly]].
      Its solvers are in [[numerical-methods/linear-solver]].
      """

  Scenario: Follow a reference to a topic
    When I open the course "aeronautics"
    And I open "sparse-matrices.md" to read it
    And I follow the reference "the FEM topic"
    Then I am in the course "aeronautics" at the topic "numerical-methods" › "finite-elements"

  Scenario: Follow a reference to a section
    When I open the course "aeronautics"
    And I open "sparse-matrices.md" to read it
    And I follow the reference "2 Assembly"
    Then I am reading "fem-notes.md" at the section "2 Assembly"
    And I see the text "The element matrices are assembled into the global stiffness matrix."

  Scenario: A broken reference is not a link
    When I open the course "aeronautics"
    And I open "sparse-matrices.md" to read it
    Then I see the reference "linear-solver" as broken

  Scenario: Add a reference while writing
    When I open the course "aeronautics"
    And I write material in the topic "linear-solvers"
    And I name it "Iterative solvers"
    And I type:
      """
      Conjugate gradients solve the system from
      """
    And I add a reference to the section "2 Assembly" of "fem-notes.md" in "numerical-methods" › "finite-elements"
    Then the text I typed ends with "[[numerical-methods/finite-elements/fem-notes.md#2 Assembly]]"
    When I preview it
    Then I see the reference "2 Assembly" as a link

  Scenario: See how references are written while writing
    When I open the course "aeronautics"
    And I write material in the topic "linear-solvers"
    And I open the help on references
    Then I see how to refer to a topic, a material and a section
    And I see that a label follows a "|"

  Scenario: Saving with a broken reference tells which
    When I open the course "aeronautics"
    And I write material in the topic "linear-solvers"
    And I name it "Iterative solvers"
    And I type:
      """
      As in [[numerical-methods/finite-element]].
      """
    And I save it
    Then I am told the reference "[[numerical-methods/finite-element]]" is broken
    And I see "iterative-solvers.md" under "numerical-methods" › "linear-solvers"

  Scenario: A topic shows the materials it is mentioned in
    When I open the course "aeronautics"
    Then the topic "finite-elements" is mentioned in "sparse-matrices.md"
    When I open the mention "sparse-matrices.md"
    Then I am reading "sparse-matrices.md"

  Scenario: A reader of a shared course follows references
    Given I have shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "aeronautics"
    And I open "sparse-matrices.md" to read it
    And I follow the reference "2 Assembly"
    Then I am reading "fem-notes.md" at the section "2 Assembly"

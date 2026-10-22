Feature: Editing material
  As a student
  I want to correct and extend my own notes in the assistant
  So that what I study from, and what the assistant writes from it, stays right

  The text of a Markdown or plain text material can be edited by the owners of its course.
  Once saved, the material is processed again: it is read, searched, summarised and quizzed
  as its new text. A PDF or a video cannot be edited.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      A linear element interpolates linearly between its two nodes.
      """

  Rule: The owners of a course edit the text of its Markdown and text material

    @platform
    Scenario: Edit a material
      When I change the text of "fem-notes.md" to:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Shape functions
        A linear element interpolates linearly between its two nodes.

        # 3 Assembly
        The element matrices are assembled into the global stiffness matrix.
        """
      Then "fem-notes.md" is eventually ready
      And I see the sections:
        | section           | level |
        | 1 Introduction    | 1     |
        | 2 Shape functions | 1     |
        | 3 Assembly        | 1     |
      And I read "The element matrices are assembled" in the section "3 Assembly" of "fem-notes.md"

    Scenario: Start editing from the material as it is
      When I open "fem-notes.md" for editing
      Then I am given its text exactly as I uploaded it

    @platform
    Scenario: Searching finds the new text, not the old
      When I change the text of "fem-notes.md" to:
        """
        # 1 Introduction
        Galerkin's method weights the residual with the shape functions.
        """
      And "fem-notes.md" is eventually ready
      Then searching "aeronautics" for "Galerkin residual" finds "fem-notes.md"
      But searching "aeronautics" no longer finds the text "divides a domain into small elements"

    Scenario Outline: Only Markdown and text material can be edited
      Given I have uploaded "<filename>" to "aeronautics/numerical-methods/finite-elements"
      When I change the text of "<filename>" to "anything"
      Then I am told only Markdown and text material can be edited

      Examples:
        | filename      |
        | lecture-1.pdf |
        | lecture-3.mp4 |

    Scenario: A reader of a shared course cannot edit its material
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" changes the text of "fem-notes.md" to "anything"
      Then the student "tom" is not allowed to do that

    Scenario: A material cannot be emptied
      When I change the text of "fem-notes.md" to ""
      Then I am told the material cannot be empty

  Rule: What was made from a material follows its edits

    Scenario: Notes stay on their passage when it is still there
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      When I change the text of "fem-notes.md" to:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Linear elements
        A linear element interpolates linearly between its two nodes.
        """
      Then the notes of "fem-notes.md" are:
        | section           | passage               | note           |
        | 2 Linear elements | between its two nodes | why two nodes? |

    Scenario: A note whose passage was removed is kept, marked as detached
      Given I have noted "compare with Galerkin" on "divides a domain" in "1 Introduction" of "fem-notes.md"
      When I change the text of "fem-notes.md" to:
        """
        # 1 Introduction
        Finite elements approximate the solution piecewise.
        """
      Then the note "compare with Galerkin" is detached, as its passage "divides a domain" is no longer there

    @ai
    Scenario: Summaries and quizzes of an edited material are out of date
      Given I have asked for a summary of "fem-notes.md"
      And I have asked for a quiz of 2 questions on "fem-notes.md"
      When I change the text of "fem-notes.md" to:
        """
        # 1 Introduction
        Finite elements approximate the solution piecewise.
        """
      And I ask for a summary of "fem-notes.md"
      Then I get the summary I got before
      But I am told it is out of date, as "fem-notes.md" was edited since

@wip
Feature: Notes
  As a student
  I want to take notes on parts of my material, texts and videos alike
  So that my own thoughts stay next to what they are about

  A note on a text is anchored to a passage: the words selected in a section.
  A note on a video is anchored to a moment in it, e.g. 12:30.
  Notes are private: only the student who took them sees them, even in a shared course.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      A linear element interpolates linearly between its two nodes.
      """

  Rule: A note on a text is anchored to a passage

    Scenario: Take a note on a passage
      When I note "compare with Galerkin's method" on "divides a domain into small elements" in "1 Introduction" of "fem-notes.md"
      Then the notes of "fem-notes.md" are:
        | section        | passage                              | note                           |
        | 1 Introduction | divides a domain into small elements | compare with Galerkin's method |

    Scenario: Notes are listed in the order of the document
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      And I have noted "compare with Galerkin's method" on "divides a domain" in "1 Introduction" of "fem-notes.md"
      When I list the notes of "fem-notes.md"
      Then the notes of "fem-notes.md" are:
        | section           | passage               | note                           |
        | 1 Introduction    | divides a domain      | compare with Galerkin's method |
        | 2 Shape functions | between its two nodes | why two nodes?                 |

    Scenario: A note can only be anchored to words in its section
      When I note "typo?" on "words that are not there" in "1 Introduction" of "fem-notes.md"
      Then I am told the passage is not in that section

  Rule: A note on a video is anchored to a moment

    Scenario: Take a note at a moment of a video
      Given I have uploaded the video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      When I note "derivation of the stiffness matrix" at 12:30 of "lecture-3.mp4"
      And I note "worked example" at 03:05 of "lecture-3.mp4"
      Then the notes of "lecture-3.mp4" are:
        | at    | note                               |
        | 03:05 | worked example                     |
        | 12:30 | derivation of the stiffness matrix |

    Scenario: A note cannot be after the end of a video
      Given I have uploaded the 45-minute video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      When I note "too late" at 50:00 of "lecture-3.mp4"
      Then I am told the video is only 45:00 long

  Rule: Notes can be changed and deleted

    Scenario: Edit a note
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      When I change the note "why two nodes?" to "two nodes, so linear"
      Then the notes of "fem-notes.md" are:
        | section           | passage               | note                 |
        | 2 Shape functions | between its two nodes | two nodes, so linear |

    Scenario: Delete a note
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      When I delete the note "why two nodes?"
      Then "fem-notes.md" has no notes

    Scenario: Deleting a material deletes its notes
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then I have no notes

  Rule: Notes are private

    Scenario: A reader of a shared course does not see the owner's notes
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      Then the student "tom" sees no notes on "fem-notes.md"

    Scenario: A reader of a shared course takes their own notes
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" notes "ask in class" on "two nodes" in "2 Shape functions" of "fem-notes.md"
      Then the student "tom" sees 1 note on "fem-notes.md"
      But "fem-notes.md" has no notes

@wip
Feature: Summaries
  As a student
  I want the assistant to summarise a section, a whole document or a whole topic
  So that I can revise the main points quickly

  A summary is written by the AI from the material it summarises, and cites the
  sections it draws on. Summaries are saved: asking for a summary again shows the
  saved one, and a new one is written only when the student asks for a new one.
  Earlier summaries are kept, newest first.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.

      ## 2.1 Linear elements
      A linear element interpolates linearly between its two nodes.

      # 3 Assembly
      The element matrices are assembled into the global stiffness matrix.
      """

  Rule: A section, a document or a topic can be summarised

    @gogi
    Scenario: Summarise a section
      When I ask for a summary of the section "2 Shape functions" of "fem-notes.md"
      Then I get a summary
      And the summary cites only:
        | material     | section             |
        | fem-notes.md | 2 Shape functions   |
        | fem-notes.md | 2.1 Linear elements |

    Scenario: Summarise a whole document
      When I ask for a summary of "fem-notes.md"
      Then I get a summary
      And the summary cites every section of "fem-notes.md"

    @gogi
    Scenario: Summarise a topic from all of its material
      Given I have uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have uploaded "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
      When I ask for a summary of the topic "aeronautics/numerical-methods/finite-elements"
      Then I get a summary
      And the summary cites "fem-notes.md" and "fe-meshing.txt"
      But the summary does not cite "fd-schemes.txt"

    Scenario: Videos are not summarised
      Given I have uploaded the video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      When I ask for a summary of the topic "aeronautics/numerical-methods/finite-elements"
      Then the summary cites "fem-notes.md"
      But the summary does not cite "lecture-3.mp4"

    Scenario: A topic without material cannot be summarised
      When I ask for a summary of the topic "aeronautics/numerical-methods/spectral-methods"
      Then I am told there is no material to summarise

  Rule: Summaries are saved, and new ones are written only on request

    Scenario: Asking again shows the saved summary
      Given I have asked for a summary of the section "3 Assembly" of "fem-notes.md"
      When I ask for a summary of the section "3 Assembly" of "fem-notes.md"
      Then I get the summary I got before
      And no new summary was written

    Scenario: Ask for a new summary
      Given I have asked for a summary of the section "3 Assembly" of "fem-notes.md"
      When I ask for a new summary of the section "3 Assembly" of "fem-notes.md"
      Then I get a summary I have not seen before
      And the summaries of the section "3 Assembly" of "fem-notes.md" are, newest first:
        | summary |
        | new     |
        | earlier |

    Scenario: A topic summary is out of date once the topic's material changes
      Given I have asked for a summary of the topic "aeronautics/numerical-methods/finite-elements"
      When I upload the file "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      And I ask for a summary of the topic "aeronautics/numerical-methods/finite-elements"
      Then I get the summary I got before
      But I am told it is out of date, as "fe-meshing.txt" was added since

    Scenario: Deleting a material deletes its summaries
      Given I have asked for a summary of "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then I have no summaries of "fem-notes.md"

  Rule: Summaries are private

    Scenario: A reader of a shared course gets their own summaries
      Given I have asked for a summary of "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" asks for a summary of "fem-notes.md"
      Then the student "tom" gets a summary written for them

@ai
Feature: Generating material with the AI
  As a student
  I want the AI to write new material from materials I choose
  So that I get revision notes, cheat sheets and worked examples drawn from my own material

  The owners of a course choose materials of a topic and say what to make: one of the kinds
  below, their own instructions, or both. The AI writes Markdown from the materials' text,
  using nothing else, and cites the sections it drew on with references to them (see References
  between topics), so they are links in the new material and the topic is mentioned in it.

    | kind            | named           |
    | revision notes  | Revision notes  |
    | cheat sheet     | Cheat sheet     |
    | combined notes  | Combined notes  |
    | worked examples | Worked examples |

  With instructions only, it is named "Generated notes". What the AI writes is not saved: the
  student reads it, edits it, names it and saves it like material they wrote, in the topic of
  their choice (see Writing material). Videos have no text, so they can't be chosen; the
  material chosen must be ready, and at most 60,000 characters in all.

  Background:
    Given I am the student "maria"
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

  Rule: The AI writes new material from the materials chosen

    @platform
    Scenario: Generate revision notes from two materials
      When I generate "revision notes" from "fem-notes.md, fe-meshing.md"
      Then I am given Markdown named "Revision notes"
      And it is drawn from the sections "1 Introduction, 2 Assembly, 1 Meshing"
      And the materials of "aeronautics/numerical-methods/finite-elements" are:
        | filename      |
        | fem-notes.md  |
        | fe-meshing.md |

    Scenario: The generated material cites its sources with references
      When I generate "revision notes" from "fem-notes.md"
      Then its text refers to "[[numerical-methods/finite-elements/fem-notes.md#1 Introduction]]"
      And its text refers to "[[numerical-methods/finite-elements/fem-notes.md#2 Assembly]]"
      And none of its references is broken

    Scenario Outline: The kinds of material
      When I generate "<kind>" from "fem-notes.md"
      Then I am given Markdown named "<name>"
      And the AI was asked for <asked>

      Examples:
        | kind            | name            | asked                                                     |
        | revision notes  | Revision notes  | revision notes                                            |
        | cheat sheet     | Cheat sheet     | a cheat sheet                                             |
        | combined notes  | Combined notes  | the materials combined into one set of notes              |
        | worked examples | Worked examples | worked examples                                           |

    Scenario: Instructions in the student's own words
      When I generate from "fem-notes.md" with the instructions "Five questions to test myself on assembly"
      Then I am given Markdown named "Generated notes"
      And the AI was asked for "Five questions to test myself on assembly"

    Scenario: A kind and instructions together
      When I generate "cheat sheet" from "fem-notes.md" with the instructions "One page at most"
      Then I am given Markdown named "Cheat sheet"
      And the AI was asked for a cheat sheet
      And the AI was asked for "One page at most"

    Scenario: Each generation is new
      Given I have generated "revision notes" from "fem-notes.md"
      When I generate "revision notes" from "fem-notes.md"
      Then I am given Markdown unlike the last

  Rule: What the AI wrote is saved like written material, in any topic

    @platform
    Scenario: Save generated material in another topic
      Given I have generated "revision notes" from "fem-notes.md"
      When I write the material "FEM revision" in "aeronautics/numerical-methods/linear-solvers" with the generated text
      Then "fem-revision.md" is eventually ready
      And the topic "numerical-methods/finite-elements" of "aeronautics" is mentioned in:
        | subject           | topic          | material        |
        | numerical-methods | linear-solvers | fem-revision.md |

  Rule: Only material with text, ready and not too much, by the owners of its course

    Scenario: Something must be chosen and asked for
      When I generate "revision notes" from ""
      Then I am told to choose at least one material
      When I generate from "fem-notes.md" with the instructions ""
      Then I am told to choose a kind or write instructions

    Scenario: A video cannot be chosen
      Given I have uploaded "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      When I generate "revision notes" from "fem-notes.md, lecture-3.mp4"
      Then I am told "lecture-3.mp4" is a video, with no text to generate from

    Scenario: Material that isn't ready cannot be chosen
      Given I have just uploaded "fe-volumes.md" to "aeronautics/numerical-methods/finite-elements"
      When I generate "revision notes" from "fe-volumes.md"
      Then I am told "fe-volumes.md" is not ready yet

    Scenario: Too much material at once
      Given the most material generated from at once is 100 characters
      When I generate "revision notes" from "fem-notes.md, fe-meshing.md"
      Then I am told the material chosen is too long, and to choose less

    Scenario: A reader of a shared course cannot generate material
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" generates "revision notes" from "fem-notes.md"
      Then the student "tom" is not allowed to do that

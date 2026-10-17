@wip
Feature: Quizzes
  As a student
  I want the assistant to quiz me on a section, a whole document or a whole topic
  So that I find out what I know and what I need to study again

  A quiz is written by the AI from the material it covers. Each question has four
  choices, one of them correct, and cites the section it comes from. Quizzes are saved:
  asking for a quiz again shows the saved one, and a new one is written only when the
  student asks for a new one. Earlier quizzes are kept, newest first.

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

  Rule: A section, a document or a topic can be quizzed

    @gogi
    Scenario: Get a quiz on a section
      When I ask for a quiz of 3 questions on the section "2 Shape functions" of "fem-notes.md"
      Then I get a quiz of 3 questions
      And every question has 4 choices, one of them correct
      And every question cites one of the sections "2 Shape functions" or "2.1 Linear elements" of "fem-notes.md"

    Scenario: Get a quiz on a whole document
      When I ask for a quiz of 5 questions on "fem-notes.md"
      Then I get a quiz of 5 questions
      And every question cites a section of "fem-notes.md"

    @gogi
    Scenario: Get a quiz on a topic from all of its material
      Given I have uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have uploaded "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
      When I ask for a quiz of 6 questions on the topic "aeronautics/numerical-methods/finite-elements"
      Then I get a quiz of 6 questions
      And the questions cite "fem-notes.md" and "fe-meshing.txt"
      But no question cites "fd-schemes.txt"

    Scenario: Videos are not quizzed
      Given I have uploaded the video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      When I ask for a quiz of 3 questions on the topic "aeronautics/numerical-methods/finite-elements"
      Then no question cites "lecture-3.mp4"

    Scenario Outline: A quiz has between 1 and 20 questions
      When I ask for a quiz of <count> questions on "fem-notes.md"
      Then I am told a quiz has between 1 and 20 questions

      Examples:
        | count |
        | 0     |
        | 21    |

  Rule: Quizzes are saved, and new ones are written only on request

    Scenario: Asking again shows the saved quiz
      Given I have asked for a quiz of 3 questions on the section "3 Assembly" of "fem-notes.md"
      When I ask for a quiz of 3 questions on the section "3 Assembly" of "fem-notes.md"
      Then I get the quiz I got before
      And no new quiz was written

    Scenario: Ask for a new quiz
      Given I have asked for a quiz of 3 questions on the section "3 Assembly" of "fem-notes.md"
      When I ask for a new quiz of 3 questions on the section "3 Assembly" of "fem-notes.md"
      Then I get a quiz I have not seen before
      And I have 2 quizzes on the section "3 Assembly" of "fem-notes.md", newest first

    Scenario: A topic quiz is out of date once the topic's material changes
      Given I have asked for a quiz of 3 questions on the topic "aeronautics/numerical-methods/finite-elements"
      When I upload the file "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      And I ask for a quiz of 3 questions on the topic "aeronautics/numerical-methods/finite-elements"
      Then I get the quiz I got before
      But I am told it is out of date, as "fe-meshing.txt" was added since

    Scenario: Deleting a material deletes its quizzes
      Given I have asked for a quiz of 3 questions on "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then I have no quizzes on "fem-notes.md"

  Rule: A quiz is taken and scored

    Scenario: Take a quiz
      Given I have a quiz of 3 questions on "fem-notes.md"
      When I answer 2 of its questions correctly and 1 wrongly
      Then my score is 2 out of 3
      And for the question I got wrong I see the correct answer and the section to study again

    Scenario: A quiz can be taken again
      Given I have taken a quiz of 3 questions on "fem-notes.md" and scored 1 out of 3
      When I take it again and answer every question correctly
      Then my scores for the quiz are, newest first:
        | score  |
        | 3 of 3 |
        | 1 of 3 |

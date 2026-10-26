@ai
Feature: Asking the assistant
  As a student
  I want to ask the assistant about my material in my own words
  So that I can get answers, summaries, quizzes and flashcards without looking for the right button

  The student asks while reading a material or studying a topic. The assistant answers
  questions from the course's material only, and cites the sections its answer draws on;
  when the material does not cover the question, it says so rather than answer from
  elsewhere. A request for a summary, a quiz or flashcards is recognised as one, and gets
  the same saved summary, quiz or deck the student would get by asking for it directly (see
  Summaries, Quizzes and Flashcards). "This section", "this document" and "this topic" refer to what the student
  is reading or studying.

  The assistant keeps the conversation of each student on each material and each topic,
  so follow-up questions can refer to what was said before, and the conversation is
  there when the student comes back to it. A student can start a new conversation.

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

  Rule: Questions are answered from the course's material, citing it

    @platform
    Scenario: Ask a question about the material being read
      Given I am reading the section "1 Introduction" of "fem-notes.md"
      When I ask the assistant "What does the finite element method divide a domain into?"
      Then the assistant answers
      And the answer cites the section "1 Introduction" of "fem-notes.md"

    Scenario: A question is answered from all of the course's material
      Given I have uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements" with the content:
        """
        A mesh of triangles is generated with Delaunay triangulation.
        """
      And I am reading the section "1 Introduction" of "fem-notes.md"
      When I ask the assistant "How is a mesh of triangles generated?"
      Then the answer cites "fe-meshing.txt"

    Scenario: A question the material does not cover
      Given I am reading the section "1 Introduction" of "fem-notes.md"
      When I ask the assistant "Who won the 1998 World Cup?"
      Then the assistant tells me my material does not cover it
      And the answer cites nothing

  Rule: Requests for summaries, quizzes and flashcards are recognised

    @platform
    Scenario: Ask for a summary of the section being read
      Given I am reading the section "2 Shape functions" of "fem-notes.md"
      When I ask the assistant "Summarise this section"
      Then the assistant gives me a summary of the section "2 Shape functions" of "fem-notes.md"

    Scenario Outline: Ask for a summary of a document or a topic
      Given I am reading the section "1 Introduction" of "fem-notes.md"
      When I ask the assistant "<request>"
      Then the assistant gives me a summary of <scope>

      Examples:
        | request                         | scope                                                     |
        | Summarise the whole document    | "fem-notes.md"                                            |
        | Give me a summary of this topic | the topic "aeronautics/numerical-methods/finite-elements" |

    Scenario: A summary asked for again is the saved one, unless a new one is asked for
      Given I am reading the section "3 Assembly" of "fem-notes.md"
      And I have asked the assistant "Summarise this section"
      When I ask the assistant "Summarise this section"
      Then the assistant gives me the summary I got before
      When I ask the assistant "Write a new summary of this section"
      Then the assistant gives me a summary I have not seen before

    Scenario: Ask for a quiz
      Given I am reading the section "1 Introduction" of "fem-notes.md"
      When I ask the assistant "Quiz me with 3 questions on the whole document"
      Then the assistant gives me a quiz of 3 questions on "fem-notes.md"

    Scenario: Ask for flashcards
      Given I am reading the section "1 Introduction" of "fem-notes.md"
      When I ask the assistant "Make 4 flashcards of the whole document"
      Then the assistant gives me 4 flashcards of "fem-notes.md"
      And I have 4 cards due for review

  Rule: The conversation is kept

    Scenario: A follow-up question refers to the earlier one
      Given I am reading the section "2 Shape functions" of "fem-notes.md"
      And I have asked the assistant "What do shape functions do?"
      When I ask the assistant "And between how many nodes does a linear one interpolate?"
      Then the assistant is given my earlier question and its answer
      And the answer cites the section "2.1 Linear elements" of "fem-notes.md"

    Scenario: The conversation is there when I come back
      Given I have asked the assistant "What do shape functions do?" while reading "fem-notes.md"
      When I open "fem-notes.md" again
      Then my conversation with the assistant on "fem-notes.md" shows "What do shape functions do?" and its answer

    Scenario: Start a new conversation
      Given I have asked the assistant "What do shape functions do?" while reading "fem-notes.md"
      When I start a new conversation on "fem-notes.md"
      Then my conversation with the assistant on "fem-notes.md" is empty
      And the assistant is not given my earlier question

    Scenario: Conversations are private
      Given I have asked the assistant "What do shape functions do?" while reading "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" opens "fem-notes.md"
      Then the conversation of "tom" with the assistant on "fem-notes.md" is empty

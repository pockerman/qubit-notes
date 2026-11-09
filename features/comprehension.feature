@ai
Feature: Checking my understanding
  As a student
  I want the assistant to question me on my material and tell me how well I understood it
  So that I find out what I really understand, and what to study again

  The comprehension assistant (ComprehensionAssistantAgent) checks a student's understanding of a
  section (with its subsections), a whole material, a topic, or a whole subject: every text of
  every topic of it. It asks one open question at a time, from the material, citing the section
  it comes from, and testing understanding rather than recall of wording. The student answers in
  their own words, typed or spoken (see Answering by voice). The assistant then tells them whether
  they understood it ("yes", "partly" or "no"), why, citing the sections that say so, and asks the
  next question, following up on what they got wrong or left out. Each question and assessment is
  given what was asked and answered before in the check.

  The student ends a check when they like, having answered at least one question, and gets its
  verdict: a summary of how well they understood the material, what they understood, and the
  sections to study again. A check asks at most 20 questions; after the 20th answer it asks no
  more, and waits to be ended. An ended check takes no more answers.

  Checks are kept, each student's their own: those of a section, a material, a topic or a subject
  are listed newest first, and an unfinished one can be taken up again. Anyone who can read the
  course can check their understanding of it. A check can be deleted, and is deleted with its
  material, or the course. Videos have no text, so a topic's or a subject's are left out, and a
  video on its own can't be checked. What the AI takes is counted in the student's usage as
  "comprehension".

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
      """

  Rule: It asks questions from the material, citing it

    Scenario: Check my understanding of a section
      When I check my understanding of the section "2 Shape functions" of "fem-notes.md"
      Then the assistant asks me a question
      And the question cites one of the sections "2 Shape functions" or "2.1 Linear elements" of "fem-notes.md"

    Scenario: Check my understanding of a whole material
      When I check my understanding of "fem-notes.md"
      Then the assistant asks me a question
      And the assistant was given the sections "1 Introduction", "2 Shape functions" and "2.1 Linear elements"

    Scenario: Check my understanding of a topic, from all of its material
      Given I have uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have uploaded "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
      When I check my understanding of the topic "aeronautics/numerical-methods/finite-elements"
      Then the assistant asks me a question
      And the assistant was given "fem-notes.md" and "fe-meshing.txt"
      But the assistant was not given "fd-schemes.txt"

    Scenario: Check my understanding of a whole subject, from every topic of it
      Given I have uploaded "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
      And I have uploaded "wings.txt" to "aeronautics/aerodynamics/wings"
      When I check my understanding of the subject "aeronautics/numerical-methods"
      Then the assistant asks me a question
      And the assistant was given "fem-notes.md" and "fd-schemes.txt"
      But the assistant was not given "wings.txt"

    Scenario: A video has no text to question me on
      Given I have uploaded the video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      When I check my understanding of "lecture-3.mp4"
      Then I am told "lecture-3.mp4" is a video, with no text to question me on

    Scenario: A subject with no material
      Given I have created the subject "Structures" in "aeronautics"
      When I check my understanding of the subject "aeronautics/structures"
      Then I am told there is no material to question me on

  Rule: It assesses each answer, and asks the next question

    Scenario: Answer a question I understood
      Given I am checking my understanding of the section "2 Shape functions" of "fem-notes.md"
      When I answer "Shape functions interpolate the solution inside each element"
      Then the assistant says I understood it "yes", citing the material
      And the assistant asks me the next question

    Scenario: Answer a question I didn't understand
      Given I am checking my understanding of the section "2 Shape functions" of "fem-notes.md"
      When I answer "I don't know"
      Then the assistant says I understood it "no", citing the material
      And the assistant asks me the next question

    Scenario: The assistant is given what was asked and answered before
      Given I am checking my understanding of "fem-notes.md"
      And I have answered "The method divides a domain into elements"
      When I answer "I am not sure"
      Then the assistant was given my earlier answer "The method divides a domain into elements"

    Scenario: A spoken answer is kept as spoken
      Given I am checking my understanding of "fem-notes.md"
      When I answer "Shape functions interpolate the solution", having said it
      Then my answer is kept as spoken

    Scenario: An answer needs words
      Given I am checking my understanding of "fem-notes.md"
      When I answer nothing
      Then I am told to answer the question

    Scenario: After 20 questions it asks no more
      Given I am checking my understanding of "fem-notes.md"
      When I answer 20 questions
      Then the assistant asks me no more questions
      And I am told to end the check when I answer again

  Rule: Ending a check gives its verdict

    Scenario: End a check
      Given I am checking my understanding of the section "2 Shape functions" of "fem-notes.md"
      And I have answered "Shape functions interpolate the solution inside each element"
      And I have answered "I don't know"
      When I end the check
      Then I get a verdict with a summary, what I understood and the sections to study again
      And the check is ended

    Scenario: An ended check takes no more answers
      Given I am checking my understanding of "fem-notes.md"
      And I have answered "I don't know"
      And I have ended the check
      When I answer "Now I know"
      Then I am told the check is ended

    Scenario: A check needs an answer before it ends
      Given I am checking my understanding of "fem-notes.md"
      When I end the check
      Then I am told to answer at least one question first

  Rule: Checks are kept, each student's their own

    Scenario: Take up a check again
      Given I am checking my understanding of "fem-notes.md"
      And I have answered "I don't know"
      When I open the check again
      Then it has my answer "I don't know" and the question after it

    Scenario: My checks are listed newest first
      Given I have checked my understanding of "fem-notes.md"
      And I have checked my understanding of "fem-notes.md" again
      When I list my checks of "fem-notes.md"
      Then I see 2 checks, the newest first

    Scenario: Delete a check
      Given I have checked my understanding of "fem-notes.md"
      When I delete the check
      Then I have no checks of "fem-notes.md"

    Scenario: Another student's check is their own
      Given I have checked my understanding of "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" opens my check
      Then the check is not found
      And the student "tom" has no checks of "fem-notes.md"

    Scenario: A reader checks their understanding
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" checks their understanding of "fem-notes.md"
      Then the assistant asks them a question

    Scenario: A student of another course can't check it
      When the student "pedro" checks their understanding of "fem-notes.md"
      Then the check is refused, the course not being shared with them

    Scenario: A check is deleted with its material
      Given I have checked my understanding of "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then no check of mine is kept

    Scenario: A check is deleted with the course
      Given I have checked my understanding of "fem-notes.md"
      When I delete the course "aeronautics"
      Then no check of mine is kept

    Scenario: What it takes is counted in my usage
      When I check my understanding of "fem-notes.md"
      Then my AI usage has "comprehension"

@ui
Feature: Checking my understanding in the browser
  As a student
  I want the comprehension assistant beside what I am reading or studying
  So that I can be questioned on it, by typing or saying my answers, and see how well I understood it

  "Check understanding", next to "AI" in the reader and on a topic's page, and on a subject's page,
  opens the comprehension assistant beside the material (see Checking my understanding). In the
  reader it checks the section being read, or, chosen, the whole material; on a topic's page the
  topic, and on a subject's page the whole subject. It lists the student's earlier checks of it,
  newest first, to take up again, see the verdict of, or delete, and starts a new one.

  Each question is shown with the section it comes from; each answer with how well it was
  understood, and why. The student types their answer, or records it with "Record", stops with
  "Stop", and corrects what was heard before they send it (see Answering by voice); the model that
  hears it is chosen as the speech model is, and kept in their browser. "End the check" shows the
  verdict: its summary, what they understood, and the sections to study again.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Scenario: Check my understanding of what I am reading
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the comprehension check
    And I start a check of "the whole material"
    Then I see the assistant's question
    When I type the answer "I don't know"
    Then I see how well I understood it
    And I see the assistant's next question
    When I end the check in the browser
    Then I see the verdict, with what to study again

  Scenario: Say my answer
    Given the app can hear with OpenAI
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the comprehension check
    And I start a check of "the whole material"
    And I record my answer and stop
    Then my answer reads "What I said, as heard by gpt-4o-mini-transcribe"
    When I send my answer
    Then I see how well I understood it

  Scenario: Check my understanding of a whole subject
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the comprehension check
    And I start a check of "the whole subject"
    Then I see the assistant's question

  Scenario: Take up an earlier check again
    When I open the course "Aeronautics"
    And I open the topic "Finite elements"
    And I open the comprehension check
    And I start a check of "the topic"
    And I type the answer "I don't know"
    And I close the comprehension check
    And I open the comprehension check
    Then I see 1 earlier check
    When I take up the earlier check
    Then I see my answer "I don't know"

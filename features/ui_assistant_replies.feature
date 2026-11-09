@ui
Feature: Copying and rating the assistant's replies in the browser
  As a student
  I want to copy what the assistant replied, and to say whether it was good
  So that I can use its answer elsewhere, and help it answer better

  Below each reply of the assistant are "Copy", which copies the reply as Markdown (a quiz with
  its questions and choices, flashcards with their fronts and backs) and says "Copied", and a
  thumbs up and a thumbs down. The thumb chosen stays pressed, also when the conversation is
  opened again; choosing it again takes the rating back (see Rating the assistant's replies).

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "What does the finite element method divide a domain into?"

  Scenario: Copy an answer
    When I copy the assistant's reply
    Then I am told it was copied
    And what I copied is the assistant's answer

  Scenario: Copy a quiz
    When I ask "Quiz me with 2 questions on the whole document"
    And I copy the assistant's reply
    Then what I copied has the quiz's questions and their choices

  Scenario: Rate a reply
    When I give the assistant's reply a thumbs up
    Then the thumbs up of the reply is pressed
    When I come back to the page later
    And I open the assistant
    Then the thumbs up of the reply is pressed

  Scenario: Change and take back a rating
    When I give the assistant's reply a thumbs up
    And I give the assistant's reply a thumbs down
    Then the thumbs down of the reply is pressed
    And the thumbs up of the reply is not pressed
    When I give the assistant's reply a thumbs down
    Then neither thumb of the reply is pressed

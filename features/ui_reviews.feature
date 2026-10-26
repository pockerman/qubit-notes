@ui
Feature: Flashcards and reviews in the browser
  As a student
  I want to get flashcards from the assistant and review them when they are due
  So that I learn my material by heart without keeping track of what to study when

  Flashcards are asked for from the assistant, in words, as summaries and quizzes are. A card
  is turned over to show its answer. Reviews, in the app's menu, shows the cards due in all of
  the student's courses one at a time: the student shows its answer and says how well they
  remembered it, Again, Hard, Good or Easy, and the next card due follows.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Scenario: Get flashcards from the assistant
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the assistant
    And I ask "Make 2 flashcards of the whole document"
    Then I see a deck of 2 flashcards
    When I turn over its first card
    Then I see the answer of its first card

  Scenario: Review the cards due
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    Then I see that 2 cards are due
    When I show the answer and remembered it "Good"
    Then I see that 1 card is due
    When I show the answer and remembered it "Again"
    Then I am told there is nothing to review now, and when the next card is due

  Scenario: Nothing to review
    When I choose "Reviews" from the menu
    Then I am told there is nothing to review now

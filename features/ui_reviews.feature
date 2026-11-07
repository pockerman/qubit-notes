@ui
Feature: Flashcards and reviews in the browser
  As a student
  I want to get flashcards from the assistant and review them when they are due
  So that I learn my material by heart without keeping track of what to study when

  Flashcards are asked for from the assistant, in words, as summaries and quizzes are. A card
  is turned over to show its answer. Reviews, in the app's menu, lists the cards due by course,
  by subject, by material and by section, with how many are due in each, and the student chooses
  what to review: a section, a material, a subject, a course or all of them. Those cards come one at a time: the
  student shows its answer and says how well they remembered it, Again, Hard, Good or Easy, and
  the next card due follows, until none is left there. Below them, History
  shows the student's latest 50 reviews, newest first, each with its card, its course, how well
  they remembered it and when, and how long until it was due again.

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
    When I choose to review "All my cards"
    Then I see that 2 cards are due
    When I show the answer and remembered it "Good"
    Then I see that 1 card is due
    When I show the answer and remembered it "Again"
    Then I am told there is nothing to review now, and when the next card is due

  Scenario: The cards due are listed by course, subject, material and section
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    Then I see the cards due:
      | what              | cards   |
      | All my cards      | 2 cards |
      | Aeronautics       | 2 cards |
      | Numerical methods | 2 cards |
      | fem-notes.md      | 2 cards |
      | 1 Introduction    | 1 card  |
      | 2 Shape functions | 1 card  |
    And I am shown no card until I choose what to review

  Scenario: Review one section
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "2 Shape functions"
    Then I see that 1 card is due
    And the card shown is from "fem-notes.md › 2 Shape functions"
    When I show the answer and remembered it "Good"
    Then I am told there is nothing left to review here
    When I go back to everything due
    Then I see that 1 card is due

  Scenario: Review one subject
    Given I have asked for 2 flashcards of "fem-notes.md"
    And I have uploaded "wings.md" to "aeronautics/aerodynamics/lift"
    And I have asked for 1 flashcard of "wings.md"
    When I choose "Reviews" from the menu
    Then I see that 3 cards are due
    When I choose to review "Numerical methods"
    Then I see that 2 cards are due
    When I go back to everything due
    And I choose to review "Aerodynamics"
    Then I see that 1 card is due
    And the card shown is from "Aerodynamics"

  Scenario: Review one material
    Given I have asked for 2 flashcards of "fem-notes.md"
    And I have uploaded "intervals.md" to "music/theory/harmony"
    And I have asked for 1 flashcard of "intervals.md"
    When I choose "Reviews" from the menu
    Then I see that 3 cards are due
    When I choose to review "fem-notes.md"
    Then I see that 2 cards are due

  Scenario: My reviews are in my history, newest first
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    Then I am told I haven't reviewed anything yet
    When I choose to review "All my cards"
    And I show the answer and remembered it "Good"
    Then I see that 1 card is due
    When a minute passes
    And I show the answer and remembered it "Again"
    Then my history shows:
      | remembered | due again in |
      | Again      | 10 minutes   |
      | Good       | 1 day        |

  Scenario: Nothing to review
    When I choose "Reviews" from the menu
    Then I am told there is nothing to review now

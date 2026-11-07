@ui
Feature: Flashcards and reviews in the browser
  As a student
  I want to get flashcards from the assistant and review them when they are due
  So that I learn my material by heart without keeping track of what to study when

  Flashcards are asked for from the assistant, in words, as summaries and quizzes are. A card
  is turned over to show its answer. Reviews, in the app's menu, has a card for each course with
  cards due, as in My courses, with how many. Opening one shows its subjects, and a card for each
  of their sections, with how many are due in each. Choosing a section, or a subject, reviews its
  cards one at a time: the student shows its answer and says how well they remembered it, Again,
  Hard, Good or Easy, and the next card due follows, until none is left there. Below them, History
  has each subject on its own: its latest 50 reviews, newest first, each with its card, how well
  they remembered it and when, and how long until it was due again, and after them its cards they
  have not reviewed yet. It has every subject on the first page, the subjects of the course in a
  course, and the subject alone when reviewing it or a section of it.

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

  Scenario: The cards due, by course
    Given I have asked for 2 flashcards of "fem-notes.md"
    And I have uploaded "intervals.md" to "music/theory/harmony"
    And I have asked for 1 flashcard of "intervals.md"
    When I choose "Reviews" from the menu
    Then I see that 3 cards are due
    And I see the cards due:
      | what        | cards   |
      | Aeronautics | 2 cards |
      | Music       | 1 card  |
    And I am shown no card until I choose what to review

  Scenario: A course's cards due, by subject and section
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Aeronautics"
    Then I see that 2 cards are due
    And I see the cards due:
      | what              | cards   |
      | Numerical methods | 2 cards |
      | 1 Introduction    | 1 card  |
      | 2 Shape functions | 1 card  |
    And I am shown no card until I choose what to review

  Scenario: Review one section
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Aeronautics"
    And I choose to review "2 Shape functions"
    Then I see that 1 card is due
    And the card shown is from "fem-notes.md › 2 Shape functions"
    When I show the answer and remembered it "Good"
    Then I am told there is nothing left to review here
    When I go back to the sections
    Then I see that 1 card is due

  Scenario: Review one subject, until nothing is due
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Aeronautics"
    And I choose to review "Numerical methods"
    Then I see that 2 cards are due
    When I show the answer and remembered it "Good"
    Then I see that 1 card is due
    When I show the answer and remembered it "Again"
    Then I am told there is nothing left to review here
    When I choose "Reviews" from the menu
    Then I am told there is nothing to review now, and when the next card is due

  Scenario: My history has my reviews, newest first
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Aeronautics"
    And I choose to review "Numerical methods"
    And I show the answer and remembered it "Good"
    Then I see that 1 card is due
    When a minute passes
    And I show the answer and remembered it "Again"
    Then my history shows:
      | remembered | due again in |
      | Again      | 10 minutes   |
      | Good       | 1 day        |

  Scenario: My history has the cards I have not reviewed
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    Then my history shows 2 cards not reviewed yet
    When I choose to review "Aeronautics"
    And I choose to review "1 Introduction"
    And I show the answer and remembered it "Good"
    Then my history shows 1 card not reviewed yet

  Scenario: My history is of each subject on its own
    Given I have asked for 2 flashcards of "fem-notes.md"
    And I have uploaded "wings.md" to "aeronautics/aerodynamics/lift"
    And I have asked for 1 flashcard of "wings.md"
    And I have uploaded "intervals.md" to "music/theory/harmony"
    And I have asked for 1 flashcard of "intervals.md"
    When I choose "Reviews" from the menu
    Then my history has "Aeronautics › Aerodynamics, Aeronautics › Numerical methods, Music › Theory"
    When I choose to review "Aeronautics"
    Then my history has "Aeronautics › Aerodynamics, Aeronautics › Numerical methods"
    When I choose to review "Aerodynamics"
    Then my history has "Aeronautics › Aerodynamics"
    And my history shows 1 card not reviewed yet
    When I go back to the sections
    And I choose to review "1 Introduction"
    Then my history has "Aeronautics › Numerical methods"
    And my history shows 2 cards not reviewed yet

  Scenario: Nothing to review
    When I choose "Reviews" from the menu
    Then I am told there is nothing to review now

  Scenario: Nothing in my history
    When I choose "Reviews" from the menu
    Then I am told I haven't reviewed anything yet

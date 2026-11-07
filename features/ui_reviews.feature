@ui
Feature: Flashcards and reviews in the browser
  As a student
  I want to get flashcards from the assistant and review them when they are due
  So that I learn my material by heart without keeping track of what to study when

  Flashcards are asked for from the assistant, in words, as summaries and quizzes are. A card
  is turned over to show its answer. Reviews, in the app's menu, shows the subjects with cards,
  each with how many it has, due or not, and nothing else; a collection of papers has no subjects,
  so it is shown in its place. The cards of an earlier deck no longer count. Opening a subject shows
  how many cards are due, a card for each of its sections, with how many it has, and below them its
  History. Choosing a section reviews its cards due one at a time: the student shows its answer
  and says how well they remembered it, Again, Hard, Good or Easy, and the next card due follows,
  until none is left there, and they are told when the next is due. History has the subject's
  latest 50 reviews, newest first, each with its card, how well they remembered it and when, and
  how long until it was due again, and after them its cards they have not reviewed yet.

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

  Scenario: The first page is the subjects and how many cards each has, and nothing else
    Given I have asked for 2 flashcards of "fem-notes.md"
    And I have uploaded "wings.md" to "aeronautics/aerodynamics/lift"
    And I have asked for 1 flashcard of "wings.md"
    And I have uploaded "intervals.md" to "music/theory/harmony"
    And I have asked for 1 flashcard of "intervals.md"
    When I choose "Reviews" from the menu
    Then I see the cards:
      | what              | cards   |
      | Aerodynamics      | 1 card  |
      | Numerical methods | 2 cards |
      | Theory            | 1 card  |
    And I am shown nothing but the subjects

  Scenario: A subject's cards, by section
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Numerical methods"
    Then I see that 2 cards are due
    And I see the cards:
      | what              | cards   |
      | 1 Introduction    | 1 card  |
      | 2 Shape functions | 1 card  |
    And I am shown no card until I choose what to review

  Scenario: Review one section
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Numerical methods"
    And I choose to review "2 Shape functions"
    Then I see that 1 card is due
    And the card shown is from "fem-notes.md › 2 Shape functions"
    When I show the answer and remembered it "Good"
    Then I am told there is nothing left to review here
    When I go back to the sections
    Then I see that 1 card is due

  Scenario: Review until nothing is due
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Numerical methods"
    And I choose to review "1 Introduction"
    And I show the answer and remembered it "Good"
    And I go back to the sections
    And I choose to review "2 Shape functions"
    And I show the answer and remembered it "Again"
    Then I am told there is nothing left to review here, and when the next card is due

  Scenario: A subject with nothing due still shows all its cards
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Numerical methods"
    And I choose to review "1 Introduction"
    And I show the answer and remembered it "Good"
    And I go back to the sections
    And I choose to review "2 Shape functions"
    And I show the answer and remembered it "Good"
    And I go back to the sections
    Then I see the cards:
      | what              | cards  |
      | 1 Introduction    | 1 card |
      | 2 Shape functions | 1 card |
    When I go back to the subjects
    Then I see the cards:
      | what              | cards   |
      | Numerical methods | 2 cards |

  Scenario: A subject's history has its reviews, newest first
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Numerical methods"
    And I choose to review "1 Introduction"
    And I show the answer and remembered it "Good"
    And I go back to the sections
    And a minute passes
    And I choose to review "2 Shape functions"
    And I show the answer and remembered it "Again"
    Then my history shows:
      | remembered | due again in |
      | Again      | 10 minutes   |
      | Good       | 1 day        |

  Scenario: A subject's history has the cards I have not reviewed
    Given I have asked for 2 flashcards of "fem-notes.md"
    When I choose "Reviews" from the menu
    And I choose to review "Numerical methods"
    Then my history shows 2 cards not reviewed yet
    When I choose to review "1 Introduction"
    And I show the answer and remembered it "Good"
    Then my history shows 1 card not reviewed yet

  Scenario: A subject's history is its own
    Given I have asked for 2 flashcards of "fem-notes.md"
    And I have uploaded "wings.md" to "aeronautics/aerodynamics/lift"
    And I have asked for 1 flashcard of "wings.md"
    When I choose "Reviews" from the menu
    And I choose to review "Aerodynamics"
    Then my history has "Aeronautics › Aerodynamics"
    And my history shows 1 card not reviewed yet
    When I go back to the subjects
    And I choose to review "Numerical methods"
    And I choose to review "1 Introduction"
    Then my history has "Aeronautics › Numerical methods"
    And my history shows 2 cards not reviewed yet

  Scenario: Nothing to review
    When I choose "Reviews" from the menu
    Then I am told there is nothing to review now

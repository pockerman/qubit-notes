@ai
Feature: Flashcards
  As a student
  I want the assistant to make flashcards of a section, a whole document or a whole topic
  So that I can learn the material's terms, facts and ideas by heart

  A deck of flashcards is written by the AI from the material it covers. Each card has a
  front, a question or a term, and a back, its answer, and cites the section it comes from.
  Decks are saved as quizzes are: asking for a deck again shows the saved one, and a new
  one is written only when the student asks for a new one. Earlier decks are kept, newest
  first. Each student's decks are their own.

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

  Rule: A section, a document or a topic can be made into flashcards

    @platform
    Scenario: Get flashcards of a section
      When I ask for 3 flashcards of the section "2 Shape functions" of "fem-notes.md"
      Then I get a deck of 3 flashcards
      And every card has a front and a back
      And every card cites one of the sections "2 Shape functions" or "2.1 Linear elements" of "fem-notes.md"

    Scenario: Get flashcards of a whole document
      When I ask for 5 flashcards of "fem-notes.md"
      Then I get a deck of 5 flashcards
      And every card cites a section of "fem-notes.md"

    Scenario: Get flashcards of a topic from all of its material
      Given I have uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have uploaded "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
      When I ask for 6 flashcards of the topic "aeronautics/numerical-methods/finite-elements"
      Then I get a deck of 6 flashcards
      And the cards cite "fem-notes.md" and "fe-meshing.txt"
      But no card cites "fd-schemes.txt"

    Scenario Outline: A deck has between 1 and 30 cards
      When I ask for <count> flashcards of "fem-notes.md"
      Then I am told a deck has between 1 and 30 cards

      Examples:
        | count |
        | 0     |
        | 31    |

  Rule: Decks are saved, and new ones are written only on request

    Scenario: Asking again shows the saved deck
      Given I have asked for 3 flashcards of the section "3 Assembly" of "fem-notes.md"
      When I ask for 3 flashcards of the section "3 Assembly" of "fem-notes.md"
      Then I get the deck I got before
      And no new deck was written

    Scenario: Ask for a new deck
      Given I have asked for 3 flashcards of the section "3 Assembly" of "fem-notes.md"
      When I ask for 3 new flashcards of the section "3 Assembly" of "fem-notes.md"
      Then I get a deck I have not seen before
      And I have 2 decks of the section "3 Assembly" of "fem-notes.md", newest first

    Scenario: A topic's deck is out of date once the topic's material changes
      Given I have asked for 3 flashcards of the topic "aeronautics/numerical-methods/finite-elements"
      When I upload the file "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      And I ask for 3 flashcards of the topic "aeronautics/numerical-methods/finite-elements"
      Then I get the deck I got before
      But I am told the deck is out of date, as "fe-meshing.txt" was added since

    Scenario: Decks are private
      Given I have asked for 3 flashcards of "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" asks for 3 flashcards of "fem-notes.md"
      Then the student "tom" gets a deck written for them

    Scenario: Deleting a material deletes its decks
      Given I have asked for 3 flashcards of "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then I have no flashcards of "fem-notes.md"

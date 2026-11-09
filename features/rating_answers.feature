@ai
Feature: Rating the assistant's replies
  As a student
  I want to give the assistant's reply a thumbs up or a thumbs down
  So that how well it answers can be told, and made better

  Every reply of the assistant, an answer, a summary, a quiz or flashcards, can be rated "up" or
  "down" by the student it replied to, and the rating changed or taken back. The conversation
  shows the student's rating of each reply. A rating is kept with what was asked and replied, so
  it is still there to learn from after the student starts a new conversation; it is deleted with
  the material, the course or the student it is of.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    And I am reading the section "1 Introduction" of "fem-notes.md"
    And I have asked the assistant "What does the finite element method divide a domain into?"

  Scenario: A reply has no rating until it is rated
    Then the assistant's reply has no rating

  Scenario Outline: Rate a reply
    When I rate the assistant's reply "<rating>"
    Then the assistant's reply is rated "<rating>"
    And my conversation with the assistant on "fem-notes.md" shows the reply rated "<rating>"

    Examples:
      | rating |
      | up     |
      | down   |

  Scenario: Change a rating
    Given I have rated the assistant's reply "up"
    When I rate the assistant's reply "down"
    Then my conversation with the assistant on "fem-notes.md" shows the reply rated "down"

  Scenario: Take a rating back
    Given I have rated the assistant's reply "down"
    When I take back my rating of the assistant's reply
    Then my conversation with the assistant on "fem-notes.md" shows the reply with no rating

  Scenario: A summary is rated like an answer
    When I ask the assistant "Summarise this section"
    And I rate the assistant's reply "up"
    Then the assistant's reply is rated "up"

  Scenario: Only "up" and "down" are ratings
    When I rate the assistant's reply "meh"
    Then the rating is refused as invalid

  Scenario: Only the student it replied to rates a reply
    Given I have shared the course "aeronautics" with "tom" as a reader
    When the student "tom" rates my assistant's reply "down"
    Then the rating is refused as not found

  Scenario: A rating outlives the conversation
    Given I have rated the assistant's reply "down"
    When I start a new conversation on "fem-notes.md"
    Then my rating "down" of "What does the finite element method divide a domain into?" is kept

  Scenario: A rating is deleted with its material
    Given I have rated the assistant's reply "down"
    When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
    Then no rating of mine is kept

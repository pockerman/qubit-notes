@ai
Feature: Reviews
  As a student
  I want my flashcards to come back for review when I am about to forget them
  So that I remember the material for longer, with less studying

  Every card of a student's decks is scheduled for review, and is due as soon as its deck is
  written. Reviewing a card, the student says how well they remembered it, and that decides
  when it is due again (spaced repetition, as in SM-2):

    | I remembered it | it is due again                                               |
    | Again           | in 10 minutes, and its interval starts over                   |
    | Hard            | after 1.2 times its interval, at least a day                  |
    | Good            | after a day, then 6 days, then its interval times its ease    |
    | Easy            | after 4 days, then its interval times its ease and 1.3        |

  A card's ease starts at 2.5: Again lowers it by 0.2, Hard by 0.15, and Easy raises it by
  0.15, before its next interval is worked out; it is never below 1.3. Intervals are
  whole days, rounded. The reviews due are those of all the student's courses, or of one
  course, oldest due first; a course the student is no longer a member of is not reviewed,
  until it is shared with them again. When a new deck of a scope is written, the cards of
  the earlier decks of it are no longer reviewed, so the same material isn't reviewed twice.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Rule: A deck's cards are due for review as soon as it is written

    Scenario: New cards are due
      Given I have asked for 3 flashcards of "fem-notes.md"
      Then I have 3 cards due for review

    Scenario: Nothing is due without flashcards
      Then I have no cards due for review

    Scenario: The reviews due in one course
      Given I have asked for 3 flashcards of "fem-notes.md"
      And I have uploaded "intervals.md" to "music/theory/harmony"
      And I have asked for 2 flashcards of "intervals.md"
      Then I have 5 cards due for review
      And I have 2 cards due for review in the course "music"

    Scenario: A new deck takes the place of the earlier one in reviews
      Given I have asked for 3 flashcards of "fem-notes.md"
      When I ask for 2 new flashcards of "fem-notes.md"
      Then I have 2 cards due for review
      And they are the cards of the new deck

    Scenario: Another student's cards are not my reviews
      Given I have asked for 3 flashcards of "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      Then the student "tom" has no cards due for review

  Rule: How well I remembered a card decides when it is due again

    Scenario Outline: A new card is due again after my answer
      Given I have asked for 1 flashcard of "fem-notes.md"
      When I review the card and remembered it "<answer>"
      Then the card is due again in <due>
      And I have no cards due for review
      But I have 1 card due for review after <due>

      Examples:
        | answer | due        |
        | Again  | 10 minutes |
        | Hard   | 1 day      |
        | Good   | 1 day      |
        | Easy   | 4 days     |

    Scenario: A card I know well comes back later each time
      Given I have asked for 1 flashcard of "fem-notes.md"
      When I review the card each time it is due, and remember it:
        | answer | due again in |
        | Good   | 1 day        |
        | Good   | 6 days       |
        | Good   | 15 days      |
        | Easy   | 52 days      |

    Scenario: A card I forget starts over
      Given I have asked for 1 flashcard of "fem-notes.md"
      When I review the card each time it is due, and remember it:
        | answer | due again in |
        | Good   | 1 day        |
        | Good   | 6 days       |
        | Again  | 10 minutes   |
        | Good   | 1 day        |
        | Good   | 6 days       |
        | Good   | 14 days      |

    Scenario: A card can't be remembered some other way
      Given I have asked for 1 flashcard of "fem-notes.md"
      When I review the card and remembered it "Perfectly"
      Then I am told to answer Again, Hard, Good or Easy

    Scenario: Another student's card can't be reviewed
      Given I have asked for 1 flashcard of "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" reviews my card
      Then they are told there is no such card

  Rule: Only the courses I am a member of are reviewed

    Scenario: A reader's cards are hidden once they are removed from the course
      Given I have shared the course "aeronautics" with "tom" as a reader
      And the student "tom" has asked for 2 flashcards of "fem-notes.md"
      When I stop sharing the course "aeronautics" with "tom"
      Then the student "tom" has no cards due for review
      And the student "tom" can't review their cards

    Scenario: The cards come back when the course is shared again
      Given I have shared the course "aeronautics" with "tom" as a reader
      And the student "tom" has asked for 2 flashcards of "fem-notes.md"
      And I have stopped sharing the course "aeronautics" with "tom"
      When I share the course "aeronautics" with "tom" as a reader
      Then the student "tom" has 2 cards due for review

  Rule: Reviews go with their material

    Scenario: Deleting a material deletes its reviews
      Given I have asked for 3 flashcards of "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then I have no cards due for review

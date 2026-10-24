@ui
Feature: Topics in the browser
  As a student
  I want a course page that lists its topics, and a page of its own for each topic
  So that I see at a glance what a course covers, and find a topic's material in one place

  The course page lists each subject's topics, not their material. Each topic shows its
  status, and its owners can move it up or down and delete it:
    | status                | when                                         |
    | no material           | the topic has none                           |
    | processing            | any of its material is still being processed |
    | failed                | any of its material could not be processed   |
    | ready · 2 materials   | all of its material is ready                 |
  The topic's name opens its page, which has its material in the order it is meant to be read
  (see Reading a subject in order), "Add material" and "Write material" for its owners, the materials it is mentioned in (see References between topics), and the
  assistant for the whole topic (see Asking the assistant in the browser). Material is read from the topic page, and the reader goes
  back to it.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    And I have created the topic "numerical-methods/finite-volumes" in "aeronautics"

  Rule: The course page lists the topics, with their status and the owners' actions

    Scenario: The course page lists topics, not their material
      When I open the course "aeronautics"
      Then I see the topics "finite-elements, finite-volumes" under "numerical-methods"
      But I do not see "fe-basics.txt" or "fem-notes.md" on the course page
      And each topic offers only "Move up", "Move down" and "Delete"

    Scenario: A topic's status
      Given I have uploaded a PDF "scan.pdf" of pictures only to "aeronautics/numerical-methods/finite-differences"
      When I open the course "aeronautics"
      Then the topics show the statuses:
        | topic              | status              |
        | finite-elements    | ready · 2 materials |
        | finite-volumes     | no material         |
        | finite-differences | failed              |

    Scenario: Delete a topic and its material
      When I open the course "aeronautics"
      And I delete the topic "finite-elements", and confirm it
      Then I am told before that its 2 materials are deleted with it
      And I see the topics "finite-volumes" under "numerical-methods"

    Scenario: Deleting a topic asks first
      When I open the course "aeronautics"
      And I delete the topic "finite-elements", but cancel
      Then I see the topics "finite-elements, finite-volumes" under "numerical-methods"

    Scenario: A reader of a shared course sees the topics but cannot change them
      Given I have shared the course "aeronautics" with "tom" as a reader
      And I am signed in as "tom"
      When I open the course "aeronautics"
      Then I see the topics "finite-elements, finite-volumes" under "numerical-methods"
      And I am not offered to move or delete topics

  Rule: A topic's page has its material, and what is done with it

    Scenario: Open a topic and read its material
      When I open the course "aeronautics"
      And I open the topic "finite-elements"
      Then I am on the topic "numerical-methods" › "finite-elements"
      And I see its materials "fe-basics.txt, fem-notes.md"
      When I open "fem-notes.md" to read it
      And I go back
      Then I am on the topic "numerical-methods" › "finite-elements"

    Scenario: Add material from the topic's page
      When I open the course "aeronautics"
      And I open the topic "finite-volumes"
      And I add "fv-basics.txt" to this topic
      Then I am on the topic "numerical-methods" › "finite-volumes"
      And I see its materials "fv-basics.txt"

    Scenario: Move a material up or down
      When I open the course "aeronautics"
      And I open the topic "finite-elements"
      And I move the material "fem-notes.md" up
      Then I see its materials "fem-notes.md, fe-basics.txt"
      And they are still in that order when I open the topic again

    Scenario: Delete material from the topic's page
      When I open the course "aeronautics"
      And I open the topic "finite-elements"
      And I delete "fe-basics.txt"
      Then I see its materials "fem-notes.md"

    Scenario: A reader of a shared course reads a topic but cannot add to it
      Given I have shared the course "aeronautics" with "tom" as a reader
      And I am signed in as "tom"
      When I open the course "aeronautics"
      And I open the topic "finite-elements"
      Then I see its materials "fe-basics.txt, fem-notes.md"
      But I am not offered to add, write, move or delete material

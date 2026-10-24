@ui
Feature: Subjects and topics in the browser
  As a student
  I want a course page that lists its subjects, and a page of its own for each subject and topic
  So that I see at a glance what a course covers, and find a topic's material in one place

  The course page lists the course's subjects by name, each with "Rename" for its owners, and
  nothing else of them; a subject's name opens its page. Owners create subjects and topics before
  they have any material: "New subject" and "New topic" on the course page (see Subjects).

  A subject's page lists its topics, not their material, with "Rename" and "Add topic" for its
  owners, and "Delete" while it has no topics. Each topic shows its status, and its owners can
  move it up or down, rename it and delete it:
    | status                | when                                         |
    | no material           | the topic has none                           |
    | processing            | any of its material is still being processed |
    | failed                | any of its material could not be processed   |
    | ready · 2 materials   | all of its material is ready                 |
  The topic's name opens its page, which has its material in the order it is meant to be read
  (see Reading a subject in order), "Add material" and "Write material" for its owners, the
  materials it is mentioned in (see References between topics), and the assistant for the whole
  topic (see Asking the assistant in the browser). Material is read from the topic page, and the
  reader goes back to it; the topic page goes back to its subject's page.

  Elsewhere, the topics "under" a subject are those on its page, and opening a topic from the
  course page opens its subject's page first.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    And I have created the topic "numerical-methods/finite-volumes" in "aeronautics"
    And I have created the subject "Fluid Dynamics" in "aeronautics"

  Rule: The course page lists the subjects, which their owners rename

    Scenario: The course page lists subjects, not their topics
      When I open the course "Aeronautics"
      Then I see the subjects "Fluid Dynamics, Numerical methods"
      But I do not see "Finite elements" or "Finite volumes" on the course page
      And each subject offers only "Rename"

    Scenario: Rename a subject on the course page
      When I open the course "Aeronautics"
      And I rename the subject "Numerical methods" to "Numerical Analysis" on the course page
      Then I see the subjects "Fluid Dynamics, Numerical Analysis"

    Scenario: A reader of a shared course sees the subjects but cannot rename them
      Given I have shared the course "aeronautics" with "tom" as a reader
      And I am signed in as "tom"
      When I open the course "Aeronautics"
      Then I see the subjects "Fluid Dynamics, Numerical methods"
      And each subject offers nothing

  Rule: A subject's page lists its topics, with their status and the owners' actions

    Scenario: A subject's page lists topics, not their material
      When I open the course "Aeronautics"
      And I open the subject "Numerical methods"
      Then I am on the subject "Numerical methods"
      And I see the topics "Finite elements, Finite volumes" under "Numerical methods"
      But I do not see "fe-basics.txt" or "fem-notes.md" on the subject's page
      And each topic offers only "Move up", "Move down", "Rename" and "Delete"

    Scenario: A topic's status
      Given I have uploaded a PDF "scan.pdf" of pictures only to "aeronautics/numerical-methods/finite-differences"
      When I open the course "Aeronautics"
      And I open the subject "Numerical methods"
      Then the topics show the statuses:
        | topic              | status              |
        | Finite elements    | ready · 2 materials |
        | Finite volumes     | no material         |
        | Finite differences | failed              |

    Scenario: Delete a topic and its material
      When I open the course "Aeronautics"
      And I open the subject "Numerical methods"
      And I delete the topic "Finite elements", and confirm it
      Then I am told before that its 2 materials are deleted with it
      And I see the topics "Finite volumes" under "Numerical methods"

    Scenario: Deleting a topic asks first
      When I open the course "Aeronautics"
      And I open the subject "Numerical methods"
      And I delete the topic "Finite elements", but cancel
      Then I see the topics "Finite elements, Finite volumes" under "Numerical methods"

    Scenario: Go back to the course
      When I open the course "Aeronautics"
      And I open the subject "Numerical methods"
      And I go back to the course
      Then I see the subjects "Fluid Dynamics, Numerical methods"

    Scenario: A reader of a shared course sees the topics but cannot change them
      Given I have shared the course "aeronautics" with "tom" as a reader
      And I am signed in as "tom"
      When I open the course "Aeronautics"
      And I open the subject "Numerical methods"
      Then I see the topics "Finite elements, Finite volumes" under "Numerical methods"
      And I am not offered to move or delete topics
      And I am not offered to rename the subject, or add topics to it

  Rule: Subjects and topics are created before their material

    Scenario: Create a subject
      When I open the course "Aeronautics"
      And I create the subject "Heat Transfer"
      Then I see the subjects "Fluid Dynamics, Heat Transfer, Numerical methods"
      When I open the subject "Heat Transfer"
      Then I see the subject "Heat Transfer" with no topics yet
      And the subject offers "Rename", "Add topic" and "Delete"

    Scenario: Add a topic to a subject without topics
      When I open the course "Aeronautics"
      And I open the subject "Fluid Dynamics"
      And I add the topic "Turbulence" to the subject "Fluid Dynamics"
      Then I see the topics "Turbulence" under "Fluid Dynamics"
      And the topics show the statuses:
        | topic      | status      |
        | Turbulence | no material |

    Scenario: Delete a subject without topics
      When I open the course "Aeronautics"
      And I open the subject "Fluid Dynamics"
      And I delete the subject "Fluid Dynamics"
      Then I see the subjects "Numerical methods"

    Scenario: A subject with topics can't be deleted
      When I open the course "Aeronautics"
      And I open the subject "Numerical methods"
      Then the subject "Numerical methods", which has topics, does not offer "Delete"

  Rule: A topic's page has its material, and what is done with it

    Scenario: Open a topic and read its material
      When I open the course "Aeronautics"
      And I open the topic "Finite elements"
      Then I am on the topic "Numerical methods" › "Finite elements"
      And I see its materials "fe-basics.txt, fem-notes.md"
      When I open "fem-notes.md" to read it
      And I go back
      Then I am on the topic "Numerical methods" › "Finite elements"
      When I go back to the subject
      Then I am on the subject "Numerical methods"

    Scenario: Add material from the topic's page
      When I open the course "Aeronautics"
      And I open the topic "Finite volumes"
      And I add "fv-basics.txt" to this topic
      Then I am on the topic "Numerical methods" › "Finite volumes"
      And I see its materials "fv-basics.txt"

    Scenario: Move a material up or down
      When I open the course "Aeronautics"
      And I open the topic "Finite elements"
      And I move the material "fem-notes.md" up
      Then I see its materials "fem-notes.md, fe-basics.txt"
      And they are still in that order when I open the topic again

    Scenario: Delete material from the topic's page
      When I open the course "Aeronautics"
      And I open the topic "Finite elements"
      And I delete "fe-basics.txt"
      Then I see its materials "fem-notes.md"

    Scenario: A reader of a shared course reads a topic but cannot add to it
      Given I have shared the course "aeronautics" with "tom" as a reader
      And I am signed in as "tom"
      When I open the course "Aeronautics"
      And I open the topic "Finite elements"
      Then I see its materials "fe-basics.txt, fem-notes.md"
      But I am not offered to add, write, move or delete material

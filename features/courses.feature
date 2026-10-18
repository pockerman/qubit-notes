Feature: Courses
  As a student
  I want to create a course before I have any material for it
  So that I can set up what I study, and add to it as I go

  A course's name is lowercase words joined by hyphens, e.g. "computer-science".
  Uploading to a course I don't have yet still creates it.

  Background:
    Given I am the student "maria"

  @gogi
  Scenario: Create a course
    When I create the course "computer-science"
    Then I see the courses:
      | course           |
      | computer-science |
    And I am the owner of the course "computer-science"
    And the course "computer-science" has no material

  Scenario: A course I already have cannot be created again
    Given I have created the course "computer-science"
    When I create the course "computer-science"
    Then I am told I already have the course "computer-science"

  Scenario Outline: A course's name is lowercase words joined by hyphens
    When I create the course "<name>"
    Then I am told the course name is invalid

    Examples:
      | name             |
      | Computer Science |
      | computer_science |
      | -computers       |

  Rule: A course is organised into subjects and topics, which stay when their material is gone

    Scenario: Create a topic before adding material to it
      Given I have created the course "computer-science"
      When I create the topic "distributed-systems/introduction" in "computer-science"
      Then the topics of "computer-science" are:
        | subject             | topic        | materials |
        | distributed-systems | introduction | 0         |

    Scenario: Add material to a topic that has some already
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      When I upload the file "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      Then the topics of "aeronautics" are:
        | subject           | topic           | materials |
        | numerical-methods | finite-elements | 2         |

    @gogi
    Scenario: A topic stays when all of its material is deleted
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      When I delete the material "fe-basics.txt" from "aeronautics/numerical-methods/finite-elements"
      Then the topics of "aeronautics" are:
        | subject           | topic           | materials |
        | numerical-methods | finite-elements | 0         |

    Scenario: A reader of a shared course cannot create topics in it
      Given I have created the course "computer-science"
      And I have shared the course "computer-science" with "tom" as a reader
      When the student "tom" creates the topic "networks/routing" in "computer-science"
      Then the student "tom" is not allowed to do that

  Rule: The topics of a subject are in the order they are meant to be read

    A subject's topics are listed in the order its owners set, the same for every member.
    A new topic goes after the subject's other topics. Subjects stay in alphabetical order.

    Background:
      Given I have created the course "computer-science"
      And I have created the topic "distributed-systems/introduction" in "computer-science"
      And I have created the topic "distributed-systems/consensus" in "computer-science"
      And I have created the topic "distributed-systems/replication" in "computer-science"

    Scenario: New topics go after the others
      Then the topics of "distributed-systems" in "computer-science" are, in order:
        | topic        |
        | introduction |
        | consensus    |
        | replication  |

    Scenario: Set the order of a subject's topics
      When I put the topics of "distributed-systems" in "computer-science" in the order:
        | topic        |
        | introduction |
        | replication  |
        | consensus    |
      Then the topics of "distributed-systems" in "computer-science" are, in order:
        | topic        |
        | introduction |
        | replication  |
        | consensus    |

    Scenario: The order is the same for every member
      Given I have shared the course "computer-science" with "tom" as a reader
      When I put the topics of "distributed-systems" in "computer-science" in the order:
        | topic        |
        | replication  |
        | consensus    |
        | introduction |
      Then the student "tom" sees the topics of "distributed-systems" in "computer-science" in the order:
        | topic        |
        | replication  |
        | consensus    |
        | introduction |

    Scenario: A topic keeps its place when its material comes and goes
      Given I have uploaded "consensus.txt" to "computer-science/distributed-systems/consensus"
      And I have put the topics of "distributed-systems" in "computer-science" in the order:
        | topic        |
        | consensus    |
        | introduction |
        | replication  |
      When I delete the material "consensus.txt" from "computer-science/distributed-systems/consensus"
      Then the topics of "distributed-systems" in "computer-science" are, in order:
        | topic        |
        | consensus    |
        | introduction |
        | replication  |

    Scenario: An order must have each of the subject's topics once
      When I put the topics of "distributed-systems" in "computer-science" in the order:
        | topic        |
        | replication  |
        | introduction |
      Then I am told the order must have each of the topics of "distributed-systems" once

    Scenario: A reader cannot change the order
      Given I have shared the course "computer-science" with "tom" as a reader
      When the student "tom" puts the topics of "distributed-systems" in "computer-science" in the order:
        | topic        |
        | replication  |
        | consensus    |
        | introduction |
      Then the student "tom" is not allowed to do that

  Rule: Deleting a course removes it and everything in it, for every member

    Only the student who created a course can delete it; other owners and readers cannot.

    @gogi
    Scenario: Delete a course
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have uploaded "rome.txt" to "history/ancient-history/rome"
      When I delete the course "aeronautics"
      Then I see the courses:
        | course  |
        | history |
      And searching "history" for "rome" finds "rome.txt"

    @gogi
    Scenario: A deleted course is gone for its members too
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have shared the course "aeronautics" with "tom" as a reader
      When I delete the course "aeronautics"
      Then the student "tom" has no courses

    Scenario: Deleting a course deletes its topics, notes, summaries, quizzes and conversations
      Given I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.
        """
      And I have created the topic "numerical-methods/finite-volumes" in "aeronautics"
      And I have noted "why small?" on "small elements" in "1 Introduction" of "fem-notes.md"
      And I have a summary and a quiz of "fem-notes.md"
      And I have asked the assistant "What do shape functions do?" while reading "fem-notes.md"
      When I delete the course "aeronautics"
      And I create the course "aeronautics"
      Then the course "aeronautics" has no material
      And the topics of "aeronautics" are empty
      And I have no notes, summaries, quizzes or conversations

    @gogi
    Scenario: The assistant forgets what it remembered from a deleted course's material
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have uploaded "rome.txt" to "history/ancient-history/rome"
      And the assistant remembers "struggles with shape functions" from "fe-basics.txt"
      And the assistant remembers "mixes up the Punic wars" from "rome.txt"
      When I delete the course "aeronautics"
      Then the assistant no longer remembers "struggles with shape functions"
      But the assistant still remembers "mixes up the Punic wars"

    Scenario Outline: Only the creator can delete a course
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have shared the course "aeronautics" with "tom" as <role>
      When the student "tom" deletes the course "aeronautics"
      Then the student "tom" is not allowed to do that
      And the course "aeronautics" is still there

      Examples:
        | role     |
        | a reader |
        | an owner |

    Scenario: Deleting a course I do not have
      When I delete the course "aeronautics"
      Then I am told I have no course "aeronautics"

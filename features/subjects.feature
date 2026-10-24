Feature: Subjects
  As a student
  I want to create a subject before I have any topics for it
  So that I can lay out what a course covers, and fill it in as I go

  A course is organised into subjects, each with its topics. A subject is created with a name,
  e.g. "Distributed Systems", and known by its id, made from that name: "distributed-systems"
  (see The names of subjects and topics). A subject is also created by creating a topic in it,
  or by uploading to it. A subject stays when its topics are deleted, as a topic stays when its
  material is deleted. Its owners can delete a subject that has no topics; one that has topics is
  deleted by deleting them first. Subjects are listed in alphabetical order of their ids.

  Background:
    Given I am the student "maria"
    And I have created the course "computer-science"

  @platform
  Scenario: Create a subject before any of its topics
    When I create the subject "Distributed Systems" in "computer-science"
    Then the subjects of "computer-science" are:
      | subject             | name                | topics |
      | distributed-systems | Distributed Systems | 0      |

  Scenario: Subjects created in other ways are listed too
    Given I have created the subject "Networks" in "computer-science"
    And I have created the topic "Introduction" in the subject "Distributed Systems" in "computer-science"
    And I have uploaded "fe-basics.txt" to "computer-science/numerical-methods/finite-elements"
    Then the subjects of "computer-science" are:
      | subject             | name                | topics |
      | distributed-systems | Distributed Systems | 1      |
      | networks            | Networks            | 0      |
      | numerical-methods   | Numerical methods   | 1      |

  Scenario: Add a topic to a subject
    Given I have created the subject "Distributed Systems" in "computer-science"
    When I create the topic "Introduction" in the subject "distributed-systems" in "computer-science"
    Then the topics of "computer-science" are named:
      | subject             | subject name        | topic        | topic name   |
      | distributed-systems | Distributed Systems | introduction | Introduction |

  Scenario: A subject stays when its topics are deleted
    Given I have created the topic "Introduction" in the subject "Distributed Systems" in "computer-science"
    When I delete the topic "distributed-systems/introduction" from "computer-science"
    Then the subjects of "computer-science" are:
      | subject             | name                | topics |
      | distributed-systems | Distributed Systems | 0      |

  Scenario: A subject the course has can't be created again
    Given I have created the subject "Distributed Systems" in "computer-science"
    When I create the subject "distributed systems" in "computer-science"
    Then I am told the course already has the subject "Distributed Systems"

  Scenario: A subject's name needs a letter or digit
    When I create the subject " - " in "computer-science"
    Then I am told a subject's name needs at least one letter or digit

  Rule: Owners delete subjects that have no topics

    @platform
    Scenario: Delete a subject without topics
      Given I have created the subject "Networks" in "computer-science"
      And I have created the subject "Distributed Systems" in "computer-science"
      When I delete the subject "networks" from "computer-science"
      Then the subjects of "computer-science" are:
        | subject             | name                | topics |
        | distributed-systems | Distributed Systems | 0      |

    Scenario: A subject with topics is not deleted
      Given I have created the topic "Introduction" in the subject "Distributed Systems" in "computer-science"
      When I delete the subject "distributed-systems" from "computer-science"
      Then I am told to delete the topics of "Distributed Systems" first
      And the subjects of "computer-science" are:
        | subject             | name                | topics |
        | distributed-systems | Distributed Systems | 1      |

  Rule: Only owners create and delete subjects

    Scenario: A reader cannot create a subject
      Given I have shared the course "computer-science" with "tom" as a reader
      When the student "tom" creates the subject "Networks" in "computer-science"
      Then the student "tom" is not allowed to do that

    Scenario: A reader cannot delete a subject
      Given I have created the subject "Networks" in "computer-science"
      And I have shared the course "computer-science" with "tom" as a reader
      When the student "tom" deletes the subject "networks" from "computer-science"
      Then the student "tom" is not allowed to do that

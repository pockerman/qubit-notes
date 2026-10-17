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

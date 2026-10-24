Feature: The names of subjects and topics
  As a student
  I want my subjects and topics shown with the names I gave them
  So that my course reads "Numerical Methods › Finite Elements", not "numerical-methods › finite-elements"

  A subject or topic is known by its id: lowercase words joined by hyphens, e.g.
  "finite-elements", made from the name it is created with. The id is in the topic's links,
  and in references to it (see References between topics), and never changes. Its name is what
  the student typed, e.g. "Finite Elements", and is what the app shows. A subject or topic
  created without a name, e.g. by uploading to a new location, is named after its id, with
  spaces for hyphens and a capital first letter: "finite-elements" is "Finite elements". The
  owners of a course can rename its subjects and topics; a name can't be blank, and two topics
  of a subject can't have the same name.

  Background:
    Given I am the student "maria"
    And I have created the course "computer-science"

  Rule: A subject or topic has the name it is created with

    @platform
    Scenario: Create a topic with names
      When I create the topic "Introduction" in the subject "Distributed Systems" in "computer-science"
      Then the topics of "computer-science" are named:
        | subject             | subject name        | topic        | topic name   |
        | distributed-systems | Distributed Systems | introduction | Introduction |

    Scenario: A topic created without a name is named after its id
      When I upload the file "fe-basics.txt" to "computer-science/numerical-methods/finite-elements"
      Then the topics of "computer-science" are named:
        | subject           | subject name      | topic           | topic name      |
        | numerical-methods | Numerical methods | finite-elements | Finite elements |

    Scenario: A topic of a subject that has a name keeps the subject's name
      Given I have created the topic "Introduction" in the subject "Distributed Systems" in "computer-science"
      When I create the topic "Consensus" in the subject "distributed-systems" in "computer-science"
      Then the topics of "computer-science" are named:
        | subject             | subject name        | topic        | topic name   |
        | distributed-systems | Distributed Systems | introduction | Introduction |
        | distributed-systems | Distributed Systems | consensus    | Consensus    |

  Rule: The owners rename subjects and topics, which keep their ids

    Background:
      Given I have created the topic "Introduction" in the subject "Distributed Systems" in "computer-science"
      And I have uploaded "intro.txt" to "computer-science/distributed-systems/introduction"

    @platform
    Scenario: Rename a topic
      When I rename the topic "distributed-systems/introduction" of "computer-science" to "Getting Started"
      Then the topics of "computer-science" are named:
        | subject             | subject name        | topic        | topic name      |
        | distributed-systems | Distributed Systems | introduction | Getting Started |
      And the materials of "computer-science/distributed-systems/introduction" are:
        | filename  |
        | intro.txt |

    Scenario: Rename a subject
      When I rename the subject "distributed-systems" of "computer-science" to "Distributed Computing"
      Then the topics of "computer-science" are named:
        | subject             | subject name          | topic        | topic name   |
        | distributed-systems | Distributed Computing | introduction | Introduction |

    Scenario: A name can't be blank
      When I rename the topic "distributed-systems/introduction" of "computer-science" to " "
      Then I am told a name can't be blank

    Scenario: Two topics of a subject can't have the same name
      Given I have created the topic "Consensus" in the subject "distributed-systems" in "computer-science"
      When I rename the topic "distributed-systems/consensus" of "computer-science" to "introduction"
      Then I am told the subject already has a topic named "Introduction"

    Scenario: A reader cannot rename
      Given I have shared the course "computer-science" with "tom" as a reader
      When the student "tom" renames the topic "distributed-systems/introduction" of "computer-science" to "Basics"
      Then the student "tom" is not allowed to do that

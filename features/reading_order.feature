Feature: Reading a subject in order
  As a student
  I want each topic's material in the order it is meant to be read, and to go on to what comes next
  So that I can read a subject through, from one material to the next, without going back to the course

  The material of a topic is in the order its owners set, the same for every member; new
  material goes after the topic's other material. (Material uploaded before the order was kept
  goes after the ordered material, by name.)

  Reading a material, the student can go to the next material or the previous one. After a
  topic's last material comes the first material of the subject's next topic, in the order of
  its topics (see Courses); topics without material ready to read are passed over. A subject's
  first material has no previous one, and its last no next one. Only material that is ready can
  be read, so material still being processed, or that failed to be, is passed over too.

  Background:
    Given I am the student "maria"
    And I have created the course "aeronautics"
    And I have created the topic "numerical-methods/finite-elements" in "aeronautics"
    And I have created the topic "numerical-methods/finite-differences" in "aeronautics"
    And I have created the topic "numerical-methods/finite-volumes" in "aeronautics"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "fe-assembly.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "fv-basics.txt" to "aeronautics/numerical-methods/finite-volumes"

  Rule: The owners of a course set the order of each topic's material

    Scenario: New material goes after the topic's other material
      When I upload the file "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      Then the materials of "aeronautics/numerical-methods/finite-elements" are:
        | filename        |
        | fe-basics.txt   |
        | fe-assembly.txt |
        | fe-meshing.txt  |

    Scenario: Set the order of a topic's material
      Given I have uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      When I put the material of "aeronautics/numerical-methods/finite-elements" in the order:
        | filename        |
        | fe-basics.txt   |
        | fe-meshing.txt  |
        | fe-assembly.txt |
      Then the materials of "aeronautics/numerical-methods/finite-elements" are:
        | filename        |
        | fe-basics.txt   |
        | fe-meshing.txt  |
        | fe-assembly.txt |

    Scenario: The order is the same for every member
      Given I have shared the course "aeronautics" with "tom" as a reader
      When I put the material of "aeronautics/numerical-methods/finite-elements" in the order:
        | filename        |
        | fe-assembly.txt |
        | fe-basics.txt   |
      Then the student "tom" sees the materials of "aeronautics/numerical-methods/finite-elements" in the order:
        | filename        |
        | fe-assembly.txt |
        | fe-basics.txt   |

    Scenario: The material keeps its order when one of it is deleted
      Given I have uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      When I delete the material "fe-basics.txt" from "aeronautics/numerical-methods/finite-elements"
      Then the materials of "aeronautics/numerical-methods/finite-elements" are:
        | filename        |
        | fe-assembly.txt |
        | fe-meshing.txt  |

    Scenario: An order must have each of the topic's materials once
      When I put the material of "aeronautics/numerical-methods/finite-elements" in the order:
        | filename      |
        | fe-basics.txt |
      Then I am told the order must have each of the materials of "numerical-methods/finite-elements" once

    Scenario: A reader cannot change the order
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" puts the material of "aeronautics/numerical-methods/finite-elements" in the order:
        | filename        |
        | fe-assembly.txt |
        | fe-basics.txt   |
      Then the student "tom" is not allowed to do that

  Rule: From a material, the student goes on to the next one, or back to the previous one

    @platform
    Scenario: The next material is the next of its topic
      When I open "fe-basics.txt"
      Then the next material is "fe-assembly.txt" in "numerical-methods/finite-elements"
      And there is no previous material

    Scenario: After a topic's last material comes the next topic's first, passing over topics without any
      When I open "fe-assembly.txt"
      Then the previous material is "fe-basics.txt" in "numerical-methods/finite-elements"
      And the next material is "fv-basics.txt" in "numerical-methods/finite-volumes"

    Scenario: Before a topic's first material comes the previous topic's last
      When I open "fv-basics.txt"
      Then the previous material is "fe-assembly.txt" in "numerical-methods/finite-elements"
      And there is no next material

    Scenario: The next material follows the order the owners set
      Given I have put the material of "aeronautics/numerical-methods/finite-elements" in the order:
        | filename        |
        | fe-assembly.txt |
        | fe-basics.txt   |
      When I open "fe-assembly.txt"
      Then the next material is "fe-basics.txt" in "numerical-methods/finite-elements"

    Scenario: Material that isn't ready is passed over
      Given I have uploaded a PDF "scan.pdf" of pictures only to "aeronautics/numerical-methods/finite-differences"
      When I open "fe-assembly.txt"
      Then the next material is "fv-basics.txt" in "numerical-methods/finite-volumes"

    Scenario: The next material stays in the subject
      Given I have uploaded "blasius.txt" to "aeronautics/aerodynamics/boundary-layers"
      When I open "fv-basics.txt"
      Then there is no next material

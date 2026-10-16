Feature: Sharing courses
  As a student
  I want to share a course's material with classmates
  So that we can study from the same notes

  A course has members. Owners upload and delete material and manage the members;
  readers can only see and study from the material.

  Background:
    Given I am the student "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"

  Rule: Owners share a course as a reader or as an owner

    @gogi
    Scenario: Share a course with a classmate as a reader
      When I share the course "aeronautics" with "tom" as a reader
      Then the student "tom" sees the courses:
        | course      | owned by | role   |
        | aeronautics | maria    | reader |
      And the student "tom" sees the materials of the course "aeronautics":
        | subject           | topic           | filename      |
        | numerical-methods | finite-elements | fe-basics.txt |

    @gogi
    Scenario: See who a course is shared with
      Given I have shared the course "aeronautics" with "tom" as a reader
      And I have shared the course "aeronautics" with "lena" as an owner
      When I list the members of the course "aeronautics"
      Then I see the members:
        | student | role   |
        | lena    | owner  |
        | maria   | owner  |
        | tom     | reader |

    @gogi
    Scenario: A co-owner can add material to a shared course
      Given I have shared the course "aeronautics" with "lena" as an owner
      When the student "lena" uploads "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
      Then the upload is accepted for processing
      And the materials of the course "aeronautics" include "fd-schemes.txt"

  Rule: Readers cannot change a shared course

    Background:
      Given I have shared the course "aeronautics" with "tom" as a reader

    Scenario: A reader cannot upload material
      When the student "tom" uploads "tom-notes.txt" to "aeronautics/numerical-methods/finite-elements"
      Then the student "tom" is not allowed to do that

    Scenario: A reader cannot delete material
      When the student "tom" deletes the material "fe-basics.txt" from "aeronautics/numerical-methods/finite-elements"
      Then the student "tom" is not allowed to do that
      And the materials of the course "aeronautics" include "fe-basics.txt"

    Scenario: A reader cannot share the course
      When the student "tom" shares the course "aeronautics" with "sam" as a reader
      Then the student "tom" is not allowed to do that

  Rule: Owners can stop sharing, but a course always keeps an owner

    @gogi
    Scenario: Stop sharing a course
      Given I have shared the course "aeronautics" with "tom" as a reader
      When I stop sharing the course "aeronautics" with "tom"
      Then the student "tom" has no courses

    Scenario: The last owner cannot leave
      When I stop sharing the course "aeronautics" with "maria"
      Then I am told a course must keep at least one owner

  Rule: Course names only need to be unique for the student who creates them

    @gogi
    Scenario: Two students each have a course with the same name
      Given the student "tom" has uploaded "tom-fe.txt" to "aeronautics/structures/beams"
      When I list my courses
      Then I see the courses:
        | course      |
        | aeronautics |
      And the materials of the course "aeronautics" do not include "tom-fe.txt"

@ui
Feature: Managing materials and sharing in the browser
  As a student
  I want to manage my courses and their material on screen
  So that I can organise what I study without any tooling

  Scenario: Sign in and see the platform status
    When I open the study assistant
    And I sign in as "maria"
    Then I see that I am signed in as "maria"
    And I see that the platform is connected
    And I see that I have no courses yet

  @gogi
  Scenario: Upload material to a new course
    Given I am signed in as "maria"
    When I upload "fe-basics.txt" to the course "aeronautics", subject "numerical-methods", topic "finite-elements"
    Then I see the course "aeronautics" in my courses
    And I see "fe-basics.txt" under "numerical-methods" › "finite-elements"
    And I see that "fe-basics.txt" is ready

  Scenario: Material is grouped by subject and topic
    Given I am signed in as "maria"
    And I have uploaded these materials:
      | location                                         | filename       |
      | aeronautics/numerical-methods/finite-elements    | fe-basics.txt  |
      | aeronautics/numerical-methods/finite-differences | fd-schemes.txt |
      | aeronautics/aerodynamics/boundary-layers         | blasius.txt    |
    When I open the course "aeronautics"
    Then I see the subjects "aerodynamics, numerical-methods"
    And I see "fd-schemes.txt" under "numerical-methods" › "finite-differences"
    And I see "blasius.txt" under "aerodynamics" › "boundary-layers"

  Scenario: Delete material
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "aeronautics"
    And I delete "fe-basics.txt"
    Then I no longer see "fe-basics.txt"

  Scenario: Share a course and see its members
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "aeronautics"
    And I open its members
    And I share it with "tom" as a reader
    Then I see "tom" as a reader of the course

  Scenario: Members are on a page of their own
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have shared the course "aeronautics" with "tom" as a reader
    When I open the course "aeronautics"
    Then I do not see the members on the course page
    When I open its members
    Then I see "tom" as a reader of the course
    And I can go back to the course "aeronautics"

  Scenario: A reader sees who else is in a shared course
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "aeronautics"
    And I open its members
    Then I see "maria" as an owner of the course
    And I see "tom" as a reader of the course
    But I am not offered to share the course

  @gogi
  Scenario: A reader sees a shared course but cannot change it
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "aeronautics"
    Then I see that the course is shared with me by "maria" as a reader
    And I see "fe-basics.txt" under "numerical-methods" › "finite-elements"
    But I cannot upload, delete or share in this course

  Scenario: Names are written as lowercase words joined by hyphens
    Given I am signed in as "maria"
    When I upload "intro.txt" to the course "Computer Science", subject "Distributed Systems Design", topic "Introduction"
    Then I see the course "computer-science" in my courses
    And I see "intro.txt" under "distributed-systems-design" › "introduction"

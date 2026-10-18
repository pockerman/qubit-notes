@ui
Feature: Courses in the browser
  As a student
  I want to start from my courses, and create one when I have none
  So that I always know where my material is and where to add more

  Scenario: A student without courses is offered to create one
    Given I am signed in as "maria"
    Then I see that I have no courses yet
    And I am offered to create a new course

  Scenario: Create a course
    Given I am signed in as "maria"
    When I create the course "Computer Science"
    Then I am in the course "computer-science"
    And I see that it has no material yet

  Scenario: My courses are listed when I sign in
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "rome.txt" to "history/ancient-history/rome"
    When I go to my courses
    Then I see the courses "aeronautics, history"

  Scenario: Add material on its own page
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    When I open the course "aeronautics"
    And I add "fe-basics.txt" to the subject "Numerical Methods", topic "Finite Elements"
    Then I am back in the course "aeronautics"
    And I see "fe-basics.txt" under "numerical-methods" › "finite-elements"

  Scenario: Edit a material in the reader
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    And I edit its text to:
      """
      # 1 Introduction
      Finite elements approximate the solution piecewise.
      """
    Then I see the text "Finite elements approximate the solution piecewise."

  Scenario: Add material to a topic that has some already
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "aeronautics"
    And I add "fe-meshing.txt" to the topic "finite-elements"
    Then I am back in the course "aeronautics"
    And I see "fe-basics.txt" under "numerical-methods" › "finite-elements"
    And I see "fe-meshing.txt" under "numerical-methods" › "finite-elements"

  Scenario: A topic stays when all of its material is deleted
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "aeronautics"
    And I delete "fe-basics.txt"
    Then I no longer see "fe-basics.txt"
    But I still see the topic "numerical-methods" › "finite-elements", with no material

  Scenario: Create a topic in the browser
    Given I am signed in as "maria"
    And I have created the course "computer-science"
    When I open the course "computer-science"
    And I create the topic "Introduction" in the subject "Distributed Systems"
    Then I still see the topic "distributed-systems" › "introduction", with no material

  Scenario: Add a topic to a subject the course already has
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "aeronautics"
    And I add the topic "Finite Volumes" to the subject "numerical-methods"
    Then I still see the topic "numerical-methods" › "finite-volumes", with no material
    And I see "fe-basics.txt" under "numerical-methods" › "finite-elements"

  Scenario: A reader of a shared course is not offered to create topics
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "aeronautics"
    Then I am not offered to create a topic

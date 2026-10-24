@ui
Feature: Courses in the browser
  As a student
  I want to start from my courses, and create one when I have none
  So that I always know where my material is and where to add more

  The Add material page asks for a subject; the topic and the file are optional. Its button
  says what it does: "Create subject" with only a subject, "Create topic" with a topic too, and
  "Upload" with a file, which needs a topic. A subject created there stays on the page, so a
  topic can be added to it; a topic created or uploaded to opens its page.

  Scenario: A student without courses is offered to create one
    Given I am signed in as "maria"
    Then I see that I have no courses yet
    And I am offered to create a new course

  Scenario: Create a course
    Given I am signed in as "maria"
    When I create the course "Computer Science"
    Then I am in the course "Computer Science"
    And I see that it has no material yet

  Scenario: My courses are listed when I sign in
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "rome.txt" to "history/ancient-history/rome"
    When I go to my courses
    Then I see the courses "Aeronautics, History"

  Scenario: Add material on its own page
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    When I open the course "Aeronautics"
    And I add "fe-basics.txt" to the subject "Numerical Methods", topic "Finite Elements"
    Then I am on the topic "Numerical Methods" › "Finite Elements"
    And I see its materials "fe-basics.txt"

  Scenario: Create a subject, then a topic, on the Add material page, without a file
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    When I open the course "Aeronautics"
    And on the Add material page I fill in the subject "Fluid Dynamics"
    Then its button says "Create subject"
    When I press it
    Then I am told the subject "Fluid Dynamics" is created, and can add a topic to it
    When I fill in the topic "Turbulence"
    Then its button says "Create topic"
    When I press it
    Then I am on the topic "Fluid Dynamics" › "Turbulence"
    And I see that the topic has no material yet

  Scenario: A file is uploaded to a topic
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    When I open the course "Aeronautics"
    And on the Add material page I fill in the subject "Fluid Dynamics"
    And I choose the file "turbulence.txt"
    Then its button says "Upload"
    When I press it
    Then I am told to fill in the topic the file goes in

  Scenario: Edit a material in the reader
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    When I open the course "Aeronautics"
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
    When I open the course "Aeronautics"
    And I open the topic "Finite elements"
    And I add "fe-meshing.txt" to this topic
    Then I see its materials "fe-basics.txt, fe-meshing.txt"

  Scenario: A topic stays when all of its material is deleted
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I open the topic "Finite elements"
    And I delete "fe-basics.txt"
    Then I no longer see "fe-basics.txt"
    When I go back to the subject
    Then I still see the topic "Numerical methods" › "Finite elements", with no material

  Scenario: Create a topic in the browser
    Given I am signed in as "maria"
    And I have created the course "computer-science"
    When I open the course "Computer science"
    And I create the topic "Introduction" in the subject "Distributed Systems"
    Then I still see the topic "Distributed Systems" › "Introduction", with no material

  Scenario: Add a topic to a subject the course already has
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I add the topic "Finite Volumes" to the subject "Numerical methods"
    Then I still see the topic "Numerical methods" › "Finite Volumes", with no material
    And I see "fe-basics.txt" under "Numerical methods" › "Finite elements"

  Scenario: Move a topic up or down
    Given I am signed in as "maria"
    And I have created the course "computer-science"
    And I have created the topic "distributed-systems/introduction" in "computer-science"
    And I have created the topic "distributed-systems/consensus" in "computer-science"
    And I have created the topic "distributed-systems/replication" in "computer-science"
    When I open the course "Computer science"
    And I open the subject "Distributed systems"
    And I move the topic "Replication" up
    Then the topics of "Distributed systems" are shown in the order "Introduction, Replication, Consensus"
    When I move the topic "Introduction" down
    Then the topics of "Distributed systems" are shown in the order "Replication, Introduction, Consensus"
    And they are still in that order when I open the subject again

  Scenario: A reader of a shared course is not offered to reorder topics
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has uploaded "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
    And the student "maria" has shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    Then I am not offered to move topics
    And I am not offered to rename subjects or topics

  Scenario: Delete a course
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "rome.txt" to "history/ancient-history/rome"
    When I open the course "Aeronautics"
    And I delete the course, and confirm it
    Then I am in my courses
    And I see the courses "History"

  Scenario: Deleting a course asks first
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I delete the course, but cancel
    Then I see "fe-basics.txt" under "Numerical methods" › "Finite elements"

  Scenario: Only the creator is offered to delete a course
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has shared the course "aeronautics" with "tom" as an owner
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    Then I am not offered to delete the course

  Scenario: A reader of a shared course is not offered to create topics
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    Then I am not offered to create a topic

  Scenario: Rename a topic
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I rename the topic "Finite elements" to "The Finite Element Method"
    Then I see "fe-basics.txt" under "Numerical methods" › "The Finite Element Method"
    When I open the topic "The Finite Element Method"
    Then I am on the topic "Numerical methods" › "The Finite Element Method"

  Scenario: Rename a subject
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I rename the subject "Numerical methods" to "Numerical Methods for PDEs"
    Then I see "fe-basics.txt" under "Numerical Methods for PDEs" › "Finite elements"

  Scenario: Cancel renaming
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I start renaming the topic "Finite elements" to "Something else", but cancel
    Then I see "fe-basics.txt" under "Numerical methods" › "Finite elements"

  Scenario: Change a course's title from my courses
    Given I am signed in as "maria"
    And I have created the course "computer-science"
    When I go to my courses
    And I change the title of "Computer science" to "Computer Science 101"
    Then I see the courses "Computer Science 101"

  Scenario: Change a course's title on its page
    Given I am signed in as "maria"
    And I have created the course "computer-science"
    When I open the course "Computer science"
    And I change the title of "Computer science" to "Computer Science 101"
    Then I am in the course "Computer Science 101"

  Scenario: Only the course's creator is offered to change its title
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has shared the course "aeronautics" with "tom" as an owner
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    Then I am not offered to change the course's title

  Scenario: Rename a topic on its page
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I open the topic "Finite elements"
    And I rename the topic "Finite elements" to "The Finite Element Method"
    Then I am on the topic "Numerical methods" › "The Finite Element Method"

  Scenario: A reader is not offered to rename a topic on its page
    Given the student "maria" has uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the student "maria" has shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    And I open the topic "Finite elements"
    Then I am not offered to rename the topic

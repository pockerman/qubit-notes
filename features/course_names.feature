Feature: The titles of courses
  As a student
  I want my courses shown with the titles I gave them, and to change them
  So that I see "Computer Science", not "computer-science"

  A course is known by its name: lowercase words joined by hyphens, e.g. "computer-science",
  made from the title it is created with. The name is in the course's links and never changes.
  Its title is what the student typed, e.g. "Computer Science", and is what the app shows, the
  same for every member. A course created without a title, e.g. by uploading to a new course,
  is titled after its name, as subjects and topics are (see The names of subjects and topics):
  "computer-science" is "Computer science". Only the student who created a course can change
  its title; it can't be blank, or the title of another of their courses.

  Background:
    Given I am the student "maria"

  Rule: A course has the title it is created with

    @platform
    Scenario: Create a course with a title
      When I create the course "computer-science" titled "Computer Science"
      Then I see the courses:
        | course           | title            |
        | computer-science | Computer Science |

    Scenario: A course created without a title is titled after its name
      When I upload the file "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      Then I see the courses:
        | course      | title       |
        | aeronautics | Aeronautics |

  Rule: The student who created a course changes its title, and its name stays

    Background:
      Given I have created the course "computer-science" titled "Computer Science"
      And I have uploaded "intro.txt" to "computer-science/distributed-systems/introduction"

    @platform
    Scenario: Change a course's title
      When I change the title of "computer-science" to "Computer Science 101"
      Then I see the courses:
        | course           | title                |
        | computer-science | Computer Science 101 |
      And the materials of "computer-science/distributed-systems/introduction" are:
        | filename  |
        | intro.txt |

    Scenario: Every member sees the new title
      Given I have shared the course "computer-science" with "tom" as a reader
      When I change the title of "computer-science" to "Computer Science 101"
      Then the student "tom" sees the course "computer-science" titled "Computer Science 101"

    Scenario: A title can't be blank
      When I change the title of "computer-science" to " "
      Then I am told a title can't be blank

    Scenario: Two of my courses can't have the same title
      Given I have created the course "history" titled "History"
      When I change the title of "history" to "computer science"
      Then I am told I already have a course titled "Computer Science"

    Scenario Outline: Only the course's creator changes its title
      Given I have shared the course "computer-science" with "tom" as <role>
      When the student "tom" changes the title of "computer-science" to "CS"
      Then the student "tom" is not allowed to do that

      Examples:
        | role     |
        | a reader |
        | an owner |

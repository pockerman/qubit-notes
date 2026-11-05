Feature: Reading progress
  As a student
  I want the app to know which sections I have opened
  So that I can see how far through my material I am

  Every time the reader shows a student a section is kept. A section is shown with its subsections,
  so they count as opened too. Opening a section isn't proof of reading it, so the app says
  "opened", not "read". Each student's progress is their own.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.

      ## 2.1 Linear elements
      A linear element interpolates linearly between its two nodes.

      # 3 Assembly
      The element matrices are assembled into the global stiffness matrix.
      """

  Scenario: Nothing is opened to begin with
    Then I have opened 0 of the 4 sections of "fem-notes.md"

  Scenario: Opening a section
    When I open the section "1 Introduction" of "fem-notes.md"
    Then I have opened 1 of the 4 sections of "fem-notes.md"

  Scenario: Opening a section opens its subsections
    When I open the section "2 Shape functions" of "fem-notes.md"
    Then I have opened the sections "2 Shape functions, 2.1 Linear elements" of "fem-notes.md"

  Scenario: Opening a section again counts it once
    When I open the section "1 Introduction" of "fem-notes.md"
    And I open the section "1 Introduction" of "fem-notes.md"
    Then I have opened 1 of the 4 sections of "fem-notes.md"
    And every time I opened "fem-notes.md" is kept: 2

  Scenario: There is no such section
    When I open section 99 of "fem-notes.md"
    Then I am told there is no such section

  Scenario: My progress is my own
    Given I have shared the course "aeronautics" with "tom" as a reader
    And I have opened the section "1 Introduction" of "fem-notes.md"
    Then the student "tom" has opened 0 of the 4 sections of "fem-notes.md"

  Scenario: Someone who isn't a member of the course has no progress in it
    When the student "tom" opens the section "1 Introduction" of "fem-notes.md"
    Then the student "tom" is not allowed to do that

  Scenario: A section the material no longer has isn't counted
    Given I have opened the section "3 Assembly" of "fem-notes.md"
    When I change the text of "fem-notes.md" to:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    And "fem-notes.md" is eventually ready
    Then I have opened 0 of the 1 sections of "fem-notes.md"

  Scenario: Deleting a material deletes its progress
    Given I have opened the section "1 Introduction" of "fem-notes.md"
    When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
    Then nothing is kept of what I opened

  Scenario: Deleting a course deletes its progress
    Given I have opened the section "1 Introduction" of "fem-notes.md"
    When I delete the course "aeronautics"
    Then nothing is kept of what I opened

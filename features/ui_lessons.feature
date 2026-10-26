@ui
Feature: Lessons from a document in the browser
  As a student
  I want to make a subject's lessons from a document on the subject's page
  So that a textbook becomes my topics in one go

  "Make lessons from a document" on a subject's page takes a PDF, an EPUB or a Markdown file and
  makes a topic of each of its headings, after the subject's other topics (see Lessons from a
  document). The student is told how many lessons were made, or why none could be.

  Background:
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    And I have created the subject "Numerical methods" in "aeronautics"
    And I have the file "fem.md" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Scenario: Make lessons from a document
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I make lessons from "fem.md"
    Then I am told 2 lessons were made
    And I see the topics "1 Introduction, 2 Shape functions" under "Numerical methods"
    When I open the topic "2 Shape functions"
    Then I see its materials "2-shape-functions.md"

  Scenario: A file that is not a document
    Given I have the file "notes.txt" with the content:
      """
      The finite element method divides a domain into small elements.
      """
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I make lessons from "notes.txt"
    Then I see that lessons are made only from a PDF, an EPUB or a Markdown file
    And I see the subject "Numerical methods" with no topics yet

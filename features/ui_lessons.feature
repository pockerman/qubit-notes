@ui
Feature: Lessons from a document in the browser
  As a student
  I want to make a subject's lessons from a document on the subject's page
  So that a textbook becomes my topics in one go

  "Make lessons from a document" on a subject's page takes a PDF, an EPUB or a Markdown file and
  makes a topic of each of its headings, after the subject's other topics (see Lessons from a
  document). The student is told how many lessons were made, or why none could be. A lesson made
  from a PDF or an EPUB downloads the whole document, under its own name, as its original.

  The subject's page lists the originals its lessons were made from, under "Originals", each
  with how many lessons were made from it and a download. A PDF can be shown on the page, and
  hidden again; an EPUB, which a browser can't show, is downloaded to be read. Originals are
  hidden until the student shows them.

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

  Scenario: A lesson downloads the original PDF
    Given I have the PDF "fem.pdf" with the pages:
      | page | text                                                            | outline           | level |
      | 1    | The finite element method divides a domain into small elements. | 1 Introduction    | 1     |
      | 2    | A linear element interpolates linearly between its two nodes.   | 2 Shape functions | 1     |
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I make lessons from "fem.pdf"
    Then I am told 2 lessons were made
    When I open the topic "2 Shape functions"
    And I open "2-shape-functions.md" to read it
    And I download its original
    Then I get "fem.pdf", the file I made the lessons from

  Scenario: Show and hide the original on the subject's page
    Given I have the PDF "fem.pdf" with the pages:
      | page | text                                                            | outline           | level |
      | 1    | The finite element method divides a domain into small elements. | 1 Introduction    | 1     |
      | 2    | A linear element interpolates linearly between its two nodes.   | 2 Shape functions | 1     |
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I make lessons from "fem.pdf"
    Then I see the original "fem.pdf", made into 2 lessons, hidden
    When I show the original "fem.pdf"
    Then I see "fem.pdf" on the page
    When I hide the original "fem.pdf"
    Then I see the original "fem.pdf", made into 2 lessons, hidden
    When I download the original "fem.pdf" from the subject's page
    Then I get "fem.pdf", the file I made the lessons from

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

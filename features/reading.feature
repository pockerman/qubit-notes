Feature: Reading material
  As a student
  I want to read my material in the assistant, section by section
  So that I can study, take notes and ask for summaries and quizzes in one place

  A document is divided into sections: its chapters and the headings within them.
  A Markdown file's sections are its headings; a PDF's come from its outline (bookmarks),
  or are its pages if it has no outline; a plain text file is a single section.
  A section includes its subsections, so "2 Shape functions" includes "2.1 Linear elements".

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

      ## 2.2 Quadratic elements
      A quadratic element adds a node in the middle of each edge.

      # 3 Assembly
      The element matrices are assembled into the global stiffness matrix.
      """

  Rule: A document is read section by section

    @platform
    Scenario: See the sections of a document
      When I open "fem-notes.md"
      Then I see the sections:
        | section                 | level |
        | 1 Introduction          | 1     |
        | 2 Shape functions       | 1     |
        | 2.1 Linear elements     | 2     |
        | 2.2 Quadratic elements  | 2     |
        | 3 Assembly              | 1     |

    @platform
    Scenario: Read a section
      When I read the section "2.1 Linear elements" of "fem-notes.md"
      Then I read "A linear element interpolates linearly between its two nodes."

    Scenario: Reading a section includes its subsections
      When I read the section "2 Shape functions" of "fem-notes.md"
      Then I read "Shape functions interpolate the solution inside each element."
      And I read "A linear element interpolates linearly between its two nodes."
      And I read "A quadratic element adds a node in the middle of each edge."

    Scenario: A PDF without an outline is read page by page
      Given I have uploaded a 3-page PDF "lecture-1.pdf" without an outline to "aeronautics/numerical-methods/finite-elements"
      When I open "lecture-1.pdf"
      Then I see the sections:
        | section | level |
        | Page 1  | 1     |
        | Page 2  | 1     |
        | Page 3  | 1     |

    Scenario: A document is not readable until it has been processed
      Given I have just uploaded "fe-meshing.txt" to "aeronautics/numerical-methods/finite-elements"
      When I open "fe-meshing.txt" before it is ready
      Then I am told the material is still being processed

  Rule: The original file can be downloaded

    @platform
    Scenario: Download the original file
      When I download "fem-notes.md"
      Then I get the file exactly as I uploaded it

  Rule: Readers of a shared course can read its material

    Scenario: A reader reads a shared course's material
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" reads the section "3 Assembly" of "fem-notes.md"
      Then the student "tom" reads "The element matrices are assembled into the global stiffness matrix."

    Scenario: A student who isn't a member cannot read a course's material
      When the student "tom" reads the section "3 Assembly" of "fem-notes.md"
      Then the student "tom" is not allowed to do that

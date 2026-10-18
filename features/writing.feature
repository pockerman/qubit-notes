Feature: Writing material
  As a student
  I want to write the material of a topic myself, typing or pasting it in
  So that I can study from my own notes without making a file first

  Owners of a course write a Markdown material in one of its topics. They give it a name,
  which is stored as a filename: lowercase words joined by hyphens, ending in ".md", e.g.
  "Shape functions" is "shape-functions.md". Once saved, a written material is like an uploaded
  Markdown file: it is processed, read section by section, searched, summarised, quizzed
  and edited (see Editing material).

  Background:
    Given I am the student "maria"
    And I have created the course "aeronautics"
    And I have created the topic "numerical-methods/finite-elements" in "aeronautics"

  Rule: The owners of a course write Markdown material in its topics

    @gogi
    Scenario: Write a material
      When I write the material "Shape functions" in "aeronautics/numerical-methods/finite-elements" with the text:
        """
        # 1 Shape functions
        Shape functions interpolate the solution inside each element.

        ## 1.1 Linear elements
        A linear element interpolates linearly between its two nodes.
        """
      Then "shape-functions.md" is eventually ready
      And I see the sections:
        | section             | level |
        | 1 Shape functions   | 1     |
        | 1.1 Linear elements | 2     |
      And searching "aeronautics" for "interpolates linearly" finds "shape-functions.md"

    Scenario Outline: The name is stored as a Markdown filename
      When I write the material "<name>" in "aeronautics/numerical-methods/finite-elements" with the text:
        """
        Shape functions interpolate the solution inside each element.
        """
      Then the materials of "aeronautics/numerical-methods/finite-elements" are:
        | filename   |
        | <filename> |

      Examples:
        | name               | filename           |
        | Shape functions    | shape-functions.md |
        | shape-functions.md | shape-functions.md |
        | Week 3: Assembly!  | week-3-assembly.md |

    Scenario: A written material is edited like an uploaded one
      Given I have written the material "Shape functions" in "aeronautics/numerical-methods/finite-elements" with the text:
        """
        # 1 Shape functions
        Shape functions interpolate the solution inside each element.
        """
      When I open "shape-functions.md" for editing
      Then I am given its text exactly as I wrote it

    Scenario: A name already used in the topic is not taken over
      Given I have written the material "Shape functions" in "aeronautics/numerical-methods/finite-elements" with the text:
        """
        Shape functions interpolate the solution inside each element.
        """
      When I write the material "Shape functions" in "aeronautics/numerical-methods/finite-elements" with the text:
        """
        Something else entirely.
        """
      Then I am told the topic already has "shape-functions.md"
      And the text of "shape-functions.md" is still "Shape functions interpolate the solution inside each element."

    Scenario Outline: A material needs a name and some text
      When I write the material "<name>" in "aeronautics/numerical-methods/finite-elements" with the text:
        """
        <text>
        """
      Then I am told <problem>

      Examples:
        | name            | text                                   | problem                      |
        |                 | Shape functions interpolate the field. | the material needs a name    |
        | !!!             | Shape functions interpolate the field. | the material needs a name    |
        | Shape functions |                                        | the material needs some text |

    Scenario: A reader of a shared course cannot write material in it
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" writes the material "Tom's notes" in "aeronautics/numerical-methods/finite-elements" with the text:
        """
        Notes of my own.
        """
      Then the student "tom" is not allowed to do that

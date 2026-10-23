Feature: References between topics
  As a student
  I want my material to refer to the other topics, materials and sections of my course
  So that I can follow what a topic builds on, and find what builds on it

  A Markdown material, whether written, uploaded or converted from a PDF or an EPUB, refers to
  another part of its course with a reference in double brackets:
    | reference                                                     | refers to                                   |
    | [[numerical-methods/finite-elements]]                         | the topic finite-elements of numerical-methods |
    | [[numerical-methods/finite-elements/fem-notes.md]]            | the material fem-notes.md in that topic     |
    | [[numerical-methods/finite-elements/fem-notes.md#2 Assembly]] | the section "2 Assembly" of that material   |
  A label may follow a "|": [[numerical-methods/finite-elements|the FEM topic]] is shown as
  "the FEM topic". Without one, a reference is shown as the name of what it refers to: the
  topic's, the material's or the section's, e.g. "finite-elements".

  A reference is to the material's own course; it is followed as a link: to the topic's page,
  or to the material, opened at the section if it names one. A reference to something
  the course doesn't have, mistyped or since deleted, is broken: it is shown, but not as a link,
  and the student is told of it when they save the material. Text in code is never a reference.

  A topic is mentioned in each material that refers to it, to one of its materials, or to one of
  their sections. A PDF or an EPUB downloaded as it is now has each reference as its label, as
  text.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Assembly
      The element matrices are assembled into the global stiffness matrix.
      """
    And I have created the topic "numerical-methods/linear-solvers" in "aeronautics"

  Rule: A material refers to the topics, materials and sections of its course

    @platform
    Scenario: The references of a material
      When I write the material "Sparse matrices" in "aeronautics/numerical-methods/linear-solvers" with the text:
        """
        # 1 Sparse matrices
        The stiffness matrix of [[numerical-methods/finite-elements]] is sparse.
        It is assembled as in [[numerical-methods/finite-elements/fem-notes.md#2 Assembly|the assembly]],
        see [[numerical-methods/finite-elements/fem-notes.md]].
        """
      Then the references of "sparse-matrices.md" are:
        | shown as        | refers to | subject           | topic           | material     | section    |
        | finite-elements | topic     | numerical-methods | finite-elements |              |            |
        | the assembly    | section   | numerical-methods | finite-elements | fem-notes.md | 2 Assembly |
        | fem-notes.md    | material  | numerical-methods | finite-elements | fem-notes.md |            |
      And none of its references is broken

    Scenario: A reference in code is not one
      When I write the material "Wiki syntax" in "aeronautics/numerical-methods/linear-solvers" with the text:
        """
        A reference is written `[[subject/topic]]`:

        ```
        [[numerical-methods/finite-elements]]
        ```
        """
      Then "wiki-syntax.md" has no references

    Scenario Outline: A reference to what the course doesn't have is broken
      When I write the material "Sparse matrices" in "aeronautics/numerical-methods/linear-solvers" with the text:
        """
        The stiffness matrix of <reference> is sparse.
        """
      Then the material is saved
      And I am told "sparse-matrices.md" has the broken reference "<reference>"
      And the references of "sparse-matrices.md" are:
        | shown as   | refers to |
        | <shown as> | nothing   |

      Examples:
        | reference                                                      | shown as         |
        | [[numerical-methods/finite-element]]                           | finite-element   |
        | [[numerical-methods/finite-elements/lecture-9.pdf]]            | lecture-9.pdf    |
        | [[numerical-methods/finite-elements/fem-notes.md#9 Nothing]]   | 9 Nothing        |
        | [[finite-elements]]                                            | finite-elements  |

    Scenario: Editing a material tells of its broken references too
      When I change the text of "fem-notes.md" to:
        """
        # 1 Introduction
        The matrices are solved as in [[numerical-methods/linear-solver]].
        """
      Then I am told "fem-notes.md" has the broken reference "[[numerical-methods/linear-solver]]"

    Scenario: A reference to a material breaks when the material is deleted
      Given I have written the material "Sparse matrices" in "aeronautics/numerical-methods/linear-solvers" with the text:
        """
        It is assembled as in [[numerical-methods/finite-elements/fem-notes.md]].
        """
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then the references of "sparse-matrices.md" are:
        | shown as     | refers to |
        | fem-notes.md | nothing   |

    Scenario: A topic of another course is not referred to
      Given I have created the course "mechanics"
      And I have created the topic "numerical-methods/finite-elements" in "mechanics"
      When I write the material "Sparse matrices" in "mechanics/numerical-methods/finite-elements" with the text:
        """
        As in [[numerical-methods/linear-solvers]].
        """
      Then I am told "sparse-matrices.md" has the broken reference "[[numerical-methods/linear-solvers]]"

  Rule: A topic is mentioned in the materials that refer to it

    Background:
      Given I have written the material "Sparse matrices" in "aeronautics/numerical-methods/linear-solvers" with the text:
        """
        # 1 Sparse matrices
        The stiffness matrix of [[numerical-methods/finite-elements]] is sparse.
        It is assembled as in [[numerical-methods/finite-elements/fem-notes.md#2 Assembly]].
        """

    @platform
    Scenario: A topic's mentions
      Then the topic "numerical-methods/finite-elements" of "aeronautics" is mentioned in:
        | subject           | topic          | material           |
        | numerical-methods | linear-solvers | sparse-matrices.md |
      And the topic "numerical-methods/linear-solvers" of "aeronautics" is mentioned in nothing

    Scenario: A material no longer mentions a topic once its references to it are gone
      When I change the text of "sparse-matrices.md" to:
        """
        # 1 Sparse matrices
        Most of a stiffness matrix's entries are zero.
        """
      Then the topic "numerical-methods/finite-elements" of "aeronautics" is mentioned in nothing

    Scenario: A deleted material mentions nothing
      When I delete the material "sparse-matrices.md" from "aeronautics/numerical-methods/linear-solvers"
      Then the topic "numerical-methods/finite-elements" of "aeronautics" is mentioned in nothing

    Scenario: A reader of a shared course sees its references and mentions
      Given I have shared the course "aeronautics" with "tom" as a reader
      Then the student "tom" sees that the topic "numerical-methods/finite-elements" of "aeronautics" is mentioned in:
        | subject           | topic          | material           |
        | numerical-methods | linear-solvers | sparse-matrices.md |
      And the student "tom" sees 2 references in "sparse-matrices.md"

  Rule: A converted material downloaded as it is now has its references as text

    Scenario: The references of a converted PDF are its labels
      Given I have uploaded a PDF "lecture-1.pdf" to "aeronautics/numerical-methods/finite-elements" with the pages:
        | page | text                                                            | outline        | level |
        | 1    | The finite element method divides a domain into small elements. | 1 Introduction | 1     |
      And I have changed the text of "lecture-1.pdf" to:
        """
        # 1 Introduction
        The system is solved with [[numerical-methods/linear-solvers|sparse solvers]].
        """
      When I download "lecture-1.pdf" as it is now
      Then its text includes "The system is solved with sparse solvers."
      But its text does not include "[["

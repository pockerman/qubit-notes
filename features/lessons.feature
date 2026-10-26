Feature: Lessons from a document
  As a student
  I want to make a subject's lessons from a PDF, an EPUB or a Markdown document, such as a textbook
  So that I don't have to create each topic and add its material one by one

  The owner of a course uploads a document to one of its subjects, and the app makes a topic, a
  lesson, of each of its headings at its top level: the shallowest level with at least two
  headings, so a book whose only top heading is its title is divided into its chapters. Each
  lesson is named after its heading, e.g. "2 Shape functions" (with the id 2-shape-functions),
  and has one Markdown material, named after it too, with the text up to the next lesson's
  heading. The lesson's heading is its material's top heading, and the headings within it are
  its sections. A PDF or an EPUB is converted to Markdown first, as it is when uploaded (see PDF
  and EPUB material as Markdown), and each lesson keeps the pictures in its text.

  Text before the first lesson's heading is a lesson of its own, named after the document's
  title if it has one, else "Introduction". A document with fewer than two headings is a single
  lesson, named after its title or its file. The lessons go after the subject's other topics,
  in the order of the document; a lesson whose id the subject already has is given one with a
  number after it, e.g. 1-introduction-2.

  A PDF's or an EPUB's lessons keep it as their original: each lesson downloads it, the whole
  document as it was uploaded, and downloads itself as it is now as a PDF or an EPUB laid out
  anew from its Markdown, as a converted material does. The original is kept until the last of
  its lessons' materials is deleted, and the subject lists the originals of its lessons, each
  with the lessons made from it. A Markdown document's lessons are their own text, so it isn't
  kept.

  The document is made into lessons in the background; the student follows it as they follow an
  upload. Lessons the app stopped making are made again when it starts.

  Background:
    Given I am the student "maria"
    And I have created the course "aeronautics"
    And I have created the subject "Numerical methods" in "aeronautics"

  Rule: Each heading at the document's top level is a lesson

    @platform
    Scenario: A PDF's outline gives its lessons
      When I make lessons in "aeronautics/numerical-methods" from a PDF "fem.pdf" with the pages:
        | page | text                                                                 | outline           | level |
        | 1    | The finite element method divides a domain into small elements.     | 1 Introduction    | 1     |
        | 2    | A linear element interpolates linearly between its two nodes.       | 2 Shape functions | 1     |
        | 3    | The element matrices are assembled into the global stiffness matrix. | 3 Assembly        | 1     |
      Then the lessons are made
      And the subject "numerical-methods" of "aeronautics" has the lessons:
        | lesson            | topic             | material            |
        | 1 Introduction    | 1-introduction    | 1-introduction.md   |
        | 2 Shape functions | 2-shape-functions | 2-shape-functions.md |
        | 3 Assembly        | 3-assembly        | 3-assembly.md       |
      And I read "The element matrices are assembled" in the lesson "3-assembly" of "aeronautics/numerical-methods"

    Scenario: An EPUB's chapters give its lessons
      When I make lessons in "aeronautics/numerical-methods" from an EPUB "fem.epub" with the chapters:
        | chapter           | text                                                            |
        | 1 Introduction    | The finite element method divides a domain into small elements. |
        | 2 Shape functions | A linear element interpolates linearly between its two nodes.   |
      Then the subject "numerical-methods" of "aeronautics" has the lessons:
        | lesson            | topic             | material             |
        | 1 Introduction    | 1-introduction    | 1-introduction.md    |
        | 2 Shape functions | 2-shape-functions | 2-shape-functions.md |

    Scenario: The headings within a lesson are its sections
      When I make lessons in "aeronautics/numerical-methods" from the Markdown "fem.md":
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Shape functions
        Shape functions interpolate the solution inside each element.

        ## 2.1 Linear elements
        A linear element interpolates linearly between its two nodes.
        """
      Then the lesson "2-shape-functions" of "aeronautics/numerical-methods" has the sections:
        | section             | level |
        | 2 Shape functions   | 1     |
        | 2.1 Linear elements | 2     |

    Scenario: A book is divided into its chapters, and its preface is a lesson of its own
      When I make lessons in "aeronautics/numerical-methods" from the Markdown "fem-book.md":
        """
        # The Finite Element Method
        This book is for engineers.

        ## 1 Introduction
        The finite element method divides a domain into small elements.

        ## 2 Shape functions
        Shape functions interpolate the solution inside each element.

        ### 2.1 Linear elements
        A linear element interpolates linearly between its two nodes.
        """
      Then the subject "numerical-methods" of "aeronautics" has the lessons:
        | lesson                     | topic                      | material                      |
        | The Finite Element Method  | the-finite-element-method  | the-finite-element-method.md  |
        | 1 Introduction             | 1-introduction             | 1-introduction.md             |
        | 2 Shape functions          | 2-shape-functions          | 2-shape-functions.md          |
      And the lesson "2-shape-functions" of "aeronautics/numerical-methods" has the sections:
        | section             | level |
        | 2 Shape functions   | 1     |
        | 2.1 Linear elements | 2     |

    Scenario: A document without headings is a single lesson
      When I make lessons in "aeronautics/numerical-methods" from the Markdown "meshing-notes.md":
        """
        A mesh of triangles is generated with Delaunay triangulation.
        """
      Then the subject "numerical-methods" of "aeronautics" has the lessons:
        | lesson        | topic         | material         |
        | Meshing notes | meshing-notes | meshing-notes.md |

    Scenario: A lesson keeps the pictures in its text
      When I make lessons in "aeronautics/numerical-methods" from a PDF "meshing.pdf" with a picture in its section "1 Meshing"
      Then the lesson "1-meshing" of "aeronautics/numerical-methods" has that image, and is missing none

  Rule: A PDF's or an EPUB's lessons keep it as their original

    Background:
      Given I have made lessons in "aeronautics/numerical-methods" from a PDF "fem.pdf" with the pages:
        | page | text                                                                 | outline           | level |
        | 1    | The finite element method divides a domain into small elements.     | 1 Introduction    | 1     |
        | 2    | A linear element interpolates linearly between its two nodes.       | 2 Shape functions | 1     |
        | 3    | The element matrices are assembled into the global stiffness matrix. | 3 Assembly        | 1     |

    @platform
    Scenario: The subject lists the originals of its lessons
      Then the subject "numerical-methods" of "aeronautics" has the originals:
        | original | lessons                                        |
        | fem.pdf  | 1-introduction, 2-shape-functions, 3-assembly  |

    Scenario: A reader sees the originals too
      Given I have shared the course "aeronautics" with "tom" as a reader
      Then the student "tom" sees the originals of "numerical-methods" in "aeronautics": "fem.pdf"

    Scenario: An original goes from the list with the last of its lessons
      When I delete the topic "numerical-methods/1-introduction" from "aeronautics"
      Then the subject "numerical-methods" of "aeronautics" has the originals:
        | original | lessons                       |
        | fem.pdf  | 2-shape-functions, 3-assembly |
      When I delete the topic "numerical-methods/2-shape-functions" from "aeronautics"
      And I delete the topic "numerical-methods/3-assembly" from "aeronautics"
      Then the subject "numerical-methods" of "aeronautics" has no originals

    @platform
    Scenario: A lesson downloads the original document
      When I download the original of the lesson "2-shape-functions" of "aeronautics/numerical-methods"
      Then I get the file exactly as I uploaded it

    Scenario: A lesson downloads itself as a PDF
      When I download the lesson "2-shape-functions" of "aeronautics/numerical-methods" as it is now
      Then I get a PDF called "2-shape-functions.pdf"
      And its text includes "A linear element interpolates linearly"
      But its text does not include "assembled into the global stiffness matrix"

    Scenario: The original is kept until the last of its lessons is deleted
      When I delete the topic "numerical-methods/1-introduction" from "aeronautics"
      And I delete the topic "numerical-methods/2-shape-functions" from "aeronautics"
      Then the original "fem.pdf" is kept in "aeronautics"
      When I delete the topic "numerical-methods/3-assembly" from "aeronautics"
      Then the original "fem.pdf" is no longer kept in "aeronautics"

    Scenario: A Markdown document isn't kept
      When I make lessons in "aeronautics/numerical-methods" from the Markdown "shape-functions.md":
        """
        # 4 Quadrature
        Gauss quadrature integrates the element matrices.

        # 5 Meshing
        A mesh of triangles is generated with Delaunay triangulation.
        """
      And I download the lesson "4-quadrature" of "aeronautics/numerical-methods"
      Then I get its own text, which does not include "Delaunay triangulation"

  Rule: Lessons the app stopped making are made when it starts again

    Scenario: The app stops while making lessons
      Given the app stopped while making lessons in "aeronautics/numerical-methods" from the Markdown "fem.md":
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Shape functions
        Shape functions interpolate the solution inside each element.
        """
      When the app starts again
      Then the lessons are made
      And the subject "numerical-methods" of "aeronautics" has the lessons:
        | lesson            | topic             | material             |
        | 1 Introduction    | 1-introduction    | 1-introduction.md    |
        | 2 Shape functions | 2-shape-functions | 2-shape-functions.md |

  Rule: Lessons go after the subject's other topics

    Scenario: The lessons follow the topics the subject has
      Given I have created the topic "numerical-methods/1-introduction" in "aeronautics"
      When I make lessons in "aeronautics/numerical-methods" from the Markdown "fem.md":
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Shape functions
        Shape functions interpolate the solution inside each element.
        """
      Then the topics of "numerical-methods" in "aeronautics" are, in order:
        | topic             |
        | 1-introduction    |
        | 1-introduction-2  |
        | 2-shape-functions |

  Rule: Only an owner makes lessons, from a document that can be read

    Scenario: A file that is not a PDF, an EPUB or Markdown
      When I make lessons in "aeronautics/numerical-methods" from the file "lecture.mp4"
      Then I am told to make lessons from a PDF, an EPUB or a Markdown file

    Scenario: A PDF without text
      When I make lessons in "aeronautics/numerical-methods" from a PDF of pictures only "scan.pdf"
      Then making the lessons fails, as "scan.pdf" has no text to convert, as it may be scanned
      And the subject "numerical-methods" of "aeronautics" has no topics

    Scenario: A reader cannot make lessons
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" makes lessons in "aeronautics/numerical-methods" from the Markdown "fem.md"
      Then the student "tom" is not allowed to do that

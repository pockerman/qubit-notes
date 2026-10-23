Feature: PDF and EPUB material as Markdown
  As a student
  I want my PDFs and e-books turned into text I can edit
  So that I can correct and extend all my material, not only the notes I wrote myself

  A PDF or an EPUB is converted to Markdown when it is uploaded, and from then on the material
  is that Markdown: it is read, edited, searched, summarised and quizzed as Markdown is. The
  material keeps the name it was uploaded with, e.g. "lecture-1.pdf".

  - A PDF's headings come from its outline (bookmarks) if it has one, else from the sizes of its
    fonts; a PDF with neither is divided into its pages, "Page 1", "Page 2" and so on. Lists and
    tables are kept as Markdown's.
  - An EPUB's headings are its chapters' and theirs within them.
  - The pictures in a PDF or an EPUB become the material's images (see Images in Markdown
    material), shown where they were.
  - A PDF without text, such as a scanned one, cannot be converted: there is no recognising of
    text in pictures.

  Two files can be downloaded: the original, exactly as it was uploaded, and the material as it
  is now, as a PDF or an EPUB like the original. The latter is laid out anew from the material's
  Markdown, with its headings, text, lists, tables and images; the original's fonts, columns and
  page breaks are not kept.

  PDFs uploaded before this feature stay as they were: read, but not edited.

  Background:
    Given I am the student "maria"

  Rule: A PDF or an EPUB is converted to Markdown when it is uploaded

    @platform
    Scenario: A PDF's outline gives its headings
      Given I have uploaded a PDF "lecture-1.pdf" to "aeronautics/numerical-methods/finite-elements" with the pages:
        | page | text                                                                 | outline           | level |
        | 1    | The finite element method divides a domain into small elements.     | 1 Introduction    | 1     |
        | 2    | A linear element interpolates linearly between its two nodes.       | 2 Shape functions | 1     |
        | 3    | The element matrices are assembled into the global stiffness matrix. | 3 Assembly        | 1     |
      When I open "lecture-1.pdf"
      Then I see the sections:
        | section           | level |
        | 1 Introduction    | 1     |
        | 2 Shape functions | 1     |
        | 3 Assembly        | 1     |
      And I read "The element matrices are assembled" in the section "3 Assembly" of "lecture-1.pdf"

    Scenario: A PDF's font sizes give its headings when it has no outline
      Given I have uploaded a PDF "lecture-2.pdf" to "aeronautics/numerical-methods/finite-elements" with the lines:
        | text                                                            | size |
        | Introduction                                                    | 20   |
        | The finite element method divides a domain into small elements. | 11   |
        | Shape functions                                                 | 20   |
        | Linear elements                                                 | 15   |
        | A linear element interpolates linearly between its two nodes.   | 11   |
      When I open "lecture-2.pdf"
      Then I see the sections:
        | section         | level |
        | Introduction    | 1     |
        | Shape functions | 1     |
        | Linear elements | 2     |

    Scenario: A PDF with no outline and one size of font is divided into its pages
      Given I have uploaded a 3-page PDF "lecture-3.pdf" without an outline to "aeronautics/numerical-methods/finite-elements"
      When I open "lecture-3.pdf"
      Then I see the sections:
        | section | level |
        | Page 1  | 1     |
        | Page 2  | 1     |
        | Page 3  | 1     |

    @platform
    Scenario: An EPUB's chapters give its headings
      Given I have uploaded an EPUB "fem-book.epub" to "aeronautics/numerical-methods/finite-elements" with the chapters:
        | chapter           | text                                                                 |
        | 1 Introduction    | The finite element method divides a domain into small elements.     |
        | 2 Shape functions | A linear element interpolates linearly between its two nodes.       |
        | 3 Assembly        | The element matrices are assembled into the global stiffness matrix. |
      When I open "fem-book.epub"
      Then I see the sections:
        | section           | level |
        | 1 Introduction    | 1     |
        | 2 Shape functions | 1     |
        | 3 Assembly        | 1     |

    Scenario Outline: The pictures of a PDF or an EPUB become the material's images
      Given I have uploaded <kind> "<filename>" with a picture in its section "1 Meshing" to "aeronautics/numerical-methods/finite-elements"
      When I open "<filename>" for editing
      Then its text shows an image in the section "1 Meshing"
      And "<filename>" has that image, and is missing none

      Examples:
        | kind     | filename      |
        | a PDF    | meshing.pdf   |
        | an EPUB  | meshing.epub  |

    Scenario: A PDF without text cannot be converted
      When I upload a PDF "scan.pdf" of pictures only to "aeronautics/numerical-methods/finite-elements"
      Then the material "scan.pdf" fails to be processed
      And I am told "scan.pdf" has no text to convert, as it may be scanned

  Rule: A converted material is edited as Markdown

    Background:
      Given I have uploaded a PDF "lecture-1.pdf" to "aeronautics/numerical-methods/finite-elements" with the pages:
        | page | text                                                            | outline           | level |
        | 1    | The finite element method divides a domain into small elements. | 1 Introduction    | 1     |
        | 2    | A linear element interpolates linearly between its two nodes.   | 2 Shape functions | 1     |

    @platform
    Scenario: Edit a converted PDF
      When I change the text of "lecture-1.pdf" to:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Shape functions
        A linear element interpolates linearly between its two nodes.

        # 3 Assembly
        The element matrices are assembled into the global stiffness matrix.
        """
      Then "lecture-1.pdf" is eventually ready
      And I see the sections:
        | section           | level |
        | 1 Introduction    | 1     |
        | 2 Shape functions | 1     |
        | 3 Assembly        | 1     |

    Scenario: Start editing a converted PDF from its Markdown
      When I open "lecture-1.pdf" for editing
      Then I am given Markdown with the headings "1 Introduction" and "2 Shape functions"

  Rule: The original and the material as it is now can both be downloaded

    Background:
      Given I have uploaded a PDF "lecture-1.pdf" to "aeronautics/numerical-methods/finite-elements" with the pages:
        | page | text                                                            | outline           | level |
        | 1    | The finite element method divides a domain into small elements. | 1 Introduction    | 1     |
        | 2    | A linear element interpolates linearly between its two nodes.   | 2 Shape functions | 1     |
      And I have changed the text of "lecture-1.pdf" to:
        """
        # 1 Introduction
        Galerkin's method weights the residual with the shape functions.
        """

    @platform
    Scenario: Download the original PDF
      When I download the original of "lecture-1.pdf"
      Then I get the file exactly as I uploaded it

    @platform
    Scenario: Download the PDF as it is now
      When I download "lecture-1.pdf" as it is now
      Then I get a PDF called "lecture-1.pdf"
      And its text includes "Galerkin's method weights the residual"
      But its text does not include "divides a domain into small elements"

    Scenario: Download an EPUB as it is now
      Given I have uploaded an EPUB "fem-book.epub" to "aeronautics/numerical-methods/finite-elements" with the chapters:
        | chapter        | text                                                            |
        | 1 Introduction | The finite element method divides a domain into small elements. |
      And I have changed the text of "fem-book.epub" to:
        """
        # 1 Introduction
        Galerkin's method weights the residual with the shape functions.
        """
      When I download "fem-book.epub" as it is now
      Then I get an EPUB called "fem-book.epub" with the chapter "1 Introduction"
      And its text includes "Galerkin's method weights the residual"

    Scenario: The material as it is now has its images
      Given I have uploaded a PDF "meshing.pdf" with a picture in its section "1 Meshing" to "aeronautics/numerical-methods/finite-elements"
      When I download "meshing.pdf" as it is now
      Then I get a PDF with 1 picture

    Scenario: A reader of a shared course downloads both
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" downloads the original of "lecture-1.pdf"
      Then the student "tom" gets the file exactly as I uploaded it
      When the student "tom" downloads "lecture-1.pdf" as it is now
      Then the student "tom" gets a PDF called "lecture-1.pdf"

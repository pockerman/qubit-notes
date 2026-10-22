Feature: Images in Markdown material
  As a student
  I want the images of my Markdown notes to be kept with them
  So that I study from my notes as I wrote them, figures and all

  A Markdown material refers to its images the way Markdown does, e.g.
  ![A mesh of triangles](figures/mesh.png). The owners of its course add those images to it;
  an image is kept with its material under the path the material refers to it by, and goes
  when the material does. An image is not a material of its own: it is not listed, searched,
  summarised or quizzed. Images on the web (https://...) are shown as they are and not kept.

  PNG, JPEG, GIF and WebP images up to 10 MB are accepted. A PDF's images are part of the
  PDF; only Markdown material has images of its own.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Meshing
      The domain is divided into triangles.

      ![A mesh of triangles](figures/mesh.png)

      # 2 Shape functions
      ![A linear shape function](figures/linear.png)
      ![The finite element logo](https://example.org/logo.png)
      """

  Rule: A material's images are added to it under the paths it refers to them by

    @platform
    Scenario: Add an image a material refers to
      When I add the image "figures/mesh.png" to "fem-notes.md"
      Then "fem-notes.md" has the images "figures/mesh.png"
      And the image "figures/mesh.png" of "fem-notes.md" is the one I added

    Scenario: The images a material refers to but does not have are missing
      Given I have added the image "figures/mesh.png" to "fem-notes.md"
      Then "fem-notes.md" is missing the images "figures/linear.png"

    Scenario: An image is matched to its reference by its file name
      When I add an image called "linear.png" to "fem-notes.md"
      Then "fem-notes.md" has the images "figures/linear.png"

    Scenario: Adding an image again replaces it
      Given I have added the image "figures/mesh.png" to "fem-notes.md"
      When I add another image as "figures/mesh.png" to "fem-notes.md"
      Then the image "figures/mesh.png" of "fem-notes.md" is the one I added last

    Scenario: An image is not a material of its own
      When I add the image "figures/mesh.png" to "fem-notes.md"
      Then the materials of "aeronautics/numerical-methods/finite-elements" are:
        | filename     |
        | fem-notes.md |
      And the topics of "aeronautics" are:
        | subject           | topic           | materials |
        | numerical-methods | finite-elements | 1         |

    Scenario: An image the material does not refer to is not added
      When I add the image "figures/other.png" to "fem-notes.md"
      Then I am told "fem-notes.md" does not refer to "other.png"

  Rule: Only images, and not too large

    Scenario Outline: The image types that are accepted
      When I add the image "figures/mesh.<extension>" to "fem-notes.md", which it refers to
      Then the image is <outcome>

      Examples:
        | extension | outcome  |
        | png       | accepted |
        | jpg       | accepted |
        | jpeg      | accepted |
        | gif       | accepted |
        | webp      | accepted |
        | svg       | rejected |
        | bmp       | rejected |

    Scenario: An image larger than 10 MB is rejected
      When I add an image of 11 MB as "figures/mesh.png" to "fem-notes.md"
      Then I am told the image is larger than 10 MB

    Scenario Outline: Only Markdown material has images of its own
      Given I have uploaded "<filename>" to "aeronautics/numerical-methods/finite-elements"
      When I add the image "figures/mesh.png" to "<filename>"
      Then I am told only Markdown material has images

      Examples:
        | filename      |
        | fe-basics.txt |
        | lecture-1.pdf |

  Rule: Images go with their material, and are shared with its course

    @platform
    Scenario: Deleting a material deletes its images
      Given I have added the image "figures/mesh.png" to "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then the image "figures/mesh.png" of "fem-notes.md" is gone

    Scenario: A material keeps its images when its text is edited
      Given I have added the image "figures/mesh.png" to "fem-notes.md"
      When I change the text of "fem-notes.md" to:
        """
        # 1 Meshing
        The domain is divided into triangles and quadrilaterals.

        ![A mesh of triangles](figures/mesh.png)
        """
      Then "fem-notes.md" has the images "figures/mesh.png"

    Scenario: A reader sees a shared course's images but cannot add any
      Given I have added the image "figures/mesh.png" to "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      Then the student "tom" sees the image "figures/mesh.png" of "fem-notes.md"
      When the student "tom" adds the image "figures/linear.png" to "fem-notes.md"
      Then the student "tom" is not allowed to do that

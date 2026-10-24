@ui
Feature: Images in the browser
  As a student
  I want to add the images of my Markdown notes as I upload or write them
  So that I see my figures where they belong when I read

  Background:
    Given I am signed in as "maria"
    And I have created the course "aeronautics"
    And I have created the topic "numerical-methods/finite-elements" in "aeronautics"

  Scenario: Upload a Markdown file with its images
    Given I have the file "fem-notes.md" with the content:
      """
      # 1 Meshing
      The domain is divided into triangles.

      ![A mesh of triangles](figures/mesh.png)
      """
    When I open the course "Aeronautics"
    And I add "fem-notes.md" and the image "mesh.png" to the topic "Finite elements"
    And I open "fem-notes.md" to read it
    Then I see the image "A mesh of triangles"

  Scenario: Add an image while writing
    When I open the course "Aeronautics"
    And I write material in the topic "Finite elements"
    And I name it "Meshing"
    And I type:
      """
      # 1 Meshing
      The domain is divided into triangles.

      """
    And I add the image "mesh.png" with the caption "A mesh of triangles"
    And I preview it
    Then I see the image "A mesh of triangles"
    When I save it
    And I open "meshing.md" to read it
    Then I see the image "A mesh of triangles"

  Scenario: Add a missing image from the reader
    Given I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Meshing
      ![A mesh of triangles](figures/mesh.png)
      """
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    Then I see that the image "figures/mesh.png" is missing
    When I add the missing image "figures/mesh.png" from "mesh.png"
    Then I see the image "A mesh of triangles"

  Scenario: A reader is not offered to add missing images
    Given I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Meshing
      ![A mesh of triangles](figures/mesh.png)
      """
    And I have shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    Then I see that the image "figures/mesh.png" is missing
    But I am not offered to add it

  Scenario: Add an image while editing a material
    Given I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Meshing
      The domain is divided into triangles.
      """
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I start editing it
    And I add the image "mesh.png" with the caption "A mesh of triangles"
    And I save my changes
    Then I see the image "A mesh of triangles"

  Scenario: Plain text material is not offered images while editing
    Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    When I open the course "Aeronautics"
    And I open "fe-basics.txt" to read it
    And I start editing it
    Then I am not offered to add an image

Feature: Downloading a subject as a zip
  As a student
  I want to download everything of a subject in one file
  So that I keep a copy of its material and my flashcards, to read or study elsewhere

  A subject downloads as "<subject>.zip", with a folder for each of its topics, numbered in the
  order they are read, holding the topic's material in its reading order, each as it is now. A
  Markdown material with images is in a folder of its own, its images beside it under the paths
  it refers to them by, so it reads as it does in the app. A material converted from a PDF or an
  EPUB comes with its original. The student's flashcards of the subject, every card they review,
  due or not, are in flashcards.csv, which a flashcard app can import, and flashcards.md, to read.
  README.md says what the zip holds. The zip is made when it is asked for, and not kept. Everyone who can see the subject downloads it, with their own
  flashcards and no one else's.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Meshing
      The domain is divided into triangles.

      ![A mesh of triangles](figures/mesh.png)
      """
    And I have uploaded "solvers.md" to "aeronautics/numerical-methods/solvers" with the content:
      """
      # 1 Iterative solvers
      Conjugate gradients solve symmetric systems.
      """
    And I have uploaded "lift.md" to "aeronautics/aerodynamics/lift" with the content:
      """
      # 1 Lift
      Lift comes from the pressure difference over a wing.
      """

  Scenario: Download a subject
    When I download the subject "numerical-methods" of "aeronautics"
    Then I get "Numerical methods.zip"
    And it has the files:
      | file                                        |
      | README.md                                   |
      | flashcards.csv                              |
      | flashcards.md                               |
      | 1 Finite elements/fem-notes.md              |
      | 2 Solvers/solvers.md                        |
    And "2 Solvers/solvers.md" in it is the material "solvers.md" as it is now
    And the zip isn't kept on the server once it is sent

  Scenario: The topics are numbered in the order they are read
    Given I have put the topics of "numerical-methods" of "aeronautics" in the order "solvers, finite-elements"
    When I download the subject "numerical-methods" of "aeronautics"
    Then it has the files:
      | file                                        |
      | README.md                                   |
      | flashcards.csv                              |
      | flashcards.md                               |
      | 1 Solvers/solvers.md                        |
      | 2 Finite elements/fem-notes.md              |

  Scenario: A Markdown material comes with its images
    Given I have added the image "figures/mesh.png" to "fem-notes.md"
    When I download the subject "numerical-methods" of "aeronautics"
    Then it has the file "1 Finite elements/fem-notes/figures/mesh.png"
    And "1 Finite elements/fem-notes/figures/mesh.png" in it is the image I added

  Scenario: A converted material comes with its original
    Given I have uploaded a PDF "beams.pdf" to "aeronautics/numerical-methods/solvers" with the pages:
      | page | text                    | outline  | level |
      | 1    | Beams bend under loads. | 1 Beams  | 1     |
    When I download the subject "numerical-methods" of "aeronautics"
    Then it has the file "2 Solvers/beams.md"
    And "2 Solvers/beams.pdf" in it is the file I uploaded as "beams.pdf"

  Scenario: My flashcards of the subject are in it
    Given I have asked for 2 flashcards of "fem-notes.md"
    And I have asked for 1 flashcard of "lift.md"
    When I download the subject "numerical-methods" of "aeronautics"
    Then flashcards.csv in it has 2 cards from "fem-notes.md"
    And flashcards.md in it has the cards of flashcards.csv

  Scenario: Only my own flashcards are in it
    Given I have shared the course "aeronautics" with "pedro" as a reader
    And the student "pedro" has asked for 2 flashcards of "fem-notes.md"
    When I download the subject "numerical-methods" of "aeronautics"
    Then flashcards.csv in it has no cards

  Scenario: A reader of the course downloads it
    Given I have shared the course "aeronautics" with "pedro" as a reader
    When the student "pedro" downloads the subject "numerical-methods" of "aeronautics"
    Then I get "Numerical methods.zip"

  Scenario: Someone the course isn't shared with can't
    When the student "pedro" downloads the subject "numerical-methods" of "aeronautics"
    Then the download is refused as not found

  Scenario: A subject there isn't
    When I download the subject "thermodynamics" of "aeronautics"
    Then the download is refused as not found

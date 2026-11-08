@ui
Feature: Downloading a subject as a zip in the browser
  As a student
  I want to download a subject from its page
  So that I keep a copy of its material and my flashcards

  A subject's page has "Download as zip" for everyone who can see it, which downloads the subject
  as "<subject>.zip" (see Downloading a subject as a zip).

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Meshing
      The domain is divided into triangles.
      """

  Scenario: Download a subject from its page
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I download the subject as a zip
    Then I get the zip "Numerical methods.zip" with "1 Finite elements/fem-notes.md"

  Scenario: A reader downloads it too
    Given I have shared the course "aeronautics" with "tom" as a reader
    And I am signed in as "tom"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I download the subject as a zip
    Then I get the zip "Numerical methods.zip" with "1 Finite elements/fem-notes.md"

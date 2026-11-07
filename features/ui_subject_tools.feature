@ui
Feature: The tools of a subject in the browser
  As a student who writes a course
  I want to choose a subject's tools as I lay out the course
  So that they are there, and only there, where its material is read and written

  "New subject" offers the tools there are, to attach any of them. A subject's page lists them,
  for its owners to change. Material of a subject without the Go compiler has no "Go" button, and
  its Go code blocks can't be opened in the Go editor.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "go-basics.md" to "go/programming/basics" with the content:
      """
      # 1 Hello

      ```go
      package main
      ```
      """

  Scenario: Attach a tool when creating a subject
    When I open the course "Go"
    And I create the subject "Concurrency" with the tool "Go compiler"
    And I open the subject "Concurrency"
    Then the tool "Go compiler" is attached

  Scenario: Without the tool there is no Go editor
    When I open the course "Go"
    And I open "go-basics.md" to read it
    Then I am not offered the Go editor

  Scenario: Attach a tool to a subject, then detach it
    When I open the course "Go"
    And I open the subject "Programming"
    And I attach the tool "Go compiler"
    And I open the course "Go"
    And I open "go-basics.md" to read it
    Then I am offered the Go editor
    When I open the course "Go"
    And I open the subject "Programming"
    And I detach the tool "Go compiler"
    And I open the course "Go"
    And I open "go-basics.md" to read it
    Then I am not offered the Go editor

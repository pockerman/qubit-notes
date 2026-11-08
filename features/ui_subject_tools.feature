@ui
Feature: The tools of a subject in the browser
  As a student who writes a course
  I want to choose a subject's tools as I lay out the course
  So that they are there, and only there, where its material is read and written

  "New subject" has a "Tools" section with the tools there are, to attach any of them to the
  subject's notes. A subject's page doesn't show them until its owners choose "Tools" there,
  to change them. The tools attached to a
  subject are in the "Tools" menu of its material, as it is read, edited or written, to open one
  beside it. Material of a subject without tools has no "Tools" menu, and its Go code blocks can't
  be opened in the Go editor.

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

  Scenario: "New subject" offers the tools to attach
    When I open the course "Go"
    And I start a new subject
    Then I can attach the tools "Go compiler,Python interpreter"

  Scenario: A subject's page shows its tools only when asked
    When I open the course "Go"
    And I open the subject "Programming"
    Then I don't see the subject's tools
    When I choose to see the subject's tools
    Then I can attach the tool "Go compiler"

  Scenario: The attached tools are in the Tools menu
    Given I have attached the tools "go" to the subject "programming" of "go"
    When I open the course "Go"
    And I open "go-basics.md" to read it
    Then the Tools menu has "Go compiler"
    When I choose "Go compiler" from the Tools menu
    Then I see the Go editor but not the assistant

  Scenario: The Tools menu is there while writing material
    Given I have attached the tools "go" to the subject "programming" of "go"
    When I open the course "Go"
    And I write material in the topic "Basics"
    Then the Tools menu has "Go compiler"

  Scenario: A subject with both tools has both in the Tools menu
    Given I have attached the tools "go,python" to the subject "programming" of "go"
    When I open the course "Go"
    And I open "go-basics.md" to read it
    Then the Tools menu has "Go compiler,Python interpreter"
    When I choose "Python interpreter" from the Tools menu
    Then I see the Python editor but not the assistant

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

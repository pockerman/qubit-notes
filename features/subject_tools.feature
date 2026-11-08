Feature: The tools of a subject
  As a student who writes a course
  I want to attach tools to a subject
  So that its material comes with what it takes to try it out

  A tool, a compiler or an interpreter, is attached to a subject when it is created, or by its
  owners afterwards. The app has the Go compiler ("go"), the Python interpreter ("python"), the
  C++ compiler ("cpp") and the SQL interpreter ("sql"). A subject has no tools unless they are attached,
  and they go with the subject when it is deleted. Everyone who can see the subject sees its tools;
  only the owners of the course change them. A tool appears where the subject's material is read,
  edited and written (see The Go editor in the browser, The Python editor in the browser, The C++ and SQL editors
  in the browser).

  Background:
    Given I am the student "maria"
    And I have created the course "languages"

  Scenario: The tools there are
    Then the app offers the tools "go,python,cpp,sql"

  Scenario: Create a subject with a tool
    When I create the subject "Programming in Go" in "languages" with the tools "go"
    Then the subject "programming-in-go" of "languages" has the tools "go"

  Scenario: A subject has no tools unless they are attached
    When I create the subject "History" in "languages"
    Then the subject "history" of "languages" has no tools

  Scenario: A tool the app doesn't have
    When I create the subject "Fortran" in "languages" with the tools "punched-cards"
    Then I am told there is no tool "punched-cards"
    And the course "languages" has no subjects

  Scenario: Attach a tool to a subject afterwards
    Given I have created the subject "Programming in Go" in "languages"
    When I attach the tools "go" to the subject "programming-in-go" of "languages"
    Then the subject "programming-in-go" of "languages" has the tools "go"

  Scenario: Attach a tool to a subject made by uploading to it
    Given I have uploaded "notes.md" to "languages/programming/basics"
    When I attach the tools "go" to the subject "programming" of "languages"
    Then the subject "programming" of "languages" has the tools "go"

  Scenario: Remove a tool from a subject
    Given I have created the subject "Programming in Go" in "languages"
    And I have attached the tools "go" to the subject "programming-in-go" of "languages"
    When I attach no tools to the subject "programming-in-go" of "languages"
    Then the subject "programming-in-go" of "languages" has no tools

  Scenario: A subject the course doesn't have
    When I attach the tools "go" to the subject "nothing" of "languages"
    Then I am told there is no subject "nothing"

  Scenario: Readers see a subject's tools, and don't change them
    Given I have created the subject "Programming in Go" in "languages"
    And I have attached the tools "go" to the subject "programming-in-go" of "languages"
    And I have shared the course "languages" with "tom" as a reader
    Then the student "tom" sees the tools "go" of the subject "programming-in-go" of "languages"
    When the student "tom" attaches no tools to the subject "programming-in-go" of "languages"
    Then they are not allowed to
    And the subject "programming-in-go" of "languages" has the tools "go"

  Scenario: A subject's tools go with it
    Given I have created the subject "Programming in Go" in "languages"
    And I have attached the tools "go" to the subject "programming-in-go" of "languages"
    When I delete the subject "programming-in-go" from "languages"
    And I create the subject "Programming in Go" in "languages"
    Then the subject "programming-in-go" of "languages" has no tools

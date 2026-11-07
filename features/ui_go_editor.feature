@ui
Feature: The Go editor in the browser
  As a student of Go
  I want to run Go beside the notes I am reading
  So that I can try things out without leaving them

  Where the Go compiler is attached to a subject (see The tools of a subject), its material has a
  "Go" button next to "Edit", "Download" and "AI", also while it is edited or written, which opens
  the Go editor beside the text, in the place of the notes or the assistant, with a small program
  to start from. "Run", or Ctrl+Enter,
  runs what is in it, and what it printed is shown below as it was printed, whatever it says. A Go
  code block in a material has "Open in the Go editor", which puts its code there. What is typed
  stays in the editor while the material is open, when the editor is closed and opened again.

  Background:
    Given I am signed in as "maria"
    And the app can run Go programs
    And I have uploaded "go-basics.md" to "go/programming/basics" with the content:
      """
      # 1 Hello
      A first program:

      ```go
      package main

      import "fmt"

      func main() {
        fmt.Println("hello from the notes")
      }
      ```

      Some other code:

      ```python
      print("not Go")
      ```
      """
    And I have attached the tools "go" to the subject "programming" of "go"
    When I open the course "Go"
    And I open "go-basics.md" to read it

  Scenario: Write a program and run it
    When I open the Go editor
    Then the Go editor has a program to start from
    When I write the Go program:
      """
      package main

      import "fmt"

      func main() {
        fmt.Println("<b>typed</b>")
      }
      """
    And I run it
    Then I see the program printed "<b>typed</b>"

  Scenario: Run with the keyboard
    When I open the Go editor
    And I press Ctrl+Enter in the Go editor
    Then I see the program printed "hello, world"

  Scenario: Open a code block in the Go editor
    Then only the Go code block can be opened in the Go editor
    When I open the code block in the Go editor
    And I run it
    Then I see the program printed "hello from the notes"

  Scenario: A program that doesn't compile
    When I open the Go editor
    And I write the Go program:
      """
      package main

      func main() {
        undefined()
      }
      """
    And I run it
    Then I see the program printed "undefined: undefined"
    And I am told it ended with exit code 1

  Scenario: The editor keeps what I typed
    When I open the Go editor
    And I write the Go program:
      """
      package main // mine
      """
    And I close the Go editor
    And I open the Go editor
    Then the Go editor has "package main // mine"

  Scenario: The editor takes the place of the assistant
    When I open the assistant
    And I open the Go editor
    Then I see the Go editor but not the assistant

  Scenario: The Go editor beside the material being edited
    When I edit the material, typing "A new first line"
    And I open the Go editor
    And I run it
    Then I see the program printed "hello, world"
    And the text being edited still has "A new first line"

  Scenario: The Go editor beside the material being written
    When I open the course "Go"
    And I write material in the topic "Basics"
    And I type:
      """
      # 1 Goroutines
      """
    And I open the Go editor
    And I run it
    Then I see the program printed "hello, world"

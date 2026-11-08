@ui
Feature: The Python editor in the browser
  As a student of Python
  I want to run Python beside the notes I am reading
  So that I can try things out without leaving them

  Where the Python interpreter is attached to a subject (see The tools of a subject), "Python
  interpreter" is in the "Tools" menu of its material, also while it is edited or written, and
  opens the Python editor beside the text, as the Go editor is opened (see The Go editor in the
  browser), with a small program to start from. "Run", or Ctrl+Enter, runs what is in it, and what
  it printed is shown below. Tab indents by four spaces. A Python code block ("python" or "py") has
  "Open in the Python editor", which puts its code there. What is typed stays in the editor while
  the material is open.

  Background:
    Given I am signed in as "maria"
    And the app can run Python programs
    And I have uploaded "python-basics.md" to "python/programming/basics" with the content:
      """
      # 1 Hello
      A first program:

      ```python
      print("hello from the notes")
      ```

      Some other code:

      ```go
      package main
      ```
      """
    And I have attached the tools "python" to the subject "programming" of "python"
    When I open the course "Python"
    And I open "python-basics.md" to read it

  Scenario: Write a program and run it
    When I open the Python editor
    Then the Python editor has a program to start from
    When I write the Python program:
      """
      print("<b>typed</b>")
      """
    And I run it
    Then I see the program printed "<b>typed</b>"

  Scenario: Run with the keyboard
    When I open the Python editor
    And I press Ctrl+Enter in the Python editor
    Then I see the program printed "hello, world"

  Scenario: Open a code block in the Python editor
    Then only the Python code block can be opened in the Python editor
    When I open the code block in the Python editor
    And I run it
    Then I see the program printed "hello from the notes"

  Scenario: A program that fails
    When I open the Python editor
    And I write the Python program:
      """
      undefined()
      """
    And I run it
    Then I see the program printed "NameError"
    And I am told it ended with exit code 1

  Scenario: The editor keeps what I typed
    When I open the Python editor
    And I write the Python program:
      """
      print("mine")
      """
    And I close the Python editor
    And I open the Python editor
    Then the Python editor has "print("mine")"

  Scenario: Tab indents by four spaces
    When I open the Python editor
    And I write the Python program:
      """
      if True:
      """
    And I press Tab at the end of the Python program
    Then the Python editor has "if True:    "

  Scenario: The Python editor beside the material being edited
    When I edit the material, typing "A new first line"
    And I open the Python editor
    And I run it
    Then I see the program printed "hello, world"
    And the text being edited still has "A new first line"

  Scenario: The Python editor beside the material being written
    When I open the course "Python"
    And I write material in the topic "Basics"
    And I type:
      """
      # 1 Lists
      """
    And I open the Python editor
    And I run it
    Then I see the program printed "hello, world"

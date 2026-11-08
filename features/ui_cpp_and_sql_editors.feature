@ui
Feature: The C++ and SQL editors in the browser
  As a student of C++ or of databases
  I want to run C++ and SQL beside the notes I am reading
  So that I can try things out without leaving them

  Where the C++ compiler or the SQL interpreter is attached to a subject (see The tools of a
  subject), it is in the "Tools" menu of its material and opens its editor beside the text, as the
  Go editor is opened (see The Go editor in the browser), with a small program to start from. A C++
  code block ("cpp", "c++", "cxx", "cc") has "Open in the C++ editor", and an SQL one ("sql",
  "sqlite") "Open in the SQL editor". Each editor keeps what is typed in it while the material is
  open.

  Background:
    Given I am signed in as "maria"
    And the app can run C++ programs
    And the app can run SQL programs
    And I have uploaded "systems.md" to "systems/programming/basics" with the content:
      """
      # 1 Hello
      A first program:

      ```cpp
      #include <iostream>
      int main() { std::cout << "hello from the notes" << std::endl; }
      ```

      A first query:

      ```sql
      SELECT 'rows from the notes';
      ```
      """
    And I have attached the tools "cpp,sql" to the subject "programming" of "systems"
    When I open the course "Systems"
    And I open "systems.md" to read it

  Scenario: Both are in the Tools menu
    Then the Tools menu has "C++ compiler,SQL interpreter"

  Scenario: Write a C++ program and run it
    When I open the C++ editor
    Then the C++ editor has a program to start from
    When I press Ctrl+Enter in the C++ editor
    Then I see the program printed "hello, world"

  Scenario: A C++ program that doesn't compile
    When I open the C++ editor
    And I write the C++ program:
      """
      int main() { undefined(); }
      """
    And I run it
    Then I see the program printed "was not declared in this scope"
    And I am told it ended with exit code 1

  Scenario: Open a C++ code block in the C++ editor
    When I open the code block in the C++ editor
    And I run it
    Then I see the program printed "hello from the notes"

  Scenario: Write SQL and run it
    When I open the SQL editor
    Then the SQL editor has a program to start from
    When I write the SQL program:
      """
      SELECT 'typed';
      """
    And I run it
    Then I see the program printed "typed"

  Scenario: Open an SQL code block in the SQL editor
    When I open the code block in the SQL editor
    And I run it
    Then I see the program printed "rows from the notes"

  Scenario: Each editor keeps what was typed in it
    When I open the C++ editor
    And I write the C++ program:
      """
      // mine
      """
    And I open the SQL editor
    And I write the SQL program:
      """
      -- mine
      """
    And I open the C++ editor
    Then the C++ editor has "// mine"

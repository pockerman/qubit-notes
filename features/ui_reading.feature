@ui
Feature: Reading material in the browser
  As a student
  I want to read my material section by section on screen
  So that I can study without leaving the assistant

  Scenario: Open a material and read a section
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.

      ## 2.1 Linear elements
      A linear element interpolates linearly between its two nodes.
      """
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    Then I see its sections "1 Introduction, 2 Shape functions, 2.1 Linear elements"
    And I see the text "The finite element method divides a domain into small elements."
    When I choose the section "2.1 Linear elements"
    Then I see the text "A linear element interpolates linearly between its two nodes."

  Scenario: The text takes most of the page
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    And my screen is 1440 pixels wide
    When I open the course "aeronautics"
    And I open "fem-notes.md" to read it
    Then the text is at least 60% of the page wide

  Scenario: Markdown is shown formatted
    Given I am signed in as "maria"
    And I have uploaded "building-blocks.md" to "computer-science/distributed-systems/introduction" with the content:
      """
      # Building blocks
      The **main** building blocks, and the pillar each one serves:

      | Building block | Main pillar | Course lesson                                     |
      |----------------|-------------|---------------------------------------------------|
      | Load balancer  | Scalability | [Load balancing](https://example.org/load-balancing) |
      | Message queue  | Reliability | [Messaging](https://example.org/messaging)          |

      ```
      ip addr show
      ```
      """
    When I open the course "computer-science"
    And I open "building-blocks.md" to read it
    Then I see a table with the columns "Building block, Main pillar, Course lesson"
    And the table has the rows:
      | Building block | Main pillar | Course lesson  |
      | Load balancer  | Scalability | Load balancing |
      | Message queue  | Reliability | Messaging      |
    And "Load balancing" links to "https://example.org/load-balancing"
    And "main" is in bold
    And "ip addr show" is shown as code

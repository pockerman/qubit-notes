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
    When I open the course "Aeronautics"
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
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    Then the text is at least 60% of the page wide

  Scenario: Mathematics in LaTeX is typeset
    Given I am signed in as "maria"
    And I have uploaded "speed-up.md" to "computer-science/parallel-computing/performance" with the content:
      """
      # Efficiency
      The efficiency of $p$ processors is $E_p = \frac{S_p}{p}$, where the speed-up is

      $$
      S_p = \frac{T_1}{T_p}
      $$

      $$E_p = \frac{S_p}{p}$$

      A licence costs $5, or $10 with support.
      """
    When I open the course "Computer science"
    And I open "speed-up.md" to read it
    Then "E_p = \frac{S_p}{p}" is typeset as mathematics, in the text
    And "S_p = \frac{T_1}{T_p}" is typeset as mathematics, on a line of its own
    And "E_p = \frac{S_p}{p}" is typeset as mathematics, on a line of its own
    And I see the text "A licence costs $5, or $10 with support."

  Scenario: Mathematics that isn't valid LaTeX is shown as written
    Given I am signed in as "maria"
    And I have uploaded "typo.md" to "computer-science/parallel-computing/performance" with the content:
      """
      The speed-up is $S_p = \frac{T_1}{T_p$.
      """
    When I open the course "Computer science"
    And I open "typo.md" to read it
    Then I see "S_p = \frac{T_1}{T_p" as written, marked as mathematics that could not be typeset

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
    When I open the course "Computer science"
    And I open "building-blocks.md" to read it
    Then I see a table with the columns "Building block, Main pillar, Course lesson"
    And the table has the rows:
      | Building block | Main pillar | Course lesson  |
      | Load balancer  | Scalability | Load balancing |
      | Message queue  | Reliability | Messaging      |
    And "Load balancing" links to "https://example.org/load-balancing"
    And "main" is in bold
    And "ip addr show" is shown as code

  Scenario: Code is shown as written, comments and all
    Given I am signed in as "maria"
    And I have uploaded "load-balancing.md" to "computer-science/distributed-systems/introduction" with the content:
      """
      # Load balancing
      A ```Service``` of type `LoadBalancer`:

      ```yaml
      # load-balancer.yaml
      #   kubectl apply -f load-balancer.yaml
      kind: Service
      ```
      """
    When I open the course "Computer science"
    And I open "load-balancing.md" to read it
    Then "# load-balancer.yaml" is shown as code
    And "kind: Service" is shown as code
    And "Service" is shown as code in the text
    And "LoadBalancer" is shown as code in the text

  Scenario: Links written in HTML are links
    Given I am signed in as "maria"
    And I have uploaded "circuits.md" to "computer-science/distributed-systems/introduction" with the content:
      """
      # Circuits
      Read about <a href="https://example.org/breadboard">breadboards</a> and <a href='https://example.org/ohm'>**Ohm's** law</a>.
      Not this one: <a href="javascript:alert(1)">trap</a>.
      """
    When I open the course "Computer science"
    And I open "circuits.md" to read it
    Then "breadboards" links to "https://example.org/breadboard"
    And "Ohm's law" links to "https://example.org/ohm"
    And "trap" is shown, but not as a link

  Scenario: Go on to the next topic, and back
    Given I am signed in as "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "fe-assembly.txt" to "aeronautics/numerical-methods/finite-elements"
    And I have uploaded "fv-basics.txt" to "aeronautics/numerical-methods/finite-volumes"
    When I open the course "Aeronautics"
    And I open "fe-assembly.txt" to read it
    Then the next topic is shown as "Finite volumes"
    And I am not offered a previous topic
    When I go to the next topic
    Then I am reading "fv-basics.txt"
    And the previous topic is shown as "Finite elements"
    And I am not offered a next topic
    When I go to the previous topic
    Then I am reading "fe-basics.txt"

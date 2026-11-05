@ui
Feature: The AI's usage in the browser
  As a student of qubit-notes, or an admin paying for its AI
  I want to see how many tokens the AI has used
  So that I know what it costs without looking in the database

  "Usage", under "Settings" in the app's menu, shows the tokens the student has used over the last
  30 days, in all and by what they were used on. Admins also see each student's.

  Background:
    Given I am signed in as "maria"
    And the AI uses 1000 input tokens and 200 output tokens each time
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    And I have asked the AI for a summary

  Scenario: A student sees their usage
    When I choose "Settings › Usage" from the menu
    Then I see I have used "1,200" tokens
    And I see "Summaries" used "1,200" tokens
    And I don't see the usage of each student

  Scenario: An admin sees each student's usage
    Given "alex" is an admin of qubit-notes
    And I am signed in as "alex"
    When I choose "Settings › Usage" from the menu
    Then I see the student "maria" used "1,200" tokens

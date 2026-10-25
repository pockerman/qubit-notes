@ui
Feature: My account in the browser
  As a student
  I want a view of my account under Settings
  So that I change my email or password in a few clicks

  "Settings" in the app's menu opens a submenu of its views: "AI model" (see Settings in the
  browser) and "Account". Account shows the student's email, with a form to change it, which then
  asks for the code Cognito emails, and a form to change their password, which asks for the
  current one, and the new one twice (see My account). Signed in by name, Account says there is
  no email or password to change.

  @cognito
  Scenario: Change my password
    Given the app signs students in with Cognito
    And Cognito has the user "maria" with the email "maria@example.com" and the password "Old-password-1"
    And I have signed in to the app with Cognito as "maria"
    When I choose "Settings › Account" from the menu
    And I change my password from "Old-password-1" to "New-password-2" in my account
    Then I am told my password is changed
    And Cognito takes "New-password-2" as the password of "maria"

  @cognito
  Scenario: The new password, twice
    Given the app signs students in with Cognito
    And Cognito has the user "maria" with the email "maria@example.com" and the password "Old-password-1"
    And I have signed in to the app with Cognito as "maria"
    When I choose "Settings › Account" from the menu
    And I give my new password as "New-password-2", then "New-password-3"
    Then I am told the new passwords are not the same
    And Cognito takes "Old-password-1" as the password of "maria"

  @cognito
  Scenario: Change my email
    Given the app signs students in with Cognito
    And Cognito has the user "maria" with the email "maria@example.com" and the password "Old-password-1"
    And I have signed in to the app with Cognito as "maria"
    When I choose "Settings › Account" from the menu
    Then I see my email is "maria@example.com"
    When I change my email to "maria@uni.example" in my account
    And I enter the code Cognito sent
    Then I see my email is "maria@uni.example"

  Scenario: Signed in by name, there is nothing to change
    Given I am signed in as "maria"
    When I choose "Settings › Account" from the menu
    Then I am told I sign in by name, with no email or password to change
    And I am not offered to change my email or password

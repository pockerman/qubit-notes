@cognito
Feature: My account
  As a student
  I want to change my email and my password from the app
  So that I keep my account up to date without asking an admin

  Where students sign in with Cognito (see Signing in with Amazon Cognito), their email and
  password are their Cognito account's. The app shows a student their email, and changes it or
  their password through Cognito, with the token they signed in with; it never keeps either.
  A new password needs the current one, and Cognito checks it against the user pool's rules, e.g.
  at least 12 characters. A new email is used once the student confirms it with the code Cognito
  emails to it; until then they keep the one they had. Run without Cognito, students sign in by
  name, so there is no email or password to change (see My account in the browser).

  Background:
    Given the app signs students in with Cognito
    And Cognito has the user "maria" with the email "maria@example.com" and the password "Old-password-1"
    And I have signed in with Cognito as "maria"

  Scenario: My email
    When I look at my account
    Then I am told my email is "maria@example.com"

  Scenario: Change my password
    When I change my password from "Old-password-1" to "New-password-2"
    Then Cognito takes "New-password-2" as the password of "maria"

  Scenario: The current password is needed
    When I change my password from "Wrong-password-1" to "New-password-2"
    Then I am told my current password is not right
    And Cognito takes "Old-password-1" as the password of "maria"

  Scenario: A new password meets the user pool's rules
    When I change my password from "Old-password-1" to "short"
    Then I am told the new password does not meet the rules for passwords
    And Cognito takes "Old-password-1" as the password of "maria"

  Scenario: Change my email, once I confirm it
    When I change my email to "maria@uni.example"
    Then I am told to enter the code sent to "maria@uni.example"
    And I am told my email is "maria@example.com"
    When I confirm my email with the code Cognito sent
    Then I am told my email is "maria@uni.example"

  Scenario: A wrong code
    Given I have changed my email to "maria@uni.example"
    When I confirm my email with the code "000000"
    Then I am told the code is not right
    And I am told my email is "maria@example.com"


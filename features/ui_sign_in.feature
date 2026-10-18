@ui @cognito
Feature: Signing in with Amazon Cognito in the browser
  As a student
  I want to sign in once with my Cognito account
  So that I study without saying who I am again

  The tests stand in for Cognito with a sign-in page of their own that works as Cognito's does.

  Background:
    Given the app signs students in with Cognito
    And Cognito has the user "maria"

  Scenario: Sign in with Cognito
    When I open the app
    Then I am sent to sign in with Cognito
    When I sign in to Cognito as "maria"
    Then I am back in the app, signed in as "maria"

  Scenario: Sign out
    Given I have signed in to the app with Cognito as "maria"
    When I sign out
    Then I am sent to sign in with Cognito

@cognito
Feature: Signing in with Amazon Cognito
  As a student
  I want only me to be able to act as me
  So that my courses, notes and quizzes are mine and those I share them with

  Where qubit-notes is deployed, students sign in with Amazon Cognito: the browser is sent to
  Cognito's sign-in page and comes back with an access token, which goes with every request.
  The app checks the token: signed by the app's user pool, issued to the app, an access token,
  and not expired. The student is the Cognito username in the token, so they share courses with
  each other by username.

  Run without Cognito, as in development and these tests by default, a student says who they
  are by name, as before.

  Background:
    Given the app signs students in with Cognito

  Scenario: A student is who their token says
    Given I have signed in with Cognito as "maria"
    When I create the course "aeronautics"
    Then the course "aeronautics" is created by "maria"

  Scenario: Saying who you are is not enough
    When I say I am "maria" without a token
    Then I am asked to sign in

  Scenario Outline: Tokens that are not accepted
    Given I have a Cognito token for "maria" that is <problem>
    When I list my courses with it
    Then I am asked to sign in

    Examples:
      | problem                          |
      | expired                          |
      | signed by another key            |
      | from another user pool           |
      | issued to another app            |
      | an ID token, not an access token |

  Scenario: A video is played with the token in its link
    Given I have signed in with Cognito as "maria"
    And I have uploaded the video "lecture-1.mp4" to "aeronautics/numerical-methods/finite-elements"
    When I play "lecture-1.mp4" with my token in its link
    Then I get the video

  Scenario: A video's link does not play without a token
    Given I have signed in with Cognito as "maria"
    And I have uploaded the video "lecture-1.mp4" to "aeronautics/numerical-methods/finite-elements"
    When I play "lecture-1.mp4" with only my name in its link
    Then I am asked to sign in

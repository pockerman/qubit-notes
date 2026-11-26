@ui
Feature: Pushing a subject to a repository in the browser
  As a student
  I want to connect a subject to my GitHub repository and push it from the subject's page
  So that keeping my work in Git is a click, not a call of the app's API

  A subject's page has "Repository" for everyone who can see it, owners and readers alike, next to
  "Download as zip". It opens the subject's repository, as the student sees it (see Pushing a
  subject to a repository):

  - A subject that isn't connected asks for the repository, as "owner/name", and a token that may
    write to it, with a link to where GitHub gives fine-grained tokens. "Connect" connects it; if
    the app refuses, it says why, and what was typed stays, except the token.
  - A connected subject shows its repository, as a link to it on GitHub, and when it was last
    pushed, as a link to that commit, or "Never pushed". The token is never shown, not even in
    part. "Push" pushes the subject; while it pushes, it says "Pushing…" and can't be pushed
    again. It then says how many files the push wrote and removed, with a link to the commit, or
    that there was nothing new to push.
  - "Disconnect" asks first, saying the repository is left as it is, then disconnects the subject.

  The panel closes with its ✕, or with "Repository" again.

  Background:
    Given I am signed in as "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    And GitHub has the repository "maria/numerical-methods", which the token "maria-token" may write to

  Scenario: Connect a subject from its page
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    Then I am asked for a repository and a token that may write to it
    When I connect it to "maria/numerical-methods" with the token "maria-token"
    Then I see the subject is connected to "maria/numerical-methods", which links to it on GitHub
    And I see it has never been pushed
    And I am not shown "maria-token" on the page

  Scenario: Close the subject's repository with its ✕
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I close the subject's repository
    Then I don't see the subject's repository

  Scenario: A token that can't write is refused, and what I typed stays
    Given GitHub has the repository "maria/old-notes", which the token "maria-token" may only read
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I connect it to "maria/old-notes" with the token "maria-token"
    Then I am told the token may not write to "maria/old-notes"
    And the repository is still filled in as "maria/old-notes", and the token is empty
    And the subject "numerical-methods" of "aeronautics" is not connected

  Scenario: Without the app's secret, I am told why a subject can't be connected
    Given qubit-notes is running without a secret key
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I connect it to "maria/numerical-methods" with the token "maria-token"
    Then I am told the app can't keep the token without its secret

  Scenario: Push a connected subject
    Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
    And I have noted "compare with Galerkin's method" on "divides a domain into small elements" in "1 Introduction" of "fem-notes.md"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I push the subject
    Then I am told the push wrote 3 files, with a link to its commit
    And I see it was last pushed just now, as a link to that commit
    And "maria/numerical-methods" has one new commit on its default branch

  Scenario: Nothing new to push
    Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
    And I have pushed the subject "numerical-methods" of "aeronautics"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I push the subject
    Then I am told there is nothing new to push
    And "maria/numerical-methods" has no new commit

  Scenario: A push removes the files of what I deleted, and says so
    Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
    And I have noted "compare with Galerkin's method" on "divides a domain into small elements" in "1 Introduction" of "fem-notes.md"
    And I have pushed the subject "numerical-methods" of "aeronautics"
    And I have deleted the material "fem-notes.md"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I push the subject
    Then I am told the push wrote 1 file and removed 2, with a link to its commit

  Scenario: A push GitHub refuses says why
    Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
    And GitHub no longer lets the token "maria-token" write to "maria/numerical-methods"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I push the subject
    Then I am told GitHub refused the push: the token may not write to "maria/numerical-methods"
    And I see it has never been pushed

  Scenario: Disconnect a subject, after saying yes
    Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    And I disconnect the subject
    Then I am asked to confirm, and told "maria/numerical-methods" is left as it is
    When I confirm
    Then I am asked for a repository and a token that may write to it
    And the subject "numerical-methods" of "aeronautics" is not connected

  Scenario: A reader connects and pushes to their own repository
    Given I have shared the course "aeronautics" with "pedro" as a reader
    And GitHub has the repository "pedro/numerical-methods", which the token "pedro-token" may write to
    And I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
    And I am signed in as "pedro"
    When I open the course "Aeronautics"
    And I open the subject "Numerical methods"
    And I open the subject's repository
    Then I am asked for a repository and a token that may write to it
    When I connect it to "pedro/numerical-methods" with the token "pedro-token"
    And I push the subject
    Then "pedro/numerical-methods" has one new commit on its default branch
    And "maria/numerical-methods" has no new commit

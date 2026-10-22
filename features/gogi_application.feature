Feature: The app as an application of gogi
  As someone running qubit-notes
  I want it to use gogi as one of gogi's applications, with its own key
  So that its courses, notes and AI calls are its own on a gogi that serves other applications too

  Where gogi serves many applications, the app is registered with gogi by gogi's operator
  (gogi-admin register qubit-notes) and run with the key it is given
  (QUBIT_NOTES_GOGI_API_KEY); every call the app makes to gogi carries it. Where gogi has a
  certificate authority of its own, as without a domain, the app is given its certificate
  (QUBIT_NOTES_GOGI_CA_FILE). The app's summaries, quizzes and answers are written with its
  own Anthropic key, which is stored in gogi once, as the app's credential "anthropic":

    qubit-notes store-provider-key anthropic   (the key is read from standard input)

  Run against a gogi without keys, as in development, the app needs no key.

  @platform @gogi_keys
  Scenario: The app works as an application of gogi
    Given gogi requires keys and the app runs with the key of the application "qubit-notes"
    And I am the student "maria"
    When I create the course "aeronautics"
    And I upload the file "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    Then the materials of "aeronautics/numerical-methods/finite-elements" are:
      | filename      |
      | fe-basics.txt |
    And another application of gogi does not see the course "aeronautics" of "maria"

  @platform @gogi_keys
  Scenario: The app's Anthropic key is stored in gogi as the app's own
    Given gogi requires keys and the app runs with the key of the application "qubit-notes"
    When the app's Anthropic key is stored
    Then gogi has the credential "anthropic" of "qubit-notes", without showing its value

  @platform @gogi_wrong_key
  Scenario: The health check tells when gogi does not take the app's key
    Given gogi requires keys and the app runs with a key gogi did not give
    When I check its health
    Then it reports that it is degraded
    And it reports that gogi does not take the app's key

  Scenario: The health check tells when the platform does not take the app's key
    Given qubit-notes is running
    And the platform does not take the app's key
    When I check its health
    Then it reports that it is degraded
    And it reports that gogi does not take the app's key

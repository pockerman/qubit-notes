Feature: The app on its own
  As someone running qubit-notes
  I want it to need nothing but its own database, a place for files and a model provider
  So that it can be run and deployed without the gogi platform

  By default (QUBIT_NOTES_PLATFORM=standalone) the app is its own platform:
  - it keeps the uploaded files on disk (QUBIT_NOTES_FILES_DIR), or in an S3 bucket
    (QUBIT_NOTES_FILES_BUCKET) where it's deployed;
  - it reads each document into its sections, divides them into chunks and embeds them, in the
    background, and keeps the chunks in its own database: with pgvector on Postgres, in a plain
    table on SQLite;
  - it keeps the conversations with the assistant and what the assistant remembers in its own
    database too;
  - it calls the model provider (QUBIT_NOTES_LLM_PROVIDER, anthropic or openai) itself, with the
    key it is given (QUBIT_NOTES_ANTHROPIC_API_KEY, QUBIT_NOTES_OPENAI_API_KEY), and the model
    QUBIT_NOTES_LLM_MODEL names, or the one its admins choose in the app (see The AI's model).

  What the app is missing is said in plain words, e.g. "the app is missing its Anthropic key",
  where students may see it: the health check names a missing key by its provider, not by the
  setting that holds it.

  Material is embedded with the model QUBIT_NOTES_EMBEDDING_MODEL names:
    | model                  | runs                      | needs                       |
    | bge-small-en-v1.5      | in the app (the default)  | nothing                     |
    | all-minilm-l6-v2       | in the app                | nothing                     |
    | voyage-3.5-lite        | at Voyage AI              | QUBIT_NOTES_VOYAGE_API_KEY  |
    | text-embedding-3-small | at OpenAI                 | QUBIT_NOTES_OPENAI_API_KEY  |
  Material embedded with one model is found only by searching with the same model, so changing
  the model means embedding the material again (qubit-notes reembed).

  QUBIT_NOTES_PLATFORM=gogi uses gogi instead, as before (see The app as an application of gogi);
  gogi-python is then installed beside the app (make install-gogi): it isn't one of the app's
  dependencies, so the app builds and runs without it.

  Scenarios tagged @platform run against the app's own platform with --platform=standalone, where
  the AI is a stand-in unless --with-ai is given, and against gogi with --platform=gogi.

  @standalone
  Scenario: The health check reports the app's own parts
    Given qubit-notes is running on its own
    When I check its health
    Then it reports that it is healthy
    And it reports "database", "files", "embeddings" and "ai" as serving

  @standalone
  Scenario: The health check tells when the app has no key for its model provider
    Given qubit-notes is running on its own, without a key for its model provider
    When I check its health
    Then it reports that it is degraded
    And it reports "ai" as not serving
    And it reports the key of "anthropic" as missing
    And nothing it reports names a setting

  @standalone
  Scenario Outline: Material is found with the embedding model the app uses
    Given qubit-notes is running on its own, embedding material with "<model>"
    And I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Assembly
      The element matrices are assembled into the global stiffness matrix.
      """
    When the course "aeronautics" is searched for "how are the element matrices combined"
    Then the first passage found is from the section "2 Assembly" of "fem-notes.md"

    Examples:
      | model             |
      | bge-small-en-v1.5 |
      | all-minilm-l6-v2  |

    @embedding_keys
    Examples:
      | model                  |
      | voyage-3.5-lite        |
      | text-embedding-3-small |

  @standalone
  Scenario: Material is not found by searching with another embedding model
    Given qubit-notes is running on its own, embedding material with "bge-small-en-v1.5"
    And I am the student "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      The finite element method divides a domain into small elements.
      """
    When the app is restarted, embedding material with "all-minilm-l6-v2"
    And the course "aeronautics" is searched for "finite elements"
    Then no passage is found
    When the material is embedded again
    And the course "aeronautics" is searched for "finite elements"
    Then the first passage found is from "fe-basics.txt"

  @standalone
  Scenario: Material and conversations outlast a restart of the app
    Given qubit-notes is running on its own
    And I am the student "maria"
    And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      The finite element method divides a domain into small elements.
      """
    When the app is restarted
    Then the materials of "aeronautics/numerical-methods/finite-elements" are:
      | filename      |
      | fe-basics.txt |
    And I can download "fe-basics.txt" as it was uploaded
    And the course "aeronautics" is searched for "finite elements" with "fe-basics.txt" first

  @standalone
  Scenario: An ingestion a restart interrupted finishes after it
    Given qubit-notes is running on its own
    And I am the student "maria"
    And the app stops before it has processed what is uploaded
    When I upload the file "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
    And the app is restarted
    Then the material "fe-basics.txt" is eventually ready

  @standalone
  Scenario: Provider keys are the app's settings, not stored in a platform
    Given qubit-notes is running on its own
    When the app's Anthropic key is stored
    Then the app says to set QUBIT_NOTES_ANTHROPIC_API_KEY instead

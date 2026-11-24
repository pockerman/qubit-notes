@ai
Feature: Prompt versions
  As the maintainer of qubit-notes
  I want every prompt the app gives the AI to have numbered versions, recorded with what they produce
  So that a change to a prompt can be compared with the version before it, measured, and rolled back

  Each prompt the app gives the AI is a folder of prompts/ with a file for each of its versions,
  v1.md, v2.md, …, and a prompt.toml that names the version in use, e.g. active = 2. These are
  the prompts:

    | prompt              | for                                     |
    | study-assistant     | whatever a student asks the assistant   |
    | summaries           | a summary                               |
    | quiz                | a quiz                                  |
    | flashcards          | a deck of flashcards                    |
    | generating          | material generated from a topic's       |
    | comprehension-check | a check of a student's understanding    |
    | audio-narration     | the narration of a material's audio     |
    | writing-assistant   | the writing assistant's replies         |

  A prompt is changed by adding a version, and the version in use is changed by naming it in
  prompt.toml. A version once released never changes: prompts/versions.lock has the SHA-256 of
  every released version, and the app's checks fail if a released version's file differs from it,
  or if a version isn't in it yet. `qubit-notes prompts lock` adds the new versions to it; nothing
  else changes it.

  The version a prompt is used at is recorded with everything it produces: in its trace (see
  Tracing the AI), as the prompt's name and version, e.g. "quiz" v2, with the SHA-256 of its text;
  and with what is saved of it: a summary, a quiz, a deck of flashcards, generated material, a
  reply of the assistant or of the writing assistant, a check of understanding and the audio of a
  material are each kept with the version of the prompt they were written with.

  The app's admins (see The app's keys, set by its admins) see every prompt, its versions and the
  version in use, read each version, and compare two versions, line by line. They can choose
  another version of a prompt from the app, e.g. to roll back a change that made it worse: the
  choice is kept in the app's database and used from then on, for everyone, and again when the app
  restarts, rather than prompt.toml's, until they choose prompt.toml's again.

  Background:
    Given "alex" is an admin of qubit-notes
    And the prompt "quiz" has the versions 1 and 2, with 2 in use
    And I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """

  Rule: Each prompt has numbered versions, one of them in use

    Scenario Outline: Every prompt the app uses has a version in use
      Then the prompt "<prompt>" has a version in use, which is released

      Examples:
        | prompt              |
        | study-assistant     |
        | summaries           |
        | quiz                |
        | flashcards          |
        | generating          |
        | comprehension-check |
        | audio-narration     |
        | writing-assistant   |

    Scenario: The AI is given the version in use
      When I ask the AI for a quiz
      Then the AI was given the version 2 of the prompt "quiz"

    Scenario: Naming another version in prompt.toml uses it
      Given prompt.toml of "quiz" names the version 1
      When I ask the AI for a quiz
      Then the AI was given the version 1 of the prompt "quiz"

    Scenario: A prompt.toml naming a version that doesn't exist is refused
      Given prompt.toml of "quiz" names the version 3
      Then the app refuses its prompts, as "quiz" has no version 3

  Rule: A released version never changes

    Scenario: The released versions are as they were released
      Then the check of the prompts passes

    Scenario: A changed released version fails the check
      Given the version 1 of the prompt "quiz" has been edited
      Then the check of the prompts fails, naming the version 1 of "quiz" as changed

    Scenario: A new version fails the check until it is locked
      Given the prompt "quiz" has a new version 3
      Then the check of the prompts fails, naming the version 3 of "quiz" as not released
      When I lock the prompts
      Then the check of the prompts passes
      And the version 3 of "quiz" is released

    Scenario: Locking the prompts never changes a released version
      Given the version 1 of the prompt "quiz" has been edited
      When I lock the prompts
      Then the check of the prompts fails, naming the version 1 of "quiz" as changed

  Rule: The version is recorded with what it produces

    Scenario: A trace records the version of its prompt
      Given qubit-notes traces the AI
      When I ask the AI for a quiz
      Then its trace records the prompt "quiz" at the version 2, with the SHA-256 of its text

    Scenario Outline: What the AI writes is kept with the version of its prompt
      When I ask the AI for <what>
      Then it is kept as written with the prompt "<prompt>" at the version in use

      Examples:
        | what                | prompt          |
        | a question answered | study-assistant |
        | a summary           | summaries       |
        | a quiz              | quiz            |
        | flashcards          | flashcards      |
        | generated material  | generating      |

    Scenario: A quiz keeps the version it was written with when the version in use changes
      Given I have asked the AI for a quiz, which is kept
      When the admin "alex" chooses the version 1 of the prompt "quiz"
      Then my quiz is kept as written with the prompt "quiz" at the version 2

  Rule: The admins compare versions, and choose the one in use

    Scenario: An admin sees every prompt, its versions and the one in use
      When the admin "alex" looks at the prompts
      Then they see the prompt "quiz" with the versions 1 and 2, and 2 in use, as prompt.toml names it
      And they see every prompt the app uses

    Scenario: An admin reads a version
      When the admin "alex" reads the version 1 of the prompt "quiz"
      Then they see the text of the version 1 of "quiz"

    Scenario: An admin compares two versions, line by line
      When the admin "alex" compares the versions 1 and 2 of the prompt "quiz"
      Then they see the lines of the version 1 that the version 2 removes, and the lines it adds

    Scenario: An admin rolls back to an earlier version
      When the admin "alex" chooses the version 1 of the prompt "quiz"
      And I ask the AI for a quiz
      Then the AI was given the version 1 of the prompt "quiz"
      And the admin "alex" sees the version 1 of "quiz" in use, as an admin chose it

    Scenario: The admins' choice is kept when the app restarts
      Given the admin "alex" has chosen the version 1 of the prompt "quiz"
      When qubit-notes restarts
      And I ask the AI for a quiz
      Then the AI was given the version 1 of the prompt "quiz"

    Scenario: Choosing prompt.toml's version again
      Given the admin "alex" has chosen the version 1 of the prompt "quiz"
      When the admin "alex" chooses prompt.toml's version of the prompt "quiz"
      And I ask the AI for a quiz
      Then the AI was given the version 2 of the prompt "quiz"

    Scenario Outline: Only a version that exists can be chosen
      When the admin "alex" chooses the version <version> of the prompt "<prompt>"
      Then the choice is refused as not found

      Examples:
        | prompt  | version |
        | quiz    | 3       |
        | unknown | 1       |

    Scenario: Only the app's admins see and choose prompts
      When the student "maria" looks at the prompts
      Then I am told only the app's admins can see them
      When the student "maria" chooses the version 1 of the prompt "quiz"
      Then the choice is refused as not allowed

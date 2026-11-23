@ai
Feature: Tracing the AI
  As the maintainer of qubit-notes
  I want every call to the AI traced, with what it was given, what it answered and how it went
  So that I can see why a reply was good or bad, and measure the AI and make it better

  Every call to the AI is sent as a trace to Langfuse, where it can be looked into. A trace is of
  one thing the student asked for: an answer, a summary, a quiz, flashcards, generated material, a
  comprehension check, a writing assistant's reply, the audio of a material or a transcription,
  named by its purpose, as in the AI's usage (see The AI's usage). It holds a step for each call to
  the AI made for it, so a call the app made again, because the reply was no good, is a second step
  of the same trace. Each call's step records:

    | what              | for example                                            |
    | prompt            | the name and version of the system prompt, e.g. quiz v1 |
    | provider, model   | anthropic, claude-sonnet-5-5                           |
    | input             | the prompt the AI was given, and its history's length  |
    | output            | what the AI answered                                   |
    | tokens            | the input and output tokens it used                    |
    | latency           | how long the call took                                 |
    | outcome           | ok, an unusable reply, or failed at the provider       |

  Where the AI is given passages of the student's material, as the assistant is, the trace also
  records the search that found them: the question searched for, and each passage with its
  reference (P1, P2, …), its material and section. A trace names the student it was for by their
  id, and the conversation it is part of, if any, so a conversation can be followed in Langfuse.
  Audio is not sent: the audio of a material is traced with the text read aloud, a transcription
  with the text heard. Nor are the keys the app is given for the AI's providers.

  A student's rating of a reply (see Rating the assistant's replies, and The writing assistant) is
  sent as the score "rating" of the reply's trace: 1 for "up", 0 for "down". Changing the rating
  changes the score, and taking it back deletes it.

  Traces hold the student's material, so they are deleted with it: deleting a material deletes the
  traces of what was asked about it, and deleting a course those of everything in it. The AI's
  usage is kept, as before. A deletion that Langfuse can't take now is tried again later.

  Tracing never stands in the way of the student: if Langfuse can't be reached, the student gets
  their reply all the same, and the trace is lost. Without Langfuse's keys (QUBIT_NOTES_LANGFUSE_PUBLIC_KEY
  and QUBIT_NOTES_LANGFUSE_SECRET_KEY; QUBIT_NOTES_LANGFUSE_HOST is its EU cloud unless set), nothing
  is traced.

  Background:
    Given I am the student "maria"
    And qubit-notes traces the AI
    And the AI uses 1000 input tokens and 200 output tokens each time
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """
    And I am reading the section "1 Introduction" of "fem-notes.md"

  Rule: Every call to the AI is traced

    Scenario: Nothing is traced before the AI is asked
      Then nothing has been traced

    Scenario Outline: What I ask the AI for is traced by its purpose, with its prompt
      When I ask the AI for <what>
      Then 1 trace "<purpose>" has been traced for me
      And its step used the prompt "<prompt>" at its version
      And its step records the provider, the model, the input, the output, the latency and the outcome "ok"
      And its step used 1000 input tokens and 200 output tokens

      Examples:
        | what                | purpose    | prompt            |
        | a question answered | assistant  | study-assistant   |
        | a summary           | summary    | summaries         |
        | a quiz              | quiz       | quiz              |
        | flashcards          | flashcards | flashcards        |
        | generated material  | generating | generating        |

    Scenario: A saved summary is not traced again
      When I ask the AI for a summary
      And I ask the AI for a summary
      Then 1 trace "summary" has been traced for me

    Scenario: The assistant's trace records the passages it was given
      When I ask the assistant "What does the finite element method divide a domain into?"
      Then the trace of the reply records the search for "What does the finite element method divide a domain into?"
      And the search found the passage "P1" of "fem-notes.md", in the section "1 Introduction"

    Scenario: A conversation can be followed across its traces
      When I ask the assistant "What does the finite element method divide a domain into?"
      And I ask the assistant "What do shape functions do?"
      Then both traces are of my conversation on "fem-notes.md"

    Scenario: A reply the app can't use is a step of the same trace
      Given the AI first replies with something that is not valid
      When I ask the assistant "What does the finite element method divide a domain into?"
      Then 1 trace "assistant" has been traced for me
      And it has 2 calls to the AI, the first with the outcome "unusable reply", the second "ok"

    Scenario: A call that fails at the provider is traced, but uses no tokens
      Given the AI's provider fails
      When I try to ask the AI for a summary
      Then 1 trace "summary" has been traced for me
      And its step records the outcome "failed at the provider", with the provider's error
      And I have used no tokens

    Scenario: Audio is traced by its text, not its sound
      Given the app can speak with OpenAI
      When I ask for the audio of "fem-notes.md"
      Then once it is made, the audio of "fem-notes.md" is ready
      And the trace "audio" records the text read aloud, and no audio

  Rule: A rating of a reply is a score of its trace

    Background:
      Given I have asked the assistant "What does the finite element method divide a domain into?"

    Scenario Outline: Rating a reply scores its trace
      When I rate the assistant's reply "<rating>"
      Then the trace of the reply has the score "rating" of <score>

      Examples:
        | rating | score |
        | up     | 1     |
        | down   | 0     |

    Scenario: Changing a rating changes the score
      Given I have rated the assistant's reply "up"
      When I rate the assistant's reply "down"
      Then the trace of the reply has the score "rating" of 0

    Scenario: Taking a rating back deletes the score
      Given I have rated the assistant's reply "up"
      When I take back my rating of the assistant's reply
      Then the trace of the reply has no score "rating"

    Scenario: A writing assistant's reply is scored the same way
      Given I have asked the writing assistant "Write an introduction to the finite element method"
      When I rate the writing assistant's reply "down"
      Then the trace of the writing assistant's reply has the score "rating" of 0

  Rule: Traces are deleted with the material they hold

    Scenario: Deleting a material deletes its traces
      Given I have asked the assistant "What does the finite element method divide a domain into?"
      And I have asked the AI for a summary
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then nothing traced for me is kept
      And I have used 2000 input tokens and 400 output tokens in 2 requests

    Scenario: Deleting a course deletes the traces of everything in it
      Given I have asked the AI for a quiz
      When I delete the course "aeronautics"
      Then nothing traced for me is kept

    Scenario: A deletion Langfuse can't take now is tried again
      Given I have asked the AI for a summary
      And Langfuse can't be reached
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      And Langfuse can be reached again
      Then nothing traced for me is kept

  Rule: Tracing never stands in the way of the student

    Scenario: The reply is given when Langfuse can't be reached
      Given Langfuse can't be reached
      When I ask the assistant "What does the finite element method divide a domain into?"
      Then the assistant answers
      And I have used 1000 input tokens and 200 output tokens in 1 request

    Scenario: Nothing is traced without Langfuse's keys
      Given qubit-notes does not trace the AI
      When I ask the AI for a summary
      Then nothing has been traced
      And I have used 1000 input tokens and 200 output tokens in 1 request

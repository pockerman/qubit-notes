@ai
Feature: Answering by voice
  As a student
  I want to say my answers rather than type them
  So that I can explain what I understood as I would out loud

  A student records what they say with their microphone, and OpenAI's transcription model turns
  it into text, which they can correct before they send it as their answer (see Checking my
  understanding). So answering by voice needs the app's OpenAI key, whichever AI the student
  chose to question them. They choose which of OpenAI's transcription models hears it, as they
  choose the speech model:
    | model                  | name                   |
    | gpt-4o-mini-transcribe | GPT-4o mini Transcribe |
    | gpt-4o-transcribe      | GPT-4o Transcribe      |
    | whisper-1              | Whisper                |
  The app's own (QUBIT_NOTES_TRANSCRIPTION_MODEL, gpt-4o-mini-transcribe by default) hears it if
  they choose none. A recording is at most 25 MB, and isn't kept. What it takes is counted in the
  student's usage as "transcription".

  Background:
    Given I am the student "maria"

  Scenario: The transcription models
    When I ask which models can hear what I say
    Then I am offered the transcription models "gpt-4o-mini-transcribe,gpt-4o-transcribe,whisper-1"
    And the app's own is "gpt-4o-mini-transcribe"

  Scenario: Say an answer
    Given the app can hear with OpenAI
    When I say "Shape functions interpolate the solution inside each element"
    Then I get the text "Shape functions interpolate the solution inside each element"
    And it was heard by "gpt-4o-mini-transcribe"
    And my AI usage has "transcription"

  Scenario: Choose the model that hears it
    Given the app can hear with OpenAI
    When I say "Shape functions interpolate the solution" to "whisper-1"
    Then it was heard by "whisper-1"

  Scenario: A model that isn't one of them
    Given the app can hear with OpenAI
    When I say "Shape functions interpolate the solution" to "parrot-2"
    Then I am told there is no transcription model "parrot-2"

  Scenario: Without the app's OpenAI key
    Given the app can't hear, having no OpenAI key
    When I ask which models can hear what I say
    Then I am told the app can't hear what I say
    When I say "Shape functions interpolate the solution"
    Then the recording is refused, as the app has no OpenAI key

  Scenario: A recording with nothing in it
    Given the app can hear with OpenAI
    When I say nothing
    Then I am told the recording is empty

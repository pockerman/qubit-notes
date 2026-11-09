@ai
Feature: Audio of a material
  As a student
  I want to listen to my material
  So that I can study it away from the screen, on a walk or on the bus

  A student asks for the audio of a material they can read, with instructions if they like, e.g.
  "explain it like a lecture, with an example for each idea" or "a calm voice, slowly". The AI
  first writes a narration of the material to be listened to, not read: formulas said in words,
  code and tables described rather than read out, following the instructions, which also say how
  it is spoken. Then the narration is read aloud by OpenAI's speech model, so audio needs the
  app's OpenAI key, whichever AI the student chose for the narration. Making it takes a while: the
  audio is "generating" until it is "ready" to listen to, or has "failed", saying why.

  The student chooses which of OpenAI's speech models reads it aloud, as they choose the AI:
    | model           | name                 | follows how to speak it |
    | gpt-4o-mini-tts | GPT-4o mini TTS      | yes                     |
    | tts-1           | TTS-1 (fast)          | no                      |
    | tts-1-hd        | TTS-1 HD (best sound) | no                      |
  The app's own (QUBIT_NOTES_SPEECH_MODEL, gpt-4o-mini-tts by default) reads it if they choose none.
  Only gpt-4o-mini-tts is told how to speak it; the others read it as they do. The model it was
  read by is kept with the audio, and an improved audio is read by the model chosen then.

  A student has at most one audio of a material, which is their own: another student of the course
  can't hear it, and makes their own. It can be deleted, and another asked for. It can also be
  improved: the student says what to change, e.g. "too fast" or "skip the history", and the AI
  writes a new narration from the material, its earlier narration and the suggestions, which
  takes the place of the earlier audio. Its audio is deleted with the material, or the course.

  Background:
    Given I am the student "maria"
    And the app can speak with OpenAI
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      Shape functions interpolate the solution inside each element.
      """

  Rule: A student asks for the audio of a material, with instructions

    Scenario: A material has no audio until it is asked for
      Then "fem-notes.md" has no audio of mine

    Scenario: Ask for the audio of a material
      When I ask for the audio of "fem-notes.md"
      Then the audio of "fem-notes.md" is generating
      And once it is made, the audio of "fem-notes.md" is ready
      And its narration is of "1 Introduction" and "2 Shape functions"
      And I can listen to it as MP3
      And the narration was read aloud by OpenAI

    Scenario: Instructions say how it is written and spoken
      When I ask for the audio of "fem-notes.md" with the instructions "explain it like a lecture, slowly"
      Then once it is made, the audio of "fem-notes.md" is ready
      And the AI was told to write it "explain it like a lecture, slowly"
      And it was read aloud as the AI said to speak it
      And the audio of "fem-notes.md" has the instructions "explain it like a lecture, slowly"

    Scenario: A long narration is read aloud in parts, made one audio
      Given "long-notes.md" in "aeronautics/numerical-methods/finite-elements" has 40 sections
      When I ask for the audio of "long-notes.md"
      Then once it is made, the audio of "long-notes.md" is ready
      And its narration was read aloud in more than one part, each short enough for OpenAI
      And I can listen to it as MP3

    Scenario: Making the audio is counted in my AI usage
      When I ask for the audio of "fem-notes.md"
      Then once it is made, the audio of "fem-notes.md" is ready
      And my AI usage has "audio"

  Rule: A student has one audio of a material, which they delete or improve

    Scenario: Delete the audio and ask for another
      Given I have the audio of "fem-notes.md"
      When I delete the audio of "fem-notes.md"
      Then "fem-notes.md" has no audio of mine
      And its file is deleted
      When I ask for the audio of "fem-notes.md" with the instructions "shorter"
      Then once it is made, the audio of "fem-notes.md" is ready
      And the audio of "fem-notes.md" has the instructions "shorter"

    Scenario: Asking again while it has audio
      Given I have the audio of "fem-notes.md"
      When I ask for the audio of "fem-notes.md"
      Then I am told to delete or improve the audio of "fem-notes.md" first

    Scenario: Improve the audio with suggestions
      Given I have the audio of "fem-notes.md"
      When I suggest "too fast, and give an example of a shape function" for the audio of "fem-notes.md"
      Then once it is made, the audio of "fem-notes.md" is ready
      And the AI was given its earlier narration and "too fast, and give an example of a shape function"
      And it is a new narration
      And the earlier audio's file is deleted

    Scenario: Improving needs audio to improve
      When I suggest "slower" for the audio of "fem-notes.md"
      Then I am told there is no audio of "fem-notes.md" to improve

    Scenario: Nothing is done twice at once
      Given the app is slow to speak
      And I have asked for the audio of "fem-notes.md"
      When I ask for the audio of "fem-notes.md"
      Then I am told the audio of "fem-notes.md" is being made

  Rule: The student chooses the speech model

    Scenario: The speech models to choose from
      When I ask which speech models there are
      Then I am told the speech models are "gpt-4o-mini-tts, tts-1, tts-1-hd"
      And I am told the app's own is "gpt-4o-mini-tts"
      And I am told the app can speak

    Scenario: Without a choice, the app's own reads it
      When I ask for the audio of "fem-notes.md"
      Then once it is made, the audio of "fem-notes.md" is ready
      And it was read aloud by "gpt-4o-mini-tts"
      And the audio of "fem-notes.md" was read by "gpt-4o-mini-tts"

    Scenario Outline: Choose the speech model
      When I ask for the audio of "fem-notes.md" read by "<model>"
      Then once it is made, the audio of "fem-notes.md" is ready
      And it was read aloud by "<model>"
      And the audio of "fem-notes.md" was read by "<model>"

      Examples:
        | model           |
        | gpt-4o-mini-tts |
        | tts-1           |
        | tts-1-hd        |

    Scenario: Only gpt-4o-mini-tts is told how to speak it
      When I ask for the audio of "fem-notes.md" read by "tts-1-hd", with the instructions "slowly"
      Then once it is made, the audio of "fem-notes.md" is ready
      And it was read aloud with no instructions on how to speak it

    Scenario: An improved audio is read by the model chosen then
      Given I have the audio of "fem-notes.md"
      When I suggest "warmer" for the audio of "fem-notes.md", read by "tts-1"
      Then once it is made, the audio of "fem-notes.md" is ready
      And the audio of "fem-notes.md" was read by "tts-1"

    Scenario: A model that isn't one of them
      When I ask for the audio of "fem-notes.md" read by "whisper-1"
      Then I am told to choose one of the speech models

  Rule: Audio needs OpenAI, and text to narrate

    Scenario: Without the app's OpenAI key
      Given the app can't speak, having no OpenAI key
      When I ask for the audio of "fem-notes.md"
      Then I am told audio needs the app's OpenAI key
      And "fem-notes.md" has no audio of mine

    Scenario: Speaking fails
      Given OpenAI fails to speak
      When I ask for the audio of "fem-notes.md"
      Then once it is made, the audio of "fem-notes.md" has failed, saying why
      When I delete the audio of "fem-notes.md"
      Then "fem-notes.md" has no audio of mine

    Scenario: A video has no audio to make
      Given I have uploaded the video "lecture.mp4" to "aeronautics/numerical-methods/finite-elements"
      When I ask for the audio of "lecture.mp4"
      Then I am told only text has audio

  Rule: A student's audio is their own

    Scenario: Another student of the course has their own
      Given I have the audio of "fem-notes.md"
      And I have shared the course "aeronautics" with "tom" as a reader
      Then "fem-notes.md" has no audio of "tom"
      And "tom" can't listen to mine

    Scenario: A reader makes their own
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" asks for the audio of "fem-notes.md"
      Then once it is made, the audio of "fem-notes.md" of "tom" is ready
      And "fem-notes.md" has no audio of mine

    Scenario: Not of a course I'm in
      When the student "pedro" asks for the audio of "fem-notes.md"
      Then the audio is refused, the course not being shared with them

    Scenario: Audio is deleted with its material
      Given I have the audio of "fem-notes.md"
      When I delete the material "fem-notes.md" from "aeronautics/numerical-methods/finite-elements"
      Then no audio is kept

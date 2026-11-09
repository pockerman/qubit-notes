@ui
Feature: Audio of a material in the browser
  As a student
  I want to make, play, improve and delete the audio of what I am reading
  So that I can listen to it without leaving the app

  "Audio", next to "Edit", "Download" and "AI" in the reader, opens the material's audio beside the
  text (see Audio of a material). With no audio yet, it offers to make it, with instructions to
  give if I like. While it is made it says so; once ready, it plays it, can download it, shows its
  narration, and offers to improve it with suggestions or to delete it. If it failed, it says why,
  and offers to delete it, to ask for another.

  As with the AI, the student chooses the speech model among OpenAI's, each with its name; the
  choice is kept in their browser, for all their audio, and the model an audio was read by is shown
  with it. Without the app's OpenAI key, none can be chosen, and it says why.

  Background:
    Given I am signed in as "maria"
    And the app can speak with OpenAI
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.
      """
    When I open the course "Aeronautics"
    And I open "fem-notes.md" to read it
    And I open the audio

  Scenario: Make the audio and listen to it
    Then I am offered to make the audio
    When I make the audio with the instructions "like a lecture"
    Then I see the audio is ready to play
    And I see its narration has "1 Introduction"
    And I see the instructions "like a lecture"

  Scenario: Improve the audio
    When I make the audio
    And I improve the audio with "slower, please"
    Then I see the audio is ready to play
    And I see the suggestions "slower, please"

  Scenario: Delete the audio and make another
    When I make the audio
    And I delete the audio
    Then I am offered to make the audio
    When I make the audio with the instructions "shorter"
    Then I see the audio is ready to play

  Scenario: The audio is still there when I come back
    When I make the audio
    And I come back to the page later
    And I open the audio
    Then I see the audio is ready to play

  Scenario: Choose the speech model
    Then I can choose the speech model from "GPT-4o mini TTS, TTS-1 (fast), TTS-1 HD (best sound)"
    And "GPT-4o mini TTS" is chosen
    When I choose the speech model "TTS-1 HD (best sound)"
    And I make the audio
    Then I see it was read by "TTS-1 HD (best sound)"
    When I come back to the page later
    And I open the audio
    Then "TTS-1 HD (best sound)" is chosen

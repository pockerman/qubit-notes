@ui
Feature: Papers in the browser
  As a student
  I want my papers under My papers, apart from my courses
  So that I can read, note and ask about each paper on screen

  Scenario: My courses and My papers are tabs, opening on My courses
    Given I am signed in as "maria"
    Then I see the tabs "My courses, My papers", with "My courses" chosen
    When I choose the tab "My papers"
    Then I see the tabs "My courses, My papers", with "My papers" chosen
    And I see that I have no collections yet
    When I choose the tab "My courses"
    Then I see that I have no courses yet

  Scenario: Create a collection under My papers, apart from my courses
    Given I am signed in as "maria"
    When I go to my papers
    And I create the collection "Reinforcement Learning"
    Then I am in the collection "Reinforcement Learning"
    And I see that it has no papers yet
    When I go to my courses
    Then I see that I have no courses yet

  Scenario: Add a paper, and read it by its sections
    Given I am signed in as "maria"
    And I have created the collection "reinforcement-learning" titled "Reinforcement learning"
    When I open the collection "Reinforcement learning"
    And I add the paper "dqn.md" with the content:
      """
      # Playing Atari with Deep Reinforcement Learning

      ## Abstract
      A deep network learns to play Atari games from their pixels.

      ## Method
      Q-learning with experience replay trains the network.
      """
    Then I see the paper "Playing Atari with Deep Reinforcement Learning"
    When I open the paper "Playing Atari with Deep Reinforcement Learning"
    Then I am reading "Playing Atari with Deep Reinforcement Learning" of "Reinforcement learning"
    And I see its sections "Playing Atari with Deep Reinforcement Learning, Abstract, Method"

  Scenario: Change a paper's details
    Given I am signed in as "maria"
    And I have created the collection "reinforcement-learning" titled "Reinforcement learning"
    And I have uploaded the paper "dqn.md" to "reinforcement-learning"
    When I open the collection "Reinforcement learning"
    And I change the details of the paper "Dqn" to the title "Human-level control", the authors "Volodymyr Mnih, Koray Kavukcuoglu", the year "2015" and the venue "Nature"
    Then I see the paper "Human-level control" by "Volodymyr Mnih, Koray Kavukcuoglu · 2015 · Nature"

  Scenario: Note a passage of a paper, and ask the assistant about it
    Given I am signed in as "maria"
    And I have created the collection "reinforcement-learning" titled "Reinforcement learning"
    And I have uploaded the paper "dqn.md" to "reinforcement-learning" with the content:
      """
      # Abstract
      A deep network learns to play Atari games from their pixels, with experience replay.
      """
    When I open the collection "Reinforcement learning"
    And I open the paper "Abstract"
    And I select "with experience replay" and note "compare with prioritised replay"
    Then I see my note "compare with prioritised replay"
    When I open the assistant
    And I ask "What is experience replay?"
    Then I see an answer that cites "Abstract"

  Scenario: Ask the assistant about the whole collection
    Given I am signed in as "maria"
    And I have created the collection "reinforcement-learning" titled "Reinforcement learning"
    And I have uploaded the paper "dqn.md" to "reinforcement-learning" with the content:
      """
      # Abstract
      A deep network learns to play Atari games from their pixels, with experience replay.
      """
    When I open the collection "Reinforcement learning"
    And I open the assistant
    And I ask "What is experience replay?"
    Then I see an answer that cites "Abstract"

  Scenario: Share a collection
    Given I am signed in as "maria"
    And I have created the collection "reinforcement-learning" titled "Reinforcement learning"
    When I open the collection "Reinforcement learning"
    And I open its members
    And I share it with "tom" as a reader
    Then I see "tom" as a reader of the course

Feature: Papers
  As a student
  I want to keep the papers I read in collections of their own
  So that I can study each paper, with notes and the assistant, as a whole

  Papers are kept apart from courses, under My Papers, in collections, e.g. "reinforcement-learning". A paper is
  uploaded to a collection and stays one paper: it is never made into lessons or topics. A PDF or an EPUB is
  converted to Markdown, as material is (see PDF and EPUB material as Markdown), and is read by its own sections,
  e.g. Abstract, Introduction and Method, with notes on its passages as on any material (see Notes).

  A paper has details: its title, authors, year, venue and DOI. They are filled in from the paper where they can
  be, from a PDF's own title and authors, a DOI on its first page, and the year of an arXiv identifier, and its
  collection's owners can change them. A paper without a title is titled after its file.

  The assistant answers about the paper being read from that paper alone. Asked on the collection, it answers from
  all the collection's papers (see Asking the assistant).

  A collection is shared, and deleted, as a course is (see Sharing courses). A student's collections and courses
  share their names: a collection can't be called as one of their courses is.

  Background:
    Given I am the student "maria"

  Rule: Collections of papers are apart from courses

    Scenario: Create a collection
      When I create the collection "reinforcement-learning" titled "Reinforcement learning"
      Then my collections are:
        | collection             | title                  |
        | reinforcement-learning | Reinforcement learning |
      And I have no courses

    Scenario: A course is not a collection
      Given I have created the course "aeronautics"
      Then I have no collections

    Scenario: A collection can't be called as one of my courses is
      Given I have created the course "aeronautics"
      When I create the collection "aeronautics" titled "Aeronautics"
      Then I am told I already have a course or a collection called "aeronautics"

  Rule: An uploaded paper stays one paper

    Background:
      Given I have created the collection "reinforcement-learning" titled "Reinforcement learning"

    @platform
    Scenario: Upload a paper in Markdown
      When I upload the paper "dqn.md" to "reinforcement-learning" with the content:
        """
        # Playing Atari with Deep Reinforcement Learning

        ## Abstract
        A deep network learns to play Atari games from their pixels.

        ## Method
        Q-learning with experience replay trains the network.
        """
      Then the papers of "reinforcement-learning" are:
        | paper  | title                                          |
        | dqn.md | Playing Atari with Deep Reinforcement Learning |
      And "dqn.md" is read by its sections "Playing Atari with Deep Reinforcement Learning, Abstract, Method"

    @platform
    Scenario: A paper in a PDF is converted, and is not made into lessons
      When I upload the paper "ppo.pdf" to "reinforcement-learning", whose pages read:
        | page                                    | outline      |
        | We propose proximal policy optimization | Abstract     |
        | Clipped surrogate objective             | Method       |
        | PPO outperforms other methods           | Experiments  |
      Then the papers of "reinforcement-learning" are:
        | paper   | title |
        | ppo.pdf | Ppo   |
      And "ppo.pdf" is read by its sections "Abstract, Method, Experiments"

    Scenario: Only text can be a paper
      When I upload the paper "talk.mp4" to "reinforcement-learning"
      Then I am told a paper must be a PDF, an EPUB, a Markdown or a text file

    Scenario: Delete a paper
      Given I have uploaded the paper "dqn.md" to "reinforcement-learning"
      When I delete the paper "dqn.md" from "reinforcement-learning"
      Then "reinforcement-learning" has no papers

  Rule: A paper has details, filled in from it where they can be

    Background:
      Given I have created the collection "reinforcement-learning" titled "Reinforcement learning"

    Scenario: The details of a PDF are filled in from it
      When I upload the paper "1707.06347.pdf" to "reinforcement-learning", a PDF titled "Proximal Policy Optimization Algorithms" by "John Schulman; Filip Wolski" whose first page reads "arXiv:1707.06347v2 [cs.LG] doi:10.48550/arXiv.1707.06347"
      Then the details of "1707.06347.pdf" are:
        | title   | Proximal Policy Optimization Algorithms |
        | authors | John Schulman, Filip Wolski             |
        | year    | 2017                                    |
        | venue   | arXiv                                   |
        | doi     | 10.48550/arXiv.1707.06347               |

    Scenario: Change a paper's details
      Given I have uploaded the paper "dqn.md" to "reinforcement-learning"
      When I change the details of "dqn.md" to:
        | title   | Human-level control through deep reinforcement learning |
        | authors | Volodymyr Mnih, Koray Kavukcuoglu                       |
        | year    | 2015                                                    |
        | venue   | Nature                                                  |
        | doi     | 10.1038/nature14236                                     |
      Then the details of "dqn.md" are:
        | title   | Human-level control through deep reinforcement learning |
        | authors | Volodymyr Mnih, Koray Kavukcuoglu                       |
        | year    | 2015                                                    |
        | venue   | Nature                                                  |
        | doi     | 10.1038/nature14236                                     |

    Scenario: A paper needs a title
      Given I have uploaded the paper "dqn.md" to "reinforcement-learning"
      When I change the details of "dqn.md" to:
        | title | |
      Then I am told a paper needs a title

  Rule: Notes and the assistant work on papers as on material

    Background:
      Given I have created the collection "reinforcement-learning" titled "Reinforcement learning"
      And I have uploaded the paper "dqn.md" to "reinforcement-learning" with the content:
        """
        # Abstract
        A deep network learns to play Atari games from their pixels, with experience replay.
        """
      And I have uploaded the paper "ppo.md" to "reinforcement-learning" with the content:
        """
        # Abstract
        Proximal policy optimization clips the policy update; it needs no experience replay.
        """

    Scenario: Take a note on a passage of a paper
      When I note "compare with prioritised replay" on "with experience replay" in "Abstract" of "dqn.md"
      Then the notes of "dqn.md" are:
        | section  | passage                | note                            |
        | Abstract | with experience replay | compare with prioritised replay |

    @ai @platform
    Scenario: The assistant answers about a paper from that paper alone
      Given I have asked the assistant "What is experience replay?" while reading "dqn.md"
      Then the assistant answers
      And the answer cites "dqn.md"
      And the answer does not cite "ppo.md"

    @ai @platform
    Scenario: The assistant answers about the collection from all its papers
      Given I am studying the collection "reinforcement-learning"
      When I ask the assistant "What is experience replay?"
      Then the assistant answers
      And the answer cites "dqn.md"
      And the answer cites "ppo.md"

    @ai
    Scenario: The assistant summarises a paper
      Given I have asked the assistant "Summarise this paper" while reading "dqn.md"
      Then the assistant gives me a summary of "dqn.md"

  Rule: A collection is shared and deleted as a course is

    Background:
      Given I have created the collection "reinforcement-learning" titled "Reinforcement learning"
      And I have uploaded the paper "dqn.md" to "reinforcement-learning"

    Scenario: Share a collection with a classmate as a reader
      When I share the collection "reinforcement-learning" with "tom" as a reader
      Then the student "tom" sees the collections:
        | collection             | owned by | role   |
        | reinforcement-learning | maria    | reader |
      And the student "tom" sees the papers "dqn.md" in "reinforcement-learning"

    Scenario: A reader can't add papers, or change their details
      Given I have shared the collection "reinforcement-learning" with "tom" as a reader
      When the student "tom" uploads the paper "notes.md" to "reinforcement-learning"
      Then the student "tom" is not allowed to do that
      When the student "tom" changes the title of the paper "dqn.md" to "Mine"
      Then the student "tom" is not allowed to do that

    Scenario: Delete a collection
      When I delete the collection "reinforcement-learning"
      Then I have no collections

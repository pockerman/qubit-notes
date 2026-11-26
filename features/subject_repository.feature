@ai
Feature: Pushing a subject to a repository
  As a student
  I want to push everything I made while studying a subject to a Git repository of mine
  So that my notes, summaries, flashcards and quizzes are kept, versioned and readable outside the app

  A student connects a subject to a repository on GitHub, e.g. "maria/numerical-methods", with a
  token GitHub gives them that may write to it (a fine-grained token with read and write access to
  its contents). Each subject is connected on its own, to its own repository: the subject is the
  repository's whole content, whatever course it is in. The token is kept in the app's database,
  encrypted with the app's secret (QUBIT_NOTES_SECRET_KEY), and never shown back; without the
  secret, a subject can't be connected.

  Pushing writes, in one commit on the repository's default branch, everything of the subject
  that is the student's own, as Markdown:

    | file                                     | what it holds                                                      |
    | README.md                                | the subject, its topics in reading order, and what each file holds |
    | <n> <topic>/<material>/<material>.md     | a material the student wrote in Markdown, as it is now             |
    | <n> <topic>/<material>/<image path>      | each image of that material, at the path the material refers to it by, so it shows on GitHub |
    | <n> <topic>/<material>/notes.md          | the notes and highlights of a material, in the order of the material: the section and the passage of each, or its moment in a video |
    | <n> <topic>/<material>/summaries.md      | the summaries of the material and of its sections, newest first    |
    | <n> <topic>/<material>/quizzes.md        | the quizzes on the material and its sections: each question, its choices, the correct one, the section it cites, and the student's scores |
    | <n> <topic>/<material>/flashcards.md     | the decks of the material and of its sections, each card's front and back |
    | <n> <topic>/summaries.md, quizzes.md, flashcards.md | those of the whole topic                                |
    | flashcards.csv                           | every card of the subject, which a flashcard app can import        |
    | summaries.md, quizzes.md, flashcards.md  | those of the whole subject                                         |

  Topics are numbered in the order they are read, and named as in the app, as in a downloaded
  subject (see Downloading a subject as a zip). A file is written only when it has something in it.
  When it was pushed is told by its commit, not in the files.
  A material is pushed only when the student wrote it: Markdown they uploaded, or generated
  material they saved (see Generating material). It is pushed as its text is now, beside what they
  made of it. Other material isn't pushed, as it isn't theirs to keep in Git and may be large: a
  PDF or an EPUB, even once converted to Markdown, a video, or material of someone else's course
  shared with them. It can be downloaded as a zip.

  Pushing again writes the subject as it is then: what changed is changed, and the files the app
  wrote that would now be empty, or that belong to a topic or material that was renamed or deleted,
  are removed. Files of the repository the app didn't write are left as they are. When nothing
  changed since the last push, nothing is committed.

  A student pushes only their own work, as they see it: in a shared course, a reader can connect
  the subject to a repository of their own and push their own notes, summaries, flashcards and
  quizzes, never anyone else's. A student can disconnect a subject, which forgets the token; the
  repository is left as it is.

  Background:
    Given I am the student "maria"
    And I have uploaded "fem-notes.md" to "aeronautics/numerical-methods/finite-elements" with the content:
      """
      # 1 Introduction
      The finite element method divides a domain into small elements.

      # 2 Shape functions
      A linear element interpolates linearly between its two nodes.
      """
    And I have uploaded "solvers.md" to "aeronautics/numerical-methods/solvers" with the content:
      """
      # 1 Iterative solvers
      Conjugate gradients solve symmetric systems.
      """
    And GitHub has the repository "maria/numerical-methods", which the token "maria-token" may write to

  Rule: A subject is connected to a repository with a token that may write to it

    Scenario: Connect a subject to a repository
      When I connect the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods" with the token "maria-token"
      Then the subject "numerical-methods" of "aeronautics" is connected to "maria/numerical-methods"
      And it has never been pushed
      And the token is never shown back

    Scenario: A token that can't write to the repository is refused
      Given GitHub has the repository "maria/old-notes", which the token "maria-token" may only read
      When I connect the subject "numerical-methods" of "aeronautics" to "maria/old-notes" with the token "maria-token"
      Then I am told the token may not write to "maria/old-notes"
      And the subject "numerical-methods" of "aeronautics" is not connected

    Scenario: A repository that isn't there is refused
      When I connect the subject "numerical-methods" of "aeronautics" to "maria/no-such-repo" with the token "maria-token"
      Then I am told GitHub has no repository "maria/no-such-repo" that the token can see
      And the subject "numerical-methods" of "aeronautics" is not connected

    Scenario: Without the app's secret, a subject can't be connected
      Given qubit-notes is running without a secret key
      When I connect the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods" with the token "maria-token"
      Then I am told the app can't keep the token without its secret
      And the subject "numerical-methods" of "aeronautics" is not connected

    Scenario: Each subject is connected to its own repository
      Given I have uploaded "lift.md" to "aeronautics/aerodynamics/lift" with the content:
        """
        # 1 Lift
        Lift comes from the pressure difference over a wing.
        """
      And GitHub has the repository "maria/aerodynamics", which the token "maria-token" may write to
      When I connect the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods" with the token "maria-token"
      And I connect the subject "aerodynamics" of "aeronautics" to "maria/aerodynamics" with the token "maria-token"
      Then the subject "numerical-methods" of "aeronautics" is connected to "maria/numerical-methods"
      And the subject "aerodynamics" of "aeronautics" is connected to "maria/aerodynamics"

    Scenario: Disconnect a subject
      Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
      And I have pushed the subject "numerical-methods" of "aeronautics"
      When I disconnect the subject "numerical-methods" of "aeronautics"
      Then the subject "numerical-methods" of "aeronautics" is not connected
      And the app keeps no token for it
      And "maria/numerical-methods" still has the files it was pushed

    Scenario: A subject there isn't
      When I connect the subject "thermodynamics" of "aeronautics" to "maria/numerical-methods" with the token "maria-token"
      Then the connection is refused as not found

  Rule: Pushing writes everything of the subject that is the student's own

    Background:
      Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"

    Scenario: Push a subject
      Given I have noted "compare with Galerkin's method" on "divides a domain into small elements" in "1 Introduction" of "fem-notes.md"
      And I have highlighted "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      And I have asked for a summary of "fem-notes.md"
      And I have asked for a quiz of 2 questions on "fem-notes.md"
      And I have asked for 2 flashcards of "fem-notes.md"
      And I have asked for a summary of the topic "aeronautics/numerical-methods/solvers"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has one new commit on its default branch, with the files:
        | file                                           |
        | README.md                                      |
        | flashcards.csv                                 |
        | 1 Finite elements/fem-notes/fem-notes.md       |
        | 1 Finite elements/fem-notes/notes.md           |
        | 1 Finite elements/fem-notes/summaries.md       |
        | 1 Finite elements/fem-notes/quizzes.md         |
        | 1 Finite elements/fem-notes/flashcards.md      |
        | 2 Solvers/summaries.md                         |
        | 2 Solvers/solvers/solvers.md                   |
      And the subject "numerical-methods" of "aeronautics" was pushed just now, with that commit

    Scenario: Notes and highlights are in the order of the material, with their passages
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      And I have highlighted "divides a domain into small elements" in "1 Introduction" of "fem-notes.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "1 Finite elements/fem-notes/notes.md" in "maria/numerical-methods" has the notes:
        | section           | passage                              | note           |
        | 1 Introduction    | divides a domain into small elements |                |
        | 2 Shape functions | between its two nodes                | why two nodes? |

    Scenario: Notes on a video are at their moments
      Given I have uploaded the video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      And I have noted "derivation of the stiffness matrix" at 12:30 of "lecture-3.mp4"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "1 Finite elements/lecture-3/notes.md" in "maria/numerical-methods" has the notes:
        | at    | note                               |
        | 12:30 | derivation of the stiffness matrix |

    Scenario: Every summary is pushed, newest first
      Given I have asked for a summary of "fem-notes.md"
      And I have asked for a new summary of "fem-notes.md"
      And I have asked for a summary of the section "2 Shape functions" of "fem-notes.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "1 Finite elements/fem-notes/summaries.md" in "maria/numerical-methods" has 3 summaries, newest first, each with what it summarises

    Scenario: A quiz is pushed with its answers and my scores
      Given I have taken a quiz of 3 questions on "fem-notes.md" and scored 1 out of 3
      When I push the subject "numerical-methods" of "aeronautics"
      Then "1 Finite elements/fem-notes/quizzes.md" in "maria/numerical-methods" has the quiz's 3 questions, each with its choices, the correct one and the section it cites
      And it has my score of 1 out of 3

    Scenario: Every card of the subject is in flashcards.csv
      Given I have asked for 2 flashcards of "fem-notes.md"
      And I have asked for 1 flashcard of "solvers.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then flashcards.csv in "maria/numerical-methods" has 2 cards from "fem-notes.md" and 1 from "solvers.md"

    Scenario: The topics are numbered in the order they are read
      Given I have noted "a first note" on "divides a domain" in "1 Introduction" of "fem-notes.md"
      And I have put the topics of "numerical-methods" of "aeronautics" in the order "solvers, finite-elements"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has the file "2 Finite elements/fem-notes/notes.md"

    Scenario: A material I wrote is pushed as it is
      When I push the subject "numerical-methods" of "aeronautics"
      Then "1 Finite elements/fem-notes/fem-notes.md" in "maria/numerical-methods" is:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Shape functions
        A linear element interpolates linearly between its two nodes.
        """

    Scenario: A material I wrote is pushed with its images
      Given I have changed the text of "fem-notes.md" to:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        ![A mesh](figures/mesh.png)
        """
      And I have added the image "figures/mesh.png" to "fem-notes.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "1 Finite elements/fem-notes/figures/mesh.png" in "maria/numerical-methods" is the image I added

    Scenario: A material I didn't write isn't pushed, only what I made of it
      Given I have uploaded a PDF "stiffness.pdf" to "aeronautics/numerical-methods/finite-elements" with the pages:
        | text                                   | outline | level | page |
        | The stiffness matrix is symmetric.     |         |       |      |
      And I have uploaded the video "lecture-3.mp4" to "aeronautics/numerical-methods/finite-elements"
      And I have noted "derivation of the stiffness matrix" at 12:30 of "lecture-3.mp4"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has the file "1 Finite elements/lecture-3/notes.md"
      And "maria/numerical-methods" has no file of the material "stiffness.pdf"
      And "maria/numerical-methods" has no file of the material "lecture-3.mp4"

    Scenario: A subject with nothing made of its material yet
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has one new commit, with the files:
        | file                                     |
        | README.md                                |
        | 1 Finite elements/fem-notes/fem-notes.md |
        | 2 Solvers/solvers/solvers.md             |

    Scenario: A subject that isn't connected can't be pushed
      Given I have disconnected the subject "numerical-methods" of "aeronautics"
      When I push the subject "numerical-methods" of "aeronautics"
      Then I am told the subject isn't connected to a repository

    Scenario: A push GitHub refuses leaves the repository as it was
      Given GitHub no longer lets the token "maria-token" write to "maria/numerical-methods"
      When I push the subject "numerical-methods" of "aeronautics"
      Then I am told GitHub refused the push: the token may not write to "maria/numerical-methods"
      And "maria/numerical-methods" has no new commit
      And the subject "numerical-methods" of "aeronautics" has never been pushed

  Rule: Pushing again writes the subject as it is then

    Background:
      Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
      And I have noted "compare with Galerkin's method" on "divides a domain into small elements" in "1 Introduction" of "fem-notes.md"
      And I have pushed the subject "numerical-methods" of "aeronautics"

    Scenario: What changed is pushed in a new commit
      Given I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has one new commit, changing only "1 Finite elements/fem-notes/notes.md"
      And "1 Finite elements/fem-notes/notes.md" in "maria/numerical-methods" has 2 notes

    Scenario: A material I changed is pushed as it is now
      Given I have changed the text of "solvers.md" to:
        """
        # 1 Iterative solvers
        Conjugate gradients solve symmetric positive definite systems.
        """
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has one new commit, changing only "2 Solvers/solvers/solvers.md"

    Scenario: Nothing is committed when nothing changed
      When I push the subject "numerical-methods" of "aeronautics"
      Then I am told there is nothing new to push
      And "maria/numerical-methods" has no new commit

    Scenario: A file with nothing left in it is removed
      Given I have deleted my note "compare with Galerkin's method" of "fem-notes.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has no file "1 Finite elements/fem-notes/notes.md"

    Scenario: A renamed topic moves to its new folder
      Given I have renamed the topic "numerical-methods/finite-elements" of "aeronautics" to "The Finite Element Method"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has the file "1 The Finite Element Method/fem-notes/notes.md"
      And "maria/numerical-methods" has the file "1 The Finite Element Method/fem-notes/fem-notes.md"
      And "maria/numerical-methods" has no file "1 Finite elements/fem-notes/notes.md"
      And "maria/numerical-methods" has no file "1 Finite elements/fem-notes/fem-notes.md"

    Scenario: A deleted material's files are removed, its images too
      Given I have changed the text of "fem-notes.md" to:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        ![A mesh](figures/mesh.png)
        """
      And I have added the image "figures/mesh.png" to "fem-notes.md"
      And I have pushed the subject "numerical-methods" of "aeronautics"
      And I have deleted the material "fem-notes.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" has no file "1 Finite elements/fem-notes/notes.md"
      And "maria/numerical-methods" has no file "1 Finite elements/fem-notes/fem-notes.md"
      And "maria/numerical-methods" has no file "1 Finite elements/fem-notes/figures/mesh.png"

    Scenario: Files the app didn't write are left as they are
      Given "maria/numerical-methods" has a file "my-own-notes.md" that the app didn't write
      And I have noted "why two nodes?" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      When I push the subject "numerical-methods" of "aeronautics"
      Then "maria/numerical-methods" still has the file "my-own-notes.md" as it was

  Rule: A student pushes only their own work

    Background:
      Given I have shared the course "aeronautics" with "pedro" as a reader
      And GitHub has the repository "pedro/numerical-methods", which the token "pedro-token" may write to

    Scenario: A reader of the course pushes their own work to their own repository
      Given I have noted "compare with Galerkin's method" on "divides a domain into small elements" in "1 Introduction" of "fem-notes.md"
      And the student "pedro" has noted "a note of pedro's" on "between its two nodes" in "2 Shape functions" of "fem-notes.md"
      When the student "pedro" connects the subject "numerical-methods" of "aeronautics" to "pedro/numerical-methods" with the token "pedro-token"
      And the student "pedro" pushes the subject "numerical-methods" of "aeronautics"
      Then "1 Finite elements/fem-notes/notes.md" in "pedro/numerical-methods" has the notes:
        | section           | passage               | note              |
        | 2 Shape functions | between its two nodes | a note of pedro's |
      And "pedro/numerical-methods" has no file "1 Finite elements/fem-notes/fem-notes.md"

    Scenario: Each student's connection is their own
      Given I have connected the subject "numerical-methods" of "aeronautics" to "maria/numerical-methods"
      Then the subject "numerical-methods" of "aeronautics" is not connected, as the student "pedro" sees it

    Scenario: Someone the course isn't shared with can't connect it
      When the student "lucia" connects the subject "numerical-methods" of "aeronautics" to "pedro/numerical-methods" with the token "pedro-token"
      Then the connection is refused as not found

Feature: Study materials
  As a student
  I want to upload my study material and organise it by course, subject and topic
  So that the assistant answers from what I am actually studying

  Material lives at a location "<course>/<subject>/<topic>",
  e.g. "aeronautics/numerical-methods/finite-elements".
  Uploading to a course I don't have yet creates it, with me as its owner.

  Background:
    Given I am the student "maria"

  Rule: Uploaded material becomes searchable once it has been processed

    @platform
    Scenario: Upload a text note to a topic
      When I upload the file "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements" with the content:
        """
        The finite element method divides a domain into small elements
        and approximates the solution with simple functions on each element.
        """
      Then the upload is accepted for processing
      And the material "fe-basics.txt" is eventually ready

    Scenario Outline: Only supported file types are accepted
      When I upload the file "<filename>" to "aeronautics/numerical-methods/finite-elements"
      Then the upload is <outcome>

      Examples:
        | filename     | outcome                 |
        | notes.txt    | accepted for processing |
        | notes.md     | accepted for processing |
        | lecture.pdf  | accepted for processing |
        | song.mp3     | rejected as unsupported |

    Scenario Outline: Videos are accepted
      When I upload the file "<filename>" to "aeronautics/numerical-methods/finite-elements"
      Then the upload is accepted for processing

      Examples:
        | filename     |
        | lecture.mp4  |
        | lecture.webm |

    Scenario: An empty file is rejected
      When I upload the file "empty.txt" to "aeronautics/numerical-methods/finite-elements" with no content
      Then the upload is rejected as empty

    @platform
    Scenario: A file too large to send in one piece is uploaded
      When I upload a 10 MB file "lecture-notes.pdf" to "aeronautics/numerical-methods/finite-elements"
      Then the upload is accepted for processing

    Scenario: A file larger than the upload limit is rejected
      Given the upload limit is 1 MB
      When I upload a 2 MB file "lecture-notes.pdf" to "aeronautics/numerical-methods/finite-elements"
      Then the upload is rejected as too large
      And I am told the limit is 1 MB

    Scenario Outline: Material must be uploaded to a course, a subject and a topic
      When I upload the file "notes.txt" to "<location>"
      Then the upload is rejected as having an invalid location

      Examples:
        | location                                         |
        | aeronautics                                      |
        | aeronautics/numerical-methods                    |
        | aeronautics/numerical-methods/finite-elements/2d |
        | Aeronautics/Numerical Methods/Finite Elements    |

  Rule: Material is listed grouped by course, subject and topic

    Background:
      Given I have uploaded these materials:
        | location                                           | filename          |
        | aeronautics/numerical-methods/finite-elements      | fe-basics.txt     |
        | aeronautics/numerical-methods/finite-elements      | fe-meshing.txt    |
        | aeronautics/numerical-methods/finite-differences   | fd-schemes.txt    |
        | aeronautics/aerodynamics/boundary-layers           | blasius.txt       |
        | mathematics/linear-algebra/eigenvalues             | power-method.txt  |

    @platform
    Scenario: List my courses
      When I list my courses
      Then I see the courses:
        | course      |
        | aeronautics |
        | mathematics |

    @platform
    Scenario: List the material of a course
      When I list the materials of the course "aeronautics"
      Then I see the materials:
        | subject           | topic              | filename       |
        | aerodynamics      | boundary-layers    | blasius.txt    |
        | numerical-methods | finite-differences | fd-schemes.txt |
        | numerical-methods | finite-elements    | fe-basics.txt  |
        | numerical-methods | finite-elements    | fe-meshing.txt |

    @platform
    Scenario: List the material of a single topic
      When I list the materials of "aeronautics/numerical-methods/finite-differences"
      Then I see the materials:
        | subject           | topic              | filename       |
        | numerical-methods | finite-differences | fd-schemes.txt |

  Rule: Each student sees only their own material

    @platform
    Scenario: Another student's course is not in my list
      Given the student "tom" has uploaded "rome.txt" to "history/ancient-history/rome"
      And I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      When I list my courses
      Then I see the courses:
        | course      |
        | aeronautics |

  Rule: Deleting material removes it and everything the assistant learned from it

    @platform
    Scenario: Delete a material
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      And searching "aeronautics" for "finite element" finds "fe-basics.txt"
      When I delete the material "fe-basics.txt" from "aeronautics/numerical-methods/finite-elements"
      Then the materials of "aeronautics/numerical-methods/finite-elements" are empty
      And searching "aeronautics" for "finite element" finds nothing from "fe-basics.txt"

    @platform
    Scenario: The assistant forgets what it remembered from a deleted material
      Given I have uploaded "fe-basics.txt" to "aeronautics/numerical-methods/finite-elements"
      And I have uploaded "fd-schemes.txt" to "aeronautics/numerical-methods/finite-differences"
      And the assistant remembers "struggles with shape functions" from "fe-basics.txt"
      And the assistant remembers "confuses forward and central differences" from "fd-schemes.txt"
      When I delete the material "fe-basics.txt" from "aeronautics/numerical-methods/finite-elements"
      Then the assistant no longer remembers "struggles with shape functions"
      But the assistant still remembers "confuses forward and central differences"

    Scenario: Deleting material that does not exist
      When I delete the material "missing.txt" from "aeronautics/numerical-methods/finite-elements"
      Then I am told the material was not found

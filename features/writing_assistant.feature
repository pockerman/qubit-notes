@ai
Feature: The writing assistant
  As a student writing material of my own
  I want an assistant that helps me write it, and finds and cites what it draws on from the web
  So that I can write good notes quickly, and know where what they say comes from

  The writing assistant (WriteMaterialAssistantAgent) helps an owner of a course write or edit a
  Markdown material in one of its topics. The student asks it in their own words: to write
  material on a subject they propose ("Write an introduction to the finite element method"), or
  to help with one section of the material they are writing ("Add a worked example to this
  section"), whose text it is given with the rest of what they have written so far.

  It searches the web for what it needs, unless the student says not to, and cites what it draws
  on: its reply is Markdown with numbered markers, [1], [2], …, each one of its references, given
  with their titles and addresses. A reply drawn on nothing from the web cites nothing. Follow-up
  requests can refer to the earlier ones and their replies, which the student's browser gives it
  again. The AI the student chose answers, as everywhere (see The AI's model), and what it took is
  counted in their usage as "writing". Where the AI can't search the web (on gogi), it answers
  from what it knows, and says it searched nothing.

  The replies aren't kept by the app: what the student takes of them goes into their material
  (see The writing assistant in the browser).

  Background:
    Given I am the student "maria"
    And I have created the course "aeronautics"
    And I have created the topic "numerical-methods/finite-elements" in "aeronautics"

  Rule: It writes what the student asks, from the web, citing it

    Scenario: Ask it to write material on a subject
      When I ask the writing assistant "Write an introduction to the finite element method"
      Then the writing assistant replies in Markdown
      And it searched the web for it
      And its reply cites its references by number, each with a title and an address

    Scenario: Help with a section of what I am writing
      When I ask the writing assistant "Add a worked example to this section" about the section "2 Shape functions" of:
        """
        # 1 Introduction
        The finite element method divides a domain into small elements.

        # 2 Shape functions
        Shape functions interpolate the solution inside each element.
        """
      Then the writing assistant replies in Markdown
      And it was given the section "2 Shape functions" to help with
      And it was given what I have written so far

    Scenario: It is told the course and the topic being written in
      When I ask the writing assistant "Write an introduction to the finite element method"
      Then it was told the material is for "Aeronautics" › "Numerical methods" › "Finite elements"

    Scenario: A follow-up refers to the earlier request
      Given I have asked the writing assistant "Write an introduction to the finite element method"
      When I ask the writing assistant "Make it shorter" after that
      Then it was given my earlier request and its reply

    Scenario: Without searching the web
      When I ask the writing assistant "Write an introduction to the finite element method", not searching the web
      Then the writing assistant replies in Markdown
      And it didn't search the web
      And its reply cites nothing

    Scenario: Where the AI can't search the web
      Given the AI can't search the web
      When I ask the writing assistant "Write an introduction to the finite element method"
      Then the writing assistant replies in Markdown
      And it didn't search the web
      And its reply cites nothing

    Scenario: What it takes is counted in my usage
      When I ask the writing assistant "Write an introduction to the finite element method"
      Then my AI usage has "writing"

  Rule: It helps the owners of the course write in it

    Scenario: A reader can't write in the course
      Given I have shared the course "aeronautics" with "tom" as a reader
      When the student "tom" asks the writing assistant "Write an introduction" in "aeronautics/numerical-methods/finite-elements"
      Then the writing assistant is refused, as only owners write material

    Scenario: A topic there isn't
      When I ask the writing assistant "Write an introduction" in "aeronautics/numerical-methods/meshing"
      Then the writing assistant is refused as not found

    Scenario: It needs something to do
      When I ask the writing assistant nothing
      Then I am told to ask the writing assistant something

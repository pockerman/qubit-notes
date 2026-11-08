Feature: Running Python programs
  As a student of Python
  I want to run Python programs from the app
  So that I can try out what I am learning as I read

  A student's program is run by the Python interpreter in a sandbox of its own, thrown away
  afterwards, as Go programs are (see Running Go programs): no network, an unprivileged user, and
  limits on its memory, CPU, processes, files and time. Only the standard library is there. They
  get what the interpreter or the program printed, and how it ended. A program can be at most
  64 KB, and only a few programs, of any language, run at a time. Programs are run only where the
  app is set up for them (QUBIT_NOTES_PYTHON_RUNNER=docker); elsewhere the app says so. Only
  signed-in students run programs.

  Background:
    Given I am the student "maria"

  Rule: Where the app can run programs, a student's program is run

    Background:
      Given the app can run Python programs

    Scenario: Run a program
      When I run the Python program:
        """
        print("hello")
        """
      Then the program printed "hello"
      And it ended with the exit code 0

    Scenario: A program that fails
      When I run the Python program:
        """
        undefined()
        """
      Then the program printed "NameError"
      And it ended with the exit code 1

    Scenario: A program that doesn't end is stopped
      When I run the Python program:
        """
        while True:
            pass
        """
      Then I am told the program ran out of time

    Scenario: Nothing to run
      When I run the Python program:
        """

        """
      Then I am told to write a Python program to run

    Scenario: A program that is too large
      When I run a Python program of 65 KB
      Then I am told a Python program can be at most 64 KB
      And no program was run

    Scenario: Too many programs at once
      Given as many programs are running as the app allows
      When I run the Python program:
        """
        print("hello")
        """
      Then I am told other programs are running
      And no program was run

    Scenario: Only signed-in students run programs
      When someone who isn't signed in runs a Python program
      Then they are refused
      And no program was run

  Rule: Where the app can't, it says so

    Scenario: The app isn't set up to run programs
      When I run the Python program:
        """
        print("hello")
        """
      Then I am told Python programs can't be run here

Feature: Running C++ programs
  As a student of C++
  I want to compile and run C++ programs from the app
  So that I can try out what I am learning as I read

  A student's program is compiled by g++, as C++20, and run in a sandbox of its own, thrown away
  afterwards, as Go programs are (see Running Go programs): no network, an unprivileged user, and
  limits on its memory, CPU, processes, files and time, which is for compiling and running both.
  Only the standard library is there. They get what the compiler or the program printed, and how
  it ended. A program can be at most 64 KB, and only a few programs, of any language, run at a
  time. Programs are run only where the app is set up for them (QUBIT_NOTES_CPP_RUNNER=docker);
  elsewhere the app says so. Only signed-in students run programs.

  Background:
    Given I am the student "maria"

  Rule: Where the app can run programs, a student's program is run

    Background:
      Given the app can run C++ programs

    Scenario: Run a program
      When I run the C++ program:
        """
        #include <iostream>

        int main() {
            std::cout << "hello" << std::endl;
        }
        """
      Then the program printed "hello"
      And it ended with the exit code 0

    Scenario: A program that doesn't compile
      When I run the C++ program:
        """
        int main() {
            undefined();
        }
        """
      Then the program printed "'undefined' was not declared in this scope"
      And it ended with the exit code 1

    Scenario: A program that doesn't end is stopped
      When I run the C++ program:
        """
        int main() {
            while (true) {}
        }
        """
      Then I am told the program ran out of time

    Scenario: Nothing to run
      When I run the C++ program:
        """

        """
      Then I am told to write a C++ program to run

    Scenario: A program that is too large
      When I run a C++ program of 65 KB
      Then I am told a C++ program can be at most 64 KB
      And no program was run

    Scenario: Only signed-in students run programs
      When someone who isn't signed in runs a C++ program
      Then they are refused
      And no program was run

  Rule: Where the app can't, it says so

    Scenario: The app isn't set up to run programs
      When I run the C++ program:
        """
        int main() {}
        """
      Then I am told C++ programs can't be run here

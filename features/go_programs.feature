Feature: Running Go programs
  As a student of Go
  I want to run Go programs from the app
  So that I can try out what I am learning as I read

  A student's program is compiled and run in a sandbox of its own, thrown away afterwards: no
  network, an unprivileged user, and limits on its memory, CPU, processes, files and time. They
  get what the compiler or the program printed, and how it ended. A program can be at most 64 KB,
  and only a few run at a time. Programs are run only where the app is set up for them
  (QUBIT_NOTES_GO_RUNNER=docker); elsewhere the app says so. Only signed-in students run programs.

  Background:
    Given I am the student "maria"

  Rule: Where the app can run programs, a student's program is run

    Background:
      Given the app can run Go programs

    Scenario: Run a program
      When I run the Go program:
        """
        package main

        import "fmt"

        func main() {
          fmt.Println("hello")
        }
        """
      Then the program printed "hello"
      And it ended with the exit code 0

    Scenario: A program that doesn't compile
      When I run the Go program:
        """
        package main

        func main() {
          undefined()
        }
        """
      Then the program printed "undefined: undefined"
      And it ended with the exit code 1

    Scenario: A program that doesn't end is stopped
      When I run the Go program:
        """
        package main

        func main() {
          for {
          }
        }
        """
      Then I am told the program ran out of time

    Scenario: Nothing to run
      When I run the Go program:
        """

        """
      Then I am told to write a Go program to run

    Scenario: A program that is too large
      When I run a Go program of 65 KB
      Then I am told a Go program can be at most 64 KB
      And no program was run

    Scenario: Too many programs at once
      Given as many programs are running as the app allows
      When I run the Go program:
        """
        package main
        """
      Then I am told other Go programs are running
      And no program was run

    Scenario: Only signed-in students run programs
      When someone who isn't signed in runs a Go program
      Then they are refused
      And no program was run

  Rule: Where the app can't, it says so

    Scenario: The app isn't set up to run programs
      When I run the Go program:
        """
        package main
        """
      Then I am told Go programs can't be run here

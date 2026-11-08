Feature: Running SQL
  As a student of databases
  I want to run SQL from the app
  So that I can try out queries as I read about them

  A student's SQL is run by SQLite, on a database of its own in memory that starts empty and is
  thrown away afterwards, in a sandbox like that of Go programs (see Running Go programs). It is
  run in SQLite's safe mode, so nothing typed reaches files or a shell. What a query returns is
  printed as a table, and the first error stops it. A program can be at most 64 KB, and only a few
  programs, of any language, run at a time. SQL is run only where the app is set up for it
  (QUBIT_NOTES_SQL_RUNNER=docker); elsewhere the app says so. Only signed-in students run it.

  Background:
    Given I am the student "maria"

  Rule: Where the app can run SQL, a student's SQL is run

    Background:
      Given the app can run SQL programs

    Scenario: Run a query
      When I run the SQL program:
        """
        SELECT 'hello';
        """
      Then the program printed "hello"
      And it ended with the exit code 0

    Scenario: An error stops it
      When I run the SQL program:
        """
        SELECT nope;
        """
      Then the program printed "no such column: nope"
      And it ended with the exit code 1

    Scenario: A query that doesn't end is stopped
      When I run the SQL program:
        """
        WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT count(*) FROM c;
        """
      Then I am told the program ran out of time

    Scenario: Nothing to run
      When I run the SQL program:
        """

        """
      Then I am told to write a SQL program to run

    Scenario: Only signed-in students run SQL
      When someone who isn't signed in runs a SQL program
      Then they are refused
      And no program was run

  Rule: Where the app can't, it says so

    Scenario: The app isn't set up to run SQL
      When I run the SQL program:
        """
        SELECT 1;
        """
      Then I am told SQL programs can't be run here

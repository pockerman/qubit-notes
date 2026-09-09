# qubit-note: Distributed Systems | Data & Databases | SQL Isolation Levels

## Overview

SQL isolation levels are predefined settings (such as Read Committed, Repeatable Read, and Serializable) that determine how strictly transactions are kept separate from each other, with each level preventing certain concurrency anomalies like dirty reads, non-repeatable reads, and phantom reads.


## SQL Isolation Levels

In database systems, an isolation level refers to the degree to which one transaction is isolated from the effects of other concurrent transactions.

It defines how and when the changes made by one transaction become visible to others, ensuring data consistency and integrity.

Isolation is the “I” in the 
ACID
properties of transactions (Atomicity, Consistency, Isolation, Durability) and is crucial for maintaining correctness in concurrent environments.

However, there is a trade-off between isolation and performance. Lower isolation levels allow more concurrent access (higher throughput) but risk more anomalies (inconsistent reads), while higher isolation levels reduce such anomalies at the cost of more blocking or waiting between transactions.

In simple terms, relaxed isolation = higher concurrency + potential inconsistencies, whereas strict isolation = fewer anomalies + potential slowdown.

Choosing the right level is about balancing accuracy vs. performance for your application’s needs.

Standard SQL Isolation Levels: The ANSI SQL standard defines four isolation levels in increasing order of strictness: Read Uncommitted, Read Committed, Repeatable Read, and Serializable.

(Many database systems provide these or similar levels. For instance, PostgreSQL’s default is Read Committed, while MySQL’s InnoDB engine defaults to Repeatable Read.)

The higher the level, the more types of inconsistent outcomes (“anomalies”) are prevented.

Below, we explain the major isolation levels, Read Committed, Repeatable Read, and Serializable and the anomalies each one addresses.

Common Data Anomalies in Concurrent Transactions
When transactions run concurrently, several types of anomalies (unexpected or incorrect behaviors) can occur if isolation is insufficient.

The main anomalies that isolation levels deal with include:

Dirty Read: This occurs when a transaction reads data that has been written by another transaction that has not yet committed. In other words, a transaction sees uncommitted changes from a concurrent transaction. If that other transaction rolls back, the first transaction would have read data that “never officially existed,” leading to inconsistencies.

Non-Repeatable Read: This happens when a transaction reads the same row twice and gets different values each time because another transaction modified that data and committed in between the two reads. The data “did not repeat”. What was true a moment ago has changed when read again within the same transaction.

Phantom Read: This occurs when a transaction re-executes a query returning a set of rows (e.g. “SELECT * FROM ... WHERE condition”) and finds that new rows satisfying the condition have appeared (or some have disappeared) due to another transaction’s commit. The second read sees a “phantom” row that wasn’t there before, because another transaction inserted or deleted data in the interim.

Each isolation level places certain restrictions on concurrent reads/writes to prevent some of these anomalies.

Below we describe the levels in detail and note which anomalies are prevented at each level.

Read Committed Isolation Level
Read Committed is one of the most commonly used isolation levels (the default in many systems, like Oracle and PostgreSQL) because it strikes a balance between consistency and performance.

At this level, a transaction sees only data that has been committed by other transactions at the moment it is read.

In practical terms, dirty reads are prevented, You cannot read uncommitted (dirty) data from another concurrent transaction. Each query in a transaction will get the most recently committed data as of the start of that query.

However, Read Committed does not guarantee repeatable reads within the same transaction.

If another transaction commits a change after you’ve read some data, a subsequent read of that same data in your transaction can return a new value. This means non-repeatable reads are possible at Read Committed.

Phantom reads are also possible, since range of data can change between two queries.

Anomalies prevented: Dirty reads (you will never read inconsistent, uncommitted data).
Anomalies possible: Non-repeatable reads and phantom reads may occur.

Repeatable Read Isolation Level
Repeatable Read is a stricter isolation level that ensures that if a transaction reads data twice, it will see the same values each time, assuming it hasn’t modified that data itself.

In other words, once data is read in a transaction, no other transaction can modify that data until the first transaction completes, guaranteeing repeatable reads (no inconsistent re-reads).

This is often implemented by keeping read locks on rows or by using a snapshot of the data.

As a result, dirty reads and non-repeatable reads are prevented under Repeatable Read.

However, phantom reads can still occur in the standard definition of Repeatable Read.

Another transaction might insert or delete rows that satisfy a query’s WHERE condition.

Since Repeatable Read (in the SQL standard) does not necessarily lock the range of possible rows (no range-locking), a re-executed query could see new “phantom” rows.

Anomalies prevented: Dirty reads and non-repeatable reads are not possible (the data you read won’t magically change on you within the transaction).
Anomalies possible: Phantom reads are still possible and another transaction could add or remove rows that affect a query’s results.


Serializable Isolation Level
Serializable is the highest (strictest) isolation level.

A serializable execution of transactions is one in which the outcome is as if the transactions ran one by one in some serial order, rather than interleaved.

In effect, Serializable isolation prevents all the anomalies we described: no dirty reads, no non-repeatable reads, and no phantom reads occur.

Serializable provides the strongest guarantee of consistency, and it is the closest to truly “ACID” isolation.

Under Serializable, the database’s concurrency control (through locking or multiversioning with validation) will ensure that any sequence of concurrent transactions yields the same result as some sequential execution.

If the system detects a potential conflict that could result in an anomaly (e.g. a phantom), it will typically block one transaction or roll it back with a serialization error to maintain consistency. This level therefore sacrifices a lot of concurrency; transactions might have to wait or retry, but integrity is preserved as if transactions executed one at a time.



Anomalies prevented: Dirty reads, non-repeatable reads, and phantom reads are all prevented – no inconsistent reads or phantoms occur at Serializable. All transactions appear fully isolated.
Anomalies possible: None of the standard read anomalies are allowed; effectively, Serializable = no anomalies (it even prevents more subtle anomalies like write skew, depending on the implementation). If a schedule of transactions can’t be serialized, the DBMS will not let it complete.

Each higher isolation level includes the guarantees of the levels below it and adds protection against additional anomalies.

For example, Repeatable Read does everything Read Committed does and also ensures repeatable reads; Serializable does everything Repeatable Read does and also prevents phantoms.

It’s important to choose an isolation level based on application needs: use the lowest level that safely handles your use-case to avoid unnecessary performance costs.

For many applications, Read Committed is sufficient, providing a good balance of consistency (no dirty reads) and concurrency. In high-integrity systems (financial, etc.), Serializable might be warranted despite the performance hit, to ensure absolutely correct results.



## Summary

## References


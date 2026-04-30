# qubit-note: Distributed Systems Series | Data Replication Part 6 | PACELC, CAP and CALM Theorems 


## Overview

In this note we will look into three theorems that aapply to distributed systems. Specifically, we will look into

- <a href="https://en.wikipedia.org/wiki/CAP_theorem">CAP theorem</a>
- <a href="https://en.wikipedia.org/wiki/PACELC_design_principle">PACELC design principle</a>
- <a href="https://cacm.acm.org/research/keeping-calm/">Keeping CALM: When Distributed Consistency Is Easy</a>

**keywords** CAP-theorem, PACELC-theorem, CALM-theorem, System-design, Data-replication, Distributed-system

## PACELC, CAP and CALM Theorems 

Let's start with the CAP theorem. 

### CAP theorem

According to [1]:

_In database theory, the CAP theorem, also named Brewer's theorem after computer scientist Eric Brewer, states that any distributed data store can provide at most two of the following three guarantees:_

- Consistency
- Availability
- Partition tolerance

Let's see what these terms mean. 

**Consistency**

Every read receives the most recent write or an error. Consistency means that all clients see the same data at the same time, no matter which node they connect to. For this to happen, whenever data is written to one node, it must be instantly forwarded or replicated to all the other nodes in the system before the write is deemed successful. Consistency as defined in the CAP theorem is quite different from the consistency guaranteed in ACID database transactions.

**Availability** 

Every request received by a non-failing node in the system must result in a response, without the guarantee that it contains the most recent version of the data. 
Note that the availability as defined in CAP theorem is different from high availability in software architecture [1].

**Partition tolerance**

The system continues to operate despite an arbitrary number of messages being dropped (or delayed) by the network between nodes.

Given that network partitions are given when working with distributed systems, we essentially need to choose between availability and consistency.

----
**Remark**

We will see below, see CALM theorem, that a monotonic program can achieve all three i,e, consistency, availability and partition tolerance all at once.

----

### PACELC theorm

The CAP theorem is useful in understanding requierements on a distributed system. However, the PACELC theorem offers a more comprehensive farmework and can be seen as an extension of the CAP theorem.
The theorem states that in the event of a network partition (P), a system must choose between availability (A) and consistency (C), as defined by the CAP theorem; however, in normal operation without partitions (E), the system must choose between latency (L) and consistency (C).
The PACELC theorem extends the CAP theorem by acknowledging that latency and consistency trade-offs are present even when the system is functioning normally, not just during network failures [2].

The PACELC theorem was first described by Daniel J. Abadi in 2010 and formally proved in 2018.
It introduces four primary configurations [2]: 

- PA/EL prioritize availability and low latency over consistency 
- PA/EC availability during partitions, consistency otherwise
- PC/EL consistency during partitions, lower latency otherwise 
- PC/EC consistency at all times

Systems like Amazon DynamoDB, Cassandra, and Riak are classified as PA/EL, meaning they prioritize availability and low latency during partitions and also sacrifice consistency for lower latency in normal operation.
In contrast, fully ACID-compliant systems such as VoltDB/H-Store, MySQL Cluster, and PostgreSQL are PC/EC, ensuring consistency at all times, even at the cost of availability and latency.
The theorem is particularly relevant for designing cloud applications and systems operating in intermittently connected environments, such as IoT and mobile applications, where both partition and non-partition trade-offs must be considered.


### CALM theorem


The CALM theorem, standing for Consistency as Logical Monotonicity, establishes that a program can achieve consistent, coordination-free distributed implementation if and only if it is expressible in monotonic logic [3].
 
A monotonic program is considered _safe_  when information i.e. their outputs grow or remain unchanged as new data arrives, allowing them to proceed without coordination [3].
In contrast, in non-monotonic programs, a property can change when new information arrives and thus require runtime coordination to ensure consistent outcomes.
This theorem shifts the focus from traditional storage consistency models to program-level properties, enabling static analysis and reducing reliance on expensive runtime enforcement mechanisms like two-phase commit or Paxos. The CALM Theorem has inspired new programming language designs, such as Bloom, and tools that help developers build systems that are both highly available and consistent by identifying and isolating non-monotonic components.

## Summary

This qubit note surveys three foundational theorems: CAP, PACELC, and CALM. These theorems explain fundamental trade-offs in distributed system design. The CAP theorem states that in the presence of network partitions a system must choose between consistency and availability, clarifying the specific meanings of these guarantees in a distributed context. The PACELC theorem as an extension of CAP, highlights that systems face trade-offs not only during partitions (availability vs. consistency) but also during normal operation (latency vs. consistency), and categorizing real-world systems based on these choices. Finally, the CALM theorem is discussed as a complementary perspective, showing that programs expressed with monotonic logic can achieve consistency, availability, and partition tolerance without coordination, shifting the focus from storage-level guarantees to program-level properties and influencing modern distributed system design and languages.

## References

1. <a href="https://en.wikipedia.org/wiki/CAP_theorem">CAP theorem</a>
2. <a href="https://en.wikipedia.org/wiki/PACELC_design_principle">PACELC design principle</a>
3. <a href="https://cacm.acm.org/research/keeping-calm/">Keeping CALM: When Distributed Consistency Is Easy</a>

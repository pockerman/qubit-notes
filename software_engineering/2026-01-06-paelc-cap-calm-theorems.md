# qubit-note: Distributed Systems Series | Data Replication Part 6 | PACELC, CAP and CALM Theorems 


## Overview

In this note we will look into three theorems that aapply to distributed systems. Specifically, we will look into

- <a href="https://en.wikipedia.org/wiki/CAP_theorem">CAP theorem</a>
- <a href="https://cacm.acm.org/research/keeping-calm/">Keeping CALM: When Distributed Consistency Is Easy</a>

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

Every request received by a non-failing node in the system must result in a response, without the guarantee that it contains the most recent version of the data. This is the definition of availability in CAP theorem as defined by Gilbert and Lynch.[1] Availability as defined in CAP theorem is different from high availability in software architecture.

**Partition tolerance**

The system continues to operate despite an arbitrary number of messages being dropped (or delayed) by the network between nodes.

Given that network partitions are given when working with distributed systems, we essentially need to choose between availability and consistency.

----
**Remark**

We will see below, see CALM theorem, that a monotonic program can achieve all three i,e, consistency, availability and partition tolerance all at once.

----

### PACELC theorm


### CALM theorem


The CALM theorem, standing for Consistency as Logical Monotonicity, establishes that a program can achieve consistent, coordination-free distributed implementation if and only if it is expressible in monotonic logic.
 Monotonic programs are "safe" in the face of missing information, meaning their outputs grow or remain unchanged as new data arrives, allowing them to proceed without coordination.
 In contrast, non-monotonic programs, where the truth of a property can change with new information, require runtime coordination to ensure consistent outcomes.
 This theorem shifts the focus from traditional storage consistency models to program-level properties, enabling static analysis and reducing reliance on expensive runtime enforcement mechanisms like two-phase commit or Paxos.
 The CALM Theorem has inspired new programming language designs, such as Bloom, and tools that help developers build systems that are both highly available and consistent by identifying and isolating non-monotonic components.

 A


## Summary

## References

1. <a href="https://en.wikipedia.org/wiki/CAP_theorem">CAP theorem</a>
3. <a href="https://cacm.acm.org/research/keeping-calm/">Keeping CALM: When Distributed Consistency Is Easy</a>

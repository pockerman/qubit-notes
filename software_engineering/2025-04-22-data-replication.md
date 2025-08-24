# qubit-note: Data Replication


## Overview

In this qubit note I go over data replication. This is a process whereby copies of the data are created and stored.
Data replicatin improves both system availability and reliability

**keywords** system-design, software-architecture, data-patterns, data-replication

## Data replication


Data replication is the process of creating and maintaining multiple copies of the same data across different locations, systems, or servers to improve data availability, reliability, performance, and fault tolerance. The purpose of data replication is to:

- Ensure data availability even if one server or system fails.
- Improve read performance by distributing queries across replicas.
- Facilitate disaster recovery and backup.

There are two main replication approaches; synchronous and asynchronous.
In synchronous replication, the data is copied to replicas instantly (in real-time). In fact, with synchronous replication, an operation is incomplete until the data has been copied and acknowledgments have been received from all the participating nodes [1]. This ensures consistency but can potentially add latency.
On the other hand, in asynchronous replication the data is copied with a delay. This allows for faster responses, but replicas may temporarily hold outdated data.

We can also distinguish replication strategies based on the number of leader nodes [1]. 
Typically, in systems with leadership, the leading nodes are capable of handling read/write requests. On the other hand, following nodes are mainly restricted to serving read requests.
Based on this strategy, we can distinguish the following configurations [1]:


- Single leader systems
- Multi-leader systems
- Leader-less systems

In a single leader system there is just one leading node that coordinates the operation.
The leader accepts requests and propagates these to the followers. This is a simple configuration 
but given that poses a single point of failure, SPF, it can invalidate the point or replications.
Multi-leader systems have more than one node as a leader. Although this avoids SPF, conflicts may arise that require resolution [1].
Finally, in leader-less systems,there is no leader node that coordinates operations. Hence all participating nodes can accept read/write operations.
Just like with multi-leader systems, this creates conflicts that we need to address. A number of conflict resolution strategies exist:

- Last-Write-Wins (LWW)
- Version Vectors (or Vector Clocks)
- Operational Transformation (OT)
- Conflict-free Replicated Data Types (CRDTs)



## Summary

Data replication is the process of maintaining multiple copies of the same data across different locations or servers to enhance availability, reliability, performance, and fault tolerance. It can be performed synchronously, ensuring consistency at the cost of latency, or asynchronously, which offers faster responses but may lead to temporary inconsistencies. Replication strategies also differ based on leadership models, including single-leader systems (simpler but with a single point of failure), multi-leader systems (more resilient but prone to conflicts), and leader-less systems (fully distributed but requiring robust conflict resolution). Common conflict resolution methods include Last-Write-Wins, version vectors, operational transformation, and conflict-free replicated data types (CRDTs).


## References

1. Dominik Tornow, _Think Distributed Systems_, Manning Publications


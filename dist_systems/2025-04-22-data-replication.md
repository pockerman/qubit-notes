# qubit-note: Distributed Systems Series | Data Replication Part 1


## Overview

Data replicaiton is one of the techniques we can employ in order to improve the latency and availability of a distributed system [2].
in this series of notes we go ove the essential elements of data replication. Specifically we discuss the following ideas:

- Replication strategies (see below)
- <a href="2025-12-30-state-machine-replication.md">State machine replication</a>
- <a href="2025-12-31-consensus.md">Consensus</a>
- <a href="2026-01-05-broadcast-protocols.md">Boradcast protocols</a>
- <a href="2026-01-06-paelc-cap-calm-theorems.md">PACELC, CAP and CALM theorems</a>

In this qubit note series I go over data replication. This is a process whereby copies of the data are created and stored.
Data replicatin improves both system availability and reliability. In this part of the series we will discuss what data replication is
and expand over some common replication strategies

**keywords** System-design, Software-architecture, Data-replication, Distributed-system

## Data replication

Let's start by giving a definition of what data repliaction is. As the name implies, data replication is the process of creating and maintaining multiple copies of the same data across different locations, systems, or servers.

You may ask yourself why exactly do we need data replication. As already mentioned, data replication improves the availability, the reliability, the performance, and fault tolerance of a distributed system. It's easy to understand why. Storing data on single machine essentially introduces a single point of failure (SPD). Thus data replication allows us to overcome the consequences associate with
SPF. Cen

However, data replication is not easy primarily because we need to ensure consistency of the data. Consistency models, such as eventual consistency, and data replication algorithms, like Raft,
play a key role in data replication [3]. Central also to the discussion of replication is _replication transparency_ i.e. the ability of the system to hide the existence of multiple objects providing the
illusion of a single object [1].

### Replication strategies

Let's discuss replication strategies. There are two main replication approaches; synchronous and asynchronous.
In synchronous replication, the data is copied to replicas instantly (in real-time). In fact, with synchronous replication, an operation is incomplete until the data has been copied and acknowledgments have been received from all the participating nodes [1]. This ensures consistency but can potentially add latency.
On the other hand, in asynchronous replication the data is copied with a delay. This allows for faster responses, but replicas may temporarily hold outdated data.
In practice, we can use a hybrid approach where a majority number of nodes has to acknowledge the operation. This majority is often called a quorum [1].
The rest of the replicas can continue asynchronously with the operation.

On top of the synchronous/asynchronous strategies, we have strategies based on the participating nodes.
Based on this strategy, we can distinguish the following configurations [1]:

- Single leader systems
- Multi-leader systems
- Leader-less systems

Typically, in systems with leadership, the leading nodes are capable of handling read/write requests. 
On the other hand, following nodes are mainly restricted to serving read requests.
Specifically, in a single leader system there is just one leading node that coordinates the operation.
The leader accepts requests and propagates these to the followers. This is a simple configuration 
but given that poses an SPF, it can invalidate the point of replication.
Multi-leader systems have more than one node as a leader. Although this avoids SPF, conflicts may arise that require resolution [1].
Finally, in leader-less systems,there is no leader node that coordinates operations. Hence all participating nodes can accept read/write operations.
Just like with multi-leader systems, this creates conflicts that we need to address. A number of conflict resolution strategies exist:

- Last-Write-Wins (LWW)
- Version Vectors (or Vector Clocks)
- Operational Transformation (OT)
- Conflict-free Replicated Data Types (CRDTs)

We will discuss these strategies further in the series. The next part will discuss <a href="2025-04-28-consistency-models.md">consistency models</a>


## Summary

Data replication is the process of maintaining multiple copies of the same data across different locations or servers to enhance availability, reliability, performance, and fault tolerance. It can be performed synchronously, ensuring consistency at the cost of latency, or asynchronously, which offers faster responses but may lead to temporary inconsistencies. Replication strategies also differ based on leadership models, including single-leader systems (simpler but with a single point of failure), multi-leader systems (more resilient but prone to conflicts), and leader-less systems (fully distributed but requiring robust conflict resolution). Common conflict resolution methods include Last-Write-Wins, version vectors, operational transformation, and conflict-free replicated data types (CRDTs).


## References

1. Dominik Tornow, _Think Distributed Systems_, Manning Publications
2. Pekka Enberg, _Latency Reduce delay in software systems_ Manning Publications
3. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
4. <a href="https://milvus.io/ai-quick-reference/what-are-some-methods-for-conflict-resolution-in-distributed-databases">What are some methods for conflict resolution in distributed databases?</a>


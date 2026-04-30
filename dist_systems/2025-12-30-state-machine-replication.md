# qubit-note: Distributed Systems Series | Data Replication Part 3 | State Machine Replication

## Overview

In this qubit-note we will discuss <a href="https://en.wikipedia.org/wiki/State_machine_replication">state machine replication</a>.
This is a technique used to implement   a fault-tolerant service by replicating servers and coordinating client interactions with server replicas. 
However, it also provides a framework for understanding and designing replication management protocols [1]. It is therefore, very relevant to the
discussion of data replication. In fact, Raft replication algorithm is based on state machine replication [2].

State machine replication works uner a simple principle; if two identical, deterministic processes begin in the same state and receive the same inputs in the same order, they will
produce the same output and reach the same state [4].

All in all, for our purposes we can view state machine replication as another replication strategy (see <a href="2025-04-22-data-replication.md">qubit-note: Distributed Systems Series | Data Replication Part 1</a>).

**keywords** System-design, Software-architecture, Data-replication, Distributed-system, State-machine-replication

## State machine replication

State machine replication is a technique for implementing fault-tolerant systems. However, it can also be used
for implementing replication protocols. Actually, many distributed SQL databases and key–value stores use state machine replication to implement replication
across multiple nodes [3].

In state machine replication, when a client sends a request to a node and the request is 
acknowledged, then the effect of the request on the system state is persistent, even if some components fail.
When a
node accepts a client request, any subsequent requests to any other node in the cluster
are guaranteed to see any updates caused by the request, providing a linearizability guarantee [3].

In order to achieve fault tolerance, the cluster has to be able to guarantte that a number of
nodes can fail without disruption. This depends both on the size of the cluster as well as the 
type of failures it can handle [3]. As a general rule, the larger the cluster, the more failures it can tolerate, the
more complex it is to operate, the higher the latency, and the higher the associated cost.

Assuming non-Byzantine failures; i.e. network partitions, disk crashes, then a cluster can tolerate
$f$ failures if it has a total of $2f + 1$ replicas [2,3].
For example, if you have five nodes in your cluster, two of them can fail. This is because the remaining nodes can form a _quorum_ of
$f + 1$, which is the minimum number of nodes required to maintain consistency and availability [3].
Note, however, that the minimum cluster size for creating a quorum is three nodes. Hence, the minimum cluster size for fault-tolerant systems is three [3]

You can implement state machine replication using algorithms like [3]:

- <a href="https://en.wikipedia.org/wiki/Paxos_(computer_science)">Paxos</a>
- <a href="https://en.wikipedia.org/wiki/Raft_(algorithm)">Raft</a>
- <a href="https://brooker.co.za/blog/2014/05/19/vr.html">Viewstamped Replication</a>


State machine replication is a replication approach that guarantees all nodes in a distributed system maintain the same state by executing the same commands in the same order [3]. 
Unlike traditional replication, which focuses on data or service duplication for availability or load balancing without strict state consistency, state machine replication enforces a consistent global state across nodes. It achieves this by using consensus algorithms to agree on the order of commands, even in the presence of failures or network partitions. This provides strong consistency and fault tolerance but introduces additional latency, a tradeoff that is examined in the context of the Viewstamped Replication algorithm [3].

There are many open-source projects that implement state machine replication and expose APIs on top of it; <a href="https://etcd.io/">etcd</a> and <a href="https://zookeeper.apache.org/">Apache Zookeper</a>

## Summary

his qubit-note discusses state machine replication (SMR), a technique for building fault-tolerant systems by replicating servers and coordinating client interactions with replicas. SMR is widely used in distributed databases and key-value stores to ensure consistent replication across nodes. When a client request is acknowledged by a node, its effect on the system state is persistent, and subsequent requests to other nodes see the update, providing linearizability.

Fault tolerance in SMR depends on cluster size and failure type. For non-Byzantine failures (e.g., network partitions, disk crashes), a cluster with 
$2f+1$ replicas can tolerate $f$ failures, forming a quorum of $f+1$ nodes to maintain consistency. The minimum cluster size for fault-tolerant systems is three.

SMR relies on consensus algorithms to maintain a consistent global state across all nodes by executing the same sequence of commands in the same order, even under failures or network partitions. Popular algorithms for implementing SMR include Paxos, Raft, and Viewstamped Replication. While SMR provides strong consistency and fault tolerance, it comes with a latency tradeoff compared to traditional replication strategies.

In the next post we will talk about <a href="2025-12-31-consensus.md">qubit-note: Distributed Systems Series | Data Replication Part 4 | Consensus</a>

## References

1. <a href="https://en.wikipedia.org/wiki/State_machine_replication">state machine replication</a>
2. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_,
3. Pekka Enberg, _Latency Reduce delay in software systems_ Manning Publications
4. Dominik Tornow, _Think Distributed Systems_, Manning Publications

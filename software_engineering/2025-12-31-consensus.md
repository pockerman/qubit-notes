# qubit-note: Distributed Systems Series | Data Replication Part 4 | Consensus

## Overview

In this qubit-note we will discuss <a href="https://en.wikipedia.org/wiki/Consensus_(computer_science)">consensus</a> in a distributed system. Consensus has many applications e.g.
a set of processes deciding on which one should hold a lock or commit a transaction [2]. State machine replication
we discussed in <a href="2025-12-30-state-machine-replication.md">State machine replication</a> poses a solution
to the consensus problem.

**keywords** System-design, Software-architecture, Data-replication, Distributed-system, Consensus


## Consensus

Let's start by first understanding what the consensus problem is all about. The consensus problem in distributed systems is the challenge of getting a group of independent computers (nodes) to agree on a single value or decision, even when some of them may fail or messages may be delayed or lost. In other words we require a set of processes to agree on a value so that [2]:

- fault-tolerance is maintained
- every non-faulty process eventually agrees on a value
- the final decision of every non-faulty process is the same everywhere
- the value that is agreed has been proposed by a process

State machine replication can used to solve the consensus problem; propose values to the leader node and chose the first one
to be durably replicated to the followers [2]. There are many open-source projects that implement state machine replication and expose APIs on top of it; <a href="https://etcd.io/">etcd</a> and <a href="https://zookeeper.apache.org/">Apache Zookeper</a>


When components are not not subject to failure, achieving consensus is trivial. However, in practice components
do fail and the network may reorder, delay, lose, or duplicate messages. Solving the consensus problem under these conditions
is not easy anymore [3]. Consensus however is very signficiant in the context of distributed systems as it enables processes to advance in lockstep, ensuring fault tolerance by allowing the
group to compensate for any failed member [3].

So how do we implement consensus? One approach is to use leader-based consensus. This is what  algorithms, such as Multi-Paxos, Raft, or Viewstamped Replication do [3].
Another approach is to use quorum-based consensus. We can also combine leader-based and quorum based approaches [3].



## Summary

This qubit-note introduces the consensus problem in distributed systems, which is the challenge of ensuring that multiple independent nodes agree on a single decision despite failures, message delays, or losses. Consensus is essential for tasks such as lock acquisition, transaction commits, and data replication.

The post outlines the core properties of consensus: fault tolerance, eventual agreement among all non-faulty processes, a single consistent decision across the system, and the guarantee that the agreed value was proposed by a participating process. It highlights state machine replication as a practical way to solve consensus, where proposed values are ordered and durably replicated—an approach used by systems like etcd and Apache ZooKeeper.

While consensus is trivial in failure-free environments, real-world distributed systems must handle crashes and unreliable networks, making the problem significantly harder. The note emphasizes the importance of consensus in enabling coordinated progress and fault tolerance. Finally, it briefly introduces common implementation strategies, including leader-based algorithms (such as Paxos, Raft, and Viewstamped Replication), quorum-based approaches, and hybrids that combine both techniques.

## References

1. <a href="https://en.wikipedia.org/wiki/Consensus_(computer_science)">Consensus</a>
2. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
3. Dominik Tornow, _Think Distributed Systems_, Manning Publications






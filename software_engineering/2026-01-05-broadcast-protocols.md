# qubit-note: Distributed Systems Series | Data Replication Part 5 | Broadcast Protocols


## Overview

<a href="2025-12-30-state-machine-replication.md">State machine replication</a> protocols like Raft require two main components [1]:

- A <a href="https://en.wikipedia.org/wiki/Broadcasting_(networking)">broadcast protocal</a>
- A function that handles the updates on each replica

In this note we will discuss broadcast protocols.

**keywords** Boradcast-protocol, System-design, Data-replication, Distributed-system

## Broadcast Protocols

We are aware of point-to-point or uncast communication protocols like TCP. This is the protocol that is mostly utilised over the the internet.
However, with data replication we are interested into delivering a message to a group of processes thus in this scenario we are mostly interested
in multicast protocols. 

There are various such protocols see e.g. [1]:

- Best-effort broadcast
- Reliable broadcast
- Eager reliable broadcast
- Gossip broadcast protocol

These protocols typically do not make any guarantees about the order to the messages in many cases though this is also required.
Total order boradcast builds on the guarantees by reliable broadcast and also ensures that messages are delivered in the same order to all
processes [1].


## Summary


Data replication requires sending messages to groups of processes, making multicast communication essential.
Broadcast protocols are essential in doing so. This short note, introduced several such protocols like best-effort, reliable, eager reliable, and gossip-based protocols, each offering different delivery guarantees. While many of these do not enforce message ordering, total order broadcast extends reliable broadcast by ensuring that all processes receive messages in the same order, a key requirement for consistent replication.

## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
# qubit-note: Distributed Systems | Data Replication | Common Conflict Resolution Strategies

## Overview

When multiple nodes or processes update the same data at the same time (such as in a distributed database, multi-leader replication, or collaborative editing), conflicts can occur.
Conflict resolution strategies are vital to ensure all copies of the data remain consistent.
In this note we will review the following resolution strategies

- Last-Write-Wins (LWW) 
- Vector Clocks
- Logical Clocks


## Common Conflict Resolution Strategies

Last-write-wins (LWW) is a straightforward conflict resolution policy where the latest update wins.

In practice, each write is tagged with a timestamp (or a monotonically increasing logical counter), and if two updates conflict, the system chooses the one with the most recent timestamp.

For example, Apache Cassandra uses a “last-write-wins” approach: every write is timestamped, and the database selects the value with the newest timestamp when a conflict occurs.

This ensures a single consistent value is picked quickly without complex merging.

Advantages
LWW is simple to implement and fast.

There is no need to keep multiple versions or perform a merge. You just keep the newest update.

This strategy works well in systems where occasional overwrites are acceptable and clock synchronization is reasonably reliable.

Drawbacks
The simplicity of LWW comes at the cost of potential data loss. If two updates occur at nearly the same time on different nodes, one will be arbitrarily dropped in favor of the other.

In other words, resolving a conflict by last-write-wins means discarding all but one of the concurrent updates, so one user’s change could be lost.

Additionally, LWW usually relies on synchronized physical clocks.

If clocks drift or a timestamp is incorrect, a newer update might be mistaken for an older one and get overwritten. This risk makes pure LWW less ideal for globally distributed systems where clock skew can occur.

(Some systems mitigate this by using hybrid logical clocks or other schemes, but the fundamental issue is that ordering by time can be imperfect.)

Vector Clocks
A vector clock is a mechanism for tracking causality and event ordering in distributed systems.

Instead of a single timestamp, each node keeps a vector of counters (one counter per node in the system).

This allows the system to record a partial ordering of events without any global physical clock.

By exchanging and comparing vector clocks, one can tell whether an event happened-before, happened-after, or was concurrent with another event on a different node.

In simple terms, if every element of Node A’s vector clock is less than or equal to the corresponding elements of Node B’s vector clock, then A’s event occurred before (and possibly led to) B’s event.

If neither clock is ≤ the other (each has at least one element higher than the other’s), the two events are concurrent (they happened independently with no causal relationship).


Vector clocks are essential for identifying and resolving conflicts in systems with concurrent updates because they explicitly capture causality.

Unlike LWW (which blindly picks one update based on time), vector clocks allow a system to detect a conflict, i.e., recognize when two updates happened in parallel and then decide how to resolve it.

For example, Amazon DynamoDB and similar distributed databases have used vector clocks to tag each data version; if two users update the same record on different servers concurrently, the vector timestamps will be incomparable, signaling a conflict that needs resolution (such as merging or prompting a client to reconcile).

This way, no update is lost silently: the system knows two versions exist and can either merge changes or preserve both versions for later resolution instead of arbitrarily discarding one.

Overhead and Drawbacks
The main trade-off with vector clocks is the overhead of storing and transmitting the vector metadata.

The vector length equals the number of nodes or replicas, so it grows with system size.

Every message or data item must carry this vector of counters, which can become large in a big cluster and consume extra bandwidth and storage.

Maintaining vector clocks can also add complexity in code.

Moreover, while vector clocks detect conflicts, the resolution of the conflict (how to merge the concurrent updates) is still up to the application or a higher-level algorithm (e.g. CRDTs or custom merge logic).

In summary, vector clocks provide a powerful way to detect concurrent updates and preserve causality at the cost of additional metadata and complexity.


Logical Clocks (Lamport Timestamps)
Logical clocks are a broader term for systems of assigning artificial time to events.

The most common form is the Lamport timestamp, introduced by Leslie Lamport, which provides a simple way to order events in a distributed system without relying on physical time.

A Lamport clock is essentially a counter that each process maintains and increments on each event; when a process sends a message, it attaches its current counter value, and the receiver sets its clock to the max of its own value and the received value (then increments by one).

This algorithm ensures that if Event A happened-before Event B (meaning A causally influences B), then A’s timestamp is smaller than B’s timestamp.

Logical clocks thereby establish an ordering of events that is consistent with causality.

Guarantees and Limitations
Lamport logical clocks can totally order events (e.g. if two events happen at different processes, their timestamps can be compared and one will be “earlier” or “later”).

This is useful for many distributed algorithms that need a consistent global sequence of events (such as ordering operations or coordinating actions).

However, Lamport timestamps cannot indicate concurrent events.

If two events are truly independent (neither caused the other), a Lamport clock will still assign one a smaller number and the other a larger number, but that ordering is arbitrary and does not reflect a causal relationship.

In other words, Lamport clocks capture happens-before relations but cannot distinguish concurrency. Two concurrent events might end up ordered one way or another by their timestamps, and you can’t tell just from the numbers that they were concurrent.

This is why more advanced schemes like vector clocks were developed: to detect when events are concurrent (causally unrelated).

Each of these strategies has different strengths and trade-offs in handling concurrent updates:

Last-Write-Wins (LWW): Simplicity and speed. Only a single timestamp per update is needed, and conflict resolution is just a matter of picking the highest timestamp. However, concurrent updates are not truly reconciled. One update overwrites the other, potentially losing data. LWW assumes a reliable ordering (usually wall-clock time or a logical clock) and is suitable when occasional lost updates are acceptable and ease of implementation is a priority (for example, caching systems or certain user settings where the latest change naturally overrides previous ones).

Vector Clocks: Conflict detection and causality tracking. Vector clocks add more metadata (an array of counters) but in return they can detect concurrency and preserve all causally distinct versions of data. This makes them ideal for systems that need to merge changes or at least flag conflicts instead of dropping updates. With vector clocks, if two writes conflict, the system knows about it and can take appropriate action (merge automatically, keep both versions, or ask a user to decide). The trade-off is higher overhead per operation and more complex implementation. Vector clocks are used in scenarios requiring strong eventual consistency guarantees, such as multi-master databases or collaborative applications where no updates should be lost.

Logical Clocks (Lamport timestamps): Basic ordering with minimal overhead. Lamport clocks use just an integer counter per process to timestamp events, making them very lightweight. They ensure a consistent global order of events that respects causality, which can be sufficient for many algorithms and even for simple conflict resolution (by treating the highest timestamp as last-writer). However, logical clocks do not detect concurrent conflicts. They will order every event one way or another, even if events happened at the same time on different nodes. Thus, using Lamport clocks for conflict resolution is effectively similar to LWW (the “last” logical timestamp wins), with the same caveat that concurrent changes get totally ordered but without awareness that a conflict occurred. Lamport clocks shine in use cases like distributed logging, global snapshots, or any situation where we only need to order events, not merge them.

## Summary

In summary, choosing a conflict resolution strategy in a distributed system depends on your consistency needs and tolerance for lost updates.

LWW offers simplicity but might drop data, vector clocks offer accuracy in tracking conflicts but with more overhead, and logical clocks provide an easy way to order events without capturing full concurrency information.

Many modern systems combine these techniques or use advanced structures like CRDTs (Conflict-Free Replicated Data Types) that can automatically merge concurrent changes without losses.

## References

1. <a href="https://www.designgurus.io/course-play/grokking-scalable-systems-for-interviews/doc/what-are-common-conflict-resolution-strategies-lastwritewins-vector-clocks-logical-clocks">What Are Common Conflict Resolution Strategies (Last‑write‑wins, Vector Clocks, Logical Clocks)?</a>
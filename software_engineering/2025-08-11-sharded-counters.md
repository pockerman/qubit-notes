# quibit-note: Sharded Counters

## Overview

In this qubit note, we will discuss the sharded counters pattern. This is a pattern we can use whenever there is a 
need in our system to scale counting. It is also an approach we can follow in order to address the top k problem.


**keywords** system-design, distributed-systems

## Sharded counters

Let's start by first trying to describe the problem we want to address. 

**The problem**

In a distributed system, you might need to keep track of counts. Here are some examples that
such a need arises:

- Number of likes on a social media post
- Number of views on a video
- Number of active sessions for a user

We can certainly store the counter as a single tuple/document or key in our databases. However, this approach
is problematic when we work with systems that have to deal with high traffic. These are the two main problems
that such a database approach has:

1. Database write contention
2. Throughput limit

When multiple machines try to update the same row at the same time it is unavoidable that we need to serialize these operations leading to
data locks which eventually degrades performance. In addition, the machine that holds the counter eventually becomes a bottlenec.


**The sharded counters**

When using sharded counters, we don't just store one counter but $N$ separate sub-counters. Each of these counters
is tored independently. When the total is needed, we sum these sub-counters in order to get the total value.

There are two questions that we need to address. How to pick $N$ and how to pick which shard to increment.
As you can probably guess, the number of shards we use is important in order to have a good performing system. If the shard count is small for a specific write workload, 
we face high write contention, which results in slow writes. On the other hand, if the shard count is too high for a particular write profile, we encounter a higher overhead on the read operation. 

There are various was we can use in order to choose which shard to increment. Two popular approaches are:

- Random choice
- Using various application specific metrics

One thing one needs to note about sharded counters is that reading in general becomes more expensive/slower In general, shards may reside on different nodes and we need to read all the shards
in order to respond with the right sum. That's why it is mentioned above that a too high shard count may be problematic.

## Summary

In summary, the sharded counter pattern trades off read simplicity for write scalability by distributing increments across multiple independent counters, then summing them to get the total.
It is an approach we can follow in order 

## References

1. <a href="https://medium.com/%40awesomefirebase/sharding-counters-in-firestore-conception-of-a-real-time-polls-app-a06f896e6483">Sharding counters in Firestore: conception of a real-time polls app-part1</a>
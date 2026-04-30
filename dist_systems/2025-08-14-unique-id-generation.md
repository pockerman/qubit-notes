# qubit-note: Unique ID Generation

## Overview

In this note, I discuss three different ways we can possibly use in a distributed system in order to create unique ids.
Namely, I will discuss:

- Using UUID
- Using a database 
- Using a range handler

Each approach has its advantages and disadvantages and depens on the systems requirement which one to use.

**keywords** system-design, distributed-systems

## Unique ID generation

Very frequently, we need to create unique ids in our system so that we can uniquely label entities. Sometimes this process may be
straightforward e.g. use the email id of the user to uniquely label them. However, sometimes this is not so straightforward e.g.
how do we label the tasks to be executed in the background of our system? We need a way to uniquely identify these tasks so that
we can poll their status.

### UUID

The first approach that comes to mind is to use UUID. A UUID is a 128-bit number that can be used to identify information in 
informatics systems. Typically, a UUID has a very low probability of creating a duplicate. According to Wikipedia,_ _after generating 
1 billion  UUIDs every second for approaximately 100 years would the probability of creating a single duplictae reach 50%_.

Generating a UUID in Python is trivial:


```
import uuid

# Create a random UUID
my_uuid = uuid.uuid4()
print(my_uuid)  # e.g., 550e8400-e29b-41d4-a716-446655440000
```

UUIDs have different versions the version 4, used above, generates a pseudorandom number.
An approach like this has the following advantages [1]:

- Simple 
- No coordination between servers 


However, 128 bits may be more than engough that what an application requires; e.g. 64 bits. In addition, UUIDs do not go up with time
and can be non-numeric [1].

### Using a database

Relational databases offer ```auto_increment``` functionality to uniquely assing ids to tuples if needed. However, this approach does not
work out of the box in a distributed system. First a single database may not be large enough. We can address this by adding more database servers
but then generating unique IDs accross these is not necessarilly easy [1].

It is worth mentioning that Flicker is using what the call a ticket server. The idea behind a ticket server is pretty much what we discussed above i.e. use the 
```auto_increment``` feature in a single database server.


### Using a range handler

One way to avoid constant communication with a central ID generator is by allocating a block or range of IDs to each node or service in the system.
A  database or ID service in the system is responsible for handing out these ranges. 
Each node generates IDs locally within its assigned block until the block is exhausted.

The central allocator, keeps track of which ID ranges are already assigned.
When a node requests a range, it allocates the next unused block (e.g., 1–1000, 1001–2000, etc.).
The node generates IDs sequentially or randomly within its range; no network calls needed.
When the range is used up, the node requests a new range.
Since ranges never overlap, IDs are guaranteed to be unique system-wide.


Some of the advantages of a range handler include:


- Low latency: Since ids are generated at the node level no constant remote calls.
- Scalable: Works well with many nodes.
- Simple logic: No complex coordination once ranges are assigned.

On the flip side, the range handler approach has some disadvantages:

- Possible waste: If a node fails before using its whole range, the unused IDs are lost.
- Central dependency: Still requires a reliable central service for range allocation.
- Range exhaustion bursts: If many nodes run out of ranges at the same time, the central allocator may be stressed.

## Summary

This note explores three common strategies for generating unique IDs in distributed systems namely, UUIDs, database auto-increment, and the range handler approach. UUIDs provide simplicity and eliminate the need for server coordination but may be larger than necessary and lack ordering. Databases can generate sequential IDs via auto_increment, but scaling across multiple servers introduces complexity. The range handler approach assigns each node a unique block of IDs from a central allocator, enabling low-latency, local ID generation without constant coordination, though it can waste unused IDs if nodes fail, relies on a central service, and risks range exhaustion under heavy simultaneous demand.

## References

1. Alex Xu _System Design Interview, An insider's view_.
2. <a href="https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/">Ticket Servers: Distributed Unique Primary Keys on the Cheap</a>

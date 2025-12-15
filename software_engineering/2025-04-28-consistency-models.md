# qubit-note: Consistency Models


## Overview

In this note I give a brief overview of the most common <a href="https://en.wikipedia.org/wiki/Consistency_model">consistency models</a> used when designing distributed systems.
The choice of the model depends heavily on the application requirements and therefore this is not  a discussion
over which model is better but rather stating the attributes of each approach. 
In this note, I will discuss the following models:

- Strong consistency
- Sequential consistency
- Eventual consistency

For more information about consistency models see <a href="https://jepsen.io/consistency/models">Consistency Models</a>.

**keywords** consistency-models, software-architecture, system-design, distributed-systems

## Consistency models

In an ideal world, when a client sends a request to a replicated store, this request gets executed instantly.
However this is far from what is happening in reality. In particular, when we have a system where the read requests
can be served by any follower and not the leader, then it is possible that two clients may get a different view of the 
state of the system [2]. This will be particularly true if we have weighted the availability of the system more
than its consisyency see <a href="https://en.wikipedia.org/wiki/CAP_theorem">CAP Theorem</a>.

More formally, consistency models define the various views that observers of a system can have with respect
to the system state. We will look into the following consistency models:

- Strong consistency
- Sequential consistency
- Eventual consistency

Let's briefly go over each of these terms.

### Strong consistency

As the name implies this form guarantees that a client will be able to observe the state of a system
that it is not affected if any of the replicas is lagging behind. This will be the case if the
read/write requests are wired to the leader. In other words, every request appears to be atomic [2].
Strong consistency is also known as <a href="https://jepsen.io/consistency/models/linearizable">linearizability</a> [2].
However, in this consistency model all reads and writes have to go through the leader node which causes a chocking point
which limits the throughput.

### Sequential consistency

If we relax the real-time guarantees of the stong consistency model then we have the seqiential consistency model.
In this model, the replica will receive the requests in the same order as the leader but it may not be
necessarilly up to date with the leader. A typical example of sequential consistency is when a producer and a consumer
are synchronized via a queue [2]. If we pin a client to a specific replica, then each client will have a different view of the system
in different times.


### Eventual consistency

Eventual consistency allows us to read from replica nodes but there is no guarantee that the data will be up to date with the leader node.
As its name imples, eventual consistency guarantees that all replicas eventually
will converge to the same final state provided that the writes to the system stop [2].
Pinning a client to a particular replica somehow poses a single point of failure for that client.
To counter this, we can allow the client to read from any replica but in this case the data the client
reads may be quite out-of-sync from the leader.

Eventual consistency is the model of choice when prioritizing low latency as it eliminates the expensive node coordination [4].


### Other consistency models

There is a numbe of consistency models other than what is mentioned above; casiual consistency and strong eventual consisyency are some.
However, I would like to briefly mention session consistency as this is very prevalent for web and mobile applications [4].
Session consistency guarantees that within a single user session, reads are monotonic and users always see their own writes. Updates are visible immediately only to the same session, not necessarily to other users. This model is ideal for individual user–focused applications (like e-commerce carts or web/mobile apps), where a consistent personal experience matters, but it is not suitable for collaborative applications that require shared, real-time visibility.


## Summary

In summary, a consistency model defines the rules about how operations (especially reads and writes) appear to execute across multiple nodes, threads, or users in a distributed or concurrent system.
The three consistency models above have different guarantees that stem from the different trade offs they offer.
It's upon the system architect to decide which consistency model should be used. Note that a system does not have to use just one consistency
model but can blend these depending on the requirements of the subsystem viewed. 


## References

1. <a href="https://en.wikipedia.org/wiki/Consistency_model">Consistency models</a>
2. Roberto Vitillo _Understanding Distributed Stystems. What every developer should know about large distributed apllications_
3. <a href="https://en.wikipedia.org/wiki/CAP_theorem">CAP Theorem</a>
4. Pekka Enberg _Latency Reduce Delay in Software Systems_, Manning Publications.

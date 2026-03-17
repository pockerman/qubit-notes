# qubit-note: Distributed Systems Series | Part 2 | Challenges in Distributed Systems

## Overview

<a href="#">Introduction to Distributed Systems</a> introduced the idea of a distributed system and gave some examples.
In addition, we saw the core example of a distributed system that we will be exapanding on in these notes.

In this note, we will discuss briefly the core challenges that we need to address when designing a distributed system and
associate these challenges with our running example. Speciffically, designing distributed systems evolves around
the following challenges:

- Communication
- Coordination
- Scalability
- Resiliency
- Operations

## Challenges of distributed system design

Let's discuss some core challenges we need to address when disgining distributed systems.

### Communication

In <a href="#">Introduction to Distributed Systems</a> we split our imaginary system into two layers; the we server layer and the database layer.
Now that the two services live in different machines they need to communicate over the network. This add uncertainty as the network is notoriously unstable.
It also add latency into our application. We will need to be able to understand how the stack works despite the fact that network libraries typically abstract all
the communication details.

### Coordination

As our database grows larger, we will have to add more nodes to support it. This is easy to do as we have separated the web application from the database.
However, the database nodes have to be coordinated in order to provide a single coherent whole view of the data to the clients.
Coordianation is distributed systems is difficult and there are a number of techniques we will discuss.

### Scalability

The performance of d distributed system illustrates how efficiently it can handle load [1]. In general, it is measured with _throughput_ and _response time_.
Throughput is defined as the number of operations per second the system can process [1]. Response time represents the overall time between a client request and 
time it received the response. In general, the load on a system can be measured in different ways and it is very specific to the use cases the system can handle.

### Resiliency

A systme is resilient when it can continue to do its job even when a failure happens [1]. When working with distributed systems given the scale that typically these systems
have, any failure that can happen eventually will happen [1]. Somehow independent of the how small the probability of occurence is, as the number of operations increases,
the absolute number of failures will increase. 

Failures unavoidably affect the availability of a system. The availability is defined as as the amount of time the system can serve requests divided by the duration of the 
period measured i.e. it is the percentage of time the system is capable of serving requests [1].


### Operations

Just like any other system, a distributed system is designed and developed in order to be deployed and do useful work.
However, this implies a number of things such as testing, maintenance, ability to roll back changes and ability to monitor the system.
All these operations should happen in a way that do not affect the availability of the system [1].




## Summary

Designing distributed systems involves addressing several key challenges that arise when system components run on different machines. First, communication becomes complex because services (such as a web server and a database) must interact over unreliable networks that introduce latency and uncertainty. Coordination is required when multiple nodes—like distributed database instances—must work together to present a consistent view of data to clients. Scalability focuses on how efficiently the system handles increasing load, typically measured through throughput (operations per second) and response time (delay between request and response). Resiliency ensures the system continues functioning despite inevitable failures, maintaining high availability over time. Finally, operations covers the practical aspects of running the system in production, including testing, monitoring, maintenance, and safely deploying or rolling back changes without disrupting service.



## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
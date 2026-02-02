# qubit-note: Distributed Systems Series | Resiliency Part 1 | Failure Causes

## Overview

In this part of the series we want to discuss how to make a distributed system more resilient to failure. To this end
we need to know the most common causes of failure we can encounter in a distributed system. In this qubit-note, we will discuss the following

- Single point of failure
- Network paritioning
- Slow processes
- Load spikes

**keywords** software-architecture, system-design, distributed-systems, failure-causes, system-resilience

## Failure causes

#### Single point of failure

A distributed system consists of a number of nodes that many things can go wrong within each node that can cause it to malfunction e.g. software bugs, disk crashes.
A single point of failure (SPF) is a node of the system that when it crashes, or performs suboptimally, the whole system crashes with it [1].
The most glaring example is perhaps an application that cannot connect to its backend because the backend service is down.

Obviously, SPFs should be detected when architecturing the system. Sometimes identifying SPFs is easy. However, the best way to identify a node
whether is an SPF or not is to what would happen to the system if the node were to fail [1].

#### Network paritioning

The network that a distributed system operates on can be unreliable in many aspects. For example packets may be dropped or the network may simply be slow.
When a client sends a request to a server it expects that a response will be returned. This however need not be the case. The client though has no way of
knowing whether the response is on its way or not. At this point a client has two options either wait or fail the request [1].
There are several reasons why the client hasn't received a response [1]:

- The request has been dropped by a proxy or router or network switch
- The server is slow or crashed
- The server's response has been dropped by a proxy or router or network switch

#### Slow processes

A process running on a server many times can slow down. From a client's perspective a slow process is the same as an one that isn't running at all.
Typically, a process is slowing down because of resource leaks with memory leaks is probably the most well known. Other issues may be
a thread that is making HTTP requests without setting  a timeout. If the call never returns then the thread will never be returend to the thread pool [1].


#### Load spikes

Typically a system is designed having a certain load pattern in mind. However often this assumption fails in practice for a variety of reasons [1]:

- The requests may exhibit some sort of seasonality
- Some requests might be more expensive than others
- Some requests are malicious intended to abuse the system e.g. DDoS attacks


## Summary

This note introduces common causes of failure in distributed systems as a foundation for building resilient architectures. It focuses on four major failure categories.

- Single points of failure (SPFs)
- Network partitioning
- Slow processes
- Load spikes

Overall, understanding these failure modes is a prerequisite to designing resilient distributed systems.


## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_


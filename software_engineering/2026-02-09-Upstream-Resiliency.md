# qubit-note: Distributed Systems Series | Resiliency Part 3 | Upstream Resiliency

## Overview

<a href="2026-02-04-Downstream-Resiliency.md">qubit-note: Distributed Systems Series | Resiliency Part 2 | Downstream Resiliency</a>
discussed various options we can employ in order to handle downstream failures i.e. failures that are caused due to a failed
interaction with another service.

In this note, we want to look into how to handle failures within our system e.g. when our server is overloaded. Specifically,
we will look into:

- <a href="https://en.wikipedia.org/wiki/Load_shedding">Load shedding</a>
- Load leveling
- <a href="https://en.wikipedia.org/wiki/Rate_limiting">Rate limiting</a>
- Bulkhead
- Health check
- Watchdog

**keywords** software-architecture, system-design, distributed-systems, failure-causes, system-resilience

## Upstream reciliency

Let's start this note by discussing load shedding.

#### Load shedding

In layman's terms load shedding refers to rejecting requests when our system is overloaded. What it means for a system to be overloaded depends on
the system at hand [1]. When a server detects that is overlaoded it can reject the incoming request by returning 503 i.e. Service Unavailable.
Note that load shedding cannot completely offload from the server the cost of handling the request [1]. How much handling the server has to do depends
on how it handles the rejection process. 


#### Load leveling

When the clients of our service do not expect a response within a short time frame, we can use load leveling instead of load shedding.
The idea behind load leveling is to introduce a messaging channel between the client and the service. The client pushes messages
to the messaging channel instead of to the server directly. The server pulls the messages at its own pace [1].

## Summary

Both load leveling and load shedding don't address an increase in load directly. Instead they attempt to protect the service from getting overloaded.
In order for a service to be able to handle more request, it has to be scaled out [1]. Therefore, these mechanisms are typically combined with autoscaling [1].

## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
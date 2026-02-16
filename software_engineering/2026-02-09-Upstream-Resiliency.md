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

#### Rate limiting
 With rate limiting or throttling the server will reject a request when a specific quota is exceeded [1].
 Quotas are typically applied to specific users, API keys or IP addresses [1]. When a request is rate-limited we need to return
 a response with a speciific error code.  When working with HTTP APIs, the most common way to do this is to return a response with statuc code 429.
 The response can also include a Retry-After header that indicates how long to wait before making a new request [1].

 Other uses of rate limiting include enforcing price tiers and to some extent help with DDoS[1].

 #### Bulkhead


 #### Health check


## Summary

Both load leveling and load shedding don't address an increase in load directly. Instead they attempt to protect the service from getting overloaded.
In order for a service to be able to handle more request, it has to be scaled out [1]. Therefore, these mechanisms are typically combined with autoscaling [1].

## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
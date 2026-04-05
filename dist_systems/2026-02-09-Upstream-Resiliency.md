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

Both load leveling and load shedding don't address an increase in load directly. Instead they attempt to protect the service from getting overloaded.
In order for a service to be able to handle more request, it has to be scaled out [1]. Therefore, these mechanisms are typically combined with autoscaling [1].

#### Rate limiting

 With rate limiting or throttling the server will reject a request when a specific quota is exceeded [1].
 Quotas are typically applied to specific users, API keys or IP addresses [1]. When a request is rate-limited we need to return
 a response with a speciific error code.  When working with HTTP APIs, the most common way to do this is to return a response with statuc code 429.
 The response can also include a Retry-After header that indicates how long to wait before making a new request [1].

 Other uses of rate limiting include enforcing price tiers and to some extent help with DDoS[1].

 #### Bulkhead

 The bulkhead pattern, named after the partitions of a ship's hull, is to isolate a fault in one part of a service from degrading the entrire service [1].
 Some clients create a lot more load one a service than others. This means that if there is no mechanism to isolate this client, it can degrade the whole
 system. We have seen that rate-limiting as an approach to prevent a single client from using more resources than it should. Howver, this is not bulletproof.

 The bulkhead pattern partitions a shared resource behind a load balancer and assigns each user of the service  to a specific partition.
 This means that the requests of the greedy user can only utilize the resources in the partition he has been assigned to. Unavoidably, the greedy user
 will negatively affect the other users in the same partition however the pattern does not allow any furthre mitigation of the entire system.


 #### Health check

 A health check allows us to query a service is overloaded or not. That is it gives us the potentially to stop the traffic to a service that is
 operating at its limit. This is in contrast to the patterns we have seen above. The service exposes a health endpoint that is periodically queried by the
 load balancer. If the enpoint returns an error the load balancer will consider the service unhealthy and won't propagate traffic into it [1].


 #### Watchdog

 A watchdog is implemented as a background thread that monitors the runnning process. It wakes up periodically and checks various aspects of the
 running process like memory consumption. When the metric is identified to exceed a configured threshold, the watchdog will restart the running
 process [1]. This approach allows the system to gain some room before failing and gives time to the engineering team to identify the bug.
 Obviously, a watchdog has to be tested thoroughly otherwise we may end restarting the process continuous.ly


## Summary


This note discusses upstream resiliency, focusing on how to handle failures that originate within our own system—especially overload scenarios. It presents several complementary patterns: load shedding (rejecting requests with 503 when overloaded), load leveling (using a message queue so the server can process requests at its own pace), rate limiting (enforcing per-client quotas with 429 responses), bulkheads (partitioning resources to isolate noisy or greedy clients), health checks (allowing load balancers to stop sending traffic to unhealthy instances), and watchdogs (monitoring processes and restarting them when critical thresholds are exceeded). Together, these techniques protect system stability by rejecting excess load, smoothing traffic, isolating failures, and enabling detection and recovery.


## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
# qubit-note: Distributed Systems Series | Resiliency Part 2 | Downstream Resiliency

## Overview

<a href="software_engineering/2026-01-28-Failure-Causes.md">qubit-note: Distributed Systems Series | Resiliency Part 1 | Failure Causes</a> introduced
some common failures in a distrbuted system. In this note we will discuss some techniques to address these. Specifically,
we will assume that our system interacts with another service that we don't necessarilly control. How our system should behave when this
service is down or is slow?

**keywords** software-architecture, system-design, distributed-systems, failure-causes, system-resilience

## Downstream resiliency

A deployed distributed system in most cases will interact with third party serevices. For various reasons this interaction
may not be such that the system can run smoothly. We want to have mechanisms that prevent our system to degrade to a state that
it cannot function anymore. Some of these mecahnisms include [1]:

- Timeouts
- Retries
- <a href="2025-04-30-circuit-breaker-pattern.md">Circuit breaker</a>

Let's briefly discuss these.


### Timeouts

One of the simplest ways to safeguard a system from not operating third party services is to use timeouts. A timout specifies the 
duration that the a client should wait until a response from the third party service arrives. If a response has not arrived within
the specified interval, the client abords the connection. Timeouts are very simple to implement. Typically an API that 
handles requests will allow us to set this. Here is an example from python's ```requests``` package:

```
import requests
response = requests.get(url='https://get-something.com', timeout=10)
```

The major problem with timeouts is that getting the time to wait right can be very tricky. Ideally, we should set the timeout based on the
desired false timeout rate [1].

### Retries

There are many reasons why a request may fail. Fault tolerant applications typically don't bail out immediately but rather attempt the request again.
However, if the downstream service is overwhelmed, retrying immediately will not have better chances to success. Retrying therefore needs to be slowed down down with 
increasingly longer delays between individual retries [1]. In addition, we will need to set the maximum number of retries. A common approach to set the
delay between retries is the <a href="https://en.wikipedia.org/wiki/Exponential_backoff">exponential backoff</a> [1].


### Circuit breaker

Retries are effective when the failure is of transient nature. However, failures may non-transient. We need therefore a mechanism that detects these faults
in downstream dependencies and stops new requests from being sent. The <a href="2025-04-30-circuit-breaker-pattern.md">Circuit breaker</a> is meant to do exactly that.
In a nutshell, a circuit breaker will temporarly block access to a faulty service after it detects failures.
Thus, it allows the system to recover effectively by preventing attempts that most likely will not be successful.
This is a very useful technique to incorpoate in our API design as it helps us build resilient systems.


## Summary


This qubit note explains downstream resiliency in distributed systems—how a system should behave when it depends on external or third-party services that may be slow, unreliable, or completely unavailable. The goal is to prevent failures in downstream services from cascading and degrading the entire system.

It introduces three core resiliency mechanisms:

- Timeouts: Limit how long a client waits for a response from a downstream service. If the response takes too long, the request is aborted to avoid tying up system resources. Timeouts are easy to implement but hard to tune correctly, and should ideally be set based on an acceptable false-timeout rate.

- Retries: Instead of failing immediately, a system can retry failed requests to handle transient issues. However, retries must be controlled—using delays and a maximum retry count—to avoid overwhelming an already struggling service. Exponential backoff is a common strategy to progressively increase wait times between retries.

- Circuit breakers: When failures are persistent rather than transient, retries are ineffective. A circuit breaker detects repeated failures and temporarily blocks requests to the failing service, allowing the system to degrade gracefully and recover without wasting resources.


## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
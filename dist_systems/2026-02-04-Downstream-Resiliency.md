# qubit-note: Distributed Systems Series | Resiliency | Downstream Resiliency

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
the specified interval, the client aborts the connection. A timeout is essentially a hard boundary. Timeouts are very simple to implement. Typically an API that 
handles requests will allow us to set this. Here is an example from python's ```requests``` package:

```
import requests
response = requests.get(url='https://get-something.com', timeout=10)
```
As a system designer, you should assume every network call will eventually hang, and you must assign a strict timeout to every single one.
In fact, we can distinguish between the following phases when looking at a network request:

- the handshake i.e. establishing the connection
- Wait for the server to process and return the data

Most HTTP libraries allow you to set two separate timeout values to handle these phases independently. 
for example, Python's ``requests`` library, we can use a tuple ``timeout=(2, 8)``.

The major problem with timeouts is that getting the time to wait right can be very tricky. Ideally, we should set the timeout based on the
desired false timeout rate [1]. Furthermore, a rule of thumb can be:

- Connection Timeout (2 seconds): If the downstream server is healthy, it should "answer the door" almost instantly. If you can't even establish a connection after 2 seconds, the server is likely down, or the network is severed. Fail fast.
- Read Timeout (8 seconds): Once connected, you might need to give the server a bit more time to query its database and generate your data payload.

Where do these numbers come from?
In a real production environment, an architect doesn't pull resilience numbers out of thin air or rely on "gut feeling." You arrive at these thresholds by analyzing historical monitoring baselines and strict Service Level Agreement (SLA) targets. For example, if your monitoring dashboard shows that 99% of healthy API requests usually finish in under 2 seconds, a 2-second connection timeout becomes a defensible, data-driven decision rather than a guess.

A Service Level Agreement (SLA) is a formal, legally binding contract between a service provider (such as a payment processor or cloud platform) and its customers that defines the expected service level. It acts as the "Standard of Quality" for the relationship.

While an SLA often covers things like Uptime (e.g., "The system will be online 99.9% of the time"), for an architect, the most important part is the Latency Guarantee. If an API's SLA promises that 95% of requests will be processed in under 500ms, you use that "promise" to set your timeouts. If they break that promise, your timeout triggers to protect your system. These triggered timeouts also serve as the documentable evidence you need to hold your vendors financially accountable.

### Retries

There are many reasons why a request may fail. Fault tolerant applications typically don't bail out immediately but rather attempt the request again.
Indeed for example most cloud failures are transient. However, if the downstream service is overwhelmed, retrying immediately will not have better chances to success. Retrying therefore needs to be slowed down down with  increasingly longer delays between individual retries [1]. In addition, we will need to set the maximum number of retries. A common approach to set the
delay between retries is the <a href="https://en.wikipedia.org/wiki/Exponential_backoff">exponential backoff</a> [1].


---
**Exponential Backoff**

Exponential Backoff is a network resilience strategy in which an application progressively increases the wait time between retry attempts after a failure. Instead of immediately and repeatedly hammering a struggling service with requests (which can accidentally cause a Distributed Denial of Service attack), the system multiplies the delay after each failed attempt (e.g., waiting 1 second, then 2 seconds, then 4 seconds, then 8 seconds). This gives the overwhelmed downstream system the necessary "breathing room" to recover. It was popularized by Bob Metcalfe and David Boggs in their seminal 1976 paper "Ethernet: Distributed Packet Switching for Local Computer Networks", which you can find here: http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-75-7_Ethernet_Distributed_Packet_Switching_for_Local_Computer_Networks.pdf

---

Here is an example of how exponential backoff will look like
```
Attempt 1 fails. Wait 1 second.
Attempt 2 fails. Wait 2 seconds.
Attempt 3 fails. Wait 4 seconds.
Attempt 4 fails. Wait 8 seconds.
```


---
**Remark**


Retries are a superpower, but they are dangerous. If you retry a payment request, you must ensure you aren't accidentally charging the customer twice. To do this safely, you must generate a unique "Safety Key" (Idempotency Key) in your Business Layer and pass it into your service. This ensures that every retry attempt presents the exact same identity to the server, so the payment processor knows to ignore duplicates. We will see this in action in Listing 10.2.

---

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


In the next part: <a href="2026-02-09-Upstream-Resiliency.md">qubit-note: Distributed Systems Series | Resiliency Part 3 | Upstream Resiliency</a> we will see how to handle
external requests that somehow push our system to its limits. 

## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_

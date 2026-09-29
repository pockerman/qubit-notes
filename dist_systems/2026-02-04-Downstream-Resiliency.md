# qubit-note: Distributed Systems Series | Resiliency | Downstream Resiliency

## Overview

<a href="software_engineering/2026-01-28-Failure-Causes.md">qubit-note: Distributed Systems Series | Resiliency Part 1 | Failure Causes</a> introduced
some common failures in a distrbuted system. In this note we will discuss some techniques to address these. Specifically,
we will assume that our system interacts with another service that we don't necessarilly control. How our system should behave when this
service is down or is slow?

## Downstream resiliency

A deployed distributed system in most cases will interact with third party serevices. For various reasons this interaction
may not be such that the system can run smoothly. We want to have mechanisms that prevent our system to degrade to a state that
it cannot function anymore. Some of these mecahnisms include [1]:

- Timeouts
- Retries
- Fallbacks
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


Retries are a superpower, but they are dangerous. If you retry a payment request, you must ensure you aren't accidentally charging the customer twice. To do this safely, you must generate a unique "Safety Key" (Idempotency Key) in your Business Layer and pass it into your service. This ensures that every retry attempt presents the exact same identity to the server, so the payment processor knows to ignore duplicates. 

---

### Fallbacks

What happens when the Timeout is reached, and all the Retries have failed? The system is truly broken. This is where the Fallback comes in.

A Fallback is an architectural resilience pattern that provides a pre-programmed alternative response when a primary operation fails. Instead of allowing an external error to crash the application or display a broken screen to the user, a fallback gracefully degrades the experience by returning default data, using a previously cached response, or executing a simplified business rule.

It is your architectural "Plan B," designed to keep the system functional and save the business transaction even when your downstream dependencies are completely broken.

Example 1: If your Netflix app cannot reach the sophisticated "AI Recommendation API" to generate your personalized homepage, the Fallback is to simply return a hardcoded list of the "Top 10 Global Hits." The user still gets to watch a movie.

Example 2: If your e-commerce site cannot reach the "Live Shipping Calculator API," the Fallback is to charge a flat $5.00 shipping fee. You might lose a few dollars on postage, but you still gain $100 on the sale. This is a classic Business Tradeoff: you are intentionally choosing to lose a few dollars on postage (by switching to a flat fee) to save the $100 sale that would have been lost to a server crash.

When you combine Timeouts, Exponential Backoff, and Fallbacks, you transform your application from a fragile piece of glass into a highly resilient shock absorber.

But what happens when the external service isn't just having a temporary hiccup? What happens when it is completely dead, and the database is actively on fire? That is when the shock absorbers bottom out, and we need to bring out the heavy artillery: The Circuit Breaker.

### Circuit breaker

Timeouts and Retries are great for temporary network blips. But what happens if the third-party Payment API you rely on is completely offline for an hour?
If you just rely on Timeouts, every customer who tries to check out will be forced to stare at a loading spinner for 10 seconds before the Timeout finally triggers and throws an error. During those 10 seconds, the thread on your server is blocked. If thousands of users try to check out at the same time, your servers will quickly run out of threads, memory will spike, and your entire application will crash.

A failure in a downstream service has now cascaded upstream, bringing your system down.

To stop cascading failures, we use the <a href="2025-04-30-circuit-breaker-pattern.md">Circuit breaker</a> pattern. 
In a nutshell, a circuit breaker will temporarly block access to a faulty service after it detects failures.
Thus, it allows the system to recover effectively by preventing attempts that most likely will not be successful.
This is a very useful technique to incorpoate in our API design as it helps us build resilient systems.

We will discuss more about this pattern in <a href="2025-04-30-circuit-breaker-pattern.md">Circuit breaker pattern section</a>. 

### Summary: 

This qubit note explains downstream resiliency in distributed systems—how a system should behave when it depends on external or third-party services that may be slow, unreliable, or completely unavailable. The goal is to prevent failures in downstream services from cascading and degrading the entire system.

It introduces four main resilience mechanisms:

1. Timeouts

   * Define how long the system waits for a downstream service.
   * If the service does not respond within the limit, the request is aborted.
   * Timeouts prevent resources such as threads from being held indefinitely.
   * They should be based on monitoring data and SLA/latency requirements rather than arbitrary values. 

2. Retries

   * Failed requests can be attempted again because many failures are temporary.
   * Retries should have a maximum number of attempts and increasing delays.
   * Exponential backoff is recommended, e.g. `1s → 2s → 4s → 8s`.
   * Retries must be used carefully for operations such as payments because repeating a request can cause duplicate side effects. Idempotency keys can make such operations safe to retry. 

3. Fallbacks

   * When the primary service fails after timeouts/retries, the system uses an alternative response or behavior.
   * Examples include cached data, default values, or simplified business logic.
   * The objective is graceful degradation rather than completely failing the user request. 

4. Circuit Breakers

   * Used when a downstream service is persistently failing.
   * Instead of repeatedly sending requests that are likely to fail, the circuit breaker temporarily blocks requests to that service.
   * This prevents cascading failures, where one unavailable service eventually exhausts the resources of your own application. 

Overall we have the following schematics

```
Request
   │
   ▼
Downstream Service
   │
   ├── Success ──────────────► Response
   │
   └── Failure
        │
        ▼
     Timeout
        │
        ▼
      Retry
        │
        ├── Success ─────────► Response
        │
        └── Still failing
              │
              ▼
           Fallback
              │
              └── OR
                    ▼
              Circuit Breaker
                    │
                    ▼
             Stop sending requests
             temporarily
```

In the next part: <a href="2026-02-09-Upstream-Resiliency.md">qubit-note: Distributed Systems Series | Resiliency Part 3 | Upstream Resiliency</a> we will see how to handle external requests that somehow push our system to its limits. 





## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_

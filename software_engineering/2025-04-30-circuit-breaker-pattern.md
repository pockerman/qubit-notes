# qubit-note: qubit-note: Architecture Series | Circuit Breaker Pattern

## Overview

In this note I discuss the <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker">circuit braker pattern</a>.
In a nutshell, a circuit breaker will temporarly block access to a faulty service after it detects failures.
Thus, it allows the system to recover effectively by preventing attempts that most likely will not be successful.
This is a very useful technique to incorpoate in our API design as it helps us build resilient systems.


**keywords** software-architecture, system-design, distributed-systems, design-patterns

## Circuit breaker pattern

Let's describe first the problem that the circuit breaker pattern tries to solve.

We know that in modern software systems calls to services can fail. 
The reason of the failuer can be transient at least in the eyes of the caller which
means that it may be fixed rather fast. Hence, a tactic that we employ in such scenarios
is to use <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/retry">retries</a>.

However, not all faults are transient and can take some time in order to fix it.
If an application implements the retry pattern then this means that the service that 
is not functioning as it should, is being called repeatedly. 

This will cause a cascade of failures. Perhaps an easy fix for this is to use a time-out mechanism;
if the application does not receive a response from the service within the given time interval, the application
will reply with an error message of some kind.

The problem with this tactic is that when dealing with concurrent requests, typically the case in modern systems,
these requests will be blocked and potentially will hold system resources database connections, memory e.t.c.
Obviously, this is a scenario that we don't want to materialise. In these cases, what we want is 
fail the operation immediately and only allow the service invocation if it is likely to succeed.

The circuit breaker pattern offers a solution to such cases and it allows the application
to operate normally without waiting for the fault to be fixed or wasting CPU cycles.
In addition, the pattern also enables the application to detect when the service fault is resolved.

The circuite breaker pattern can be implemented as a state machine.
It monitors the number of recent failures and, using this information,
it decides if the operation should proceed or to return an exception immediately.
We need to specify three thresholds for the pattern to work; the number of failuers we are willing to tolarate, the 
time interval that these failues are acceptable the minimum number of successes to change from Half-open to Closed.

The circuit breaker pattern has three states:

- Closed
- Open
- Half-open

The closed state is considered the normal state that the system should be in.
Every time a call to the service fails, the circuit breaker will increment this counter.
If the number of recent failures exceeds a specified threshold within the specified time period, 
then the circuit breaker is placed in the Open state and starts a time-out timer. 
When the timer expires, the proxy is placed into the Half-open state.

The Open state is considered the faulty state; the request from the application fails immediately and an exception is returned to the application.

The half-open state is kind of the testaing state. This is because in this state some
requests will  be attempted to be served. If all of these requests are successful then 
the system transitions to the closed state and begins operating normally.
If however, one of these requests fails then the system will transition to the open state.


On the surface, the circuite breaker may look similar to a rate limiter; both are used to limit calls to an API or a service
However, rate limiters simply block the traffic to a service if the number of requests exceeds a specified number
within a specified time interval. On the other hand, the circuit breaker tries to isolate the failure to one component
Overall, a circuit breaker is in general _smarter_ than a rate limiter.
However, this comes with the price of increased complexity.

## Summary

The note explains the circuit breaker pattern, a software architecture pattern used to build resilient distributed systems. Its goal is to prevent repeated calls to a failing service, which can waste resources and trigger cascading failures.

In modern systems, service calls often fail. While retries help with transient issues, they can worsen situations when failures persist, especially under high concurrency. Timeouts alone aren’t enough, because blocked requests can still consume resources like threads, memory, and database connections.

The circuit breaker pattern addresses this by failing fast when a service is likely to fail and only allowing calls when recovery is probable. It’s typically implemented as a state machine that tracks recent failures using configurable thresholds.

The pattern has three states:

- Closed: Normal operation. Failures are counted, and if they exceed a threshold within a time window, the breaker opens.
- Open: Calls fail immediately without contacting the service. After a timeout, the breaker moves to half-open.
- Half-open: A limited number of test requests are allowed. If they succeed, the breaker closes; if any fail, it reopens.

Finally, the note contrasts circuit breakers with ate limiters. While both restrict calls, rate limiters are based purely on request volume, whereas circuit breakers are failure-aware and isolate faulty components. Circuit breakers are more intelligent but also more complex to implement.


## References

1.  <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker">circuit braker pattern</a>

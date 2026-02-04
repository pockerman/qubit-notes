# qubit-note: Distributed Systems Series | Resiliency Part 2 | Downstream Resiliency

## Overview

<a href="software_engineering/2026-01-28-Failure-Causes.md">qubit-note: Distributed Systems Series | Resiliency Part 1 | Failure Causes</a> introduced
some common failures in a distrbuted system. In this note we will discuss some techniques to address these. Specifically,
we will assume that our system interacts with another service that we don't necessarilly control. How our system should behave when this
service is down or is slow?

**keywords** software-architecture, system-design, distributed-systems, failure-causes, system-resilience

## Downstream resiliency

A deployed distributed system in most cases will interact with third party serevices. For various reasons this interaction
may not be such that the system can run smoothly. We want to have mechanisma that prevent our system to degrade to a state that
it cannot function anymore. Some of these mecahnisms include [1]:

- Timeouts
- Retries
- <a href="2025-04-30-circuit-breaker-pattern.md">Circuit breaker</a>

Let's briefly discuss these.


## Summary

## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
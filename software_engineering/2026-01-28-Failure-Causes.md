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

#### Networke paritioning




## Summary

## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_


# qubit-note: Distributed Systems | Scalability | Little’s Law

## Overview

In this note we will discuss Little's Law. 
This law is a simple equation from queueing theory that tells is that the averange number of items in progress in a system is equal to the average arrival rate multiplied by the average time each item spends in the system [1].


## Little’s Law

Little’s law is a simple equation from queueing theory that tells is that the averange number of items in progress in a system is equal to the average arrival rate multiplied by the average time each item spends in the system [1]. It was discovered by John Little in the 1960s, andprovides a powerful way to analyze queues and performance in both everyday scenarios and computer systems [1].

Little's law links the following key metrics

- throughput
- time
- concurrency

Mathematically Little's law is as follows [1]

$$ L = \lambda \times W$$

Where $L$ is the load or concurrency or in practical terms the average number of items in the system simultaneously. $\lambda$ is the average
rate at which items enter and exit the system e.g. requests per second the server accepts. $W$ is the wait time or latency i.e. the average time each item spends in the system for example the response time per request.


---
**Remark: Work In Progress**

The average number of items in a system is sometimes called work in progress or WIP

--- 

There are two things about Little's law o0n should be aware. The law holds for a stable queueing system. The law  does not depend on the distribution of arrivals or service times or the order of service [1].

So how can we use Little's law in designing distributed systems?. Little’s Law is very important because it connects throughput, latency, and concurrency; meaning  the metrics we are interested in when building scalable systems. It provides a quick reality check and estimation tool for
system capacity or identifying bottlenecks.

Below is an example from [1]. Consider a web API. It can process 150 requests/second. Each request can take 0.35 seconds to complete on average.
How many requests the API can process concurrently? This is a simple application of Little's law

$$L = 150 \times 0.35=52.5$$

Assume now that for some reason a database call is taking longer and the average response time is increased to 1.5 seconds.
Assuming the same arrival rate then the system concurrency is

$$L = 150 \times 1.5=225$$

meaning that the load on the system has gone four times up.


## Summary

Little’s Law is a fundamental principle from queueing theory that relates concurrency, throughput, and latency in a system through the equation ($L = \lambda \times W$), where $L$ is the average number of items in the system (work in progress), $\lambda$ is the average arrival or processing rate, and $W$ is the average time an item spends in the system. The note explains that the law applies to stable systems regardless of arrival or service-time distributions, making it highly useful in distributed systems and scalability analysis. By connecting throughput and response time to system load, Little’s Law provides a practical way to estimate capacity and identify bottlenecks. The note demonstrates this with a web API example, showing how increased latency dramatically raises system concurrency and therefore system load.


## References

1. <a href="https://www.designgurus.io/course-play/grokking-scalable-systems-for-interviews/doc/what-is-littles-law-and-how-to-use-it-for-quick-capacity-estimates-in-system-design">What is Little’s Law and How to Use It for Quick Capacity Estimates in System Design</a>
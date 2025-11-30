# qubit-note: Architecture Patterns-Scalability Patterns

## Overview

Scalability is a promperty of a system that shows us how well it can handle growth i.e. increasing number of requests.
There are various patterns that we can use to improve the scalability of system and un this qubit note we will review some 
of them.

**keywords** system-scalability, software-architecture, distributed-systems

## Architecture Patterns-Scalability Patterns

We all of us want our system to scale easily i.e. be able to add more servers or be able to partition
the workload so that the system can continue to operate properly. We have two main ways to scale a system:

- Horizontally
- Vertically

Horizontal scaling, also known as "scale out," involves increasing the capacity of the system by adding more machines or servers to a system to distribute the workload across a larger pool of resources. Vertical scaling enhances a single machine's power by adding CPU, RAM, or storage.
Both approaches have advantages and disadvantages and they can be used in combination.

Horizontal scaling, in theory, allows for nearly horizontal scaling allows for nearly unlimited scalability as it is not constrained by the hardware limits of a single server. Therefore, it is particularly beneficial for handling large-scale, distributed workloads and is widely used in modern cloud environments, such as Kubernetes, where tools like the <a href="https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/">HorizontalPodAutoscaler (HPA)</a> automatically adjust the number of application pods based on observed metrics like CPU or memory utilization. However, this approach is, typically, more involved to implement and maintain.

Both horizontal and verical scalability pin point the hardward requirements. However, in order for a system to scale we also
need to consider the software installed on it. Indeed, tightly coupled software systems may not scale even if we increase the available
resources. 

Below are some commonly used patterns that increase the scalability of our software system:

- Caching
- Database replication
- Database sharding
- <a href="2025-04-21-load-balancing.md">Load balancing</a>
- Asynchronous processing
- Stateless services
 

## Summary

Scalability is the property of a system that tells us how it copes with growth i.e. more requests, more data. 
A scalable system can handle more traffic and process more data. We have two main types of hardware scalability; vertical and horizontal.
Vertical scalability means to increase the power of a single machine (more CPU, RAM, storage). 
Horizontal scalability means to add more machines or instances to distribute workload.
This approach offers near-unlimited scalability and is widely used in cloud environments such as Kubernetes, where tools like the Horizontal Pod Autoscaler (HPA) adjust the number of pods based on demand.

However, we also need to address the software that runs on the hardware and how it copes with increasing volume. Various patterns exist to improve the scalability from the software
perspective such as database sharding and load balancing.


## References

1. <a href="https://github.com/binhnguyennus/awesome-scalability">awesome-scalability</a>
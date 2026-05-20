# qubit-note: Distributed Systems | Scalability | Cold & Warm Starts


## Overview

In this note we review to ideas associated with scalability and system behaviour. Namely,
we will discuss cold and warms starts.


## Cold & Warm Starts

Conceptually understanding cold and warm starts is very easy; cold start refers to starting up a system, application, or function from scratch with no pre-existing state whilst a warm start means restarting or reusing a system that’s already initialized or cached, resulting in much faster startup and response times [1].

Thus, when dealing with system performance cold starts better be avoided as they introduce extra latency and obviously slowdowns.
This is because when in cold start a system will typically have to do things like  code loading, establishing database connections, read configuration files and fill empty caches. Warm starts on the other hand, don't have this overhead and therefore the system can respond quickly.
Typically, cold starts exhibit the following characteristics [1]:

- Require full initialization
- High latency on first contact

---
**Remark**

 A cold start occurs when something is run for first time, or if it hasn’t been used in a while [1]. 
 An example of the latter are serverless platforms like AWS Lambda. An AWS Lambda will perform a cold start for a function if it’s invoked after a period of no activity or when scaling up to handle more traffic. Similarly, a database cache might go cold after a restart or failover, meaning the cache has to build up again from empty [1].

 ---

Warm starts should be prefered in terms of improving latency and throughput. However, you should note that  keeping things running to stay warm can consume more memory or compute resources continuously. For example, keeping a cache warm might mean using extra memory to store data, and keeping a server always on (to avoid cold boot) might incur costs. If the performance gains outweight costs then warm starts should be used.

There are several examples one can see the action of cold and warm starts some have already been mentioned.

- System boots
- Launching an application
- Web caching

## Summary

All in all, cold starts and warm starts are all about initialization state and performance.
Understanding cold versus warm starts is important in terms of system scalability as it affects how your architecture handles growth and load.
In general, a scalable system should try to minimize cold start impacts so that adding more capacity or handling sporadic traffic doesn’t degrade the user experience.
For example, load balancers might route traffic in a way to keep some servers warm, or cloud services may offer auto-scaling with warm pools (pre-initialized instances ready to take traffic).
In addition, <a href="https://www.geeksforgeeks.org/system-design/what-is-cache-warming/">cache warming</a> techniques can be used after deployment so that users don’t hit entirely empty caches.
By anticipating cold start costs, architects can improve performance during scale-ups or deployments and ensure the system remains responsive.
 

## References

1. <a href="https://www.designgurus.io/course-play/grokking-scalable-systems-for-interviews/doc/what-are-cold-starts-and-warm-starts-and-why-do-they-matter-for-performance">What are Cold Starts and Warm Starts, and Why Do They Matter for Performance?</a>
# qubit-note: Distributed Systems Series | Caching Part 2 | Cache Coherence

## Overview

In this note we will discuss cache coherency i.e. how multiple caches can maintain a uniform view of the cached data.


**keywords** software-architecture, system-design, distributed-systems, caching, data-replication

## Cache Coherence

Cache coherence means that multiple caches maintain a uniform view of the cached data [2].
For example, CPU caches stay consistent when accessing the same memory. 
In multi-core systems, each core has its own cache, which can lead to stale data if one core modifies cached data that other cores also hold. 
To prevent this, CPUs use cache-coherence protocols like MESI.

The MESI protocol tracks the state of each cache line using four states [2]:

- Modified: One cache has changed the data; it differs from main memory.
- Exclusive: One cache has an unmodified copy that matches main memory.
- Shared:  Multiple caches share an unmodified copy that matches main memory.
- Invalid: The cache line is not valid or not present.

These states coordinate updates so all cores see a consistent view of memory.


### Cache hit ratio

Caches speed up access by storing frequently used data, but because caches are smaller than the full dataset, performance depends on maximizing the cache hit ratio.
This is the proportion of requests served from the cache. It is defined as [2]:

$$\text{Hit ratio} = \frac{\text{Hits}}{\text{Hits} + \text{Misses}}$$

Higher ratios mean faster workloads, while lower ratios mean more access to slower primary storage.

Improving the hit ratio involves focusing on the working set; i.e. the subset of data actively used during a given time. 
The working set is usually much smaller than the total dataset and changes over time, such as popular products on an e-commerce site or viral posts on social media. Caching this frequently accessed data yields the biggest performance gains.


## Summary


The note explains cache coherence; how multiple caches keep a consistent view of shared data—and why it’s critical in both hardware and distributed systems.

It first illustrates the problem using **multi-core CPUs**, where each core has its own cache. When multiple caches store the same data, writes by one core can leave other caches with **stale values** unless a coordination mechanism exists. CPUs solve this using cache coherence protocols, most notably MESI, which tracks cache lines through four states:

- Modified
- Exclusive
- Shared 
- Invalid

We also discussed  cache hit ratio as a key metric for evaluating cache effectiveness. It’s defined as the proportion of cache accesses served directly from the cache versus total accesses. A higher hit ratio means better performance, since fewer requests hit slower primary storage.

Finally, it introduces the idea of the working set; the subset of data that is frequently accessed during a given period. Because caches are smaller than total datasets, maximizing performance depends on ensuring the working set fits in the cache. Real-world examples include popular products in e-commerce or viral posts on social media, which dominate access patterns despite much larger overall datasets.


## References

1. <a href="https://en.wikipedia.org/wiki/Cache_coherence">Cache coherence</a>
2. Pekka Enberg, _Latency Reduce delay in software systems_ Manning Publications
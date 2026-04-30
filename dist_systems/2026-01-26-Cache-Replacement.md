# qubit-note: Distributed Systems Series | Caching Part 3 | Cache Replacement


## Overview

<a href="software_engineering/2026-01-21-cache-coherency.md">qubit-note: Distributed Systems Series | Caching Part 2 | Cache Coherence</a> discussed the notion of 
cache coherency i.e. how multiple caches can maintain a uniform view of the cached data. A cache however only has a certain capacity and when this
capacity is reached we need somehow update the cache. In this note, we will review some cache replacement techniques or <a href="https://en.wikipedia.org/wiki/Cache_replacement_policies">cache replacement policies</a>. We will be discussing the following policies:

- Least recently used (LRU)
- Least frequently used (LFU)
- First-in, first-out (FIFO)
- SIEVE

**keywords** software-architecture, system-design, distributed-systems, caching, data-replication

## Cache replacement

The purpose of caching is to reduce the access latency by introducing a temporary copy of the data that is faster to access than the 
primary storage [2]. The caching layer therefore will be typically  located in a proximity with to the access point.
Caching however is typically expensive as the cache memory is more expensive than disk storage. For
example the the price per gigabyte for DRAM is ten times higher than that of SSDs [2].
As a result we can only cache a rather limited size of the data.

However, when the cache is fully occupied, some elements have to be evicted from it.
This is where  the cache replacement policy determines what we throw out from the cache. 
Choosing the right cache replacement policy is critical for maintaining a high cache hit ratio and, therefore, low-latency
access, but the decision can be workload-specific [2]. Typically the replacement policy is based on how long the element
has been in the cache or how frequently it is accessed. Below are some frequently use cache replacement policies.


#### Least recently used (LRU)

The least recently used (LRU) replacement policy evicts data elements from
the cache based on them not being used recently. LRU caching can maintain a high hit ratio for workloads with high
temporal locality. If recently accessed data in the cache is likely to be accessed
shortly, LRU will ensure that relevant data stays in the cache. On the other
hand, if your workload has a low degree of locality, LRU can perform worse than not caching at all because your
workload may bring data to the cache that you never reuse, resulting in high Least recently used overhead from caching and evicting.


#### Least frequently used (LFU)

Another policy is the least frequently used policy whereby data is replaced based on how frequently the are used.
Hence LRU is looking at the recency of data access but LFU is looking at the fequency of data usage.
LFU can maintain a high cache hit ratio and, therefore, low-latency access for workloads where access to different elements is irregular [2]. 
With LRU, when a cache element is accessed, it is eagerly promoted by moving it to the head of the cache to ensure it remains in the cache.


#### First-in, first-out (FIFO) and SIEVE
The first-in, first-out (FIFO) replacement policy evicts data elements based on when they were added to the cache [2].
FIFO replacement uisng lazy promotion and quick demotion can outperform LRU [2].
In contrast to LRU, the basic FIFO replacement policy has no promotion, as elements are evicted purely based on when they were added. 


#### SIEVE

This is another cache replacement policy that is actually a variant of FIFO with re-insertion [2].
Whereas FIFO with re-insertion adds elements at the head of the FIFO queue, SIEVE retains the element’s position at re-insertion. 


#### Time-to-live (TTL)

The replacement policies we looked at above determine whic elements should be removed.
However, sometimes we want to be able to control the freshness of the data, even when there is no
need to evict anything. The time-to-live  is a mechanism used in caching to limit how
long a cached element can stay in the cache before it is considered stale and, therefore, is purged from the cache.

TTL is a very simple approach to invalidate cache entries
In particular, if you are not using <a href="2026-01-20-Caching.md">write-through or write-behind caching</a>, 
where updates to the data go through the cache, making sure backing storage updates are reflected in the cache can be complex.
TTL solves the invalidation problem by simply allowing entries in the cache to remain live for a limited time, after which the application must retrieve data from the database
or backing store [2]. 

Although TTL is very simple it does have some downsides [2]. 
Specifically,picking the correct value for TTL can be tricky and can seriously affect the performance of the applicaiton if we get it wrong.
As a rule of thumb, TTL is great for caching data that only changes some of the time, but it is often tricky for more dynamic data.


## Summary

Here’s a concise summary of the text:

The note explains **cache replacement policies**, which decide what data to evict when a cache reaches capacity. Because caches are expensive and limited in size, choosing the right replacement strategy is critical for achieving a high cache hit ratio and low latency, and the best choice often depends on workload characteristics.

It reviews several common policies:

- Least Recently Used (LRU): Evicts items that haven’t been accessed recently. It works well for workloads with strong temporal locality but can perform poorly when data is rarely reused.
- Least Frequently Used (LFU): Evicts items that are accessed least often, focusing on usage frequency rather than recency. It can be effective for irregular access patterns.
- First-In, First-Out (FIFO): Evicts items in the order they were added, with no promotion on access. Despite its simplicity, FIFO with optimizations like lazy promotion can outperform LRU in some cases.
* **SIEVE:** A variant of FIFO with re-insertion, where reinserted elements keep their position instead of moving to the head.

The note also discusses Time-to-Live (TTL), which limits how long cache entries remain valid regardless of cache pressure. TTL simplifies cache invalidation and freshness management, especially when writes do not go through the cache, but choosing an appropriate TTL value is difficult and can negatively impact performance if set incorrectly. TTL works best for data that changes infrequently.


## References

1. <a href="https://en.wikipedia.org/wiki/Cache_replacement_policies">Cache replacement policies</a>
2. Pekka Enberg, _Latency Reduce delay in software systems_ Manning Publications
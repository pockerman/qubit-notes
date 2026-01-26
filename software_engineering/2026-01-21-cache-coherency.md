# qubit-note: Distributed Systems Series | Caching Part 2 | Cache Coherence

## Overview

In this note we will discuss cache coherency i.e. how multiple caches can maintain a uniform view of the cached data.


**keywords** software-architecture, system-design, distributed-systems, caching, data-replication

## Cache Coherence

Cache coherence means that multiple caches maintain a uniform view of the cached data.
For example, in modern CPUs with multiple cores, each core maintains its own cache.
When your program reads data from memory, that data is cached in the per-core CPU
cache to speed up subsequent accesses. If another core reads the same data, it will pull
that data into its cache, so it’s cached in two places. However, the coherency issue arises
when one of the cores writes to data cached by other cores. Only one core will see the
latest value—the other cores see stale data, resulting in an incoherent system, unless
there’s coordination between the different caches

CPUs coordinate cache coherence using a protocol such as MESI.
The MESI protocol defines four states for each cache line (for example, a 64-byte
block of cached memory):
- Modified (M) means that a single cache has a valid and modified copy of data. The
CPU is free to change the cache line further.
- Exclusive (E) means that a single cache has a valid copy that isn’t modified and
matches the contents of the main memory. Modifying the cache line puts it into
the modified (M) state.
- Shared (S) means that one more cache has a valid, unmodified copy of data that
matches the contents of the main memory.
- Invalid (I) means a cache line is either invalid or absent.


### Cache hit ratio

A cache makes things run faster, providing a temporary copy of essential data with
faster access latency than the primary data storage. As we have already discussed, you
can use a key–value store, such as Redis, to cache query results you’d otherwise have to
fetch from a database server, such as MySQL or Postgres. However, you can’t generally
cache all your data (if you could, you would probably be using replication), so how can
you maximize your performance with the constraint that your cache is smaller than the
dataset you’re working with? The answer is to maximize the cache hit ratio.
The cache hit ratio is a number that describes the ratio between your cache hits and
total cache accesses. Usually, you calculate the cache hit ratio as the number of cache
hits divided by the sum of cache hits and misses, as shown in the following equation:

$$\text{Hit ratio} = \frac{\text{Hits}}{\text{Hits} + \text{Misses}}$$

The cache hit ratio tells you how effective your cache is for a given workload. The
higher the cache hit ratio, the more your workload is served from your cache and,
hopefully, the faster it is. A cache hit ratio of 100% means all your data accesses were
from the cache, and a hit ratio of 0% means none of them were, so the data had to be
retrieved from the primary storage.

One way to improve the cache hit ratio is to think of it from the perspective of the
working set, which is the dataset an application needs to perform its function at a par-
ticular time. The working set is often smaller than the total dataset the application can
access, and it can change over time. For example, if we return to the e-commerce exam-
ple, you may have a product catalog in the tens or hundreds of gigabytes. Still, your
users are browsing just the products on the front page or ones that have become pop-
ular. That set of frequently accessed products could be your application’s working set.
Similarly, in a social media application, some posts may have become extremely pop-
ular and are, therefore, accessed frequently, but with a heavy tail of less popular posts
that are rarely accessed. The set of posts accessed during a particular period would be
the working set.

## Summary


The note explains **cache coherence**—how multiple caches keep a consistent view of shared data—and why it’s critical in both hardware and distributed systems.

It first illustrates the problem using **multi-core CPUs**, where each core has its own cache. When multiple caches store the same data, writes by one core can leave other caches with **stale values** unless a coordination mechanism exists. CPUs solve this using **cache coherence protocols**, most notably **MESI**, which tracks cache lines through four states:

* **Modified** (changed and owned by one cache),
* **Exclusive** (owned by one cache, unchanged),
* **Shared** (unchanged and present in multiple caches), and
* **Invalid** (not usable).

The note then shifts to **cache hit ratio**, a key metric for evaluating cache effectiveness. It’s defined as the proportion of cache accesses served directly from the cache versus total accesses. A higher hit ratio means better performance, since fewer requests hit slower primary storage.

Finally, it introduces the idea of the **working set**—the subset of data that is frequently accessed during a given period. Because caches are smaller than total datasets, maximizing performance depends on ensuring the working set fits in the cache. Real-world examples include popular products in e-commerce or viral posts on social media, which dominate access patterns despite much larger overall datasets.


## References

1. <a href="https://en.wikipedia.org/wiki/Cache_coherence">Cache coherence</a>
2. Pekka Enberg, _Latency Reduce delay in software systems_ Manning Publications
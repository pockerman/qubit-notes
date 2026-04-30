# qubit-note: Caching Part 4 | Negative Caching


## Overview

We have discussed various <a href="2026-01-20-Caching.md">caching methods</a> and their trade offs.
The discussion may have alluded to the fact that caching is all about real data. However, this need not be
the case. We can also cache negative results e.g. a request that returned a 404. This is called negative caching


## Negative caching

Caching is a technique that can improve the latency of an application by facilitating access to a faster memory layer other than
the database layer or the hard disk. Apart from caching existing data we can also cache a failure or not found result.
This is called negative caching. With negative caching  we dont just store successful responses, but also cache certain errors (e.g., 404 Not Found) or queries that return empty results (e.g., “no rows”), for a short time. The advanatge of such a strategy is that we  protect the databases and upstreams from repeated, identical misses and failures, slash latency for repeat lookups that would fail anyway, and smooth out incident blast radius. In other words, negative caching prevents our system from perfroming  the same redaundunt operation that fails over and over, which can save time and resources.



## Summary

## References
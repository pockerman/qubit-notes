# qubit-note: Caching Part 4 | Negative Caching


## Overview

We have discussed various <a href="2026-01-20-Caching.md">caching methods</a> and their trade offs.
The discussion may have alluded to the fact that caching is all about real data. However, this need not be
the case. We can also cache negative results e.g. a request that returned a 404. This is called negative caching.


## Negative caching

Caching is a technique that can improve the latency of an application by facilitating access to a faster memory layer other than
the database layer or the hard disk. Apart from caching existing data we can also cache a failure or not found result.
This is called negative caching. With negative caching  we dont just store successful responses, but also cache certain errors e.g., 404  or queries that return empty results for a short time. The advanatge of such a strategy is that we  protect the databases and upstreams from repeated, identical misses and failures, slash latency for repeat lookups. In other words, negative caching prevents our system from perfroming  the same redaundunt operation that fails over and over, which can save time and resources.

The following image illustrates how negative caching works

The following are some examples of negative caching [1].

- Avoid redudant requests
- Respond faster on errors
- Cost and resource savings
- Improve cache hit ratios

Below are some common scenarios where negative caching is or can be used [1].

- DNS lookup failures
- HTTP 404 errors
- API errors and rate limiting
- Queries with empty result sets

When Should You Cache 404 or Empty Results?
Negative caching is powerful, but it should be used judiciously. Caching 404 errors or empty results makes sense only in certain situations:

When you expect repeated requests for the same missing item: If an item is missing and multiple clients or users keep requesting it, caching the "not found" response is beneficial. A great example is a popular URL that was removed; instead of hitting your server every time, the first 404 can be cached and all subsequent users get the cached 404 until it expires. This scenario often occurs with bots or crawlers repeatedly accessing invalid URLs, or users retrying a search. In such cases, caching the 404/empty result significantly cuts down redundant traffic (as seen with The Onion’s case).

When the missing data is unlikely to appear immediately: If you know that a 404 is truly a missing resource (e.g., a deleted page) or an empty query means "no data exists" (not just temporarily empty), then a negative cache with a reasonable TTL is safe. For instance, a product ID that doesn’t exist in your database likely won’t magically appear in the next few seconds. Caching that miss for a short period (say a minute) will not harm consistency but will save a lot of overhead. Stability of content is key: as one expert noted, if your content "doesn't change much," caching 404s can help a lot. If it’s truly an old or permanent 404, feel free to cache it (some systems even cache such errors for several minutes or more by default).

When failures are expensive to compute: Use negative caching if a failure results from an expensive operation. For example, an empty result that came from a complex database query or an extensive search should be cached briefly. This ensures that if the same query comes again, the system can return the cached "no results" quickly rather than re-running the heavy query. The costlier the operation to find out something doesn’t exist, the more you gain by caching that outcome.

High traffic scenarios and rate limiting: If your system (or an upstream service) is under high load and returning errors (like 503 Service Unavailable or rate limit errors), negative caching those responses for a short time can actually act as a throttle. It prevents flooding the service with identical failing requests. For example, caching a 503 for even 30 seconds can stop thousands of clients from continuously retrying during an outage window. (Some HTTP clients even do this automatically with retry-after headers or similar cues.)


However, there are also times you should NOT cache 404/empty results, or do so with great caution:

When the data is highly dynamic: If new content can appear at any moment, caching a "not found" might lead to serving stale errors. For instance, in a fast-changing API where a resource might be added soon, you wouldn't want clients to use a cached 404. They should check the origin again so they don't miss the newly added data. As a rule of thumb, if an item could exist in the near future, keep the negative TTL very short or avoid caching it. In other words, negative caching can harm correctness if the “not found” condition is transient.

If the error is due to a temporary outage or glitch: Don’t cache transient errors like network timeouts, 500 Internal Server Errors, or other temporary failures. Those should be retried, not cached (except perhaps for a few seconds) because the problem might be resolved on the next attempt. Negative caching is best for consistent negative results (like truly nonexistent data), not one-off transient errors.

Always use reasonable TTLs: When you do cache a 404 or empty result, configure a short Time-To-Live. This is a best practice emphasized by many experts. Caching negative results “sparingly (e.g., 404s) with very short TTLs” is recommended. For example, on the order of seconds or a few minutes, depending on how quickly things could change. Short TTLs ensure that if the situation changes (the data appears, the page is created, etc.), the negative cache will expire soon and clients will get fresh results. For instance, DNS negative caches often use a small TTL (like 5 minutes or less) for domains that might be registered or updated soon, and CDNs default to a couple minutes for 404s unless configured otherwise. Always balance the performance gain with the risk of staleness.

Provide ways to invalidate if necessary: In scenarios where you implement negative caching in your application, consider how to force refresh if needed. For example, if an admin knows a previously missing item has just been added, you might purge the negative cache for that key so users aren’t stuck seeing "not found." While standard HTTP caches will naturally drop the entry after the TTL, in a custom cache you should make sure negative entries don’t stick around too long or can be evicted manually.



## Summary

In this note we discussed negative caching. With negative caching we store unsuccesful results e.g. 404 or an empty result set.
The driving idea behind negative caching is to avoid doing work that is known to fail. Such an approach is very useful for cases that
failures occur frequently.

## References

1. <a href="https://www.designgurus.io/course-play/grokking-scalable-systems-for-interviews/doc/what-is-negative-caching-and-when-should-you-cache-404-or-empty-results">What Is Negative Caching and When Should You Cache 404 or Empty Results?</a>
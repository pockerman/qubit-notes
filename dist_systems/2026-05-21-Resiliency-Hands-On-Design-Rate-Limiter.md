# qubit-note: Distributed Systems | Resiliency | Hands On | Design a Rate Limiter

## Overview

We looked into various techniques about how to improve the upstream resiliency of a system (see <a href="2026-02-09-Upstream-Resiliency.md">Upstream Resiliency</a>).
One of the techniques we mentioned was rate limiting. Since rate limiting is ubiquitous in contemporary systems, we will discuss if a bit further.
We will also discuss how we can potentially design a rate limiter.

## Design a rate limiter

Recall from the note <a href="2026-02-09-Upstream-Resiliency.md">Upstream Resiliency</a> that with rate limiting or throttling the server will reject a request when a specific quota is exceeded [1].
Whether this is a threshold we follow strictly or we allow the requests to exceed it for a short period of time, distinguises hard and soft rate limiting [2].
In addition, we can apply rate limiting in various levels of our stack. for example the HTTP layer or we can apply rate limiting by IP address using Iptables, see e.g [3]. 
There are a number of algorithms on can implement for rate limiting [2]:

- Token bucket
- Leaking bucket
- Fixed window
- Sliding window log
- Sliding window counter

As a client you should try to not getting rate limited as this affects the user experience. In this setting:

- Know the limits of the external APIs you are using
- Use caches to avoid frequent API calls
- Add sufficent back off time to retry logic
- Always implement code to catch exceptions or errors from when rate limited

---
**Remark: Rate Limiter Headers**

When implementing rate limiting at the HTTP level, typicall you want to return a 429 error code.
However, there is more information the server can provide to the client via various HTTP headers [2]:


- ```X-Ratelimit-Remaining``` The remaining number of allowed requests within the window
- ```X-Ratelimit-Limit``` How many calls the client can make per time window
- ```X-Ratelimit-Retry-After``` The number of seconds to wait until you can make a request again without being rate limited


Whe a use has sent too many requests, a 429 error code and the ```X-Ratelimit-Retry-After``` are returned by the HTTP server.

---

### Desing  a rate limiter

Let's now see how we can desgin a rate limiter.


## Summary

## References

1. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
2. Alex Xu, _System Design Interview_, Second Edition
3. <a href="https://blog.programster.org/rate-limit-requests-with-iptables">Rate Limit Requests with Iptables</a>


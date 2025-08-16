# qubit-note: Semantic Caching


## Overview

Caching plays a significant role when thinking minimizing latency in a system. <a href="https://redis.io/">Redis</a> and
<a href="https://memcached.org/">memcached</a> are two widedly used technologies. However, modern systems
rely more and more on the outputs of machine learning models such as deep neural networks or large language models (LLMs).
The output of these models is inherently probabilistic so for the same input you may get a slightly different address.
This is paricular the case with LLMs where they are able to provide a number of different answers that remain semantically
the same for the same input. 

This behavious is problematic when we think traditional caching. In this qubit-note, I discuss semantic caching
that allows us to utilise caching even when using ML models

**keywords** semantic-caching, system-design, distributed-systems

## Semantic caching

Let's briefly recall what traditinal caching is. Consider the query

```
SELECT * FROM users WHERE age = 30
```

we can save the result of this query in the cache as a key-value pair

```
cache[query] = result set
```

If the exact same query comes in we can look into the cache before turning to the database.
This is more or less what traditional caching is all about.

Let's consider now the case where the search engine utilises an LLM to translate the user query into an SQL. Thus, a query may be of the form

```
Give me all users that their age is 30 years old
```

or

```
Return the  users that they are  30 years old
```

The LLM will successfully turn this into the right SQL: ```SELECT * FROM users WHERE age = 30```
and we can now store the SQL and go back to the traditional scenario. 

There is a catch however. We need to call an LLM to give us the query and then look into the cache and associate the
user query with the SQL.

If we were able to store somehow the meaning of a query alognside with the result set then we could perform some sort 
of similarity search in the cache. This is what a  semantic cache differs from traditional caching methods; it stores the meaning of a query or requests instead of just the raw data [1].
In other words, semantic caching stores data based on its meaning using for example an embedding model.
This means that two queries with the same meaning will return the same result, even if the underlying data has changed [1]. 
Semantic caching allows us to cache LLM responses and thus we can shorten data retrieval time, lower API call expenses, and improve scalability [1].

Some disadvanatges of semantic caching are:


- Complex cache management: Must track predicates and check subset/overlap relationships.
- Cache invalidation: If underlying data changes, determining which semantic cache entries are stale can be tricky.
- Overhead: More CPU time needed to decide cache hits/misses (vs. simple key-based lookup).


Check the article <a href="https://redis.io/blog/what-is-semantic-caching/">Semantic caching for faster, smarter LLM apps</a>, for best practices for implementing semantic caching.


## Summary

In summary, semantic caching extends traditional caching methods to better support modern machine learning–driven systems, especially those using large language models (LLMs). Unlike traditional caching, which stores query–result pairs for exact matches, semantic caching stores the meaning of queries—often via embeddings—so that semantically equivalent queries map to the same cached result, even if their wording differs. This approach reduces latency, lowers costs from repeated model calls, and improves scalability when working with probabilistic model outputs. However, semantic caching introduces added complexity in cache management, invalidation, and lookup overhead compared to conventional key-based caching.

## References

1. <a href="https://zilliz.com/glossary/semantic-cache">Understanding Semantic Cache</a>
2. <a href="https://redis.io/blog/what-is-semantic-caching/">Semantic caching for faster, smarter LLM apps</a>


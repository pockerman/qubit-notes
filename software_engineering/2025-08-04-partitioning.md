# quibit-note: Partitioning

## Overview

Whenever we want to guarantee the scalability of a data system we need to consider partitioning.
In general, by partitioning a system we try to address any scalability limitations of
a single component [2].

In this note, I will discuss the most common partitioning approaches available.
In a similar topic, we have discussed <a href="https://github.com/pockerman/qubit-notes/blob/main/ml/2025-05-11-training-patterns-for-distributed-ML.md">Training Patterns for Distributed ML</a> and
<a href="https://github.com/pockerman/qubit-notes/blob/main/ml/2025-05-07-data-ingestion-patterns-for-dist-ml.md">Data Ingestion Patterns for Distributed ML</a>.

**keywords** partitioning, software-architecture, system-design, distributed-systems

## Partitioning

For large applications, it is typically infeasible to fit the complete data set in a single server; consider for example training a machine learning model
over a large data set. In order to overcome this we want to somehow split the data into smaller groups and store these groups in multiple servers [3].

There exist various ways one can partition a dataset. Two of the most common ones are [1].

- Range partitioning
- Hash partitioning

Let's briefly discuss the two approaches.

**Range partitioning**

With range paritioning the data is divided  non-overlapping segments based on specified value ranges of a partition key column.
This technique is particularly useful for continuous partition keys, such as time, enabling efficient data organization and query optimization.
It is commonly used with date columns, where each partition can represent a specific time period like a month or quarter.
Also note that if the data is stored in sorted order on disk within each partition, we can have fast range scans [1].

Range partitioning has two main drawbacks [1]:

- If the distribution of the keys is not more or less uniform then we may have to deal with unbalanced partitions
- Some access patterns e.g. range partitioning by date, can lead to hotspots

**Hash partitioning**


Hash partitioning works by applying a hash function to a specified partition key (such as a column value or expression), which generates a hash value that determines the specific partition where the data is stored. This method ensures an even distribution of data, which helps achieve load balancing, improves query performance through parallel processing, and enhances scalability.
 
Despite the fact that hash partitioning ensures that the resulting partitions contain more or less the same number of entries, it does not eliminate hotspots [1].
This will be indeed the case if the access pattern is not uniform e.g. when a key is accessed significantly more often than others.



Regardless of the approach we want to follow in order to parition our dataset there are two challenges we need to address [3]:

- Even data distribution across the available servers
- Minimize data movement when nodes are added/removed

<a href="https://en.wikipedia.org/wiki/Consistent_hashing">Consistent hashing</a> can be used in order to solve the latter problem [3].

**Static vs dynamic partitioning**

One other question we need to address is how many partitions should we generate? This of course depends on the system we are delaing with. The number of partitions can be predetermined and
never change thereafter i.e. _static partitioning_. This is a simple approach with the obvious disadvantage; too many partitions add overhead while too few partitions limit scalability [1].

Dynamic paritioning creates partitions on-demand. Typically, we start with one partition and split thereafter when for example it exceeds a certain size or the number of requests
it serves is beyond a threshold.

## Summary

Partitioning is a key strategy for ensuring scalability in data systems by distributing datasets across multiple servers. Two common techniques are:

- range partitioning
- hash partitioning 


Range partitioning divides data into value-based segments (e.g., by date) for efficient queries but risks unbalanced partitions and hotspots. Hash partitioning, uses hash functions to evenly distribute data and improve load balancing. Both approaches may  still face hotspots under skewed access patterns. Regardless of method, challenges include achieving even data distribution and minimizing data movement when nodes are added or removed, for which consistent hashing can help. Additionally, systems must decide between static partitioning, where the number of partitions is fixed in advance, and dynamic partitioning, which creates new partitions on demand to better adapt to workload changes.

## References

1. Roberto Vitillo _Understanding Distributed Stystems. What every developer should know about large distributed apllications_
2. Dominik Tornow _Think Distributed Systems_, Manning Publications.
3. Alex Xu, _System Design Interview_. 
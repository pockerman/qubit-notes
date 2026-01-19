# quibit-note: Distributed Systems Series | Partitioning | Partitioning Part 1

## Overview

We have discussed <a href="2025-04-22-data-replication.md">qubit-note: Distributed Systems Series | Data Replication Part 1</a> as a technique to
increase the availability of a system by copying data across various locations. However, replicating the entire dataset across numerous locations can be impractical 
due to storage costs and network bandwidth requirements.

Whenever we want to guarantee the scalability of a data system we need to consider partitioning.
By partitioning a dataset we divided it into smaller pieces, each of which is accessible independently, enabling efficient reads and writes [4].
Patitioning as a technique can be applied to a number of situations e.g. partitioning TCP connections using a <a href="2025-04-21-load-balancing.md">load balancer</a> [1].
In general, by partitioning a system we try to address any scalability limitations of a single component [2].

In this note, I will discuss the most common partitioning approaches available.
In a similar topic, we have discussed <a href="https://github.com/pockerman/qubit-notes/blob/main/ml/2025-05-11-training-patterns-for-distributed-ML.md">Training Patterns for Distributed ML</a> and
<a href="https://github.com/pockerman/qubit-notes/blob/main/ml/2025-05-07-data-ingestion-patterns-for-dist-ml.md">Data Ingestion Patterns for Distributed ML</a>.

**keywords** partitioning, software-architecture, system-design, distributed-systems

## Partitioning

For large applications, it is typically infeasible to fit the complete data set in a single server; consider for example training a machine learning model
over a large data set. In order to overcome this we want to somehow split the data into smaller groups and store these groups in multiple servers [3].

----
**Remark**

When we discuss partitioning the term sharding often comes up. Sharding refers to a specific
type of paritioning namely horizontal paritioning [4].

----


There exist various ways one can partition a dataset.

- Horizontal partitioning
- Vertical partitioning
- <a href="https://www.sciencedirect.com/topics/computer-science/range-partitioning">Range partitioning</a>
- Hash partitioning
- Logical partitioning

Let's briefly discuss the two approaches.

#### Horizontal partitioning

Horizontal partitioning is frequently applied on database partitioning. However, we can use it beyon database systems.
For example, horizontal partitioning is often used in online transaction processing
(OLTP) systems [4]. 

When using horizontal partitioning on a database system, we typically partition the data on the values of specific column.
For example, if we store a ```User``` entity in our database alongoside the user's location, then we can partition the table
based on the location.  If, for example, we store timestamps we could use range partitioning (see below).

When querying the database that it has been horizontally partitioned, we first need to detrmine the partition we need
to query. However, note that maintaining consistency between the database and an index in the horizontally partitioned database can
be challenging [4].

#### Range partitioning

With range paritioning the data is divided  in non-overlapping segments based on specified value ranges of a partition key column.
This technique is particularly useful for continuous partition keys, such as time, enabling efficient data organization and query optimization.
It is commonly used with date columns, where each partition can represent a specific time period like a month or quarter.
Also note that if the data is stored in sorted order on disk within each partition, we can have fast range scans [1].

Range partitioning has two main drawbacks [1]:

- If the distribution of the keys is not more or less uniform then we may have to deal with unbalanced partitions
- Some access patterns e.g. range partitioning by date, can lead to hotspots.

#### Hash partitioning

Hash partitioning works by applying a hash function to a specified partition key (such as a column value or expression), which generates a hash value that determines the specific partition where the data is stored. This method ensures an even distribution of data, which helps achieve load balancing, improves query performance through parallel processing, and enhances scalability.
 
Despite the fact that hash partitioning ensures that the resulting partitions contain more or less the same number of entries, it does not eliminate hotspots [1].
This will be indeed the case if the access pattern is not uniform e.g. when a key is accessed significantly more often than others.

Regardless of the approach we want to follow in order to parition our dataset there are two challenges we need to address [3]:

- Even data distribution across the available servers
- Minimize data movement when nodes are added/removed

<a href="https://en.wikipedia.org/wiki/Consistent_hashing">Consistent hashing</a> can be used in order to solve the latter problem [3].

#### Vertical partitioning


Vertical partitioning is a database technique that divides records by columns rather than by rows [4]. Instead of storing complete records together, related fields are grouped into separate partitions. This approach is mainly used in OLAP systems, which are read-intensive and optimized for large analytical queries such as aggregations, joins, sorting, and machine learning workloads.

Vertical partitioning improves performance by enabling better compression, reduced read amplification, and more efficient query execution, since only the required columns are read. Storing similar data types together allows databases to compress data more effectively and leverage CPU optimizations like SIMD. It can also make some join operations faster.

However, vertical partitioning has drawbacks: it is harder to scale because each partition still spans all rows, and writes are slower since updates must touch multiple partitions. The text also distinguishes between static partitioning, where partitions are fixed in advance, and dynamic partitioning, where partitions are created or split as needed based on size or load, trading simplicity for adaptability and scalability.


We can combine both vertical and horizontal partitioning into a hybird partitioning in order to mitigate the downsides of the two [4].

#### Logical partitioning

The two main partitioning strategies for data are horizontal and vertical partitioning [4]. However, we can employ data partitioning based on the 
application needs. Load balancing  is one other way we can apply parititioning. In this section, we briefly discuss some alternative partitioning
approaches. For more details see [4] chapter 5.

- **Functional partitioning**: Functional partitioning methods partition the data based on how the application uses it i.e. the applications usage patterns.
- **Geographical partitioning**: As the name implies, in this strategy we partition the data based on geographical location e.g. the physical location of the client. 
- **User-based partitioning**: This is similar to geographical location but this time the data is partition based on the user.
- **Time-based partitioning**: Time-based partitioning is a strategy for partitioning data based on time.
- **Overpartitioning**: In this approach not only do we partition the data but also have multiple copies of each partition i.e. replicating the partitions.

#### Static vs dynamic partitioning

One other question we need to address is how many partitions should we generate? This of course depends on the system we are delaing with. The number of partitions can be predetermined and
never change thereafter i.e. _static partitioning_. This is a simple approach with the obvious disadvantage; too many partitions add overhead while too few partitions limit scalability [1].

Dynamic paritioning creates partitions on-demand. Typically, we start with one partition and split thereafter when for example it exceeds a certain size or the number of requests
it serves is beyond a threshold.

## Summary

This note introduces partitioning as a fundamental technique for achieving scalability in distributed systems, complementing data replication. Partitioning divides large datasets or workloads into smaller, independently accessible pieces, enabling efficient reads, writes, and parallel processing while avoiding the impracticality of fully replicating data.

The text reviews common partitioning strategies:

* **Horizontal partitioning (sharding):** Splits data by rows based on a partition key (e.g., user location or timestamp). Widely used in OLTP systems, it improves scalability but introduces challenges around indexing and consistency.
* **Range partitioning:** Divides data into non-overlapping value ranges (e.g., time-based partitions). It supports efficient range queries but can suffer from unbalanced partitions and hotspots.
* **Hash partitioning:** Uses a hash function to evenly distribute data across partitions, improving load balance. However, hotspots can still arise from skewed access patterns.
* **Vertical partitioning:** Splits data by columns rather than rows, primarily used in OLAP systems. It improves compression, reduces read amplification, and speeds analytical queries, but makes writes slower and scaling harder.
* **Hybrid partitioning:** Combines horizontal and vertical partitioning to balance their trade-offs.
* **Logical partitioning:** Partitions data based on application needs, such as functional, geographical, user-based, time-based partitioning, or overpartitioning with replicated partitions.

Finally, it distinguishes between static partitioning, where partitions are fixed in advance, and dynamic partitioning, where partitions are created or split on demand to adapt to data size and load, trading simplicity for flexibility and scalability.

Note that partitioning can introduce a fair amount of complexity in a system. Partition imbalances can cause the same problems that we are trying to solve and limit the
ability of  a system to scale. Partitions are independent, we will need transactions to update multiple partitions atomically [1].


## References

1. Roberto Vitillo _Understanding Distributed Stystems. What every developer should know about large distributed apllications_
2. Dominik Tornow _Think Distributed Systems_, Manning Publications
3. Alex Xu, _System Design Interview_
4. Pekka Enberg, _Latency Reduce delay in software systems_ Manning Publications

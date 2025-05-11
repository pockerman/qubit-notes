# qubit-note: Data Ingestion Patterns for Distributed ML

## Overview

In this note, I discuss three patterns for data ingestion when working with distributed ML.
Specifically, I discuss the following patterns

- Batching pattern
- Sharding pattern
- Caching pattern

**keywords** machine-learning, distributed-machine-learning, data-ingestion

## Data ingestion patterns for distributed ML


In data ingestion, batching involves grouping data records from
the entire dataset into batches that will be used to train the machine learning model
sequentially.

We can apply the batching pattern when we want to handle and prepare large datasets
for model training. When the framework we are using can handle only in-memory
datasets, we can process small batches of the entire large datasets to ensure that each
batch can be handled within limited memory. In addition, if a dataset is divided into
batches, we can perform heavy computations on each batch sequentially without
requiring a huge amount of computational resources.


### Batching pattern

If you have worked for some time with ML models then you have heard the terms batch gradient decent or
mini-bacth gradient descent. This is a version of the classic gradient descent algorithm where we don't
feed the training data into the model all at once but rather split the data into chunks and sequentially
pass these chunks to the model.

The batching pattern is essentially this; split the dataset into chunks and feed these chunks to the model.
Thus, batching groups the data into batches that is then used to train the ML model sequentially.
This pattern allows us to deal with smaller chunks of data each time.

Batching can really slow down training. This is where we can use sharding.


### Sharding pattern

Sharding as a concept it's not new. Indeed it is used when working with distributed databases in order to
split data or workload across multiple machines (nodes) to improve scalability, performance, and availability.
Sharding is simply the process of splitting a  large datasets into smaller bits that is spread across multiple nodes.

We can use the same idea when training ML models. Meaning we can have multiple computing nodes that each
node has a copy of the model. At every epock, we train each copy of model on a different shard and then somehow communicate
the local copies of the models to all participating workers. Notice that we can also mix batching when the shard is rather large.

### Caching pattern

The last pattern I want to discuss is caching. Caching is a well known technique that is used to improve the time response
of an application. It involves storing relevant data in memory rather than fetching the data from the database.
This idea can be applied when training ML models.

When training ML models we iterate over a number of epochs i.e. steps that our model sees the entire dataset.
Assuming that there is enough RAM memory on the compute nodes, we can store the batches in the RAM instead of fetching
from hard disk; fetching 1MB of data from the disk takes about 30 ms but referencing the main memory takes about 100 ns [2].
This is however, a bit counterintuitive as we have assumed that the dataset is so large that can't fit in RAM.
Although caching in RAM is more popular particularly when fetching data from remote databases, we can also cache on disk.
Examples include; ``joblib```, ```diskcache``` and ```sqlite```. As mentioned above this won't be as fast as caching in RAM,
but definitely it improves the performance when comprated to simply fetching the batch from the disk.


## References

1. Yuan Tang, _Distributed Machine Learning Patterns_, Manning Publications, 2024.
2. Alex Xu, _System Design Interview. An insider's guide_, 2020.
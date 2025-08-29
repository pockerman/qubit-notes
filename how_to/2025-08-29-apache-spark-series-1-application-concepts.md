# qubit-note: Apache Spark Series 1-Application concepts

## Overview

This qubit note opens a series of notes on <a href="https://spark.apache.org/">Apache Spark</a>. Specifically, some core concepts on how an Apache Spark application is executed
These concepts allow us to better understand what Spark is doing behind the scenes when its executing our programs. The material in this post is taken from the excellent book <a href="https://www.oreilly.com/library/view/learning-spark-2nd/9781492050032/">Learning Spark. Lighting-fasts data analytics</a>. Moreover, you can find a complete set of notes on Spark at <a href="https://github.com/pockerman/ml_notes">Statistics, Probability \& Machine Learning Notes</a>. Whilst Spark is written in Scala it also supports Java and Python i.e. you can write your programs
in any of the three languages. In this series we will be using Python.

**keywords** Apache-Spark, big-data, high-performance-computing, Python 

## Application concepts for Apache Spark

Let's begin by introducing the following terms [2]:

- Application
- ```SparkSession```
- Job
- Stage
- Task

An application is a user's program that is built using Spark's APIs. It consists of a driver program and executors on the cluster. A job consists, possibly, of many stages that depend on each other. This dependency is organized into a Direct Acyclic Graph or DAG. Each node in the DAG represents a stage [1]. Furthermore, each stage is composed of tasks.    A task is the unit of work in Spark that is executed by an executor. An executor is typically a computing node on the cluster that Spark is deployed. A computing node may be a multicore machine.  Thus, each task is mapped to a single core and works on a single partition of the data. The following article <a href="https://medium.com/@goyalsaurabh66/spark-basics-rdds-stages-tasks-and-dag-8da0f52f0454">Spark Basics : RDDs,Stages,Tasks and DAG</a> describes nicely these concepts. The last term is ```SparkSession```. It provides an entry point for interacting with the underlying functionality that Spark offers. 

A ```SparkSession``` is either created automatically for us, this will be the case when using the shell, or the application needs to instantiate one. The following snippet shows this: 

```
from pyspark.sql import SparkSession

def main():
    # Your additional code goes here (e.g., argument parsing, data loading, etc.)
    
    app_name = "MySparkApp"

    spark = SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

    # ... your processing logic here ...

    # Stop the SparkSession when done
    spark.stop()

if __name__ == "__main__":
    main()

```

----
**Remark 1**

Note that there can be only one ```SparkSession``` per JVM. 

----

### Transformations & actions

Let's now turn into what operations can we execute. Operations on a distributed data set can be classified into two types; transformations and actions [2]. 
You can find more information on these two operations in <a href="https://spark.apache.org/docs/latest/rdd-programming-guide.html">RDD Programming Guide</a>. 
Below I just give a brief overview of what each operation entails.


#### Transformations

Transformations in Spark transform a ```DataFrame``` into a new one. This is done without altering the original data. Hence a transformation is an immutable operation as far as the original data is concerned. Some examples of transformations are listed below:

- ```orderBy()```
- ```groupBy()```
- ```filter()```
- ```join()```

All transformations in Spark are evaluated lazily [2] (see <a href="https://en.wikipedia.org/wiki/Lazy_evaluation">Lazy evaluation</a>). What this means is that their results are not computed immediately; instead a transformation in encoded as a lineage. This allows Spark to rearrange certain transformations, coalesce them or perform certain optimizations for more efficient execution (e.g. by joining or pipelining some operations and assign them to a stage) [2].

----

**Remark 2**

Lazy evaluation allows Spark to optimize our queries. Lineage and data immutability allow for fault tolerance [1]. Since Spark records all transformations in its lineage and the ```DataFrames``` are immutable between the transformations, it can reproduce the origin data by simply replaying the recorded lineage [1].


----

**Wide and narrow transformations**

We can classify transformations according to the dependencies they have as transformations with _narrow dependencies_ or transformations with _wide dependencies_ [2]. A narrow transformation is a transformation that can be computed from a single input. In particular, a narrow transformation does not need to exchange data with other partitions (of the data) in order to compute the result. Wide transformations read data from other partitions in order to compute the result. ```groupBy``` or ```orderBy``` are two transformations that instruct Spark to perform wide transformations [2]. Evidently, we should avoid wide transformations if possible.

#### Actions

An action triggers the lazy evaluation of all the recorded transformations [2]. A list of actions is given below.

- ```show()```
- ```take()```
- ```count()```
- ```collect()```

#### Query plan

Both actions and transformations contribute to a query plan in Spark [2]( the following article on Medium is a nice review on the topic <a href="https://medium.com/the-code-shelf/spark-query-plans-for-dummies-6f3733bab146">Spark Query Plans for Dummies</a>). Nothing in this plan is executed until an action is invoked [2].

## Summary

In this note I went briefly onto some of the basic but core concepts in Spark. Specifically, we saw what a job, a stage, and a task are. And how these are used to organize computation in Spark. Furthermore, we touched upon the ```SparkSession``` construct. This entity gives us access to all the functionality provided by Spark. Finally, we saw the two types of operations that we can apply of an RDD. Namely transformations and actions. We will come back to these topics as these an occurring theme when working with Spark.

In <a href="2025-08-29-apache-spark-series-2-hello-world.md">qubit-note: Apache Spark Series 2-Hello World</a> I will describe how to submit a standalone Python application to Spark for execution.

## References

1. <a href="https://spark.apache.org/">Apache Spark</a>
2. Jules S. Damji, Brooke Wenig, Tathagata Das, Deny Lee, _Learning Spark. Lighting-fasts data analytics_, 2nd Edition, O'Reilly.

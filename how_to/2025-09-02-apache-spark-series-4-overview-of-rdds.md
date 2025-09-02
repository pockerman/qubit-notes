# qubit-note: Apache Spark Series 4-Overview of RDDs

## Overview

In  <a href="2025-08-29-apache-spark-series-1-application-concepts.md">qubit-note: Apache Spark Series 1-Application concepts</a> we went over some basic but core concepts associated with Apache Spark. In this qubit note, I will introduce the most basic abstraction in Spark namely the RDD (or the Resilient Distributed Dataset) [2].   Although, modern applications most likely will be using the ```DataFrame``` and/or ```DataSet``` APIs, still the RDD data structure is what lies underneath the latter two and therefore always useful to know.  As we will see, there are various methods to create an RDD in Spark. The following example is taken for <a href="https://sparkbyexamples.com/apache-spark-rdd/how-to-create-an-rdd-using-parallelize/">Spark by {Examples}</a>.

## Overview of RDDs

The RDD is perhaps the most basic abstraction in Spark. An RDD is an immutable collection of objects that can be distributed across a cluster of computers. An RDD collection is divided into a number of partitions so that each node on a Spark cluster  can independently perform computations. There are three concepts associated with an RDD [2]:

- Dependencies
- Partitions
- Compute function

Partitions provide the ability to split the work and therefore to parallelize computation across executors. The compute function produces the data that will be stored in the RDD. Finally the dependencies, inform Spark how an RDD is constructed. This allows for RDD resiliency as Spark, if needed, is able to recreate the RDD from the dependencies [2]. 

Now that we have a very simplified overview of what an RDD is, let's how we can create one. 

### Create a Spark RDD with Python

There are two main methods available in Spark to create an RDD: 

- ```SparkContext.parallelize``` method
- Read from a file

The first method is illustrated in the code listing example below:

```
from pyspark import SparkConf, SparkContext

def main():
    # Initialize Spark configuration and context
    conf = SparkConf().setAppName("Hello Spark RDD")
    sc = SparkContext(conf=conf)

    # Create an RDD from an array of numbers
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rdd = sc.parallelize(data)

    # Perform an action on each element
    rdd.foreach(lambda x: print(x))

    # Display number of partitions
    print("Number of Partitions:", rdd.getNumPartitions())

    # Perform an action: get first element
    print("Action: First element:", rdd.first())

    # Stop the Spark context
    sc.stop()

if __name__ == "__main__":
    main()

```

----

**Remark**

Creating a ```SparkContext``` is not necessary when we use the Spark shell as one such object is already created for us.

----

The second method is to read a file from disk. This is also shown in the snippet below.

```
from pyspark import SparkConf, SparkContext

def main():
    # Initialize Spark configuration and context
    conf = SparkConf().setAppName("Hello Spark RDD")
    sc = SparkContext(conf=conf)

    # Path to your CSV file
    csv_file = "/home/alex/qi3/learn_scala/scripts/spark/data/train.csv"
    csv_rdd = sc.textFile(csv_file)

    # Display number of partitions
    print("Number of Partitions:", csv_rdd.getNumPartitions())

    # Print the first element (header)
    print("Action: First element:", csv_rdd.first())

    # Stop the Spark context
    sc.stop()

if __name__ == "__main__":
    main()

```

However, we are interested in converting the contents of the file into floating point numbers so that we can feed them to a machine learning algorithm. We can do this as follows.  we can use the ```map()``` function to convert the ```RDD[String]``` into an ```RDD[Array[Double]]```


```
from pyspark import SparkConf, SparkContext

def parse_line(line):
    try:
        arr = line.split(",")
        return [float(arr[0]), float(arr[1]), float(arr[2])]
    except Exception:
        # Return default values on failure
        return [-100.0, -100.0, -100.0]

def main():
    conf = SparkConf().setAppName("Parse CSV to Double RDD")
    sc = SparkContext(conf=conf)

    csv_file = "/home/alex/qi3/learn_scala/scripts/spark/data/train.csv"
    csv_rdd = sc.textFile(csv_file)

    double_rdd = csv_rdd.map(parse_line)

    # Example: Collect a few elements to see the result
    print(double_rdd.take(5))

    sc.stop()

if __name__ == "__main__":
    main()

```

We can also use a schema in order to let Spark know the type of the data but this requires that we use a ```DataFrame``` instead and not an RDD.
Note also that Spark divides by default data into two partitions and distributes them across a cluster. The number of partitions can be specified while creating an RDD as shown below.

```
from pyspark import SparkConf, SparkContext

def main():
    conf = SparkConf().setAppName("Hello Spark RDD File with Partitions")
    sc = SparkContext(conf=conf)

    # File path (adjust to your system)
    csv_file = "/home/alex/qi3/learn_scala/scripts/spark/data/train.csv"

    # Specify number of partitions (4 in this case)
    csv_rdd = sc.textFile(csv_file, minPartitions=4)

    print("Number of Partitions:", csv_rdd.getNumPartitions())
    print("First element:", csv_rdd.first())

    sc.stop()

if __name__ == "__main__":
    main()

```

### Other methods

As an aside, we can create an RDD by using the following also:

- JDBC
- Cassandra
- HBase
- Elasticsearch

## Transformations and actions

In <a href="2025-08-29-apache-spark-series-1-application-concepts.md">qubit-note: Apache Spark Series 1-Application concepts</a>  we introduced the two types of operations one can apply on an RDD namely transformations and actions [1]. 
You can find more information on these two operations in <a href="https://spark.apache.org/docs/latest/rdd-programming-guide.html">RDD Programming Guide</a>. Below we just give a brief overview of what each operation entails.

### Transformations

Transformations in Spark transform a ```DataFrame``` into a new one. This is done without altering the original data. Hence a transformation is an immutable operation as far as the original data is concerned. Some examples of transformations are listed below [3]

- ```map(function)```: It returns a new data set by operating on each element of the source RDD.
- ```flatMap(function)```: Similar to map, but each item can be mapped to zero, one, or more items.
- ```mapPartitions(function)```: Similar to map, but works on the partition level.
- ```mapPartitionsWithIndex(function)```: Similar to ```mapPartitions```, but provides a function with an Int value to indicate the index position of the partition.

- ```filter(function)```: It returns a new RDD that contains only elements that satisfy the predicate.
- ```union(otherDataset)```: It returns a new data set that contains the elements of the source RDD and the ```otherDataset```  RDD. Note that the participating RDDs should be of the same data type.

- ```intersection(otherDataset)```: It returns a new data set that contains the intersection of elements from the source RDD and the argument RDD.

### Actions

An action triggers the lazy evaluation of all the recorded transformations [1]. A list of actions is given below [3].

- ```collect()```: Returns all the elements of the data set are returned as an array to the driver program.
- ```count()```:  Returns the number of elements in the data set.
- ```reduce(function)```: It returns a data set by aggregating the elements of the RDD it is applied on. The aggregation is done by using  the user provided ```function``` argument. The ```function``` should take two arguments and returns a single argument. Moreover it should be commutative and associative so that it can be operated in parallel. 

- ```first()```: Returns the first element in the data set.
- ```take(n)```: Returns the first ```n``` elements in the data set as an array.
- ```takeOrdered(n, [ordering])```: Return the first ```n```  elements of the RDD using either their natural order or a custom comparator.
- ```takeSample(withReplacement, num, [seed])```: Returns an array with a random sample of num elements of the dataset, with or without replacement, optionally pre-specifying a random number generator seed.
- ```saveAsTextFile(path)```: Write the elements of the RDD as a text file in the local file system, HDFS, or any another supported storage system.
- ```foreach(function)```: Applies the ```function``` argument on each element in the RDD.

## Summary

This qubit note introduces Apache Spark’s Resilient Distributed Dataset (RDD), the fundamental abstraction underlying Spark’s higher-level APIs such as DataFrame and Dataset. It explains that RDDs are immutable collections distributed across a cluster and composed of partitions, dependencies, and compute functions, which together enable fault tolerance and parallel computation. The document outlines two main methods to create an RDD—using SparkContext.parallelize for in-memory collections and textFile() for files—along with examples of reading CSV files, handling parsing errors, and setting custom partitions. It also provides an overview of transformations (which create new RDDs without altering the original data) and actions (which trigger computation and return results), listing key operations for both categories.

## References

1. <a href="https://spark.apache.org/docs/latest/rdd-programming-guide.html">RDD Programming Guide</a>
2. Jules S. Damji, Brooke Wenig, Tathagata Das, Deny Lee, _Learning Spark. Lighting-fasts data analytics_, 2nd Edition, O'Reilly.
3. Subhashini Chellappan, Dharanitharan Ganesan, _Practical Apache Spark. Using the Scala API_, Apress
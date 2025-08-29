# qubit-note: Apache Spark Series 2-Hello World

## Overview

In  <a href="2025-08-29-apache-spark-series-1-Application concepts.md">qubit-note: Apache Spark Series 1-Application concepts</a> we went over some basic but core concepts associated with Spark. In this note, I describe the steps you need to take in order to submit a self-contained application to be executed by Spark. You should also check the official documentation on <a href="https://spark.apache.org/docs/latest/quick-start.html#self-contained-applications">Self-contained Applications</a>. 

**keywords** Apache-Spark, big-data, high-performance-computing, Python

## Apache Spark Hello World

I will assume that the environment is already set.If you haven't installed Spark on your machine check the documentation here <a href="https://spark.apache.org/downloads.html">Download Apache Spark</a>.
In this note, I will be using Spark-4.0.0.

The following script is a simple _Hello World_ example application to be executed by Spark:

```
from pyspark import SparkConf, SparkContext

def main():
    conf = SparkConf().setAppName("Hello Python Spark")
    sc = SparkContext(conf=conf)

    print("Spark version:            ", sc.version)
    print("Spark master:             ", sc.master)
    print("Spark running 'locally'?: ", sc.master.startswith("local"))

    sc.stop()

if __name__ == "__main__":
    main()
```

Let's submit this application to Spark. For this we need to execute the ```spark-submit``` script in the bin directory of your Spark installation:

```
/your/path/to/spark/bin/spark-submit hello_spark.py
```

Running the script produces the following: 

```
...
Spark version:             4.0.0
Spark master:              local[*]
Spark running 'locally'?:  True
...

```

Note that running the Script will produce a lot more output. We will see how to control the logging level in another note.


## Summary

This note, part of the Apache Spark Series, demonstrates how to create and run a simple "Hello World" application using Apache Spark (version 4.0.0). Building on the concepts introduced in the first series note, it walks through setting up a minimal PySpark script that initializes a SparkContext, prints basic Spark environment details (version, master, and whether it's running locally), and shuts down the context. The guide also explains how to execute this application using the spark-submit command and provides an example of the expected output.

## References

1. Jules S. Damji, Brooke Wenig, Tathagata Das, Deny Lee, _Learning Spark. Lighting-fasts data analytics_, 2nd Edition, O'Reilly.
# qubit-note: Apache Spark Series 3-Create a Toy Apache Spark Cluster With Docker

## Overview

In  <a href="2025-08-29-apache-spark-series-1-application-concepts.md">qubit-note: Apache Spark Series 1-Application concepts</a> we went over some basic but core concepts associated with Spark. In this note, I describe the steps you need to take in order to submit a self-contained application to be executed by Spark. You should also check the official documentation on <a href="https://spark.apache.org/docs/latest/quick-start.html#self-contained-applications">Self-contained Applications</a>. 

**keywords** Apache-Spark, big-data, high-performance-computing, Python, Docker

## Create a toy Apache Spark cluster with Docker

In this qubit-note we will create a toy Apache Spark cluster using Docker. The following docker-compose file will create a master node and two workers

```
version: "3.8"
services:
  spark-master:
    image: bitnami/spark:latest
    container_name: spark-master
    environment:
      - SPARK_MODE=master
    ports:
      - "8080:8080"
      - "7077:7077"
    networks:
      - spark-net
    volumes:
      - /home/alex/.ivy2:/opt/bitnami/.ivy2

  spark-worker-1:
    image: bitnami/spark:latest
    container_name: spark-worker-1
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    networks:
      - spark-net

  spark-worker-2:
    image: bitnami/spark:latest
    container_name: spark-worker-2
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    networks:
      - spark-net

networks:
  spark-net:

```

We will use the script for <a href="2025-08-29-apache-spark-series-2-hello-world.md">qubit-note: Apache Spark Series 2-Hello World</a> as a script to submit to our cluster.
Submit the script by opening a terminal and navigate where the ```hello_spark.py``` is located and issue:

```
docker cp hello_spark.py spark-master:/opt/bitnami/spark/hello_spark.py
docker exec -it spark-master   spark-submit --conf spark.jars.ivy=/tmp/.ivy2 --master spark://spark-master:7077 /opt/bitnami/spark/hello_spark.py
```

Open http://localhost:8080/ and you will be able to access the UI for the master node and the application status.


## Summary

In this qubit note we created a small Apache cluster using Docker having one master node and two workers. We also submitted a toy Spark application in the cluster
and accessed the master node UI allowing to investiagte the application status.

## References

1. <a href="https://spark.apache.org/docs/latest/cluster-overview.html">Cluster Mode Overview</a>
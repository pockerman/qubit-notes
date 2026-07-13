# qubit-note: Kubernetes | Intro to Kubernetes

## Overview

Kubernetes is a computing platform for managing container-based applications. It was originally created by Google but is now managed by the Cloud Native Computing Foundation (CNCF), a committee that has huge industry support and is also responsible for many other interesting projects.


In this book, Kubernetes is presented as the production “backbone” for running microservices: a container orchestration platform that manages and automates deploying and scaling container-based applications, and is framed as “a platform for microservices.” 

The book emphasizes why Kubernetes is a practical choice: it’s becoming a standard platform for distributed apps, it’s easier to use via managed cloud offerings (the book uses Azure), and it also comes bundled with Docker Desktop for local learning/experimentation.  

Core Kubernetes concepts the book focuses on are:

A cluster is made of nodes (typically VMs), and nodes run pods (the basic unit of computation). Pods can contain one or more containers, but the book keeps it simple by running one microservice per pod.  

Rather than running “naked” pods, the book jumps straight to using a Deployment to manage pods in production. The Deployment monitors pods and replaces them if they crash or hang, and it can run multiple replicas for redundancy and load balancing. 

A Service exposes the pods and creates DNS records so other components can reach them by name. 

Later chapters connect Kubernetes to reliability and scaling: Kubernetes health checks (readiness and liveness probes) help detect unhealthy services and restart them, and Kubernetes supports horizontal and elastic scaling (scaling the cluster by adding nodes, and scaling individual microservices by increasing replicas, potentially automatically).  

Finally, the book highlights Kubernetes’ automatable API as a key enabler for building an automated continuous deployment pipeline. 


## Summary
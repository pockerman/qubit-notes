# qubit-note: Kubernetes | Create a Kubernetes Cluster on AWS

## Overview

In this qubit note we will discuss how to create a Kubernetes cluster on AWS. Specifically, how to create a Kubernetes cluster on 
<a href="https://aws.amazon.com/eks/">Amazon Elastic Kubernetes Service (EKS)</a>. Amazon EKS is a managed Kubernetes service that automates cluster operations, making it easier to deploy and scale containerized applications on AWS and other environments.


## Create a Kubernetes Cluster on AWS

To create a cluster in Amazon EKS, you need the following:

- An Amazon Web Services account
- AWS CLI installed
- ```eksctl``` CLI tool installed (this is the official CLI for AWS EKS)

After you’ve installed the AWS CLI, authenticate the client to access your AWS account:

```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: eu-central-1
Default output format [None]:
```

The ```eksctl``` tool is the official CLI for Amazon EKS. It uses the AWS credentials you’ve
configured to authenticate with AWS. Using eksctl, create the cluster:

```
eksctl create cluster --name my-first-k8-cluster --region eu-central-1
```

By default, eksctl creates a cluster with two worker nodes in the specified region. You can adjust this paramater by specifying the --nodes flag.
When you no longer need the EKS cluster, delete it to avoid being charged for unused resources:

```
eksctl delete cluster my-first-k8-cluster --region eu-central-1
```

## References

1. <a href="https://aws.amazon.com/eks/">Amazon Elastic Kubernetes Service (EKS)</a>
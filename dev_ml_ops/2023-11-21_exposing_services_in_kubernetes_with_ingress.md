# Exposing services in Kubernetes with Ingress

## Overview

In <a href="kubernetes_101.md">Kubernetes 101</a>, I discussed how to use a Kubernetes _Service_ in order to create a simple API gateway.
Despite the simplicity of the approach, it has some noticeable disadvantages. 
Namely, it becomes problematic when a large numbers of services is used, since each service needs its own public IP address. 

We can overcome the aforementioned problem by exposing these services through an _Ingress_ object, see  [1] for more details.
Apart from providng a single IP address, an _Ingress_ object provides HTTP authentication, cookie-based session affinity and URL rewriting [1].
These are features that a service object cannot provide. An _Ingress_ object can be used to expose a single service but typically,
we use it alongside multiple services.

In this post, I will continue from where we left in <a href="kubernetes_101.md">Kubernetes 101</a> and use _Ingress_ in order to expose
the services. In addition, I would like to have a more realistic scenario; one service will provide access to trained ML models whilst the
other service will give access to the data scientist to trigger a new pipeline for training the model. Furthermore, it will allow the data scientist
to update the datasets used for training the models. Note that <a href="https://www.kubeflow.org/">kubeflow</a> can be used in order to implement what
I am trying to do here. I will discuss this in another post.

The material covered in this post is discussed in great detail in [1].
 You can find the source code for this post here <a href="https://github.com/pockerman/kubernetes_ml_service">kubernetes_ml_service</a>.
 In order to use the files make sure that you build  your own Docker images and push these a public Docker hub repository. For example,


 ```
 cd info_service
 docker build -t kubernetes-ml-info-api:0.1 .
 docker tag kubernetes-ml-info-api:0.1 <your-repo-name>/<your-image-name>:<your-image-tag>
 docker push <your-repo-name>/<your-image-name>:<your-image-tag>

 ```

 Depending on your setting, you many need to login to docker via the docker CLI using

 ```
 docker login
 ```

You can test if a container runs successfully by running

```
docker run --rm -p <container-exposed-port>:<app-port> --name <container-name>  <image-name>:<image-tag>
```

 Note also that you may need to adapt the supplied Kubernetes files to match the names above. 

**keywords:** kubernetes, kubernetes-ingres, docker, api-gateway, mlops, ml-system, python

## Exposing services in Kubernetes with Ingress

_Ingress_ in Kubernetes is a way to expose services that are running in the cluster to external clients.
It has the follwoing three components [1]:

- An API object which is for defining and configureing an ingress object.
- A load balancer responsible for routing traffic to the backend services
- A controller that minitors the API for ingress objects and deploys the load balancer.

### Kubernetes _Ingress_

Exposing services via an _Ingress_ object is done via referecing the related service objects
in the aforementioned _Ingress_ object. Kubernetes then uses the _Ingress_ object to
configure a load balancer that makes the services accessible to external clients through a common entrypoint [1].

An _Ingress_ object will use the information in the HTTP header in order to properly route the request
to the right service. The public DNS entries for the involved services under the _Ingress_ object, point
to the same object. Thus, if the client request specifies ```models-price-prediction.io``` the _Ingress_ 
forwards this to the pods that belong to the ```models-price-prediction``` service.

#### Ingress controller

 This controller is the link between the _Ingress_ object and the actual physical ingress (the reverse proxy). Often the controller and the proxy run as two processes in the same container or as two containers in the same pod. You can find a list of the avilable _Ingress_  controllers here: <a href="https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/">Ingress Controllers</a>


 If you use minikube to run Kubernetes, you install the controller as

 ```
 minikube addons enable ingress
 ```

 Note that  _Ingress_ uses virtual hosting to figure out where to forward the request, you won’t get the desired result by simply sending an HTTP request to the Ingress’ IP address and port. You need to make sure that the Host header in the HTTP request matches one of the rules in the Ingress object.

### The application

Now that I have an understanding what _Ingress_  constitutes, I will create a small cluster that implements some machine learning related fucntionality.
The cluster will expose the following services

- info listening at port 8000
- serve listening at port 8001
- train listening at port 8002
- service-404 listening at port 8003

These services will be run in their own pods; see the ```setup``` directory in the provided source code.

#### Info service

The first service we will implement is simple; exposes one endpoint that names the services available. How to build the pod and the service manifest files can 
be found in <a href="kubernetes_101.md">Kubernetes 101</a> and also in [1]. The ```setup``` directory in the code source files already contains these files for you.
Make sure that yo

#### Serve and train service

The serve service is used to access the trained machine learning model. 

An Ingress object can contain many rules and therefore map multiple hosts and paths to multiple services. You’ve already created an Ingress for the _ml-info-service-com_ service. Now we will create one for the _ml-serve-service_ and _ml-train-service_ services.


```
/usr/local/lib/python3.10/site-packages/sklearn/base.py:348: InconsistentVersionWarning: Trying to unpickle estimator LogisticRegression from version 1.1.2 when using version 1.3.2. This might lead to breaking code or invalid results. Use at your own risk. For more info please refer to:
https://scikit-learn.org/stable/model_persistence.html#security-maintainability-limitations
  warnings.warn(

```


### Exposing the application

Now that we have an understanding what each service is meant to do, let's see how we can expose these services via Kubernetes.
Fire up ```minikube``` or whichever tool you happen to use.

```
minikube start
```

Then we need to  setup the pods and the services we want to expose. The ```setup``` directory contains the manifest files we need.

```
minikube kubectl -- apply -f setup/ --recursive
```

Similarly, we can create the _Ingress_ object

```
minikube kubectl -- apply -f ingress/ --recursive
```

We can check the created _Ingress_ objects via

```
minikube kubectl -- get ingresses
```

Let's try to access these objects. I will use a simple Python script that utilizes Python's ```requests``` module. Check the supplied code. 


## Summary

In this post I went over how to set up and use _Ingress_ in Kubernetes.
Although we focused on having a single _Ingress_ object with our Kubernetes cluster, this need not be the case.
Multiple _Ingress_ objects are also possible and each one of these will get their own IP address [1]. _Ingress_ involves quite a bit of details that
I have not covered herein. The interested reader is refered to [1] chapter 12, and the official documentation in [2].

In the presented example, I glossed over various essential details. For example, I assumed that the user supplied dataset is a simple file that can be stored in memory.
This may not necessarily be true and in fact for most interesting scenarios this is rather an oversimplification. Additionally, when a model makes a prediction
we need to monitor the prediciton it made with the given data so that we can retrain the model. In order to do so we need to persist the data somehow.
Also, typically, we will launch a number of workers that run our model and propagate the request to one of them. We will start addressing some of the
shortcomings in later posts.


## References

1. <a href="https://www.manning.com/books/kubernetes-in-action-second-edition">_Kubernetes in Action_, Manning Publications, 2nd Edition</a>.
2. <a href="https://kubernetes.io/docs/concepts/services-networking/ingress/">Ingress</a>
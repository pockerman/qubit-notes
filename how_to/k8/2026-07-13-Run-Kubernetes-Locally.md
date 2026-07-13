# qubit-note: Kubernetes | Run Kubernetes Locally


## Overview

Often we want to try out a technology before fully adopt it. We can use minikube in order to try out Kubernetes on our local machine.



##  Run Kubernetes Locally


Minikube is a tool that lets you easily use Kubernetes on your local machine.
To install the Minikube CLI locally, you can get the latest prebuilt release or build
from source. To install the latest release of minikube on a Linux-based machine, do:

```
wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 -O minikube
$ sudo install -m 755 minikube /usr/local/bin/minikube
```

This will put the minikube binary in your path and make it accessible from everywhere.
Once it’s installed, you can verify the Minikube version with the following command:

```
minikube version


minikube version: v1.38.1
commit: c93a4cb9311efc66b90d33ea03f75f2c4120e9b0
```

Minikube can be deployed as a virtual machine, a container, or bare metal. This is
configured using the ```--driver``` flag while creating a cluster on Minikube. When this
flag is not specified, Minikube will automatically select the best available runtime environment.


---
**Remark**

A hypervisor is a software or hardware component that creates and manages virtual
machines. It is responsible for allocating and managing the physical resources (CPU,
memory, storage, network) of a host system and allowing multiple virtual machines
(VMs) to run concurrently on the same physical hardware. 

---

Minikube supports a
range of hypervisors, such as VirtualBox, Hyperkit, Docker Desktop, Hyper-V, and so
on. The drivers page gives an overview of the supported runtimes.

Minikube can also use a container runtime to create a cluster on a host machine.
This driver is available only on a Linux-based host, where it’s possible to run Linux
containers natively without having to use a VM. While a container-based runtime
does not offer the same level of isolation as a virtual machine, it does offer the best
performance and resource utilization. At the time of writing, Minikube has support
for Docker Engine and Podman (experimental).
Other tools that can be used for running local Kubernetes clusters using Linux
containers are as follows:

- Kubernetes in Docker Desktop 
- kind
- k3d


Use the minikube start command to create a Kubernetes cluster locally:

```
minikube start
```

By default the cluster will be allocated 2 GB of RAM. If you don’t like the defaults, you
can override parameters such as the memory and number of CPUs, as well as picking
a certain Kubernetes version for the Minikube VM—for example:

```
minikube start --cpus=4 --memory=4096 --kubernetes-version=v1.27.0
```

Additionally, you can specify the number of cluster nodes by overriding the default value of one node:

```
minikube start --cpus=2 --memory=4096 --nodes=2

```

To inspect the status of the Minikube cluster do:

```
minikube status
```

Similarly, to inspect the status of the Kubernetes cluster running inside Minikube do:

```
kubectl cluster-info
```

The Minikube CLI has built-in help that you can use to discover the subcommands on your own.
Aside from start, stop, and delete, you should become familiar with the ip, ssh, tunnel, dashboard, and docker-env commands.

---
**Remark**

If for any reason your Minikube becomes unstable or you want to
start fresh, you can remove it with minikube stop and minikube
delete. Then minikube start will give you a fresh installation.

---

## References
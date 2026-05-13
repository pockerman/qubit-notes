#qubit-note: Distributed Systems | Resiliency | Liveness and Readiness Checks

## Overview

In this note we will look into another topic when it comes to the resiliency of a distributed system.
Namely we will look into:

- Liveness checks
- Readiness checks

Both can be implemented at the load balancer level.


## Liveness and readiness checks

In plain words, a liveness check verifies that an application instance is still running properly. Moreover, it will trigger a restart if that it's not the case.  A  readiness check determines if the application is prepared to handle requests. It thus informs the  load balancer whether it should send traffic to it.

There isn't much else into this so let's see how to implement them and how they are used in practice.

So in practice, a liveness check should a lightweight test to confirm the process is alive and functioning.
We don't want to it to be a heavy weight test as we will run it periodically.
If the liveness check fails, the the operatting environment should restart the process in order to recover from the failuer [1].
As an example, Kubernetes uses liveness probes to detect situations like deadlocks or crashes; it restarts the container to restore service availability. A simple liveness probe could be an HTTP GET to ```/health``` that returns success if the app process is up. Alternatively, it could be a low-level check (like responding to a ping or executing a trivial command in the app). If this check fails (e.g., the app doesn’t respond or returns an error), the system knows the app isn’t healthy and should be restarted [1].

In summary, here some key points about liveness checks [1]:

- **Purpose:** Ensure the application continues to run. It’s essentially a heartbeat or ping; if the heart stops (check fails), the platform assumes the app is dead and needs restarting.
- **On failure:** A failing liveness check triggers a restart. 
- **Implementation:** Liveness checks are often minimal and fast. 


Although the application is may be up  and running, it might not be ready to handle traffic.
A readiness check is designed to prevent traffic from reaching instances that can’t fully serve requests [1].
Thus upon failure of a readiness check, the instance is marked unready and removed from the load balancer’s pool of active servers.

Unlike liveness, a failing readiness check does not restart the app. It simply tells the load balancer (or orchestrator) to stop sending new traffic to that instance until it becomes ready again [1].

In load-balanced architectures, both checks are vital for  high availability and smooth deployments. Specifically [1]:

- High vailability
- Zero-downtime deployments
- Graceful degradation
- Auto-healing
- Protection against false alarms 


## Summary

In this note we discussed liveness and readiness checks. Both liveness and readiness checks are types of health checks used in modern cloud environments (especially in microservices and container orchestration like Kubernetes) to improve reliability.

A liveness check is essentially a heartbeat. When a liveness check fails the environment will typically restart the failing
process. On the other hand when a readiness check fails the process is removed from the pool of the available process in the load balancer.

## References

1. <a href="https://www.designgurus.io/course-play/grokking-scalable-systems-for-interviews/doc/what-is-the-difference-between-liveness-checks-and-readiness-checks-in-load-balancers">What Is the Difference between Liveness Checks and Readiness Checks in Load Balancers?</a>

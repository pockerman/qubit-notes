# qubit-note: Backend-for-frontend Pattern

## Overview

In this short note, we will go over the so called <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends">backend-for-frontend pattern</a> or BFF.

The microservice architecture  is a well established architectural pattern for modern day software. 
This pattern poses some core advantages over  software monoliths such as scaling and deploying independently.

One problem that arises when we use microservices is the fact that often the client, e.g a web browser, needs to make 
multiple calls to perhaps multiple services in order to create the corresponding view. This has
two main disadvantages:

- Increase the latency needed to load a view (and consequently reduce the user experience)
- Forces the client to be aware of the various services that it needs to call (this can cause serious problems when we think software maintainance)

The <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends">backend-for-frontend pattern</a> 
is a pattern that we can utilise to reduce the number of service calls the client has to undertake.


**keywords** system-design, software-architecture, software-patterns, microservices

## Backend-for-frontend pattern

One of the problem that surfaces when working with microservices is that often in order for a client to fulfill its mission it needs
to make a number of API calls. This of course increases the latency and diminishes the user experience. 

One architecture pattern we can employ in order to solve such a problem is the <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends">backend-for-frontend pattern</a>. In this pattern, the client communicates with a service that it is responsible for aggregating the responses of the needed API calls.
This approach has several advantages such as cutting down the number of requests the client has to do on our servers.
Instead of customizing the backend for the various clients, we use a third service to manipulate the needed data for every client.
Additionally, we can  embed logic related to failovers and/or
retries inside of this service.


A BFF is intentionally thing and most BFFs use lightweight frameworks in Node.js, Go, or similar languages optimized for I/O rather than computation [4].
The core logic is aggregation i.e. calling backend services in parallel where possible, combining responses, and returning a shaped payload. However, complexities arise when dealing with handling failure. When one of five backend calls times out, the BFF must decide whether to return partial data, substitute defaults, or fail the entire request. Aggressive timeouts are essential since a BFF that waits 30s for a struggling backend service defeats the purpose. Most teams set BFF timeouts well below their client-facing SLAs, allowing time for retries or fallbacks before the client gives up.

 


This may sound like the <a href="https://microservices.io/patterns/apigateway.html"API Gateway pattern</a> and indeed it is as the backend-for-frontend is a kind
of an API Gateway pattern. But there are a few differences. This is best explained using the digrams below.

| ![bff-vs-api-gateway](./imgs/bff-vs-api-gateway.png)        |
|:-----------------------------------------------------------:|
|             **Figure 1: BFF vs API Gateway patterns**       |


So the API Gateway represents a single point of enrty into the system. This is regardless of the type of the client.
In contrast, as we have already mentioned, the backend-for-frontend pattern represents an entry point suitable for a particular type of client.

So the next obvious question is when to use BFF over API Gateway? Obviously, when we do not want to support multiple client types, we can use
the latter as there is no need to use the former. However, when this is not the case we need to start thinking
how different the different client types we want to support are. Questions like the communication
protocols used e.g. REST vs GraphQL or authentication approaches used  can help towards making a decision.

---
**Remark**

BFFs solve a similar problem to GraphQL through a different mechanism. GraphQL gives clients flexibility to request what they need; BFFs give backend teams control over what each client receives. GraphQL works well when you have many clients with unpredictable data needs. BFFs work well when you have a few known clients with stable requirements and want to optimize specifically for each [4].

---

Note that BFF does not come for free and induces a maintenace overhead as there is another service to deploy, monitor and maintain.
For example if we have three different clients we may  have three BFFs, each with its own codebase and deployment pipeline [4]. 
For small teams, this overhead may outweigh the benefits. 
For larger organizations where client teams can own their BFFs, the autonomy and performance gains often justify the investment.


## Summary

The Backend-for-Frontend (BFF) pattern is an architectural approach used in microservices systems to improve client performance and maintainability by introducing a dedicated backend service per client type (e.g., web, mobile). Instead of having clients call multiple microservices directly—which increases latency and complexity—a BFF aggregates and orchestrates those calls, returning a tailored response optimized for that specific client. This reduces network overhead, simplifies client logic, and allows handling concerns like retries and partial failures centrally. Unlike a general API Gateway, which serves all clients uniformly, a BFF is specialized per client, offering greater flexibility and control at the cost of additional services to build and maintain.


## References

1. <a href="https://samnewman.io/patterns/architectural/bff/">Pattern: Backends For Frontends</a>	
2. <a href="https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends">Backends for Frontends pattern</a>
3. <a href="https://medium.com/@platform.engineers/api-gateway-and-backends-for-frontends-bff-patterns-a-technical-overview-8d2b7e8a0617">API Gateway and Backends for Frontends (BFF) Patterns: A Technical Overview</a>
4. Den Odell _Performance Engineering in Practice_, Manning Publications

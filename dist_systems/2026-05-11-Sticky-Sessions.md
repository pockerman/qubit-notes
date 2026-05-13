# qubit-notes: Distributed Systems | Resiliency | Sticky Sessions

## Overview

The note <a href="2025-04-21-load-balancing.md">load balancing</a> discussed how we can balance the work load on a system. Oftentimes we want all
requests from a specific user to be consistently routed to the same server. Session affinity or sticky sessions is load balancing technique
that we can use.

## Sticky sessions

As traffic grows through a web applications, we are forced to deploy this on multiple servers. A load balancer is then placed in front of these
web servers and in one way or another distributes the requests across these servers for efficiency.
Web  applications are usually implemented using HTTP, (see <a href="2026-04-09-Part-8-HTTP.md">HTTP</a>). HTTP however is a stateless protocol,
which means each request is independent and previous interactions are not stored. This can lead to problems if user-specific data is stored in a single server’s
A very common example where we need to remeber user interaction data is a shopping cart. 
When a user is shopping online and adds items to his cart, he may be  suddenly logged out or find the cart cart empty if a new request gets routed to a different server that doesn’t have the user's session information.

Sticky sessions solve this problem by binding a user’s session to one server, ensuring continuity of data and experience [1].
How is this done? The load balancer should somehow identify and remember which server a user is tied to.
This can be done in various ways:

- Assign an identifier to the user
- Track the client’s IP address

On the user’s first request, the load balancer might set a special session cookie that encodes which server handled the request.
Consquently, the load balancer reads this cookie on each request and routes the user to the same server that served them initially. 

---
**Remark**
 Sticky-sessions based on IP tracking but are less reliable if multiple users share an IP or if a single user’s IP changes. [1]

 ---

Hence sticky sessions allow us session data e.g. login state to stay in  the same server.
Sticky sessions exist to address real needs in session management. Below are some benefits of session affinity [1].

- Consistent session data: Given that a user's session data is kept on single server the session management is greatly simplified.
- Improved performance: Storing session data on one server we can utilize in-memory caching. 
- Easy implementation: Enabling sticky sessions is usually as simple as a configuration change on the load balancer and requires no changes to application code. 


---
**Remark**

Most modern load balancers (NGINX, HAProxy, cloud load balancers, etc.) support session affinity out of the box. 
This makes it an attractive quick solution for session management, especially in legacy applications. 
You don’t have to redesign how sessions are stored, since the load balancer takes care of keeping a user’s traffic on the same server [1].

---

However sticky sessions have some serious drawbacks that can impact scalability and reliability. 
Some are listed below. 

- Uneven load: Session affinity can lead to uneven load distribution across servers. 
- Session loss on crash: With sticky sessions, crucial session data lives only in one server’s memory by default. If that server goes down or restarts, all users tied to it will lose their sessions (e.g. they could be logged out or lose unsaved data).
- Maintenance: Because users are tied to specific servers, performing maintenance or updates on a server is harder.

Sticky sessions therefore better be avoided by default. In addition, avoid using them when:

- High availablity requirements
- Horizontal scalling
- Architectures based on microservices

---
**Remark**

In general, when working with cloud-native applications is better to store session state externally e.g. a database or not at all.
Another option is using token-based authentication such as JWT.
All in all, avoid session affinity unless you have a specific requirement for it in a stateful legacy application.

---


## Summary

Sticky sessions, also known as session affinity, are a load balancing technique used to ensure that all requests from the same user are consistently routed to the same server in a multi-server web application environment. Since HTTP is stateless, user-specific session data such as login state or shopping cart contents may be lost if requests are distributed across different servers. Sticky sessions solve this by allowing the load balancer to identify users, typically through cookies or IP tracking, and route them back to the same server that initially handled their session. This simplifies session management, improves performance through in-memory session storage, and is easy to configure using load balancers like NGINX or HAProxy. However, sticky sessions can also create uneven server load, lead to session loss if a server crashes, and complicate maintenance and horizontal scaling. As a result, modern cloud-native and microservices-based systems generally prefer storing session state externally, such as in databases or Redis, or using stateless authentication approaches like JWTs instead of relying on session affinity.


## References

1. <a href="https://www.designgurus.io/course-play/grokking-scalable-systems-for-interviews/doc/what-are-sticky-sessions-session-affinity-and-when-should-i-avoid-them">What Are Sticky Sessions (Session Affinity) and When Should I Avoid Them?</a>
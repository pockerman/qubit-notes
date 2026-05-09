# qubit-note: Distributed Systems Design Concepts Part 1

## Overview

Throughout the series we have discussed a number of concepts related to distributed systems.
In this five parts series of notes we will briefly mention 25 most common concepts one should be aware of
when setting up to design a distributed system. in this note we will discuss the following concepts


- Domain Name System (DNS); Translates human-friendly website names (like google.com) into IP addresses computers use.
- Load balancer; Distributes incoming traffic across multiple servers to keep the system fast and reliable.
- API Gateway; A single entry point that routes client requests to backend services in a microservices system.
- Content Delivery Network (CDN); A network of servers that delivers static content (like images or videos) from locations closer to the user.
- Forward Proxy vs Reverse Proxy; A forward proxy hides the client from the server; a reverse proxy hides the server from the client.

The material in this note is primarily taken from [1].


## Distributed systems design concepts part 1

**Domain Name System (DNS)**

The Domain Name System (DNS) is a core part of the internet that translates human-readable domain names, such as _www.cnn.com_, into machine-readable IP addresses used by computers to communicate. When a user enters a website address into a browser, the computer sends a DNS query to a recursive resolver, which searches through a hierarchy of DNS servers including root servers, Top-Level Domain (TLD) servers, and authoritative name servers to find the correct IP address. Once the IP address is resolved, it is returned to the browser, enabling it to connect to the appropriate server and retrieve the requested website or service.

**Load balancer**

A load balancer is a software component or networking device that distributes incoming traffic across multiple servers to improve scalability, reliability, and performance. By spreading requests efficiently, load balancers help prevent individual servers from becoming overloaded, reduce response latency, and maintain high availability during traffic spikes or server failures. They use different algorithms to decide how traffic should be routed, including Round Robin, which cycles requests evenly across servers; Least Connections, which sends traffic to the server with the fewest active connections; and IP Hash, which routes requests based on the client’s IP address to maintain session persistence by consistently directing the same client to the same server.

**API Gateway**

An API Gateway is a server or service that acts as a single entry point between external clients and backend services, especially in microservices-based architectures. It simplifies communication by routing incoming requests to the appropriate services while handling cross-cutting concerns such as authentication, authorization, rate limiting, caching, and request transformation. By centralizing these responsibilities, the API Gateway improves security, reduces backend complexity, and helps manage traffic efficiently. It can also cache common responses to reduce latency and backend load, enforce throttling policies to protect services from excessive requests, and transform requests or responses to ensure compatibility between clients and internal services. Overall, API Gateways are a key architectural component for building scalable, secure, and maintainable distributed systems.

**Content Delivery Network**

A Content Delivery Network (CDN) is a distributed network of geographically dispersed servers designed to deliver web content such as images, videos, scripts, and stylesheets more efficiently to users. Instead of serving content directly from a central origin server, a CDN routes user requests to the nearest edge server, reducing latency and improving performance. If the requested content is already cached on the edge server, it is delivered immediately; otherwise, the CDN retrieves it from the origin server or another CDN node, caches it locally, and then serves it to the user. CDNs also periodically refresh cached content to keep it synchronized with the origin server, helping improve scalability, reliability, and overall user experience for web applications and services.


**Forward Proxy vs Reverse Proxy**

A forward proxy and a reverse proxy are both intermediary servers, but they serve different purposes and sit on opposite sides of a network connection. A forward proxy sits in front of client machines and forwards client requests to the internet on their behalf, often providing features such as anonymity, access control, filtering, or caching. In contrast, a reverse proxy sits in front of one or more backend servers and forwards incoming client requests to those servers. Reverse proxies are commonly used for load balancing, security, SSL termination, and caching, while also hiding the internal server infrastructure from clients. In simple terms, a forward proxy represents the client, whereas a reverse proxy represents the server.


## Summary

This note introduces five foundational concepts in distributed systems design that are essential for building scalable and reliable applications. It explains how the Domain Name System (DNS) translates human-readable domain names into IP addresses, enabling internet communication, and how load balancers distribute traffic across multiple servers to improve performance and availability. The note also discusses API Gateways, which act as centralized entry points for routing, authentication, caching, and traffic management in microservices architectures, as well as Content Delivery Networks (CDNs), which improve user experience by serving cached content from geographically closer servers. Finally, it compares forward and reverse proxies, highlighting how forward proxies represent clients while reverse proxies protect and manage backend servers.


## References

1. <a href="https://www.designgurus.io/blog/system-design-interview-fundamentals">25 Fundamental System Design Concepts You Must Know Before Your Interview</a>
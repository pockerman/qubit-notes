# qubit-note: API Basics | Some Best Practices in API Design

## Overview

In the API basics  series of notes we will go over some fundamental concepts regarding API design and development.
APIs from the connecting tissue in a distributed system and the internet. There are various API architectural approaches one can
take see <a href="../dist_systems/2026-04-09-Part-7-API.md">qubit-note: Part 7 | Communication | APIs</a> for a review.
Each approach has its advanatges and disadvantages. Moreover, designing APIs is not easy. In this  note we will go over some best practices regarding API design.
This article is editted from [1].

**keywords** API-design, system-design, distributed-systems


##  Some best practices in API design

APIs are a significant aspect of a distributed system as they allow the participating nodes to communicate with each other.
In general, we want APIs that behave in a consisten and predictable manner, they are secure and easy to maintain and evolve.
Desigining  APIs with such attributes is not necessarilly easy however following some best practices can be very helpful towards this goal [1].

- Naming: Use clear and concise names when building an API. Names should convey the message of what something is and/or does. Establish conventions and stick to these
- Pagination: Not all APIs should support pagination, but as the volume of data grows most likely you need to implement it in your APIs. So its always better to be prepared for such a scenario.
- Sorting and filtering: Use query strings in order to allow filtering and/or sorting of the API responses. Make sure that these are properly documented.
- Cross resource references: Use clear linking between connected resources. Avoid excessively long query strings that make the API harder to understand.
- Idempotency: Not all API call are suppossed to be idempotent but make sure that those that they are expected to be, such as GET requests, remain as such. This is very important particularly when we think that users most likely will retry a request several times. 
- Rate limiting: Implement rate limiting in order to control the number of requests a user can make to an API within a certain timeframe. This is crucial for maintaining the reliability and availability. of the API.
- Versioning: One thing we have learnt from the software engineering field is that requirements change and so do your APIs. Make sure that you have proper versioning to support backward compatibility.
- Security: Nowadays, API security is not an option but something that we need to satisfy. Well-designed APIs are secure by design. Make sure that you use proper authentication/authorization using API Keys, JWTs, OAuth2, and other mechanisms.




## Summary

In a nutshell, APIs are the backbone of communication in distributed systems, but designing them effectively requires attention to clarity, consistency, and robustness. Best practices include using clear naming conventions, supporting pagination and query-based sorting/filtering, and maintaining clean cross-resource references. Ensuring idempotency for appropriate calls, implementing rate limiting, and providing proper versioning all help improve reliability and adaptability as systems evolve. Finally, strong security through mechanisms like API keys, JWTs, and OAuth2 is essential to protect data and maintain trust.

## References

1. <a href="https://bytebytego.com">ByteByteGo</a>

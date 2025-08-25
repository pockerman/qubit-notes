# qubit-note: Architecture Patterns-Service Oriented Architecture Pattern

## Overview

This qubit note  continues the series in software architecture patterns and discusses the <a href="#https://en.wikipedia.org/wiki/Service-oriented_architecture">service oriented architecture pattern</a> or SOA for short. This is a design pattern that organizes applications as a collection of loosely coupled, reusable services that communicate via standardized protocols and well-defined contracts. 
SOA supports both orchestration ,i.e centralized coordination, and choreography, i.e.decentralized coordination, see also <a href="2025-04-20-managing-distributed-workflows.md">qubit-note: Managing Distributed Workflows</a>.


**keywords** service-oriented-architecture, SOA, software-architecture, system-design, distributed-systems


## Service oriented architecture pattern

SOA is a software development design pattern that structures applications as a collection of loosely coupled, reusable services.
Each service is an independent unit responsible for performing a specific function, such as checking customer data or processing a payment, 
and can be used by other programs or people, known as service consumers. These services interact across diverse platforms and programming languages 
using standardized communication protocols, promoting reusability, efficiency, and easier integration.

At its core, SOA is based on the principles of loose coupling, where services operate independently with minimal dependencies, allowing them to evolve and change over time without affecting other parts of the system. Services communicate through well-defined APIs called service contracts, which specify the operations provided, along with the input and output data formats.
This abstraction from implementation details means consumers only need to know the contract, not how the service is implemented.

This pattern enables greater flexibility and agility in development by allowing services to be developed, tested, and deployed independently, facilitating faster iteration and more frequent releases.
It supports horizontal scaling by adding more instances of individual services as demand grows, enhancing scalability and resilience.
The architecture also promotes interoperability, as services can be composed and reused across different applications and organizations using standardized protocols and data formats.

SOA systems typically involve service providers (maintainers of services) and service consumers (applications or users that use services).
Services can be discovered through a registry, and their use is governed by public contracts. Two key interaction patterns are service orchestration, 
where a central component coordinates services to fulfill a request, and service choreography, which involves coordinated interactions without a single point of control.
Service-oriented architectures (SOA) can be implemented in many ways. 

In general,  SOA relies heavily on message buses and communication via SOAP. In this token, the <a href="https://en.wikipedia.org/wiki/Enterprise_service_bus">enterprise service bus</a> or ESB, is a common architectural pattern used in SOA to manage integrations, perform message transformations, handle routing, and convert communication protocols, acting as a centralized integration layer.

SOA differs from monolithic architectures by breaking down large systems into smaller, independent components, reducing the risk of system-wide failures and enabling more adaptable and maintainable systems. It is distinct from microservices architecture, where each service typically has its own dedicated database, whereas SOA often uses a centralized database shared by all services.
While SOA is a foundational pattern, it can serve as a basis for transitioning towards microservices or be combined with other architectural styles like headless architecture, which focuses on the separation of the frontend from the backend and is orthogonal to the choice of backend architecture.

The implementation of SOA requires careful planning, including identifying services based on business processes, defining clear service contracts, and using tools for continuous integration and deployment. The design consistency of SOA is guided by principles such as normalized service contracts, statelessness, reusability, and discoverability through metadata.

Typical components of a SOA design include: services, services registry and a messaging system [3]. This architecture pattern promptes, [3], reusability and scalability. On the other hand,
it increases the complexity of the architecture whilst it does not favour reliability and availability whilst it can inhibit the system performance.

## Summary

Service-Oriented architecture is a software design pattern that organizes applications as a collection of loosely coupled, reusable services that communicate via standardized protocols and well-defined contracts. Each service performs a specific function and can be independently developed, deployed, and scaled, promoting flexibility, interoperability, and efficient integration across diverse platforms. SOA supports both orchestration ,i.e centralized coordination, and choreography, i.e.decentralized coordination. It often uses enterprise service buses (ESB) for message routing and transformations. While it enhances scalability and reusability compared to monolithic systems, SOA introduces increased architectural complexity, can impact performance, and typically relies on shared databases rather than the decentralized model of microservices.

## References

1. <a href="#https://en.wikipedia.org/wiki/Service-oriented_architecture">Service oriented architecture pattern</a>
2. <a href="https://en.wikipedia.org/wiki/Enterprise_service_bus">Enterprise service bus</a>
3. Michael Keeling, _Design It! From programmer to software architecture_, The Pragmatic Programmers.
# qubit-note: Architecture Patterns-Ports and Adapters Pattern


## Overview


Often when designing systems we need to support a number of services e.g. a system where its role is to collect data
from various sensors.  On top of that the services could change. When facing such a scenarion, the ports and adapters pattern, also known as <a href="https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)">Hexagonal Architecture</a> is a suitable candidate.

In this qubit note, I will briefly discuss the port and adapters pattern. Note that the term services includes frameworks, UIs and databases.

**keywords** software-architecture, architecture-patterns, system-design


## Ports and adapters pattern

The core idea of this pattern is to isloate core business logic so that we can use it in different contexts [2].
The components that provide either data or events are attached at runtime so that the core logic has access to them.
Below are the main components of this pattern [2].


**Elements**

This pattern has three core elemnts

- Core layer (domain)
- Port
- Adapter

The core layer is unaware from where the various data it is manimulating originates from.
The port describes the interface between the core layer and an adapter.  There are two types of ports:
- Inbound Ports: Interfaces the outside world calls to tell the app to do something.
- Outbound Ports: Interfaces the application calls to talk to the outside world.

An adapter is simply code that interacts with the 
external services to fetch data and/or events i.e it provides implementations of those interfaces for specific technologies (e.g., Postgres, REST, gRPC, file system).


**Relations**

Furthermore, the pattern has three main relations

- Exposes; which ports are available from a given layer
- Implements; the ports which constrain an adapter.
- Injects; specifies the adapters that are available to a given layer.


**Rules for use**

The core logic cannot import, reference, or depend on framework classes, database drivers, HTTP libraries, or UI code.
All communication between the core and the outside world must go through ports. 
Adapters depend on the ports and the core will never depend on the adapters.
External systems never dictate core behavior — they just provide data or receive results.
The domain models and business logic should never contain:

- ORM annotations
- HTTP response objects
- JSON serialization code
- Framework-specific types

If you see for example ```import requests``` or ```import sqlalchemy``` in your domain model — you’ve broken the rule.


**Strengths**

Just like the <a href="2025-08-12-architecture-patterns-layers-pattern.md">layers pattern</a> this pattern also favours maintainability, and portability, as well as reusability and testability.


**Weaknesses**

This is a  powerful pattern for building clean, maintainable, and testable systems, but like any architecture, it has trade-offs and potential weaknesses.
Here are the main weaknesses and pitfalls you should be aware of:

- More complexity and boilerplate
- Can be harder to navigate in the code
- Potential for interface explosion
- Slower feedback loops in early stages

## Summary

The Ports and Adapters pattern (Hexagonal Architecture) is a software design approach that isolates core business logic from external systems like databases, frameworks, and UIs by introducing ports (interfaces) and adapters (implementations). The core layer defines the application's rules and communicates with the outside world only through ports, while adapters handle the details of interacting with specific technologies. This separation improves maintainability, portability, testability, and reusability, but comes with trade-offs such as added complexity, more boilerplate code, potential interface overload, and slower development in early stages. By enforcing strict boundaries—ensuring the core never depends on external libraries or frameworks—the pattern enables flexible, long-lived systems that can adapt to changing technologies.

## References

1. <a href="https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)">Hexagonal Architecture</a> 
2. Michael Keeling, _Design It! From programmer to software architecture_, The Pragmatic Programmers.
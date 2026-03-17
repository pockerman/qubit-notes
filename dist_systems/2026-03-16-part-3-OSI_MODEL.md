# qubit-note: Distributed Systems Series | Part 3 | Inter-Process Communication

## Overview

Distibuted systems comprise of processes that communicate over the network. Interprocess communication (PIC) is at the heart of a distributed system.
We need therefore to have an understanding about the communication stack when designing distributed systems. In this qubit note
we will give a hig level overview of what is happening behind the scenes when a process communicates with anothe process.


## Inter process communication

Inter process communication (IPC) is at the heart of a distributed system. When a process sends data to another process some sort of a 
protocol has to be followed in order for the two processes to communicate effectively.
In general, communication protocols are arranged in a stack where each layer in the stack uses the the abstractions provided by the layer below.
Lower layers are closer to the hardware.

One such interconnection model is the OSI or Open Systems Interconnection model [1].
In this model, the components of a communication stack are distinguished in seven abstraction layers: 

- Physical
- Data Link
- Network
- Transport
- Session
- Presentation
- Application

According to [1]:

_The model describes communications from the physical implementation of transmitting bits across a transmission medium to the highest-level representation of data of a distributed application. Each layer has well-defined functions and semantics and serves a class of functionality to the layer above it and is served by the layer below it. Established, well-known communication protocols are decomposed in software development into the model's hierarchy of function calls._

The following is a schematic that gives an overview of the journey and HTTP request has to follow in order to reach another process. The request begins at the application layer.
This is the layer that primarily software engineers work. This layer defines protocols such as HTTP or DNS. The transport layer uses ports in order to communicate between two processes. Various protocols can be used at this level.
The most important one is the <a href="https://en.wikipedia.org/wiki/Transmission_Control_Protocol">Transmission Control Protocol (TCP)</a> 
The internet layer is responsible to route packets from one machine to another. The <a href="https://en.wikipedia.org/wiki/Internet_Protocol">Internet Protocol (IP)</a> is the core protocol
at this layer [2]. Finally, the link layer operates on local network links e.g. Ethernet or Wi-Fi. It is the layer where the hardwware is implemented. Switches at this layer forward the 
packets based on they <a href="https://en.wikipedia.org/wiki/MAC_address">MAC address</a> they have been assigned [2].

Although significant engineering effort has been placed to make the aforementioned abstractions robust and secure, abstractions do leak. Troubleshooting network issues requires
that we understand a few of the details of the layers below the layer we are working on.


## Summary

Inter-process communication (IPC) is a core component of distributed systems, enabling processes on different machines to exchange data over a network using structured communication protocols organized in layers. The OSI model describes this layered approach with seven levels, ranging from the physical transmission of bits to the application-level representation of data. In practice, when a request such as HTTP is sent, it travels through several layers: the application layer (protocols like HTTP and DNS), the transport layer (e.g., TCP using ports for process-to-process communication), the network layer (IP for routing packets between machines), and the link layer (hardware-level communication using technologies like Ethernet or Wi-Fi and MAC addresses). While these abstractions simplify development, they can leak in real-world scenarios, meaning engineers often need to understand lower networking layers when diagnosing issues in distributed systems.


## References

1. <a href="https://en.wikipedia.org/wiki/OSI_model">OSI model</a>
2. Robert Vitillo, _Understanding Distributed Systems What every developer should know about large distributed applications_
# Note: Domain Name System

## Overview

In this note, I cover some of the details of the Domain Name System or DNS for short.

**keywords** domain-name-system, system-design

## Domain name system

We know that computers are uniquely identified using <a href="https://en.wikipedia.org/wiki/IP_address">IP addresses</a>. 
However, only rarely do we, as humans,  use these addresses to reach a website hosted on a given machine. We, most of the time, use the 
domain name of the website in order to access it as this is definitely easier in terms of our memory capacity. 
The translation of the domain name into a legitimate IP address is done by the <a href="https://en.wikipedia.org/wiki/Domain_Name_System">domain name system</a>.


So the DNS is somehow the naming service of today's internet. It's job is do map the user-friendly domain names such as ```google.com```
to machine friendly IP addresses. the browser then that we use to access the internet queries the DNS for the IP address that corresponds to
the user provided domain name. 

Given the nature of the service that DNS provides it has been implemented as a distributed system consisting of a number
of different types of servers:

- DNS resolver
- Root-level name servers
- Top-level domain (TLD) name servers
- Authoritative name servers

I won't cover the details of these in this post, however I want to answer the following simple question.

_How does the browser know the address of the DNS machine?_

The answer to this question is that typically, the OS that we happen to use has a list of the IP addresses of DNS resolvers e.g. under linux this
will be in ```/etc/resolv.conf```.  The system then can query these resolvers for any DNS queries.
These DNS resolvers can  resolve DNS related queries using special software e.g. the <a href="https://en.wikipedia.org/wiki/BIND">Berkeley Internet Name Domain</a>, or BIND.
The address of these resolvers rarely changes.


Given the role of the DNS it is natural that we prioritise availability and scalability versus consistency.
Recall that strong consistency means that all users see the same data at the same time, no matter where they are in the world. 
In the case of DNS this translates that once a  DNS record changes, everyone should immediately get the updated IP address.
However, given the distributed nature of DNS satisfying such a requirement would cause a number of problems:

- Massive network traffic
- Slower response times
- Bottlenecks at the authoritative servers

As a distributed system, DNS uses caching in order to enhance scalability.
In other words, When a resolver queries a DNS record, it stores the result for a period defined by the <a href="https://en.wikipedia.org/wiki/Time_to_live">Time to Live (TTL) value</a>.
This tactic is in general ok as most of the time, DNS records don’t change frequently. In additiion if we do need faster propagation,
we can lower the TTL before making changes. The downside of course of such an approach is that if a domain’s IP address changes, 
it might take minutes or hours for the change to propagate everywhere as some resolvers still use the cached version until the TTL expires.



## References

1. <a href="https://en.wikipedia.org/wiki/IP_address">IP addresses</a>
2. <a href="https://en.wikipedia.org/wiki/Domain_Name_System">Domain name system</a>
3. <a href="https://en.wikipedia.org/wiki/BIND">Berkeley Internet Name Domain</a>
4. <a href="https://en.wikipedia.org/wiki/Time_to_live">Time to Live (TTL) value</a>
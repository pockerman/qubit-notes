# Note: Managing Distributed Workflows

## Overview

In this note, I cover some of the options available when we need to manage distributed workflows from
an architecture perspective. The ideas has been taken from the excellent book of Neal Ford et. al. 
_Software Architecture: The Hard Parts. Modern Trade-Off Analyses for Distributed Architectures_ by O'Reilly.
I highly recommend reading this book.


**keywords** software-architecture, system-design, distributed-systems, workflow-management

## Managing Distributed Workflows

Often times in software systems we need to somehow coordinate a number services in order to have the desired domain specific outcome.
Two appraoches we can utilise in our designs are orchestration and choreography [1].
Let's discuss what these two aproaches entail. 

**Orchestration**

As you can probably imagine, this approach implies the existence of an orchestrator service that all participating services
interact with. This is shown in the following image.

The orchestrotor in general should not implement any other domain behaviour aside of the worflow it orchestrates [1].
This pattern is useful when the workflow we work on has more than one happy paths and/or error paths. Some advantages of
the orchestrator pattern include [1]:

- Centrally managed workflow easier to manage state
- Easy(-ier) to recover
- Easy(-ier) error handling

Disadvanges include:

- No fault tolerance
- Limited scalability
- Service coupling


**Choreography**

Choreography does not have any central coordination component. Instead  the participating services can interact with each
other in predefined ways and under predefined circumstances. This is shown schematically in the image below


This approach avoids the problem of SPF (signle point of failure)
that the orchestrator pattern assumes. However, as the number of error cases increases, the complexity of the pattern also increases.
Some of the advantages that the choreography pattern include [1]:

- Service decoupling
- Scalability
- Fault tolerance

Similarly, some of the disadvantages are:

- Difficult to do error handling
- Difficult to do state management
- Difficult to recover 


The need to coordiante services in distributed software systems is one of the reasons/forces that create and/or increase the
complexity of dealing with such systems. 
As with anything with software engineering both the orchestartor and choreographer come with trade-offs and its the architect's 
job to choose which one to implement. 

One of the main issues we need to account for when deciding which solution to utilise is state management.
The orchestrator pattern easily facilitates this as there exists only one single source of truth. In contrast,
with choreography this is more involved. Some common solutions are [1]:

- <a href="https://en.wikipedia.org/wiki/Front_controller">Front controller pattern</a>
- Utilize stamp coupling 
- Stateless choreography

I will touch on these is future notes.


## References

1. Neal Ford et. al.  _Software Architecture: The Hard Parts. Modern Trade-Off Analyses for Distributed Architectures_ by O'Reilly.
2. <a href="https://en.wikipedia.org/wiki/Front_controller">Front controller pattern</a>



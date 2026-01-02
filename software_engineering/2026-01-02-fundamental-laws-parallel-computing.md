# qubit-note Parallel Computing Series | Fundamental Laws of Parallel Computing

## Overview

Parallel computing whether it is process-based or thread-based or stream processing is at heart of improving the scalability
of modern systems as increasing the clock rate of the CPU has diminished significantly due to physical constraints.

Parallel computing however it's not easy as it requires a new set of rules. Thus being able to understand the performance of an application
is essential. In this qubit-note, I will discuss some commonly used laws in the field of parallel computing.


## Fundamental Laws of Parallel Computing

We will look into the following laws in this qubit note

- <a href="https://en.wikipedia.org/wiki/Speedup">Speedup</a>
- <a href="https://en.wikipedia.org/wiki/Amdahl%27s_law">Amdahl's law</a>
- Gustafson-Barsis's law
- Little's law
- <a href="https://en.wikipedia.org/wiki/Efficiency">Efficiency</a>

Amdahl's and Gustafson-Barsis's laws are both concerned with the speedup of an application i.e. how the performance of our application
is improved (or gets worse) as we add more processing units into it. The speedup is defined as the following fraction

$$S_p  = \frac{T_s}{T_p}$$


where $T_s$ is the time taken by the same parallel machine executing (on one processor) the fastest known seial algorithm, and $T_p$ is the time required to execute the parallel algorithm using $p$ processors. Theoreticlly, the speedup is constrained between [2]:

$$1 \leq S_p \leq p$$


Theoretically, therefore, the best we can hope is for linear speedup; i.e. $S_p = p$. Speedup is a global measure
of the quatlity of a parallel algorithm. Note that this definition assumes that the problem size is fixed and
only the number of processors increases. However, this may not necessarily be true; as the number of processors increases
we want to solve larger problems.

Now that we have a theoretical understanding what speedup is let's look into two specific laws for speedup in parallele computing.

#### Amdahl's law

The theoretical ideal speedup is linear. However, this is rarely true in practice; communication and/or
synchronization costs come into play. In addition, not all the code in our program can be parallelized.
Amdahl's law takes into consideration the fraction of operations in a computation that must be performed sequentially and therefore
proposes a another formula for speedup.

$$S_p = \frac{1}{f + \frac{1-f}{p}}$$


where $f$ is the fraction of operations in a computation that must be performed sequentially. Also $f$ is bounded:

$$0 \leq f \leq 1$$


Thus, Amdahl's law states that the maximum speedup achievable on $p$ processors is bounded from above. In particular,  

$$S_p \leq \frac{1}{f + \frac{1-f}{p}}$$

Consequently, a small fraction of sequential operations can severely limit the achivable speedup. For example, on a machine with $p$ processors if we run an algorithm where $f=10\%$ then we cannot achieve a speedup greater than 10 regardless of how many processors the parallel algoritjm is using

$$S_p = \frac{1}{0.1 + \frac{0.9}{p}} \leq \frac{1}{0.1} = 10$$

Note that the formula above, gives

$$S_p \leq p$$

if our program is perfectly parallelized i.e. $f=0$.


## Summary


## References

1. Robert Robey, _Parallel and High Performance Computing_, Manning Publications
2. Michael Cosnard, Denis Trystram, _Parallel Algorithms And Architectures_, International Thomson Computer Press
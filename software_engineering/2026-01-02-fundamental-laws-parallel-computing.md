# qubit-note Parallel Computing Series | Fundamental Laws of Parallel Computing

## Overview

Parallel computing whether it is process-based or thread-based or stream processing is at heart of improving the scalability
of modern systems as increasing the clock rate of the CPU has diminished significantly due to physical constraints.

Parallel computing however it's not easy as it requires a new set of rules. Thus being able to understand the performance of an application
is essential. In this qubit-note, I will discuss some commonly used laws in the field of parallel computing. Specifically, we will look into
speedup, latency and efficiency of parallel computing.


## Fundamental Laws of Parallel Computing

We will look into the following laws in this qubit note

- <a href="https://en.wikipedia.org/wiki/Speedup">Speedup</a>
- <a href="https://en.wikipedia.org/wiki/Amdahl%27s_law">Amdahl's law</a>
- <a href="https://en.wikipedia.org/wiki/Gustafson's_law">Gustafson-Barsis's law</a>
- <a href="https://en.wikipedia.org/wiki/Little%27s_law">Little's law</a>
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


#### Gustafson-Barsis's law

Amdahl's law assumes that the problem size remains the same. However, in practice when we have more processing elements in our disposal we want to solve larger problems.
With this observation Gustafson and Barsis proposed in 1988 the following speedup estimation that now bears their names [1]:

$$S_p = p - f(p -1)$$

According to this law, larger problems can be solved in the same time by using more processing elements.

In addition, we have the following denitions associated  with Amdahl's and  Gustafson-Barsis's laws respectively [1:

**Strong scaling** represents the time solution with respect to $p$ for a fixed total problem size.

**Weak scaling** represents the time to solution with respect to $p$ for a fixed sized problem per processor i.e as the number of processors increase the job size a processor has to execute does not decrease.

#### Little's law

#### Efficiency

The efficiency $E_p$ shows the average usage of the processors and it is defined as [3]

$$E_p = \frac{S_p}{p}$$

Thus, $E_p$ is between $[1/p, 1]$

**Example**

Let's assume that a serial algorithm solves a problem in 10 seconds and a parallel algorithm by using 5 processors solves the problem in 2 seconds. Then:

$$S_p = \frac{10}{2} = 5$$
$$E_p = \frac{5}{5} = 1$$

In this example, we have that $S_p = p$ i.e. the maximum possible theoritically and this ensues $E_p = 1$.
Similarly, if we assume $T_s = 8s$ and $T_p=2s$ then the metrics become

$$S_p = \frac{8}{2} = 4$$
$$E_p = \frac{4}{5} = 0.8$$

## Summary


## References

1. Robert Robey, Yuliana Zamora, _Parallel and High Performance Computing_, Manning Publications
2. Michael Cosnard, Denis Trystram, _Parallel Algorithms And Architectures_, International Thomson Computer Press
3. Michael J. Quinn, _Parallel Computing Theory And Practice 2nd Edition_, McGraw-Hill 
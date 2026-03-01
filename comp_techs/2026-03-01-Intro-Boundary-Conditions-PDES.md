# qubit-note: The Maths Project Series | Intro to Boundary Conditions for PDEs

## Overview

<a href="2026-01-01-intro-to-pdes.md">qubit-note: Intro to PDEs</a> introduced the idea of PDE and gave some examples.
In this note we will discuss the idea of boundary conditions. These are essential components if a PDE is to be solved.


**keywords** partial-differential-equations, PDE, boundary-conditions, initial-conditions, mathematical-physics


## Intro to boundary conditions for PDEs

In general, all physical problems have boundaries of some kind [1]. 
Furthermore, boundary and initial conditions are problem specific and applications should discover what is the best boundary and initial conditions.
We need however to be able to mathematically describe what happens at the boundary of the physical domain that the PDE is to be solved in order to
adequately describe the problem [1]. We have the following general types of boundary conditions for a second order PDE:

### Dirichlet boundary condition

This boundary condition, prescribes a certain value of the unknown function at the boundary of the physical domain.
Consider for example the 1D heat flow along a rod of length $L$:

$$
u_t = a^2u_xx, 0<x<L, 0<t<T 
$$

at the edges of the rod we prescibe a certain temperature:

$$
u(0, t) = U_1, u(L,t)=U_2
$$


### Neumann boundary condition

This boundary condition prescribes the normal derivative of the function on the boundary. For the 1D heat flow this could be

$$
\frac{\partial u}{\partial x}|_{x=L} = 0
$$

The physical meaning of the condition is that we control the flow flow of the temperature rather than its value

### Robin boundary condition

This is a linear combination of the Neumann and Dirichlet conditions

$$
au + \frac{\partial u}{\partial x} = h
$$

This implies that both the value and flux of the temperature are linked


Note that there are other types of boundary conditions such as periodic boundary conditions and Cauchy boundary conditions. 
We will introduce these conditions further in these notes.

## Summary

This note builds on an introduction to partial differential equations by explaining the role of boundary conditions, which are essential for solving physical PDE problems. Since real-world systems have boundaries, we must mathematically describe what happens at the edges of the domain in addition to specifying initial conditions. For second-order PDEs, the main types are Dirichlet conditions, which fix the value of the unknown function at the boundary (e.g., prescribing temperature at the ends of a rod in the heat equation); Neumann conditions, which fix the normal derivative and therefore control the flux rather than the value (e.g., zero heat flow at an insulated boundary); and Robin conditions, which combine the function and its derivative in a linear relation, linking value and flux. 

## References

1. Stanley J. Farlow, _Partial Differential Equations for Scientists and Engineers_, Dover Publications
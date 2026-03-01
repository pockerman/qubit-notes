# qubit-note: The Maths Project Series | Intro to PDEs

## Overview

In this series of notes I will be discussing partial differential equations (PDEs) and techniques one can employ
to solve a partial differential equation. 


**keywords** Partial-differential-equations, PDE, Mathematical-physics

## Intro to PDEs

Let's start with a definition. A PDE is an equation that contains partial derivatives. 
In contrast, an ordinary differential equation (ODE) contains only one variable i.e. the unknown function depends only on one variable [1].
Hence, PDEs are equation whereby the unknown function depends on several variables e.g. spatial variables and time.
Below are some examples of PDEs taken from [1]:

- Heat equation in 1D

$$u_t = u_x$$

- Heat equation in 2D

$$u_t = u_{xx} + u_{yy}$$

- Telegraph equation

$$u_{tt} = u_{xx} + a u_t + bu$$

In thse series of notes we will mostly be concerned with methods to solve a given PDE. This depends on the structure
of the equation so it is helpful to be able to classify a PDE. This can be done in many different ways such as [1]:

- The order of the PDE; i.e. the order of the highest partial derivative
- Number of variables; i.e. the number of independent variables
- Linearity
- Homogeneity
- Kinds of coefficients

Let me expand a bit on the linearity criterion. An equation can be linear or non-linear. For example, the following equation

$$x+1=0$$

is a linear equation whereas the next one is non-linear

$$x^2 + 4 = 0$$

In a linear PDE, the dependent variable and all its derivatives appear in a linear fashion [1]. A second order linear equation in two variables
has the following general form [1]:

$$Au_{xx} + Bu_{yx} + Cu_{yy} + Du_x + Eu_y + Fu = G$$

where the coefficients can be constants or functions of $x$ and $y$. All linear PDEs of this form are either of the following three types:

- Parabolic: $B^2-4AC = 0$
- Hyperbolic: $B^2-4AC > 0$
- Elliptic: $B^2-4AC < 0$

We will discuss these types further in these notes. Furthermore, below are some useful techniques we can use to solve a PDE [1].

- Separation of variables
- Integral transforms
- Change of coordinates
- Transformation of the dependent variable
- Numerical methods
- Pertubation methods
- Impulse-response technique
- Integral equations
- Calculues of variations
- Eigenfunction expansion

We will also discuss these techniques in these notes. 


## Summary

A PDE is an  equation  that involves partial derivatives where the unknown function depends on multiple variables (such as space and time) this is in contrast to ODEs that depend on a single variable. Solving a PDE often depends on the structure of the equestion. The structure of a PDE allows us to classify it. Key classification criteria include the order of the equation, number of variables, linearity, homogeneity, and the nature of coefficients. Special attention is given to linearity, explaining that linear PDEs involve the dependent variable and its derivatives in a linear manner.

For second-order linear PDEs in two variables, a general form is given, and such equations are classified as parabolic, hyperbolic, or elliptic based on the discriminant 

$$B^2 -4AC$$

There are various techniques one can employ in order to solve a PDE. These tools include separation of variables, integral transforms, 
coordinate changes, numerical methods, and eigenfunction expansions, which will be explored further in the series.

## References

1. Stanley J. Farlow, _Partial Differential Equations for Scientists and Engineers_, Dover Publications

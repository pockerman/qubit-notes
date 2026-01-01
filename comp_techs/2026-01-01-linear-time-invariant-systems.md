# qubit-note: The Maths Project Series | Linear Time-Invariant Systems

## Overview

Linear systems form a cornerstone of mathematical modelling of dynamical systems. Indeed a system or some aspects of it can be modelled using a linear model. Furthermore, non-linear systems can be linearized around a certain mode of operation. In this section, we give a brief overview of linear time-invariant systems. The major advantage of linear systems is that in terms of analysis a far simpler. Moreover, understanding the dynamics and thus stability of the system is easier.

**keywords** Dynamical-systems, Linear-systems, Ode, Time-invariant


## Linear time-invariant systems

Let's consider the following system 

$$\frac{d \mathbf{x}}{dt} = \mathbf{f}(\mathbf{x}, \mathbf{u}), ~~ \mathbf{y} = \mathbf{g}(\mathbf{x}, \mathbf{u})$$

As before, $\mathbf{x}$ represents the state of the modelled system whilst  $\mathbf{u}$ represents some control input to the system. Note that the right-hand side terms do not depend explicitly on the time variable $t$. 

If $\mathbf{f}$ or $\mathbf{g}$ or both are non-linear, then the system is non-linear. In this case, we can linearize the system i.e. its dynamics, using a Taylor series expansion near a fixed point $(\bar{\mathbf{x}}, \bar{\mathbf{u}})$. Recall that at a fixed point is  a point where:

$$\mathbf{f}(\bar{\mathbf{x}}, \bar{\mathbf{u}}) = \mathbf{0}$$

The linear, or linearized, dynamics can be written in the following matrix form (assuming no errors)

$$\frac{d\mathbf{x}}{dt} = \mathbf{A}\mathbf{x} + \mathbf{B}\mathbf{u}, ~~ \mathbf{y} = \mathbf{C}\mathbf{x} + \mathbf{D}\mathbf{u}$$

When $\mathbf{u} = \mathbf{0}$ and when there are no measurement errors i.e. $\mathbf{y} = \mathbf{x}$. The system reduces to:

$$\frac{d\mathbf{x}}{dt} = \mathbf{A}\mathbf{x}$$

The solution to this ODE is [1]

$$\mathbf{x}(t) = e^{\mathbf{A}t}\mathbf{x}(0)$$

Thus $\mathbf{x}(t)$ depends or is determined entirely by the matrix $\mathbf{A}$. The stability of the unforced system therefore, can be understood via the eigenvalues and eigenvectors of  $\mathbf{A}$. In particular we have the following cases:

- All the eigenvalues $\lambda$ satisfy $Re(\lambda) < 0$. Then the system is stable and all solutions decay to $\mathbf{u} = \mathbf{0}$ as $t \rightarrow \infty$
- There exists at least one eigenvalue $\lambda$ with $Re(\lambda) > 0$ then the system is unsatble and will diverge from the fixed point along the corresponding unstable eigenvector direction.


Now let's assume that $\mathbf{u} \neq \mathbf{0}$ and that $\mathbf{x}(0) = \mathbf{0}$. In this case the solution up to time $t$ is given by [1]:

$$\mathbf{x}(t) = \int_{0}^t e^{\mathbf{A}(t - \tau)} \mathbf{B}\mathbf{u}(\tau)d \tau $$

This integral is nothing more than a <a href="https://en.wikipedia.org/wiki/Convolution">convolution</a>. Thus, we can write:

$$\mathbf{x}(t) =  e^{\mathbf{A}t} \mathbf{B} * \mathbf{u}(t)$$

## Summary

This qubit-note introduces linear time-invariant (LTI) systems as a fundamental tool for modeling and analyzing dynamical systems. Linear models are widely used because they simplify analysis, and even nonlinear systems can often be approximated by linearizing their dynamics around a fixed operating point using a Taylor expansion.

The system dynamics can be expressed in a general state–space form, where the system is nonlinear if the governing functions are nonlinear. By linearizing around a fixed point—where the system’s dynamics vanish—the equations reduce to a linear state–space model characterized by constant matrices  $\mathbf{A,B,C,D}$.

When the input vector $\mathbf{u} = \mathbf{0}$$ the system’s behavior is entirely determined by the matrix $\mathbf{A}$ with solutions expressed using the matrix exponential. Stability is analyzed through the eigenvalues of $\mathbf{A}$: if all eigenvalues have negative real parts, the system is stable; if any have positive real parts, the system is unstable.

When external inputs are present, the system’s response is given by an integral involving the matrix exponential and the input signal. This integral represents a convolution, highlighting the key property of LTI systems: their output can be understood as the convolution of the input with the system’s impulse response.


## References

1. Steven L. Brunton, J. Nathan Kutz, _Data-Driven Science and Engineering. Machine Learning, Dynamical System and Control_, Cambridge University Press.
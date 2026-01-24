# qubit-note: Temporal Difference Learning

## Overview

In this qubit-note we will review <a href="https://en.wikipedia.org/wiki/Temporal_difference_learning">Temporal Difference Learning</a>. This is one of the pillars of reinforcement learning
algorithms. 


**keywords** Temporal-difference-learning, Reinforcement-learning

## Temporal differnce learning

Temporal difference learning (TDL) is an online learning algorithm i.e. updates happen continuously, as new information arrives.
As we will discuss below TDL does not require the transition probabilities therefore it belongs to the  class of model-free reinforcement learning methods.
These methods  learn by bootstrapping from the current estimate of the value function [1]. 
These methods sample from the environment, like Monte Carlo methods, and perform updates based on current estimates, like dynamic programming methods [1].
The essence of TDL is given by the equation below

$$
V(s) = V(s) + \alpha \delta
$$

where $V(s)$ is the state value function for state $s$, $\alpha$ is a learning parameter and
$\delta$ is the so called TD error defined as:

$$
\delta = r_{t} + \gamma V_s_{t+1} - V(s)
$$

where $r_{t}$ is the instantaneous reward that the agent received and $\gamma$ is a discount factor indicating how much the agent is interested in the future.
The TD error shows how good the chosen action was however it does not tell us which action will lead to a better next state.
In layman's terms, we can think of the TD error as the difference between what we expected from a decision and what we actually got.

----
**Remark**

When using TDL the action is chosen i.e. sampled out of a policy $\pi$. This policy is formulated based on the data we collect.
There is not need therefore for explicit transition probabilities.

## Summary

## References

1. <a href="https://en.wikipedia.org/wiki/Temporal_difference_learning">Temporal Difference Learning</a>
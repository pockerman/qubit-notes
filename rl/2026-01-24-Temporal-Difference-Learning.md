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
So:

- $\delta > 0$ output was better than expected
- $\delta < 0$ output was worse than expected
- $\delta \approx 0$ prediction was accurate

----
**Remark**

When using TDL the action is chosen i.e. sampled out of a policy $\pi$. This policy is formulated based on the data we collect.
There is not need therefore for explicit transition probabilities.

----

The TD error is the learning signal, similar to the value of the loss function when training machine learning models with gradient decent.
TDL given sufficient experience, will find the optimal value function for any given policy [2]. Typically, the 
convergence behaviour will exhibit small fluctuations around the optimal value due to sampling that the algorithm perofrms.


## Summary

Temporal Difference Learning (TDL) is a core reinforcement learning method that learns state value functions online, updating estimates continuously as new experience arrives. It is a model-free approach, meaning it does not require knowledge of environment transition probabilities.

TDL combines ideas from Monte Carlo methods (learning from sampled experience) and dynamic programming (bootstrapping from current value estimates). Learning is driven by the temporal difference (TD) error, which measures the discrepancy between the predicted value of a state and the observed reward plus the discounted value of the next state. This TD error acts as the learning signal that updates the value function.

Actions are selected according to a policy that is learned from data, rather than from an explicit model of the environment. While the TD error indicates how good an outcome was compared to expectations, it does not directly specify which action is optimal—only how to adjust value estimates.

Given sufficient experience, temporal difference learning converges to the optimal value function for a fixed policy, though in practice the estimates may fluctuate slightly due to sampling noise.
In following notes we will look into some common TDL algoritms such as 

- TD(0)
- SARSA
- Q-learning

## References

1. <a href="https://en.wikipedia.org/wiki/Temporal_difference_learning">Temporal Difference Learning</a>
2. Hadi Aghazadeh, _Reinforcement Learning for Business_, Manning Publications
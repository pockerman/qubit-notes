# qubit-note: Solving a Markov Decision Process

## Overview

<a href="2026-02-22-Markov-Decision-Process.md">qubit-note: Markov Decision Process</a> introduced the idea of a MArkov decision process or MDP.
In this qubit-note we will give a very high level overview of some popular approaches that can be
used to solve an MDP. Specifically, we will briefly introduce the following approaches

- <a href="https://en.wikipedia.org/wiki/Multi-armed_bandit">Multi-armed bandits (MAB)</a>
- <a href="2026-01-24-Temporal-Difference-Learning.md">qubit-note: Temporal Difference Learning</a>
- <a href="https://en.wikipedia.org/wiki/Monte_Carlo_method">Monte Carlo learning</a>
- <a href="https://www.geeksforgeeks.org/competitive-programming/dynamic-programming/">Dynamic programming</a>
- Tree search


**keywords** markov-decision-process, markov-property, reinforcement-learning

## Solving a Markov decision process

In this qubit note we will review five different paradigms which can be used to solve an MDP.
Namely, we will discuss:

- Multi-armed bandits (MAB)
- Temporal difference learning
- Monte Carlo learning
- Dynamic programming
- Tree search

Let's start with MAB

### Multi-armed bandits

Multi-armed bandits are perhaps the simplest reinforcement learning problem we can encounter. 
Despite this, MAB formulations have wide spread applicability to areas such as  e-commerce ad campaign.
MAB formulations compared to full reinfoercement learning algorithms are rather lightweight since the framework does not account
for state transitions, or any sequential decision making where current state dependents on previous one. Indeed multi-armed bandits involve a 
the following cycle: choose an action, observe a reward, update your beliefs. This cycle is repeatedly executed until some criteria is met.
Some common algorithms to solve MAB problems include <a href="https://en.wikipedia.org/wiki/Thompson_sampling">Thomoson sampling</a> and 
<a href="https://en.wikipedia.org/wiki/Upper_Confidence_Bound">Upper Confidence Bound (UCB)</a>


### Monte Carlo learning

Monte Carlo methods in reinforcement learning are model-free algorithms that estimate value functions and improve policies by sampling complete episodes of interaction with the environment and averaging the observed returns**. Instead of using a model of state transitions, the agent runs episodes following a policy, records the rewards obtained after visiting states or state–action pairs, and uses the total discounted return to update value estimates. Because updates occur only after an episode finishes, Monte Carlo methods produce unbiased but high-variance estimates and work best in episodic tasks such as games. They can be used for prediction (estimating the value of a fixed policy) or control (learning an optimal policy), often using strategies like ε-greedy exploration or importance sampling for off-policy learning.


### Dynamic  programming

Dynamic Programming (DP) methods in reinforcement learning are a set of algorithms used to compute optimal value functions and policies when a complete model of the environment is known, including transition probabilities and rewards. These methods iteratively evaluate and improve policies by applying the Bellman equations to update state or action values until convergence. Two core processes are policy evaluation (estimating the value function for a given policy) and policy improvement (updating the policy to choose actions with higher expected value), which together form policy iteration. Another common approach is value iteration, which combines these steps by repeatedly updating value estimates toward the optimal Bellman value. Because DP methods require full knowledge of the environment and involve updates over all states, they are mainly used as theoretical foundations or planning tools, rather than for learning directly from experience.

### Temporal difference learning

Temporal-Difference (TD) learning is a class of model-free reinforcement learning methods that learn value functions by updating estimates from other learned estimates at each time step** rather than waiting until the end of an episode. TD methods combine ideas from Monte Carlo learning (learning from sampled experience) and dynamic programming (bootstrapping using current value estimates). After observing a transition from state (s) to (s') with reward (r), the value estimate is updated using the TD error, which measures the difference between the predicted value and a one-step lookahead estimate. Because updates happen incrementally during interaction, TD learning works well for both episodic and continuing tasks and typically has lower variance than Monte Carlo methods. Common algorithms in this family include TD(0) for prediction and control methods such as SARSA and Q-learning.


### Tree search

Tree search methods in reinforcement learning are planning techniques that use a look-ahead search over possible future states and actions** to choose better decisions. Starting from the current state, the algorithm builds a search tree where nodes represent states and edges represent actions, then simulates potential future trajectories using a model of the environment. By evaluating the expected rewards of different branches, the agent selects actions that appear most promising. A widely used approach is Monte Carlo Tree Search (MCTS), which balances exploration and exploitation by repeatedly simulating episodes through the tree and updating value estimates. Tree search methods are powerful for decision-time planning, especially in environments like games, because they can approximate optimal actions without computing full value functions over the entire state space.



## Summary

This note gives a high-level overview of several common approaches for solving a Markov Decision Process (MDP) in reinforcement learning. It introduces five paradigms: Multi‑Armed Bandit, Monte Carlo Method learning, Dynamic Programming, Temporal-Difference Learning, and tree search. Multi-armed bandits represent the simplest setting, focusing on repeatedly choosing actions and updating beliefs based on rewards without modeling state transitions. Monte Carlo methods learn value estimates by averaging returns from complete episodes, while dynamic programming solves MDPs using known environment models and iterative policy evaluation and improvement. Temporal-difference learning combines ideas from Monte Carlo and dynamic programming by updating value estimates incrementally using the TD error during interaction. Finally, tree search methods perform look-ahead simulations over possible future states to guide decision-making, often using techniques like Monte Carlo Tree Search. Together, these approaches represent different strategies for learning or planning optimal policies in reinforcement learning problems.


## References

1. <a href="https://en.wikipedia.org/wiki/Multi-armed_bandit">Multi-armed bandits</a>
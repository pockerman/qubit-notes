# qubit-note: Q-learning

## Overview

<a href="2026-01-25-SARSA.md">qubit-note: SARSA or State-Action-Reward-State-Action</a> discussed SARSA a variant of Temporal Difference Learning.
In this note we will look into another popular TDL approach namely <a href="https://en.wikipedia.org/wiki/Q-learning">Q-learning</a>.


**keywords** temporal-difference-learning, Q-learning, reinforcement-learning

## Q-learning

Q-learning, just like SARSA, is a model-free reinforcement learning algorithm that learns how good an action is in a given state, without needing a model of the environment.
As the name suggests, the algorithms learns a state-action value function $Q(s,\alpha)$. 
The algorithm is very similar to SARSA. Before we show the algorithmic steps, here is the update function used in Q-learning

$$
Q(s,\alpha) = Q(s,\alpha) + \eta \big[r_t + \gamma \max_{\alpha_{t+1}} Q(s_{t+1}, \alpha_{t+1}) - Q(s,\alpha)\big]
$$

The algorithm just like SARSA looks into the future but always selects the action that provides the best $Q$. Contrast this with the update formula 
for SARSA:

$$
Q(s_t, \alpha_t) = Q(s_t, \alpha_t) + \eta \left[r_{t+1} + \gamma Q(s_{t+1}, \alpha_{t+1}) - Q(s_t, \alpha_t) \right]
$$

So Q-learning instead of consulting $\pi$ about $\alpha_{t+1}$ it simply acts greedily and selects the action that provides the best state-action value function.
This is called optimistic bootstrapping; assume the best possible action will be taken next, regardless of what we'll actually do [2].
Here are the steps for Q-learning. These are very similar to SARSA:

#### Step 1

The first step is to initialize the table table that represents $Q(s,\alpha)$ to arbitrary values; often this is just zero. This however, can also
be values that encourage exploration.

#### Step 2

The algorithm begins by some be presented with a state. Q-learning needs to decide what to do whilst at this state. This is done using a policy
$\pi$ which most often will be an $\epsilon-$greedy policy.

#### Step 3

The algorithm will execute the action that was selected from step 2. The environment will respond with a reward $r_t$ and the new state $s_{t+1}$.
In order to apply the update formula we need to calculate what is the best $Q$ at $s_{t+1}$. 
The update rule, see above, is using the future $maxQ(s_{t+1}, \alpha_{t+1})$ in order to update the current $Q(s_{t}, \alpha_{t})$
Compared to SARSA, in Q-learning we don't necessarily choose $\alpha_{t+1}$ when at $s_{t+1}$ but instead ask the policy to provide the action to.

#### Step 4

After updating, we move to $s_{t+1}$ and ask $\pi$ to provide us with an action and we repeat step 3. 
If we've reached a terminal state (like the end of a game or a completed transaction), the episode ends and we start fresh.
The environment has to inform the agent about whether it reached the end of the game or not. So when we take an action in the environment,
we will usually receive not just a reward signal and the next state but also a flag indicating if the end of the game or simulation has been reached.


All in all, Q-learning learns the optimal policy. It is a fast and efficient algorithm that is ideal for batch learning [2]. 
Q-learning, compared to SARSA, is more optimistic which can be dangerous in risky domains, and it suffers from maximization bias that can overestimate action values when estimates are noisy [2].


## Summary

This note introduces Q-learning as a popular temporal-difference, model-free reinforcement learning algorithm.
Q-learning learns a state–action value function that estimates how good it is to take action $\alpha$ in state $s$, without needing a model of the environment. Its update rule uses the maximum estimated future Q-value rather than the value of the action actually taken, which makes it an off-policy method:

$$
Q(s,\alpha) = Q(s,\alpha) + \eta \big[r_t + \gamma \max_{\alpha_{t+1}} Q(s_{t+1}, \alpha_{t+1}) - Q(s,\alpha)\big]
$$

Unlike SARSA, which updates based on the next action chosen by the current policy, Q-learning assumes the best possible action will be taken next (“optimistic bootstrapping”). This allows it to directly learn the optimal policy.

The algorithm proceeds by initializing the Q-table, selecting actions using a policy such as ε-greedy, executing actions to observe rewards and next states, updating Q-values using the max future Q-value, and repeating until a terminal state is reached.

Overall, the note emphasizes that Q-learning is efficient and well-suited for batch learning, but also highlights its downsides: it can be overly optimistic in risky environments and may suffer from maximization bias, leading to overestimated action values when rewards are noisy.



## References

1. <a href="https://en.wikipedia.org/wiki/Q-learning">Q-learning</a>
2. Hadi Aghazadeh, _Reinforcement Learning for Business_, Manning Publications
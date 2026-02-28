# qubit-note: Markov Decision Process

## Overview

In this qubit-note, we introduce the mathematical concept of a <a href="https://en.wikipedia.org/wiki/Markov_decision_process">Markov decision process</a>, or MDP, and in particular finite Markov decision process. An MDP is a discrete-time stochastic control process. It can be used as a  framework for modeling decision making in situations where outcomes are partly random and partly under the control of a decision maker [2]. Furthermore, MDPs are useful for studying optimization problems solved via <a href="https://en.wikipedia.org/wiki/Dynamic_programming">dynamic programming</a>. 

Within the  MDP framework, the environment states are fully observable at each time step. <a href="https://en.wikipedia.org/wiki/Partially_observable_Markov_decision_process">Partially observable Markov decision processes (POMDP)</a> is a more general framework in which the agent cannot fully observe the state of an environment. Moreover, even though it is often assumed that the state evolves according
to an MDP, very often this model is not known, thus motivating the use of the so called <a href="https://en.wikipedia.org/wiki/Model-free_(reinforcement_learning)">_model-free_</a> reiforcement learning. 
Similarly, when a model is not known, it may be possible to first learn an MDP using, for example, data-driven methods and then use this for _model-based_ RL (see [4] for a review of these methods).

Note that both MDP and POMDP constitute frameworks upon which we can build solution algorithms and they are not algorithms themselves.

----
**Remark**

MDPs were known at least as early as the 1950s; a core body of research on 
Markov decision processes resulted from Ronald Howard's 1960 book, Dynamic Programming and Markov Processes [2]. 
They are used in many disciplines such as robotics, automatic control, economics and manufacturing. 
The name of MDPs comes from the Russian mathematician <a href="https://en.wikipedia.org/wiki/Andrey_Markov">Andrey Markov</a> as they are an extension of Markov chains. We will introduce MDPs by first considering Markov processes (MP) or Markov chains.

----

**keywords** markov-decision-process, markov-property, reinforcement-learning


## Markov decision process

In order to better understand what an MDP is, we need to first understand what a Markov process or chain is.
So let's start with that.

## Markov process

Frequently, we deal with systems that we can observe their state. For example, we can tell whether today is sunny or raining or if a car is moving or not. The system can transition to various states under some governing dynamics. Let's assume  that somehow we can tell that the system can encompass a state from a given state space $\mathbb{S}$. Let's assume also that this set is finite. Our observations can then form a sequence of states 

$$s_1 \rightarrow s_2 \rightarrow s_3 \rightarrow s_1 \dots$$

We call such a sequence of states a history or trajectory. We now ask ourselves what is the probability to go from $s_1$ to $s_2$ or more generally, what is the probability to transition to $s_{t+1}$
given that we have experience the trajectory $T_{t}$? That is we want to know 

$$P(s_{t+1}|T_t)=P(s_{t+1}|s_t, s_{t-1}, s_{t-2}, \dots)=?$$

where $T_t$ denotes the states we have seen up until and including time step $t$.
Depending on the situation and how far back in the trajectory we want to go, the expression above may involve a number of terms. The Markov assumption greatly simplifies things. The above probability will only depend on the current state $s_t$ and the current action taken i.e. 

$$P(s_{t+1}|T_t)=P(s_{t+1}|s_t)$$

The equation above simply says that the probability transitioning to $s_{t+1}$ given the experience $T_t$ is equal to the probability of 
transitioning to this state given that we have been to state $s_t$. This implies that the probability of going to $s_{t+1}$ only depends on the previous state $s_t$

Under the Markov assumption, we can device a transition matrix that shows us the probability moving from state $i$ to state $j$.
We still need to model these probabilities, but this is easier than dealing with the whole trajectory. Thus, we can say that a Markov process
conists of two essential elements

- A set of states $\mathbb{S}$ that the system can be in
- A transition matrix $\mathbf{T}$ that defines the system dynamics. 

The element $T_{i,j}$ is the probability when in state $i$ to transition to state $j$. If we have $N$ states, then $\mathbf{T}$ will be of size $N\times N$. A useful graphical representation of a Markov process is as graph where the nodes of the graph represent the states of the system and the edges the possible transitions between states. Such a representation is also common when modeling finite state machines.


## Markov decision processes

Now that we have an understanding what a Markov process is, we want to look into Markov decision processes and incorporate the 
actions space $\mathbb{A}$. Now the trajectory $T_t$ will include not just states but also actions and rewards. Thus we can rewrite

$$P(s_{t+1}|T_t)=P(s_{t+1}|s_t, s_{t-1}, s_{t-2}, \dots)=?$$

as 

$$P(s_{t+1}|T_t)=P(s_{t+1}|s_t, \alpha_t, s_{t-1}, \alpha_{t-1}, \dots)=?$$

and similarly,

$$P(s_{t+1}|T_t)=P(s_{t+1}|s_t)$$

as

$$P(s_{t+1}|T_t)=P(s_{t+1}|s_t, \alpha_t)$$

The last equation simply says that the probability transitioning to $s_{t+1}$ given the experience $T_t$ is equal to the probability of 
transitioning to this state given that we have been to state $s_t$ and selected action $\alpha_t$. This implies that the probability of going to $s_{t+1}$ only depends on the previous state $s_t$ and the action we selected when at that state. Specifically, let's follow the convention in [1], and define an MDP as the following tuple

$$
(\mathbb{S}, \mathbb{A}, P_{s}^{\alpha}, R_{s_is_j}^{\alpha_k}, \gamma, S_0)
$$

where apart from the state space $\mathbb{S}$ and the action space $\mathbb{A}$, it also includes a so-called discount factor $\gamma$ and intial state $S_0$ and a reward function $R_{s_is_j}^{\alpha_k}$ that provides the reward going from state $s_i$ to state $s_j$ by choosing action $\alpha_k$ and the probability of taking action $\alpha$ when at state $s$.

A game (or any other control task) that exhibits the Markov property is said to be a Markov decision process (MDP). With an MDP, the current state alone contains enough information to choose optimal actions to maximize future rewards. Modeling a control task as an MDP is a key concept in reinforcement learning.  The MDP model simplifies an RL problem dramatically, as we do not need to take into account all previous states or actions; we don’t need to have memory, we just need to analyze the present situation. Hence, we always attempt to model a problem as (at least approximately) a Markov decision processes. The card game Blackjack (also known as 21) is an MDP because we can play the game successfully just by knowing our current state (what cards we have, and the dealer’s one face-up card).

----
**Remark 1:**

In many practical applications completely satisfying the Markov property is impractical or even impossible. In these
cases we try to stay as close to it as possible.

----

### Dynamics of MDP

MDPs pose a classical framework or formalism for sequential decision making. In this framework the actions that the decision maker performs, influence both the subsequent rewards as well as the futures  states and thus the future rewards to be received [1]. When dealing with MDPs in the reinforcement learning framework we estimate in one way or another, either of the following two functions:

- $Q(s, \alpha)$ for each action $\alpha$ and state $s$. This is called the state-action value function see e.g Q-learning.
- $V(s)$ for each state $s$ given that we have optimal action selections. This caled the state value function, see e.g. [value iteration @sec-value-iteration]

Note that both quantities are state dependent. A value function in RL defines the expected cumulative reward of the agent starting from a particular state or state-action pair, following a certain policy. And, as stated above, there are two types of value functions: state-value function $V(s)$ and action-value function $Q(s,\alpha)$. 

Since we are dealing with finite MDPs, $\mathbb{S}$, $\mathbb{A}$ and $\mathbb{R}$ are finite. One question is that how the agent transitions from one state to another. Clearly this depends on the action selected but how does it choose that action?
Let's assume that $R_t$ and $S_t$ are <a href="https://en.wikipedia.org/wiki/Random_variable">random variables</a> that have well defined <a href="https://en.wikipedia.org/wiki/Probability_distribution">discrete probability distribution</a> that depends only on the previous state and action. Hence, for  given values of state and reward say $s_t$ and $r_t$ respectively, the function $p(s_t, r_t | s_{t-1}, \alpha_{t-1})$
defines the so-called dynamics of the MDP [1]. The dynamics function isa mapping from $\mathbb{S}\times \mathbb{R} \times \mathbb{S} \times \mathbb{A}$ to the interval $[0,1]$. It specifies a probability distribution for each choice of $s$ and $\alpha$ [1]. Hence

$$\sum_s \sum_r p(s,r|s, \alpha) = 1,~~ \forall s \in \mathbb{S}, \alpha \in \mathbb{A}$$

In an MDP, the probabilities given by the dynamics function completely characterize the
environment’s dynamics [1]. This means that the probability of each possible value for $s_t$ and $r_t$ depends only on the immediately preceding state and action, i.e. on $s_{t-1}$ and $\alpha_{t-1}$.  Therefore, state must include information about all aspects
of the past agent-environment interaction that make a difference for the future. If it does, we will say that the state satisfies the Markov property. Given the dynamics function $p$ we can compute anything that we may be interested in about the environment e.g.

- The state transition probabilities $p(\dot{s} | s, \alpha) = \sum_r p(\dot{s}, r | s, \alpha)$
- The expected rewards for state-action pairs $r(s, \alpha) = \sum_r r \sum_{\dot{s}} p(\dot{s}, r | s \alpha)$

## Summary

This qubit-note introduced the mathematical concept of Markov decision process. An MDP is a discrete-time stochastic control process. It can be used as a  framework for modeling decision making in situations where outcomes are partly random and partly under the control of a decision maker [2]. Furthermore, MDPs are useful for studying optimization problems solved via <a href="https://en.wikipedia.org/wiki/Dynamic_programming">dynamic programming</a>. Within the  MDP framework, the environment states are fully observable at each time step. 

An MDP generalizes the notion of a Markov process or a Markov chain in order to include actions and rewards.
This makes an MDP a suitable framework for decision making and control. A simple
Markov process is a set of states $\mathbb{S}$ along with a transition probability function that describes the transitioning from one
state to the next. The defining property of a Markov process and an MDP is that the probability of being in a future state is entirely determined by the current state, 
and not by previous states or hidden variables. 

Note however, that in general, the measured state of the system may correspond to a measurement of a higher-dimensional environmental state that evolves according to a stochastic, nonlinear dynamical system. Finally note that the MDP framework is closely related to transition state theory and the Perron-Frobenius operator, which is the adjoint of the Koopman operator.

Actions are very important in an MDP. Without actions the agent simply becomes an observer and cannot influence the process.
The agent employs a policy $\pi$ in order to select an action at a given state.

## References

1.  Richard S. Sutton and Andrew G. Barto, _Reinforcement Learning: An Introduction_, available at: http://incompleteideas.net/book/RLbook2020.pdf, last accessed 18/02/2024..
2. <a href="https://en.wikipedia.org/wiki/Markov_decision_process">Markov decision processes</a>
3. <a href="https://en.wikipedia.org/wiki/Andrey_Markov">Andrey Markov</a>
4. Thomas M. Moerland, Joost Broekens, Aske Plaat, Catholijn M. Jonker, _Model-based Reinforcement Learning: A Survey_, https://arxiv.org/abs/2006.16712, last accessed 02/01/2026.

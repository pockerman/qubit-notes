# qubit-note: LLM Series | Prompt Engineering Part 2

## Overview

<a href="2025-04-29-prompt-methods.md">qubit-note: LLM Series | Prompt Engineering Part 1</a> looked into three ptompt engineering
approaches. In this qubit note we expand into these techniques by looking into the following approaches:

- <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
- <a href="https://www.promptingguide.ai/techniques/react">Reasoning and Acting (ReAct)</a>
- <a href="https://langchain-ai.github.io/langgraph/tutorials/rewoo/rewoo/">Reasoning WithOut Observation (ReWOO)</a>

**keywords:** Large-language-models, Prompt-engineering, AI-engineering, Machine-learning

## Prompt Engineering

In this note we discuss the following three prompting techniques:

- <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
- <a href="https://www.promptingguide.ai/techniques/react">Reasoning and Acting (ReAct)</a>
- <a href="https://langchain-ai.github.io/langgraph/tutorials/rewoo/rewoo/">Reasoning WithOut Observation (ReWOO)</a>

Let's start by discussing Tree-of-Thoughts prompting (ToT)

#### Tree-of-Thoughts prompting (ToT)

Tree-of-thoughts (ToT) prompting is a technique that was developed to enhance the problem-solving
capabilities of LLMs by enabling more structured exploration of different reasoning paths.
The technique itself builds on a number of other approaches [4]:

- CoT prompting, which enables step-by-step reasoning
- Self-consistency methods that generate multiple reasoning paths
- Human problem-solving approaches that involve exploration and backtracking

The key innovation of ToT is that it approaches the thinking process as  a tree search problem.
Specifically, at each step, the model can generate and evaluate multiple thoughts, or intermediate reasoning steps, and then select the
most promising paths to continue exploring. This allows for more sophisticated problem-solving that
includes exploration, evaluation, and backtracking capabilities [4].

Although ToT is a powerful technique can have several drawbacks [4]. Namely:

- The approach explores multiple paths which increases computational complexity.
- Because it generates multiple path the evaluation process is more involved.
- Often the model needs to combine insights from different paths inducing possible coherence problems.
- ToT prompts tend to be complex

#### Reasoning and Acting (ReAct)

ReAct combines reasoning and acting to solve complex language reasoning and decision-making tasks.
It does so by allowing LLMs to mimic human-like operations from the real world, and thus models can take
actions in order to gain information. ReAct is an iterative process exhibiting the following characteristics [4]:

- Reasoning traces
- Actions
- Observations

ReAct is a good prompting techique to use when [4]

- When a task requires information beyond the LLM’s pre-trained knowledge
- When an LLM needs to navigate and interact with a simulated environment 
- When you need to combine the power of LLMs with the capabilities of external tools
- When the task requires a problem to be broken down into smaller steps and decisions must be made based on intermediate results

Just like ToT, ReAct has a number of limitations [4]

- Dependency on external tools
- Error propagation 
- Token limitations
- Computational cost
- Prompt complexity 

#### Reasoning WithOut Observation


## Summary


## References

1. <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
2.  <a href="https://www.promptingguide.ai/techniques/react">Reasoning and Acting (ReAct)</a>
3. <a href="https://langchain-ai.github.io/langgraph/tutorials/rewoo/rewoo/">Reasoning WithOut Observation (ReWOO)</a>
4.  Ken Huang, _LLM Design Patterns_, Packt Publishing

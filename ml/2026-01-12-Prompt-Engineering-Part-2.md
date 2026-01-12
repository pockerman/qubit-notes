# qubit-note: LLM Series | Prompt Engineering Part 2

## Overview

<a href="2025-04-29-prompt-methods.md">qubit-note: LLM Series | Prompt Engineering Part 1</a> looked into three ptompt engineering
approaches. In this qubit note we expand into these techniques by looking into the following approaches:

- <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
- <a href="https://www.promptingguide.ai/techniques/react">Reasoning and Acting (ReAct)</a>
- <a href="https://langchain-ai.github.io/langgraph/tutorials/rewoo/rewoo/">Reasoning WithOut Observation (ReWOO)</a>

## Prompt Engineering

Let's start by discussing Tree-of-Thoughts prompting (ToT)

#### Tree-of-Thoughts prompting (ToT)

Tree-of-thoughts (ToT) prompting is a technique that was developed to enhance the problem-solving
capabilities of LLMs by enabling more structured exploration of different reasoning paths

ToT builds on several techniques:
- CoT prompting, which enables step-by-step reasoning
- Self-consistency methods that generate multiple reasoning paths
- Human problem-solving approaches that involve exploration and backtracking

The key innovation of ToT is treating thinking as a tree search problem, where at each step, the model
can generate and evaluate multiple “thoughts” (intermediate reasoning steps) and then select the
most promising paths to continue exploring. This allows for more sophisticated problem-solving that
includes exploration, evaluation, and backtracking capabilities.

While powerful, ToT faces several challenges:
• Computational complexity: Exploring multiple paths can be computationally expensive
• Evaluation difficulty: Determining the quality of different thought paths can be challenging
• Coherence across branches: Ensuring consistency when combining insights from different branches
• Prompt design complexity: Creating effective ToT prompts requires careful consideration

#### Reasoning and Acting (ReAct)

Reasoning and Acting (ReAct) is a prompting technique developed by researchers from Princeton
University and Google that enhances an LLM’s ability to perform reasoning and acting in simulated
environments (https://arxiv.org/pdf/2210.03629). It allows LLMs to mimic human-like
operations in the real world, where we reason verbally and take actions to gain information. ReAct
combines reasoning and acting to solve complex language reasoning and decision-making tasks.

The key characteristics of ReAct are as follows:
• Reasoning traces: LLMs generate text that explains their thought process step by step
• Action generation: LLMs produce text actions that represent interactions with external tools
or environments
• Observation incorporation: The results of actions (observations) are fed back into the LLM’s
context, influencing subsequent reasoning and actions
• Iterative process: ReAct typically involves multiple Thought/Action/Observation steps, allowing
for dynamic problem solving

ReAct excels in the following scenarios:
• When a task requires information beyond the LLM’s pre-trained knowledge (for example,
multi-hop question answering or fact verification)
• When an LLM needs to navigate and interact with a simulated environment (for example,
online shopping or text-based games)

When you need to combine the power of LLMs with the capabilities of external tools (for
example, search engines, calculators, and APIs)
• When the task requires a problem to be broken down into smaller steps and decisions must be
made based on intermediate results

While ReAct is a powerful framework, it has certain limitations:
• Dependency on external tools: ReAct’s effectiveness is partly dependent on the capabilities
and reliability of the external tools it uses
• Error propagation: Errors in tool use or interpretation of observations can propagate through
the reasoning process, leading to incorrect conclusions or actions
• Token limitations: The iterative nature of ReAct can lead to long sequences of text, potentially
exceeding the token limits of some LLMs
• Computational cost: Multiple rounds of reasoning, action, and observation can be computationally
expensive, especially when using LLMs or complex tools
• Prompt engineering challenges: Designing effective ReAct prompts that properly guide the
LLM’s reasoning and action selection can be challenging and may require experimentation


#### Reasoning WithOut Observation


## Summary


## References

1. <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
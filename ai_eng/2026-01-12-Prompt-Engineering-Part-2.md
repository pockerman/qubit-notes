# qubit-note: LLM Basics | Prompt Engineering Part 2

## Overview

<a href="2025-04-29-prompt-methods.md">Prompt Engineering Part 1</a> looked into three prompt engineering
approaches. In this qubit note we expand the available techniques by looking into the following approaches:

- <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
- <a href="https://www.promptingguide.ai/techniques/react">Reasoning and Acting (ReAct)</a>

## Prompt Engineering

In this note we discuss the following three prompting techniques:

- <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
- <a href="https://www.promptingguide.ai/techniques/react">Reasoning and Acting (ReAct)</a>

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
includes exploration, evaluation, and backtracking capabilities [4]. Here is an example
of a prompt using ToT:

```
Instructions: Analyze this movie review using the Tree-of-Thought method :

1. Generate three potential sentiment labels (branches) for the review (e.g., Positive, Negative, Neutral/Mixed).
2. For each branch, evaluate pros and cons based on evidence from the text.
3. Select the best label based on the strongest evidence.
4. Output only the final label as: Sentiment: <label>

---
Review: $MOVIE=REVIEW

---
Sentiment:
```

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

---
**Remark**

We will discuss again ReAct and ToT when we discuss reasoning in LLM agents, see  <a href="./agents/2026-05-16-AI Agents-Decision-Making-AI-Agents.md">Decision Making in AI Agents</a>.

---

Here is an example of how a ReAct prompt might look like:

```
You are an AI assistant that uses the ReAct (Reasoning + Acting) framework to analyze movie reviews.

Your task is to determine the sentiment of the following movie review.

Follow this process:

1. Thought: Briefly reason about the review and identify important clues such as positive or negative language, tone, emotions, and overall opinion.
2. Action: Extract relevant evidence phrases from the review.
3. Observation: Analyze whether the extracted evidence supports Positive, Negative, or Neutral/Mixed sentiment.
4. Repeat Thought → Action → Observation as needed until you are confident.
5. Final Answer: Output only the final sentiment label in the following format:

Sentiment: <Positive | Negative | Neutral/Mixed>

---
Review:
$MOVIE_REVIEW
---

```

Just like ToT, ReAct has a number of limitations [4]

- Dependency on external tools
- Error propagation 
- Token limitations
- Computational cost
- Prompt complexity 


## Summary

This note expands on prompt engineering techniques for large language models by introducing Tree-of-Thoughts Prompting (ToT), Reasoning and Acting (ReAct). Tree-of-Thoughts prompting improves problem-solving by treating reasoning as a tree-search process where the model explores multiple reasoning paths, evaluates intermediate thoughts, and backtracks when necessary, enabling more structured and sophisticated decision-making. However, ToT increases computational complexity, prompt complexity, and the difficulty of evaluating and combining reasoning paths. The note also explains ReAct, a framework that combines reasoning with actions and observations, allowing LLMs to interact with external tools or environments while iteratively solving problems. ReAct is especially useful when tasks require external knowledge, tool usage, or step-by-step decision-making, but it introduces challenges such as dependency on external tools, error propagation, token limitations, computational cost, and complex prompts. Overall, the note highlights how advanced prompting strategies can improve LLM reasoning and agent-like behavior beyond basic prompting techniques.



## References

1. <a href="https://www.promptingguide.ai/techniques/tot">Tree-of-Thoughts prompting (ToT)</a>
2.  <a href="https://www.promptingguide.ai/techniques/react">Reasoning and Acting (ReAct)</a>
3. <a href="https://langchain-ai.github.io/langgraph/tutorials/rewoo/rewoo/">Reasoning WithOut Observation (ReWOO)</a>
4.  Ken Huang, _LLM Design Patterns_, Packt Publishing

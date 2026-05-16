# qubit-note: AI Agents| Introduction

## Overview

So far we have discussed LLMs as static components i.e. a query is given in one way or another to the model and the
model responded according to its knowledge. We also saw techinques to further increase the base knowledge a model has by using
for example fine tuning or RAG techniques. In this series we want to take things a bit further and disucss AI agents based on LLMs.

## Introduction

AI agents and in particular multi-agent systens are the next evolution of how we can utilize and interact with an LLM. Although LLMs are very capable
they fall short when real world problem solving is concerned. Firstly, LLMs have statick knowledge; we are able to overcome this by using fine tuning and/or RAG but the
matter still remains that an LLM knows as much as its training dataset includes. Secondly,  an LLM is not able to act. Very often real world problems require an action e.g.
send a notification. LLMs by themselves cannot do this. Finally, modern systems often involve complex workflows. LLMs, as they stand, do not have the ability to manage complex workflows. 

So why AI agents solve these problems then?

AI agents constitute a major if not fundamnetal shift in how we interact with a large language model. LLMs possess the knowledge needed but their are passive. In contrast, AI agents
are active components of a system able to make decisions and utilise tools in order to execute the assigned task. Specifically, AI agents bring the following capabilities on top
of an LLM [1]:

- External connectivity
- Action execution
- Workflow orchestration

Hence an AI agent not only can it understand requests but also it can break these down into executable steps, determine which tools are needed for each of these steps and coordiante their execution.
Let's move on and discuss the core components of an AI agent.

### Core components of an AI agent

Now that we understand why AI agents are useful, let's see the core components that an AI constitutes of.
One thing you need to bear in mind is that a reliable agent is not  just a supercharged LLM, this is a  carefully designed system built on three foundational components [1]:

- Memory
- Tool integration
- Decision making

Let's see what each of these entails. We will briefly discuss  these here and cover them in more detail in dedicated sections.

#### Memory

Memory is the backbone of any intelligent agent. Without it, agents would forget past interactions, leading to frustrating user experiences.
There are two types of memory [1]:

- Short-term memory
- Long-term memory

#### Tool integration

Tool integration is one of the most effective strategies for reducing hallucinations in agents. By connecting LLMs to trusted external systems, e.g.  APIs, databases, and knowledge graphs, we enable them to retrieve real data rather than relying on guesses or assumptions. This significantly enhances the reliability of agents, ensuring their outputs are actionable and grounded in reality.
By integrating tools, agents can ground their responses in verified sources of truth, such as:

- APIs for real-time data 
- Databases 
- External systems for executing actions 

This grounding ensures that the agent doesn’t rely on guesswork, reducing hallucinations and improving user trust.

#### Decision making

Integrating memory and tools makes an AI agent functional, but decision-making is what makes it intelligent. Decision-making frameworks determine how an agent reasons, selects tools, orchestrates workflows, and ultimately fulfills user requests. Without proper decision-making, an agent might use the wrong tool for a task, execute tasks in the wrong order, or fail to adapt to ambiguous or evolving user requests [1]. Decision maiking can be rule-based or AI-based. The Reasoning and Act or ReAct framwork is one of the most powerful decision making frameworks we will discuss [1].

## Summary


## References

1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications
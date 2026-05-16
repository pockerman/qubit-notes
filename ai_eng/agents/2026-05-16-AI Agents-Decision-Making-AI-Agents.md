# qubit-note: AI Agents | Decision Making in AI Agents

## Overview

In this note we will discuss decision making in AI agents. There are two main
frameworks where decision making can be discussed:

- Rule-based systems
- AI-based systems

Two main approaches for AI-based systems are ReAct and ToT (see <a href="../2026-01-12-Prompt-Engineering-Part-2.md">Prompt Engineering Part 2</a>)


##  Decision Making in AI Agents

Decision-making frameworks generally fall into two categories: rule-based systems and AI-driven reasoning.

Rule-based systems rely on predefined logic. For example:

If the query mentions "flight," use the flight booking API.
If the query mentions "hotel," use the hotel booking API.
While simple and transparent, rule-based systems are rigid. They cannot handle ambiguous requests or adapt to unexpected scenarios. For instance, if a user asks, "Find me a pet-friendly hotel near Union Square," a purely rule-based system might fail to address the "pet-friendly" constraint without explicit programming.

AI-driven systems, in contrast, use models like LLMs to dynamically reason through tasks. Instead of relying on hardcoded rules, the agent analyzes user input, determines the required steps, and selects the appropriate tools. This approach is flexible, scalable, and capable of handling complex queries.


ReAct Framework: Reasoning + acting
The ReAct framework (Reasoning + Acting), shown in figure 6.5, combines reasoning (thinking about the next step) with acting (performing a task) in an iterative process. By alternating between reasoning and acting, agents can dynamically adapt their workflows, ensuring each action is informed by the context of previous steps.

Here is how ReAct works:

Reasoning: The agent reasons about the user’s request and determines the next step.
Acting: The agent executes the action, such as querying a tool or retrieving data.
Observing: The agent observes the results of the action and incorporates them into its reasoning.
Repeating: This cycle continues until the agent produces a final answer.

The ReAct framework ensures agents handle tasks step-by-step, dynamically adjusting to changing information and user feedback.

Enhancing Decision-Making with Tree-of-Thought (ToT)
While ReAct handles tasks iteratively, Tree-of-Thought (ToT) expands on this by exploring multiple potential solutions simultaneously. This is especially useful for tasks involving high uncertainty or multiple valid answers.

For example suppose the user asks the following question related to supply chain optimization: "How can we reduce shipping costs for our European customers?"

Branch 1: Evaluate new shipping partners.
Branch 2: Analyze warehouse consolidation strategies.
Branch 3: Explore bulk shipping discounts.
The agent evaluates each branch, simulates potential outcomes, and selects the most cost-effective solution. This parallel exploration makes ToT ideal for solving complex, multi-faceted problems.


## Summary

## References


1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications
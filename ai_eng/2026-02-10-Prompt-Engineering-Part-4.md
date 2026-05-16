# qubit-note: LLM Series | Prompt Engineering Part 4

## Overview 

We have seen various prompting techniques in previous posts; <a href="2025-04-29-Prompt-Engineering-Part-1.md">qubit-note: LLM Series | Prompt Engineering Part 1</a> and
<a href="2026-01-12-Prompt-Engineering-Part-2.md">qubit-note: LLM Series | Prompt Engineering Part 2</a>. In this note, we will go over as to what
constitutes a good prompt.


## Prompt Engineering Part 4

Prompt engineering is the process of crafting instructions that guide AI language models to generate desired outcomes. At first glance, it might seem straightforward. 
We simply tell the AI what we want, and it delivers. However, anyone who has worked with these models quickly discovers that writing effective prompts is more challenging than it appears.
In fact the prompting techniques we have already discussed illustrate that the model's output may vary depending on the prompt.
Indeed, the ease of getting started with prompt engineering can be misleading. While anyone can write a prompt, not everyone can write one that consistently produces high-quality results. 


### What are the characteristics of a good prompt:

A prompt typically consists of several components:

- The task description 
- The context provides necessary background information. 
- The concrete task is the specific question to answer or action to perform.

Given that, a good good prompt is one that clearly steers the model toward the task you want, with minimal ambiguity, and constrains the output so it’s predictable and reliable.

A well-structured prompt typically includes clear instructions (what to do), relevant context (background to ground the response), focused input data (only what matters), an explicit output format (template/structure/length), and explicit quality criteria (e.g., be factual, avoid speculation, stay grounded in provided context) .

Furthermore, most model APIs allow us to split prompts into several kinds of prompts: 

- system 
- user 
- assistant

System prompts typically contain task descriptions and role-playing instructions that shape how the model behaves throughout the conversation.
On the other hand, user prompts contain the actual task or question. For instance, if we are building a chatbot that helps buyers understand property disclosures, the system prompt might instruct the model to act as an experienced real estate agent, while the user prompt contains the specific question about a property.

Clarity is the key factor to effective prompting.  Specific and unambiguous instructions help AI models generate appropriate responses. 
We should explain exactly what we want, define any scoring systems or formats we expect, and eliminate assumptions about what the model might already know.

Context is equally important. Providing relevant information helps models perform better and reduces hallucinations. 
If, for example, we want the model to answer questions about a research paper, including that paper in the context will significantly improve response quality. 
Without sufficient context, the model must rely on its internal knowledge, which may be outdated or incorrect.

 
## Summary

A good prompt clearly defines the task, provides sufficient context, specifies constraints and expected output format, and may include examples to guide the model toward reliable responses. Effective prompts reduce ambiguity by stating the audience, desired style, length, and evaluation criteria, while complex tasks can benefit from structured reasoning approaches such as Tree-of-Thoughts Prompting or Reasoning and Acting. Strong prompts often include grounding instructions to improve factual accuracy and are typically refined iteratively through testing and adjustment. In practice, a good prompt is usually a combination of a clear objective, relevant context, constraints, examples, and a well-defined output structure.


## References

1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications

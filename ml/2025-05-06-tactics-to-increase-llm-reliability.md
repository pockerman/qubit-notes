# qubit-note: LLM Series | Tactics to Increase LLM Reliability

## Overview

In this note I briefly summarise some of the tactics one can follow in order to increase 
the reliability of LLM models. LLMs have proven that they are capable of many different things thus
we need to take their capability somehow for granted. On the other hand, LLMs have not yet
proven their reliability i.e consistently produce the appropriate response. Increasing the 
reliability of an AI system, is one of main duties of an AI engineer.

In this brief note I summarise some tactics we can employ in order to increase the reliability of an LLM model:

- Tactic 0: Don't use an LLM if you don't have to
- Tactic 1: Use the right model for your application
- Tactic 2: Explore prompting
- Tactic 3: Use fine-tuning
- Tactic 4: Use RAG and GraphRAG
- Tactic 5: Use tools
- Tactic 6: Implement facts checking


**keywords** Large-language-models, LLM-reliability, AI-engineering

## Tactics to increase LLM reliability

LLMs are becoming ubiquitous in modern software either as copilots, bots or any kind or search engine.
Despite their versatility, LLMs have weaknesses that should be addressed. In this short note,
I briefly discuss various tactics to improve LLM reliability. Specifically, I discuss the following 7 tactics:

- Tactic 0: Don't use an LLM if you don't have to
- Tactic 1: Use the right model for your application
- Tactic 2: Explore prompting
- Tactic 3: Use fine-tuning
- Tactic 4: Use RAG and GraphRAG
- Tactic 5: Use tools
- Tactic 6: Implement facts checking

Let's discuss these tactics one by one.

### Tactic 0: Don't use an LLM if you don't have to

Obvious as it may sound, don't use an LLM or any ML model if you don't have to. ML models are not deterministic, so this means
that the output is stochastic. If something can be inferred by your normal code flow, then use this rather than an ML model.
You avoid any stochasticity problems plus you don't need to pay for the inference costs.


### Tactic 1: Use the right model for your application

Although large language models can in general cope with any text that is thrown at them (within limits), some models have been tuned
for specific tasks e.g. maths problems. The first tactic involves identifying the particularities of our application and thus 
target the right LLM. This is also relevant with respect to the size of the model; inference with a GPT-4o model should be
faster when compared to a full blown GPT-4 model.

### Tactic 2: Explore prompting

We, and our applications, interact with LLMs using prompts. We can improve the response of an LLM by exploring various tactics such as
few-shot prompting where a number of examples is included in the prompt in order to guide the reponse of the LLM, Chain-of-Thought and
ReAct. For more information see [1, 2].

### Tactic 3: Use fine-tuning

Prompting can get us that far. If however the quality of the responses has not been improved, we should look into fine-tuning.
In this case, we will need a, typically, small dataset where for every instance we have the desired model response.
We train the model over this small dataset. As its name suggests, we  don't do a full blown model training but rather trying
to train the model in order to imporve its response for our particular scope. Fine-tuning is similar to transfer learning, however
with the former we train the whole model and not just a portion of it, e.g. output layer, as its typically the case with fine-tuning.


### Tactic 4: Use RAG and GraphRAG

An alternative to fine-tuning is RAG or retrieval-augmented-generation and its cousing GraphRAG.
Fine-tuing is ideal if we want to imporve the responses of an LLM in a rather limited cases. 
However, it is not ideal if we want to use our LLM on specific domain that the model has not been trained on.
RAG allows us to augment the models knowledge via interacting with a data source and injecting specific
knowledge in the prompt we give to the model. Typically vector databases are used to propel RAG but this need not
be the case. Using a knowledge graph instead is called a GraphRAG. 
GraphRAG can produce more accurate responses however it may be more difficult to develop.

### Tactic 5: Use tools

RAG is useful to inject information into an LLM that it has not been trained on and it changes relatively
infrequently. However, there are cases where the data we need to pass into the LLM change dynamically e.g. weather data.
In this case need to use tools.

I consider both RAG and GraphRAG as some sort of tooling however under the term tools in LLMs is meant ta function, an API and database
that the LLM can call itself dynamically. The introduction of the <a href="https://www.anthropic.com/news/model-context-protocol">model context protocol</a> 
can seriously help us in this direction.

### Tactic 6: Implement facts checking

Finally, you need to implement some sort of facts checking of the response that your LLM came up with.
As mentioned previously, LLMs are stochastic in nature and their response is not necessarilly the same for the
same input. Of course most of the time the semantics, i.e. dates, numbers, feelings e.t.c, should stay the say.
In any case it is towards your advantage to somehow verify what the model produced is valid. Reflection is one approach you can use.
Using another model is a second. Extracting the facts of interest is a third. All these may or may not be easy to implement but
if you want your AI system to be reliable you need to invest time into such approaches.


## Summary 

This note outlines practical engineering tactics to improve the reliability of large language models, emphasizing that while LLMs are powerful, their outputs are inherently stochastic and not consistently reliable by default. It presents a hierarchy of strategies, starting with avoiding LLMs entirely when deterministic code suffices, and then selecting an appropriate model tailored to the task and performance constraints. The text highlights the importance of prompt engineering (e.g., few-shot prompting and chain-of-thought), followed by fine-tuning when prompting alone is insufficient. It contrasts fine-tuning with retrieval-based approaches such as RAG and GraphRAG, which inject external, domain-specific knowledge at inference time. The note also discusses the use of tools and APIs for accessing dynamic data and concludes with the need for fact-checking mechanisms—such as reflection, secondary models, or explicit fact extraction—to validate outputs and ensure dependable AI system behavior.

<a href="2026-01-12-LLM-Hallucination-How-to-Measure-It-Part-1.md">qubit-note: LLM Series | LLM Hallucination & How to Measure It PArt 1</a> introduces various approaches
about how to detect and measure LLM model hallucinations


## References

1. Shivendra Srivastava and Naresh Vurukonda, _Prompt Engineering in Action_, Manning Publications.
2. <a href="https://www.promptingguide.ai/">Prompt Engineering Guide</a>
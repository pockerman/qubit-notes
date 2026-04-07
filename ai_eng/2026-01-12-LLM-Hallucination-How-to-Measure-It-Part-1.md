# qubit-note: LLM Series | LLM Hallucination & How to Measure It PArt 1


## Overview 

Large language models are capable of many different things and they are reshaping the way
we conceive businesses. However, LLMs have limitations which if we don't address can break
an application in a non-recoberable way. It is important therefore that we can monitor the
performance of an LLM model.

<a href="2025-05-06-tactics-to-increase-llm-reliability.md">qubit-note: LLM Series | Tactics to Increase LLM Reliability</a>
discussed several tactics we can employ in order to imporove the perforance of such models. These where general guidelines.
In this series of notes we will go in more details. 

We will start with one of the major problems that reduce the performance of LLMs that is model hallucination

**keywords** Large-language-models, LLM-hallucination, LLM-reliability, AI-engineering

## LLM Hallucination & How to Measure It PArt 1

As language models like GPT become more advanced and more widely used, hallucinations  emerge as a major challenge. 
Hallucinations occur whenan AI system generate content that is untrue, inconsistent, or just plain made-up. 
This, obviously, can lead to the spread of fake information, incorrect medical diagnoses, bad financial advice, and many other potential harms that can be detrimental for a business.

There seems to be some controversy regarding the term _hallucination_ in the AI community, I won't go into this
discussion as our perspective in this series is purely from a systems engineering perspective. Thus, in this series of notes the term
will correspond to a class of issues around truthfulness, consistency, and coherence in language model outputs. 

We can, however, distinguish betweem[1]:

- Intrinsic hallucinations
- Extrinsic hallucinations


The first class of hallucinations corresponds to the cases where the language model generates content that is false or inconsistent based on the knowledge and patterns it has learned from its training data, rather than from the specific conversational context or prompt [1]. The second type of hallucinations occur when the model introduces information that doesn't exist in the provided input or context at all. Unlike intrinsic hallucinations that stem from flawed training knowledge, extrinsic hallucinations represent complete fabrications where the model generates content with no grounding in any available source material [1].


Overall, there are several contributing factors to model hallucinations [1]:

- Training data
- Exposure bias
- Errroneous decoding
- Parametric knowledge bias
- Imperfect representation

Now that we have an understanding of what LLM halluicantions are we want to address how to identify model hallucination and how to measure it.

#### Identify & measure hallucinations

According to [1], there are four steps in this process:

1. Identify the grounding data
2. Create measurement test sets
3. Extract claims and validate against the grounding data
4. Report metrics

We wiil discuss these steps and the involved metrics/evaluation approaches in comning notes.
The list below briefly mentions the various metrics/evaluation approaches we can use. See also [1].

- Grounding Defect Rate (GDR)
- Hallucination Severity Score (HSS)
- Topic-wise Analysis
- <a href="https://arxiv.org/abs/2305.14251">FActScore metric</a>
- <a href="https://en.wikipedia.org/wiki/ROUGE_(metric)">ROUGE metric</a>
- LLM as a judge
- Human evaluation
- Red teaming
- Use a monitoring framework


## Summary

This note introduces LLM hallucination as a critical limitation that can undermine the reliability and safety of applications built on large language models. Hallucinations are defined from a systems engineering perspective as failures of truthfulness, consistency, or coherence, and are categorized into intrinsic hallucinations, which arise from incorrect or inconsistent knowledge learned during training, and extrinsic hallucinations, where the model fabricates information not grounded in the given input or context. The text outlines key causes of hallucinations, including issues in training data, exposure bias, decoding errors, and imperfect knowledge representation. It then presents a high-level framework for identifying and measuring hallucinations—grounding outputs in reference data, creating evaluation test sets, validating extracted claims, and reporting metrics—while briefly surveying common evaluation methods such as grounding defect rates, severity scores, factuality metrics, LLM-based judging, human evaluation, and monitoring practices.

## References

1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications
# qubit-note: LLM Series | Prompt Engineering Part 3

## Overview

When interacting with large language models (LLMs) through prompts, several key parameters can be configured to influence the model's behavior and output. 
Tuning appropriatelly these parameters can enhance the reliability and minimize hallucination in the generated responses.
In this qubit note we will review some of these parameters. Namely, we will discuss

- temperature
- <a href="https://en.wikipedia.org/wiki/Top-p_sampling">top-p sampling</a>
- maximum output tokens
- penalty strengths
- stop sequences

## Prompt Engineering

There are several parameters that we can in tune in order to improve the generated response from a large language model.
We review some of them below


#### Temperature parameter

Perhaps the most known model parameter is the temperature. It controls the randomness and diversity of a chatbot's responses [1]. 
Specifically, the temperature parameter adjusts the distribution of next token probabilities during text generation.
Low temperature values produce more deterministic responses that are more grounded on the provided taining data.
The temperature values vary in the range $[0,2]$.  
Hightemperature values introduce more randomness and diversity into the model's responses. This may be required if we want more casual and conversational responses
e.g. when implementing a chatbot. 


#### Top-p parameter

Another parameter that works closely with the temperature parameter is top-p. This is actually a sampling technique but LLM providers allow us
to control the pool of candiate tokens a model can use. Specifically, this parameter determines the cumulative probability threshold for selecting the top tokens [1].

The top-p (or nucleus) sampling technique is a powerful tool for controlling the randomness and quality of LLM outputs. By tuning the top-p value, we can reduce the risk of hallucinations and improve the coherence and relevance of generated responses. For example, setting top-p to 0.9 means that the model will only consider the smallest set of most probable tokens whose cumulative probability exceeds 90%. This helps eliminate less likely and potentially irrelevant or inconsistent choices.

Similar to the temperature parameter, lower top-p values (e.g., 0.5 to 0.7) result in more focused and deterministic responses because they restrict the selection to only the most probable tokens. This means the model is more likely to choose common words, leading to more predictable but potentially less creative outputs.
Higher top-p values (e.g., 0.8 to 0.95) allow for more diversity and creativity in the generated text. A higher threshold allows the model to consider a wider range of tokens, including less common ones, which can lead to more varied and interesting outputs. However, this increased diversity also comes with a higher risk of irrelevant or incorrect information [1].


----
**Remark**

Temperature and top-p work in sequence; i.e. top-p first narrows the candidate tokens, then temperature controls randomness within that subset. 
For reliable outputs, use temperature=0.3 with top_p=0.8. For creative but controlled responses, try temperature=0.7 with top_p=0.9 [1].

----

There is also a top-k m paramter that restricts sampling to the top k most probable tokens. However, top-p is more adaptive than top-k.


#### Output tokens

Another parameter we can control is the length of the LLM response. In particular, allowing a model to generate lengthy and possibly open-ended outputs 
increases the potential for a model to generate inconsistent and/or contradictory details. Thus apart form being more expensive, lengthy outputs can also be of bad quality.
In a similar token, allowing for open-ended multi-turn conversations can lead to the model losing track of what is being discusses and generate
responses that are inconsistent with the original topic.

Most LLM providers expose a parameter in their API that allows us to set the number of output tokens. In addition, we can use stop sequences; i.e.
define specific tokens or phrases that signal the model to stop generating further content.  
For example, using a stop sequence like "\n" can prevent the model from continuing beyond a single paragraph [1].



#### Frequency and presence penalties 

Frequency and presence penalties are mechanisms that reduce repetition in LLM outputs to improve diversity and overall text quality.

- Frequency penalty reduces the likelihood of generating tokens in proportion to how often they’ve already appeared.
- Presence penalty discourages reuse of any token that has appeared at least once, regardless of frequency.

Higher penalty values push the model toward generating new tokens instead of repeating old ones. Penalty values range from −2.0 to 2.0, with 0.5–1.0 recommended for most use cases.


## Summary

This note explains how prompt-tuning parameters influence LLM behavior and how adjusting them can improve reliability and reduce hallucinations.

It covers the main controls:

- Temperature: Regulates randomness. Low values produce deterministic, factual outputs; higher values increase creativity and conversational tone.
- Top-p (nucleus sampling): Limits token selection to the most probable set whose cumulative probability exceeds a threshold. Lower values yield focused, predictable responses; higher values allow more diversity but increase risk of errors. Top-p is applied before temperature.
- Output length and stop sequences: Limiting maximum output tokens and defining stop sequences helps prevent overly long, inconsistent, or off-topic responses.
- Frequency and presence penalties: Reduce repetition by discouraging reuse of previously generated tokens, improving diversity and text quality.

Overall, the note emphasizes that carefully tuning these parameters—such as using low temperature and moderate top-p for reliability—can significantly improve LLM response quality and consistency.


## References

1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications

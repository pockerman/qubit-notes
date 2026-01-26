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

Another parameter that works closely with the temperature parameter

The top-p (or nucleus) sampling technique is a powerful tool for controlling the randomness and quality of LLM outputs. By tuning the top-p value, we can reduce the risk of hallucinations and improve the coherence and relevance of generated responses.

Top-p sampling works by limiting the pool of candidate tokens to a subset of the most probable options at each generation step. The "p" value determines the cumulative probability threshold for selecting the top tokens. For example, setting top-p to 0.9 means that the model will only consider the smallest set of most probable tokens whose cumulative probability exceeds 90%. This helps eliminate less likely and potentially irrelevant or inconsistent choices.

To find the optimal top-p value for a given task, it's recommended to start with a value around 0.9 and then adjust it based on the observed quality and consistency of the generated outputs. The top-p value, also known as nucleus sampling, sets a probability threshold for token selection during text generation.

Lower top-p values (e.g., 0.5 to 0.7) result in more focused and deterministic responses because they restrict the selection to only the most probable tokens. This means the model is more likely to choose "safe" or common words, leading to more predictable but potentially less creative outputs.

Higher top-p values (e.g., 0.8 to 0.95) allow for more diversity and creativity in the generated text. With a higher threshold, the model considers a wider range of tokens, including less common ones, which can lead to more varied and interesting outputs. However, this increased diversity also comes with a higher risk of irrelevant or incorrect information.

The choice of top-p value thus involves a trade-off between consistency and creativity, and should be tuned based on the specific requirements of the task at hand.


----
**Remark**

Temperature and top-p work in sequence: top-p first narrows the candidate tokens, then temperature controls randomness within that subset. For reliable outputs, use temperature=0.3 with top_p=0.8. For creative but controlled responses, try temperature=0.7 with top_p=0.9.

----


#### Output tokens

When an LLM is allowed to generate lengthy, open-ended outputs, there is a greater potential for the model to introduce tangential or contradictory details that are not grounded in the original context. Similarly, in a multi-turn conversation, each additional turn increases the risk of the model losing track of the main topic and generating responses that are inconsistent with previous statements or the intended goal of the interaction.


Limiting the length and complexity of LLM-generated outputs and the number of conversational turns is an effective strategy for reducing the risk of hallucinations. By keeping responses concise and focused and preventing conversations from dragging on indefinitely, we can minimize the chances of the model generating irrelevant, inconsistent, or fabricated information.

To effectively limit output and turns, developers can implement the following strategies:

- Set maximum token limits for generated responses: By restricting the number of tokens (words or subwords) the model can generate in a single response, we can encourage more concise and focused outputs. This can be done through the LLM API or by post-processing the generated text.
- Use stop sequences: Defining specific tokens or phrases that signal the model to stop generating further content can help ensure responses are well-structured and limited to the intended scope. For example, using a stop sequence like "\n" can prevent the model from continuing beyond a single paragraph.
- Implement strict rules for ending conversations: Setting a maximum number of turns per conversation and having clear conditions for when to terminate the interaction can help prevent conversations from becoming overly complex or meandering. This can be based on the nature of the user's query, the relevance of the model's responses, or a predefined turn limit.
- Provide user controls: Giving users the ability to end the conversation or request a new topic can help keep interactions focused and prevent the model from generating unnecessary or irrelevant content.


----
**Remark**

Tip
In practice, setting a maximum token limit (e.g., 200-300 tokens) and a stop sequence like "\n" can prevent the model from generating irrelevant or overly verbose responses.

----


#### Applying frequency and presence penalties for balanced content

Frequency and presence penalties are techniques for encouraging an LLM to generate more diverse and balanced content by discouraging the repetition of previously generated tokens. By applying these penalties, we can reduce the likelihood of the model generating repetitive or redundant outputs, which can help mitigate hallucinations and improve the overall quality of the generated text.

The frequency penalty penalizes a token based on how often it has already been generated in the text so far. The more times it has appeared, the higher penalty it receives to reduce future reuse likelihood.

The presence penalty is simpler and penalizes a token equally just for having occurred at all previously. It discourages reuse regardless of frequency.

Higher penalty values increase the model's likelihood of sampling new tokens rather than repeating old ones. Penalties range from -2.0 to 2.0. Use 0.5-1.0 for most cases.


#### Minimizing intrinsic randomness for stable performance

## Summary

## References

1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications
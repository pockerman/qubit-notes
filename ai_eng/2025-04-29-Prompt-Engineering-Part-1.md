# qubit-note: LLM Series | Prompt Engineering Part 1


## Overview

In this note I want to go over some basic prompting techniques.
Specifically, we will look into the following methods

- <a herf="https://www.promptingguide.ai/techniques/zeroshot">Zero-shot prompting</a>
- <a href="https://www.promptingguide.ai/techniques/fewshot">Few-shot prompting</a>
- <a href="https://www.promptingguide.ai/techniques/cot">Chain-of-thought prompting</a>

The material in this note is mainly taken from the book <a href="https://www.manning.com/books/prompt-engineering-in-action">_Prompt Engineering in Action_</a>.
If you want to learn more about prompting techniques, apart from the aforementioned book, you can also
visit <a href="https://www.promptingguide.ai/">Prompt Engineering Guide</a>.

**keywords:** large-language-models, prompt-engineering, AI-engineering, machine-learning

## Prompt Engineering

There is no doupt that, at the time of writing this note, LLMs have completely overtaken the
tech industry as they open new paths of doing a lot of things  including software development.

Primarily, a user/client interacts with an LLM via a user prompt. Similarly, we have the system prompt which
basically sets the context up that the user prompt should be interpreted, establishes the tone of the reply 
and possibly provides examples and instructions how the task should be carried out. 
Although personally I wouldn't necessarilly call crafting a prompt an engineering discipline, there exists certainly approaches
we can use in order to improve our prompts and hence the response from the model. 

Overall these techniques/methods allow us to [5]:

- Enhance the quality of the model response
- Appreciate the limitations of the model

Let's start with two techniques  that most of us have used in one way or another.

### Zero-shot and few-shot  prompting

These two approaches refer to the number of examples the model sees before asked to performed a certain task.
Zero-shot means that the model sees no examples whilst few-shot means that the model gets to see a few examples
before crafting its response. 

Thus zero-shot prompting relies exclusively on the capability of the model to parser the user and system prompts
and generate a response. To a great extent this capability depends on the data used to train the model.

In contrast, in few-shot learning, the model gets to see a few examples of what constitutes a right response.
Few-shot learning may be particularly useful in cases when the model has to respond to a task that has multiple outcomes.

Both techniques are rather easy to implement, well nothing really to implement in the zero-shot case, however they have several use cases [5]:

- Language translation
- Sentiment analysis
- Chatbot development

Despite their rather extensive usage, these approaches have limitations. I have already mentioned that zero-shot learning
basically relies on the model's capacity to generate a correct response. With few-shot learning one can guide the model
towards a solution however this approach may be problematic when the conext window is small. 


###  Chain-of-thought prompting

Chain-of-thought is akin to divide-and-conquer technique as in this approach the model breaks down the given problem into smaller steps that can reason about more easilly.
Thus, in this appraoch a step-by-step solution guide to the problem at hand is provided to the model.
We can fuse zero-shot and few-shot learning into chain-of-thought to further enhance the model's capabilities [5].

Note however, that zero-shot prompting combined with chain-of-thought may sometimes be problematic; as the model is not supplied with any example of how to act,
it may generate a number of reasoning steps and thus may not scale.

Use case of chain-of-thought include, [5]:

- Content generation
- Hypothesis testing
- Coding assistants


We can utilise chain-of-thought with <a href="https://www.promptingguide.ai/techniques/react">ReAct</a> in order to accomodate for the fact
that chain-of-thought does not account for any external information. According to [4], often such a combination can lead to a very good prompting
approach. 

CoT prompting, although powerful, has some limitations:
- It can inflict high token usage as well as computation time
- When doing multi-step reasonig there is a potential for error propagation
- Just loke all prompting techniques, the quality of the initial prompt is important
- Finally, CoT may not be suitable for all types of problems

Note that CoT has several extensions:

- Adaptive CoT
- Multi-modal CoT: https://arxiv.org/abs/2302.00923
- Collaborative CoT: https://arxiv.org/html/2409.07355v1
- Meta-learning for CoT: https://arxiv.org/abs/2311.05922

## Summary

This qubit-note provides an overview of basic prompting techniques used to interact effectively with large language models, focusing on zero-shot, few-shot, and chain-of-thought (CoT) prompting. It explains how zero-shot and few-shot prompting differ in the number of examples provided to the model, highlighting their simplicity, common use cases, and limitations related to model capability and context window size. The note then introduces chain-of-thought prompting, which encourages step-by-step reasoning to improve performance on complex tasks, along with its benefits, typical applications, and trade-offs such as higher token usage and potential error propagation. Overall, the text emphasizes how these prompting methods can improve response quality, reveal model limitations, and be combined or extended (e.g., with ReAct or advanced CoT variants) to handle more sophisticated reasoning tasks.

## References


1. <a herf="https://www.promptingguide.ai/techniques/zeroshot">Zero-shot prompting</a>
2. <a href="https://www.promptingguide.ai/techniques/fewshot">Few-shot prompting</a>
3. <a href="https://www.promptingguide.ai/techniques/cot">Chain-of-thought prompting</a>
4. <a href="https://www.promptingguide.ai/techniques/react">ReAct</a>
5. Shivendra Srivastava and Naresh Vurukonda, _Prompt Engineering in Action_, Manning Publications.

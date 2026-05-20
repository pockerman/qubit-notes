# qubit-note: LLM Series | RAG or Fine Tuning?

## Overview

Both fine tuning and <a href="2025-05-03-retrieval-augmented-generation.md">Retrieval Augmented Generation (RAG)</a> are approaches we can use in order
to improve the perfromance of an LLM. However, there are scenarios where one is better than the other.
In this qubit note, we will discuss some guidelines when to use one over the other.


## RAG or Fine Tuning?

Fine tuning is the process of further training a pre-trained LLM on a typically smaller,
specific dataset to adapt it for a particular task. The model’s weights are then adjusted
based on our own data, making it more tailored to our organization’s unique needs.
With fine tuning the training dataset is typically smaller, task-specific and labelled. Fine-tuning essentially makes the model a specialist rather than a generalist.

On the other hand, Retrieval Augmented Generation or RAG is a framework that allows us to enhance the capabilities of an LLM.
This is done by allowing the model to retrieve relevant information associated to the user query before shaping its response.
Thus  at a high level, when using RAG apart from the LLM, we also have a retriever component.

Naturally the question arises which approach should one use. The answer is, as in many things in software engineering and modeling, it depends
For both approaches there are consideration we need to take into account before deciding in favour or against any of the two.

Typically RAG is quite useful when we want to use up-to-date data with the model that was not used during the training of the model. 
In terms of training costs RAG achieves this in a rather less expensive way
as we don't need to train or label any data. RAG however, is not cost free as usually we need to maintain a database where we fetch data
from in order to inject this into the model. Hence per model call the RAG approach involves at least one more call to search in the database.
RAG is not useful if the model is underperforming with the given task it will typically inject more context into a model that already underperforms.

Apart from costs we also need to be able to appreciate the complexity of the task that is presented to a model.
RAG is also not very useful here and we should prefer fine tuning instead. Alongside with the increased training cost that
fine tuning appraoches present, we need to consider that it requires a higher degree of machine learning engineering expertise; e.g. training process optimization
distributed training e.t.c. Due to labelling in fine tuning, it may be easier for us to better understand why the model produced a certain output whilst with
RAG this may not be the case.

Although above we discussed RAG vs fine tuning mode, this need not be the case and combining both approaches may be the solution in improving the performance of our model.
Recall that we discussed an number of prompting methodologies see e.g. <a href="2025-04-29-Prompt-Engineering-Part-1.md">Prompt Engineering Part 1</a> and  <a href="2026-01-12-Prompt-Engineering-Part-2.md">Prompt Engineering Part 2</a> 

So overall, we have prompt engineering, fine tuning and RAG so the natural question is when to use each?
Below is a practical decision framework from [1].

We start with prompt testing.  Can we get acceptable results by just changing your prompt?
We can do the following test [1]:

Write a better prompt and run 10 real examples through it. If 8 out of 10 responses meet your quality bar, stop here. You're done. Prompting takes minutes and costs nothing.

Obviously, the more examples we use the better understanding we get whether prompt engineering will solve our problems.

The prompting test failed. Next question: Does your problem involve facts that change frequently?

If information changes daily, weekly, or even monthly, you need RAG. Fine-tuning locks in knowledge at training time. RAG fetches fresh data with every query.

For example, imagine that your customer support bot needs to know current inventory levels. Today you have 50 blue shirts. Tomorrow you have zero. With RAG, the bot checks your database in real-time and gives accurate availability. With fine-tuning, the bot would confidently tell customers you have 50 blue shirts forever, even when you're sold out.

**The consistency challenge**

Your data is stable, but prompting still isn't working. Final question: Do you need the model to consistently follow a specific style or format, or use specialized domain knowledge?

This is where fine-tuning excels. When you need unwavering consistency across thousands of interactions, when domain expertise is critical, or when specific formats must be followed perfectly every time, fine-tuning is your answer.

For example, suppose your legal document assistant must cite sources in Bluebook format and never invent case law. You've tried detailed prompts, but after long conversations, the model forgets the format or hallucinates cases. After fine-tuning on 500 examples of correct citations, the model maintains perfect format even in 50-turn conversations. It never invents a case because it learned from your examples that uncertain answers should trigger "I cannot find that case in my training data."


## Summary

In this qubit note I provided some guideline on how to choose  fine-tuning or RAG in order to improve large language model (LLM) performance. Specifically, fine-tuning involves retraining a pre-trained model on a smaller, labeled, and task-specific dataset, making it well-suited for cases requiring model adaptation to unique tasks but with higher costs and technical expertise requirements. RAG, on the other hand, enhances an LLM by retrieving relevant external information at query time, making it more cost-effective and ideal for incorporating up-to-date data without retraining. However, RAG is less useful when the model fundamentally underperforms at a task or when task complexity demands deeper model adjustments. Both approaches have trade-offs in cost, complexity, and interpretability.

## References

1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications


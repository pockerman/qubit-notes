# qubit-note: RAG or Fine Tuning?

## Overview

Both fine tuning and <a href="2025-05-03-retrieval-augmented-generation.md">quibit-note: Retrieval Augmented Generation (RAG)</a> are appraoces we can use in order
to improve the perfromance of an LLM. However, there are scenarios where one is better than the other.
In this qubit note, I will provide some guidelines when to use one over the other.

**keywords** RAG, Fine-Tuning, AI-engineering, large-language-models

## RAG or Fine Tuning?

Fine tuning is the process of further training a pre-trained LLM on a typically smaller,
specific dataset to adapt it for a particular task. The model’s weights are then adjusted
based on our own data, making it more tailored to our organization’s unique needs.
One could argue that the fine tuning process is similar to pre-training, the difference is in the training
dataset, which is typically smaller, task-specific and labelled.

On the other hand, Retrieval Augmented Generation or RAG is a framework that allows us to enhance the capabilities of an LLM.
This is done by allowing the model to retrieve relevant information associated to the user query before shaping its response.
Thus  at a high level, when using RAG apart from the LLM, we also have a retriever component.

Naturally the question arises which approach should one use. The answer is, as in many things in software engineering and modeling, it depends
For both approaches there are consideration we need to take into account before deciding in favour or against any of the two.

Typically RAG is quite useful when we want to use up-to-date data with are model that was not used during the training of the model. 
Both RAG and fine tuning can help us decrease however in terms of training costs RAG achieves this is a rather less expensive way
as we don't need to train or label any data. RAG however, is not cost free as usually we need to maintain a database where we fetch data
from in order to inject this into the model. Hence per model call the RAG approach involves at least one more call to search in the database.
RAG is not useful if the model is underperforming with the given task it will typically inject more context into a model that already underperforms.

Apart from costs we also need to be able to approeciate the complexity of the task that is presented to a model.
RAG is also not very useful here and we should prefer fine tuning instead. Alongside with the increased training cost that
fine tuning appraoches present, we need to consider that it requires a higher degree of machine learning engineering expertise; e.g. training process optimization
distributed training e.t.c. Due to labelling in fine tuning, it may be easier for us to bettern understand why the model produced a certain output whilst with
RAG this may not be the case.


Although above I present RAG vs fine tuning mode. This need not be the case and combining both approaches may be the solution in improving the performance of our model.


## Summary

In this qubit note I provided some guideline on how to choose  fine-tuning or RAG in order to improve large language model (LLM) performance. Specifically, fine-tuning involves retraining a pre-trained model on a smaller, labeled, and task-specific dataset, making it well-suited for cases requiring model adaptation to unique tasks but with higher costs and technical expertise requirements. RAG, on the other hand, enhances an LLM by retrieving relevant external information at query time, making it more cost-effective and ideal for incorporating up-to-date data without retraining. However, RAG is less useful when the model fundamentally underperforms at a task or when task complexity demands deeper model adjustments. Both approaches have trade-offs in cost, complexity, and interpretability.

## References
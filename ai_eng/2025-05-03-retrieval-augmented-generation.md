# quibit-note: Retrieval Augmented Generation (RAG)

## Overview

Large language models (LLMs) are changing the way we search the internet or how we
develop software amongst other things. Although LLMs  are powerful models, they have limitations.
One of these limitations is that the quality of their response drops rather drastically when they are 
asked a question outside of the time window they were trained on or when asked domain specific questions.

In this note I want to discuss one approach that we can use in order to update the model
with information that it was not trained on. 
Specifically, I want to discuss <a href="https://en.wikipedia.org/wiki/Retrieval-augmented_generation">retrieval augmented generation</a> or RAG; its main componets and
the typical workflow.

**keywords** RAG, AI-engineering, large-language-models, LLM, retrieval-augmented-generation, 


## Retrieval augmented generation 


LLMs are indeed powerful models that have the potential to  change the way we do a lot of things.
Despite their capabilities, they have limitations.
One of these limitations is that the quality of their response drops rather drastically when they are 
asked question outside of the time window they were trained on or when asked domain specific questions.
In these scenarios, the model will provide a response, unless is instructed not to, but in most cases
this response is made up and does not correspond to any real fact. In such a case we say that the model hallucinated.
One way to improve the reponses of an LLM in such scenarios is to utilize RAG.

Retrieval augmented generation is a framework that allows us to enhance the capabilities of an LLM.
This is done by allowing the model to retrieve relevant information associated to the user query before shaping its response.
Thus  at a high level, when using RAG apart from the LLM, we also have a retriever component.

The job of the retriever is to act similar to a search engine. It searches any external data sources, 
typically a <a href="https://en.wikipedia.org/wiki/Vector_database">vector database</a>, in real-time.
Its job is to ensure that the generator has up-to-date information that is relevant to user query.

Let's discuss the typical RAG workflow

### The RAG pipeline

The typical RAG pipeline consists of the following steps [1]:

- Pre-Retrieval 
- Retrieval, 
- Post-Retrieval phases. 

As its name propbaly implies, during the pre-retrieval step we collect the data that we want to use in order to enhance our model.
This is an offline step whereby we clean the data, create embeddings, index it and store in a database. The most common type
of databases used in a RAG pipeline are <a href="https://en.wikipedia.org/wiki/Vector_database">vector databases</a>. 
Although nothing is stopping us from having this step performed during the user query i.e. online, given the amount of work required it would slow things down
considerably.

During the retrieval stage, the system deals with the user query. A RAG system may not use the user prompt in its original form.
Instead various optimizations may be applied before sending it to the model. This prompt tranformation aims at enhancing the searches; reduce irrelevant results, enhance retrieval performance [1]. 

The last step in a RAG pipeline is  post-retrieval. In this step, the retrieved documents are somehow refined before we pass these into the LLM model in order to generate a response.
Such refinements include, see [1], prompt compression and priority re-ranking


GraphRAG is a similar approach to RAG, however it is using knowledge graphs to back up the RAG pipeline. GraphRAG has been reported to produce
better accuracy than the usual RAG [3]. A similar concept to RAG is CAG or Cached Augmented Generation [4].


## Summary

LLMs are powerful but limited by outdated training data and domain gaps, often leading to hallucinations when asked questions outside their knowledge scope. RAG addresses this by combining an LLM with a retriever that pulls relevant, up-to-date information, typically from a vector database, before the model generates a response. The RAG workflow has three main phases: pre-retrieval (data preparation, embedding, and indexing), retrieval (query handling and optimization), and post-retrieval (refining and re-ranking documents before passing them to the model). Variants like GraphRAG, which integrates knowledge graphs, and Cached Augmented Generation (CAG) further extend the approach, offering improvements in accuracy and efficiency.

<a href="2025-08-21-indexing-for-rag.md">qubit-note: Indexing for RAG</a> discusses further how to do indexing for RAG-based applications.
<a href="2025-08-28-evaluate-RAG-based-system.md">qubit-note: Evaluate a RAG-based System</a> provides some hints how to evaluate a RAG-based system.

## References

1. Shivendra Srivastava and Naresh Vurukonda _Prompt Engineering in Action_, Manning Publications.
2. <a href="https://neo4j.com/labs/genai-ecosystem/">GenAI Ecosystem</a>
3. <a href="https://www.youtube.com/watch?v=knDDGYHnnSI">GraphRAG: The Marriage of Knowledge Graphs and RAG: Emil Eifrem</a>
4. <a href="https://www.youtube.com/watch?v=HdafI0t3sEY">RAG vs. CAG: Solving Knowledge Gaps in AI Models</a>

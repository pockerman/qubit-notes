# quibit-note: Retrieval Augmented Generation (RAG)

## Overview

Large language models (LLMs) are changing the way we search the internet or how we do
develop software amongst other things. Although LLMs  are powerful models, they have limitations.
One of these limitations is that the quality of their response drops rather drastically when they are 
asked question outside of the time window they were trained on or when asked domain specific questions.

In this note I want to discuss one approach that we can use in order to update the model
with information that it was not trained on. 
Specifically, I want to discuss <a href="https://en.wikipedia.org/wiki/Retrieval-augmented_generation">retrieval augmented generation</a> or RAG; its main componets and
the typical workflow.

**keywords** large-language-models, LLM, retrieval-augmented-generation, RAG


## Retrieval augmented generation 


LLMs are indeed powerful models that have the potential to  change the way we do a lot of things.
Although LLMs  are powerful models, they have limitations.
One of these limitations is that the quality of their response drops rather drastically when they are 
asked question outside of the time window they were trained on or when asked domain specific questions.
In these scenarios the model will provide a response unless is instructed not to, but in most cases
this response is made up and does not correspond to any real fact. In such a case we say that the model hallucinated.
One way to improve the reponses of an LLM in such scenarios is to utilize RAG.

Retrieval augmented generation is a framework that allows us to enhance the capabilities of an LLM.
This is down by allowing the model to retrieve relevant to user user query information before shaping its response.
Thus  at a high level, when using RAG apart from the LLM, we also have a retriever component.

The job of the retriever is to act similar to a search engine. It searches external data sources, 
typically a <a href="https://en.wikipedia.org/wiki/Vector_database">vector database</a>, in real-time.
Its job is to ensure that the generator has up-to-date inofrmation that is relevant to user query.

Let's now turn attention to the RAG workflow

### The RAG pipeline

The typical RAG pipeline consists of the following steps [1]:

The RAG workflow consists of 
- Pre-Retrieval 
- Retrieval, 
- Post-Retrieval phases. 

As its name propbaly implies, during the pre-retrieval step we collect the data that we want to use in order to enhance out model.
This is an offline step whereby we clean the data, create embeddings, index it and store in a database. The most common type
of databases used in a RAG pipeline are <a href="https://en.wikipedia.org/wiki/Vector_database">vector databases</a>. 
Although nothins stopping us to have this step performed during the user query i.e. online, given the amount of work required it would slow things down
considerably.

During the retrieval stage, the system deals with the user query. A RAG system may not use the user prompt in its original form.
Instead various optimization may be applied before sending it to the model. This prompt tranformation aims at enhancing the searches; reduce irrelevant results, enhance retrieval performance [1]. 

The last step in a RAG pipeline is  post-retrieval. In this step, the retrieved documents are somehow refined before we pass these into the LLM model in order to generate a response.
Such refinements include, see [1], prompt compression and priority re-ranking


GraphRAG is a similar approach to RAG, however it is using knowledge graphs to back up the RAG pipeline. GraphRAG has been reported to produce
better accuracy than the usual RAG [3]. A similar concept to RAG is CAG or Cached Augmented Generation [4].




## References

1. Shivendra Srivastava and Naresh Vurukonda _Prompt Engineering in Action_, Manning Publications.
2. <a href="https://neo4j.com/labs/genai-ecosystem/">GenAI Ecosystem</a>
3. <a href="https://www.youtube.com/watch?v=knDDGYHnnSI">GraphRAG: The Marriage of Knowledge Graphs and RAG: Emil Eifrem</a>
4. <a href="https://www.youtube.com/watch?v=HdafI0t3sEY">RAG vs. CAG: Solving Knowledge Gaps in AI Models</a>
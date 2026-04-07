# qubit-note: Indexing for RAG

## Overview

Qubit note <a href="2025-05-03-retrieval-augmented-generation.md">quibit-note: Retrieval Augmented Generation (RAG)</a> discussed the RAG pattern
and its basic usage. However often this is not enough. Many times, although relevant data exist in the database, we may notice inaccurate answers.
Most of the times we can attribute these inacurrasies to one or to any combination of the following inefficiencies [1]:

- Inefficient text indexing
- Inefficient use of metadata
- Inefficient queries

Text indexing in a vector database is very important as it allows us to efficiently have access to the correct documents.
In this qubit note I discuss how to address inefficient text indexing.

**keywords** RAG, RAG-indexing, AI-engineering

## Indexing for RAG

With RAG-based applications, the retrieval accuracy plays a key role. Although the indexing that
we use during ingestion depends heavily on the application at hand, relying only on basic indexing
can reduce retrieval performance. This is true even if the query is rather clear [1].

We know from <a href="2025-05-03-retrieval-augmented-generation.md">quibit-note: Retrieval Augmented Generation (RAG)</a>
that text indexing basically refers to how we create the embeddings for our text i.e. the embedding model we use.
In addition, the size of the chunk we use also plays a role. Typically, small chucks may perform better for rather
precise questions. However, given that they contain less context, they are usually ineffective for broader queries.
On the other hand, larger chunks may provide broader spectrum but fail for specific questions [1].
Unfortunately, there is no rule to follow in this case and depends on the application in order to establish the right balance betweent the two.

----
**Remark: Sentence Expansion**

The sentence expansion method is a natural language processing (NLP) technique used to enrich a sentence by adding more descriptive or contextual details while preserving its original meaning. It involves extending the sentence with additional words, phrases, or clauses—such as adjectives, adverbs, examples, or explanations in order to make it more informative, engaging, or specific. This method is often applied in tasks like text generation, content rewriting, and improving AI-driven responses. It helps provide better clarity and depth but must be done carefully to avoid altering the intended message or introducing ambiguity

----

Given this disparity, we can use additional embeddings based on distinct chunk features, therefore making
each text chunk more adaptable and searchable.

Let's get a bit more detailed into this subject. 

Generating a high quality answers depends on the relevance and accuracy of the text retrieved from the database.
The quality of the retrieval depends on factors such as [1]:

- The strategy we used for splitting
- The overall embedding approach we use

I have already hinted about the splitting strategy; the granularity of the chunks will affect the retrieval accuracy.
In addition, the overall embedding approach we use affects the indexing and therefore the retrieval of the documents.
We typically use two types of document splitting [1]:

- Splitting by document hierarchy
- Splitting by size

The first approach is a text processing technique used to divide large documents into smaller, structured segments based on their inherent hierarchical organization (e.g., chapters, sections, subsections, paragraphs). Instead of splitting text arbitrarily by length or tokens, this method respects the document's logical structure, ensuring that each chunk retains meaningful context and relationships between sections. This is particularly useful in applications like retrieval-augmented generation (RAG), search indexing, and document summarization, as it helps preserve semantic continuity and improves relevance during retrieval or analysis.

The second approach is a text chunking method where documents are divided into fixed-size segments based on a predetermined limit—such as a set number of characters, words, or tokens—without considering the document's logical or hierarchical structure. Each chunk is created sequentially, and if a section exceeds the specified size, it is further broken down until all pieces conform to the size constraint. This method is simple, fast, and widely used in retrieval-augmented generation (RAG), embeddings, and search indexing because it ensures predictable chunk sizes for processing and storage. However, it can disrupt semantic flow by splitting sentences or paragraphs arbitrarily, leading to potential context loss between chunks.

When selecting which approach to use bear in mind both the document type as well as the search you want perform.

## Summary

In this qubit note we discussed the importance of efficient text indexing for improving retrieval accuracy in Retrieval-Augmented Generation (RAG) systems.
Inaccurate answers often stem from poor indexing, improper use of metadata, or suboptimal queries. Indexing quality depends on factors like embedding models, chunking strategy, and chunk size—where smaller chunks may benefit precise queries, and larger ones offer broader context but may reduce specificity. Two main chunking strategies are highlighted: splitting by document hierarchy, which preserves logical structure for better semantic continuity, and splitting by absolute size, which ensures predictable processing but may fragment context. Selecting the right method depends on both the document type and the intended retrieval use case. Additionally, advanced indexing techniques involve generating multiple embeddings for each chunk, enhancing searchability.

## References

1. Roberto Infante, _AI Agents and Applications_, Manning Publications
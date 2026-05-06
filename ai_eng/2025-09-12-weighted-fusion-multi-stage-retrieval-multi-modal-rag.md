# qubit-note: Document Fusion & Multi-stage Retrieval


## Overview

<a href="2025-08-21-indexing-for-rag.md">qubit-note: Indexing for RAG</a> discussed how to imporve indexing for RAG systems. However, depending on the application, this may not be enough.
In addition, applications typically involve more than one modalities in terms of data e.g. text, images and video. In this qubit note I want to discuss a 
hybrid approach for improving retrieval. The approach combines weighted fusion and multi-stage retrieval.

A simple implementation can be found at: <a href="https://github.com/pockerman/multi_modal_rag/tree/main">Document fusion & multi-step retrieval of multi-modal RAG</a>


**keywords** weighted-fusion, multi-stage-retrieval, RAG, AI-engineering, large-language-models, LLM, retrieval-augmented-generation

## Document fusion & multi-stage retrieval for multi-modal RAG

Embedding models map documents to vectors thus creating a semantic space where similar meanings cluster together. 
This ia a powerful approach known as dense retrieval [4]. It has however limitations when deployed in real-world applications.
Let's consider the  scenario whereby the user asks a question and while the answer is contained within the documnent corpus we have
indexed, the retrieved documents do not contain it. How this can be possible? The problem lies with how dense retrieval works and there
are three key reasons why [4]:

- Semantic drift
- Recall limitations
- Domain gaps

The bottom line is that in real-world retrieval we need more advanced techniques than simply taking the top-k nearest vectors [4].
Below are some approaches we can use to imporve the information retrieval.

### Hybrid retrieval

The first line of attack is to combine two complementary approaches [4]:

- Dense retrievals i.e. search based on embeddings
- Sparse retrieval i.e. search based on keywords like the <a href="https://www.geeksforgeeks.org/nlp/what-is-bm25-best-matching-25-algorithm/">Best Matching 25 Algorithm</a>

---
**Remark**

BM25 is the most common sparse retrieval algorithm, but alternatives include <a href="https://www.geeksforgeeks.org/machine-learning/understanding-tf-idf-term-frequency-inverse-document-frequency/">TF-IDF</a> i.e. Term Frequency-Inverse Document Frequency and learned sparse methods like <a href="https://www.pinecone.io/learn/splade/">SPLADE</a>. 

---

In such a hybrid approach, the dense model recognizes the conceptual relationship between the various terms whilst the sparse retrieval
prioritizes documents containing the exact terms [4]. Hence, a typical hybrid retrieval system will work as follows

- Execute dense retrieval to find semantically related documents
- Execute sparse search to find keyword matching documents
- Combine both result sets and remove duplicates
- Apply a reranking step

Such an approach is used in production systems as it improves recall by ensuring the right documents are somewhere in the results set.


### Multi-stage retrieval

Hybrid redtrieval improves the recall however in a retrieval application we are also interested in precision.

---
**Remark: Precision**

Precision in the context of document retrieval measures how many of the retrieved documents are actually relevant. 
It answers the question: _Are the most relevant documents at the top of my results?_ [4].

---

Multi-stage retrieval uses a filtering pipeline.  We split the task of finding and ranking documents into states. Specifically, see e.g. [4],

1. Broad retrieval: Find documents that are protentially relevant. The aim here is the fetch as many relevant documents as possible.
2. Progressive filtering: apply selective filetering to narrow the documents from stage 1
3. Precision Reranking (Ranking): Use sophisticated models to sort what remains

Broad retrieval is typically a hybrid retrieval i.e. dense and sparse search as we saw in the previous section. Traditional emebedding models e.g. OpenAI embeddings, are bi-encoders meaning the encode both the query and each documents into separate vectors and then compare these vectors using for example cosine similarity. One problem with such an approach is that the query and and documents never interact directly [4].


A <a href="https://www.sbert.net/examples/cross_encoder/applications/README.html">cross-encoder</a> takes a different approach [4]:

1. They accept both the query and document as a single input pair
2. Process this pair through all layers of the transformer model
3. Output a single relevance score

This allows the model to capture complex interactions between query and document terms. A cross-encoder can understand, for example, that "work accommodation" in the query is highly relevant to "ADA" in the document, even if these specific terms don't co-occur. Thus, multi-stage retrieval is a core component of any advanced RAG architecture, designed to enhance the quality and relevance of retrieved information.


### Document fusion

We have seen that hybrid search involves two searches a dense search based on embeddings and sparse search based on keywords. 
In addition, we may have indexed our DB in a such a way that both small and large chunks are used, see e.g.  <a href="2025-08-21-indexing-for-rag.md">qubit-note: Indexing for RAG</a>.

In order to answer the user query not all documents are of equal importance. And this is the responsibility of stage 2 Progressive filtering; to filter out irrelevant or less relevant documents.
Furthermore, we can use document fusion i.e. somehow fuse the documents together. Two popular approaches include weighted fusion and reciprocal rank fusion or RRF. 
These appraoches will typically compute a score:

**Weighted fusion** 

For two documents, weighted fusion would give a score:

$$fused_{score} = w_1 * doc^{1}_{score} + w_2 * doc^{2}_{score} $$

**Reciprocal rank fusion**

$$RRF_{score} = \sum_i (1 / (k + rank_i))$$

where $k$ is a smoothing constant to control the weight of existing ranks. Note that we are taking a sum as we assume that a document has a large and small chunks.
Similarly, we can assume that an image document is associated with a text document i.e. a caption or image description.

Overall, document fusion allows us to score the retrieved documents in a different way than simply relying on distance scores.


Colllectively, multi-stage retrieval combined with document fusion could work as follows

1. Indexing for each document produce one or more representations e.g. embeddings, metadata, summaries. 
2. Multi-stage retrieval
   1. Broad retrieval:  Find documents that are protentially relevant. The aim here is the fetch as many relevant documents as possible.
   2. Filter: Remove irrelevant documents
   3. Fuse: Merge candidate sets, normalize scores, compute fused score (weighted) 
   4. Re-rank: Run cross-modal re-ranker (e.g. cross-encoder that takes query + documents) over top $N$ fused candidates.
3. Pass the the top $M$ candidates to the model.



## Summary

This note explains how to improve retrieval in RAG systems by combining hybrid retrieval, multi-stage retrieval, and document fusion. While dense retrieval using embeddings is powerful, it suffers from issues like semantic drift, recall limitations, and domain gaps, so it is often complemented with sparse methods such as keyword-based search (e.g., BM25) to improve recall. A multi-stage retrieval pipeline then refines results by first retrieving a broad set of candidates, filtering them, and finally reranking them using more sophisticated models like cross-encoders, which better capture query-document interactions. Document fusion techniques, such as weighted fusion and reciprocal rank fusion, further enhance ranking by combining scores from multiple sources or representations (e.g., text, images, different chunk sizes). Together, these techniques create a more robust retrieval pipeline that balances recall and precision, ultimately improving the quality of information passed to the language model.


## References

1. <a href="https://huyenchip.com/2023/10/10/multimodal.html">Multimodality and Large Multimodal Models (LMMs)</a> 
2. <a href="https://www.assembled.com/blog/better-rag-results-with-reciprocal-rank-fusion-and-hybrid-search">Better RAG results with Reciprocal Rank Fusion and Hybrid Search</a>
3. <a href="https://www.sbert.net/examples/cross_encoder/applications/README.html">cross-encoders</a>
4. Rush Shahani _Building Reliable AI Systems_, Manning Publications 
5. <a href="https://www.geeksforgeeks.org/nlp/what-is-bm25-best-matching-25-algorithm/">What is BM25 (Best Matching 25) Algorithm</a>


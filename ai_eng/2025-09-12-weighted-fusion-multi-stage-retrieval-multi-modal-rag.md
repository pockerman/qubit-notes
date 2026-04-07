# qubit-note: Document Fusion & Multi-stage Retrieval for Multi-modal RAG


## Overview

<a href="2025-08-21-indexing-for-rag.md">qubit-note: Indexing for RAG</a> discussed how to imporve indexing for RAG systems. However, depending on the application, this may not be enough.
In addition, applications typically involve more than one modalities in terms of data e.g. text, images and video. In this qubit note I want to discuss a 
hybrid approach for improving retrieval. The approach combines weighted fusion and multi-stage retrieval.

A simple implementation can be found at: <a href="https://github.com/pockerman/multi_modal_rag/tree/main">Document fusion & multi-step retrieval of multi-modal RAG</a>


**keywords** weighted-fusion, multi-stage-retrieval, RAG, AI-engineering, large-language-models, LLM, retrieval-augmented-generation

## Document fusion & multi-stage retrieval for multi-modal RAG

The approach we will discuss in this note consists of two main components; document fusion and multi-state retrieval
Document fusion is a technique used to combine results from different modalities or retrieval sources to improve the overall performance of a multimodal RAG system.
Two approaches for document fusion are weighted fusion and reciprocal rank fusion, or RRF.
In addition, multi-stage retrieval is a core component of any advanced RAG architecture, designed to enhance the quality and relevance of retrieved information.

### Document fusion

Often vector search is not enough. Indeed the performance of the search depends on indexing as well as the user query. Let's assume that
we have indexed our DB in a such a way that both small and large chunks are used, see e.g.  <a href="2025-08-21-indexing-for-rag.md">qubit-note: Indexing for RAG</a>.
We send the user query in the DB and now we want to somehow combine the results. Document fusion is a technique that allows us to do exactly this. Two commonly used
approaches are weighted fusion and reciprocal rank fusion. 

For two documents, weighted fusion would give a score:

$$fused_{score} = w_1 * doc^{1}_{score} + w_2 * doc^{2}_{score} $$

Reciprocal rank fusion would give s document score as

$$RRF_{score} = \sum_i (1 / (k + rank_i))$$

where $k$ is a smoothing constant to control the weight of existing ranks. Note that we are taking a sum as we assume that a document has a large and small chunks.
Similarly, we can assume that an image document is associated with a text document i.e. a caption or image description.


### Multi-stage retrieval

Document fusion allows us to score the retrieved documents in a different way than simply relying on distance scores. Multi-stage retrieval involves a number 
of steps aiming at refining the retreived results at every step. The first step involves a broad retrieval. The second step involves the use of a <a href="https://www.sbert.net/examples/cross_encoder/applications/README.html">cross-encoder</a> or a visual-language model to compute fine-grained similarities between the user query and the retrieved documents.

In our case, the results from the broad retrieval can be combined using a fusion approach discussed above. Then we use the cross-encoder to reranke the
fused documents.

Collectively a hybrid document fusion and multi-stage retrival could work as follows:


1. Indexing: For each image produce one or more representations (embeddings, captions, metadata). Two collections are used one for the images and one for the description of the image
2. Multi-stage retrieval. 
   1. Retrieve: Get the top $K$ images and image descriptions i.e two DB queries
   2. Fuse: Merge candidate sets, normalize scores, compute fused score (weighted) 
   3. Re-rank: Run cross-modal re-ranker (e.g. cross-encoder that takes query + image) over top $N$ fused candidates; final ranking from re-rank.
3. Generate: top $M$ candidates (images + captions + metadata) into context for the generator. If the generator is text-only, supply captions & metadata; if multi-modal generator, feed images directly.


## Summary

This qubit note introduces a hybrid approach for improving retrieval in multi-modal retrieval-augmented generation (RAG) systems by combining document fusion and multi-stage retrieval. Document fusion enhances performance by merging results from different modalities (e.g., text, images, metadata) using techniques such as weighted fusion or reciprocal rank fusion. Multi-stage retrieval refines search results in successive steps: starting with broad retrieval, then applying fusion, and finally re-ranking with more precise models like cross-encoders or vision-language models. Together, these methods enable more accurate, context-aware retrieval across modalities, ultimately improving the quality of information fed into downstream generators.

## References

1. <a href="https://huyenchip.com/2023/10/10/multimodal.html">Multimodality and Large Multimodal Models (LMMs)</a> 
2. <a href="https://www.assembled.com/blog/better-rag-results-with-reciprocal-rank-fusion-and-hybrid-search">Better RAG results with Reciprocal Rank Fusion and Hybrid Search</a>
3. <a href="https://www.sbert.net/examples/cross_encoder/applications/README.html">cross-encoders</a>


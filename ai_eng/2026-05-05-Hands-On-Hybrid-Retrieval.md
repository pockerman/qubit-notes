# qubit-note: Hands On | Hybrid Retrieval

## Overview 

This qubit note is a hands-on session for hybrid retrieval. Specifically, we will create a database with documents about a topic specifically the
HTTP protocol. We will use ChromaDB for stroing the documents. We will then use BM25 and ```SentenceTransformer```. 


```
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
 
documents = [
    "California employees must give a 30-day notice before resignation.",
    "All new hires are eligible for health insurance after 90 days.",
    "Termination for cause may lead to loss of severance benefits.",
    "Employees may request remote work accommodations under ADA.",
    "Maternity and adoption leave are fully paid for 12 weeks."
]
 
tokenized_corpus = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_corpus)
 
dense_model = SentenceTransformer("intfloat/e5-base")
dense_embeddings = dense_model.encode(documents, normalize_embeddings=True)
 
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def hybrid_retrieve(query, top_k=5, bm25_k=10, dense_k=10):
    """
    Hybrid retrieval with cross-encoder reranking
    
    Args:
        query: User question/query text
        top_k: Number of final results to return
        bm25_k: Number of results to fetch from BM25
        dense_k: Number of results to fetch from dense retrieval
        
    Returns:
        List of (document, relevance_score) tuples
    """
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_indices = np.argsort(bm25_scores)[-bm25_k:][::-1]
    bm25_hits = [documents[i] for i in bm25_indices]
    
    query_embedding = dense_model.encode(query, normalize_embeddings=True)
    cosine_scores = cosine_similarity([query_embedding], dense_embeddings)[0]
    dense_indices = np.argsort(cosine_scores)[-dense_k:][::-1]
    dense_hits = [documents[i] for i in dense_indices]
    
    candidates = []
    seen = set()
    for doc in bm25_hits + dense_hits:
        if doc not in seen:
            candidates.append(doc)
            seen.add(doc)
    
    if len(candidates) > 1:
        pairs = [[query, doc] for doc in candidates]
        scores = cross_encoder.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
    else:
        return [(doc, 1.0) for doc in candidates][:top_k]


```


This function implements our complete multi-stage retrieval pipeline:

BM25 Retrieval: We first tokenize the query and use BM25 to calculate relevance scores based on keyword matching. Then we get the top-k documents by these scores.
Dense Retrieval: We encode the query into a vector and calculate its cosine similarity with all document embeddings. Then we get the top-k documents by semantic similarity.
Combination with Deduplication: We merge the results from both methods, being careful to avoid duplicates. The order matters here - we prioritize documents that appear earlier in the combined list.
Cross-Encoder Reranking: Finally, we use a cross-encoder model to score each (query, document) pair more precisely and sort the results by these scores.


```
def test_retriever():
    queries = [
        "How much notice do I need before quitting in California?",
        "Do we have paid adoption leave?",
        "What happens if someone gets fired for misconduct?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = hybrid_retrieve(query, top_k=2)
        print("\nTop Results:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"{i}. [{score:.3f}] {doc}")
        print("-" * 50)
 
test_retriever()

```

To appreciate the value of our hybrid approach, let's examine what would happen if we used only one method:

BM25 alone might miss the first result for "quitting" because it doesn't contain that exact word
Dense retrieval alone might retrieve conceptually related but less helpful documents
Without cross-encoder reranking, we might get the right documents but in the wrong order


## Summary

## References

1.  Rush Shahani _Building Reliable AI Systems_, Manning Publications 
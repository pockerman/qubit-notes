# qubit-note: Evaluate a RAG-based System

## Overview

<a href="2025-05-03-retrieval-augmented-generation.md">quibit-note: Retrieval Augmented Generation (RAG)</a> discussed the concept of RAG, whilst 
<a href="2025-08-21-indexing-for-rag.md">qubit-note: Indexing for RAG</a> discussed how to imporve indexing for RAG systems. In this note I want to
discuss some ideas on how to evaluate a RAG-based system.

**keywords** RAG, AI-engineering, large-language-models, LLM, retrieval-augmented-generation

## Evaluate a RAG-based system

RAG based systems typically involve a number of components and this is what makes their evaluation rather involved. Let's first discuss how to evaluate the 
retrieval step.

### Evaluate the retrieval step

The retrieval step involves embeding the user's query and using the resulting vector to search for relevant documents in our database.
Some metrics we can use for evaluating the retreived documents are:

- Precision@k: How many of the top k retrieved documents are relevant?
- Recall@k: How many of all relevant documents were retrieved in the top k?
- <a href="https://en.wikipedia.org/wiki/Mean_reciprocal_rank">Mean Reciprocal Rank</a> or MRR: Measures the rank position of the first relevant document.
- <a href="https://www.evidentlyai.com/ranking-metrics/ndcg-metric">Normalized Discounted Cumulative Gain</a> or NDCG: Weighs relevance based on position in the ranked list.

Let's discuss these metrics. 

Precision@k and Recall@k are common metrics that help evaluate the performance of ranking algorithms. 
The approach is similar to the metrics used in classification models. For more information see [3]

MRR is a metric used to evaluate systems that return ranked lists of results (like retrieval-based or search systems). It measures how well the system ranks the first relevant item for a given query.
The MRR metric is defined as, see [1]:

$$MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{rank_i}$$

where $rank_i$ refers to the rank position of the first relevant document for the i-th query and $|Q|$ is the number of queries.

The NDCG metric evaluates the quality of recommendation and information retrieval systems. 
Specifically, NDCG helps measure a machine learning algorithm's ability to sort items based on relevance [2]. 


### Evalaute generation quality

After retrieving the relevant documents, the system should generate a response. This is another aspect 
that we need to evaluate. Some metrics we can use here are:

- Faithfulness/Groundedness: Does the answer strictly rely on retrieved documents? (No hallucinations)
- Relevance: Is the generated text answering the query?
- Factuality: Are facts accurate according to trusted sources?

Evaluating generation quality may not be straightforward. Particularly, if we don't have reference answers.
If however such answers exist, we can use metrics such as <a href="https://en.wikipedia.org/wiki/BLEU">BLEU</a>, <a href="https://en.wikipedia.org/wiki/ROUGE_(metric)">ROUGE</a>, or 
<a href="https://huggingface.co/spaces/evaluate-metric/bertscore">BERTScore</a>. Another approach can be to use another model to rate factuality and faithfulness i.e. LLM-as-a-judge.
Human evaluation can also be employed i.e. domain experts score the model's output. However, this approach may not be easy to automate.

Many times task specific metrics may be more appropriate. For example for question-answering tasks metrics like F1 or ExactMatch may be more useful.
In addition, comparing RAG output with some sort of baseline e.g. the output of an older system may be of use.

### Evaluate system performance

We need also to consider the overall system performance. Here things are probably more streamilined with general system evaluation metrics such as latency, cost and availability.
These metrics depend heavily on the system at hand and which of these metrics we want to prioritize/improve.


## Summary

This note outlines approaches to evaluating Retrieval-Augmented Generation (RAG) systems, emphasizing the complexity arising from their multiple components. It first addresses retrieval evaluation, highlighting metrics such as Precision@k, Recall@k, Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (NDCG) to assess the relevance and ranking of retrieved documents. Next, it discusses evaluating generation quality, focusing on faithfulness, relevance, and factuality, with metrics like BLEU, ROUGE, and BERTScore when reference answers are available, or LLM-as-a-judge and human evaluation when they are not. Task-specific metrics (e.g., F1, Exact Match) and baseline comparisons are also recommended. Finally, the note stresses evaluating overall system performance through latency, cost, and availability, which depend on the system’s goals and constraints.

## References

1. <a href="https://en.wikipedia.org/wiki/Mean_reciprocal_rank">Mean Reciprocal Rank</a>
2. <a href="https://www.evidentlyai.com/ranking-metrics/ndcg-metric">Normalized Discounted Cumulative Gain</a>
3. <a href="https://www.evidentlyai.com/ranking-metrics/precision-recall-at-k">Precision and recall at K in ranking and recommendations</a>

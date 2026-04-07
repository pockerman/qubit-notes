# qubit-note: LLM Series | Augmentation Techniques for Text Data

## Overview

In this qubit note we will be looking into ways to augment text data. Augmenting text data can be more challenging than when working with image data, where simple transformations such as rotation or flipping can create valid new samples.  When augmenting text daya we need to maintian semantic integrity and coherence. Just like with image data augmentation, our goal is
to increase the dataset size and diversity, adderess data imbalqnce and data bias so that we improve model robustness.

**keywords:** llms, data-augmentation, AI-engineering

## Augmentation Techniques for Text Data

There are various techniques we can use in order to augment text data ranging from simple word-level manipulations to more complex semantic transformations.
Let's review some of these [1]:

- Synonym replacement; that is replace words with their synonymsThis technique involves replacing words in the original text with their synonyms. We can use <a href="https://en.wikipedia.org/wiki/WordNet">WordNet</a> to find synonyms or use T5.
- <a href="https://lokalise.com/blog/back-translation-best-practices/">Back-translation</a>; that is translate the text in another language and then back to the original. It can be  very effective when we want to introduce natural variations in sentence structure and word choices.
- Use T5 to generate text. Some activities include 
	- Paraphrasing; that is somehow rephrase the sentences using, for example,  T5. 
	- Apply transformations based on sentiment
	- Text expansion
- Use existing LLMs to generate data for us

Let's now how we can ensure data quality. Sure we need to be able to generate as much data as it is needed but we also need to be thoughtful
about the quality of the generated data; at the end of the day our models pick up patterns from the data and we need to make sure that these patterns actually exist.

In general we should limit the proportion of augmented data. A common practice is to start with a 1:1 ratio of original to augmented data and adjust based on model performance [1].
Various techniques exist [1]:

- Quality filtering
- Human-in-the-loop validation
- Evaluate the impact of data augmentation on the LLM performance: Perplexity and diversity are two metrics we should investigate.

## Summary

Text data augmentation aims to increase dataset size and diversity while preserving semantic integrity, which makes it more challenging than image data augmentation. The primary goals are to improve model robustness, address data imbalance, and reduce bias. Common text augmentation techniques range from simple word-level methods to more advanced semantic approaches, including synonym replacement (using tools like WordNet or T5), back-translation, paraphrasing, sentiment-based transformations, text expansion, and data generation with large language models.

When using LLMs for augmentation, careful prompt engineering, quality control, and diversity management (e.g., temperature and top-p sampling) are essential. Preserving meaning is critical, and techniques such as sentence embedding similarity and contextual word embeddings help ensure that augmented text remains semantically consistent with the original. To maintain data quality, augmented data should be used in moderation—often starting with a 1:1 ratio relative to original data—and validated through filtering, human review, and performance evaluation using metrics such as perplexity and diversity.

## References

1. Ken Huang _LLM Design Patterns_, Packt Publishing

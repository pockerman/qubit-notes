# qubit-note: Fine Tuning LLMs

## Overview

In this note, we will revise fine-tuning of LLMs. The discussion is not meant to be exhaustive but rather
a high level overview of the topic. In this note we will discuss:

- What is fine tuning
- Methodologies for fine tuning (full fine tuning, LoRA and QLoRA)

## Fine tuning LLMs

Let's first of all discuss what fine-tuning is. In simple terms, fine-tuning is taking a pre-trained LLM and training it further on your own custom, 
domain-specific or task-specific examples so it adapts its behavior to your use case. 
Thus the purpose of fine tuning is to adapt an LLM to a given scope.

Typically, with fine tuning we will have to prepare input/output examples (often in a chat/message format), then run additional training so the model’s weights get updated based on those examples—so it learns your domain’s terminology, preferred tone, and response style, instead of relying only on prompting. 

Fine tuning a model should follow a structured approach just like any other training methodology for machine learning.
Specifically, the AI platform should somehow support the following phases:

- Data preparation: Collecting, formatting, and validating the examples that will teach the model
- Model selection: Choosing the base model and fine-tuning method appropriate for your task
- Training: Configuring, executing, and evaluating the fine-tuning process
- Deploypment: Deploy the trained model to production
- Monitoring: Monitor the performance of the model in production

### Approaches to fine tuning

There are various approaches to fine tuning. Perhaps the simplest approach is full fine tuning.
In full fine-tuning, you update all of the model’s parameters. It can give the best task/domain adaptation, but it’s expensive (large RAM requirements as well as compute resources) and increases the risk of catastrophic forgetting.

The other side of the spectrum is Parameter-Efficient Fine-Tuning (PEFT). In PEFT you keep the base model frozen and train only a small number of added parameters (“adapters”), which drastically reduces compute and memory needs. Two practical PEFT methods are: LoRA and QLoRA.

- LoRA (Low-Rank Adaptation): adds small trainable adapter matrices to selected modules while leaving the original weights unchanged; often trains only ~0.1%–1% of parameters while retaining most of full fine-tuning quality.
- QLoRA (Quantized LoRA): combines LoRA with 4-bit quantization (plus techniques like NF4 and double quantization) so you can fine-tune much larger models on limited hardware (for example, a 7B model on a ~24GB GPU).


Fine tuning in general should increase the perfromance of a model on a specific domain. In addition, <a href="2025-05-03-retrieval-augmented-generation.md">Retrieval Augmented Generation</a>
can also be used for this task. We will discuss when should we use each of these techniques in <a href="2025-08-31-RAG-or-fine-tuning.md">RAG or Fine Tuning?</a>. 
qubit note <a href="2026-05-15-Hands-On-Fine-Tune-LLaMA.md">Fine Tune  LLaMA-2-7B</a> shows how to fine tune a LLaMA-2-7B model.

## Summary

This note provides a high-level overview of fine-tuning large language models (LLMs), describing it as the process of adapting a pre-trained model to a specific domain or task using custom training examples. It outlines the typical fine-tuning workflow, including data preparation, model selection, training, deployment, and monitoring. The text compares different fine-tuning approaches, starting with full fine-tuning, where all model parameters are updated for maximum adaptation at the cost of high computational requirements and possible catastrophic forgetting. It then introduces parameter-efficient fine-tuning (PEFT) methods such as Low-Rank Adaptation (LoRA), which trains only small adapter layers while keeping the original model weights frozen, and Quantized Low-Rank Adaptation (QLoRA), which combines LoRA with low-bit quantization to enable fine-tuning large models on limited hardware. The note also highlights that fine-tuning can improve model performance on specialized domains and mentions Retrieval-Augmented Generation (RAG) as a complementary technique for enhancing LLM capabilities.


## References

1. Rush Shahani, _Building Reliable AI Systems_, Manning Publications

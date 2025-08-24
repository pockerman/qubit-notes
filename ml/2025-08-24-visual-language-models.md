# qubit-note: Visual Language Models

## Overview

Large language models or LLMs for short, are definitely reshaping the field of AI. A very promising  variant of these models is
what is known as vision language models or VLMs. A VLM can understand, process, and sometimes generate both 
visual data (images, videos) and textual data (language) in a unified way. This of course has the potential
to replace traditional vision models based on, for example the ResNet architecture.

In this qubit note I briefly discuss VLMs and provide some references for furthre research.

**keywords**  large-vision-models, AI-engineering, generative-AI


## Visual language models

In short a VLM is a deep neural network designed to take both images and text as input, understand their relationship, and output meaningful information.
A VLM therefore is a multi-modal model that combines computer vision and natural language processing. Such models are useful when 
the task in hand involves not just object detection but further output text-based information about the detected object. Or
when the object detection depends on understanding some sort of text. VLMs have typically good zero-shot performance and generalise well.
They can work with different types of images, documents and web pages [1].



From an architecture prespective, a VLM typically has two main components:

- A vision encoder 
- A language encoder  

The vision encoder, extracts visual features from images or videos (e.g., using a convolutional neural network or a Vision Transformer (ViT)).
The language encoder processes text (e.g., using a transformer-based language model like BERT or GPT).

Some examples of VLMs include:

- CLIP (OpenAI):  Connects images and text by mapping them into the same space, enabling zero-shot image classification.
- BLIP/BLIP-2: Designed for visual question answering (VQA), captioning, and retrieval tasks.
- Flamingo (DeepMind): Few-shot vision-language reasoning.
- GPT-4 with vision: Can interpret images and answer questions about them.

There is a lot to be said about VLMs; how to select them, how to fine-tune them. We will touch on these issues in later posts.
Meanwhile, going over the references provided can be very useful.


## Summary

In summary, VLMs are a promising variant of large language models (LLMs) capable of understanding, processing, and generating both visual and textual data in a unified manner. They integrate computer vision and natural language processing, making them ideal for tasks requiring both object detection and contextual text interpretation. Architecturally, VLMs typically include a vision encoder (e.g., CNNs or Vision Transformers) and a language encoder (e.g., BERT, GPT). Examples include CLIP, BLIP, Flamingo, and GPT-4 with vision, which excel in zero-shot learning and generalization. These models are increasingly replacing traditional vision systems and hold potential for diverse applications like visual question answering, captioning, and retrieval.

## References

1. <a href="https://huggingface.co/blog/vlms">Vision Language Models Explained</a>
2. <a href="https://huggingface.co/blog/vlms-2025">Vision Language Models (Better, Faster, Stronger)</a>
3. <a href="https://huggingface.co/blog/trl-vlm-alignment#multimodal-group-relative-policy-optimization-grpo">Vision Language Model Alignment in TRL</a>
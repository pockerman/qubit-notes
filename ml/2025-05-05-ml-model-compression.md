# qubit-note: ML Model Compression

## Overview

Very often we want to reduce the size of a machine learning model; e.g. when we want to deploy
the model on an edge device. There are various ways we can do this. In this note I discuss
some of the approaches we can follow in order to compress an ML model

**keywords:** machine-learning, ml-model-compression

## ML model compression

Although in general large models are exepected to have better accuracy, there cases where we can trade
a bit of accuracy with a significantly smaller model. Compressing an ML model is sometimes the only
viable way in order to deploy this model. Comression techniques include: 


- <a href="https://pytorch.org/tutorials/intermediate/pruning_tutorial.html">Model pruning</a> 
- <a href="https://pytorch.org/docs/stable/quantization.html">Model quantization</a> 
- <a href="https://en.wikipedia.org/wiki/Knowledge_distillation">Knowledge distillation</a>

Model pruning is a technique used in deep learning to remove unimportant parameters from neural networks without compromising the performance of the model
significantly. The process aims at reducing the size of the neural network and the computational resources required to run it.
It can be applied to weights, biases, or entire neurons, with weight pruning being the most common due to its minimal impact on the model's architecture.

Model quantization reduces the precision of model parameters, such as weights and activations, from high-precision formats like 32-bit floating point to lower-precision formats like 8-bit integer  or even 4-bit integer.This reduction in precision leads to substantial benefits including decreased memory usage, faster inference times, and reduced energy consumption.
Quantization can be applied in various ways depending on the model and hardware requirements.

Knowledge distillation also known as model distillation, is an ML technique whereby knowledge is transferred  from a large model to a smaller one. 
This process aims to train a more compact model to mimic a larger, more complex model without losing performance. 
Typically, we call the large model as the _teacher_, and the smaller model is called the _student_.
Knowledge distillation is particularly useful for deploying models on less powerful hardware, such as mobile devices, by making them more cost-effective and faster to evaluate.
 
## References

- <a href="https://pytorch.org/tutorials/intermediate/pruning_tutorial.html">Model pruning</a> 
- <a href="https://pytorch.org/docs/stable/quantization.html">Model quantization</a> 
- <a href="https://en.wikipedia.org/wiki/Knowledge_distillation">Knowledge distillation</a>
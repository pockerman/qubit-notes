# Note: Bias-Variance Dilemma

## Overview

When working with supervised machine learning models we typically need to address the so called
<a href="https://en.wikipedia.org/wiki/Bias%E2%80%93variance_tradeoff">bias-variance dilemma</a> or trade off. In this note, I describe what this dilemma consists of.

**keywords** bias-variance-dilemma, machine-learning, supervised-learning

## Bias-variance dilemma

The bias-variance dilemma frequently pops up when working
with machine learning models and it is related with the complexity of the model.
Specifically, in supervised learning, we have an input $\mathbf{x}$ and we are trying to learn its relation to a variable $\mathbf{y}=f(\mathbf{x})$.
We assume a relationship that has the following form:

$$\mathbf{y}=f(\mathbf{x}) + \boldsymbol{\epsilon}$$

where $\boldsymbol{\epsilon}$ is some random noise; e.g. in linear regression we assume that this term follow a zero-mean normal distribution.
We want to be able to assess how well the model fits the data. Therefore, we decompose the overall error in three factors/components

- **Bias:** The error caused by simplified assumptions in the model. High bias means the model is underfitting i.e. it's too simple to capture the underlying patterns.
- **Variance:** The error from the model's sensitivity to fluctuations in the training data. High variance means the model is overfitting i.e. it's too complex and captures noise in the training data.
- **Irreducible Error:** The inherent noise in the problem that can't be reduced by any model.


For example a linear regression model is a model with high bias but low variance i.e. this means that 
the model predictions can frequently be off but otherwise the predicted outputs have low variance.
In contrast, models such as neural networks have low bias but high variance i.e. our predictions will be in general accurate
but exhibit wild variations.


In general we would like both model bias and model variance to be small however it is not possible to minimize both simultaneously. 
A very simple model will often have high bias and low variance and therefore the
model will in general undrefit the data.  A model with high variance will produce predictions that will vary widedly based on the input features so a model
with high variance will exhibit overfitting. So schematically:


$$\text{Underfitting}\rightarrow \text{High Bias}$$
$$\text{Overerfitting}\rightarrow \text{High Variance}$$


High bias can be mitigated by introducing complexity into the model e.g. more features or more layers. 
High variance can be mitigated by using more data or regularization techniques.

----
**Remark**

Notice that high variance can also be observed due to outliers in the data, see question [Q16: How can you make your models more robust to outliers?](#q16), and may
not neccessarily be a consequence of overiffiting.

----


From what we discussed above, the bias variance dilema is effectively related with the modelling assumptions we made i.e. a simple model will in general show high bias whilst a highly complex model will in genral exhibit high variance. That being said, we can increase the model complexity in order to mitigate bias and we can use more data in order to mitigate
high variance.

The model bias-variance is effectively related to the <a href="https://machinelearningmastery.com/overfitting-and-underfitting-with-machine-learning-algorithms/">model overfitting or underfitting</a> the data set.
Typically a model that underfits the data will have low complexity and it will exhibit low performance in both during training and testing i.e. when targeting both the train and the test set.
In contrast when facing overfitting, the model will typically exhibit very good performance on the training zero; the model loss will be almost zero.
However, the model exhibits very low performance on the test set. In this case the model is very complex for the presented data set and it able to pick up the
noise that is present in it. Some common remedies for overfitting are:

- Decrease model complexity if possible
- Increase the volume of the training data set (e.g. consider data augmentation)
- Use reguralization
- Use dropout (for deep neural networks)
- Consider early stopping the training process


## References

1. <a href="https://en.wikipedia.org/wiki/Bias%E2%80%93variance_tradeoff">Bias-variance dilemma</a>
2. <a href="https://machinelearningmastery.com/overfitting-and-underfitting-with-machine-learning-algorithms/">Overfitting and underfitting with machine learning algorithms</a>

# qubit-note: Dimensionality Reduction with PCA

## Overview

More than often we need to deal with datasets that have many features. 
Using all these features in a model is not necesserilly a good thing as it increases all
aspects of the computation plus it hinders the interpretability of the model i.e. for humans
to be able to explain why the model output is this or that. 

Reducing the number of features or dimensions of the dataset is one approach one can
follow and in this short note I discuss one of the available dimensionality reduction
techniques i.e. <a href="https://en.wikipedia.org/wiki/Principal_component_analysis">principal component analysis</a> or PCA.

**keywords:** dimensionality-reduction, PCA, data-models, machine-learning

## Dimensionality reduction with PCA

PCA can be classified as an unsupervised algorithm as it does not require any labels. The founding idea behind PCA is that
is a column has high variance then it contains more information than a column with less variance.

When using PCA we compute what we call the principal components. We then use these components to somehow change the basis of the data.
Thus, PCA can be viewed as a basis-change technique of a vector space. This change of basis is done by projecting the 
data points onto the first few principal components. Typically, implementations of the algorithm will accept as an input
the number of princiapl components to retain/use. The project is performed such that we obtain lower-dimensional data while preserving as much of the data's variation as possible. The first principal component can equivalently be defined as a direction that maximizes the variance of the projected data. The $i-$th principal component can be taken as a direction orthogonal to the first $i − 1$ principal components that maximizes the variance of the projected data [1]. 



PCA is a versatile methodology and as a dimensionality reduction techinque, it can be used for visualization of high-dimensional data, for noise filtering, and for feature selection. 

## References

1.  <a href="https://en.wikipedia.org/wiki/Principal_component_analysis">Principal component analysis</a>
# qubit-note: Dimensionality Reduction with PCA

## Overview

More than often we need to deal with datasets that have many features. 
Using all these features in a model is not necesserilly a good thing as it increases all
aspects of the computation, memory footprint, train and inference time e.t.c,  plus it hinders the interpretability of the model i.e. for humans
to be able to explain why the model output is this or that. 

Reducing the number of features or dimensions of the dataset is an approach one can
follow and in this short note I discuss one of the available dimensionality reduction
techniques i.e. <a href="https://en.wikipedia.org/wiki/Principal_component_analysis">principal component analysis</a> or PCA.

**keywords:** dimensionality-reduction, PCA, data-models, machine-learning

## Dimensionality reduction with PCA

PCA can be classified as an unsupervised algorithm as it does not require any labels. The founding idea behind PCA is that
if a column has high variance then it contains more information than a column with less variance.

When using PCA we compute what we call the principal components. We then use these components to somehow change the basis of the data.
Thus, PCA can be viewed as a basis-change technique of a vector space. This change of basis is done by projecting the 
data points onto the first few principal components. Typically, implementations of the algorithm will accept as an input
the number of princiapl components we want to retain/use. The projection is performed such that we obtain lower-dimensional data while preserving as much of the data's variation as possible. The first principal component can equivalently be defined as a direction that maximizes the variance of the projected data. The $i-$th principal component can be taken as a direction orthogonal 
to the first $i − 1$ principal components that maximizes the variance of the projected data [1]. 


The following Python script use the <a href="https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html">PCA</a> 
class from <a href="https://scikit-learn.org/stable/index.html">sklearn</a>.

```
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


if __name__ == '__main__':

	rng = np.random.RandomState(1)
	X = np.dot(rng.rand(2, 2), rng.randn(2, 200)).T
	
	pca = PCA(n_components=2)
	pca.fit(X)

	print("PCA components: ")
	print(pca.components_)
	print("PCA explained variance: ")
	print(pca.explained_variance_)

```

Running the script produces the following output:

```
PCA components: 
[[-0.94446029 -0.32862557]
 [-0.32862557  0.94446029]]
PCA explained variance: 
[0.7625315 0.0184779]
```

The implementation of PCA uses the <a href="https://en.wikipedia.org/wiki/Singular_value_decomposition">singular value decomposition</a> or SVD.
This is one of the most important matrix factorization techniques used in a lot fields.

PCA is a versatile methodology and as a dimensionality reduction techinque, it can be used for visualization of high-dimensional data, for noise filtering, and for feature selection. 
However, given that is looking the variation present in a feature it is sensitive to outliers.

## References

1.  <a href="https://en.wikipedia.org/wiki/Principal_component_analysis">Principal component analysis</a>
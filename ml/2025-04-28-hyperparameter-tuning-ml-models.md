# Note: Hyperparameter Tuning in ML Models

## Overview

When working with ML models we need to deal with two types of parameters; the model parameters e.g weights in a neural network
and parameters that somehow specify how the model behaves e.g. number of neighbors in a KNN model or how it will be trained
e.g. learning rate. The latter two types of parameters are called hyperparameters and we don't train these but rather try to
infer these. In this note I will discuss methodologies one can use in order to specify these parameters.
Specifically, I will discuss:

- _Grid-search_
- _Random-search_

**keywords** machine-learning, hyperparameter-tuning, grid-search, random-search, sklearn

## Hyperparameter tuning in ML models

A hyperparameter is a model argument whose value is set before the learning process begins.
However, a hyperparameter may affect both the performance of the model during deployment as well as
during training. 

Perhaps the most popular method for hyperparameter tuning is the so called _grid-search_.
This approach involves forming a Cartesian product of the parameters we want to investigate.
The training then proceeds by exhaustively searching over these values and select the 
model that performs best. This approach is simple to set up and use however it can eventually
become quite costly. 

The following code snippet taking from [2], shows how to do grid-search with sklearn

```
from sklearn import svm, datasets
from sklearn.model_selection import GridSearchCV
iris = datasets.load_iris()
parameters = {'kernel':('linear', 'rbf'), 'C':[1, 10]}
svc = svm.SVC()
clf = GridSearchCV(svc, parameters)
clf.fit(iris.data, iris.target)
sorted(clf.cv_results_.keys())
```

_Random-search_ is another popular methodology for hyperparamter tuning. In this approach, we establish a 
joint distribution over the Cartesian product formed by the values of the parameters we want to investigate and sample
from this distribution. This avoids the problematic search over a potentially large space. 

The following code snippet, taken from [3], shows how to do random-search with sklearn

```
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform
iris = load_iris()
logistic = LogisticRegression(solver='saga', tol=1e-2, max_iter=200,
                              random_state=0)
distributions = dict(C=uniform(loc=0, scale=4),
                     penalty=['l2', 'l1'])
clf = RandomizedSearchCV(logistic, distributions, random_state=0)
search = clf.fit(iris.data, iris.target)
search.best_params_
```

Although random-search does not go over all the specified values, it may miss the optimal
parameters. In contrast, the exhaustive search performed by grid-search gurantees that the optimal
set will be found.

Other hyperparameter tuning approaches include Bayesian optimization, Gradient-based optimization and Evolutionary optimization.
See [1] for more information and further references.

## References

1. <a href="https://en.wikipedia.org/wiki/Hyperparameter_optimization">Hyperparameter optimization</a>
2. <a href="https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html">GridSearchCV</a>
3. <a href="https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html">RandomizedSearchCV</a>
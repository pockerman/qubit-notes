# qubit-note: ML Series | Machine Learning Concepts Part 5

## Overview

In this ML Series note we will look into the following machine learning concepts:

- What is the bias-variance tradeoff?
- What are outliers and how to handle them?
- What is hyperparameter tuuning?

### Concept 21:  What is bias-variance tradeoff?

This is fundamental concept in machine learning as it describes the tradeoff between the two sources of error that affect model performance.
The total error can be decomposed as

$$
\text{Error} = (\tex{Bias})^2 + \text{Variance} + \text{Irreducible Error}
$$

The bias-variance dilema tells us that we cannot decrease both the bias and the variance of a model.
We discuss more this in <a href="2025-04-26-bias-variance-dilemma.md">Bias-Variance Dilemma</a>

### Concept 22: What are outliers and how to handle them?

Outliers are data points that differ significantly from other observations in the dataset. 
Outliers can arise from various such rare events, errors or variability in the data source. 
Outliers in general cause problems problems in machine learning models as they skew the statistics.
This is especially true for regression and distance-based algorithms.

There are various methods that we can use i9n order to detect outliers

- Box Plot/IQR 
- Z-Score 
- Scatter plots, histograms or violin plots.


For a gneral ML task, we may choose to remove the outliers. However we wmay also choose to:
Handling Methods:

- Transform the data e.g.  log, square root or other transformations to reduce skewness.
- Cap/floor Values
- Use models not sensitive to outliers 


### Concept 23:  What is hyperparameter tuuning?

Hyperparameters are parameters set before training like learning rate, number of trees in random forest, regularization strength, etc that cannot be learned directly from the data.
Hyperparameter tuning is the process of finding the best set of hyperparameters for a machine learning model to maximize performance. 

Spome common hyperparameter tuning methods are:

- Grid search
- Random search
- Bayesian optimization

We discuss more hyperparameter tuning in <a href="2025-04-28-hyperparameter-tuning-ml-models.md">Hyperparameter Tuning in ML Models</a>

## Summary


This note introduces three important machine learning concepts: the bias-variance tradeoff, outliers, and hyperparameter tuning. The bias-variance tradeoff explains the balance between underfitting and overfitting, where reducing one source of error often increases the other, making it a core challenge in model design. The note also discusses outliers, which are abnormal data points that can distort model performance, especially in regression and distance-based algorithms, and presents common detection and handling techniques such as IQR, Z-scores, transformations, and robust models. Finally, it explains hyperparameter tuning, the process of selecting optimal model settings like learning rate or tree depth using methods such as grid search, random search, and Bayesian optimization to improve overall model performance.


## References

1. <a href="https://www.geeksforgeeks.org/machine-learning/machine-learning-interview-questions/">Machine Learning Interview Questions and Answers</a>
2. <a href="https://www.dailydoseofds.com/">Daily Dose of Data Science</a>
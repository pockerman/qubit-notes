# qubit-note: ML Series | Machine Learning Concepts Part 1

## Overview

In this now we will summarize some common concepts in machine learning such what is overfittings and
what is regualrization.



### Concept 1: What is overfitting?

We say that a model overfits the train set when it pics up every nuance and noise that is present in it. A very clear 
sign of model overfitting is when the accuracy is very high in the training set but rather high in the test/validation set.
in other words, the model learns random fluctuation in the train set.

### Concept 2: How can it we avoid overfitting?

There are several ways one can use in order to avoid model overfitting:

- Early stopping: Stop training when validation accuracy stops improving, even if training accuracy is still increasing.
- Regularization: Techniques like L1 (Lasso) or L2 (Ridge) regularization. These methods add penalties to large weights to reduce model complexity.
- Use a simpler model: use a simpler model if it can explain the data equally well.
- Dropout: if using neural networks, randomly drop neurons during training to prevent over-reliance on specific nodes.
- Cross-Validation: Use k-fold cross-validation to ensure the model generalizes well.

### Concept 3: What is underfitting?

Underfitting is somehow the opposite of overfitting, the model exhibits low performance both in the train and test set.
In other words, the model does not have the capacity to actually model the data.

### Concept 4: How can we avoid overfitting?

The  obvious answer is to increase the complexity of the model. Other than that, we can also use:

- More relevant features: Include meaningful features that better represent the data.
- Reduce regularization if it is used: Too much regularization can restrict the model’s ability to learn.
- Train longer: Allow the model more epochs or iterations to properly learn patterns.

### Concept 5: What is regularizarion?

This is a technique one can use in order to reduce model complexity and thus prevent overfitting. 
Typically, regularization  works by adding a penalty term to the loss function to discourage the model from assigning too much importance (large weights) to specific features. This helps the model generalize better on unseen data.

There are various regularization approaches:

- Lasso or L1 regularization: Adds the absolute value of weights as a penalty which can shrink some weights to zero and perform feature selection.
- Ridge or L2 regularization: Adds the squared value of weights as a penalty which reduces large weights but doesn’t eliminate them.
- Elastic Net: Combines both L1 and L2 penalties to balance feature selection and weight reduction.
- Dropout (for Neural Networks): Randomly drops neurons during training to avoid over-reliance on specific nodes.

### Concept 6: What are some model evaluation metrics in machine learning?

Ther are various model evaluation techniques and this indicates that there is not one size fits all.
An evaluation technique will, typically, assess an aspect of the model performance. Overall we evaluate a model based 
on the metrics we care in the most.

Regardless of the technique, it is important to state that  we should split the data set into train and test set.
The test set is held apart and used only for model evaluation. Some common split ratios are 70/30 and 80/20

----
**Remark Cross Validation**

Cross validation is a common theme in machine learning and there are a handful of ways to do it.
The k-folds cross validation consists of splitting the data into k folds train on k-1 folds, validate on the remaining fold and average the results to reduce bias. Cross validation is a common training technique when there is a scarsity of the data

---

Below are some evaluation metric for classification tasks.

- Confusion Matrix (for Classification): Counts True Positives, True Negatives, False Positives and False Negatives.
- Accuracy: Proportion of correct predictions over total predictions.
- Precision: Here correct positive predictions are divided by Total predicted positives.
- Recall (Sensitivity): Here correct positive predictions are divided by Total actual positives.
- F1-Score: Harmonic mean of precision and recall. It balances precision and recall.
- ROC Curve & AUC: Measures model’s ability to distinguish between classes. Here AUC is area under the ROC curve.


## Summary

This note introduces several foundational machine learning concepts related to model training, generalization, and evaluation. It explains overfitting, where a model learns noise and performs well on training data but poorly on unseen data, and underfitting, where the model is too simple to capture underlying patterns. The note discusses techniques to improve generalization such as early stopping, regularization, dropout, simpler models, and cross-validation. It also explains regularization methods including L1 (Lasso), L2 (Ridge), Elastic Net, and dropout in neural networks. Finally, it provides an overview of common model evaluation practices and metrics, including train/test splits, k-fold cross-validation, confusion matrices, accuracy, precision, recall, F1-score, and ROC-AUC for classification tasks.


## References

1. <a href="https://www.geeksforgeeks.org/machine-learning/machine-learning-interview-questions/">Machine Learning Interview Questions and Answers</a>
2. <a href="https://www.dailydoseofds.com/">Daily Dose of Data Science</a>


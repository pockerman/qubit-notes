# qubit-note: ML Series | Machine Learning Concepts Part 2

## Overview

We continue the series of machine learning concepts by looking into the following:

- What is a confusion matrix
- What is the difference between precision and recall? 
- What is the  $F1$ score?
- What are some common loss functions in machine learning?
- What is the  AUC/ROC curve?

We will continue counting from where we finished in the previous note

### Concept 7: What is a confusion matrix? 

We noticed the confusion matrix when discussing metrics for evaluating classifiers, see _Concept 6: What are some model evaluation metrics in machine learning?_.
As its name suggests, a  confusion matrix is a table. It is  used to evaluate the performance of a classification model. 
It compares the predicted labels with the actual labels, telling how well the model is performing and what types of errors it makes.

Specifically, we log four types of counters (for a binary classification problem)

- True Positives (TP): Correctly predicted positive cases.
- True Negatives (TN): Correctly predicted negative cases.
- False Positives (FP): Negative cases incorrectly predicted as positive.
- False Negatives (FN): Positive cases incorrectly predicted as negative.


From these counters we can compute, precision, recall and $F1$ score.

### Concept 8: What is the difference between precision and recall?

Precision and recall are two metrics we can compute out of a confusion matrix.

Precision is defined as  the ratio between the true positives(TP) and all the positive examples (TP+FP) predicted by the model. 

$$\text{Precision} = \frac{TP}{TP + FP}$$


In other words, it measures how many of the predicted positive examples are actually true positives. It is a measure of the model's ability to avoid false positives and make accurate positive predictions.
**Example:** In spam detection, high precision means most emails marked as spam are truly spam.

Recall is defined as the ratio of true positives (TP) and the total number of examples (TP+FN) that actually fall in the positive class. 

$$\text{Recall} = \frac{TP}{TP + FN}$$

Recall measures how many of the actual positive examples are correctly identified by the model. It is a measure of the model's ability to avoid false negatives and identify all positive examples correctly. Recall is also known as True Positive Rate or TPR.

**Example:** In disease detection, high recall means most sick patients are correctly identified.

Depending on the application we may want to optimize against either of the two; precision is about being exact (avoiding false positives) 
whilst recall is about being comprehensive (avoiding false negatives) [1].

We can also compute the following metric (False Positive Rate)

$$\text{FPR} = \frac{FP}{FP + TN}$$

### Concept 9: What is the  $F1$ score?

The $F1$ score is defined as the harmonic means of precision and recall. Namely:

$$
F1 = 2 \times \frac{\text{Precision}\times \text{Recall}}{\text{Precision} + \text{Recall}}
$$

The $F1$ score is a metric we can use when there high class imbalance.

### Concept 10: What are some common loss functions in machine learning?

Machine learning models optimze during training a loss function. A loss function measures the error between the model’s predicted output and the actual target value. 
They guide the optimization process during training. There are many different loss functions one can use [1]. 

- Mean Squared Error (MSE): Used in regression problem. It penalizes larger errors more heavily by squaring them.
- Mean Absolute Error (MAE): Used in regression as it takes absolute differences between predicted and actual values. It is less sensitive to outliers than MSE.
- R-squared (R²): Used in regression and measures how well the model explains variance in the target variable (This is not actually a loss function but a metric to assess the model quality).
- Huber Loss: It combines MSE and MAE making it less sensitive to outliers than MSE.
- Cross-Entropy Loss (Log Loss): Used in classification problem. It measures the difference between predicted probability distribution and actual labels.
- Hinge Loss: Used for classification with SVMs. It encourages maximum margin between classes.
- KL Divergence: Measures how one probability distribution differs from another hence used in probabilistic models.
- Exponential Loss: Used in boosting methods like AdaBoost; penalizes misclassified points more strongly.

### Concept 11: What is the  AUC/ROC curve?

The Receiver Operating Characteristic or ROC curve is a graphical plot that shows the trade-off between True Positive Rate (TPR / Recall) and False Positive Rate (FPR) at different threshold values (see also _Concept 7: What is the difference between precision and recall?_.

The Area Under the Curve or AUC is the area under the ROC curve. 
It represents the probability that a randomly chosen positive instance is ranked higher than a randomly chosen negative instance [1].

AUC = 1 → Perfect classifier
AUC = 0.5 → Random guessing
AUC < 0.5 → Worse than random


ROC shows performance across thresholds. AUC summarizes overall model performance into a single number.

**Example:** If a medical test has an AUC of 0.90, it means there’s a 90% chance that the model will rank a randomly chosen diseased patient higher than a healthy one.

## Summary

This note continues the overview of core machine learning concepts by focusing on classification evaluation metrics and loss functions. It explains how a confusion matrix summarizes model predictions using true positives, true negatives, false positives, and false negatives, which are then used to compute precision, recall, and the F1 score. Precision measures how accurate positive predictions are, while recall measures how well the model identifies all positive cases, with the F1 score balancing both metrics, especially in imbalanced datasets. The note also introduces common loss functions such as MSE, MAE, Cross-Entropy, Huber Loss, and KL Divergence, highlighting their use in regression, classification, and probabilistic models. Finally, it discusses ROC curves and AUC, which evaluate classifier performance across different decision thresholds by analyzing the trade-off between true positive and false positive rates, with AUC providing a single measure of overall classification quality.


## References

1. <a href="https://www.geeksforgeeks.org/machine-learning/machine-learning-interview-questions/">Machine Learning Interview Questions and Answers</a>
2. <a href="https://www.dailydoseofds.com/">Daily Dose of Data Science</a>

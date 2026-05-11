# qubit-note: ML Series | Machine Learning Concepts Part 3

## Overview

In this ML Series note we will look into the following machine learning concepts:

- When not to use  accuracy as a metric for classification performance?
- What is cross-validation?
- What is the difference between regularization, standardization and normalization?
- What is feature engineering?
- Which are some feature selection techniques?

### Concept 11: When not to use  accuracy as a metric for classification performance?

Accuracy is very common metric when we want to assess the perfromnce of a classifier.
It is defined as

$$
\text{Accuracy} = \frac{\text{Number of instances classified correctly}}{\text{Total number of examples}}
$$

However, accuracy can be misleading, especially with imbalanced datasets. In such cases we should use:

- Precision and/or  recall provide better insight into model performance (see _Concept 7: What is the difference between precision and recall?_).
- $F1$-score combines precision and recall as their harmonic mean, giving a balanced measure of model effectiveness (see _Concept 8: What is the  $F1$ score?_)

### Concept 12: What is cross-validation?

Cross-validation is a model evaluation technique used to test how well a machine learning model generalizes to unseen data. Instead of training and testing on a single split, the dataset is divided into multiple subsets (called folds) and the model is trained and tested multiple times on different folds.

Below are the general steps to perform CV:

- Split the dataset into $k$ folds like 5 or 10.
- Train the model on $(k-1)$ folds and test it on the remaining fold.
- Repeat this process $k$ times so that every fold is used for testing once.
- Take the average of all results as the final performance score.

The procedure above is known as $k-$fold cross validation, however, it's not the only one CV method:

- Stratified k-Fold: Similar to k-Fold but keeps class distribution balanced (useful in classification).
- Leave-One-Out (LOO): Special case where k = number of samples and every single point acts as a test set once.
- Hold-Out Method: Simple train/test split and is considered a basic form of validation.

### Concept 13: What is the difference between regularization, standardization and normalization?

Regularization is a technique used to reduce overfitting by adding a penalty term to the model’s loss function, discouraging overly complex models .e.g L1 (Lasso), L2 (Ridge), Elastic Net.
See also _Concept 5: What is regularizarion?_


Standardization is preprocessing step that rescales features so they have mean = 0 and standard deviation = 1.
Effectively, a feature is rescaled according to:

$$
x = \frac{x - \mu}{\sigma}
$$

Standardization can be useful to algorithms that are sensitive to feature scales such as  SVM, KNN, logistic and linear regression.
Normalization is also a preprocessing step that rescales feature values into a fixed range, usually [0, 1].
A feature is scaled according to

$$
x = \frac{x - x_{min}}{x_{max} - x_{min}}
$$

This is useful when features have very different scales or units.

### Concept 14: What is feature engineering?

Feature engineering is the process of creating, transforming or selecting relevant features from raw data to improve the performance of a machine learning model. Better features often lead to better model accuracy and generalization. It also reduces overfitting and make the model easier to interpret [1].

Key steps in feature engineering:

- Feature creation: Generate new features from existing data like extracting “year” or “month” from a date column.
- Feature transformation: Apply scaling, normalization or mathematical transformations (log, square root) to features.
- Feature encoding: Convert categorical variables into numerical form like one-hot encoding, label encoding.
- Feature selection: Identify and keep only the most relevant features using techniques like correlation analysis, mutual information or model-based importance scores.

### Concept 15:  Which are some feature selection techniques?

Feature selection is the process of choosing the most relevant features from your dataset to improve model performance, reduce overfitting and simplify the model.
There are various methods we can use for this task [1]:

**Filter Methods** 

Filter methods evaluate each feature independently with target variable. Feature with high correlation with target variable are selected as it means this feature has some relation and can help us in making predictions. Here features are selected based on statistical measures without involving any machine learning model.

Some examples are:

- Correlation Coefficient: Remove features highly correlated with others.
- Chi-Square Test: For categorical features.
- ANOVA F-Test: For numerical features.

**Wrapper Methods** 

It uses different combination of features and compute relation between these subset features and target variable and based on conclusion addition and removal of features are done. Stopping criteria for selecting the best subset are usually pre-defined by the person training the model such as when the performance of the model decreases or a specific number of features are achieved.

Some examples are:

- Forward selection: Start with no features and add one at a time.
- Backward elimination: Start with all features and remove one at a time.
- Recursive feature elimination (RFE): Iteratively removes least important features using model weights.

**Embedded Methods** 

Embedded methods perform feature selection during the model training process allowing the model to select the most relevant features based on the training process dynamically.

Some examples are:

- Lasso Regression (L1 regularization): Can shrink some feature coefficients to zero.
- Decision trees / Random forest feature importance: Select features based on importance scores learned during training.

## Summary

This note discusses several important machine learning concepts related to model evaluation, preprocessing, and feature selection. It explains that accuracy can be misleading for imbalanced classification problems and that metrics such as precision, recall, and the F1-score often provide better insight into model performance. It introduces cross-validation, particularly k-fold cross-validation, as a technique for evaluating how well a model generalizes to unseen data. The note also distinguishes between regularization, which reduces overfitting by penalizing model complexity, and preprocessing techniques such as standardization and normalization, which rescale feature values for better training stability. Additionally, it covers feature engineering, the process of creating and transforming useful features from raw data, and summarizes common feature selection methods including filter, wrapper, and embedded approaches used to improve model performance and reduce overfitting.


## References

1. <a href="https://www.geeksforgeeks.org/machine-learning/machine-learning-interview-questions/">Machine Learning Interview Questions and Answers</a>
2. <a href="https://www.dailydoseofds.com/">Daily Dose of Data Science</a>

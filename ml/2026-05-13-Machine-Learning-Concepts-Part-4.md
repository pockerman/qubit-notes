# qubit-note: ML Series | Machine Learning Concepts Part 4

In this ML Series note we will look into the following machine learning concepts:

- What is dimensionality reduction?
- What is categorical data and how to handle it?
- How to handle missing and duplicate values?
- What is Oversampling and undersampling?
- Ho can we use SMOTE to handle data imbalance?


### Concept 16:  What is dimensionality reduction?

More often than not the data we deal in machine learning are high dimensional i.e. they involve a number of attributes often referred to as the curse of dimensionality.
This makes both visualizing the data space difficult whilst it also increases the computation and storage costs.
Dimensionality reduction techniques are methods that allow us to reduce the dimension of the involved data in a consistent and meaningful manner.
Perhaps the most common dimensionality reduction technique is <a href="2025-05-08-dimensionality-reduction-with-PCA.md">PCA</a>.

### Concept 17:  What is categorical data and how to handle it?

The term categorical data refers to data attributes  that represent discrete values and/or categories. Examples of such data include
sex, color or ethinicity. This is in contrast to the continuous numerical values that machine learning models expect. 

There are two types of categorical data nominal and ordinal. The former have no inherent order e.g. color. The latter
have a meaningful order e.g. high, low, medium.

Categorical data must be converted into numerical values somehow in order to be used in machine learning models.
Approaches to do so include

- Label Encoding: Converts each category into a unique integer. For example Red=0, Blue=1, Green=2. This is suitable for ordinal data.
- One-Hot Encoding: Converts categories into binary vectors, creating a new column for each category. For example : Color with Red, Blue, Green becomes three columns: [1,0,0], [0,1,0], [0,0,1]. Suitable for nominal data.
- Binary encoding: Converts categories into binary code, reducing dimensionality compared to one-hot encoding.
- Target/Mean encoding: Replaces categories with mean of target variable for regression or probability of positive class in classification.


### Concept 18: How to handle missing and duplicate values?

Real-world datasets are messy and a lot of clean up has to be done before they can be used. One of the things
the modeller has to decide is how to treat missing data. There are various approaches to this problem.

**Remove rows or columns:**

- Drop rows with missing values 
- Drop columns if most values are missing.

**Imputation:**

- Replace missing values with mean/median (for numerical) or mode (for categorical).
- Fill missing values using previous or next valid value in time series data.
- Predict missing values using a model trained on other features.

### Concept 19: What is oversampling and undersampling?

Often we deal with data that the classes are imbalanced. If we don't do something about this the machine learning model will be biased towards
the dominating class. Both oversampling and undersampling allow us to deal with this situation.

Oversampling increases the number of samples in the minority class to balance the dataset.Techniques include:

- Random oversampling: Duplicate random samples from the minority class.
- SMOTE (Synthetic Minority Over-sampling Technique): Generate synthetic samples by interpolating between existing minority samples.

Undersampling reduces the number of samples in the majority class to balance the dataset. Techniques include:

- Random undersampling: Randomly remove samples from the majority class.
- Cluster-based undersampling: Remove samples based on clustering to retain diversity.
Example: We have a dataset of 1000 positive samples, 100 negative samples.


### Concept 20: Ho can we use SMOTE to handle data imbalance?

SMOTE (Synthetic Minority Over-sampling Technique) creates synthetic data points for minority classes using linear interpolation between existing samples.
The model is trained on more diverse examples rather than duplicating existing points. It may introduce noise into the dataset, potentially affecting model performance if overused.


## Summary

This note introduces several important machine learning concepts related to data preprocessing and handling imbalanced datasets. It explains dimensionality reduction as a way to reduce the complexity of high-dimensional data, highlighting techniques such as Principal Component Analysis (PCA). The text also discusses categorical data, distinguishing between nominal and ordinal categories, and describes common encoding methods such as label encoding, one-hot encoding, binary encoding, and target encoding to transform categorical values into numerical representations suitable for machine learning models. In addition, it covers strategies for handling missing and duplicate values through removal or imputation techniques. Finally, the note examines class imbalance problems and presents oversampling and undersampling methods, with special emphasis on Synthetic Minority Over-sampling Technique (SMOTE), which generates synthetic minority-class samples to improve model training on imbalanced datasets.



## References

1. <a href="https://www.geeksforgeeks.org/machine-learning/machine-learning-interview-questions/">Machine Learning Interview Questions and Answers</a>
2. <a href="https://www.dailydoseofds.com/">Daily Dose of Data Science</a>
